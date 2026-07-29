#!/usr/bin/env bash
set -euo pipefail

# Evaluate every completed trainable-module prediction with the independent
# standard and all-sample LLM-Judge tracks, then compare module regimes.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
cd "$PROJECT_ROOT"

if [[ -x /root/miniconda3/envs/ETrain/bin/python ]]; then
  DEFAULT_PYTHON=/root/miniconda3/envs/ETrain/bin/python
else
  DEFAULT_PYTHON=python3
fi
PYTHON_BIN="${PYTHON_BIN:-$DEFAULT_PYTHON}"
export PYTHONPATH="$PROJECT_ROOT${PYTHONPATH:+:$PYTHONPATH}"

FACTOR="${FACTOR:-visual_substrate}"
MODULE_MODES="${MODULE_MODES:-vision_only projector_only llm_only}"
DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final}"
ORDER_JSON="${ORDER_JSON:-$DATA_ROOT/splits/$FACTOR/transition_order.json}"
RESULT_BASE="${RESULT_BASE:-$PROJECT_ROOT/results/coin++_trainable_modules/$FACTOR}"
GENERIC_RUNNER="${GENERIC_RUNNER:-$SCRIPT_DIR/run_dual_track_eval.sh}"
COMPARATOR="${COMPARATOR:-$PROJECT_ROOT/scripts/compare_coinpp_module_dual_eval.py}"

read -r -a modes <<< "$MODULE_MODES"
if [[ "${#modes[@]}" -eq 0 ]]; then
  echo "MODULE_MODES is empty" >&2
  exit 1
fi

result_roots=()
for mode in "${modes[@]}"; do
  root="$RESULT_BASE/$mode/eval"
  if [[ ! -d "$root" ]]; then
    echo "Missing module evaluation root: $root" >&2
    exit 1
  fi
  result_roots+=("$root")
done
RESULT_ROOTS="$(printf '%s ' "${result_roots[@]}")"
RESULT_ROOTS="${RESULT_ROOTS% }"

FACTOR="$FACTOR" \
PROJECT_ROOT="$PROJECT_ROOT" \
PYTHON_BIN="$PYTHON_BIN" \
DATA_ROOT="$DATA_ROOT" \
ORDER_JSON="$ORDER_JSON" \
RESULT_ROOTS="$RESULT_ROOTS" \
JUDGE_MODEL="${JUDGE_MODEL:-qwen3.6}" \
JUDGE_BASE_URL="${JUDGE_BASE_URL:-${OPENAI_BASE_URL:-http://127.0.0.1:8001/v1}}" \
JUDGE_API_KEY="${JUDGE_API_KEY:-${OPENAI_API_KEY:-EMPTY}}" \
JUDGE_BATCH_SIZE="${JUDGE_BATCH_SIZE:-8}" \
JUDGE_WORKERS="${JUDGE_WORKERS:-4}" \
JUDGE_TIMEOUT="${JUDGE_TIMEOUT:-180}" \
JUDGE_RETRIES="${JUDGE_RETRIES:-3}" \
SKIP_COMPLETED="${SKIP_COMPLETED:-0}" \
  bash "$GENERIC_RUNNER"

comparison_dir="$RESULT_BASE/comparison_dual"
"$PYTHON_BIN" "$COMPARATOR" \
  --result-base "$RESULT_BASE" \
  --output-dir "$comparison_dir" \
  --order-json "$ORDER_JSON" \
  --factor-name "$FACTOR" \
  --modes "${modes[@]}"

echo
echo "Trainable-module dual-track comparison:"
echo "  $comparison_dir/module_comparison_dual.md"
