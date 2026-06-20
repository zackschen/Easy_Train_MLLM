#!/usr/bin/env python3
"""Metadata extraction for CoIN Factor-1 data-transition experiments.

Default paths assume this file is run from your project root:
  raw data: ./cl_dataset/coin
  output:   ./cl_dataset/coin_factor1_meta

Commands:
  python factor1_coin_meta.py inventory
  python factor1_coin_meta.py build --max-samples-per-dataset 1000
  python factor1_coin_meta.py gaps --split all
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import random
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator


DATASETS: dict[str, dict[str, Any]] = {
    "vqav2": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "aliases": ["vqav2", "vqa_v2", "vqa-v2"]},
    "gqa": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "aliases": ["gqa"]},
    "visual7w": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "aliases": ["visual7w", "visual_7w"]},
    "tallyqa": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "skill_hint": "counting", "aliases": ["tallyqa", "tally_qa"]},
    "ai2d": {"regime": "structured_visual_qa", "visual": "diagram", "knowledge": False, "skill_hint": "diagram_reasoning", "aliases": ["ai2d"]},
    "chartqa": {"regime": "structured_visual_qa", "visual": "chart", "knowledge": False, "skill_hint": "chart_reasoning", "aliases": ["chartqa", "chart_qa"]},
    "chartqa_eval": {"regime": "structured_visual_qa", "visual": "chart", "knowledge": False, "skill_hint": "chart_reasoning", "aliases": ["chartqa_eval", "chartqa-eval"]},
    "docvqa": {"regime": "structured_visual_qa", "visual": "document", "knowledge": False, "skill_hint": "document_reasoning", "aliases": ["docvqa", "doc_vqa"]},
    "infographicvqa": {"regime": "structured_visual_qa", "visual": "infographic", "knowledge": False, "skill_hint": "document_reasoning", "aliases": ["infographicvqa", "infographic_vqa"]},
    "okvqa": {"regime": "knowledge_intensive_qa", "visual": "natural_photo", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["okvqa", "ok_vqa", "ok-vqa"]},
    "aokvqa": {"regime": "knowledge_intensive_qa", "visual": "natural_photo", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["aokvqa", "a_okvqa", "a-okvqa"]},
    "scienceqa": {"regime": "knowledge_intensive_qa", "visual": "science_diagram", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["scienceqa", "science_qa", "scienceqa-full", "scienceqa-img"]},
    "mmmu": {"regime": "knowledge_intensive_qa", "visual": "academic_figure", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["mmmu"]},
    "slake": {"regime": "expert_medical_qa", "visual": "medical", "knowledge": True, "skill_hint": "medical_reasoning", "aliases": ["slake"]},
    "vqarad": {"regime": "expert_medical_qa", "visual": "medical", "knowledge": True, "skill_hint": "medical_reasoning", "aliases": ["vqarad", "vqa_rad", "vqa-rad"]},
    "pathvqa": {"regime": "expert_medical_qa", "visual": "medical", "knowledge": True, "skill_hint": "medical_reasoning", "aliases": ["pathvqa", "path_vqa"]},
    "remote_sensing_vqa": {"regime": "expert_remote_sensing_qa", "visual": "remote_sensing", "knowledge": True, "skill_hint": "remote_sensing_reasoning", "aliases": ["remote_sensing_vqa", "rsvqa", "remote-sensing-sft-data"]},
    "lrs_vqa": {"regime": "expert_remote_sensing_qa", "visual": "remote_sensing", "knowledge": True, "skill_hint": "remote_sensing_reasoning", "aliases": ["lrs_vqa", "lrs-vqa", "lrs_vqa"]},
}

Q_FIELDS = ["question", "query", "prompt", "instruction", "problem", "text", "Question"]
A_FIELDS = ["answer", "answers", "label", "response", "target", "final_answer", "multiple_choice_answer", "direct_answer", "Answer"]
C_FIELDS = ["choices", "options", "candidates", "multiple_choices"]
R_FIELDS = ["rationale", "rationales", "explanation", "solution", "reasoning"]
I_FIELDS = ["image", "images", "image_path", "img_path", "image_file", "filename", "file_name", "path", "image_id", "img_id"]

YES_NO = {"yes", "no", "true", "false"}
COLORS = {"red", "blue", "green", "yellow", "black", "white", "gray", "grey", "brown", "orange", "purple", "pink", "silver", "gold", "golden"}
ATTRIBUTES = COLORS | {"large", "small", "big", "tiny", "round", "square", "rectangular", "wooden", "metal", "metallic", "plastic", "open", "closed", "empty", "full"}
TEXT_SPAN_DATASETS = {"docvqa", "infographicvqa"}
KNOWLEDGE_DATASETS = {"okvqa", "aokvqa", "scienceqa", "mmmu", "slake", "vqarad", "pathvqa"}


def norm_key(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(x).lower()).strip("_")


def compact(x: Any) -> str:
    if x is None or isinstance(x, bytes):
        return ""
    if isinstance(x, str):
        return re.sub(r"\s+", " ", x.replace("<image>", " ")).strip()
    if isinstance(x, (int, float, bool)):
        return str(x)
    if isinstance(x, list):
        return " ".join(t for t in (compact(v) for v in x) if t)
    if isinstance(x, dict):
        for k in ["text", "value", "answer", "content", "label"]:
            if k in x:
                return compact(x[k])
    return str(x)


def safe_json(x: Any, max_len: int = 1000) -> Any:
    if x is None or isinstance(x, (bool, int, float)):
        return None if isinstance(x, float) and (math.isnan(x) or math.isinf(x)) else x
    if isinstance(x, bytes):
        return f"<bytes:{len(x)}>"
    if isinstance(x, str):
        return x if len(x) <= max_len else x[:max_len] + "...<truncated>"
    if isinstance(x, dict):
        return {str(k): safe_json(v, max_len) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [safe_json(v, max_len) for v in x[:20]]
    return str(x)


def as_list(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return []
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
            try:
                return as_list(ast.literal_eval(s))
            except Exception:
                pass
        return [s]
    if isinstance(x, dict):
        for k in ["text", "answer", "label", "value", "content"]:
            if k in x:
                return as_list(x[k])
        return [json.dumps(safe_json(x), ensure_ascii=False)]
    if isinstance(x, Iterable) and not isinstance(x, (bytes, bytearray)):
        out: list[str] = []
        for item in x:
            out.extend(as_list(item))
        return [v for v in out if v]
    return [str(x)]


def first(row: dict[str, Any], names: list[str]) -> Any:
    lower = {norm_key(k): k for k in row}
    for n in names:
        k = lower.get(norm_key(n))
        if k is not None:
            return row[k]
    return None


def conv_qa(row: dict[str, Any]) -> tuple[str, str]:
    conv = first(row, ["conversations", "conversation", "messages", "dialog", "chat"])
    if conv is None:
        return "", ""
    if isinstance(conv, str):
        try:
            conv = json.loads(conv)
        except Exception:
            return compact(conv), ""
    if not isinstance(conv, list):
        return "", ""
    q, a = "", ""
    for msg in conv:
        if not isinstance(msg, dict):
            continue
        role = compact(msg.get("role") or msg.get("from")).lower()
        text = compact(msg.get("content") or msg.get("value") or msg.get("text"))
        if not text:
            continue
        if not q and role in {"human", "user", "question", "prompter"}:
            q = text
        elif q and not a and role in {"gpt", "assistant", "answer", "model"}:
            a = text
            break
    return q, a


def img_ref(x: Any) -> str | None:
    if x is None:
        return None
    if isinstance(x, str):
        return x
    if isinstance(x, bytes):
        return f"<embedded_image_bytes:{len(x)}>"
    if isinstance(x, dict):
        if x.get("path"):
            return compact(x["path"])
        if x.get("bytes") is not None:
            b = x["bytes"]
            return f"<embedded_image_bytes:{len(b) if isinstance(b, bytes) else 'unknown'}>"
        return json.dumps(safe_json(x), ensure_ascii=False)
    if isinstance(x, list) and x:
        return img_ref(x[0])
    return compact(x) or None


def infer_split(path: Path) -> str:
    s = "/".join(path.parts).lower()
    if re.search(r"(^|[/_.-])train(ing)?($|[/_.-])", s):
        return "train"
    if "validation" in s or re.search(r"(^|[/_.-])val($|[/_.-])", s) or "dev" in path.name.lower():
        return "val"
    if re.search(r"(^|[/_.-])test($|[/_.-])", s):
        return "test"
    return "unknown"


def data_files(root: Path) -> Iterator[Path]:
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".parquet", ".jsonl", ".json"} and not p.name.startswith("."):
            yield p


def dataset_dir(raw_root: Path, dataset: str) -> Path | None:
    aliases = {norm_key(a) for a in DATASETS[dataset].get("aliases", [dataset])}
    direct = raw_root / dataset
    if direct.exists():
        return direct
    matches = []
    for p in raw_root.rglob("*"):
        if not p.is_dir():
            continue
        name = norm_key(p.name)
        parent = norm_key(p.parent.name)
        if name in aliases or parent in aliases or any(a in name for a in aliases):
            matches.append(p)
    if not matches:
        return None
    dataful = [p for p in matches if any(data_files(p))]
    return sorted(dataful or matches, key=lambda x: (len(str(x)), str(x)))[0]


def rows_from(path: Path, batch_size: int = 2048) -> Iterator[dict[str, Any]]:
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as pq  # type: ignore
        except Exception as e:
            raise RuntimeError("Need pyarrow: pip install pyarrow") from e
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=batch_size):
            yield from batch.to_pylist()
        return
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if isinstance(obj, list):
        for r in obj:
            if isinstance(r, dict):
                yield r
    elif isinstance(obj, dict):
        for k in ["data", "examples", "annotations", "questions", "samples"]:
            if isinstance(obj.get(k), list):
                for r in obj[k]:
                    if isinstance(r, dict):
                        yield r
                return
        yield obj


def normalize_answer(x: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[,，]", "", x.lower().strip()))


def tok_count(x: str) -> int:
    return len(re.findall(r"\w+", x))


def is_number(x: str) -> bool:
    return bool(re.fullmatch(r"[$€£¥]?\s*-?\d+(\.\d+)?\s*(%|percent|m|million|b|billion|k|thousand)?", normalize_answer(x)))


def has(q: str, pat: str) -> bool:
    return re.search(pat, q.lower()) is not None


def canonical(dataset: str, split: str, file: Path, idx: int, row: dict[str, Any]) -> dict[str, Any] | None:
    q = compact(first(row, Q_FIELDS))
    ans_val = first(row, A_FIELDS)
    a = compact(ans_val)
    if not q or not a:
        cq, ca = conv_qa(row)
        q = q or cq
        a = a or ca
    if not q or not a:
        return None
    choices = as_list(first(row, C_FIELDS))
    raw_meta = {}
    for k in ["question_type", "answer_type", "semantic", "semantic_type", "category", "subject", "type", "task", "source", "id", "question_id", "image_id"]:
        v = first(row, [k])
        if v is not None:
            raw_meta[k] = safe_json(v)
    return {
        "_dataset": dataset,
        "_split": split,
        "_source_file": str(file),
        "_source_index": idx,
        "question": q,
        "answer": a,
        "answers": as_list(ans_val) or [a],
        "choices": choices,
        "rationale": compact(first(row, R_FIELDS)) or None,
        "image": img_ref(first(row, I_FIELDS)),
        "raw_metadata": raw_meta,
    }


def answer_type(s: dict[str, Any]) -> tuple[str, float, str]:
    a = normalize_answer(s["answer"])
    if s["choices"]:
        return "option", 0.95, "rule"
    if a in YES_NO:
        return "yes_no", 0.98, "rule"
    if is_number(a):
        return "number", 0.98, "rule"
    if s["_dataset"] in TEXT_SPAN_DATASETS:
        return "text_span", 0.85, "dataset_default+rule"
    if a in ATTRIBUTES:
        return "attribute", 0.90, "rule"
    if tok_count(a) <= 3:
        return "object", 0.70, "weak_rule"
    return "free_form", 0.65, "weak_rule"


def skill_type(s: dict[str, Any], cfg: dict[str, Any]) -> tuple[str, str | None, float, str]:
    q = s["question"].lower()
    meta = " ".join(compact(v).lower() for v in s["raw_metadata"].values())
    text = f"{q} {meta}"
    d = s["_dataset"]
    if d in {"chartqa", "chartqa_eval"} or has(text, r"\b(chart|graph|bar|line chart|pie chart|axis|trend|legend|x-axis|y-axis)\b"):
        sec = "comparison" if has(text, r"\b(compare|larger|smaller|higher|lower|highest|lowest|increase|decrease|difference|more|less)\b") else None
        return "chart_reasoning", sec, 0.90, "dataset_default+rule"
    if d == "docvqa" or has(text, r"\b(invoice|receipt|form|document|table|row|column|total|date|amount)\b"):
        return "document_reasoning", "table_reading" if has(text, r"\b(table|row|column|cell)\b") else "text_reading", 0.86, "dataset_default+rule"
    if d == "infographicvqa":
        return "document_reasoning", "chart_reasoning" if has(text, r"\b(chart|graph|bar|trend|axis)\b") else "text_reading", 0.82, "dataset_default+rule"
    if d == "ai2d" or has(text, r"\b(diagram|arrow|flow|part|component|process)\b"):
        return "diagram_reasoning", None, 0.86, "dataset_default+rule"
    if has(text, r"\b(how many|number of|count|total number)\b"):
        return "counting", None, 0.95, "rule"
    if has(text, r"\b(what color|which color|color is|what shape|which shape|what size|how big|material)\b"):
        return "attribute", None, 0.93, "rule"
    if has(text, r"\b(left of|right of|behind|in front of|next to|beside|on top of|under|below|above|holding|wearing|near)\b"):
        return "relation", None, 0.90, "rule"
    if has(text, r"\b(compare|larger|smaller|higher|lower|highest|lowest|more|less|same|different|difference)\b"):
        return "comparison", None, 0.88, "rule"
    if has(text, r"\b(say|says|read|written|word|text|letter|sign|label)\b"):
        return "text_reading", None, 0.88, "rule"
    if d in KNOWLEDGE_DATASETS or cfg["knowledge"]:
        return cfg.get("skill_hint", "knowledge_reasoning"), None, 0.80, "dataset_default"
    if has(text, r"\b(why|used for|purpose|cause|likely|infer|reason|because)\b"):
        return "knowledge_reasoning", None, 0.76, "weak_rule"
    if cfg.get("skill_hint"):
        return cfg["skill_hint"], None, 0.72, "dataset_default"
    return "recognition", None, 0.82, "rule"


def evidence_type(s: dict[str, Any], primary: str, secondary: str | None, cfg: dict[str, Any]) -> tuple[str, str | None, float, str]:
    q = s["question"].lower()
    d = s["_dataset"]
    if d in {"chartqa", "chartqa_eval"} or primary == "chart_reasoning":
        sec = "cross_region" if secondary == "comparison" or has(q, r"\b(trend|compare|highest|lowest|increase|decrease|difference)\b") else None
        return "chart_element", sec, 0.86, "dataset_default+rule"
    if d == "docvqa" or primary == "document_reasoning":
        if has(q, r"\b(table|row|column|cell|total|sum)\b"):
            return "table_cell", None, 0.82, "rule"
        if d == "infographicvqa":
            return "text_span", "cross_region", 0.76, "dataset_default+weak_rule"
        return "text_span", None, 0.82, "dataset_default+rule"
    if d == "ai2d" or primary == "diagram_reasoning":
        return "diagram_region", "cross_region" if has(q, r"\b(process|flow|path|between|relationship|cause)\b") else None, 0.80, "dataset_default+rule"
    if cfg["knowledge"] or primary in {"knowledge_reasoning", "medical_reasoning", "remote_sensing_reasoning"}:
        return "image_plus_knowledge", None, 0.78, "dataset_default+rule"
    if primary in {"counting", "relation", "comparison"}:
        return "multi_region", None, 0.82, "rule"
    if primary in {"recognition", "attribute"}:
        return "single_region", None, 0.84, "rule"
    if primary == "text_reading":
        return "text_span", None, 0.82, "rule"
    return "unknown", None, 0.35, "fallback"


def label(s: dict[str, Any]) -> dict[str, Any]:
    d = s["_dataset"]
    cfg = DATASETS[d]
    at, ac, asrc = answer_type(s)
    sp, ss, sc, ssrc = skill_type(s, cfg)
    ep, es, ec, esrc = evidence_type(s, sp, ss, cfg)
    protocol = "multiple_choice" if s["choices"] else ("answer_with_rationale" if s["rationale"] else ("free_form_answer" if tok_count(s["answer"]) > 12 else "short_answer"))
    pconf = 0.95 if s["choices"] else (0.90 if s["rationale"] or protocol == "short_answer" else 0.72)
    k = bool(cfg["knowledge"] or sp == "knowledge_reasoning" or has(s["question"], r"\b(why|used for|purpose|cause|likely|infer|reason)\b"))
    kconf = 0.85 if cfg["knowledge"] else (0.72 if k else 0.82)
    conf = {
        "visual_substrate": 1.0,
        "skill_type": sc,
        "evidence_type": ec,
        "answer_type": ac,
        "protocol_type": pconf,
        "requires_external_knowledge": kconf,
    }
    raw = "|".join([d, s["_split"], s["_source_file"], str(s["_source_index"]), s["question"], s["answer"]])
    return {
        "id": f"{d}_{s['_split']}_{hashlib.sha1(raw.encode()).hexdigest()[:16]}",
        "dataset": d,
        "regime": cfg["regime"],
        "split": s["_split"],
        "source_file": s["_source_file"],
        "source_index": s["_source_index"],
        "image": s["image"],
        "question": s["question"],
        "answer": s["answer"],
        "answers": s["answers"],
        "choices": s["choices"] or None,
        "rationale": s["rationale"],
        "visual_substrate": cfg["visual"],
        "skill_type_primary": sp,
        "skill_type_secondary": ss,
        "evidence_type_primary": ep,
        "evidence_type_secondary": es,
        "answer_type": at,
        "protocol_type": protocol,
        "requires_external_knowledge": k,
        "question_length": tok_count(s["question"]),
        "answer_length": tok_count(s["answer"]),
        "normalized_answer": normalize_answer(s["answer"]),
        "label_source": {
            "visual_substrate": "dataset_default",
            "skill_type": ssrc,
            "evidence_type": esrc,
            "answer_type": asrc,
            "protocol_type": "rule",
            "requires_external_knowledge": "dataset_default+rule",
        },
        "label_confidence": conf,
        "overall_label_confidence": min(conf.values()),
        "raw_metadata": s["raw_metadata"],
    }


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def cmd_inventory(args: argparse.Namespace) -> int:
    out = args.output_root / "metadata" / "dataset_inventory.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for d in args.datasets:
        root = dataset_dir(args.raw_root, d)
        if root is None:
            records.append({"dataset": d, "status": "missing_dir"})
            continue
        files = list(data_files(root))
        if args.max_files_per_dataset:
            files = files[: args.max_files_per_dataset]
        if not files:
            records.append({"dataset": d, "dataset_dir": str(root), "status": "no_data_files"})
            continue
        for fp in files:
            split = infer_split(fp)
            num, cols, fq, fa = 0, set(), "", ""
            try:
                for row in rows_from(fp):
                    if num == 0:
                        cols = set(row.keys())
                        c = canonical(d, split, fp, num, row)
                        if c:
                            fq, fa = c["question"][:120], c["answer"][:120]
                    num += 1
            except Exception as e:
                records.append({"dataset": d, "dataset_dir": str(root), "file": str(fp), "split": split, "status": "read_error", "error": repr(e)})
                continue
            records.append({"dataset": d, "dataset_dir": str(root), "file": str(fp), "split": split, "num_rows": num, "columns": "|".join(sorted(cols)), "first_question": fq, "first_answer": fa, "status": "ok"})
    with out.open("w", encoding="utf-8", newline="") as f:
        fields = sorted({k for r in records for k in r})
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)
    print(f"Wrote inventory: {out}")
    return 0


def iter_labeled(d: str, raw_root: Path, max_samples: int | None) -> Iterator[dict[str, Any]]:
    root = dataset_dir(raw_root, d)
    if root is None:
        print(f"[warn] missing dataset dir: {d}", file=sys.stderr)
        return
    n, skipped = 0, 0
    for fp in data_files(root):
        split = infer_split(fp)
        for i, row in enumerate(rows_from(fp)):
            c = canonical(d, split, fp, i, row)
            if c is None:
                skipped += 1
                continue
            yield label(c)
            n += 1
            if max_samples and n >= max_samples:
                print(f"[info] {d}: reached max_samples={max_samples}, skipped={skipped}", file=sys.stderr)
                return
    print(f"[info] {d}: labeled={n}, skipped={skipped}", file=sys.stderr)


def llm_prompt(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": r["id"],
        "dataset": r["dataset"],
        "visual_substrate": r["visual_substrate"],
        "question": r["question"],
        "answer": r["answer"],
        "current_labels": {
            "skill_type_primary": r["skill_type_primary"],
            "skill_type_secondary": r["skill_type_secondary"],
            "evidence_type_primary": r["evidence_type_primary"],
            "evidence_type_secondary": r["evidence_type_secondary"],
            "requires_external_knowledge": r["requires_external_knowledge"],
        },
        "instruction": "Return JSON labels for skill_type_primary, skill_type_secondary, evidence_type_primary, evidence_type_secondary, requires_external_knowledge, confidence. Use question/answer/dataset only.",
    }


def write_stats(meta: Path, out_dir: Path, threshold: float, review_n: int, seed: int) -> None:
    rng = random.Random(seed)
    stats: Counter[tuple[str, str, str, str]] = Counter()
    split_counts: Counter[tuple[str, str]] = Counter()
    review_pool: dict[str, list[dict[str, Any]]] = defaultdict(list)
    review_seen: Counter[str] = Counter()
    low_path = out_dir / "low_confidence_samples.jsonl"
    prompt_path = out_dir / "llm_review_prompts.jsonl"
    low_count = 0
    with meta.open("r", encoding="utf-8") as f, low_path.open("w", encoding="utf-8") as low, prompt_path.open("w", encoding="utf-8") as prm:
        for line in f:
            r = json.loads(line)
            d, sp = r["dataset"], r["split"]
            split_counts[(d, sp)] += 1
            fields = {
                "visual_substrate": r.get("visual_substrate"),
                "skill_type_primary": r.get("skill_type_primary"),
                "skill_type_secondary": r.get("skill_type_secondary"),
                "evidence_type_primary": r.get("evidence_type_primary"),
                "evidence_type_secondary": r.get("evidence_type_secondary"),
                "answer_type": r.get("answer_type"),
                "protocol_type": r.get("protocol_type"),
                "requires_external_knowledge": str(r.get("requires_external_knowledge")),
            }
            for k, v in fields.items():
                if v:
                    stats[(d, sp, k, str(v))] += 1
            if float(r.get("overall_label_confidence", 1.0)) < threshold:
                low.write(json.dumps(r, ensure_ascii=False) + "\n")
                prm.write(json.dumps(llm_prompt(r), ensure_ascii=False) + "\n")
                low_count += 1
            review_seen[d] += 1
            seen = review_seen[d]
            if len(review_pool[d]) < review_n:
                review_pool[d].append(r)
            else:
                j = rng.randint(1, seen)
                if j <= review_n:
                    review_pool[d][j - 1] = r

    totals: Counter[tuple[str, str, str]] = Counter()
    for (d, sp, field, _), c in stats.items():
        totals[(d, sp, field)] += c
    stats_path = out_dir / "dataset_label_stats.csv"
    with stats_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dataset", "split", "field", "label", "count", "ratio"])
        w.writeheader()
        for (d, sp, field, lab), c in sorted(stats.items()):
            t = totals[(d, sp, field)]
            w.writerow({"dataset": d, "split": sp, "field": field, "label": lab, "count": c, "ratio": round(c / t, 6) if t else 0})
    counts_path = out_dir / "dataset_split_counts.csv"
    with counts_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dataset", "split", "count"])
        w.writeheader()
        for (d, sp), c in sorted(split_counts.items()):
            w.writerow({"dataset": d, "split": sp, "count": c})
    review_path = out_dir / "human_review_samples.jsonl"
    write_jsonl(review_path, [r for rows in review_pool.values() for r in rows])
    print(f"Wrote stats: {stats_path}")
    print(f"Wrote split counts: {counts_path}")
    print(f"Wrote low-confidence samples: {low_path} ({low_count})")
    print(f"Wrote human review samples: {review_path}")
    print(f"Wrote LLM review prompts: {prompt_path}")


def cmd_build(args: argparse.Namespace) -> int:
    out_dir = args.output_root / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = out_dir / "sample_metadata.jsonl"
    empty = []
    with meta.open("w", encoding="utf-8") as out:
        for d in args.datasets:
            print(f"[build] {d}", file=sys.stderr)
            n = 0
            try:
                for r in iter_labeled(d, args.raw_root, args.max_samples_per_dataset):
                    out.write(json.dumps(r, ensure_ascii=False) + "\n")
                    n += 1
            except Exception as e:
                print(f"[error] {d}: {e}", file=sys.stderr)
                if args.fail_on_empty:
                    raise
            if n == 0:
                empty.append(d)
                print(f"[warn] no samples written for {d}", file=sys.stderr)
    print(f"Wrote metadata: {meta}")
    if empty and args.fail_on_empty:
        return 2
    write_stats(meta, out_dir, args.low_confidence_threshold, args.review_per_dataset, args.seed)
    return 0


def js(a: Counter[str], b: Counter[str]) -> float:
    labels = sorted(set(a) | set(b))
    sa, sb = sum(a.values()), sum(b.values())
    if not sa or not sb:
        return 0.0
    pa, pb = [a[x] / sa for x in labels], [b[x] / sb for x in labels]
    pm = [(x + y) / 2 for x, y in zip(pa, pb)]
    def kl(p: list[float], q: list[float]) -> float:
        return sum(x * math.log2(x / y) for x, y in zip(p, q) if x > 0 and y > 0)
    return 0.5 * kl(pa, pm) + 0.5 * kl(pb, pm)


def jacc(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def dist(rows: list[dict[str, Any]], field: str) -> Counter[str]:
    return Counter(str(r[field]) for r in rows if r.get(field) not in {None, ""})


def top(c: Counter[str], k: int = 5) -> str:
    s = sum(c.values())
    return "" if not s else "; ".join(f"{lab}:{n/s:.2f}" for lab, n in c.most_common(k))


def load_transitions(path: Path | None) -> list[tuple[str, str, str]]:
    if path is None:
        return [
            ("T_nat_to_struct", "natural_photo_qa", "structured_visual_qa"),
            ("T_nat_to_knowledge", "natural_photo_qa", "knowledge_intensive_qa"),
            ("T_struct_to_medical", "structured_visual_qa", "expert_medical_qa"),
            ("T_struct_to_remote", "structured_visual_qa", "expert_remote_sensing_qa"),
        ]
    with path.open("r", encoding="utf-8", newline="") as f:
        return [(r["transition_id"], r["old_regime"], r["new_regime"]) for r in csv.DictReader(f)]


def cmd_gaps(args: argparse.Namespace) -> int:
    regimes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with args.metadata.open("r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if args.split != "all" and r.get("split") != args.split:
                continue
            if float(r.get("overall_label_confidence", 0.0)) < args.min_confidence:
                continue
            regimes[r["regime"]].append(r)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    field_map = {
        "visual_gap": "visual_substrate",
        "skill_gap": "skill_type_primary",
        "evidence_gap": "evidence_type_primary",
        "answer_distribution_gap": "answer_type",
    }
    fields = ["transition_id", "old_regime", "new_regime", "old_n", "new_n", "visual_gap", "skill_gap", "evidence_gap", "answer_distribution_gap", "answer_vocab_overlap", "metadata_overlap_score", "old_visual_top", "new_visual_top", "old_skill_top", "new_skill_top", "old_evidence_top", "new_evidence_top", "old_answer_type_top", "new_answer_type_top"]
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for tid, old, new in load_transitions(args.transitions):
            old_rows, new_rows = regimes.get(old, []), regimes.get(new, [])
            gaps, tops, sims = {}, {}, []
            for g, field in field_map.items():
                od, nd = dist(old_rows, field), dist(new_rows, field)
                val = js(od, nd)
                gaps[g] = val
                sims.append(1.0 - val)
                tops[f"old_{field}"], tops[f"new_{field}"] = top(od), top(nd)
            ov = {r.get("normalized_answer", "") for r in old_rows if r.get("normalized_answer")}
            nv = {r.get("normalized_answer", "") for r in new_rows if r.get("normalized_answer")}
            ans_overlap = jacc(ov, nv)
            sims.append(ans_overlap)
            w.writerow({
                "transition_id": tid,
                "old_regime": old,
                "new_regime": new,
                "old_n": len(old_rows),
                "new_n": len(new_rows),
                "visual_gap": round(gaps["visual_gap"], 6),
                "skill_gap": round(gaps["skill_gap"], 6),
                "evidence_gap": round(gaps["evidence_gap"], 6),
                "answer_distribution_gap": round(gaps["answer_distribution_gap"], 6),
                "answer_vocab_overlap": round(ans_overlap, 6),
                "metadata_overlap_score": round(sum(sims) / len(sims), 6),
                "old_visual_top": tops["old_visual_substrate"],
                "new_visual_top": tops["new_visual_substrate"],
                "old_skill_top": tops["old_skill_type_primary"],
                "new_skill_top": tops["new_skill_type_primary"],
                "old_evidence_top": tops["old_evidence_type_primary"],
                "new_evidence_top": tops["new_evidence_type_primary"],
                "old_answer_type_top": tops["old_answer_type"],
                "new_answer_type_top": tops["new_answer_type"],
            })
    print(f"Wrote transition gaps: {args.output}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CoIN Factor-1 metadata tool.")
    sub = p.add_subparsers(dest="cmd", required=True)
    common_datasets = list(DATASETS)

    inv = sub.add_parser("inventory")
    inv.add_argument("--raw-root", type=Path, default=Path("./cl_dataset/coin"))
    inv.add_argument("--output-root", type=Path, default=Path("./cl_dataset/coin_factor1_meta"))
    inv.add_argument("--datasets", nargs="+", default=common_datasets)
    inv.add_argument("--max-files-per-dataset", type=int, default=None)

    b = sub.add_parser("build")
    b.add_argument("--raw-root", type=Path, default=Path("./cl_dataset/coin"))
    b.add_argument("--output-root", type=Path, default=Path("./cl_dataset/coin_factor1_meta"))
    b.add_argument("--datasets", nargs="+", default=common_datasets)
    b.add_argument("--max-samples-per-dataset", type=int, default=None)
    b.add_argument("--review-per-dataset", type=int, default=200)
    b.add_argument("--low-confidence-threshold", type=float, default=0.70)
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--fail-on-empty", action="store_true")

    g = sub.add_parser("gaps")
    g.add_argument("--metadata", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/sample_metadata.jsonl"))
    g.add_argument("--output", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/transition_gap_table.csv"))
    g.add_argument("--transitions", type=Path, default=None)
    g.add_argument("--min-confidence", type=float, default=0.70)
    g.add_argument("--split", default="train")
    return p


def main() -> int:
    args = parser().parse_args()
    if hasattr(args, "raw_root"):
        args.raw_root = args.raw_root.expanduser().resolve()
    if hasattr(args, "output_root"):
        args.output_root = args.output_root.expanduser().resolve()
    if args.cmd == "inventory":
        return cmd_inventory(args)
    if args.cmd == "build":
        return cmd_build(args)
    if args.cmd == "gaps":
        return cmd_gaps(args)
    raise SystemExit(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
