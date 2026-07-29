#!/usr/bin/env python3
"""Check final Factor-1 train JSON distribution and 10k split readiness.

This script is intended for the final merged/canonicalized LLaVA-format dataset,
for example:
  cl_dataset/coin_factor1_train_v6_diagram_skill_canonical/train.json

It reports:
  - total / image / text-only / duplicate-id statistics
  - distribution by dataset, regime, visual substrate, skill, evidence, answer
  - whether selected target categories satisfy train+eval support requirements
  - optional existence/size checks for already-built strict split directories
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

FACTOR_FIELDS = {
    "visual_substrate": "visual_substrate",
    "skill_requirement": "skill_type_primary",
    "evidence_complexity": "evidence_complexity",
    "answer_distribution": "answer_type",
}

DEFAULT_TARGETS = {
    "visual_substrate": ["natural_photo", "medical", "document", "infographic", "diagram", "chart"],
    "skill_requirement": [
        "recognition",
        "counting",
        "medical_reasoning",
        "knowledge_reasoning",
        "chart_reasoning",
        "document_reasoning",
        "text_reading",
        "diagram_reasoning",
        "relation",
        "attribute",
    ],
    "evidence_complexity": ["single_evidence", "multi_evidence", "cross_region_or_multihop", "cross_context"],
}

DEFAULT_STAGE_ORDER = {
    "evidence_complexity": ["single_evidence", "multi_evidence", "cross_region_or_multihop", "cross_context"],
    "skill_requirement": [
        "recognition",
        "counting",
        "medical_reasoning",
        "knowledge_reasoning",
        "chart_reasoning",
        "document_reasoning",
        "text_reading",
        "diagram_reasoning",
        "relation",
        "attribute",
    ],
    "visual_substrate": ["natural_photo", "medical", "document", "infographic", "diagram", "chart"],
}


def load_rows(path: Path) -> list[dict[str, Any]]:
    if path.suffix == ".jsonl":
        rows = []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
        return rows
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array or JSONL: {path}")
    return data


def md(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("metadata")
    return value if isinstance(value, dict) else {}


def get_value(row: dict[str, Any], key: str, default: str = "unknown") -> str:
    value = md(row).get(key, row.get(key, default))
    if value is None or value == "":
        return default
    return str(value)


def sample_id(row: dict[str, Any]) -> str:
    return str(row.get("id") or "")


def pct(n: int, total: int) -> float:
    return round(n * 100 / total, 4) if total else 0.0


def count_by(rows: list[dict[str, Any]], key: str) -> Counter[str]:
    return Counter(get_value(row, key) for row in rows)


def parse_target_arg(values: list[str]) -> dict[str, list[str]]:
    targets = {factor: list(categories) for factor, categories in DEFAULT_TARGETS.items()}
    for value in values or []:
        if "=" not in value:
            raise SystemExit(f"Invalid --targets {value!r}. Expected factor=cat1,cat2")
        factor, cats = value.split("=", 1)
        factor = factor.strip()
        if factor not in FACTOR_FIELDS:
            raise SystemExit(f"Unknown factor in --targets: {factor}")
        parsed = [item.strip() for item in cats.replace(";", ",").split(",") if item.strip()]
        if not parsed:
            raise SystemExit(f"No categories for --targets {value!r}")
        targets[factor] = parsed
    return targets


def table_lines(rows: list[list[Any]]) -> list[str]:
    if not rows:
        return []
    header = rows[0]
    lines = ["| " + " | ".join(str(x) for x in header) + " |"]
    lines.append("|" + "|".join("---" for _ in header) + "|")
    for row in rows[1:]:
        lines.append("| " + " | ".join(str(x) for x in row) + " |")
    return lines


def counter_table(counter: Counter[str], total: int, limit: int | None = None) -> list[list[Any]]:
    rows: list[list[Any]] = [["label", "count", "ratio"]]
    items = counter.most_common(limit)
    for label, count in items:
        rows.append([f"`{label}`", count, f"{pct(count, total)}%"])
    return rows


def summarize_basic(rows: list[dict[str, Any]]) -> dict[str, Any]:
    ids = [sample_id(row) for row in rows if sample_id(row)]
    id_counts = Counter(ids)
    duplicate_ids = {sid: count for sid, count in id_counts.items() if count > 1}
    image_count = sum(1 for row in rows if row.get("image"))
    canonicalized = sum(1 for row in rows if isinstance(md(row).get("canonicalization"), dict))
    return {
        "samples": len(rows),
        "with_image": image_count,
        "text_only": len(rows) - image_count,
        "unique_ids": len(id_counts),
        "duplicate_id_count": len(duplicate_ids),
        "duplicate_rows_extra": sum(count - 1 for count in duplicate_ids.values()),
        "canonicalized_samples": canonicalized,
        "top_duplicate_ids": dict(Counter(duplicate_ids).most_common(20)),
    }


def build_sufficiency(rows: list[dict[str, Any]], targets: dict[str, list[str]], required: int) -> list[dict[str, Any]]:
    result = []
    for factor, categories in targets.items():
        field = FACTOR_FIELDS[factor]
        counts = count_by(rows, field)
        for category in categories:
            count = counts.get(category, 0)
            result.append(
                {
                    "factor": factor,
                    "category": category,
                    "count": count,
                    "required": required,
                    "gap": max(0, required - count),
                    "surplus": max(0, count - required),
                    "status": "OK" if count >= required else "SHORT",
                }
            )
    return result


def image_prefix(value: Any) -> str:
    if not value:
        return "text_only"
    text = str(value)
    if text.startswith("/"):
        parts = Path(text).parts
        return "/".join(parts[:4]) if len(parts) >= 4 else text
    parts = text.split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 else text


def inspect_images(rows: list[dict[str, Any]], image_folder: Path | None, max_missing: int) -> dict[str, Any]:
    prefixes = Counter(image_prefix(row.get("image")) for row in rows)
    image_rows = [row for row in rows if row.get("image")]
    result: dict[str, Any] = {
        "image_prefixes": dict(prefixes.most_common()),
        "checked": 0,
        "missing_count": 0,
        "missing_examples": [],
    }
    if image_folder is None:
        result["check_status"] = "skipped_no_image_folder"
        return result
    image_folder = image_folder.resolve()
    missing_examples = []
    missing_count = 0
    checked = 0
    for row in image_rows:
        image = str(row.get("image") or "")
        if not image:
            continue
        path = Path(image) if image.startswith("/") else image_folder / image
        checked += 1
        if not path.exists():
            missing_count += 1
            if len(missing_examples) < max_missing:
                missing_examples.append({"id": sample_id(row), "image": image, "expected_path": str(path)})
    result["checked"] = checked
    result["missing_count"] = missing_count
    result["missing_examples"] = missing_examples
    result["check_status"] = "ok" if missing_count == 0 else "missing_images"
    return result


def inspect_split_root(split_root: Path, targets: dict[str, list[str]]) -> list[dict[str, Any]]:
    rows = []
    if not split_root:
        return rows
    for factor, categories in targets.items():
        for category in categories:
            train_path = split_root / factor / "trainable" / "train" / category / "train.json"
            eval_path = split_root / factor / "trainable" / "eval" / category / "eval.json"
            entry = {
                "factor": factor,
                "category": category,
                "train_path": str(train_path),
                "eval_path": str(eval_path),
                "train_exists": train_path.exists(),
                "eval_exists": eval_path.exists(),
                "train_count": None,
                "eval_count": None,
            }
            if train_path.exists():
                entry["train_count"] = len(load_rows(train_path))
            if eval_path.exists():
                entry["eval_count"] = len(load_rows(eval_path))
            rows.append(entry)
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--train-json", type=Path, required=True)
    p.add_argument("--output-root", type=Path, default=None)
    p.add_argument("--split-root", type=Path, default=None, help="Optional built strict split root to inspect.")
    p.add_argument("--image-folder", type=Path, default=None, help="Optional LLaVA --image_folder used to verify image paths.")
    p.add_argument("--max-missing-images", type=int, default=50, help="Max missing image examples saved in reports.")
    p.add_argument("--train-samples-per-class", type=int, default=10000)
    p.add_argument("--eval-samples-per-class", type=int, default=1000)
    p.add_argument("--targets", action="append", default=[], help="Override targets: factor=cat1,cat2. Repeatable.")
    p.add_argument("--top-combos", type=int, default=30)
    p.add_argument("--top-limit", type=int, default=None)
    args = p.parse_args()

    train_json = args.train_json.resolve()
    output_root = args.output_root.resolve() if args.output_root else train_json.parent
    split_root = args.split_root.resolve() if args.split_root else None
    image_folder = args.image_folder.resolve() if args.image_folder else None
    output_root.mkdir(parents=True, exist_ok=True)

    rows = load_rows(train_json)
    total = len(rows)
    required = args.train_samples_per_class + args.eval_samples_per_class
    targets = parse_target_arg(args.targets)

    basic = summarize_basic(rows)
    distributions: dict[str, dict[str, int]] = {
        "dataset": dict(count_by(rows, "dataset").most_common()),
        "regime": dict(count_by(rows, "regime").most_common()),
        "media_source": dict(count_by(rows, "media_source").most_common()),
    }
    for factor, field in FACTOR_FIELDS.items():
        distributions[factor] = dict(count_by(rows, field).most_common())

    visual_skill = Counter((get_value(row, "visual_substrate"), get_value(row, "skill_type_primary")) for row in rows)
    factor_combo = Counter(
        (
            get_value(row, "visual_substrate"),
            get_value(row, "skill_type_primary"),
            get_value(row, "evidence_complexity"),
        )
        for row in rows
    )
    sufficiency = build_sufficiency(rows, targets, required)
    split_checks = inspect_split_root(split_root, targets) if split_root else []
    image_checks = inspect_images(rows, image_folder, args.max_missing_images)

    summary = {
        "train_json": str(train_json),
        "output_root": str(output_root),
        "split_root": str(split_root) if split_root else None,
        "image_folder": str(image_folder) if image_folder else None,
        "required_per_category": required,
        "train_samples_per_class": args.train_samples_per_class,
        "eval_samples_per_class": args.eval_samples_per_class,
        "basic": basic,
        "distributions": distributions,
        "target_sufficiency": sufficiency,
        "split_checks": split_checks,
        "image_checks": image_checks,
        "top_visual_skill": [
            {"visual_substrate": v, "skill_requirement": s, "count": c}
            for (v, s), c in visual_skill.most_common(args.top_combos)
        ],
        "top_visual_skill_evidence": [
            {"visual_substrate": v, "skill_requirement": s, "evidence_complexity": e, "count": c}
            for (v, s, e), c in factor_combo.most_common(args.top_combos)
        ],
    }

    json_path = output_root / "factor1_final_distribution.json"
    md_path = output_root / "factor1_final_distribution.md"
    suff_csv = output_root / "factor1_target_sufficiency.csv"
    split_csv = output_root / "factor1_split_check.csv"
    missing_csv = output_root / "factor1_missing_images.csv"

    json_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_csv(suff_csv, sufficiency)
    if split_checks:
        write_csv(split_csv, split_checks)
    if image_checks.get("missing_examples"):
        write_csv(missing_csv, image_checks["missing_examples"])

    lines: list[str] = []
    lines.append("# Factor-1 Final Distribution Check")
    lines.append("")
    lines.append(f"- train_json: `{train_json}`")
    lines.append(f"- samples: {basic['samples']}")
    lines.append(f"- with_image: {basic['with_image']}")
    lines.append(f"- text_only: {basic['text_only']}")
    lines.append(f"- duplicate_id_count: {basic['duplicate_id_count']}")
    lines.append(f"- canonicalized_samples: {basic['canonicalized_samples']}")
    lines.append(f"- image_check_status: {image_checks['check_status']}")
    lines.append(f"- image_checked: {image_checks['checked']}")
    lines.append(f"- missing_images: {image_checks['missing_count']}")
    lines.append(f"- required_per_target_category: {required}")
    lines.append("")

    lines.append("## Target Sufficiency")
    rows_table: list[list[Any]] = [["factor", "category", "count", "required", "gap", "status"]]
    for item in sufficiency:
        status = "OK" if item["status"] == "OK" else f"SHORT {item['gap']}"
        rows_table.append([f"`{item['factor']}`", f"`{item['category']}`", item["count"], item["required"], item["gap"], status])
    lines.extend(table_lines(rows_table))
    lines.append("")

    for name in ["visual_substrate", "skill_requirement", "evidence_complexity", "answer_distribution", "dataset", "regime", "media_source"]:
        lines.append(f"## {name}")
        lines.extend(table_lines(counter_table(Counter(distributions[name]), total, args.top_limit)))
        lines.append("")

    lines.append("## Image Prefixes")
    lines.extend(table_lines(counter_table(Counter(image_checks["image_prefixes"]), total, args.top_limit)))
    lines.append("")

    if image_checks.get("missing_examples"):
        lines.append("## Missing Image Examples")
        missing_rows: list[list[Any]] = [["id", "image", "expected_path"]]
        for item in image_checks["missing_examples"]:
            missing_rows.append([f"`{item.get('id')}`", f"`{item.get('image')}`", f"`{item.get('expected_path')}`"])
        lines.extend(table_lines(missing_rows))
        lines.append("")

    lines.append("## Top Visual-Skill Combos")
    combo_rows: list[list[Any]] = [["visual", "skill", "count"]]
    for item in summary["top_visual_skill"]:
        combo_rows.append([f"`{item['visual_substrate']}`", f"`{item['skill_requirement']}`", item["count"]])
    lines.extend(table_lines(combo_rows))
    lines.append("")

    lines.append("## Top Visual-Skill-Evidence Combos")
    combo3_rows: list[list[Any]] = [["visual", "skill", "evidence", "count"]]
    for item in summary["top_visual_skill_evidence"]:
        combo3_rows.append([
            f"`{item['visual_substrate']}`",
            f"`{item['skill_requirement']}`",
            f"`{item['evidence_complexity']}`",
            item["count"],
        ])
    lines.extend(table_lines(combo3_rows))
    lines.append("")

    if split_checks:
        lines.append("## Built Split Check")
        split_rows: list[list[Any]] = [["factor", "category", "train_exists", "train_count", "eval_exists", "eval_count"]]
        for item in split_checks:
            split_rows.append([
                f"`{item['factor']}`",
                f"`{item['category']}`",
                item["train_exists"],
                item["train_count"],
                item["eval_exists"],
                item["eval_count"],
            ])
        lines.extend(table_lines(split_rows))
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    short = [item for item in sufficiency if item["status"] != "OK"]
    print(f"Wrote: {md_path}")
    print(f"Wrote: {json_path}")
    print(f"Wrote: {suff_csv}")
    if split_checks:
        print(f"Wrote: {split_csv}")
    if image_checks.get("missing_examples"):
        print(f"Wrote: {missing_csv}")
    print(f"samples={basic['samples']} with_image={basic['with_image']} text_only={basic['text_only']} duplicates={basic['duplicate_id_count']} missing_images={image_checks['missing_count']}")
    if short:
        print("SHORT categories:")
        for item in short:
            print(f"  {item['factor']}/{item['category']}: {item['count']}/{item['required']} gap={item['gap']}")
        return 2
    if image_checks.get("missing_count", 0):
        print("Target categories satisfy the required support, but some image files are missing.")
        return 3
    print("All target categories satisfy the required support.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
