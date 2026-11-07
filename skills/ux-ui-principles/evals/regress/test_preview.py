#!/usr/bin/env python3
"""Regression cases for the preview, asset and network scripts:
direction_preview.js, build_previews.js, backoffice_preview.js (--out / --singles), icons.py, photo_search.py, showcase_fetch.py.

Usage:
  python3 evals/regress/test_preview.py

One PASS / FAIL / NOT RUN line per case; exit 1 on any FAIL. Playwright cases need NODE_PATH or a local
playwright module (NOT RUN otherwise, exit 3 from the script); network cases need curl to reach the host
(NOT RUN otherwise). Runs from any cwd and writes only to a temp folder; at the end it checks that the
repo's assets/ (git status and the library preview files) did not change. Standard library only.
"""
import json, os, shutil, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, "..", ".."))
SCRIPTS = os.path.join(SKILL, "scripts")
FIX = os.path.join(HERE, "preview")
PREVIEWS = os.path.join(SKILL, "assets", "directions", "previews")
PHOTO_COMPS = {"c2", "c3", "c6", "c9", "c11", "c12", "c13"}
RESULTS = []


def report(status, name, detail=""):
    RESULTS.append(status)
    print(f"{status:7} {name}{'  (' + detail + ')' if detail else ''}", flush=True)


def check(name, ok, detail=""):
    report("PASS" if ok else "FAIL", name, "" if ok else detail)


def run(cmd, env=None, timeout=300, cwd=None):
    e = dict(os.environ)
    e.update(env or {})
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=e, timeout=timeout, cwd=cwd or TMP)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired as x:
        return -9, x.stdout or "", f"timeout after {timeout}s"


def node(script, *a, **kw):
    return run(["node", os.path.join(SCRIPTS, script), *a], **kw)


def py(script, *a, **kw):
    return run([sys.executable, os.path.join(SCRIPTS, script), *a], **kw)


def harness(code, **kw):
    """Run python code with the scripts folder importable (for offline fakes of network calls)."""
    return run([sys.executable, "-c", f"import sys; sys.path.insert(0, {SCRIPTS!r})\n" + code], **kw)


def online(url):
    try:
        return subprocess.run(["curl", "-sSI", "--fail", "--max-time", "10", url], capture_output=True).returncode == 0
    except OSError:
        return False


def snapshot():
    g = subprocess.run(["git", "-C", SKILL, "status", "--porcelain", "assets/"], capture_output=True, text=True).stdout
    files = {}
    if os.path.isdir(PREVIEWS):
        for f in os.listdir(PREVIEWS):
            p = os.path.join(PREVIEWS, f)
            if os.path.isfile(p):
                st = os.stat(p)
                files[f] = (st.st_size, st.st_mtime_ns)
    return g, files


