#!/usr/bin/env bash
set -euo pipefail

# LLaVA smoke run for cl_dataset/coin_factor1_train_v2.
#
# This follows scripts/LLaVA/COIN/Train/*.sh:
#   - deepspeed ETrain/Train/LLaVA/train_mem.py
#   - LLaVA/Vicuna checkpoint arguments
#   - --image_folder ./cl_dataset
#   - conversation JSON with separate "image" field
#
# Data-only smoke check:
#   bash scripts/smoke_run_factor1_train_v2.sh
#
# Minimal LLaVA LoRA training smoke run:
#   RUN_TRAIN=1 CUDA_VISIBLE_DEVICES=0 bash scripts/smoke_run_factor1_train_v2.sh
#
# Common overrides:
#   MAX_SAMPLES=128 MAX_STEPS=5 PER_DEVICE_BATCH=1 GRAD_ACCUM=1 bash scripts/smoke_run_factor1_train_v2.sh
#   RUN_TRAIN=1 INCLUDE_GPUS=localhost:0 MODEL_PATH=... PROJECTOR_PATH=... VISION_TOWER=... bash scripts/smoke_run_factor1_train_v2.sh

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

TRAIN_ROOT="${TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2}"
TRAIN_JSON="${TRAIN_JSON:-$TRAIN_ROOT/train.json}"
MANIFEST_JSON="${MANIFEST_JSON:-$TRAIN_ROOT/manifest.json}"

OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/outputs/factor1_v2_llava_smoke}"
SMOKE_DATA_DIR="${SMOKE_DATA_DIR:-$OUTPUT_ROOT/data}"
SMOKE_TRAIN_JSON="${SMOKE_TRAIN_JSON:-$SMOKE_DATA_DIR/train.llava.smoke.json}"
OUTPUT_DIR="${OUTPUT_DIR:-$OUTPUT_ROOT/llava_lora_run}"

MAX_SAMPLES="${MAX_SAMPLES:-256}"
MAX_IMAGES_TO_CHECK="${MAX_IMAGES_TO_CHECK:-64}"
SEED="${SEED:-42}"

RUN_TRAIN="${RUN_TRAIN:-0}"
PROMPT_VERSION="${PROMPT_VERSION:-v1}"
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/checkpoints/Vicuna/vicuna-7b-v1.5}"
PROJECTOR_PATH="${PROJECTOR_PATH:-$PROJECT_ROOT/checkpoints/Vicuna/vicuna-7b-v1.5-projector/mm_projector.bin}"
VISION_TOWER="${VISION_TOWER:-$PROJECT_ROOT/checkpoints/clip-vit-large-patch14-336}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"
DS_CONFIG_PATH="${DS_CONFIG_PATH:-$PROJECT_ROOT/scripts/zero3_offload.json}"
INCLUDE_GPUS="${INCLUDE_GPUS:-localhost:0}"
MASTER_PORT="${MASTER_PORT:-29631}"

MAX_STEPS="${MAX_STEPS:-5}"
PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-1}"
GRAD_ACCUM="${GRAD_ACCUM:-1}"
MODEL_MAX_LENGTH="${MODEL_MAX_LENGTH:-2048}"
LR="${LR:-2e-4}"
MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-2e-5}"
LORA_R="${LORA_R:-128}"
LORA_ALPHA="${LORA_ALPHA:-256}"
BF16="${BF16:-True}"
TF32="${TF32:-True}"
DATALOADER_NUM_WORKERS="${DATALOADER_NUM_WORKERS:-2}"

mkdir -p "$SMOKE_DATA_DIR" "$OUTPUT_DIR"

cd "$PROJECT_ROOT"

echo "Factor-1 v2 LLaVA smoke run"
echo "  project root:        $PROJECT_ROOT"
echo "  train json:          $TRAIN_JSON"
echo "  manifest:            $MANIFEST_JSON"
echo "  smoke train json:    $SMOKE_TRAIN_JSON"
echo "  image folder:        $IMAGE_FOLDER"
echo "  output dir:          $OUTPUT_DIR"
echo "  max samples:         $MAX_SAMPLES"
echo "  run train:           $RUN_TRAIN"

"$PYTHON_BIN" - "$TRAIN_JSON" "$MANIFEST_JSON" "$SMOKE_TRAIN_JSON" "$IMAGE_FOLDER" "$MAX_SAMPLES" "$MAX_IMAGES_TO_CHECK" "$SEED" <<'PYCODE'
import json
import os
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

