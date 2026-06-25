#!/usr/bin/env python3
"""Metadata extraction for CoIN Factor-1 data-transition experiments.

Default paths assume this file is run from your project root:
  raw data: ./cl_dataset/coin
  output:   ./cl_dataset/coin_factor1_meta

Commands:
  python factor1_coin_meta.py inventory
  python factor1_coin_meta.py build --max-samples-per-dataset 1000
  python factor1_coin_meta.py refine-skills --datasets vqav2 --limit 200
  python factor1_coin_meta.py refine-metadata --datasets vqav2 --limit 100
  python factor1_coin_meta.py gaps --split all
"""

from __future__ import annotations

import argparse
import ast
import base64
import csv
import hashlib
import json
import math
import mimetypes
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Iterator


DATASETS: dict[str, dict[str, Any]] = {
    "vqav2": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "aliases": ["vqav2", "vqa_v2", "vqa-v2"]},
    "gqa": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "aliases": ["gqa"]},
    "visual7w": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "aliases": ["visual7w", "visual_7w"]},
    "tallyqa": {"regime": "natural_photo_qa", "visual": "natural_photo", "knowledge": False, "skill_hint": "counting", "aliases": ["tallyqa", "tally_qa"]},
    "ai2d": {"regime": "structured_visual_qa", "visual": "diagram", "knowledge": False, "skill_hint": "diagram_reasoning", "aliases": ["ai2d"]},
    "chartqa": {"regime": "structured_visual_qa", "visual": "chart", "knowledge": False, "skill_hint": "chart_reasoning", "aliases": ["chartqa", "chart_qa"]},
    "chartqa_eval": {"regime": "structured_visual_qa", "visual": "chart", "knowledge": False, "skill_hint": "chart_reasoning", "aliases": ["chartqa_eval", "chartqa-eval"]},
    "docvqa": {"regime": "structured_visual_qa", "visual": "document", "knowledge": False, "skill_hint": "document_reasoning", "aliases": ["docvqa", "doc_vqa"]},
    "infographicvqa": {"regime": "structured_visual_qa", "visual": "infographic", "knowledge": False, "skill_hint": "document_reasoning", "aliases": ["infographicvqa", "infographic_vqa"]},
    "okvqa": {"regime": "knowledge_intensive_qa", "visual": "natural_photo", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["okvqa", "ok_vqa", "ok-vqa"]},
    "aokvqa": {"regime": "knowledge_intensive_qa", "visual": "natural_photo", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["aokvqa", "a_okvqa", "a-okvqa"]},
    "scienceqa": {"regime": "knowledge_intensive_qa", "visual": "science_diagram", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["scienceqa", "science_qa", "scienceqa-full", "scienceqa-img"]},
    "mmmu": {"regime": "knowledge_intensive_qa", "visual": "academic_figure", "knowledge": True, "skill_hint": "knowledge_reasoning", "aliases": ["mmmu"]},
    "slake": {"regime": "expert_medical_qa", "visual": "medical", "knowledge": True, "skill_hint": "medical_reasoning", "aliases": ["slake"]},
    "vqarad": {"regime": "expert_medical_qa", "visual": "medical", "knowledge": True, "skill_hint": "medical_reasoning", "aliases": ["vqarad", "vqa_rad", "vqa-rad"]},
    "pathvqa": {"regime": "expert_medical_qa", "visual": "medical", "knowledge": True, "skill_hint": "medical_reasoning", "aliases": ["pathvqa", "path_vqa"]},
    "remote_sensing_vqa": {"regime": "expert_remote_sensing_qa", "visual": "remote_sensing", "knowledge": True, "skill_hint": "remote_sensing_reasoning", "aliases": ["remote_sensing_vqa", "rsvqa", "remote-sensing-sft-data"]},
    "lrs_vqa": {"regime": "expert_remote_sensing_qa", "visual": "remote_sensing", "knowledge": True, "skill_hint": "remote_sensing_reasoning", "aliases": ["lrs_vqa", "lrs-vqa", "lrs_vqa"]},
}

Q_FIELDS = ["question", "query", "prompt", "instruction", "problem", "question_text", "input", "user", "human", "text", "Question"]
A_FIELDS = ["answer", "answers", "direct_answer", "direct_answers", "correct_answer", "answer_text", "response", "output", "assistant", "gpt", "target", "final_answer", "multiple_choice_answer", "label", "Answer"]
C_FIELDS = ["choices", "options", "candidates", "multiple_choices", "choice_list"]
R_FIELDS = ["rationale", "rationales", "explanation", "solution", "reasoning"]
I_FIELDS = ["image", "images", "image_path", "img_path", "image_file", "filename", "file_name", "path", "image_id", "img_id"]

YES_NO = {"yes", "no", "true", "false"}
COLORS = {"red", "blue", "green", "yellow", "black", "white", "gray", "grey", "brown", "orange", "purple", "pink", "silver", "gold", "golden"}
ATTRIBUTES = COLORS | {"large", "small", "big", "tiny", "round", "square", "rectangular", "wooden", "metal", "metallic", "plastic", "open", "closed", "empty", "full"}
TEXT_SPAN_DATASETS = {"docvqa", "infographicvqa"}
KNOWLEDGE_DATASETS = {"okvqa", "aokvqa", "scienceqa", "mmmu", "slake", "vqarad", "pathvqa"}
REGIME_DIR_HINTS = {
    "natural_photo_qa": "natural",
    "structured_visual_qa": "structured",
    "knowledge_intensive_qa": "knowledge",
    "expert_medical_qa": "expert_medical",
    "expert_remote_sensing_qa": "expert_remote_sensing",
}

PRIMARY_SKILLS = {
    "recognition",
    "attribute",
    "counting",
    "relation",
    "comparison",
    "text_reading",
    "chart_reasoning",
    "document_reasoning",
    "diagram_reasoning",
    "knowledge_reasoning",
    "medical_reasoning",
    "remote_sensing_reasoning",
}
SECONDARY_SKILLS = PRIMARY_SKILLS | {"table_reading", "spatial_grounding", "visual_grounding"}
VISUAL_SUBSTRATES = {
    "natural_photo",
    "document",
    "infographic",
    "chart",
    "diagram",
    "science_diagram",
    "academic_figure",
    "medical",
    "remote_sensing",
    "screenshot",
    "map",
    "synthetic",
    "other",
}
VISUAL_SUBSTRATE_ALIASES = {
    "photo": "natural_photo",
    "natural_image": "natural_photo",
    "natural_scene": "natural_photo",
    "document_image": "document",
    "scientific_diagram": "science_diagram",
    "academic_plot": "academic_figure",
    "medical_image": "medical",
    "radiology": "medical",
    "satellite": "remote_sensing",
    "aerial": "remote_sensing",
    "remote_sensing_image": "remote_sensing",
    "screen": "screenshot",
}
EVIDENCE_SOURCES = {
    "object",
    "attribute",
    "scene",
    "action",
    "spatial_relation",
    "text",
    "table",
    "chart",
    "diagram",
    "medical_region",
    "remote_sensing_region",
    "map",
    "external_knowledge",
    "other",
}
EVIDENCE_SOURCE_ALIASES = {
    "object_region": "object",
    "visual_object": "object",
    "visual_attribute": "attribute",
    "global_scene": "scene",
    "ocr": "text",
    "text_span": "text",
    "table_cell": "table",
    "chart_element": "chart",
    "diagram_region": "diagram",
    "knowledge": "external_knowledge",
    "image_plus_knowledge": "external_knowledge",
}
EVIDENCE_SCOPES = {
    "single_region",
    "global_image",
    "multi_region",
    "cross_region",
    "cross_page",
    "image_plus_knowledge",
}
EVIDENCE_SCOPE_ALIASES = {
    "single": "single_region",
    "one_region": "single_region",
    "global": "global_image",
    "whole_image": "global_image",
    "multiple_regions": "multi_region",
    "multi_evidence": "multi_region",
    "cross_modal": "image_plus_knowledge",
    "external_knowledge": "image_plus_knowledge",
}
ANSWER_TYPES = {"yes_no", "number", "option", "text_span", "attribute", "object", "free_form"}
VLM_METADATA_SCHEMA_VERSION = "factor1-vlm-metadata-v1"
SKILL_ALIASES = {
    "object_recognition": "recognition",
    "scene_recognition": "recognition",
    "scene_understanding": "recognition",
    "visual_recognition": "recognition",
    "object": "recognition",
    "yes_no_recognition": "recognition",
    "color": "attribute",
    "shape": "attribute",
    "size": "attribute",
    "material": "attribute",
    "spatial_relation": "relation",
    "spatial_reasoning": "relation",
    "visual_relation": "relation",
    "ocr": "text_reading",
    "ocr_reading": "text_reading",
    "reading": "text_reading",
    "text": "text_reading",
    "chart": "chart_reasoning",
    "document": "document_reasoning",
    "diagram": "diagram_reasoning",
    "knowledge": "knowledge_reasoning",
    "medical": "medical_reasoning",
    "remote_sensing": "remote_sensing_reasoning",
}
QUESTION_INSTRUCTION_PATTERNS = [
    r"\s*answer the question using a single word or phrase\.?\s*$",
    r"\s*answer with a single word or phrase\.?\s*$",
    r"\s*answer using a single word or phrase\.?\s*$",
    r"\s*give a short answer\.?\s*$",
    r"\s*respond with a short answer\.?\s*$",
]
LLM_SKILL_SYSTEM_PROMPT = """You label the visual skill needed to answer VQA samples.

Use only the supplied dataset, visual substrate, question, answer, and choices.

Primary skill taxonomy:
- recognition: identify an object, scene, action, event, affordance, or visible entity.
- attribute: identify color, shape, size, material, state, age, gender, or another visible attribute.
- counting: count visible objects or determine an explicit quantity.
- relation: determine a spatial or semantic relation, including location, containment, support, interaction, or viewpoint.
- comparison: compare attributes or quantities across visible entities.
- text_reading: read visible text, letters, numbers, signs, labels, captions, or printed words. Do not select this because an answer instruction contains "word" or "phrase".
- chart_reasoning: reason over bars, lines, axes, legends, plotted values, or charts.
- document_reasoning: read or reason over forms, receipts, tables, documents, infographics, or dense layouts.
- diagram_reasoning: reason over diagrams, arrows, parts, flows, scientific illustrations, or schematics.
- knowledge_reasoning: external or common knowledge beyond direct visual evidence is necessary.
- medical_reasoning: medical image interpretation or clinical knowledge is necessary.
- remote_sensing_reasoning: satellite, aerial, or remote-sensing interpretation is necessary.

Return only JSON:
{"labels":[{"id":"...","skill_type_primary":"...","skill_type_secondary":null,"requires_external_knowledge":false,"confidence":0.0}]}

confidence is between 0 and 1."""

