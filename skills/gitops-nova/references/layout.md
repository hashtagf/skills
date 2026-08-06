# Repository layout and the generators that walk it

Contents:
- [The tree](#the-tree)
- [Why environment-first, not service-first](#why-environment-first-not-service-first)
- [The multi-source `$values` pattern](#the-multi-source-values-pattern)
- [ApplicationSet generators](#applicationset-generators)
- [When something needs its own Application](#when-something-needs-its-own-application)
- [Naming](#naming)
- [CODEOWNERS](#codeowners)

---

## The tree

```
CODEOWNERS
README.md                    the layout + the rules, so intent outlives its author

bootstrap/
  argocd/
    values.yaml              Argo CD's own Helm values
    README.md                the two-step install runbook (see references/bootstrap.md)
  nonprod/root-app.yaml      root Application — apply by hand once per cluster
  prod/root-app.yaml

projects/
  nonprod.yaml               AppProject: broad, dev self-serve
  prod.yaml                  AppProject: locked, explicit sources only

apps/
  nonprod/                   ← root-nonprod recurses this directory
    argocd-self.yaml         Argo CD adopts its own hand-installed release
    platform-appset.yaml     upstream platform charts, once per cluster
    services-appset.yaml     shared chart × services × envs
    gateway-config.yaml      raw manifests are fine here — no wrapper Application needed
    <one-off>-app.yaml       anything the appsets cannot express
  prod/
    platform-appset.yaml
    services-appset.yaml

charts/
  <org>-service/             THE shared service chart
    Chart.yaml
    values.yaml              documented defaults
    templates/
      _helpers.tpl
      deployment.yaml        one Deployment per components entry
      service.yaml           one Service per component that has a port
      httproute.yaml         release-level route (+ policy-free twin for exempt paths)
      component-httproute.yaml
      externalsecret.yaml
      securitypolicy.yaml    edge auth, rendered only when enabled
  <stateful-thing>/          a second chart ONLY when the workload kind differs

envs/
  dev/services/<svc>/values.yaml
  uat/services/<svc>/values.yaml
  staging/services/<svc>/values.yaml
  prod/services/<svc>/values.yaml       CODEOWNERS-gated

platform/
  <subsystem>/               cluster-scoped objects you want diffed, not applied
                             (node pools, resource quotas, priority classes)

observability/
  upstream/<chart>.yaml      pinned upstream values      (gated)
  chart/
    Chart.yaml               (gated)
    values.yaml              (gated)
    templates/               (gated)
    dashboards/<folder>/*.json   ← dev self-serve
    alerts/<service>.yaml        ← dev self-serve
```

`apps/<tier>/` is scanned with `directory: {recurse: true}` by the root Application, so
**anything** you drop there becomes managed: an ApplicationSet, an Application, or a plain
manifest (a `Gateway`, a `ClusterSecretStore`). That last case is worth knowing — a
cluster-wide singleton does not need a wrapper Application, and wrapping it only adds a layer
someone has to read through.

## Why environment-first, not service-first

`envs/<env>/services/<svc>/` beats `services/<svc>/<env>/` for three reasons that all come
from the same place:

1. **`envs/prod/` is one CODEOWNERS line.** The service-first layout needs one line per
   service and silently fails open when someone adds service number twelve.
2. **A CI job writing a dev tag physically cannot reach a prod path.** Its write path is
   `envs/dev/services/<svc>/values.yaml`, and a bug in its path construction lands in another
   dev file, not in prod.
3. **A reviewer can read `envs/prod/` end to end.** "What runs in prod" is one directory
   listing, not a `find`.

The cost is real: comparing one service across environments becomes a `diff` across
directories instead of a directory listing. That is the cheaper of the two costs, because
cross-env comparison is something you do while thinking, and prod review is something you do
under time pressure.

## The multi-source `$values` pattern

The single most useful Argo CD idiom: take the **chart** from wherever it lives, take the
**values** from your repo.

```yaml
spec:
  sources:
    - repoURL: git@github.com:acme/acme-gitops.git
      targetRevision: main
      ref: values                     # names this source; no path = nothing rendered from it
    - repoURL: https://charts.example.io
      chart: some-upstream-chart
      targetRevision: "1.4.2"         # pin
      helm:
        releaseName: some-upstream
        valueFiles:
          - "$values/platform/some-upstream.yaml"
```

Rules that save an afternoon:

- The `ref` source must have **no `path`**. Give it one and Argo CD tries to render that
  directory too, and you get a duplicate-resource error that reads like a chart bug.
- `$values` resolves against the **repo root** of the `ref` source, not the other source's
  path.
- The same repo can appear twice — once as `ref: values`, once as a chart source with a
  `path`. That is how a local chart reads a values file that lives outside the chart
  directory, which Helm's own `.Files` cannot do.
- Values files **deep-merge over** chart defaults. An *absent* key does not inherit a
  sibling's value; it leaves the chart default standing. This is the single most common
  source of "I set `readyPath` and it kept using `/readyz`".

## ApplicationSet generators

### list — a fixed set of upstream charts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata: {name: platform-nonprod, namespace: argocd}
spec:
  goTemplate: true
  generators:
    - list:
        elements:
          - name: gateway
            repoURL: oci://registry.example.io/gateway-helm
            chart: gateway-helm
            version: "v1.8.2"          # comment what SOFTWARE version this chart ships
            namespace: gateway-system
  template:
    metadata: {name: "{{ .name }}"}
    spec:
      project: nonprod
      source:
        repoURL: "{{ .repoURL }}"
        chart: "{{ .chart }}"
        targetRevision: "{{ .version }}"
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{ .namespace }}"
      syncPolicy:
        automated: {prune: true, selfHeal: true}
        syncOptions: [CreateNamespace=true, ServerSideApply=true]
```

Chart version and shipped software version are different numbers. Record both, in a comment
next to the pin — otherwise a bump PR cannot be reviewed without pulling the chart.

### matrix — services × environments

```yaml
  generators:
    - matrix:
        generators:
          - list:
              elements:
                - env: dev
                # - env: uat        # parked: secrets unseeded, no image pinned
          - list:
              elements:
                - service: api      # values must exist in EVERY enabled env
                - service: worker
  template:
    metadata: {name: "{{ .service }}-{{ .env }}"}
    spec:
      project: nonprod
      sources:
        - repoURL: git@github.com:acme/acme-gitops.git
          targetRevision: main
          ref: values
        - repoURL: git@github.com:acme/acme-gitops.git
          targetRevision: main
          path: charts/acme-service
          helm:
            releaseName: "{{ .service }}"
            valueFiles:
              - "$values/envs/{{ .env }}/services/{{ .service }}/values.yaml"
      destination:
        server: https://kubernetes.default.svc
        namespace: "{{ .env }}"
```

The matrix is a **cross product** — enabling `uat` requires a values file for *every* service
in the list. Park an environment by commenting out its list entry, not by deleting the values
tree; the values stay reviewable and re-enabling is one line.

The generated names (`<service>-<env>`) become the handle for RBAC globs, so if you write
`applications, sync, nonprod/*-dev` in a policy, keep that in lockstep with this template.
A rename here silently widens or narrows permissions.

### git directory generator — tempting, and usually wrong

Generating an Application per directory found in git makes a **deleted directory delete a
workload**, with `prune: true` doing exactly what it was told. Explicit lists are a few more
lines and they make onboarding a service a reviewable diff instead of a side effect of a
`git mv`. Use the directory generator for content that is genuinely fire-and-forget
(dashboards), not for workloads.

## When something needs its own Application

The shared chart plus an appset covers most services. Break out when:

- **the workload kind differs** — a StatefulSet with PVCs, a DaemonSet, a Job;
- **the env matrix does not apply** — a thing that exists in dev only, or once per cluster;
- **it needs a different sync tier** — see the ladder in `references/sync-policy.md`;
- **it is a raw manifest** — a `Gateway`, a `ClusterSecretStore`, a `GatewayClass`. Drop it
  in `apps/<tier>/` and let the root app's recursion pick it up.

Write the reason in a comment at the top of the file. "Why is this not in the appset" is the
first question every reader has, and answering it once costs two lines.

## Naming

| Thing | Convention | Why |
| ---| ---| --- |
| Application from appset | `<service>-<env>` | RBAC globs and the UI both sort usefully |
| Helm release | `<service>` (not `<service>-<env>`) | the namespace already carries the env; the release name ends up in every Service DNS name |
| Primary component's Service | bare release name (`payment`) | it is the name other services already dial |
| Other components' Services | `<release>-<component>` | adding a component can never rename an existing Service |
| Secret synced by ExternalSecret | `<release>-secrets` | predictable from the release name alone |
| Namespace | the environment (`dev`, `staging`, `prod`) | one destination entry per env in the AppProject |

That fourth row is the one that matters. If the primary component were suffixed too, adding a
sidecar component would rename the Service every caller resolves — a silent, cluster-wide
outage from what looked like an additive change.

## CODEOWNERS

```
# Prod values: devops approval required — dev teams self-serve dev/uat/staging.
/envs/prod/     @acme/devops

# Shared machinery affects every env.
/charts/        @acme/devops
/apps/          @acme/devops
/projects/      @acme/devops
/bootstrap/     @acme/devops
/platform/      @acme/devops

# Observability: machinery gated, CONTENT deliberately self-serve.
/observability/chart/Chart.yaml   @acme/devops
/observability/chart/values.yaml  @acme/devops
/observability/chart/templates/   @acme/devops
/observability/upstream/          @acme/devops
# dashboards/ and alerts/ are intentionally unowned — see the note below.
```

Leaving `dashboards/` and `alerts/` unowned is a decision, not an oversight, and the comment
saying so belongs in the file. The alternative — devops review on every dashboard — reliably
produces dashboards that live in the Grafana UI instead of in git, which is the exact failure
the repo exists to prevent. Write that reason down or someone will "fix" it.

CODEOWNERS does nothing without branch protection requiring review from code owners. If the
team is not there yet, say so in the file as a `TODO` naming the team that must exist first —
an unenforced CODEOWNERS reads as a control and is not one.
