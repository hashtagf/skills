#!/usr/bin/env python3
"""Regression cases for the Python delivery checkers' shared contract (check.py, slop_check, placeholders,
contrast, state_check, review_report, design_md_check).

Usage: python3 evals/regress/test_py_checkers.py      (any cwd; writes only to a temp folder)

Contract: exit 0 ok, 1 check failed, 2 usage or input error (one "usage:" / "error:" line, never a
traceback), 3 not run. Fixtures live in evals/regress/py_checkers/ and are copied to a temp folder.
One PASS / FAIL / NOT RUN line per case. Exit 1 on any failure. Standard library only.
"""
import json, os, shutil, subprocess, sys, tempfile, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
FIX = os.path.join(HERE, "py_checkers")
results = []


def py(script, *a, cwd, env=None):
    r = subprocess.run([sys.executable, os.path.join(SCRIPTS, script), *a], cwd=cwd, capture_output=True,
                       text=True, timeout=300, env=env)
    return r.returncode, r.stdout, r.stderr


def case(name, ok, detail=""):
    results.append("PASS" if ok else "FAIL")
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + ("" if ok else f"\n      {str(detail).strip()[:600]}"))


def not_run(name, why):
    results.append("NOT RUN")
    print(f"NOT RUN  {name} ({why})")


def dwidth(t):
    return sum(0 if unicodedata.combining(c) or unicodedata.category(c) in ("Mn", "Me", "Cf")
               else 2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in t)


