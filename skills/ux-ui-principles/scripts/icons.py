#!/usr/bin/env python3
"""Find and paste icons from Lucide (UI glyphs) and Simple Icons (brand marks) — references/iconography.md "Icon libraries".

Usage:
  python3 scripts/icons.py search booking calendar          # Lucide names + Simple Icons brands matching the words
  python3 scripts/icons.py lucide calendar-check phone [--size 20] [--stroke 2] [--sprite icons.svg]
  python3 scripts/icons.py brand line whatsapp [--ground "#faf7ef"] [--mono] [--size 20]   # --ground: #rgb or #rrggbb
  options: [--lucide-version 1.58.0] [--simple-version 16.35.0]

lucide  prints each icon as inline SVG ready to paste: currentColor, aria-hidden, class="icon", your size and
        stroke (one stroke width per page). Unknown names get the closest matches. --sprite writes a <symbol> sprite
        to use as <svg class="icon"><use href="icons.svg#calendar-check"/></svg>.
brand   prints the brand's single-path SVG with its hex colour (or currentColor with --mono), checks the colour
        against --ground (3:1, WCAG 1.4.11) and falls back to mono when it fails, and prints the brand's
        guidelines, licence and source links. A brand that is not in Simple Icons (PromptPay, KBank, SCB, Lazada,
        Agoda, Wongnai, LINE MAN …) must come from the brand's own media kit: never redraw a logo.

Versions are pinned (at least two weeks old) so pages stay reproducible; data is cached in the temp folder
(written only after a successful fetch; an empty or broken cache file is fetched again).
Network: curl to cdn.jsdelivr.net. Standard library only.
"""
import json, os, re, subprocess, sys, tempfile

LUCIDE_V = "1.58.0"       # lucide-static, ISC, published 2026-10-16
SIMPLE_V = "16.35.0"      # simple-icons, CC0 project (each brand keeps its trademark), published 2026-10-11
CDN = "https://cdn.jsdelivr.net/npm"
CACHE = os.path.join(tempfile.gettempdir(), "ux-ui-icons-cache")


def arg(name, default=None):
    a = sys.argv
    if name not in a:
        return default
    i = a.index(name) + 1
    return a[i] if i < len(a) else ""


def get(url):
    r = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "60", url], capture_output=True)
    if r.returncode:
        raise RuntimeError(f"{url}: {r.stderr.decode('utf-8', 'replace').strip() or 'curl failed'}")
    return r.stdout.decode("utf-8")


def _valid(text, name):
    if not text.strip():
        return False
    if name.endswith(".json"):
        try:
            json.loads(text)
        except ValueError:
            return False
    return True


def cached(url, name):
    """Return the file at url, cached under CACHE. Fetches first and writes atomically, so a failed or
    interrupted fetch never leaves a file behind; an empty or unreadable cached file is fetched again."""
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if os.path.exists(p):
        try:
            text = open(p, encoding="utf-8").read()
            if _valid(text, name):
                return text
        except (OSError, UnicodeDecodeError):
            pass
    text = get(url)
    if not _valid(text, name):
        raise RuntimeError(f"{url}: empty or invalid response")
    fd, tmp = tempfile.mkstemp(dir=CACHE, prefix=".part-")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    os.replace(tmp, p)
    return text


def lucide_tags(v):
    return json.loads(cached(f"{CDN}/lucide-static@{v}/tags.json", f"lucide-{v}-tags.json"))


def simple_data(v):
    d = json.loads(cached(f"{CDN}/simple-icons@{v}/data/simple-icons.json", f"simple-{v}.json"))
    return d if isinstance(d, list) else d["icons"]


