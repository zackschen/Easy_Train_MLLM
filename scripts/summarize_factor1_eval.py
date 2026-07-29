#!/usr/bin/env python3
"""Summarize Factor-1 continual evaluation results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_ORDER = ["single_evidence", "multi_evidence", "cross_region_or_multihop", "cross_context"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--result-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, default=None)
    p.add_argument("--stage-order", nargs="*", default=DEFAULT_ORDER)
    p.add_argument("--task-order", nargs="*", default=DEFAULT_ORDER)
    p.add_argument("--metric", default="relaxed_match", choices=["relaxed_match", "exact_match"])
    p.add_argument("--factor-name", default="evidence_complexity")
    return p.parse_args()


def load_metrics(result_root: Path, stage_order: list[str]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for idx, stage in enumerate(stage_order, 1):
        stage_name = f"{idx}_{stage}"
        path = result_root / stage_name / "metrics_all.json"
        if not path.exists():
            print(f"[warn] missing metrics: {path}")
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            row = dict(item)
            row["stage_index"] = idx
            row["stage_name"] = stage_name
            row["trained_until"] = stage
            rows.append(row)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fields})


def metric_lookup(rows: list[dict[str, Any]], metric: str) -> dict[tuple[str, str], float]:
    out = {}
    for row in rows:
        out[(row["trained_until"], row["task"])] = float(row.get(metric, 0.0))
    return out


def write_matrix(
    path: Path,
    rows: list[dict[str, Any]],
    stage_order: list[str],
    task_order: list[str],
    metric: str,
) -> None:
    lookup = metric_lookup(rows, metric)
    matrix_rows = []
    for stage in stage_order:
        row = {"trained_until": stage}
        for task in task_order:
            value = lookup.get((stage, task))
            row[task] = "" if value is None else f"{value:.6f}"
        matrix_rows.append(row)
    write_csv(path, matrix_rows, ["trained_until", *task_order])


def compute_forgetting(
    rows: list[dict[str, Any]],
    stage_order: list[str],
    task_order: list[str],
    metric: str,
) -> list[dict[str, Any]]:
    lookup = metric_lookup(rows, metric)
    final_stage = stage_order[-1]
    out = []
    for task in task_order:
        if task not in stage_order:
            continue
        learned_idx = stage_order.index(task)
        after_learning_stages = stage_order[learned_idx:]
        values = [lookup.get((stage, task)) for stage in after_learning_stages]
        values = [v for v in values if v is not None]
        if not values:
            continue
        score_at_learning = lookup.get((task, task))
        best_after_learning = max(values)
        final_score = lookup.get((final_stage, task))
        forgetting = None if final_score is None else best_after_learning - final_score
        out.append(
            {
                "task": task,
                "score_at_learning": "" if score_at_learning is None else f"{score_at_learning:.6f}",
                "best_after_learning": f"{best_after_learning:.6f}",
                "final_score": "" if final_score is None else f"{final_score:.6f}",
                "forgetting": "" if forgetting is None else f"{forgetting:.6f}",
            }
        )
    return out


def write_markdown(
    path: Path,
    rows: list[dict[str, Any]],
    stage_order: list[str],
    task_order: list[str],
    metric: str,
    forgetting_rows: list[dict[str, Any]],
    factor_name: str,
) -> None:
    lookup = metric_lookup(rows, metric)
    lines = []
    display_name = factor_name.replace("_", " ").title()
    lines.append(f"# Factor-1 {display_name} Continual Evaluation ({metric})")
    lines.append("")
    lines.append("## Performance Matrix")
    lines.append("")
    lines.append("| Trained until | " + " | ".join(task_order) + " |")
    lines.append("|---|" + "|".join(["---:"] * len(task_order)) + "|")
    for stage in stage_order:
        vals = []
        for task in task_order:
            v = lookup.get((stage, task))
            vals.append("-" if v is None else f"{v:.3f}")
        lines.append("| " + stage + " | " + " | ".join(vals) + " |")
    lines.append("")
    lines.append("## Forgetting")
    lines.append("")
    lines.append("| Task | Score at learning | Best after learning | Final score | Forgetting |")
    lines.append("|---|---:|---:|---:|---:|")
    for row in forgetting_rows:
        lines.append(
            "| {task} | {score_at_learning} | {best_after_learning} | {final_score} | {forgetting} |".format(
                **row
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    result_root = args.result_root.resolve()
    output_dir = (args.output_dir or result_root / "summary").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_metrics(result_root, args.stage_order)
    if not rows:
        raise SystemExit(f"No metrics found under {result_root}")

    flat_fields = [
        "stage_index",
        "stage_name",
        "trained_until",
        "task",
        "num_samples",
        "image_samples",
        "text_only_samples",
        "exact_match",
        "relaxed_match",
        "number_match",
        "yes_no_match",
        "eval_file",
        "predictions_file",
    ]
    write_csv(output_dir / "summary.csv", rows, flat_fields)
    write_matrix(output_dir / "matrix_relaxed_match.csv", rows, args.stage_order, args.task_order, "relaxed_match")
    write_matrix(output_dir / "matrix_exact_match.csv", rows, args.stage_order, args.task_order, "exact_match")
    forgetting = compute_forgetting(rows, args.stage_order, args.task_order, args.metric)
    write_csv(
        output_dir / f"forgetting_{args.metric}.csv",
        forgetting,
        ["task", "score_at_learning", "best_after_learning", "final_score", "forgetting"],
    )
    write_markdown(
        output_dir / "learning_matrix.md",
        rows,
        args.stage_order,
        args.task_order,
        args.metric,
        forgetting,
        args.factor_name,
    )
    print(f"Wrote summary files to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
