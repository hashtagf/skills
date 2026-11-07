#!/usr/bin/env python3
"""Regression cases for the non-checker Python tools: _net, _color, look, ds_lookup, halftone, export_tokens,
icons, photo_search, showcase_fetch, code_extract, design_md, direction_recipe, tweaks_panel.

Usage: python3 evals/regress/test_py_tools.py      (any cwd; writes only to a temp folder)

Shared contract checked here: exit 0 ok, 1 check failed, 2 usage or input error (one "error: ..." line, never a
Traceback), 3 not run. Fixtures live in evals/regress/py_tools/ and evals/fixtures/. One PASS / FAIL / NOT RUN
line per case; exit 1 on any FAIL. Standard library only (halftone cases need Pillow, NOT RUN without it).
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
FIX = os.path.join(HERE, "py_tools")
APPS = os.path.join(SKILL, "evals", "fixtures")
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPTS)
import _color  # noqa: E402
import _net  # noqa: E402

RESULTS = []
TMP = None


def report(status, name, detail=""):
    RESULTS.append(status)
    print(f"{status:7} {name}{'  (' + str(detail)[:400] + ')' if detail else ''}", flush=True)


def check(name, ok, detail=""):
    report("PASS" if ok else "FAIL", name, "" if ok else detail)


def py(script, *a, cwd=None, timeout=300):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *a], capture_output=True, text=True,
                       cwd=cwd or TMP, env=env, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


def usage_error(name, script, *a):
    rc, out, err = py(script, *a)
    check(f"{name}: exit 2, one 'error:' line, no Traceback",
          rc == 2 and "Traceback" not in out + err and err.strip().startswith("error:"), f"rc={rc} {(out + err)[-300:]}")


def front(md, key):
    m = re.search(r"^\s*%s:\s*\"?([^\"\n]*)\"?\s*$" % re.escape(key), md.split("\n---", 1)[0], re.M)
    return m.group(1) if m else None


# 1. _net: one curl wrapper, atomic cache, NotRun
def test_net():
    d = os.path.join(TMP, "cache")
    good = os.path.join(TMP, "good.json")
    with open(good, "w") as f:
        f.write('{"a": 1}')
    url = "file://" + good
    text = _net.cached(url, "x.json", d)
    check("_net.cached fetches and writes the cache file", json.loads(text) == {"a": 1} and os.path.getsize(os.path.join(d, "x.json")) > 0)
    open(os.path.join(d, "x.json"), "w").close()
    check("_net.cached: a 0-byte cache file is fetched again", _net.cached(url, "x.json", d) == text)
    with open(os.path.join(d, "x.json"), "w") as f:
        f.write("{broken")
    check("_net.cached: an invalid JSON cache file is fetched again", _net.cached(url, "x.json", d) == text)
    try:
        _net.cached("file:///nonexistent/ux-ui-nope.json", "nope.json", d)
        raised = False
    except _net.NetError:
        raised = True
    left = [f for f in os.listdir(d) if f == "nope.json" or f.startswith(".part-")]
    check("_net.cached: failed fetch raises NetError and leaves no file or temp part", raised and not left, left)
    try:
        _net.get("http://127.0.0.1:9/", timeout=5)
        kind = "none"
    except _net.NotRun:
        kind = "NotRun"
    except _net.NetError:
        kind = "NetError"
    check("_net.get: unreachable host raises NotRun (maps to exit 3)", kind == "NotRun" and _net.EXIT_NOT_RUN == 3, kind)
    dup = [s for s in ("icons.py", "photo_search.py", "showcase_fetch.py")
           if re.search(r"subprocess\.run\(\[\"curl\"", open(os.path.join(SCRIPTS, s), encoding="utf-8").read())]
    check("icons / photo_search / showcase_fetch have no curl helper of their own", not dup, dup)
    env = dict(os.environ, TMPDIR=os.path.join(TMP, "icons") + "/")
    os.makedirs(env["TMPDIR"], exist_ok=True)
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "icons.py"), "lucide", "phone", "--lucide-version", "0.0.0-nope"],
                       capture_output=True, text=True, env=env, cwd=TMP, timeout=90)
    check("icons.py failed CDN fetch: exit 3, NOT RUN line, no Traceback", r.returncode == 3 and "NOT RUN" in r.stdout and "Traceback" not in r.stderr,
          f"rc={r.returncode} {r.stdout[-200:]}{r.stderr[-200:]}")


# 2. colour maths in one place
def test_color():
    ok = (_color.hex_rgb("abc") == _color.hex_rgb("#aabbcc") and _color.hex_rgb("#aabbcc80") == _color.hex_rgb("#aabbcc")
          and _color.has_alpha("#aabbcc80") and not _color.has_alpha("#abc") and round(_color.ratio("#000", "#fff")) == 21
          and _color.luminance is _color.lum and _color.contrast is _color.ratio and _color.best_ink("#111") == "#ffffff")
    check("_color: 3/4/6/8-digit hex, alpha flag, ratio, aliases, best_ink", ok)
    own = []
    for s in ("icons.py", "tweaks_panel.py", "export_tokens.py", "design_md.py", "code_extract.py", "direction_recipe.py"):
        src = open(os.path.join(SCRIPTS, s), encoding="utf-8").read()
        own += [f"{s}:{m}" for m in re.findall(r"^def (lum|ratio|lin|delin|to_oklch|from_oklch|mix|reach|norm_hex|hex_rgb)\(", src, re.M)]
    check("no owned script defines its own luminance / contrast / OKLCH maths", not own, own)


# 3. bad input: exit 2, no Traceback
def test_usage():
    jpg = os.path.join(HERE, "preview", "tiny.jpg")
    usage_error("look.py trailing --n", "look.py", "landing", "--n")
    usage_error("look.py --n x", "look.py", "landing", "--n", "x")
    usage_error("look.py unknown kind", "look.py", "zzz-nothing")
    usage_error("ds_lookup --sub nosuch", "ds_lookup.py", "adeo-mozaic", "design-reference", "--sub", "nosuch")
    usage_error("ds_lookup --find '('", "ds_lookup.py", "--find", "(")
    usage_error("ds_lookup --max without value", "ds_lookup.py", "--find", "density", "--max")
    usage_error("ds_lookup unknown slug", "ds_lookup.py", "nope-nope")
    usage_error("halftone --ink red", "halftone.py", jpg, "o.jpg", "--ink", "red")
    usage_error("halftone --cell 0", "halftone.py", jpg, "o.jpg", "--cell", "0")
    usage_error("halftone missing picture", "halftone.py", "nope.jpg", "o.jpg")
    usage_error("export_tokens --only foo", "export_tokens.py", "cobalt", "--only", "foo")
    usage_error("export_tokens trailing --out", "export_tokens.py", "cobalt", "--out")
    usage_error("export_tokens --json oklch() value", "export_tokens.py", "--json", os.path.join(FIX, "tokens_oklch.json"))
    usage_error("export_tokens --json malformed", "export_tokens.py", "--json", os.path.join(FIX, "malformed.json"))
    usage_error("export_tokens --json missing accent", "export_tokens.py", "--json", os.path.join(FIX, "tokens_noaccent.json"))
    usage_error("export_tokens --json missing file", "export_tokens.py", "--json", "nope.json")
    usage_error("export_tokens unknown id", "export_tokens.py", "nope")
    usage_error("icons.py unknown subcommand", "icons.py", "nope", "x")
    usage_error("icons.py --size without value", "icons.py", "lucide", "phone", "--size")
    usage_error("icons.py --ground white", "icons.py", "brand", "line", "--ground", "white")
    usage_error("photo_search --n x", "photo_search.py", "room", "--n", "x")
    usage_error("photo_search --source nope", "photo_search.py", "room", "--source", "nope")
    usage_error("showcase_fetch --limit 0", "showcase_fetch.py", "--limit", "0")
    usage_error("direction_recipe unknown id", "direction_recipe.py", "nope")
    usage_error("direction_recipe trailing --out", "direction_recipe.py", "coral", "--out")
    usage_error("code_extract missing folder", "code_extract.py", "nope-dir")
    usage_error("design_md missing interview file", "design_md.py", "cobalt", "--interview", "nope.json", "--out", "x")
    usage_error("design_md malformed interview", "design_md.py", "cobalt", "--interview", os.path.join(FIX, "malformed.json"), "--out", "x")
    usage_error("design_md --from-code missing folder", "design_md.py", "--from-code", "nope-dir", "--out", "x")
    usage_error("design_md unknown direction", "design_md.py", "nope", "--interview", os.path.join(FIX, "iv_strings.json"), "--out", "x")
    usage_error("tweaks_panel missing page", "tweaks_panel.py", "nope.html")
    usage_error("tweaks_panel bad --presets", "tweaks_panel.py", os.path.join(FIX, "tweaks-page.html"), "--presets", "Bad:red", "--out", "t.html")
    rc, out, err = py("direction_recipe.py", "--out", "r.md", "coral")
    check("direction_recipe --out r.md coral (flag first) writes the recipe", rc == 0 and os.path.exists(os.path.join(TMP, "r.md")), f"rc={rc} {err}")
    try:
        import PIL  # noqa: F401
        rc, out, err = py("halftone.py", jpg, "h.jpg", "--size", "64", "--ink", "2a1410")
        check("halftone valid run (ink without #) writes the picture", rc == 0 and os.path.getsize(os.path.join(TMP, "h.jpg")) > 0, err)
    except ImportError:
        report("NOT RUN", "halftone valid run", "no Pillow")


# 4. export_tokens --only without --out; alpha warning; --json without id
def test_export():
    rc, out, err = py("export_tokens.py", "cobalt", "--only", "css,shadcn")
    heads = re.findall(r"^/\* ===== (\S+) ===== \*/$", out, re.M)
    check("export_tokens --only css,shadcn prints both files to stdout, one header each", rc == 0 and heads == ["tokens.css", "shadcn-globals.css"]
          and "@theme inline" in out, heads)
    rc, out, err = py("export_tokens.py", "cobalt", "--only", "tailwind")
    check("export_tokens --only tailwind prints only the Tailwind theme", rc == 0 and "tailwind-theme.css" in out and "--color-paper: oklch" not in out, out[:200])
    rc, out, err = py("export_tokens.py", "cobalt")
    check("export_tokens without --only still prints tokens.css only (no header)", rc == 0 and out.startswith("/* Tokens for direction") and "=====" not in out)
    rc, out, err = py("export_tokens.py", "--json", os.path.join(FIX, "tokens_alpha.json"))
    check("export_tokens --json without id works; #rrggbbaa warns that alpha is dropped",
          rc in (0, 1) and "Traceback" not in err and "has alpha" in err and 'direction "tokens_alpha"' in out, f"rc={rc} {err[-300:]}")


# 5. look.py
def test_look():
    rc, out, err = py("look.py", "cover")
    kinds = re.findall(r"^\s{4}(\w+) · composition", out, re.M)
    check("look.py cover shows the cover references first, synonyms add deck/report", rc == 0 and kinds[:2] == ["cover", "cover"] and "deck" in kinds, kinds)
    rc, out, err = py("look.py", "invoice")
    kinds = re.findall(r"^\s{4}(\w+) · composition", out, re.M)
    if any(r["kind"] == "document" and os.path.exists(r["img"]) for r in __import__("_library").load()):
        check("look.py invoice: document studies first, then report/cover; no false 'no pictures' note",
              rc == 0 and kinds[:1] == ["document"] and "report" in kinds and "No pictures for" not in out, f"rc={rc} {kinds}")
    else:
        check("look.py invoice without document pictures: 'no pictures for invoice yet; nearest: ...', exit 0",
              rc == 0 and "No pictures for invoice yet; nearest:" in out and "- /" in out, f"rc={rc} {out[:200]}")
    for word, kind in (("คาเฟ่", "cafe"), ("ร้านกาแฟ", "cafe"), ("เบเกอรี่", "cafe"), ("แลนดิ้ง", "landing"), ("หน้าแรก", "landing"),
                       ("แดชบอร์ด", "product"), ("หลังบ้าน", "product"), ("สไลด์", "deck"), ("พรีเซนต์", "deck"), ("พอร์ต", "portfolio"),
                       ("โรงแรม", "destination"), ("ร้านอาหาร", "destination"), ("ท่องเที่ยว", "destination"), ("รายงาน", "report"), ("ราคา", "pricing")):
        rc, out, err = py("look.py", word)
        kinds = re.findall(r"^\s{4}(\w+) · composition", out, re.M)
        check(f"look.py {word} -> {kind}", rc == 0 and kinds and kinds[0] == kind, f"rc={rc} {kinds}")
    src = open(os.path.join(SCRIPTS, "look.py"), encoding="utf-8").read()
    check("look.py: identity kind map removed", '{"destination": "destination"' not in src)
    # Mobbin catalog: integrity, tag lookup, fetch usage
    cat = json.load(open(os.path.join(SCRIPTS, "..", "assets", "mobbin", "catalog.json"), encoding="utf-8"))
    apps = cat["apps"]
    bad = [a["slug"] for a in apps if a["verdict"] not in ("template", "study", "skip") or len(a["screens"]) != 4
           or any(s["kind"] not in ("landing", "product", "auth") for s in a["screens"]) or not a["tags"] or not a["note"]]
    check("mobbin catalog: ranks 50-100, unique slugs, 4 typed screens, verdict, tags and note per app",
          [a["rank"] for a in apps] == list(range(50, 101)) and len({a["slug"] for a in apps}) == len(apps) and not bad, bad)
    have = os.path.exists(os.path.join(SCRIPTS, "..", "assets", "mobbin", "img", "twenty-1.jpg"))
    rc, out, err = py("look.py", "crm")
    apps_listed = re.findall(r"^    from: ([^,]+), screen \d+: https://mobbin", out, re.M)
    if have:
        check("look.py crm (a Mobbin tag) lists Mobbin screens, one per app, template first",
              rc == 0 and apps_listed and apps_listed[0].strip() == "Twenty" and len(apps_listed) == len(set(apps_listed)), f"rc={rc} {apps_listed}")
    else:
        check("look.py crm without Mobbin pictures: exit 2 with the fetch hint", rc == 2 and "mobbin_fetch.py" in err, f"rc={rc} {err[-200:]}")
    # one template library: every collection loads into the same row shape; look.py prints one format for all
    sys.path.insert(0, SCRIPTS)
    import _library
    rows = _library.load()
    keys = {"id", "app", "kind", "tags", "verdict", "take", "comp", "img", "full", "origin", "local", "source", "collection"}
    odd = [r["id"] for r in rows if set(r) != keys or r["verdict"] not in ("template", "study")
           or r["origin"] not in ("ours", "generated", "product")]
    check("_library.load: every collection yields the same row keys, verdict and origin",
          {r["collection"] for r in rows} >= {"references", "mobbin"} and not odd, odd[:5])
    rc, out, err = py("look.py", "dashboard")
    items = out.count("\n- /")
    check("look.py dashboard: every listed picture has one verdict/origin line and one from: credit",
          rc == 0 and items and out.count("\n    from: ") == items
          and len(re.findall(r"^    \w+ · composition \S+ · (?:template|study) · (?:our build|designed page|real product screen)$", out, re.M)) == items,
          f"rc={rc} items={items}")
    for doc in ("SKILL.md", os.path.join("references", "direction-library.md")):
        txt = open(os.path.join(SCRIPTS, "..", doc), encoding="utf-8").read()
        check(f"{doc} points at the template library, not at a collection", "assets/LIBRARY.md" in txt
              and "assets/mobbin/" not in txt and "assets/showcase/" not in txt)
    usage_error("mobbin_fetch.py missing --urls file", "mobbin_fetch.py", "--urls", os.path.join(TMP, "no-such-urls.json"))


# 6. tweaks_panel accent text / focus by contrast
def test_tweaks():
    page = os.path.join(TMP, "tw.html")
    shutil.copy(os.path.join(FIX, "tweaks-page.html"), page)
    rc, out, err = py("tweaks_panel.py", page, "--out", "tw-out.html", "--presets", "Sun:#f5c518,Rust:#c2410c,Mint:#3ddc97")
    html = open(os.path.join(TMP, "tw-out.html"), encoding="utf-8").read() if rc == 0 else ""
    m = re.search(r"PRE=(\[\[.*?\]\]),KEY=", html)
    pre = json.loads(m.group(1)) if m else []
    bad = []
    for name, acc, ink, tl, fl, td, fd in pre:
        for fg, bgs, need, what in ((ink, [acc], 4.5, "ink on accent"), (tl, ["#faf7ef", "#ffffff"], 4.5, "text light"),
                                    (fl, ["#faf7ef", "#ffffff"], 3.0, "focus light"), (td, ["#16130e", "#1f1b15"], 4.5, "text dark"),
                                    (fd, ["#16130e", "#1f1b15"], 3.0, "focus dark")):
            r = min(_color.ratio(fg, b) for b in bgs)
            if r < need:
                bad.append(f"{name} {what} {fg} {r:.2f}")
    check("tweaks_panel: per swatch, accent text 4.5:1 and focus 3:1 on paper+surface (light and dark), ink 4.5:1 on the accent",
          rc == 0 and len(pre) == 3 and not bad, bad or f"rc={rc} {err[-200:]}")
    check("tweaks_panel: the raw light accent is not used as text (Sun #f5c518 is moved)", pre and pre[0][3] != "#f5c518", pre[:1])
    check("tweaks_panel: the panel script sets text/focus from the swatch, not the raw accent",
          "root.style.setProperty(V.text,S.accent)" not in html and "p[3+2*d]" in html)


# 7. code_extract / design_md --from-code
def test_code_extract():
    rc, out, err = py("code_extract.py", os.path.join(APPS, "rn-app"), "--json")
    res = json.loads(out) if rc == 0 else {}
    stack = " ".join(res.get("stack", []))
    check("code_extract rn-app: stack names React Native and Expo", "React Native" in stack and "Expo" in stack, stack)
    check("code_extract rn-app: numeric radius 12 read from the theme object", "12px" in res.get("radii", {}), res.get("radii"))
    check("code_extract rn-app: theme-object colours found (primary #ff5a5f, on-surface #222222)",
          res.get("light", {}).get("primary") == "#ff5a5f" and res.get("light", {}).get("on-surface") == "#222222", res.get("light"))
    o = os.path.join(TMP, "rn-md")
    py("design_md.py", "--from-code", os.path.join(APPS, "rn-app"), "--out", o)
    md = open(os.path.join(o, "DESIGN.md"), encoding="utf-8").read() if os.path.exists(os.path.join(o, "DESIGN.md")) else ""
    check("design_md --from-code rn-app: radius 12px from code", front(md, "md") == "12px", front(md, "md"))
    rc, out, err = py("code_extract.py", os.path.join(APPS, "thai-form"), "--json")
    res = json.loads(out) if rc == 0 else {}
    check("code_extract thai-form: Thai detected from lang=\"th\"", res.get("language", {}).get("thai") is True, res.get("language"))
    o = os.path.join(TMP, "th-md")
    py("design_md.py", "--from-code", os.path.join(APPS, "thai-form"), "--out", o)
    md = open(os.path.join(o, "DESIGN.md"), encoding="utf-8").read() if os.path.exists(os.path.join(o, "DESIGN.md")) else ""
    body = re.search(r"body-md:\n(?:\s{4}.*\n)*?\s{4}lineHeight: ([\d.]+)", md)
    check("design_md --from-code thai-form: body line-height 1.6 (not 1.5)", body and body.group(1) == "1.6", body and body.group(1))
    check("design_md --from-code thai-form: no '8px from the most used border-radius' when none exist",
          "the most used border-radius" not in md and "no radius found in code" in md, re.findall(r"- Base radius.*", md))
    rc, out, err = py("code_extract.py", os.path.join(APPS, "checkout"), "--json")
    res = json.loads(out) if rc == 0 else {}
    L, ev = res.get("light", {}), res.get("light_evidence", {})
    ink, canvas = L.get("on-surface"), L.get("canvas")
    check("code_extract checkout: on-surface is not the 1.9:1 grey; it passes 4.5:1 or is a noted default",
          ink and ink != "#bbbbbb" and _color.ratio(ink, canvas) >= 4.5 and "4.5:1" in ev.get("on-surface", ""), (ink, ev.get("on-surface")))
    rc, out, err = py("code_extract.py", os.path.join(APPS, "rn-app"), "--json")
    res = json.loads(out) if rc == 0 else {}
    L = res.get("light", {})
    check("code_extract complete(): derived border is a light tint of ink, not full ink",
          L.get("border") not in (L.get("on-surface"), L.get("muted")) and _color.ratio(L["border"], L["canvas"]) < 1.5, (L.get("border"), L.get("canvas")))
    rc, out, err = py("code_extract.py", os.path.join(APPS, "landing-designmd"), "--json")
    res = json.loads(out) if rc == 0 else {}
    ex = [s for s in res.get("stack", []) if s.lower().startswith("existing") and "design.md" in s.lower()]
    check("code_extract: one 'existing DESIGN.md' entry (no duplicate on case-insensitive filesystems)", len(ex) == 1, res.get("stack"))


# 8. direction_recipe vs export_tokens; design_md interview strings
def test_recipe():
    import export_tokens
    rc, out, err = py("export_tokens.py", "--list")
    ids = [x.strip() for x in out.split(",") if x.strip()]
    bad = []
    for i in ids:
        rc, rec, err = py("direction_recipe.py", i)
        if rc or export_tokens.DISPLAY_CLAMP not in rec:
            bad.append(i)
    rc, css, err = py("export_tokens.py", "cobalt")
    check("direction_recipe display clamp == export_tokens --text-display for all %d directions" % len(ids),
          len(ids) >= 58 and not bad and "--text-display: %s" % export_tokens.DISPLAY_CLAMP in css, bad[:5])
    rc, rec, err = py("direction_recipe.py", "brutal")
    check("direction_recipe brutal: ink #000000 is not banned by its own recipe",
          "**ink** `#000000`" in rec and "pure #000 or #fff as text or ground" not in rec and "never pure black or white" not in rec, rec[:400])
    rc, rec, err = py("direction_recipe.py", "coral")
    check("direction_recipe coral (no pure colours): the plain ban stays", "pure #000 or #fff as text or ground" in rec)
    o = os.path.join(TMP, "ivs")
    rc, out, err = py("design_md.py", "cobalt", "--interview", os.path.join(FIX, "iv_strings.json"), "--out", o)
    md = open(os.path.join(o, "DESIGN.md"), encoding="utf-8").read() if rc == 0 else ""
    check("design_md: interview \"feel\": \"warm\" is one item, not letters", "- warm: warm neutrals" in md and "\n- w: " not in md, f"rc={rc} {err[-200:]}")
    check("design_md: \"languages\": \"th\" as a string turns on the Thai rules", "Thai: Noto Sans Thai" in md and "lineHeight: 1.6" in md)
    check("design_md: a bare 0 tracking is written 0em", not re.search(r"letterSpacing: 0\s*$", md, re.M))
    rc, out, err = py("design_md.py", "cobalt", "--interview", os.path.join(FIX, "iv_strings.json"), cwd=SKILL)
    check("design_md without --out refuses to write into the skill folder (exit 2)",
          rc == 2 and not os.path.exists(os.path.join(SKILL, "DESIGN.md")), f"rc={rc} {err}")


# 9. bug hunt: one case (or more) per fixed bug, temp fixtures only
def run_in(code, *a, env=None):
    """Run a few lines of Python with the scripts folder importable (stubs: look.ROOT, photo_search.get ...)."""
    r = subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, %r)\n%s" % (SCRIPTS, code), *a], capture_output=True,
                       text=True, cwd=TMP, env=dict(env or os.environ, PYTHONDONTWRITEBYTECODE="1"), timeout=120)
    return r.returncode, r.stdout, r.stderr


def look_at(root, *a):
    return run_in("import look; look.ROOT = sys.argv[1]; sys.exit(look.main(sys.argv[2:]))", root, *a)


def wfile(p, text):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)
    return p


def mobbin_root(name, apps, pictures=True):
    """A temp library root with only a Mobbin catalog (and, with pictures, a 1-byte file per screen)."""
    root = os.path.join(TMP, name)
    cat = {"apps": [{"slug": s, "name": s.title(), "verdict": v, "tags": t, "note": "n", "url": "https://mobbin.com/" + s,
                     "screens": [{"img": "img/%s-1.jpg" % s, "kind": "product"}]} for s, v, t in apps]}
    wfile(os.path.join(root, "assets", "mobbin", "catalog.json"), json.dumps(cat))
    if pictures:
        for s, _, _ in apps:
            wfile(os.path.join(root, "assets", "mobbin", "img", "%s-1.jpg" % s), "x")
    return root


def look_error(name, root, *a):
    rc, out, err = look_at(root, *a)
    check(name, rc == 2 and "Traceback" not in out + err and err.strip().startswith("error:") and "catalog.json" in err,
          f"rc={rc} {(out + err)[-300:]}")


PHOTO_STUB = """import json, photo_search as p
titles = json.loads(sys.argv[2])
p.commons = lambda q, n, m: [{"title": t, "artist": "a", "license": "CC0", "w": 1, "h": 1, "source": "commons",
                              "page": "page-%d" % i, "img": "https://x/%d" % i} for i, t in enumerate(titles)]
