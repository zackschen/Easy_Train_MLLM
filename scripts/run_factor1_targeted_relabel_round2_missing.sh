#!/usr/bin/env bash
set -euo pipefail

# Round-2 targeted relabeling for the remaining Factor-1 shortages after v3.
#
# Remaining shortages observed after merging v2 + first targeted pass:
#   visual_substrate: chart, diagram
#   skill_requirement: text_reading, diagram_reasoning
#
# This wrapper deliberately restricts candidate mining to chart/diagram/OCR-like
# sources so the Qwen budget is not spent on natural_photo or medical samples.

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
RAW_ROOT="${RAW_ROOT:-$PROJECT_ROOT/cl_dataset/coin}"

BASE_TRAIN_JSON="${BASE_TRAIN_JSON:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v3/train.json}"
POOL_ROOT="${POOL_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_pool_v4_missing}"
TARGET_ROOT="${TARGET_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_meta_v4_missing}"
TARGETED_TRAIN_ROOT="${TARGETED_TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_targeted_train_v4_missing}"
MERGED_TRAIN_ROOT="${MERGED_TRAIN_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_train_v4}"
SPLIT_ROOT="${SPLIT_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_10k_v4}"

# Keep this narrow. Add textvqa only if you have registered it in factor1_coin_meta.py.
DATASETS_OVERRIDE="${DATASETS_OVERRIDE:-chartqa chartqa_eval ai2d scienceqa docvqa infographicvqa}"

TARGET_COUNT="${TARGET_COUNT:-13000}"
POOL_MAX_SAMPLES_PER_DATASET="${POOL_MAX_SAMPLES_PER_DATASET:-100000}"
MAX_TOTAL_CANDIDATES="${MAX_TOTAL_CANDIDATES:-60000}"
CANDIDATE_MULTIPLIER="${CANDIDATE_MULTIPLIER:-4.0}"
MIN_SCORE="${MIN_SCORE:-3}"
MIN_CANDIDATES_PER_DEFICIT="${MIN_CANDIDATES_PER_DEFICIT:-2000}"
MAX_CANDIDATES_PER_CATEGORY="${MAX_CANDIDATES_PER_CATEGORY:-30000}"

API_BASE="${API_BASE:-http://127.0.0.1:8001/v1}"
API_KEY="${API_KEY:-EMPTY}"
MODEL="${MODEL:-qwen3.6}"
BATCH_SIZE="${BATCH_SIZE:-1}"
MAX_TOKENS="${MAX_TOKENS:-4096}"
TIMEOUT="${TIMEOUT:-300}"
RETRIES="${RETRIES:-2}"

RUN_SPLIT_CHECK="${RUN_SPLIT_CHECK:-1}"
CHECK_RAW_DATASETS="${CHECK_RAW_DATASETS:-1}"
SELECT_ONLY="${SELECT_ONLY:-0}"
BUILD_POOL="${BUILD_POOL:-1}"

cd "$PROJECT_ROOT"

if [[ ! -f "$BASE_TRAIN_JSON" ]]; then
  echo "Base train JSON does not exist: $BASE_TRAIN_JSON" >&2
  echo "Run the v3 merge first, or set BASE_TRAIN_JSON explicitly." >&2
  exit 1
fi

if [[ "$CHECK_RAW_DATASETS" == "1" ]]; then
  echo "[0/7] Check raw datasets for round-2 sources"
  read -r -a dataset_values <<< "$DATASETS_OVERRIDE"
  "$PYTHON_BIN" - "$RAW_ROOT" "${dataset_values[@]}" <<'PYCODE'
import sys
from pathlib import Path
import factor1_coin_meta as meta
raw_root = Path(sys.argv[1])
datasets = sys.argv[2:]
missing = []
for dataset in datasets:
    path = meta.dataset_dir(raw_root, dataset)
    if path is None:
        missing.append(dataset)
        print(f"MISSING {dataset}")
    else:
        files = list(meta.data_files(path))[:3]
        print(f"FOUND {dataset}: {path} files={[str(p.name) for p in files]}")
if missing:
    print("\nRaw data for these datasets is missing under RAW_ROOT.", file=sys.stderr)
    print("Set RAW_ROOT to the server path that contains the downloaded HF datasets, or copy these datasets first:", file=sys.stderr)
    print("  " + " ".join(missing), file=sys.stderr)
    raise SystemExit(2)
PYCODE
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

bash scripts/run_factor1_targeted_relabel_v3.sh
