#!/usr/bin/env python3
"""Check WCAG 2.x contrast ratios for color pairs.

Usage:
  python3 contrast.py pairs.json            # JSON: [{"name","fg","bg","min"}...]
  python3 contrast.py "#0f6e64" "#ffffff"   # single pair, prints ratio
  python3 contrast.py --css page.html       # read token blocks (:root, .dark, [data-theme], @theme), check role pairs per theme
  python3 contrast.py --css tokens.css      # also works on a stylesheet; local @import and <link> files are followed

--css finds every token block: rules whose selector is :root, html or body, a theme class or
attribute (.dark, .light, .theme-x, [data-theme=…], [data-mode=…], [data-color-scheme=…]) alone or
on :root/html/body, and Tailwind v4 @theme {} (also inside @media). It layers each block's custom
properties over the base (first light) block and checks known role pairs (ink/bg, muted/panel,
accent-ink/accent, field/panel, foreground/background, …) plus naming patterns: --X with --X-ink,
--X-foreground or --on-X, and --lN with --lNi. A leading "color-" is ignored (--color-ink = ink)
and paper/paper-2/paper-3 count as bg/panel grounds. Blocks whose selector mentions "dark" are
layered over the first plain dark block (approximating the cascade for palette variants); blocks
other than :root ones are labelled "(light theme)" / "(dark theme)". Values resolved: #hex, rgb(), hsl(), oklch()
and var(--x) references (with fallback). color-mix(), alpha and transparent values are skipped. Local
@import and <link rel=stylesheet> files are read too. It cannot see colors set outside tokens.
Exit 2 (check.py: N/A) when no token block or no checkable pair is found.

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
import math
import os


def _hex(r, g, b):
    clamp = lambda x: max(0, min(255, round(x * 255)))
    return "#%02x%02x%02x" % (clamp(r), clamp(g), clamp(b))


def _oklch_to_hex(L, C, h):
    a, b = C * math.cos(math.radians(h)), C * math.sin(math.radians(h))
    l_, m_, s_ = L + 0.3963377774 * a + 0.2158037573 * b, L - 0.1055613458 * a - 0.0638541728 * b, L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s_ = l_ ** 3, m_ ** 3, s_ ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s_
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s_
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s_
    enc = lambda x: 12.92 * x if x <= 0.0031308 else 1.055 * (max(x, 0) ** (1 / 2.4)) - 0.055
    return _hex(enc(max(r, 0)), enc(max(g, 0)), enc(max(bl, 0)))


def _hsl_to_hex(h, sat, lig):
    c = (1 - abs(2 * lig - 1)) * sat
    x = c * (1 - abs((h / 60) % 2 - 1)); m = lig - c / 2
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h % 360 // 60)]
    return _hex(r + m, g + m, b + m)


def resolve_color(value, tok, depth=0):
    """Return #rrggbb for hex, rgb(), hsl(), oklch() and var(--x[, fallback]); else None."""
    if not value or depth > 6:
        return None
    v = value.strip()
    if re.fullmatch(r"#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?", v):
        return v
    m = re.fullmatch(r"var\(\s*--([\w-]+)\s*(?:,\s*(.+))?\)", v)
    if m:
        return resolve_color(tok.get(m.group(1)) or m.group(2), tok, depth + 1)
    m = re.fullmatch(r"oklch\(\s*([\d.]+)(%?)\s+([\d.]+)\s+([\d.]+)(?:deg)?\s*\)", v)
    if m:
        L = float(m.group(1)) / (100 if m.group(2) else 1)
        return _oklch_to_hex(L, float(m.group(3)), float(m.group(4)))
    m = re.fullmatch(r"rgba?\(\s*(\d+)[\s,]+(\d+)[\s,]+(\d+)\s*\)", v)
    if m:
        return _hex(*(int(x) / 255 for x in m.groups()))
    m = re.fullmatch(r"hsl\(\s*([\d.]+)(?:deg)?[\s,]+([\d.]+)%[\s,]+([\d.]+)%\s*\)", v)
    if m:
        return _hsl_to_hex(float(m.group(1)), float(m.group(2)) / 100, float(m.group(3)) / 100)
    return None