def test_direction_preview():
    pw_env = {"TMPDIR": TMP + "/"}
    # 1: help, validation, default output
    rc, out, err = node("direction_preview.js", "--help", timeout=20)
    check("direction_preview --help prints usage, exit 0, renders nothing", rc == 0 and "Usage" in out and "→" not in out, f"rc={rc}")
    rc, out, err = node("direction_preview.js", "-h", timeout=20)
    check("direction_preview -h exit 0", rc == 0 and "Usage" in out, f"rc={rc}")
    rc, out, err = node("build_previews.js", "--help", timeout=20)
    check("build_previews --help prints usage, exit 0, runs nothing", rc == 0 and "Usage" in out and "> node" not in out, f"rc={rc}")
    rc, out, err = node("build_previews.js", "--only", "nope", timeout=20)
    check("build_previews --only <unknown> exit 2", rc == 2, f"rc={rc}")
    for name, a in (("unknown --ids entry", ["--ids", "dose,nope"]), ("unknown --comp", ["--ids", "dose", "--comp", "c99"]),
                    ("unknown --subject", ["--ids", "dose", "--subject", "nope"]), ("--ids without value", ["--ids"]),
                    ("unknown argument", ["--ids dose"])):
        rc, out, err = node("direction_preview.js", *a, timeout=20)
        check(f"direction_preview {name} exit 2", rc == 2 and "→" not in out, f"rc={rc} {err.strip()[:120]}")

    rc, out, err = node("direction_preview.js", "--ids", "dose", env=pw_env)
    tmp_root = os.path.join(TMP, "ux-ui-previews")
    said = [l for l in out.splitlines() if l.startswith("output: ")]
    check("--ids without --out announces a temp folder, not assets/", bool(said) and os.path.realpath(TMP) in os.path.realpath(said[0][8:].split(" (")[0]),
          out[:200])
    if rc == 3:
        report("NOT RUN", "--ids dose without --out renders into the temp folder", "no Playwright")
    else:
        made = [os.path.join(r, f) for r, _, fs in os.walk(tmp_root) for f in fs if f == "dose.jpg"]
        check("--ids dose without --out renders into the temp folder", rc == 0 and bool(made), f"rc={rc} {err[-200:]}")

    o = os.path.join(TMP, "dp-out")
    rc, out, err = node("direction_preview.js", "--ids", "dose", "--out", o)
    if rc == 3:
        report("NOT RUN", "--ids dose --out <tmp> writes dose.jpg there", "no Playwright")
    else:
        check("--ids dose --out <tmp> writes dose.jpg there", rc == 0 and os.path.getsize(os.path.join(o, "dose.jpg")) > 1000, f"rc={rc}")

    # 2: subjects without photographs never land in a photo composition
    packs = json.load(open(os.path.join(SKILL, "assets/directions/content-packs.json")))["packs"]
    dirs = json.load(open(os.path.join(SKILL, "assets/directions/directions.json")))["directions"]
    o = os.path.join(TMP, "dp-uv")
    rc, out, err = node("direction_preview.js", "--ids", "cobalt,ribbon,ultraviolet", "--out", o)
    moved = {l.split()[0]: l.rsplit(" in ", 1)[1].split()[0] for l in out.splitlines() if "drawn in" in l}
    bad = {k: v for k, v in moved.items() if v in PHOTO_COMPS}
    check("--ids cobalt,ribbon,ultraviolet (saas, no photo) moves picks only to non-photo compositions",
          rc in (0, 3) and len(moved) == 2 and not bad, f"rc={rc} moved={moved}")
    photo_dir = next((d for d in dirs if d["comp"] in PHOTO_COMPS), None)
    nophoto = next((k for k, v in packs.items() if not v.get("photo")), None)
    if photo_dir and nophoto:
        rc, out, err = node("direction_preview.js", "--ids", photo_dir["id"], "--subject", nophoto, "--out", os.path.join(TMP, "dp-np"))
        line = next((l for l in out.splitlines() if "needs photographs" in l), "")
        check(f"--ids {photo_dir['id']} ({photo_dir['comp']}) --subject {nophoto} is redrawn without photos",
              rc in (0, 3) and line and line.rsplit(" in ", 1)[1].split()[0] not in PHOTO_COMPS, f"rc={rc} {out[:200]}")
    src = open(os.path.join(SCRIPTS, "direction_preview.js"), encoding="utf-8").read()
    check("direction_preview docstring names c1..c14 (no c1..c10)", "c1..c10" not in src and "c1..c14" in src)
    o = os.path.join(TMP, "dp-th")
    rc, out, err = node("direction_preview.js", "--ids", "dose", "--sheet", "--thai", "--out", o)
    if rc == 3:
        report("NOT RUN", "--sheet --thai logs the sheet-th.jpg it wrote", "no Playwright")
    else:
        line = next((l for l in out.splitlines() if l.startswith("sheet ")), "")
        check("--sheet --thai logs the sheet-th.jpg it wrote", rc == 0 and line.endswith("sheet-th.jpg") and os.path.exists(line.split("→ ")[1]),
              f"rc={rc} {line}")


