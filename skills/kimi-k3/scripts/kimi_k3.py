#!/usr/bin/env python3
"""Send a prompt to Kimi K3 (Moonshot API) and print the reply.

Kimi K3 speaks the OpenAI chat-completions protocol, so this talks to
`https://api.moonshot.ai/v1/chat/completions` with nothing but the Python
standard library — no `openai` package, no `jq`, no `curl` escaping headaches.

Auth: set MOONSHOT_API_KEY in the environment (a funded top-up is required to
unlock the model — see the quickstart).

Examples:
  kimi_k3.py "Explain lock-free queues in 3 bullets"
  echo "prompt from stdin" | kimi_k3.py
  kimi_k3.py --system "You are a terse code reviewer" --effort high "review: ..."
  kimi_k3.py --image ./diagram.png "What does this architecture do?"
  kimi_k3.py --show-reasoning "Is 9.11 bigger than 9.9?"
  kimi_k3.py --json "..."         # raw API response for scripting

Exit codes: 0 ok · 1 request/API error · 2 usage/config error.
"""
import argparse
import base64
import json
import mimetypes
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import NoReturn

DEFAULT_MODEL = "kimi-k3"
DEFAULT_BASE_URL = "https://api.moonshot.ai/v1"


def die(msg, code=2) -> NoReturn:
    print(f"kimi_k3: {msg}", file=sys.stderr)
    sys.exit(code)


def make_ssl_context():
    """Verify TLS using certifi's CA bundle when the interpreter has no system
    trust store — the common macOS python.org case (`cafile` is None until
    'Install Certificates.command' is run). Falls back to the default context."""
    ctx = ssl.create_default_context()
    if ssl.get_default_verify_paths().cafile is None:
        try:
            import certifi
            ctx.load_verify_locations(cafile=certifi.where())
        except Exception:
            pass
    return ctx


def image_part(ref):
    """Build an OpenAI-style image_url part. A local path is inlined as a
    base64 data URL; anything that looks like a URL is passed through."""
    if ref.startswith(("http://", "https://", "data:")):
        return {"type": "image_url", "image_url": {"url": ref}}
    if not os.path.isfile(ref):
        die(f"image not found: {ref}")
    mime = mimetypes.guess_type(ref)[0] or "image/png"
    with open(ref, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def build_messages(prompt, system, images):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    if images:
        content = [{"type": "text", "text": prompt}] + [image_part(i) for i in images]
    else:
        content = prompt
    messages.append({"role": "user", "content": content})
    return messages


def main():
    p = argparse.ArgumentParser(
        prog="kimi_k3.py",
        description="Send a prompt to Kimi K3 (Moonshot API) and print the reply.",
    )
    p.add_argument("prompt", nargs="?", help="the prompt (or pipe it via stdin)")
    p.add_argument("--system", help="system prompt")
    p.add_argument("--effort", choices=["low", "high", "max"],
                   help="reasoning_effort; omit to use the model default (max)")
    p.add_argument("--image", action="append", default=[], metavar="PATH|URL",
                   help="attach an image (repeatable); local path is base64-inlined")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"default: {DEFAULT_MODEL}")
    p.add_argument("--temperature", type=float, help="sampling temperature")
    p.add_argument("--max-tokens", type=int, help="max output tokens")
    p.add_argument("--show-reasoning", action="store_true",
                   help="also print the model's thinking/reasoning trace")
    p.add_argument("--json", action="store_true",
                   help="print the raw JSON response instead of just the text")
    p.add_argument("--base-url", default=os.environ.get("MOONSHOT_BASE_URL", DEFAULT_BASE_URL))
    p.add_argument("--timeout", type=float, default=300.0, help="request timeout (s)")
    args = p.parse_args()

    prompt = args.prompt
    if prompt is None and not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    if not prompt:
        die("no prompt given (pass an argument or pipe it via stdin)")

    api_key = os.environ.get("MOONSHOT_API_KEY")
    if not api_key:
        die("MOONSHOT_API_KEY is not set. Get a key at https://platform.moonshot.ai "
            "(a min $1 top-up unlocks the model), then: export MOONSHOT_API_KEY=sk-...")

    payload = {
        "model": args.model,
        "messages": build_messages(prompt, args.system, args.image),
    }
    if args.effort:
        payload["reasoning_effort"] = args.effort
    if args.temperature is not None:
        payload["temperature"] = args.temperature
    if args.max_tokens is not None:
        payload["max_tokens"] = args.max_tokens

    url = args.base_url.rstrip("/") + "/chat/completions"
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=args.timeout, context=make_ssl_context()) as resp:
            body = resp.read().decode()
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        try:
            detail = json.loads(detail).get("error", {}).get("message", detail)
        except (ValueError, AttributeError):
            pass
        die(f"API error {e.code}: {detail}", code=1)
    except urllib.error.URLError as e:
        die(f"network error: {e.reason}", code=1)

    if args.json:
        print(body)
        return

    try:
        data = json.loads(body)
        msg = data["choices"][0]["message"]
    except (ValueError, KeyError, IndexError):
        die(f"unexpected response shape:\n{body}", code=1)

    if args.show_reasoning:
        # Moonshot returns thinking in `reasoning_content`; tolerate `reasoning` too.
        reasoning = msg.get("reasoning_content") or msg.get("reasoning")
        if reasoning:
            print("--- reasoning ---")
            print(reasoning.strip())
            print("--- answer ---")

    print((msg.get("content") or "").strip())

    usage = data.get("usage")
    if usage:
        print(
            f"\n[tokens: {usage.get('prompt_tokens', '?')} in / "
            f"{usage.get('completion_tokens', '?')} out]",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
