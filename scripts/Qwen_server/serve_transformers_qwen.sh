#!/usr/bin/env bash
set -euo pipefail

MODEL_PATH="${MODEL_PATH:-/mnt/hdd1/chencheng/cl_dataset/coin/checkpoints/Qwen3.6}"
SERVED_MODEL_NAME="${SERVED_MODEL_NAME:-qwen3.6}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
VLLM_API_KEY="${VLLM_API_KEY:-EMPTY}"
DTYPE="${DTYPE:-float16}"
CUDA_VISIBLE_DEVICES="${CUDA_VISIBLE_DEVICES:-0,1,2,3,4,5,6,7}"
DEVICE_MAP="${DEVICE_MAP:-auto}"
MAX_MEMORY="${MAX_MEMORY:-30GiB}"
CPU_MEMORY="${CPU_MEMORY:-128GiB}"

export CUDA_VISIBLE_DEVICES
export VLLM_API_KEY

echo "Starting Transformers OpenAI-compatible server"
echo "  model path:          $MODEL_PATH"
echo "  served model name:   $SERVED_MODEL_NAME"
echo "  endpoint:            http://${HOST}:${PORT}/v1"
echo "  CUDA_VISIBLE_DEVICES:$CUDA_VISIBLE_DEVICES"
echo "  dtype:               $DTYPE"
echo "  device map:          $DEVICE_MAP"
echo "  max memory per GPU:  $MAX_MEMORY"

exec python scripts/Qwen_server/serve_transformers_qwen_api.py \
  --model-path "$MODEL_PATH" \
  --served-model-name "$SERVED_MODEL_NAME" \
  --host "$HOST" \
  --port "$PORT" \
  --api-key "$VLLM_API_KEY" \
  --dtype "$DTYPE" \
  --device-map "$DEVICE_MAP" \
  --max-memory "$MAX_MEMORY" \
  --cpu-memory "$CPU_MEMORY"
