#!/usr/bin/env python3
"""Regression cases for the delivery checkers (check.py, state_check, contrast, slop_check,
render_check / _composition, admin_check, fold_check).

Usage: python3 evals/regress/test_checkers.py      (any cwd; writes only to a temp folder)

Fixtures live in evals/regress/checkers/ and are copied to a temp folder before each run, so
screenshots and render-check folders never land in the repo. One PASS / FAIL / NOT RUN line per
case; browser cases print NOT RUN (not a failure) when Playwright or a browser is unavailable.
Exit 1 on any failure. Standard library only.
"""
import os, shutil, socket, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
FIX = os.path.join(HERE, "checkers")
NODE = shutil.which("node")
results = []


def run(cmd, cwd):
    env = dict(os.environ)
    repo_nm = os.path.join(os.path.dirname(os.path.dirname(SKILL)), "node_modules")
    if os.path.isdir(repo_nm):
        env["NODE_PATH"] = os.pathsep.join(x for x in (env.get("NODE_PATH"), repo_nm) if x)
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300, env=env)
    return r.returncode, r.stdout + r.stderr


def py(script, *a, cwd):
    return run([sys.executable, os.path.join(SCRIPTS, script), *a], cwd)


def js(script, *a, cwd):
    return run([NODE, os.path.join(SCRIPTS, script), *a], cwd)


def case(name, ok, detail=""):
    results.append(("PASS" if ok else "FAIL", name))
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n      {detail.strip()[:600]}"))


def not_run(name, why):
    results.append(("NOT RUN", name))
    print(f"NOT RUN  {name} ({why})")


def browser_ok(tmp):
    if not NODE:
        return False, "node not found"
    code, out = js("render_check.js", "--doctor", cwd=tmp)
    return (code == 0, out.strip().splitlines()[-1] if out.strip() else "no output")


def closed_port():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close()
    return p


def line_of(out, name):
    return next((l for l in out.splitlines() if l.strip().endswith(" " + name) or l.split()[1:2] == [name]), "")


