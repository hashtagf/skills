# The values file is the decision log

Contents:
- [Why this is the highest-leverage habit here](#why-this-is-the-highest-leverage-habit-here)
- [What a comment must answer](#what-a-comment-must-answer)
- [The four shapes](#the-four-shapes)
- [Markers](#markers)
- [Correcting a comment](#correcting-a-comment)
- [Measurements beat adjectives](#measurements-beat-adjectives)
- [What not to comment](#what-not-to-comment)
- [Where this pays off](#where-this-pays-off)

---

## Why this is the highest-leverage habit here

A GitOps repo has an unusual property: **the configuration outlives every other record of why
it is that way.** The ticket closes. The Slack thread ages out. The ADR was written before the
third revision. The person who made the call changed teams. What survives is a line in a values
file that says `readyPath: /healthz`, and no way to tell whether that was considered or copied.

The consequence is specific and expensive: nobody dares change it, or somebody changes it
casually and reintroduces the incident it was written to prevent. Both are bad; the second is
worse.

Writing the reason costs thirty seconds at the moment you already have all the context. There
is no cheaper moment, and it will never be this cheap again.

This also changes what an LLM agent can do with the repo later. An agent reading
`PROVIDER_URL: https://api.example.net` can only pattern-match. An agent reading that line
with a comment saying it is a production endpoint, that dev shares production's egress IPs, and
that the API key lives per-tenant in a database rather than here, can reason about a change
instead of guessing at one.

## What a comment must answer

Not what the line does — the key already says that. Answer the questions the next person will
actually have:

1. **Why this value and not the obvious one?**
2. **What breaks if it changes?**
3. **What was measured or verified**, and when?
4. **What has to become true before this can be deleted or changed?**

The fourth is the one people skip and the one that compounds. A temporary setting with no exit
condition is permanent by default.

## The four shapes

### 1 — The non-obvious default

```yaml
readyPath: /healthz   # payment serves only /healthz (no /readyz) — chart default /readyz 404s
```

One line, and it prevents someone from "fixing" the inconsistency and taking the service out
of the endpoints.

### 2 — The accepted risk

Four parts: what, why it is acceptable, what changes it, when it goes.

```yaml
# ⚠️ DEV ONLY — MODE=development wires DevAuth, which injects identity headers itself.
# The real headers come from the edge JWT filter, which does not exist yet. With a public
# route and no edge policy, ANY caller can inject X-User-Id and act as that user.
# Accepted ONLY while this is dev data. Remove before any real tenant, and never copy
# this key to uat/staging/prod.
MODE: development
```

Now a reader can act. Without it they must escalate, and escalation is slow enough that they
usually just leave it.

### 3 — The deliberate omission

The hardest thing to see in a config file is something that is not there.

```yaml
# AUTH_SERVICE_URL is deliberately unset. The outbound client posts to a path its own
# source marks as an unconfirmed proposal. Config treats the URL as optional, so unset
# means employee-create skips credential provisioning entirely — which beats calling a
# path that may 404. Set it to http://auth (ClusterIP, NEVER the public hostname) once
# the path is agreed.
```

An absent key and a forgotten key look identical. This is the only way to tell them apart.

### 4 — The dependency that is not visible from here

```yaml
# MUST be the same DB the deposit service reads: bank writes bank_statement and deposit's
# consumer looks it up by the StatementID in the command — a miss is treated as a broken
# contract and dead-letters. deposit @ dev uses ledger_dev with no prefix, so bank
# must too.
MONGO_DB: ledger_dev
```

This value looks wrong (a service pointing at another service's database) and is right. Without
the comment, someone corrects it and breaks a pipeline in a way that surfaces as dead-letters
in a third service.

## Markers

A small, consistent vocabulary makes the repo greppable:

| Marker | Means | Example |
| ---| ---| --- |
| `⚠️` | changing or copying this has consequences beyond this file | a dev-only auth bypass |
| `TODO(<scope>):` | known work, with the scope that owns it | `TODO(east-west): move to ClusterIP` |
| `ponytail:` (or your own word) | delete this when its condition is met | `ponytail: remove when the real adapter lands` |
| `<ADR-ID>` | the decision record this implements | `ARCH-0014`, `ADR-0007` |
| `<DEBT-ID>` | known debt this is an instance of | `DEBT-0003` |

The exact words do not matter; using them consistently does. Pick them, write them in the repo
README, and then `grep -rn 'ponytail:'` answers "what cleanup is outstanding" in one command —
which is the difference between a cleanup list that exists and one that does not.

Referencing an ADR id is what keeps the comment short. The values file says *what and what
breaks*; the ADR holds the argument. Without the reference, either the comment becomes an essay
or the reasoning is lost.

## Correcting a comment

A stale comment is worse than no comment, because it is actively believed. When you find one
wrong, correct it **in place and say so**:

```yaml
# Corrected 2026-08-04 — this comment used to end "flip to true only after checking who
# owns the exchange", which was wrong twice. The exchange EXISTS and is legacy-owned. And
# flipping this flag would not declare it anyway: the declare needs `configure`, which this
# user does not have and deliberately will not get — the broker refuses it, which is a
# stronger version of what this flag was reaching for. Leave it false.
DECLARE_SMS_EXCHANGE: "false"
```

Recording the correction is not ceremony. Someone already read the old version and formed a
belief from it; the correction is addressed to them. It also tells the next reader that this
line has been examined recently, which is information they cannot get any other way.

## Measurements beat adjectives

"Small", "should be enough", "seems fine" are not reviewable. Numbers with a date are.

```yaml
# Next.js, not a Go binary: measured 46Mi at rest against 8–18Mi for every Go service
# here, and a JS runtime's floor moves with page count. The chart default would leave
# only ~5x headroom on a runtime that spikes on first render after a deploy.
resources:
  requests: {cpu: 20m, memory: 128Mi}
  limits:   {memory: 512Mi}
```

A future reader can re-measure and compare. With an adjective, they can only re-guess.

Same for verification: "verified 2026-07-31 from the public internet — no headers → 401, hand-
sent identity headers → 404 DATA_NOT_FOUND, meaning the gate passed and the request reached the
handler" is evidence. "This looks exposed" is a hunch, and hunches do not survive a busy week.

## What not to comment

The habit fails if it becomes noise. Skip:

- restating the key (`replicas: 1  # one replica`);
- anything the chart's own `values.yaml` already explains — comment there once instead;
- process narration (`# added by Bob for the sprint 12 release`) — git has that, and it goes
  stale immediately;
- long-form argument that belongs in an ADR. Reference it.

The test: **would this line change what a competent stranger does?** If not, cut it.

## Where this pays off

- **Onboarding** — a new engineer reads the values files and learns the system, including its
  scars, without a meeting.
- **Incidents** — "why is this set this way" is answered in the file you already have open,
  not in a search of a closed ticket tracker.
- **Audits** — accepted risks are enumerated with their conditions, so the audit becomes a
  review of decisions rather than a discovery exercise.
- **Cleanup** — `grep -rn 'ponytail:\|TODO('` is the backlog, and it is attached to the code
  it describes rather than to a board nobody opens.
- **Agent-assisted work** — an agent asked to change a value can see the constraint instead of
  discovering it by breaking something.
