#!/usr/bin/env python3
"""Trigger eval: without a slash command, does Claude pick ux-ui-principles over the other installed skills?

Each prompt runs headless (`claude -p`, this repo loaded as a plugin, the user's other skills as installed),
with write tools disabled and few turns; the first Skill call is recorded. `should` prompts must load
ux-ui-principles; `should_not` prompts must not.

Usage:
  python3 evals/trigger_eval.py [--model sonnet] [--jobs 6] [--repeat 3] [--match "states"] [--out evals/results/trigger.json]
  python3 evals/trigger_eval.py --score evals/results/trigger.json

Progress prints one line per prompt as it finishes; results are saved after each prompt. --repeat N runs each
prompt N times (single runs are noisy: report a per-prompt trigger rate); --match keeps prompts containing the text.

Costs real API usage (small: a few turns per prompt). Standard library only.
"""
import json, os, subprocess, sys, tempfile, threading, time
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
DENY = "Write,Edit,Bash,NotebookEdit,Agent,WebFetch,WebSearch"
NAME = "ux-ui-principles"

SHOULD = [
    "Review the usability of our checkout flow and rank the problems.",
    "ออกแบบหน้าอนุมัติถอนเงินสำหรับทีม finance ให้หน่อย",
    "Which component should I use here: tooltip, popover or dialog, for showing fee details?",
    "ตรวจ UX หน้าสมัครสมาชิกนี้ให้หน่อย ว่าควรแก้อะไรก่อน",
    "Design the information architecture and permission flow for a 3-role payments admin.",
    "How should the empty, loading and error states work on our orders table?",
    "ช่วยจัดกลุ่มเมนูหลังบ้านใหม่ ตอนนี้มี 23 เมนูรก ๆ",
    "Write a page design spec for the refund approval screen with all states.",
    "Our app has no DESIGN.md; extract one from the existing codebase.",
    "Is 44px required for touch targets under WCAG 2.2?",
    "ทำ landing page สำหรับคลินิกความงาม ดูหรู มี animation",
    "Pick a chart for showing weekly refunds by reason and say how to color it.",
]
# A more specific installed skill that is also a correct pick for a `should` prompt; counted as PASS, shown as "alt".
ALT: dict[str, list[str]] = {}

SHOULD_NOT = [
    "Write a Python function that parses ISO 8601 dates with timezones.",
    "Fix this React bug: useEffect runs twice in development.",
    "Create a Helm chart for a Go service with an HPA.",
    "เขียน test case สำหรับ API login ให้หน่อย",
    "Summarize what changed in this release for the team in Thai.",
    "Explain the difference between TCP and UDP.",
]


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def run_one(item, model):
    prompt, want = item
    cwd = tempfile.mkdtemp(prefix="trig-")
    cmd = ["claude", "-p", prompt, "--plugin-dir", REPO, "--model", model, "--output-format", "stream-json",
           "--verbose", "--disallowedTools", DENY, "--max-turns", "3"]
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=600).stdout
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
    skills, cost = [], None
    for line in out.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "assistant":
            for c in o["message"].get("content", []):
                if c.get("type") == "tool_use" and c["name"] == "Skill":
                    skills.append(c["input"].get("skill", ""))
        if o.get("type") == "result":
            cost = o.get("total_cost_usd")
    return {"prompt": prompt, "should": want, "skills": skills, "cost": cost}


def good_pick(r):
    loaded = any(NAME in s for s in r["skills"])
    if r["should"] and not loaded and any(a in s for a in ALT.get(r["prompt"], []) for s in r["skills"]):
        return True
    return loaded == r["should"]


def report(results):
    if len({r["prompt"] for r in results}) < len(results):  # repeated runs: per-prompt rate
        by = {}
        for r in results:
            by.setdefault((r["prompt"], r["should"]), []).append(good_pick(r))
        for (p, sh), v in by.items():
            print(f"{sum(v)}/{len(v)} {'should' if sh else 'not  '} | {p[:70]}")
    ok = 0
    for r in results:
        good = good_pick(r)
        ok += good
        print(f"{'PASS' if good else 'FAIL'} {'should' if r['should'] else 'not  '} -> {r['skills'] or '-'} | {r['prompt'][:70]}")
    print(f"\n{ok}/{len(results)} pass · total ${sum(r['cost'] or 0 for r in results):.2f}")


def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__); return 0
    if "--score" in sys.argv:
        report(json.load(open(arg("--score", "")))); return 0
    items = [(p, True) for p in SHOULD] + [(p, False) for p in SHOULD_NOT]
    if arg("--match"):
        items = [i for i in items if arg("--match").lower() in i[0].lower()]
    items = items * int(arg("--repeat", "1"))
    model, jobs = arg("--model", "sonnet"), int(arg("--jobs", "6"))
    out = arg("--out", os.path.join(HERE, "results", "trigger.json"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    results, lock, t0 = [], threading.Lock(), time.time()
    print(f"running {len(items)} prompts, {jobs} at a time, model {model}", flush=True)
    with ThreadPoolExecutor(jobs) as ex:
        for f in as_completed([ex.submit(run_one, i, model) for i in items]):
            r = f.result()
            with lock:
                results.append(r)
                json.dump(results, open(out, "w"), ensure_ascii=False, indent=1)
            good = good_pick(r)
            print(f"[{len(results)}/{len(items)} {time.time() - t0:.0f}s] {'PASS' if good else 'FAIL'} | {r['prompt'][:60]}", flush=True)
    print()
    report(results)
    print("saved", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
