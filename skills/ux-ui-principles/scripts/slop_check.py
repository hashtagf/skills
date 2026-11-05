#!/usr/bin/env python3
"""Flag template-look ("AI slop") patterns in an HTML page and its local CSS.

Usage:
  python3 slop_check.py page.html [more.html ...] [--json]

Reads inline <style>, style="" attributes and local <link rel=stylesheet> files.
Each rule is a deterministic heuristic. A hit means "look at this in the render",
not "this is wrong": a device is fine when the brief asks for it or you can
defend it in one sentence (references/design-quality.md §2).

Levels: flag (likely default/defect) and note (worth a look).
Exit code 1 if any flag is found, 2 on usage error.
Standard library only.
"""
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

HEADINGS = {"h1", "h2", "h3"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}
FILLER = ["supercharge", "unlock", "all-in-one", "seamless", "revolutioniz",
          "next-generation", "next-gen", "empower", "elevate your", "game-chang",
          "cutting-edge", "unleash", "effortless", "transform your", "lorem ipsum",
          "your workflow", "the future of"]
WEAK_CTA = {"submit", "click here", "learn more", "get started", "read more", "ok"}


class Node:
    __slots__ = ("tag", "attrs", "children", "text", "parent")

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent = tag, attrs, parent
        self.children, self.text = [], []

    def cls(self):
        return set((self.attrs.get("class") or "").split())

    def all_text(self):
        out = list(self.text)
        for c in self.children:
            out.append(c.all_text())
        return " ".join(t for t in out if t).strip()

    def walk(self):
        yield self
        for c in self.children:
            yield from c.walk()


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.cur: Node = self.root
        self.styles, self.links, self.scripts = [], [], []
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = {k: (v or "") for k, v in attrs}
        n = Node(tag, a, self.cur)
        self.cur.children.append(n)
        if tag == "link" and "stylesheet" in a.get("rel", ""):
            self.links.append(a.get("href", ""))
        if a.get("style"):
            self.styles.append("x{" + a["style"] + "}")
        if tag in ("style", "script"):
            self._in = tag
        if tag not in VOID:
            self.cur = n

    def handle_endtag(self, tag):
        self._in = None
        n = self.cur
        while n is not self.root and n.tag != tag:
            n = n.parent or self.root
        if n is not self.root:
            self.cur = n.parent or self.root

    def handle_data(self, data):
        if self._in == "style":
            self.styles.append(data)
        elif self._in == "script":
            self.scripts.append(data)
        elif data.strip():
            self.cur.text.append(data.strip())


def css_rules(css):
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    for m in re.finditer(r"([^{}]+)\{([^{}]*)\}", css):
        yield m.group(1).strip(), m.group(2)


