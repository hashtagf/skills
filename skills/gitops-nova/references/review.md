# REVIEW mode — auditing a GitOps repo

Contents:
- [Order findings by blast radius](#order-findings-by-blast-radius)
- [Run the script first](#run-the-script-first)
- [The judgment checks](#the-judgment-checks)
- [Reading a repo you did not write](#reading-a-repo-you-did-not-write)
- [Say what you did not check](#say-what-you-did-not-check)
- [Report shape](#report-shape)

---

## Order findings by blast radius

Not by count, not by file, not by severity label. By what a single bad merge — or a single
motivated stranger — can reach.

| Tier | What belongs here |
| ---| --- |
| **1 — reachable and dangerous** | admin/ops surface on the internet; credentials committed; a service that trusts identity headers with no edge policy in front; internal APIs behind a flag that is on |
| **2 — unbounded** | `prune: true` on shared cluster-scoped objects; wildcard `sourceRepos`; a cluster-wide secret store; CI able to write prod paths |
| **3 — silently wrong** | exempt path bypassing its own allowlist; a disabled backend with a live producer; `enabled: false` that does nothing; probes on a portless component |
| **4 — will bite later** | unpinned versions; missing resource requests; undocumented decisions; parked-vs-broken indistinguishable |

Tier 1 findings should lead the report even if there is only one and there are forty of tier 4.
A list sorted by frequency buries the thing that matters.

## Run the script first

```bash
python3 scripts/audit.py <repo> --format json
```

Thirty seconds, and it changes what is worth reading closely. Every finding it produces is
mechanically decidable from the files; anything requiring judgment is below.

Treat its output as a floor. A clean run means the obvious checks passed, not that the repo is
sound.

## The judgment checks

### Exposure

- For every `route.enabled: true`, ask **who calls this from outside the cluster?** Grep the
  other values files for the hostname. If the answer is "nobody" or "one endpoint", the route
  is too wide or should not exist.
- Look at what the **process** serves, not just what the route says — the application's own
  repo, if you have it. A route allowlist protects the paths you knew about.
- Identify **mesh-verifies** services: ones whose auth gate only checks that identity headers
  are present. Public + no edge policy = full impersonation with three curl headers. This is
  the highest-value single check in an audit and it cannot be automated, because "does this
  service verify a token itself" is a code question.

### Secrets

- Any values key holding a literal credential — the script catches obvious shapes, not a
  base64 blob in an unexpected key.
- Is the store **scoped**, or is it the cluster's shared one? A correctly-shaped
  ExternalSecret pointed at an account-wide store is a leak waiting for one wrong path.
- Does any *service* hold an **admin** credential for a shared system (broker admin, DB
  superuser)? Per-service accounts with per-service permissions, or a compromise of the
  smallest service is a compromise of the platform.
- Is a credential **copied** between paths? Copies drift and rotation misses one.

### Blast radius

- `clusterResourceWhitelist: {"*","*"}` — expected during bring-up, suspicious after. Is
  there a `TODO` naming what it should narrow to?
- Is CODEOWNERS **enforced**? An unenforced CODEOWNERS reads as a control and is not one.
  Check branch protection, not just the file.
- Does the AppProject's destination list actually **bound** anything, or does it list every
  namespace on the cluster?
- Can CI push to `envs/prod/`?

### Correctness that silently degrades

- A **disabled backend with a live producer** — grep for the disabled service's DNS name in
  other values files. Producers buffer and drop; nothing turns red.
- **Dead config**: an env var pointing at a service whose consuming code path was removed. It
  looks like a live integration in a grep and it is not one.
- **Parked vs broken**: a commented-out generator entry with a comment is parked; without one,
  nobody can tell. Same for a values tree with no generator entry.
- **A green pod that is not working**: a worker with a static liveness probe, no readiness
  probe, and no port is invisible to every signal you have.

### Documentation debt

- Values with non-obvious numbers and no reason recorded. Ask, for each: could a new person
  change this safely? If not, it is a finding, not a nitpick — see
  `references/decision-log.md`.
- Comments that contradict the values around them. A stale comment is worse than none: it is
  actively believed. Check dates and cross-references rather than assuming currency.

## Reading a repo you did not write

An efficient order, roughly 30 minutes for a repo of this shape:

```
1. README + CODEOWNERS         what the authors think the rules are
2. projects/*.yaml             the blast-radius boundaries, stated
3. apps/*/                     what actually exists, and at which sync tier
4. charts/*/values.yaml        the contract every service is written against
5. charts/*/templates/         only the ones the values suggest are load-bearing
6. envs/*/                     every values file — this is where the truth is
7. git log --oneline -40       what changes, how often, and by whom (robot vs human)
```

Step 6 is where the time goes and where the findings are. Steps 1–5 tell you what questions
to ask of it.

Two reading habits pay off:

- **Trust the values over the README.** The README describes intent at the time it was
  written; values describe what is running.
- **Read the comments as evidence, not decoration.** In a well-kept repo they carry
  measurements, dates, and exit conditions — often the only record of why something is the way
  it is. In a poorly-kept one, their absence *is* the finding.

## Say what you did not check

A GitOps repo audit cannot see:

- the cluster (what is actually running, and what was applied by hand and never committed);
- IAM policies and role scopes behind the ARNs referenced in values;
- the contents of any image;
- whether a secret path exists in the store, or who can write to it;
- branch protection, unless you check the host separately;
- what the application code actually serves, unless you read that repo too.

State this plainly. A report that lists twelve findings without naming its own boundaries
implies the rest was verified, and a clean report is more dangerous than a missing one — it
gets quoted later as evidence.

## Report shape

```markdown
## Scope
What I read, and what I could not see from this repo alone.

## Findings

### 1 — Reachable and dangerous
**F1. <one-line claim>** — `path/to/file.yaml:NN`
What is exposed / at risk. How it happens. What closes it.

### 2 — Unbounded
...

## Things done well
Name them, specifically.

## Suggested order of work
1. …
```

Include the "done well" section and be specific. It is not politeness: an audit that reads as
uniformly negative gets filed, and the tier-1 findings go with it. Naming what is working also
tells the team which patterns to copy when they fix the rest.
