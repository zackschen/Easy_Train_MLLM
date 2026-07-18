#!/usr/bin/env bash
set -euo pipefail

# Evaluate Factor-1 Evidence Complexity continual checkpoints.
#
# It evaluates each stage checkpoint on every evidence-complexity eval split:
#   checkpoint after single_evidence              -> all 4 eval tasks
#   checkpoint after multi_evidence               -> all 4 eval tasks
#   checkpoint after cross_region_or_multihop     -> all 4 eval tasks
#   checkpoint after cross_context                -> all 4 eval tasks
#
# The output is a learning/forgetting matrix under:
#   results/factor1_eval/evidence_complexity/summary/

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

BALANCED_ROOT="${BALANCED_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_balanced_v2}"
EVAL_ROOT="${EVAL_ROOT:-$BALANCED_ROOT/evidence_complexity/trainable/eval}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"

DEFAULT_CKPT_ROOT="$PROJECT_ROOT/checkpoints/LLaVA/Instruction/Factor1-Pilot/evidence_complexity"
if [[ -z "${CKPT_ROOT:-}" ]]; then
  CKPT_ROOT=""
  for candidate in     "$DEFAULT_CKPT_ROOT"     "$BALANCED_ROOT/checkpoints/evidence_complexity"     "$BALANCED_ROOT/evidence_complexity/checkpoints"     "$BALANCED_ROOT/checkpoints"     "$BALANCED_ROOT"; do
    if [[ -d "$candidate/1_single_evidence" ]]; then
      CKPT_ROOT="$candidate"
      break
    fi
  done
  if [[ -z "$CKPT_ROOT" ]]; then
    CKPT_ROOT="$DEFAULT_CKPT_ROOT"
  fi
fi

RESULT_ROOT="${RESULT_ROOT:-$BALANCED_ROOT/evidence_complexity_eval_results}"
MODEL_BASE="${MODEL_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/vicuna-7b-v1.5}"
CONV_MODE="${CONV_MODE:-vicuna_v1}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"

STAGES=(single_evidence multi_evidence cross_region_or_multihop cross_context)
TASKS=(single_evidence multi_evidence cross_region_or_multihop cross_context)
if [[ -n "${STAGES_OVERRIDE:-}" ]]; then
  read -r -a STAGES <<< "$STAGES_OVERRIDE"
fi
if [[ -n "${TASKS_OVERRIDE:-}" ]]; then
  read -r -a TASKS <<< "$TASKS_OVERRIDE"
fi

LIMIT="${LIMIT:-20}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-64}"
TEMPERATURE="${TEMPERATURE:-0}"
NUM_BEAMS="${NUM_BEAMS:-1}"

cd "$PROJECT_ROOT"
mkdir -p "$RESULT_ROOT"

echo "Factor-1 Evidence LLaVA evaluation"
echo "  project root:   $PROJECT_ROOT"
echo "  checkpoint root:$CKPT_ROOT"
echo "  eval root:      $EVAL_ROOT"
echo "  image folder:   $IMAGE_FOLDER"
echo "  result root:    $RESULT_ROOT"
echo "  model base:     $MODEL_BASE"
echo "  cuda devices:   $CUDA_VISIBLE_DEVICES"
echo "  stages:         ${STAGES[*]}"
echo "  tasks:          ${TASKS[*]}"

if [[ ! -d "$CKPT_ROOT" ]]; then
  echo "Checkpoint root does not exist: $CKPT_ROOT" >&2
  exit 1
fi
if [[ ! -d "$EVAL_ROOT" ]]; then
  echo "Eval root does not exist: $EVAL_ROOT" >&2
  exit 1
fi
if [[ ! -d "$MODEL_BASE" ]]; then
  echo "MODEL_BASE does not exist: $MODEL_BASE" >&2
  exit 1
fi

for idx in "${!STAGES[@]}"; do
  stage_no=$((idx + 1))
  stage="${STAGES[$idx]}"
  stage_name="${stage_no}_${stage}"
  ckpt="$CKPT_ROOT/$stage_name"
  out_dir="$RESULT_ROOT/$stage_name"

  if [[ ! -d "$ckpt" ]]; then
    echo "Missing checkpoint for stage $stage_name: $ckpt" >&2
    exit 1
  fi

  eval_args=()
  for task in "${TASKS[@]}"; do
    eval_file="$EVAL_ROOT/$task/eval.json"
    if [[ ! -f "$eval_file" ]]; then
      echo "Missing eval file for task $task: $eval_file" >&2
      exit 1
    fi
    eval_args+=(--eval-file "$task:$eval_file")
  done

  extra_args=()
  if [[ -n "$LIMIT" ]]; then
    extra_args+=(--limit "$LIMIT")
  fi

  echo
  echo "================ Eval stage ${stage_no}/${#STAGES[@]}: $stage_name ================"
  echo "  checkpoint: $ckpt"
  echo "  output:     $out_dir"

  CUDA_VISIBLE_DEVICES="$CUDA_VISIBLE_DEVICES" "$PYTHON_BIN" scripts/eval_factor1_llava_json.py \
    --model-path "$ckpt" \
    --model-base "$MODEL_BASE" \
    --stage-name "$stage_name" \
    --image-folder "$IMAGE_FOLDER" \
    --output-dir "$out_dir" \
    --conv-mode "$CONV_MODE" \
    --temperature "$TEMPERATURE" \
    --num-beams "$NUM_BEAMS" \
    --max-new-tokens "$MAX_NEW_TOKENS" \
    "${extra_args[@]}" \
    "${eval_args[@]}"
done

"$PYTHON_BIN" scripts/summarize_factor1_eval.py \
  --result-root "$RESULT_ROOT" \
  --stage-order "${STAGES[@]}" \
  --task-order "${TASKS[@]}" \
  --metric relaxed_match

echo
echo "Evaluation completed."
echo "  summary csv:      $RESULT_ROOT/summary/summary.csv"
echo "  relaxed matrix:   $RESULT_ROOT/summary/matrix_relaxed_match.csv"
echo "  exact matrix:     $RESULT_ROOT/summary/matrix_exact_match.csv"
echo "  forgetting csv:   $RESULT_ROOT/summary/forgetting_relaxed_match.csv"
echo "  markdown table:   $RESULT_ROOT/summary/learning_matrix.md"
