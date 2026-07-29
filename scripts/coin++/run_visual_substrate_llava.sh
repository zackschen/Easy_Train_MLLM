#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTOR="visual_substrate" MASTER_PORT="${MASTER_PORT:-29652}" bash "$SCRIPT_DIR/run_factor1_cl_train_llava.sh"