train_json = Path(sys.argv[1])
manifest_json = Path(sys.argv[2])
llava_output = Path(sys.argv[3])
image_folder = Path(sys.argv[4])
max_samples = int(sys.argv[5])
max_images_to_check = int(sys.argv[6])
seed = int(sys.argv[7])

if not train_json.exists():
    raise SystemExit(f"train.json not found: {train_json}")

with train_json.open("r", encoding="utf-8") as f:
    data = json.load(f)

if not isinstance(data, list) or not data:
    raise SystemExit(f"train.json must be a non-empty JSON list: {train_json}")

train_root = train_json.parent
source_image_base = train_root
if manifest_json.exists():
    try:
        manifest = json.loads(manifest_json.read_text(encoding="utf-8"))
        source_image_base = Path(manifest.get("image_folder_for_training") or train_root)
    except Exception:
        source_image_base = train_root

required_roles = {"human", "gpt"}
malformed = []
for row in data[: min(len(data), 2000)]:
    conv = row.get("conversations")
    if not isinstance(conv, list) or len(conv) < 2:
        malformed.append({"id": row.get("id"), "error": "bad conversations"})
        continue
    for msg in conv:
        if msg.get("from") not in required_roles or not isinstance(msg.get("value"), str):
            malformed.append({"id": row.get("id"), "error": "bad message", "message": msg})
            break
if malformed:
    raise SystemExit("Malformed conversation rows: " + json.dumps(malformed[:5], ensure_ascii=False))

rng = random.Random(seed)
by_dataset = defaultdict(list)
for row in data:
    dataset = row.get("metadata", {}).get("dataset") or row.get("dataset") or "unknown"
    by_dataset[dataset].append(row)

