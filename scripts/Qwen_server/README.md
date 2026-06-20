# Qwen3.6 API Server

## Environment

```bash
conda activate coin
```

The `coin` environment is located at:

```text
/mnt/hdd1/chencheng/conda_envs/coin
```

Installed runtime stack:

- vLLM 0.8.5
- PyTorch 2.6.0+cu124
- OpenAI Python client 2.41.1
- Transformers 5.12.1
- Hugging Face Accelerate 1.14.0
- qwen-vl-utils 0.0.14

## Current Checkpoint Limitation

The local checkpoint is not a plain text-only Qwen CausalLM. Its `config.json`
declares:

```text
architectures = ["Qwen3_5ForConditionalGeneration"]
model_type = "qwen3_5"
language_model_only = false
```

It also includes a vision tower and hybrid `linear_attention` text layers.
The V100-compatible vLLM stack can import the config, but vLLM 0.8.5 cannot
serve this architecture:

```text
Qwen3_5ForConditionalGeneration has no vLLM implementation and the Transformers implementation is not compatible with vLLM.
```

Newer vLLM/PyTorch stacks are more likely to support newer Qwen architectures,
but they require GPUs newer than the Tesla V100S in this machine.

## Start Transformers API Server

Use this server for the current Qwen3.6 checkpoint on V100S:

```bash
conda activate coin
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 bash scripts/Qwen_server/serve_transformers_qwen.sh
```

The endpoint is OpenAI-compatible:

```text
http://127.0.0.1:8000/v1
```

Useful overrides:

```bash
PORT=8001 VLLM_API_KEY=sk-local bash scripts/Qwen_server/serve_transformers_qwen.sh
MAX_MEMORY=28GiB CPU_MEMORY=256GiB bash scripts/Qwen_server/serve_transformers_qwen.sh
```

This fallback uses Transformers + Accelerate instead of vLLM. It is slower than
vLLM, but it is the practical option for this checkpoint on V100S.

## vLLM Script

```bash
conda activate coin
bash scripts/Qwen_server/serve_vllm_qwen.sh
```

The default dtype is `half` because Tesla V100/V100S GPUs do not support BF16.
This environment is pinned to an older V100-compatible runtime. The startup
guard accepts compute capability 7.0 or newer by default. The script also sets
`VLLM_USE_V1=0` because V100S cannot use the newer vLLM V1 engine.

Keep this script for plain CausalLM checkpoints that vLLM 0.8.5 supports. It
does not successfully serve the current `Qwen3_5ForConditionalGeneration`
checkpoint.

If you run on A100/H100 or newer GPUs, you can switch back to BF16:

```bash
DTYPE=bfloat16 bash scripts/Qwen_server/serve_vllm_qwen.sh
```

Common overrides:

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 TENSOR_PARALLEL_SIZE=4 bash scripts/Qwen_server/serve_vllm_qwen.sh
CUDA_VISIBLE_DEVICES=0,1,2,3,4,5,6,7 TENSOR_PARALLEL_SIZE=8 bash scripts/Qwen_server/serve_vllm_qwen.sh
PORT=8001 VLLM_API_KEY=sk-local MAX_MODEL_LEN=8192 bash scripts/Qwen_server/serve_vllm_qwen.sh
```

This Qwen3.6 checkpoint is large enough that one 32GB V100S is not sufficient.
Use 8 GPUs for the current checkpoint, or lower memory settings if you need to
fit a smaller allocation.

The OpenAI-compatible API endpoint is:

```text
http://127.0.0.1:8000/v1
```

## Test API

```bash
conda activate coin
python scripts/Qwen_server/call_vllm_qwen.py --prompt "你好，请介绍一下你自己。"
```

Streaming:

```bash
python scripts/Qwen_server/call_vllm_qwen.py --stream --prompt "写一段简短的排序算法解释。"
```
