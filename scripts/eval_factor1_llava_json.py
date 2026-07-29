#!/usr/bin/env python3
"""Evaluate a LLaVA LoRA checkpoint on Factor-1 JSON eval splits."""

from __future__ import annotations

import argparse
import json
import os
import re
import string
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from tqdm import tqdm
from transformers import AutoConfig, AutoTokenizer

from ETrain.Models.LLaVA.language_model.llava_llama import LlavaLlamaForCausalLM
from ETrain.Models.LLaVA.checkpoint_utils import align_state_dict_keys_to_model
from ETrain.utils.LLaVA.constants import (
    DEFAULT_IMAGE_PATCH_TOKEN,
    DEFAULT_IMAGE_TOKEN,
    DEFAULT_IM_END_TOKEN,
    DEFAULT_IM_START_TOKEN,
    IMAGE_TOKEN_INDEX,
)
from ETrain.utils.LLaVA.conversation import SeparatorStyle, conv_templates
from ETrain.utils.LLaVA.mm_utils import KeywordsStoppingCriteria, tokenizer_image_token


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--model-path", required=True, type=Path)
    p.add_argument("--model-base", default=None, type=Path)
    p.add_argument("--stage-name", required=True)
    p.add_argument("--image-folder", required=True, type=Path)
    p.add_argument("--output-dir", required=True, type=Path)
    p.add_argument("--eval-file", action="append", required=True, help="task_name:path/to/eval.json")
    p.add_argument("--conv-mode", default="vicuna_v1")
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--top-p", type=float, default=None)
    p.add_argument("--num-beams", type=int, default=1)
    p.add_argument("--max-new-tokens", type=int, default=64)
    p.add_argument("--limit", type=int, default=None)
    p.add_argument("--device", default="cuda")
    return p.parse_args()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_llava_lora(model_path: Path, model_base: Path | None, device: str):
    adapter_config_path = model_path / "adapter_config.json"
    if model_base is None:
        cfg = load_json(adapter_config_path)
        model_base = Path(cfg["base_model_name_or_path"])

    print(f"Loading tokenizer from base: {model_base}")
    tokenizer = AutoTokenizer.from_pretrained(str(model_base), use_fast=False)
    lora_cfg = AutoConfig.from_pretrained(str(model_path))

    print(f"Loading base LLaVA model: {model_base}")
    model = LlavaLlamaForCausalLM.from_pretrained(
        str(model_base),
        # low_cpu_mem_usage=True can leave parameters on the meta device in this
        # local Transformers/PyTorch stack, which later crashes at model.to(...).
        low_cpu_mem_usage=False,
        config=lora_cfg,
        torch_dtype=torch.float16,
    )

    # Vision-only checkpoints contain CLIP tensors, so materialize the delayed
    # vision tower before applying non-LoRA weights.
    vision_tower = model.get_vision_tower()
    if vision_tower is not None and not vision_tower.is_loaded:
        vision_tower.load_model()

    non_lora_path = model_path / "non_lora_trainables.bin"
    if non_lora_path.exists():
        print(f"Loading non-LoRA trainables: {non_lora_path}")
        non_lora = torch.load(str(non_lora_path), map_location="cpu")
        aligned, unmatched = align_state_dict_keys_to_model(non_lora, model)
        if non_lora and not aligned:
            raise RuntimeError(
                "No non-LoRA checkpoint tensors matched the base LLaVA model; "
                f"first keys: {list(non_lora)[:5]}"
            )
        model.load_state_dict(aligned, strict=False)
        print(f"Loaded {len(aligned)}/{len(non_lora)} non-LoRA tensors")
        if unmatched:
            print(f"Warning: {len(unmatched)} non-LoRA tensors were unmatched: {unmatched[:5]}")

    print(f"Loading LoRA adapter: {model_path}")
    from peft import PeftModel

    model = PeftModel.from_pretrained(model, str(model_path))
    print("Merging LoRA weights")
    model = model.merge_and_unload()

    meta_params = [name for name, param in model.named_parameters() if getattr(param, "is_meta", False)]
    if meta_params:
        preview = ", ".join(meta_params[:10])
        raise RuntimeError(
            f"Model still has {len(meta_params)} meta parameters after loading LoRA. "
            f"First parameters: {preview}. This usually means the base checkpoint was not fully materialized."
        )

    mm_use_im_patch_token = getattr(model.config, "mm_use_im_patch_token", True)
    mm_use_im_start_end = getattr(model.config, "mm_use_im_start_end", False)
    if mm_use_im_patch_token:
        tokenizer.add_tokens([DEFAULT_IMAGE_PATCH_TOKEN], special_tokens=True)
    if mm_use_im_start_end:
        tokenizer.add_tokens([DEFAULT_IM_START_TOKEN, DEFAULT_IM_END_TOKEN], special_tokens=True)
    model.resize_token_embeddings(len(tokenizer))

    vision_tower = model.get_vision_tower()
    if not vision_tower.is_loaded:
        vision_tower.load_model()
    vision_tower.to(device=device, dtype=torch.float16)
    image_processor = vision_tower.image_processor

    model.to(device=device, dtype=torch.float16)
    model.eval()
    return tokenizer, model, image_processor


