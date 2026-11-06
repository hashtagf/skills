#!/usr/bin/env python3
"""Look before you build: list the pictures to open for a kind of page.

Usage:
  python3 scripts/look.py <kind> [--direction <id>] [--n 3]
  python3 scripts/look.py --kinds

Prints absolute paths of real designed pages of that kind (assets/references, plus the showcase study set when
it has been fetched locally), what to take from each, and, with --direction, that direction's preview, its
product UI preview and its composition. Open (Read) every listed image before writing code; then say in the
answer which ones you looked at and the one move you are taking from them.

Kinds (run --kinds for the current list): landing, pricing, campaign, editorial, report, cover, deck, product,
mobile, portfolio, destination, nonprofit, game, cafe. A word that is a kind always shows that kind; a synonym
adds kinds to it (cover -> cover + deck + report). Synonyms: dashboard/admin/back office -> product,
blog/article/magazine -> editorial, slides/presentation -> deck, app -> mobile, cafe/coffee/roastery/bakery/shop
-> cafe + landing, hotel/restaurant/travel -> destination + landing, waitlist -> landing. Thai words work too:
คาเฟ่/ร้านกาแฟ/เบเกอรี่, แลนดิ้ง/หน้าแรก, แดชบอร์ด/หลังบ้าน, สไลด์/พรีเซนต์, พอร์ต, โรงแรม/ร้านอาหาร/ท่องเที่ยว,
รายงาน, ราคา, บทความ, แอป, ปก, เอกสาร.
document, invoice and resume have no pictures yet: the script says so and shows the nearest kinds (report,
cover). Exit 0 with pictures or a market study, 2 for an unknown kind, direction or bad flag.

Market studies (assets/market/catalog.json): when the kind or a synonym has a study (clinic: dental, dentist,
medical, ทันตกรรม ...), it also prints the category look, the gaps, checked facts and the screenshots of
design-led and category sites. No study yet: run the market research in design-direction.md §9 Round B.
Standard library only.
"""
import argparse, json, os, re, sys

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
    "document": ["report", "cover"], "back office": ["product"],
    # Thai
    "คาเฟ่": ["cafe", "landing"], "ร้านกาแฟ": ["cafe", "landing"], "กาแฟ": ["cafe", "landing"], "เบเกอรี่": ["cafe", "landing"],
    "แลนดิ้ง": ["landing"], "แลนดิ้งเพจ": ["landing"], "หน้าแรก": ["landing"],
    "แดชบอร์ด": ["product", "report"], "หลังบ้าน": ["product"], "ระบบหลังบ้าน": ["product"],
    "สไลด์": ["deck"], "พรีเซนต์": ["deck"], "พรีเซนเทชัน": ["deck"], "พอร์ต": ["portfolio"], "พอร์ตโฟลิโอ": ["portfolio"],
    "โรงแรม": ["destination", "landing"], "ร้านอาหาร": ["destination", "landing"], "ท่องเที่ยว": ["destination", "landing"],
    "รายงาน": ["report"], "ราคา": ["pricing"], "แพ็กเกจ": ["pricing"], "บทความ": ["editorial"], "บล็อก": ["editorial"],
    "แอป": ["mobile", "product"], "ปก": ["cover"], "เอกสาร": ["report", "cover"], "ใบแจ้งหนี้": ["report", "cover"],
    "เรซูเม่": ["report", "cover"],
}
# words with no pictures of their own yet: say so and show the nearest kinds
NO_PICTURES = {"document": "document", "invoice": "invoice", "resume": "resume", "เอกสาร": "document",
               "ใบแจ้งหนี้": "invoice", "เรซูเม่": "resume"}
SYN.update({"invoice": ["report", "cover"], "resume": ["report", "cover"]})


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write("error: %s (run with --help)\n" % message)
        sys.exit(2)


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
        out.append({"kind": r["kind"], "comp": r.get("comp") or "", "why": r["note"], "src": "showcase " + r["url"], "img": img,
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


def main(argv=None):
    ap = Parser(prog="look.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", nargs="*", help="kind of page or a synonym (one or more words)")
    ap.add_argument("--direction", help="direction id: also print its previews and recipe")
    ap.add_argument("--n", type=int, default=3, help="pictures per kind (default 3)")
    ap.add_argument("--kinds", action="store_true", help="list kinds and synonyms")
    a = ap.parse_args(argv)
    if a.n < 1:
        ap.error("--n must be 1 or more")
    rows = references() + showcase()
    kinds = sorted({r["kind"] for r in rows})
    if a.kinds or not a.kind:
        print("kinds:", ", ".join(kinds)); print("synonyms:", ", ".join(sorted(SYN))); return 0
    want = " ".join(a.kind).strip().lower()
    if want not in SYN and want not in kinds:
        want = want.replace(" ", "-") if want.replace(" ", "-") in SYN else want
    mkind, mstudy = market(want)
    targets = ([want] if want in kinds else []) + [t for t in SYN.get(want, []) if t != want]
    if not targets and mstudy:
        targets = ["landing"]
    n = a.n
    picked = []
    for t in targets:
        pool = [r for r in rows if r["kind"] == t and os.path.exists(r["img"])]
        pool.sort(key=lambda r: (r["src"] != "reference",))  # references first, then showcase
        picked += pool[:n]
    if not picked and not mstudy:
        print(f"error: no pictures for '{want}' (kinds: {', '.join(kinds)}; synonyms: --kinds)", file=sys.stderr)
        print("No market study either: run the market research (design-direction.md §9 Round B) and record it with scripts/market_fetch.js.", file=sys.stderr)
        return 2
    if want in NO_PICTURES:
        print(f"No pictures for {NO_PICTURES[want]} yet; nearest: {', '.join(targets)}. Take layout and type moves from them, not the page kind.\n")
    print(f"Open every image below before building ({want}). Then name the one move you take from them.\n")
    for r in picked:
        print(f"- {r['img']}\n    {r['kind']} · composition {r['comp'] or '-'} · {r['src']}\n    take: {r['why']}")
        if r.get("full") and os.path.exists(r["full"]):
            print(f"    longer view: {r['full']}")
    if mstudy:
        print_market(mkind, mstudy, n)
    d = a.direction
    if d:
        data = json.load(open(os.path.join(ROOT, "assets", "directions", "directions.json"), encoding="utf-8"))["directions"]
        x = next((y for y in data if y["id"] == d), None)
        if not x:
            print(f"error: unknown direction {d!r} (python3 scripts/export_tokens.py --list)", file=sys.stderr); return 2
        prev = os.path.join(ROOT, "assets", "directions", "previews")
        print(f"\nDirection {x['name']} ({x['group']}): composition {x.get('comp')} on '{x.get('subject')}'")
        for p in (os.path.join(prev, d + ".jpg"), os.path.join(prev, "product", d + "-overview.jpg")):
            print(f"- {p}" + ("" if os.path.exists(p) else "   (not built: node scripts/build_previews.js --only directions,brand)"))
        print(f"  recipe: python3 scripts/direction_recipe.py {d}")
        print(f"  start from: scripts/compositions.js {x.get('comp')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