VLM_METADATA_SYSTEM_PROMPT = """You annotate multimodal VQA samples for a continual-learning benchmark.

Inspect each supplied image together with its question and reference answer. Do not solve a different task and do not use answer-format instructions such as "single word" as evidence.

Return one label per sample using only these taxonomies.

visual_substrate:
natural_photo, document, infographic, chart, diagram, science_diagram, academic_figure, medical, remote_sensing, screenshot, map, synthetic, other

skill_type_primary:
recognition, attribute, counting, relation, comparison, text_reading, chart_reasoning, document_reasoning, diagram_reasoning, knowledge_reasoning, medical_reasoning, remote_sensing_reasoning

evidence_source_primary and evidence_source_secondary:
object, attribute, scene, action, spatial_relation, text, table, chart, diagram, medical_region, remote_sensing_region, map, external_knowledge, other

evidence_scope:
- single_region: one localized region/span/cell is sufficient.
- global_image: the whole scene is sufficient without combining distinct evidence.
- multi_region: two or more distinct regions/items/spans must be collected.
- cross_region: evidence from distinct regions must be related or composed.
- cross_page: evidence crosses pages, panels, frames, or separate images.
- image_plus_knowledge: visual evidence must be combined with external knowledge.

evidence_count is the minimum number of distinct visual regions, objects, text spans, cells, or panels needed. Use 1 for direct global recognition. reasoning_hops is 0 for direct perception/readout, 1 for one relation/comparison/operation, 2 for two-step composition, and 3 for three or more steps.

answer_type:
yes_no, number, option, text_span, attribute, object, free_form

Return only JSON:
{"labels":[{"id":"...","visual_substrate":"...","skill_type_primary":"...","skill_type_secondary":null,"evidence_source_primary":"...","evidence_source_secondary":null,"evidence_scope":"...","evidence_count":1,"reasoning_hops":0,"requires_external_knowledge":false,"answer_type":"...","confidence":{"visual_substrate":0.0,"skill_type":0.0,"evidence":0.0,"requires_external_knowledge":0.0,"answer_type":0.0}}]}"""


def norm_key(x: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(x).lower()).strip("_")


def compact(x: Any) -> str:
    if x is None or isinstance(x, bytes):
        return ""
    if isinstance(x, str):
        return re.sub(r"\s+", " ", x.replace("<image>", " ")).strip()
    if isinstance(x, (int, float, bool)):
        return str(x)
    if isinstance(x, list):
        return " ".join(t for t in (compact(v) for v in x) if t)
    if isinstance(x, dict):
        for k in ["text", "value", "answer", "content", "label"]:
            if k in x:
                return compact(x[k])
    return str(x)


def question_for_label(question: str) -> str:
    """Remove answer-format instructions that must not affect semantic labels."""
    q = compact(question)
    for pattern in QUESTION_INSTRUCTION_PATTERNS:
        q = re.sub(pattern, "", q, flags=re.IGNORECASE)
    return compact(q)


def safe_json(x: Any, max_len: int = 1000) -> Any:
    if x is None or isinstance(x, (bool, int, float)):
        return None if isinstance(x, float) and (math.isnan(x) or math.isinf(x)) else x
    if isinstance(x, bytes):
        return f"<bytes:{len(x)}>"
    if isinstance(x, str):
        return x if len(x) <= max_len else x[:max_len] + "...<truncated>"
    if isinstance(x, dict):
        return {str(k): safe_json(v, max_len) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [safe_json(v, max_len) for v in x[:20]]
    return str(x)


def as_list(x: Any) -> list[str]:
    if x is None:
        return []
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return []
        if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
            try:
                return as_list(ast.literal_eval(s))
            except Exception:
                pass
        return [s]
    if isinstance(x, dict):
        for k in ["text", "answer", "label", "value", "content"]:
            if k in x:
                return as_list(x[k])
        return [json.dumps(safe_json(x), ensure_ascii=False)]
    if isinstance(x, Iterable) and not isinstance(x, (bytes, bytearray)):
        out: list[str] = []
        for item in x:
            out.extend(as_list(item))
        return [v for v in out if v]
    return [str(x)]


def first(row: dict[str, Any], names: list[str]) -> Any:
    lower = {norm_key(k): k for k in row}
    for n in names:
        k = lower.get(norm_key(n))
        if k is not None:
            return row[k]
    return None


def conv_qa(row: dict[str, Any]) -> tuple[str, str]:
    conv = first(row, ["conversations", "conversation", "messages", "dialog", "chat", "texts"])
    if conv is None:
        return "", ""
    if isinstance(conv, str):
        try:
            conv = json.loads(conv)
        except Exception:
            return compact(conv), ""
    if isinstance(conv, dict):
        for key in ("messages", "conversations", "texts", "dialog"):
            if isinstance(conv.get(key), list):
                conv = conv[key]
                break
        else:
            conv = [conv]
    if not isinstance(conv, list):
        return "", ""
    q, a = "", ""
    for msg in conv:
        if not isinstance(msg, dict):
            continue
        direct_q = compact(first(msg, ["user", "human", "question", "prompt", "input"]))
        direct_a = compact(first(msg, ["assistant", "gpt", "answer", "response", "output"]))
        if direct_q and direct_a:
            return direct_q, direct_a
        role = compact(msg.get("role") or msg.get("from")).lower()
        text = compact(msg.get("content") or msg.get("value") or msg.get("text"))
        if not text:
            continue
        if not q and role in {"human", "user", "question", "prompter"}:
            q = text
        elif q and not a and role in {"gpt", "assistant", "answer", "model"}:
            a = text
            break
    return q, a


def img_ref(x: Any) -> str | None:
    if x is None:
        return None
    if isinstance(x, str):
        return x
    if isinstance(x, bytes):
        return f"<embedded_image_bytes:{len(x)}>"
    if isinstance(x, dict):
        if x.get("path"):
            return compact(x["path"])
        if x.get("bytes") is not None:
            b = x["bytes"]
            return f"<embedded_image_bytes:{len(b) if isinstance(b, bytes) else 'unknown'}>"
        return json.dumps(safe_json(x), ensure_ascii=False)
    if isinstance(x, list) and x:
        return img_ref(x[0])
    return compact(x) or None


def infer_split(path: Path) -> str:
    s = "/".join(path.parts).lower()
    if re.search(r"(^|[/_.-])train(ing)?($|[/_.-])", s):
        return "train"
    if "validation" in s or re.search(r"(^|[/_.-])val($|[/_.-])", s) or "dev" in path.name.lower():
        return "val"
    if re.search(r"(^|[/_.-])test($|[/_.-])", s):
        return "test"
    return "unknown"


def data_files(root: Path) -> Iterator[Path]:
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in {".parquet", ".jsonl", ".json", ".csv"} and not p.name.startswith("."):
            yield p


def dataset_dir(raw_root: Path, dataset: str) -> Path | None:
    aliases = {norm_key(a) for a in DATASETS[dataset].get("aliases", [dataset])}
    direct = raw_root / dataset
    if direct.exists():
        return direct
    matches = []
    for p in raw_root.rglob("*"):
        if not p.is_dir():
            continue
        name = norm_key(p.name)
        parent = norm_key(p.parent.name)
        if name in aliases or parent in aliases or any(a in name for a in aliases):
            matches.append(p)
    if not matches:
        return None
    files_by_root = {path: list(data_files(path)) for path in matches}
    dataful = [path for path, files in files_by_root.items() if files]
    preferred_group = REGIME_DIR_HINTS.get(DATASETS[dataset]["regime"], "")

    def rank(path: Path) -> tuple[int, int, int, int, str]:
        normalized_parts = {norm_key(part) for part in path.parts}
        files = files_by_root.get(path, [])
        legacy_penalty = int(bool({"playground", "checkpoints", "results"} & normalized_parts))
        group_penalty = int(preferred_group not in normalized_parts)
        parquet_penalty = int(not any(file.suffix.lower() == ".parquet" for file in files))
        return legacy_penalty, group_penalty, parquet_penalty, len(str(path)), str(path)

    return sorted(dataful or matches, key=rank)[0]


def rows_from(path: Path, batch_size: int = 2048) -> Iterator[dict[str, Any]]:
    if path.suffix.lower() == ".parquet":
        try:
            import pyarrow.parquet as pq  # type: ignore
        except Exception as e:
            raise RuntimeError("Need pyarrow: pip install pyarrow") from e
        pf = pq.ParquetFile(path)
        for batch in pf.iter_batches(batch_size=batch_size):
            yield from batch.to_pylist()
        return
    if path.suffix.lower() == ".jsonl":
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)
        return
    if path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            yield from csv.DictReader(f)
        return
    with path.open("r", encoding="utf-8") as f:
        obj = json.load(f)
    if isinstance(obj, list):
        for r in obj:
            if isinstance(r, dict):
                yield r
    elif isinstance(obj, dict):
        for k in ["data", "examples", "annotations", "questions", "samples"]:
            if isinstance(obj.get(k), list):
                for r in obj[k]:
                    if isinstance(r, dict):
                        yield r
                return
        yield obj