def test_preview_out():
    # direction_preview: --group / --width / --height change the set or size -> temp folder, never the library.
    # Run on a copy of scripts/ + the direction data with no Playwright reachable, so it prints its output line and stops (exit 3).
    cp = os.path.join(TMP, "skillcopy")
    shutil.copytree(SCRIPTS, os.path.join(cp, "scripts"))
    os.makedirs(os.path.join(cp, "assets", "directions"))
    for f in ("directions.json", "content-packs.json"):
        shutil.copy(os.path.join(SKILL, "assets", "directions", f), os.path.join(cp, "assets", "directions"))
    group = json.load(open(os.path.join(SKILL, "assets/directions/directions.json")))["directions"][0]["group"]
    nenv = {k: v for k, v in os.environ.items() if k not in ("NODE_PATH", "PW_MODULE", "PW_CHROMIUM")}
    nenv.update(PATH="/usr/bin:/bin", NODE_PATH="", TMPDIR=TMP + "/")
    lib = os.path.join(cp, "assets", "directions", "previews")
    for name, a in (("--group " + group, ["--group", group]), ("--width 600", ["--width", "600"]), ("--height 600", ["--height", "600"])):
        try:
            r = subprocess.run([shutil.which("node") or "node", os.path.join(cp, "scripts", "direction_preview.js"), *a], capture_output=True, text=True, env=nenv, timeout=120, cwd=TMP)
        except subprocess.TimeoutExpired:
            report("FAIL", f"direction_preview {name} without --out -> temp folder", "timeout")
            continue
        said = [l for l in r.stdout.splitlines() if l.startswith("output: ")]
        ok = bool(said) and os.path.realpath(said[0][8:].split(" (")[0]).startswith(os.path.realpath(TMP)) and not os.path.exists(lib)
        if r.returncode != 3 and not ok:
            report("NOT RUN", f"direction_preview {name} without --out -> temp folder", "Playwright still found from the copy")
            continue
        check(f"direction_preview {name} without --out -> temp folder, library folder untouched", ok, f"rc={r.returncode} {r.stdout[:200]} {r.stderr[-200:]}")
    # backoffice_preview: --singles is honoured with --out
    o = os.path.join(TMP, "bo-singles")
    rc, out, err = node("backoffice_preview.js", "--styles", "calm", "--screens", "records,approval", "--singles", "approval", "--out", o)
    if rc == 3:
        report("NOT RUN", "backoffice_preview --singles approval --out keeps only calm-approval.jpg", "no Playwright")
    else:
        files = sorted(os.listdir(o)) if os.path.isdir(o) else []
        check("backoffice_preview --singles approval --out keeps only calm-approval.jpg", rc == 0 and files == ["calm-approval.jpg"], f"rc={rc} {files} {err[-200:]}")
    o = os.path.join(TMP, "bo-all")
    rc, out, err = node("backoffice_preview.js", "--styles", "calm", "--screens", "records,approval", "--out", o)
    if rc != 3:
        files = sorted(os.listdir(o)) if os.path.isdir(o) else []
        check("backoffice_preview --out without --singles keeps every single", rc == 0 and files == ["calm-approval.jpg", "calm-records.jpg"], f"rc={rc} {files}")