selected = []
datasets = sorted(by_dataset)
base_quota = max(1, max_samples // max(1, len(datasets)))
for dataset in datasets:
    rows = by_dataset[dataset]
    rng.shuffle(rows)
    selected.extend(rows[:base_quota])

if len(selected) < max_samples:
    selected_ids = {id(x) for x in selected}
    rest = [x for x in data if id(x) not in selected_ids]
    rng.shuffle(rest)
    selected.extend(rest[: max_samples - len(selected)])
selected = selected[:max_samples]
rng.shuffle(selected)

def resolve_image(image_value):
    if not image_value:
        return None
    p = Path(image_value)
    candidates = []
    if p.is_absolute():
        candidates.append(p)
    candidates.append(source_image_base / p)
    candidates.append(train_root / p)
    candidates.append(train_root / p.name)
    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()
    return None

def image_value_for_llava(abs_image_path):
    # Existing LLaVA training scripts use --image_folder ./cl_dataset, so the JSON
    # image value must be relative to that folder.
    try:
        return os.path.relpath(abs_image_path, image_folder.resolve())
    except Exception:
        return str(abs_image_path)

try:
    from PIL import Image
except Exception as exc:
    raise SystemExit(f"Pillow is required for image verification: {exc}")

bad_images = []
checked = 0
image_rows = 0
text_only_rows = 0
llava_rows = []

for original in selected:
    row = dict(original)
    row["conversations"] = [dict(m) for m in original["conversations"]]
    image_path = resolve_image(row.get("image"))

    if row.get("image"):
        image_rows += 1
        if image_path is None:
            bad_images.append({"id": row.get("id"), "image": row.get("image"), "error": "missing"})
        else:
            llava_image = image_value_for_llava(image_path)
            row["image"] = llava_image
            llava_joined = image_folder / llava_image
            if not llava_joined.exists():
                bad_images.append({"id": row.get("id"), "image": llava_image, "error": f"not found under image_folder={image_folder}"})
            elif checked < max_images_to_check:
                try:
                    with Image.open(llava_joined) as im:
                        im.verify()
                    checked += 1
                except Exception as exc:
                    bad_images.append({"id": row.get("id"), "image": str(llava_joined), "error": repr(exc)})
    else:
        text_only_rows += 1
        for msg in row["conversations"]:
            if msg.get("from") == "human":
                msg["value"] = msg["value"].replace("<image>", "").strip()

    llava_rows.append(row)

if bad_images:
    raise SystemExit("Image verification failed: " + json.dumps(bad_images[:10], ensure_ascii=False))

llava_output.parent.mkdir(parents=True, exist_ok=True)
llava_output.write_text(json.dumps(llava_rows, ensure_ascii=False, indent=2), encoding="utf-8")

stats = {
    "source_samples": len(data),
    "selected_samples": len(selected),
    "image_samples": image_rows,
    "text_only_samples": text_only_rows,
    "images_checked": checked,
    "datasets": Counter((r.get("metadata", {}).get("dataset") or "unknown") for r in selected),
    "visual_substrate": Counter((r.get("metadata", {}).get("visual_substrate") or "unknown") for r in selected),
    "skill_type_primary": Counter((r.get("metadata", {}).get("skill_type_primary") or "unknown") for r in selected),
    "evidence_complexity": Counter((r.get("metadata", {}).get("evidence_complexity") or "unknown") for r in selected),
    "answer_type": Counter((r.get("metadata", {}).get("answer_type") or "unknown") for r in selected),
}
print("LLaVA smoke data built successfully")
for key in ["source_samples", "selected_samples", "image_samples", "text_only_samples", "images_checked"]:
    print(f"  {key}: {stats[key]}")
print("  datasets:", dict(stats["datasets"].most_common()))
print("  evidence_complexity:", dict(stats["evidence_complexity"].most_common()))
print(f"  llava output: {llava_output}")
PYCODE

if [[ "$RUN_TRAIN" != "1" ]]; then
  echo
  echo "Data smoke check finished. Training was not launched because RUN_TRAIN=$RUN_TRAIN."
  echo "Run minimal LLaVA training with:"
  echo "  RUN_TRAIN=1 CUDA_VISIBLE_DEVICES=0 bash scripts/smoke_run_factor1_train_v2.sh"
  echo "If checkpoint paths differ, set MODEL_PATH, PROJECTOR_PATH, and VISION_TOWER."
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

echo
echo "Launching LLaVA smoke training"
echo "  model:       $MODEL_PATH"
echo "  projector:   $PROJECTOR_PATH"
echo "  vision:      $VISION_TOWER"
echo "  data:        $SMOKE_TRAIN_JSON"
echo "  image folder:$IMAGE_FOLDER"
echo "  max steps:   $MAX_STEPS"
echo "  include:     $INCLUDE_GPUS"
echo "  output:      $OUTPUT_DIR"

deepspeed --include "$INCLUDE_GPUS" --master_port "$MASTER_PORT" ETrain/Train/LLaVA/train_mem.py \
  --deepspeed "$DS_CONFIG_PATH" \
  --lora_enable True --lora_r "$LORA_R" --lora_alpha "$LORA_ALPHA" --mm_projector_lr "$MM_PROJECTOR_LR" \
  --model_name_or_path "$MODEL_PATH" \
  --pretrain_mm_mlp_adapter "$PROJECTOR_PATH" \
  --version "$PROMPT_VERSION" \
  --data_path "$SMOKE_TRAIN_JSON" \
  --image_folder "$IMAGE_FOLDER" \
  --vision_tower "$VISION_TOWER" \
  --mm_projector_type mlp2x_gelu \
  --mm_vision_select_layer -2 \
  --mm_use_im_start_end False \
  --mm_use_im_patch_token False \
  --image_aspect_ratio pad \
  --group_by_modality_length True \
  --bf16 "$BF16" \
  --output_dir "$OUTPUT_DIR" \
  --max_steps "$MAX_STEPS" \
  --num_train_epochs 1 \
  --per_device_train_batch_size "$PER_DEVICE_BATCH" \
  --per_device_eval_batch_size 1 \
  --gradient_accumulation_steps "$GRAD_ACCUM" \
  --evaluation_strategy no \
  --save_strategy no \
  --learning_rate "$LR" \
  --weight_decay 0. \
  --warmup_ratio 0.03 \
  --lr_scheduler_type cosine \
  --logging_steps 1 \
  --tf32 "$TF32" \
  --model_max_length "$MODEL_MAX_LENGTH" \
  --gradient_checkpointing True \
  --dataloader_num_workers "$DATALOADER_NUM_WORKERS" \
  --lazy_preprocess True \
  --report_to none

echo
echo "LLaVA smoke training completed: $OUTPUT_DIR"
