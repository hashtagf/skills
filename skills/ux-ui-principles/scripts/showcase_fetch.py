#!/usr/bin/env python3
"""Fetch the Open Design showcase (https://open-design.ai/showcase/) as a local study set.

Usage:
  python3 scripts/showcase_fetch.py [--out assets/showcase] [--limit 100] [--delay 1.0]

For every item on the showcase index: title, type, attribution and licence lines, the "how to create" brief
(the page's own design notes), and its pictures (first view + full page), resized. Writes
<out>/items.json and <out>/img/<slug>.jpg + <slug>-full.jpg.

Pictures are a STUDY SET, not assets: each item's licence covers the plugin, "not every depicted asset", so the
pictures stay local (git-ignored) and are never copied into client work. Re-run to refresh.
Network: curl (system certificates). Pillow resizes the pictures. Be polite: one request per --delay seconds.
"""
import html, io, json, os, re, subprocess, sys, time

BASE = "https://open-design.ai"
UA = "Mozilla/5.0 (design study; ux-ui-principles skill)"


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def get_bytes(url):
    return subprocess.run(["curl", "-sL", "--max-time", "60", "-A", UA, url], capture_output=True).stdout


def get(url):
    return get_bytes(url).decode("utf-8", "replace")


SKIP = re.compile(r"^(Tip:|Gallery|Download and Install|Export and Get|Related|More |Designed For|Highlights)", re.I)


def sections(page):
    """[{h, text}] for every h2/h3 between the title and the related-items list."""
    parts = re.split(r"(<h[23][^>]*>.*?</h[23]>)", page, flags=re.S)
    out, head = [], None
    for part in parts:
        m = re.match(r"<h([23])[^>]*>(.*?)</h[23]>", part, re.S)
        if m:
            head = text_of(m.group(2))
            if re.match(r"^(Related|More )", head):
                break
            continue
        if head and not SKIP.match(head):
            body = text_of(part)
            if body:
                out.append({"h": head, "text": body[:1500]})
    return out


def text_of(fragment):
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", fragment, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t).strip()


def main():
    out = os.path.abspath(arg("--out", os.path.join(os.path.dirname(__file__), "..", "assets", "showcase")))
    limit, delay = int(arg("--limit", "100")), float(arg("--delay", "1.0"))
    os.makedirs(os.path.join(out, "img"), exist_ok=True)
    index = get(BASE + "/showcase/?type=all")
    slugs = sorted(set(re.findall(r'href="/showcase/([a-z0-9-]+)/"', index)))[:limit]
    from PIL import Image
    items = []
    for n, slug in enumerate(slugs, 1):
        page = get(f"{BASE}/showcase/{slug}/")
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", page, re.S)
        imgs = re.findall(r'src="(/showcase/generated/[^"]+\.(?:png|jpe?g|webp))"', page)
        view = next((u for u in imgs if "view-1" in u), imgs[0] if imgs else None)
        full = next((u for u in imgs if "full-page" in u), None)
        item = {
            "slug": slug, "title": text_of(h1.group(1)) if h1 else slug,
            "type": slug.replace("-design", "").split("-")[-1],
            "url": f"{BASE}/showcase/{slug}/",
            "sections": sections(page),
            "view": view and BASE + view, "full": full and BASE + full,
        }
        for key, url, w, cap in (("img", item["view"], 1440, 1000), ("img_full", item["full"], 960, 2800)):
            if not url:
                continue
            raw = get_bytes(url)
            try:
                im = Image.open(io.BytesIO(raw)).convert("RGB")
            except Exception:
                continue
            if im.width > w:
                im = im.resize((w, round(im.height * w / im.width)))
            im = im.crop((0, 0, im.width, min(im.height, cap)))
            name = f"img/{slug}{'' if key == 'img' else '-full'}.jpg"
            im.save(os.path.join(out, name), "JPEG", quality=72, optimize=True)
            item[key] = name
            time.sleep(delay / 2)
        att = [x["text"] for x in item["sections"] if x["h"].lower().startswith("source and attribution")]
        item["attribution"] = att[0] if att else ""
        items.append(item)
        print(f"[{n}/{len(slugs)}] {slug} {'img' if item.get('img') else 'NO IMAGE'}", flush=True)
        json.dump(items, open(os.path.join(out, "items.json"), "w"), ensure_ascii=False, indent=1)
        time.sleep(delay)
    print("saved", len(items), "items to", out)


if __name__ == "__main__":
    main()
