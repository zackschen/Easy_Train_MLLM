#!/usr/bin/env bash
set -euo pipefail

# Targeted second-pass Factor-1 metadata labeling.
#
# Purpose:
#   Start from the existing v2 training set, build a larger unrefined metadata
#   pool from the raw datasets, select likely candidates for under-supported
#   factor categories, run Qwen/VLM metadata labeling only on those candidates,
#   convert them to LLaVA format, merge with v2, and verify the 10k target split.
#
# Typical use on the Qwen/VLLM server:
#   API_BASE=http://127.0.0.1:8001/v1 bash scripts/factor1_data_pipeline/run_factor1_targeted_relabel_v3.sh
#
# If you only want to inspect selected candidates before Qwen labeling:
#   SELECT_ONLY=1 bash scripts/factor1_data_pipeline/run_factor1_targeted_relabel_v3.sh

PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$PIPELINE_DIR/../.." && pwd)}"
export PYTHONPATH="$PIPELINE_DIR${PYTHONPATH:+:$PYTHONPATH}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RAW_ROOT="${RAW_ROOT:-$PROJECT_ROOT/cl_dataset/coin}"

BASE_TRAIN_JSON="${BASE_TRAIN_JSON:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v2/train.json}"
POOL_ROOT="${POOL_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_pool_v3}"
TARGET_ROOT="${TARGET_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_meta_v3}"
TARGETED_TRAIN_ROOT="${TARGETED_TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_train_v3}"
MERGED_TRAIN_ROOT="${MERGED_TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v3}"
SPLIT_ROOT="${SPLIT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_10k_v3}"

POOL_METADATA="${POOL_METADATA:-$POOL_ROOT/metadata/sample_metadata.jsonl}"
TARGETED_METADATA="${TARGETED_METADATA:-$TARGET_ROOT/metadata/targeted_candidates.jsonl}"
TARGETED_REFINED="${TARGETED_REFINED:-$TARGET_ROOT/metadata/targeted_candidates.vlm.jsonl}"
TARGETED_CACHE="${TARGETED_CACHE:-$TARGET_ROOT/metadata/targeted_candidates.vlm.cache.jsonl}"
TARGETED_REPORT="${TARGETED_REPORT:-$TARGET_ROOT/metadata/targeted_candidates.report.json}"

API_BASE="${API_BASE:-http://127.0.0.1:8001/v1}"
API_KEY="${API_KEY:-EMPTY}"
MODEL="${MODEL:-qwen3.6}"
BATCH_SIZE="${BATCH_SIZE:-1}"
MAX_TOKENS="${MAX_TOKENS:-4096}"
TIMEOUT="${TIMEOUT:-300}"
RETRIES="${RETRIES:-2}"
CHECK_API="${CHECK_API:-1}"

POOL_MAX_SAMPLES_PER_DATASET="${POOL_MAX_SAMPLES_PER_DATASET:-50000}"
TARGET_COUNT="${TARGET_COUNT:-12000}"
CANDIDATE_MULTIPLIER="${CANDIDATE_MULTIPLIER:-2.0}"
MAX_TOTAL_CANDIDATES="${MAX_TOTAL_CANDIDATES:-60000}"
MIN_SCORE="${MIN_SCORE:-4}"
MIN_CANDIDATES_PER_DEFICIT="${MIN_CANDIDATES_PER_DEFICIT:-500}"
MAX_CANDIDATES_PER_CATEGORY="${MAX_CANDIDATES_PER_CATEGORY:-16000}"

BUILD_POOL="${BUILD_POOL:-1}"
SELECT_ONLY="${SELECT_ONLY:-0}"
REFINE_ONLY="${REFINE_ONLY:-0}"
CONVERT_ONLY="${CONVERT_ONLY:-0}"
RUN_SPLIT_CHECK="${RUN_SPLIT_CHECK:-1}"
FAIL_ON_ERROR="${FAIL_ON_ERROR:-1}"
ALLOW_TEXT_ONLY="${ALLOW_TEXT_ONLY:-1}"
JSON_MODE="${JSON_MODE:-1}"
ENABLE_THINKING="${ENABLE_THINKING:-0}"
IMAGE_ROOTS="${IMAGE_ROOTS:-}"
EXCLUDE_METADATA="${EXCLUDE_METADATA:-}"

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
mkdir -p "$TARGET_ROOT/metadata"

