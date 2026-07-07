#!/usr/bin/env python3
"""Conservative post-repair for Factor-1 VLM metadata labels.

Motivation:
VLM labelers often collapse evidence to single_evidence when the final answer is
one object. For controlled continual-learning factors, evidence should describe
what must be inspected to answer the question. Spatial relation, comparison, and
counting questions generally require multiple visual regions/evidence units.

This script preserves original labels in *_vlm_before_repair fields and writes
repair provenance in label_repair.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable

SPATIAL_PATTERNS = [
    r"\b(to the left of|left of|to the right of|right of)\b",
    r"\b(next to|beside|near|nearest to|closest to|adjacent to)\b",
    r"\b(behind|in front of|front of|above|below|under|over|beneath)\b",
    r"\b(on top of|at the bottom of|at the top of|between|inside|outside)\b",
    r"\b(where is|located|positioned|relative to)\b",
]
COMPARISON_PATTERNS = [
    r"\b(compare|compared|difference between|more than|less than|greater than|fewer than)\b",
    r"\b(larger|smaller|bigger|higher|lower|taller|shorter|longer|wider|narrower)\b",
    r"\b(most|least|highest|lowest|largest|smallest|biggest|fewest)\b",
]
COUNTING_PATTERNS = [
    r"\b(how many|number of|count|total number|amount of)\b",
]
CHART_LOOKUP_PATTERNS = [
    r"\b(represents?|corresponds? to|for country|for category|for year|for month)\b",
    r"\b(bar|line|point|axis|legend|segment|slice|row|column|cell)\b",
]
TEXT_LOOKUP_PATTERNS = [
    r"\b(read|written|printed|word|words|letter|letters|sign|label|title|caption)\b",
]


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(x for x in (compact(v) for v in value) if x)
    if isinstance(value, dict):
        for key in ("text", "value", "answer", "content", "label"):
            if key in value:
                return compact(value[key])
    return str(value)


def matches_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def compute_evidence_complexity(scope: str, evidence_count: int, reasoning_hops: int, external: bool) -> dict[str, Any]:
    scope_level = {
        "single_region": 1,
        "global_image": 1,
        "multi_region": 2,
        "cross_region": 3,
        "cross_page": 4,
        "image_plus_knowledge": 4,
    }.get(scope, 1)
    score = scope_level + min(max(evidence_count, 1) - 1, 2) + min(max(reasoning_hops, 0), 3) + int(bool(external))
    if scope in {"cross_page", "image_plus_knowledge"} or external or reasoning_hops >= 3:
        level, label = 4, "cross_context"
    elif scope == "cross_region" or reasoning_hops >= 2 or evidence_count > 3:
        level, label = 3, "cross_region_or_multihop"
    elif scope == "multi_region" or evidence_count >= 2 or reasoning_hops >= 1:
        level, label = 2, "multi_evidence"
    else:
        level, label = 1, "single_evidence"
    return {"evidence_complexity": label, "evidence_complexity_level": level, "evidence_complexity_score": score}


def preserve_original(row: dict[str, Any], field: str) -> None:
    backup = f"{field}_vlm_before_repair"
    if backup not in row:
        row[backup] = row.get(field)


def set_field(row: dict[str, Any], field: str, value: Any, changes: dict[str, Any]) -> None:
    old = row.get(field)
    if old != value:
        preserve_original(row, field)
        row[field] = value
        changes[field] = {"from": old, "to": value}


def force_multi_evidence(row: dict[str, Any], changes: dict[str, Any], reason: str, scope: str = "multi_region", min_count: int = 2, min_hops: int = 1) -> None:
    count = row.get("evidence_count")
    hops = row.get("reasoning_hops")
    try:
        count_i = int(count)
    except (TypeError, ValueError):
        count_i = 1
    try:
        hops_i = int(hops)
    except (TypeError, ValueError):
        hops_i = 0
    count_i = max(count_i, min_count)
    hops_i = max(hops_i, min_hops)
    external = bool(row.get("requires_external_knowledge"))

    set_field(row, "evidence_scope", scope, changes)
    set_field(row, "evidence_count", count_i, changes)
    set_field(row, "reasoning_hops", hops_i, changes)
    complexity = compute_evidence_complexity(scope, count_i, hops_i, external)
    for field, value in complexity.items():
        set_field(row, field, value, changes)


def repair_row(row: dict[str, Any]) -> tuple[dict[str, Any], list[str], dict[str, Any]]:
    row = dict(row)
    question = compact(row.get("question"))
    q = question.lower()
    visual = compact(row.get("visual_substrate"))
    reasons: list[str] = []
    changes: dict[str, Any] = {}

    spatial = matches_any(q, SPATIAL_PATTERNS)
    comparison = matches_any(q, COMPARISON_PATTERNS)
    counting = matches_any(q, COUNTING_PATTERNS)
    chart_lookup = visual in {"chart", "infographic", "document", "diagram", "map"} and matches_any(q, CHART_LOOKUP_PATTERNS)
    text_lookup = matches_any(q, TEXT_LOOKUP_PATTERNS)

    if spatial:
        reasons.append("spatial_relation_question")
        set_field(row, "skill_type_primary", "relation", changes)
        set_field(row, "evidence_source_primary", "spatial_relation", changes)
        set_field(row, "evidence_type_primary", "multi_region", changes)
        force_multi_evidence(row, changes, "spatial_relation_question", scope="multi_region", min_count=2, min_hops=1)

    if comparison:
        reasons.append("comparison_question")
        set_field(row, "skill_type_primary", "comparison", changes)
        set_field(row, "evidence_source_primary", "attribute", changes)
        set_field(row, "evidence_type_primary", "multi_region", changes)
        force_multi_evidence(row, changes, "comparison_question", scope="multi_region", min_count=2, min_hops=1)

    if counting:
        reasons.append("counting_question")
        set_field(row, "skill_type_primary", "counting", changes)
        # Counting multiple visible instances is at least multi-evidence unless already harder.
        current_scope = compact(row.get("evidence_scope"))
        scope = current_scope if current_scope in {"cross_region", "cross_page", "image_plus_knowledge"} else "multi_region"
        set_field(row, "evidence_type_primary", scope, changes)
        force_multi_evidence(row, changes, "counting_question", scope=scope, min_count=2, min_hops=1)

    if chart_lookup and not spatial and not comparison:
        reasons.append("structured_visual_lookup")
        if visual == "chart":
            set_field(row, "skill_type_primary", "chart_reasoning", changes)
            set_field(row, "evidence_source_primary", "chart", changes)
        elif visual in {"document", "infographic"}:
            set_field(row, "skill_type_primary", "document_reasoning", changes)
            set_field(row, "evidence_source_primary", "text", changes)
        elif visual in {"diagram", "map"}:
            set_field(row, "skill_type_primary", "diagram_reasoning", changes)
            set_field(row, "evidence_source_primary", "diagram", changes)
        set_field(row, "evidence_type_primary", "multi_region", changes)
        force_multi_evidence(row, changes, "structured_visual_lookup", scope="multi_region", min_count=2, min_hops=1)

    if text_lookup and compact(row.get("skill_type_primary")) == "recognition":
        reasons.append("text_lookup_recognition_to_text_reading")
        set_field(row, "skill_type_primary", "text_reading", changes)

    if changes:
        row["label_repair"] = {
            "version": "factor1-repair-v1",
            "reasons": reasons,
            "changes": changes,
        }
        src = compact(row.get("label_source"))
        row["label_source"] = f"{src}+conservative_repair" if src else "conservative_repair"
    return row, reasons, changes


def iter_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)


def main() -> int:
    parser = argparse.ArgumentParser(description="Conservatively repair Factor-1 evidence/skill labels")
    parser.add_argument("--input", type=Path, default=Path("cl_dataset/coin_factor1_meta_all/metadata/sample_metadata.vlm.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("cl_dataset/coin_factor1_meta_all/metadata/sample_metadata.vlm.repaired.jsonl"))
    parser.add_argument("--summary", type=Path, default=Path("cl_dataset/coin_factor1_meta_all/metadata/sample_metadata.vlm.repaired.summary.json"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--show-id", action="append", default=[])
    args = parser.parse_args()

    total = changed = 0
    reason_counts: Counter[str] = Counter()
    field_counts: Counter[str] = Counter()
    examples: dict[str, Any] = {}

    out_f = None
    if not args.dry_run:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        out_f = args.output.open("w", encoding="utf-8")
    try:
        for row in iter_jsonl(args.input):
            total += 1
            repaired, reasons, changes = repair_row(row)
            row_id = compact(row.get("id"))
            if changes:
                changed += 1
                for reason in reasons:
                    reason_counts[reason] += 1
                for field in changes:
                    field_counts[field] += 1
                if len(examples) < 20:
                    examples[row_id] = {"question": row.get("question"), "answer": row.get("answer"), "reasons": reasons, "changes": changes}
            if row_id in args.show_id:
                examples[row_id] = {"before": row, "after": repaired, "reasons": reasons, "changes": changes}
            if out_f is not None:
                out_f.write(json.dumps(repaired, ensure_ascii=False) + "\n")
    finally:
        if out_f is not None:
            out_f.close()

    summary = {
        "input": str(args.input),
        "output": None if args.dry_run else str(args.output),
        "total": total,
        "changed": changed,
        "changed_ratio": round(changed / total, 6) if total else 0,
        "reason_counts": dict(reason_counts),
        "field_counts": dict(field_counts),
        "examples": examples,
    }
    if not args.dry_run:
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
