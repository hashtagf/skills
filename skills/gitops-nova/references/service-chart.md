# The one shared service chart

Contents:
- [Why one chart](#why-one-chart)
- [The components model](#the-components-model)
- [Values contract](#values-contract)
- [Helm traps that cost real time](#helm-traps-that-cost-real-time)
- [Resources and QoS](#resources-and-qos)
- [Probes](#probes)
- [Scheduling constraints](#scheduling-constraints)
- [Per-component images](#per-component-images)
- [Making an unsafe render fail](#making-an-unsafe-render-fail)
- [When to write a second chart](#when-to-write-a-second-chart)

---

## Why one chart

A chart per service looks like separation of concerns and behaves like copy-paste. Every
improvement — a probe default, a label, a resource floor, a security context — becomes an
N-way edit, and the edit will be applied to N-1 services because someone will be on leave.
Six months in, the charts have diverged in ways nobody chose, and "what does our standard
deployment look like" has no answer.

One chart inverts that: a fix lands once and every service gets it on next sync. The cost is
that the chart must express real per-service variation without becoming a maze of `if`. The
components map is how it does that.

The rule for keeping it honest: **if a values key exists to serve exactly one service, it is
probably a sign that service needs its own chart** — or that the key is describing something
that belongs in the service's own image.

## The components model

One entry per running unit of the service. Most services have exactly one.

```yaml
components:
  app:                        # the primary component — keeps the bare release name
    replicas: 1
    port: 8080
    healthPath: /healthz
    readyPath: /readyz
    env: {LOG_LEVEL: debug}
  worker:                     # no port -> no Service, no probes, no scrape
    replicas: 1
    env: {MODE: worker}
  mock:                       # dev-only stand-in, its own image, no service credentials
    port: 9090
    healthPath: /healthz
    secrets: false
    image: {repository: ghcr.io/acme/mock, tag: sandbox}
```

Each entry renders one Deployment. Three derived behaviours make the map do real work rather
than just loop:

| Values state | What renders | Why it is derived rather than flagged |
| ---| ---| --- |
| `port` present | Deployment + Service + scrape annotation | a component with no listener has no Service to make and nothing to scrape — a flag would just let you configure a contradiction |
| `healthPath` present | liveness + readiness probes | probes need a port; a component with neither serves no HTTP and probing it CrashLoops |
| `secrets: false` | the synced Secret is left out of that container | a component that is not the service has no business holding the service's credentials |

Deriving from `port` rather than a separate `service.enabled` means one fewer way for values
to describe an impossible object. That is the general principle for this chart: **derive what
you can, flag only what is a genuine choice.**

The trade-off to state out loud: a background worker with no port is invisible to both
readiness alerting and metrics scraping. That is a real gap and the fix is a port in the
worker's own code, not a values flag. Say that in the values comment where the worker is
declared, or it reads as an oversight.

## Values contract

```yaml
image:
  repository: ""          # registry path
  tag: ""                 # <env>-<sha> from CI, or the promoted release tag
  pullSecret: registry-pull

defaultResources:         # a DEFAULT, not an empty map — see below
  requests: {cpu: 10m, memory: 64Mi}
  limits:   {memory: 256Mi}

nodeSelector: {}          # service-wide; a component may override
tolerations: []

components:
  app: {replicas: 1, port: 8080, healthPath: /healthz, readyPath: /readyz, env: {}}

env: {}                   # shared by every component, merged under per-component env

secrets:
  enabled: false
  storeRef: <scoped-store>
  path: ""                # e.g. acme/dev/payment
  keys: []                # key NAMES only, never values

route:
  enabled: false
  gatewayName: <gateway>
  gatewayNamespace: <ns>
  hostnames: []
  paths: []               # empty = catchall. Set it.
  jwtExemptPaths: []
  jwt:
    enabled: false
    jwksURI: ""
    claimToHeaders: []
```

Every default here should carry a comment explaining what breaks if it changes. The chart's
`values.yaml` is read far more often than its templates, and it is where a new service author
learns the system.

## Helm traps that cost real time

### `default` treats `false` as empty

```gotemplate
{{- if default true $m.enabled }}   {{/* WRONG: enabled:false is silently ignored */}}
```

Helm's `default` returns the fallback for any *empty* value, and `false` is empty. An explicit
`enabled: false` in a values file therefore does nothing, silently — the worst possible
failure shape for a flag whose whole job is to turn something off.

```gotemplate
{{- $m := $c.metrics | default dict }}
{{- $off := and (kindIs "bool" $m.enabled) (not $m.enabled) }}
{{- if and $c.port (not $off) }}
```

`kindIs "bool"` distinguishes "explicitly false" from "absent". Use `default` freely for maps,
lists, and strings — the trap is bools (and `0`).

### Values deep-merge; an absent key does not fall back to a sibling

```yaml
components:
  app:
    healthPath: /healthz
    # readyPath omitted, expecting it to follow healthPath
```

It does not. Values files merge *over chart defaults*, so an absent `readyPath` leaves the
chart's `/readyz` standing — and the pod never goes Ready because it serves no `/readyz`.
Either make the template do the fallback explicitly (`$c.readyPath | default $c.healthPath`)
or require the key. Do one of them deliberately; the bug is quiet either way.

### A per-component default must actually be per-component

```gotemplate
resources: {{- ($c.resources | default $.Values.defaultResources) | toYaml | nindent 12 }}
```

If the fallback only exists on the top-level `app` key, every other component ships with no
requests or limits at all. Measured on a real fleet: 13 of 15 containers were BestEffort
because the default reached only one component per service.

### Range scoping

Inside `{{- range $name, $c := .Values.components }}` the dot is rebound. `.Values` is gone;
use `$.Values`. Every helper call needs `$` too — `include "chart.name" $`, not
`include "chart.name" .`. This produces empty names rather than an error, so it renders and
then fails at apply time with a message about an invalid resource name.

### Large CRDs and client-side apply

Charts that bundle sizeable CRDs blow the 256KB `last-applied-configuration` annotation limit.
Use `syncOptions: [ServerSideApply=true]` on those Applications. The error you get otherwise
mentions annotation size, not CRDs, and is easy to misread as an etcd problem.

## Resources and QoS

`resources: {}` is not neutral. It produces **BestEffort** QoS, and that has two consequences
on any cluster you share:

- BestEffort pods are the **first** thing the kubelet evicts under node pressure. Your
  money-path service dies before the observability stack that was supposed to report it.
- No memory limit means one leak takes the whole node, including other teams' pods. The
  offending container is OOMKilled by the kernel and writes nothing on the way out; the only
  record is a Kubernetes event that ages out.

Set a real default and size it from measurement, not intuition:

```yaml
defaultResources:
  requests: {cpu: 10m, memory: 64Mi}    # close to measured idle, so the scheduler packs honestly
  limits:   {memory: 256Mi}             # wide, because a limit sized to idle OOMKills on first load
```

**No CPU limit**, deliberately. CPU is compressible: the kernel throttles rather than kills,
so a CPU limit turns "slow" into something that looks exactly like a hang — and it does so
under load, when you can least afford an ambiguous symptom. Memory is not compressible, so its
limit is doing real work.

Override per service once that service has load numbers worth using, and say in the comment
what the numbers were. A runtime with a different floor (a JS server against a Go binary) will
need it immediately; that is a fact about the runtime and belongs in the values file with the
measurement next to it.

## Probes

**Liveness answers "is this process wedged".** It must be static — a handler that returns 200
without touching anything external. Point it at a dependency check and the first broker or
database blip CrashLoops every replica of every service at once, converting a degraded system
into a down one, right when the dependency is already struggling.

**Readiness answers "can this serve right now".** It should ping the dependencies. A pod that
cannot reach its database should leave the Service endpoints and stop receiving traffic — that
is the entire point, and a static readiness probe is a wasted opportunity that hides real
outages behind green pods.

Two consequences for the chart:

- `healthPath` and `readyPath` are separate keys with separate meanings; do not collapse them.
- If a service only serves one of the two, say which in the values comment and point both keys
  at it knowingly. `readyPath: /healthz  # service serves no /readyz — chart default 404s`
  is a fine line; discovering it from 53 restarts is not.

Probes are rendered **only** when a `healthPath` exists, and they need a port. A worker with
probes wired to a port it never opens is a guaranteed CrashLoopBackOff that looks like an
application bug.

## Scheduling constraints

Keep `nodeSelector` and `tolerations` empty by default, overridable per service and per
component. Empty defaults mean rendering is byte-identical for every service that does not
use them — which is what makes adding the feature safe.

Per-component override before service-wide is the useful precedence: pinning *one* component
to an architecture is the whole point of a canary. The app moves; its worker and mock stay.

Prefer well-known labels (`kubernetes.io/arch`) over custom pool labels. The kubelet sets them
on every node without your autoscaler's help, so the selector keeps meaning the same thing if
the pool is renamed, replaced, or the workload moves to a managed node group.

Before pinning to a non-default architecture, verify the image is actually a multi-platform
index. A single-arch image does **not** fail to schedule — it schedules and then CrashLoops on
`exec format error`, which reads like a corrupt binary.

## Per-component images

A component may run a different image than the service:

```yaml
components:
  mock:
    image: {repository: ghcr.io/acme/nova-mock, tag: sandbox}
```

Each field falls back to the top-level image when omitted. Reach for it only when the
component **is not the service** — a dev-only mock, a test harness. A component that *is* the
service must share the promoted digest, or the artifact you tested is not the artifact you
shipped.

Two things follow, and both belong in a comment where the key is used:

- CI bumps only the **top-level** `image.tag`. A component image is pinned by hand, so it will
  quietly go stale unless someone owns it.
- A binary that fabricates data (a mock wallet, a seeded balance provider) must live in its own
  image, never bundled into the service image. Bundled, it is one `command:` override away from
  running in production.

## Making an unsafe render fail

Where a values combination would produce something silently insecure, refuse to render:

```gotemplate
{{- if not $covered }}
{{- fail (printf "route.jwtExemptPaths entry %q is not covered by any route.paths prefix (%v). The policy-free route would carry it around the allowlist, unauthenticated. Add a covering prefix, or drop the exempt path." $exempt $.Values.route.paths) }}
{{- end }}
```

The reasoning generalises: **a Helm error is loud and lands on the person who caused it; a
quietly re-opened path is found by whoever finds it first.** Filtering the bad entry silently
would be worse than failing — an auth-exempt webhook would start 401-ing with nothing pointing
at the cause.

Good candidates for a `fail` guard:

- an exempt path not covered by the route allowlist (bypasses the allowlist entirely);
- an exempt path exactly **equal** to an allowlisted prefix (two routes carry the same prefix,
  one with the policy and one without, and Gateway API breaks that tie on route creation
  timestamp — whether auth applies becomes nondeterministic);
- `secrets.enabled: true` with an empty `secrets.path`;
- a route enabled with no hostnames;
- an image tag that is empty or `latest`.

Keep the message long and specific. It is read exactly once, by someone who does not yet know
what they did, and every word you save costs them a search.

## When to write a second chart

- **the kind differs** — StatefulSet + PVCs, DaemonSet, CronJob-only;
- **the lifecycle differs** — something that exists once per cluster, not per env;
- **the shared chart would need a flag only this workload uses.**

Write the reason at the top of the new chart. "Why is this not the shared chart" is the first
question every reader will have, and answering it prevents someone from helpfully merging the
two back together.
