#!/usr/bin/env python3
"""Compare CoIN++ trainable-module regimes using rescored continual matrices."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-base", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--order-json", type=Path, required=True)
    parser.add_argument("--modes", nargs="+", required=True)
    parser.add_argument("--factor-name", default="visual_substrate")
    parser.add_argument("--metric", default="primary_score")
    parser.add_argument("--summary-dir-name", default="summary_official")
    return parser.parse_args()


def read_stages(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    stages = [str(value) for value in payload.get("trainable_order", [])]
    if not stages:
        raise ValueError(f"No trainable_order found in {path}")
    return stages


def read_matrix(path: Path, stages: list[str]) -> list[list[float]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing matrix: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = {row["trained_until"]: row for row in csv.DictReader(handle)}
    matrix = []
    for stage in stages:
        if stage not in rows:
            raise ValueError(f"{path} is missing stage={stage}")
        matrix.append([float(rows[stage][task]) for task in stages])
    return matrix


def summarize_mode(
    mode: str,
    matrix: list[list[float]],
    stages: list[str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    count = len(stages)
    diagonal = [matrix[index][index] for index in range(count)]
    final_scores = matrix[-1]
    seen_scores = [mean(matrix[index][: index + 1]) for index in range(count)]
    task_rows = []
    for task_index, task in enumerate(stages):
        after_learning = [matrix[row][task_index] for row in range(task_index, count)]
        best = max(after_learning)
        final = final_scores[task_index]
        task_rows.append(
            {
                "mode": mode,
                "task": task,
                "score_at_learning": diagonal[task_index],
                "best_after_learning": best,
                "final_score": final,
                "forgetting": best - final,
                "final_minus_learning": final - diagonal[task_index],
            }
        )
    old_tasks = task_rows[:-1] if count > 1 else task_rows
    summary = {
        "mode": mode,
        "final_average": mean(final_scores),
        "mean_seen_score": mean(seen_scores),
        "mean_score_at_learning": mean(diagonal),
        "average_forgetting_old_tasks": mean(row["forgetting"] for row in old_tasks),
        "bwt_old_tasks": mean(row["final_minus_learning"] for row in old_tasks),
        "final_task_score": final_scores[-1],
    }
    return summary, task_rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    field: (
                        f"{row.get(field):.6f}"
                        if isinstance(row.get(field), float)
                        else row.get(field, "")
                    )
                    for field in fields
                }
            )


def write_markdown(
    path: Path,
    summaries: list[dict[str, Any]],
    task_rows: list[dict[str, Any]],
    stages: list[str],
    factor_name: str,
    metric: str,
) -> None:
    by_mode_task = {(row["mode"], row["task"]): row for row in task_rows}
    lines = [
        f"# {factor_name.replace('_', ' ').title()} Module Comparison",
        "",
        f"Scoring protocol: dataset-native metrics with LLM-Judge fallback; matrix metric: `{metric}`.",
        "",
        "## Overall Continual Metrics",
        "",
        "| Mode | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) | Final task |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            "| {mode} | {final_average:.4f} | {mean_seen_score:.4f} | "
            "{mean_score_at_learning:.4f} | {average_forgetting_old_tasks:.4f} | "
            "{bwt_old_tasks:.4f} | {final_task_score:.4f} |".format(**row)
        )

    lines.extend(
        [
            "",
            "## Final Scores by Task",
            "",
            "| Mode | " + " | ".join(stages) + " |",
            "|---|" + "|".join(["---:"] * len(stages)) + "|",
        ]
    )
    for summary in summaries:
        mode = summary["mode"]
        cells = [f"{by_mode_task[(mode, task)]['final_score']:.4f}" for task in stages]
        lines.append("| " + mode + " | " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## Forgetting by Task",
            "",
            "| Mode | Task | At learning | Best | Final | Forgetting | BWT |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in task_rows:
        lines.append(
            "| {mode} | {task} | {score_at_learning:.4f} | {best_after_learning:.4f} | "
            "{final_score:.4f} | {forgetting:.4f} | {final_minus_learning:.4f} |".format(
                **row
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    stages = read_stages(args.order_json.resolve())
    result_base = args.result_base.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    all_task_rows = []
    matrices = {}
    for mode in args.modes:
        path = (
            result_base
            / mode
            / "eval"
            / args.summary_dir_name
            / f"matrix_{args.metric}.csv"
        )
        matrix = read_matrix(path, stages)
        summary, task_rows = summarize_mode(mode, matrix, stages)
        summaries.append(summary)
        all_task_rows.extend(task_rows)
        matrices[mode] = matrix

    write_csv(
        output_dir / f"module_comparison_{args.metric}.csv",
        summaries,
        [
            "mode",
            "final_average",
            "mean_seen_score",
            "mean_score_at_learning",
            "average_forgetting_old_tasks",
            "bwt_old_tasks",
            "final_task_score",
        ],
    )
    write_csv(
        output_dir / f"module_task_metrics_{args.metric}.csv",
        all_task_rows,
        [
            "mode",
            "task",
            "score_at_learning",
            "best_after_learning",
            "final_score",
            "forgetting",
            "final_minus_learning",
        ],
    )
    write_markdown(
        output_dir / "module_comparison.md",
        summaries,
        all_task_rows,
        stages,
        args.factor_name,
        args.metric,
    )
    (output_dir / "module_comparison.json").write_text(
        json.dumps(
            {
                "factor": args.factor_name,
                "metric": args.metric,
                "stages": stages,
                "summaries": summaries,
                "task_metrics": all_task_rows,
                "matrices": matrices,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote official/Judge module comparison to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