def clean_question(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("<image>", " ")).strip()


def get_qa(row: dict[str, Any]) -> tuple[str, str]:
    question = ""
    answer = ""
    for msg in row.get("conversations", []):
        if msg.get("from") == "human" and not question:
            question = clean_question(str(msg.get("value", "")))
        if msg.get("from") == "gpt" and not answer:
            answer = str(msg.get("value", "")).strip()
    return question, answer


_ARTICLES = re.compile(r"\b(a|an|the)\b", flags=re.IGNORECASE)
_PUNCT_TABLE = str.maketrans("", "", string.punctuation)


def normalize_answer(s: str) -> str:
    s = str(s).lower().strip()
    s = s.translate(_PUNCT_TABLE)
    s = _ARTICLES.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def parse_number(s: str) -> float | None:
    m = re.search(r"[-+]?\d*\.?\d+", str(s).replace(",", ""))
    if not m:
        return None
    try:
        return float(m.group(0))
    except ValueError:
        return None


def score_prediction(pred: str, gt: str, answer_type: str | None) -> dict[str, float]:
    pn = normalize_answer(pred)
    gn = normalize_answer(gt)
    exact = float(pn == gn)
    relaxed = exact
    if not relaxed and gn:
        relaxed = float(gn in pn or pn in gn)

    number_match = 0.0
    if answer_type == "number":
        pv = parse_number(pred)
        gv = parse_number(gt)
        number_match = float(pv is not None and gv is not None and abs(pv - gv) < 1e-6)
        relaxed = max(relaxed, number_match)

    yes_no_match = 0.0
    if answer_type == "yes_no":
        yes = {"yes", "yeah", "yep", "true"}
        no = {"no", "not", "false"}
        p_first = pn.split(" ")[0] if pn else ""
        g_first = gn.split(" ")[0] if gn else ""
        yes_no_match = float((p_first in yes and g_first in yes) or (p_first in no and g_first in no))
        relaxed = max(relaxed, yes_no_match)

    return {
        "exact_match": exact,
        "relaxed_match": relaxed,
        "number_match": number_match,
        "yes_no_match": yes_no_match,
    }


