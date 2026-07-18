#!/usr/bin/env python3
"""Build support-aware balanced Factor-1 splits.

The raw Factor-1 metadata contains fine-grained labels, but not every label is
large enough to be a reliable continual-learning stage. This script turns the
full train.json into balanced factor benchmarks:

- trainable: enough support for balanced train/eval splits.
- eval_only: enough support for evaluation, but too small for training stages.
- tail_diagnostic: very small categories kept for auditing / data expansion.

All image paths are normalized for the existing LLaVA loader:
  Image.open(os.path.join(image_folder, item["image"]))
"""

from __future__ import annotations

import argparse
import json
import os
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_FACTORS = {
    "visual_substrate": "visual_substrate",
    "skill_requirement": "skill_type_primary",
    "evidence_complexity": "evidence_complexity",
    "answer_distribution": "answer_type",
}


DEFAULT_STAGE_ORDER = {
    "evidence_complexity": [
        "single_evidence",
        "multi_evidence",
        "cross_region_or_multihop",
        "cross_context",
    ],
    "skill_requirement": [
        "recognition",
        "attribute",
        "relation",
        "counting",
        "comparison",
        "text_reading",
        "chart_reasoning",
        "document_reasoning",
        "diagram_reasoning",
        "knowledge_reasoning",
        "medical_reasoning",
        "remote_sensing_reasoning",
    ],
    "visual_substrate": [
        "natural_photo",
        "chart",
        "document",
        "infographic",
        "diagram",
        "medical",
        "map",
        "remote_sensing",
        "screenshot",
        "synthetic",
        "academic_figure",
        "science_diagram",
        "other",
    ],
    "answer_distribution": [
        "yes_no",
        "number",
        "option",
        "text_span",
        "attribute",
        "object",
        "free_form",
    ],
}


def parse_include_categories(values: list[str]) -> dict[str, list[str]]:
    include: dict[str, list[str]] = {}
    for value in values or []:
        if "=" not in value:
            raise SystemExit(f"Invalid --include-categories value: {value}. Expected FACTOR=cat1,cat2")
        factor, categories = value.split("=", 1)
        factor = factor.strip()
        if factor not in DEFAULT_FACTORS:
            raise SystemExit(f"Unknown factor in --include-categories: {factor}")
        parsed = [c.strip() for c in categories.replace(";", ",").split(",") if c.strip()]
        if not parsed:
            raise SystemExit(f"No categories provided for factor: {factor}")
        include[factor] = parsed
    return include


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--train-json",
        type=Path,
        default=Path("cl_dataset/coin_factor1_train_v2/train.json"),
        help="Full Factor-1 LLaVA-format training JSON.",
    )
    p.add_argument(
        "--train-root",
        type=Path,
        default=Path("cl_dataset/coin_factor1_train_v2"),
        help="Root that contains images/ for the full Factor-1 training set.",
    )
    p.add_argument(
        "--image-folder",
        type=Path,
        default=Path("cl_dataset"),
        help="Image folder passed to LLaVA --image_folder.",
    )
    p.add_argument(
        "--output-root",
        type=Path,
        default=Path("cl_dataset/coin_factor1_balanced_v2"),
        help="Where balanced factor splits will be written.",
    )
    p.add_argument(
        "--factors",
        nargs="*",
        default=list(DEFAULT_FACTORS),
        choices=list(DEFAULT_FACTORS),
        help="Factors to build.",
    )
    p.add_argument(
        "--include-categories",
        action="append",
        default=[],
        metavar="FACTOR=CAT1,CAT2",
        help=(
            "Optional category allow-list for a factor. Repeat for multiple factors. "
            "Example: --include-categories visual_substrate=natural_photo,medical"
        ),
    )
    p.add_argument(
        "--strict-included-categories",
        action="store_true",
        help="Fail if any requested category cannot produce the requested train/eval split.",
    )
    p.add_argument("--train-samples-per-class", type=int, default=1000)
    p.add_argument("--eval-samples-per-class", type=int, default=300)
    p.add_argument(
        "--eval-only-samples-per-class",
        type=int,
        default=300,
        help="Max eval samples for categories with medium support.",
    )
    p.add_argument(
        "--tail-samples-per-class",
        type=int,
        default=200,
        help="Max samples kept for long-tail diagnostic categories.",
    )
    p.add_argument(
        "--min-train-support",
        type=int,
        default=3000,
        help="Minimum support for a factor category to become a trainable stage.",
    )
    p.add_argument(
        "--min-eval-support",
        type=int,
        default=500,
        help="Minimum support for eval_only categories.",
    )
    p.add_argument(
        "--balance-by",
        nargs="*",
        default=["dataset"],
        choices=["dataset", "regime", "visual_substrate", "skill_type_primary", "evidence_complexity", "answer_type"],
        help="Metadata fields used for stratified sampling inside each category.",
    )
    p.add_argument("--max-images-to-check", type=int, default=80)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--allow-text-only", action="store_true", default=True)
    p.add_argument(
        "--preserve-image-paths",
        action="store_true",
        help=(
            "Do not require local image files while building splits. Keep image paths "
            "as unresolved paths relative to --image-folder, derived from --train-root."
        ),
    )
    p.add_argument(
        "--compact",
        action="store_true",
        help="Write JSON without indentation to reduce disk usage.",
    )
    args = p.parse_args()
    args.include_category_map = parse_include_categories(args.include_categories)
    return args


