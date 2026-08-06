---
name: gitops-nova
description: >-
  SOP for designing, bootstrapping, extending, and auditing an Argo CD GitOps repository —
  app-of-apps layout, AppProjects as blast-radius boundaries, ONE shared service Helm chart
  driven by per-(service, env) values, ApplicationSet generators, the three-tier sync ladder
  (auto / manual / observe-only), secrets by reference via External Secrets, digest promotion
  dev→uat→staging→prod, Gateway API exposure with default-deny routes, and the CODEOWNERS
  split that gates machinery without putting devops in front of the dev team. Use this skill
  whenever the user mentions Argo CD, ArgoCD, GitOps, app-of-apps, ApplicationSet, AppProject,
  a "deploy repo" / "manifest repo" / "k8s config repo", a Helm chart per service, sync policy,
  prune / selfHeal, External Secrets Operator, promoting an image to prod, onboarding a new
  service or a new environment onto a cluster, or says things like "ทำ gitops", "วาง structure
  repo deploy", "ArgoCD จัดโครงสร้างยังไง", "เพิ่ม service ใหม่เข้า cluster", "ขึ้น prod ยังไง",
  "review repo deploy ให้หน่อย" — including when they only ask to "just add one service",
  because where that service's values live, which sync policy it inherits, and whether its
  route is a catchall is exactly what decides whether the next bad merge is a rollback or an
  outage. Also use it to audit an existing GitOps repo for blast radius, secrets committed to
  git, unpinned versions, and admin surfaces exposed to the internet. This is about the repo
  that describes the cluster — not about writing Terraform / cloud infrastructure (a separate
  repo), not about debugging a pod that is already running, and not about the application's
  own source code.
---

# GitOps for Argo CD

Design the repository that describes a cluster, so that a wrong merge is a revert and not an
incident.

The failure this prevents is specific and common: a repo grows one Helm chart per service,
a values file per service per env that drifts, `prune: true` on everything because that was
the example in the docs, and a catchall HTTPRoute per service. It works for six months.
Then someone renames a directory and Argo CD prunes a StatefulSet, or a service ships an
ops endpoint on its main listener and it is on the internet the same afternoon. None of
those are Kubernetes problems. They are repository-design problems, and they are decided
on day one.

---

## Step 1 — Pick the mode

| Mode | Signals | Deliverable | Effort |
| ---| ---| ---| --- |
| **BOOTSTRAP** | new cluster, "set up ArgoCD", "we need a gitops repo", nothing exists yet | repo skeleton + bootstrap runbook + first service green | half a day |
| **ONBOARD** | "add service X", "add uat", "install cert-manager", repo already exists | values file + generator entry + the checks in `references/promotion.md` | 30–60 min |
| **REVIEW** | "review our deploy repo", "is this safe", an audit or a handover | findings ordered by blast radius, with fixes | 1–2 h |
| **PROMOTE** | "ship to prod", "we need a prod cluster", nonprod already works | prod project + appsets + the gating that makes prod different | half a day |

Say which mode you picked. In BOOTSTRAP, run `scripts/scaffold.py` rather than typing YAML
from memory — it emits a chart whose traps are already handled, and every one of those traps
below cost somebody a production afternoon to find.

If the repo already exists, run `scripts/audit.py` **first**, in every mode. It is thirty
seconds and it changes what you should work on: there is no point onboarding a tenth service
into a repo that has a database URI committed in plaintext.

---

## Step 2 — Every structural choice answers one question

**What can a single bad merge destroy?**

That is the axis. Argo CD's whole job is to apply git to a cluster continuously and without
asking, so the repository is not documentation — it is a loaded actuator. Directory layout,
AppProject scope, sync policy, and CODEOWNERS are four different mechanisms that all exist
to bound the same thing, and they compose:

| Mechanism | Bounds | Failure it stops |
| ---| ---| --- |
| **AppProject** | which repos may be sources, which namespaces may be destinations | an app in the wrong namespace, a chart from an unvetted repo |
| **Sync policy** | whether git applies at all, and whether it may delete | a moved directory pruning live workloads |
| **CODEOWNERS** | who may merge which path | a dev editing prod values, or devops becoming the bottleneck on a dashboard |
| **Directory layout** | what a single PR can touch at once | one edit that quietly changes every environment |

When a design decision feels arbitrary, ask which of these four it is buying, and how much.
If it buys none of them, it is preference, and preference should lose to whatever is simpler
to read.

