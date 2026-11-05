#!/usr/bin/env python3
"""Export eval results as JSON files for the eval dashboard.

Usage: python3 evals/export_dashboard_data.py OUT_DIR
Writes scenarios.json (one row per routing scenario, with pass/fail per run), routing_runs.json
(one row per routing run) and trigger.json (one row per trigger prompt, with pass rate per run).
Standard library only.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import route_eval as R  # noqa: E402
import trigger_eval as T  # noqa: E402

RES = os.path.join(HERE, "results")
ROUTING_RUNS = ["v3", "v4", "v5", "v6", "v7", "v8"]
TRIGGER_RUNS = ["v3", "v4", "v5", "v6", "v8"]


def load(name):
    p = os.path.join(RES, name)
    return json.load(open(p)) if os.path.exists(p) else None


def main(out):
    os.makedirs(out, exist_ok=True)
    evs = json.load(open(os.path.join(HERE, "evals.json")))["evals"]
    byid = {e["id"]: e for e in evs}
    runs = {v: {r["id"]: r for r in (load(f"routing-{v}.json") or [])} for v in ROUTING_RUNS}

    rows = []
    for e in evs:
        row = {"id": e["id"], "field": e.get("field", ""), "category": e.get("category", ""),
               "prompt": e["prompt"], "fixture": os.path.basename(e.get("fixture", "")) or "",
               "expected": " + ".join("/".join(g) for g in e["expected_reads"])}
        for v in ROUTING_RUNS:
            r = runs[v].get(e["id"])
            row[v] = "" if r is None else ("pass" if R.score(e, r)["ok"] else "fail")
        last = next((runs[v][e["id"]] for v in reversed(ROUTING_RUNS) if e["id"] in runs[v]), None)
        if last:
            s = R.score(e, last)
            row.update({"latest": "pass" if s["ok"] else "fail",
                        "missed": " + ".join("/".join(g) for g in s["missed"]),
                        "wrong": ", ".join(s["wrong"]), "files": len(set(last["opened"])),
                        "kb": s["kb"], "cost": round(last["cost"] or 0, 2)})
        else:
            row.update({"latest": "", "missed": "", "wrong": "", "files": None, "kb": None, "cost": None})
        rows.append(row)
    json.dump(rows, open(os.path.join(out, "scenarios.json"), "w"), ensure_ascii=False, indent=1)

    rr = []
    for i, v in enumerate(ROUTING_RUNS):
        res = list(runs[v].values())
        if not res:
            continue
        ok = [R.score(byid[r["id"]], r)["ok"] for r in res]
        g = [R.score(byid[r["id"]], r)["ok"] for r in res if byid[r["id"]].get("field") == "greenfield"]
        b = [R.score(byid[r["id"]], r)["ok"] for r in res if byid[r["id"]].get("field") == "brownfield"]
        rr.append({"run": v, "order": i, "scenarios": len(res), "passed": sum(ok), "rate": round(sum(ok) / len(ok), 4),
                   "greenfield_passed": sum(g), "greenfield": len(g), "brownfield_passed": sum(b), "brownfield": len(b),
                   "cost": round(sum(r["cost"] or 0 for r in res), 2)})
    json.dump(rr, open(os.path.join(out, "routing_runs.json"), "w"), indent=1)

    trig = {}
    for v in TRIGGER_RUNS:
        for r in load(f"trigger-{v}.json") or []:
            t = trig.setdefault(r["prompt"], {"prompt": r["prompt"], "should": "should load" if r["should"] else "should not load"})
            t.setdefault(v + "_n", 0)
            t.setdefault(v + "_ok", 0)
            t[v + "_n"] += 1
            t[v + "_ok"] += T.good_pick(r)
    for t in trig.values():
        for v in TRIGGER_RUNS:
            n = t.pop(v + "_n", 0)
            ok = t.pop(v + "_ok", 0)
            t[v] = f"{ok}/{n}" if n else ""
            t[v + "_rate"] = round(ok / n, 4) if n else None
    json.dump(list(trig.values()), open(os.path.join(out, "trigger.json"), "w"), ensure_ascii=False, indent=1)
    print("wrote", len(rows), "scenarios,", len(rr), "routing runs,", len(trig), "trigger prompts to", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(RES, "dashboard"))
