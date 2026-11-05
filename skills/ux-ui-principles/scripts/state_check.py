#!/usr/bin/env python3
"""Static state-coverage scan: which required UI states have any marker in the source.

Usage: python3 scripts/state_check.py <dir-or-file> [--json] [--need loading,empty,error,...]

Looks for loading, empty, error, disabled, focus, selected, submitting, success,
hover, plus offline/permission when asked. A hit means a marker exists somewhere,
not that the state is reachable or correct; a miss means "unverified, review by
hand". Report results as Manual, never as "covered". Stdlib only.
"""
import json, os, re, sys

STATES = {
    "loading": r"skeleton|spinner|isLoading|loading|aria-busy|pending",
    "empty": r"empty|no[\s_-]?(data|results|items|records)|nothing (here|found)|zero[\s_-]?state",
    "error": r"error|failed|aria-invalid|role=.alert|catch\s*\(|onerror",
    "disabled": r"\bdisabled\b|aria-disabled",
    "focus": r":focus-visible|focus-visible:|:focus\b|focus:|\.focus\(",
    "selected": r"aria-selected|aria-current|aria-pressed|\bselected\b|\bis-active\b|\bactive\b",
    "submitting": r"submitting|isSubmitting|saving|isPending|aria-busy|is-busy|data-state=.submitting|class(Name)?=[\"'][^\"']*\bbusy\b|\.busy\b|\bbusy\s*[:=]",
    "success": r"success|saved|toast|confirmation|done|role=.status[^>]*>[^<]*(done|saved|added|แล้ว)|\bundo\b|เลิกทำ",
    "hover": r":hover|hover:",
    "offline": r"offline|navigator\.onLine|retry",
    "permission": r"forbidden|unauthori[sz]ed|permission|403|read-?only|not allowed",
}
DEFAULT = ["loading", "empty", "error", "disabled", "focus", "selected", "submitting", "success", "hover"]
EXT = (".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte", ".html", ".css", ".astro")
SKIP = {"node_modules", "dist", "build", ".next", "reports", "evals", "__pycache__"}


def files(path):
    if os.path.isfile(path):
        yield path
        return
    for d, dirs, fs in os.walk(path):
        dirs[:] = [x for x in dirs if x not in SKIP and not x.startswith(".")]
        for f in fs:
            if f.endswith(EXT):
                yield os.path.join(d, f)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    need = DEFAULT
    if "--need" in argv:
        need = [x for x in argv[argv.index("--need") + 1].split(",") if x in STATES]
        args = [a for a in args if a != argv[argv.index("--need") + 1]]
    if not args:
        print(__doc__)
        return 2
    hits = {s: [] for s in need}
    n = 0
    for f in files(args[0]):
        n += 1
        try:
            text = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for s in need:
            if re.search(STATES[s], text, re.I):
                hits[s].append(f)
    missing = [s for s in need if not hits[s]]
    rep = {"files": n, "found": {s: len(v) for s, v in hits.items() if v}, "missing": missing,
           "note": "Marker present != state reachable or correct; missing = unverified. Label results Manual."}
    if "--json" in argv:
        print(json.dumps(rep, indent=2))
    else:
        print(f"{n} files scanned")
        for s in need:
            print(f"  {'ok ' if hits[s] else 'MISS'} {s}" + (f" ({len(hits[s])} files)" if hits[s] else ""))
        print(rep["note"])
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
