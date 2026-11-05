#!/usr/bin/env python3
"""Turn a direction (assets/directions/directions.json) into code-ready design tokens.

Usage:
  python3 export_tokens.py <direction-id> [--out DIR] [--only css,tailwind,shadcn]
  python3 export_tokens.py --json my-tokens.json [--out DIR]     # same keys as a directions.json entry
  python3 export_tokens.py --list
  python3 export_tokens.py <direction-id> --print-dark     # derived dark theme as JSON (used by previews)

Writes into DIR (default ./tokens-<id>/):
  tokens.css          plain CSS custom properties: color roles (light + dark), type, space,
                      radius, shadow, motion. Works in any stack.
  tailwind-theme.css  Tailwind v4: @theme inline mapping onto tokens.css
  shadcn-globals.css  shadcn/ui variable names (:root and .dark) plus @theme inline

The dark theme is derived, then every text/background pair is checked (WCAG AA) and the
derived colors are nudged until they pass. A pair that still fails is printed and exit
code is 1. Review the output; it is a starting point, not a finished brand.
Standard library only.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DIRS = os.path.join(HERE, "..", "assets", "directions", "directions.json")


# ---------- color math (sRGB hex <-> OKLCH) ----------
def hex_rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def delin(c):
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def to_oklch(h):
    r, g, b = [lin(x) for x in hex_rgb(h)]
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = l ** (1 / 3), m ** (1 / 3), s ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def from_oklch(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return "#" + "".join("%02x" % round(delin(x) * 255) for x in (r, g, bl))


def lum(h):
    r, g, b = [lin(x) for x in hex_rgb(h)]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def ok_css(h):
    L, C, H = to_oklch(h)
    return "oklch(%.1f%% %.3f %.0f)" % (L * 100, C, H)


def mix(a, b, t):
    """t of b over a, in linear light."""
    ra, rb = [lin(x) for x in hex_rgb(a)], [lin(x) for x in hex_rgb(b)]
    return "#" + "".join("%02x" % round(delin(x * (1 - t) + y * t) * 255) for x, y in zip(ra, rb))


def best_on(bg, a, b):
    return a if ratio(bg, a) >= ratio(bg, b) else b


def reach(color, bg, need, direction):
    """Move lightness of color (+1 lighter, -1 darker) until it has `need` contrast on bg."""
    L, C, H = to_oklch(color)
    for _ in range(60):
        c = from_oklch(L, C, H)
        if ratio(c, bg) >= need:
            return c
        L = max(0.0, min(1.0, L + 0.01 * direction))
    return from_oklch(L, C, H)


# ---------- themes ----------
def light_theme(d):
    return dict(ground=d["ground"], surface=d["surface"], ink=d["ink"], muted=d["muted"],
                accent=d["accent"], accent_ink=d["accentInk"], tints=list(d["tints"]))


def derive_dark(d):
    _, gC, gH = to_oklch(d["ground"])
    tint = min(gC, 0.02)
    ground = from_oklch(0.18, tint, gH)
    surface = from_oklch(0.225, tint, gH)
    ink = from_oklch(0.95, tint * 0.4, gH)
    muted = reach(from_oklch(0.72, tint, gH), ground, 4.5, +1)
    accent = reach(d["accent"], ground, 4.5, +1)
    accent_ink = best_on(accent, ground, ink)
    tints = []
    for t in d["tints"]:
        _, c, h = to_oklch(t)
        tints.append(from_oklch(0.30, min(c, 0.05), h))
    return dict(ground=ground, surface=surface, ink=ink, muted=muted, accent=accent,
                accent_ink=accent_ink, tints=tints)


def derive_light_from_dark(d):
    _, gC, gH = to_oklch(d["ground"])
    ground = from_oklch(0.97, min(gC, 0.015), gH)
    surface = "#ffffff"
    ink = from_oklch(0.2, min(gC, 0.02), gH)
    muted = reach(from_oklch(0.5, min(gC, 0.02), gH), ground, 4.5, -1)
    accent = reach(d["accent"], ground, 4.5, -1)
    accent_ink = best_on(accent, "#ffffff", ink)
    tints = []
    for t in d["tints"]:
        _, c, h = to_oklch(t)
        tints.append(from_oklch(0.92, min(c, 0.06), h))
    return dict(ground=ground, surface=surface, ink=ink, muted=muted, accent=accent,
                accent_ink=accent_ink, tints=tints)


NOTES = []


def roles(t, dark, label=""):
    t = dict(t)
    g = t["ground"]
    d = +1 if dark else -1
    base = {"ok": "#14733f", "warn": "#9a6400", "bad": "#b3261e", "info": "#2a4bd7"}
    if dark:
        base = {"ok": "#5ac88a", "warn": "#e8b04a", "bad": "#f2837a", "info": "#7fa8f0"}
    for k, v in base.items():
        t[k] = reach(v, g, 4.5, d)
    # accent as a FILL keeps the direction's color; text on it must pass, so pick the best ink.
    cands = [t["accent_ink"], g, t["ink"], "#ffffff", "#000000"]
    best = max(cands, key=lambda c: ratio(c, t["accent"]))
    if best != t["accent_ink"] and ratio(t["accent_ink"], t["accent"]) < 4.5:
        NOTES.append("%s: text on accent changed %s -> %s (%.1f:1)" % (label, t["accent_ink"], best, ratio(best, t["accent"])))
        t["accent_ink"] = best
    # accent as TEXT (links, icons) is a separate, darker/lighter step so the fill stays on brand.
    t["accent_text"] = reach(t["accent"], g, 4.5, d)
    if t["accent_text"] != t["accent"]:
        NOTES.append("%s: accent-text %s derived from accent %s for links" % (label, t["accent_text"], t["accent"]))
    # cards that sit on the opposite tone of the page (light cards on a dark ground) need their own ink.
    si = t["ink"] if ratio(t["ink"], t["surface"]) >= 4.5 else max([g, "#000000", "#ffffff"], key=lambda c: ratio(c, t["surface"]))
    t["surface_ink"] = si
    t["surface_muted"] = t["muted"] if ratio(t["muted"], t["surface"]) >= 4.5 else reach(mix(t["surface"], si, 0.35), t["surface"], 4.5, -1 if lum(si) < lum(t["surface"]) else +1)
    if si != t["ink"]:
        NOTES.append("%s: cards are the opposite tone; use surface-ink/surface-muted on cards" % label)
    t["border"] = mix(g, t["ink"], 0.16)
    t["subtle"] = mix(g, t["ink"], 0.05)
    t["focus"] = reach(t["accent"], g, 3.0, d)
    return t


def checks(name, t):
    pairs = [("ink on ground", t["ink"], t["ground"], 4.5), ("ink on surface", t["surface_ink"], t["surface"], 4.5),
             ("muted on ground", t["muted"], t["ground"], 4.5), ("muted on surface", t["surface_muted"], t["surface"], 4.5),
             ("accent-ink on accent", t["accent_ink"], t["accent"], 4.5),
             ("accent-text on ground", t["accent_text"], t["ground"], 4.5),
             ("focus ring on ground", t["focus"], t["ground"], 3.0),
             ("border on ground", t["border"], t["ground"], 1.0)]
    for k in ("ok", "warn", "bad", "info"):
        pairs.append((k + " on ground", t[k], t["ground"], 4.5))
    out = []
    for label, fg, bg, need in pairs:
        r = ratio(fg, bg)
        out.append((name, label, r, need, r >= need))
    return out


# ---------- emit ----------
SPACE = "--space-3xs: 2px; --space-2xs: 4px; --space-xs: 8px; --space-sm: 12px; --space-md: 16px; --space-lg: 24px; --space-xl: 40px; --space-2xl: 64px; --space-3xl: 96px;"
TEXT = ("--text-xs: 0.8125rem; --text-sm: 0.875rem; --text-md: 1rem; --text-lg: 1.25rem; --text-xl: 1.5625rem; --text-2xl: 1.953rem; --text-3xl: 2.441rem;\n"
        "  --text-display: clamp(2.75rem, 5vw + 1rem, 5.25rem); --text-section: clamp(2rem, 2.5vw + 1rem, 3.5rem);")
MOTION = ("--ease-out: cubic-bezier(0.22, 1, 0.36, 1); --ease-in: cubic-bezier(0.64, 0, 0.78, 0); --ease-in-out: cubic-bezier(0.65, 0, 0.35, 1);\n"
          "  --dur-fast: 120ms; --dur-base: 240ms; --dur-slow: 600ms;  /* motion.md: micro 100-150, layout 200-300, reveal 500-800 */")


def color_block(t, indent="  "):
    rows = [("paper", t["ground"]), ("surface", t["surface"]), ("surface-ink", t["surface_ink"]), ("surface-muted", t["surface_muted"]), ("ink", t["ink"]), ("muted", t["muted"]),
            ("rule", t["border"]), ("subtle", t["subtle"]), ("accent", t["accent"]), ("accent-ink", t["accent_ink"]), ("accent-text", t["accent_text"]),
            ("focus", t["focus"]), ("ok", t["ok"]), ("warn", t["warn"]), ("bad", t["bad"]), ("info", t["info"])]
    rows += [("tint-%d" % (i + 1), c) for i, c in enumerate(t["tints"])]
    return "\n".join("%s--color-%s: %s; /* %s */" % (indent, k, ok_css(v), v) for k, v in rows)


def radii(d):
    r = int(d["radius"])
    btn = {"pill": "999px", "round": "%dpx" % max(8, round(r * 0.6)), "square": "0px"}.get(d.get("btn"), "%dpx" % r)
    return r, btn


def emit_css(d, light, dark, dark_is_default):
    r, btn = radii(d)
    disp, body = d["display"], d["body"]
    fonts = ('--font-display: "%s", "Noto Sans Thai", ui-sans-serif, sans-serif;\n'
             '  --font-body: "%s", "Noto Sans Thai", ui-sans-serif, sans-serif;\n'
             '  --font-mono: "DM Mono", ui-monospace, monospace;') % (disp, body)
    first, second, first_name, second_name = (dark, light, "dark", "light") if dark_is_default else (light, dark, "light", "dark")
    sh = "0 1px 2px rgb(0 0 0 / 0.08), 0 14px 32px -16px rgb(0 0 0 / 0.30)" if d.get("surf") in ("lift", "plastic", "paper") else "none"
    return f"""/* Tokens for direction "{d['id']}" ({d['name']}). Generated by export_tokens.py; edit the source, not this file.
   Fonts: add the Google Fonts links for {disp} and {body}; Thai falls back to Noto Sans Thai. */
