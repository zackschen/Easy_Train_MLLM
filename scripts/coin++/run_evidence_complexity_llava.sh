#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FACTOR="evidence_complexity" MASTER_PORT="${MASTER_PORT:-29654}" bash "$SCRIPT_DIR/run_factor1_cl_train_llava.sh"
