# Observability in the GitOps repo

Contents:
- [Machinery vs content](#machinery-vs-content)
- [One stack for the nonprod environments](#one-stack-for-the-nonprod-environments)
- [Its own namespace](#its-own-namespace)
- [Scrape: default on, opt out with a reason](#scrape-default-on-opt-out-with-a-reason)
- [Alerts that deserve to page](#alerts-that-deserve-to-page)
- [Dashboards belong in git](#dashboards-belong-in-git)
- [Disabling half a pipeline](#disabling-half-a-pipeline)
- [Managed dependencies need exporters](#managed-dependencies-need-exporters)

---

## Machinery vs content

Two different things live here and they have different owners:

| | Path | Owner | Changes |
| ---| ---| ---| --- |
| **machinery** | `observability/upstream/*.yaml`, `observability/chart/{Chart,values}.yaml`, `chart/templates/` | devops (CODEOWNERS) | rare, risky |
| **content** | `observability/chart/dashboards/`, `chart/alerts/` | anyone (unowned) | constant, cheap |

Split them so a dev adding a dashboard never touches a chart pin, and a chart bump never risks
someone's content.

The unowned half is a decision that will look like an oversight, so write the reason in
CODEOWNERS itself: a devops review on every dashboard reliably produces dashboards that live in
the monitoring UI instead of in git — which is the exact failure the repo exists to prevent.

Content must live **inside** the chart directory (`chart/dashboards/`, not `../dashboards/`)
because Helm's `.Files.Glob` cannot read above the chart root. That constraint is why the
ownership split is expressed as file-level CODEOWNERS entries rather than as separate
directories.

## One stack for the nonprod environments

One stack serving dev + uat + staging, with series told apart by an `env` label the collector
stamps from the namespace. Three separate stacks triple the cost of answering the same question
and make cross-environment comparison impossible — which is most of what you want the stack for
("is this slow in staging too?").

Production is the exception: its stack should be separate, because the thing that tells you
prod is broken should not share a failure domain with nonprod.

## Its own namespace

The stack goes in its own namespace (`obs`), not inside `dev`. Monitoring must survive whatever
breaks an environment namespace — the thing that tells you `dev` is broken cannot live inside
`dev`. Add the namespace to the AppProject destinations and say why in a comment; it is the
kind of line someone tidies away.

Its secrets belong under a **separate path prefix** too (`acme/obs/*`, not `acme/dev/*`), so
that the dev-team write policy cannot reach the alert routing or the admin password. Alert
destinations are a security control: whoever can change them can silence you.

## Scrape: default on, opt out with a reason

Default **on** for any component that has a port. Rationale: a metric nobody scrapes is
invisible, and requiring an opt-in means every new service is unmonitored until someone
remembers. Defaulting on makes forgetting fail loudly instead of quietly.

That inverts the exposure default deliberately — for exposure, forgetting must fail *closed*;
for observability, forgetting must fail *loud*. Same principle, opposite direction: make the
forgotten case the one you will notice.

Two cases need explicit handling:

**A component with no `/metrics` handler must opt out, with a comment naming what is missing.**

```yaml
metrics:
  enabled: false   # no /metrics handler — verified: no promhttp/obs.Handler registration
                   # anywhere in the repo. Flip to true in the same PR that adds one.
```

Leaving it on creates a permanently failing target, which fires a scrape-down alert every day
until someone mutes the rule. **One un-opted-out service can disable your alerting** — that is
the real cost, not the noise.

**A component with no port cannot be scraped at all.** A background worker is therefore
invisible to both metrics and readiness alerting. The fix is a port in the worker's own code,
not a values flag. Say that in the comment where the worker is declared, or it reads as a
configuration mistake rather than a known gap with a named owner.

## Alerts that deserve to page

Two things a rule needs before it is allowed to wake someone:

**An `action` annotation** — the first command to run. A page with no action is a dashboard
panel wearing a pager, and the recipient's only option is to escalate.

**A deliberate `noDataState`.** "No data" is not "healthy". If the pipeline stops, every rule
sees nothing at once.

- `Alerting` when absence is itself the failure — a worker's readiness series vanishing means
  the worker is gone.
- `OK` when the series legitimately does not exist yet — a counter before its first increment.

Getting this backwards is the difference between "the pipeline died and paged us" and "the
pipeline died and everything went green".

Alert coverage worth having, in rough priority:

| Layer | Catches |
| ---| --- |
| the pipeline itself | scrape down, log pipeline dead, rule evaluation failing, compaction stalled |
| workload state | pod never Ready, worker not Ready, CrashLooping, OOMKilled |
| the money path | queue backlog, DLQ not empty, outbox backlog, dedup store unavailable |
| the edge | upstream unreachable, 5xx rate |
| managed dependencies | broker publishers blocked, consumer lag, cache evictions, disk headroom |

The first row is the one teams skip, and it is the one that makes every other row trustworthy.
An alerting stack with no alerts about itself is a stack that fails silently in exactly the way
that matters.

The second row is worth a specific note: **a green pod is not a working pod.** A worker that
stopped consuming behind a passing liveness probe is the classic silent outage, and catching it
needs workload-state metrics plus a readiness probe that actually checks the consumer.

## Dashboards belong in git

Provision dashboards from files and turn UI editing **off** (`allowUiUpdates: false`). Editing
in the UI then does nothing permanent — the next reload restores the file.

That is intentional and worth explaining to the team, because it will feel obstructive the
first time: it keeps git and the screen in agreement, instead of leaving everyone to guess
which one is real. The workflow is: build in the UI, export, commit.

Use the export-for-sharing form, which strips the instance-specific datasource IDs. A dashboard
exported the ordinary way carries UIDs from the instance it was built on and renders empty
elsewhere.

## Disabling half a pipeline

If a backend is disabled while its producers still point at it, the producers do not fail
loudly — they buffer and drop. A trace exporter with no collector behind the name resolves
nothing and logs a resolver error every few seconds, forever, while spans go on the floor.

So: **disable both halves in one PR, or neither.** And when you disable something to save
money, write the re-enable condition in the same comment — "turn this back on in the PR that
adds an exporter to a service, not before" — because the measurement that justified disabling
("zero traces") stops being true the moment someone wires a producer, and nobody re-checks a
decision whose reason was not written down.

## Managed dependencies need exporters

Managed services usually publish either nothing to Prometheus or the wrong things:

- **Cache / in-memory store**: often publishes nothing; the cloud metrics omit hit/miss ratio,
  evictions, and blocked clients — the numbers that answer "is the cache working".
- **Broker**: per-queue depth is frequently absent from cloud metrics (dimensions are
  broker-level only), and it is the single most useful number you can have.
- **Log/stream platform**: consumer lag lives in the consumer group's own offsets, not in a
  broker metric, so a JMX-style exporter will not give it to you. An ordinary client connection
  will.

Run one small exporter per dependency, label them so the collector can discover them, and note
in the values **why** each exists — specifically, what the cloud provider's own metrics do not
give you. That comment is what stops someone from deleting the exporter as redundant.

Cloud-metric exporters are the one metered part of the stack. Enumerate the metrics you want
rather than enabling namespace-wide discovery, put the cost reasoning in a comment at the top
of the config, and pick a scrape interval matched to the decision the metric supports — average
latency does not need 60-second resolution, and 60 seconds costs five times what 300 does.
