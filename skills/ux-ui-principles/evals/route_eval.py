#!/usr/bin/env python3
"""Routing eval: does the skill open the right reference files for each eval prompt?

Runs each prompt in evals.json headless (`claude -p`) with this repo loaded as a plugin and write tools
disabled, records every Read/Grep/Glob under the skill directory, and scores it against the eval's
`expected_reads` (list of any-of groups; `fixture` copies files into the run directory; a group passes when one of its names was opened) and
`must_not_read`. Also reports how many bytes of skill files were loaded (context cost).

Usage:
  python3 evals/route_eval.py [--ids 1,4,9] [--model sonnet] [--jobs 6] [--max-turns 12] [--out evals/results/routing.json]
  python3 evals/route_eval.py --score evals/results/routing.json      # re-score saved transcripts

Progress prints one line per prompt as it finishes; results are saved after each prompt (a killed run
keeps what finished: re-run only the missing ones with --ids). --max-turns defaults to 12: routing is scored on
files opened, which happens in the first turns; raise it (v3 used 30) when comparing against older results.

Costs real API usage (about $0.2-0.5 per prompt with sonnet). Standard library only.
"""
import json, os, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SKILL))
DENY = "Write,Edit,Bash,NotebookEdit,Agent,WebFetch,WebSearch,Skill"


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def run_one(ev, model, turns=12):
    cwd = tempfile.mkdtemp(prefix="route-")
    if ev.get("fixture"):  # an existing page the prompt refers to, copied into the run directory
        import shutil
        shutil.copytree(os.path.join(SKILL, ev["fixture"]), cwd, dirs_exist_ok=True)
    prompt = "/hashtagf-skills:ux-ui-principles " + ev["prompt"]
    cmd = ["claude", "-p", prompt, "--plugin-dir", REPO, "--model", model, "--output-format", "stream-json",
           "--verbose", "--disallowedTools", DENY, "--max-turns", str(turns)]
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=900).stdout
    except subprocess.TimeoutExpired as e:  # keep what streamed before the timeout instead of crashing the run
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
    opened, cost, text = [], None, ""
    for line in out.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "assistant":
            for c in o["message"].get("content", []):
                if c.get("type") == "tool_use":
                    path = c["input"].get("file_path") or c["input"].get("path") or ""
                    if SKILL in path:
                        opened.append(os.path.relpath(path, SKILL))
        if o.get("type") == "result":
            cost, text = o.get("total_cost_usd"), (o.get("result") or "")[:400]
    return {"id": ev["id"], "opened": opened, "cost": cost, "answer_head": text}


def score(ev, r):
    stems = [o.replace(".md", "") for o in r["opened"]]
    hit = lambda name: any(s.endswith(name) for s in stems)
    groups = ev.get("expected_reads", [])
    passed = [g for g in groups if any(hit(n) for n in g)]
    bad = [n for n in ev.get("must_not_read", []) if hit(n)]
    size = sum(os.path.getsize(os.path.join(SKILL, o)) for o in set(r["opened"]) if os.path.isfile(os.path.join(SKILL, o)))
    return {"recall": f"{len(passed)}/{len(groups)}", "ok": len(passed) == len(groups) and not bad,
            "missed": [g for g in groups if g not in passed], "wrong": bad, "kb": round(size / 1024, 1)}


def report(evs, results):
    byid = {e["id"]: e for e in evs}
    oks = 0
    for r in sorted(results, key=lambda r: r["id"]):
        s = score(byid[r["id"]], r)
        r["score"] = s
        oks += s["ok"]
        print(f"#{r['id']:>2} {'PASS' if s['ok'] else 'FAIL'} recall {s['recall']} wrong {s['wrong'] or '-'} "
              f"missed {s['missed'] or '-'} | {len(set(r['opened']))} files {s['kb']}KB | ${r['cost'] or 0:.2f}")
    total = sum(r["cost"] or 0 for r in results)
    print(f"\n{oks}/{len(results)} pass · total ${total:.2f}")


def main():
    evs = json.load(open(os.path.join(HERE, "evals.json")))["evals"]
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__); return 0
    if "--score" in sys.argv:
        report(evs, json.load(open(arg("--score", "")))); return 0
    ids = arg("--ids")
    if ids:
        want = {int(i) for i in ids.split(",")}
        evs_run = [e for e in evs if e["id"] in want]
    else:
        evs_run = evs
    model, jobs, turns = arg("--model", "sonnet"), int(arg("--jobs", "6")), int(arg("--max-turns", "12"))
    out = arg("--out", os.path.join(HERE, "results", "routing.json"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    results, lock, t0 = [], threading.Lock(), time.time()
    print(f"running {len(evs_run)} prompts, {jobs} at a time, max {turns} turns, model {model}", flush=True)
    with ThreadPoolExecutor(jobs) as ex:
        futs = {ex.submit(run_one, e, model, turns): e for e in evs_run}
        for f in as_completed(futs):
            r = f.result()
            with lock:
                results.append(r)
                json.dump(sorted(results, key=lambda x: x["id"]), open(out, "w"), ensure_ascii=False, indent=1)
            s = score(futs[f], r)
            print(f"[{len(results)}/{len(evs_run)} {time.time() - t0:.0f}s] #{r['id']} {'PASS' if s['ok'] else 'FAIL'} "
                  f"recall {s['recall']} | {len(set(r['opened']))} files | ${r['cost'] or 0:.2f}", flush=True)
    print()
    report(evs, results)
    print("saved", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
