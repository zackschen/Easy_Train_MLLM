#!/usr/bin/env python3
"""Select targeted unlabeled Factor-1 candidates for another VLM metadata pass.

This script is intentionally heuristic. It does not assign final labels; it only
selects likely candidates for under-supported factor categories. Final labels are
still produced by factor1_coin_meta.py refine-metadata.
"""
from __future__ import annotations

import argparse
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

FACTOR_FIELDS = {
    "visual_substrate": "visual_substrate",
    "skill_requirement": "skill_type_primary",
    "evidence_complexity": "evidence_complexity",
}

TARGET_CATEGORIES = {
    "visual_substrate": ["natural_photo", "medical", "document", "infographic", "diagram", "chart"],
    "skill_requirement": [
        "recognition",
        "counting",
        "medical_reasoning",
        "knowledge_reasoning",
        "chart_reasoning",
        "document_reasoning",
        "text_reading",
        "diagram_reasoning",
        "relation",
        "attribute",
    ],
    "evidence_complexity": ["single_evidence", "multi_evidence", "cross_region_or_multihop", "cross_context"],
}

DATASET_VISUAL = {
    "vqav2": "natural_photo",
    "gqa": "natural_photo",
    "visual7w": "natural_photo",
    "tallyqa": "natural_photo",
    "okvqa": "natural_photo",
    "aokvqa": "natural_photo",
    "docvqa": "document",
    "infographicvqa": "infographic",
    "ai2d": "diagram",
    "scienceqa": "diagram",
    "chartqa": "chart",
    "chartqa_eval": "chart",
    "slake": "medical",
    "vqarad": "medical",
    "pathvqa": "medical",
    "textvqa": "natural_photo",
    "stvqa": "natural_photo",
    "dvqa": "chart",
    "plotqa": "chart",
    "figureqa": "chart",
    "iconqa": "diagram",
}

DATASET_SKILL = {
    "tallyqa": "counting",
    "chartqa": "chart_reasoning",
    "chartqa_eval": "chart_reasoning",
    "docvqa": "document_reasoning",
    "infographicvqa": "document_reasoning",
    "ai2d": "diagram_reasoning",
    "scienceqa": "diagram_reasoning",
    "mmmu": "knowledge_reasoning",
    "okvqa": "knowledge_reasoning",
    "aokvqa": "knowledge_reasoning",
    "slake": "medical_reasoning",
    "vqarad": "medical_reasoning",
    "pathvqa": "medical_reasoning",
    "textvqa": "text_reading",
    "stvqa": "text_reading",
    "dvqa": "chart_reasoning",
    "plotqa": "chart_reasoning",
    "figureqa": "chart_reasoning",
    "iconqa": "diagram_reasoning",
}

ATTRIBUTE_RE = re.compile(r"\b(color|colour|shape|size|material|pattern|texture|type of|kind of|what color|what colour|how big|how large)\b")
RELATION_RE = re.compile(r"\b(left|right|above|below|under|over|behind|front|next to|beside|between|near|closest|farthest|where is|to the left|to the right|on top of|spatial)\b")
COUNT_RE = re.compile(r"\b(how many|number of|count|total number|amount of)\b")
TEXT_RE = re.compile(r"\b(read|text|word|words|letter|letters|sign|says|written|printed|label|title|caption|name on|number on|date|address)\b")
CHART_RE = re.compile(r"\b(chart|graph|bar|line|axis|axes|legend|plot|trend|value|percentage|percent|x-axis|y-axis)\b")
DOCUMENT_RE = re.compile(r"\b(document|page|form|table|paragraph|section|header|footer|invoice|receipt|statement|field|cell|row|column)\b")
DIAGRAM_RE = re.compile(r"\b(diagram|figure|arrow|flow|process|part|labeled|labelled|structure|component|cycle|system)\b")
COMPARE_RE = re.compile(r"\b(more|less|greater|smaller|larger|higher|lower|highest|lowest|maximum|minimum|same|different|difference|compare|comparison|which .* more|which .* less)\b")
MULTI_RE = re.compile(r"\b(and|both|between|from .* to|total|sum|difference|compare|after|before|if|based on .* and|according to .* and)\b")
KNOWLEDGE_RE = re.compile(r"\b(why|what is the purpose|used for|cause|because|likely|infer|imply|mean|known as)\b")


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return " ".join(compact(v) for v in value)
    return str(value).strip()


