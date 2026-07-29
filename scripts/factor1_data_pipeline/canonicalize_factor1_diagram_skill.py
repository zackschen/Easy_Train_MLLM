#!/usr/bin/env python3
"""Canonicalize diagram-substrate samples into diagram_reasoning skill.

This script is for the Factor-1 skill ontology where diagram_reasoning means
"reasoning over a structured/symbolic diagram substrate" rather than a generic
low-level relation/counting/attribute skill. It only rewrites samples that match
both a diagram-like visual substrate and a diagram-source dataset.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

DEFAULT_DATASETS = {"iconqa", "ai2d", "scienceqa"}
DEFAULT_VISUALS = {"diagram", "science_diagram", "symbolic_diagram"}
DEFAULT_SOURCE_SKILLS = {"relation", "counting", "attribute", "comparison", "recognition", "text_reading"}


def load_json_array(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array: {path}")
    return data


def md(row: dict[str, Any]) -> dict[str, Any]:
    return row.get("metadata") or {}


def value(row: dict[str, Any], key: str) -> str:
    return str(md(row).get(key) or row.get(key) or "unknown")


def counts(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    return dict(Counter(value(row, key) for row in rows).most_common())


def parse_csv(value: str) -> set[str]:
    return {item.strip() for item in value.replace(";", ",").split(",") if item.strip()}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--datasets", default=",".join(sorted(DEFAULT_DATASETS)))
    p.add_argument("--visuals", default=",".join(sorted(DEFAULT_VISUALS)))
    p.add_argument("--source-skills", default=",".join(sorted(DEFAULT_SOURCE_SKILLS)))
    p.add_argument("--target-skill", default="diagram_reasoning")
    p.add_argument("--indent", type=int, default=None)
    args = p.parse_args()

    datasets = parse_csv(args.datasets)
    visuals = parse_csv(args.visuals)
    source_skills = parse_csv(args.source_skills)

    rows = load_json_array(args.input)
    before_skill = counts(rows, "skill_type_primary")
    before_visual = counts(rows, "visual_substrate")

    out_rows: list[dict[str, Any]] = []
    changed = 0
    changed_by_dataset: Counter[str] = Counter()
    changed_by_old_skill: Counter[str] = Counter()

    for row in rows:
        out = dict(row)
        out["conversations"] = [dict(msg) for msg in row.get("conversations", [])]
        meta = dict(out.get("metadata") or {})
        dataset = str(meta.get("dataset") or row.get("dataset") or "")
        visual = str(meta.get("visual_substrate") or row.get("visual_substrate") or "")
        skill = str(meta.get("skill_type_primary") or row.get("skill_type_primary") or "")
        should_change = dataset in datasets and visual in visuals and skill in source_skills
        if should_change:
            canonical = dict(meta.get("canonicalization") or {})
            canonical["diagram_skill"] = {
                "old_skill_type_primary": skill,
                "new_skill_type_primary": args.target_skill,
                "reason": "diagram substrate from diagram-source dataset",
            }
            meta["canonicalization"] = canonical
            meta["skill_type_primary_before_diagram_canonical"] = skill
            old_secondary = meta.get("skill_type_secondary")
            meta["skill_type_primary"] = args.target_skill
            if not old_secondary or old_secondary == args.target_skill:
                meta["skill_type_secondary"] = skill
            changed += 1
            changed_by_dataset[dataset] += 1
            changed_by_old_skill[skill] += 1
        out["metadata"] = meta
        out_rows.append(out)

    after_skill = counts(out_rows, "skill_type_primary")
    after_visual = counts(out_rows, "visual_substrate")

    args.output_root.mkdir(parents=True, exist_ok=True)
    train_path = args.output_root / "train.json"
    with train_path.open("w", encoding="utf-8") as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=args.indent, separators=None if args.indent else (",", ":"))

    manifest = {
        "input": str(args.input),
        "output_train_json": str(train_path),
        "samples": len(rows),
        "changed_samples": changed,
        "datasets": sorted(datasets),
        "visuals": sorted(visuals),
        "source_skills": sorted(source_skills),
        "target_skill": args.target_skill,
        "changed_by_dataset": dict(changed_by_dataset.most_common()),
        "changed_by_old_skill": dict(changed_by_old_skill.most_common()),
        "before_skill_type_primary": before_skill,
        "after_skill_type_primary": after_skill,
        "before_visual_substrate": before_visual,
        "after_visual_substrate": after_visual,
    }
    manifest_path = args.output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"wrote={train_path}")
    print(f"manifest={manifest_path}")
    print(f"samples={len(rows)} changed={changed}")
    print(f"changed_by_dataset={dict(changed_by_dataset.most_common())}")
    print(f"changed_by_old_skill={dict(changed_by_old_skill.most_common())}")
    print(f"diagram_reasoning before={before_skill.get(args.target_skill, 0)} after={after_skill.get(args.target_skill, 0)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