def main():
    tmp = tempfile.mkdtemp(prefix="ux-checkers-")
    try:
        work = os.path.join(tmp, "checkers")
        shutil.copytree(FIX, work)
        f = lambda n: os.path.join(work, n)

        # 1. check.py states: PASS when every state has a marker; scope = page + linked files; MISS lines only
        code, out = py("check.py", f("states-all.html"), cwd=tmp)
        case("states: all markers -> PASS", "PASS     states" in out, out)
        code, out = py("check.py", f("states-scope/page.html"), cwd=tmp)
        st = out[out.find("states"):]
        case("states: scope is page + linked script/css, not sibling files",
             "MANUAL   states" in out and "MISS hover" not in st and "MISS loading" not in st and "MISS empty" in st, out)
        case("states: excerpt shows MISS lines only", "files scanned" not in st and " ok " not in st, out)
        code, out = py("state_check.py", f("states-scope/page.html"), f("states-scope/app.js"), "--json", cwd=tmp)
        case("state_check: several paths scanned together", '"files": 2' in out and code == 1, out)

        # 5. contrast.py: theme blocks, @theme, html, exit 2 on zero pairs, selector clean-up
        code, out = py("contrast.py", "--css", f("data-theme-dark.css"), cwd=tmp)
        case("contrast: [data-theme=dark] block read, failing muted caught",
             code == 1 and '[[data-theme="dark"]]' in out and "FAIL   3.67:1" in out, out)
        case("contrast: .dark and html[data-theme] blocks read, labelled by theme",
             "[.dark]  (dark theme)" in out and "(light theme)" in out and "2.64:1" in out and "2.23:1" in out, out)
        case("contrast: component rule (.card) ignored", "[.card]" not in out, out)
        code, out = py("contrast.py", "--css", f("tw-theme.css"), cwd=tmp)
        case("contrast: Tailwind v4 @theme block read", code == 1 and "[@theme]" in out and "--foreground on --background" in out, out)
        code, out = py("contrast.py", "--css", f("html-tokens.css"), cwd=tmp)
        case("contrast: html{} tokens read", code == 0 and "[html]" in out and "1/1 pairs pass" in out, out)
        code, out = py("contrast.py", "--css", f("no-pairs.css"), cwd=tmp)
        case("contrast: zero checkable pairs -> N/A, exit 0, no '0/0 pass'", code == 0 and out.startswith("N/A") and "0/0" not in out, out)
        code, out = py("check.py", f("no-pairs.html"), cwd=tmp)
        case("check.py: contrast with zero pairs -> N/A", "N/A      contrast" in out, out)
        code, out = py("contrast.py", "--css", f("html-junk.css"), cwd=tmp)
        case("contrast: HTML junk stripped from selector label", "[.dark]" in out and "<" not in out.split("\n")[0], out)

        # 6. slop_check: icon-card-row / nav-without-icons
        code, out = py("slop_check.py", f("team-grid.html"), cwd=tmp)
        case("slop: photo team grid is not an icon-card-row", "icon-card-row" not in out, out)
        code, out = py("slop_check.py", f("icon-cards.html"), cwd=tmp)
        case("slop: svg / small img / icon-class cards still flag icon-card-row", "icon-card-row" in out, out)
        code, out = py("slop_check.py", f("header-nav-cta.html"), cwd=tmp)
        case("slop: brand + 4 menu links + 2 buttons is not app nav", "nav-without-icons" not in out, out)
        code, out = py("slop_check.py", f("sidebar-8.html"), cwd=tmp)
        case("slop: sidebar of 8 text links still flags nav-without-icons", "nav-without-icons" in out and "8 of 8" in out, out)

        # 4. navigation errors: missing file is reported before any browser starts
        if NODE:
            for s in ("render_check.js", "admin_check.js", "fold_check.js"):
                code, out = js(s, f("nofile.html"), cwd=tmp)
                case(f"{s}: missing file -> error, exit 2", code == 2 and "error: file not found" in out and "PASS" not in out and "Traceback" not in out, out)
        else:
            not_run("missing-file cases", "node not found")

        ok, why = browser_ok(tmp)
        browser_cases = ["unreachable URL x3", "fold CTA fallback", "oklab/alpha colours", "entrance animation settle"]
        if not ok:
            for n in browser_cases:
                not_run(n, why)
        else:
            out_dir = os.path.join(tmp, "out")
            url = f"http://127.0.0.1:{closed_port()}/"
            for s in ("render_check.js", "admin_check.js", "fold_check.js"):
                code, out = js(s, url, "--out", out_dir, cwd=tmp)
                case(f"{s}: refused URL -> ERROR with reason, exit 1",
                     code == 1 and "ERROR could not load" in out and "ERR_CONNECTION_REFUSED" in out and "did not finish" not in out and "PASS" not in out, out)
            code, out = js("fold_check.js", f("fold-cta-fallback.html"), "--out", out_dir, cwd=tmp)
            case("fold: hero a.btn found as CTA (no .btn-primary)", code == 0 and 'CTA "See the beans"' in out and "no primary CTA" not in out, out)
            code, out = js("render_check.js", f("oklab-bg.html"), "--fast", "--out", out_dir, cwd=tmp)
            weak = next((l for l in out.splitlines() if "below 7:1" in l), "")
            case("render: oklab/oklch colours parsed (no false low contrast)", "p.lede" not in weak and "p.ink" not in weak, out)
            case("render: alpha text composited over its background", "p.half" in weak, out)
            code, out = js("render_check.js", f("animated.html"), "--fast", "--out", out_dir, cwd=tmp)
            weak = next((l for l in out.splitlines() if "below 7:1" in l), "")
            case("render: entrance animation finished before measuring", "p.anim" not in weak and "ERROR" not in out, out)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n = {k: sum(1 for s, _ in results if s == k) for k in ("PASS", "FAIL", "NOT RUN")}
    print(f"\n{n['PASS']} passed, {n['FAIL']} failed, {n['NOT RUN']} not run")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
