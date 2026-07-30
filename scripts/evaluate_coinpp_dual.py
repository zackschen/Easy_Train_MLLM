#!/usr/bin/env python3
"""Evaluate every CoIN++ prediction with two independent scoring tracks.

Track 1, ``standard``, uses the source benchmark's registered metric whenever
the required annotations are available. Otherwise it directly compares the
normalized prediction and reference answer.

Track 2, ``llm_judge``, sends every prediction to an OpenAI-compatible judge.
The judge follows the original CoIN 0-10 scoring convention. Its raw score and
the normalized [0, 1] score are both retained.
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
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import evaluate_coinpp_predictions as standard_eval


JUDGE_PROMPT_VERSION = "coinpp-all-results-judge-0-10-v1"


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
    parser.add_argument("--project-root", type=Path, default=Path("."))
    parser.add_argument(
        "--metadata-jsonl",
        action="append",
        type=Path,
        default=[],
        help="Metadata JSONL containing full references/choices; repeatable.",
    )
    parser.add_argument("--annotation-cache", type=Path, default=None)
    parser.add_argument("--scored-dir-name", default="predictions_dual")
    parser.add_argument("--metrics-file-name", default="metrics_dual_all.json")
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
    parser.add_argument("--judge-workers", type=int, default=4)
    parser.add_argument("--judge-timeout", type=float, default=180.0)
    parser.add_argument("--judge-retries", type=int, default=3)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--skip-completed", action="store_true")
    parser.add_argument(
        "--allow-missing-reference",
        action="store_true",
        help="Keep samples without a reference as unscored in the standard track.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if not args.result_root and not args.prediction_dir:
        raise SystemExit("Provide at least one --result-root or --prediction-dir.")
    if not args.judge_model:
        raise SystemExit(
            "The dual protocol judges every prediction. Set JUDGE_MODEL or pass --judge-model."
        )
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be positive.")
    if args.judge_batch_size <= 0:
        raise SystemExit("--judge-batch-size must be positive.")
    if args.judge_workers <= 0:
        raise SystemExit("--judge-workers must be positive.")
    if args.judge_retries < 0:
        raise SystemExit("--judge-retries cannot be negative.")


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


def parse_score(value: Any) -> float | None:
    if isinstance(value, bool):
        return 10.0 if value else 0.0
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        score = float(value)
    elif isinstance(value, str):
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", value.strip())
        if not match:
            return None
        score = float(match.group(0))
    else:
        return None
    if not math.isfinite(score):
        return None
    return min(10.0, max(0.0, score))


def normalize_judge_results(
    payload: Any,
    expected_keys: list[str] | None = None,
) -> dict[str, dict[str, Any]]:
    expected_keys = expected_keys or []
    if isinstance(payload, dict):
        candidates = None
        for field in ("results", "judgments", "labels", "scores"):
            value = payload.get(field)
            if isinstance(value, list):
                candidates = value
                break
        if candidates is None and any(
            field in payload
            for field in (
                "key",
                "id",
                "score",
                "rating",
                "correctness_score",
                "correct",
            )
        ):
            candidates = [payload]
    else:
        candidates = payload
    if not isinstance(candidates, list) and len(expected_keys) == 1:
        raw_score = parse_score(candidates)
        if raw_score is not None:
            return {
                expected_keys[0]: {
                    "raw_score_0_10": raw_score,
                    "score": raw_score / 10.0,
                    "reason": "",
                }
            }
    if not isinstance(candidates, list):
        raise ValueError(f"Judge JSON must contain a result list, got {type(candidates).__name__}")

    output: dict[str, dict[str, Any]] = {}
    parsed_without_valid_key: list[dict[str, Any]] = []
    for item in candidates:
        if isinstance(item, dict):
            key = str(item.get("key") or item.get("id") or item.get("sample_id") or "")
            raw_score = parse_score(
                item.get("score", item.get("rating", item.get("correctness_score")))
            )
            if raw_score is None and "correct" in item:
                raw_score = parse_score(item["correct"])
            reason = str(item.get("reason") or item.get("explanation") or "").strip()
        else:
            key = ""
            raw_score = parse_score(item)
            reason = ""
        if raw_score is None:
            continue
        result = {
            "raw_score_0_10": raw_score,
            "score": raw_score / 10.0,
            "reason": reason,
        }
        if key:
            output[key] = result
        else:
            parsed_without_valid_key.append(result)

    # With one input there is no ambiguity: accept a valid score even when the
    # model omitted, shortened, or rewrote the transport key.
    if len(expected_keys) == 1:
        expected_key = expected_keys[0]
        if expected_key in output:
            return {expected_key: output[expected_key]}
        parsed_results = [*output.values(), *parsed_without_valid_key]
        if len(parsed_results) == 1:
            return {expected_key: parsed_results[0]}
    return output


def judge_request(
    samples: list[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    endpoint = args.judge_base_url.rstrip("/") + "/chat/completions"
    transport_to_internal: dict[str, str] = {}
    compact_samples = []
    for index, sample in enumerate(samples):
        transport_key = f"s{index}"
        transport_to_internal[transport_key] = sample["judge_key"]
        compact_samples.append(
            {
                "key": transport_key,
                "question": sample["row"].get("question", ""),
                "ground_truth_answers": sample["references"],
                "assistant_answer": sample["row"].get("pred", ""),
            }
        )
    system_prompt = (
        "You are a precise evaluator for visual question answering. The image is not provided; "
        "evaluate the assistant answer only against the question and ground-truth answer(s), as in "
        "the original CoIN answer-quality evaluation. Give an accuracy score from 0 to 10: 10 means "
        "fully correct or semantically equivalent; 7-9 means essentially correct with a minor issue; "
        "4-6 means partially correct or incomplete; 1-3 means mostly incorrect but slightly relevant; "
        "0 means incorrect, contradictory, or no answer. Ignore harmless capitalization, punctuation, "
        "units formatting, and concise explanatory text. Return JSON only using "
        "{\"results\":[{\"key\":\"...\",\"score\":0,\"reason\":\"brief reason\"}]}. "
        "Return exactly one result for every key."
    )
    body = {
        "model": args.judge_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "Evaluate every sample:\n"
                + json.dumps(compact_samples, ensure_ascii=False),
            },
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
    message = response_body["choices"][0]["message"]
    content = message.get("content") or message.get("reasoning_content") or ""
    try:
        payload = parse_json_payload(content)
        returned = normalize_judge_results(
            payload,
            expected_keys=list(transport_to_internal),
        )
    except ValueError:
        if len(samples) != 1:
            raise
        scalar_content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE,
        )
        raw_score = parse_score(scalar_content)
        if raw_score is None:
            raise
        returned = {
            "s0": {
                "raw_score_0_10": raw_score,
                "score": raw_score / 10.0,
                "reason": "Recovered from a singleton scalar response.",
            }
        }
    return {
        transport_to_internal[key]: result
        for key, result in returned.items()
        if key in transport_to_internal
    }


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
                f"Judge omitted {len(pending)} keys: "
                f"{[item['judge_key'][:12] for item in pending[:5]]}"
            )
        except (OSError, KeyError, ValueError, urllib.error.HTTPError) as error:
            last_error = error
        if attempt < args.judge_retries:
            time.sleep(min(8.0, 1.5 * (2**attempt)))

    # Local inference servers occasionally omit one item from a batch.
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


def read_judge_cache(path: Path | None) -> dict[str, dict[str, Any]]:
    if path is None or not path.is_file():
        return {}
    cache: dict[str, dict[str, Any]] = {}
    for row in standard_eval.read_jsonl(path):
        key = str(row.get("judge_key") or "")
        if (
            key
            and row.get("prompt_version") == JUDGE_PROMPT_VERSION
            and row.get("model")
        ):
            cache[key] = row
    return cache


def cache_row(key: str, result: dict[str, Any], model: str) -> dict[str, Any]:
    return {
        "judge_key": key,
        "model": model,
        "prompt_version": JUDGE_PROMPT_VERSION,
        **result,
    }


def run_all_judgments(
    items: Iterable[dict[str, Any]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    unique = {item["judge_key"]: item for item in items}
    cache = read_judge_cache(args.judge_cache)
    results = {key: cache[key] for key in unique.keys() & cache.keys()}
    pending = [item for key, item in unique.items() if key not in cache]
    batches = [
        pending[start : start + args.judge_batch_size]
        for start in range(0, len(pending), args.judge_batch_size)
    ]
    print(
        f"[judge-all] rows={len(unique)} cached={len(results)} pending={len(pending)} "
        f"batches={len(batches)} workers={args.judge_workers}",
        flush=True,
    )
    if not batches:
        return results

    cache_handle = None
    if args.judge_cache:
        args.judge_cache.parent.mkdir(parents=True, exist_ok=True)
        cache_handle = args.judge_cache.open("a", encoding="utf-8")

    completed = 0
    batch_iter = iter(batches)
    try:
        with ThreadPoolExecutor(max_workers=args.judge_workers) as executor:
            in_flight: dict[Future[dict[str, dict[str, Any]]], list[dict[str, Any]]] = {}

            def submit_next() -> bool:
                try:
                    batch = next(batch_iter)
                except StopIteration:
                    return False
                in_flight[executor.submit(request_with_retries, batch, args)] = batch
                return True

            for _ in range(min(len(batches), args.judge_workers * 2)):
                submit_next()

            while in_flight:
                done, _ = wait(in_flight, return_when=FIRST_COMPLETED)
                for future in done:
                    batch = in_flight.pop(future)
                    returned = future.result()
                    for key, result in returned.items():
                        row = cache_row(key, result, str(args.judge_model))
                        results[key] = row
                        if cache_handle is not None:
                            cache_handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                    if cache_handle is not None:
                        cache_handle.flush()
                    completed += len(batch)
                    if completed == len(pending) or completed % max(
                        args.judge_batch_size, 1000
                    ) < len(batch):
                        print(
                            f"[judge-all] completed={completed}/{len(pending)} "
                            f"cached={len(unique) - len(pending)}",
                            flush=True,
                        )
                    submit_next()
    finally:
        if cache_handle is not None:
            cache_handle.close()

    missing = unique.keys() - results.keys()
    if missing:
        raise RuntimeError(f"Judge results are missing {len(missing)} unique predictions")
    return results


def standard_score(
    row: dict[str, Any],
    annotation: dict[str, Any] | None,
    allow_missing_reference: bool,
) -> tuple[dict[str, Any], list[str]]:
    evaluation, fallback_reason = standard_eval.score_native(row, annotation)
    references, reference_source = standard_eval.references_for_row(row, annotation)
    dataset = str((row.get("metadata") or {}).get("dataset") or "").lower()
    if evaluation is not None:
        evaluation = dict(evaluation)
        evaluation["score"] = evaluation["primary_score"]
        return evaluation, references

    if not references:
        if not allow_missing_reference:
            raise RuntimeError(
                f"No reference answer for id={row.get('id')} dataset={dataset or 'unknown'}"
            )
        return {
            "protocol": "unscored",
            "metric": "unscored",
            "score": None,
            "primary_score": None,
            "official_metric": False,
            "dataset": dataset,
            "references": [],
            "reference_source": reference_source,
            "fallback_reason": fallback_reason,
        }, references

    score = standard_eval.normalized_accuracy(str(row.get("pred", "")), references)
    return {
        "protocol": "direct_comparison",
        "metric": "normalized_answer_match",
        "score": score,
        "primary_score": score,
        "official_metric": False,
        "dataset": dataset,
        "references": references,
        "reference_source": reference_source,
        "fallback_reason": fallback_reason,
    }, references


def prepare_rows(
    jobs: list[standard_eval.PredictionJob],
    annotations: dict[str, dict[str, Any]],
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    prepared: list[dict[str, Any]] = []
    judge_items: list[dict[str, Any]] = []
    for job in jobs:
        output_rows = []
        for row in job.rows:
            annotation = annotations.get(str(row.get("id", "")))
            standard, references = standard_score(
                row,
                annotation,
                args.allow_missing_reference,
            )
            key = judge_key(row, references, str(args.judge_model))
            output_row = dict(row)
            output_row["evaluation"] = {
                "standard": standard,
                "llm_judge": {
                    "protocol": "llm_judge_all",
                    "metric": "coin_0_10_accuracy",
                    "score": None,
                    "raw_score_0_10": None,
                    "judge_key": key,
                    "judge_model": args.judge_model,
                    "judge_prompt_version": JUDGE_PROMPT_VERSION,
                    "reference_source": standard.get("reference_source"),
                    "references": references,
                },
            }
            output_rows.append(output_row)
            judge_items.append(
                {
                    "judge_key": key,
                    "row": row,
                    "references": references,
                }
            )
        prepared.append({"job": job, "rows": output_rows})

    judge_results = run_all_judgments(judge_items, args)
    for item in prepared:
        for row in item["rows"]:
            judge = row["evaluation"]["llm_judge"]
            result = judge_results[judge["judge_key"]]
            judge.update(
                {
                    "score": float(result["score"]),
                    "raw_score_0_10": float(result["raw_score_0_10"]),
                    "reason": result.get("reason", ""),
                    "judge_status": "cache_or_api",
                }
            )
    return prepared


def pearson(left: list[float], right: list[float]) -> float | None:
    if len(left) != len(right) or len(left) < 2:
        return None
    left_mean = mean(left)
    right_mean = mean(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_scale = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_scale = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    if left_scale == 0 or right_scale == 0:
        return None
    return numerator / (left_scale * right_scale)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    standard_values = [
        float(row["evaluation"]["standard"]["score"])
        for row in rows
        if row["evaluation"]["standard"].get("score") is not None
    ]
    judge_values = [
        float(row["evaluation"]["llm_judge"]["score"])
        for row in rows
        if row["evaluation"]["llm_judge"].get("score") is not None
    ]
    paired = [
        (
            float(row["evaluation"]["standard"]["score"]),
            float(row["evaluation"]["llm_judge"]["score"]),
        )
        for row in rows
        if row["evaluation"]["standard"].get("score") is not None
        and row["evaluation"]["llm_judge"].get("score") is not None
    ]
    confusion = Counter()
    for standard_value, judge_value in paired:
        standard_correct = standard_value >= 0.5
        judge_correct = judge_value >= 0.5
        if standard_correct and judge_correct:
            confusion["both_correct"] += 1
        elif not standard_correct and not judge_correct:
            confusion["both_incorrect"] += 1
        elif standard_correct:
            confusion["standard_only_correct"] += 1
        else:
            confusion["judge_only_correct"] += 1

    agreement = (
        (confusion["both_correct"] + confusion["both_incorrect"]) / len(paired)
        if paired
        else None
    )
    standard_protocols = Counter(
        row["evaluation"]["standard"]["protocol"] for row in rows
    )
    return {
        "num_samples": len(rows),
        "num_standard_scored": len(standard_values),
        "num_judged": len(judge_values),
        "standard_score": mean(standard_values) if standard_values else None,
        "llm_judge_score": mean(judge_values) if judge_values else None,
        "standard_coverage": len(standard_values) / len(rows) if rows else 0.0,
        "judge_coverage": len(judge_values) / len(rows) if rows else 0.0,
        "official_metric_coverage": (
            standard_protocols["official_metric"] / len(rows) if rows else 0.0
        ),
        "direct_comparison_coverage": (
            standard_protocols["direct_comparison"] / len(rows) if rows else 0.0
        ),
        "standard_judge_agreement_at_0_5": agreement,
        "standard_judge_pearson": pearson(
            [pair[0] for pair in paired],
            [pair[1] for pair in paired],
        ),
        "standard_judge_mean_absolute_gap": (
            mean(abs(left - right) for left, right in paired) if paired else None
        ),
        "agreement_confusion_at_0_5": dict(confusion),
        "standard_protocol_counts": dict(standard_protocols),
        "standard_metric_counts": dict(
            Counter(row["evaluation"]["standard"]["metric"] for row in rows)
        ),
    }


def summarize_job(
    job: standard_eval.PredictionJob,
    rows: list[dict[str, Any]],
    scored_path: Path,
) -> dict[str, Any]:
    by_dataset: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        dataset = str((row.get("metadata") or {}).get("dataset") or "unknown")
        by_dataset[dataset].append(row)
    per_dataset = {
        dataset: summarize_rows(dataset_rows)
        for dataset, dataset_rows in sorted(by_dataset.items())
    }
    overall = summarize_rows(rows)
    standard_dataset_scores = [
        value["standard_score"]
        for value in per_dataset.values()
        if value["standard_score"] is not None
    ]
    judge_dataset_scores = [
        value["llm_judge_score"]
        for value in per_dataset.values()
        if value["llm_judge_score"] is not None
    ]
    original = standard_eval.original_metric_lookup(job.stage_dir).get(job.task, {})
    stage = str(rows[0].get("stage") if rows else job.stage_dir.name)
    return {
        "stage": stage,
        "task": job.task,
        "eval_file": original.get("eval_file"),
        "predictions_file": str(job.prediction_path),
        "scored_predictions_file": str(scored_path),
        **overall,
        "standard_dataset_macro_score": (
            mean(standard_dataset_scores) if standard_dataset_scores else None
        ),
        "llm_judge_dataset_macro_score": (
            mean(judge_dataset_scores) if judge_dataset_scores else None
        ),
        "per_dataset": per_dataset,
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_outputs(
    prepared: list[dict[str, Any]],
    annotation_report: dict[str, Any],
    args: argparse.Namespace,
) -> None:
    stage_metrics: dict[Path, list[dict[str, Any]]] = defaultdict(list)
    result_manifests: dict[Path, dict[str, Any]] = {}

    for item in prepared:
        job: standard_eval.PredictionJob = item["job"]
        rows: list[dict[str, Any]] = item["rows"]
        scored_path = job.stage_dir / args.scored_dir_name / f"{job.task}.jsonl"
        standard_eval.write_jsonl(scored_path, rows)
        stage_metrics[job.stage_dir].append(summarize_job(job, rows, scored_path))

        manifest = result_manifests.setdefault(
            job.result_root,
            {
                "evaluation_protocol": "independent_standard_and_llm_judge",
                "standard_track": {
                    "registered_metric_first": True,
                    "fallback": "normalized_answer_match",
                },
                "llm_judge_track": {
                    "coverage": "all_predictions",
                    "model": args.judge_model,
                    "prompt_version": JUDGE_PROMPT_VERSION,
                    "raw_scale": "0_to_10",
                    "reported_scale": "0_to_1",
                    "image_provided_to_judge": False,
                },
                "annotation_report": annotation_report,
                "stages": [],
            },
        )
        if str(job.stage_dir) not in manifest["stages"]:
            manifest["stages"].append(str(job.stage_dir))

    for stage_dir, metrics in stage_metrics.items():
        metrics.sort(key=lambda row: row["task"])
        path = stage_dir / args.metrics_file_name
        write_json(path, metrics)
        print(f"[write] {path}")

    for result_root, manifest in result_manifests.items():
        path = result_root / "dual_evaluation_manifest.json"
        write_json(path, manifest)
        print(f"[write] {path}")


def main() -> int:
    args = parse_args()
    validate_args(args)
    args.project_root = args.project_root.resolve()
    args.result_root = [path.resolve() for path in args.result_root]
    args.prediction_dir = [path.resolve() for path in args.prediction_dir]
    args.metadata_jsonl = [path.resolve() for path in args.metadata_jsonl]
    if args.annotation_cache:
        args.annotation_cache = args.annotation_cache.resolve()
    if args.judge_cache:
        args.judge_cache = args.judge_cache.resolve()

    jobs = standard_eval.discover_jobs(args)
    needed_ids = {
        str(row.get("id", ""))
        for job in jobs
        for row in job.rows
        if row.get("id") is not None
    }
    print(
        f"CoIN++ dual evaluation: jobs={len(jobs)} "
        f"predictions={sum(len(job.rows) for job in jobs)} unique_ids={len(needed_ids)}"
    )
    annotations, annotation_report = standard_eval.load_annotations(args, needed_ids)
    print(
        f"Annotation recovery: resolved={annotation_report['resolved_ids']}/"
        f"{annotation_report['needed_ids']} missing={annotation_report['missing_ids']}"
    )
    prepared = prepare_rows(jobs, annotations, args)
    write_outputs(prepared, annotation_report, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