def test_icons():
    env = {"TMPDIR": os.path.join(TMP, "icons") + "/"}
    os.makedirs(env["TMPDIR"], exist_ok=True)
    cache = os.path.join(env["TMPDIR"], "ux-ui-icons-cache")
    results = [py("icons.py", "lucide", "phone", "--lucide-version", "0.0.0-nope", env=env, timeout=90) for _ in range(2)]
    ok = all(r[0] == 3 and "JSONDecodeError" not in r[1] + r[2] for r in results)
    left = os.path.exists(os.path.join(cache, "lucide-0.0.0-nope-tags.json"))
    check("icons.py failed fetch twice: exit 3 both times, no cache file left", ok and not left,
          f"rcs={[r[0] for r in results]} left={left}")
    rc, out, err = py("icons.py", "brand", "line", "--ground", "white", env=env, timeout=30)
    check("icons.py --ground white exit 2 with usage", rc == 2 and "hex" in (out + err) and "Traceback" not in err, f"rc={rc}")
    rc, out, err = py("icons.py", "brand", "line", "--ground", "#12345", env=env, timeout=30)
    check("icons.py --ground #12345 exit 2", rc == 2, f"rc={rc}")
    if not online("https://cdn.jsdelivr.net/npm/lucide-static@1.58.0/package.json"):
        report("NOT RUN", "icons.py 0-byte cache file is refetched", "no network to cdn.jsdelivr.net")
        report("NOT RUN", "icons.py --ground #fff accepted", "no network")
        return
    os.makedirs(cache, exist_ok=True)
    open(os.path.join(cache, "lucide-1.58.0-tags.json"), "w").close()
    rc, out, err = py("icons.py", "lucide", "phone", env=env, timeout=120)
    check("icons.py 0-byte cache file is refetched", rc == 0 and "<svg" in out and os.path.getsize(os.path.join(cache, "lucide-1.58.0-tags.json")) > 0,
          f"rc={rc} {err[-200:]}")
    rc, out, err = py("icons.py", "brand", "line", "--ground", "#fff", env=env, timeout=120)
    check("icons.py --ground #fff accepted", rc == 0 and "brand-mark" in out, f"rc={rc} {err[-200:]}")


PHOTO_FAKE = """
import photo_search as p
hits = [dict(source='commons', title='Good picture', license='CC0', artist='A', w=2000, h=1500, page='https://x/1',
             img='file://' + {jpg!r}),
        dict(source='commons', title='Broken link', license='CC0', artist='B', w=2000, h=1500, page='https://x/2',
             img='file:///nonexistent/ux-ui-missing.jpg')]
p.commons = lambda q, n, m: list(hits)
{extra}
sys.argv = ['photo_search.py', 'room'] + {argv!r}
sys.exit(p.main())
"""


def test_photo_search():
    jpg = os.path.join(FIX, "tiny.jpg")
    d = os.path.join(TMP, "ph1")
    rc, out, err = harness(PHOTO_FAKE.format(jpg=jpg, extra="", argv=["--download", d, "--pick", "1,9"]))
    check("photo_search --pick 1,9 (2 hits) exit 2 before downloading",
          rc == 2 and "1 to 2" in err and (not os.path.isdir(d) or not os.listdir(d)), f"rc={rc} {err[-200:]}")
    rc, out, err = harness(PHOTO_FAKE.format(jpg=jpg, extra="", argv=["--download", d, "--pick", "x"]))
    check("photo_search --pick x exit 2", rc == 2, f"rc={rc}")
    d = os.path.join(TMP, "ph2")
    rc, out, err = harness(PHOTO_FAKE.format(jpg=jpg, extra="", argv=["--download", d, "--pick", "1,2", "--name", "good,broken"]))
    cred = json.load(open(os.path.join(d, "credits.json"))) if os.path.exists(os.path.join(d, "credits.json")) else {}
    check("photo_search failed download: skipped, exit 1, saved file credited",
          rc == 1 and os.path.exists(os.path.join(d, "good.jpg")) and list(cred) == ["good"] and "Traceback" not in err, f"rc={rc} cred={cred}")
    d = os.path.join(TMP, "ph3")
    crash = ("_g = p.get\n_n = [0]\ndef g(u):\n    _n[0] += 1\n    if _n[0] > 1: raise KeyboardInterrupt\n    return _g(u)\np.get = g")
    rc, out, err = harness(PHOTO_FAKE.format(jpg=jpg, extra=crash, argv=["--download", d, "--pick", "1,2", "--name", "first,second"]))
    cred = json.load(open(os.path.join(d, "credits.json"))) if os.path.exists(os.path.join(d, "credits.json")) else {}
    check("photo_search writes credits.json right after each saved file (run killed mid-way)",
          rc != 0 and os.path.exists(os.path.join(d, "first.jpg")) and "first" in cred, f"rc={rc} cred={cred}")


