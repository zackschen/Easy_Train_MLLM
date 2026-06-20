#!/usr/bin/env python3
import argparse
import json
import os
import sys
import urllib.error
import urllib.request


def parse_args():
    parser = argparse.ArgumentParser(
        description="Call a local vLLM OpenAI-compatible Qwen server."
    )
    parser.add_argument("--base-url", default=os.getenv("OPENAI_BASE_URL", "http://127.0.0.1:8000/v1"))
    parser.add_argument("--api-key", default=os.getenv("OPENAI_API_KEY", os.getenv("VLLM_API_KEY", "EMPTY")))
    parser.add_argument("--model", default=os.getenv("SERVED_MODEL_NAME", "qwen3.6"))
    parser.add_argument("--prompt", default="你好，请用一句话介绍你自己。")
    parser.add_argument("--system", default="")
    parser.add_argument("--max-tokens", type=int, default=1024)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.8)
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--presence-penalty", type=float, default=1.5)
    parser.add_argument("--enable-thinking", action="store_true")
    parser.add_argument("--preserve-thinking", action="store_true")
    parser.add_argument("--stream", action="store_true")
    parser.add_argument("--timeout", type=int, default=300)
    return parser.parse_args()


def build_messages(args):
    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})
    return messages


def request_chat(args):
    url = args.base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": args.model,
        "messages": build_messages(args),
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "top_p": args.top_p,
        "presence_penalty": args.presence_penalty,
        "top_k": args.top_k,
        "chat_template_kwargs": {
            "enable_thinking": args.enable_thinking,
            "preserve_thinking": args.preserve_thinking,
        },
        "stream": args.stream,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {args.api_key}",
        },
        method="POST",
    )
    return urllib.request.urlopen(req, timeout=args.timeout)


def print_stream(resp):
    for raw_line in resp:
        line = raw_line.decode("utf-8", errors="replace").strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[len("data:") :].strip()
        if data == "[DONE]":
            break
        chunk = json.loads(data)
        delta = chunk["choices"][0].get("delta", {})
        text = delta.get("content")
        if text:
            print(text, end="", flush=True)
    print()


def print_response(resp):
    data = json.load(resp)
    print(data["choices"][0]["message"]["content"])


def main():
    args = parse_args()
    try:
        with request_chat(args) as resp:
            if args.stream:
                print_stream(resp)
            else:
                print_response(resp)
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        print(f"HTTP {exc.code}: {error_body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Request failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