---

## The layout

```
bootstrap/
  argocd/          Argo CD's OWN install values — helm install by hand once, then self-managed
  <cluster>/       root Application per cluster (apply once by hand, then never again)
projects/          AppProject per trust tier: nonprod (broad) + prod (locked)
apps/
  <tier>/          the app-of-apps leaves: ApplicationSets + one-off Applications
charts/
  <service-chart>/ THE ONE shared service chart — per-service shape lives in values
  <special>/       a chart only for workloads the shared chart genuinely cannot express
envs/
  dev|uat|staging/ dev-team self-serve via PR
  prod/            CODEOWNERS-gated
platform/          cluster-scoped things you want diffed but not applied (node pools, quotas)
observability/
  upstream/        values for upstream chart pins   (gated)
  chart/
    templates/     wiring                            (gated)
    dashboards/    ← dev self-serve
    alerts/        ← dev self-serve
```

Two things about this tree are load-bearing and everything else is taste:

**`charts/` holds one shared chart, not one per service.** A chart per service means every
fix to probes, resources, or labels is an N-way edit that will be applied to N-1 services.
Per-service shape belongs in values as a **components map** — `app`, `worker`, `mock`,
`harness` — where each entry renders one Deployment. Reach for a second chart only when the
workload's *kind* differs (a StatefulSet with PVCs is not a Deployment with a values flag).

**`envs/` is indexed by environment first, service second** (`envs/dev/services/payment/`),
not the reverse. That way `envs/prod/` is one CODEOWNERS line and one directory a reviewer
can read end to end, and CI writing a dev image tag can never touch a prod path.

Full tree, naming conventions, and the ApplicationSet generators that walk it are in
`references/layout.md`.

---

## The three-tier sync ladder

Sync policy is a risk dial, not a default. Three settings, and the gap between the second
and third is the one people miss:

| Tier | Policy | Use for | Why |
| ---| ---| ---| --- |
| **auto** | `automated: {prune: true, selfHeal: true}` | nonprod app workloads | recreatable in minutes; drift should not survive |
| **manual** | `syncOptions` only, **no `automated:`** | prod | a reviewed merge and a deliberate sync are two different acts of consent |
| **observe-only** | **no `automated:` block at all**, plus nothing that applies | cluster-scoped or shared-tenancy objects | git becomes a live diff, not an actuator |

`automated: {prune: false, selfHeal: false}` is **not** observe-only. It still applies git to
the cluster on every commit — it just will not delete or re-converge. For a node pool whose
requirement change means a fleet-wide node replacement, that difference is the whole ballgame:
the apply belongs to a human watching it, not to a merge.

Promotion up the ladder is a deliberate change of its own, never a drive-by:
`observe-only → automated{prune:false,selfHeal:false} → +prune` after one clean drift cycle.

Sync options, `ServerSideApply`, and the resource-tracking gotcha that makes hand-created
objects read `OutOfSync` forever are in `references/sync-policy.md`.

---

## Rules that make the repo survivable

Reasons in parentheses — the reason tells you when a rule may flex.

1. **Secrets are references, never values.** A values file may carry a *path*
   (`nova/dev/payment`) and *key names*; the operator syncs the values in-cluster. (Git is
   replicated to every laptop and every CI runner forever, and `git rm` does not unpublish.
   A path is useless without the IAM role that can read it.)

2. **The store a workload reads through is scoped to that workload's paths**, not the
   cluster's shared account-wide store. (Otherwise every namespace that can create an
   ExternalSecret can read every other team's credentials, and the blast radius of one
   compromised manifest is the entire secret store.)

3. **Pin every version, everywhere** — chart versions, image tags, AMI aliases. Never
   `targetRevision: HEAD` on an upstream chart, never `:latest`. (An unpinned upstream chart
   turns someone else's release into your unreviewed deploy; you will find out from an
   alert.)

4. **Promote a digest, never a rebuild.** The tag that soaked on staging is retagged for
   prod, not rebuilt from the same commit. (A rebuild is a different artifact — different
   base-image patches, different transitive deps. Testing artifact A and shipping artifact B
   makes the soak meaningless.)

5. **CI writes exactly one field.** The service repo's pipeline commits `image.tag` into
   `envs/<env>/services/<svc>/values.yaml` and touches nothing else. (Anything more and the
   deploy repo stops being reviewable — you can no longer tell a human decision from a robot
   one in the log.)