def evaluate_file(
    task_name: str,
    eval_path: Path,
    args: argparse.Namespace,
    tokenizer,
    model,
    image_processor,
) -> dict[str, Any]:
    rows = load_json(eval_path)
    if args.limit:
        rows = rows[: args.limit]

    pred_dir = args.output_dir / "predictions"
    pred_dir.mkdir(parents=True, exist_ok=True)
    pred_path = pred_dir / f"{task_name}.jsonl"

    metrics_sum = {"exact_match": 0.0, "relaxed_match": 0.0, "number_match": 0.0, "yes_no_match": 0.0}
    answer_type_counts: dict[str, int] = {}
    image_count = 0
    text_only_count = 0

    conv_template = conv_templates[args.conv_mode]
    stop_str = conv_template.sep if conv_template.sep_style != SeparatorStyle.TWO else conv_template.sep2

    with pred_path.open("w", encoding="utf-8") as f:
        for row in tqdm(rows, desc=f"{args.stage_name}/{task_name}"):
            question, gt = get_qa(row)
            answer_type = (row.get("metadata") or {}).get("answer_type")
            answer_type_counts[str(answer_type or "unknown")] = answer_type_counts.get(str(answer_type or "unknown"), 0) + 1

            has_image = bool(row.get("image"))
            if has_image:
                image_count += 1
                if model.config.mm_use_im_start_end:
                    qs = DEFAULT_IM_START_TOKEN + DEFAULT_IMAGE_TOKEN + DEFAULT_IM_END_TOKEN + "\n" + question
                else:
                    qs = DEFAULT_IMAGE_TOKEN + "\n" + question
            else:
                text_only_count += 1
                qs = question

            conv = conv_template.copy()
            conv.append_message(conv.roles[0], qs)
            conv.append_message(conv.roles[1], None)
            prompt = conv.get_prompt()

            if has_image:
                input_ids = tokenizer_image_token(prompt, tokenizer, IMAGE_TOKEN_INDEX, return_tensors="pt").unsqueeze(0)
                image_path = args.image_folder / row["image"]
                image = Image.open(image_path).convert("RGB")
                image_tensor = image_processor.preprocess(image, return_tensors="pt")["pixel_values"][0]
                images = image_tensor.unsqueeze(0).half().to(args.device)
            else:
                input_ids = tokenizer(prompt, return_tensors="pt").input_ids
                images = None

            input_ids = input_ids.to(args.device)
            stopping_criteria = KeywordsStoppingCriteria([stop_str], tokenizer, input_ids)

            with torch.inference_mode():
                output_ids = model.generate(
                    input_ids,
                    images=images,
                    do_sample=args.temperature > 0,
                    temperature=args.temperature,
                    top_p=args.top_p,
                    num_beams=args.num_beams,
                    max_new_tokens=args.max_new_tokens,
                    use_cache=True,
                    stopping_criteria=[stopping_criteria],
                )

            input_len = input_ids.shape[1]
            pred = tokenizer.batch_decode(output_ids[:, input_len:], skip_special_tokens=True)[0].strip()
            if pred.endswith(stop_str):
                pred = pred[: -len(stop_str)].strip()

            score = score_prediction(pred, gt, answer_type)
            for k in metrics_sum:
                metrics_sum[k] += score[k]

            f.write(
                json.dumps(
                    {
                        "id": row.get("id"),
                        "stage": args.stage_name,
                        "task": task_name,
                        "question": question,
                        "gt": gt,
                        "pred": pred,
                        "answer_type": answer_type,
                        "score": score,
                        "metadata": row.get("metadata", {}),
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
            f.flush()

    n = len(rows)
    metrics = {
        "stage": args.stage_name,
        "task": task_name,
        "eval_file": str(eval_path),
        "predictions_file": str(pred_path),
        "num_samples": n,
        "image_samples": image_count,
        "text_only_samples": text_only_count,
        "answer_type_counts": answer_type_counts,
    }
    for k, v in metrics_sum.items():
        metrics[k] = v / n if n else 0.0
    return metrics


def parse_eval_files(values: list[str]) -> list[tuple[str, Path]]:
    parsed = []
    for value in values:
        if ":" not in value:
            raise SystemExit(f"--eval-file must be task:path, got: {value}")
        name, path = value.split(":", 1)
        parsed.append((name, Path(path)))
    return parsed


def main() -> int:
    args = parse_args()
    args.model_path = args.model_path.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer, model, image_processor = load_llava_lora(args.model_path, args.model_base, args.device)

    metrics = []
    for task_name, eval_path in parse_eval_files(args.eval_file):
        metrics.append(evaluate_file(task_name, eval_path.resolve(), args, tokenizer, model, image_processor))

    metrics_path = args.output_dir / "metrics_all.json"
    metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote metrics: {metrics_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