p.get = lambda u: b"\\xff\\xd8\\xff" + b"x" * 10
sys.exit(p.main(["q", "--source", "commons", "--download", sys.argv[1]]))
"""


def test_bugfixes():
    try:
        import PIL  # noqa: F401
        have_pil = True
    except ImportError:
        have_pil = False
    # bug 1: corrupt catalog.json -> one error line naming the file, exit 2; a missing catalog is still fine
    for label, text in (("'{bad'", "{bad"), ("'{}'", "{}"), ("'[]'", "[]"), ("empty", "")):
        root = os.path.join(TMP, "cat-" + str(len(label)) + label.strip("'{}[]") )
        wfile(os.path.join(root, "assets", "mobbin", "catalog.json"), text)
        look_error(f"bug1 look.py with a {label} mobbin catalog.json: error naming the file, exit 2", root, "landing")
        root2 = root + "-sc"
        wfile(os.path.join(root2, "assets", "showcase", "catalog.json"), text if text != "[]" else '{"x": 1}')
        look_error(f"bug1 look.py with a {label if text != '[]' else 'dict'} showcase catalog.json: error naming the file, exit 2", root2, "landing")
    root = os.path.join(TMP, "cat-market")
    wfile(os.path.join(root, "assets", "market", "catalog.json"), "[]")
    look_error("bug1 look.py with a '[]' market catalog.json: error naming the file, exit 2", root, "landing")
    rc, out, err = look_at(os.path.join(TMP, "cat-none"), "--kinds")
    check("bug1 look.py with no catalogs at all: --kinds exit 0", rc == 0 and "Traceback" not in err, f"rc={rc} {err[-200:]}")
    # bug 10: one pool across tag targets (chat + ai-chat): templates before the study
    root = mobbin_root("lib-chat", [("telegram", "study", ["chat"]), ("v0", "template", ["ai-chat"]), ("mistral", "template", ["ai-chat"])])
    rc, out, err = look_at(root, "chat", "--n", "2")
    apps = re.findall(r"^    from: ([^,]+), screen", out, re.M)
    check("bug10 look.py chat --n 2: templates (v0, mistral) before the study (telegram) across tags",
          rc == 0 and apps[:2] == ["V0", "Mistral"] and "Telegram" in apps[2:], f"rc={rc} {apps} {err[-200:]}")
    # bug 11: "ai chat" -> ai-chat, also for tags and kinds
    rc, out, err = look_at(root, "ai chat")
    check("bug11 look.py \"ai chat\" finds the ai-chat tag (space -> dash for tags too)", rc == 0 and "from: V0" in out, f"rc={rc} {err[-200:]}")
    # bug 12: the fetch hint without pictures (tag known from the catalog) and with no catalogs at all
    root = mobbin_root("lib-nopix", [("twenty", "template", ["crm"])], pictures=False)
    rc, out, err = look_at(root, "crm")
    check("bug12 look.py crm, catalog but no pictures: exit 2 with 'pictures not fetched' and mobbin_fetch.py",
          rc == 2 and "pictures not fetched" in err and "mobbin_fetch.py" in err, f"rc={rc} {err[-300:]}")
    rc, out, err = look_at(os.path.join(TMP, "cat-none"), "crm")
    check("bug12 look.py crm with no catalogs fetched: exit 2 with the fetch hint",
          rc == 2 and "pictures not fetched" in err and "fetch.py" in err, f"rc={rc} {err[-300:]}")
    # bug 18: --direction validated before anything is printed
    rc, out, err = py("look.py", "landing", "--direction", "nope")
    check("bug18 look.py --direction nope: exit 2, nothing on stdout", rc == 2 and out == "" and "unknown direction" in err, f"rc={rc} {out[:200]}")

    # bug 2 / 3: mobbin_fetch input validation (never the real assets: --out and --urls are temp paths)
    mout = os.path.join(TMP, "mb", "out")
    def urls(name, data):
        return wfile(os.path.join(TMP, "mb", name), data if isinstance(data, str) else json.dumps(data))
    good = urls("good.json", {"a": ["http://127.0.0.1:9/a.jpg"]})
    usage_error("bug2 mobbin_fetch urls.json '[]'", "mobbin_fetch.py", "--urls", urls("list.json", "[]"), "--out", mout)
    usage_error("bug2 mobbin_fetch --urls a folder", "mobbin_fetch.py", "--urls", os.path.join(TMP, "mb"), "--out", mout)
    usage_error("bug2 mobbin_fetch --delay nan", "mobbin_fetch.py", "--urls", good, "--out", mout, "--delay", "nan")
    usage_error("bug3 mobbin_fetch slug '../../escaped'", "mobbin_fetch.py", "--urls", urls("esc.json", {"../../escaped": ["http://127.0.0.1:9/a.jpg"]}), "--out", mout)
    check("bug3 mobbin_fetch: nothing written outside --out", not os.path.exists(os.path.join(TMP, "escaped-1.jpg")) and not os.path.exists(mout))
    usage_error("bug3 mobbin_fetch a string instead of a list", "mobbin_fetch.py", "--urls", urls("str.json", {"a": "http://127.0.0.1:9/a.jpg"}), "--out", mout)
    usage_error("bug3 mobbin_fetch a non-http URL", "mobbin_fetch.py", "--urls", urls("ftp.json", {"a": ["ftp://x/a.jpg"]}), "--out", mout)
    if have_pil:
        usage_error("bug2 mobbin_fetch --out an existing file", "mobbin_fetch.py", "--urls", good, "--out", good)
        ro = os.path.join(TMP, "mb", "ro")
        os.makedirs(ro)
        os.chmod(ro, 0o555)
        if os.access(ro, os.W_OK):
            report("NOT RUN", "bug2 mobbin_fetch read-only --out", "running as root")
        else:
            usage_error("bug2 mobbin_fetch read-only --out", "mobbin_fetch.py", "--urls", good, "--out", ro)
        os.chmod(ro, 0o755)
    else:
        report("NOT RUN", "bug2 mobbin_fetch --out a file / read-only", "no Pillow")

    # bug 4 / 5 / 16 / 17 / 19: design_md
    usage_error("bug4 design_md interview energy: [\"calm\"]", "design_md.py", "cobalt", "--interview", wfile(os.path.join(TMP, "iv-energy.json"), '{"energy": ["calm"]}'), "--out", "x4")
    usage_error("bug4 design_md interview brand: {}", "design_md.py", "cobalt", "--interview", wfile(os.path.join(TMP, "iv-brand.json"), '{"brand": {}}'), "--out", "x4")
    ivok = os.path.join(FIX, "iv_strings.json")
    afile = wfile(os.path.join(TMP, "afile"), "x")
    usage_error("bug5 design_md --out an existing file", "design_md.py", "cobalt", "--interview", ivok, "--out", afile)
    rod = os.path.join(TMP, "ro-out")
    os.makedirs(rod)
    os.chmod(rod, 0o555)
    if not os.access(rod, os.W_OK):
        usage_error("bug5 design_md read-only --out", "design_md.py", "cobalt", "--interview", ivok, "--out", rod)
    else:
        report("NOT RUN", "bug5 design_md read-only --out", "running as root")
    os.chmod(rod, 0o755)
    os.makedirs(os.path.join(TMP, "dirmd", "DESIGN.md"))
    usage_error("bug5 design_md DESIGN.md is a folder + --force", "design_md.py", "cobalt", "--interview", ivok, "--out", os.path.join(TMP, "dirmd"), "--force")
    o = os.path.join(TMP, "null-brand")
    rc, out, err = py("design_md.py", "cobalt", "--interview", wfile(os.path.join(TMP, "iv-null.json"), '{"brand": null, "goal": null}'), "--out", o)
    md = open(os.path.join(o, "DESIGN.md"), encoding="utf-8").read() if rc == 0 else ""
    check("bug16 design_md \"brand\": null uses the direction name, never \"None\"",
          rc == 0 and front(md, "name") == "Cobalt" and "None" not in md, f"rc={rc} {front(md, 'name')} {err[-200:]}")
    um = os.umask(0o022)
    os.umask(um)
    want_mode = 0o666 & ~um
    mode = os.stat(os.path.join(o, "DESIGN.md")).st_mode & 0o777 if rc == 0 else None
    check("bug19 design_md: DESIGN.md gets normal permissions (0666 & ~umask), not 0600", mode == want_mode, oct(mode or 0))
    rc, out, err = py("design_md.py", "cobalt", "--interview", ivok, "--out", os.path.join(TMP, "wired"), "--wire")
    ag = os.path.join(TMP, "wired", "AGENTS.md")
    check("bug19 design_md --wire: AGENTS.md written (atomic, normal mode)",
          rc == 0 and "design-md:start" in open(ag, encoding="utf-8").read() and os.stat(ag).st_mode & 0o777 == want_mode, f"rc={rc} {err[-200:]}")
    for script, a in (("design_md.py", ()), ("direction_recipe.py", ()), ("export_tokens.py", ()), ("icons.py", ()), ("photo_search.py", ())):
        rc, out, err = py(script, *a)
        check(f"bug17 {script} without required args: one 'error: ... (run with --help)' line on stderr, nothing on stdout, exit 2",
              rc == 2 and out == "" and err.strip().startswith("error:") and "--help" in err and len(err.strip().splitlines()) == 1,
              f"rc={rc} out={out[:80]!r} err={err[-200:]!r}")
        rc, out, err = py(script, "--help")
        check(f"bug17 {script} --help still prints the full help (exit 0)", rc == 0 and "Usage" in out and len(out.splitlines()) > 8, f"rc={rc}")

    # bug 19: _net.write_atomic and the other writers: normal mode, temp file + os.replace
    p = os.path.join(TMP, "wa", "f.txt")
    _net.write_atomic(p, "x")
    check("bug19 _net.write_atomic: file mode 0666 & ~umask (not 0600)", os.stat(p).st_mode & 0o777 == want_mode, oct(os.stat(p).st_mode & 0o777))
    rc, out, err = py("export_tokens.py", "cobalt", "--out", "tok")
    rc2, out2, err2 = py("direction_recipe.py", "coral", "--out", "rec.md")
    shutil.copy(os.path.join(FIX, "tweaks-page.html"), os.path.join(TMP, "twm.html"))
    rc3, out3, err3 = py("tweaks_panel.py", "twm.html", "--out", "twm-out.html")
    modes = [os.stat(os.path.join(TMP, f)).st_mode & 0o777 for f in ("tok/tokens.css", "rec.md", "twm-out.html") if os.path.exists(os.path.join(TMP, f))]
    plain = [s for s in ("export_tokens.py", "direction_recipe.py", "tweaks_panel.py", "design_md.py")
             if re.search(r"\bopen\([^)]*[\"']w[\"']", open(os.path.join(SCRIPTS, s), encoding="utf-8").read())]
    check("bug19 export_tokens / direction_recipe / tweaks_panel write atomically with normal modes (no plain open(..., 'w'))",
          (rc, rc2, rc3) == (0, 0, 0) and modes == [want_mode] * 3 and not plain, f"{(rc, rc2, rc3)} {[oct(m) for m in modes]} {plain}")

    # bug 6: package.json [] / dependencies null
    for label, pj in (("[]", "[]"), ("dependencies null", '{"dependencies": null, "devDependencies": ["x"]}')):
        src = os.path.join(TMP, "pj-" + label.replace(" ", "-").strip("[]") + "x")
        wfile(os.path.join(src, "package.json"), pj)
        wfile(os.path.join(src, "a.css"), ":root{--bg:#ffffff}")
        rc, out, err = py("code_extract.py", src, "--json")
        check(f"bug6 code_extract package.json {label}: treated as empty, exit 0", rc == 0 and "Traceback" not in err, f"rc={rc} {err[-200:]}")
        rc, out, err = py("design_md.py", "--from-code", src, "--out", os.path.join(src, "o"))
        check(f"bug6 design_md --from-code package.json {label}: exit 0", rc == 0 and "Traceback" not in err, f"rc={rc} {err[-200:]}")
    # bug 13: rgb() alpha percent
    import code_extract
    check("bug13 code_extract rgb(100 50 25 / 50%) -> #643219 (alpha % is not a channel %)",
          code_extract.to_hex("rgb(100 50 25 / 50%)") == "#643219" and code_extract.to_hex("rgb(100%, 0%, 0%)") == "#ff0000"
          and code_extract.to_hex("rgba(255, 0, 0, 50%)") == "#ff0000", code_extract.to_hex("rgb(100 50 25 / 50%)"))
    # bug 14: anchors / ids are not colours
    src = os.path.join(TMP, "anchors")
    wfile(os.path.join(src, "index.html"), '<style>#cafe { color: #123456 }</style><a href="#add">x</a><a id="#bad">y</a>'
          '<svg><rect fill="url(#cafe)"/></svg><script>document.querySelector("#bad")</script>')
    rc, out, err = py("code_extract.py", src, "--json")
    cols = set(json.loads(out).get("colors", {})) if rc == 0 else None
    check("bug14 code_extract: #add / #bad / #cafe in href, id, url(), selectors are not colours", cols == {"#123456"}, cols)
    # bug 7: halftone non-finite numbers
    jpg = os.path.join(HERE, "preview", "tiny.jpg")
    for flag, v in (("--bright", "nan"), ("--angle", "inf"), ("--angle", "nan"), ("--cell", "nan")):
        usage_error(f"bug7 halftone {flag} {v}", "halftone.py", jpg, "o7.jpg", flag, v)
    # bug 8 / 9: photo_search download names and credits (stubbed search and download, no network)
    d8 = os.path.join(TMP, "ph8")
    wfile(os.path.join(d8, "credits.json"), "[]")
    rc, out, err = run_in(PHOTO_STUB, d8, json.dumps(["a"]))
    check("bug8 photo_search credits.json [] : exit 2, error line, credits left as they were, nothing downloaded",
          rc == 2 and err.strip().startswith("error:") and open(os.path.join(d8, "credits.json")).read() == "[]"
          and os.listdir(d8) == ["credits.json"], f"rc={rc} {err[-200:]} {os.listdir(d8)}")
    d9 = os.path.join(TMP, "ph9")
    titles = ["วัดพระแก้ว", "ร้านกาแฟ", "Shop front.JPG", "Shop front.jpg", "!!!"]
    rc, out, err = run_in(PHOTO_STUB, d9, json.dumps(titles, ensure_ascii=False))
    files = sorted(os.listdir(d9)) if os.path.isdir(d9) else []
    cred = json.load(open(os.path.join(d9, "credits.json"), encoding="utf-8")) if "credits.json" in files else {}
    check("bug9 photo_search default names: Thai kept, extension dropped, collisions de-duplicated, never empty",
          rc == 0 and len(cred) == 5 and "" not in cred and ".jpg" not in files and "วัดพระแก้ว" in cred and "ร้านกาแฟ" in cred
          and "shop-front" in cred and "shop-front-2" in cred and any(k.startswith("photo-") for k in cred)
          and len([f for f in files if f.endswith(".jpg")]) == 5, f"rc={rc} {files} {err[-200:]}")
    rc, out, err = run_in(PHOTO_STUB, d9, json.dumps(["ร้านกาแฟ-new"], ensure_ascii=False))
    check("bug9 photo_search rerun: an existing photo's name is not overwritten by another photo",
          json.load(open(os.path.join(d9, "credits.json"), encoding="utf-8"))["ร้านกาแฟ"]["page"] == "page-1", err[-200:])
    # bug 15: 'İ' before </body> (lower() lengthens the string)
    page = wfile(os.path.join(TMP, "dotted.html"), "<html><head><style>:root{--accent:#c2410c}</style></head><body><p>" + "İ" * 40 + "</p></body></html>\n")
    rc, out, err = py("tweaks_panel.py", page, "--out", "dotted-out.html")
    html = open(os.path.join(TMP, "dotted-out.html"), encoding="utf-8").read() if rc == 0 else ""
    check("bug15 tweaks_panel with 'İ' in the page: panel inserted right before </body>, </html> intact",
          rc == 0 and html.rstrip().endswith("</body></html>") and 'id="tw"' in html and html.index('id="tw"') > html.index("İ" * 40), f"rc={rc} {html[-120:]!r}")
    # bug 16: export_tokens --json "display": null
    tj = json.load(open(os.path.join(FIX, "tokens_alpha.json"), encoding="utf-8"))
    tj = tj["directions"][0] if isinstance(tj, dict) and "directions" in tj else tj
    tj.update(display=None, body=None)
    rc, out, err = py("export_tokens.py", "--json", wfile(os.path.join(TMP, "tok-null.json"), json.dumps(tj)))
    check("bug16 export_tokens --json \"display\": null uses the default face, never \"None\"",
          rc in (0, 1) and "None" not in out and '--font-display: "Inter"' in out, f"rc={rc} {re.findall(r'--font-display:[^;]*', out)} {err[-200:]}")
    # bug 20: lucide names are case-insensitive (cache seeded in a temp TMPDIR, no network)
    tdir = os.path.join(TMP, "icons20") + "/"
    cache = os.path.join(tdir, "ux-ui-icons-cache")
    wfile(os.path.join(cache, "lucide-9.9.9-tags.json"), '{"calendar": ["date"], "calendar-check": ["date"]}')
    for n in ("calendar", "calendar-check"):
        wfile(os.path.join(cache, "lucide-9.9.9-%s.svg" % n), '<svg xmlns="http://www.w3.org/2000/svg"><rect width="1"/></svg>')
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, "icons.py"), "lucide", "Calendar", "CalendarCheck", "--lucide-version", "9.9.9"],
                       capture_output=True, text=True, cwd=TMP, env=dict(os.environ, TMPDIR=tdir), timeout=60)
    check("bug20 icons.py lucide Calendar CalendarCheck -> calendar, calendar-check (case normalised)",
          r.returncode == 0 and 'data-lucide="calendar"' in r.stdout and 'data-lucide="calendar-check"' in r.stdout, f"rc={r.returncode} {r.stdout[-200:]}")


def main():
    global TMP
    TMP = tempfile.mkdtemp(prefix="ux-ui-test-py-tools-")
    try:
        for t in (test_net, test_color, test_usage, test_export, test_look, test_tweaks, test_code_extract, test_recipe, test_bugfixes):
            try:
                t()
            except Exception as e:  # a crash in one group is a FAIL, the others still run
                report("FAIL", f"{t.__name__} crashed", repr(e))
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    nf = RESULTS.count("FAIL")
    print(f"{RESULTS.count('PASS')} pass, {nf} fail, {RESULTS.count('NOT RUN')} not run")
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
