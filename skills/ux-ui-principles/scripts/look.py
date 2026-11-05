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


def main():
    rows = references() + showcase()
    kinds = sorted({r["kind"] for r in rows})
    if "--kinds" in sys.argv or len(sys.argv) < 2 or sys.argv[1].startswith("-"):
        print("kinds:", ", ".join(kinds)); print("synonyms:", ", ".join(sorted(SYN))); return 0
    want = sys.argv[1].lower()
    targets = SYN.get(want, [want])
    n = int(arg("--n", "3"))
    picked = []
    for t in targets:
        pool = [r for r in rows if r["kind"] == t and os.path.exists(r["img"])]
        pool.sort(key=lambda r: (r["src"] != "reference",))  # references first, then showcase
        picked += pool[:n]
    if not picked:
        print(f"No pictures for '{want}'. Kinds: {', '.join(kinds)}"); return 1
    print(f"Open every image below before building ({want}). Then name the one move you take from them.\n")
    for r in picked:
        print(f"- {r['img']}\n    {r['kind']} · composition {r['comp'] or '-'} · {r['src']}\n    take: {r['why']}")
        if r.get("full") and os.path.exists(r["full"]):
            print(f"    longer view: {r['full']}")
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
