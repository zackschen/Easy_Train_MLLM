#!/usr/bin/env bash
set -euo pipefail

# Generic continual evaluator for a CoIN++ Factor-1 track. Every stage
# checkpoint is evaluated on every task in that factor's transition order.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$PROJECT_ROOT"

FACTOR="${FACTOR:-evidence_complexity}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final}"
SPLIT_ROOT="${SPLIT_ROOT:-$DATA_ROOT/splits/$FACTOR}"
EVAL_DIR="${EVAL_DIR:-$SPLIT_ROOT/trainable/eval}"
ORDER_JSON="${ORDER_JSON:-$SPLIT_ROOT/transition_order.json}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"

CHECKPOINT_ROOT="${CHECKPOINT_ROOT:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++/$FACTOR}"
MODEL_BASE="${MODEL_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/vicuna-7b-v1.5}"
RESULT_ROOT="${RESULT_ROOT:-$PROJECT_ROOT/results/coin++/$FACTOR/eval}"
EVALUATOR="${EVALUATOR:-$PROJECT_ROOT/scripts/eval_factor1_llava_json.py}"
SUMMARIZER="${SUMMARIZER:-$PROJECT_ROOT/scripts/summarize_factor1_eval.py}"

EVAL_GPUS="${EVAL_GPUS:-0}"
PARALLEL_STAGES="${PARALLEL_STAGES:-0}"
START_STAGE="${START_STAGE:-1}"
END_STAGE="${END_STAGE:-0}"
SKIP_COMPLETED="${SKIP_COMPLETED:-1}"
DRY_RUN="${DRY_RUN:-0}"
RUN_SUMMARY="${RUN_SUMMARY:-1}"

CONV_MODE="${CONV_MODE:-vicuna_v1}"
TEMPERATURE="${TEMPERATURE:-0.0}"
NUM_BEAMS="${NUM_BEAMS:-1}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-64}"
LIMIT="${LIMIT:-}"
METRIC="${METRIC:-relaxed_match}"

for required_path in "$ORDER_JSON" "$EVAL_DIR" "$MODEL_BASE" "$IMAGE_FOLDER" "$EVALUATOR" "$SUMMARIZER"; do
  if [[ ! -e "$required_path" ]]; then
    echo "Missing required path: $required_path" >&2
    exit 1
  fi
done
if [[ "$DRY_RUN" != "1" && ! -d "$CHECKPOINT_ROOT" ]]; then
  echo "Missing checkpoint root: $CHECKPOINT_ROOT" >&2
  exit 1
fi
if [[ "$DRY_RUN" != "1" ]]; then
  if ! "$PYTHON_BIN" -c "import torch, transformers, peft; assert torch.cuda.is_available()" >/dev/null 2>&1; then
    echo "The selected Python cannot import the LLaVA evaluation stack or access CUDA: $PYTHON_BIN" >&2
    echo "Activate the training environment or set PYTHON_BIN=/path/to/environment/bin/python." >&2
    exit 1
  fi
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

IFS=',' read -r -a GPU_LIST <<< "$EVAL_GPUS"
if [[ "${#GPU_LIST[@]}" -eq 0 || -z "${GPU_LIST[0]}" ]]; then
  echo "EVAL_GPUS must contain at least one GPU id." >&2
  exit 1
fi
if [[ "$DRY_RUN" == "1" ]]; then
  PARALLEL_STAGES=0
fi

mkdir -p "$RESULT_ROOT/logs"

resolve_checkpoint() {
  local stage_dir="$1"
  if [[ -f "$stage_dir/adapter_config.json" && ( -f "$stage_dir/adapter_model.bin" || -f "$stage_dir/adapter_model.safetensors" ) ]]; then
    printf '%s\n' "$stage_dir"
    return 0
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    printf '%s\n' "$stage_dir"
    return 0
  fi

  "$PYTHON_BIN" - "$stage_dir" <<'PYCODE'
import sys
from pathlib import Path

root = Path(sys.argv[1])
candidates = []
for path in root.glob("checkpoint-*"):
    try:
        step = int(path.name.rsplit("-", 1)[1])
    except (IndexError, ValueError):
        continue
    valid = (path / "adapter_config.json").is_file() and (
        (path / "adapter_model.bin").is_file()
        or (path / "adapter_model.safetensors").is_file()
    )
    if valid:
        candidates.append((step, path))
if not candidates:
    raise SystemExit(f"No valid LoRA checkpoint found under {root}")
print(max(candidates)[1])
PYCODE
}

