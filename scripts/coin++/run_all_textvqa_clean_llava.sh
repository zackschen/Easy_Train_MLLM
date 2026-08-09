#!/usr/bin/env bash
set -euo pipefail

# One-command CoIN++ rerun on the cleaned TextVQA targets. All outputs use a
# separate namespace, and every child runner keeps its own resume/skip logic.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$SCRIPT_DIR/../.." && pwd)}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
cd "$PROJECT_ROOT"

DATA_ROOT="${DATA_ROOT:-$PROJECT_ROOT/cl_dataset/coin_factor1_final_textvqa_clean}"
IMAGE_FOLDER="${IMAGE_FOLDER:-$PROJECT_ROOT/cl_dataset}"
CHECKPOINT_BASE="${CHECKPOINT_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++_textvqa_clean}"
RESULT_BASE="${RESULT_BASE:-$PROJECT_ROOT/results/coin++_textvqa_clean}"
MODULE_CHECKPOINT_BASE="${MODULE_CHECKPOINT_BASE:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++_TrainableModules_textvqa_clean}"
MODULE_RESULT_BASE="${MODULE_RESULT_BASE:-$PROJECT_ROOT/results/coin++_trainable_modules_textvqa_clean}"

MODEL_VERSION="${MODEL_VERSION:-vicuna-7b-v1.5}"
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/checkpoints/LLaVA/Vicuna/$MODEL_VERSION}"
MODEL_BASE="${MODEL_BASE:-$MODEL_PATH}"

FACTORS="${FACTORS:-evidence_complexity skill_requirement visual_substrate}"
MODULE_FACTORS="${MODULE_FACTORS:-evidence_complexity skill_requirement visual_substrate}"
MODULE_MODES="${MODULE_MODES:-}"
EVIDENCE_COMPLEXITY_MODULE_MODES="${EVIDENCE_COMPLEXITY_MODULE_MODES:-vision_only projector_only llm_only llm_projector}"
SKILL_REQUIREMENT_MODULE_MODES="${SKILL_REQUIREMENT_MODULE_MODES:-vision_only projector_only llm_only}"
VISUAL_SUBSTRATE_MODULE_MODES="${VISUAL_SUBSTRATE_MODULE_MODES:-vision_only projector_only llm_only}"

INCLUDE_GPUS="${INCLUDE_GPUS:-localhost:0,1,2,3}"
EVAL_GPUS="${EVAL_GPUS:-0,1,2,3}"
EVAL_PARALLEL_STAGES="${EVAL_PARALLEL_STAGES:-1}"
EVAL_LIMIT="${EVAL_LIMIT:-}"
FACTOR_MASTER_PORT_BASE="${FACTOR_MASTER_PORT_BASE:-29800}"
MODULE_MASTER_PORT_BASE="${MODULE_MASTER_PORT_BASE:-29900}"

RUN_FACTOR_TRAIN="${RUN_FACTOR_TRAIN:-1}"
RUN_FACTOR_EVAL="${RUN_FACTOR_EVAL:-1}"
RUN_MODULE_TRAIN="${RUN_MODULE_TRAIN:-1}"
RUN_MODULE_EVAL="${RUN_MODULE_EVAL:-1}"
RUN_DUAL_EVAL="${RUN_DUAL_EVAL:-auto}"
RUN_MODULE_DUAL_EVAL="${RUN_MODULE_DUAL_EVAL:-auto}"
AUTO_RESUME="${AUTO_RESUME:-1}"
SKIP_COMPLETED_EVAL="${SKIP_COMPLETED_EVAL:-1}"
ALLOW_UNVERIFIED_CLEAN_DATA="${ALLOW_UNVERIFIED_CLEAN_DATA:-0}"
DRY_RUN="${DRY_RUN:-0}"

JUDGE_MODEL="${JUDGE_MODEL:-qwen3.6}"
JUDGE_BASE_URL="${JUDGE_BASE_URL:-${OPENAI_BASE_URL:-http://127.0.0.1:8001/v1}}"
JUDGE_API_KEY="${JUDGE_API_KEY:-${OPENAI_API_KEY:-EMPTY}}"
JUDGE_WORKERS="${JUDGE_WORKERS:-4}"
JUDGE_TIMEOUT="${JUDGE_TIMEOUT:-180}"
JUDGE_RETRIES="${JUDGE_RETRIES:-3}"
JUDGE_LIMIT="${JUDGE_LIMIT:-}"
JUDGE_PROBE_TIMEOUT="${JUDGE_PROBE_TIMEOUT:-5}"

