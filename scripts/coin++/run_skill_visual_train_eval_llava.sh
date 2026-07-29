#!/usr/bin/env bash
set -euo pipefail

# End-to-end runner:
#   1. train Skill Requirement continually
#   2. evaluate every Skill checkpoint on every Skill task
#   3. train Visual Substrate continually
#   4. evaluate every Visual checkpoint on every Visual task

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$PROJECT_ROOT"

TRAIN_SCRIPT="${TRAIN_SCRIPT:-$SCRIPT_DIR/run_factor1_cl_train_llava.sh}"
EVAL_SCRIPT="${EVAL_SCRIPT:-$SCRIPT_DIR/run_factor1_cl_eval_llava.sh}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final}"
CHECKPOINT_BASE="${CHECKPOINT_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++}"
RESULT_BASE="${RESULT_BASE:-$PROJECT_ROOT/results/coin++}"
MODEL_VERSION="${MODEL_VERSION:-vicuna-7b-v1.5}"
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/$MODEL_VERSION}"
MODEL_BASE="${MODEL_BASE:-$MODEL_PATH}"

INCLUDE_GPUS="${INCLUDE_GPUS:-localhost:0,1,2,3,4,5,6,7}"
EVAL_GPUS="${EVAL_GPUS:-0,1,2,3,4,5,6,7}"
EVAL_PARALLEL_STAGES="${EVAL_PARALLEL_STAGES:-1}"
EVAL_LIMIT="${EVAL_LIMIT:-}"
SKIP_COMPLETED_TRAIN="${SKIP_COMPLETED_TRAIN:-1}"
SKIP_COMPLETED_EVAL="${SKIP_COMPLETED_EVAL:-1}"
DRY_RUN="${DRY_RUN:-0}"

RUN_SKILL_TRAIN="${RUN_SKILL_TRAIN:-1}"
RUN_SKILL_EVAL="${RUN_SKILL_EVAL:-1}"
RUN_VISUAL_TRAIN="${RUN_VISUAL_TRAIN:-1}"
RUN_VISUAL_EVAL="${RUN_VISUAL_EVAL:-1}"
SKILL_RESUME_FROM_STAGE="${SKILL_RESUME_FROM_STAGE:-}"
VISUAL_RESUME_FROM_STAGE="${VISUAL_RESUME_FROM_STAGE:-}"
SKILL_MASTER_PORT="${SKILL_MASTER_PORT:-29653}"
VISUAL_MASTER_PORT="${VISUAL_MASTER_PORT:-29652}"

for required_path in "$TRAIN_SCRIPT" "$EVAL_SCRIPT" "$DATA_ROOT" "$MODEL_PATH"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Missing required path: $required_path" >&2
    exit 1
  fi
done

detect_resume_stage() {
  local factor="$1"
  local order_json="$DATA_ROOT/splits/$factor/transition_order.json"
  local checkpoint_root="$CHECKPOINT_BASE/$factor"
  "$PYTHON_BIN" - "$order_json" "$checkpoint_root" <<'PYCODE'
import json
import sys
from pathlib import Path

order_path = Path(sys.argv[1])
root = Path(sys.argv[2])
stages = json.loads(order_path.read_text(encoding="utf-8")).get("trainable_order", [])
for idx, stage in enumerate(stages, 1):
    path = root / f"{idx}_{stage}"
    valid = (path / "adapter_config.json").is_file() and (
        (path / "adapter_model.bin").is_file()
        or (path / "adapter_model.safetensors").is_file()
    )
    if not valid:
        print(idx)
        break
else:
    print(0)
PYCODE
}

run_factor() {
  local factor="$1"
  local run_train="$2"
  local run_eval="$3"
  local resume_override="$4"
  local master_port="$5"
  local checkpoint_root="$CHECKPOINT_BASE/$factor"
  local factor_result_root="$RESULT_BASE/$factor"

  echo
  echo "================ CoIN++ end-to-end factor: $factor ================"

  if [[ "$run_train" == "1" ]]; then
    local detected_resume
    detected_resume="$(detect_resume_stage "$factor")"
    local resume_stage="${resume_override:-$detected_resume}"
    if [[ "$resume_stage" == "0" && "$SKIP_COMPLETED_TRAIN" == "1" ]]; then
      echo "[skip train] all $factor checkpoints already exist"
    else
      if [[ "$resume_stage" == "0" ]]; then
        resume_stage=1
      fi
      echo "[train] factor=$factor resume_from_stage=$resume_stage"
      FACTOR="$factor" \
      PROJECT_ROOT="$PROJECT_ROOT" \
      PYTHON_BIN="$PYTHON_BIN" \
      DATA_ROOT="$DATA_ROOT" \
      MODEL_PATH="$MODEL_PATH" \
      OUTPUT_ROOT="$checkpoint_root" \
      LOG_DIR="$factor_result_root/logs" \
      INCLUDE_GPUS="$INCLUDE_GPUS" \
      MASTER_PORT="$master_port" \
      RESUME_FROM_STAGE="$resume_stage" \
      DRY_RUN="$DRY_RUN" \
        bash "$TRAIN_SCRIPT"
    fi
  fi

  if [[ "$run_eval" == "1" ]]; then
    echo "[eval] factor=$factor"
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    MODEL_BASE="$MODEL_BASE" \
    CHECKPOINT_ROOT="$checkpoint_root" \
    RESULT_ROOT="$factor_result_root/eval" \
    EVAL_GPUS="$EVAL_GPUS" \
    PARALLEL_STAGES="$EVAL_PARALLEL_STAGES" \
    LIMIT="$EVAL_LIMIT" \
    SKIP_COMPLETED="$SKIP_COMPLETED_EVAL" \
    DRY_RUN="$DRY_RUN" \
      bash "$EVAL_SCRIPT"
  fi
}

cat <<EOF
CoIN++ Skill + Visual train/eval pipeline
  project root:          $PROJECT_ROOT
  data root:             $DATA_ROOT
  model:                 $MODEL_PATH
  training GPUs:         $INCLUDE_GPUS
  evaluation GPUs:       $EVAL_GPUS
  parallel evaluation:   $EVAL_PARALLEL_STAGES
  evaluation samples:    ${EVAL_LIMIT:-1000} per task
  skip complete train:   $SKIP_COMPLETED_TRAIN
  skip complete eval:    $SKIP_COMPLETED_EVAL
  dry run:               $DRY_RUN
EOF

run_factor "skill_requirement" "$RUN_SKILL_TRAIN" "$RUN_SKILL_EVAL" "$SKILL_RESUME_FROM_STAGE" "$SKILL_MASTER_PORT"
run_factor "visual_substrate" "$RUN_VISUAL_TRAIN" "$RUN_VISUAL_EVAL" "$VISUAL_RESUME_FROM_STAGE" "$VISUAL_MASTER_PORT"

echo
echo "Skill and Visual continual training/evaluation pipeline completed."
echo "  skill summary:  $RESULT_BASE/skill_requirement/eval/summary/learning_matrix.md"
echo "  visual summary: $RESULT_BASE/visual_substrate/eval/summary/learning_matrix.md"
