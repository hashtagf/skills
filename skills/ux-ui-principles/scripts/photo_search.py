#!/usr/bin/env python3
"""Find open-licensed photographs of the subject's world (references/visual-assets.md §2b).

Usage:
  python3 scripts/photo_search.py "dental treatment room" ["dentist child" ...] [--source commons|openverse|both]
          [--n 8] [--min-width 1000] [--download DIR] [--pick 1,3] [--name dental-room,dental-chair]

Searches Wikimedia Commons (and Openverse) and keeps only licences a commercial page may use: CC0, public domain,
CC BY and CC BY-SA. Non-commercial (NC), no-derivatives (ND) and unknown licences are dropped. Prints per hit:
number, title, licence, creator, size, file page and a 1280px picture URL.

Look at the candidates before choosing (download a few, open them): reject clutter, staged stock, people who
could be mistaken for the client's staff or patients, and anything that does not show the subject's world.
--download DIR saves the --pick'ed hits (default all) as DIR/<name>.jpg and merges their credits into
DIR/credits.json ({name: {title, artist, license, page}}), the format assets/photos/credits.json uses.
Credit every photo on the page (footer line) and list it in the hand-off as a stand-in to replace.

Network: curl (system certificates) to the Commons API and api.openverse.org, anonymous, one request per query.
Standard library only.
"""
import json, os, re, subprocess, sys, urllib.parse

UA = "ux-ui-principles-skill/1.0 (photo search for design work)"
ALLOWED = re.compile(r"^(cc0|cc[- ]?zero|public domain|pd|pdm|cc[- ]by(-sa)?([- ][0-9.]+)?|by(-sa)?)$", re.I)


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def get(url):
    # curl uses the system certificates (Python's own store is often missing on macOS)
    r = subprocess.run(["curl", "-sSL", "--fail", "--max-time", "60", "-A", UA, url], capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode("utf-8", "replace").strip() or f"curl exit {r.returncode}")
    return r.stdout


def clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", html or "")).strip()


def ok_license(name):
    n = (name or "").strip()
    if re.search(r"\b(nc|nd)\b|non-?commercial|no ?deriv", n, re.I):
        return False
    return bool(ALLOWED.match(n)) or n.lower().startswith(("public domain", "cc by", "cc-by", "cc0"))


def commons(q, n, min_w):
    params = {"action": "query", "generator": "search", "gsrsearch": q + " filetype:bitmap", "gsrnamespace": 6,
              "gsrlimit": n * 3, "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1280, "format": "json"}
    data = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(params)))
    out = []
    for p in sorted(data.get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
        lic = clean(m.get("LicenseShortName", {}).get("value"))
        if ii["width"] < min_w or not ok_license(lic):
            continue
        out.append({"source": "commons", "title": p["title"].replace("File:", ""), "license": lic,
                    "artist": clean(m.get("Artist", {}).get("value")) or "unknown", "w": ii["width"], "h": ii["height"],
                    "page": ii["descriptionurl"], "img": ii.get("thumburl") or ii["url"]})
    return out[:n]


def openverse(q, n, min_w):
    params = {"q": q, "license": "cc0,pdm,by,by-sa", "page_size": n * 2, "mature": "false"}
    data = json.loads(get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(params)))
    out = []
    for r in data.get("results", []):
        lic = (r.get("license") or "").lower()
        name = {"cc0": "CC0", "pdm": "Public domain"}.get(lic, "CC " + lic.upper() + (" " + r["license_version"] if r.get("license_version") else ""))
        if (r.get("width") or min_w) < min_w or not ok_license(name):
            continue
        out.append({"source": "openverse/" + (r.get("provider") or "?"), "title": r.get("title") or r["id"], "license": name,
                    "artist": r.get("creator") or "unknown", "w": r.get("width"), "h": r.get("height"),
                    "page": r.get("foreign_landing_url") or r.get("url"), "img": r.get("url")})
    return out[:n]


def main():
    qs = [a for i, a in enumerate(sys.argv[1:], 1) if not a.startswith("--") and sys.argv[i - 1] not in
          ("--source", "--n", "--min-width", "--download", "--pick", "--name")]
    if not qs:
        print(__doc__); return 2
    src, n, min_w = arg("--source", "commons"), int(arg("--n", "8")), int(arg("--min-width", "1000"))
    hits = []
    for q in qs:
        for fn in ([commons] if src == "commons" else [openverse] if src == "openverse" else [commons, openverse]):
            try:
                hits += fn(q, n, min_w)
            except Exception as e:  # network or API change: say so, keep the other source
                print(f"[{fn.__name__}] '{q}' failed: {e}")
    if not hits:
        print("No usable hits. Search the subject's world (the room, the tool, the material), not the category."); return 1
    for i, h in enumerate(hits, 1):
        print(f"{i:>2}. {h['title'][:90]}\n    {h['license']} · {h['artist'][:60]} · {h['w']}x{h['h']} · {h['source']}\n    page: {h['page']}\n    img:  {h['img']}")
    out = arg("--download")
    if not out:
        print("\nNext: --download DIR --pick 2,5 --name a,b, then open each picture before using it."); return 0
    picks = [int(x) for x in arg("--pick", ",".join(str(i) for i in range(1, len(hits) + 1))).split(",")]
    names = (arg("--name") or "").split(",") if arg("--name") else []
    os.makedirs(out, exist_ok=True)
    cpath = os.path.join(out, "credits.json")
    credits = json.load(open(cpath, encoding="utf-8")) if os.path.exists(cpath) else {}
    for j, k in enumerate(picks):
        h = hits[k - 1]
        name = names[j] if j < len(names) and names[j] else re.sub(r"[^a-z0-9]+", "-", h["title"].lower())[:40].strip("-")
        body = get(h["img"])
        if not body[:3] == b"\xff\xd8\xff" and not body[:8] == b"\x89PNG\r\n\x1a\n":
            print(f"skip {name}: not an image (the server returned something else)"); continue
        ext = ".png" if body[:4] == b"\x89PNG" else ".jpg"
        open(os.path.join(out, name + ext), "wb").write(body)
        credits[name] = {"title": h["title"], "artist": h["artist"], "license": h["license"], "page": h["page"]}
        print(f"saved {os.path.join(out, name + ext)}  ({h['license']}, {h['artist'][:40]})")
    json.dump(credits, open(cpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"credits → {cpath}. Footer line: 'ภาพ: <artist> (<licence>)' linked to each page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