run_stage() {
  local stage_no="$1"
  local stage="$2"
  local gpu_id="$3"
  local stage_key="${stage_no}_${stage}"
  local checkpoint
  checkpoint="$(resolve_checkpoint "$CHECKPOINT_ROOT/$stage_key")"
  local output_dir="$RESULT_ROOT/$stage_key"
  local metrics_file="$output_dir/metrics_all.json"

  if [[ "$SKIP_COMPLETED" == "1" && -s "$metrics_file" ]]; then
    echo "[skip] $stage_key already evaluated"
    return 0
  fi

  local eval_args=()
  local task
  for task in "${STAGES[@]}"; do
    local eval_file="$EVAL_DIR/$task/eval.json"
    if [[ ! -f "$eval_file" ]]; then
      echo "Missing eval split: $eval_file" >&2
      return 1
    fi
    eval_args+=(--eval-file "$task:$eval_file")
  done

  local extra_args=()
  if [[ -n "$LIMIT" ]]; then
    extra_args+=(--limit "$LIMIT")
  fi
  local command=(
    "$PYTHON_BIN" "$EVALUATOR"
    --model-path "$checkpoint"
    --model-base "$MODEL_BASE"
    --stage-name "$stage"
    --image-folder "$IMAGE_FOLDER"
    --output-dir "$output_dir"
    --conv-mode "$CONV_MODE"
    --temperature "$TEMPERATURE"
    --num-beams "$NUM_BEAMS"
    --max-new-tokens "$MAX_NEW_TOKENS"
    --device cuda
    "${extra_args[@]}"
    "${eval_args[@]}"
  )

  echo "[eval] factor=$FACTOR stage=$stage_key gpu=$gpu_id checkpoint=$checkpoint"
  if [[ "$DRY_RUN" == "1" ]]; then
    printf 'CUDA_VISIBLE_DEVICES=%q' "$gpu_id"
    printf ' %q' "${command[@]}"
    printf '\n'
    return 0
  fi
  CUDA_VISIBLE_DEVICES="$gpu_id" "${command[@]}"
}

SELECTED_NOS=()
SELECTED_NAMES=()
for idx in "${!STAGES[@]}"; do
  stage_no=$((idx + 1))
  if (( stage_no >= START_STAGE && stage_no <= END_STAGE )); then
    SELECTED_NOS+=("$stage_no")
    SELECTED_NAMES+=("${STAGES[$idx]}")
  fi
done

cat <<EOF
CoIN++ Factor-1 continual evaluation
  factor:           $FACTOR
  checkpoint root: $CHECKPOINT_ROOT
  eval root:       $EVAL_DIR
  result root:     $RESULT_ROOT
  stages:          ${STAGES[*]}
  selected range:  $START_STAGE-$END_STAGE
  samples/task:    ${LIMIT:-1000}
  GPUs:            ${GPU_LIST[*]}
  parallel:        $PARALLEL_STAGES
  skip completed:  $SKIP_COMPLETED
EOF

if [[ "$PARALLEL_STAGES" == "1" ]]; then
  cursor=0
  while (( cursor < ${#SELECTED_NOS[@]} )); do
    pids=()
    labels=()
    for slot in "${!GPU_LIST[@]}"; do
      selected_idx=$((cursor + slot))
      if (( selected_idx >= ${#SELECTED_NOS[@]} )); then
        break
      fi
      stage_no="${SELECTED_NOS[$selected_idx]}"
      stage="${SELECTED_NAMES[$selected_idx]}"
      stage_key="${stage_no}_${stage}"
      log_file="$RESULT_ROOT/logs/$stage_key.log"
      run_stage "$stage_no" "$stage" "${GPU_LIST[$slot]}" >"$log_file" 2>&1 &
      pids+=("$!")
      labels+=("$stage_key")
      echo "[start] $stage_key gpu=${GPU_LIST[$slot]} -> $log_file"
    done

    failed=0
    for idx in "${!pids[@]}"; do
      if wait "${pids[$idx]}"; then
        echo "[complete] ${labels[$idx]}"
      else
        echo "[failed] ${labels[$idx]}; inspect $RESULT_ROOT/logs/${labels[$idx]}.log" >&2
        failed=1
      fi
    done
    if [[ "$failed" == "1" ]]; then
      exit 1
    fi
    cursor=$((cursor + ${#GPU_LIST[@]}))
  done
else
  for idx in "${!SELECTED_NOS[@]}"; do
    stage_no="${SELECTED_NOS[$idx]}"
    stage="${SELECTED_NAMES[$idx]}"
    stage_key="${stage_no}_${stage}"
    log_file="$RESULT_ROOT/logs/$stage_key.log"
    run_stage "$stage_no" "$stage" "${GPU_LIST[0]}" 2>&1 | tee "$log_file"
  done
fi

if [[ "$DRY_RUN" == "1" || "$RUN_SUMMARY" != "1" ]]; then
  exit 0
fi

"$PYTHON_BIN" "$SUMMARIZER" \
  --result-root "$RESULT_ROOT" \
  --stage-order "${STAGES[@]}" \
  --task-order "${STAGES[@]}" \
  --metric "$METRIC" \
  --factor-name "$FACTOR"

echo
echo "Evaluation completed for factor=$FACTOR"
echo "  table:       $RESULT_ROOT/summary/learning_matrix.md"
echo "  matrix:      $RESULT_ROOT/summary/matrix_${METRIC}.csv"
echo "  forgetting:  $RESULT_ROOT/summary/forgetting_${METRIC}.csv"
echo "  predictions: $RESULT_ROOT/<stage>/predictions/*.jsonl"
