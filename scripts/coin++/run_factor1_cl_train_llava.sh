#!/usr/bin/env bash
set -euo pipefail

# Generic continual LLaVA trainer for CoIN++ Factor-1 tracks.
#
# Examples:
#   bash scripts/coin++/run_factor1_cl_train_llava.sh
#   FACTOR=visual_substrate bash scripts/coin++/run_factor1_cl_train_llava.sh
#   AUTO_RESUME=0 FACTOR=visual_substrate bash scripts/coin++/run_factor1_cl_train_llava.sh
#   RESUME_FROM_STAGE=4 FACTOR=visual_substrate bash scripts/coin++/run_factor1_cl_train_llava.sh
#   MAX_STEPS=20 INCLUDE_GPUS=localhost:0 bash scripts/coin++/run_factor1_cl_train_llava.sh
#   MODEL_VERSION=vicuna-13b-v1.5 PER_DEVICE_BATCH=2 bash scripts/coin++/run_factor1_cl_train_llava.sh

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$PROJECT_ROOT"

FACTOR="${FACTOR:-evidence_complexity}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final_textvqa_clean}"
SPLIT_ROOT="${SPLIT_ROOT:-$DATA_ROOT/splits/$FACTOR}"
TRAIN_DIR="${TRAIN_DIR:-$SPLIT_ROOT/trainable/train}"
EVAL_DIR="${EVAL_DIR:-$SPLIT_ROOT/trainable/eval}"
ORDER_JSON="${ORDER_JSON:-$SPLIT_ROOT/transition_order.json}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"

PROMPT_VERSION="${PROMPT_VERSION:-v1}"
MODEL_VERSION="${MODEL_VERSION:-vicuna-7b-v1.5}"
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/$MODEL_VERSION}"
PROJECTOR_PATH="${PROJECTOR_PATH:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/$MODEL_VERSION-projector/mm_projector.bin}"
VISION_TOWER="${VISION_TOWER:-$PROJECT_ROOT/checkpoints/LLaVA/clip-vit-large-patch14-336}"
DS_CONFIG_PATH="${DS_CONFIG_PATH:-$PROJECT_ROOT/scripts/zero3_offload.json}"

OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++_textvqa_clean/$FACTOR}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/results/coin++_textvqa_clean/$FACTOR/logs}"
INCLUDE_GPUS="${INCLUDE_GPUS:-localhost:0,1,2,3}"
MASTER_PORT="${MASTER_PORT:-29651}"

RUN_TRAIN="${RUN_TRAIN:-1}"
DRY_RUN="${DRY_RUN:-0}"
RESET_EACH_STAGE="${RESET_EACH_STAGE:-0}"
AUTO_RESUME="${AUTO_RESUME:-1}"
RESUME_FROM_STAGE="${RESUME_FROM_STAGE:-}"
STOP_AFTER_STAGE="${STOP_AFTER_STAGE:-0}"

NUM_TRAIN_EPOCHS="${NUM_TRAIN_EPOCHS:-1}"
MAX_STEPS="${MAX_STEPS:-}"
PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-4}"
PER_DEVICE_EVAL_BATCH="${PER_DEVICE_EVAL_BATCH:-1}"
GRAD_ACCUM="${GRAD_ACCUM:-8}"
MODEL_MAX_LENGTH="${MODEL_MAX_LENGTH:-2048}"
LR="${LR:-2e-4}"
MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-2e-5}"
VISION_TOWER_LR="${VISION_TOWER_LR:-}"
TRAINABLE_MODULES="${TRAINABLE_MODULES:-}"
LORA_R="${LORA_R:-128}"
LORA_ALPHA="${LORA_ALPHA:-256}"
BF16="${BF16:-True}"
TF32="${TF32:-True}"
DATALOADER_NUM_WORKERS="${DATALOADER_NUM_WORKERS:-4}"
SAVE_STRATEGY="${SAVE_STRATEGY:-epoch}"
SAVE_TOTAL_LIMIT="${SAVE_TOTAL_LIMIT:-1}"

if [[ ! -d "$SPLIT_ROOT" ]]; then
  echo "Missing split root: $SPLIT_ROOT" >&2
  exit 1
fi
if [[ ! -f "$ORDER_JSON" ]]; then
  echo "Missing transition order: $ORDER_JSON" >&2
  exit 1
fi
if [[ ! -d "$IMAGE_FOLDER" ]]; then
  echo "Missing image folder: $IMAGE_FOLDER" >&2
  exit 1
fi

if [[ -n "${STAGES_OVERRIDE:-}" ]]; then
  read -r -a STAGES <<< "$STAGES_OVERRIDE"
else
  mapfile -t STAGES < <("$PYTHON_BIN" - "$ORDER_JSON" <<'PYCODE'
import json
import sys
from pathlib import Path
order = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
for item in order.get('trainable_order', []):
    print(item)
PYCODE
)
fi

