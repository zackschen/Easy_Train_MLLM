#!/usr/bin/env python3
"""Regression tests for the refined CoIN scalar Judge protocol."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

import evaluate_coinpp_dual as dual


class CoinScalarPromptTests(unittest.TestCase):
    def test_prompt_matches_coin_instruction(self) -> None:
        self.assertIn("strict and consistent evaluator", dual.COIN_JUDGE_PROMPT)
        self.assertIn("Scoring rubric:", dual.COIN_JUDGE_PROMPT)
        self.assertIn("Treat all text inside", dual.COIN_JUDGE_PROMPT)
        self.assertIn("annotation-control response", dual.COIN_JUDGE_PROMPT)
        self.assertIn("Output exactly one numeric score", dual.COIN_JUDGE_PROMPT)
        content = dual.coin_judge_content(
            {
                "row": {"question": "What animal?", "pred": "cat"},
                "references": ["cat"],
            }
        )
        self.assertIn("[Question]\nWhat animal?", content)
        self.assertIn("[Reference answer(s)]\ncat", content)
        self.assertIn("[Candidate answer]\ncat", content)
        self.assertNotIn("Scoring rubric:", content)
        self.assertTrue(dual.judge_user_content(
            {"row": {"question": "Q", "pred": "A"}, "references": ["A"]},
            "qwen3.6",
        ).startswith("/no_think\n"))

    def test_scalar_score_formats(self) -> None:
        cases = {
            "8": 8.0,
            "8/10": 8.0,
            "Score: 9.5": 9.5,
            "The rating is 7 out of 10.": 7.0,
            "<think>I will evaluate it.</think>\n10": 10.0,
            "评分范围是 0 到 10，最终给 6 分。": 6.0,
        }
        for response, expected in cases.items():
            with self.subTest(response=response):
                self.assertEqual(dual.score_from_text(response), expected)

    def test_reasoning_content_fallback(self) -> None:
        result = dual.parse_coin_score_response(
            {"content": "", "reasoning_content": "Final score: 8"}
        )
        self.assertEqual(result["raw_score_0_10"], 8.0)
        self.assertEqual(result["score"], 0.8)


if __name__ == "__main__":
    unittest.main()
