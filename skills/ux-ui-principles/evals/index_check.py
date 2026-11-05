#!/usr/bin/env python3
"""Keep the skill untangled: every file has a reason, every reference resolves.

What: fails when
  1. a file in references/ or scripts/ has no row in README.md "ดัชนีไฟล์" (no stated reason to exist);
  2. a row in that index names a file that no longer exists;
  3. a relative markdown link in SKILL.md, README.md, references/ or assets/ points nowhere;
Why: merges and renames silently break routing; the skill is used on its own, so every path must resolve inside it.
How: python3 evals/index_check.py   (from the skill root; standard library only; exit 1 on any problem)
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []

readme = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
index = readme.split("## ดัชนีไฟล์", 1)[1] if "## ดัชนีไฟล์" in readme else ""
if not index:
    problems.append("README.md has no '## ดัชนีไฟล์' section")
rows = set(re.findall(r"^\| `([^`]+)` \|", index, re.M))

for folder in ("references", "scripts"):
    for name in sorted(os.listdir(os.path.join(ROOT, folder))):
        full = os.path.join(ROOT, folder, name)
        if name.startswith((".", "__")) or os.path.isdir(full):
            continue
        if name not in rows:
            problems.append(f"no index row: {folder}/{name}")
for row in sorted(rows):
    cands = [c for part in row.split(", ") for c in ([os.path.join(ROOT, part)] if "/" in part else [os.path.join(ROOT, "references", part), os.path.join(ROOT, "scripts", part)])]
    if not any(os.path.exists(c.rstrip("/")) for c in cands):
        problems.append(f"index row without a file: {row}")

LINK = re.compile(r"\]\(([^)\s]+)\)")
def md_files():
    yield os.path.join(ROOT, "SKILL.md")
    yield os.path.join(ROOT, "README.md")
    for sub in ("references", "assets"):
        for d, dirs, files in os.walk(os.path.join(ROOT, sub)):
            dirs[:] = [x for x in dirs if x not in ("design-systems", "previews", "img")]
            for f in files:
                if f.endswith(".md"):
                    yield os.path.join(d, f)
for path in md_files():
    text = open(path, encoding="utf-8").read()
    for target in LINK.findall(text):
        if re.match(r"^[a-z]+:", target) or target.startswith("#"):
            continue
        dest = os.path.normpath(os.path.join(os.path.dirname(path), target.split("#")[0]))
        if not os.path.exists(dest):
            problems.append(f"broken link: {os.path.relpath(path, ROOT)} -> {target}")

for p in problems:
    print("FAIL  " + p)
print(f"{len(problems)} problem(s); {len(rows)} index rows" if problems else f"PASS  {len(rows)} index rows, every file explained, every link resolves")
sys.exit(1 if problems else 0)