6. **Gate machinery, not content.** CODEOWNERS covers `charts/`, `apps/`, `projects/`,
   `bootstrap/`, `envs/prod/`. Leave dashboards, alert rules, and nonprod values unowned.
   (A devops bottleneck on content is exactly how dashboards end up hand-clicked in the UI
   and alert rules end up living in one person's browser — the failure the repo exists to
   prevent.)

7. **Routes are allowlists, not catchalls.** List the paths the edge may forward. (A
   catchall publishes every path the process serves, including the ops and admin plane it
   only ever expected on localhost. The pod's own authorization is then the only thing left,
   and it was written assuming it was not on the internet.)

8. **East-west traffic uses the in-cluster address**, never the service's own public
   hostname. (The public name hairpins pod → NAT → CDN → load balancer → edge → back into the
   same cluster: slower, billed, and it starts returning 401 the day edge auth is enabled —
   for a call that never needed to leave the cluster.)

9. **An unsafe render must fail loudly.** Where a values combination would silently produce
   an unauthenticated path or a nondeterministic policy binding, `fail` in the template. (A
   Helm error is loud and lands on the author; a quietly re-opened path is discovered by
   whoever finds it first, and that might not be you.)

10. **Liveness is static; readiness is real.** Liveness answers "is this process wedged",
    readiness answers "can it serve right now". (Point liveness at a dependency check and the
    first broker blip CrashLoops the entire fleet, turning a degraded system into a down one.)

11. **Every non-obvious value carries its reason, and its exit condition.** Not what the line
    does — what breaks if it changes, what was measured, and what has to become true before
    it can be deleted. (Six months later the values file is the only surviving record of the
    decision; the ticket is closed, the Slack thread is gone, and the person left. See
    `references/decision-log.md` — this is the cheapest habit here and the highest-leverage.)

12. **Write down what is deliberately not wired.** A parked environment, a disabled backend,
    a service with no image yet — say so in the file, with the precondition for turning it on.
    (An empty directory and a deliberately-empty directory look identical, so the next person
    either "fixes" a decision or inherits a mystery.)

---

## Mode workflows

### BOOTSTRAP

```
1. Confirm the boundaries      → clusters, envs, trust tiers, who reviews prod
2. Scaffold                    → scripts/scaffold.py (chart traps pre-handled)
3. Bootstrap Argo CD by hand   → references/bootstrap.md (two-step; nothing installs the installer)
4. Give it the repo credential → read-only deploy key, out of band, never committed
5. Apply the root Application  → once, by hand; everything else flows from git
6. Land ONE service end to end → green before adding a second
7. Write the repo README       → the layout and the rules, so the next person inherits intent
```

Step 6 is the one people skip. A repo with nine half-wired services and no green one is
harder to debug than an empty repo, because every failure has several plausible causes.

### ONBOARD

```
1. Values file first           → envs/<env>/services/<svc>/values.yaml
2. Then the generator entry    → a generator pointing at a missing file renders a broken app
3. Seed the secret path        → before merge; an unseeded ExternalSecret is a red app forever
4. Pin a real image tag        → an empty tag renders `repo:` and fails as InvalidImageName
5. Decide exposure explicitly  → default is no route; a route needs a paths allowlist
6. Decide scrape explicitly    → opt out with a comment naming what is missing
```

Order matters: values file, *then* generator. The reverse produces a red application in the
UI that looks like a platform fault and is really a missing file.

### REVIEW

Run `scripts/audit.py`, then read `references/review.md` for what the script cannot decide.
Report findings **ordered by blast radius**, not by count or by file:

```
1. Reachable and dangerous     → admin surface on the internet, credentials in git
2. Unbounded                   → wildcard project sources, prune on shared cluster-scoped objects
3. Silently wrong              → disabled backend with a live consumer, exempt-path bypass
4. Will bite later             → unpinned versions, missing resources, undocumented decisions
```

State what you did **not** check. A gitops repo audit cannot see the cluster, the IAM
policies, or what is actually inside an image — say so plainly rather than letting a clean
report imply a clean system.

### PROMOTE

Prod is not "nonprod with different values". What differs is listed in
`references/promotion.md`; the short version is that prod gets its own AppProject with an
explicit source list and no wildcards, its own Argo CD instance where possible, manual sync,
CODEOWNERS on every path, and versions promoted only after they soak.

