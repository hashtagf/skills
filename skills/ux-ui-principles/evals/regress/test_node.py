#!/usr/bin/env python3
"""Regression cases for the Node scripts' shared contract (_args.js, _pw.js, _color.js) and level-2/3 fixes:
help and usage errors, temp output for URL targets, oklch colours in admin_check, market_fetch exit codes,
flow_check steps validation, script_check destructuring, build_previews library paths, --json of the five checkers
(_report.js: one document on stdout, exit code unchanged, usage error / NOT RUN / navigation ERROR as JSON).

Usage: python3 evals/regress/test_node.py      (any cwd; writes only to temp folders)

Fixtures live in evals/regress/node/. One PASS / FAIL / NOT RUN line per case; browser cases print NOT RUN
when Playwright or a browser is unavailable. Exit 1 on any failure. At the end it checks that
`git status --porcelain assets/` of the skill did not change. Standard library only.
"""
import functools, http.server, json, os, shutil, socket, subprocess, sys, tempfile, threading

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
FIX = os.path.join(HERE, "node")
NODE = shutil.which("node")
RESULTS = []
CLI = ["render_check.js", "fold_check.js", "admin_check.js", "flow_check.js", "script_check.js", "market_fetch.js",
       "build_previews.js", "direction_preview.js", "backoffice_preview.js"]


def report(status, name, detail=""):
    RESULTS.append(status)
    print(f"{status:7} {name}" + (f"\n        {detail.strip()[:500]}" if detail and status == "FAIL" else f"  ({detail})" if detail else ""), flush=True)


def check(name, ok, detail=""):
    report("PASS" if ok else "FAIL", name, "" if ok else detail)


def js(script, *a, cwd, env=None, timeout=180):
    e = dict(os.environ)
    nm = os.path.join(os.path.dirname(os.path.dirname(SKILL)), "node_modules")
    if os.path.isdir(nm):
        e["NODE_PATH"] = os.pathsep.join(x for x in (e.get("NODE_PATH"), nm) if x)
    e.update(env or {})
    try:
        r = subprocess.run([NODE, os.path.join(SCRIPTS, script), *a], cwd=cwd, capture_output=True, text=True, env=e, timeout=timeout)
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -9, "", f"timeout after {timeout}s"


def traced(err):
    return "Traceback" in err or "\n    at " in err or "UnhandledPromiseRejection" in err


SHAPE = ("script", "target", "result", "exit", "findings", "artifacts")
LEVELS = ("fail", "flag", "warn", "note", "pass")


def jdoc(out):
    """The single JSON object on stdout, or None (json.loads rejects anything before or after it)."""
    try:
        d = json.loads(out)
    except ValueError:
        return None
    return d if isinstance(d, dict) else None


def shape_ok(d, script, rc):
    return bool(d) and all(k in d for k in SHAPE) and d["script"] == script[:-3] and d["exit"] == rc \
        and isinstance(d["findings"], list) and isinstance(d["artifacts"], dict) \
        and all({"level", "rule", "message", "where"} <= set(f) and f["level"] in LEVELS for f in d["findings"])


def has_finding(d, rule, levels=("fail", "flag")):
    return any(f["rule"] == rule and f["level"] in levels for f in d["findings"])


def write(p, text):
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(text)
    return p


def assets_status():
    return subprocess.run(["git", "-C", SKILL, "status", "--porcelain", "assets/"], capture_output=True, text=True).stdout


def closed_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close()
    return p


def serve(folder):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    h = functools.partial(Quiet, directory=folder)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/"