def normalize_answer(x: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[,，]", "", x.lower().strip()))


def tok_count(x: str) -> int:
    return len(re.findall(r"\w+", x))


def is_number(x: str) -> bool:
    return bool(re.fullmatch(r"[$€£¥]?\s*-?\d+(\.\d+)?\s*(%|percent|m|million|b|billion|k|thousand)?", normalize_answer(x)))


def has(q: str, pat: str) -> bool:
    return re.search(pat, q.lower()) is not None


def representative_answer(value: Any) -> tuple[str, list[str]]:
    answers = as_list(value)
    if not answers:
        return "", []
    grouped: dict[str, list[str]] = defaultdict(list)
    for answer in answers:
        grouped[normalize_answer(answer)].append(answer)
    best = max(grouped.values(), key=lambda values: (len(values), -answers.index(values[0])))
    return best[0], answers


def indexed_choice_answer(row: dict[str, Any], choices: list[str], answer_value: Any) -> str | None:
    if not choices:
        return None
    index_value = first(
        row,
        ["correct_choice_idx", "correct_choice_index", "answer_idx", "answer_index", "correct_index"],
    )
    if index_value is None and isinstance(answer_value, (int, float)):
        index_value = answer_value
    if index_value is None and isinstance(answer_value, str):
        stripped = answer_value.strip()
        if re.fullmatch(r"[A-Za-z]", stripped):
            index_value = ord(stripped.upper()) - ord("A")
        elif re.fullmatch(r"\d+", stripped):
            index_value = int(stripped)
    try:
        index = int(index_value)
    except (TypeError, ValueError):
        return None
    return choices[index] if 0 <= index < len(choices) else None


def canonical(dataset: str, split: str, file: Path, idx: int, row: dict[str, Any]) -> dict[str, Any] | None:
    q = compact(first(row, Q_FIELDS))
    choices = as_list(first(row, C_FIELDS))
    ans_val = first(row, A_FIELDS)
    choice_answer = indexed_choice_answer(row, choices, ans_val)
    if choice_answer is not None:
        ans_val = choice_answer
    a, answers = representative_answer(ans_val)
    if not q or not a:
        cq, ca = conv_qa(row)
        q = q or cq
        if not a and ca:
            a, answers = ca, [ca]
    if not q or not a:
        return None
    raw_meta = {}
    for k in ["question_type", "answer_type", "semantic", "semantic_type", "category", "subject", "type", "task", "source", "id", "question_id", "image_id"]:
        v = first(row, [k])
        if v is not None:
            raw_meta[k] = safe_json(v)
    return {
        "_dataset": dataset,
        "_split": split,
        "_source_file": str(file),
        "_source_index": idx,
        "question": q,
        "answer": a,
        "answers": answers or [a],
        "choices": choices,
        "rationale": compact(first(row, R_FIELDS)) or None,
        "image": img_ref(first(row, I_FIELDS)),
        "raw_metadata": raw_meta,
    }


def answer_type(s: dict[str, Any]) -> tuple[str, float, str]:
    a = normalize_answer(s["answer"])
    if s["choices"]:
        return "option", 0.95, "rule"
    if a in YES_NO:
        return "yes_no", 0.98, "rule"
    if is_number(a):
        return "number", 0.98, "rule"
    if s["_dataset"] in TEXT_SPAN_DATASETS:
        return "text_span", 0.85, "dataset_default+rule"
    if a in ATTRIBUTES:
        return "attribute", 0.90, "rule"
    if tok_count(a) <= 3:
        return "object", 0.70, "weak_rule"
    return "free_form", 0.65, "weak_rule"


def skill_type(s: dict[str, Any], cfg: dict[str, Any]) -> tuple[str, str | None, float, str]:
    q = question_for_label(s["question"]).lower()
    meta = " ".join(compact(v).lower() for v in s["raw_metadata"].values())
    text = f"{q} {meta}"
    d = s["_dataset"]
    if d in {"chartqa", "chartqa_eval"} or has(text, r"\b(chart|graph|bar|line chart|pie chart|axis|trend|legend|x-axis|y-axis)\b"):
        sec = "comparison" if has(text, r"\b(compare|larger|smaller|higher|lower|highest|lowest|increase|decrease|difference|more|less)\b") else None
        return "chart_reasoning", sec, 0.90, "dataset_default+rule"
    if d == "docvqa" or has(text, r"\b(invoice|receipt|form|document|table|row|column|total|date|amount)\b"):
        return "document_reasoning", "table_reading" if has(text, r"\b(table|row|column|cell)\b") else "text_reading", 0.86, "dataset_default+rule"
    if d == "infographicvqa":
        return "document_reasoning", "chart_reasoning" if has(text, r"\b(chart|graph|bar|trend|axis)\b") else "text_reading", 0.82, "dataset_default+rule"
    if d == "ai2d" or has(text, r"\b(diagram|arrow|flow|part|component|process)\b"):
        return "diagram_reasoning", None, 0.86, "dataset_default+rule"
    if has(text, r"\b(how many|number of|count|total number)\b"):
        return "counting", None, 0.95, "rule"
    if has(text, r"\b(what color|which color|color is|what shape|which shape|what size|how big|material)\b"):
        return "attribute", None, 0.93, "rule"
    if has(text, r"\b(left of|right of|behind|in front of|next to|beside|on top of|under|below|above|holding|wearing|near)\b"):
        return "relation", None, 0.90, "rule"
    if has(text, r"\b(compare|larger|smaller|higher|lower|highest|lowest|more|less|same|different|difference)\b"):
        return "comparison", None, 0.88, "rule"
    if has(text, r"\b(say|says|read|written|word|text|letter|sign|label)\b"):
        return "text_reading", None, 0.88, "rule"
    if d in KNOWLEDGE_DATASETS or cfg["knowledge"]:
        return cfg.get("skill_hint", "knowledge_reasoning"), None, 0.80, "dataset_default"
    if has(text, r"\b(why|used for|purpose|cause|likely|infer|reason|because)\b"):
        return "knowledge_reasoning", None, 0.76, "weak_rule"
    if cfg.get("skill_hint"):
        return cfg["skill_hint"], None, 0.72, "dataset_default"
    return "recognition", None, 0.82, "rule"


def evidence_type(s: dict[str, Any], primary: str, secondary: str | None, cfg: dict[str, Any]) -> tuple[str, str | None, float, str]:
    q = question_for_label(s["question"]).lower()
    d = s["_dataset"]
    if d in {"chartqa", "chartqa_eval"} or primary == "chart_reasoning":
        sec = "cross_region" if secondary == "comparison" or has(q, r"\b(trend|compare|highest|lowest|increase|decrease|difference)\b") else None
        return "chart_element", sec, 0.86, "dataset_default+rule"
    if d == "docvqa" or primary == "document_reasoning":
        if has(q, r"\b(table|row|column|cell|total|sum)\b"):
            return "table_cell", None, 0.82, "rule"
        if d == "infographicvqa":
            return "text_span", "cross_region", 0.76, "dataset_default+weak_rule"
        return "text_span", None, 0.82, "dataset_default+rule"
    if d == "ai2d" or primary == "diagram_reasoning":
        return "diagram_region", "cross_region" if has(q, r"\b(process|flow|path|between|relationship|cause)\b") else None, 0.80, "dataset_default+rule"
    if cfg["knowledge"] or primary in {"knowledge_reasoning", "medical_reasoning", "remote_sensing_reasoning"}:
        return "image_plus_knowledge", None, 0.78, "dataset_default+rule"
    if primary in {"counting", "relation", "comparison"}:
        return "multi_region", None, 0.82, "rule"
    if primary in {"recognition", "attribute"}:
        return "single_region", None, 0.84, "rule"
    if primary == "text_reading":
        return "text_span", None, 0.82, "rule"
    return "unknown", None, 0.35, "fallback"


def label(s: dict[str, Any]) -> dict[str, Any]:
    d = s["_dataset"]
    cfg = DATASETS[d]
    at, ac, asrc = answer_type(s)
    sp, ss, sc, ssrc = skill_type(s, cfg)
    ep, es, ec, esrc = evidence_type(s, sp, ss, cfg)
    protocol = "multiple_choice" if s["choices"] else ("answer_with_rationale" if s["rationale"] else ("free_form_answer" if tok_count(s["answer"]) > 12 else "short_answer"))
    pconf = 0.95 if s["choices"] else (0.90 if s["rationale"] or protocol == "short_answer" else 0.72)
    label_q = question_for_label(s["question"])
    k = bool(cfg["knowledge"] or sp == "knowledge_reasoning" or has(label_q, r"\b(why|used for|purpose|cause|likely|infer|reason)\b"))
    kconf = 0.85 if cfg["knowledge"] else (0.72 if k else 0.82)
    conf = {
        "visual_substrate": 1.0,
        "skill_type": sc,
        "evidence_type": ec,
        "answer_type": ac,
        "protocol_type": pconf,
        "requires_external_knowledge": kconf,
    }
    raw = "|".join([d, s["_split"], s["_source_file"], str(s["_source_index"]), s["question"], s["answer"]])
    return {
        "id": f"{d}_{s['_split']}_{hashlib.sha1(raw.encode()).hexdigest()[:16]}",
        "dataset": d,
        "regime": cfg["regime"],
        "split": s["_split"],
        "source_file": s["_source_file"],
        "source_index": s["_source_index"],
        "image": s["image"],
        "question": s["question"],
        "question_for_label": label_q,
        "answer": s["answer"],
        "answers": s["answers"],
        "choices": s["choices"] or None,
        "rationale": s["rationale"],
        "visual_substrate": cfg["visual"],
        "skill_type_primary": sp,
        "skill_type_secondary": ss,
        "evidence_type_primary": ep,
        "evidence_type_secondary": es,
        "answer_type": at,
        "protocol_type": protocol,
        "requires_external_knowledge": k,
        "question_length": tok_count(s["question"]),
        "answer_length": tok_count(s["answer"]),
        "normalized_answer": normalize_answer(s["answer"]),
        "label_source": {
            "visual_substrate": "dataset_default",
            "skill_type": ssrc,
            "evidence_type": esrc,
            "answer_type": asrc,
            "protocol_type": "rule",
            "requires_external_knowledge": "dataset_default+rule",
        },
        "label_confidence": conf,
        "overall_label_confidence": min(conf.values()),
        "raw_metadata": s["raw_metadata"],
    }


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def cmd_inventory(args: argparse.Namespace) -> int:
    out = args.output_root / "metadata" / "dataset_inventory.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    records = []
    for d in args.datasets:
        root = dataset_dir(args.raw_root, d)
        if root is None:
            records.append({"dataset": d, "status": "missing_dir"})
            continue
        files = list(data_files(root))
        if args.max_files_per_dataset:
            files = files[: args.max_files_per_dataset]
        if not files:
            records.append({"dataset": d, "dataset_dir": str(root), "status": "no_data_files"})
            continue
        for fp in files:
            split = infer_split(fp)
            num, cols, fq, fa = 0, set(), "", ""
            try:
                for row in rows_from(fp):
                    if num == 0:
                        cols = set(row.keys())
                        c = canonical(d, split, fp, num, row)
                        if c:
                            fq, fa = c["question"][:120], c["answer"][:120]
                    num += 1
            except Exception as e:
                records.append({"dataset": d, "dataset_dir": str(root), "file": str(fp), "split": split, "status": "read_error", "error": repr(e)})
                continue
            records.append({"dataset": d, "dataset_dir": str(root), "file": str(fp), "split": split, "num_rows": num, "columns": "|".join(sorted(cols)), "first_question": fq, "first_answer": fa, "status": "ok"})
    with out.open("w", encoding="utf-8", newline="") as f:
        fields = sorted({k for r in records for k in r})
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(records)
    print(f"Wrote inventory: {out}")
    return 0


def iter_labeled(d: str, raw_root: Path, max_samples: int | None) -> Iterator[dict[str, Any]]:
    root = dataset_dir(raw_root, d)
    if root is None:
        print(f"[warn] missing dataset dir: {d}", file=sys.stderr)
        return
    n, skipped = 0, 0
    for fp in data_files(root):
        split = infer_split(fp)
        for i, row in enumerate(rows_from(fp)):
            c = canonical(d, split, fp, i, row)
            if c is None:
                skipped += 1
                continue
            yield label(c)
            n += 1
            if max_samples and n >= max_samples:
                print(f"[info] {d}: reached max_samples={max_samples}, skipped={skipped}", file=sys.stderr)
                return
    print(f"[info] {d}: labeled={n}, skipped={skipped}", file=sys.stderr)


def llm_prompt(r: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": r["id"],
        "dataset": r["dataset"],
        "visual_substrate": r["visual_substrate"],
        "question": r["question"],
        "answer": r["answer"],
        "current_labels": {
            "skill_type_primary": r["skill_type_primary"],
            "skill_type_secondary": r["skill_type_secondary"],
            "evidence_type_primary": r["evidence_type_primary"],
            "evidence_type_secondary": r["evidence_type_secondary"],
            "requires_external_knowledge": r["requires_external_knowledge"],
        },
        "instruction": "Return JSON labels for skill_type_primary, skill_type_secondary, evidence_type_primary, evidence_type_secondary, requires_external_knowledge, confidence. Use question/answer/dataset only.",
    }


def write_stats(meta: Path, out_dir: Path, threshold: float, review_n: int, seed: int) -> None:
    rng = random.Random(seed)
    stats: Counter[tuple[str, str, str, str]] = Counter()
    split_counts: Counter[tuple[str, str]] = Counter()
    review_pool: dict[str, list[dict[str, Any]]] = defaultdict(list)
    review_seen: Counter[str] = Counter()
    low_path = out_dir / "low_confidence_samples.jsonl"
    prompt_path = out_dir / "llm_review_prompts.jsonl"
    low_count = 0
    with meta.open("r", encoding="utf-8") as f, low_path.open("w", encoding="utf-8") as low, prompt_path.open("w", encoding="utf-8") as prm:
        for line in f:
            r = json.loads(line)
            d, sp = r["dataset"], r["split"]
            split_counts[(d, sp)] += 1
            fields = {
                "visual_substrate": r.get("visual_substrate"),
                "skill_type_primary": r.get("skill_type_primary"),
                "skill_type_secondary": r.get("skill_type_secondary"),
                "evidence_type_primary": r.get("evidence_type_primary"),
                "evidence_type_secondary": r.get("evidence_type_secondary"),
                "evidence_source_primary": r.get("evidence_source_primary"),
                "evidence_scope": r.get("evidence_scope"),
                "evidence_complexity": r.get("evidence_complexity"),
                "evidence_complexity_level": r.get("evidence_complexity_level"),
                "reasoning_hops": r.get("reasoning_hops"),
                "answer_type": r.get("answer_type"),
                "protocol_type": r.get("protocol_type"),
                "requires_external_knowledge": str(r.get("requires_external_knowledge")),
            }
            for k, v in fields.items():
                if v:
                    stats[(d, sp, k, str(v))] += 1
            if float(r.get("overall_label_confidence", 1.0)) < threshold:
                low.write(json.dumps(r, ensure_ascii=False) + "\n")
                prm.write(json.dumps(llm_prompt(r), ensure_ascii=False) + "\n")
                low_count += 1
            review_seen[d] += 1
            seen = review_seen[d]
            if len(review_pool[d]) < review_n:
                review_pool[d].append(r)
            else:
                j = rng.randint(1, seen)
                if j <= review_n:
                    review_pool[d][j - 1] = r

    totals: Counter[tuple[str, str, str]] = Counter()
    for (d, sp, field, _), c in stats.items():
        totals[(d, sp, field)] += c
    stats_path = out_dir / "dataset_label_stats.csv"
    with stats_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dataset", "split", "field", "label", "count", "ratio"])
        w.writeheader()
        for (d, sp, field, lab), c in sorted(stats.items()):
            t = totals[(d, sp, field)]
            w.writerow({"dataset": d, "split": sp, "field": field, "label": lab, "count": c, "ratio": round(c / t, 6) if t else 0})
    counts_path = out_dir / "dataset_split_counts.csv"
    with counts_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["dataset", "split", "count"])
        w.writeheader()
        for (d, sp), c in sorted(split_counts.items()):
            w.writerow({"dataset": d, "split": sp, "count": c})
    review_path = out_dir / "human_review_samples.jsonl"
    write_jsonl(review_path, [r for rows in review_pool.values() for r in rows])
    print(f"Wrote stats: {stats_path}")
    print(f"Wrote split counts: {counts_path}")
    print(f"Wrote low-confidence samples: {low_path} ({low_count})")
    print(f"Wrote human review samples: {review_path}")
    print(f"Wrote LLM review prompts: {prompt_path}")