def lower_text(row: dict[str, Any]) -> str:
    parts = [compact(row.get("question")), compact(row.get("answer"))]
    raw = row.get("raw_metadata")
    if isinstance(raw, dict):
        for key in ("question", "question_type", "types", "semantic", "semanticStr", "fullAnswer"):
            if key in raw:
                parts.append(compact(raw.get(key)))
    return " ".join(parts).lower()


def row_id(row: dict[str, Any]) -> str:
    return compact(row.get("id"))


def row_meta(row: dict[str, Any], key: str) -> str:
    md = row.get("metadata") or {}
    return compact(md.get(key) or row.get(key))


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def iter_json_array(path: Path) -> Iterable[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array: {path}")
    yield from data


def add_existing_ids_from_train(path: Path, ids: set[str]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in iter_json_array(path):
        sid = row_id(row)
        if sid:
            ids.add(sid)
        md = row.get("metadata") or {}
        for factor, field in FACTOR_FIELDS.items():
            value = compact(md.get(field) or row.get(field))
            if value:
                counts[(factor, value)] += 1
    return counts


def add_existing_ids_from_metadata(path: Path, ids: set[str]) -> Counter[tuple[str, str]]:
    counts: Counter[tuple[str, str]] = Counter()
    for row in iter_jsonl(path):
        sid = row_id(row)
        if sid:
            ids.add(sid)
        for factor, field in FACTOR_FIELDS.items():
            value = compact(row.get(field))
            if value:
                counts[(factor, value)] += 1
    return counts


def score_visual(row: dict[str, Any], category: str) -> int:
    dataset = row_meta(row, "dataset")
    visual = row_meta(row, "visual_substrate")
    score = 0
    if DATASET_VISUAL.get(dataset) == category:
        score = max(score, 8)
    if visual == category:
        score = max(score, 5)
    return score


def score_skill(row: dict[str, Any], category: str) -> int:
    dataset = row_meta(row, "dataset")
    skill = row_meta(row, "skill_type_primary")
    text = lower_text(row)
    score = 0
    if DATASET_SKILL.get(dataset) == category:
        score = max(score, 7)
    if skill == category:
        score = max(score, 4)
    if category == "attribute" and ATTRIBUTE_RE.search(text):
        score = max(score, 8)
    elif category == "relation" and RELATION_RE.search(text):
        score = max(score, 8)
    elif category == "counting" and COUNT_RE.search(text):
        score = max(score, 8)
    elif category == "text_reading" and TEXT_RE.search(text):
        score = max(score, 8)
    elif category == "chart_reasoning" and CHART_RE.search(text):
        score = max(score, 8)
    elif category == "document_reasoning" and DOCUMENT_RE.search(text):
        score = max(score, 8)
    elif category == "diagram_reasoning" and DIAGRAM_RE.search(text):
        score = max(score, 8)
    elif category == "knowledge_reasoning" and KNOWLEDGE_RE.search(text):
        score = max(score, 6)
    elif category == "medical_reasoning" and dataset in {"slake", "vqarad", "pathvqa"}:
        score = max(score, 8)
    elif category == "recognition" and not any(rx.search(text) for rx in [ATTRIBUTE_RE, RELATION_RE, COUNT_RE, TEXT_RE, CHART_RE, DOCUMENT_RE, DIAGRAM_RE, COMPARE_RE]):
        score = max(score, 3)
    return score


def score_evidence(row: dict[str, Any], category: str) -> int:
    evidence = row_meta(row, "evidence_complexity")
    scope = row_meta(row, "evidence_scope")
    skill = row_meta(row, "skill_type_primary")
    dataset = row_meta(row, "dataset")
    text = lower_text(row)
    score = 0
    if evidence == category:
        score = max(score, 5)
    if category == "cross_region_or_multihop":
        if scope in {"cross_region", "cross_page", "multi_region", "image_plus_knowledge"}:
            score = max(score, 6)
        if skill in {"relation", "comparison", "counting", "chart_reasoning", "document_reasoning", "diagram_reasoning"}:
            score = max(score, 5)
        if RELATION_RE.search(text) or COMPARE_RE.search(text) or MULTI_RE.search(text):
            score = max(score, 8)
        if dataset in {"chartqa", "chartqa_eval", "docvqa", "infographicvqa", "ai2d"}:
            score = max(score, 4)
    elif category == "cross_context":
        if scope == "image_plus_knowledge" or dataset in {"okvqa", "aokvqa", "scienceqa", "mmmu", "slake", "vqarad", "pathvqa"}:
            score = max(score, 7)
        if KNOWLEDGE_RE.search(text):
            score = max(score, 7)
    elif category == "multi_evidence":
        if scope == "multi_region" or COUNT_RE.search(text) or COMPARE_RE.search(text):
            score = max(score, 6)
    elif category == "single_evidence":
        if evidence == "single_evidence" or scope in {"single_region", "global_image"}:
            score = max(score, 4)
    return score


def score(row: dict[str, Any], factor: str, category: str) -> int:
    if factor == "visual_substrate":
        return score_visual(row, category)
    if factor == "skill_requirement":
        return score_skill(row, category)
    if factor == "evidence_complexity":
        return score_evidence(row, category)
    return 0


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-metadata", type=Path, required=True, help="Unrefined metadata JSONL built from the raw datasets.")
    p.add_argument("--base-train-json", type=Path, action="append", default=[], help="Existing LLaVA train JSON to count and exclude. Repeatable.")
    p.add_argument("--exclude-metadata", type=Path, action="append", default=[], help="Existing metadata JSONL to exclude/count. Repeatable.")
    p.add_argument("--output", type=Path, required=True, help="Selected candidate metadata JSONL for refine-metadata.")
    p.add_argument("--report", type=Path, default=None)
    p.add_argument("--target-count", type=int, default=12000, help="Desired support per target category after relabeling.")
    p.add_argument("--candidate-multiplier", type=float, default=2.0, help="How many weak candidates to select per current deficit.")
    p.add_argument("--min-candidates-per-deficit", type=int, default=500)
    p.add_argument("--max-candidates-per-category", type=int, default=16000)
    p.add_argument("--max-total-candidates", type=int, default=60000)
    p.add_argument("--min-score", type=int, default=4)
    p.add_argument("--keep-all-if-no-deficit", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    existing_ids: set[str] = set()
    current_counts: Counter[tuple[str, str]] = Counter()
    for path in args.base_train_json:
        current_counts.update(add_existing_ids_from_train(path, existing_ids))
    for path in args.exclude_metadata:
        current_counts.update(add_existing_ids_from_metadata(path, existing_ids))

    deficits: dict[str, dict[str, int]] = {}
    for factor, categories in TARGET_CATEGORIES.items():
        deficits[factor] = {}
        for category in categories:
            current = current_counts[(factor, category)]
            deficits[factor][category] = max(0, args.target_count - current)

    candidate_rows: list[dict[str, Any]] = []
    seen_candidate_ids: set[str] = set()
    for row in iter_jsonl(args.candidate_metadata):
        sid = row_id(row)
        if not sid or sid in existing_ids or sid in seen_candidate_ids:
            continue
        seen_candidate_ids.add(sid)
        candidate_rows.append(row)

    selected: dict[str, dict[str, list[tuple[int, dict[str, Any]]]]] = defaultdict(lambda: defaultdict(list))
    selected_ids: set[str] = set()
    selected_reasons: dict[str, list[str]] = defaultdict(list)

    target_pairs: list[tuple[int, str, str, int]] = []
    for factor, cats in deficits.items():
        for category, deficit in cats.items():
            if deficit > 0 or args.keep_all_if_no_deficit:
                target_pairs.append((deficit, factor, category, deficit))
    target_pairs.sort(reverse=True)

    for _, factor, category, deficit in target_pairs:
        if deficit <= 0:
            continue
        quota = max(args.min_candidates_per_deficit, math.ceil(deficit * args.candidate_multiplier))
        quota = min(quota, args.max_candidates_per_category)
        scored: list[tuple[int, dict[str, Any]]] = []
        for row in candidate_rows:
            sid = row_id(row)
            if sid in selected_ids:
                continue
            s = score(row, factor, category)
            if s >= args.min_score:
                scored.append((s, row))
        scored.sort(key=lambda item: (item[0], row_meta(item[1], "dataset"), row_id(item[1])), reverse=True)
        take = scored[:quota]
        for s, row in take:
            sid = row_id(row)
            selected_ids.add(sid)
            selected[factor][category].append((s, row))
            selected_reasons[sid].append(f"{factor}:{category}:score={s}")
        if len(selected_ids) >= args.max_total_candidates:
            break

    # Backfill by the best aggregate score if the category-wise pass hit the max too early.
    if len(selected_ids) < args.max_total_candidates:
        aggregate: list[tuple[int, dict[str, Any]]] = []
        for row in candidate_rows:
            sid = row_id(row)
            if sid in selected_ids:
                continue
            best = 0
            best_label = None
            for factor, cats in deficits.items():
                for category, deficit in cats.items():
                    if deficit <= 0:
                        continue
                    s = score(row, factor, category)
                    if s > best:
                        best = s
                        best_label = f"{factor}:{category}:score={s}"
            if best >= args.min_score and best_label:
                aggregate.append((best, row))
        aggregate.sort(key=lambda item: (item[0], row_meta(item[1], "dataset"), row_id(item[1])), reverse=True)
        for s, row in aggregate[: max(0, args.max_total_candidates - len(selected_ids))]:
            sid = row_id(row)
            selected_ids.add(sid)
            selected_reasons[sid].append(f"aggregate:score={s}")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    selected_rows = [row for row in candidate_rows if row_id(row) in selected_ids]
    with args.output.open("w", encoding="utf-8") as f:
        for row in selected_rows:
            out = dict(row)
            out["targeted_relabel_reasons"] = selected_reasons[row_id(row)]
            f.write(json.dumps(out, ensure_ascii=False) + "\n")

    selected_by_dataset = Counter(row_meta(r, "dataset") for r in selected_rows)
    selected_by_rule_factor = {
        factor: Counter(row_meta(r, field) for r in selected_rows)
        for factor, field in FACTOR_FIELDS.items()
    }
    selected_by_target = {
        factor: {category: len(rows) for category, rows in by_cat.items()}
        for factor, by_cat in selected.items()
    }
    report = {
        "target_count": args.target_count,
        "candidate_multiplier": args.candidate_multiplier,
        "candidate_pool": len(candidate_rows),
        "excluded_existing_ids": len(existing_ids),
        "selected_total": len(selected_rows),
        "current_counts": {
            factor: {category: current_counts[(factor, category)] for category in cats}
            for factor, cats in TARGET_CATEGORIES.items()
        },
        "deficits": deficits,
        "selected_by_target": selected_by_target,
        "selected_by_dataset": dict(selected_by_dataset.most_common()),
        "selected_by_rule_factor": {
            factor: dict(counter.most_common()) for factor, counter in selected_by_rule_factor.items()
        },
    }
    report_path = args.report or args.output.with_suffix(".report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"selected={len(selected_rows)} candidate_pool={len(candidate_rows)} output={args.output}")
    print(f"report={report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