if [[ "${#STAGES[@]}" -eq 0 ]]; then
  echo "No stages found for factor=$FACTOR" >&2
  exit 1
fi

mkdir -p "$OUTPUT_ROOT" "$LOG_DIR"

stage_checkpoint_complete() {
  local stage_output="$1"
  local required_file
  local required_files=(
    adapter_config.json
    adapter_model.bin
    config.json
    non_lora_trainables.bin
    trainer_state.json
  )

  for required_file in "${required_files[@]}"; do
    if [[ ! -s "$stage_output/$required_file" ]]; then
      return 1
    fi
  done
  return 0
}
stage_checkpoint_reusable() {
  local stage_output="$1"
  local marker="$stage_output/.coinpp_stage_complete"

  stage_checkpoint_complete "$stage_output" || return 1
  [[ -s "$marker" ]] || return 1
  grep -Fqx "data_root=$DATA_ROOT" "$marker"
}


write_stage_complete_marker() {
  local stage_output="$1"
  local stage_no="$2"
  local stage="$3"

  {
    printf 'factor=%s\n' "$FACTOR"
    printf 'stage_number=%s\n' "$stage_no"
    printf 'stage=%s\n' "$stage"
    printf 'data_root=%s\n' "$DATA_ROOT"
    printf 'trainable_modules=%s\n' "${TRAINABLE_MODULES:-legacy_llm_projector}"
    printf 'completed_at=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$stage_output/.coinpp_stage_complete"
}

AUTO_RESUME_REASON="manual"
ALL_STAGES_COMPLETE=0
if [[ -z "$RESUME_FROM_STAGE" ]]; then
  RESUME_FROM_STAGE=1
  AUTO_RESUME_REASON="disabled"

  if [[ "$AUTO_RESUME" == "1" && "$RESET_EACH_STAGE" == "0" ]]; then
    RESUME_FROM_STAGE=$(( ${#STAGES[@]} + 1 ))
    AUTO_RESUME_REASON="all stages complete"

    for idx in "${!STAGES[@]}"; do
      stage_no=$((idx + 1))
      stage="${STAGES[$idx]}"
      stage_output="$OUTPUT_ROOT/${stage_no}_${stage}"
      if ! stage_checkpoint_reusable "$stage_output"; then
        RESUME_FROM_STAGE="$stage_no"
        AUTO_RESUME_REASON="first incomplete checkpoint: ${stage_no}_${stage}"
        break
      fi
    done

    if [[ "$RESUME_FROM_STAGE" -gt "${#STAGES[@]}" ]]; then
      ALL_STAGES_COMPLETE=1
    fi
  elif [[ "$RESET_EACH_STAGE" == "1" ]]; then
    AUTO_RESUME_REASON="disabled because RESET_EACH_STAGE=1"
  fi
fi

if [[ ! "$RESUME_FROM_STAGE" =~ ^[1-9][0-9]*$ ]]; then
  echo "RESUME_FROM_STAGE must be a positive integer; got: $RESUME_FROM_STAGE" >&2
  exit 1
fi
if [[ "$RESUME_FROM_STAGE" -gt $(( ${#STAGES[@]} + 1 )) ]]; then
  echo "RESUME_FROM_STAGE=$RESUME_FROM_STAGE exceeds the valid range 1-$(( ${#STAGES[@]} + 1 ))" >&2
  exit 1
fi

missing=0
for required_path in "$MODEL_PATH" "$VISION_TOWER" "$DS_CONFIG_PATH"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Missing required path: $required_path" >&2
    missing=1
  fi
done
if [[ "$RESET_EACH_STAGE" == "1" || "$RESUME_FROM_STAGE" == "1" ]]; then
  if [[ ! -f "$PROJECTOR_PATH" ]]; then
    echo "Missing projector path for base-stage training: $PROJECTOR_PATH" >&2
    missing=1
  fi
fi
if [[ "$missing" == "1" ]]; then
  echo "Set MODEL_PATH, PROJECTOR_PATH, VISION_TOWER, or DS_CONFIG_PATH before training." >&2
  exit 1
fi

cat <<EOF
CoIN++ Factor-1 continual LLaVA training
  project root:       $PROJECT_ROOT
  factor:             $FACTOR
  split root:         $SPLIT_ROOT
  image folder:       $IMAGE_FOLDER
  model:              $MODEL_PATH
  projector:          $PROJECTOR_PATH
  output root:        $OUTPUT_ROOT
  logs:               $LOG_DIR
  stages:             ${STAGES[*]}
  reset each stage:   $RESET_EACH_STAGE
  auto resume:        $AUTO_RESUME
  resume from stage:  $RESUME_FROM_STAGE
  resume decision:    $AUTO_RESUME_REASON
  max steps:          ${MAX_STEPS:-<epoch mode>}
  epochs:             $NUM_TRAIN_EPOCHS
  batch/accum:        $PER_DEVICE_BATCH / $GRAD_ACCUM
  trainable modules:  ${TRAINABLE_MODULES:-<legacy llm+projector>}
  learning rates:     base=$LR projector=$MM_PROJECTOR_LR vision=${VISION_TOWER_LR:-<base>}
  run train:          $RUN_TRAIN
  dry run:            $DRY_RUN
EOF

if [[ "$ALL_STAGES_COMPLETE" == "1" ]]; then
  echo
  echo "All ${#STAGES[@]} stages already have complete checkpoints; nothing to train."
  echo "  checkpoints: $OUTPUT_ROOT"
  exit 0
fi

previous_ckpt=""
for idx in "${!STAGES[@]}"; do
  stage_no=$((idx + 1))
  stage="${STAGES[$idx]}"
  stage_data="$TRAIN_DIR/$stage/train.json"
  stage_eval="$EVAL_DIR/$stage/eval.json"
  stage_output="$OUTPUT_ROOT/${stage_no}_${stage}"
  stage_log="$LOG_DIR/${stage_no}_${stage}.log"

  if [[ ! -f "$stage_data" ]]; then
    echo "Missing stage train data: $stage_data" >&2
    exit 1
  fi
  if [[ ! -f "$stage_eval" ]]; then
    echo "Warning: missing stage eval data: $stage_eval" >&2
  fi

  if [[ "$RESET_EACH_STAGE" == "0" && "$stage_no" -lt "$RESUME_FROM_STAGE" ]]; then
    echo "Skipping completed stage $stage_no: $stage"
    previous_ckpt="$stage_output"
    continue
  fi

  train_args=(
    ETrain/Train/LLaVA/train_mem.py
    --deepspeed "$DS_CONFIG_PATH"
    --lora_enable True --lora_r "$LORA_R" --lora_alpha "$LORA_ALPHA" --mm_projector_lr "$MM_PROJECTOR_LR"
    --model_name_or_path "$MODEL_PATH"
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
    --per_device_train_batch_size "$PER_DEVICE_BATCH"
    --per_device_eval_batch_size "$PER_DEVICE_EVAL_BATCH"
    --gradient_accumulation_steps "$GRAD_ACCUM"
    --evaluation_strategy no
    --save_strategy "$SAVE_STRATEGY"
    --save_total_limit "$SAVE_TOTAL_LIMIT"
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

  if [[ -n "$TRAINABLE_MODULES" ]]; then
    train_args+=(--trainable_modules "$TRAINABLE_MODULES")
  fi
  if [[ -n "$VISION_TOWER_LR" ]]; then
    train_args+=(--vision_tower_lr "$VISION_TOWER_LR")
  fi

  if [[ -n "$MAX_STEPS" ]]; then
    train_args+=(--max_steps "$MAX_STEPS" --num_train_epochs "$NUM_TRAIN_EPOCHS")
  else
    train_args+=(--num_train_epochs "$NUM_TRAIN_EPOCHS")
  fi

  # Always initialize the frozen projector consistently. When projector weights
  # were trained previously, the continual checkpoint loaded below overrides it.
  train_args+=(--pretrain_mm_mlp_adapter "$PROJECTOR_PATH")
  if [[ "$RESET_EACH_STAGE" == "1" || -z "$previous_ckpt" ]]; then
    stage_previous="<base model>"
  else
    train_args+=(--previous_task_model_path "$previous_ckpt")
    stage_previous="$previous_ckpt"
  fi

  echo
  echo "================ CoIN++ $FACTOR stage ${stage_no}/${#STAGES[@]}: $stage ================"
  echo "  train data: $stage_data"
  echo "  eval data:  $stage_eval"
  echo "  output:     $stage_output"
  echo "  previous:   $stage_previous"
  echo "  include:    $INCLUDE_GPUS"
  echo "  log:        $stage_log"

  if [[ "$RUN_TRAIN" != "1" || "$DRY_RUN" == "1" ]]; then
    printf 'deepspeed --include %q --master_port %q' "$INCLUDE_GPUS" "$MASTER_PORT"
    printf ' %q' "${train_args[@]}"
    printf '\n'
  else
    mkdir -p "$stage_output"
    deepspeed --include "$INCLUDE_GPUS" --master_port "$MASTER_PORT" "${train_args[@]}" 2>&1 | tee "$stage_log"

    if ! stage_checkpoint_complete "$stage_output"; then
      echo "Training exited successfully but checkpoint is incomplete: $stage_output" >&2
      exit 1
    fi
    write_stage_complete_marker "$stage_output" "$stage_no" "$stage"
  fi

  previous_ckpt="$stage_output"

  if [[ "$STOP_AFTER_STAGE" != "0" && "$stage_no" -ge "$STOP_AFTER_STAGE" ]]; then
    echo "Stopping after stage $stage_no because STOP_AFTER_STAGE=$STOP_AFTER_STAGE"
    break
  fi
done

echo
echo "CoIN++ training script finished for factor=$FACTOR"
echo "  checkpoints: $OUTPUT_ROOT"
echo "  logs:        $LOG_DIR"