def cmd_build(args: argparse.Namespace) -> int:
    out_dir = args.output_root / "metadata"
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = out_dir / "sample_metadata.jsonl"
    empty = []
    with meta.open("w", encoding="utf-8") as out:
        for d in args.datasets:
            print(f"[build] {d}", file=sys.stderr)
            n = 0
            try:
                for r in iter_labeled(d, args.raw_root, args.max_samples_per_dataset):
                    out.write(json.dumps(r, ensure_ascii=False) + "\n")
                    n += 1
            except Exception as e:
                print(f"[error] {d}: {e}", file=sys.stderr)
                if args.fail_on_empty:
                    raise
            if n == 0:
                empty.append(d)
                print(f"[warn] no samples written for {d}", file=sys.stderr)
    print(f"Wrote metadata: {meta}")
    if empty and args.fail_on_empty:
        return 2
    write_stats(meta, out_dir, args.low_confidence_threshold, args.review_per_dataset, args.seed)
    return 0


def js(a: Counter[str], b: Counter[str]) -> float:
    labels = sorted(set(a) | set(b))
    sa, sb = sum(a.values()), sum(b.values())
    if not sa or not sb:
        return 0.0
    pa, pb = [a[x] / sa for x in labels], [b[x] / sb for x in labels]
    pm = [(x + y) / 2 for x, y in zip(pa, pb)]
    def kl(p: list[float], q: list[float]) -> float:
        return sum(x * math.log2(x / y) for x, y in zip(p, q) if x > 0 and y > 0)
    return 0.5 * kl(pa, pm) + 0.5 * kl(pb, pm)