TRAIN_SCRIPT="$SCRIPT_DIR/run_factor1_cl_train_llava.sh"
EVAL_SCRIPT="$SCRIPT_DIR/run_factor1_cl_eval_llava.sh"
MODULE_TRAIN_SCRIPT="$SCRIPT_DIR/run_trainable_modules_llava.sh"
MODULE_EVAL_SCRIPT="$SCRIPT_DIR/run_trainable_modules_eval_llava.sh"
DUAL_EVAL_SCRIPT="$SCRIPT_DIR/run_dual_track_eval.sh"
MODULE_DUAL_EVAL_SCRIPT="$SCRIPT_DIR/run_trainable_modules_dual_eval.sh"

validate_binary_toggle() {
  local name="$1"
  local value="$2"
  if [[ "$value" != "0" && "$value" != "1" ]]; then
    echo "$name must be 0 or 1; got: $value" >&2
    exit 1
  fi
}

validate_judge_toggle() {
  local name="$1"
  local value="$2"
  if [[ "$value" != "0" && "$value" != "1" && "$value" != "auto" ]]; then
    echo "$name must be 0, 1, or auto; got: $value" >&2
    exit 1
  fi
}

module_modes_for_factor() {
  local factor="$1"
  if [[ -n "$MODULE_MODES" ]]; then
    printf '%s\n' "$MODULE_MODES"
    return 0
  fi

  case "$factor" in
    evidence_complexity)
      printf '%s\n' "$EVIDENCE_COMPLEXITY_MODULE_MODES"
      ;;
    skill_requirement)
      printf '%s\n' "$SKILL_REQUIREMENT_MODULE_MODES"
      ;;
    visual_substrate)
      printf '%s\n' "$VISUAL_SUBSTRATE_MODULE_MODES"
      ;;
    *)
      echo "No default module modes for factor=$factor; set MODULE_MODES." >&2
      return 1
      ;;
  esac
}

for toggle in RUN_FACTOR_TRAIN RUN_FACTOR_EVAL RUN_MODULE_TRAIN RUN_MODULE_EVAL; do
  validate_binary_toggle "$toggle" "${!toggle}"
done
validate_judge_toggle RUN_DUAL_EVAL "$RUN_DUAL_EVAL"
validate_judge_toggle RUN_MODULE_DUAL_EVAL "$RUN_MODULE_DUAL_EVAL"

required_paths=(
  "$DATA_ROOT" "$TRAIN_SCRIPT" "$EVAL_SCRIPT" "$MODULE_TRAIN_SCRIPT"
  "$MODULE_EVAL_SCRIPT" "$DUAL_EVAL_SCRIPT" "$MODULE_DUAL_EVAL_SCRIPT"
)
if [[ "$RUN_FACTOR_TRAIN" == "1" || "$RUN_FACTOR_EVAL" == "1" \
  || "$RUN_MODULE_TRAIN" == "1" || "$RUN_MODULE_EVAL" == "1" ]]; then
  required_paths+=("$IMAGE_FOLDER" "$MODEL_PATH")
fi
for required in "${required_paths[@]}"; do
  if [[ ! -e "$required" ]]; then
    echo "Missing required path: $required" >&2
    exit 1
  fi
done

"$PYTHON_BIN" - "$DATA_ROOT" "$FACTORS" "$MODULE_FACTORS" "$ALLOW_UNVERIFIED_CLEAN_DATA" <<'PYCODE'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
factors = set(sys.argv[2].split()) | set(sys.argv[3].split())
allow_unverified = sys.argv[4] == "1"
report_path = root / "textvqa_cleaning_report.json"
if not report_path.is_file():
    if not allow_unverified:
        raise SystemExit(f"Missing clean-data report: {report_path}")
    print(f"[warn] clean-data report not found: {report_path}")
else:
    report = json.loads(report_path.read_text(encoding="utf-8"))
    remaining = report.get("remaining_control_training_targets")
    missing = report.get("missing_answer_mappings")
    if remaining != 0 or missing != 0:
        raise SystemExit(
            "Clean-data validation failed: "
            f"remaining_control_training_targets={remaining}, "
            f"missing_answer_mappings={missing}"
        )
    print(
        "Clean TextVQA validation: "
        f"repaired={report.get('unique_training_targets_repaired')}, "
        f"remaining_controls={remaining}, missing_mappings={missing}"
    )

for factor in sorted(factors):
    factor_root = root / "splits" / factor
    order_path = factor_root / "transition_order.json"
    if not order_path.is_file():
        raise SystemExit(f"Missing transition order: {order_path}")
    order = json.loads(order_path.read_text(encoding="utf-8"))
    stages = order.get("trainable_order", [])
    if not stages:
        raise SystemExit(f"No trainable stages in {order_path}")
    for stage in stages:
        train_path = factor_root / "trainable" / "train" / stage / "train.json"
        eval_path = factor_root / "trainable" / "eval" / stage / "eval.json"
        if not train_path.is_file() or not eval_path.is_file():
            raise SystemExit(
                f"Incomplete factor split: factor={factor}, stage={stage}, "
                f"train={train_path.is_file()}, eval={eval_path.is_file()}"
            )
    print(f"Factor split: {factor}, stages={len(stages)}")
