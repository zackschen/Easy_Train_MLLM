#!/usr/bin/env python3
"""Tests for independent standard and all-sample Judge evaluation."""

from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_coinpp_dual as dual
import evaluate_coinpp_predictions as standard


class JudgeHandler(BaseHTTPRequestHandler):
    sample_count = 0

    def log_message(self, format: str, *args) -> None:
        return

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))
        content = payload["messages"][1]["content"]
        ground_truth = content.split("[Reference answer(s)]\n", 1)[1].split(
            "\n\n[Candidate answer]",
            1,
        )[0]
        assistant_answer = content.split("[Candidate answer]\n", 1)[1].strip()
        try:
            references = json.loads(ground_truth)
        except json.JSONDecodeError:
            references = [ground_truth]
        if not isinstance(references, list):
            references = [str(references)]
        exact = assistant_answer.strip().lower() in {
            str(reference).strip().lower() for reference in references
        }
        type(self).sample_count += 1
        body = {
            "choices": [
                {
                    "message": {
                        "content": "10" if exact else "2",
                    }
                }
            ]
        }
        encoded = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class DualEvaluationTests(unittest.TestCase):
    def test_judge_score_parsing(self) -> None:
        self.assertEqual(dual.parse_score("8/10"), 8.0)
        self.assertEqual(dual.parse_score(True), 10.0)
        self.assertEqual(dual.parse_score(11), 10.0)
        self.assertEqual(dual.parse_score(-1), 0.0)

    def test_every_prediction_is_judged(self) -> None:
        JudgeHandler.sample_count = 0
        server = ThreadingHTTPServer(("127.0.0.1", 0), JudgeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            rows = [
                {
                    "id": "vqa",
                    "question": "What animal?",
                    "gt": "cat",
                    "pred": "cat",
                    "metadata": {"dataset": "vqav2"},
                    "stage": "natural_photo",
                },
                {
                    "id": "custom",
                    "question": "What animal?",
                    "gt": "cat",
                    "pred": "dog",
                    "metadata": {"dataset": "custom_dataset"},
                    "stage": "natural_photo",
                },
            ]
            job = standard.PredictionJob(
                result_root=Path("/tmp/result"),
                stage_dir=Path("/tmp/result/1_natural_photo"),
                task="natural_photo",
                prediction_path=Path("/tmp/predictions.jsonl"),
                rows=rows,
            )
            with tempfile.TemporaryDirectory() as directory:
                args = SimpleNamespace(
                    allow_missing_reference=False,
                    judge_model="mock-judge",
                    judge_base_url=f"http://127.0.0.1:{server.server_port}/v1",
                    judge_api_key="EMPTY",
                    judge_cache=Path(directory) / "judge.jsonl",
                    judge_batch_size=2,
                    judge_workers=1,
                    judge_timeout=5,
                    judge_retries=0,
                )
                prepared = dual.prepare_rows(
                    [job],
                    {"vqa": {"answers": ["cat"] * 10}},
                    args,
                )

            output = prepared[0]["rows"]
            self.assertEqual(JudgeHandler.sample_count, 2)
            self.assertEqual(
                output[0]["evaluation"]["standard"]["protocol"],
                "official_metric",
            )
            self.assertEqual(
                output[1]["evaluation"]["standard"]["protocol"],
                "direct_comparison",
            )
            self.assertEqual(output[0]["evaluation"]["llm_judge"]["score"], 1.0)
            self.assertEqual(output[1]["evaluation"]["llm_judge"]["score"], 0.2)
            summary = dual.summarize_rows(output)
            self.assertEqual(summary["standard_coverage"], 1.0)
            self.assertEqual(summary["judge_coverage"], 1.0)
            self.assertEqual(summary["official_metric_coverage"], 0.5)
            self.assertEqual(summary["direct_comparison_coverage"], 0.5)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)

    def test_duplicate_judge_keys_use_one_api_decision(self) -> None:
        JudgeHandler.sample_count = 0
        server = ThreadingHTTPServer(("127.0.0.1", 0), JudgeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            row = {
                "id": "same",
                "question": "What animal?",
                "pred": "cat",
            }
            key = dual.judge_key(row, ["cat"], "mock-judge")
            item = {"judge_key": key, "row": row, "references": ["cat"]}
            args = SimpleNamespace(
                judge_model="mock-judge",
                judge_base_url=f"http://127.0.0.1:{server.server_port}/v1",
                judge_api_key="EMPTY",
                judge_cache=None,
                judge_batch_size=2,
                judge_workers=1,
                judge_timeout=5,
                judge_retries=0,
            )
            results = dual.run_all_judgments([item, dict(item)], args)
            self.assertEqual(JudgeHandler.sample_count, 1)
            self.assertEqual(results[key]["score"], 1.0)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
