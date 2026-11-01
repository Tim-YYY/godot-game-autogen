#!/usr/bin/env python3
"""
Validate generated game assets: file validity, format, dimensions, alpha channel.

Usage:
  python check_image.py path/to/image.png [--expect-alpha] [--min 512x512]
Exit codes:
  0  all checks passed
  1  file missing / unreadable / unknown format
  2  alpha channel expected but missing (sprite transparency)
  3  dimensions below minimum
"""

import argparse
import os
import struct
import sys


def parse_png(path):
    with open(path, "rb") as f:
        if f.read(8) != b"\x89PNG\r\n\x1a\n":
            return None
        f.read(4)  # IHDR chunk length
        if f.read(4) != b"IHDR":
            return None
        w, h = struct.unpack(">II", f.read(8))
        bit_depth = f.read(1)[0]
        color_type = f.read(1)[0]
        return {"format": "PNG", "width": w, "height": h,
                "alpha": color_type in (4, 6), "bit_depth": bit_depth}


_SOF = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}


def parse_jpeg(path):
    with open(path, "rb") as f:
        if f.read(2) != b"\xff\xd8":
            return None
        while True:
            b = f.read(1)
            while b == b"\xff":
                b = f.read(1)
            if not b:
                return None
            marker = b[0]
            if marker in _SOF:
                f.read(3)  # length + precision
                h, w = struct.unpack(">HH", f.read(4))
                return {"format": "JPEG", "width": w, "height": h, "alpha": False}
            if marker in (0xD8, 0xD9, 0x01):
                continue
            seg = f.read(2)
            if len(seg) < 2:
                return None
            length = struct.unpack(">H", seg)[0]
            if length < 2:
                return None
            f.read(length - 2)


def parse_webp(path):
    with open(path, "rb") as f:
        if f.read(4) != b"RIFF":
            return None
        f.read(4)
        if f.read(4) != b"WEBP":
            return None
        chunk = f.read(4)
        size = struct.unpack("<I", f.read(4))[0]
        if chunk == b"VP8X":
            flags = f.read(1)[0]
            f.read(3)  # reserved
            w = struct.unpack("<I", f.read(3) + b"\x00")[0] + 1
            h = struct.unpack("<I", f.read(3) + b"\x00")[0] + 1
            return {"format": "WEBP", "width": w, "height": h,
                    "alpha": bool(flags & 0x10)}
        if chunk == b"VP8L":
            f.read(1)  # signature 0x2F
            bits = struct.unpack("<I", f.read(4))[0]
            w = (bits & 0x3FFF) + 1
            h = ((bits >> 14) & 0x3FFF) + 1
            return {"format": "WEBP", "width": w, "height": h,
                    "alpha": bool(bits >> 28)}
        if chunk == b"VP8 ":
            # lossy VP8, no alpha; dimensions need a deeper parse, report unknown
            return {"format": "WEBP", "width": 0, "height": 0, "alpha": False}
    return None


def parse_image(path):
    parsers = [parse_png, parse_jpeg, parse_webp]
    for p in parsers:
        try:
            info = p(path)
            if info:
                return info
        except (OSError, struct.error):
            return None
    return None


def main():
    ap = argparse.ArgumentParser(description="Validate a generated game asset")
    ap.add_argument("path", help="image file to check")
    ap.add_argument("--expect-alpha", action="store_true",
                    help="require a transparent background (sprites/icons)")
    ap.add_argument("--min", default=None,
                    help="minimum dimensions as WxH, e.g. 512x512")
    args = ap.parse_args()

    if not os.path.isfile(args.path):
        print(f"[FAIL] file not found: {args.path}")
        return 1

    size = os.path.getsize(args.path)
    if size == 0:
        print(f"[FAIL] file is empty: {args.path}")
        return 1

    info = parse_image(args.path)
    if not info:
        print(f"[FAIL] unknown or corrupt image format: {args.path}")
        return 1

    print(f"[OK] {info['format']} {info['width']}x{info['height']} "
          f"alpha={info['alpha']} bytes={size}")

    if args.expect_alpha and not info.get("alpha"):
        print(f"[FAIL] expected transparent background but image has no alpha "
              f"channel: {args.path}")
        return 2

    if args.min:
        try:
            mw, mh = (int(x) for x in args.min.lower().split("x"))
        except ValueError:
            print(f"[error] bad --min value: {args.min}", file=sys.stderr)
            return 1
        if info["width"] < mw or info["height"] < mh:
            print(f"[FAIL] dimensions {info['width']}x{info['height']} below "
                  f"minimum {mw}x{mh}: {args.path}")
            return 3

    print("[PASS] all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