:root {{
  color-scheme: {first_name};
{color_block(first)}
  {fonts}
  --display-weight: {d['dw']}; --tracking-display: {d['track']};
  --radius-card: {r}px; --radius-input: {max(6, round(r * 0.6))}px; --radius-button: {btn}; --radius-pill: 999px;
  --shadow-card: {sh};
  {SPACE}
  {TEXT}
  {MOTION}
  --container: 1280px; --gutter: clamp(20px, 5vw, 64px);
}}
[data-theme="{second_name}"] {{
  color-scheme: {second_name};
{color_block(second)}
}}
@media (prefers-color-scheme: {second_name}) {{
  :root:not([data-theme]) {{
{color_block(second, '    ')}
  }}
}}
@media (prefers-reduced-motion: reduce) {{
  :root {{ --dur-fast: 0.01ms; --dur-base: 0.01ms; --dur-slow: 0.01ms; }}
}}
"""


def emit_tailwind(d):
    return f"""/* Tailwind v4 theme for "{d['id']}". Import after tokens.css:  @import "tailwindcss"; @import "./tokens.css"; */
@theme inline {{
  --color-paper: var(--color-paper);
  --color-surface: var(--color-surface);
  --color-surface-ink: var(--color-surface-ink);
  --color-surface-muted: var(--color-surface-muted);
  --color-ink: var(--color-ink);
  --color-muted: var(--color-muted);
  --color-rule: var(--color-rule);
  --color-subtle: var(--color-subtle);
  --color-accent: var(--color-accent);
  --color-accent-ink: var(--color-accent-ink);
  --color-accent-text: var(--color-accent-text);
  --color-focus: var(--color-focus);
  --color-ok: var(--color-ok);
  --color-warn: var(--color-warn);
  --color-bad: var(--color-bad);
  --color-info: var(--color-info);
  --color-tint-1: var(--color-tint-1);
  --color-tint-2: var(--color-tint-2);
  --color-tint-3: var(--color-tint-3);
  --color-tint-4: var(--color-tint-4);
  --font-display: var(--font-display);
  --font-sans: var(--font-body);
  --font-mono: var(--font-mono);
  --radius-card: var(--radius-card);
  --radius-input: var(--radius-input);
  --radius-button: var(--radius-button);
  --shadow-card: var(--shadow-card);
}}
"""


def shadcn_vars(t):
    chart = [t["accent"]] + [reach(c, t["ground"], 3.0, -1 if ratio(t["ink"], t["ground"]) > 7 and lum(t["ground"]) > 0.5 else +1) for c in t["tints"]]
    destructive = t["bad"]
    m = {"background": t["ground"], "foreground": t["ink"], "card": t["surface"], "card-foreground": t["surface_ink"],
         "popover": t["surface"], "popover-foreground": t["surface_ink"], "primary": t["accent"], "primary-foreground": t["accent_ink"],
         "secondary": t["tints"][0], "secondary-foreground": t["ink"], "muted": t["subtle"], "muted-foreground": t["muted"],
         "accent": t["tints"][0], "accent-foreground": t["ink"], "destructive": destructive,
         "border": t["border"], "input": t["border"], "ring": t["focus"]}
    for i, c in enumerate(chart[:5]):
        m["chart-%d" % (i + 1)] = c
    m.update({"sidebar": t["surface"], "sidebar-foreground": t["ink"], "sidebar-primary": t["accent"],
              "sidebar-primary-foreground": t["accent_ink"], "sidebar-accent": t["subtle"],
              "sidebar-accent-foreground": t["ink"], "sidebar-border": t["border"], "sidebar-ring": t["focus"]})
    return m


def emit_shadcn(d, light, dark):
    def block(t):
        return "\n".join("  --%s: %s; /* %s */" % (k, ok_css(v), v) for k, v in shadcn_vars(t).items())
    r, _ = radii(d)
    names = [k for k in shadcn_vars(light)]
    inline = "\n".join("  --color-%s: var(--%s);" % (k, k) for k in names)
    return f"""/* shadcn/ui theme for "{d['id']}". Paste into app/globals.css (or src/index.css) in place of the default :root/.dark blocks. */
