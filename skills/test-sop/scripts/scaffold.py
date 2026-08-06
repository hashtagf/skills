#!/usr/bin/env python3
"""Scaffold a test documentation set at a chosen SOP level.

Writes skeletons only — the acceptance criteria and business rules depend on the real
system, so you still write those. Every spot needing input is marked TODO; run
`grep -rn TODO <dir>` and clear all of them before handing the set over.

Use --lang th when the team's working language is Thai (the generated headings and prompts
switch, so the filled document reads naturally for its readers).

Examples:
  python3 scaffold.py --out ./docs/test --level 2 --project "Shop" \
      --module "Checkout:SC-CHK:6" --module "Cart:SC-CART:4"
  python3 scaffold.py --out ./docs/test --level 4 --preset auth --project "Zyra"
  python3 scaffold.py --out ./docs/test --level 1 --project "Shop" --task "fix delete button"
  python3 scaffold.py --out ./docs/test --level 2 --lang th --module "Cart:SC-CART:4"
"""

import argparse
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------- presets

PRESETS = {
    "auth": [
        ("Register", "SC-REG", 6),
        ("Email Verification", "SC-VERIFY", 4),
        ("Login", "SC-LOGIN", 5),
        ("Social / OAuth Login", "SC-OAUTH", 5),
        ("Two-Factor Authentication", "SC-MFA", 6),
        ("Forgot / Reset Password", "SC-PWD", 6),
        ("Session & Token", "SC-SESSION", 6),
        ("Logout", "SC-LOGOUT", 4),
        ("Account Security", "SC-ACC", 5),
        ("Authorization Guard", "SC-AUTHZ", 5),
        ("Security & Abuse Prevention", "SC-SEC", 6),
        ("Edge & Resilience", "SC-EDGE", 6),
    ],
    "payment": [
        ("Checkout", "SC-CHK", 6),
        ("Payment Method", "SC-METHOD", 5),
        ("Gateway Callback & Webhook", "SC-HOOK", 6),
        ("Refund / Void", "SC-REFUND", 5),
        ("Reconciliation", "SC-RECON", 4),
        ("Invoice / Receipt", "SC-INV", 4),
        ("Fraud & Rate Limit", "SC-FRAUD", 5),
        ("Authorization Guard", "SC-AUTHZ", 4),
        ("Edge & Resilience", "SC-EDGE", 5),
    ],
    "crud": [
        ("Create", "SC-CREATE", 5),
        ("List & Search", "SC-LIST", 6),
        ("Detail & Edit", "SC-EDIT", 5),
        ("Delete", "SC-DELETE", 4),
        ("Permission", "SC-PERM", 4),
    ],
    "api": [
        ("Resource CRUD", "SC-API", 8),
        ("Authentication & Authorization", "SC-AUTHZ", 5),
        ("Validation & Error Contract", "SC-VALID", 6),
        ("Edge & Resilience", "SC-EDGE", 5),
    ],
    "integration": [
        ("Happy Integration Flow", "SC-INT", 4),
        ("Webhook Handling", "SC-HOOK", 5),
        ("Provider Failure & Retry", "SC-FAIL", 5),
        ("Credential & Config", "SC-CONF", 3),
        ("Edge & Resilience", "SC-EDGE", 5),
    ],
    "migration": [
        ("Pre-check", "SC-PRE", 3),
        ("Migration Run", "SC-RUN", 5),
        ("Post-verify & Reconcile", "SC-POST", 4),
        ("Rollback", "SC-ROLL", 3),
        ("Edge & Resilience", "SC-EDGE", 5),
    ],
}

TYPE_CYCLE = ["Happy Path", "Error Path", "Error Path", "Alternate Path", "Edge Path", "Security Path"]

# ---------------------------------------------------------------- strings

