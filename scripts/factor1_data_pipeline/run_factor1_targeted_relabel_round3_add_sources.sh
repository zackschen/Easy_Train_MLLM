#!/usr/bin/env bash
set -euo pipefail

# Round-3 targeted relabeling after v4 still lacks chart/diagram/text classes.
# This round assumes you have added extra raw datasets under RAW_ROOT, e.g.:
#   chart:   dvqa / plotqa / figureqa
#   diagram: iconqa / ai2d / scienceqa
#   text:    textvqa / stvqa / docvqa / infographicvqa

PIPELINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$PIPELINE_DIR/../.." && pwd)}"
export PYTHONPATH="$PIPELINE_DIR${PYTHONPATH:+:$PYTHONPATH}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RAW_ROOT="${RAW_ROOT:-$PROJECT_ROOT/cl_dataset/coin}"

BASE_TRAIN_JSON="${BASE_TRAIN_JSON:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v4/train.json}"
POOL_ROOT="${POOL_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_pool_v5_chart_diagram_text}"
TARGET_ROOT="${TARGET_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_meta_v5_chart_diagram_text}"
TARGETED_TRAIN_ROOT="${TARGETED_TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_train_v5_chart_diagram_text}"
MERGED_TRAIN_ROOT="${MERGED_TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v5}"
SPLIT_ROOT="${SPLIT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_10k_v5}"

# Use larger external sources first. Keep original sources as fallback.
DATASETS_OVERRIDE="${DATASETS_OVERRIDE:-dvqa plotqa figureqa iconqa ai2d scienceqa textvqa stvqa docvqa infographicvqa}"

TARGET_COUNT="${TARGET_COUNT:-13000}"
POOL_MAX_SAMPLES_PER_DATASET="${POOL_MAX_SAMPLES_PER_DATASET:-100000}"
MAX_TOTAL_CANDIDATES="${MAX_TOTAL_CANDIDATES:-80000}"
CANDIDATE_MULTIPLIER="${CANDIDATE_MULTIPLIER:-5.0}"
MIN_SCORE="${MIN_SCORE:-3}"
MIN_CANDIDATES_PER_DEFICIT="${MIN_CANDIDATES_PER_DEFICIT:-3000}"
MAX_CANDIDATES_PER_CATEGORY="${MAX_CANDIDATES_PER_CATEGORY:-50000}"

API_BASE="${API_BASE:-http://127.0.0.1:8001/v1}"
API_KEY="${API_KEY:-EMPTY}"
MODEL="${MODEL:-qwen3.6}"
BATCH_SIZE="${BATCH_SIZE:-1}"
MAX_TOKENS="${MAX_TOKENS:-4096}"
TIMEOUT="${TIMEOUT:-300}"
RETRIES="${RETRIES:-2}"

RUN_SPLIT_CHECK="${RUN_SPLIT_CHECK:-1}"
SELECT_ONLY="${SELECT_ONLY:-0}"
BUILD_POOL="${BUILD_POOL:-1}"
CHECK_RAW_DATASETS="${CHECK_RAW_DATASETS:-1}"
ALLOW_MISSING_DATASETS="${ALLOW_MISSING_DATASETS:-0}"

cd "$PROJECT_ROOT"

if [[ ! -f "$BASE_TRAIN_JSON" ]]; then
  echo "Base train JSON does not exist: $BASE_TRAIN_JSON" >&2
  echo "Set BASE_TRAIN_JSON to the latest merged train JSON." >&2
  exit 1
fi

if [[ "$CHECK_RAW_DATASETS" == "1" ]]; then
  echo "[0/7] Check raw datasets for additional chart/diagram/text sources"
  read -r -a requested_datasets <<< "$DATASETS_OVERRIDE"
  available=()
  missing=()
  while IFS= read -r line; do
    case "$line" in
      FOUND\ *) available+=("${line#FOUND }") ;;
      MISSING\ *) missing+=("${line#MISSING }") ;;
      *) echo "$line" ;;
    esac
  done < <("$PYTHON_BIN" - "$RAW_ROOT" "${requested_datasets[@]}" <<'PYCODE'
import sys
from pathlib import Path
import factor1_coin_meta as meta
raw_root = Path(sys.argv[1])
for dataset in sys.argv[2:]:
    path = meta.dataset_dir(raw_root, dataset)
    if path is None:
        print(f"MISSING {dataset}")
    else:
        files = list(meta.data_files(path))[:2]
        print(f"FOUND {dataset}")
        print(f"  {dataset}: {path} files={[p.name for p in files]}")
PYCODE
  )
  if [[ "${#missing[@]}" -gt 0 ]]; then
    echo "Missing datasets: ${missing[*]}" >&2
    if [[ "$ALLOW_MISSING_DATASETS" != "1" ]]; then
      echo "Download/copy the missing sources first, or set ALLOW_MISSING_DATASETS=1 to continue with only available datasets." >&2
      exit 2
    fi
  fi
  if [[ "${#available[@]}" -eq 0 ]]; then
    echo "No requested raw datasets are available under RAW_ROOT=$RAW_ROOT" >&2
    exit 2
  fi
  DATASETS_OVERRIDE="${available[*]}"
fi

export RAW_ROOT
export BASE_TRAIN_JSON
export POOL_ROOT
export TARGET_ROOT
export TARGETED_TRAIN_ROOT
export MERGED_TRAIN_ROOT
export SPLIT_ROOT
export DATASETS_OVERRIDE
export TARGET_COUNT
export POOL_MAX_SAMPLES_PER_DATASET
export MAX_TOTAL_CANDIDATES
export CANDIDATE_MULTIPLIER
export MIN_SCORE
export MIN_CANDIDATES_PER_DEFICIT
export MAX_CANDIDATES_PER_CATEGORY
export API_BASE
export API_KEY
export MODEL
export BATCH_SIZE
export MAX_TOKENS
export TIMEOUT
export RETRIES
export RUN_SPLIT_CHECK
export SELECT_ONLY
export BUILD_POOL

bash "$PIPELINE_DIR/run_factor1_targeted_relabel_v3.sh"
