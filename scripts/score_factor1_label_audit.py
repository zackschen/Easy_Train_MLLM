#!/usr/bin/env python3
"""Score human-reviewed Factor-1 label audit CSV."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

FACTOR_PAIRS = [
    ("visual_substrate", "human_visual_substrate"),
    ("skill_requirement", "human_skill_requirement"),
    ("evidence_complexity", "human_evidence_complexity"),
    ("answer_distribution", "human_answer_distribution"),
]


def norm(value: str | None) -> str:
    return (value or "").strip().lower()


def main() -> int:
    parser = argparse.ArgumentParser(description="Score completed Factor-1 human audit CSV")
    parser.add_argument("--csv", type=Path, default=Path("cl_dataset/coin_factor1_label_audit/audit_samples.csv"))
    parser.add_argument("--output", type=Path, default=Path("cl_dataset/coin_factor1_label_audit/human_audit_score.json"))
    args = parser.parse_args()

    rows = list(csv.DictReader(args.csv.open("r", encoding="utf-8")))
    total_reviewed = 0
    factor_total: Counter[str] = Counter()
    factor_correct: Counter[str] = Counter()
    by_dataset_total: dict[str, Counter[str]] = defaultdict(Counter)
    by_dataset_correct: dict[str, Counter[str]] = defaultdict(Counter)
    overall_flags: Counter[str] = Counter()
    exact_all_total = 0
    exact_all_correct = 0

    for row in rows:
        has_any_human = any(norm(row.get(human)) for _, human in FACTOR_PAIRS) or norm(row.get("human_is_correct"))
        if not has_any_human:
            continue
        total_reviewed += 1
        dataset = norm(row.get("dataset")) or "unknown"
        all_answered = True
        all_correct = True
        for pred_key, human_key in FACTOR_PAIRS:
            human = norm(row.get(human_key))
            pred = norm(row.get(pred_key))
            if not human:
                all_answered = False
                continue
            factor_total[pred_key] += 1
            by_dataset_total[dataset][pred_key] += 1
            if human == pred:
                factor_correct[pred_key] += 1
                by_dataset_correct[dataset][pred_key] += 1
            else:
                all_correct = False
        if all_answered:
            exact_all_total += 1
            if all_correct:
                exact_all_correct += 1
        for flag in (row.get("audit_flags") or "").split(";"):
            flag = flag.strip()
            if flag:
                overall_flags[flag] += 1

    def acc(correct: int, total: int) -> float | None:
        return None if total == 0 else round(correct / total, 4)

    out = {
        "csv": str(args.csv),
        "total_rows": len(rows),
        "reviewed_rows": total_reviewed,
        "factor_accuracy": {
            key: {
                "correct": factor_correct[key],
                "total": factor_total[key],
                "accuracy": acc(factor_correct[key], factor_total[key]),
            }
            for key, _ in FACTOR_PAIRS
        },
        "exact_all_four_accuracy": {
            "correct": exact_all_correct,
            "total": exact_all_total,
            "accuracy": acc(exact_all_correct, exact_all_total),
        },
        "by_dataset_accuracy": {
            dataset: {
                key: {
                    "correct": by_dataset_correct[dataset][key],
                    "total": by_dataset_total[dataset][key],
                    "accuracy": acc(by_dataset_correct[dataset][key], by_dataset_total[dataset][key]),
                }
                for key, _ in FACTOR_PAIRS
                if by_dataset_total[dataset][key]
            }
            for dataset in sorted(by_dataset_total)
        },
        "reviewed_flag_counts": dict(overall_flags),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