PYCODE

mkdir -p "$CHECKPOINT_BASE" "$RESULT_BASE" "$MODULE_CHECKPOINT_BASE" "$MODULE_RESULT_BASE"

cat <<EOF_SUMMARY
CoIN++ clean TextVQA end-to-end pipeline
  project root:              $PROJECT_ROOT
  data root:                 $DATA_ROOT
  factor checkpoints:        $CHECKPOINT_BASE
  factor results:            $RESULT_BASE
  module checkpoints:        $MODULE_CHECKPOINT_BASE
  module results:            $MODULE_RESULT_BASE
  factors:                   $FACTORS
  module factors:            $MODULE_FACTORS
  module mode override:       ${MODULE_MODES:-<per-factor defaults>}
  train GPUs:                $INCLUDE_GPUS
  eval GPUs:                 $EVAL_GPUS
  factor train/eval:         $RUN_FACTOR_TRAIN / $RUN_FACTOR_EVAL
  module train/eval:         $RUN_MODULE_TRAIN / $RUN_MODULE_EVAL
  factor/module dual eval:   $RUN_DUAL_EVAL / $RUN_MODULE_DUAL_EVAL
  auto resume:               $AUTO_RESUME
  dry run:                   $DRY_RUN
EOF_SUMMARY

read -r -a factor_list <<< "$FACTORS"
for idx in "${!factor_list[@]}"; do
  factor="${factor_list[$idx]}"
  checkpoint_root="$CHECKPOINT_BASE/$factor"
  factor_result_root="$RESULT_BASE/$factor"
  master_port=$((FACTOR_MASTER_PORT_BASE + idx))

  echo
  echo "================ factor $((idx + 1))/${#factor_list[@]}: $factor ================"
  if [[ "$RUN_FACTOR_TRAIN" == "1" ]]; then
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    IMAGE_FOLDER="$IMAGE_FOLDER" \
    MODEL_PATH="$MODEL_PATH" \
    OUTPUT_ROOT="$checkpoint_root" \
    LOG_DIR="$factor_result_root/logs" \
    INCLUDE_GPUS="$INCLUDE_GPUS" \
    MASTER_PORT="$master_port" \
    AUTO_RESUME="$AUTO_RESUME" \
    DRY_RUN="$DRY_RUN" \
      bash "$TRAIN_SCRIPT"
  fi

  if [[ "$RUN_FACTOR_EVAL" == "1" ]]; then
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    IMAGE_FOLDER="$IMAGE_FOLDER" \
    MODEL_BASE="$MODEL_BASE" \
    CHECKPOINT_ROOT="$checkpoint_root" \
    RESULT_ROOT="$factor_result_root/eval" \
    EVAL_GPUS="$EVAL_GPUS" \
    PARALLEL_STAGES="$EVAL_PARALLEL_STAGES" \
    LIMIT="$EVAL_LIMIT" \
    SKIP_COMPLETED="$SKIP_COMPLETED_EVAL" \
    DRY_RUN="$DRY_RUN" \
      bash "$EVAL_SCRIPT"
  fi
done

read -r -a module_factor_list <<< "$MODULE_FACTORS"
for idx in "${!module_factor_list[@]}"; do
  factor="${module_factor_list[$idx]}"
  factor_module_modes="$(module_modes_for_factor "$factor")"
  module_port=$((MODULE_MASTER_PORT_BASE + idx * 20))

  echo
  echo "================ trainable modules: $factor ================"
  echo "  modes: $factor_module_modes"
  if [[ "$RUN_MODULE_TRAIN" == "1" ]]; then
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    IMAGE_FOLDER="$IMAGE_FOLDER" \
    MODEL_PATH="$MODEL_PATH" \
    CHECKPOINT_BASE="$MODULE_CHECKPOINT_BASE" \
    RESULT_BASE="$MODULE_RESULT_BASE" \
    MODULE_MODES="$factor_module_modes" \
    INCLUDE_GPUS="$INCLUDE_GPUS" \
    MASTER_PORT="$module_port" \
    AUTO_RESUME="$AUTO_RESUME" \
    DRY_RUN="$DRY_RUN" \
      bash "$MODULE_TRAIN_SCRIPT"
  fi

  if [[ "$RUN_MODULE_EVAL" == "1" ]]; then
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    MODEL_BASE="$MODEL_BASE" \
    CHECKPOINT_BASE="$MODULE_CHECKPOINT_BASE" \
    RESULT_BASE="$MODULE_RESULT_BASE" \
    MODULE_MODES="$factor_module_modes" \
    EVAL_GPUS="$EVAL_GPUS" \
    PARALLEL_STAGES="$EVAL_PARALLEL_STAGES" \
    LIMIT="$EVAL_LIMIT" \
    SKIP_COMPLETED="$SKIP_COMPLETED_EVAL" \
    DRY_RUN="$DRY_RUN" \
      bash "$MODULE_EVAL_SCRIPT"
  fi