if ! "$PYTHON_BIN" -c "import pyarrow" >/dev/null 2>&1; then
  echo "pyarrow is required to read Parquet datasets." >&2
  echo "Install it in the current environment: $PYTHON_BIN -m pip install pyarrow" >&2
  exit 1
fi

echo "Factor-1 targeted relabel v3"
echo "  project root:       $PROJECT_ROOT"
echo "  raw root:           $RAW_ROOT"
echo "  base train json:    $BASE_TRAIN_JSON"
echo "  pool root:          $POOL_ROOT"
echo "  target root:        $TARGET_ROOT"
echo "  target count:       $TARGET_COUNT"
echo "  max candidates:     $MAX_TOTAL_CANDIDATES"
echo "  model/API:          $MODEL / $API_BASE"

if [[ "$CHECK_API" == "1" && "$SELECT_ONLY" != "1" && "$CONVERT_ONLY" != "1" ]]; then
  echo "[0/6] Check OpenAI-compatible Qwen API"
  "$PYTHON_BIN" - "$API_BASE" "$API_KEY" <<'PYCODE'
import json
import sys
import urllib.error
import urllib.request

base = sys.argv[1].rstrip("/")
api_key = sys.argv[2] if len(sys.argv) > 2 else "EMPTY"
if base.endswith("/chat/completions"):
    models_url = base[: -len("/chat/completions")] + "/models"
else:
    models_url = base + "/models"
headers = {}
if api_key:
    headers["Authorization"] = f"Bearer {api_key}"
req = urllib.request.Request(models_url, headers=headers, method="GET")
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", errors="replace")
except urllib.error.HTTPError as exc:
    print(f"API preflight failed: HTTP {exc.code} for {models_url}", file=sys.stderr)
    print("Expected API_BASE like http://127.0.0.1:8001/v1, not bare http://host:port and not a wrong port.", file=sys.stderr)
    raise SystemExit(2)
except Exception as exc:
    print(f"API preflight failed for {models_url}: {exc}", file=sys.stderr)
    raise SystemExit(2)
try:
    data = json.loads(body)
    names = [item.get("id") for item in data.get("data", []) if isinstance(item, dict)]
except Exception:
    names = []
print(f"API ok: {models_url}" + (f"; models={names[:5]}" if names else ""))
PYCODE
fi

if [[ "$REFINE_ONLY" != "1" && "$CONVERT_ONLY" != "1" ]]; then
  if [[ "$BUILD_POOL" == "1" ]]; then
    echo "[1/6] Build larger rule-metadata pool from raw datasets"
    "$PYTHON_BIN" "$PIPELINE_DIR/factor1_coin_meta.py" build \
      --raw-root "$RAW_ROOT" \
      --output-root "$POOL_ROOT" \
      --datasets "${DATASETS[@]}" \
      --max-samples-per-dataset "$POOL_MAX_SAMPLES_PER_DATASET" \
      --review-per-dataset 200
  fi

  if [[ ! -f "$POOL_METADATA" ]]; then
    echo "Pool metadata does not exist: $POOL_METADATA" >&2
    exit 1
  fi

  echo "[2/6] Select targeted candidates for under-supported factor classes"
  select_args=(
    "$PYTHON_BIN" "$PIPELINE_DIR/select_factor1_targeted_relabel_candidates.py"
    --candidate-metadata "$POOL_METADATA"
    --base-train-json "$BASE_TRAIN_JSON"
    --output "$TARGETED_METADATA"
    --report "$TARGETED_REPORT"
    --target-count "$TARGET_COUNT"
    --candidate-multiplier "$CANDIDATE_MULTIPLIER"
    --max-total-candidates "$MAX_TOTAL_CANDIDATES"
    --min-score "$MIN_SCORE"
    --min-candidates-per-deficit "$MIN_CANDIDATES_PER_DEFICIT"
    --max-candidates-per-category "$MAX_CANDIDATES_PER_CATEGORY"
  )
  if [[ -n "$EXCLUDE_METADATA" ]]; then
    IFS=: read -r -a exclude_values <<< "$EXCLUDE_METADATA"
    for exclude_path in "${exclude_values[@]}"; do
      select_args+=(--exclude-metadata "$exclude_path")
    done
  fi
  "${select_args[@]}"
