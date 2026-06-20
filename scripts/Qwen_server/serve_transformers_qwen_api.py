#!/usr/bin/env python3
"""OpenAI-compatible API server backed by Transformers.

This is a fallback for Qwen3.5 checkpoints that are not supported by the
V100-compatible vLLM stack.
"""

from __future__ import annotations

import argparse
import json
import os
import threading
import time
import uuid
from typing import Any

import torch
import uvicorn
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from transformers import (
    AutoTokenizer,
    Qwen3_5ForConditionalGeneration,
    TextIteratorStreamer,
)


DEFAULT_MODEL_PATH = "/mnt/hdd1/chencheng/cl_dataset/coin/checkpoints/Qwen3.6"

app = FastAPI(title="Qwen3.6 Transformers API", version="0.1.0")
state: dict[str, Any] = {}
generation_lock = threading.Lock()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve Qwen3.6 with Transformers.")
    parser.add_argument("--model-path", default=os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH))
    parser.add_argument("--served-model-name", default=os.getenv("SERVED_MODEL_NAME", "qwen3.6"))
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", os.getenv("VLLM_API_KEY", "EMPTY")))
    parser.add_argument("--dtype", default=os.getenv("DTYPE", "float16"), choices=["float16", "bfloat16", "float32"])
    parser.add_argument("--device-map", default=os.getenv("DEVICE_MAP", "auto"))
    parser.add_argument("--max-memory", default=os.getenv("MAX_MEMORY", "30GiB"))
    parser.add_argument("--cpu-memory", default=os.getenv("CPU_MEMORY", "128GiB"))
    return parser.parse_args()


def dtype_from_name(name: str) -> torch.dtype:
    if name == "float16":
        return torch.float16
    if name == "bfloat16":
        return torch.bfloat16
    return torch.float32


def visible_gpu_count() -> int:
    if not torch.cuda.is_available():
        return 0
    visible = os.getenv("CUDA_VISIBLE_DEVICES")
    if visible and visible != "all":
        return len([item for item in visible.split(",") if item.strip()])
    return torch.cuda.device_count()


def build_max_memory(per_gpu: str, cpu_memory: str) -> dict[Any, str]:
    max_memory: dict[Any, str] = {}
    for idx in range(visible_gpu_count()):
        max_memory[idx] = per_gpu
    max_memory["cpu"] = cpu_memory
    return max_memory


def verify_api_key(authorization: str | None) -> None:
    api_key = state["api_key"]
    if api_key in {"", "EMPTY"}:
        return
    expected = f"Bearer {api_key}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


def normalize_messages(messages: list[dict[str, Any]]) -> list[dict[str, str]]:
    normalized = []
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(str(item.get("text", "")))
            content = "\n".join(text_parts)
        normalized.append({"role": str(message.get("role", "user")), "content": str(content)})
    return normalized


def build_prompt(payload: dict[str, Any]) -> str:
    tokenizer = state["tokenizer"]
    messages = normalize_messages(payload.get("messages", []))
    if not messages:
        raise HTTPException(status_code=400, detail="messages must not be empty")
    template_kwargs = payload.get("chat_template_kwargs") or {}
    return tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
        **template_kwargs,
    )


def generation_kwargs(payload: dict[str, Any]) -> dict[str, Any]:
    temperature = float(payload.get("temperature", 0.7))
    top_p = float(payload.get("top_p", 0.8))
    top_k = int(payload.get("top_k", 20))
    max_new_tokens = int(payload.get("max_tokens", payload.get("max_new_tokens", 1024)))
    kwargs: dict[str, Any] = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature > 0,
        "eos_token_id": state["tokenizer"].eos_token_id,
        "pad_token_id": state["tokenizer"].pad_token_id or state["tokenizer"].eos_token_id,
    }
    if temperature > 0:
        kwargs["temperature"] = temperature
        kwargs["top_p"] = top_p
        kwargs["top_k"] = top_k
    return kwargs


def encode_prompt(prompt: str) -> dict[str, torch.Tensor]:
    tokenizer = state["tokenizer"]
    inputs = tokenizer(prompt, return_tensors="pt")
    device = next(state["model"].parameters()).device
    return {key: value.to(device) for key, value in inputs.items()}


def completion_payload(text: str, payload: dict[str, Any], prompt_tokens: int, completion_tokens: int) -> dict[str, Any]:
    created = int(time.time())
    return {
        "id": f"chatcmpl-{uuid.uuid4().hex}",
        "object": "chat.completion",
        "created": created,
        "model": state["served_model_name"],
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": text},
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
        },
    }


@app.get("/v1/models")
def list_models(authorization: str | None = Header(default=None)) -> dict[str, Any]:
    verify_api_key(authorization)
    return {
        "object": "list",
        "data": [
            {
                "id": state["served_model_name"],
                "object": "model",
                "created": int(time.time()),
                "owned_by": "local",
            }
        ],
    }


@app.post("/v1/chat/completions")
def chat_completions(payload: dict[str, Any], authorization: str | None = Header(default=None)) -> Any:
    verify_api_key(authorization)
    prompt = build_prompt(payload)
    inputs = encode_prompt(prompt)
    gen_kwargs = generation_kwargs(payload)

    if payload.get("stream"):
        return StreamingResponse(
            stream_completion(inputs, gen_kwargs),
            media_type="text/event-stream",
        )

    with generation_lock, torch.inference_mode():
        outputs = state["model"].generate(**inputs, **gen_kwargs)
    prompt_len = inputs["input_ids"].shape[-1]
    generated = outputs[0, prompt_len:]
    text = state["tokenizer"].decode(generated, skip_special_tokens=True)
    return JSONResponse(completion_payload(text, payload, prompt_len, generated.shape[-1]))


def stream_completion(inputs: dict[str, torch.Tensor], gen_kwargs: dict[str, Any]):
    streamer = TextIteratorStreamer(
        state["tokenizer"],
        skip_prompt=True,
        skip_special_tokens=True,
    )
    thread = threading.Thread(
        target=generate_with_streamer,
        kwargs={"inputs": inputs, "gen_kwargs": gen_kwargs, "streamer": streamer},
        daemon=True,
    )
    thread.start()
    request_id = f"chatcmpl-{uuid.uuid4().hex}"
    for text in streamer:
        chunk = {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": state["served_model_name"],
            "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}],
        }
        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
    done = {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": state["served_model_name"],
        "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
    }
    yield f"data: {json.dumps(done, ensure_ascii=False)}\n\n"
    yield "data: [DONE]\n\n"


def generate_with_streamer(
    inputs: dict[str, torch.Tensor],
    gen_kwargs: dict[str, Any],
    streamer: TextIteratorStreamer,
) -> None:
    with generation_lock, torch.inference_mode():
        state["model"].generate(**inputs, streamer=streamer, **gen_kwargs)


def load_model(args: argparse.Namespace) -> None:
    dtype = dtype_from_name(args.dtype)
    print("Loading tokenizer", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_path, trust_remote_code=True)
    print("Loading model", flush=True)
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        args.model_path,
        torch_dtype=dtype,
        device_map=args.device_map,
        max_memory=build_max_memory(args.max_memory, args.cpu_memory),
        trust_remote_code=True,
    )
    model.eval()
    state.update(
        {
            "tokenizer": tokenizer,
            "model": model,
            "served_model_name": args.served_model_name,
            "api_key": args.api_key,
        }
    )
    print("Model loaded", flush=True)


def main() -> None:
    args = parse_args()
    load_model(args)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
