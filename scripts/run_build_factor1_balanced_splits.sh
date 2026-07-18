#!/usr/bin/env bash
set -euo pipefail

# Build support-aware balanced splits for all Factor-1 dimensions.
#
# Output:
#   cl_dataset/coin_factor1_balanced_v2/
#
# Default policy:
#   trainable stage:   category support >= 3000
#   eval-only:         500 <= category support < 3000
#   tail diagnostic:   category support < 500
#   train/eval size:   1000 train + 300 eval per trainable category

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

TRAIN_JSON="${TRAIN_JSON:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2/train.json}"
TRAIN_ROOT="${TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_balanced_v2}"

FACTORS="${FACTORS:-visual_substrate skill_requirement evidence_complexity answer_distribution}"

TRAIN_SAMPLES_PER_CLASS="${TRAIN_SAMPLES_PER_CLASS:-1000}"
EVAL_SAMPLES_PER_CLASS="${EVAL_SAMPLES_PER_CLASS:-300}"
EVAL_ONLY_SAMPLES_PER_CLASS="${EVAL_ONLY_SAMPLES_PER_CLASS:-300}"
TAIL_SAMPLES_PER_CLASS="${TAIL_SAMPLES_PER_CLASS:-200}"
MIN_TRAIN_SUPPORT="${MIN_TRAIN_SUPPORT:-3000}"
MIN_EVAL_SUPPORT="${MIN_EVAL_SUPPORT:-500}"
BALANCE_BY="${BALANCE_BY:-dataset}"
MAX_IMAGES_TO_CHECK="${MAX_IMAGES_TO_CHECK:-80}"
SEED="${SEED:-42}"
COMPACT="${COMPACT:-0}"

cd "$PROJECT_ROOT"

echo "Build Factor-1 balanced splits"
echo "  project root:             $PROJECT_ROOT"
echo "  train json:               $TRAIN_JSON"
echo "  train root:               $TRAIN_ROOT"
echo "  image folder:             $IMAGE_FOLDER"
echo "  output root:              $OUTPUT_ROOT"
echo "  factors:                  $FACTORS"
echo "  train samples per class:  $TRAIN_SAMPLES_PER_CLASS"
echo "  eval samples per class:   $EVAL_SAMPLES_PER_CLASS"
echo "  min train support:        $MIN_TRAIN_SUPPORT"
echo "  min eval support:         $MIN_EVAL_SUPPORT"
echo "  balance by:               $BALANCE_BY"

read -r -a factor_values <<< "$FACTORS"
read -r -a balance_values <<< "$BALANCE_BY"

args=(
  "$PYTHON_BIN" scripts/build_factor1_balanced_splits.py
  --train-json "$TRAIN_JSON"
  --train-root "$TRAIN_ROOT"
  --image-folder "$IMAGE_FOLDER"
  --output-root "$OUTPUT_ROOT"
  --factors "${factor_values[@]}"
  --train-samples-per-class "$TRAIN_SAMPLES_PER_CLASS"
  --eval-samples-per-class "$EVAL_SAMPLES_PER_CLASS"
  --eval-only-samples-per-class "$EVAL_ONLY_SAMPLES_PER_CLASS"
  --tail-samples-per-class "$TAIL_SAMPLES_PER_CLASS"
  --min-train-support "$MIN_TRAIN_SUPPORT"
  --min-eval-support "$MIN_EVAL_SUPPORT"
  --balance-by "${balance_values[@]}"
  --max-images-to-check "$MAX_IMAGES_TO_CHECK"
  --seed "$SEED"
)

if [[ "$COMPACT" == "1" ]]; then
  args+=(--compact)
fi

"${args[@]}"
