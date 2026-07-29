#!/usr/bin/env bash
set -euo pipefail

# Build Factor-1 target splits with fixed train/eval size per selected category.
#
# Default target:
#   Visual substrate: natural_photo, medical, document, infographic, diagram, chart
#   Skill requirement: recognition, counting, medical_reasoning, knowledge_reasoning,
#                      chart_reasoning, document_reasoning, text_reading,
#                      diagram_reasoning, relation, attribute
#   Evidence complexity: single_evidence, multi_evidence,
#                        cross_region_or_multihop, cross_context
#
# By default this script requires 10000 train + 1000 eval samples per category.
# If a category is still under-supported, keep STRICT=1 to fail fast and show the
# deficient category. Set STRICT=0 only when you want partial diagnostic outputs.
#
# This script can run on a split-building server without local image files:
# PRESERVE_IMAGE_PATHS=1 keeps image paths relative to IMAGE_FOLDER but skips
# resolving image bytes. Training/evaluation still needs the actual images.

PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$PIPELINE_DIR/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

TRAIN_JSON="${TRAIN_JSON:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2/train.json}"
TRAIN_ROOT="${TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_10k_v3}"

FACTORS="${FACTORS:-visual_substrate skill_requirement evidence_complexity}"
VISUAL_CATEGORIES="${VISUAL_CATEGORIES:-natural_photo,medical,document,infographic,diagram,chart}"
SKILL_CATEGORIES="${SKILL_CATEGORIES:-recognition,counting,medical_reasoning,knowledge_reasoning,chart_reasoning,document_reasoning,text_reading,diagram_reasoning,relation,attribute}"
EVIDENCE_CATEGORIES="${EVIDENCE_CATEGORIES:-single_evidence,multi_evidence,cross_region_or_multihop,cross_context}"

TRAIN_SAMPLES_PER_CLASS="${TRAIN_SAMPLES_PER_CLASS:-10000}"
EVAL_SAMPLES_PER_CLASS="${EVAL_SAMPLES_PER_CLASS:-1000}"
EVAL_ONLY_SAMPLES_PER_CLASS="${EVAL_ONLY_SAMPLES_PER_CLASS:-1000}"
TAIL_SAMPLES_PER_CLASS="${TAIL_SAMPLES_PER_CLASS:-200}"
MIN_TRAIN_SUPPORT="${MIN_TRAIN_SUPPORT:-$((TRAIN_SAMPLES_PER_CLASS + EVAL_SAMPLES_PER_CLASS))}"
MIN_EVAL_SUPPORT="${MIN_EVAL_SUPPORT:-500}"
BALANCE_BY="${BALANCE_BY:-dataset}"
MAX_IMAGES_TO_CHECK="${MAX_IMAGES_TO_CHECK:-0}"
SEED="${SEED:-42}"
STRICT="${STRICT:-1}"
COMPACT="${COMPACT:-1}"
PRESERVE_IMAGE_PATHS="${PRESERVE_IMAGE_PATHS:-1}"

cd "$PROJECT_ROOT"

read -r -a factor_values <<< "$FACTORS"
read -r -a balance_values <<< "$BALANCE_BY"

args=(
  "$PYTHON_BIN" "$PIPELINE_DIR/build_factor1_balanced_splits.py"
  --train-json "$TRAIN_JSON"
  --train-root "$TRAIN_ROOT"
  --image-folder "$IMAGE_FOLDER"
  --output-root "$OUTPUT_ROOT"
  --factors "${factor_values[@]}"
  --include-categories "visual_substrate=$VISUAL_CATEGORIES"
  --include-categories "skill_requirement=$SKILL_CATEGORIES"
  --include-categories "evidence_complexity=$EVIDENCE_CATEGORIES"
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

if [[ "$STRICT" == "1" ]]; then
  args+=(--strict-included-categories)
fi

if [[ "$PRESERVE_IMAGE_PATHS" == "1" ]]; then
  args+=(--preserve-image-paths)
fi

if [[ "$COMPACT" == "1" ]]; then
  args+=(--compact)
fi

echo "Build Factor-1 10k target splits"
echo "  project root:       $PROJECT_ROOT"
echo "  train json:         $TRAIN_JSON"
echo "  output root:        $OUTPUT_ROOT"
echo "  train/eval per cat: $TRAIN_SAMPLES_PER_CLASS / $EVAL_SAMPLES_PER_CLASS"
echo "  factors:            $FACTORS"
echo "  visual categories:  $VISUAL_CATEGORIES"
echo "  skill categories:   $SKILL_CATEGORIES"
echo "  evidence categories:$EVIDENCE_CATEGORIES"
echo "  strict:             $STRICT"
echo "  preserve image path:$PRESERVE_IMAGE_PATHS"
echo "  image checks:       $MAX_IMAGES_TO_CHECK"

"${args[@]}"
