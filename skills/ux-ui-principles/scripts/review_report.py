#!/usr/bin/env python3
"""Turn review findings into a single self-contained HTML report (radar chart, scores with bands, Keep / Fix / Quick wins).

Usage:
  python3 review_report.py findings.json [--out review.html]
  python3 review_report.py --template        # prints an example findings.json

findings.json:
  {"title": "...", "artifact": "path or URL", "date": "YYYY-MM-DD", "verdict": "one line",
   "dimensions": [{"name": "Hierarchy", "score": 7, "evidence": "cite elements", "keep": "...", "fix": "...", "quick": "..."}],
   "keep": ["..."], "fix": [{"p": "P0", "text": "..."}], "quick": ["..."]}

Dimensions are the rubric criteria in references/review-loop.md §3-4 (3 to 8 per report, e.g. the 6 visual or 5 UX criteria). Score 0-10; bands: 0-4 Broken,
5-6 Functional, 7-8 Strong, 9-10 Exceptional. The report never averages: each dimension stands alone, so a
9 on one and a 4 on another stays visible. Standard library only.
"""
import html
import json
import math
import sys

TEMPLATE = {
    "title": "Review: landing page", "artifact": "index.html", "date": "2026-11-05",
    "verdict": "Strong direction, weak mobile hierarchy.",
    "dimensions": [
        {"name": "Direction consistency", "score": 8, "evidence": "Round buttons and leaf cards used on every section.", "keep": "Shape language", "fix": "Footer uses square chips", "quick": "Round the footer chips"},
        {"name": "Visual hierarchy", "score": 5, "evidence": "Hero headline wraps to 3 lines at 390px; CTA below the fold.", "keep": "Section rhythm", "fix": "Shorten the headline", "quick": "Set max 2 lines"},
        {"name": "Detail and craft", "score": 7, "evidence": "Spacing on a 4px scale; one off-scale 22px gap in the plan card.", "keep": "Type scale", "fix": "Off-scale gap", "quick": "Use 24px"},
        {"name": "Accessibility", "score": 9, "evidence": "Contrast passes in both themes; focus ring visible.", "keep": "Focus ring", "fix": "None", "quick": "None"}],
    "keep": ["Shape language", "Contrast in both themes"], "fix": [{"p": "P0", "text": "Hero headline over 2 lines on phone"}, {"p": "P1", "text": "Footer chips are square"}],
    "quick": ["Round the footer chips", "Cap the hero headline at 2 lines"],
}


def band(s):
    return "Broken" if s <= 4 else "Functional" if s <= 6 else "Strong" if s <= 8 else "Exceptional"


def radar(dims):
    n = len(dims)
    cx, cy, R = 170, 170, 120
    pt = lambda i, v: (cx + R * v / 10 * math.sin(2 * math.pi * i / n), cy - R * v / 10 * math.cos(2 * math.pi * i / n))
    out = ['<svg viewBox="-60 0 460 340" role="img" aria-label="Radar chart of %d scores" width="460" height="340">' % n]
    for ring in (2, 4, 6, 8, 10):
        out.append('<polygon points="%s" fill="none" stroke="#d6d9de"/>' % " ".join("%.1f,%.1f" % pt(i, ring) for i in range(n)))
    for i, d in enumerate(dims):
        x, y = pt(i, 10)
        out.append('<line x1="%d" y1="%d" x2="%.1f" y2="%.1f" stroke="#d6d9de"/>' % (cx, cy, x, y))
        lx, ly = pt(i, 11.8)
        anchor = "middle" if abs(lx - cx) < 12 else ("start" if lx > cx else "end")
        out.append('<text x="%.1f" y="%.1f" font-size="11" text-anchor="%s" fill="#4a5160">%s</text>' % (lx, ly + 4, anchor, html.escape(d["name"][:22])))
    out.append('<polygon points="%s" fill="rgba(42,109,244,.18)" stroke="#2a6df4" stroke-width="2"/>' % " ".join("%.1f,%.1f" % pt(i, d["score"]) for i, d in enumerate(dims)))
    for i, d in enumerate(dims):
        x, y = pt(i, d["score"])
        out.append('<circle cx="%.1f" cy="%.1f" r="4" fill="#2a6df4"/>' % (x, y))
    out.append("</svg>")
    return "".join(out)


