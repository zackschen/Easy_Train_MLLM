#!/usr/bin/env bash
set -euo pipefail

# Build sample metadata from all downloaded HF datasets, then refine all
# visual/skill/evidence fields through the local Qwen3.6 vLLM endpoint.
#
# Smoke test:
#   MAX_SAMPLES_PER_DATASET=20 REFINE_LIMIT=40 bash scripts/run_factor1_all_metadata.sh
#
# Full run:
#   bash scripts/run_factor1_all_metadata.sh
#
# Resume after interruption:
#   REFINE_ONLY=1 bash scripts/run_factor1_all_metadata.sh

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RAW_ROOT="${RAW_ROOT:-$PROJECT_ROOT/cl_dataset/coin}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_meta_all}"
METADATA_PATH="${METADATA_PATH:-$OUTPUT_ROOT/metadata/sample_metadata.jsonl}"
REFINED_PATH="${REFINED_PATH:-$OUTPUT_ROOT/metadata/sample_metadata.vlm.jsonl}"
CACHE_PATH="${CACHE_PATH:-$OUTPUT_ROOT/metadata/sample_metadata.vlm.cache.jsonl}"
GAP_PATH="${GAP_PATH:-$OUTPUT_ROOT/metadata/transition_gap_table.vlm.csv}"

API_BASE="${API_BASE:-http://127.0.0.1:8000/v1}"
API_KEY="${API_KEY:-EMPTY}"
MODEL="${MODEL:-qwen3.6}"
BATCH_SIZE="${BATCH_SIZE:-1}"
MAX_TOKENS="${MAX_TOKENS:-4096}"
TIMEOUT="${TIMEOUT:-300}"
RETRIES="${RETRIES:-2}"

MAX_SAMPLES_PER_DATASET="${MAX_SAMPLES_PER_DATASET:-}"
REFINE_LIMIT="${REFINE_LIMIT:-}"
REVIEW_PER_DATASET="${REVIEW_PER_DATASET:-200}"
LOW_CONFIDENCE_THRESHOLD="${LOW_CONFIDENCE_THRESHOLD:-0.70}"
SPLITS="${SPLITS:-}"
IMAGE_ROOTS="${IMAGE_ROOTS:-}"

BUILD_ONLY="${BUILD_ONLY:-0}"
REFINE_ONLY="${REFINE_ONLY:-0}"
RUN_GAPS="${RUN_GAPS:-0}"
FAIL_ON_ERROR="${FAIL_ON_ERROR:-1}"
ALLOW_TEXT_ONLY="${ALLOW_TEXT_ONLY:-0}"
ENABLE_THINKING="${ENABLE_THINKING:-0}"
JSON_MODE="${JSON_MODE:-1}"

DATASETS=(
  vqav2
  gqa
  visual7w
  tallyqa
  ai2d
  chartqa
  chartqa_eval
  docvqa
  infographicvqa
  okvqa
  aokvqa
  scienceqa
  mmmu
  slake
  vqarad
  pathvqa
  remote_sensing_vqa
  lrs_vqa
)

if [[ -n "${DATASETS_OVERRIDE:-}" ]]; then
  read -r -a DATASETS <<< "${DATASETS_OVERRIDE}"
fi

cd "$PROJECT_ROOT"

if ! "$PYTHON_BIN" -c "import pyarrow" >/dev/null 2>&1; then
  echo "pyarrow is required to read embedded images from Parquet." >&2
  echo "Install it in the current environment: $PYTHON_BIN -m pip install pyarrow" >&2
  exit 1
fi

echo "Factor-1 metadata pipeline"
echo "  project root:   $PROJECT_ROOT"
echo "  raw root:       $RAW_ROOT"
echo "  output root:    $OUTPUT_ROOT"
echo "  datasets:       ${DATASETS[*]}"
echo "  model:          $MODEL"
echo "  API:            $API_BASE"
echo "  batch size:     $BATCH_SIZE"

if [[ "$REFINE_ONLY" != "1" ]]; then
  build_args=(
    "$PYTHON_BIN" factor1_coin_meta.py build
    --raw-root "$RAW_ROOT"
    --output-root "$OUTPUT_ROOT"
    --datasets "${DATASETS[@]}"
    --review-per-dataset "$REVIEW_PER_DATASET"
    --low-confidence-threshold "$LOW_CONFIDENCE_THRESHOLD"
    --fail-on-empty
  )
  if [[ -n "$MAX_SAMPLES_PER_DATASET" ]]; then
    build_args+=(--max-samples-per-dataset "$MAX_SAMPLES_PER_DATASET")
  fi

  echo "[1/2] Building metadata from Parquet"
  "${build_args[@]}"
fi

if [[ "$BUILD_ONLY" == "1" ]]; then
  echo "BUILD_ONLY=1; stopping after build."
  exit 0
fi

if [[ ! -f "$METADATA_PATH" ]]; then
  echo "Metadata file does not exist: $METADATA_PATH" >&2
  echo "Run without REFINE_ONLY=1 first, or set METADATA_PATH." >&2
  exit 1
fi

refine_args=(
  "$PYTHON_BIN" factor1_coin_meta.py refine-metadata
  --metadata "$METADATA_PATH"
  --output "$REFINED_PATH"
  --raw-root "$RAW_ROOT"
  --cache "$CACHE_PATH"
  --datasets "${DATASETS[@]}"
  --api-base "$API_BASE"
  --api-key "$API_KEY"
  --model "$MODEL"
  --batch-size "$BATCH_SIZE"
  --max-tokens "$MAX_TOKENS"
  --timeout "$TIMEOUT"
  --retries "$RETRIES"
)

if [[ -n "$REFINE_LIMIT" ]]; then
  refine_args+=(--limit "$REFINE_LIMIT")
fi
if [[ -n "$SPLITS" ]]; then
  read -r -a split_values <<< "$SPLITS"
  refine_args+=(--splits "${split_values[@]}")
fi
if [[ -n "$IMAGE_ROOTS" ]]; then
  IFS=: read -r -a image_root_values <<< "$IMAGE_ROOTS"
  for image_root in "${image_root_values[@]}"; do
    refine_args+=(--image-root "$image_root")
  done
fi
if [[ "$FAIL_ON_ERROR" == "1" ]]; then
  refine_args+=(--fail-on-error)
fi
if [[ "$ALLOW_TEXT_ONLY" == "1" ]]; then
  refine_args+=(--allow-text-only)
fi
if [[ "$ENABLE_THINKING" == "1" ]]; then
  refine_args+=(--enable-thinking)
fi
if [[ "$JSON_MODE" != "1" ]]; then
  refine_args+=(--no-json-mode)
fi

echo "[2/2] Refining metadata with Qwen3.6"
"${refine_args[@]}"

if [[ "$RUN_GAPS" == "1" ]]; then
  gap_args=(
    "$PYTHON_BIN" factor1_coin_meta.py gaps
    --metadata "$REFINED_PATH"
    --output "$GAP_PATH"
    --split all
  )
  "${gap_args[@]}"
fi

echo "Completed."
echo "  metadata: $METADATA_PATH"
echo "  refined:  $REFINED_PATH"
echo "  cache:    $CACHE_PATH"
