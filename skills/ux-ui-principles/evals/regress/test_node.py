#!/usr/bin/env python3
"""Regression cases for the Node scripts' shared contract (_args.js, _pw.js, _color.js) and level-2/3 fixes:
help and usage errors, temp output for URL targets, oklch colours in admin_check, market_fetch exit codes,
flow_check steps validation, script_check destructuring, build_previews library paths.

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

        # 5. market_fetch --only nosuch
        rc, out, err = js("market_fetch.js", "--kind", "clinic", "--only", "nosuch", cwd=empty, timeout=30)
        check("market_fetch --only nosuch -> exit 2 listing the valid slugs", rc == 2 and "nosuch" in err and "choose from" in err and not traced(err), f"rc={rc} {err[-200:]}")

        # 4. build_previews: library --out paths resolve from the skill root, whatever the cwd
        rc, out, err = js("build_previews.js", "--dry-run", cwd=empty, timeout=30)
        outs = [l.split("--out ", 1)[1].split()[0] for l in out.splitlines() if "--out " in l]
        check("build_previews --dry-run: every --out is absolute under the skill's assets/",
              rc == 0 and len(outs) == 3 and all(o.startswith(os.path.join(SKILL, "assets") + os.sep) for o in outs) and not os.listdir(empty),
              f"rc={rc} {outs} {err[-200:]}")
        src = open(os.path.join(SCRIPTS, "build_previews.js"), encoding="utf-8").read()
        check("build_previews has no cwd-relative 'assets/…' --out", "'--out', 'assets/" not in src)

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

        # browser cases
        rc, out, err = js("render_check.js", "--doctor", cwd=empty, timeout=60)
        if rc != 0:
            why = (out.strip().splitlines() or ["no Playwright"])[-1][:80]
            for n in ("URL target -> temp, cwd stays empty (x3)", "admin_check oklch/oklab/color-mix buttons", "market_fetch skip -> 1, all shot -> 0"):
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