def render(d):
    e = html.escape
    dims = d["dimensions"]
    cards = ""
    for x in dims:
        b = band(x["score"])
        cards += '<section class="card"><div class="top"><h3>%s</h3><span class="sc %s">%s/10 · %s</span></div><p>%s</p><ul><li><b>Keep</b> %s</li><li><b>Fix</b> %s</li><li><b>Quick win</b> %s</li></ul></section>' % (
            e(x["name"]), b.lower(), x["score"], b, e(x.get("evidence", "")), e(x.get("keep", "-")), e(x.get("fix", "-")), e(x.get("quick", "-")))
    li = lambda items: "".join("<li>%s</li>" % e(i if isinstance(i, str) else "%s %s" % (i.get("p", ""), i.get("text", ""))) for i in items) or "<li>None</li>"
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%s</title>
<style>:root{--ink:#16181d;--m:#4a5160;--ln:#d6d9de}*{box-sizing:border-box}body{margin:0;background:#f6f7f9;color:var(--ink);font:15px/1.5 system-ui,"Noto Sans Thai",sans-serif}
main{max-width:1100px;margin:0 auto;padding:28px 20px 60px}h1{font-size:26px;margin:0 0 4px}.sub{color:var(--m);margin:0 0 18px}
.hero{display:grid;grid-template-columns:460px 1fr;gap:24px;align-items:center;background:#fff;border:1px solid var(--ln);border-radius:14px;padding:18px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-top:16px}.card{background:#fff;border:1px solid var(--ln);border-radius:14px;padding:16px}
.top{display:flex;justify-content:space-between;gap:8px;align-items:center}h3{margin:0;font-size:16px}h2{font-size:18px;margin:26px 0 8px}
.sc{font:700 12px system-ui;padding:3px 10px;border-radius:99px;white-space:nowrap}.broken{background:#fde4e1;color:#8a1c12}.functional{background:#fdf0d0;color:#7a4b00}.strong{background:#dff1e5;color:#14573a}.exceptional{background:#d9e6ff;color:#1c3f96}
ul{padding-left:18px;margin:8px 0 0}.lists{margin-top:16px;display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px}.lists>div{background:#fff;border:1px solid var(--ln);border-radius:14px;padding:6px 18px 14px}
@media(max-width:800px){.hero{grid-template-columns:1fr}svg{max-width:100%%;height:auto}}</style><main>
<h1>%s</h1><p class="sub">%s · %s</p>
<div class="hero">%s<div><p style="font-size:18px;margin:0 0 10px"><b>%s</b></p><p class="sub" style="margin:0">Scores are not averaged: each dimension stands alone so a strong one never hides a broken one.</p></div></div>
<div class="grid">%s</div>
<div class="lists"><div><h2>Keep</h2><ul>%s</ul></div><div><h2>Fix</h2><ul>%s</ul></div><div><h2>Quick wins</h2><ul>%s</ul></div></div></main></html>""" % (
        e(d.get("title", "Review")), e(d.get("title", "Review")), e(d.get("artifact", "")), e(d.get("date", "")), radar(dims), e(d.get("verdict", "")), cards,
        li(d.get("keep", [])), li(d.get("fix", [])), li(d.get("quick", [])))


def main():
    a = sys.argv[1:]
    if "--template" in a:
        print(json.dumps(TEMPLATE, indent=2))
        return
    files = [x for x in a if not x.startswith("--") and x != (a[a.index("--out") + 1] if "--out" in a else "")]
    if not files:
        print(__doc__)
        sys.exit(2)
    d = json.load(open(files[0]))
    dims = d.get("dimensions", [])
    if not 3 <= len(dims) <= 8:
        sys.exit("need 3 to 8 dimensions, got %d" % len(dims))
    for x in dims:
        if not 0 <= x["score"] <= 10:
            sys.exit("score out of range: %s" % x["name"])
    out = a[a.index("--out") + 1] if "--out" in a else "review.html"
    open(out, "w", encoding="utf-8").write(render(d))
    print("wrote", out)


if __name__ == "__main__":
    main()
