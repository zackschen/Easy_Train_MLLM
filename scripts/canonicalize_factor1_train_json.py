#!/usr/bin/env python3
"""Canonicalize Factor-1 labels in a LLaVA train JSON without touching images."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


def parse_map(values: list[str]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for value in values:
        if ":" not in value or "=" not in value:
            raise SystemExit(f"Invalid --map {value!r}. Expected FIELD:OLD=NEW")
        field, rest = value.split(":", 1)
        old, new = rest.split("=", 1)
        field, old, new = field.strip(), old.strip(), new.strip()
        if not field or not old or not new:
            raise SystemExit(f"Invalid --map {value!r}. Expected FIELD:OLD=NEW")
        result.setdefault(field, {})[old] = new
    return result


def sample_id(row: dict[str, Any]) -> str:
    return str(row.get("id") or "")


def count_field(rows: list[dict[str, Any]], field: str) -> Counter[str]:
    c: Counter[str] = Counter()
    for row in rows:
        md = row.get("metadata") or {}
        c[str(md.get(field) or row.get(field) or "unknown")] += 1
    return c


def apply_maps(row: dict[str, Any], maps: dict[str, dict[str, str]]) -> dict[str, Any]:
    out = dict(row)
    out["conversations"] = [dict(m) for m in row.get("conversations", [])]
    md = dict(out.get("metadata") or {})
    changed: dict[str, dict[str, str]] = {}
    for field, value_map in maps.items():
        old = str(md.get(field) or out.get(field) or "")
        if old in value_map:
            new = value_map[old]
            md[field] = new
            changed[field] = {"old": old, "new": new}
    if changed:
        canon = dict(md.get("canonicalization") or {})
        canon.update(changed)
        md["canonicalization"] = canon
    out["metadata"] = md
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output-root", type=Path, required=True)
    p.add_argument(
        "--map",
        action="append",
        default=[],
        help="Canonicalization rule FIELD:OLD=NEW. Repeatable, e.g. visual_substrate:science_diagram=diagram",
    )
    p.add_argument("--indent", type=int, default=None)
    args = p.parse_args()

    maps = parse_map(args.map)
    rows = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise SystemExit(f"Expected JSON array: {args.input}")

    before = {field: dict(count_field(rows, field).most_common()) for field in maps}
    out_rows = [apply_maps(row, maps) for row in rows]
    after = {field: dict(count_field(out_rows, field).most_common()) for field in maps}

    args.output_root.mkdir(parents=True, exist_ok=True)
    out_train = args.output_root / "train.json"
    with out_train.open("w", encoding="utf-8") as f:
        json.dump(out_rows, f, ensure_ascii=False, indent=args.indent, separators=None if args.indent else (",", ":"))

    changed = sum(
        1
        for row in out_rows
        if (row.get("metadata") or {}).get("canonicalization")
    )
    manifest = {
        "input": str(args.input),
        "output_train_json": str(out_train),
        "maps": maps,
        "samples": len(out_rows),
        "changed_samples": changed,
        "before": before,
        "after": after,
    }
    manifest_path = args.output_root / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote={out_train}")
    print(f"manifest={manifest_path}")
    print(f"samples={len(out_rows)} changed={changed}")
    for field in maps:
        print(f"[{field}] before={before[field]}")
        print(f"[{field}] after={after[field]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