done

probe_judge() {
  local models_url="${JUDGE_BASE_URL%/}/models"
  "$PYTHON_BIN" - "$models_url" "$JUDGE_API_KEY" "$JUDGE_PROBE_TIMEOUT" <<'PYCODE' >/dev/null 2>&1
import sys
import urllib.request

url, api_key, timeout = sys.argv[1], sys.argv[2], float(sys.argv[3])
request = urllib.request.Request(url)
if api_key and api_key != "EMPTY":
    request.add_header("Authorization", f"Bearer {api_key}")
with urllib.request.urlopen(request, timeout=timeout) as response:
    if response.status >= 400:
        raise SystemExit(1)
PYCODE
}

judge_phase_enabled() {
  local setting="$1"
  local label="$2"

  if [[ "$setting" == "0" ]]; then
    echo "[skip] $label disabled"
    return 1
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "[skip] $label during DRY_RUN"
    return 1
  fi
  if probe_judge; then
    return 0
  fi
  if [[ "$setting" == "1" ]]; then
    echo "$label requested, but Judge service is unavailable: $JUDGE_BASE_URL" >&2
    return 2
  fi
  echo "[skip] $label: Judge service unavailable at $JUDGE_BASE_URL"
  return 1
}

if judge_phase_enabled "$RUN_DUAL_EVAL" "factor dual evaluation"; then
  safe_judge_model="${JUDGE_MODEL//\//_}"
  for factor in "${factor_list[@]}"; do
    echo
    echo "================ dual evaluation: $factor ================"
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    RESULT_ROOTS="$RESULT_BASE/$factor/eval" \
    JUDGE_MODEL="$JUDGE_MODEL" \
    JUDGE_BASE_URL="$JUDGE_BASE_URL" \
    JUDGE_API_KEY="$JUDGE_API_KEY" \
    JUDGE_WORKERS="$JUDGE_WORKERS" \
    JUDGE_TIMEOUT="$JUDGE_TIMEOUT" \
    JUDGE_RETRIES="$JUDGE_RETRIES" \
    JUDGE_CACHE="$RESULT_BASE/judge_cache/${factor}_${safe_judge_model}_all.jsonl" \
    LIMIT="$JUDGE_LIMIT" \
      bash "$DUAL_EVAL_SCRIPT"
  done
else
  judge_status=$?
  if [[ "$judge_status" == "2" ]]; then
    exit 1
  fi
fi

if judge_phase_enabled "$RUN_MODULE_DUAL_EVAL" "module dual evaluation"; then
  safe_judge_model="${JUDGE_MODEL//\//_}"
  for factor in "${module_factor_list[@]}"; do
    factor_module_modes="$(module_modes_for_factor "$factor")"
    echo
    echo "================ module dual evaluation: $factor ================"
    FACTOR="$factor" \
    PROJECT_ROOT="$PROJECT_ROOT" \
    PYTHON_BIN="$PYTHON_BIN" \
    DATA_ROOT="$DATA_ROOT" \
    RESULT_BASE="$MODULE_RESULT_BASE/$factor" \
    MODULE_MODES="$factor_module_modes" \
    JUDGE_MODEL="$JUDGE_MODEL" \
    JUDGE_BASE_URL="$JUDGE_BASE_URL" \
    JUDGE_API_KEY="$JUDGE_API_KEY" \
    JUDGE_WORKERS="$JUDGE_WORKERS" \
    JUDGE_TIMEOUT="$JUDGE_TIMEOUT" \
    JUDGE_RETRIES="$JUDGE_RETRIES" \
    JUDGE_CACHE="$MODULE_RESULT_BASE/judge_cache/${factor}_${safe_judge_model}_all.jsonl" \
      bash "$MODULE_DUAL_EVAL_SCRIPT"
  done
else
  judge_status=$?
  if [[ "$judge_status" == "2" ]]; then
    exit 1
  fi
fi

cat <<EOF_DONE

All requested CoIN++ clean-data phases finished.
  factor summaries: $RESULT_BASE/<factor>/eval/summary/
  factor dual:      $RESULT_BASE/<factor>/eval/summary_dual/
  module summaries: $MODULE_RESULT_BASE/<factor>/<mode>/eval/summary/
  module dual:      $MODULE_RESULT_BASE/<factor>/comparison_dual/
EOF_DONE
