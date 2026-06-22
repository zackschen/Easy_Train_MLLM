#!/usr/bin/env bash
set -euo pipefail

# OpenAI-compatible vLLM server for vLLM-supported Qwen checkpoints.
#
# Examples:
#   bash scripts/Qwen_server/serve_vllm_qwen.sh
#   CUDA_VISIBLE_DEVICES=0,1,2,3 TENSOR_PARALLEL_SIZE=4 bash scripts/Qwen_server/serve_vllm_qwen.sh
#   PORT=8001 VLLM_API_KEY=sk-local MAX_MODEL_LEN=65536 bash scripts/Qwen_server/serve_vllm_qwen.sh
#
# Extra vLLM arguments can be appended after "--":
#   bash scripts/Qwen_server/serve_vllm_qwen.sh -- --max-num-seqs 8

MODEL_PATH="${MODEL_PATH:-./data/coin/checkpoints/Qwen3.6-35B-A3B}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen3.6}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8001}"
VLLM_API_KEY="${VLLM_API_KEY:-EMPTY}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-32768}"
DTYPE="${DTYPE:-half}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.90}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3}"
VLLM_USE_V1="${VLLM_USE_V1:-0}"
MIN_COMPUTE_CAPABILITY="${MIN_COMPUTE_CAPABILITY:-7.0}"
ALLOW_UNSUPPORTED_GPU="${ALLOW_UNSUPPORTED_GPU:-0}"

count_visible_gpus() {
  local ids="$1"
  if [[ -z "$ids" || "$ids" == "all" ]]; then
    echo 1
    return
  fi
  local commas="${ids//[^,]/}"
  echo $((${#commas} + 1))
}

TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-$(count_visible_gpus "$CUDA_VISIBLE_DEVICES")}"

if [[ "${1:-}" == "--" ]]; then
  shift
fi

if [[ ! -d "$MODEL_PATH" ]]; then
  echo "Model path does not exist: $MODEL_PATH" >&2
  exit 1
fi

if [[ ! -f "$MODEL_PATH/config.json" ]]; then
  echo "config.json not found under model path: $MODEL_PATH" >&2
  exit 1
fi

if [[ "$ALLOW_UNSUPPORTED_GPU" != "1" ]] && command -v nvidia-smi >/dev/null 2>&1; then
  unsupported_gpus="$(nvidia-smi --query-gpu=index,name,compute_cap --format=csv,noheader 2>/dev/null | awk -F',' -v min_cap="$MIN_COMPUTE_CAPABILITY" '
    {
      gpu_index = $1
      gpu_name = $2
      gpu_cap = $3
      gsub(/^ +| +$/, "", gpu_index)
      gsub(/^ +| +$/, "", gpu_name)
      gsub(/^ +| +$/, "", gpu_cap)
      if ((gpu_cap + 0) < (min_cap + 0)) {
        print gpu_index ", " gpu_name ", " gpu_cap
      }
    }'
  )"

  if [[ -n "$unsupported_gpus" ]]; then
    cat >&2 <<EOF
Unsupported GPU architecture detected for this vLLM stack.

Detected GPUs below the minimum compute capability of $MIN_COMPUTE_CAPABILITY:
$unsupported_gpus

This environment expects an sm70-capable PyTorch/vLLM stack.
Set ALLOW_UNSUPPORTED_GPU=1 to bypass this check at your own risk.
EOF
    exit 1
  fi
fi

if ! command -v vllm >/dev/null 2>&1; then
  echo "vLLM is not installed or not on PATH. Install it in your serving environment first, for example: pip install vllm" >&2
  exit 1
fi

export CUDA_VISIBLE_DEVICES
export VLLM_USE_V1

if [[ -n "${CONDA_PREFIX:-}" ]]; then
  shopt -s nullglob
  nvidia_lib_dirs=(
    "$CONDA_PREFIX"/lib/python*/site-packages/nvidia/cu13/lib
    "$CONDA_PREFIX"/lib/python*/site-packages/nvidia/cu13/cccl/lib
    "$CONDA_PREFIX"/lib/python*/site-packages/nvidia/*/lib
  )
  shopt -u nullglob

  if ((${#nvidia_lib_dirs[@]})); then
    nvidia_ld_path="$(IFS=:; echo "${nvidia_lib_dirs[*]}")"
    export LD_LIBRARY_PATH="${nvidia_ld_path}${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
  fi
fi

echo "Starting vLLM OpenAI-compatible server"
echo "  model path:          $MODEL_PATH"
echo "  served model name:   $SERVED_MODEL_NAME"
echo "  endpoint:            http://${HOST}:${PORT}/v1"
echo "  CUDA_VISIBLE_DEVICES:$CUDA_VISIBLE_DEVICES"
echo "  tensor parallel:     $TENSOR_PARALLEL_SIZE"
echo "  max model len:       $MAX_MODEL_LEN"
echo "  VLLM_USE_V1:         $VLLM_USE_V1"

exec vllm serve "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL_NAME" \
  --host "$HOST" \
  --port "$PORT" \
  --api-key "$VLLM_API_KEY" \
  --trust-remote-code \
  --dtype "$DTYPE" \
  --max-model-len "$MAX_MODEL_LEN" \
  --generation-config "$MODEL_PATH" \
  --gpu-memory-utilization "$GPU_MEMORY_UTILIZATION" \
  --tensor-parallel-size "$TENSOR_PARALLEL_SIZE" \
  "$@"
