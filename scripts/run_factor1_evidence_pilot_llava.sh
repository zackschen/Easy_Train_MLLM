#!/usr/bin/env bash
set -euo pipefail

# Small-scale continual-learning pilot for Factor-1 Evidence Complexity.
#
# This script follows the LLaVA/CoIN training style in:
#   scripts/LLaVA/COIN/Train/*.sh
#
# It builds disjoint train/eval splits for:
#   single_evidence -> multi_evidence -> cross_region_or_multihop -> cross_context
#
# Data-only build:
#   bash scripts/run_factor1_evidence_pilot_llava.sh
#
# Sequential pilot training:
#   RUN_TRAIN=1 INCLUDE_GPUS=localhost:0 bash scripts/run_factor1_evidence_pilot_llava.sh
#
# Smaller debugging run:
#   TRAIN_SAMPLES_PER_STAGE=128 EVAL_SAMPLES_PER_STAGE=64 MAX_STEPS=20 \
#   RUN_TRAIN=1 INCLUDE_GPUS=localhost:0 bash scripts/run_factor1_evidence_pilot_llava.sh

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

TRAIN_ROOT="${TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2}"
FACTOR_ROOT="${FACTOR_ROOT:-$TRAIN_ROOT/by_factor/evidence_complexity}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"

PILOT_ROOT="${PILOT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_pilot/evidence_complexity}"
PILOT_TRAIN_DIR="${PILOT_TRAIN_DIR:-$PILOT_ROOT/data/train}"
PILOT_EVAL_DIR="${PILOT_EVAL_DIR:-$PILOT_ROOT/data/eval}"
PILOT_SUMMARY="${PILOT_SUMMARY:-$PILOT_ROOT/pilot_summary.json}"
PILOT_CKPT_DIR="${PILOT_CKPT_DIR:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/Factor1-Pilot/evidence_complexity}"
PILOT_LOG_DIR="${PILOT_LOG_DIR:-$PROJECT_ROOT/results/factor1_pilot/evidence_complexity/logs}"

STAGES=(single_evidence multi_evidence cross_region_or_multihop cross_context)
if [[ -n "${STAGES_OVERRIDE:-}" ]]; then
  read -r -a STAGES <<< "$STAGES_OVERRIDE"
fi

TRAIN_SAMPLES_PER_STAGE="${TRAIN_SAMPLES_PER_STAGE:-1000}"
EVAL_SAMPLES_PER_STAGE="${EVAL_SAMPLES_PER_STAGE:-300}"
MAX_IMAGES_TO_CHECK="${MAX_IMAGES_TO_CHECK:-80}"
SEED="${SEED:-42}"
ALLOW_TEXT_ONLY="${ALLOW_TEXT_ONLY:-1}"

RUN_TRAIN="${RUN_TRAIN:-1}"
RUN_EVAL="${RUN_EVAL:-0}"
EVAL_CMD_TEMPLATE="${EVAL_CMD_TEMPLATE:-}"

PROMPT_VERSION="${PROMPT_VERSION:-v1}"
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/vicuna-7b-v1.5}"
PROJECTOR_PATH="${PROJECTOR_PATH:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/vicuna-7b-v1.5-projector/mm_projector.bin}"
VISION_TOWER="${VISION_TOWER:-$PROJECT_ROOT/checkpoints/LLaVA/clip-vit-large-patch14-336}"
DS_CONFIG_PATH="${DS_CONFIG_PATH:-$PROJECT_ROOT/scripts/zero3_offload.json}"
INCLUDE_GPUS="${INCLUDE_GPUS:-localhost:0,1,2,3,4,5,6,7}"
MASTER_PORT="${MASTER_PORT:-29641}"

MAX_STEPS="${MAX_STEPS:-200}"
PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-1}"
GRAD_ACCUM="${GRAD_ACCUM:-8}"
MODEL_MAX_LENGTH="${MODEL_MAX_LENGTH:-2048}"
LR="${LR:-2e-4}"
MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-2e-5}"
LORA_R="${LORA_R:-128}"
LORA_ALPHA="${LORA_ALPHA:-256}"
BF16="${BF16:-True}"
TF32="${TF32:-True}"
DATALOADER_NUM_WORKERS="${DATALOADER_NUM_WORKERS:-4}"
SAVE_STRATEGY="${SAVE_STRATEGY:-epoch}"

mkdir -p "$PILOT_TRAIN_DIR" "$PILOT_EVAL_DIR" "$PILOT_CKPT_DIR" "$PILOT_LOG_DIR"
cd "$PROJECT_ROOT"

