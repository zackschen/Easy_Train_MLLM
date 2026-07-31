#!/usr/bin/env python3
"""Send one CoIN++ scalar-evaluation request to a Judge server."""

from __future__ import annotations

import argparse
import json
import os
from types import SimpleNamespace

from evaluate_coinpp_dual import (
    COIN_JUDGE_PROMPT,
    JUDGE_PROMPT_VERSION,
    judge_references_for_row,
    judge_single_request,
    judge_user_content,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base-url",
        default=os.environ.get("JUDGE_BASE_URL", "http://127.0.0.1:8001/v1"),
    )
    parser.add_argument("--api-key", default=os.environ.get("JUDGE_API_KEY", "EMPTY"))
    parser.add_argument("--model", default=os.environ.get("JUDGE_MODEL", "qwen3.6"))
    parser.add_argument("--dataset", default="textvqa")
    parser.add_argument(
        "--question",
        default="Does having your fingers pricked mean you have diabetes?",
    )
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Reference answer; repeat for multiple references.",
    )
    parser.add_argument("--candidate", default="no")
    parser.add_argument("--timeout", type=float, default=180.0)
    parser.add_argument("--show-prompt", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    original_references = args.reference or ["no"]
    references, ignored_references, reference_policy = judge_references_for_row(
        original_references,
        args.dataset,
    )
    sample = {
        "judge_key": "probe",
        "row": {
            "question": args.question,
            "pred": args.candidate,
        },
        "references": references,
    }
    request_args = SimpleNamespace(
        judge_base_url=args.base_url,
        judge_api_key=args.api_key,
        judge_model=args.model,
        judge_timeout=args.timeout,
    )

    print(f"prompt_version={JUDGE_PROMPT_VERSION}")
    print(f"model={args.model} endpoint={args.base_url.rstrip('/')}/chat/completions")
    print(
        f"reference_policy={reference_policy} "
        f"kept={len(references)} ignored={len(ignored_references)}"
    )
    if ignored_references:
        print("ignored_references=" + json.dumps(ignored_references, ensure_ascii=False))
    if args.show_prompt:
        print("\n[SYSTEM]\n" + COIN_JUDGE_PROMPT)
        print("\n[USER]\n" + judge_user_content(sample, args.model))
    result = judge_single_request(sample, request_args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
