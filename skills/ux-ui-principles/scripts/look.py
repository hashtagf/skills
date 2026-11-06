#!/usr/bin/env python3
"""Look before you build: list the pictures to open for a kind of page.

Usage:
  python3 scripts/look.py <kind> [--direction <id>] [--n 3]
  python3 scripts/look.py --kinds

Prints absolute paths of real designed pages of that kind (assets/references, plus the showcase study set when
it has been fetched locally), what to take from each, and, with --direction, that direction's preview, its
product UI preview and its composition. Open (Read) every listed image before writing code; then say in the
answer which ones you looked at and the one move you are taking from them.

Kinds: landing, pricing, campaign, editorial, report, deck, product, mobile, portfolio, destination, nonprofit,
game, document (synonyms: dashboard/admin/back office -> product, blog/article/magazine -> editorial,
slides/presentation -> deck, app -> mobile, cafe/coffee/roastery/bakery/shop -> cafe + landing, hotel/restaurant/travel -> destination + landing, waitlist -> landing).

Market studies (assets/market/catalog.json): when the kind or a synonym has a study (clinic: dental, dentist,
medical, ทันตกรรม ...), it also prints the category look, the gaps, checked facts and the screenshots of
design-led and category sites. No study yet: run the market research in design-direction.md §9 Round B.
Standard library only.
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SYN = {
    "dashboard": ["product", "report"], "admin": ["product"], "backoffice": ["product"], "back-office": ["product"],
    "blog": ["editorial"], "article": ["editorial"], "magazine": ["editorial"], "docs": ["editorial", "landing"],
    "slides": ["deck"], "presentation": ["deck"], "app": ["mobile", "product"], "onboarding": ["mobile"],
    "hotel": ["destination", "landing"], "restaurant": ["destination", "landing"], "cafe": ["cafe", "landing"], "coffee": ["cafe", "landing"], "roastery": ["cafe", "landing"], "bakery": ["cafe", "landing"], "shop": ["cafe", "landing"],
    "travel": ["destination", "landing"], "waitlist": ["landing"], "saas": ["landing", "pricing"],
    "agency": ["portfolio", "landing"], "studio": ["portfolio", "landing"], "invoice": ["document"], "resume": ["document"],
    "cover": ["deck", "report"], "event": ["campaign", "landing"],
}


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def references():
    rows, readme = [], os.path.join(ROOT, "assets", "references", "README.md")
    for line in open(readme, encoding="utf-8"):
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(c\d+)\s*\|\s*(.+?)\s*\|\s*$", line)
        if m:
            name, kind, comp, why = m.groups()
            rows.append({"kind": kind, "comp": comp, "why": why, "src": "reference",
                         "img": os.path.join(ROOT, "assets", "references", name + ".jpg"),
                         "full": os.path.join(ROOT, "assets", "references", name + "-full.jpg")})
    return rows


def showcase():
    p = os.path.join(ROOT, "assets", "showcase", "catalog.json")
    if not os.path.exists(p):
        return []
    out = []
    for r in json.load(open(p, encoding="utf-8")):
        if r.get("verdict") != "template" or not r.get("img"):
            continue
        img = os.path.join(ROOT, "assets", "showcase", r["img"])
        kind = {"destination": "destination", "nonprofit": "nonprofit", "portfolio": "portfolio", "game": "game"}.get(r["kind"], r["kind"])
        out.append({"kind": kind, "comp": r.get("comp") or "", "why": r["note"], "src": "showcase " + r["url"], "img": img,
                    "full": os.path.join(ROOT, "assets", "showcase", r["img_full"]) if r.get("img_full") else ""})
    return out


def market(want):
    p = os.path.join(ROOT, "assets", "market", "catalog.json")
    if not os.path.exists(p):
        return None, None
    for kind, k in json.load(open(p, encoding="utf-8"))["kinds"].items():
        if want == kind or want in k.get("synonyms", []):
            return kind, k
    return None, None


def print_market(kind, k, n):
    img = os.path.join(ROOT, "assets", "market", "img")
    print(f"\nMarket study: {kind} (studied {k['studied']}; assets/market/catalog.json)")
    print(f"  category look (do not default to it): {k['category_look']}")
    print(f"  design-led moves: {k['designed_moves']}")
    print("  gaps a new page can own:")
    for g in k["gaps"]:
        print(f"    - {g}")
    print("  checked facts (re-check if older than a year; cite on the page):")
    for f in k.get("facts", []):
        print(f"    - {f['fact']}  [{f['checked']}; {f['source']}]")
    missing = False
    for verdict, cap in (("designed", n), ("category", 2)):
        print(f"  {verdict} sites (open both pictures of each):")
        for s in [s for s in k["sites"] if s["verdict"] == verdict][:cap]:
            p1 = os.path.join(img, f"{kind}-{s['slug']}-1.jpg")
            missing |= not os.path.exists(p1)
            print(f"    - {p1}{'' if os.path.exists(p1) else '   (not shot)'}\n        {s['url']} · {s['region']} · take: {s['note']}")
    if missing:
        print(f"  pictures missing: node scripts/market_fetch.js --kind {kind}")


def main():
    rows = references() + showcase()
    kinds = sorted({r["kind"] for r in rows})
    if "--kinds" in sys.argv or len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print("kinds:", ", ".join(kinds)); print("synonyms:", ", ".join(sorted(SYN))); return 0
    want = sys.argv[1].lower()
    mkind, mstudy = market(want)
    targets = SYN.get(want, ["landing"] if mstudy else [want])
    n = int(arg("--n", "3"))
    picked = []
    for t in targets:
        pool = [r for r in rows if r["kind"] == t and os.path.exists(r["img"])]
        pool.sort(key=lambda r: (r["src"] != "reference",))  # references first, then showcase
        picked += pool[:n]
    if not picked and not mstudy:
        print(f"No pictures for '{want}'. Kinds: {', '.join(kinds)}")
        print("No market study either: run the market research (design-direction.md §9 Round B) and record it with scripts/market_fetch.js.")
        return 1
    print(f"Open every image below before building ({want}). Then name the one move you take from them.\n")
    for r in picked:
        print(f"- {r['img']}\n    {r['kind']} · composition {r['comp'] or '-'} · {r['src']}\n    take: {r['why']}")
        if r.get("full") and os.path.exists(r["full"]):
            print(f"    longer view: {r['full']}")
    if mstudy:
        print_market(mkind, mstudy, n)
    d = arg("--direction")
    if d:
        data = json.load(open(os.path.join(ROOT, "assets", "directions", "directions.json"), encoding="utf-8"))["directions"]
        x = next((y for y in data if y["id"] == d), None)
        if not x:
            print(f"\nunknown direction {d}"); return 1
        prev = os.path.join(ROOT, "assets", "directions", "previews")
        print(f"\nDirection {x['name']} ({x['group']}): composition {x.get('comp')} on '{x.get('subject')}'")
        for p in (os.path.join(prev, d + ".jpg"), os.path.join(prev, "product", d + "-overview.jpg")):
            print(f"- {p}" + ("" if os.path.exists(p) else "   (not built: node scripts/build_previews.js --only directions,brand)"))
        print(f"  recipe: python3 scripts/direction_recipe.py {d}")
        print(f"  start from: scripts/compositions.js {x.get('comp')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
