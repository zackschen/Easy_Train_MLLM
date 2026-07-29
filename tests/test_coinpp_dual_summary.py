#!/usr/bin/env python3
"""End-to-end tests for dual continual matrices and module comparison."""

from __future__ import annotations

import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import compare_coinpp_module_dual_eval as comparator
import summarize_coinpp_dual_eval as summarizer


def metric_row(task: str, standard_score: float, judge_score: float) -> dict:
    return {
        "task": task,
        "num_samples": 2,
        "num_standard_scored": 2,
        "num_judged": 2,
        "standard_score": standard_score,
        "standard_dataset_macro_score": standard_score,
        "llm_judge_score": judge_score,
        "llm_judge_dataset_macro_score": judge_score,
        "standard_coverage": 1.0,
        "judge_coverage": 1.0,
        "official_metric_coverage": 0.5,
        "direct_comparison_coverage": 0.5,
        "standard_judge_agreement_at_0_5": 1.0,
        "standard_judge_pearson": 1.0,
        "standard_judge_mean_absolute_gap": abs(standard_score - judge_score),
        "predictions_file": "predictions.jsonl",
        "scored_predictions_file": "predictions_dual.jsonl",
        "per_dataset": {},
    }


class SummaryTests(unittest.TestCase):
    def test_summary_and_module_comparison(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            order = root / "order.json"
            order.write_text(
                json.dumps({"trainable_order": ["a", "b"]}),
                encoding="utf-8",
            )

            result_root = root / "single" / "eval"
            values = {
                "1_a": [metric_row("a", 0.8, 0.9), metric_row("b", 0.4, 0.5)],
                "2_b": [metric_row("a", 0.6, 0.7), metric_row("b", 0.9, 0.8)],
            }
            for stage, rows in values.items():
                stage_dir = result_root / stage
                stage_dir.mkdir(parents=True)
                (stage_dir / "metrics_dual_all.json").write_text(
                    json.dumps(rows),
                    encoding="utf-8",
                )

            with patch.object(
                sys,
                "argv",
                [
                    "summarize",
                    "--result-root",
                    str(result_root),
                    "--order-json",
                    str(order),
                    "--factor-name",
                    "test_factor",
                ],
            ):
                self.assertEqual(summarizer.main(), 0)

            summary_dir = result_root / "summary_dual"
            self.assertTrue((summary_dir / "learning_matrices.md").is_file())
            with (summary_dir / "matrix_standard_score.csv").open(
                newline="",
                encoding="utf-8",
            ) as handle:
                matrix_rows = list(csv.DictReader(handle))
            self.assertEqual(float(matrix_rows[1]["a"]), 0.6)
            self.assertEqual(float(matrix_rows[1]["b"]), 0.9)

            result_base = root / "modules"
            for mode in ("llm_only", "vision_only"):
                target = result_base / mode / "eval" / "summary_dual"
                target.mkdir(parents=True)
                for metric in ("standard_score", "llm_judge_score"):
                    source = summary_dir / f"matrix_{metric}.csv"
                    (target / source.name).write_text(
                        source.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )

            output = result_base / "comparison_dual"
            with patch.object(
                sys,
                "argv",
                [
                    "compare",
                    "--result-base",
                    str(result_base),
                    "--output-dir",
                    str(output),
                    "--order-json",
                    str(order),
                    "--modes",
                    "llm_only",
                    "vision_only",
                ],
            ):
                self.assertEqual(comparator.main(), 0)
            self.assertTrue((output / "module_comparison_dual.md").is_file())
            payload = json.loads(
                (output / "module_comparison_dual.json").read_text(encoding="utf-8")
            )
            self.assertEqual(len(payload["summaries"]), 4)


if __name__ == "__main__":
    unittest.main()
