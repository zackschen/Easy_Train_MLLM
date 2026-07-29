#!/usr/bin/env bash
set -euo pipefail

# Run the trainable-module comparison sequentially on the same data transition.
# The joint LLM+projector regime is retained as the existing-training control.

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
FACTOR="${FACTOR:-visual_substrate}"
MODULE_MODES="${MODULE_MODES:-vision_only projector_only llm_only}"
AUTO_RESUME="${AUTO_RESUME:-1}"
BASE_MASTER_PORT="${MASTER_PORT:-29721}"

read -r -a modes <<< "$MODULE_MODES"
if [[ "${#modes[@]}" -eq 0 ]]; then
  echo "MODULE_MODES is empty" >&2
  exit 1
fi

echo "CoIN++ sequential trainable-module study"
echo "  factor: $FACTOR"
echo "  modes:  ${modes[*]}"
echo "  auto resume: $AUTO_RESUME"

for idx in "${!modes[@]}"; do
  mode="${modes[$idx]}"
  port=$((BASE_MASTER_PORT + idx))
  echo
  echo "================ module $((idx + 1))/${#modes[@]}: $mode ================"
  MODULE_MODE="$mode" \
  FACTOR="$FACTOR" \
  AUTO_RESUME="$AUTO_RESUME" \
  MASTER_PORT="$port" \
  bash "$PROJECT_ROOT/scripts/coin++/run_trainable_module_cl_llava.sh"
done

echo
echo "All trainable-module training runs finished."
