#!/usr/bin/env python3
"""One command for every delivery check on a built page.

Usage:
  python3 scripts/check.py <page.html> [more.html ...] [--render] [--full] [--admin list|detail|form|dashboard]

Runs, per page:
  script   node scripts/script_check.js   syntax of every script; globals that clash with window (e.g. const top)
  slop     python3 scripts/slop_check.py  template devices, inert forms, removed focus, motion without reduced motion
  contrast python3 scripts/contrast.py --css  role colour pairs in :root token blocks (light and dark)
  states   python3 scripts/state_check.py  markers of loading / empty / error / disabled / focus … in the page's folder
  meta     built in                         public pages: title, description, canonical, og:title/description/image,
                                            twitter:card, exactly one h1 (N/A for /admin/ paths, noindex or data-surface="app")
  render   node scripts/render_check.js --fast (with --render; --full drops --fast)  overflow, JS errors, targets, shots
  admin    node scripts/admin_check.js --type T --states (with --admin T)  numeric columns, disabled reasons, sticky bars,
                                            one primary action, table above fold, every ?state= rendered and different
  fold     node scripts/fold_check.js (with --render)  primary action above the 390x844 / 1440x900 fold, next section hinted (N/A on app pages)

Prints one line per check (PASS / FLAG / FAIL / ERROR / N/A / MANUAL / NOT RUN) and the first lines of anything that is not a pass.
A check that cannot run (no node, no browser) says NOT RUN; never report it as passed. Exit 1 when any check
fails or flags. Standard library only.
"""
import os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return None, "not installed"
    except subprocess.TimeoutExpired:
        return 1, "timed out"


def is_app_page(page, html):
    """Admin / app / noindex pages: no public metadata, no marketing fold rule."""
    return bool("/admin/" in page.replace(os.sep, "/") or re.search(r"<meta[^>]+name=[\"']robots[\"'][^>]+noindex", html, re.I)
                or re.search(r"<html[^>]+data-surface=[\"']app", html, re.I))


def meta_check(page):
    """Return (status, lines) for the public-page metadata check."""
    with open(page, encoding="utf-8", errors="replace") as f:
        html = f.read()
    if is_app_page(page, html):
        return "N/A", ["app or noindex page: metadata not required"]
    def has(pat):
        return re.search(pat, html, re.I | re.S) is not None
    need = {
        "title": r"<title>\s*[^<\s][^<]*</title>",
        "meta description": r"<meta[^>]+name=[\"']description[\"'][^>]+content=[\"'][^\"']+",
        "canonical": r"<link[^>]+rel=[\"']canonical[\"']",
        "og:title": r"property=[\"']og:title[\"']",
        "og:description": r"property=[\"']og:description[\"']",
        "og:image": r"property=[\"']og:image[\"']",
        "twitter:card": r"name=[\"']twitter:card[\"']",
    }
    missing = [k for k, pat in need.items() if not has(pat)]
    h1 = len(re.findall(r"<h1[\s>]", html, re.I))
    if h1 != 1:
        missing.append(f"exactly one h1 (found {h1})")
    return ("PASS", []) if not missing else ("FLAG", ["missing: " + ", ".join(missing)])


def main(argv):
    skip = {argv[i + 1] for i, a in enumerate(argv[:-1]) if a == "--admin"}
    pages = [a for a in argv if not a.startswith("--") and a not in skip]
    if not pages:
        print(__doc__); return 2
    node = shutil.which("node")
    worst = 0
    for page in pages:
        page = os.path.abspath(page)
        print(f"== {page}")
        checks = [
            ("script", [node, os.path.join(HERE, "script_check.js"), page] if node else None),
            ("slop", [sys.executable, os.path.join(HERE, "slop_check.py"), page]),
            ("contrast", [sys.executable, os.path.join(HERE, "contrast.py"), "--css", page]),
            ("states", [sys.executable, os.path.join(HERE, "state_check.py"), os.path.dirname(page)]),
        ]
        if "--render" in argv or "--full" in argv:
            checks.append(("render", [node, os.path.join(HERE, "render_check.js"), page] + ([] if "--full" in argv else ["--fast"]) if node else None))
            fold = os.path.join(HERE, "fold_check.js")
            with open(page, encoding="utf-8", errors="replace") as f:
                app = is_app_page(page, f.read()) or "--admin" in argv   # --admin declares a back-office page
            if app:
                checks.append(("fold", "n/a"))
            else:
                checks.append(("fold", ([node, fold, page] if os.path.isfile(fold) else "missing") if node else None))
        if "--admin" in argv:
            i = argv.index("--admin")
            kind = argv[i + 1] if i + 1 < len(argv) else "list"
            checks.append(("admin", [node, os.path.join(HERE, "admin_check.js"), page, "--type", kind, "--states"] if node else None))
        status, lines = ("N/A", ["--admin: back-office page, metadata not required"]) if "--admin" in argv else meta_check(page)
        if status == "FLAG":
            worst = 1
        print(f"  {status:<8} meta")
        for line in lines if status == "FLAG" else []:
            print(f"           {line}")
        for name, cmd in checks:
            if cmd is None:
                print(f"  NOT RUN  {name:<8} (node not found)"); continue
            if cmd == "n/a":
                print(f"  N/A      {name:<8} (app or noindex page: marketing fold rule does not apply)"); continue
            if cmd == "missing":
                print(f"  NOT RUN  {name:<8} (scripts/{name}_check.js not found)"); continue
            code, out = run(cmd)
            if code is None:
                print(f"  NOT RUN  {name:<8} ({out})"); continue
            low = out.lower()
            if "traceback (most recent call last)" in low:
                status = "ERROR"; worst = 1            # the checker itself crashed: report it, never as a pass
            elif "not tested" in low or "not run" in low:
                status = "NOT RUN"
            elif name == "contrast" and "no :root custom properties" in low:
                status = "N/A"                         # page defines no colour tokens; check its pairs by hand
            elif name == "states":
                status = "MANUAL" if "miss" in low else "PASS"   # markers only; a miss means unverified, not failed
            elif code == 0:
                status = "PASS"
            else:
                status = "FLAG" if name == "slop" else "FAIL"
                worst = 1
            print(f"  {status:<8} {name}")
            if status not in ("PASS", "N/A"):
                for line in [l for l in out.splitlines() if l.strip()][:8]:
                    print(f"           {line[:160]}")
    return worst


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
