#!/usr/bin/env python3
"""Static state-coverage scan: which required UI states have any marker in the source.

Usage: python3 scripts/state_check.py <dir-or-file> [more files ...] [--json] [--need loading,empty,error,...] [--per-file] [--matrix]

Several paths are scanned together (check.py passes a page plus the local scripts and
stylesheets it links). Exit 0 when every needed state has a marker, 1 when any is missing.

--matrix: print a surface × state Markdown table (one row per source file), each cell
"Manual (marker)" or "missing", ready to paste into the review report.

--per-file: every file that fetches data must carry its own loading, error and empty
markers; forms need a busy/disabled state (and an unsaved-changes guard when long);
search/filter inputs need a no-match state; polling needs a refetch marker; an error
state needs a retry path. One mention elsewhere in the project does not count.

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


FETCH = r"\bfetch\(|useQuery|useSWR|axios|\$fetch|useFetch|\bload\s*\(|createResource"
RULES = [
    # (applies-when, required, message)
    (FETCH, STATES["loading"], "fetches data but has no loading marker"),
    (FETCH, STATES["error"], "fetches data but has no error marker"),
    (FETCH, STATES["empty"], "fetches data but has no empty marker"),
    (r"<form|onSubmit|on:submit|@submit", r"disabled|isSubmitting|submitting|aria-busy|isPending", "form without a busy/disabled state while submitting"),
    (r"type=[\"']?search|role=[\"']?search|(name|id)=[\"'][\w-]*(search|filter)|class=[\"'][^\"']*\bfilters?\b|[?&]q=", r"no[\s_-]?(match|results)|nothing found|ไม่พบ|(reset|clear) (filters|search)|empty[\s_-]?for", "search/filter without a no-match state"),
    (r"refetchInterval|setInterval\([^)]*fetch|polling", r"isFetching|isRefetching|stale|updated[\s_-]?at|last[\s_-]?updated", "polling/refetch without a refreshing or stale marker"),
    (r"isError|\bfetch\([^;]*\)\s*\.catch\(|\.then\([^;]*\.catch\(|failed to (load|fetch)|โหลด.{0,10}ไม่สำเร็จ", r"retry|try again|refetch|reload|ลองอีกครั้ง", "error state without a retry path"),
]


def per_file(path):
    gaps = []
    for f in files(path):
        if f.endswith(".css"):
            continue
        try:
            text = open(f, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        # fold in local scripts and relative imports: a page's states often live in its module
        base = os.path.dirname(f)
        for ref in re.findall(r"<script[^>]+src=[\"']([^\"':]+)[\"']|from\s+[\"'](\.{1,2}/[^\"']+)[\"']|import\([\"'](\.{1,2}/[^\"']+)[\"']\)", text):
            r = next(x for x in ref if x)
            for cand in (r, r + ".js", r + ".ts", r + ".tsx", r + ".jsx", os.path.join(r, "index.ts")):
                q = os.path.normpath(os.path.join(base, cand))
                if os.path.isfile(q):
                    text += "\n" + open(q, encoding="utf-8", errors="replace").read()
                    break
        for when, need, msg in RULES:
            if re.search(when, text, re.I) and not re.search(need, text, re.I):
                gaps.append({"file": f, "gap": msg})
        if len(re.findall(r"<textarea\b|<input\b(?![^>]*type=[\"']?(search|checkbox|radio|hidden|submit|button))", text, re.I)) >= 6 and not re.search(r"isDirty|beforeunload|unsaved", text, re.I):
            gaps.append({"file": f, "gap": "long form without an unsaved-changes guard"})
    return gaps


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    need = DEFAULT
    if "--need" in argv:
        need = [x for x in argv[argv.index("--need") + 1].split(",") if x in STATES]
        args = [a for a in args if a != argv[argv.index("--need") + 1]]
    if not args:
        print(__doc__)
        return 2
    if "--matrix" in argv:
        print("| Surface | " + " | ".join(need) + " |")
        print("|---|" + "---|" * len(need))
        for f in files(args[0]):
            if f.endswith(".css"):
                continue
            try:
                text = open(f, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            cells = ["Manual (marker)" if re.search(STATES[s], text, re.I) else "missing" for s in need]
            print(f"| {os.path.relpath(f, args[0]) if os.path.isdir(args[0]) else os.path.basename(f)} | " + " | ".join(cells) + " |")
        print("\nMarker present != state verified: render each cell before marking it Ran.")
        return 0
    if "--per-file" in argv:
        gaps = per_file(args[0])
        if "--json" in argv:
            print(json.dumps({"gaps": gaps, "note": "Static markers only; label results Manual."}, indent=2, ensure_ascii=False))
        else:
            for g in gaps:
                print(f"  GAP {g['file']}: {g['gap']}")
            print(f"{len(gaps)} gap(s). Static markers only; label results Manual.")
        return 1 if gaps else 0
    hits = {s: [] for s in need}
    n = 0
    scanned = set()
    for f in (f for a in args for f in files(a)):
        if os.path.abspath(f) in scanned:
            continue
        scanned.add(os.path.abspath(f))
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
