#!/usr/bin/env python3
"""Summarize CoIN++ dataset-native/LLM-Judge continual evaluation results."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--order-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--metrics-file-name", default="metrics_official_all.json")
    parser.add_argument("--metric", default="primary_score")
    parser.add_argument("--factor-name", default=None)
    return parser.parse_args()


def read_order(path: Path) -> list[str]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    stages = [str(value) for value in payload.get("trainable_order", [])]
    if not stages:
        raise ValueError(f"No trainable_order found in {path}")
    return stages


def load_rows(
    result_root: Path,
    stages: list[str],
    metrics_file_name: str,
) -> list[dict[str, Any]]:
    rows = []
    for index, stage in enumerate(stages, 1):
        stage_key = f"{index}_{stage}"
        path = result_root / stage_key / metrics_file_name
        if not path.is_file():
            raise FileNotFoundError(f"Missing rescored metrics: {path}")
        payload = json.loads(path.read_text(encoding="utf-8"))
        by_task = {str(item.get("task")): item for item in payload}
        missing = [task for task in stages if task not in by_task]
        if missing:
            raise ValueError(f"{path} is missing tasks: {missing}")
        for task in stages:
            row = dict(by_task[task])
            row.update(
                {
                    "stage_index": index,
                    "stage_key": stage_key,
                    "trained_until": stage,
                }
            )
            rows.append(row)
    return rows


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


def lookup(rows: list[dict[str, Any]], metric: str) -> dict[tuple[str, str], float]:
    values = {}
    for row in rows:
        value = row.get(metric)
        if value is not None:
            values[(row["trained_until"], row["task"])] = float(value)
    return values


def matrix_rows(
    rows: list[dict[str, Any]],
    stages: list[str],
    metric: str,
) -> list[dict[str, Any]]:
    values = lookup(rows, metric)
    output = []
    for trained_until in stages:
        row: dict[str, Any] = {"trained_until": trained_until}
        for task in stages:
            row[task] = values.get((trained_until, task), "")
        output.append(row)
    return output


def forgetting_rows(
    rows: list[dict[str, Any]],
    stages: list[str],
    metric: str,
) -> list[dict[str, Any]]:
    values = lookup(rows, metric)
    final_stage = stages[-1]
    output = []
    for task_index, task in enumerate(stages):
        after_learning = [
            values[(stage, task)]
            for stage in stages[task_index:]
            if (stage, task) in values
        ]
        if not after_learning:
            continue
        score_at_learning = values.get((task, task))
        final_score = values.get((final_stage, task))
        best = max(after_learning)
        output.append(
            {
                "task": task,
                "score_at_learning": score_at_learning,
                "best_after_learning": best,
                "final_score": final_score,
                "forgetting": None if final_score is None else best - final_score,
                "final_minus_learning": (
                    None
                    if final_score is None or score_at_learning is None
                    else final_score - score_at_learning
                ),
            }
        )
    return output


def flatten_dataset_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for row in rows:
        for dataset, values in sorted((row.get("per_dataset") or {}).items()):
            output.append(
                {
                    "stage_index": row["stage_index"],
                    "trained_until": row["trained_until"],
                    "task": row["task"],
                    "dataset": dataset,
                    "num_samples": values.get("num_samples"),
                    "num_scored": values.get("num_scored"),
                    "primary_score": values.get("primary_score"),
                    "official_score": values.get("official_score"),
                    "judge_score": values.get("judge_score"),
                    "token_f1": values.get("token_f1"),
                    "protocol_counts": json.dumps(
                        values.get("protocol_counts", {}),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "metric_counts": json.dumps(
                        values.get("metric_counts", {}),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                }
            )
    return output


def overall_summary(
    rows: list[dict[str, Any]],
    stages: list[str],
    metric: str,
) -> dict[str, Any]:
    values = lookup(rows, metric)
    diagonal = [values[(stage, stage)] for stage in stages]
    final_values = [values[(stages[-1], task)] for task in stages]
    seen_averages = [
        mean(values[(stage, task)] for task in stages[: index + 1])
        for index, stage in enumerate(stages)
    ]
    forgetting = forgetting_rows(rows, stages, metric)
    old_tasks = forgetting[:-1] if len(forgetting) > 1 else forgetting
    return {
        "metric": metric,
        "final_average": mean(final_values),
        "mean_seen_score": mean(seen_averages),
        "mean_score_at_learning": mean(diagonal),
        "average_forgetting_old_tasks": mean(
            float(row["forgetting"]) for row in old_tasks if row["forgetting"] is not None
        ),
        "bwt_old_tasks": mean(
            float(row["final_minus_learning"])
            for row in old_tasks
            if row["final_minus_learning"] is not None
        ),
        "final_task_score": final_values[-1],
    }


def write_markdown(
    path: Path,
    rows: list[dict[str, Any]],
    stages: list[str],
    metric: str,
    factor_name: str,
    overall: dict[str, Any],
    forgetting: list[dict[str, Any]],
) -> None:
    values = lookup(rows, metric)
    coverage = lookup(rows, "official_coverage")
    judge_coverage = lookup(rows, "judge_coverage")
    lines = [
        f"# CoIN++ {factor_name.replace('_', ' ').title()} Evaluation",
        "",
        (
            f"Primary metric: `{metric}`. Final average: **{overall['final_average']:.4f}**; "
            f"average forgetting on old tasks: **{overall['average_forgetting_old_tasks']:.4f}**; "
            f"BWT: **{overall['bwt_old_tasks']:.4f}**."
        ),
        "",
        "## Continual Matrix",
        "",
        "| Trained until | " + " | ".join(stages) + " |",
        "|---|" + "|".join(["---:"] * len(stages)) + "|",
    ]
    for stage in stages:
        cells = [f"{values[(stage, task)]:.4f}" for task in stages]
        lines.append("| " + stage + " | " + " | ".join(cells) + " |")

    lines.extend(
        [
            "",
            "## Forgetting",
            "",
            "| Task | At learning | Best after learning | Final | Forgetting | BWT |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in forgetting:
        lines.append(
            "| {task} | {score_at_learning:.4f} | {best_after_learning:.4f} | "
            "{final_score:.4f} | {forgetting:.4f} | {final_minus_learning:.4f} |".format(
                **row
            )
        )

    lines.extend(
        [
            "",
            "## Scoring Coverage",
            "",
            "| Trained until | Task | Official metric | LLM judge |",
            "|---|---|---:|---:|",
        ]
    )
    for stage in stages:
        for task in stages:
            lines.append(
                f"| {stage} | {task} | {coverage[(stage, task)]:.1%} | "
                f"{judge_coverage[(stage, task)]:.1%} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    result_root = args.result_root.resolve()
    order_path = args.order_json.resolve()
    stages = read_order(order_path)
    factor_name = args.factor_name or order_path.parent.name
    output_dir = (args.output_dir or result_root / "summary_official").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(result_root, stages, args.metrics_file_name)
    metrics_to_write = [
        args.metric,
        "dataset_macro_score",
        "official_coverage",
        "judge_coverage",
    ]
    for metric in metrics_to_write:
        matrix = matrix_rows(rows, stages, metric)
        write_csv(output_dir / f"matrix_{metric}.csv", matrix, ["trained_until", *stages])

    flat_fields = [
        "stage_index",
        "stage_key",
        "trained_until",
        "task",
        "num_samples",
        "num_scored",
        "primary_score",
        "dataset_macro_score",
        "official_score",
        "judge_score",
        "official_coverage",
        "judge_coverage",
        "unscored_count",
        "predictions_file",
        "scored_predictions_file",
    ]
    write_csv(output_dir / "summary.csv", rows, flat_fields)

    forgetting = forgetting_rows(rows, stages, args.metric)
    write_csv(
        output_dir / f"forgetting_{args.metric}.csv",
        forgetting,
        [
            "task",
            "score_at_learning",
            "best_after_learning",
            "final_score",
            "forgetting",
            "final_minus_learning",
        ],
    )
    dataset_rows = flatten_dataset_rows(rows)
    write_csv(
        output_dir / "per_dataset_scores.csv",
        dataset_rows,
        [
            "stage_index",
            "trained_until",
            "task",
            "dataset",
            "num_samples",
            "num_scored",
            "primary_score",
            "official_score",
            "judge_score",
            "token_f1",
            "protocol_counts",
            "metric_counts",
        ],
    )

    overall = overall_summary(rows, stages, args.metric)
    report = {
        "factor": factor_name,
        "stages": stages,
        "overall": overall,
        "forgetting": forgetting,
        "rows": rows,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(
        output_dir / "learning_matrix.md",
        rows,
        stages,
        args.metric,
        factor_name,
        overall,
        forgetting,
    )
    print(f"Wrote CoIN++ official/Judge summary to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
