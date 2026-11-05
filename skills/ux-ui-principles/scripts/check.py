#!/usr/bin/env python3
"""One command for every delivery check on a built page.

Usage:
  python3 scripts/check.py <page.html> [more.html ...] [--render] [--full]

Runs, per page:
  script   node scripts/script_check.js   syntax of every script; globals that clash with window (e.g. const top)
  slop     python3 scripts/slop_check.py  template devices, inert forms, removed focus, motion without reduced motion
  contrast python3 scripts/contrast.py --css  role colour pairs in :root token blocks (light and dark)
  states   python3 scripts/state_check.py  markers of loading / empty / error / disabled / focus … in the page's folder
  render   node scripts/render_check.js --fast (with --render; --full drops --fast)  overflow, JS errors, targets, shots

Prints one line per check (PASS / FLAG / FAIL / ERROR / N/A / MANUAL / NOT RUN) and the first lines of anything that is not a pass.
A check that cannot run (no node, no browser) says NOT RUN; never report it as passed. Exit 1 when any check
fails or flags. Standard library only.
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def run(cmd):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return None, "not installed"
    except subprocess.TimeoutExpired:
        return 1, "timed out"


def main(argv):
    pages = [a for a in argv if not a.startswith("--")]
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
        for name, cmd in checks:
            if cmd is None:
                print(f"  NOT RUN  {name:<8} (node not found)"); continue
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
