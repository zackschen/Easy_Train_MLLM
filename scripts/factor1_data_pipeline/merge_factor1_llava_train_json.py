#!/usr/bin/env python3
"""Merge base Factor-1 LLaVA JSON with newly converted targeted samples.

Images are rewritten to be relative to the shared cl_dataset image folder:
  base image  images/x.jpg -> coin_factor1_train_v2/images/x.jpg
  new image   images/y.jpg -> coin_factor1_targeted_train_v3/images/y.jpg
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

FACTOR_FIELDS = {
    "visual_substrate": "visual_substrate",
    "skill_requirement": "skill_type_primary",
    "evidence_complexity": "evidence_complexity",
    "answer_distribution": "answer_type",
}


def load_json_array(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Expected JSON array: {path}")
    return data


def sample_id(row: dict[str, Any]) -> str:
    return str(row.get("id") or "").strip()


def normalize_image_path(value: Any, prefix: str) -> str | None:
    if not value:
        return None
    image = str(value).strip()
    if not image:
        return None
    if image.startswith("/"):
        return image
    prefix = prefix.strip("/")
    if not prefix:
        return image
    if image.startswith(prefix + "/"):
        return image
    return f"{prefix}/{image}"


def rewrite_rows(rows: list[dict[str, Any]], prefix: str, source_name: str) -> list[dict[str, Any]]:
    out_rows: list[dict[str, Any]] = []
    for row in rows:
        out = dict(row)
        out["conversations"] = [dict(m) for m in row.get("conversations", [])]
        image = normalize_image_path(row.get("image"), prefix)
        if image:
            out["image"] = image
        else:
            out.pop("image", None)
        md = dict(out.get("metadata") or {})
        md.setdefault("merge_source", source_name)
        out["metadata"] = md
        out_rows.append(out)
    return out_rows


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "samples": len(rows),
        "with_image": sum(1 for r in rows if r.get("image")),
        "text_only": sum(1 for r in rows if not r.get("image")),
        "by_dataset": dict(Counter((r.get("metadata") or {}).get("dataset", "unknown") for r in rows).most_common()),
    }
    for factor, field in FACTOR_FIELDS.items():
        summary[f"by_{factor}"] = dict(Counter((r.get("metadata") or {}).get(field, "unknown") for r in rows).most_common())
    return summary


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base-train-json", type=Path, required=True)
    p.add_argument("--base-image-prefix", default="coin_factor1_train_v2")
    p.add_argument("--new-train-json", type=Path, required=True)
    p.add_argument("--new-image-prefix", default="coin_factor1_targeted_train_v3")
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument("--image-folder", type=Path, default=Path("cl_dataset"))
    p.add_argument("--dedupe", choices=["keep-first", "keep-last"], default="keep-first")
    p.add_argument("--indent", type=int, default=None)
    args = p.parse_args()

    base_rows = rewrite_rows(load_json_array(args.base_train_json), args.base_image_prefix, "base")
    new_rows = rewrite_rows(load_json_array(args.new_train_json), args.new_image_prefix, "targeted")

    merged: list[dict[str, Any]] = []
    seen: dict[str, int] = {}
    duplicates = 0
    for row in base_rows + new_rows:
        sid = sample_id(row)
        if sid and sid in seen:
            duplicates += 1
            if args.dedupe == "keep-last":
                merged[seen[sid]] = row
            continue
        if sid:
            seen[sid] = len(merged)
        merged.append(row)

    args.output_root.mkdir(parents=True, exist_ok=True)
    train_json = args.output_root / "train.json"
    with train_json.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=args.indent, separators=None if args.indent else (",", ":"))

    manifest = {
        "base_train_json": str(args.base_train_json),
        "new_train_json": str(args.new_train_json),
        "output_root": str(args.output_root),
        "train_json": str(train_json),
        "image_folder_for_training": str(args.image_folder),
        "base_image_prefix": args.base_image_prefix,
        "new_image_prefix": args.new_image_prefix,
        "duplicates_skipped_or_replaced": duplicates,
        "summary": summarize(merged),
    }
    manifest_path = args.output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"merged={len(merged)} duplicates={duplicates} train_json={train_json}")
    print(f"manifest={manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
