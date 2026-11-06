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
    rc, out, err = py("look.py", "document")
    check("look.py document: 'no pictures for document yet; nearest: ...', exit 0, pictures listed",
          rc == 0 and "No pictures for document yet; nearest: report, cover" in out and "- /" in out, f"rc={rc} {out[:200]}")
    for word, kind in (("คาเฟ่", "cafe"), ("ร้านกาแฟ", "cafe"), ("เบเกอรี่", "cafe"), ("แลนดิ้ง", "landing"), ("หน้าแรก", "landing"),
                       ("แดชบอร์ด", "product"), ("หลังบ้าน", "product"), ("สไลด์", "deck"), ("พรีเซนต์", "deck"), ("พอร์ต", "portfolio"),
                       ("โรงแรม", "destination"), ("ร้านอาหาร", "destination"), ("ท่องเที่ยว", "destination"), ("รายงาน", "report"), ("ราคา", "pricing")):
        rc, out, err = py("look.py", word)
        kinds = re.findall(r"^\s{4}(\w+) · composition", out, re.M)
        check(f"look.py {word} -> {kind}", rc == 0 and kinds and kinds[0] == kind, f"rc={rc} {kinds}")
    src = open(os.path.join(SCRIPTS, "look.py"), encoding="utf-8").read()
    check("look.py: identity kind map removed", '{"destination": "destination"' not in src)


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


def main():
    global TMP
    TMP = tempfile.mkdtemp(prefix="ux-ui-test-py-tools-")
    try:
        for t in (test_net, test_color, test_usage, test_export, test_look, test_tweaks, test_code_extract, test_recipe):
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
