#!/usr/bin/env python3
"""Validate a DESIGN.md design-language file against references/design-memory.md §3.

Usage:
  python3 design_md_check.py DESIGN.md [--json]

Two formats. With YAML front matter it checks the Google design.md spec (alpha): name, token groups,
{refs}, value formats, canonical section order, duplicates, WCAG pairs in components, plus our extras
(dials, status, dark theme, anti-patterns, decision log). Without front matter it checks the older
prose-only format below and warns that it is legacy.

Checks structure and the things that make the file useful to the next agent:
required sections, reasons (not only values), color roles with values and a
dark theme, an anti-pattern list, dials in range, a status line, and leftover
placeholders. It does not judge taste; contrast is checked only for the component pairs DESIGN.md
declares, so run `python3 contrast.py --css <page>` on the built tokens too.
Exit code 1 on any error, 2 on usage error. Standard library only.
"""
import json
import re
import sys

REQUIRED = {
    "personality": r"personality|brand",
    "philosophy": r"philosophy|principles",
    "typography": r"typograph|type\b|fonts?",
    "color": r"colou?r",
    "space/shape": r"spac|shape|radius|depth|elevation",
    "layout": r"layout",
    "components": r"component",
    "interaction": r"interaction|behavio",
    "anti-patterns": r"anti-?pattern|never|avoid|don't",
}
RECOMMENDED = {
    "direction dials": r"dial|variance|density",
    "decision log": r"decision",
}
ROLES = ["canvas", "surface", "text", "muted", "border", "primary", "focus",
         "success", "warning", "danger"]


def sections(md):
    out, cur = {}, None
    for line in md.splitlines():
        m = re.match(r"^#{2,3}\s+(.*)", line)
        if m:
            cur = m.group(1).strip()
            out[cur] = []
        elif cur:
            out[cur].append(line)
    return {k: "\n".join(v) for k, v in out.items()}


def find(secs, pattern):
    for name, body in secs.items():
        if re.search(pattern, name, re.I):
            return name, body
    return None, None



# ---------- Google design.md spec (alpha) ----------
CANON = [("overview", r"overview|brand\s*&\s*style"), ("colors", r"colou?rs?$"), ("typography", r"typography"),
         ("layout", r"layout"), ("elevation", r"elevation"), ("shapes", r"shapes?"), ("components", r"components?"),
         ("dos-donts", r"do'?s\s*(and|&)\s*don'?ts")]
