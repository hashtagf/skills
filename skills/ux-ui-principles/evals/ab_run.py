#!/usr/bin/env python3
"""A/B build eval: the same task done with the skill and with no skills, so the outputs can be compared.

Each task runs twice headless (`claude -p`) in its own directory (a copy of the fixture for brownfield tasks):
  with    -> this repo loaded as a plugin, prompt prefixed with the skill's slash command
  without -> no plugin, the Skill tool disabled (no skill at all)
Write/Edit/Read and node/python3 shell commands are allowed (as in real use); web tools are not. Each run's final answer is saved as ANSWER.md and its
cost in run.json.

Usage:
  python3 evals/ab_run.py OUT_DIR [--ids A,B] [--model sonnet] [--jobs 8] [--max-turns 40]
Costs real API usage (roughly $0.5-2 per run). Standard library only.
"""
import json, os, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.dirname(HERE)
REPO = os.path.dirname(os.path.dirname(SKILL))
AWAY = " I'm away today: don't ask me questions, make sensible assumptions, list them at the end, and build it."

TASKS = [
    {"id": "A", "field": "greenfield", "title": "Café landing page",
     "prompt": "ทำเว็บ landing page ให้ร้านกาแฟ specialty ชื่อ Roastery Lane ย่านอารีย์ เป็นไฟล์ index.html ไฟล์เดียว (CSS/JS inline)." + AWAY,
     "open": "index.html"},
    {"id": "B", "field": "greenfield", "title": "Refund approval (back office)",
     "prompt": "Design and build the refund approval screen for our finance team as a single index.html (inline CSS/JS, sample data). Refunds go up to 500,000 THB; finance approves or rejects." + AWAY,
     "open": "index.html"},
    {"id": "C", "field": "brownfield", "title": "Checkout trust fix",
     "prompt": "Improve trust and usability on this checkout (checkout.html). The subscription box is pre-checked and fees show after payment. Edit the files in place." + AWAY,
     "fixture": "evals/fixtures/checkout", "open": "checkout.html"},
    {"id": "D", "field": "brownfield", "title": "Dashboard chart fix",
     "prompt": "Fix the charts and KPI tiles on this dashboard (dashboard.html, charts.js): the pie has nine slices and the line axis starts at 90. Edit the files in place." + AWAY,
     "fixture": "evals/fixtures/dashboard", "open": "dashboard.html"},
]


def arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def run(task, arm, out, model, turns):
    # Work outside the repo: Claude Code refuses writes inside a loaded plugin's directory ("sensitive file"),
    # which would block only the with-skill arm. Results are copied back to OUT_DIR afterwards.
    final = os.path.join(out, task["id"], arm)
    d = os.path.join(tempfile.mkdtemp(prefix=f"ab-{task['id']}-{arm}-"), "work")
    if task.get("fixture"):
        shutil.copytree(os.path.join(SKILL, task["fixture"]), d)
    else:
        os.makedirs(d)
    if arm == "with":
        cmd = ["claude", "-p", "/hashtagf-skills:ux-ui-principles " + task["prompt"], "--plugin-dir", REPO,
               "--disallowedTools", "WebFetch,WebSearch,Agent,NotebookEdit"]
    else:
        cmd = ["claude", "-p", task["prompt"], "--disallowedTools", "WebFetch,WebSearch,Agent,NotebookEdit,Skill"]
    cmd += ["--model", model, "--output-format", "stream-json", "--verbose", "--max-turns", str(turns),
            "--permission-mode", "acceptEdits", "--allowedTools", "Bash(node:*)", "Bash(python3:*)", "Bash(ls:*)", "Bash(cat:*)"]
    try:
        raw = subprocess.run(cmd, cwd=d, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=1800).stdout
    except subprocess.TimeoutExpired as e:
        raw = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
    answer, cost, reads, skills = "", None, [], []
    for line in raw.splitlines():
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("type") == "assistant":
            for c in o["message"].get("content", []):
                if c.get("type") == "tool_use":
                    p = c["input"].get("file_path") or ""
                    if p.startswith(SKILL + os.sep):
                        reads.append(os.path.relpath(p, SKILL))
                    if c["name"] == "Skill":
                        skills.append(c["input"].get("skill", ""))
        if o.get("type") == "result":
            answer, cost = o.get("result") or "", o.get("total_cost_usd")
    open(os.path.join(d, "ANSWER.md"), "w").write(answer)
    meta = {"task": task["id"], "arm": arm, "cost": cost, "skill_files_read": reads, "skills": skills}
    json.dump(meta, open(os.path.join(d, "run.json"), "w"), indent=1)
    if os.path.exists(final):
        shutil.rmtree(final)
    shutil.copytree(d, final)
    print(f"{task['id']} {arm:7} ${cost or 0:.2f} | {len(set(reads))} skill files | answer {len(answer)} chars", flush=True)
    return meta


def main():
    if "-h" in sys.argv or "--help" in sys.argv or len(sys.argv) < 2:
        print(__doc__); return 0
    out = os.path.abspath(sys.argv[1])
    ids = set((arg("--ids") or "A,B,C,D").split(","))
    model, jobs, turns = arg("--model", "sonnet"), int(arg("--jobs", "8")), int(arg("--max-turns", "40"))
    tasks = [t for t in TASKS if t["id"] in ids]
    json.dump(tasks, open(os.path.join(out, "tasks.json") if os.path.isdir(out) else (os.makedirs(out) or os.path.join(out, "tasks.json")), "w"), ensure_ascii=False, indent=1)
    with ThreadPoolExecutor(jobs) as ex:
        list(ex.map(lambda p: run(p[0], p[1], out, model, turns), [(t, a) for t in tasks for a in ("with", "without")]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