def lum(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def ratio(a, b):
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def words(argv):
    skip = {"--size", "--stroke", "--sprite", "--ground", "--lucide-version", "--simple-version"}
    return [a for i, a in enumerate(argv) if not a.startswith("--") and argv[i - 1] not in skip]


def search(qs, lv, sv):
    tags, data = lucide_tags(lv), simple_data(sv)
    q = [w.lower() for w in qs]
    scored = []
    for name, t in tags.items():
        s = sum(3 if w in name.split("-") else 2 if w in name else 1 if any(w in x for x in t) else 0 for w in q)
        if s:
            scored.append((-s, name, t))
    print(f"Lucide {lv} (ISC): {len(scored)} match")
    for s, name, t in sorted(scored)[:12]:
        print(f"  {name:28} {', '.join(t[:6])}")
    def names(i):
        out = [i["title"].lower(), i["slug"]]
        for v in i.get("aliases", {}).values():  # aka: [str], dup/loc: objects with titles
            for x in (v if isinstance(v, list) else [v]):
                out += [x.lower()] if isinstance(x, str) else [str(t).lower() for t in (x.values() if isinstance(x, dict) else [])]
        return out
    def bscore(i):
        best = 0
        for n in names(i):
            for w in q:
                best = max(best, 3 if n == w else 2 if re.search(r"(^|\W)" + re.escape(w) + r"(\W|$)", n) else 0)
        return best
    hits = sorted((i for i in data if bscore(i)), key=lambda i: (-bscore(i), i["title"]))
    print(f"Simple Icons {sv} (brands): {len(hits)} match")
    for i in hits[:12]:
        print(f"  {i['slug']:28} {i['title']}  #{i['hex']}")
    if not scored:
        print("No Lucide glyph: draw one to Lucide's rules (iconography.md) and keep it in the project's icon file.")
    return 0


def lucide(names, lv):
    size, stroke, sprite = arg("--size", "20"), arg("--stroke", "2"), arg("--sprite")
    tags = lucide_tags(lv)
    symbols, bad = [], 0
    for n in names:
        if n not in tags:
            near = [k for k in tags if n in k or any(n in t for t in tags[k])][:8]
            print(f"<!-- '{n}' is not in Lucide {lv}. Closest: {', '.join(near) or 'none'}. "
                  f"No glyph fits: draw one to Lucide's rules (iconography.md) or drop the icon. -->")
            bad += 1
            continue
        svg = cached(f"{CDN}/lucide-static@{lv}/icons/{n}.svg", f"lucide-{lv}-{n}.svg")
        m = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S)
        if not m:
            print(f"<!-- '{n}': unexpected file, skipped -->"); bad += 1; continue
        inner = m.group(1).strip()
        inner = re.sub(r"\s*\n\s*", "", inner)
        symbols.append((n, inner))
        if not sprite:
            print(f'<svg class="icon" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
                  f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" '
                  f'data-lucide="{n}">{inner}</svg>')
    if sprite and symbols:
        body = "".join(f'<symbol id="{n}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="{stroke}" '
                       f'stroke-linecap="round" stroke-linejoin="round">{inner}</symbol>' for n, inner in symbols)
        open(sprite, "w", encoding="utf-8").write(
            f'<!-- Lucide {lv} (ISC License, lucide.dev) --><svg xmlns="http://www.w3.org/2000/svg" style="display:none">{body}</svg>\n')
        print(f"wrote {sprite} ({len(symbols)} symbols). Use: <svg class=\"icon\" aria-hidden=\"true\"><use href=\"{os.path.basename(sprite)}#{symbols[0][0]}\"/></svg>")
    print(f"<!-- Lucide {lv}, ISC License (keep the notice with the source: lucide.dev/license). "
          f"Size {size}px, stroke {stroke}: use one stroke width per page. -->")
    return 1 if bad else 0


def brand(slugs, sv):
    size, ground, mono = arg("--size", "20"), arg("--ground"), "--mono" in sys.argv
    data = {i["slug"]: i for i in simple_data(sv)}
    titles = {i["title"].lower(): i for i in data.values()}
    bad = 0
    for s in slugs:
        i = data.get(s.lower()) or titles.get(s.lower())
        if not i:
            near = [k for k in data if s.lower() in k][:6]
            print(f"<!-- '{s}' is not in Simple Icons {sv}{' (closest: ' + ', '.join(near) + ')' if near else ''}. "
                  f"Get the official mark from the brand's media kit or press page; never redraw or approximate a logo. -->")
            bad += 1
            continue
        svg = cached(f"{CDN}/simple-icons@{sv}/icons/{i['slug']}.svg", f"simple-{sv}-{i['slug']}.svg")
        m = re.search(r'<path d="([^"]+)"', svg)
        if not m:
            print(f"<!-- '{s}': unexpected file, skipped -->"); bad += 1; continue
        path = m.group(1)
        fill, note = "#" + i["hex"], ""
        if ground and not mono:
            r = ratio(fill, ground)
            if r < 3:
                note = f"brand colour #{i['hex']} is {r:.2f}:1 on {ground} (< 3:1): using currentColor; put the colour on a contrasting chip or keep it mono"
                fill = "currentColor"
            else:
                note = f"brand colour #{i['hex']} is {r:.2f}:1 on {ground} (passes 3:1)"
        if mono:
            fill = "currentColor"
        print(f'<svg class="brand-mark" width="{size}" height="{size}" viewBox="0 0 24 24" fill="{fill}" aria-hidden="true" '
              f'data-brand="{i["slug"]}"><path d="{path}"/></svg>')
        print(f"<!-- {i['title']}: trademark of its owner; use it only to name or link to that brand (contact, pay with, "
              f"integrations), unaltered. {note}")
        print(f"     guidelines: {i.get('guidelines') or 'none listed (check the source and the brand site)'}")
        print(f"     licence: {(i.get('license') or {}).get('type') or (i.get('license') or {}).get('url') or 'not listed (not proof of any licence)'}; source: {i['source']} -->")
    print("<!-- Simple Icons " + sv + " (CC0 project; brands keep their trademarks, see simpleicons.org DISCLAIMER). "
          "Give the link or button its own accessible name, e.g. aria-label=\"แชทกับเราทาง LINE\". -->")
    return 1 if bad else 0


HEX = re.compile(r"#?(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})")


def main():
    a = sys.argv[1:]
    if not a or a[0] not in ("search", "lucide", "brand"):
        print(__doc__); return 2
    g = arg("--ground")
    if g is not None and not HEX.fullmatch(g):
        print(f"usage: --ground takes a hex colour, #rgb or #rrggbb (got {g!r})", file=sys.stderr); return 2
    lv, sv = arg("--lucide-version", LUCIDE_V), arg("--simple-version", SIMPLE_V)
    w = words(sys.argv)[2:]
    if not w:
        print(__doc__); return 2
    try:
        return {"search": lambda: search(w, lv, sv), "lucide": lambda: lucide(w, lv), "brand": lambda: brand(w, sv)}[a[0]]()
    except RuntimeError as e:
        print(f"NOT RUN: {e}"); return 3


if __name__ == "__main__":
    sys.exit(main())