def read_css(path, seen=None):
    """CSS text of a .css/.html file plus local @import and <link> stylesheets."""
    seen = seen if seen is not None else set()
    path = os.path.abspath(path)
    if path in seen or not os.path.exists(path):
        return ""
    seen.add(path)
    text = open(path, encoding="utf-8").read()
    base = os.path.dirname(path)
    if path.endswith((".html", ".htm")):
        css = "\n".join(re.findall(r"<style[^>]*>(.*?)</style>", text, flags=re.S))
        refs = re.findall(r"<link[^>]+rel=[\"']stylesheet[\"'][^>]*href=[\"']([^\"']+)", text)
        refs += re.findall(r"<link[^>]+href=[\"']([^\"']+)[\"'][^>]*rel=[\"']stylesheet", text)
    else:
        css, refs = text, []
    refs += re.findall(r"@import\s+(?:url\()?[\"']?([^\"')\s;]+)", css)
    for r in refs:
        if re.match(r"[a-z]+://|//", r):
            continue
        css += "\n" + read_css(os.path.join(base, r.split("?")[0]), seen)
    return css


ROLE_PAIRS = [
    ("ink", "ground", 4.5), ("ink", "surface", 4.5), ("ink2", "ground", 4.5), ("ink2", "surface", 4.5),
    ("muted", "ground", 4.5), ("muted", "surface", 4.5), ("accent", "ground", 3.0),
    ("ink", "paper", 4.5), ("ink", "paper-2", 4.5), ("ink", "paper-3", 4.5), ("ink-2", "paper", 4.5),
    ("muted", "paper", 4.5), ("muted", "paper-2", 4.5), ("accent", "paper", 3.0),
    ("accent-deep", "paper", 3.0), ("accent-ink", "accent", 4.5), ("focus", "paper", 3.0),
    ("ink", "bg", 4.5), ("ink", "panel", 4.5), ("fg", "bg", 4.5), ("text", "surface", 4.5),
    ("muted", "panel", 4.5), ("muted", "bg", 4.5), ("faint", "panel", 4.5), ("faint", "bg", 4.5),
    ("accent", "panel", 4.5), ("accent", "bg", 4.5), ("accent-ink", "accent", 4.5),
    ("side-ink", "side", 4.5), ("side-muted", "side", 4.5),
    ("crit", "crit-soft", 4.5), ("warn", "warn-soft", 4.5), ("ok", "ok-soft", 4.5),
    ("crit", "panel", 4.5), ("ok", "panel", 4.5),
    ("field", "panel", 3.0), ("focus", "panel", 3.0), ("focus", "bg", 3.0),
    ("foreground", "background", 4.5), ("muted-foreground", "background", 4.5),
]


# A token block: :root, html, body, a theme class / attribute (.dark, .light, .theme-x, [data-theme=…],
# [data-mode=…], [data-color-scheme=…], [class~=dark]) on its own or on :root/html/body, or Tailwind v4 @theme.
_THEME = r"(?:\.(?:(?:dark|light)(?:-mode)?|theme[\w-]*|[\w-]*-theme)|\[(?:data-(?:theme|mode|color-scheme|bs-theme)|class[~*]?=[\"']?(?:dark|light))[^\]]*\])"
_TOKEN_SEL = re.compile(r"(?:(?::root|html|body)(?::where\([^)]*\)|" + _THEME + r")*|(?::where\()?" + _THEME + r"+\)?)")


def is_token_selector(sel):
    """True for selectors that hold design tokens (see _TOKEN_SEL); component rules are skipped."""
    if re.match(r"@theme\b", sel):
        return True
    parts = [p.strip() for p in sel.split(",") if p.strip()]
    return bool(parts) and all(_TOKEN_SEL.fullmatch(p) for p in parts)


