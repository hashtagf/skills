#!/usr/bin/env python3
"""Build a side-by-side report (one self-contained HTML file) from ab_run.py + ab_shots.js output.

Usage: python3 evals/ab_report.py OUT_DIR [REPORT.html]
Images are downscaled and embedded as data: URIs (needs Pillow). Runs scripts/slop_check.py on each result.
"""
import base64, html, io, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)


def img(path, width):
    if not os.path.exists(path):
        return ""
    from PIL import Image
    im = Image.open(path).convert("RGB")
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)))
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=72, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def slop(path):
    if not os.path.exists(path):
        return None
    out = subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "slop_check.py"), path, "--json"],
                         capture_output=True, text=True).stdout
    try:
        items = next(iter(json.loads(out).values()))
        return [f["rule"] for f in items if f.get("level") == "flag"]
    except Exception:
        return re.findall(r"\[flag\] ([\w-]+)", subprocess.run([sys.executable, os.path.join(SKILL, "scripts", "slop_check.py"), path],
                                                              capture_output=True, text=True).stdout)


def md(text):
    """Very small markdown: escape, then bold, code and line breaks."""
    t = html.escape(text.strip())
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    return t.replace("\n", "<br>")


def arm_block(out, t, arm, label):
    d = os.path.join(out, t["id"], arm)
    meta = json.load(open(os.path.join(d, "run.json"))) if os.path.exists(os.path.join(d, "run.json")) else {}
    answer = open(os.path.join(d, "ANSWER.md")).read() if os.path.exists(os.path.join(d, "ANSWER.md")) else ""
    page = os.path.join(d, t["open"])
    flags = slop(page)
    desk = img(os.path.join(out, f"{t['id']}-{arm}-desk.jpg"), 900)
    phone = img(os.path.join(out, f"{t['id']}-{arm}-phone.jpg"), 300)
    built = os.path.exists(page)
    reads = sorted(set(meta.get("skill_files_read", [])))
    facts = [f"<li><span>Cost</span><b>${(meta.get('cost') or 0):.2f}</b></li>",
             f"<li><span>Skill files read</span><b>{len(reads) if arm == 'with' else '—'}</b></li>",
             f"<li><span>Template-look flags</span><b>{'—' if flags is None else len(flags)}</b></li>"]
    shots = (f'<figure class="desk"><img src="{desk}" alt="{label}: desktop render of {t["title"]}"><figcaption>Desktop, 1440px</figcaption></figure>'
             f'<figure class="phone"><img src="{phone}" alt="{label}: phone render of {t["title"]}"><figcaption>Phone, 390px</figcaption></figure>'
             ) if built and desk else '<p class="none">No page was produced.</p>'
    files = f'<p class="reads">{", ".join(html.escape(os.path.basename(r)) for r in reads)}</p>' if arm == "with" and reads else ""
    fl = f'<p class="reads">Flags: {html.escape(", ".join(flags))}</p>' if flags else ""
    return f'''<div class="arm {arm}"><h4>{label}</h4><ul class="facts">{"".join(facts)}</ul>{files}{fl}
<div class="shots">{shots}</div>
<details><summary>Claude's answer</summary><div class="ans">{md(answer)}</div></details></div>'''


def main(out, dest):
    tasks = json.load(open(os.path.join(out, "tasks.json")))
    np = os.path.join(out, "notes.json")
    notes = json.load(open(np)) if os.path.exists(np) else {}
    secs = []
    for t in tasks:
        before = ""
        if t.get("fixture"):
            b = img(os.path.join(out, f"{t['id']}-before-desk.jpg"), 700)
            if b:
                before = f'<details class="before"><summary>Original page before the change</summary><img src="{b}" alt="Original {t["title"]} before any change"></details>'
        secs.append(f'''<section class="task" id="task-{t["id"].lower()}">
<header><span class="chip {t["field"]}">{t["field"]}</span><h3>{html.escape(t["title"])}</h3></header>
<blockquote>{html.escape(t["prompt"])}</blockquote>{before}{('<p class="verdict"><b>What I see:</b> ' + html.escape(notes[t["id"]]) + "</p>") if t["id"] in notes else ""}
<div class="pair">{arm_block(out, t, "with", "With the skill")}{arm_block(out, t, "without", "Without any skill")}</div></section>''')
    page = TEMPLATE.replace("{{SECTIONS}}", "\n".join(secs))
    open(dest, "w").write(page)
    print("wrote", dest, round(len(page) / 1e6, 2), "MB")


