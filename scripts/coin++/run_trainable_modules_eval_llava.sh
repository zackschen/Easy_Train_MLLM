#!/usr/bin/env bash
set -euo pipefail

# Evaluate each trainable-module regime on the same continual task matrix, then
# aggregate final accuracy, forgetting, and backward transfer across regimes.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$PROJECT_ROOT"

FACTOR="${FACTOR:-skill_requirement}"
MODULE_MODES="${MODULE_MODES:-vision_only projector_only llm_only}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final_textvqa_clean}"
ORDER_JSON="${ORDER_JSON:-$DATA_ROOT/splits/$FACTOR/transition_order.json}"
CHECKPOINT_BASE="${CHECKPOINT_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++_TrainableModules_textvqa_clean}"
RESULT_BASE="${RESULT_BASE:-$PROJECT_ROOT/results/coin++_trainable_modules_textvqa_clean}"
MODEL_BASE="${MODEL_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/vicuna-7b-v1.5}"

EVAL_SCRIPT="${EVAL_SCRIPT:-$SCRIPT_DIR/run_factor1_cl_eval_llava.sh}"
COMPARISON_SCRIPT="${COMPARISON_SCRIPT:-$PROJECT_ROOT/scripts/summarize_trainable_modules_eval.py}"

EVAL_GPUS="${EVAL_GPUS:-auto}"
MIN_FREE_GPU_MB="${MIN_FREE_GPU_MB:-20000}"
PARALLEL_STAGES="${PARALLEL_STAGES:-1}"
START_STAGE="${START_STAGE:-1}"
END_STAGE="${END_STAGE:-0}"
LIMIT="${LIMIT:-}"
SKIP_COMPLETED="${SKIP_COMPLETED:-1}"
SKIP_INCOMPLETE_MODES="${SKIP_INCOMPLETE_MODES:-0}"
RUN_SUMMARY="${RUN_SUMMARY:-1}"
RUN_COMPARISON="${RUN_COMPARISON:-1}"
DRY_RUN="${DRY_RUN:-0}"
METRIC="${METRIC:-relaxed_match}"

for required_path in "$ORDER_JSON" "$MODEL_BASE" "$EVAL_SCRIPT" "$COMPARISON_SCRIPT"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Missing required path: $required_path" >&2
    exit 1
  fi
done

read -r -a modes <<< "$MODULE_MODES"
if [[ "${#modes[@]}" -eq 0 ]]; then
  echo "MODULE_MODES is empty" >&2
  exit 1
fi

mapfile -t STAGES < <("$PYTHON_BIN" - "$ORDER_JSON" <<'PYCODE'
import json
import sys
from pathlib import Path

order = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
for stage in order.get("trainable_order", []):
    print(stage)
PYCODE
)
if [[ "${#STAGES[@]}" -eq 0 ]]; then
  echo "No trainable stages found in $ORDER_JSON" >&2
  exit 1
fi
if [[ "$END_STAGE" == "0" ]]; then
  END_STAGE="${#STAGES[@]}"