echo "Factor-1 Evidence Complexity LLaVA pilot"
echo "  project root:             $PROJECT_ROOT"
echo "  factor root:              $FACTOR_ROOT"
echo "  image folder:             $IMAGE_FOLDER"
echo "  train samples per stage:  $TRAIN_SAMPLES_PER_STAGE"
echo "  eval samples per stage:   $EVAL_SAMPLES_PER_STAGE"
echo "  stages:                   ${STAGES[*]}"
echo "  run train:                $RUN_TRAIN"
echo "  run eval:                 $RUN_EVAL"

"$PYTHON_BIN" - \
  "$FACTOR_ROOT" \
  "$TRAIN_ROOT" \
  "$IMAGE_FOLDER" \
  "$PILOT_TRAIN_DIR" \
  "$PILOT_EVAL_DIR" \
  "$PILOT_SUMMARY" \
  "$TRAIN_SAMPLES_PER_STAGE" \
  "$EVAL_SAMPLES_PER_STAGE" \
  "$MAX_IMAGES_TO_CHECK" \
  "$SEED" \
  "$ALLOW_TEXT_ONLY" \
  "${STAGES[@]}" <<'PYCODE'
import json
import os
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

factor_root = Path(sys.argv[1])
train_root = Path(sys.argv[2])
image_folder = Path(sys.argv[3])
pilot_train_dir = Path(sys.argv[4])
pilot_eval_dir = Path(sys.argv[5])
pilot_summary = Path(sys.argv[6])
train_samples_per_stage = int(sys.argv[7])
eval_samples_per_stage = int(sys.argv[8])
max_images_to_check = int(sys.argv[9])
seed = int(sys.argv[10])
allow_text_only = sys.argv[11] == "1"
stages = sys.argv[12:]

if not factor_root.exists():
    raise SystemExit(f"Factor root not found: {factor_root}")
if not train_root.exists():
    raise SystemExit(f"Train root not found: {train_root}")
if not stages:
    raise SystemExit("No stages were provided")

try:
    from PIL import Image
except Exception as exc:
    raise SystemExit(f"Pillow is required for image verification: {exc}")

required_roles = {"human", "gpt"}

def dataset_label(row):
    meta = row.get("metadata") or {}
    return meta.get("dataset") or row.get("dataset") or "unknown"

def resolve_image(image_value):
    if not image_value:
        return None
    p = Path(image_value)
    candidates = []
    if p.is_absolute():
        candidates.append(p)
    candidates.append(train_root / p)
    candidates.append(train_root / p.name)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None

def image_value_for_llava(abs_image_path):
    return os.path.relpath(abs_image_path, image_folder.resolve())

def validate_conversation(row):
    conv = row.get("conversations")
    if not isinstance(conv, list) or len(conv) < 2:
        return "bad conversations"
    for msg in conv:
        if msg.get("from") not in required_roles or not isinstance(msg.get("value"), str):
            return f"bad message: {msg}"
    return None

def normalize_for_llava(row):
    err = validate_conversation(row)
    if err:
        raise ValueError(f"id={row.get('id')}: {err}")

    out = dict(row)
    out["conversations"] = [dict(m) for m in row["conversations"]]
    image_value = out.get("image")
    image_path = resolve_image(image_value)

    if image_value and image_path is None:
        raise FileNotFoundError(f"Cannot resolve image for id={out.get('id')}, image={image_value}")

    if image_path is not None:
        llava_image = image_value_for_llava(image_path)
        joined = image_folder / llava_image
        if not joined.exists():
            raise FileNotFoundError(
                f"LLaVA image path does not exist for id={out.get('id')}: {joined} "
                f"(image_folder={image_folder}, image={llava_image})"
            )
        out["image"] = llava_image
        first_human = next((m for m in out["conversations"] if m.get("from") == "human"), None)
        if first_human is not None and "<image>" not in first_human.get("value", ""):
            first_human["value"] = first_human.get("value", "").strip() + "\n<image>"
    else:
        out.pop("image", None)
        if not allow_text_only:
            raise ValueError(f"Text-only sample is disabled: id={out.get('id')}")
        for msg in out["conversations"]:
            if msg.get("from") == "human":
                msg["value"] = msg.get("value", "").replace("<image>", "").strip()

    return out