L = {
    "en": {
        "overview": "Overview", "scenarios": "Scenarios", "steps": "Scenario Steps",
        "ac": "Acceptance Criteria", "bl": "Business Logic / Rules", "ux": "UX/UI",
        "persona": "**Persona:**", "pre": "**Pre-condition:**",
        "todo_name": "TODO name this scenario",
        "todo_overview": "TODO what this module does and how many flows it covers",
        "todo_persona": "TODO who acts + their context (write Attacker for Security Path)",
        "todo_pre": "TODO reproducible starting state",
        "todo_step": "TODO reproducible step, written from the user's point of view",
        "todo_ac": "TODO observable on screen or in an API response (aim for 5-10)",
        "todo_bl": "TODO rules / config / requirements not visible on screen",
        "todo_ux": "TODO Figma link with node-id",
        "checklist_note": "copied 1:1 from the scenario's Acceptance Criteria",
        "copy_note": "paste this block into the task description",
        "type_note": ("Types below are defaults from the script — correct them per the rules in "
                      "references/taxonomy.md"),
        "shared": "Shared Rules",
        "todo_shared": ("TODO rules true for every scenario here (token lifetimes, currency, audit "
                        "logging). Scenarios cite them as SR-1, SR-2 instead of repeating them"),
        "index_title": "Test Documentation",
        "structure": "Task structure",
        "module_list": "Module list", "total": "Total", "file": "File",
        "out_of_scope": "Out of scope",
        "out_of_scope_body": ("TODO list what will not be tested and why — a document that "
                              "doesn't say what was skipped reads as \"everything is tested\""),
        "test_data": "Test data to prepare", "name_col": "Name", "detail_col": "Detail",
        "bug_template": "Bug template",
        "bug_title_note": "Title it: `Issue [SC-XXX-NN] : <short symptom>`",
        "dod": "Definition of Done",
        "dod_items": ["every scenario checklist run, no blank items",
                      "Happy + Alternate pass 100%",
                      "every bug closed or explicitly accepted with a reason",
                      "no TODO left in any file (`grep -rn TODO .`)"],
        "trace_title": "Traceability Matrix",
        "trace_note": ("Answers \"is our coverage complete?\" with evidence — method in "
                       "references/coverage-audit.md"),
        "inventory": "Scenario inventory", "status": "Status", "risk": "Risk",
        "test_task": "Test task", "scenario": "Scenario", "bug": "Bug",
        "status_note": ("Statuses: `Pass` / `Fail` / `Blocked` / `Skipped` — Blocked and Skipped "
                        "need a written reason"),
        "distribution": "Path-type distribution", "count": "Count", "share": "Share",
        "target": "Target", "flow_type": "Flow × Type",
        "accepted_gaps": "Gaps accepted on purpose", "cell": "Cell", "reason": "Reason",
        "req_map": "Requirement → Scenario", "req": "Requirement", "complete": "Complete?",
        "bug_map": "Bug → Scenario → failed criterion", "failed_ac": "Failed criterion",
        "smoke_note": "Level 1 Smoke — prove nothing broke",
        "scope": "Scope",
        "scope_body": ("what changed + which flows it touches — walk the call sites of the changed "
                       "code, don't guess from filenames"),
        "checklist": "Checklist",
        "smoke_items": ["happy path of the flow you touched",
                        "the original bug symptom — cite the steps from the bug ticket, not memory",
                        "regression, neighbouring flow sharing the same code 1",
                        "regression, neighbouring flow sharing the same code 2",
                        "no console errors and no 5xx responses across the flow"],
        "not_tested": "Not tested",
        "not_tested_item": "what you deliberately skipped + why",
        "smoke_exit": "Closing criterion: 100% pass — L1 has no room for accepted failures",
        "nfr_note": ("Re-run per module · paste the relevant sections from "
                     "references/checklist-library.md §NFR"),
        "plan_note": "Fill from the full template in references/planning-docs.md §1",
        "summary_note": ("Fill from the full template in references/planning-docs.md §4 when the "
                         "cycle closes"),
        "summary_sec5": "5. What was not tested (never leave this empty)",
        "item": "Item", "risk_accepted": "Risk accepted",
        "wrote": "Wrote {n} file(s) to {out}",
        "skipped": "Skipped {n} existing file(s) (use --force to overwrite):",
        "next": ("Next: confirm the scenario list with the work's owner before writing criteria, "
                 "then fill every TODO. Run `grep -rn TODO {out}` before handing over."),
    },
    "th": {
        "overview": "Overview", "scenarios": "Scenarios", "steps": "Scenario Steps",
        "ac": "Acceptance Criteria", "bl": "Business Logic / Rules", "ux": "UX/UI",
        "persona": "**Persona:**", "pre": "**Pre-condition:**",
        "todo_name": "TODO ตั้งชื่อ scenario",
        "todo_overview": "TODO อธิบายว่า module นี้ทำอะไร ครอบคลุมกี่ flow",
        "todo_persona": "TODO ใครทำ + บริบทของเขา (Security Path เขียนเป็น Attacker)",
        "todo_pre": "TODO สภาวะที่ต้องมีก่อนเริ่ม ระบุให้ทำซ้ำได้",
        "todo_step": "TODO ขั้นตอนที่ทำซ้ำได้ เขียนจากมุมผู้ใช้",
        "todo_ac": "TODO สิ่งที่ตรวจได้ด้วยตาหรือด้วย API response (ควรมี 5–10 ข้อ)",
        "todo_bl": "TODO กฎ / config / ข้อกำหนดที่ตรวจจากหน้าจอไม่ได้",
        "todo_ux": "TODO Figma link พร้อม node-id",
        "checklist_note": "คัดจาก Acceptance Criteria ของ scenario แบบ 1:1",
        "copy_note": "คัดลอกบล็อกนี้ลง description ของ task",
        "type_note": "Type ที่ script ใส่ไว้เป็นค่าเริ่มต้น — แก้ให้ตรงตามกฎใน references/taxonomy.md",
        "shared": "Shared Rules",
        "todo_shared": ("TODO กฎที่ใช้กับทุก scenario ใน module นี้ (อายุ token, สกุลเงิน, audit log) "
                        "แล้วให้ scenario อ้างเป็น SR-1, SR-2 แทนการเขียนซ้ำ"),
        "index_title": "เอกสารการทดสอบ",
        "structure": "โครงสร้าง task",
        "module_list": "Module list", "total": "รวม", "file": "ไฟล์",
        "out_of_scope": "ไม่อยู่ใน scope",
        "out_of_scope_body": ("TODO เขียนสิ่งที่ไม่ทดสอบ + เหตุผล — เอกสารที่ไม่บอกว่าอะไรไม่ได้เทส "
                             "ทำให้คนอ่านเข้าใจว่าเทสหมดแล้ว"),
        "test_data": "Test data ที่ต้องเตรียม", "name_col": "ชื่อ", "detail_col": "รายละเอียด",
        "bug_template": "Bug template",
        "bug_title_note": "ตั้งชื่อ: `Issue [SC-XXX-NN] : <อาการสั้น ๆ>`",
        "dod": "Definition of Done",
        "dod_items": ["checklist ทุก scenario ถูกรันครบ ไม่มีข้อว่าง",
                      "Happy + Alternate ผ่าน 100%",
                      "bug ทุกใบปิดหรือถูก accept พร้อมเหตุผล",
                      "ไม่มี TODO ค้างในไฟล์ใด (`grep -rn TODO .`)"],
        "trace_title": "Traceability Matrix",
        "trace_note": "ตอบคำถาม \"ครอบคลุมหรือยัง\" ด้วยหลักฐาน — วิธีใช้ใน references/coverage-audit.md",
        "inventory": "Scenario inventory", "status": "สถานะ", "risk": "Risk",
        "test_task": "Test task", "scenario": "Scenario", "bug": "Bug",
        "status_note": "สถานะ: `Pass` / `Fail` / `Blocked` / `Skipped` — Blocked และ Skipped ต้องมีเหตุผลเขียนไว้",
        "distribution": "สัดส่วนตาม Type", "count": "จำนวน", "share": "สัดส่วน",
        "target": "เป้า", "flow_type": "Flow × Type",
        "accepted_gaps": "ช่องว่างที่ยอมรับโดยเจตนา", "cell": "ช่อง", "reason": "เหตุผล",
        "req_map": "Requirement → Scenario", "req": "Requirement", "complete": "ครบ?",
        "bug_map": "Bug → Scenario → AC ที่ล้มเหลว", "failed_ac": "AC ข้อที่ล้มเหลว",
        "smoke_note": "Level 1 Smoke — พิสูจน์ว่าไม่พัง",
        "scope": "ขอบเขต",
        "scope_body": ("งานที่แก้ + flow ที่กระทบ — ไล่จาก call site ของโค้ดที่แก้ "
                       "ไม่ใช่เดาจากชื่อไฟล์"),
        "checklist": "Checklist",
        "smoke_items": ["happy path ของ flow ที่แตะ",
                        "อาการเดิมของ bug — อ้าง Step จากใบ bug ห้ามเขียนใหม่จากความจำ",
                        "regression flow ข้างเคียงที่ใช้โค้ดร่วมกัน 1",
                        "regression flow ข้างเคียงที่ใช้โค้ดร่วมกัน 2",
                        "ไม่มี error ใน console และไม่มี response 5xx ตลอด flow"],
        "not_tested": "ไม่ได้ทดสอบ",
        "not_tested_item": "สิ่งที่ตั้งใจไม่เทส + เหตุผล",
        "smoke_exit": "เกณฑ์ปิด: ผ่าน 100% — L1 ไม่มีที่ให้ยอมรับข้อที่ไม่ผ่าน",
        "nfr_note": "รันซ้ำทุก module · หยิบหมวดที่เกี่ยวข้องจาก references/checklist-library.md §NFR",
        "plan_note": "คัด template เต็มจาก references/planning-docs.md §1 มาเติม",
        "summary_note": "คัด template เต็มจาก references/planning-docs.md §4 มาเติมตอนปิดรอบ",
        "summary_sec5": "5. สิ่งที่ไม่ได้ทดสอบ (ห้ามเว้นว่าง)",
        "item": "รายการ", "risk_accepted": "ความเสี่ยงที่รับไว้",
        "wrote": "เขียนไฟล์ {n} ไฟล์ที่ {out}",
        "skipped": "ข้าม {n} ไฟล์ที่มีอยู่แล้ว (ใช้ --force เพื่อเขียนทับ):",
        "next": ("ขั้นถัดไป: ยืนยัน scenario list กับเจ้าของงานก่อนเขียน AC แล้วเติมทุกจุดที่เป็น TODO "
                 "และรัน `grep -rn TODO {out}` ก่อนส่งมอบ"),
    },
}