def meta(row: dict[str, Any], key: str, default: str = "unknown") -> str:
    md = row.get("metadata") or {}
    return str(md.get(key) or row.get(key) or default)


def sample_id(row: dict[str, Any]) -> str:
    return str(row.get("id") or id(row))


def stratify_key(row: dict[str, Any], fields: list[str]) -> str:
    if not fields:
        return "all"
    return "||".join(meta(row, f) for f in fields)


def ordered_categories(factor: str, categories: list[str]) -> list[str]:
    preferred = DEFAULT_STAGE_ORDER.get(factor, [])
    preferred_set = set(preferred)
    ordered = [c for c in preferred if c in categories]
    ordered.extend(sorted(c for c in categories if c not in preferred_set))
    return ordered


def resolve_image(row: dict[str, Any], train_root: Path) -> Path | None:
    value = row.get("image")
    if not value:
        return None
    p = Path(value)
    candidates: list[Path] = []
    if p.is_absolute():
        candidates.append(p)
    candidates.append(train_root / p)
    candidates.append(train_root / p.name)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None


def unresolved_llava_image_path(row: dict[str, Any], train_root: Path, image_folder: Path) -> str | None:
    value = row.get("image")
    if not value:
        return None
    p = Path(str(value))
    if p.is_absolute():
        return str(p)
    unresolved = train_root / p
    return os.path.relpath(unresolved.resolve(strict=False), image_folder.resolve(strict=False))


def ensure_image_token(out: dict[str, Any]) -> None:
    first_human = next((m for m in out["conversations"] if m.get("from") == "human"), None)
    if first_human is not None and "<image>" not in str(first_human.get("value", "")):
        first_human["value"] = str(first_human.get("value", "")).strip() + "\n<image>"


def normalize_for_llava(
    row: dict[str, Any],
    train_root: Path,
    image_folder: Path,
    allow_text_only: bool,
    preserve_image_paths: bool,
) -> dict[str, Any]:
    out = dict(row)
    out["conversations"] = [dict(m) for m in row.get("conversations", [])]

    if preserve_image_paths and row.get("image"):
        out["image"] = unresolved_llava_image_path(row, train_root, image_folder)
        ensure_image_token(out)
        return out

    image_path = resolve_image(row, train_root)

    if row.get("image") and image_path is None:
        raise FileNotFoundError(f"Cannot resolve image for id={sample_id(row)}, image={row.get('image')}")

    if image_path is not None:
        out["image"] = os.path.relpath(image_path, image_folder.resolve())
        ensure_image_token(out)
    else:
        out.pop("image", None)
        if not allow_text_only:
            raise ValueError(f"Text-only sample is disabled: id={sample_id(row)}")
        for msg in out["conversations"]:
            if msg.get("from") == "human":
                msg["value"] = str(msg.get("value", "")).replace("<image>", "").strip()
    return out


def validate_images(rows: list[dict[str, Any]], image_folder: Path, max_images: int) -> int:
    if max_images <= 0:
        return 0
    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise SystemExit(f"Pillow is required for image verification: {exc}") from exc

    checked = 0
    for row in rows:
        image = row.get("image")
        if not image:
            continue
        if checked >= max_images:
            break
        path = image_folder / image
        if not path.exists():
            raise FileNotFoundError(f"Image does not exist under image_folder: {path}")
        with Image.open(path) as im:
            im.verify()
        checked += 1
    return checked