def stratified_sample(rows, n, rng):
    by_dataset = defaultdict(list)
    for row in rows:
        by_dataset[dataset_label(row)].append(row)

    selected = []
    datasets = sorted(by_dataset)
    quota = max(1, n // max(1, len(datasets)))
    for dataset in datasets:
        ds_rows = list(by_dataset[dataset])
        rng.shuffle(ds_rows)
        selected.extend(ds_rows[:quota])

    if len(selected) < n:
        selected_ids = {id(x) for x in selected}
        rest = [x for x in rows if id(x) not in selected_ids]
        rng.shuffle(rest)
        selected.extend(rest[: n - len(selected)])

    selected = selected[:n]
    rng.shuffle(selected)
    return selected

def write_split(rows, out_path, image_check_budget):
    normalized = []
    image_count = 0
    text_only_count = 0
    checked = 0
    for row in rows:
        item = normalize_for_llava(row)
        if "image" in item:
            image_count += 1
            if checked < image_check_budget:
                with Image.open(image_folder / item["image"]) as im:
                    im.verify()
                checked += 1
        else:
            text_only_count += 1
        normalized.append(item)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "output": str(out_path),
        "samples": len(normalized),
        "image_samples": image_count,
        "text_only_samples": text_only_count,
        "images_checked": checked,
        "by_dataset": dict(Counter(dataset_label(r) for r in rows).most_common()),
        "by_visual_substrate": dict(Counter((r.get("metadata", {}) or {}).get("visual_substrate", "unknown") for r in rows).most_common()),
        "by_skill": dict(Counter((r.get("metadata", {}) or {}).get("skill_type_primary", "unknown") for r in rows).most_common()),
        "by_answer_type": dict(Counter((r.get("metadata", {}) or {}).get("answer_type", "unknown") for r in rows).most_common()),
    }

pilot_train_dir.mkdir(parents=True, exist_ok=True)
pilot_eval_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "factor_root": str(factor_root),
    "train_root": str(train_root),
    "image_folder": str(image_folder),
    "train_samples_per_stage": train_samples_per_stage,
    "eval_samples_per_stage": eval_samples_per_stage,
    "seed": seed,
    "stages": [],
}

for stage_index, stage in enumerate(stages, 1):
    stage_json = factor_root / stage / "train.json"
    if not stage_json.exists():
        raise SystemExit(f"Stage train.json not found: {stage_json}")

    rows = json.loads(stage_json.read_text(encoding="utf-8"))
    if not isinstance(rows, list) or not rows:
        raise SystemExit(f"Stage train.json is empty or invalid: {stage_json}")

    rng = random.Random(seed + stage_index)
    shuffled = list(rows)
    rng.shuffle(shuffled)

    need = train_samples_per_stage + eval_samples_per_stage
    if len(shuffled) < need:
        raise SystemExit(
            f"Not enough samples for stage={stage}: need {need}, available {len(shuffled)}"
        )

    # Keep eval disjoint from train. The pool is already randomized first, then
    # each split is dataset-stratified to avoid a single source dominating.
    eval_pool = shuffled[: max(eval_samples_per_stage * 3, eval_samples_per_stage)]
    train_pool = shuffled[max(eval_samples_per_stage * 3, eval_samples_per_stage):]
    eval_rows = stratified_sample(eval_pool, eval_samples_per_stage, random.Random(seed + 1000 + stage_index))
    eval_ids = {r.get("id") for r in eval_rows}
    train_pool = [r for r in train_pool if r.get("id") not in eval_ids]
    train_rows = stratified_sample(train_pool, train_samples_per_stage, random.Random(seed + 2000 + stage_index))

    train_out = pilot_train_dir / f"{stage_index}_{stage}.json"
    eval_out = pilot_eval_dir / f"{stage_index}_{stage}.json"
    train_summary = write_split(train_rows, train_out, max_images_to_check)
    eval_summary = write_split(eval_rows, eval_out, max_images_to_check)

    stage_summary = {
        "stage_index": stage_index,
        "stage": stage,
        "available_samples": len(rows),
        "train": train_summary,
        "eval": eval_summary,
    }
    summary["stages"].append(stage_summary)

    print(f"Built stage {stage_index}: {stage}")
    print(f"  train: {train_out} ({train_summary['samples']} samples)")
    print(f"  eval:  {eval_out} ({eval_summary['samples']} samples)")

pilot_summary.parent.mkdir(parents=True, exist_ok=True)
pilot_summary.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote summary: {pilot_summary}")
PYCODE

if [[ "$RUN_TRAIN" != "1" ]]; then
  echo
  echo "Pilot data has been built. Training was not launched because RUN_TRAIN=$RUN_TRAIN."
  echo "Start sequential pilot training with:"
  echo "  RUN_TRAIN=1 INCLUDE_GPUS=localhost:0 bash scripts/run_factor1_evidence_pilot_llava.sh"
  exit 0