NFR_SECTIONS = ["Performance", "Accessibility", "Compatibility", "Localization",
                "Observability", "Change-related (confirmation + regression)"]


def slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s or "module"


def parse_module(spec):
    parts = spec.split(":")
    if len(parts) != 3:
        raise argparse.ArgumentTypeError(f'--module must look like "Name:CODE:count", not "{spec}"')
    name, code, count = parts[0].strip(), parts[1].strip().upper(), parts[2].strip()
    if not count.isdigit() or not 1 <= int(count) <= 30:
        raise argparse.ArgumentTypeError(f"scenario count must be 1-30, not '{count}'")
    return (name, code, int(count))


# ---------------------------------------------------------------- builders


def scenario_block(t, sid, stype):
    return f"""## {sid} · <{t['todo_name']}>

````markdown
## {sid} · <{t['todo_name']}>

**Type:** {stype}
{t['persona']} <{t['todo_persona']}>
{t['pre']} <{t['todo_pre']}>

## {t['steps']}
1. <{t['todo_step']}>
2.

## {t['ac']}
*   <{t['todo_ac']}>

## {t['bl']}
*   <{t['todo_bl']}>

## {t['ux']}
<{t['todo_ux']}>
````

### Test Scenario : <{t['todo_name']}>

> {t['checklist_note']}

````markdown
- [ ] <{t['todo_ac']}>
````
"""


