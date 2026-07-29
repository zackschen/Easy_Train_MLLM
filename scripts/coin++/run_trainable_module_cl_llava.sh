#!/usr/bin/env bash
set -euo pipefail

# Train one module regime over one fixed CoIN++ continual sequence.
#
# Examples:
#   MODULE_MODE=vision_only bash scripts/coin++/run_trainable_module_cl_llava.sh
#   MODULE_MODE=projector_only FACTOR=skill_requirement bash scripts/coin++/run_trainable_module_cl_llava.sh
#   MODULE_MODE=vision_only AUTO_RESUME=0 bash scripts/coin++/run_trainable_module_cl_llava.sh
#   MODULE_MODE=llm_only MAX_STEPS=10 DRY_RUN=1 bash scripts/coin++/run_trainable_module_cl_llava.sh

PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
MODULE_MODE="${MODULE_MODE:-llm_only}"
FACTOR="${FACTOR:-visual_substrate}"

case "$MODULE_MODE" in
  vision_only)
    LR="${LR:-2e-6}"
    VISION_TOWER_LR="${VISION_TOWER_LR:-$LR}"
    PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-2}"
    GRAD_ACCUM="${GRAD_ACCUM:-16}"
    ;;
  projector_only)
    LR="${LR:-2e-5}"
    MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-$LR}"
    PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-4}"
    GRAD_ACCUM="${GRAD_ACCUM:-8}"
    ;;
  llm_only)
    LR="${LR:-2e-4}"
    PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-4}"
    GRAD_ACCUM="${GRAD_ACCUM:-8}"
    ;;
  llm_projector)
    LR="${LR:-2e-4}"
    MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-2e-5}"
    PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-4}"
    GRAD_ACCUM="${GRAD_ACCUM:-8}"
    ;;
  all_modules)
    LR="${LR:-2e-4}"
    MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-2e-5}"
    VISION_TOWER_LR="${VISION_TOWER_LR:-2e-6}"
    PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-2}"
    GRAD_ACCUM="${GRAD_ACCUM:-16}"
    ;;
  *)
    echo "Unknown MODULE_MODE=$MODULE_MODE" >&2
    echo "Choose: vision_only, projector_only, llm_only, llm_projector, all_modules" >&2
    exit 1
    ;;
esac

OUTPUT_ROOT="${OUTPUT_ROOT:-$PROJECT_ROOT/checkpoints/LLaVA/Instruction/CoIN++_TrainableModules/$FACTOR/$MODULE_MODE}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/results/coin++_trainable_modules/$FACTOR/$MODULE_MODE/logs}"

export PROJECT_ROOT FACTOR OUTPUT_ROOT LOG_DIR
export TRAINABLE_MODULES="$MODULE_MODE"
export LR PER_DEVICE_BATCH GRAD_ACCUM
export MM_PROJECTOR_LR="${MM_PROJECTOR_LR:-2e-5}"
export VISION_TOWER_LR="${VISION_TOWER_LR:-}"

echo "CoIN++ trainable-module experiment"
echo "  module mode:       $MODULE_MODE"
echo "  fixed data factor: $FACTOR"
echo "  output root:       $OUTPUT_ROOT"
echo "  base/projector/vision lr: $LR / $MM_PROJECTOR_LR / ${VISION_TOWER_LR:-<unused>}"
echo "  batch/accum:       $PER_DEVICE_BATCH / $GRAD_ACCUM"

exec bash "$PROJECT_ROOT/scripts/coin++/run_factor1_cl_train_llava.sh"