def main():
    tmp = tempfile.mkdtemp(prefix="ux-pycheck-")
    try:
        work = os.path.join(tmp, "fx")
        shutil.copytree(FIX, work)
        f = lambda n: os.path.join(work, n)
        cwd = os.path.join(tmp, "cwd")
        os.mkdir(cwd)
        nofile = f("nofile.html")

        # 1. usage and input errors: exit 2, a usage/error line on stderr, never a traceback
        bad = os.path.join(tmp, "bad.json")
        open(bad, "w").write("{not json")
        tpl = json.loads(py("review_report.py", "--template", cwd=cwd)[1])
        str_score = json.loads(json.dumps(tpl)); str_score["dimensions"][0]["score"] = "8"
        no_score = json.loads(json.dumps(tpl)); del no_score["dimensions"][1]["score"]
        for n, d in (("str-score.json", str_score), ("no-score.json", no_score)):
            json.dump(d, open(os.path.join(tmp, n), "w"))
        usage = [
            ("slop_check: missing file", "slop_check.py", [nofile]),
            ("slop_check: no args", "slop_check.py", []),
            ("placeholders: missing file", "placeholders.py", [nofile]),
            ("placeholders: --md without a path", "placeholders.py", [f("attrs.html"), "--md"]),
            ("contrast: missing pairs file", "contrast.py", [nofile]),
            ("contrast: --css missing file", "contrast.py", ["--css", nofile]),
            ("contrast: named colours (red white)", "contrast.py", ["red", "white"]),
            ("contrast: malformed pairs JSON", "contrast.py", [bad]),
            ("state_check: --need without a value", "state_check.py", [work, "--need"]),
            ("state_check: missing path", "state_check.py", [nofile]),
            ("state_check: unknown state (--need loadin)", "state_check.py", [work, "--need", "loadin"]),
            ("review_report: string score", "review_report.py", [os.path.join(tmp, "str-score.json")]),
            ("review_report: missing score", "review_report.py", [os.path.join(tmp, "no-score.json")]),
            ("review_report: malformed JSON", "review_report.py", [bad]),
            ("review_report: missing file", "review_report.py", [nofile]),
            ("design_md_check: missing file", "design_md_check.py", [nofile]),
            ("check.py: bad --admin type", "check.py", [f("meta-ok.html"), "--admin", "table"]),
            ("check.py: no page", "check.py", []),
        ]
        for name, script, args in usage:
            code, out, err = py(script, *args, cwd=cwd)
            case(f"usage: {name} -> exit 2, no traceback", code == 2 and "Traceback" not in out + err
                 and any(l.startswith(("usage:", "error:")) or ": error:" in l for l in err.splitlines()), f"exit {code}\n{out}{err}")
        code, out, err = py("check.py", nofile, cwd=cwd)
        case("check.py: page not found -> ERROR line, exit 2", code == 2 and "page not found" in out, f"exit {code}\n{out}{err}")
        case("no stray files written into cwd by the usage cases", os.listdir(cwd) == [], os.listdir(cwd))

        # 2. review_report writes next to the input JSON (not into cwd), or to --out
        sub = os.path.join(tmp, "review")
        os.mkdir(sub)
        json.dump(tpl, open(os.path.join(sub, "findings.json"), "w"))
        code, out, err = py("review_report.py", os.path.join(sub, "findings.json"), cwd=cwd)
        case("review_report: default output next to findings.json", code == 0 and os.path.isfile(os.path.join(sub, "review.html"))
             and not os.path.exists(os.path.join(cwd, "review.html")), f"exit {code}\n{out}{err}")
        dest = os.path.join(tmp, "elsewhere.html")
        code, out, err = py("review_report.py", os.path.join(sub, "findings.json"), "--out", dest, cwd=cwd)
        case("review_report: --out honoured", code == 0 and os.path.isfile(dest), f"exit {code}\n{out}{err}")

        # 3. check.py: meta placeholders, exit codes, --json, NOT RUN without node
        code, out, err = py("check.py", f("meta-ph.html"), cwd=cwd)
        meta = out[out.find(" meta\n"):out.find(" script")]
        case("check.py meta: example.com / example.org and [ ] / {{ }} -> FLAG, exit 1",
             code == 1 and "FLAG     meta" in out and "canonical" in meta and "og:url" in meta and "og:image" in meta
             and "og:title: [ชื่อคลินิก]" in meta and "description: {{description}}" in meta and "in title:" in meta
             and "og:description" not in meta, out + err)
        code, out, err = py("check.py", f("meta-ok.html"), cwd=cwd)
        case("check.py meta: real metadata (attributes in any order) -> PASS", "PASS     meta" in out, out + err)
        code, out, err = py("check.py", f("meta-ph.html"), "--json", cwd=cwd)
        try:
            rep = json.loads(out)
            st = {c["name"]: c["status"] for c in rep[0]["checks"]}
            ok = st.get("meta") == "FLAG" and code == 1 and set(st) >= {"meta", "slop", "contrast", "states"}
        except (ValueError, KeyError, IndexError, TypeError) as e:
            ok, rep = False, e
        case("check.py --json: list of pages with per-check status", ok, f"exit {code}\n{out[:400]}{err}")
        empty = os.path.join(tmp, "empty-path")
        os.mkdir(empty)
        env = dict(os.environ, PATH=empty)                  # no node on PATH; python runs by absolute path
        code, out, err = py("check.py", f("meta-ok.html"), cwd=cwd, env=env)
        case("check.py: no node -> script NOT RUN, exit 3 (nothing failed)",
             code == 3 and "NOT RUN  script" in out and "PASS     meta" in out and "FAIL" not in out, f"exit {code}\n{out}{err}")
        code, out, err = py("check.py", f("meta-ph.html"), cwd=cwd, env=env)
        case("check.py: a FLAG outranks NOT RUN -> exit 1", code == 1 and "NOT RUN  script" in out, f"exit {code}\n{out}{err}")

        # 4. placeholders: attribute placeholders, Thai alignment by display width
        code, out, err = py("placeholders.py", f("attrs.html"), "--json", cwd=cwd)
        try:
            rows = json.loads(out)
            attr = {r["placeholder"]: r["where"] for r in rows if r["kind"] == "attribute"}
            text = {r["placeholder"] for r in rows if r["kind"] == "text"}
            ok = (attr.get("[ชื่อคลินิก]") == ["aria-label", "meta og:title"] and "{{tagline}}" in attr and "[รูปทันตแพทย์]" in attr
                  and "[tooltip]" in attr and "[เบอร์โทร]" in attr and "[not a placeholder]" not in set(attr) | text
                  and "0x-xxx-xxxx" in text and "[ชื่อทันตแพทย์]" in text and code == 0)
        except (ValueError, KeyError, TypeError):
            ok = False
        case("placeholders: og:*, alt, aria-label, title, placeholder reported as attribute placeholders", ok, out + err)
        code, out, err = py("placeholders.py", f("attrs.html"), cwd=cwd)
        body = [l for l in out.splitlines() if l.startswith("  ")]
        widths = set()
        for l in body:
            head = l.split("  (")[0]                       # drop the "(where)" suffix of attribute rows
            widths.add(dwidth(head[:head.rstrip().rindex(" ")]))
        case("placeholders: columns aligned by display width (Thai marks zero-width)", len(body) >= 8 and len(widths) == 1,
             f"widths {sorted(widths)}\n{out}")
        case("placeholders: attribute section printed", "attribute placeholder(s)" in out and "(aria-label, meta og:title)" in out, out)

        # 5. slop_check: rule id spelling, --json
        code, out, err = py("slop_check.py", f("meta-ok.html"), "--json", cwd=cwd)
        try:
            rules = {r["rule"] for r in json.loads(out)[f("meta-ok.html")]}
        except (ValueError, KeyError):
            rules = set()
        case("slop: rule id is unthemed-browser-surfaces (typo fixed)", "untheemed-browser-surfaces" not in out
             and "unthemed-browser-surfaces" in rules, out[:400])
        code, out, err = py("slop_check.py", f("attrs.html"), cwd=cwd)
        case("slop: untheemed id gone from text output", "untheemed" not in out and code in (0, 1), out)

        # 6. design_md_check: letterSpacing units, Thai detection
        code, out, err = py("design_md_check.py", f("design-ls.md"), "--json", cwd=cwd)
        try:
            msgs = [(r["level"], r["message"]) for r in json.loads(out)]
        except ValueError:
            msgs = []
        case("design_md_check: unitless letterSpacing 0.02 -> error", code == 1 and any(l == "error" and "body-md.letterSpacing" in m for l, m in msgs), out)
        case("design_md_check: letterSpacing 0 -> warn 'use 0em'", any(l == "warn" and "label.letterSpacing" in m and "0em" in m for l, m in msgs), out)
        case("design_md_check: -0.02em accepted", not any("display.letterSpacing" in m for _, m in msgs), out)
        case("design_md_check: 'thai' in a path is not Thai text", not any("Thai" in m for _, m in msgs), out)
        code, out, err = py("design_md_check.py", f("design-thai.md"), cwd=cwd)
        case("design_md_check: Thai font name triggers the Thai line-height check", "Thai is used but body lineHeight is 1.4" in out, out)

        # 7. contrast: shared _color maths (3/4/6/8-digit hex), --json
        code, out, err = py("contrast.py", "#000f", "#ffffffff", cwd=cwd)
        case("contrast: 4- and 8-digit hex parsed via _color.py", code == 0 and out.strip() == "21.00:1", out + err)
        code, out, err = py("contrast.py", "#777", "#fff", "--json", cwd=cwd)
        try:
            ok = abs(json.loads(out)["ratio"] - 4.48) < 0.01 and code == 0
        except (ValueError, KeyError):
            ok = False
        case("contrast: --json single pair", ok, out + err)

        # 8. bug-hunt regressions (one block per reproduced bug)
        bh = os.path.join(tmp, "bh")
        os.mkdir(bh)

        def put(name, text, mode="w"):
            p = os.path.join(bh, name)
            with open(p, mode, **({} if "b" in mode else {"encoding": "utf-8"})) as fh:
                fh.write(text)
            return p

        def err2(code, out, err):        # contract: exit 2, exactly one "error:" line on stderr, no traceback
            lines = [l for l in err.splitlines() if l.strip()]
            return code == 2 and "Traceback" not in out + err and len(lines) == 1 and lines[0].startswith("error:")

        # bug 1: slop_check traversal is iterative (1000 unclosed <li> / <p> nest 1000 deep)
        for name, page in (("deep-li.html", "<ul>" + "<li>item" * 1000 + "</ul>"), ("deep-p.html", "<div>" + "<p>x" * 1500 + "</div>")):
            code, out, err = py("slop_check.py", put(name, page), "--json", cwd=cwd)
            try:
                ok = code in (0, 1) and "Traceback" not in err and isinstance(json.loads(out), dict)
            except ValueError:
                ok = False
            case(f"slop: {name} (1000+ unclosed nested tags) -> normal result, no RecursionError", ok, f"exit {code}\n{err[-300:]}")

        # bug 2: placeholders --md to a directory / missing folder / non-UTF-8 file -> one error line, exit 2
        bin_md = put("utf16.md", b"\xff\xfe# x\n", "wb")
        for label, md in (("a directory", bh), ("a missing folder", os.path.join(bh, "nope", "README.md")), ("a non-UTF-8 file", bin_md)):
            code, out, err = py("placeholders.py", f("attrs.html"), "--md", md, cwd=cwd)
            case(f"placeholders: --md to {label} -> error line, exit 2", err2(code, out, err), f"exit {code}\n{out}{err}")
        case("placeholders: non-UTF-8 --md file left untouched", open(bin_md, "rb").read() == b"\xff\xfe# x\n")

        # bug 3: review_report type-checks text fields and list items; no 0-byte review.html on failure
        dims3 = [{"name": n, "score": 7} for n in "ABC"]
        for label, extra in (("evidence 5", {"dimensions": [dict(dims3[0], evidence=5)] + dims3[1:]}), ("keep [1]", {"keep": [1]}),
                             ("title null", {"title": None}), ("quick item null", {"quick": [None]}), ("fix text 3", {"dimensions": [dict(dims3[0], fix=3)] + dims3[1:]})):
            rdir = os.path.join(bh, "rr-" + label.replace(" ", "-"))
            os.mkdir(rdir)
            fj = os.path.join(rdir, "findings.json")
            json.dump(dict({"title": "R", "dimensions": dims3}, **extra), open(fj, "w"))
            code, out, err = py("review_report.py", fj, cwd=cwd)
            case(f"review_report: {label} -> error line, exit 2, no review.html left", err2(code, out, err)
                 and os.listdir(rdir) == ["findings.json"], f"exit {code}\n{out}{err}{os.listdir(rdir)}")

        # bug 12: a non-integer score is banded by its whole part (6.5 Functional, 8.9 Strong, 4.5 Broken)
        fj = os.path.join(bh, "frac.json")
        json.dump({"title": "R", "dimensions": [{"name": "A", "score": 6.5}, {"name": "B", "score": 8.9}, {"name": "C", "score": 4.5}]}, open(fj, "w"))
        code, out, err = py("review_report.py", fj, "--out", os.path.join(bh, "frac.html"), cwd=cwd)
        page = open(os.path.join(bh, "frac.html"), encoding="utf-8").read() if code == 0 else ""
        case("review_report: 6.5 Functional, 8.9 Strong, 4.5 Broken", "6.5/10 · Functional" in page and "8.9/10 · Strong" in page
             and "4.5/10 · Broken" in page, f"exit {code}\n{out}{err}")

        # bug 4: a selector list spanning lines (":root,\n:host {") is a token block
        code, out, err = py("contrast.py", "--css", put("host.css", ":root,\n:host {\n  --bg: #ffffff;\n  --ink: #bbbbbb;\n}\n"), cwd=cwd)
        case("contrast: multi-line ':root,\\n:host' block checked -> FAIL, exit 1", code == 1 and "FAIL" in out and "N/A" not in out, f"exit {code}\n{out}{err}")

        # bug 5: ":root:not(.dark)" is a light block, checked on the light ground
        code, out, err = py("contrast.py", "--css", put("notdark.css", ":root{--bg:#ffffff;--ink:#111111}\n.dark{--bg:#000000;--ink:#eeeeee}\n"
                                                         ":root:not(.dark){--muted:#999999}\n"), "--json", cwd=cwd)
        try:
            row = next(r for r in json.loads(out) if r["fg"] == "--muted")
            ok = code == 1 and row["theme"] == "light" and row["bg_value"] == "#ffffff" and row["status"] == "FAIL"
            ok = ok and any(r["block"] == ".dark" and r["theme"] == "dark" for r in json.loads(out))
        except (ValueError, StopIteration, KeyError, TypeError):
            ok = False
        case("contrast: :root:not(.dark) is light (muted on #fff FAIL), .dark still dark", ok, f"exit {code}\n{out}{err}")

        # bug 11: named colours, opaque "/ 1" / "/ 100%" alpha and !important resolve; translucent stays unresolved
        for label, css in (("named white", ":root{--bg:white;--ink:#bbbbbb}"), ("oklch / 1", ":root{--bg:#fff;--ink:oklch(80% 0 0 / 1)}"),
                           ("rgb / 100%", ":root{--bg:#fff;--ink:rgb(187 187 187 / 100%)}"), ("rgba(..., 1)", ":root{--bg:#fff;--ink:rgba(187,187,187,1)}"),
                           ("hsl / 1", ":root{--bg:#fff;--ink:hsl(0 0% 73% / 1)}"), ("!important", ":root{--bg:#ffffff;--ink:#BBBBBB !important}")):
            code, out, err = py("contrast.py", "--css", put("c11.css", css), cwd=cwd)
            case(f"contrast: {label} resolves -> FAIL, exit 1", code == 1 and "FAIL" in out, f"exit {code}\n{out}{err}")
        code, out, err = py("contrast.py", "--css", put("c11.css", ":root{--bg:#fff;--ink:rgb(0 0 0 / .5)}"), cwd=cwd)
        case("contrast: translucent rgb(… / .5) still unresolved -> N/A, exit 0", code == 0 and out.startswith("N/A"), f"exit {code}\n{out}{err}")

        # bug 6: --matrix and --per-file scan every path given, not only the first
        sa = put("sa.html", '<div class="skeleton"></div>')
        sb = put("sb.js", 'fetch("/api/x")')
        code, out, err = py("state_check.py", sa, sb, "--matrix", cwd=cwd)
        case("state_check --matrix: a row per path given", code == 0 and "| sa.html |" in out and "| sb.js |" in out, f"exit {code}\n{out}{err}")
        code, out, err = py("state_check.py", sa, sb, "--per-file", cwd=cwd)
        case("state_check --per-file: gaps in the second path found", code == 1 and "sb.js: fetches data" in out, f"exit {code}\n{out}{err}")

        # bug 13: a folder with no source files -> error line, exit 2 (not "0 files scanned", all MISS)
        emptydir = os.path.join(bh, "nosrc")
        os.mkdir(emptydir)
        for extra in ([], ["--matrix"], ["--per-file"]):
            code, out, err = py("state_check.py", emptydir, *extra, cwd=cwd)
            case(f"state_check {' '.join(extra) or '(default)'}: empty folder -> error line, exit 2", err2(code, out, err), f"exit {code}\n{out}{err}")

        # bug 7: a DD/MM date in the decision log is not a dial; a real out-of-range dial still is
        dm_head = '---\nname: Shop\nversion: alpha\ncolors:\n  primary: "#0f6e64"\n---\n## Overview\nStatus: draft\n'
        code, out, err = py("design_md_check.py", put("dm-date.md", dm_head + "## Decision log\n- 15/10/2026 picked teal\n- 2026/10/15 again\n"), "--json", cwd=cwd)
        case("design_md_check: dates 15/10/2026, 2026/10/15 are not dials", "dial value out of range" not in out and code == 0, f"exit {code}\n{out}{err}")
        code, out, err = py("design_md_check.py", put("dm-dial.md", dm_head + "## Dials\n- variance 12/10\n"), "--json", cwd=cwd)
        case("design_md_check: dial 12/10 still an error", code == 1 and "dial value out of range: 12/10" in out, f"exit {code}\n{out}{err}")

        # bug 8: a UTF-8 BOM does not hide the front matter
        code, out, err = py("design_md_check.py", put("dm-bom.md", "\ufeff" + dm_head + "## Decision log\n- 2026-10-15 picked teal\n"), cwd=cwd)
        case("design_md_check: BOM file still read as front matter (not legacy)", "no YAML front matter" not in out and code == 0, f"exit {code}\n{out}{err}")

        # bug 9: outline values matched whole (0.5px is not removal; 0px / 0em / none are)
        for css, want in (("a:focus{outline: 0.5px solid #333}", False), ("a{outline: 0px}", True), ("a{outline:0em;color:#123}", True),
                          ("a{outline: none !important}", True), ("a{outline:0}", True), ("a{outline: 0 solid red}", False)):
            code, out, err = py("slop_check.py", put("ol.html", f"<style>{css}</style><a href='/'>x</a>"), "--json", cwd=cwd)
            try:
                got = any(r["rule"] == "focus-removed" for r in json.loads(out)[os.path.join(bh, "ol.html")])
            except (ValueError, KeyError):
                got = None
            case(f"slop: '{css}' focus-removed={want}", got is want, f"exit {code}\n{out[:300]}{err}")

        # bug 10: border-color:#000 is not "pure black text or ground"; color:#000 still is
        for css, want in ((".box{border-color:#000}", False), (".box{outline-color:black}", False), (".box{color:#000}", True), (".box{background-color:#000000}", True)):
            code, out, err = py("slop_check.py", put("pb.html", f"<style>{css}</style><div class=box>x</div>"), "--json", cwd=cwd)
            try:
                got = any(r["rule"] == "pure-black" for r in json.loads(out)[os.path.join(bh, "pb.html")])
            except (ValueError, KeyError):
                got = None
            case(f"slop: '{css}' pure-black={want}", got is want, f"exit {code}\n{out[:300]}{err}")
        case("no stray files written into cwd by the bug-hunt cases", os.listdir(cwd) == [], os.listdir(cwd))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    n = {k: results.count(k) for k in ("PASS", "FAIL", "NOT RUN")}
    print(f"\n{n['PASS']} passed, {n['FAIL']} failed, {n['NOT RUN']} not run")
    return 1 if n["FAIL"] else 0


if __name__ == "__main__":
    sys.exit(main())