def module_file(t, project, name, code, count, level):
    rows, blocks = [], []
    for i in range(1, count + 1):
        sid = f"{code}-{i:02d}"
        stype = TYPE_CYCLE[(i - 1) % len(TYPE_CYCLE)]
        if level <= 2 and stype in ("Edge Path", "Security Path"):
            stype = "Error Path"  # L1-L2 don't mandate Edge/Security
        rows.append(f"| {sid} | <{t['todo_name']}> | {stype} |")
        blocks.append(scenario_block(t, sid, stype))

    head = f"""# [Module] {name}

> {project} · {t['copy_note']} · tag: `<client/admin>` · priority: `<from the risk matrix>`
> {t['type_note']}

````markdown
## {name} Module

## {t['overview']}

<{t['todo_overview']}>

## {t['shared']}

*   SR-1 — <{t['todo_shared']}>

## {t['scenarios']}

| ID | Scenario | Type |
| ---| ---| --- |
{chr(10).join(rows)}
````

---

"""
    return head + "\n---\n\n".join(blocks)


def index_file(t, project, modules, level):
    total = sum(m[2] for m in modules)
    rows = "\n".join(
        f"| {i} | {name} | {code} | {count} | `{i:02d}-{slug(name)}.md` |"
        for i, (name, code, count) in enumerate(modules, 1)
    )
    dod = "\n".join(f"- [ ] {x}" for x in t["dod_items"])
    return f"""# {project} — {t['index_title']} (Level {level})

Generated by the test-sop scaffold · the 4-tier task structure and all rules live in the
test-sop skill.

## {t['structure']}

```
[Module] <name>                        ← overview + scenario table
└─ SC-<CODE>-NN · <scenario name>      ← tag: scenario · full spec
   └─ Test Scenario : <name>            ← checklist = criteria 1:1
└─ Issue [SC-<CODE>-NN] : <symptom>    ← task type: Bug · under the Module
```

## {t['module_list']}

| # | Module | Code | Scenarios | {t['file']} |
| ---| ---| ---| ---| --- |
{rows}
|  | **{t['total']}** |  | **{total}** |  |

## {t['out_of_scope']}

- {t['out_of_scope_body']}

## {t['test_data']}

| {t['name_col']} | {t['detail_col']} |
| ---| --- |
| TODO | TODO |

## {t['bug_template']}

```markdown
## Step
1. <reproducible step from a clearly stated starting state>

## Current Result
<what actually happens> + screenshot

## **Expected Result**
<what should happen — cite which criterion>
```

{t['bug_title_note']}

## {t['dod']}

{dod}
"""


