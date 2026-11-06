#!/usr/bin/env python3
"""Run every regression suite in this folder (test_*.py) and print one summary.

Usage:
  python3 evals/regress/run.py [checkers|design|preview ...]

Each suite runs the skill's scripts on small fixtures and asserts on exit codes and output; it prints one
PASS / FAIL / NOT RUN line per case and exits 1 on any failure. NOT RUN (no browser, no network) is not a
failure. Suites write only to temp folders. Exit 1 when any suite fails. Standard library only.
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    want = sys.argv[1:]
    suites = sorted(f for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py")
                    and (not want or f[5:-3] in want))
    if not suites:
        print("no suites found"); return 2
    failed = []
    for s in suites:
        print(f"== {s}")
        r = subprocess.run([sys.executable, os.path.join(HERE, s)], capture_output=True, text=True)
        out = (r.stdout + r.stderr).rstrip()
        print(out)
        counts = {k: sum(1 for line in out.splitlines() if line.lstrip().startswith(k)) for k in ("PASS", "FAIL", "NOT RUN")}
        print(f"-- {s}: {counts['PASS']} pass, {counts['FAIL']} fail, {counts['NOT RUN']} not run, exit {r.returncode}\n")
        if r.returncode:
            failed.append(s)
    print("ALL PASS" if not failed else "FAILED: " + ", ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
