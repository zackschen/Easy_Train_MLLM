#!/usr/bin/env python3
"""Focused tests for the CoIN++ dataset-native evaluation pipeline."""

from __future__ import annotations

import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from types import SimpleNamespace


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_coinpp_predictions as evaluator


class MetricTests(unittest.TestCase):
    def test_vqa_soft_accuracy(self) -> None:
        self.assertEqual(evaluator.vqa_soft_accuracy("cat", ["cat"] * 10), 1.0)
        self.assertEqual(evaluator.vqa_soft_accuracy("dog", ["cat"] * 10), 0.0)

    def test_anls(self) -> None:
        self.assertEqual(evaluator.anls_single("hello", "hello"), 1.0)
        self.assertEqual(evaluator.anls_single("x", "hello"), 0.0)

    def test_chartqa_relaxed_accuracy(self) -> None:
        self.assertEqual(evaluator.chartqa_relaxed_accuracy("104", ["100"]), 1.0)
        self.assertEqual(evaluator.chartqa_relaxed_accuracy("106", ["100"]), 0.0)
        self.assertEqual(evaluator.chartqa_relaxed_accuracy("50%", ["0.5"]), 1.0)

    def test_multiple_choice_and_count(self) -> None:
        self.assertEqual(
            evaluator.multiple_choice_accuracy(
                "Answer: B",
                ["food"],
                ["boat", "food", "car"],
            ),
            1.0,
        )
        self.assertEqual(evaluator.count_accuracy("Two.", ["2"]), 1.0)

    def test_native_vqa_requires_full_annotations(self) -> None:
        row = {
            "id": "sample",
            "question": "What is shown?",
            "gt": "cat",
            "pred": "cat",
            "metadata": {"dataset": "vqav2"},
        }
        score, reason = evaluator.score_native(row, None)
        self.assertIsNone(score)
        self.assertEqual(reason, "vqav2_requires_10_human_answers")

        annotation = {"answers": ["cat"] * 10}
        score, reason = evaluator.score_native(row, annotation)
        self.assertIsNone(reason)
        self.assertEqual(score["metric"], "vqa_soft_accuracy")
        self.assertEqual(score["primary_score"], 1.0)


class JudgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        return

    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        payload = json.loads(self.rfile.read(length))
        samples = json.loads(payload["messages"][1]["content"].split("\n", 1)[1])
        results = [
            {
                "key": sample["key"],
                "correct": sample["candidate_answer"].lower()
                == sample["reference_answers"][0].lower(),
                "reason": "mock decision",
            }
            for sample in samples
        ]
        response = {
            "choices": [
                {
                    "message": {
                        "content": "```json\n"
                        + json.dumps({"results": results})
                        + "\n```"
                    }
                }
            ]
        }
        encoded = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)


class JudgeTests(unittest.TestCase):
    def test_openai_compatible_judge_request(self) -> None:
        server = HTTPServer(("127.0.0.1", 0), JudgeHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            args = SimpleNamespace(
                judge_base_url=f"http://127.0.0.1:{server.server_port}/v1",
                judge_api_key="EMPTY",
                judge_model="mock-judge",
                judge_timeout=5,
            )
            samples = [
                {
                    "judge_key": "correct-key",
                    "row": {
                        "question": "What animal?",
                        "pred": "cat",
                    },
                    "references": ["cat"],
                },
                {
                    "judge_key": "wrong-key",
                    "row": {
                        "question": "What animal?",
                        "pred": "dog",
                    },
                    "references": ["cat"],
                },
            ]
            results = evaluator.judge_request(samples, args)
            self.assertTrue(results["correct-key"]["correct"])
            self.assertFalse(results["wrong-key"]["correct"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