def stratified_take(
    rows: list[dict[str, Any]],
    n: int,
    rng: random.Random,
    balance_by: list[str],
    banned_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    banned_ids = banned_ids or set()
    pool = [r for r in rows if sample_id(r) not in banned_ids]
    if n <= 0 or not pool:
        return []
    if len(pool) <= n:
        shuffled = list(pool)
        rng.shuffle(shuffled)
        return shuffled

    buckets: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in pool:
        buckets[stratify_key(row, balance_by)].append(row)

    selected: list[dict[str, Any]] = []
    bucket_names = sorted(buckets)
    quota = max(1, n // max(1, len(bucket_names)))

    for name in bucket_names:
        bucket = list(buckets[name])
        rng.shuffle(bucket)
        selected.extend(bucket[:quota])

    if len(selected) < n:
        selected_ids = {sample_id(r) for r in selected}
        rest = [r for r in pool if sample_id(r) not in selected_ids]
        rng.shuffle(rest)
        selected.extend(rest[: n - len(selected)])

    selected = selected[:n]
    rng.shuffle(selected)
    return selected


def split_category(
    rows: list[dict[str, Any]],
    status: str,
    args: argparse.Namespace,
    factor_seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    rng = random.Random(factor_seed)
    shuffled = list(rows)
    rng.shuffle(shuffled)

    if status == "trainable":
        eval_rows = stratified_take(
            shuffled,
            args.eval_samples_per_class,
            random.Random(factor_seed + 11),
            args.balance_by,
        )
        eval_ids = {sample_id(r) for r in eval_rows}
        train_rows = stratified_take(
            shuffled,
            args.train_samples_per_class,
            random.Random(factor_seed + 23),
            args.balance_by,
            banned_ids=eval_ids,
        )
        return train_rows, eval_rows, []

    if status == "eval_only":
        eval_rows = stratified_take(
            shuffled,
            min(args.eval_only_samples_per_class, len(shuffled)),
            random.Random(factor_seed + 31),
            args.balance_by,
        )
        return [], eval_rows, []

    diagnostic_rows = stratified_take(
        shuffled,
        min(args.tail_samples_per_class, len(shuffled)),
        random.Random(factor_seed + 43),
        args.balance_by,
    )
    return [], [], diagnostic_rows


def category_status(count: int, args: argparse.Namespace) -> str:
    required_for_balanced = args.train_samples_per_class + args.eval_samples_per_class
    if count >= args.min_train_support and count >= required_for_balanced:
        return "trainable"
    if count >= args.min_eval_support:
        return "eval_only"
    return "tail_diagnostic"


def write_json(path: Path, rows: list[dict[str, Any]], compact: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        if compact:
            json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
        else:
            json.dump(rows, f, ensure_ascii=False, indent=2)


def summarize_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "samples": len(rows),
        "with_image": sum(1 for r in rows if r.get("image")),
        "text_only": sum(1 for r in rows if not r.get("image")),
        "by_dataset": dict(Counter(meta(r, "dataset") for r in rows).most_common()),
        "by_regime": dict(Counter(meta(r, "regime") for r in rows).most_common()),
        "by_visual_substrate": dict(Counter(meta(r, "visual_substrate") for r in rows).most_common()),
        "by_skill_requirement": dict(Counter(meta(r, "skill_type_primary") for r in rows).most_common()),
        "by_evidence_complexity": dict(Counter(meta(r, "evidence_complexity") for r in rows).most_common()),
        "by_answer_distribution": dict(Counter(meta(r, "answer_type") for r in rows).most_common()),
    }


def main() -> int:
    args = parse_args()
    train_json = args.train_json.resolve()
    train_root = args.train_root.resolve()
    image_folder = args.image_folder.resolve()
    output_root = args.output_root.resolve()

    rows = json.loads(train_json.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"Invalid or empty train JSON: {train_json}")

    normalized_cache: dict[str, dict[str, Any]] = {}

    def normalized(row: dict[str, Any]) -> dict[str, Any]:
        sid = sample_id(row)
        if sid not in normalized_cache:
            normalized_cache[sid] = normalize_for_llava(
                row,
                train_root,
                image_folder,
                args.allow_text_only,
                args.preserve_image_paths,
            )
        return normalized_cache[sid]

    manifest: dict[str, Any] = {
        "source_train_json": str(train_json),
        "train_root": str(train_root),
        "image_folder": str(image_folder),
        "output_root": str(output_root),
        "policy": {
            "min_train_support": args.min_train_support,
            "min_eval_support": args.min_eval_support,
            "train_samples_per_class": args.train_samples_per_class,
            "eval_samples_per_class": args.eval_samples_per_class,
            "eval_only_samples_per_class": args.eval_only_samples_per_class,
            "tail_samples_per_class": args.tail_samples_per_class,
            "balance_by": args.balance_by,
            "seed": args.seed,
            "include_categories": args.include_category_map,
            "strict_included_categories": args.strict_included_categories,
            "preserve_image_paths": args.preserve_image_paths,
        },
        "source_summary": summarize_rows([normalized(r) for r in rows[: min(len(rows), 1000)]]),
        "factors": {},
    }

    for factor_index, factor in enumerate(args.factors, 1):
        field = DEFAULT_FACTORS[factor]
        factor_dir = output_root / factor
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            groups[meta(row, field)].append(row)
        requested_categories = args.include_category_map.get(factor)
        categories_to_process = (
            requested_categories
            if requested_categories is not None
            else ordered_categories(factor, list(groups))
        )
        if requested_categories is not None:
            missing = [category for category in requested_categories if category not in groups]
            if missing:
                print(f"[warn] {factor}: requested categories not found in source data: {', '.join(missing)}")
            if args.strict_included_categories:
                required = args.train_samples_per_class + args.eval_samples_per_class
                insufficient = [
                    f"{category}={len(groups.get(category, []))}/{required}"
                    for category in requested_categories
                    if len(groups.get(category, [])) < required
                ]
                if insufficient:
                    raise SystemExit(
                        f"[{factor}] insufficient samples for strict target split: "
                        + ", ".join(insufficient)
                    )

        category_summaries: list[dict[str, Any]] = []
        trainable_order: list[str] = []
        eval_only_order: list[str] = []
        tail_order: list[str] = []

        for category_index, category in enumerate(categories_to_process, 1):
            source_rows = groups.get(category, [])
            status = category_status(len(source_rows), args)
            seed = args.seed + factor_index * 10000 + category_index * 100
            train_rows, eval_rows, diagnostic_rows = split_category(source_rows, status, args, seed)
            train_rows = [normalized(r) for r in train_rows]
            eval_rows = [normalized(r) for r in eval_rows]
            diagnostic_rows = [normalized(r) for r in diagnostic_rows]

            split_summary: dict[str, Any] = {
                "category": category,
                "source_count": len(source_rows),
                "status": status,
            }

            if train_rows:
                out = factor_dir / "trainable" / "train" / category / "train.json"
                write_json(out, train_rows, args.compact)
                checked = validate_images(train_rows, image_folder, args.max_images_to_check)
                split_summary["train"] = {**summarize_rows(train_rows), "path": str(out), "images_checked": checked}

            if eval_rows:
                kind = "trainable" if status == "trainable" else "eval_only"
                out = factor_dir / kind / "eval" / category / "eval.json"
                write_json(out, eval_rows, args.compact)
                checked = validate_images(eval_rows, image_folder, args.max_images_to_check)
                split_summary["eval"] = {**summarize_rows(eval_rows), "path": str(out), "images_checked": checked}

            if diagnostic_rows:
                out = factor_dir / "tail_diagnostic" / category / "diagnostic.json"
                write_json(out, diagnostic_rows, args.compact)
                checked = validate_images(diagnostic_rows, image_folder, args.max_images_to_check)
                split_summary["diagnostic"] = {
                    **summarize_rows(diagnostic_rows),
                    "path": str(out),
                    "images_checked": checked,
                }

            if status == "trainable":
                trainable_order.append(category)
            elif status == "eval_only":
                eval_only_order.append(category)
            else:
                tail_order.append(category)
            category_summaries.append(split_summary)

        transition = {
            "factor": factor,
            "field": field,
            "trainable_order": trainable_order,
            "eval_only_categories": eval_only_order,
            "tail_diagnostic_categories": tail_order,
        }
        (factor_dir / "transition_order.json").parent.mkdir(parents=True, exist_ok=True)
        (factor_dir / "transition_order.json").write_text(json.dumps(transition, ensure_ascii=False, indent=2), encoding="utf-8")

        manifest["factors"][factor] = {
            "field": field,
            "trainable_categories": trainable_order,
            "eval_only_categories": eval_only_order,
            "tail_diagnostic_categories": tail_order,
            "categories": category_summaries,
        }

        print(f"[{factor}] trainable={len(trainable_order)} eval_only={len(eval_only_order)} tail={len(tail_order)}")
        if trainable_order:
            print(f"  trainable: {', '.join(trainable_order)}")
        if eval_only_order:
            print(f"  eval_only: {', '.join(eval_only_order)}")
        if tail_order:
            print(f"  tail: {', '.join(tail_order)}")

    output_root.mkdir(parents=True, exist_ok=True)
    manifest_path = output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote balanced factor manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