fi

missing=0
for required_path in "$MODEL_PATH" "$PROJECTOR_PATH" "$VISION_TOWER" "$DS_CONFIG_PATH"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Missing required path: $required_path" >&2
    missing=1
  fi
done
if [[ "$missing" == "1" ]]; then
  echo "Set MODEL_PATH, PROJECTOR_PATH, VISION_TOWER, or DS_CONFIG_PATH before RUN_TRAIN=1." >&2
  exit 1
fi

previous_ckpt=""
for idx in "${!STAGES[@]}"; do
  stage_no=$((idx + 1))
  stage="${STAGES[$idx]}"
  stage_data="$PILOT_TRAIN_DIR/${stage_no}_${stage}.json"
  stage_output="$PILOT_CKPT_DIR/${stage_no}_${stage}"
  stage_log="$PILOT_LOG_DIR/${stage_no}_${stage}.log"

  if [[ ! -f "$stage_data" ]]; then
    echo "Stage data does not exist: $stage_data" >&2
    exit 1
  fi

  train_args=(
    ETrain/Train/LLaVA/train_mem.py
    --deepspeed "$DS_CONFIG_PATH"
    --lora_enable True --lora_r "$LORA_R" --lora_alpha "$LORA_ALPHA" --mm_projector_lr "$MM_PROJECTOR_LR"
    --model_name_or_path "$MODEL_PATH"
    --pretrain_mm_mlp_adapter "$PROJECTOR_PATH"
    --version "$PROMPT_VERSION"
    --data_path "$stage_data"
    --image_folder "$IMAGE_FOLDER"
    --vision_tower "$VISION_TOWER"
    --mm_projector_type mlp2x_gelu
    --mm_vision_select_layer -2
    --mm_use_im_start_end False
    --mm_use_im_patch_token False
    --image_aspect_ratio pad
    --group_by_modality_length True
    --bf16 "$BF16"
    --output_dir "$stage_output"
    --max_steps "$MAX_STEPS"
    --num_train_epochs 1
    --per_device_train_batch_size "$PER_DEVICE_BATCH"
    --per_device_eval_batch_size 1
    --gradient_accumulation_steps "$GRAD_ACCUM"
    --evaluation_strategy no
    --save_strategy "$SAVE_STRATEGY"
    --learning_rate "$LR"
    --weight_decay 0.
    --warmup_ratio 0.03
    --lr_scheduler_type cosine
    --logging_steps 1
    --tf32 "$TF32"
    --model_max_length "$MODEL_MAX_LENGTH"
    --gradient_checkpointing True
    --dataloader_num_workers "$DATALOADER_NUM_WORKERS"
    --lazy_preprocess True
    --report_to none
  )

  if [[ -n "$previous_ckpt" ]]; then
    train_args+=(--previous_task_model_path "$previous_ckpt")
  fi

  echo
  echo "================ Evidence pilot stage ${stage_no}/${#STAGES[@]}: $stage ================"
  echo "  data:       $stage_data"
  echo "  output:     $stage_output"
  echo "  previous:   ${previous_ckpt:-<base model>}"
  echo "  max steps:  $MAX_STEPS"
  echo "  include:    $INCLUDE_GPUS"
  echo "  log:        $stage_log"

  mkdir -p "$stage_output"
  deepspeed --include "$INCLUDE_GPUS" --master_port "$MASTER_PORT" "${train_args[@]}" 2>&1 | tee "$stage_log"

  previous_ckpt="$stage_output"

  if [[ "$RUN_EVAL" == "1" ]]; then
    if [[ -z "$EVAL_CMD_TEMPLATE" ]]; then
      echo "RUN_EVAL=1 but EVAL_CMD_TEMPLATE is empty; skipping eval." >&2
    else
      export STAGE_NO="$stage_no"
      export STAGE_NAME="$stage"
      export STAGE_DATA="$stage_data"
      export STAGE_OUTPUT="$stage_output"
      export PREVIOUS_CKPT="$previous_ckpt"
      export PILOT_EVAL_DIR
      echo "Running eval command template for stage $stage_no: $stage"
      bash -lc "$EVAL_CMD_TEMPLATE"
    fi
  fi
done

echo
echo "Evidence complexity continual pilot finished."
echo "  train data:   $PILOT_TRAIN_DIR"
echo "  eval data:    $PILOT_EVAL_DIR"
echo "  checkpoints:  $PILOT_CKPT_DIR"
echo "  logs:         $PILOT_LOG_DIR"
echo "  summary:      $PILOT_SUMMARY"