def main():
    if not NODE:
        report("NOT RUN", "all Node cases", "node not found")
        return 0
    tmp = tempfile.mkdtemp(prefix="ux-ui-test-node-")
    before = assets_status()
    srv = None
    try:
        work = os.path.join(tmp, "fix")
        shutil.copytree(FIX, work)
        f = lambda n: os.path.join(work, n)
        empty = os.path.join(tmp, "cwd"); os.makedirs(empty)
        tmpdir = os.path.join(tmp, "tmpdir"); os.makedirs(tmpdir)
        tenv = {"TMPDIR": tmpdir + "/"}

        # 1. --help: every CLI script prints its header and exits 0, renders nothing
        for s in CLI:
            rc, out, err = js(s, "--help", cwd=empty, timeout=30)
            check(f"{s} --help exit 0, header printed", rc == 0 and len(out.strip()) > 80 and "→" not in out and not err.strip(), f"rc={rc} {err[-200:]}")
        check("--help left the cwd empty", not os.listdir(empty), str(os.listdir(empty)))

        # 2. usage errors: exit 2, "error: …" on stderr, no stack trace
        bad = {"render_check.js": [f("page.html"), "--bogus"], "fold_check.js": [f("page.html"), "--sizes", "wide"],
               "admin_check.js": [f("page.html"), "--type", "nope"], "flow_check.js": [f("page.html")],
               "script_check.js": [], "market_fetch.js": [], "build_previews.js": ["--only", "nope"],
               "direction_preview.js": ["--group", "nope"], "backoffice_preview.js": ["--screens", "nope"]}
        for s, a in bad.items():
            rc, out, err = js(s, *a, cwd=empty, timeout=30)
            check(f"{s} {' '.join(a[1:] if a and a[0].startswith('/') else a) or '(no args)'} -> exit 2, error line, no trace",
                  rc == 2 and err.startswith("error: ") and not traced(err), f"rc={rc} {err[-300:]}")
        for s in ("render_check.js", "fold_check.js", "admin_check.js", "script_check.js"):
            rc, out, err = js(s, f("nofile.html"), cwd=empty, timeout=30)
            check(f"{s} missing file -> exit 2 before any browser", rc == 2 and "file not found" in err and not traced(err), f"rc={rc} {err[-200:]}")
        for name, a in (("--width abc", ["--ids", "dose", "--width", "abc"]), ("--ids without value", ["--ids"]), ("--comp c99", ["--comp", "c99"])):
            rc, out, err = js("direction_preview.js", *a, cwd=empty, timeout=30)
            check(f"direction_preview {name} -> exit 2", rc == 2 and err.startswith("error: ") and not traced(err), f"rc={rc} {err[-200:]}")
        for name, a in (("--styles nope", ["--styles", "nope"]), ("--direction nope", ["--direction", "nope"]), ("--density x", ["--density", "x"]),
                        ("--height 0", ["--height", "0"])):
            rc, out, err = js("backoffice_preview.js", *a, cwd=empty, timeout=30)
            check(f"backoffice_preview {name} -> exit 2", rc == 2 and err.startswith("error: ") and not traced(err), f"rc={rc} {err[-200:]}")

        # 6. flow_check steps file
        for name, steps in (("malformed JSON", "steps-bad.json"), ("non-array", "steps-object.json"), ("missing", "nope.json")):
            rc, out, err = js("flow_check.js", f("page.html"), f(steps), cwd=empty, timeout=30)
            check(f"flow_check {name} steps -> exit 2", rc == 2 and err.startswith("error: ") and not traced(err), f"rc={rc} {err[-200:]}")

        # 7. script_check: destructured top-level declarations clash like simple names
        rc, out, err = js("script_check.js", f("destructure.html"), cwd=empty, timeout=30)
        check("script_check: {top, left} / [a, name] / nested renamed {x: status} flagged",
              rc == 1 and "'top'" in out and "'name'" in out and "'status'" in out, out + err)
        check("script_check: {top: t1}, inner-function {top} and block-scoped parent not flagged",
              "line 11" not in out and "'parent'" not in out, out)

        # 8. --json without a browser: usage errors and script_check
        jbad = {"render_check.js": [f("page.html"), "--bogus"], "fold_check.js": [f("page.html"), "--sizes", "wide"],
                "admin_check.js": [f("page.html"), "--type", "nope"], "flow_check.js": [f("page.html")], "script_check.js": []}
        for s, a in jbad.items():
            for label, args in (("usage error", a), ("missing file", [f("nofile.html")] + (["x.json"] if s == "flow_check.js" else []))):
                rc, out, err = js(s, *args, "--json", cwd=empty, timeout=30)
                d = jdoc(out)
                check(f"{s} --json {label} -> exit 2, JSON ERROR document only",
                      rc == 2 and shape_ok(d, s, 2) and d["result"] == "ERROR" and d.get("error") and err.startswith("error: ") and not traced(err),
                      f"rc={rc} out={out[-300:]} err={err[-200:]}")
        rc, out, err = js("script_check.js", f("destructure.html"), "--json", cwd=empty, timeout=30)
        d = jdoc(out)
        check("script_check --json failing page: exit 1 = JSON exit, global-clash fail findings, pages summary",
              rc == 1 and shape_ok(d, "script_check.js", 1) and d["result"] == "FAIL" and has_finding(d, "global-clash")
              and d["pages"][0]["scripts"] and "FAIL" in err, f"rc={rc} {out[-300:]} {err[-200:]}")
        rc, out, err = js("script_check.js", f("page.html"), f("admin-oklch.html"), "--json", cwd=empty, timeout=30)
        d = jdoc(out)
        check("script_check --json passing pages: exit 0 PASS, target lists both pages",
              rc == 0 and shape_ok(d, "script_check.js", 0) and d["result"] == "PASS" and isinstance(d["target"], list) and len(d["target"]) == 2,
              f"rc={rc} {out[-300:]}")
        # NOT RUN: a copy of scripts/ with no node_modules above it, empty NODE_PATH and no npm on PATH
        scr = os.path.join(tmp, "scr", "scripts"); shutil.copytree(SCRIPTS, scr)
        nenv = {k: v for k, v in os.environ.items() if k not in ("NODE_PATH", "PW_MODULE", "PW_CHROMIUM")}
        nenv.update(PATH="/usr/bin:/bin", NODE_PATH="")
        for s, a in (("render_check.js", [f("page.html")]), ("fold_check.js", [f("page.html")]), ("admin_check.js", [f("page.html")]),
                     ("flow_check.js", [f("page.html"), f("steps-mixed.json")])):
            r = subprocess.run([NODE, os.path.join(scr, s), *a, "--json"], cwd=empty, capture_output=True, text=True, env=nenv, timeout=60)
            d = jdoc(r.stdout)
            if r.returncode != 3 and "NOT RUN" not in r.stderr and d and d.get("result") != "NOT RUN":
                report("NOT RUN", f"{s} --json without Playwright -> NOT RUN document", "Playwright still found from the copied scripts")
                continue
            check(f"{s} --json without Playwright -> exit 3, JSON NOT RUN document only",
                  r.returncode == 3 and shape_ok(d, s, 3) and d["result"] == "NOT RUN" and "NOT RUN" in r.stderr, f"rc={r.returncode} {r.stdout[-300:]} {r.stderr[-200:]}")

        # 5. market_fetch --only nosuch
        rc, out, err = js("market_fetch.js", "--kind", "clinic", "--only", "nosuch", cwd=empty, timeout=30)
        check("market_fetch --only nosuch -> exit 2 listing the valid slugs", rc == 2 and "nosuch" in err and "choose from" in err and not traced(err), f"rc={rc} {err[-200:]}")

        # 4. build_previews: library --out paths resolve from the skill root, whatever the cwd
        rc, out, err = js("build_previews.js", "--dry-run", cwd=empty, timeout=30)
        outs = [l.split("--out ", 1)[1].split()[0] for l in out.splitlines() if "--out " in l]
        check("build_previews --dry-run: every --out (6 sets, directions/backoffice/mobile too) is absolute under the skill's assets/",
              rc == 0 and len(outs) == 6 and all(o.startswith(os.path.join(SKILL, "assets") + os.sep) for o in outs) and not os.listdir(empty),
              f"rc={rc} {outs} {err[-200:]}")
        src = open(os.path.join(SCRIPTS, "build_previews.js"), encoding="utf-8").read()
        check("build_previews has no cwd-relative 'assets/…' --out", "'--out', 'assets/" not in src)
        sets = [l.split("--out ", 1)[1].split()[0] for l in out.splitlines() if l.startswith("> node")]
        order = ["directions/previews", "directions/previews/product", "backoffice/previews", "backoffice/previews", "backoffice/previews/tablet", "backoffice/previews/rtl"]
        runs = [l for l in out.splitlines() if l.startswith("> node")]
        check("build_previews --dry-run runs in the documented order (mobile 4th, before tablet/rtl)",
              [o.split(os.sep + "assets" + os.sep, 1)[-1] for o in sets] == order and len(runs) == 6 and "--mobile" in runs[3],
              out[-600:])

        # _color.js maths (shared by brand.js, compositions.js and the in-page checks)
        code = ("const c=require(%r);console.log(JSON.stringify([c.parse('#abc'),c.parse('#11223380'),c.parse('rgb(10 20 30 / 50%%)'),"
                "c.parse('rgba(1,2,3,.4)'),c.parse('nope'),+c.contrast('#000','#fff').toFixed(2),+c.contrast('#777','#fff').toFixed(2)]))") % os.path.join(SCRIPTS, "_color.js")
        r = subprocess.run([NODE, "-e", code], capture_output=True, text=True)
        try:
            v = json.loads(r.stdout)
        except ValueError:
            v = None
        check("_color.js parses hex 3/8, rgb space/slash, rgba; contrast 21 and 4.48",
              v and v[0] == [170, 187, 204, 1] and v[1][:3] == [17, 34, 51] and abs(v[1][3] - 128 / 255) < 1e-9 and v[2] == [10, 20, 30, 0.5]
              and v[3] == [1, 2, 3, 0.4] and v[4] is None and v[5] == 21 and v[6] == 4.48, r.stdout + r.stderr)

        # script_check: modules compiled as modules (multi-line import/export), root-relative and unquoted src, data-src
        sc = os.path.join(tmp, "sc"); os.makedirs(os.path.join(sc, "assets")); os.makedirs(os.path.join(sc, "sub"))
        page = lambda n, body: write(os.path.join(sc, n), f"<!doctype html><html><body>{body}</body></html>")
        write(os.path.join(sc, "assets", "index.js"), "export const x = 1;\n")
        page("mod-import.html", '<script type="module">\nimport {\n  a,\n  b\n} from "./x.js";\nconsole.log(a, b);\n</script>')
        page("mod-export.html", '<script type="module">\nexport function f() {\n  return 1;\n}\nexport default {\n  y: 2\n};\n</script>')
        page("mod-bad.html", '<script type="module">\nimport {\n  a\n} from "./x.js";\nconst = 1;\n</script>')
        page("root.html", '<script type="module" src="/assets/index.js"></script>')
        page("root-missing.html", '<script src="/assets/nope.js"></script>')
        page("unquoted.html", '<script src=assets/missing.js></script><script data-src="lazy.js"></script>')
        page("dir.html", '<script src="sub"></script>')
        for n, want in (("mod-import.html", 0), ("mod-export.html", 0), ("root.html", 0)):
            rc, out, err = js("script_check.js", os.path.join(sc, n), cwd=empty, timeout=30)
            check(f"script_check {n}: valid module / root-relative src -> PASS", rc == 0 and out.startswith("PASS"), f"rc={rc} {out[-300:]} {err[-200:]}")
        rc, out, err = js("script_check.js", os.path.join(sc, "mod-bad.html"), cwd=empty, timeout=30)
        check("script_check multi-line import + real syntax error in a module -> FAIL syntax error", rc == 1 and "syntax error" in out, f"rc={rc} {out[-300:]}")
        rc, out, err = js("script_check.js", os.path.join(sc, "root-missing.html"), cwd=empty, timeout=30)
        check("script_check root-relative src that exists nowhere -> missing-script", rc == 1 and "missing local script /assets/nope.js" in out, f"rc={rc} {out[-300:]}")
        rc, out, err = js("script_check.js", os.path.join(sc, "unquoted.html"), "--json", cwd=empty, timeout=30)
        d = jdoc(out)
        msgs = " ".join(x["message"] for x in (d or {}).get("findings", []))
        check("script_check unquoted src=assets/missing.js checked, data-src ignored",
              rc == 1 and d and has_finding(d, "missing-script") and "assets/missing.js" in msgs and "lazy.js" not in msgs, f"rc={rc} {out[-400:]}")
        rc, out, err = js("script_check.js", os.path.join(sc, "dir.html"), "--json", cwd=empty, timeout=30)
        d = jdoc(out)
        check("script_check src that is a folder -> missing-script finding, no crash",
              rc == 1 and shape_ok(d, "script_check.js", 1) and d["result"] == "FAIL" and has_finding(d, "missing-script") and not traced(err), f"rc={rc} {out[-300:]} {err[-300:]}")
        # unreadable inputs: one error line, exit 2 / JSON ERROR (skipped when running as root)
        nr = os.path.join(sc, "noread.html"); write(nr, "<!doctype html><p>x</p>"); os.chmod(nr, 0)
        if os.access(nr, os.R_OK):
            report("NOT RUN", "unreadable page -> exit 2 (script_check, render_check)", "running as root: chmod 000 still readable")
        else:
            for s_ in ("script_check.js", "render_check.js"):
                rc, out, err = js(s_, nr, "--json", cwd=empty, timeout=60)
                d = jdoc(out)
                check(f"{s_} unreadable page -> exit 2, one error line, JSON ERROR with error",
                      rc == 2 and err.startswith("error: ") and "cannot read" in err and not traced(err) and shape_ok(d, s_, 2) and d["result"] == "ERROR" and d.get("error"),
                      f"rc={rc} {out[-300:]} {err[-300:]}")
        os.chmod(nr, 0o644)
        # market_fetch --urls: a folder and a non-http(s) URL are usage errors (exit 2), before any browser
        for name, u in (("a folder", sc), ("an ftp:// line", write(os.path.join(tmp, "ftp.txt"), "x ftp://a.b/\n"))):
            rc, out, err = js("market_fetch.js", "--kind", "testkind", "--urls", u, cwd=empty, timeout=30)
            check(f"market_fetch --urls {name} -> exit 2, one error line", rc == 2 and err.startswith("error: ") and not traced(err), f"rc={rc} {err[-300:]}")
        # _args: "--" ends the options
        rc, out, err = js("script_check.js", "--", os.path.join(sc, "root.html"), cwd=empty, timeout=30)
        check("script_check -- page.html: '--' ends the options", rc == 0 and out.startswith("PASS"), f"rc={rc} {out[-200:]} {err[-200:]}")
        write(os.path.join(sc, "-dash.html"), "<!doctype html><p>x</p>")
        rc, out, err = js("script_check.js", "--", "-dash.html", cwd=sc, timeout=30)
        check("script_check -- -dash.html: a file named like an option after '--'", rc == 0 and "-dash.html" in out, f"rc={rc} {out[-200:]} {err[-200:]}")
        # _color.js: '#' required for hex, empty rgb() items rejected
        code = ("const c=require(%r);console.log(JSON.stringify([c.parse('bad'),c.parse('cafe'),c.parse('abc'),c.parse('rgb(10,20,30,)'),"
                "c.parse('rgb(,1,2,3)'),c.parse('#cafe'),c.parse('rgb(10,20,30)')]))") % os.path.join(SCRIPTS, "_color.js")
        r = subprocess.run([NODE, "-e", code], capture_output=True, text=True)
        v = jdoc('{"v":' + r.stdout.strip() + '}') if r.stdout.strip() else None
        v = v and v["v"]
        check("_color.js: bare 'bad'/'cafe'/'abc' and rgb trailing/leading comma -> null; '#cafe' and rgb() still parse",
              v and v[:5] == [None] * 5 and v[5][:3] == [204, 170, 255] and v[6] == [10, 20, 30, 1], r.stdout + r.stderr)
        # flow_check: every step is validated before any browser starts
        for name, steps in (("fill without value", [{"do": "fill", "sel": "#q"}]), ("select without value", [{"do": "select", "sel": "s"}]),
                            ("expect text without value", [{"expect": "text", "sel": "h1"}]),
                            ("wait with non-number value", [{"expect": "visible", "sel": "h1"}, {"do": "wait", "value": "abc"}]),
                            ("expect attr without attr", [{"expect": "attr", "sel": "h1", "value": "x"}]),
                            ("press without key", [{"do": "press"}]), ("empty array", [])):
            sf = write(os.path.join(tmp, "steps-v.json"), json.dumps(steps))
            rc, out, err = js("flow_check.js", f("page.html"), sf, cwd=empty, timeout=30)
            n_ = len(steps)
            check(f"flow_check {name} -> exit 2 naming the step", rc == 2 and err.startswith("error: ") and not traced(err)
                  and (f"step {n_}" in err if n_ else "no steps" in err), f"rc={rc} {err[-200:]}")

        # browser cases
        rc, out, err = js("render_check.js", "--doctor", cwd=empty, timeout=60)
        if rc != 0:
            why = (out.strip().splitlines() or ["no Playwright"])[-1][:80]
            for n in ("URL target -> temp, cwd stays empty (x3)", "admin_check oklch/oklab/color-mix buttons", "market_fetch skip -> 1, all shot -> 0",
                      "render_check fragment in a read-only folder -> wrapper in temp", "fold_check no second section message",
                      "render_check --scroll-budget caps the reveal scroll with a NOTE"):
                report("NOT RUN", n, why)
        else:
            srv, url = serve(work)
            for s, a, folder in (("render_check.js", ["--fast", "--viewport-shots"], "ux-ui-render-check"), ("fold_check.js", [], "ux-ui-fold-check"),
                                 ("admin_check.js", ["--type", "detail"], "ux-ui-admin-check")):
                rc, out, err = js(s, url + "page.html", *a, cwd=empty, env=tenv)
                made = [os.path.join(r_, x) for r_, _, fs in os.walk(os.path.join(tmpdir, folder)) for x in fs if x.endswith(".png")]
                check(f"{s} URL target -> screenshots in <tmp>/{folder}, cwd empty",
                      rc in (0, 1) and bool(made) and not os.listdir(empty) and "output: " in out, f"rc={rc} cwd={os.listdir(empty)} {out[-300:]} {err[-200:]}")
            rc, out, err = js("admin_check.js", f("admin-oklch.html"), "--type", "form", "--out", os.path.join(tmp, "adm"), cwd=empty)
            check("admin_check: oklch / oklab / color-mix filled buttons counted (one-primary FAIL)",
                  rc == 1 and "one-primary: 3 filled accent buttons" in out, f"rc={rc} {out[-300:]} {err[-200:]}")
            urls = os.path.join(tmp, "urls.txt")
            with open(urls, "w") as fh:
                fh.write(f"good {url}page.html intl\ndead http://127.0.0.1:{closed_port()}/ intl\n")
            rc, out, err = js("market_fetch.js", "--kind", "testkind", "--urls", urls, "--out", os.path.join(tmp, "mk"), "--timeout", "15000", cwd=empty)
            check("market_fetch: a skipped site -> exit 1 (WARN skip line)", rc == 1 and "WARN  skip dead" in out and "PASS  good" in out, f"rc={rc} {out[-300:]}")
            rc, out, err = js("market_fetch.js", "--kind", "testkind", "--urls", urls, "--only", "good", "--out", os.path.join(tmp, "mk"), cwd=empty)
            check("market_fetch: every site shot -> exit 0", rc == 0 and "1 shot, 0 skipped" in out, f"rc={rc} {out[-300:]}")
            # --json in the browser checkers: one document, exit code = "exit", failing cases report a fail finding
            jo = os.path.join(tmp, "jsonout")
            for s, a, rule, want in (
                    ("render_check.js", [f("page.html"), "--fast", "--viewport-shots"], "phone", 1),
                    ("fold_check.js", [f("admin-oklch.html"), "--cta", "#none"], "cta-missing", 1),
                    ("fold_check.js", [f("page.html")], None, 0),
                    ("admin_check.js", [f("admin-oklch.html"), "--type", "form"], "one-primary", 1),
                    ("flow_check.js", [f("page.html"), f("steps-mixed.json")], "step", 1)):
                rc, out, err = js(s, *a, "--out", jo, "--json", cwd=empty) if s != "flow_check.js" else js(s, *a, "--json", cwd=empty)
                d = jdoc(out)
                extra = {"render_check.js": "viewports", "fold_check.js": "sizes", "admin_check.js": "checks", "flow_check.js": "steps"}[s]
                ok = rc == want and shape_ok(d, s, rc) and extra in d and (has_finding(d, rule) if rule else d["result"] == "PASS") and err.strip()
                if s == "render_check.js" and ok:
                    ok = all(os.path.exists(p) for p in d["artifacts"].get("screenshots", [])) and len(d["viewports"]) == 2
                if s == "flow_check.js" and ok:
                    ok = [x["result"] for x in d["steps"]] == ["PASS", "PASS", "FAIL", "FAIL"]
                check(f"{s} --json {rule or 'passing'} case: exit {want} = JSON exit, stdout is only the document",
                      ok, f"rc={rc} {out[-400:]} {err[-200:]}")
            rc, out, err = js("render_check.js", f"http://127.0.0.1:{closed_port()}/", "--out", jo, "--json", cwd=empty, timeout=60)
            d = jdoc(out)
            check("render_check --json unreachable URL -> exit 1, JSON ERROR document with the reason",
                  rc == 1 and shape_ok(d, "render_check.js", 1) and d["result"] == "ERROR" and "could not load" in d.get("error", ""), f"rc={rc} {out[-300:]} {err[-200:]}")
            # fragment: the doctype wrapper goes to a temp folder (never next to the page); relative assets still load
            ro = os.path.join(tmp, "ro"); os.makedirs(ro)
            write(os.path.join(ro, "frag.html"), '<h1>Fragment</h1><p>frag text</p><img src="tiny.jpg" alt="t" width="10" height="10">')
            shutil.copy(os.path.join(os.path.dirname(FIX), "preview", "tiny.jpg"), ro)
            os.chmod(ro, 0o555)
            rc, out, err = js("render_check.js", os.path.join(ro, "frag.html"), "--fast", "--viewport-shots", "--widths", "1440", "--out", os.path.join(tmp, "frag-out"), "--json", cwd=empty)
            left = sorted(os.listdir(ro)); os.chmod(ro, 0o755)
            d = jdoc(out)
            check("render_check fragment in a read-only folder -> wrapper in temp, relative image loads, folder untouched",
                  rc in (0, 1) and d and d["result"] in ("PASS", "FAIL") and not d.get("error") and has_finding(d, "fragment", ("note",))
                  and not has_finding(d, "image-broken") and left == ["frag.html", "tiny.jpg"] and not traced(err), f"rc={rc} left={left} {out[-400:]} {err[-300:]}")
            # fold_check: a page with one section names the missing next section instead of "nullpx"
            one = write(os.path.join(tmp, "one.html"), '<!doctype html><html lang="en"><body><main><section style="height:300px"><h1>Hi</h1><a class="btn-primary" href="#">Go</a></section></main></body></html>')
            rc, out, err = js("fold_check.js", one, "--sizes", "1440x900", "--out", os.path.join(tmp, "fold1"), cwd=empty)
            check("fold_check no second section -> 'no second section found', never 'nullpx'",
                  rc == 0 and "nullpx" not in out and "no second section found" in out, f"rc={rc} {out[-400:]}")
            # render_check: the reveal scroll is capped by --scroll-budget and says so
            long_ = write(os.path.join(tmp, "long.html"), '<!doctype html><html lang="en"><body style="margin:0 40px"><h1>Long</h1><div style="height:30000px"></div><p>end</p></body></html>')
            import time
            t0 = time.time()
            rc, out, err = js("render_check.js", long_, "--widths", "1440", "--schemes", "light", "--viewport-shots", "--scroll-budget", "800",
                              "--out", os.path.join(tmp, "long-out"), "--json", cwd=empty)
            took = time.time() - t0
            d = jdoc(out)
            check("render_check --scroll-budget 800 on a 30000px page: scroll-budget NOTE, finishes quickly",
                  rc in (0, 1) and d and has_finding(d, "scroll-budget", ("note",)) and took < 40, f"rc={rc} took={took:.0f}s {out[-300:]} {err[-200:]}")
            rc, out, err = js("render_check.js", long_, "--scroll-budget", "-1", cwd=empty, timeout=30)
            check("render_check --scroll-budget -1 -> exit 2", rc == 2 and err.startswith("error: "), f"rc={rc} {err[-200:]}")
            check("browser cases left the cwd empty", not os.listdir(empty), str(os.listdir(empty)))
    finally:
        if srv:
            srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)
    after = assets_status()
    check("skill assets/ git status unchanged", before == after, after[:300])
    n = {k: RESULTS.count(k) for k in ("PASS", "FAIL", "NOT RUN")}
    print(f"\n{n['PASS']} pass, {n['FAIL']} fail, {n['NOT RUN']} not run")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
