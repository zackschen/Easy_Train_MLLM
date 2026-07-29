#!/usr/bin/env python3
"""Rescore CoIN++ predictions with dataset-native metrics and an LLM fallback.

The Factor-1 evaluation splits mix samples from several source benchmarks.  A
single string-matching rule is therefore not a valid evaluator.  This script
routes every prediction by ``metadata.dataset``:

* VQAv2/TextVQA/OK-VQA: official VQA soft accuracy (10 references required)
* DocVQA/InfographicVQA: ANLS
* ChartQA: relaxed accuracy
* multiple-choice datasets: answer accuracy with option extraction
* remaining objective QA datasets: benchmark-style normalized accuracy
* unsupported or annotation-incomplete samples: OpenAI-compatible LLM judge

It operates on saved JSONL predictions, so model inference does not need to be
rerun.  Existing prediction and metric files are never overwritten.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

from ETrain.Eval.LLaVA.CoIN.m4c_evaluator import EvalAIAnswerProcessor


VQA_DATASETS = {"vqav2", "textvqa", "okvqa"}
ANLS_DATASETS = {"docvqa", "infographicvqa"}
CHARTQA_DATASETS = {"chartqa", "chartqa_eval", "tqa"}
MULTIPLE_CHOICE_DATASETS = {"ai2d", "aokvqa", "iconqa", "mmmu", "visual7w"}
COUNT_DATASETS = {"tallyqa"}
NORMALIZED_ACCURACY_DATASETS = {
    "dvqa",
    "geometry3k",
    "gqa",
    "pathvqa",
    "slake",
    "vqarad",
}
KNOWN_DATASETS = (
    VQA_DATASETS
    | ANLS_DATASETS
    | CHARTQA_DATASETS
    | MULTIPLE_CHOICE_DATASETS
    | COUNT_DATASETS
    | NORMALIZED_ACCURACY_DATASETS
)
MEDICAL_DATASETS = {"pathvqa", "slake", "vqarad"}
JUDGE_PROMPT_VERSION = "coinpp-correctness-v1"
ANSWER_PROCESSOR = EvalAIAnswerProcessor()


@dataclass
class PredictionJob:
    result_root: Path
    stage_dir: Path
    task: str
    prediction_path: Path
    rows: list[dict[str, Any]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--result-root",
        action="append",
        type=Path,
        default=[],
        help="Evaluation root containing <stage>/predictions/*.jsonl; repeatable.",
    )
    parser.add_argument(
        "--prediction-dir",
        action="append",
        type=Path,
        default=[],
        help="A single predictions directory; repeatable.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path("."),
        help="Used to auto-discover the retained metadata JSONL files.",
    )
    parser.add_argument(
        "--metadata-jsonl",
        action="append",
        type=Path,
        default=[],
        help="Metadata JSONL containing id/answers/choices; repeatable.",
    )
    parser.add_argument(
        "--annotation-cache",
        type=Path,
        default=None,
        help="Compact reusable annotation index. It is created or extended when supplied.",
    )
    parser.add_argument("--scored-dir-name", default="predictions_official")
    parser.add_argument("--metrics-file-name", default="metrics_official_all.json")
    parser.add_argument(
        "--judge-mode",
        choices=["fallback", "off"],
        default="fallback",
        help="Use the judge only when no faithful native score is available, or leave such rows unscored.",
    )
    parser.add_argument(
        "--judge-base-url",
        default=os.environ.get("JUDGE_BASE_URL")
        or os.environ.get("OPENAI_BASE_URL")
        or "http://127.0.0.1:8001/v1",
    )
    parser.add_argument(
        "--judge-api-key",
        default=os.environ.get("JUDGE_API_KEY")
        or os.environ.get("OPENAI_API_KEY")
        or "EMPTY",
    )
    parser.add_argument("--judge-model", default=os.environ.get("JUDGE_MODEL"))
    parser.add_argument("--judge-cache", type=Path, default=None)
    parser.add_argument("--judge-batch-size", type=int, default=8)
    parser.add_argument("--judge-timeout", type=float, default=180.0)
    parser.add_argument("--judge-retries", type=int, default=3)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-completed", action="store_true")
    parser.add_argument(
        "--allow-unscored",
        action="store_true",
        help="Do not fail when judge-mode=off leaves fallback samples unscored.",
    )
    return parser.parse_args()


def read_jsonl(path: Path, limit: int | None = None) -> list[dict[str, Any]]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            rows.append(json.loads(line))
            if limit is not None and len(rows) >= limit:
                break
    return rows


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def discover_jobs(args: argparse.Namespace) -> list[PredictionJob]:
    jobs: list[PredictionJob] = []
    seen_paths: set[Path] = set()

    for result_root in args.result_root:
        root = result_root.resolve()
        for path in sorted(root.glob("*/predictions/*.jsonl")):
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            if args.skip_completed and (path.parent.parent / args.metrics_file_name).is_file():
                continue
            seen_paths.add(resolved)
            jobs.append(
                PredictionJob(
                    result_root=root,
                    stage_dir=path.parent.parent,
                    task=path.stem,
                    prediction_path=resolved,
                    rows=read_jsonl(resolved, args.limit),
                )
            )

    for prediction_dir in args.prediction_dir:
        directory = prediction_dir.resolve()
        for path in sorted(directory.glob("*.jsonl")):
            resolved = path.resolve()
            if resolved in seen_paths:
                continue
            if args.skip_completed and (directory.parent / args.metrics_file_name).is_file():
                continue
            seen_paths.add(resolved)
            jobs.append(
                PredictionJob(
                    result_root=directory.parent.parent,
                    stage_dir=directory.parent,
                    task=path.stem,
                    prediction_path=resolved,
                    rows=read_jsonl(resolved, args.limit),
                )
            )

    if not jobs:
        supplied = [str(path) for path in [*args.result_root, *args.prediction_dir]]
        raise SystemExit(f"No prediction JSONL files found under: {supplied}")
    return jobs


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def answer_text(value: Any) -> str:
    if isinstance(value, dict):
        for key in ("answer", "text", "value", "label"):
            if value.get(key) is not None:
                return str(value[key]).strip()
    return str(value).strip()


def clean_answers(value: Any) -> list[str]:
    answers = [answer_text(item) for item in ensure_list(value)]
    return [answer for answer in answers if answer]


def compact_annotation(row: dict[str, Any], source: str) -> dict[str, Any]:
    return {
        "id": str(row.get("id", "")),
        "dataset": row.get("dataset") or (row.get("metadata") or {}).get("dataset"),
        "answers": clean_answers(row.get("answers")),
        "choices": row.get("choices") or (row.get("metadata") or {}).get("choices"),
        "raw_metadata": row.get("raw_metadata") or (row.get("metadata") or {}).get("raw_metadata"),
        "annotation_source": source,
    }


def load_annotation_file(
    path: Path,
    needed_ids: set[str],
    annotations: dict[str, dict[str, Any]],
) -> tuple[int, int]:
    matched = 0
    malformed = 0
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                malformed += 1
                continue
            sample_id = str(row.get("id", ""))
            if sample_id not in needed_ids:
                continue
            candidate = compact_annotation(row, str(path))
            current = annotations.get(sample_id)
            if current is None or len(candidate["answers"]) > len(current.get("answers") or []):
                annotations[sample_id] = candidate
            matched += 1
    return matched, malformed


def auto_metadata_paths(project_root: Path) -> list[Path]:
    pattern = "cl_dataset/coin_factor1_targeted_pool*/metadata/sample_metadata.jsonl"
    return sorted(path.resolve() for path in project_root.glob(pattern))


def load_annotations(
    args: argparse.Namespace,
    needed_ids: set[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    annotations: dict[str, dict[str, Any]] = {}
    report: dict[str, Any] = {"sources": [], "needed_ids": len(needed_ids)}

    if args.annotation_cache and args.annotation_cache.is_file():
        matched, malformed = load_annotation_file(args.annotation_cache, needed_ids, annotations)
        report["sources"].append(
            {
                "path": str(args.annotation_cache),
                "kind": "cache",
                "matched_rows": matched,
                "malformed_rows": malformed,
            }
        )

    missing = needed_ids - annotations.keys()
    paths = [path.resolve() for path in args.metadata_jsonl]
    if not paths:
        paths = auto_metadata_paths(args.project_root.resolve())
    for path in paths:
        if not missing:
            break
        if not path.is_file():
            raise FileNotFoundError(f"Metadata JSONL does not exist: {path}")
        matched, malformed = load_annotation_file(path, set(missing), annotations)
        report["sources"].append(
            {
                "path": str(path),
                "kind": "metadata",
                "matched_rows": matched,
                "malformed_rows": malformed,
            }
        )
        missing = needed_ids - annotations.keys()

    if args.annotation_cache:
        cache_rows = [annotations[key] for key in sorted(annotations)]
        write_jsonl(args.annotation_cache.resolve(), cache_rows)

    report["resolved_ids"] = len(annotations)
    report["missing_ids"] = len(needed_ids - annotations.keys())
    return annotations, report


def vqa_normalize(value: Any) -> str:
    return ANSWER_PROCESSOR(str(value))


def vqa_soft_accuracy(prediction: str, references: list[str]) -> float:
    if len(references) != 10:
        raise ValueError(f"VQA accuracy requires exactly 10 references, got {len(references)}")
    prediction = vqa_normalize(prediction)
    answers = [vqa_normalize(answer) for answer in references]
    per_annotator = []
    for index in range(len(answers)):
        matches = sum(
            other_answer == prediction
            for other_index, other_answer in enumerate(answers)
            if other_index != index
        )
        per_annotator.append(min(1.0, matches / 3.0))
    return mean(per_annotator)


def levenshtein_distance(left: str, right: str) -> int:
    if len(left) < len(right):
        left, right = right, left
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, 1):
        current = [left_index]
        for right_index, right_char in enumerate(right, 1):
            current.append(
                min(
                    current[-1] + 1,
                    previous[right_index] + 1,
                    previous[right_index - 1] + (left_char != right_char),
                )
            )
        previous = current
    return previous[-1]


def anls_single(prediction: str, reference: str) -> float:
    prediction = str(prediction).lower().strip()
    reference = str(reference).lower().strip()
    if not prediction and not reference:
        return 1.0
    denominator = max(len(prediction), len(reference))
    if denominator == 0:
        return 0.0
    similarity = 1.0 - levenshtein_distance(prediction, reference) / denominator
    return similarity if similarity >= 0.5 else 0.0


def anls_score(prediction: str, references: list[str]) -> float:
    return max((anls_single(prediction, reference) for reference in references), default=0.0)


_NUMBER_WRAPPERS = re.compile(
    r"(?i)^\s*(?:the\s+answer\s+is|answer\s*:|approximately|about)\s*"
)
_CURRENCY = re.compile(r"[$€£¥]")


def parse_decimal(value: Any) -> Decimal | None:
    text = str(value).strip()
    text = _NUMBER_WRAPPERS.sub("", text)
    text = _CURRENCY.sub("", text)
    text = text.replace(",", "").strip()
    percent = text.endswith("%")
    if percent:
        text = text[:-1].strip()
    text = re.sub(r"(?i)\s*(?:dollars?|usd|people|items?|years?|units?)\s*$", "", text)
    if not re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", text):
        return None
    try:
        number = Decimal(text)
    except InvalidOperation:
        return None
    return number / Decimal(100) if percent else number


def chartqa_relaxed_accuracy(prediction: str, references: list[str]) -> float:
    prediction_number = parse_decimal(prediction)
    for reference in references:
        reference_number = parse_decimal(reference)
        if prediction_number is not None and reference_number is not None:
            if reference_number == 0:
                if prediction_number == 0:
                    return 1.0
            elif abs(prediction_number - reference_number) / abs(reference_number) <= Decimal("0.05"):
                return 1.0
        elif str(prediction).strip().lower() == str(reference).strip().lower():
            return 1.0
    return 0.0


def normalized_accuracy(prediction: str, references: list[str]) -> float:
    normalized_prediction = vqa_normalize(prediction)
    return float(any(normalized_prediction == vqa_normalize(reference) for reference in references))


def count_accuracy(prediction: str, references: list[str]) -> float:
    prediction_number = parse_decimal(vqa_normalize(prediction))
    for reference in references:
        reference_number = parse_decimal(vqa_normalize(reference))
        if prediction_number is not None and reference_number is not None:
            if prediction_number == reference_number:
                return 1.0
        elif vqa_normalize(prediction) == vqa_normalize(reference):
            return 1.0
    return 0.0


def token_f1(prediction: str, references: list[str]) -> float:
    prediction_tokens = vqa_normalize(prediction).split()
    if not prediction_tokens:
        return float(any(not vqa_normalize(reference) for reference in references))
    best = 0.0
    prediction_counts = Counter(prediction_tokens)
    for reference in references:
        reference_tokens = vqa_normalize(reference).split()
        if not reference_tokens:
            continue
        overlap = sum((prediction_counts & Counter(reference_tokens)).values())
        if overlap == 0:
            continue
        precision = overlap / len(prediction_tokens)
        recall = overlap / len(reference_tokens)
        best = max(best, 2 * precision * recall / (precision + recall))
    return best


def normalize_choices(value: Any, dataset: str) -> list[str]:
    choices = [answer_text(item) for item in ensure_list(value) if answer_text(item)]
    if dataset == "iconqa" and len(choices) == 1 and "," in choices[0]:
        choices = [item.strip() for item in choices[0].split(",") if item.strip()]
    return choices


def choices_from_question(question: str) -> list[str]:
    if "Choices:" not in question:
        return []
    choice_text = question.split("Choices:", 1)[1]
    choice_text = re.split(r"(?i)\bAnswer\s+with\b", choice_text, maxsplit=1)[0]
    matches = re.findall(
        r"(?:^|\s)([A-J])\.\s*(.*?)(?=(?:\s+[A-J]\.\s)|$)",
        choice_text,
        flags=re.DOTALL,
    )
    return [text.strip() for _, text in matches]


def option_letter(value: str, option_count: int) -> int | None:
    text = str(value).strip()
    patterns = [
        r"(?i)^\s*(?:answer\s*[:\-]?\s*)?\(?([A-J])\)?(?:[\s.:\-]|$)",
        r"(?i)\b(?:option|choice|answer)\s*(?:is|:)?\s*\(?([A-J])\)?\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            index = ord(match.group(1).upper()) - ord("A")
            return index if 0 <= index < option_count else None
    return None


def option_index(value: str, choices: list[str]) -> int | None:
    normalized = vqa_normalize(value)
    for index, choice in enumerate(choices):
        if normalized == vqa_normalize(choice):
            return index
    return option_letter(value, len(choices))


def multiple_choice_accuracy(
    prediction: str,
    references: list[str],
    choices: list[str],
) -> float:
    if normalized_accuracy(prediction, references):
        return 1.0
    if not choices:
        return 0.0
    prediction_index = option_index(prediction, choices)
    if prediction_index is None:
        return 0.0
    return float(any(option_index(reference, choices) == prediction_index for reference in references))


def references_for_row(
    row: dict[str, Any],
    annotation: dict[str, Any] | None,
) -> tuple[list[str], str]:
    if annotation and annotation.get("answers"):
        return clean_answers(annotation["answers"]), "metadata_jsonl"
    gt = str(row.get("gt", "")).strip()
    return ([gt] if gt else []), "prediction_gt"


def choices_for_row(
    row: dict[str, Any],
    annotation: dict[str, Any] | None,
    dataset: str,
) -> list[str]:
    metadata = row.get("metadata") or {}
    value = metadata.get("choices")
    if not value and annotation:
        value = annotation.get("choices")
    choices = normalize_choices(value, dataset)
    if not choices and dataset == "visual7w":
        choices = choices_from_question(str(row.get("question", "")))
    return choices


def score_native(
    row: dict[str, Any],
    annotation: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, str | None]:
    metadata = row.get("metadata") or {}
    dataset = str(metadata.get("dataset") or "").lower()
    prediction = str(row.get("pred", ""))
    references, reference_source = references_for_row(row, annotation)
    choices = choices_for_row(row, annotation, dataset)

    common = {
        "protocol": "official_metric",
        "dataset": dataset,
        "references": references,
        "reference_source": reference_source,
        "official_metric": True,
    }
    if dataset in VQA_DATASETS:
        if len(references) != 10:
            return None, f"{dataset}_requires_10_human_answers"
        return {
            **common,
            "metric": "vqa_soft_accuracy",
            "primary_score": vqa_soft_accuracy(prediction, references),
        }, None
    if dataset in ANLS_DATASETS:
        if not references:
            return None, f"{dataset}_has_no_reference_answer"
        return {
            **common,
            "metric": "anls",
            "primary_score": anls_score(prediction, references),
            "annotation_fidelity": (
                "full_references" if reference_source == "metadata_jsonl" else "single_reference"
            ),
        }, None
    if dataset in CHARTQA_DATASETS:
        if not references:
            return None, f"{dataset}_has_no_reference_answer"
        return {
            **common,
            "metric": "chartqa_relaxed_accuracy",
            "primary_score": chartqa_relaxed_accuracy(prediction, references),
        }, None
    if dataset in MULTIPLE_CHOICE_DATASETS:
        if not references:
            return None, f"{dataset}_has_no_reference_answer"
        return {
            **common,
            "metric": "multiple_choice_accuracy",
            "primary_score": multiple_choice_accuracy(prediction, references, choices),
            "choices": choices,
            "annotation_fidelity": "choices_available" if choices else "answer_only",
        }, None
    if dataset in COUNT_DATASETS:
        return {
            **common,
            "metric": "count_accuracy",
            "primary_score": count_accuracy(prediction, references),
        }, None
    if dataset in NORMALIZED_ACCURACY_DATASETS:
        result = {
            **common,
            "metric": "normalized_accuracy",
            "primary_score": normalized_accuracy(prediction, references),
        }
        if dataset in MEDICAL_DATASETS:
            result["token_f1"] = token_f1(prediction, references)
        return result, None
    if dataset:
        return None, f"no_registered_metric_for_{dataset}"
    return None, "missing_dataset_label"


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def judge_key(row: dict[str, Any], references: list[str], model: str) -> str:
    payload = {
        "prompt_version": JUDGE_PROMPT_VERSION,
        "model": model,
        "id": row.get("id"),
        "question": row.get("question"),
        "references": references,
        "prediction": row.get("pred"),
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def parse_json_payload(content: str) -> Any:
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE)
    content = content.strip()
    content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```$", "", content)
    decoder = json.JSONDecoder()
    for index, char in enumerate(content):
        if char not in "[{":
            continue
        try:
            value, _ = decoder.raw_decode(content[index:])
            return value
        except json.JSONDecodeError:
            continue
    raise ValueError(f"Judge response does not contain valid JSON: {content[:500]}")


def bool_value(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "correct", "1"}:
            return True
        if normalized in {"false", "no", "incorrect", "0"}:
            return False
    return None


def normalize_judge_results(payload: Any) -> dict[str, dict[str, Any]]:
    if isinstance(payload, dict):
        candidates = payload.get("results") or payload.get("labels") or payload.get("judgments")
        if candidates is None and ("key" in payload or "id" in payload):
            candidates = [payload]
    else:
        candidates = payload
    if not isinstance(candidates, list):
        raise ValueError(f"Judge JSON must contain a result list, got: {type(candidates).__name__}")

    output = {}
    for item in candidates:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or item.get("id") or "")
        correct = bool_value(item.get("correct"))
        if correct is None:
            correct = bool_value(item.get("score"))
        if not key or correct is None:
            continue
        output[key] = {
            "correct": correct,
            "score": float(correct),
            "reason": str(item.get("reason") or item.get("explanation") or "").strip(),
        }
    return output


def judge_request(
    samples: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    endpoint = args.judge_base_url.rstrip("/") + "/chat/completions"
    compact_samples = [
        {
            "key": sample["judge_key"],
            "question": sample["row"].get("question", ""),
            "reference_answers": sample["references"],
            "candidate_answer": sample["row"].get("pred", ""),
        }
        for sample in samples
    ]
    system_prompt = (
        "You are a strict visual-question-answering evaluator. The image is not available, so judge "
        "only whether the candidate answer is semantically equivalent to or fully supported by the "
        "reference answer(s) for the given question. Ignore capitalization, punctuation, harmless "
        "formatting, and concise explanatory wording. Reject contradictions, wrong entities or "
        "numbers, unsupported alternatives, and answers that are only partially correct. Return JSON "
        "only, with this schema: {\"results\":[{\"key\":\"...\",\"correct\":true,"
        "\"reason\":\"brief reason\"}]}. Return exactly one result for every key."
    )
    user_prompt = "Evaluate these samples:\n" + json.dumps(compact_samples, ensure_ascii=False)
    body = {
        "model": args.judge_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0,
        "max_tokens": max(512, 160 * len(samples)),
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {args.judge_api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=args.judge_timeout) as response:
        response_body = json.loads(response.read().decode("utf-8"))
    content = response_body["choices"][0]["message"]["content"]
    return normalize_judge_results(parse_json_payload(content))


def request_with_retries(
    samples: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    expected = {sample["judge_key"] for sample in samples}
    collected: dict[str, dict[str, Any]] = {}
    pending = list(samples)
    last_error: Exception | None = None

    for attempt in range(args.judge_retries + 1):
        if not pending:
            break
        try:
            returned = judge_request(pending, args)
            collected.update({key: value for key, value in returned.items() if key in expected})
            pending = [sample for sample in pending if sample["judge_key"] not in collected]
            if not pending:
                return collected
            last_error = RuntimeError(
                f"Judge omitted {len(pending)} keys: {[item['judge_key'][:12] for item in pending[:5]]}"
            )
        except (OSError, KeyError, ValueError, urllib.error.HTTPError) as error:
            last_error = error
        if attempt < args.judge_retries:
            time.sleep(min(8.0, 1.5 * (2**attempt)))

    # Batch omissions are common with local VLM servers. Recover each missing
    # item separately before failing the run.
    for sample in pending:
        singleton_error: Exception | None = None
        for attempt in range(args.judge_retries + 1):
            try:
                returned = judge_request([sample], args)
                if sample["judge_key"] in returned:
                    collected[sample["judge_key"]] = returned[sample["judge_key"]]
                    singleton_error = None
                    break
                singleton_error = RuntimeError("Judge omitted the singleton key")
            except (OSError, KeyError, ValueError, urllib.error.HTTPError) as error:
                singleton_error = error
            if attempt < args.judge_retries:
                time.sleep(min(8.0, 1.5 * (2**attempt)))
        if singleton_error is not None:
            last_error = singleton_error

    missing = expected - collected.keys()
    if missing:
        raise RuntimeError(
            f"LLM judge failed for {len(missing)} samples after retries; last error: {last_error}"
        )
    return collected


def load_judge_cache(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.is_file():
        return {}
    cache = {}
    for row in read_jsonl(path):
        key = str(row.get("judge_key") or "")
        if key:
            cache[key] = row
    return cache


def run_judge(
    fallback_items: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    if not fallback_items:
        return {}
    if args.judge_mode == "off":
        return {}
    if not args.judge_model:
        raise RuntimeError(
            f"{len(fallback_items)} samples require LLM judging, but no judge model was configured. "
            "Set JUDGE_MODEL or pass --judge-model."
        )

    cache = load_judge_cache(args.judge_cache)
    results: dict[str, dict[str, Any]] = {}
    pending = []
    for item in fallback_items:
        key = item["judge_key"]
        if key in cache:
            results[key] = cache[key]
        else:
            pending.append(item)

    new_cache_rows = []
    for start in range(0, len(pending), args.judge_batch_size):
        batch = pending[start : start + args.judge_batch_size]
        returned = request_with_retries(batch, args)
        for key, result in returned.items():
            cache_row = {
                "judge_key": key,
                "model": args.judge_model,
                "prompt_version": JUDGE_PROMPT_VERSION,
                **result,
            }
            results[key] = cache_row
            new_cache_rows.append(cache_row)
        print(
            f"[judge] completed {min(start + len(batch), len(pending))}/{len(pending)} "
            f"(cached={len(fallback_items) - len(pending)})",
            flush=True,
        )

    if args.judge_cache and new_cache_rows:
        path = args.judge_cache.resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            for row in new_cache_rows:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    return results


def prepare_scores(
    jobs: list[PredictionJob],
    annotations: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    fallback_items = []
    prepared = []
    for job in jobs:
        output_rows = []
        for row in job.rows:
            sample_id = str(row.get("id", ""))
            annotation = annotations.get(sample_id)
            evaluation, fallback_reason = score_native(row, annotation)
            if evaluation is None:
                references, reference_source = references_for_row(row, annotation)
                exact_shortcut = normalized_accuracy(str(row.get("pred", "")), references)
                if exact_shortcut:
                    evaluation = {
                        "protocol": "llm_judge",
                        "metric": "llm_judge_accuracy",
                        "primary_score": 1.0,
                        "official_metric": False,
                        "dataset": (row.get("metadata") or {}).get("dataset"),
                        "references": references,
                        "reference_source": reference_source,
                        "fallback_reason": fallback_reason,
                        "judge_status": "normalized_exact_shortcut",
                        "judge_model": args.judge_model,
                    }
                elif args.judge_mode == "off":
                    evaluation = {
                        "protocol": "unscored",
                        "metric": "unscored",
                        "primary_score": None,
                        "official_metric": False,
                        "dataset": (row.get("metadata") or {}).get("dataset"),
                        "references": references,
                        "reference_source": reference_source,
                        "fallback_reason": fallback_reason,
                    }
                else:
                    key = judge_key(row, references, str(args.judge_model))
                    evaluation = {
                        "protocol": "llm_judge",
                        "metric": "llm_judge_accuracy",
                        "primary_score": None,
                        "official_metric": False,
                        "dataset": (row.get("metadata") or {}).get("dataset"),
                        "references": references,
                        "reference_source": reference_source,
                        "fallback_reason": fallback_reason,
                        "judge_key": key,
                        "judge_model": args.judge_model,
                    }
                    fallback_items.append(
                        {
                            "judge_key": key,
                            "row": row,
                            "references": references,
                            "evaluation": evaluation,
                        }
                    )

            output_row = dict(row)
            output_row["evaluation"] = evaluation
            output_rows.append(output_row)
        prepared.append({"job": job, "rows": output_rows})

    judge_results = run_judge(fallback_items, args)
    for item in fallback_items:
        result = judge_results[item["judge_key"]]
        item["evaluation"].update(
            {
                "primary_score": float(result["score"]),
                "judge_status": "api",
                "judge_correct": bool(result["correct"]),
                "judge_reason": result.get("reason", ""),
                "judge_prompt_version": JUDGE_PROMPT_VERSION,
            }
        )
    return prepared


def summarize_dataset(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scored = [
        float(row["evaluation"]["primary_score"])
        for row in rows
        if row["evaluation"].get("primary_score") is not None
    ]
    official = [
        float(row["evaluation"]["primary_score"])
        for row in rows
        if row["evaluation"].get("protocol") == "official_metric"
        and row["evaluation"].get("primary_score") is not None
    ]
    judged = [
        float(row["evaluation"]["primary_score"])
        for row in rows
        if row["evaluation"].get("protocol") == "llm_judge"
        and row["evaluation"].get("primary_score") is not None
    ]
    token_f1_values = [
        float(row["evaluation"]["token_f1"])
        for row in rows
        if row["evaluation"].get("token_f1") is not None
    ]
    return {
        "num_samples": len(rows),
        "num_scored": len(scored),
        "primary_score": mean(scored) if scored else None,
        "official_score": mean(official) if official else None,
        "judge_score": mean(judged) if judged else None,
        "token_f1": mean(token_f1_values) if token_f1_values else None,
        "protocol_counts": dict(Counter(row["evaluation"]["protocol"] for row in rows)),
        "metric_counts": dict(Counter(row["evaluation"]["metric"] for row in rows)),
    }


def original_metric_lookup(stage_dir: Path) -> dict[str, dict[str, Any]]:
    path = stage_dir / "metrics_all.json"
    if not path.is_file():
        return {}
    try:
        return {str(row.get("task")): row for row in json.loads(path.read_text(encoding="utf-8"))}
    except (json.JSONDecodeError, TypeError):
        return {}


def summarize_job(job: PredictionJob, rows: list[dict[str, Any]], scored_path: Path) -> dict[str, Any]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        dataset = str((row.get("metadata") or {}).get("dataset") or "unknown")
        by_dataset[dataset].append(row)
    per_dataset = {
        dataset: summarize_dataset(dataset_rows)
        for dataset, dataset_rows in sorted(by_dataset.items())
    }
    overall = summarize_dataset(rows)
    dataset_scores = [
        values["primary_score"]
        for values in per_dataset.values()
        if values["primary_score"] is not None
    ]
    protocol_counts = Counter(row["evaluation"]["protocol"] for row in rows)
    metric_counts = Counter(row["evaluation"]["metric"] for row in rows)
    reference_counts = Counter(row["evaluation"].get("reference_source", "unknown") for row in rows)
    n = len(rows)

    original = original_metric_lookup(job.stage_dir).get(job.task, {})
    stage = str(rows[0].get("stage") if rows else job.stage_dir.name)
    return {
        "stage": stage,
        "task": job.task,
        "eval_file": original.get("eval_file"),
        "predictions_file": str(job.prediction_path),
        "scored_predictions_file": str(scored_path),
        "num_samples": n,
        "num_scored": overall["num_scored"],
        "primary_score": overall["primary_score"],
        "dataset_macro_score": mean(dataset_scores) if dataset_scores else None,
        "official_score": overall["official_score"],
        "judge_score": overall["judge_score"],
        "official_coverage": protocol_counts["official_metric"] / n if n else 0.0,
        "judge_coverage": protocol_counts["llm_judge"] / n if n else 0.0,
        "unscored_count": protocol_counts["unscored"],
        "protocol_counts": dict(protocol_counts),
        "metric_counts": dict(metric_counts),
        "reference_source_counts": dict(reference_counts),
        "per_dataset": per_dataset,
    }


def write_outputs(
    prepared: list[dict[str, Any]],
    annotation_report: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    stage_metrics: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    result_manifests: dict[Path, dict[str, Any]] = {}

    for item in prepared:
        job: PredictionJob = item["job"]
        rows: list[dict[str, Any]] = item["rows"]
        scored_path = job.stage_dir / args.scored_dir_name / f"{job.task}.jsonl"
        write_jsonl(scored_path, rows)
        metrics = summarize_job(job, rows, scored_path)
        stage_metrics[job.stage_dir].append(metrics)

        manifest = result_manifests.setdefault(
            job.result_root,
            {
                "scoring_protocol": "dataset_native_then_llm_judge",
                "judge_mode": args.judge_mode,
                "judge_model": args.judge_model,
                "known_dataset_routes": {
                    "vqa_soft_accuracy": sorted(VQA_DATASETS),
                    "anls": sorted(ANLS_DATASETS),
                    "chartqa_relaxed_accuracy": sorted(CHARTQA_DATASETS),
                    "multiple_choice_accuracy": sorted(MULTIPLE_CHOICE_DATASETS),
                    "count_accuracy": sorted(COUNT_DATASETS),
                    "normalized_accuracy": sorted(NORMALIZED_ACCURACY_DATASETS),
                },
                "annotation_report": annotation_report,
                "stages": [],
            },
        )
        if str(job.stage_dir) not in manifest["stages"]:
            manifest["stages"].append(str(job.stage_dir))

    total_unscored = 0
    for stage_dir, metrics in stage_metrics.items():
        metrics.sort(key=lambda row: row["task"])
        metrics_path = stage_dir / args.metrics_file_name
        metrics_path.write_text(
            json.dumps(metrics, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        total_unscored += sum(int(row["unscored_count"]) for row in metrics)
        print(f"[write] {metrics_path}")

    for result_root, manifest in result_manifests.items():
        manifest_path = result_root / "official_judge_evaluation_manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"[write] {manifest_path}")

    if total_unscored and not args.allow_unscored:
        raise RuntimeError(
            f"{total_unscored} predictions remain unscored. Configure the judge or pass "
            "--allow-unscored only for metric-pipeline debugging."
        )


def validate_args(args: argparse.Namespace) -> None:
    if not args.result_root and not args.prediction_dir:
        raise SystemExit("Provide at least one --result-root or --prediction-dir.")
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be positive.")
    if args.judge_batch_size <= 0:
        raise SystemExit("--judge-batch-size must be positive.")
    if args.judge_retries < 0:
        raise SystemExit("--judge-retries cannot be negative.")


def main() -> int:
    args = parse_args()
    validate_args(args)
    args.project_root = args.project_root.resolve()
    if args.annotation_cache:
        args.annotation_cache = args.annotation_cache.resolve()
    if args.judge_cache:
        args.judge_cache = args.judge_cache.resolve()

    jobs = discover_jobs(args)
    needed_ids = {
        str(row.get("id", ""))
        for job in jobs
        for row in job.rows
        if row.get("id") is not None
    }
    print(
        f"CoIN++ official/Judge rescoring: jobs={len(jobs)} "
        f"predictions={sum(len(job.rows) for job in jobs)} unique_ids={len(needed_ids)}"
    )
    annotations, annotation_report = load_annotations(args, needed_ids)
    print(
        f"Annotation recovery: resolved={annotation_report['resolved_ids']}/"
        f"{annotation_report['needed_ids']} missing={annotation_report['missing_ids']}"
    )
    prepared = prepare_scores(jobs, annotations, args)
    write_outputs(prepared, annotation_report, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
