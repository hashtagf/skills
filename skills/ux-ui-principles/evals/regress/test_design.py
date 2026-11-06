#!/usr/bin/env python3
"""Regression cases for the design-system / token scripts (design_md, design_md_check, export_tokens,
code_extract, tweaks_panel, brand.js).

Usage: python3 evals/regress/test_design.py      (any cwd; writes only to a temp folder)

Fixtures live in evals/regress/design/. Every script runs with cwd = a temp folder and PYTHONDONTWRITEBYTECODE,
so nothing lands in the repo. One PASS / FAIL / NOT RUN line per case (NOT RUN: node missing, not a failure).
Exit 1 on any failure. Standard library only.
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(os.path.dirname(HERE))
SCRIPTS = os.path.join(SKILL, "scripts")
FIX = os.path.join(HERE, "design")
NODE = shutil.which("node")
sys.dont_write_bytecode = True
sys.path.insert(0, SCRIPTS)
from _color import ratio  # noqa: E402

results = []


def run(cmd, cwd):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=300, env=env)
    return r.returncode, r.stdout + r.stderr


def py(script, *a, cwd):
    return run([sys.executable, os.path.join(SCRIPTS, script), *a], cwd)


def node(code, cwd):
    return run([NODE, "-e", code], cwd)


def case(name, ok, detail=""):
    results.append(("PASS" if ok else "FAIL", name))
    print(("PASS  " if ok else "FAIL  ") + name + ("" if ok else "\n      " + str(detail)[:600].replace("\n", "\n      ")))


def not_run(name, why):
    results.append(("NOT RUN", name))
    print("NOT RUN  %s (%s)" % (name, why))


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, text):
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def front(md, key):
    m = re.search(r"^\s*%s:\s*\"?([^\"\n]*)\"?\s*$" % re.escape(key), md.split("\n---", 1)[0], re.M)
    return m.group(1) if m else None


def css_var(css, name, block=0):
    """Value comment (#hex) of --name in the n-th block that defines it."""
    vals = re.findall(r"--%s:\s*[^;]+;\s*/\*\s*(#[0-9a-f]{6})" % re.escape(name), css)
    return vals[block] if len(vals) > block else None


def main():
    tmp = tempfile.mkdtemp(prefix="regress-design-")
    try:
        iv_br, iv_co = os.path.join(FIX, "iv_bracket.json"), os.path.join(FIX, "iv_colon.json")

        # 1. design_md builds before it writes: a failed run leaves no DESIGN.md (and no folder); a rerun works
        code, out = py("design_md.py", "nope", "--interview", iv_br, "--out", "e3", cwd=tmp)
        case("bug1 unknown direction: exit !=0 and no DESIGN.md/folder left",
             code != 0 and not os.path.exists(os.path.join(tmp, "e3")), (code, out, os.listdir(tmp)))
        code, out = py("design_md.py", "grid", "--interview", iv_br, "--out", "e3", cwd=tmp)
        case("bug1 rerun after failure writes DESIGN.md (no 'already exists')", code == 0 and os.path.getsize(os.path.join(tmp, "e3", "DESIGN.md")) > 0, out)
        code, out = py("design_md.py", "--backoffice", "nope", "--out", "e4", cwd=tmp)
        case("bug1 --backoffice unknown look: exit !=0 and nothing left", code != 0 and not os.path.exists(os.path.join(tmp, "e4")), (code, out))
        os.makedirs(os.path.join(tmp, "e5"))
        code, out = py("design_md.py", "nope", "--interview", iv_br, "--out", "e5", cwd=tmp)
        case("bug1 existing folder: no 0-byte DESIGN.md and no temp file", code != 0 and os.listdir(os.path.join(tmp, "e5")) == [], os.listdir(os.path.join(tmp, "e5")))

        # 2. name / description are quoted; the checker rejects unquoted values YAML would not read as a string
        for label, iv, brand in (("bracket", iv_br, "[ชื่อคลินิก]"), ("colon", iv_co, "Acme: Dental #1")):
            o = os.path.join(tmp, "q_" + label)
            code, out = py("design_md.py", "cobalt", "--interview", iv, "--out", o, cwd=tmp)
            md = read(os.path.join(o, "DESIGN.md"))
            case("bug2 %s brand written quoted" % label, ('name: %s' % json.dumps(brand, ensure_ascii=False)) in md, md[:200])
            code, out = py("design_md_check.py", os.path.join(o, "DESIGN.md"), cwd=tmp)
            case("bug2 %s quoted name passes the checker" % label, code == 0, out)
            bad = os.path.join(o, "unquoted.md")
            write(bad, md.replace('name: %s' % json.dumps(brand, ensure_ascii=False), "name: " + brand, 1))
            code, out = py("design_md_check.py", bad, cwd=tmp)
            case("bug2 %s unquoted name fails the checker" % label, code == 1 and "not a plain YAML string" in out, out)
        bad = os.path.join(tmp, "desc.md")
        write(bad, re.sub(r"^description: .*$", "description: {oops}", md, count=1, flags=re.M))
        code, out = py("design_md_check.py", bad, cwd=tmp)
        case("bug2 unquoted description starting with { fails", code == 1 and "description is not a plain YAML string" in out, out)
        bo = os.path.join(tmp, "bo_q")
        py("design_md.py", "--backoffice", "calm", "--interview", iv_co, "--out", bo, cwd=tmp)
        case("bug2 --backoffice name quoted", 'name: "Acme: Dental #1"' in read(os.path.join(bo, "DESIGN.md")))
        fc = os.path.join(tmp, "fc")
        code, out = py("design_md.py", "--from-code", os.path.join(FIX, "site"), "--interview", iv_br, "--out", fc, cwd=tmp)
        case("bug2 --from-code name quoted", 'name: "[ชื่อคลินิก]"' in read(os.path.join(fc, "DESIGN.md")), out)

        # 3. code_extract on HTML reads only <style> (and linked local CSS); light/dark per block
        code, out = py("code_extract.py", os.path.join(FIX, "site"), "--json", cwd=tmp)
        res = json.loads(out) if code == 0 else {}
        light, dark = res.get("light", {}), res.get("dark", {})
        case("bug3 HTML: light canvas found from --ground (#faf7ef), not guessed #ffffff",
             light.get("canvas") == "#faf7ef" and "--ground" in res.get("light_evidence", {}).get("canvas", ""), (light, res.get("light_evidence")))
        case("bug3 HTML: light/dark split per block (13 light, 5 dark vars)",
             len(res.get("vars_light", {})) == 13 and len(res.get("vars_dark", {})) == 5, (list(res.get("vars_light", {})), list(res.get("vars_dark", {}))))
        case("bug3 HTML: dark canvas from the @media block", dark.get("canvas") == "#13110c", dark)
        case("bug3 HTML: :root:not(.dark) counts as light", "--tint-1" in res.get("vars_light", {}))
        case("bug3 HTML: linked local stylesheet (public/extra.css) read", light.get("focus") == "#007948" and "--focus" in res.get("light_evidence", {}).get("focus", ""), res.get("light_evidence"))

        # 4. squeeze: cardInk / cardMuted honoured; text roles checked on surface too, light and dark
        code, out = py("export_tokens.py", "squeeze", cwd=tmp)
        css = out
        case("bug4 squeeze export passes all pairs", code == 0 and "all pairs pass" in out, out[-600:])
        case("bug4 squeeze surface-ink = cardInk #0b2a18, surface-muted = cardMuted #3d5a48",
             css_var(css, "color-surface-ink") == "#0b2a18" and css_var(css, "color-surface-muted") == "#3d5a48", (css_var(css, "color-surface-ink"), css_var(css, "color-surface-muted")))
        sat, sf, srf = css_var(css, "color-surface-accent-text"), css_var(css, "color-surface-focus"), css_var(css, "color-surface")
        case("bug4 squeeze surface-accent-text 4.5:1 and surface-focus 3:1 on the cream card",
             sat and sf and ratio(sat, srf) >= 4.5 and ratio(sf, srf) >= 3.0, (sat, sf, srf))
        o = os.path.join(tmp, "sq")
        py("design_md.py", "squeeze", "--interview", iv_co, "--out", o, cwd=tmp)
        md = read(os.path.join(o, "DESIGN.md"))
        case("bug4 squeeze DESIGN.md has dark-on-card #0b2a18 and card textColor on-card",
             front(md, "dark-on-card") == "#0b2a18" and '"{colors.on-card}"' in md, md[:1500])
        code, out = py("design_md_check.py", os.path.join(o, "DESIGN.md"), cwd=tmp)
        case("bug4 squeeze DESIGN.md passes the checker", code == 0, out)
        bad = os.path.join(o, "nocard.md")
        write(bad, "\n".join(l for l in md.split("\n") if not re.match(r"\s+(dark-)?(on-card|card-muted|card-primary-text|card-focus):", l)))
        code, out = py("design_md_check.py", bad, cwd=tmp)
        case("bug4 checker errors on dark-on-surface == dark-surface (old squeeze output)",
             code == 1 and "dark-on-surface on dark-surface" in out, out)
        code, out = py("export_tokens.py", "cobalt", cwd=tmp)
        dk = out.split('[data-theme="dark"]', 1)[-1]
        at, s2 = css_var(dk, "color-accent-text"), css_var(dk, "color-surface")
        case("bug4 derived dark accent-text reaches 4.5:1 on the dark surface too (cobalt)", at and ratio(at, s2) >= 4.5, (at, s2, at and ratio(at, s2)))
        code, out = py("export_tokens.py", "--list", cwd=tmp)
        ids = [x.strip() for x in out.split(",") if x.strip()]
        fails = []
        for i in ids:
            c, o2 = py("export_tokens.py", i, cwd=tmp)
            if c != 0:
                fails.append((i, o2[-300:]))
        case("bug4 all %d directions export with every pair passing" % len(ids), len(ids) >= 58 and not fails, fails[:3])
        fails = []
        for i in ids:
            o3 = os.path.join(tmp, "all", i)
            c, o2 = py("design_md.py", i, "--interview", iv_br, "--out", o3, cwd=tmp)
            c2, o4 = py("design_md_check.py", os.path.join(o3, "DESIGN.md"), cwd=tmp)
            if c or c2:
                fails.append((i, o2[-200:], o4[-300:]))
        case("bug4/5 all directions: DESIGN.md passes design_md_check (errors on AA)", not fails, fails[:3])

        # 5. back office: on-primary / primary-text derived; checker errors on a failed AA pair
        looks = json.load(open(os.path.join(SKILL, "assets", "backoffice", "styles.json")))
        looks = looks.get("styles", looks) if isinstance(looks, dict) else looks
        looks = [x["id"] for x in (looks if isinstance(looks, list) else looks.values())]
        fails = []
        for s in looks:
            o = os.path.join(tmp, "bo", s)
            py("design_md.py", "--backoffice", s, "--out", o, cwd=tmp)
            c, out = py("design_md_check.py", os.path.join(o, "DESIGN.md"), cwd=tmp)
            if c:
                fails.append((s, out))
        case("bug5 all %d back-office looks pass the checker" % len(looks), not fails, fails[:3])
        hb = read(os.path.join(tmp, "bo", "harbor", "DESIGN.md"))
        case("bug5 harbor on-primary reaches 4.5:1 on primary", ratio(front(hb, "on-primary"), front(hb, "primary")) >= 4.5, (front(hb, "on-primary"), front(hb, "primary")))
        fo = read(os.path.join(tmp, "bo", "forest", "DESIGN.md"))
        case("bug5 forest primary-text reaches 4.5:1 on canvas", ratio(front(fo, "primary-text"), front(fo, "canvas")) >= 4.5, front(fo, "primary-text"))
        bad = os.path.join(tmp, "bo", "harbor", "raw.md")
        write(bad, hb.replace('on-primary: "%s"' % front(hb, "on-primary"), 'on-primary: "#ffffff"', 1))
        code, out = py("design_md_check.py", bad, cwd=tmp)
        case("bug5 checker exits 1 on a failed AA text pair (raw white on harbor accent)", code == 1 and "on-primary on primary" in out, out)

        # 6. tweaks_panel: page variable names detected; ink on the accent by contrast ratio
        page = os.path.join(tmp, "accent-page.html")
        shutil.copy(os.path.join(FIX, "accent-page.html"), page)
        code, out = py("tweaks_panel.py", page, "--out", "t.html", cwd=tmp)
        html = read(os.path.join(tmp, "t.html")) if code == 0 else ""
        m = re.search(r"var V=(\{.*?\}),ACC=", html)
        v = json.loads(m.group(1)) if m else {}
        case("bug6 detects --accent / --on-accent / --accent-text / --focus", (v.get("accent"), v.get("ink"), v.get("text"), v.get("focus")) == ("--accent", "--on-accent", "--accent-text", "--focus"), (v, out))
        case("bug6 detects radius --r-card (pill skipped) and duration --speed", [r[0] for r in v.get("radius", [])] == ["--r-card"] and v.get("dur") == ["--speed"], v)
        code, out = py("tweaks_panel.py", page, "--out", "t2.html", "--accent-var", "--brand", "--dur-vars", "--a,--b", cwd=tmp)
        m2 = re.search(r"var V=(\{.*?\}),ACC=", read(os.path.join(tmp, "t2.html"))) if code == 0 else None
        v2 = json.loads(m2.group(1)) if m2 else {}
        case("bug6 explicit flags override detection", v2.get("accent") == "--brand" and v2.get("dur") == ["--a", "--b"], v2)
        if NODE and html:
            fns = "\n".join((re.search(r"^function %s\(.*$" % f, html, re.M) or re.match("", "")).group(0) for f in ("hx", "lum", "cr", "ink"))
            code, out = node(fns + "\nconsole.log(JSON.stringify(['#e07a2b','#2bb673','#1b3a8a','#fc0'].map(ink)))", tmp)
            case("bug6 ink picks #111111 on #e07a2b and #2bb673, white on #1b3a8a", code == 0 and json.loads(out) == ["#111111", "#111111", "#ffffff", "#111111"], out)
        else:
            not_run("bug6 ink by contrast in the panel script", "node not found")

        # 7. one radius rule for DESIGN.md and tokens
        o = os.path.join(tmp, "grid_round")
        py("design_md.py", "grid", "--interview", iv_br, "--out", o, cwd=tmp)
        md = read(os.path.join(o, "DESIGN.md"))
        code, out = py("export_tokens.py", "grid", "--shape", "soft", cwd=tmp)
        rc = re.search(r"--radius-card: (\d+)px; --radius-input: (\d+)px; --radius-button: ([\d]+px)", out)
        case("bug7 grid + round subject: DESIGN.md 24px/pill == export --shape soft 24px/999px",
             front(md, "lg") == "24px" and "{rounded.full}" in md and rc and rc.groups() == ("24", "14", "999px"), (front(md, "lg"), rc and rc.groups()))
        case("bug7 DESIGN.md decision log names --shape soft", "export_tokens.py grid --shape soft" in md)
        code, out = py("export_tokens.py", "grid", cwd=tmp)
        case("bug7 export without --shape keeps the direction (0px)", "--radius-card: 0px" in out)
        code, out = py("export_tokens.py", "grid", "--shape", "round", cwd=tmp)
        case("bug7 --shape rejects unknown values (exit 2)", code == 2, out)
        o = os.path.join(tmp, "atelier")
        py("design_md.py", "atelier", "--interview", iv_co, "--out", o, cwd=tmp)
        md = read(os.path.join(o, "DESIGN.md"))
        code, out = py("export_tokens.py", "atelier", cwd=tmp)
        rb = re.search(r"--radius-button: (\d+px)", out)
        case("bug7 atelier round button: DESIGN.md rounded.md == export --radius-button",
             rb and front(md, "md") == rb.group(1) and '"{rounded.md}"' in md, (front(md, "md"), rb and rb.group(1)))

        # 8. brand.js: 3-digit hex and the squeeze product style
        if NODE:
            b = json.dumps(os.path.join(SCRIPTS, "brand.js"))
            code, out = node("const b=require(%s);console.log(JSON.stringify([b.lum('#000'),b.lum('#fff'),b.contrast('#000','#fff'),b.lum('#0008'),b.lum('#00000080')]))" % b, tmp)
            vals = json.loads(out) if code == 0 else []
            case("bug8 brand.js lum('#000')=0, lum('#fff')=1, contrast 21:1, 4/8-digit parsed",
                 vals and vals[0] == 0 and vals[1] == 1 and round(vals[2]) == 21 and vals[3] == 0 and vals[4] == 0, out)
            dirs = json.dumps(os.path.join(SKILL, "assets", "directions", "directions.json"))
            sty = json.dumps(os.path.join(SKILL, "assets", "backoffice", "styles.json"))
            code, out = node("""const b=require(%s),fs=require('fs');let D=JSON.parse(fs.readFileSync(%s));D=Array.isArray(D)?D:D.directions;
let S=JSON.parse(fs.readFileSync(%s));S=S.styles||S;S=Array.isArray(S)?S:Object.values(S);const bad=[];
for(const d of D){const s=b.productStyle(d,S);for(const [n,f,g] of [['ink/surface',s.ink,s.surface],['muted/surface',s.muted,s.surface],['ink/ground',s.ink,s.ground],['accentInk/accent',s.accentInk,s.accent]])if(b.contrast(f,g)<4.5)bad.push(d.id+' '+n+' '+b.contrast(f,g).toFixed(2))}
console.log(JSON.stringify(bad))""" % (b, dirs, sty), tmp)
            case("bug4/8 brand.js productStyle: ink, muted on surface and ink on accent pass for every direction (squeeze incl.)", code == 0 and json.loads(out) == [], out)
        else:
            not_run("bug8 brand.js hex parsing", "node not found")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    nf = sum(1 for r in results if r[0] == "FAIL")
    print("%d pass, %d fail, %d not run" % (sum(1 for r in results if r[0] == "PASS"), nf, sum(1 for r in results if r[0] == "NOT RUN")))
    return 1 if nf else 0


if __name__ == "__main__":
    sys.exit(main())
