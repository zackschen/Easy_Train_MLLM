#!/usr/bin/env python3
"""Compare continual-evaluation matrices across trainable-module regimes."""

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
    parser.add_argument(
        "--metric",
        default="relaxed_match",
        choices=["relaxed_match", "exact_match"],
    )
    return parser.parse_args()


def load_stage_order(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    stages = [str(value) for value in data.get("trainable_order", [])]
    if not stages:
        raise ValueError(f"No trainable_order found in {path}")
    return stages


def load_matrix(path: Path, stages: list[str]) -> list[list[float]]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing evaluation matrix: {path}")

    with path.open(newline="", encoding="utf-8") as handle:
        rows = {row["trained_until"]: row for row in csv.DictReader(handle)}

    matrix = []
    for trained_until in stages:
        if trained_until not in rows:
            raise ValueError(f"Matrix {path} has no row for stage={trained_until}")
        values = []
        for task in stages:
            raw = rows[trained_until].get(task, "")
            if raw in (None, ""):
                raise ValueError(
                    f"Matrix {path} is missing stage={trained_until}, task={task}"
                )
            values.append(float(raw))
        matrix.append(values)
    return matrix


def summarize_mode(mode: str, matrix: list[list[float]], stages: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    task_count = len(stages)
    diagonal = [matrix[index][index] for index in range(task_count)]
    final_scores = matrix[-1]
    seen_averages = [mean(matrix[index][: index + 1]) for index in range(task_count)]

    task_rows = []
    for task_index, task in enumerate(stages):
        after_learning = [matrix[row][task_index] for row in range(task_index, task_count)]
        best_after_learning = max(after_learning)
        final_score = final_scores[task_index]
        task_rows.append(
            {
                "mode": mode,
                "task": task,
                "score_at_learning": diagonal[task_index],
                "best_after_learning": best_after_learning,
                "final_score": final_score,
                "forgetting": best_after_learning - final_score,
                "final_minus_learning": final_score - diagonal[task_index],
            }
        )

    old_task_rows = task_rows[:-1] if task_count > 1 else task_rows
    summary = {
        "mode": mode,
        "final_average": mean(final_scores),
        "mean_seen_accuracy": mean(seen_averages),
        "mean_score_at_learning": mean(diagonal),
        "average_forgetting_old_tasks": mean(row["forgetting"] for row in old_task_rows),
        "bwt_old_tasks": mean(row["final_minus_learning"] for row in old_task_rows),
        "final_task_score": final_scores[-1],
    }
    return summary, task_rows


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    key: f"{value:.6f}" if isinstance(value, float) else value
                    for key, value in row.items()
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
    title = factor_name.replace("_", " ").title()
    lines = [
        f"# {title} Trainable-Module Comparison ({metric})",
        "",
        "## Overall Continual Metrics",
        "",
        "| Mode | Final average | Mean seen accuracy | Mean at learning | Avg forgetting (old) | BWT (old) | Final-task score |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summaries:
        lines.append(
            "| {mode} | {final_average:.4f} | {mean_seen_accuracy:.4f} | "
            "{mean_score_at_learning:.4f} | {average_forgetting_old_tasks:.4f} | "
            "{bwt_old_tasks:.4f} | {final_task_score:.4f} |".format(**row)
        )

    task_lookup = {(row["mode"], row["task"]): row for row in task_rows}
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
        values = [f"{task_lookup[(mode, task)]['final_score']:.4f}" for task in stages]
        lines.append("| " + mode + " | " + " | ".join(values) + " |")

    lines.extend(
        [
            "",
            "## Forgetting by Task",
            "",
            "| Mode | Task | At learning | Best after learning | Final | Forgetting | Final - learning |",
            "|---|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in task_rows:
        lines.append(
            "| {mode} | {task} | {score_at_learning:.4f} | {best_after_learning:.4f} | "
            "{final_score:.4f} | {forgetting:.4f} | {final_minus_learning:.4f} |".format(**row)
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    stages = load_stage_order(args.order_json.resolve())
    result_base = args.result_base.resolve()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    summaries = []
    all_task_rows = []
    matrices = {}
    for mode in args.modes:
        matrix_path = result_base / mode / "eval" / "summary" / f"matrix_{args.metric}.csv"
        matrix = load_matrix(matrix_path, stages)
        summary, task_rows = summarize_mode(mode, matrix, stages)
        summaries.append(summary)
        all_task_rows.extend(task_rows)
        matrices[mode] = matrix

    summary_fields = [
        "mode",
        "final_average",
        "mean_seen_accuracy",
        "mean_score_at_learning",
        "average_forgetting_old_tasks",
        "bwt_old_tasks",
        "final_task_score",
    ]
    task_fields = [
        "mode",
        "task",
        "score_at_learning",
        "best_after_learning",
        "final_score",
        "forgetting",
        "final_minus_learning",
    ]
    write_csv(output_dir / f"module_comparison_{args.metric}.csv", summaries, summary_fields)
    write_csv(output_dir / f"module_task_metrics_{args.metric}.csv", all_task_rows, task_fields)
    write_markdown(
        output_dir / "module_comparison.md",
        summaries,
        all_task_rows,
        stages,
        args.factor_name,
        args.metric,
    )
    payload = {
        "factor": args.factor_name,
        "metric": args.metric,
        "stages": stages,
        "summaries": summaries,
        "task_metrics": all_task_rows,
        "matrices": matrices,
    }
    (output_dir / "module_comparison.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote trainable-module comparison to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
