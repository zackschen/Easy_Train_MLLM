#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRACKS=(visual_substrate skill_requirement evidence_complexity)

if [[ -n "${TRACKS_OVERRIDE:-}" ]]; then
  read -r -a TRACKS <<< "$TRACKS_OVERRIDE"
fi

base_port="${MASTER_PORT_BASE:-29660}"
for idx in "${!TRACKS[@]}"; do
  factor="${TRACKS[$idx]}"
  port=$((base_port + idx))
  echo
  echo "================ Running CoIN++ factor track: $factor ================"
  FACTOR="$factor" MASTER_PORT="${MASTER_PORT:-$port}" bash "$SCRIPT_DIR/run_factor1_cl_train_llava.sh"
done
