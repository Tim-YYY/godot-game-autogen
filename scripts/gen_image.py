#!/usr/bin/env python3
"""
Universal image-generation client for game asset production.

Backends (auto-detected, or forced via GAME_IMG_BACKEND env):
  - "openai"       : OpenAI-compatible POST /images/generations
                     (b64_json or url response). Works with OpenAI, SiliconFlow,
                     Together, and most vendors that expose an OpenAI-compatible API.
  - "openai-edit"  : OpenAI-compatible POST /images/edits (image-to-image, multipart).
                     Use when a reference image is supplied.

Configuration is read from environment variables first, then from
~/.workbuddy/game-assets/config.json (JSON keys override env).

Env vars:
  GAME_IMG_API_BASE   base URL (default https://api.openai.com/v1)
  GAME_IMG_API_KEY    API key
  GAME_IMG_MODEL      model name (default gpt-image-1)
  GAME_IMG_SIZE       default size (default 1024x1024)

Usage:
  python gen_image.py --prompt "..." --size 1024x1024 --out assets/sprites/x.png
  python gen_image.py --prompt "..." --ref hero.png --out assets/sprites/hero_v2.png
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

CONFIG_PATH = os.path.expanduser("~/.workbuddy/game-assets/config.json")


def load_config():
    cfg = {
        "api_base": os.environ.get("GAME_IMG_API_BASE", "https://api.openai.com/v1"),
        "api_key": os.environ.get("GAME_IMG_API_KEY", ""),
        "model": os.environ.get("GAME_IMG_MODEL", "gpt-image-1"),
        "size": os.environ.get("GAME_IMG_SIZE", "1024x1024"),
        "backend": os.environ.get("GAME_IMG_BACKEND", "openai"),
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                file_cfg = json.load(f)
            if isinstance(file_cfg, dict):
                cfg.update(file_cfg)
        except (OSError, ValueError) as e:
            print(f"[warn] failed to read {CONFIG_PATH}: {e}", file=sys.stderr)
    return cfg


def _build_multipart(fields, files):
    boundary = "----WBGameGen" + os.urandom(8).hex()
    body = b""
    for name, value in fields.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        body += str(value).encode() + b"\r\n"
    for name, (filename, data, ctype) in files.items():
        body += f"--{boundary}\r\n".encode()
        body += f'Content-Disposition: form-data; name="{name}"; filename="{filename}"\r\n'.encode()
        body += f"Content-Type: {ctype}\r\n\r\n".encode()
        body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    return body, boundary


def _extract_images(resp_bytes):
    data = json.loads(resp_bytes.decode("utf-8"))
    images = []
    for item in data.get("data", []):
        if item.get("b64_json"):
            images.append(base64.b64decode(item["b64_json"]))
        elif item.get("url"):
            with urllib.request.urlopen(item["url"], timeout=300) as r:
                images.append(r.read())
    return images


def call_openai(cfg, prompt, size, n):
    url = cfg["api_base"].rstrip("/") + "/images/generations"
    payload = {
        "model": cfg["model"],
        "prompt": prompt,
        "n": n,
        "size": size,
        "response_format": "b64_json",
    }
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    with urllib.request.urlopen(req, timeout=300) as resp:
        return _extract_images(resp.read())


def call_openai_edit(cfg, prompt, size, n, ref_path):
    url = cfg["api_base"].rstrip("/") + "/images/edits"
    with open(ref_path, "rb") as f:
        ref_data = f.read()
    fields = {
        "model": cfg["model"],
        "prompt": prompt,
        "n": str(n),
        "size": size,
    }
    files = {"image": (os.path.basename(ref_path), ref_data, "image/png")}
    body, boundary = _build_multipart(fields, files)
    headers = {
        "Authorization": f"Bearer {cfg['api_key']}",
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        return _extract_images(resp.read())


def _save_images(images, out, ext):
    if len(images) > 1:
        if os.path.splitext(out)[1] == "":
            os.makedirs(out, exist_ok=True)
            paths = []
            for i, img in enumerate(images):
                p = os.path.join(out, f"img_{i:02d}.{ext}")
                with open(p, "wb") as f:
                    f.write(img)
                paths.append(p)
            return paths
        base, _ = os.path.splitext(out)
        paths = []
        for i, img in enumerate(images):
            p = f"{base}_{i:02d}{os.path.splitext(out)[1] or '.' + ext}"
            with open(p, "wb") as f:
                f.write(img)
            paths.append(p)
        return paths

    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "wb") as f:
        f.write(images[0])
    return [out]


def main():
    ap = argparse.ArgumentParser(description="Generate game art via image API")
    ap.add_argument("--prompt", required=True, help="text prompt")
    ap.add_argument("--size", default=None, help="e.g. 1024x1024, 1920x1080")
    ap.add_argument("--n", type=int, default=1, help="number of images")
    ap.add_argument("--out", required=True, help="output file path or directory")
    ap.add_argument("--ref", default=None, help="reference image for image-to-image")
    args = ap.parse_args()

    cfg = load_config()
    if not cfg.get("api_key"):
        print("[error] no API key. set GAME_IMG_API_KEY or add api_key to "
              f"{CONFIG_PATH}", file=sys.stderr)
        return 1

    size = args.size or cfg.get("size", "1024x1024")

    try:
        if args.ref:
            images = call_openai_edit(cfg, args.prompt, size, args.n, args.ref)
        else:
            images = call_openai(cfg, args.prompt, size, args.n)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        print(f"[error] HTTP {e.code}: {body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as e:
        print(f"[error] network error: {e.reason}", file=sys.stderr)
        return 1

    if not images:
        print("[error] API returned no images", file=sys.stderr)
        return 1

    ext = "png"
    for p in _save_images(images, args.out, ext):
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())