fi

if [[ "$SELECT_ONLY" == "1" ]]; then
  echo "SELECT_ONLY=1; stopping before Qwen/VLM labeling."
  echo "  candidates: $TARGETED_METADATA"
  echo "  report:     $TARGETED_REPORT"
  exit 0
fi

if [[ "$CONVERT_ONLY" != "1" ]]; then
  if [[ ! -f "$TARGETED_METADATA" ]]; then
    echo "Targeted metadata does not exist: $TARGETED_METADATA" >&2
    exit 1
  fi

  echo "[3/6] Refine targeted candidates with Qwen/VLM metadata labeling"
  refine_args=(
    "$PYTHON_BIN" "$PIPELINE_DIR/factor1_coin_meta.py" refine-metadata
    --metadata "$TARGETED_METADATA"
    --output "$TARGETED_REFINED"
    --raw-root "$RAW_ROOT"
    --cache "$TARGETED_CACHE"
    --datasets "${DATASETS[@]}"
    --api-base "$API_BASE"
    --api-key "$API_KEY"
    --model "$MODEL"
    --batch-size "$BATCH_SIZE"
    --max-tokens "$MAX_TOKENS"
    --timeout "$TIMEOUT"
    --retries "$RETRIES"
  )
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
  "${refine_args[@]}"
fi

if [[ ! -f "$TARGETED_REFINED" ]]; then
  echo "Targeted refined metadata does not exist: $TARGETED_REFINED" >&2
  exit 1
fi

echo "[4/6] Convert newly refined targeted metadata to LLaVA train JSON"
"$PYTHON_BIN" "$PIPELINE_DIR/convert_factor1_meta_to_llava.py" \
  --metadata "$TARGETED_REFINED" \
  --output-root "$TARGETED_TRAIN_ROOT" \
  --raw-root "$RAW_ROOT" \
  --project-root "$PIPELINE_DIR" \
  --on-image-error text-only \
  --keep-raw-metadata

echo "[5/6] Merge v2 train JSON with newly targeted LLaVA samples"
"$PYTHON_BIN" "$PIPELINE_DIR/merge_factor1_llava_train_json.py" \
  --base-train-json "$BASE_TRAIN_JSON" \
  --base-image-prefix "coin_factor1_train_v2" \
  --new-train-json "$TARGETED_TRAIN_ROOT/train.json" \
  --new-image-prefix "coin_factor1_targeted_train_v3" \
  --output-root "$MERGED_TRAIN_ROOT" \
  --image-folder "$PROJECT_ROOT/cl_dataset"

if [[ "$RUN_SPLIT_CHECK" == "1" ]]; then
  echo "[6/6] Build strict 10k splits from merged v3 train JSON"
  TRAIN_JSON="$MERGED_TRAIN_ROOT/train.json" \
  TRAIN_ROOT="$PROJECT_ROOT/cl_dataset" \
  IMAGE_FOLDER="$PROJECT_ROOT/cl_dataset" \
  OUTPUT_ROOT="$SPLIT_ROOT" \
  PRESERVE_IMAGE_PATHS=1 \
  MAX_IMAGES_TO_CHECK=0 \
  bash "$PIPELINE_DIR/run_build_factor1_10k_splits.sh"
fi

echo "Completed targeted relabel pipeline."
echo "  targeted metadata: $TARGETED_METADATA"
echo "  targeted refined:  $TARGETED_REFINED"
echo "  targeted train:    $TARGETED_TRAIN_ROOT/train.json"
echo "  merged train v3:   $MERGED_TRAIN_ROOT/train.json"
echo "  split root:        $SPLIT_ROOT"
