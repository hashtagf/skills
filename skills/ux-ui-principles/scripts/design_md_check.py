#!/usr/bin/env python3
"""Validate a DESIGN.md design-language file against references/design-memory.md §3.

Usage:
  python3 design_md_check.py DESIGN.md [--json]

Checks structure and the things that make the file useful to the next agent:
required sections, reasons (not only values), color roles with values and a
dark theme, an anti-pattern list, dials in range, a status line, and leftover
placeholders. It does not judge taste and does not check contrast; run
`python3 contrast.py --css <page>` on the built tokens for that.
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


def check(md):
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