:root {{
{block(light)}
  --radius: {r / 16:.3f}rem;
}}
.dark {{
{block(dark)}
}}
@theme inline {{
{inline}
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --font-sans: "{d['body']}", "Noto Sans Thai", ui-sans-serif, sans-serif;
  --font-heading: "{d['display']}", "Noto Sans Thai", ui-sans-serif, sans-serif;
}}
"""


def load(args):
    if "--json" in args:
        return json.load(open(args[args.index("--json") + 1]))
    raw = json.load(open(DIRS))
    items = raw if isinstance(raw, list) else raw["directions"]
    if "--list" in args:
        print(", ".join(x["id"] for x in items))
        sys.exit(0)
    ids = [a for a in args if not a.startswith("--") and a not in (args[args.index("--out") + 1] if "--out" in args else None, args[args.index("--only") + 1] if "--only" in args else None)]
    if not ids:
        print(__doc__)
        sys.exit(2)
    for x in items:
        if x["id"] == ids[0]:
            return x
    print("unknown direction: %s (try --list)" % ids[0])
    sys.exit(2)


def main():
    args = sys.argv[1:]
    d = load(args)
    out = args[args.index("--out") + 1] if "--out" in args else "tokens-%s" % d["id"]
    only = (args[args.index("--only") + 1] if "--only" in args else "css,tailwind,shadcn").split(",")
    dark_is_default = lum(d["ground"]) < 0.2
    if dark_is_default:
        dark_t, light_t = light_theme(d), derive_light_from_dark(d)
    else:
        light_t, dark_t = light_theme(d), derive_dark(d)
    light_t, dark_t = roles(light_t, False, "light"), roles(dark_t, True, "dark")
    if "--print-dark" in args:
        u = dark_t
        print(json.dumps(dict(ground=u["ground"], surface=u["surface"], ink=u["ink"], muted=u["muted"],
                              accent=u["accent"], accentInk=u["accent_ink"], tints=u["tints"], dark=True)))
        return
    os.makedirs(out, exist_ok=True)
    files = {"css": ("tokens.css", emit_css(d, light_t, dark_t, dark_is_default)),
             "tailwind": ("tailwind-theme.css", emit_tailwind(d)),
             "shadcn": ("shadcn-globals.css", emit_shadcn(d, light_t, dark_t))}
    for k in only:
        name, body = files[k]
        open(os.path.join(out, name), "w").write(body)
        print("wrote", os.path.join(out, name))
    fails = 0
    for name, t in (("light", light_t), ("dark", dark_t)):
        for n, label, r, need, passed in checks(name, t):
            if not passed:
                fails += 1
                print("FAIL  %-5s %-26s %.2f:1 need %.1f:1" % (n, label, r, need))
    for n in NOTES:
        print("note  " + n)
    print("contrast: %s" % ("all pairs pass" if not fails else "%d pair(s) fail; adjust the direction's colors" % fails))
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