def jacc(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def dist(rows: list[dict[str, Any]], field: str) -> Counter[str]:
    return Counter(str(r[field]) for r in rows if r.get(field) not in {None, ""})


def top(c: Counter[str], k: int = 5) -> str:
    s = sum(c.values())
    return "" if not s else "; ".join(f"{lab}:{n/s:.2f}" for lab, n in c.most_common(k))


def load_transitions(path: Path | None) -> list[tuple[str, str, str]]:
    if path is None:
        return [
            ("T_nat_to_struct", "natural_photo_qa", "structured_visual_qa"),
            ("T_nat_to_knowledge", "natural_photo_qa", "knowledge_intensive_qa"),
            ("T_struct_to_medical", "structured_visual_qa", "expert_medical_qa"),
            ("T_struct_to_remote", "structured_visual_qa", "expert_remote_sensing_qa"),
        ]
    with path.open("r", encoding="utf-8", newline="") as f:
        return [(r["transition_id"], r["old_regime"], r["new_regime"]) for r in csv.DictReader(f)]


def cmd_gaps(args: argparse.Namespace) -> int:
    regimes: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with args.metadata.open("r", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if args.split != "all" and r.get("split") != args.split:
                continue
            if float(r.get("overall_label_confidence", 0.0)) < args.min_confidence:
                continue
            regimes[r["regime"]].append(r)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    field_map = {
        "visual_gap": "visual_substrate",
        "skill_gap": "skill_type_primary",
        "evidence_gap": "evidence_type_primary",
        "evidence_complexity_gap": "evidence_complexity",
        "answer_distribution_gap": "answer_type",
    }
    fields = ["transition_id", "old_regime", "new_regime", "old_n", "new_n", "visual_gap", "skill_gap", "evidence_gap", "evidence_complexity_gap", "answer_distribution_gap", "answer_vocab_overlap", "metadata_overlap_score", "old_visual_top", "new_visual_top", "old_skill_top", "new_skill_top", "old_evidence_top", "new_evidence_top", "old_complexity_top", "new_complexity_top", "old_answer_type_top", "new_answer_type_top"]
    with args.output.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for tid, old, new in load_transitions(args.transitions):
            old_rows, new_rows = regimes.get(old, []), regimes.get(new, [])
            gaps, tops, sims = {}, {}, []
            for g, field in field_map.items():
                od, nd = dist(old_rows, field), dist(new_rows, field)
                val = js(od, nd)
                gaps[g] = val
                sims.append(1.0 - val)
                tops[f"old_{field}"], tops[f"new_{field}"] = top(od), top(nd)
            ov = {r.get("normalized_answer", "") for r in old_rows if r.get("normalized_answer")}
            nv = {r.get("normalized_answer", "") for r in new_rows if r.get("normalized_answer")}
            ans_overlap = jacc(ov, nv)
            sims.append(ans_overlap)
            w.writerow({
                "transition_id": tid,
                "old_regime": old,
                "new_regime": new,
                "old_n": len(old_rows),
                "new_n": len(new_rows),
                "visual_gap": round(gaps["visual_gap"], 6),
                "skill_gap": round(gaps["skill_gap"], 6),
                "evidence_gap": round(gaps["evidence_gap"], 6),
                "evidence_complexity_gap": round(gaps["evidence_complexity_gap"], 6),
                "answer_distribution_gap": round(gaps["answer_distribution_gap"], 6),
                "answer_vocab_overlap": round(ans_overlap, 6),
                "metadata_overlap_score": round(sum(sims) / len(sims), 6),
                "old_visual_top": tops["old_visual_substrate"],
                "new_visual_top": tops["new_visual_substrate"],
                "old_skill_top": tops["old_skill_type_primary"],
                "new_skill_top": tops["new_skill_type_primary"],
                "old_evidence_top": tops["old_evidence_type_primary"],
                "new_evidence_top": tops["new_evidence_type_primary"],
                "old_complexity_top": tops["old_evidence_complexity"],
                "new_complexity_top": tops["new_evidence_complexity"],
                "old_answer_type_top": tops["old_answer_type"],
                "new_answer_type_top": tops["new_answer_type"],
            })
    print(f"Wrote transition gaps: {args.output}")
    return 0


def normalize_skill_name(value: Any, allowed: set[str]) -> str | None:
    if value is None:
        return None
    key = norm_key(compact(value))
    if not key or key in {"none", "null", "na", "n_a", "unknown"}:
        return None
    key = SKILL_ALIASES.get(key, key)
    return key if key in allowed else None


def parse_json_object(text: str) -> dict[str, Any]:
    content = text.strip()

    # Logs often contain repr(content), including outer quotes and escaped text.
    if len(content) >= 2 and content[0] == content[-1] and content[0] in {"'", '"'}:
        try:
            decoded = ast.literal_eval(content)
            if isinstance(decoded, str):
                content = decoded.strip()
        except (SyntaxError, ValueError):
            pass

    # Qwen thinking models may put long reasoning and JSON examples before the
    # final answer. Only the text after the last closing tag is authoritative.
    if "</think>" in content:
        content = content.rsplit("</think>", 1)[1].strip()
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL | re.IGNORECASE).strip()

    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content, flags=re.IGNORECASE)
        content = re.sub(r"\s*```$", "", content)
    try:
        obj = json.loads(content)
        if isinstance(obj, dict):
            return obj
        if isinstance(obj, list):
            return {"labels": obj}
    except json.JSONDecodeError:
        pass

    # Scan every possible JSON start. This avoids greedy regex matching across
    # multiple examples in chain-of-thought text and prefers the final answer.
    decoder = json.JSONDecoder()
    candidates: list[dict[str, Any]] = []
    for index, char in enumerate(content):
        if char not in "[{":
            continue
        try:
            obj, _ = decoder.raw_decode(content[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("labels"), list):
            candidates.append(obj)
        elif isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
            candidates.append({"labels": obj})
        elif isinstance(obj, dict) and obj.get("id"):
            candidates.append({"labels": [obj]})
    if candidates:
        return candidates[-1]

    prefix = content[:200].replace("\n", "\\n")
    suffix = content[-200:].replace("\n", "\\n")
    raise ValueError(f"No valid labels JSON found in LLM response; prefix={prefix!r}, suffix={suffix!r}")


_PARQUET_FILE_CACHE: dict[str, Any] = {}
_PARQUET_IMAGE_GROUP_CACHE_KEY: tuple[str, int, str] | None = None
_PARQUET_IMAGE_GROUP_CACHE_VALUES: list[Any] | None = None


def normalize_taxonomy_name(value: Any, allowed: set[str], aliases: dict[str, str]) -> str | None:
    if value is None:
        return None
    key = norm_key(compact(value))
    if not key or key in {"none", "null", "na", "n_a", "unknown"}:
        return None
    key = aliases.get(key, key)
    return key if key in allowed else None


def image_mime(data: bytes, path_hint: str | None = None) -> str:
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data.startswith((b"GIF87a", b"GIF89a")):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    guessed = mimetypes.guess_type(path_hint or "")[0]
    return guessed if guessed and guessed.startswith("image/") else "image/jpeg"


def image_search_roots(row: dict[str, Any], args: argparse.Namespace) -> list[Path]:
    roots: list[Path] = []
    for root in args.image_roots or []:
        roots.append(Path(root).expanduser())
    roots.extend([Path.cwd(), args.raw_root])
    source = Path(compact(row.get("source_file"))).expanduser()
    if source:
        roots.extend(list(source.parents)[:6])
    unique: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        key = str(root)
        if key not in seen:
            seen.add(key)
            unique.append(root)
    return unique


def resolve_image_path(reference: str, roots: list[Path]) -> Path | None:
    ref = reference.strip()
    if not ref or ref.startswith("<embedded_image_bytes:"):
        return None
    path = Path(ref).expanduser()
    if path.is_absolute() and path.is_file():
        return path
    relative = Path(ref[2:] if ref.startswith("./") else ref)
    for root in roots:
        candidate = root / relative
        if candidate.is_file():
            return candidate
    return None


def image_bytes_from_value(value: Any, roots: list[Path]) -> tuple[bytes, str, str] | None:
    if value is None:
        return None
    if isinstance(value, memoryview):
        value = value.tobytes()
    if isinstance(value, bytearray):
        value = bytes(value)
    if isinstance(value, bytes):
        return value, image_mime(value), "embedded_bytes"
    if isinstance(value, str):
        path = resolve_image_path(value, roots)
        if path:
            data = path.read_bytes()
            return data, image_mime(data, str(path)), str(path)
        return None
    if isinstance(value, dict):
        if value.get("bytes") is not None:
            result = image_bytes_from_value(value["bytes"], roots)
            if result:
                return result
        for key in ("path", "url", "image", "file_name", "filename"):
            if value.get(key):
                result = image_bytes_from_value(value[key], roots)
                if result:
                    return result
        return None
    if isinstance(value, (list, tuple)):
        for item in value:
            result = image_bytes_from_value(item, roots)
            if result:
                return result
    return None


def parquet_image_value(source_file: Path, source_index: int) -> Any:
    global _PARQUET_IMAGE_GROUP_CACHE_KEY, _PARQUET_IMAGE_GROUP_CACHE_VALUES
    try:
        import pyarrow.parquet as pq  # type: ignore
    except Exception as error:
        raise RuntimeError("Reading embedded Parquet images requires pyarrow: pip install pyarrow") from error

    cache_key = str(source_file)
    parquet_file = _PARQUET_FILE_CACHE.get(cache_key)
    if parquet_file is None:
        parquet_file = pq.ParquetFile(source_file)
        _PARQUET_FILE_CACHE[cache_key] = parquet_file
    names = list(parquet_file.schema_arrow.names)
    normalized = {norm_key(name): name for name in names}
    image_column = next((normalized[norm_key(name)] for name in I_FIELDS if norm_key(name) in normalized), None)
    if image_column is None:
        raise KeyError(f"No image column found in {source_file}; columns={names}")

    remaining = source_index
    for row_group in range(parquet_file.num_row_groups):
        row_count = parquet_file.metadata.row_group(row_group).num_rows
        if remaining < row_count:
            group_key = (cache_key, row_group, image_column)
            if _PARQUET_IMAGE_GROUP_CACHE_KEY != group_key:
                table = parquet_file.read_row_group(row_group, columns=[image_column])
                _PARQUET_IMAGE_GROUP_CACHE_VALUES = [
                    row[image_column] for row in table.to_pylist()
                ]
                _PARQUET_IMAGE_GROUP_CACHE_KEY = group_key
            assert _PARQUET_IMAGE_GROUP_CACHE_VALUES is not None
            return _PARQUET_IMAGE_GROUP_CACHE_VALUES[remaining]
        remaining -= row_count
    raise IndexError(f"source_index={source_index} is outside {source_file}")


def image_url_for_row(row: dict[str, Any], args: argparse.Namespace) -> tuple[str | None, str]:
    reference = row.get("image")
    if isinstance(reference, str) and reference.startswith(("http://", "https://", "data:image/")):
        return reference, reference[:200]

    roots = image_search_roots(row, args)
    result = image_bytes_from_value(reference, roots)
    source_file = Path(compact(row.get("source_file"))).expanduser()
    if result is None and source_file.is_file() and source_file.suffix.lower() == ".parquet":
        value = parquet_image_value(source_file, int(row.get("source_index", 0)))
        result = image_bytes_from_value(value, roots)
    if result is None:
        if args.allow_text_only:
            return None, "text_only_missing_image"
        raise FileNotFoundError(
            f"Cannot resolve image for id={row.get('id')}, image={reference!r}, source_file={source_file}"
        )

    data, mime, source = result
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{encoded}", source


def compute_evidence_complexity(
    evidence_scope: str,
    evidence_count: int,
    reasoning_hops: int,
    requires_external_knowledge: bool,
) -> dict[str, Any]:
    scope_level = {
        "single_region": 1,
        "global_image": 1,
        "multi_region": 2,
        "cross_region": 3,
        "cross_page": 4,
        "image_plus_knowledge": 4,
    }.get(evidence_scope, 1)
    count_level = 1 if evidence_count <= 1 else (2 if evidence_count <= 3 else 3)
    hop_level = 1 if reasoning_hops <= 0 else (2 if reasoning_hops == 1 else (3 if reasoning_hops == 2 else 4))
    knowledge_level = 4 if requires_external_knowledge else 1
    level = max(scope_level, count_level, hop_level, knowledge_level)
    labels = {
        1: "single_evidence",
        2: "multi_evidence",
        3: "cross_region_or_multihop",
        4: "cross_context",
    }
    score = (
        scope_level
        + min(max(evidence_count - 1, 0), 2)
        + min(max(reasoning_hops, 0), 3)
        + int(requires_external_knowledge)
    )
    return {
        "evidence_complexity": labels[level],
        "evidence_complexity_level": level,
        "evidence_complexity_score": score,
    }


def llm_sample_view(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "dataset": row.get("dataset"),
        "visual_substrate": row.get("visual_substrate"),
        "question": question_for_label(row.get("question_for_label") or row.get("question", "")),
        "answer": row.get("answer"),
        "choices": row.get("choices"),
    }


def llm_skill_cache_key(row: dict[str, Any], model: str) -> str:
    payload = {"model": model, **llm_sample_view(row)}
    payload.pop("id", None)
    return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load_cache(path: Path | None) -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    if path is None or not path.exists():
        return cache
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("cache_key"):
                cache[row["cache_key"]] = row
    return cache


def append_cache(path: Path | None, row: dict[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def call_openai_compatible(
    api_base: str,
    api_key: str | None,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float,
    max_tokens: int,
    timeout: int,
    enable_thinking: bool | None,
    json_mode: bool = False,
) -> str:
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    if enable_thinking is not None:
        payload["chat_template_kwargs"] = {"enable_thinking": enable_thinking}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        obj = json.loads(response.read().decode("utf-8"))
    content = obj["choices"][0]["message"]["content"]
    if isinstance(content, list):
        return "".join(compact(part.get("text")) for part in content if isinstance(part, dict))
    return compact(content)


def request_llm_skill_labels(rows: list[dict[str, Any]], args: argparse.Namespace) -> dict[str, dict[str, Any]]:
    user_payload = {
        "task": "Label each sample independently. Answer-format instruction words are not visual evidence.",
        "allowed_primary_skills": sorted(PRIMARY_SKILLS),
        "allowed_secondary_skills": sorted(SECONDARY_SKILLS),
        "samples": [llm_sample_view(row) for row in rows],
    }
    messages = [
        {"role": "system", "content": LLM_SKILL_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]
    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            content = call_openai_compatible(
                args.api_base,
                args.api_key,
                args.model,
                messages,
                args.temperature,
                args.max_tokens,
                args.timeout,
                args.enable_thinking if "qwen" in args.model.lower() else None,
            )
            labels = parse_json_object(content).get("labels")
            if not isinstance(labels, list):
                raise ValueError("LLM JSON must contain a labels list")
            return {
                str(item["id"]): item
                for item in labels
                if isinstance(item, dict) and item.get("id")
            }
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as error:
            last_error = error
            if attempt < args.retries:
                time.sleep(args.retry_sleep * (attempt + 1))
    raise RuntimeError(f"LLM skill labeling failed after {args.retries + 1} attempts: {last_error}")


def apply_skill_refinement(
    row: dict[str, Any],
    item: dict[str, Any],
    model: str,
    cache_key: str,
) -> dict[str, Any]:
    old_primary = row.get("skill_type_primary")
    old_secondary = row.get("skill_type_secondary")
    new_primary = normalize_skill_name(item.get("skill_type_primary"), PRIMARY_SKILLS) or old_primary or "recognition"
    new_secondary = normalize_skill_name(item.get("skill_type_secondary"), SECONDARY_SKILLS)
    if new_secondary == new_primary:
        new_secondary = None
    try:
        confidence = max(0.0, min(1.0, float(item.get("confidence", 0.75))))
    except (TypeError, ValueError):
        confidence = 0.75

    refined = dict(row)
    refined.setdefault("question_for_label", question_for_label(refined.get("question", "")))
    refined["skill_type_primary_rule"] = old_primary
    refined["skill_type_secondary_rule"] = old_secondary
    refined["skill_type_primary"] = new_primary
    refined["skill_type_secondary"] = new_secondary
    if isinstance(item.get("requires_external_knowledge"), bool):
        refined["requires_external_knowledge"] = item["requires_external_knowledge"]
    elif new_primary in {"knowledge_reasoning", "medical_reasoning", "remote_sensing_reasoning"}:
        refined["requires_external_knowledge"] = True

    dataset = refined.get("dataset")
    evidence_confidence = 0.70
    if dataset in DATASETS:
        sample = {
            "_dataset": dataset,
            "question": refined.get("question", ""),
            "raw_metadata": refined.get("raw_metadata", {}),
        }
        ep, es, evidence_confidence, _ = evidence_type(
            sample,
            new_primary,
            new_secondary,
            DATASETS[dataset],
        )
        refined["evidence_type_primary"] = ep
        refined["evidence_type_secondary"] = es

    sources = dict(refined.get("label_source") or {})
    sources["skill_type"] = "llm_question"
    sources["evidence_type"] = "llm_skill+rule"
    refined["label_source"] = sources

    confidences = dict(refined.get("label_confidence") or {})
    confidences["skill_type"] = confidence
    confidences["evidence_type"] = min(evidence_confidence, confidence)
    if "requires_external_knowledge" in item:
        confidences["requires_external_knowledge"] = confidence
    refined["label_confidence"] = confidences
    refined["overall_label_confidence"] = min(float(value) for value in confidences.values()) if confidences else confidence
    refined["llm_skill_judgment"] = {
        "model": model,
        "cache_key": cache_key,
        "previous_primary": old_primary,
        "previous_secondary": old_secondary,
        "raw_label": safe_json(item),
    }
    return refined


def refine_skill_batch(
    rows: list[dict[str, Any]],
    args: argparse.Namespace,
    cache: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    labels: dict[str, dict[str, Any]] = {}
    keys: dict[str, str] = {}
    uncached: list[dict[str, Any]] = []
    for row in rows:
        key = llm_skill_cache_key(row, args.model)
        keys[row["id"]] = key
        if key in cache:
            labels[row["id"]] = cache[key]["label"]
        else:
            uncached.append(row)

    if uncached:
        returned = request_llm_skill_labels(uncached, args)
        for row in uncached:
            item = returned.get(row["id"])
            if item is None:
                if args.fail_on_error:
                    raise RuntimeError(f"LLM did not return label for {row['id']}")
                item = {
                    "id": row["id"],
                    "skill_type_primary": row.get("skill_type_primary"),
                    "skill_type_secondary": row.get("skill_type_secondary"),
                    "requires_external_knowledge": row.get("requires_external_knowledge"),
                    "confidence": row.get("label_confidence", {}).get("skill_type", 0.50),
                    "error": "missing_llm_label",
                }
            labels[row["id"]] = item
            cache_row = {
                "cache_key": keys[row["id"]],
                "id": row["id"],
                "model": args.model,
                "label": item,
            }
            cache[keys[row["id"]]] = cache_row
            append_cache(args.cache, cache_row)

    return [
        apply_skill_refinement(row, labels[row["id"]], args.model, keys[row["id"]])
        for row in rows
    ]


def cmd_refine_skills(args: argparse.Namespace) -> int:
    args.api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY") or "EMPTY"
    args.api_base = (
        args.api_base
        or os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "http://127.0.0.1:8000/v1"
    )
    if args.metadata.resolve() == args.output.resolve():
        raise SystemExit("--output must differ from --metadata; the source metadata is never overwritten")
    if args.cache is None and not args.no_cache:
        args.cache = args.output.with_suffix(".cache.jsonl")

    dataset_filter = set(args.datasets or [])
    split_filter = set(args.splits or [])
    cache = load_cache(None if args.no_cache else args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending: list[dict[str, Any]] = []
    total = refined_count = unchanged = errors = 0

    def should_refine(row: dict[str, Any]) -> bool:
        if dataset_filter and row.get("dataset") not in dataset_filter:
            return False
        if split_filter and row.get("split") not in split_filter:
            return False
        if args.only_rule_source and "llm" in compact((row.get("label_source") or {}).get("skill_type")).lower():
            return False
        if args.limit is not None and refined_count + len(pending) >= args.limit:
            return False
        return True

    def flush(output_file) -> None:
        nonlocal pending, refined_count, errors
        if not pending:
            return
        try:
            output_rows = refine_skill_batch(pending, args, cache)
        except Exception as error:
            if args.fail_on_error:
                raise
            print(f"[warn] skill refinement batch failed: {error}", file=sys.stderr)
            output_rows = []
            for row in pending:
                fallback = dict(row)
                fallback["llm_skill_error"] = repr(error)
                output_rows.append(fallback)
                errors += 1
        for row in output_rows:
            output_file.write(json.dumps(row, ensure_ascii=False) + "\n")
        refined_count += len(pending)
        print(f"[refine-skills] processed={refined_count}", file=sys.stderr)
        pending = []

    with args.metadata.open("r", encoding="utf-8") as source, args.output.open("w", encoding="utf-8") as output:
        for line in source:
            if not line.strip():
                continue
            total += 1
            row = json.loads(line)
            if should_refine(row):
                pending.append(row)
                if len(pending) >= args.batch_size:
                    flush(output)
            else:
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
                unchanged += 1
        flush(output)

    print(f"Wrote LLM-refined metadata: {args.output}")
    print(f"total={total}, refined={refined_count}, unchanged={unchanged}, errors={errors}")
    if args.cache and not args.no_cache:
        print(f"Wrote/used cache: {args.cache}")
    return 0


def vlm_metadata_cache_key(row: dict[str, Any], model: str) -> str:
    payload = {
        "schema": VLM_METADATA_SCHEMA_VERSION,
        "model": model,
        "id": row.get("id"),
        "dataset": row.get("dataset"),
        "question": question_for_label(row.get("question_for_label") or row.get("question", "")),
        "answer": row.get("answer"),
        "choices": row.get("choices"),
        "image": row.get("image"),
        "source_file": row.get("source_file"),
        "source_index": row.get("source_index"),
    }
    return hashlib.sha1(json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def vlm_messages(
    prepared_rows: list[tuple[dict[str, Any], str | None, str]],
) -> list[dict[str, Any]]:
    content: list[dict[str, Any]] = [
        {
            "type": "text",
            "text": (
                f"Schema version: {VLM_METADATA_SCHEMA_VERSION}. "
                f"Annotate exactly {len(prepared_rows)} samples. Each image belongs only to the sample marker immediately before it."
            ),
        }
    ]
    for index, (row, image_url, _) in enumerate(prepared_rows, 1):
        content.append({"type": "text", "text": f"BEGIN SAMPLE {index}; id={row['id']}"})
        if image_url:
            content.append({"type": "image_url", "image_url": {"url": image_url}})
        sample_text = {
            "id": row["id"],
            "dataset": row.get("dataset"),
            "question": question_for_label(row.get("question_for_label") or row.get("question", "")),
            "reference_answer": row.get("answer"),
            "choices": row.get("choices"),
            "image_available": bool(image_url),
        }
        content.append({"type": "text", "text": json.dumps(sample_text, ensure_ascii=False)})
        content.append({"type": "text", "text": f"END SAMPLE {index}; id={row['id']}"})
    return [
        {"role": "system", "content": VLM_METADATA_SYSTEM_PROMPT},
        {"role": "user", "content": content},
    ]


def request_vlm_metadata_labels(
    prepared_rows: list[tuple[dict[str, Any], str | None, str]],
    args: argparse.Namespace,
) -> dict[str, dict[str, Any]]:
    messages = vlm_messages(prepared_rows)
    last_error: Exception | None = None
    for attempt in range(args.retries + 1):
        try:
            content = call_openai_compatible(
                args.api_base,
                args.api_key,
                args.model,
                messages,
                args.temperature,
                args.max_tokens,
                args.timeout,
                args.enable_thinking if "qwen" in args.model.lower() else None,
                args.json_mode,
            )
            labels = parse_json_object(content).get("labels")
            if not isinstance(labels, list):
                raise ValueError("VLM JSON must contain a labels list")
            returned = {
                str(item["id"]): item
                for item in labels
                if isinstance(item, dict) and item.get("id")
            }
            expected = {row["id"] for row, _, _ in prepared_rows}
            missing = expected - set(returned)
            if missing:
                raise ValueError(f"VLM omitted {len(missing)} ids: {sorted(missing)[:5]}")
            return returned
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, KeyError, ValueError) as error:
            last_error = error
            if attempt < args.retries:
                time.sleep(args.retry_sleep * (attempt + 1))
    raise RuntimeError(f"VLM metadata labeling failed after {args.retries + 1} attempts: {last_error}")


def confidence_value(confidence: Any, field: str, default: float = 0.75) -> float:
    value = confidence.get(field, default) if isinstance(confidence, dict) else confidence
    try:
        return max(0.0, min(1.0, float(value)))
    except (TypeError, ValueError):
        return default


def apply_vlm_metadata_refinement(
    row: dict[str, Any],
    item: dict[str, Any],
    model: str,
    cache_key: str,
    media_source: str,
) -> dict[str, Any]:
    refined = dict(row)
    refined.setdefault("question_for_label", question_for_label(refined.get("question", "")))

    visual = normalize_taxonomy_name(
        item.get("visual_substrate"),
        VISUAL_SUBSTRATES,
        VISUAL_SUBSTRATE_ALIASES,
    ) or refined.get("visual_substrate") or "other"
    skill_primary = normalize_skill_name(item.get("skill_type_primary"), PRIMARY_SKILLS) or refined.get("skill_type_primary") or "recognition"
    skill_secondary = normalize_skill_name(item.get("skill_type_secondary"), SECONDARY_SKILLS)
    if skill_secondary == skill_primary:
        skill_secondary = None
    evidence_source_primary = normalize_taxonomy_name(
        item.get("evidence_source_primary"),
        EVIDENCE_SOURCES,
        EVIDENCE_SOURCE_ALIASES,
    ) or "other"
    evidence_source_secondary = normalize_taxonomy_name(
        item.get("evidence_source_secondary"),
        EVIDENCE_SOURCES,
        EVIDENCE_SOURCE_ALIASES,
    )
    if evidence_source_secondary == evidence_source_primary:
        evidence_source_secondary = None
    evidence_scope = normalize_taxonomy_name(
        item.get("evidence_scope"),
        EVIDENCE_SCOPES,
        EVIDENCE_SCOPE_ALIASES,
    ) or "single_region"
    try:
        evidence_count = max(0, min(99, int(item.get("evidence_count", 1))))
    except (TypeError, ValueError):
        evidence_count = 1
    try:
        reasoning_hops = max(0, min(9, int(item.get("reasoning_hops", 0))))
    except (TypeError, ValueError):
        reasoning_hops = 0
    requires_knowledge = item.get("requires_external_knowledge")
    if not isinstance(requires_knowledge, bool):
        requires_knowledge = skill_primary in {
            "knowledge_reasoning",
            "medical_reasoning",
            "remote_sensing_reasoning",
        }
    if requires_knowledge and evidence_scope not in {"cross_page", "image_plus_knowledge"}:
        evidence_scope = "image_plus_knowledge"
    answer_type_vlm = normalize_taxonomy_name(item.get("answer_type"), ANSWER_TYPES, {})

    refined.setdefault("visual_substrate_rule", refined.get("visual_substrate"))
    refined.setdefault("skill_type_primary_rule", refined.get("skill_type_primary"))
    refined.setdefault("skill_type_secondary_rule", refined.get("skill_type_secondary"))
    refined.setdefault("evidence_type_primary_rule", refined.get("evidence_type_primary"))
    refined.setdefault("evidence_type_secondary_rule", refined.get("evidence_type_secondary"))
    refined.setdefault("answer_type_rule", refined.get("answer_type"))

    refined["visual_substrate"] = visual
    refined["visual_substrate_vlm"] = visual
    refined["skill_type_primary"] = skill_primary
    refined["skill_type_secondary"] = skill_secondary
    refined["evidence_source_primary"] = evidence_source_primary
    refined["evidence_source_secondary"] = evidence_source_secondary
    refined["evidence_scope"] = evidence_scope
    refined["evidence_count"] = evidence_count
    refined["reasoning_hops"] = reasoning_hops
    refined["evidence_type_primary"] = evidence_scope
    refined["evidence_type_secondary"] = evidence_source_primary
    refined["requires_external_knowledge"] = requires_knowledge
    refined["answer_type_vlm"] = answer_type_vlm
    refined.update(
        compute_evidence_complexity(
            evidence_scope,
            evidence_count,
            reasoning_hops,
            requires_knowledge,
        )
    )

    confidence = item.get("confidence", 0.75)
    sources = dict(refined.get("label_source") or {})
    sources.update(
        {
            "visual_substrate": "vlm_image_question",
            "skill_type": "vlm_image_question",
            "evidence_type": "vlm_image_question",
            "requires_external_knowledge": "vlm_image_question",
            "answer_type_vlm": "vlm_image_question",
            "evidence_complexity": "deterministic_from_vlm_factors",
        }
    )
    refined["label_source"] = sources
    confidences = dict(refined.get("label_confidence") or {})
    confidences.update(
        {
            "visual_substrate": confidence_value(confidence, "visual_substrate"),
            "skill_type": confidence_value(confidence, "skill_type"),
            "evidence_type": confidence_value(confidence, "evidence"),
            "requires_external_knowledge": confidence_value(confidence, "requires_external_knowledge"),
            "answer_type_vlm": confidence_value(confidence, "answer_type"),
        }
    )
    refined["label_confidence"] = confidences
    refined["overall_label_confidence"] = min(float(value) for value in confidences.values())
    refined["vlm_metadata_judgment"] = {
        "schema_version": VLM_METADATA_SCHEMA_VERSION,
        "model": model,
        "cache_key": cache_key,
        "media_source": media_source,
        "raw_label": safe_json(item),
    }
    return refined


def refine_metadata_batch(
    rows: list[dict[str, Any]],
    args: argparse.Namespace,
    cache: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    keys: dict[str, str] = {}
    labels: dict[str, dict[str, Any]] = {}
    media_sources: dict[str, str] = {}
    prepared: list[tuple[dict[str, Any], str | None, str]] = []
    failed: dict[str, str] = {}

    for row in rows:
        key = vlm_metadata_cache_key(row, args.model)
        keys[row["id"]] = key
        if key in cache:
            labels[row["id"]] = cache[key]["label"]
            media_sources[row["id"]] = cache[key].get("media_source", "cache")
            continue
        try:
            image_url, media_source = image_url_for_row(row, args)
            prepared.append((row, image_url, media_source))
            media_sources[row["id"]] = media_source
        except Exception as error:
            if args.fail_on_error:
                raise
            failed[row["id"]] = repr(error)

    if prepared:
        returned = request_vlm_metadata_labels(prepared, args)
        for row, _, media_source in prepared:
            item = returned[row["id"]]
            labels[row["id"]] = item
            cache_row = {
                "cache_key": keys[row["id"]],
                "id": row["id"],
                "model": args.model,
                "schema_version": VLM_METADATA_SCHEMA_VERSION,
                "media_source": media_source,
                "label": item,
            }
            cache[keys[row["id"]]] = cache_row
            append_cache(args.cache, cache_row)

    output: list[dict[str, Any]] = []
    for row in rows:
        if row["id"] in failed:
            fallback = dict(row)
            fallback["vlm_metadata_error"] = failed[row["id"]]
            output.append(fallback)
        else:
            output.append(
                apply_vlm_metadata_refinement(
                    row,
                    labels[row["id"]],
                    args.model,
                    keys[row["id"]],
                    media_sources[row["id"]],
                )
            )
    return output


def cmd_refine_metadata(args: argparse.Namespace) -> int:
    args.api_key = args.api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("VLLM_API_KEY") or "EMPTY"
    args.api_base = (
        args.api_base
        or os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "http://127.0.0.1:8000/v1"
    )
    args.raw_root = args.raw_root.expanduser().resolve()
    args.image_roots = [root.expanduser().resolve() for root in args.image_roots or []]
    if args.metadata.resolve() == args.output.resolve():
        raise SystemExit("--output must differ from --metadata")
    if args.cache is None and not args.no_cache:
        args.cache = args.output.with_suffix(".cache.jsonl")

    dataset_filter = set(args.datasets or [])
    split_filter = set(args.splits or [])
    cache = load_cache(None if args.no_cache else args.cache)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pending: list[dict[str, Any]] = []
    total = refined_count = unchanged = errors = 0

    def should_refine(row: dict[str, Any]) -> bool:
        if dataset_filter and row.get("dataset") not in dataset_filter:
            return False
        if split_filter and row.get("split") not in split_filter:
            return False
        if args.only_unlabeled and "vlm" in compact((row.get("label_source") or {}).get("visual_substrate")).lower():
            return False
        if args.limit is not None and refined_count + len(pending) >= args.limit:
            return False
        return True

    def flush(output_file) -> None:
        nonlocal pending, refined_count, errors
        if not pending:
            return
        try:
            output_rows = refine_metadata_batch(pending, args, cache)
        except Exception as error:
            if args.fail_on_error:
                raise
            print(f"[warn] VLM metadata batch failed: {error}", file=sys.stderr)
            output_rows = []
            for row in pending:
                fallback = dict(row)
                fallback["vlm_metadata_error"] = repr(error)
                output_rows.append(fallback)
        for row in output_rows:
            errors += int("vlm_metadata_error" in row)
            output_file.write(json.dumps(row, ensure_ascii=False) + "\n")
        refined_count += len(pending)
        print(f"[refine-metadata] processed={refined_count}, errors={errors}", file=sys.stderr)
        pending = []

    with args.metadata.open("r", encoding="utf-8") as source, args.output.open("w", encoding="utf-8") as output:
        for line in source:
            if not line.strip():
                continue
            total += 1
            row = json.loads(line)
            if should_refine(row):
                pending.append(row)
                if len(pending) >= args.batch_size:
                    flush(output)
            else:
                output.write(json.dumps(row, ensure_ascii=False) + "\n")
                unchanged += 1
        flush(output)

    print(f"Wrote VLM-refined metadata: {args.output}")
    print(f"total={total}, refined={refined_count}, unchanged={unchanged}, errors={errors}")
    if args.cache and not args.no_cache:
        print(f"Wrote/used cache: {args.cache}")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="CoIN Factor-1 metadata tool.")
    sub = p.add_subparsers(dest="cmd", required=True)
    common_datasets = list(DATASETS)

    inv = sub.add_parser("inventory")
    inv.add_argument("--raw-root", type=Path, default=Path("./cl_dataset/coin"))
    inv.add_argument("--output-root", type=Path, default=Path("./cl_dataset/coin_factor1_meta"))
    inv.add_argument("--datasets", nargs="+", default=common_datasets)
    inv.add_argument("--max-files-per-dataset", type=int, default=None)

    b = sub.add_parser("build")
    b.add_argument("--raw-root", type=Path, default=Path("./cl_dataset/coin"))
    b.add_argument("--output-root", type=Path, default=Path("./cl_dataset/coin_factor1_meta"))
    b.add_argument("--datasets", nargs="+", default=common_datasets)
    b.add_argument("--max-samples-per-dataset", type=int, default=None)
    b.add_argument("--review-per-dataset", type=int, default=200)
    b.add_argument("--low-confidence-threshold", type=float, default=0.70)
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--fail-on-empty", action="store_true")

    g = sub.add_parser("gaps")
    g.add_argument("--metadata", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/sample_metadata.jsonl"))
    g.add_argument("--output", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/transition_gap_table.csv"))
    g.add_argument("--transitions", type=Path, default=None)
    g.add_argument("--min-confidence", type=float, default=0.70)
    g.add_argument("--split", default="train")

    rs = sub.add_parser(
        "refine-skills",
        help="Relabel skill_type fields through an OpenAI-compatible LLM API.",
    )
    rs.add_argument("--metadata", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/sample_metadata.jsonl"))
    rs.add_argument("--output", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/sample_metadata.llm_skill.jsonl"))
    rs.add_argument("--cache", type=Path, default=None)
    rs.add_argument("--no-cache", action="store_true")
    rs.add_argument("--datasets", nargs="+", default=None)
    rs.add_argument("--splits", nargs="+", default=None)
    rs.add_argument("--limit", type=int, default=None)
    rs.add_argument("--batch-size", type=int, default=20)
    rs.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "qwen3.6"))
    rs.add_argument("--api-base", default=None)
    rs.add_argument("--api-key", default=None)
    rs.add_argument("--temperature", type=float, default=0.0)
    rs.add_argument("--max-tokens", type=int, default=4096)
    rs.add_argument("--timeout", type=int, default=120)
    rs.add_argument("--retries", type=int, default=2)
    rs.add_argument("--retry-sleep", type=float, default=2.0)
    rs.add_argument(
        "--enable-thinking",
        action="store_true",
        help="Enable Qwen thinking output. Disabled by default for deterministic classification.",
    )
    rs.add_argument("--only-rule-source", action="store_true")
    rs.add_argument("--fail-on-error", action="store_true")

    rm = sub.add_parser(
        "refine-metadata",
        help="Use a multimodal Qwen-compatible API to jointly label visual, skill, and evidence metadata.",
    )
    rm.add_argument("--metadata", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/sample_metadata.jsonl"))
    rm.add_argument("--output", type=Path, default=Path("./cl_dataset/coin_factor1_meta/metadata/sample_metadata.vlm.jsonl"))
    rm.add_argument("--raw-root", type=Path, default=Path("./cl_dataset/coin"))
    rm.add_argument("--image-root", dest="image_roots", action="append", type=Path, default=None)
    rm.add_argument("--cache", type=Path, default=None)
    rm.add_argument("--no-cache", action="store_true")
    rm.add_argument("--datasets", nargs="+", default=None)
    rm.add_argument("--splits", nargs="+", default=None)
    rm.add_argument("--limit", type=int, default=None)
    rm.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="Samples/images per API call. Keep 1 unless vLLM was launched with a larger multimodal limit.",
    )
    rm.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "qwen3.6"))
    rm.add_argument("--api-base", default=None)
    rm.add_argument("--api-key", default=None)
    rm.add_argument("--temperature", type=float, default=0.0)
    rm.add_argument("--max-tokens", type=int, default=4096)
    rm.add_argument("--timeout", type=int, default=300)
    rm.add_argument("--retries", type=int, default=2)
    rm.add_argument("--retry-sleep", type=float, default=2.0)
    rm.add_argument("--enable-thinking", action="store_true")
    rm.add_argument("--no-json-mode", dest="json_mode", action="store_false")
    rm.add_argument("--allow-text-only", action="store_true")
    rm.add_argument("--only-unlabeled", action="store_true")
    rm.add_argument("--fail-on-error", action="store_true")
    rm.set_defaults(json_mode=True)
    return p


def main() -> int:
    args = parser().parse_args()
    if hasattr(args, "raw_root"):
        args.raw_root = args.raw_root.expanduser().resolve()
    if hasattr(args, "output_root"):
        args.output_root = args.output_root.expanduser().resolve()
    if args.cmd == "inventory":
        return cmd_inventory(args)
    if args.cmd == "build":
        return cmd_build(args)
    if args.cmd == "gaps":
        return cmd_gaps(args)
    if args.cmd == "refine-skills":
        return cmd_refine_skills(args)
    if args.cmd == "refine-metadata":
        return cmd_refine_metadata(args)
    raise SystemExit(args.cmd)


if __name__ == "__main__":
    raise SystemExit(main())