def check(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        html = f.read()
    t = Tree()
    t.feed(html)
    css = "\n".join(t.styles)
    base = os.path.dirname(os.path.abspath(path))
    for href in t.links:
        p = os.path.join(base, href.split("?")[0])
        if href and not re.match(r"^[a-z]+:", href) and os.path.isfile(p):
            with open(p, encoding="utf-8", errors="replace") as f:
                css += "\n" + f.read()
    js = "\n".join(t.scripts)
    rules = list(css_rules(css))
    nodes = list(t.root.walk())
    out = []

    def add(level, rule, msg, examples=()):
        out.append({"level": level, "rule": rule, "message": msg,
                    "examples": [e[:80] for e in list(examples)[:3]]})

    # Classes that render uppercase small labels
    upper = set()
    for sel, body in rules:
        if re.search(r"text-transform\s*:\s*uppercase", body):
            upper |= set(re.findall(r"\.([\w-]+)", sel))
    eyebrow = re.compile(r"eyebrow|kicker|overline|pretitle|tagline|label")
    hits = []
    for n in nodes:
        sibs = n.children
        for i, c in enumerate(sibs):
            if c.tag in HEADINGS and i > 0:
                prev = sibs[i - 1]
                if prev.cls() & upper or any(eyebrow.search(k) for k in prev.cls()):
                    hits.append(prev.all_text())
    if len(hits) >= 2:
        add("flag", "eyebrow-labels", f"{len(hits)} small/uppercase labels above headings; put the information in the heading", hits)

    # Language variants (<span lang="th">…</span><span lang="en">…</span>) are one headline in
    # two languages, not a styled word; nested non-lang spans inside a variant still count.
    def styled_child(h):
        kids = [c for c in h.children if not (c.tag == "span" and "lang" in c.attrs)]
        kids += [g for c in h.children if c.tag == "span" and "lang" in c.attrs for g in c.children]
        return any(c.tag in ("span", "em", "i", "mark", "strong", "b") and "lang" not in c.attrs
                   and "nb" not in c.cls() for c in kids)
    accent = [n.all_text() for n in nodes if n.tag in ("h1", "h2") and styled_child(n)]
    if accent:
        # Roman + italic emphasis (em/i, at most one headline per page) is a recipe device, not slop: note, not flag.
        def italic_only(n):
            return all(c.tag in ("em", "i") for c in n.children if c.tag in ("span", "em", "i", "mark", "strong", "b") and "lang" not in c.attrs)
        hs = [n for n in nodes if n.tag in ("h1", "h2") and styled_child(n)]
        if len(hs) <= 1 and all(italic_only(n) for n in hs):
            add("note", "italic-emphasis", "one headline uses italic emphasis (allowed by the recipes once per page; waive in the context card)", accent)
        else:
            add("flag", "accent-word-headline", f"{len(accent)} headline(s) style one word differently", accent)

    if re.search(r"(-webkit-)?background-clip\s*:\s*text", css):
        add("flag", "gradient-text", "gradient-filled text")

    idx = [n.all_text() for n in nodes if re.fullmatch(r"0[1-9]\.?", n.all_text() or "")]
    if len(idx) >= 3:
        add("note", "index-numbering", f"{len(idx)} '01/02/03' markers; keep only for real sequences", idx)

    # Rows of identical cards (3-12 siblings, same tag+class, each with a heading and an icon)
    rows = []
    for n in nodes:
        if n.tag in ("table", "tbody", "thead", "tr", "select"):
            continue
        sig = Counter((c.tag, c.attrs.get("class", "")) for c in n.children
                      if c.tag in ("div", "li", "article", "a"))
        for (tag, k), cnt in sig.items():
            if not 3 <= cnt <= 12:
                continue
            group = [c for c in n.children if c.tag == tag and c.attrs.get("class", "") == k]
            iconed = sum(1 for g in group
                         if any(d.tag in HEADINGS | {"h4"} for d in g.walk())
                         and any(d.tag in ("svg", "i", "img") for d in g.walk()))
            if iconed >= 3:
                rows.append(f"{tag}.{k or '-'} x{iconed}: " + " / ".join(g.all_text()[:20] for g in group[:3]))
    if rows:
        add("flag", "icon-card-row", f"{len(rows)} row(s) of identical icon+heading cards; vary the composition", rows)

    radii = [m for m in re.findall(r"border-radius\s*:\s*([^;}]+)", css) if not re.fullmatch(r"\s*0(px)?\s*", m)]
    rounded = [m for m in radii if not re.fullmatch(r"\s*(50%|999\w*|9999\w*)\s*", m)]
    if len(css) > 800 and not rounded:
        add("note", "all-square", "no rounded corners anywhere; fine for a print or brutalist direction, otherwise mix shapes (SKILL.md, user away rule)")
    if re.search(r"\.js\s+[^{]*\{[^}]*opacity\s*:\s*0", css) and "prefers-reduced-motion" not in css:
        add("flag", "reveal-hides-content", "content is hidden until scripted reveal and no reduced-motion fallback; plain screenshots and print show blanks (motion.md)")

    tw_arb = re.findall(r"\b(?:bg|text|border|ring|fill|stroke|from|to|via|outline|shadow)-\[(?:#|rgb|hsl|oklch)[^\]]*\]", html)
    if tw_arb:
        add("note", "tailwind-arbitrary-color", f"{len(tw_arb)} Tailwind arbitrary color classes; use theme tokens (tailwind.md)", sorted(set(tw_arb))[:5])
    grads = len(re.findall(r"(linear|radial|conic)-gradient\(", css))
    if grads > 3:
        add("note", "decorative-gradients", f"{grads} gradients; keep them for one deliberate use")
    blur = len(re.findall(r"backdrop-filter\s*:", css))
    if blur > 2:
        add("note", "glass-overuse", f"backdrop-filter used {blur} times; glass is an accent, check text contrast over it")
    glows = [b for _, b in rules for m in re.finditer(r"box-shadow\s*:\s*([^;]+)", b)
             if re.search(r"\b0(px)?\s+0(px)?\s+([2-9]\d|\d{3,})px", m.group(1))]
    if glows:
        add("note", "glow-shadows", f"{len(glows)} glow shadows (0 0 ≥20px)")

    fams = Counter()
    for sel, b in rules:
        if re.search(r":lang\(|\[lang|\.lang-|\[data-lang", sel or ""):
            continue  # per-language families (Thai pair) are counted by the base rule, not again
        for m in re.finditer(r"font-family\s*:\s*([^;]+)", b):
            first = m.group(1).split(",")[0].strip().strip("'\"").lower()
            if not first.startswith("var(") and "mono" not in first and first not in ("inherit", "sans-serif", "serif", "system-ui"):
                fams[first] += 1
    if len(fams) > 2:
        add("flag", "too-many-typefaces", f"{len(fams)} typefaces; one, two at most (mono not counted)", fams.keys())
    mono_sel = [s for s, b in rules if re.search(r"font-family\s*:[^;]*mono", b, re.I)
                and not re.search(r"\b(code|pre|kbd|samp)\b", s)]
    if mono_sel:
        add("note", "mono-outside-code", "monospace set on non-code selectors", mono_sel)

    radii = Counter(m.group(1).strip() for _, b in rules
                    for m in re.finditer(r"border-radius\s*:\s*([^;]+)", b)
                    if "var(" not in m.group(1))
    if len(radii) > 4:
        add("flag", "inconsistent-radii", f"{len(radii)} distinct raw border-radius values; use radius tokens", radii.keys())

    raw_hex = sum(len(re.findall(r"#[0-9a-fA-F]{3,8}\b", re.sub(r"--[\w-]+\s*:[^;]+;?", "", b))) for _, b in rules)
    if raw_hex > 12:
        add("note", "hardcoded-colors", f"{raw_hex} raw hex colors outside custom properties; reference tokens")

    # Palette: saturated hues in UI chrome, pure black
    import colorsys
    hues = set()
    for h in re.findall(r"#([0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b", css):
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
        hh, ll, ss = colorsys.rgb_to_hls(r, g, b)
        if ss > 0.45 and 0.25 < ll < 0.8:
            hues.add(int(hh * 360) // 30)
    if len(hues) > 2:
        add("note", "many-saturated-hues", f"{len(hues)} saturated hue families in CSS; UI chrome usually needs ≤ 2 (color-palette.md)")
    if re.search(r"(background(-color)?|color)\s*:\s*(#000\b|#000000\b|black\b|rgb\(\s*0\s*,\s*0\s*,\s*0\s*\))", css):
        add("note", "pure-black", "pure black used for text or ground; use a tinted ink / near-black")
    sections = len([n for n in nodes if n.tag == "section"])
    if sections >= 3 and not re.search(r"(@keyframes|animation\s*:|transition\s*:|animate\(|IntersectionObserver)", css + js):
        add("note", "no-motion", f"{sections} sections and no transition/animation at all; public pages need the motion baseline (motion.md §1)")

    if re.search(r"outline\s*:\s*(none|0)\b", css) and ":focus-visible" not in css:
        add("flag", "focus-removed", "outline removed with no :focus-visible replacement")
    if re.search(r"(@keyframes|animation\s*:|transition\s*:)", css) and "prefers-reduced-motion" not in css:
        add("flag", "no-reduced-motion", "motion without a prefers-reduced-motion path")

    text = t.root.all_text()
    low = text.lower()
    filler = [w for w in FILLER if w in low]
    if filler:
        add("flag", "filler-copy", "generic marketing phrases; say what this product does", filler)
    btns = [n.all_text() for n in nodes if n.tag in ("button", "a") and n.all_text().lower().strip(" →›>") in WEAK_CTA]
    if len(btns) >= 2:
        add("note", "weak-cta-labels", f"{len(btns)} generic action labels; name the outcome", btns)
    dots = len(re.findall(r"\S\s+·\s+\S", text))
    arrows = len(re.findall(r"→", text))
    if dots >= 3:
        add("note", "middot-meta", f"{dots} 'A · B · C' strings")
    if arrows >= 3:
        add("note", "arrow-links", f"{arrows} '→' appended to text")

    VAL_JS = re.compile(r"setCustomValidity|\.validity|checkValidity|reportValidity|aria-invalid|zod|yup|"
                        r"resolver|useForm|Formik|vee-validate|validate\(|errors\[")
    FORMAT = re.compile(r"phone|tel|mobile|email|zip|post|id[-_]?card|national|citizen|tax|date|amount|price|url|เบอร์|อีเมล")
    for n in nodes:
        if n.tag != "form":
            continue
        fields = [d for d in n.walk() if d.tag in ("input", "select", "textarea")
                  and d.attrs.get("type") not in ("submit", "button", "hidden", "reset")]
        if not fields:
            continue
        has_handler = n.attrs.get("action") or n.attrs.get("method") == "dialog" or n.attrs.get("onsubmit") or re.search(r"submit|addEventListener|onSubmit|FormData", js)
        if not has_handler:
            add("flag", "inert-form", "form with no action and no submit handling; specify submit, validation, error and success behavior")
        rules = any(any(k in d.attrs for k in ("required", "pattern", "min", "max", "minlength", "maxlength"))
                    or d.attrs.get("type") in ("email", "url", "number", "tel", "date") for d in fields)
        messages = re.search(r"aria-invalid|field-error|error-message|role=\"alert\"", html) or VAL_JS.search(js)
        if not rules and not messages:
            add("flag", "form-without-validation", f"form with {len(fields)} field(s) but no rules (required/type/pattern) and no error messages; see forms.md §6b")
        elif not messages:
            add("flag", "form-without-messages", "fields have rules but no own error messages / aria-invalid / error summary; browser bubbles only (forms.md §6b)")
        unnamed = [d.attrs.get("type", d.tag) for d in fields if not d.attrs.get("name")]
        if unnamed:
            add("note", "unnamed-fields", f"{len(unnamed)} form fields without name", unnamed)
        nohint = [d.attrs.get("name") or d.attrs.get("id") or d.attrs.get("type", d.tag) for d in fields
                  if d.tag in ("input", "textarea")
                  and (d.attrs.get("type") in ("tel", "email", "url") or FORMAT.search((d.attrs.get("name", "") + " " + d.attrs.get("id", "")).lower()))
                  and not d.attrs.get("placeholder") and not d.attrs.get("aria-describedby")]
        if nohint:
            add("note", "format-field-without-example", f"{len(nohint)} format field(s) with neither an example placeholder nor a hint (forms.md §3)", nohint)
    # App navigation items without icons (iconography.md: navigation = icon + label). Applies to product UI:
    # a sidebar / aside, or a nav of 7+ items. A public page's short text menu (3-6 links) is a convention, not slop.
    navs = [n for n in nodes if n.tag in ("aside", "nav") or any(k in ("sidebar", "side", "nav-list", "menu") for k in n.cls())]
    for nv in navs[:1]:
        links = [a for a in nv.walk() if a.tag == "a"]
        app_nav = nv.tag == "aside" or any(k in ("sidebar", "side") for k in nv.cls()) or len(links) >= 7
        if app_nav and len(links) >= 4:
            with_icon = [a for a in links if any(d.tag in ("svg", "img", "i", "use") or any("icon" in k or k in ("ic", "fa") for k in d.cls())
                                                 for d in a.walk() if d is not a)]
            if len(with_icon) < len(links) / 2:
                add("flag", "nav-without-icons", f"{len(links) - len(with_icon)} of {len(links)} navigation items have no icon; use icon + label from one family (iconography.md)",
                    [a.all_text() for a in links if a not in with_icon])
    if re.search(r"[\u25B2\u25BC\u2191\u2193]", html + js):
        add("note", "glyph-as-icon", "text arrows (up/down triangles) used as trend icons; use an icon from the set plus visually hidden text (iconography.md)")
    # Product-UI doctrine (app-screen-rules.md §7): viewport-scaled type, cards nested in cards, hero in an app shell.
    vw = [sel for sel, body in rules
          for m in re.findall(r"font-size\s*:\s*([^;}]+)", body)
          if re.search(r"\d\s*vw\b", m) and not re.search(r"clamp\(|min\(|max\(", m)]
    if vw:
        add("flag", "viewport-scaled-font", f"{len(vw)} rule(s) size type in raw vw units (no clamp); text jumps with window width (app-screen-rules.md §7)", vw)
    cardish = lambda n: any(re.search(r"(^|-)(card|panel|tile)($|-)", k) for k in n.cls()) and not any(k.endswith(("-title", "-body", "-header", "-footer", "-label", "-value")) for k in n.cls())
    nested = [c.cls() for n in nodes if cardish(n) for c in n.walk() if c is not n and cardish(c)]
    if nested:
        add("flag", "nested-cards", f"{len(nested)} card/panel inside another card/panel; one framed level, use spacing or dividers inside (app-screen-rules.md §7)", [" ".join(sorted(x)) for x in nested])
    shell = any(n.tag == "aside" or "sidebar" in n.cls() for n in nodes)
    hero = [n.cls() for n in nodes if any(k in ("hero", "jumbotron", "banner-hero") for k in n.cls())]
    if shell and hero:
        add("flag", "hero-in-app", "decorative hero inside an app shell (sidebar present); an operational screen opens on its task (app-screen-rules.md §7)", [" ".join(sorted(x)) for x in hero])
    return out


def main(argv):
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print(__doc__)
        return 2
    as_json = "--json" in argv
    report, flags = {}, 0
    for p in files:
        res = check(p)
        report[p] = res
        flags += sum(1 for r in res if r["level"] == "flag")
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for p, res in report.items():
            print(f"== {p}: {sum(r['level']=='flag' for r in res)} flag, {sum(r['level']=='note' for r in res)} note")
            for r in res:
                ex = f"  e.g. {r['examples']}" if r["examples"] else ""
                print(f"  [{r['level']}] {r['rule']}: {r['message']}{ex}")
        print("Heuristics only: confirm each hit in the rendered page.")
    return 1 if flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