def traceability_file(t, project, modules):
    rows = []
    for _name, code, count in modules:
        for i in range(1, count + 1):
            rows.append(f"| {code}-{i:02d} | <name> | <Type> | <R?> | | | |")
    types = [("Happy Path", "~20%"), ("Alternate Path", "~20%"), ("Error Path", "~30%"),
             ("Edge Path", "~15%"), ("Security Path", "~15%")]
    dist = "\n".join(f"| {n} | | | {tg} |" for n, tg in types)
    return f"""# {t['trace_title']} — {project}

{t['trace_note']}

## 1. {t['inventory']}

| ID | {t['scenario']} | Type | {t['risk']} | {t['test_task']} | {t['status']} | {t['bug']} |
| ---| ---| ---| ---| ---| ---| --- |
{chr(10).join(rows)}

{t['status_note']}

## 2. {t['distribution']}

| Type | {t['count']} | {t['share']} | {t['target']} |
| ---| ---| ---| --- |
{dist}

## 3. {t['flow_type']}

| Flow | Happy | Alternate | Error | Edge | Security |
| ---| ---| ---| ---| ---| --- |
{chr(10).join(f"| {name} | | | | | |" for name, _, _ in modules)}

### {t['accepted_gaps']}

| {t['cell']} | {t['reason']} |
| ---| --- |
| TODO | TODO |

## 4. {t['req_map']}

| Req | {t['req']} | {t['scenario']} | {t['complete']} |
| ---| ---| ---| --- |
| | | | |

## 5. {t['bug_map']}

| {t['bug']} | {t['scenario']} | {t['failed_ac']} | {t['status']} |
| ---| ---| ---| --- |
| | | | |
"""


