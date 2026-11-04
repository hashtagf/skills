#!/usr/bin/env python3
"""Check WCAG 2.x contrast ratios for color pairs.

Usage:
  python3 contrast.py pairs.json            # JSON: [{"name","fg","bg","min"}...]
  python3 contrast.py "#0f6e64" "#ffffff"   # single pair, prints ratio
  python3 contrast.py --css page.html       # read :root token blocks, check role pairs per theme

--css finds every rule whose selector contains :root (including inside @media),
layers its custom properties over the base :root block, and checks known role
pairs (ink/bg, muted/panel, accent-ink/accent, field/panel, …) plus naming
patterns: --X with --X-ink or --on-X, and --lN with --lNi. Blocks whose selector
mentions "dark" are layered over the first plain dark block (approximating the
cascade for palette variants). Only #hex values are resolved; var() references
and transparent values are skipped. It cannot see colors set outside tokens.

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


import re

ROLE_PAIRS = [
    ("ink", "bg", 4.5), ("ink", "panel", 4.5), ("fg", "bg", 4.5), ("text", "surface", 4.5),
    ("muted", "panel", 4.5), ("muted", "bg", 4.5), ("faint", "panel", 4.5), ("faint", "bg", 4.5),
    ("accent", "panel", 4.5), ("accent", "bg", 4.5), ("accent-ink", "accent", 4.5),
    ("side-ink", "side", 4.5), ("side-muted", "side", 4.5),
    ("crit", "crit-soft", 4.5), ("warn", "warn-soft", 4.5), ("ok", "ok-soft", 4.5),
    ("crit", "panel", 4.5), ("ok", "panel", 4.5),
    ("field", "panel", 3.0), ("focus", "panel", 3.0), ("focus", "bg", 3.0),
]


def css_blocks(text):
    """Yield (label, {prop: value}) for rules whose selector contains :root."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out, stack, buf, i = [], [], "", 0
    while i < len(text):
        c = text[i]
        if c == "{":
            sel = buf.strip().splitlines()[-1] if buf.strip() else ""
            if "<" in sel or ">" in sel and ":root" not in sel:
                sel = re.split(r"[<>]", sel)[-1]
            stack.append(sel.strip()); buf = ""
        elif c == "}":
            sel = stack.pop() if stack else ""
            if ":root" in sel and "--" in buf:
                props = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);?", buf))
                ctx = " ".join(x for x in stack if x.startswith("@"))
                out.append(((ctx + " " + sel).strip(), {k: v.strip() for k, v in props.items()}))
            buf = ""
        else:
            buf += c
        i += 1
    return out


def check_css(path):
    blocks = css_blocks(open(path, encoding="utf-8").read())
    if not blocks:
        print("no :root custom properties found"); return 2
    base = blocks[0][1]
    dark_base = next((p for l, p in blocks[1:] if "dark" in l and "palette" not in l), {})
    hexv = lambda v: v if v and re.fullmatch(r"#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?", v) else None
    failed = total = 0
    for label, props in blocks:
        tok = dict(base)
        if "dark" in label:  # theme variants layer over the main dark block, as in the browser
            tok.update(dark_base)
        tok.update(props)
        pairs = list(ROLE_PAIRS)
        for k in tok:
            if k + "-ink" in tok: pairs.append((k + "-ink", k, 4.5))
            if "on-" + k in tok: pairs.append(("on-" + k, k, 4.5))
            m = re.fullmatch(r"(l\d+)", k)
            if m and k + "i" in tok: pairs.append((k + "i", k, 4.5))
        seen, rows = set(), []
        for fg, bg, need in pairs:
            if (fg, bg) in seen: continue
            seen.add((fg, bg))
            if label != blocks[0][0] and fg not in props and bg not in props: continue
            a, b = hexv(tok.get(fg)), hexv(tok.get(bg))
            if not (a and b): continue
            r = ratio(a, b); ok = r >= need; total += 1; failed += not ok
            rows.append(f"  {'PASS' if ok else 'FAIL'}  {r:5.2f}:1  need {need}:1  --{fg} on --{bg}  ({a} on {b})")
        if rows:
            print(f"[{label}]"); print("\n".join(rows))
    print(f"\n{total - failed}/{total} pairs pass")
    return 1 if failed else 0


def main(argv):
    if len(argv) == 3 and argv[1] == "--css":
        return check_css(argv[2])
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
