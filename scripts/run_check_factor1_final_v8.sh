#!/usr/bin/env bash
set -euo pipefail

# Final distribution check for Factor-1 v8 after diagram-skill canonicalization.
# Override paths through environment variables if your final version name differs.

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

TRAIN_ROOT="${TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v8_diagram_skill_canonical}"
TRAIN_JSON="${TRAIN_JSON:-$TRAIN_ROOT/train.json}"
SPLIT_ROOT="${SPLIT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_10k_v8_diagram_skill_canonical}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$TRAIN_ROOT/final_stats}"
TRAIN_SAMPLES_PER_CLASS="${TRAIN_SAMPLES_PER_CLASS:-10000}"
EVAL_SAMPLES_PER_CLASS="${EVAL_SAMPLES_PER_CLASS:-1000}"
MAX_MISSING_IMAGES="${MAX_MISSING_IMAGES:-100}"
TOP_LIMIT="${TOP_LIMIT:-}"

cd "$PROJECT_ROOT"

if [[ ! -f "$TRAIN_JSON" ]]; then
  echo "TRAIN_JSON does not exist: $TRAIN_JSON" >&2
  echo "If you did not create the canonical version, set TRAIN_ROOT or TRAIN_JSON explicitly." >&2
  exit 1
fi

args=(
  "$PYTHON_BIN" scripts/check_factor1_final_distribution.py
  --train-json "$TRAIN_JSON"
  --output-root "$OUTPUT_ROOT"
  --image-folder "$IMAGE_FOLDER"
  --train-samples-per-class "$TRAIN_SAMPLES_PER_CLASS"
  --eval-samples-per-class "$EVAL_SAMPLES_PER_CLASS"
  --max-missing-images "$MAX_MISSING_IMAGES"
)

if [[ -d "$SPLIT_ROOT" ]]; then
  args+=(--split-root "$SPLIT_ROOT")
else
  echo "[warn] split root does not exist, skip split check: $SPLIT_ROOT" >&2
fi

if [[ -n "$TOP_LIMIT" ]]; then
  args+=(--top-limit "$TOP_LIMIT")
fi

echo "Check Factor-1 final distribution"
echo "  project root: $PROJECT_ROOT"
echo "  train json:   $TRAIN_JSON"
echo "  split root:   $SPLIT_ROOT"
echo "  image folder: $IMAGE_FOLDER"
echo "  output root:  $OUTPUT_ROOT"

"${args[@]}"