def smoke_file(t, project, task):
    items = "\n".join(f"- [ ] <{x}>" for x in t["smoke_items"])
    return f"""# Test : {task}

> {project} · {t['smoke_note']}

## {t['scope']}

<{t['scope_body']}>

## {t['checklist']}

```markdown
{items}
```

## {t['not_tested']}

- <{t['not_tested_item']}>

{t['smoke_exit']}
"""


def nfr_file(t):
    body = "\n\n".join(f"## {s}\n\n```markdown\n- [ ] TODO\n```" for s in NFR_SECTIONS)
    return f"# Non-Functional Checklist\n\n> {t['nfr_note']}\n\n{body}\n"


def plan_file(t, project):
    return f"""# Test Plan — {project}

> {t['plan_note']}

## 1. Scope / out of scope

TODO

## 2. Test Strategy

TODO

## 3. Test Environment

TODO

## 4. Risk Assessment

| # | Risk | Impact | Likelihood | Level | Covering scenarios |
| ---| ---| ---| ---| ---| --- |
| R1 | TODO | | | | |

## 5. Entry Criteria

- [ ] TODO

## 6. Exit Criteria

- [ ] TODO

## 7. Roles

TODO

## 8. Schedule

TODO
"""


def summary_file(t, project):
    return f"""# Test Summary Report — {project}

> {t['summary_note']}

## {t['summary_sec5']}

| {t['item']} | {t['reason']} | {t['risk_accepted']} |
| ---| ---| --- |
| TODO | | |
"""


# ---------------------------------------------------------------- main


def main():
    p = argparse.ArgumentParser(description="Scaffold a test documentation set (test-sop skill)")
    p.add_argument("--out", required=True, help="output directory")
    p.add_argument("--level", type=int, choices=[1, 2, 3, 4], default=2)
    p.add_argument("--project", default="Project")
    p.add_argument("--module", action="append", type=parse_module, default=[],
                   help='"Name:CODE:count" — repeatable')
    p.add_argument("--preset", choices=sorted(PRESETS), help="ready-made module list")
    p.add_argument("--task", default="TODO work item", help="used with --level 1")
    p.add_argument("--lang", choices=["en", "th"], default="en",
                   help="language of the generated skeletons (default en)")
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    args = p.parse_args()

    t = L[args.lang]
    out = Path(args.out)
    modules = list(args.module)
    if args.preset:
        modules = PRESETS[args.preset] + modules
    if args.level >= 2 and not modules:
        p.error("--module or --preset is required for level 2 and above")

    out.mkdir(parents=True, exist_ok=True)
    written, skipped = [], []

    def write(relpath, content):
        target = out / relpath
        if target.exists() and not args.force:
            skipped.append(relpath)
            return
        target.write_text(content, encoding="utf-8")
        written.append(relpath)

    if args.level == 1:
        write("test-smoke.md", smoke_file(t, args.project, args.task))
    else:
        write("00-INDEX.md", index_file(t, args.project, modules, args.level))
        for i, (name, code, count) in enumerate(modules, 1):
            write(f"{i:02d}-{slug(name)}.md",
                  module_file(t, args.project, name, code, count, args.level))
        n = len(modules)
        if args.level >= 3:
            write(f"{n + 1:02d}-non-functional.md", nfr_file(t))
            write(f"{n + 2:02d}-traceability-matrix.md",
                  traceability_file(t, args.project, modules))
        if args.level >= 4:
            write(f"{n + 3:02d}-test-plan.md", plan_file(t, args.project))
            write(f"{n + 4:02d}-test-summary-report.md", summary_file(t, args.project))

    print(t["wrote"].format(n=len(written), out=out))
    for f in written:
        print(f"  + {f}")
    if skipped:
        print("\n" + t["skipped"].format(n=len(skipped)))
        for f in skipped:
            print(f"  - {f}")
    if args.level >= 2:
        print("\n" + t["next"].format(out=out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
