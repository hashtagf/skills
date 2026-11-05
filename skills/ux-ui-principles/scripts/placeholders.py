#!/usr/bin/env python3
"""List every placeholder still on a page, so the owner knows exactly what to supply.

Usage:
  python3 placeholders.py <page.html> [--md README.md] [--json]

Finds text inside elements with class "ph" (or data-placeholder) and any [ ... ] or {{ ... }}
token in visible text; attributes, <script> and <style> are ignored. Prints a table with counts.
With --md, writes or replaces a "## Placeholders" section in the given Markdown file.

Proof must never be a placeholder (marketing-copy.md "Never invent proof"): a placeholder that
looks like reviews, ratings, customer counts or awards is reported on stderr as a warning; leave
that proof out of the page instead. Exit 0. Standard library only.
"""
import json
import os
import re
import sys
from collections import Counter
from html.parser import HTMLParser

TOKEN = re.compile(r"\[[^\[\]\n]{1,80}\]|\{\{[^{}\n]{1,80}\}\}")
PROOF = re.compile(r"review|รีวิว|rating|คะแนน|ลูกค้า\s*\d|\d+\s*customers|customers|award|รางวัล|testimonial|ดาว|stars?\b", re.I)


class Scan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []          # (tag, is_ph)
        self.skip = 0
        self.ph = Counter()
        self.loose = Counter()
        self._buf = None

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "template"):
            self.skip += 1
            return
        a = {k: (v or "") for k, v in attrs}
        is_ph = "ph" in a.get("class", "").split() or "data-placeholder" in a
        if tag in ("br", "img", "input", "meta", "link", "hr", "source", "wbr"):
            return
        self.stack.append((tag, is_ph))
        if is_ph and self._buf is None:
            self._buf = [len(self.stack), []]

    def handle_endtag(self, tag):
        if tag in ("script", "style", "template"):
            self.skip = max(0, self.skip - 1)
            return
        while self.stack:
            t, _ = self.stack.pop()
            if self._buf and len(self.stack) < self._buf[0]:
                text = " ".join("".join(self._buf[1]).split())
                if text:
                    self.ph[text] += 1
                self._buf = None
            if t == tag:
                break

    def handle_data(self, data):
        if self.skip:
            return
        if self._buf is not None:
            self._buf[1].append(data)
        else:
            for m in TOKEN.findall(data):
                self.loose[" ".join(m.split())] += 1


def scan(path):
    s = Scan()
    with open(path, encoding="utf-8", errors="replace") as f:
        s.feed(f.read())
    total = Counter(s.ph)
    total.update(s.loose)
    return total


def md_section(items):
    lines = ["## Placeholders", "", "Replace each one with the real fact, then remove its `ph` wrapper.", "",
             "| Placeholder | Times |", "|---|---|"]
    lines += ["| `%s` | %d |" % (k.replace("|", "\\|"), v) for k, v in items]
    return "\n".join(lines) + "\n"


def write_md(path, section):
    old = open(path, encoding="utf-8").read() if os.path.isfile(path) else ""
    pat = re.compile(r"^## Placeholders\b.*?(?=^## |\Z)", re.S | re.M)
    new = pat.sub(lambda m: section + "\n", old, count=1) if pat.search(old) else (old.rstrip() + "\n\n" + section if old else section)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new)


def main(argv):
    pages = [a for i, a in enumerate(argv) if not a.startswith("--") and (i == 0 or argv[i - 1] != "--md")]
    if not pages:
        print(__doc__)
        return 2
    total = Counter()
    for p in pages:
        total.update(scan(p))
    items = sorted(total.items(), key=lambda kv: (-kv[1], kv[0]))
    for k, _ in items:
        if PROOF.search(k):
            print("warning: placeholder looks like proof (%s); leave proof off the page until it is real" % k, file=sys.stderr)
    if "--json" in argv:
        print(json.dumps(dict(items), ensure_ascii=False, indent=2))
    else:
        print("%d distinct placeholder(s), %d in total" % (len(items), sum(total.values())))
        w = max([len(k) for k, _ in items] + [11])
        for k, v in items:
            print("  %s  %d" % (k.ljust(w), v))
    if "--md" in argv:
        md = argv[argv.index("--md") + 1]
        write_md(md, md_section(items))
        print("wrote section to", md)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
