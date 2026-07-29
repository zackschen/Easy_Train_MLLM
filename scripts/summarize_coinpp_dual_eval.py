#!/usr/bin/env python3
"""Build separate standard and LLM-Judge continual-learning reports."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from statistics import mean
from typing import Any


CORE_METRICS = ("standard_score", "llm_judge_score")
MATRIX_METRICS = (
    "standard_score",
    "standard_dataset_macro_score",
    "llm_judge_score",
    "llm_judge_dataset_macro_score",
    "standard_judge_agreement_at_0_5",
    "standard_judge_mean_absolute_gap",
    "official_metric_coverage",
    "direct_comparison_coverage",
    "judge_coverage",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--result-root", type=Path, required=True)
    parser.add_argument("--order-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=None)
    parser.add_argument("--metrics-file-name", default="metrics_dual_all.json")
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
    rows: list[dict[str, Any]] = []
    for index, stage in enumerate(stages, 1):
        stage_key = f"{index}_{stage}"
        path = result_root / stage_key / metrics_file_name
        if not path.is_file():
            raise FileNotFoundError(f"Missing dual-track metrics: {path}")
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
    output: dict[tuple[str, str], float] = {}
    for row in rows:
        value = row.get(metric)
        if value is not None:
            output[(row["trained_until"], row["task"])] = float(value)
    return output


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
        at_learning = values.get((task, task))
        final_score = values.get((final_stage, task))
        best = max(after_learning)
        output.append(
            {
                "task": task,
                "score_at_learning": at_learning,
                "best_after_learning": best,
                "final_score": final_score,
                "forgetting": None if final_score is None else best - final_score,
                "final_minus_learning": (
                    None
                    if at_learning is None or final_score is None
                    else final_score - at_learning
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
    missing = [
        (stage, task)
        for stage in stages
        for task in stages
        if (stage, task) not in values
    ]
    if missing:
        raise ValueError(f"Metric {metric} is incomplete; first missing cells: {missing[:5]}")
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
            float(row["forgetting"])
            for row in old_tasks
            if row["forgetting"] is not None
        ),
        "bwt_old_tasks": mean(
            float(row["final_minus_learning"])
            for row in old_tasks
            if row["final_minus_learning"] is not None
        ),
        "final_task_score": final_values[-1],
    }


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
                    "num_standard_scored": values.get("num_standard_scored"),
                    "num_judged": values.get("num_judged"),
                    "standard_score": values.get("standard_score"),
                    "llm_judge_score": values.get("llm_judge_score"),
                    "official_metric_coverage": values.get("official_metric_coverage"),
                    "direct_comparison_coverage": values.get(
                        "direct_comparison_coverage"
                    ),
                    "judge_coverage": values.get("judge_coverage"),
                    "standard_judge_agreement_at_0_5": values.get(
                        "standard_judge_agreement_at_0_5"
                    ),
                    "standard_judge_pearson": values.get("standard_judge_pearson"),
                    "standard_judge_mean_absolute_gap": values.get(
                        "standard_judge_mean_absolute_gap"
                    ),
                    "standard_protocol_counts": json.dumps(
                        values.get("standard_protocol_counts", {}),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "standard_metric_counts": json.dumps(
                        values.get("standard_metric_counts", {}),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                    "agreement_confusion_at_0_5": json.dumps(
                        values.get("agreement_confusion_at_0_5", {}),
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                }
            )
    return output


def fmt(value: Any) -> str:
    return "" if value is None else f"{float(value):.4f}"


def append_matrix(
    lines: list[str],
    title: str,
    rows: list[dict[str, Any]],
    stages: list[str],
    metric: str,
) -> None:
    values = lookup(rows, metric)
    lines.extend(
        [
            f"## {title}",
            "",
            "| Trained until | " + " | ".join(stages) + " |",
            "|---|" + "|".join(["---:"] * len(stages)) + "|",
        ]
    )
    for stage in stages:
        cells = [fmt(values.get((stage, task))) for task in stages]
        lines.append("| " + stage + " | " + " | ".join(cells) + " |")
    lines.append("")


def append_forgetting(
    lines: list[str],
    title: str,
    rows: list[dict[str, Any]],
) -> None:
    lines.extend(
        [
            f"## {title}",
            "",
            "| Task | At learning | Best after learning | Final | Forgetting | BWT |",
            "|---|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        lines.append(
            "| {task} | {at_learning} | {best} | {final} | {forgetting} | {bwt} |".format(
                task=row["task"],
                at_learning=fmt(row["score_at_learning"]),
                best=fmt(row["best_after_learning"]),
                final=fmt(row["final_score"]),
                forgetting=fmt(row["forgetting"]),
                bwt=fmt(row["final_minus_learning"]),
            )
        )
    lines.append("")


def write_markdown(
    path: Path,
    rows: list[dict[str, Any]],
    stages: list[str],
    factor_name: str,
    overalls: dict[str, dict[str, Any]],
    forgetting: dict[str, list[dict[str, Any]]],
) -> None:
    lines = [
        f"# CoIN++ {factor_name.replace('_', ' ').title()} Dual Evaluation",
        "",
        "The standard and LLM-Judge tracks are independent. The standard track uses a "
        "registered source-benchmark metric when possible and normalized answer comparison "
        "otherwise. The LLM Judge scores every prediction on CoIN's 0-10 scale; matrices below "
        "report that score normalized to [0, 1].",
        "",
        "## Continual Summary",
        "",
        "| Track | Final average | Mean seen | At learning | Avg forgetting (old) | BWT (old) |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric, label in (
        ("standard_score", "Standard"),
        ("llm_judge_score", "LLM Judge"),
    ):
        summary = overalls[metric]
        lines.append(
            "| {label} | {final_average:.4f} | {mean_seen_score:.4f} | "
            "{mean_score_at_learning:.4f} | {average_forgetting_old_tasks:.4f} | "
            "{bwt_old_tasks:.4f} |".format(label=label, **summary)
        )
    lines.append("")

    append_matrix(lines, "Standard Score Matrix", rows, stages, "standard_score")
    append_matrix(lines, "LLM-Judge Score Matrix", rows, stages, "llm_judge_score")
    append_forgetting(
        lines,
        "Standard-Score Forgetting",
        forgetting["standard_score"],
    )
    append_forgetting(
        lines,
        "LLM-Judge Forgetting",
        forgetting["llm_judge_score"],
    )

    official = lookup(rows, "official_metric_coverage")
    direct = lookup(rows, "direct_comparison_coverage")
    judged = lookup(rows, "judge_coverage")
    agreement = lookup(rows, "standard_judge_agreement_at_0_5")
    lines.extend(
        [
            "## Coverage And Agreement",
            "",
            "| Trained until | Task | Official metric | Direct compare | Judge | Agreement@0.5 |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for stage in stages:
        for task in stages:
            key = (stage, task)
            lines.append(
                f"| {stage} | {task} | {official[key]:.1%} | {direct[key]:.1%} | "
                f"{judged[key]:.1%} | {agreement[key]:.1%} |"
            )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    result_root = args.result_root.resolve()
    order_path = args.order_json.resolve()
    stages = read_order(order_path)
    factor_name = args.factor_name or order_path.parent.name
    output_dir = (args.output_dir or result_root / "summary_dual").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(result_root, stages, args.metrics_file_name)
    for metric in MATRIX_METRICS:
        matrix = matrix_rows(rows, stages, metric)
        write_csv(
            output_dir / f"matrix_{metric}.csv",
            matrix,
            ["trained_until", *stages],
        )

    summary_fields = [
        "stage_index",
        "stage_key",
        "trained_until",
        "task",
        "num_samples",
        "num_standard_scored",
        "num_judged",
        "standard_score",
        "standard_dataset_macro_score",
        "llm_judge_score",
        "llm_judge_dataset_macro_score",
        "standard_coverage",
        "judge_coverage",
        "official_metric_coverage",
        "direct_comparison_coverage",
        "standard_judge_agreement_at_0_5",
        "standard_judge_pearson",
        "standard_judge_mean_absolute_gap",
        "predictions_file",
        "scored_predictions_file",
    ]
    write_csv(output_dir / "summary.csv", rows, summary_fields)

    forgetting: dict[str, list[dict[str, Any]]] = {}
    overalls: dict[str, dict[str, Any]] = {}
    for metric in CORE_METRICS:
        forgetting[metric] = forgetting_rows(rows, stages, metric)
        overalls[metric] = overall_summary(rows, stages, metric)
        write_csv(
            output_dir / f"forgetting_{metric}.csv",
            forgetting[metric],
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
            "num_standard_scored",
            "num_judged",
            "standard_score",
            "llm_judge_score",
            "official_metric_coverage",
            "direct_comparison_coverage",
            "judge_coverage",
            "standard_judge_agreement_at_0_5",
            "standard_judge_pearson",
            "standard_judge_mean_absolute_gap",
            "standard_protocol_counts",
            "standard_metric_counts",
            "agreement_confusion_at_0_5",
        ],
    )

    report = {
        "factor": factor_name,
        "protocol": "independent_standard_and_llm_judge",
        "stages": stages,
        "overall": overalls,
        "forgetting": forgetting,
        "rows": rows,
    }
    (output_dir / "summary.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown(
        output_dir / "learning_matrices.md",
        rows,
        stages,
        factor_name,
        overalls,
        forgetting,
    )
    print(f"Wrote CoIN++ dual-track summary to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
