#!/usr/bin/env python3
"""Check WCAG 2.x contrast ratios for color pairs.

Usage:
  python3 contrast.py pairs.json            # JSON: [{"name","fg","bg","min"}...]
  python3 contrast.py "#0f6e64" "#ffffff"   # single pair, prints ratio

`min` defaults to 4.5 (normal text). Use 3 for large text, UI components,
focus indicators and graphics (WCAG 1.4.3 / 1.4.11). Colors: #rgb or #rrggbb.
Exit code 1 if any pair fails. Alpha/transparency is not supported: resolve
colors against their actual background first.
"""
import json
import sys


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hex_color):
    h = hex_color.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(ch * 2 for ch in h)
    if len(h) != 6:
        raise ValueError(f"unsupported color: {hex_color}")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def ratio(fg, bg):
    a, b = luminance(fg), luminance(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def main(argv):
    if len(argv) == 3:
        print(f"{ratio(argv[1], argv[2]):.2f}:1")
        return 0
    if len(argv) != 2:
        print(__doc__)
        return 2
    with open(argv[1], encoding="utf-8") as f:
        pairs = json.load(f)
    failed = 0
    for p in pairs:
        r = ratio(p["fg"], p["bg"])
        need = float(p.get("min", 4.5))
        ok = r >= need
        failed += not ok
        print(f"{'PASS' if ok else 'FAIL'}  {r:5.2f}:1  need {need}:1  {p.get('name', '')}  {p['fg']} on {p['bg']}")
    print(f"\n{len(pairs) - failed}/{len(pairs)} pairs pass")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
