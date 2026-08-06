# Sync policy — the risk dial

Contents:
- [What each field actually does](#what-each-field-actually-does)
- [The three tiers](#the-three-tiers)
- [Observe-only, precisely](#observe-only-precisely)
- [Promotion up the ladder](#promotion-up-the-ladder)
- [Sync options worth knowing](#sync-options-worth-knowing)
- [Permanent OutOfSync that is not drift](#permanent-outofsync-that-is-not-drift)
- [Diff noise](#diff-noise)

---

## What each field actually does

| Field | Effect | The failure it enables |
| ---| ---| --- |
| `automated:` present | git is applied on every detected change, no human | a merge is a deploy — including a merge nobody meant as one |
| `prune: true` | resources that vanish from git are **deleted** | a moved or renamed directory deletes live workloads |
| `selfHeal: true` | live drift is reverted to git continuously | a legitimate emergency `kubectl edit` is undone within minutes |
| `syncOptions` only | nothing applies until a human syncs | drift accumulates silently unless someone looks |

`selfHeal` deserves a second look because it is the one people enable without thinking. It is
correct for anything you would want reverted, and it actively fights you during an incident:
scale a Deployment by hand to survive a spike and it scales back. That is the right default
for nonprod and the wrong one for a cluster where the on-call's first move is `kubectl`.
The fix is not to disable it — it is to make the emergency lever a git commit.

## The three tiers

```yaml
# TIER 1 — auto. Nonprod application workloads.
syncPolicy:
  automated: {prune: true, selfHeal: true}
  syncOptions: [CreateNamespace=true]
```
Recreatable in minutes, owned by one team, blast radius is one namespace. Drift should not
survive; a wrong merge is a revert.

```yaml
# TIER 2 — manual. Production.
syncPolicy:
  syncOptions: [CreateNamespace=true]
  # no automated block — a reviewed merge and a deliberate sync are two acts of consent
```
The merge says "this change is correct". The sync says "now is the moment". Collapsing them
means every approving review is also a deploy authorisation, which is not what a reviewer
believes they are giving at 6pm on a Friday.

```yaml
# TIER 3 — observe-only. Cluster-scoped or shared-tenancy objects.
syncPolicy:
  syncOptions:
    - ApplyOutOfSyncOnly=true
    - ServerSideApply=true
  # no automated block AT ALL — this Application exists to render a diff
```
Node pools, priority classes, quotas, CRDs on a cluster you share with another team. Git
becomes a live diff so hand-applied drift becomes *visible*, without git becoming the thing
that applies it.

## Observe-only, precisely

This is the distinction that gets lost, so it is worth stating flatly:

> `automated: {prune: false, selfHeal: false}` is **not** observe-only. It still applies git
> to the cluster on every commit. It only declines to delete and to re-converge.

For a node pool, a requirement change is a fleet-wide node replacement. That belongs to a
human running `kubectl apply` while watching nodes drain — not to a merge, and not to a
merge's side effect on a Tuesday afternoon.

And on a **shared** cluster the stakes are not symmetric: `prune: true` on cluster-scoped
objects means a wrong path or a bad generator can delete the node pool carrying every running
node, including the other team's. You will not get to explain that it was a path typo.

Point the destination namespace at something the AppProject already allows (`argocd` works)
and say why in a comment: every object under that path is cluster-scoped, so the namespace is
never used — but if a namespaced resource is ever added there, it fails loudly at the project
boundary rather than landing somewhere unintended.

## Promotion up the ladder

Never a drive-by. Each step is its own change with its own reason:

```
observe-only
  → automated {prune: false, selfHeal: false}      after the diff has been clean for a while
    → + prune                                       after one full drift cycle with no surprises
```

Write the current step and the condition for the next one in the Application's own comment.
"When can we turn this on" is the question that otherwise gets answered by whoever is bravest.

## Sync options worth knowing

| Option | Use when |
| ---| --- |
| `CreateNamespace=true` | the destination namespace is not managed elsewhere. Harmless when it exists |
| `ServerSideApply=true` | large CRDs, or adopting pre-existing unowned resources. Avoids the 256KB last-applied annotation limit |
| `ApplyOutOfSyncOnly=true` | large apps — only touches resources that differ, so a sync is not a full re-apply |
| `PrunePropagationPolicy=foreground` | deletion order matters (a controller before its CRDs) |
| `Replace=true` | last resort — a full replace, which for a Service drops and recreates it |
| `RespectIgnoreDifferences=true` | you use `ignoreDifferences` and want sync to respect it too, not just the diff view |

`ServerSideApply=true` is also how you adopt resources a chart did not create — an upstream
chart that must take over CRDs installed by hand at a lower version. Client-side apply fails
on those with a message about annotation size that does not mention adoption at all.

## Permanent OutOfSync that is not drift

Symptom: every object in an Application reads `OutOfSync`, but `kubectl diff -f <path>` exits
0 and a hand-normalised comparison is empty.

Cause: Argo CD's default resource tracking stamps `app.kubernetes.io/instance` into the
**desired** manifest. Objects created earlier by `kubectl apply` do not carry it. Live differs
from desired by exactly that label, forever, on every object.

Fix: sync once. The label lands and the app goes green; after that, an `OutOfSync` means real
drift.

Two warnings that matter more than the fix:

1. **Do not run that first sync before the PR describing the objects is merged.** A sync
   applies `targetRevision`, and if `main` still holds the pre-change version you will revert
   the live fleet to it. This has bitten people the same afternoon they wired the app.
2. If you cannot sync yet, switch tracking to annotation-based
   (`application.resourceTrackingMethod: annotation` in the argocd-cm) rather than living with
   permanent red — a dashboard that is always red trains everyone to ignore it, which costs
   more than the drift it was meant to surface.

## Diff noise

Some diffs are permanent and meaningless — a mutating webhook injecting a sidecar, an
autoscaler owning `replicas`, a cloud controller writing a load balancer status. Silence them
narrowly:

```yaml
spec:
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers: ["/spec/replicas"]        # an autoscaler owns this
```

Keep each entry narrow and comment what writes the field. A broad `ignoreDifferences` is how a
real change stops being visible, and unlike a noisy diff, that failure is silent.

If you find yourself adding a third entry for the same chart, the chart is fighting a
controller — fix that instead. Ignore rules are a way of recording a known conflict, not a way
of resolving one.