TEMPLATE = """<title>Skill vs No Skill</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Thai:wght@400;600&family=IBM+Plex+Sans:wght@400;600&family=IBM+Plex+Mono:wght@500&display=swap" rel="stylesheet">
<style>
/* Layout: one column of task sections, each a two-up comparison that stacks on phones */
:root{--bg:#f4f5f2;--panel:#ffffff;--ink:#1b1d1a;--muted:#5d625a;--line:#dcdfd8;--with:#1f6b4f;--with-soft:#e3f1ea;--without:#6b5a1f;--without-soft:#f3eedd;
  --sans:"IBM Plex Sans","IBM Plex Sans Thai",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#141613;--panel:#1d201c;--ink:#ecefe8;--muted:#a3a99e;--line:#30342e;--with:#7fd3ae;--with-soft:#1d3329;--without:#e0c77a;--without-soft:#332d1a;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#141613;--panel:#1d201c;--ink:#ecefe8;--muted:#a3a99e;--line:#30342e;--with:#7fd3ae;--with-soft:#1d3329;--without:#e0c77a;--without-soft:#332d1a;color-scheme:dark}
body{background:var(--bg);color:var(--ink);font:15px/1.55 var(--sans)}
main{max-width:1320px;margin:0 auto;padding-block:40px 64px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));display:grid;gap:48px}
h1{font-size:clamp(28px,4vw,40px);line-height:1.15;margin:0;text-wrap:balance}
.intro p{color:var(--muted);max-width:72ch;margin:10px 0 0}
.task{display:grid;gap:16px}
.task header{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.task h3{font-size:22px;margin:0}
.chip{font:500 12px var(--mono);letter-spacing:.04em;padding:3px 8px;border-radius:6px;border:1px solid var(--line);color:var(--muted)}
blockquote{margin:0;padding:12px 16px;background:var(--panel);border:1px solid var(--line);border-radius:10px;color:var(--muted);max-width:90ch}
.pair{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,520px),1fr));gap:16px}
.arm{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px;min-width:0;display:grid;gap:12px;align-content:start}
.arm h4{margin:0;font-size:16px}
.arm.with h4{color:var(--with)}.arm.without h4{color:var(--without)}
.facts{list-style:none;margin:0;padding:0;display:flex;flex-wrap:wrap;gap:8px}
.facts li{display:flex;gap:8px;align-items:baseline;padding:4px 10px;border-radius:8px;font-size:13px}
.with .facts li{background:var(--with-soft)}.without .facts li{background:var(--without-soft)}
.facts span{color:var(--muted)}.facts b{font-variant-numeric:tabular-nums}
.reads{margin:0;font:500 12px/1.5 var(--mono);color:var(--muted);overflow-wrap:anywhere}
.shots{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,150px);gap:12px;align-items:start}
figure{margin:0;display:grid;gap:4px}
figure img,.before img{display:block;width:100%;max-width:100%;border:1px solid var(--line);border-radius:8px;background:#fff}
.desk{max-height:640px;overflow:auto;border-radius:8px}
.phone{max-height:640px;overflow:auto}
figcaption{font-size:12px;color:var(--muted)}
.none{margin:0;padding:24px;border:1px dashed var(--line);border-radius:8px;color:var(--muted);text-align:center}
details summary{cursor:pointer;font-weight:600;font-size:14px}
details summary:focus-visible{outline:2px solid var(--ink);outline-offset:3px;border-radius:4px}
.ans{margin-top:8px;font-size:14px;color:var(--ink);max-height:420px;overflow:auto;padding-right:6px}
.ans code{font:500 12px var(--mono);background:var(--bg);padding:1px 4px;border-radius:4px}
.before img{max-width:700px;margin-top:8px}
.verdict{margin:0;max-width:90ch;padding:12px 16px;border-left:3px solid var(--ink);background:var(--panel);border-radius:0 10px 10px 0}
@media (max-width:560px){.shots{grid-template-columns:1fr}.phone{max-width:240px}}
</style>
<main>
<div class="intro"><h1>The same four tasks, with the ux-ui-principles skill and without any skill</h1>
<p>Round 2, after the skill gained a visual gate (look at the direction preview and recipe before building; run script_check and slop_check before delivering). Each task ran headless on Claude Sonnet twice: once with the skill loaded through its slash command, once with skills disabled. Both runs got the same prompt, could read and write files and run node/python3, and had no web access. Brownfield tasks started from the same fixture project. Screenshots are the first screens of the page each run left behind. "Template-look flags" counts patterns the skill's slop_check.py treats as generic; fewer is better, but read the screenshots, not only the number.</p></div>
{{SECTIONS}}
</main>
"""

if __name__ == "__main__":
    o = os.path.abspath(sys.argv[1])
    main(o, sys.argv[2] if len(sys.argv) > 2 else os.path.join(o, "report.html"))
