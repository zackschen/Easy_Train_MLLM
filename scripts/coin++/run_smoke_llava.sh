#!/usr/bin/env bash
set -euo pipefail

# Two-stage, tiny-step validation run. It validates model/data plumbing without
# launching the full 10k-per-stage experiment.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTOR="${FACTOR:-evidence_complexity}"
INCLUDE_GPUS="${INCLUDE_GPUS:-localhost:0}"
MAX_STEPS="${MAX_STEPS:-2}"
PER_DEVICE_BATCH="${PER_DEVICE_BATCH:-1}"
GRAD_ACCUM="${GRAD_ACCUM:-1}"
STOP_AFTER_STAGE="${STOP_AFTER_STAGE:-2}"
OUTPUT_ROOT="${OUTPUT_ROOT:-$PWD/checkpoints/LLaVA/Instruction/CoIN++_Smoke_textvqa_clean/$FACTOR}"
LOG_DIR="${LOG_DIR:-$PWD/results/coin++_smoke_textvqa_clean/$FACTOR/logs}"

FACTOR="$FACTOR" INCLUDE_GPUS="$INCLUDE_GPUS" MAX_STEPS="$MAX_STEPS" \
PER_DEVICE_BATCH="$PER_DEVICE_BATCH" GRAD_ACCUM="$GRAD_ACCUM" \
STOP_AFTER_STAGE="$STOP_AFTER_STAGE" OUTPUT_ROOT="$OUTPUT_ROOT" LOG_DIR="$LOG_DIR" \
bash "$SCRIPT_DIR/run_factor1_cl_train_llava.sh"