fi
if (( START_STAGE < 1 || END_STAGE > ${#STAGES[@]} || START_STAGE > END_STAGE )); then
  echo "Invalid stage range: START_STAGE=$START_STAGE END_STAGE=$END_STAGE, total=${#STAGES[@]}" >&2
  exit 1
fi

GPU_SELECTION="explicit"
if [[ "$EVAL_GPUS" == "auto" ]]; then
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    echo "EVAL_GPUS=auto requires nvidia-smi; set EVAL_GPUS explicitly." >&2
    exit 1
  fi

  selected_gpus=()
  while IFS=',' read -r gpu_index free_mb; do
    gpu_index="${gpu_index// /}"
    free_mb="${free_mb// /}"
    if [[ "$gpu_index" =~ ^[0-9]+$ && "$free_mb" =~ ^[0-9]+$ ]] \
      && (( free_mb >= MIN_FREE_GPU_MB )); then
      selected_gpus+=("$gpu_index")
    fi
  done < <(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits)

  if [[ "${#selected_gpus[@]}" -eq 0 ]]; then
    echo "No GPU has at least ${MIN_FREE_GPU_MB} MiB free for evaluation." >&2
    echo "Wait for a GPU or lower MIN_FREE_GPU_MB only if the model is known to fit." >&2
    exit 1
  fi
  EVAL_GPUS="$(IFS=,; printf '%s' "${selected_gpus[*]}")"
  GPU_SELECTION="auto (free memory >= ${MIN_FREE_GPU_MB} MiB)"
fi

checkpoint_complete() {
  local checkpoint="$1"
  local adapter_present=0
  if [[ -s "$checkpoint/adapter_model.bin" || -s "$checkpoint/adapter_model.safetensors" ]]; then
    adapter_present=1
  fi
  [[ "$adapter_present" == "1" ]] \
    && [[ -s "$checkpoint/adapter_config.json" ]] \
    && [[ -s "$checkpoint/config.json" ]] \
    && [[ -s "$checkpoint/non_lora_trainables.bin" ]] \
    && [[ -s "$checkpoint/trainer_state.json" ]]
}

cat <<EOF
CoIN++ trainable-module continual evaluation
  factor:              $FACTOR
  modes:               ${modes[*]}
  stages:              ${STAGES[*]}
  checkpoint base:     $CHECKPOINT_BASE
  result base:         $RESULT_BASE
  evaluation GPUs:     $EVAL_GPUS
  GPU selection:       $GPU_SELECTION
  parallel stages:     $PARALLEL_STAGES
  selected stages:     $START_STAGE-$END_STAGE
  samples/task:        ${LIMIT:-1000}
  metric:              $METRIC
  skip completed eval: $SKIP_COMPLETED
  dry run:             $DRY_RUN
EOF

evaluated_modes=()
for mode in "${modes[@]}"; do
  checkpoint_root="$CHECKPOINT_BASE/$FACTOR/$mode"
  missing_checkpoints=()
  if [[ "$DRY_RUN" != "1" ]]; then
    for idx in "${!STAGES[@]}"; do
      stage_no=$((idx + 1))
      stage="${STAGES[$idx]}"
      stage_key="${stage_no}_${stage}"
      if ! checkpoint_complete "$checkpoint_root/$stage_key"; then
        missing_checkpoints+=("$stage_key")
      fi
    done
  fi

  if [[ "${#missing_checkpoints[@]}" -gt 0 ]]; then
    echo "[incomplete] mode=$mode missing: ${missing_checkpoints[*]}" >&2
    if [[ "$SKIP_INCOMPLETE_MODES" == "1" ]]; then
      echo "[skip mode] $mode"
      continue
    fi
    echo "Set SKIP_INCOMPLETE_MODES=1 to evaluate only fully trained modes." >&2
    exit 1
  fi

  mode_result_root="$RESULT_BASE/$FACTOR/$mode/eval"
  echo
  echo "================ evaluate module: $mode ================"
  FACTOR="$FACTOR" \
  PROJECT_ROOT="$PROJECT_ROOT" \
  PYTHON_BIN="$PYTHON_BIN" \
  DATA_ROOT="$DATA_ROOT" \
  ORDER_JSON="$ORDER_JSON" \
  MODEL_BASE="$MODEL_BASE" \
  CHECKPOINT_ROOT="$checkpoint_root" \
  RESULT_ROOT="$mode_result_root" \
  EVAL_GPUS="$EVAL_GPUS" \
  PARALLEL_STAGES="$PARALLEL_STAGES" \
  START_STAGE="$START_STAGE" \
  END_STAGE="$END_STAGE" \
  LIMIT="$LIMIT" \
  SKIP_COMPLETED="$SKIP_COMPLETED" \
  RUN_SUMMARY="$RUN_SUMMARY" \
  DRY_RUN="$DRY_RUN" \
  METRIC="$METRIC" \
    bash "$EVAL_SCRIPT"
  evaluated_modes+=("$mode")
done

if [[ "${#evaluated_modes[@]}" -eq 0 ]]; then
  echo "No complete trainable-module checkpoints were selected." >&2
  exit 1
fi

if [[ "$DRY_RUN" != "1" && "$RUN_SUMMARY" == "1" && "$RUN_COMPARISON" == "1" ]]; then
  comparison_dir="$RESULT_BASE/$FACTOR/comparison"
  "$PYTHON_BIN" "$COMPARISON_SCRIPT" \
    --result-base "$RESULT_BASE/$FACTOR" \
    --output-dir "$comparison_dir" \
    --order-json "$ORDER_JSON" \
    --factor-name "$FACTOR" \
    --metric "$METRIC" \
    --modes "${evaluated_modes[@]}"
fi

echo
echo "Trainable-module evaluation completed."
echo "  per-mode results: $RESULT_BASE/$FACTOR/<mode>/eval/summary/"
if [[ "$RUN_COMPARISON" == "1" ]]; then
  echo "  module comparison: $RESULT_BASE/$FACTOR/comparison/module_comparison.md"
fi
