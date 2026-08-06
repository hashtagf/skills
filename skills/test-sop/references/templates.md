# Copy-paste templates

Every template sits in a ```markdown``` block so it can be pasted straight into a task
description. Write the filled content in **the team's language** — the examples here are
English, but a Thai-speaking team should get Thai (mixed with English technical terms is
normal and reads fastest for them).

## Contents

1. Module task
2. Scenario spec
3. Test case checklist
4. Bug report
5. API-only scenario spec
6. L1 smoke checklist
7. Banned words in acceptance criteria

---

## 1. Module task

```markdown
## <Name> Module

## Overview

<what this module does> — covers N main flows:

*   flow 1
*   flow 2
*   flow 3

## Shared Rules

Rules that apply to every scenario in this module. Scenarios reference them by number instead
of repeating them.

*   SR-1 — <e.g. every state-changing endpoint requires a CSRF token>
*   SR-2 — <e.g. all amounts are THB with 2 decimals>

## Scenarios

| ID | Scenario | Type |
| ---| ---| --- |
| SC-XXX-01 | <scenario name> | Happy Path |
| SC-XXX-02 | <scenario name> | Error Path |
| SC-XXX-03 | <scenario name> | Security Path |
```

**Shared Rules is what keeps a large module from bloating.** Anything true for every scenario —
token lifetimes, currency handling, audit logging, rate limits — goes here once, and each
scenario's Business Logic section says "SR-1, SR-3 apply" plus only what is specific to it.
Without this, the same five rules get retyped in every scenario, which is most of the volume in
a 40-scenario set and makes the rules drift apart as they're edited.

**IDs:** `SC-<CODE>-<two digits>` where CODE abbreviates the module (LOGIN, PWD, ORDER, PAY).
Numbers must not change once the list is confirmed, because bugs and the traceability matrix
cite them. To add scenarios, append — never insert in the middle.

## 2. Scenario spec

```markdown
## SC-XXX-01 · <scenario name>

**Type:** Happy Path
**Persona:** <who acts + their context>
**Pre-condition:** <the starting state, stated so anyone can reproduce it>

## Scenario Steps
1. <a reproducible step, written from the user's point of view>
2. ...

## Acceptance Criteria
*   <something observable on screen or in an API response>

## Business Logic / Rules
*   <rules, config values, security requirements that aren't visible on screen>

## UX/UI
<Figma link including the node-id of that screen>
```

**Personas need context**, not just "User" — write "Registered User — has an account, email
already verified", because half the pre-condition hides inside the persona. For Security paths
write the persona as "Attacker — has a proxy pool across many IPs" so whoever runs it knows
what to prepare.

**Aim for 5–10 criteria.** Fewer than 5 usually means the thinking isn't finished; more than
10 usually means the scenario should be split.

## 3. Test case checklist

One scenario = one tracker task named `Test Scenario : <scenario name>`, containing the
acceptance criteria 1:1.

```markdown
- [ ] <criterion 1, copied verbatim>
- [ ] <criterion 2, copied verbatim>
```

It must be 1:1 so that a failing item identifies exactly one criterion, and traceability back
to the requirement needs no interpretation.
The only allowed edit: dropping a long parenthetical reference so the line reads well on a
phone. Never drop a condition that has to be checked.

## 4. Bug report

Title: `Issue [SC-XXX-NN] : <short symptom>`, filed under the **Module**, not under the
scenario (one bug usually spans several scenarios, and scenarios should stay specs rather than
becoming bug archives).

```markdown
## Step
1. <reproducible step from a clearly stated starting state>
2. ...

## Current Result
<what actually happens> + screenshot / screen recording

## **Expected Result**
<what should happen — cite which criterion or business rule>
```

**The expected result must cite a criterion.** If you can't cite one, either the spec doesn't
cover this (add the criterion first) or it's a personal opinion rather than a bug (talk to the
PM before filing).

### Severity rubric

The summary report buckets bugs into four severities, so they need one shared definition —
otherwise every ticket becomes a negotiation. Severity is about consequence, not effort to fix.

| Severity | Definition | Examples |
| ---| ---| --- |
| **Critical** | data loss or corruption, money wrong, unauthorized access, or the primary flow is impossible for everyone — and there is no workaround | charged twice; another user's data visible; nobody can log in |
| **High** | a main flow fails or produces a wrong result for a common case; a workaround exists but is unreasonable to ask of users | reset password succeeds but login then fails; totals wrong on one payment method |
| **Medium** | a secondary flow or an uncommon case fails, or the primary flow is unpleasant but completable | validation message missing; a filter combination returns the wrong count |
| **Low** | cosmetic, wording, or an edge case with negligible impact | text overflows at 320px; inconsistent capitalisation |

Two rules that prevent most arguments:
- **Security findings start at High and move up, never down**, unless the attack is impossible in
  the deployed configuration — and then say why in the ticket.
- **Frequency raises severity, it doesn't lower it.** A wrong total that hits 1% of orders is
  still Critical; being rare makes it harder to find, not cheaper to ship.

## 5. API-only scenario spec

Drop UX/UI, add Request/Response.

```markdown
## SC-XXX-01 · <scenario name>

**Type:** Error Path
**Persona:** <the calling client + the permissions it holds>
**Pre-condition:** <required database state + which token is used>

## Request
```
POST /api/v1/orders
Authorization: Bearer <token for role user>
{ "items": [], "coupon": "EXPIRED2020" }
```

## Expected Response
```
422 Unprocessable Entity
{ "error_code": "EMPTY_CART", "message": "..." }
```

## Acceptance Criteria
*   responds 422 with error_code `EMPTY_CART`
*   no order is created in the database
*   no stack trace or table name appears in the response

## Business Logic / Rules
*   validate at the first layer, before touching the database
```

## 6. L1 smoke checklist

L1 has no scenario specs — one task named `Test : <work item>`.

```markdown
## Scope
<what changed + which flows it touches>

## Checklist
- [ ] <happy path of the flow you touched>
- [ ] <the original bug symptom — cite the steps from the bug ticket>
- [ ] <regression, neighbouring flow 1>
- [ ] <regression, neighbouring flow 2>

## Not tested
- <what you deliberately skipped + why>
```

## 7. Banned words in acceptance criteria

If a criterion contains one of these, rewrite it — they make the result depend on who ran the
test rather than on the system. Thai equivalents are listed because these are the phrases that
actually appear in Thai-language test docs.

| Don't write | Write instead |
| ---| --- |
| the system is fast / ระบบทำงานเร็ว | redirects within 1 second |
| easy to use / ใช้งานง่าย | the primary action is visible without scrolling |
| data is secure / ข้อมูลปลอดภัย | calling the API with a `user` role token returns 403 |
| displays correctly / แสดงผลถูกต้อง | the table total equals the sum of the visible rows |
| works normally / ทำงานได้ปกติ | (name the observable behaviour — if you can't, you don't yet know what to test) |
| handles large data / รองรับข้อมูลจำนวนมาก | 10,000 rows load within 3 seconds with no frozen frame |
| no errors / ไม่มี error | no console errors and no 5xx responses across the whole flow |
