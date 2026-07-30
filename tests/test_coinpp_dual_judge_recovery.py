#!/usr/bin/env python3
"""Regression tests for local Judge key and singleton response recovery."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_coinpp_dual as dual


class JudgeRecoveryTests(unittest.TestCase):
    def test_singleton_wrong_key_is_rebound(self) -> None:
        result = dual.normalize_judge_results(
            {"results": [{"key": "rewritten-key", "score": 8, "reason": "ok"}]},
            expected_keys=["s0"],
        )
        self.assertEqual(set(result), {"s0"})
        self.assertEqual(result["s0"]["score"], 0.8)

    def test_singleton_missing_key_is_rebound(self) -> None:
        result = dual.normalize_judge_results(
            {"results": [{"score": 9}]},
            expected_keys=["s0"],
        )
        self.assertEqual(result["s0"]["raw_score_0_10"], 9.0)

    def test_singleton_scalar_payload_is_accepted(self) -> None:
        result = dual.normalize_judge_results(7, expected_keys=["s0"])
        self.assertEqual(result["s0"]["score"], 0.7)

    def test_batch_does_not_guess_missing_key_assignments(self) -> None:
        result = dual.normalize_judge_results(
            {"results": [{"score": 10}, {"score": 0}]},
            expected_keys=["s0", "s1"],
        )
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