The strongest control is the cheapest one: **if dev accounts do not exist on the prod Argo CD
instance, prod is out of reach by deployment rather than by RBAC.** RBAC is a policy you must
keep correct; a missing account is not.

---

## Scripts

### `scripts/audit.py` — static audit of a GitOps repo

```bash
python3 scripts/audit.py /path/to/gitops-repo              # human-readable, ordered by severity
python3 scripts/audit.py /path/to/repo --format json       # for CI
python3 scripts/audit.py /path/to/repo --fail-on high      # exit 1 — use as a merge gate
```

Checks what is mechanically decidable from the files alone: credentials committed as values,
unpinned charts and images, `prune` on cluster-scoped paths, catchall public routes,
JWT-exempt paths that bypass their own allowlist, probes on portless components, workloads
with no resource requests, generator entries whose values file does not exist, project source
allowlists that are wildcards, apps sourcing repos their project forbids, duplicate hostnames,
and east-west env vars pointing at the repo's own public hostnames.

It cannot see your cluster, so it is a floor and not a ceiling — `references/review.md` covers
the judgment half.

### `scripts/scaffold.py` — repo skeleton with the traps pre-handled

```bash
python3 scripts/scaffold.py --out ./my-gitops --project acme \
  --repo git@github.com:acme/acme-gitops.git \
  --envs dev,uat,staging,prod --services api,worker

python3 scripts/scaffold.py --out ./my-gitops --project acme --repo ... --minimal   # dev only
```

Emits bootstrap values + root apps, AppProjects, appsets, CODEOWNERS, a README, and the shared
service chart — with the `kindIs "bool"` guard, per-component resource fallback, port-driven
Service/probes/scrape, and the exempt-path `fail` guard already written. Then edit the values;
do not re-derive the templates.

---

## Reference map — what to read when

| File | Read it when |
| ---| --- |
| `references/layout.md` | laying out the tree, or writing ApplicationSet generators and the multi-source `$values` pattern |
| `references/bootstrap.md` | day 0 — installing Argo CD, the repo credential, self-management, root apps, projects |
| `references/service-chart.md` | writing or fixing the shared chart; the full Helm trap list |
| `references/sync-policy.md` | choosing prune/selfHeal, `ServerSideApply`, or explaining a permanent `OutOfSync` |
| `references/secrets.md` | wiring External Secrets, scoping a store, deciding what may stay in git |
| `references/promotion.md` | the CI contract, digest promotion, parking an env, what makes prod different |
| `references/exposure.md` | routes, edge auth, path allowlists, east-west, the exempt-path bypass |
| `references/observability.md` | the machinery/content split, scrape opt-in, what makes an alert worth paging |
| `references/review.md` | REVIEW mode — the judgment checks the script cannot make |
| `references/decision-log.md` | writing the comments; the convention that makes values files survive their authors |
| `examples/review-report.md` | you want a finished audit as a reference for the deliverable's shape |

---

## Common failure modes

| Symptom | Fix |
| ---| --- |
| a chart per service, fixes applied N-1 times | one shared chart, per-service shape in a components map |
| a moved directory deleted live workloads | sync ladder — `prune` is for recreatable nonprod workloads only |
| node pool / CRD changes applied by a merge | observe-only: no `automated:` block at all, not `automated:{false,false}` |
| every object reads `OutOfSync` and diffs are empty | resource-tracking label on hand-created objects — sync once; see `references/sync-policy.md` |
| an ops endpoint turned out to be public | route allowlist, not catchall — `references/exposure.md` |
| a webhook exempted from auth also bypassed the allowlist | exempt paths must be *covered by* the allowlist; segment semantics, not string prefix |
| worker pods are BestEffort and get evicted first | resource default must fall back **per component**, not just at the top level |
| `enabled: false` in values did nothing | Helm's `default` treats `false` as empty — guard with `kindIs "bool"` |
| a worker CrashLoops on probes it never serves | port presence drives Service + probes; portless components get neither |
| the whole fleet CrashLooped when the broker blipped | liveness static, readiness real |
| spans/metrics vanish with no error | a disabled backend whose consumer still points at it — disable both halves in one PR |
| red apps nobody can explain | generator entry landed before the values file, or the secret path was never seeded |
| prod values drifted from staging and nobody noticed | promote the digest, not a rebuild; diff prod against staging values in the promotion PR |
| a values file nobody dares change | rule 11 — record the reason and the exit condition when you write the line, not later |