def css_blocks(text):
    """Yield (label, {prop: value}) for token blocks (:root, html, theme selectors, @theme)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    out, stack, buf, i = [], [], "", 0
    while i < len(text):
        c = text[i]
        if c == "{":
            sel = buf.strip().splitlines()[-1] if buf.strip() else ""
            sel = re.split(r";", sel)[-1]                     # "@import …; :root" on one line
            if "<" in sel:          # leftover HTML before the selector; a bare ">" is a CSS child combinator, kept
                sel = re.split(r"<[^<>]*>?", sel)[-1]
            stack.append(sel.strip()); buf = ""
        elif c == "}":
            sel = stack.pop() if stack else ""
            if "--" in buf and (":root" in sel or is_token_selector(sel)):
                props = dict(re.findall(r"--([\w-]+)\s*:\s*([^;]+);?", buf))
                ctx = " ".join(x for x in stack if x.startswith("@"))
                out.append(((ctx + " " + sel).strip(), {k: v.strip() for k, v in props.items()}))
            buf = ""
        else:
            buf += c
        i += 1
    return out


def theme_of(label):
    return "dark" if "dark" in label.lower() else "light"


def check_css(path):
    blocks = css_blocks(read_css(path))
    if not blocks:
        print("no :root custom properties found (no :root, html, .dark, [data-theme] or @theme token block)"); return 2
    base_i = next((i for i, (l, _) in enumerate(blocks) if theme_of(l) == "light"), 0)
    base = blocks[base_i][1]
    dark_base = next((p for i, (l, p) in enumerate(blocks) if i != base_i and "dark" in l and "palette" not in l), {})
    strip = lambda d: {(k[6:] if k.startswith("color-") else k): v for k, v in d.items()}
    failed = total = 0
    for i, (label, props) in enumerate(blocks):
        raw = dict(base)
        if "dark" in label:  # theme variants layer over the main dark block, as in the browser
            raw.update(dark_base)
        raw.update(props)
        hexv = lambda name: resolve_color(tok.get(name), raw)
        tok = strip(raw)
        props = strip(props)
        pairs = list(ROLE_PAIRS)
        for k in tok:
            if k + "-ink" in tok: pairs.append((k + "-ink", k, 4.5))
            if k + "-foreground" in tok: pairs.append((k + "-foreground", k, 4.5))
            if "on-" + k in tok: pairs.append(("on-" + k, k, 4.5))
            m = re.fullmatch(r"(l\d+)", k)
            if m and k + "i" in tok: pairs.append((k + "i", k, 4.5))
        seen, rows = set(), []
        for fg, bg, need in pairs:
            if (fg, bg) in seen: continue
            seen.add((fg, bg))
            if i != base_i and fg not in props and bg not in props: continue
            a, b = hexv(fg), hexv(bg)
            if not (a and b): continue
            r = ratio(a, b); ok = r >= need; total += 1; failed += not ok
            rows.append(f"  {'PASS' if ok else 'FAIL'}  {r:5.2f}:1  need {need}:1  --{fg} on --{bg}  ({a} on {b})")
        if rows:
            print(f"[{label}]" + ("" if ":root" in label or i == base_i else f"  ({theme_of(label)} theme)")); print("\n".join(rows))
    if not total:
        print("no checkable colour pairs: token blocks found, but no known role pair resolves to plain colours (check pairs by hand)")
        return 2
    print(f"\n{total - failed}/{total} pairs pass")
    return 1 if failed else 0


def main(argv):
    if len(argv) == 3 and argv[1] == "--css":
        return check_css(argv[2])
    if len(argv) == 3:
        print(f"{ratio(argv[1], argv[2]):.2f}:1")
        return 0
    if len(argv) != 2 or argv[1] in ("-h", "--help"):
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
