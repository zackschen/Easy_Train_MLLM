#!/usr/bin/env bash
set -euo pipefail

# Run the independent standard + all-sample Judge protocol for all data factors.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
RUNNER="${RUNNER:-$SCRIPT_DIR/run_dual_track_eval.sh}"
FACTORS="${FACTORS:-evidence_complexity skill_requirement visual_substrate}"

read -r -a factors <<< "$FACTORS"
for factor in "${factors[@]}"; do
  echo
  echo "===== Dual evaluation: $factor ====="
  FACTOR="$factor" \
  PROJECT_ROOT="$PROJECT_ROOT" \
  PYTHON_BIN="${PYTHON_BIN:-}" \
  JUDGE_MODEL="${JUDGE_MODEL:-qwen3.6}" \
  JUDGE_BASE_URL="${JUDGE_BASE_URL:-${OPENAI_BASE_URL:-http://127.0.0.1:8001/v1}}" \
  JUDGE_API_KEY="${JUDGE_API_KEY:-${OPENAI_API_KEY:-EMPTY}}" \
  JUDGE_BATCH_SIZE="${JUDGE_BATCH_SIZE:-8}" \
  JUDGE_WORKERS="${JUDGE_WORKERS:-4}" \
  JUDGE_TIMEOUT="${JUDGE_TIMEOUT:-180}" \
  JUDGE_RETRIES="${JUDGE_RETRIES:-3}" \
  LIMIT="${LIMIT:-}" \
  SKIP_COMPLETED="${SKIP_COMPLETED:-0}" \
    bash "$RUNNER"
done

echo
echo "All requested CoIN++ factor evaluations completed."
