#!/usr/bin/env python3
"""Convert Factor-1 refined metadata into LLaVA-style supervised training data.

Output format is compatible with ETrain/Dataset/LLaVA/llava_dataset.py:
[
  {
    "id": "...",
    "image": "images/dataset/id.jpg",   # omitted for text-only samples
    "conversations": [
      {"from": "human", "value": "Question...\n<image>"},
      {"from": "gpt", "value": "Answer"}
    ],
    "metadata": {...}
  }
]

Use output root as --image_folder during LLaVA training.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Iterable


META_KEYS = [
    "dataset",
    "regime",
    "split",
    "source_file",
    "source_index",
    "visual_substrate",
    "skill_type_primary",
    "skill_type_secondary",
    "evidence_type_primary",
    "evidence_type_secondary",
    "evidence_source_primary",
    "evidence_source_secondary",
    "evidence_scope",
    "evidence_complexity",
    "evidence_complexity_level",
    "evidence_complexity_score",
    "answer_type",
    "answer_type_vlm",
    "label_source",
    "label_confidence",
    "overall_label_confidence",
    "vlm_metadata_error",
]


def compact(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return ""
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, list):
        return " ".join(part for part in (compact(v) for v in value) if part)
    if isinstance(value, dict):
        for key in ("text", "value", "answer", "content", "label"):
            if key in value:
                return compact(value[key])
    return str(value)


def safe_name(value: Any, default: str = "unknown") -> str:
    text = compact(value).lower()
    text = re.sub(r"[^a-z0-9_.-]+", "_", text).strip("_")
    return text or default


def iter_rows(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        first = f.read(1)
        f.seek(0)
        if first == "[":
            data = json.load(f)
            if not isinstance(data, list):
                raise ValueError(f"JSON input must be a list: {path}")
            for item in data:
                if isinstance(item, dict):
                    yield item
        else:
            for line_no, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(f"Bad JSONL at {path}:{line_no}: {error}") from error
                if isinstance(item, dict):
                    yield item


class JsonArrayWriter:
    def __init__(self, path: Path, indent: int | None = None):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.f = path.open("w", encoding="utf-8")
        self.indent = indent
        self.count = 0
        self.f.write("[\n")

    def write(self, item: dict[str, Any]) -> None:
        if self.count:
            self.f.write(",\n")
        if self.indent is None:
            text = json.dumps(item, ensure_ascii=False, separators=(",", ":"))
            self.f.write(text)
        else:
            text = json.dumps(item, ensure_ascii=False, indent=self.indent)
            self.f.write(text)
        self.count += 1

    def close(self) -> None:
        self.f.write("\n]\n")
        self.f.close()


def import_meta_module(project_root: Path):
    sys.path.insert(0, str(project_root.resolve()))
    import factor1_coin_meta  # type: ignore
    return factor1_coin_meta


def data_url_to_bytes(url: str) -> tuple[bytes, str]:
    if not url.startswith("data:"):
        raise ValueError("Only data:image URLs are supported for exported images")
    header, payload = url.split(",", 1)
    mime = header.split(";", 1)[0].replace("data:", "")
    ext = {
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/png": "png",
        "image/webp": "webp",
        "image/gif": "gif",
    }.get(mime, "jpg")
    return base64.b64decode(payload), ext


def stable_image_stem(row: dict[str, Any]) -> str:
    row_id = compact(row.get("id"))
    if row_id:
        return safe_name(row_id)
    raw = "|".join(compact(row.get(k)) for k in ("dataset", "split", "question", "answer", "source_file", "source_index"))
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def resolve_and_export_image(row: dict[str, Any], meta_module: Any, args: argparse.Namespace) -> tuple[str | None, str]:
    image_args = SimpleNamespace(
        raw_root=args.raw_root.expanduser().resolve(),
        image_roots=[p.expanduser().resolve() for p in args.image_roots],
        allow_text_only=True,
    )
    try:
        image_url, media_source = meta_module.image_url_for_row(row, image_args)
    except Exception as error:
        if args.on_image_error == "raise":
            raise
        return None, f"image_error:{type(error).__name__}:{error}"

    if not image_url:
        return None, media_source
    if image_url.startswith(("http://", "https://")):
        if args.on_image_error == "raise":
            raise ValueError(f"Remote image URL is not exported: {image_url[:200]}")
        return None, "remote_image_not_exported"

    data, ext = data_url_to_bytes(image_url)
    dataset = safe_name(row.get("dataset"))
    rel_path = Path("images") / dataset / f"{stable_image_stem(row)}.{ext}"
    out_path = args.output_root / rel_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if not out_path.exists() or out_path.stat().st_size != len(data):
        out_path.write_bytes(data)
    return rel_path.as_posix(), media_source


def build_training_item(row: dict[str, Any], image_rel: str | None, media_source: str, args: argparse.Namespace) -> dict[str, Any] | None:
    question = compact(row.get("question"))
    answer = compact(row.get("answer"))
    if not question or not answer:
        return None

    if image_rel:
        if args.image_token_position == "prefix":
            user_value = f"<image>\n{question}"
        else:
            user_value = f"{question}\n<image>"
    else:
        if args.skip_text_only:
            return None
        user_value = question

    item: dict[str, Any] = {
        "id": compact(row.get("id")) or stable_image_stem(row),
        "conversations": [
            {"from": "human", "value": user_value},
            {"from": "gpt", "value": answer},
        ],
        "metadata": {key: row.get(key) for key in META_KEYS if key in row},
    }
    item["metadata"]["media_source"] = media_source
    if image_rel:
        item["image"] = image_rel
    if row.get("choices"):
        item["metadata"]["choices"] = row.get("choices")
    if args.keep_raw_metadata and row.get("raw_metadata") is not None:
        item["metadata"]["raw_metadata"] = row.get("raw_metadata")
    return item


def row_allowed(row: dict[str, Any], args: argparse.Namespace, per_dataset_counts: Counter[str]) -> bool:
    dataset = compact(row.get("dataset"))
    split = compact(row.get("split"))
    if args.datasets and dataset not in args.datasets:
        return False
    if args.splits and split not in args.splits:
        return False
    if args.max_samples_per_dataset is not None and per_dataset_counts[dataset] >= args.max_samples_per_dataset:
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Convert Factor-1 metadata to LLaVA train JSON")
    parser.add_argument("--metadata", type=Path, default=Path("cl_dataset/coin_factor1_meta_all/metadata/sample_metadata.vlm.jsonl"))
    parser.add_argument("--output-root", type=Path, default=Path("cl_dataset/coin_factor1_train"))
    parser.add_argument("--raw-root", type=Path, default=Path("cl_dataset/coin"))
    parser.add_argument("--image-roots", type=Path, nargs="*", default=[])
    parser.add_argument("--project-root", type=Path, default=Path("."), help="Directory containing factor1_coin_meta.py")
    parser.add_argument("--datasets", nargs="*", default=[])
    parser.add_argument("--splits", nargs="*", default=[])
    parser.add_argument("--max-samples-per-dataset", type=int, default=None)
    parser.add_argument("--skip-text-only", action="store_true")
    parser.add_argument("--keep-raw-metadata", action="store_true")
    parser.add_argument("--image-token-position", choices=["suffix", "prefix"], default="suffix")
    parser.add_argument("--on-image-error", choices=["text-only", "skip", "raise"], default="text-only")
    parser.add_argument("--indent", type=int, default=None)
    parser.add_argument("--no-by-dataset", action="store_true")
    parser.add_argument("--no-by-regime", action="store_true")
    args = parser.parse_args()

    args.metadata = args.metadata.expanduser().resolve()
    args.output_root = args.output_root.expanduser().resolve()
    args.raw_root = args.raw_root.expanduser().resolve()
    args.project_root = args.project_root.expanduser().resolve()
    args.image_roots = [p.expanduser().resolve() for p in args.image_roots]

    meta_module = import_meta_module(args.project_root)
    args.output_root.mkdir(parents=True, exist_ok=True)

    writers: dict[str, JsonArrayWriter] = {
        "all": JsonArrayWriter(args.output_root / "train.json", indent=args.indent)
    }
    stats: Counter[str] = Counter()
    per_dataset_counts: Counter[str] = Counter()
    by_dataset_counts: Counter[str] = Counter()
    by_regime_counts: Counter[str] = Counter()

    def writer_for(kind: str, name: str) -> JsonArrayWriter:
        key = f"{kind}:{safe_name(name)}"
        if key not in writers:
            writers[key] = JsonArrayWriter(args.output_root / kind / safe_name(name) / "train.json", indent=args.indent)
        return writers[key]

    try:
        for row in iter_rows(args.metadata):
            stats["seen"] += 1
            dataset = compact(row.get("dataset")) or "unknown"
            regime = compact(row.get("regime")) or "unknown"
            if not row_allowed(row, args, per_dataset_counts):
                stats["filtered"] += 1
                continue

            image_rel, media_source = resolve_and_export_image(row, meta_module, args)
            if not image_rel and media_source.startswith("image_error"):
                stats["image_errors"] += 1
                if args.on_image_error == "skip":
                    stats["skipped_image_error"] += 1
                    continue

            item = build_training_item(row, image_rel, media_source, args)
            if item is None:
                stats["skipped_invalid_or_text_only"] += 1
                continue

            writers["all"].write(item)
            if not args.no_by_dataset:
                writer_for("by_dataset", dataset).write(item)
                by_dataset_counts[dataset] += 1
            if not args.no_by_regime:
                writer_for("by_regime", regime).write(item)
                by_regime_counts[regime] += 1
            per_dataset_counts[dataset] += 1
            stats["written"] += 1
            if image_rel:
                stats["with_image"] += 1
            else:
                stats["text_only"] += 1

            if stats["seen"] % 10000 == 0:
                print(f"[progress] seen={stats['seen']} written={stats['written']} images={stats['with_image']} text_only={stats['text_only']}", flush=True)
    finally:
        for writer in writers.values():
            writer.close()

    manifest = {
        "metadata": str(args.metadata),
        "output_root": str(args.output_root),
        "train_json": str(args.output_root / "train.json"),
        "image_folder_for_training": str(args.output_root),
        "stats": dict(stats),
        "by_dataset": dict(sorted(by_dataset_counts.items())),
        "by_regime": dict(sorted(by_regime_counts.items())),
        "note": "Use --image_folder equal to output_root. Image paths in JSON are relative to output_root.",
    }
    (args.output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