DIM = re.compile(r"^-?\d+(\.\d+)?(px|em|rem)$|^0$")
HEX = re.compile(r"^#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
CSSFN = re.compile(r"^(rgb|rgba|hsl|hsla|hwb|oklch|oklab|lch|lab|color-mix)\(", re.I)
TYPO_PROPS = {"fontFamily", "fontSize", "fontWeight", "lineHeight", "letterSpacing", "fontFeature", "fontVariation"}
COMP_PROPS = {"backgroundColor", "textColor", "typography", "rounded", "padding", "size", "height", "width"}


def split_front(md):
    m = re.match(r"^---\s*\n([\s\S]*?)\n---\s*(\n|$)", md)
    return (m.group(1), md[m.end():]) if m else (None, md)


def scalar(v):
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    return v


def parse_yaml(text):
    """Tiny indentation-based parser: nested maps of scalars (all this format needs)."""
    root, stack, dups = {}, [(-1, None)], []
    stack = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        ind = len(raw) - len(raw.lstrip())
        m = re.match(r"^\s*([^:#]+?):\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1).strip().strip("\"'"), m.group(2).strip()
        while stack and stack[-1][0] >= ind:
            stack.pop()
        cur = stack[-1][1]
        if key in cur:
            dups.append(key)
        if val == "":
            cur[key] = {}
            stack.append((ind, cur[key]))
        else:
            cur[key] = scalar(val)
    return root, dups


def lum_hex(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h[:3])
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    x, y = sorted((lum_hex(a), lum_hex(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


def resolve(tokens, ref):
    cur = tokens
    for part in ref.strip("{}").split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def check_spec(md, fm_text, body):
    res = []
    add = lambda lvl, msg: res.append({"level": lvl, "message": msg})
    tokens, dups = parse_yaml(fm_text)
    for d in dups:
        add("error", f"duplicate key in front matter: {d}")
    if not tokens.get("name"):
        add("error", "front matter has no name")
    if tokens.get("version") not in (None, "alpha"):
        add("warn", f"unknown spec version {tokens.get('version')}; this checker knows alpha")
    elif tokens.get("version") is None:
        add("warn", "no version: alpha in front matter")
    colors = tokens.get("colors")
    if not isinstance(colors, dict) or not colors:
        add("error", "no colors in front matter")
        colors = {}
    elif "primary" not in colors:
        add("error", "colors has no primary")
    for k, v in colors.items():
        if not isinstance(v, str):
            add("error", f"colors.{k} must be a color string")
            continue
        if not (HEX.match(v) or CSSFN.match(v) or re.match(r"^[a-zA-Z]+$", v)):
            add("error", f"colors.{k} is not a valid color: {v}")
    for grp in ("rounded", "spacing"):
        gv = tokens.get(grp) or {}
        if not isinstance(gv, dict):
            add("error", f"{grp} must be a map of name: dimension, got: {str(gv)[:40]}")
            continue
        for k, v in gv.items():
            if isinstance(v, str) and not DIM.match(v) and not re.match(r"^-?\d+(\.\d+)?$", v):
                add("warn", f"{grp}.{k} is not a dimension (px, em, rem): {v}")
    typo = tokens.get("typography") or {}
    if not isinstance(typo, dict):
        add("error", "typography must be a map of name: {properties}")
        typo = {}
    for n, spec in typo.items():
        if not isinstance(spec, dict):
            add("error", f"typography.{n} must be a map")
            continue
        for p, v in spec.items():
            if p not in TYPO_PROPS:
                add("warn", f"typography.{n}.{p} is not a known property")
        fs = spec.get("fontSize")
        if fs and not DIM.match(fs):
            add("error", f"typography.{n}.fontSize needs px, em or rem: {fs}")
    refs = re.findall(r"\{([a-zA-Z0-9_.-]+)\}", fm_text)
    for r in sorted(set(refs)):
        if resolve(tokens, r) is None:
            add("error", f"unresolved token reference {{{r}}}")
    comps = tokens.get("components") or {}
    if not isinstance(comps, dict):
        add("error", "components must be a map")
        comps = {}
    for n, spec in comps.items():
        if not isinstance(spec, dict):
            add("error", f"components.{n} must be a map")
            continue
        for p in spec:
            if p not in COMP_PROPS:
                add("warn", f"components.{n}.{p} is not a known component property")
        bg, fg = spec.get("backgroundColor"), spec.get("textColor")
        def val(x):
            x = resolve(tokens, x) if x and x.startswith("{") else x
            return x if isinstance(x, str) and HEX.match(x) else None
        a, b = val(bg), val(fg)
        if a and b and ratio(a, b) < 4.5:
            add("warn", f"components.{n}: text on background is {ratio(a, b):.1f}:1, below 4.5:1")
    # pairs on the page itself
    for fgk, bgk in (("on-surface", "canvas"), ("on-surface", "surface"), ("muted", "canvas"), ("on-primary", "primary"),
                     ("primary-text", "canvas"), ("dark-on-surface", "dark-canvas"), ("dark-muted", "dark-canvas"),
                     ("dark-on-primary", "dark-primary"), ("dark-primary-text", "dark-canvas")) + tuple(
            (("on-tint-%d" % i), ("tint-%d" % i)) for i in range(1, 5)) + tuple(
            (("dark-on-tint-%d" % i), ("dark-tint-%d" % i)) for i in range(1, 5)):
        if HEX.match(colors.get(fgk, "")) and HEX.match(colors.get(bgk, "")) and ratio(colors[fgk], colors[bgk]) < 4.5:
            add("warn", f"colors {fgk} on {bgk} is {ratio(colors[fgk], colors[bgk]):.1f}:1, below 4.5:1")
    if not any(k.startswith("dark-") for k in colors) and not re.search(r"light only|dark theme", md, re.I):
        add("warn", "no dark-* colors and no 'light only' decision")
    # sections
    heads = [m.group(1).strip() for m in re.finditer(r"^##\s+(.*)$", body, re.M)]
    seen = {}
    for h in heads:
        seen[h.lower()] = seen.get(h.lower(), 0) + 1
    for h, n in seen.items():
        if n > 1:
            add("error", f"duplicate section heading: {h}")
    omitted = tokens.get("omitted", "")
    order = []
    for h in heads:
        for idx, (key, pat) in enumerate(CANON):
            if re.match(pat, h, re.I):
                order.append((idx, key))
                break
    if [i for i, _ in order] != sorted(i for i, _ in order):
        add("error", "canonical sections are out of order (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts)")
    present = {k for _, k in order}
    for key, _ in CANON:
        if key not in present and key not in str(omitted):
            add("warn", f"missing section: {key}")
    sec = sections(body)
    _, dd = find(sec, r"do'?s")
    n = len([b for b in (dd or "").splitlines() if re.match(r"\s*[-*]\s+\S", b)])
    if dd is not None and n < 3:
        add("warn", "Do's and Don'ts has fewer than 3 bullets; list what the brand deliberately avoids")
    # our extras
    if not re.search(r"status\s*:\s*(draft|approved)", md, re.I):
        add("warn", "no 'Status: draft|approved' line; agents cannot tell if values are binding")
    if not re.search(r"\bdials?\b|variance", md, re.I):
        add("warn", "no direction dials section")
    if not re.search(r"^##\s+decision", md, re.I | re.M):
        add("warn", "no Decision log; record why, not only what")
    for m in re.finditer(r"(\d+)\s*/\s*10", md):
        if not 1 <= int(m.group(1)) <= 10:
            add("error", f"dial value out of range: {m.group(0)}")
    if re.search(r"thai", md, re.I):
        lhs = [float(v.get("lineHeight")) for v in (tokens.get("typography") or {}).values()
               if isinstance(v, dict) and re.match(r"^\d+(\.\d+)?$", str(v.get("lineHeight", "")))]
        body_lh = [float(v["lineHeight"]) for k, v in (tokens.get("typography") or {}).items()
                   if k.startswith("body") and isinstance(v, dict) and re.match(r"^\d+(\.\d+)?$", str(v.get("lineHeight", "")))]
        if body_lh and min(body_lh) < 1.55:
            add("warn", f"Thai is used but body lineHeight is {min(body_lh)} (< 1.55)")
        if not lhs:
            add("warn", "Thai is used but no unitless lineHeight is stated")
    ph = [p for p in re.findall(r"<[a-z][\w /-]*>|\bTODO\b|\bTBD\b|lorem", md, re.I) if not re.match(r"<(br|hr|p|div|span|a|img)\b", p, re.I)]
    if ph:
        add("warn", f"placeholders left: {', '.join(sorted(set(ph))[:5])}")
    return res


def check(md):
    fm, body = split_front(md)
    if fm is not None:
        return check_spec(md, fm, body)
    res = check_legacy(md)
    res.insert(0, {"level": "warn", "message": "no YAML front matter: legacy prose-only format; the Google design.md spec uses front matter tokens"})
    return res


def check_legacy(md):
    res = []
    add = lambda lvl, msg: res.append({"level": lvl, "message": msg})
    secs = sections(md)
    if not secs:
        add("error", "no ## sections found")
        return res
    for label, pat in REQUIRED.items():
        name, body = find(secs, pat)
        if not name:
            add("error", f"missing section: {label}")
        elif len((body or "").strip()) < 10:
            add("error", f"section '{name}' is empty")
    for label, pat in RECOMMENDED.items():
        if not find(secs, pat)[0]:
            add("warn", f"missing recommended section: {label}")

    if not re.search(r"status\s*:\s*(draft|approved)", md, re.I):
        add("warn", "no 'Status: draft|approved' line; agents cannot tell if values are binding")

    _, pers = find(secs, REQUIRED["personality"])
    if pers:
        bullets = [b for b in pers.splitlines() if re.match(r"\s*[-*]\s+\S", b)]
        bare = [b.strip() for b in bullets if not re.search(r"[—:–-]\s+\S", b.strip()[2:])]
        if bullets and len(bare) == len(bullets):
            add("warn", "personality is adjectives only; say what each means on screen")

    _, col = find(secs, REQUIRED["color"])
    if col:
        if not re.search(r"#[0-9a-fA-F]{3,8}\b|oklch\(|rgb\(|hsl\(", col):
            add("error", "color section has no values")
        missing = [r for r in ROLES if not re.search(r"\b" + r, col, re.I)]
        if len(missing) > 4:
            add("warn", f"few color roles named; missing {', '.join(missing)}")
        if not re.search(r"dark", col, re.I) and not re.search(r"dark (mode|theme)", md, re.I):
            add("warn", "no dark theme values or an explicit 'light only' decision")

    _, anti = find(secs, REQUIRED["anti-patterns"])
    if anti is not None:
        n = len([b for b in anti.splitlines() if re.match(r"\s*[-*]\s+\S", b)]) or anti.count("·") + 1
        if n < 3:
            add("warn", f"only {n} anti-pattern(s); list what the brand deliberately avoids")

    for m in re.finditer(r"(\d+)\s*/\s*10", md):
        if not 1 <= int(m.group(1)) <= 10:
            add("error", f"dial value out of range: {m.group(0)}")

    if re.search(r"thai", md, re.I):
        lh = [float(x) for x in re.findall(r"line-height[^\n]*?(\d\.\d+)", md, re.I)]
        if not lh:
            add("warn", "Thai is used but no line-height is stated (body 1.55–1.7 recommended)")
        elif max(lh) < 1.55:
            add("warn", f"Thai body line-height {max(lh)} < 1.55")

    _, typ = find(secs, REQUIRED["typography"])
    if typ and not re.search(r"because|for |so |reason|—", typ, re.I):
        add("warn", "typography lists fonts without a reason")

    ph = re.findall(r"<[a-z][\w /-]*>|\bTODO\b|\bTBD\b|lorem", md, re.I)
    ph = [p for p in ph if not re.match(r"<(br|hr|p|div|span|a|img)\b", p, re.I)]
    if ph:
        add("warn", f"placeholders left: {', '.join(sorted(set(ph))[:5])}")
    return res


def main(argv):
    files = [a for a in argv if not a.startswith("--")]
    if len(files) != 1:
        print(__doc__)
        return 2
    with open(files[0], encoding="utf-8") as f:
        res = check(f.read())
    if "--json" in argv:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        for r in res:
            print(f"[{r['level']}] {r['message']}")
        print(f"{sum(r['level']=='error' for r in res)} error, {sum(r['level']=='warn' for r in res)} warn")
    return 1 if any(r["level"] == "error" for r in res) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
