"""The skill's template library: every picture collection read into one row shape. Standard library only.

  load(root=None) -> [row]   one row per picture, in collection order (COLLECTIONS)
  tags(rows)      -> sorted tags in use

Row (the same for every collection; README "Template library" in assets/LIBRARY.md):
  id        unique name (collection-local slug, plus -<n> for the n-th screen of an app)
  kind      page kind: landing, product, auth, cafe, deck, report, cover, editorial, ...
  tags      finer words to search by (crm, finance, ai-chat, canvas ...); may be empty
  verdict   template (start from its move) | study (one detail worth learning)
  take      what to take from it, in our words
  comp      composition id in scripts/compositions.js, or ""
  img/full  absolute picture paths (full may be "")
  origin    ours (built with this skill) | generated (rendered template or showcase page) | product (a real app's screen)
  local     True when the picture is git-ignored and rebuilt by a fetch script (other people's work: study only)
  source    short provenance line with the link, for the answer's credit; never a reason to pick one row over another

Skipped entries are not rows. A collection whose catalog is missing yields nothing (its pictures are optional).
Collections and how to rebuild them: COLLECTIONS below and assets/LIBRARY.md.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# name -> (folder under assets/, local?, rebuild command)
COLLECTIONS = {
    "references": ("references", False, "committed"),
    "showcase": ("showcase", True, "python3 scripts/showcase_fetch.py"),
    "mobbin": ("mobbin", True, "python3 scripts/mobbin_fetch.py"),
}


def _references(root):
    d = os.path.join(root, "assets", "references")
    readme = os.path.join(d, "README.md")
    if not os.path.exists(readme):
        return []
    rows = []
    for line in open(readme, encoding="utf-8"):
        m = re.match(r"\|\s*`([^`]+)`\s*\|\s*([^|]+?)\s*\|\s*(c\d+)\s*\|\s*(.+?)\s*\|\s*$", line)
        if not m:
            continue
        name, kind, comp, why = m.groups()
        ours = "own build" in why.lower()
        rows.append({"id": name, "kind": kind, "tags": [], "verdict": "template", "take": why, "comp": comp,
                     "img": os.path.join(d, name + ".jpg"), "full": os.path.join(d, name + "-full.jpg"),
                     "origin": "ours" if ours else "generated", "local": False,
                     "source": "assets/references (%s)" % ("our build" if ours else "Apache-2.0, see NOTICE")})
    return rows


def _showcase(root):
    d = os.path.join(root, "assets", "showcase")
    p = os.path.join(d, "catalog.json")
    if not os.path.exists(p):
        return []
    rows = []
    for r in json.load(open(p, encoding="utf-8")):
        if r.get("verdict") not in ("template", "study") or not r.get("img"):
            continue
        rows.append({"id": r["slug"], "kind": r["kind"], "tags": [], "verdict": r["verdict"], "take": r["note"],
                     "comp": r.get("comp") or "", "img": os.path.join(d, r["img"]),
                     "full": os.path.join(d, r["img_full"]) if r.get("img_full") else "",
                     "origin": "generated", "local": True, "source": r["url"]})
    return rows


def _mobbin(root):
    d = os.path.join(root, "assets", "mobbin")
    p = os.path.join(d, "catalog.json")
    if not os.path.exists(p):
        return []
    rows = []
    for a in json.load(open(p, encoding="utf-8"))["apps"]:
        if a["verdict"] == "skip":
            continue
        for i, sc in enumerate(a["screens"], 1):
            rows.append({"id": "%s-%d" % (a["slug"], i), "app": a["name"], "kind": sc["kind"], "tags": a["tags"],
                         "verdict": a["verdict"], "take": a["note"], "comp": "", "img": os.path.join(d, sc["img"]),
                         "full": "", "origin": "product", "local": True,
                         "source": "%s, screen %d: %s" % (a["name"], i, a["url"])})
    return rows


_LOADERS = {"references": _references, "showcase": _showcase, "mobbin": _mobbin}


def load(root=None):
    root = root or ROOT
    rows = []
    for name in COLLECTIONS:
        for r in _LOADERS[name](root):
            r.setdefault("app", r["id"])
            r["collection"] = name
            rows.append(r)
    return rows


def tags(rows):
    return sorted({t for r in rows for t in r["tags"]})