SHOW_FAKE = """
import showcase_fetch as s
pages = {{'https://open-design.ai/showcase/?type=all': open({idx!r}).read()}}
item = open({item!r}).read()
s.get = lambda u: pages.get(u, item)
sys.argv = ['showcase_fetch.py', '--limit', '2', '--delay', '0', '--out', {out!r}]
sys.exit(s.main())
"""


def test_showcase():
    rc, out, err = harness(
        "import showcase_fetch as s\n"
        f"v, f = s.item_images(open({os.path.join(FIX, 'showcase_item.html')!r}).read(), 'https://open-design.ai/showcase/alpha/')\n"
        "print(v); print(f)", timeout=30)
    lines = out.split()
    check("showcase item_images: view from srcset (>=1440w), full = tall capture, icons and related items ignored",
          rc == 0 and lines == ["https://r.example.test/files/view-1440", "https://r.example.test/files/full-orig"], f"{out!r} {err[-200:]}")
    rc, out, err = harness(
        "import showcase_fetch as s\n"
        f"print(s.item_images(open({os.path.join(FIX, 'showcase_item_noimg.html')!r}).read(), 'https://x/'))", timeout=30)
    check("showcase item_images: no pictures -> (None, None)", rc == 0 and out.strip() == "(None, None)", out)
    rc, out, err = harness(
        "import showcase_fetch as s\ntry:\n    s.get_bytes('file:///nonexistent/ux-ui-x')\n    print('NO ERROR')\n"
        "except s.FetchError as e:\n    print('FetchError')", timeout=30)
    check("showcase get_bytes raises on curl failure (--fail / return code)", out.strip() == "FetchError", out + err[-200:])
    try:
        import PIL  # noqa: F401
        have_pil = True
    except ImportError:
        have_pil = False
    if not have_pil:
        report("NOT RUN", "showcase exits non-zero when no picture was fetched", "no Pillow")
    else:
        rc, out, err = harness(SHOW_FAKE.format(idx=os.path.join(FIX, "showcase_index.html"), item=os.path.join(FIX, "showcase_item_noimg.html"),
                                                out=os.path.join(TMP, "sc-none")), timeout=60)
        check("showcase exits non-zero when no picture was fetched", rc == 1 and "NO IMAGE" in out, f"rc={rc} {err[-200:]}")
    if not have_pil or not online("https://open-design.ai/showcase/"):
        report("NOT RUN", "showcase_fetch --limit 2 live run fetches pictures", "no network or Pillow")
        return
    o = os.path.join(TMP, "sc-live")
    rc, out, err = py("showcase_fetch.py", "--limit", "2", "--delay", "1", "--out", o, timeout=300)
    imgs = [f for f in os.listdir(os.path.join(o, "img"))] if os.path.isdir(os.path.join(o, "img")) else []
    check("showcase_fetch --limit 2 live run fetches pictures", rc == 0 and "NO IMAGE" not in out and len(imgs) >= 2, f"rc={rc} {out[-300:]}")


def main():
    global TMP
    TMP = tempfile.mkdtemp(prefix="ux-ui-test-preview-")
    before = snapshot()
    try:
        for t in (test_direction_preview, test_preview_out, test_icons, test_photo_search, test_showcase):
            try:
                t()
            except Exception as e:  # a crash in one group is a failure, keep going
                report("FAIL", f"{t.__name__} crashed", repr(e))
        after = snapshot()
        check("repo assets/ unchanged (git status and library previews)", before == after,
              "changed: " + ", ".join(sorted(set(before[1].items()) ^ set(after[1].items())))[:300] if before[1] != after[1] else after[0][:300])
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
    n = {k: RESULTS.count(k) for k in ("PASS", "FAIL", "NOT RUN")}
    print(f"{n['PASS']} pass, {n['FAIL']} fail, {n['NOT RUN']} not run")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
