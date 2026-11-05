#!/usr/bin/env python3
"""Look up the design-system study guides in assets/design-systems/ without opening whole files.

Usage:
  ds_lookup.py --list                      # slugs
  ds_lookup.py <slug>                      # outline: sections with sizes
  ds_lookup.py <slug> <section>            # print one section; e.g. design-reference | agent-prompt | sources
  ds_lookup.py <slug> <section> --sub tokens   # only the ### sub-section whose title contains 'tokens'
  ds_lookup.py --find "density" [--max 3]  # search all guides; slug, section, matching lines

Sections match by case-insensitive substring of the "## " title (spaces or dashes). Standard library only.
The guides are a secondary study (see assets/design-systems/index.md): confirm exact values at the linked source.
"""
import os, re, sys

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "design-systems")


def slugs():
    return sorted(f[:-3] for f in os.listdir(DIR) if f.endswith(".md") and f != "index.md")


def split(text, level):
    """[(title, body)] for headings of exactly `level` hashes; text before the first heading is ('', body)."""
    pat = re.compile(r"^%s (.+)$" % ("#" * level), re.M)
    out, last, title = [], 0, ""
    for m in pat.finditer(text):
        out.append((title, text[last:m.start()]))
        title, last = m.group(1).strip(), m.end()
    out.append((title, text[last:]))
    return [(t, b.strip("\n")) for t, b in out if t or b.strip()]


def norm(s):
    return re.sub(r"[\s_-]+", " ", re.sub(r"^\d+\.\s*", "", s.strip()).lower()).strip()


# guides with another layout (e.g. radix-themes: numbered sections) map the standard names to theirs
ALIASES = {
    "design reference": ["color palette", "typography", "component styling", "layout", "radius"],
    "agent prompt": ["agent prompt", "starter prompt"],
    "implementation starting point": ["implementation"],
}


def load(slug):
    p = os.path.join(DIR, slug + ".md")
    if not os.path.isfile(p):
        near = [s for s in slugs() if slug in s]
        sys.exit("unknown slug %r%s" % (slug, "; did you mean: " + ", ".join(near) if near else " (use --list)"))
    return open(p, encoding="utf-8").read()


def main(a):
    if not a or a[0] in ("-h", "--help"):
        print(__doc__); return
    if a[0] == "--list":
        print("\n".join(slugs())); return
    if a[0] == "--find":
        if len(a) < 2: sys.exit("--find needs a pattern")
        rx = re.compile(a[1], re.I)
        mx = int(a[a.index("--max") + 1]) if "--max" in a else 3
        hits = 0
        for s in slugs():
            for title, body in split(load(s), 2):
                lines = [l.strip() for l in body.split("\n") if rx.search(l)]
                if lines:
                    hits += 1
                    print("%s :: %s" % (s, title or "(intro)"))
                    for l in lines[:mx]:
                        print("   " + (l[:200] + "…" if len(l) > 200 else l))
        print("\n%d section hits" % hits); return
    text = load(a[0])
    secs = split(text, 2)
    if len(a) == 1 or a[1].startswith("--"):
        for t, b in secs:
            print("%6d chars  %s" % (len(b), t or "(intro)"))
        return
    want = norm(a[1])
    m = [(t, b) for t, b in secs if want in norm(t)]
    if not m and want in ALIASES:
        m = [(t, b) for t, b in secs if any(k in norm(t) for k in ALIASES[want])]
    if not m: sys.exit("no section matching %r; run without a section for the outline" % a[1])
    sub = norm(a[a.index("--sub") + 1]) if "--sub" in a else None
    for t, b in m:
        if sub:
            parts = [(st, sb) for st, sb in split(b, 3) if sub in norm(st)]
            if not parts: continue
            for st, sb in parts: print("### %s\n%s\n" % (st, sb))
        else:
            print("## %s\n%s\n" % (t, b))


if __name__ == "__main__":
    main(sys.argv[1:])
