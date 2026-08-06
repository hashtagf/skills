# Secrets — references, never values

Contents:
- [The rule and why it is absolute](#the-rule-and-why-it-is-absolute)
- [The shape](#the-shape)
- [Scope the store, not just the secret](#scope-the-store-not-just-the-secret)
- [Reusing a controller you do not own](#reusing-a-controller-you-do-not-own)
- [Path conventions](#path-conventions)
- [What may stay in git](#what-may-stay-in-git)
- [Seeding, and the failure when you forget](#seeding-and-the-failure-when-you-forget)
- [Rotation](#rotation)

---

## The rule and why it is absolute

A values file may carry a secret's **path** and its **key names**. Never a value.

The reason is not that git is insecure — it is that git is *permanent and replicated*. The
repo is on every developer laptop, in every CI runner's cache, in every fork, and in the
history after you delete the line. `git rm` does not unpublish; rewriting history does not
reach the clones. A credential committed once is rotated, not removed.

A path, by contrast, is useless without the IAM role that can read it. Publishing
`acme/dev/payment` tells an attacker a name they could have guessed.

## The shape

An operator (External Secrets Operator, or an equivalent) reads the value from your secret
manager at runtime and projects it into a Kubernetes Secret. The chart renders the
ExternalSecret; the values file names the path and the keys.

```yaml
# values
secrets:
  enabled: true
  storeRef: acme-scoped-store
  path: acme/dev/payment
  keys: [MONGO_URI, REDIS_PASSWORD, RABBIT_URI]
```

```gotemplate
{{- if .Values.secrets.enabled }}
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: {{ include "chart.name" . }}
spec:
  refreshInterval: 1m
  secretStoreRef:
    kind: ClusterSecretStore
    name: {{ .Values.secrets.storeRef }}
  target:
    name: {{ include "chart.name" . }}-secrets
  data:
    {{- range .Values.secrets.keys }}
    - secretKey: {{ . }}
      remoteRef:
        key: {{ $.Values.secrets.path }}
        property: {{ . }}
    {{- end }}
{{- end }}
```

The container mounts it whole with `envFrom.secretRef`. That is all-or-nothing per container,
which is why a component that should not hold the service's credentials needs an explicit
opt-out (`secrets: false`) rather than a subset.

Check which API version the **running** operator serves before writing `v1beta1`. Operators
in this space have moved through `v1alpha1` → `v1beta1` → `v1` and a manifest for a version
the CRD does not serve fails at apply with a message about an unknown kind, which reads like
the operator is missing.

## Scope the store, not just the secret

The store is where least privilege actually lives. A cluster-wide store bound to an
account-wide read role means **any namespace that can create an ExternalSecret can read every
team's credentials** — including a namespace a dev self-serves into.

Create your own store bound to a role scoped to your paths:

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata: {name: acme-scoped-store}
spec:
  provider:
    aws:
      service: SecretsManager
      region: ap-southeast-1
      role: arn:aws:iam::<acct>:role/acme-external-secrets-nonprod   # acme/{dev,uat,staging}/* only
      auth:
        jwt:
          serviceAccountRef: {name: external-secrets, namespace: external-secrets}
```

Then the failure mode of a wrong `secrets.path` is a denied read, not a cross-team leak.

## Reusing a controller you do not own

On a shared cluster the operator often already exists, installed by a platform team and
serving other workloads. **Do not install a second release.** Two ESO releases fight over the
same CRDs and webhooks and break every team's secret sync — a much larger outage than the one
you were avoiding.

Bind to the existing controller instead. Most implementations let a *store* name a different
role while authenticating with the **controller's** ServiceAccount token, so you get your own
scoped role without creating a ServiceAccount or touching the shared one's role annotation.
That annotation is the tempting shortcut and it is destructive: changing it re-scopes every
other team's secret access at once.

Write both facts in a comment on the store manifest — that you are reusing their controller,
and that you must never touch their SA. The next person's instinct will be to "fix" the
missing install.

## Path conventions

```
<org>/<env>/<service>            acme/dev/payment
<org>/<shared-tier>/<thing>      acme/obs/grafana
```

Two properties make this worth the rigidity:

- **It maps to an IAM policy as a prefix.** `acme/dev/*` is one statement.
- **It separates who may write.** A dev-team policy may write `acme/{dev,uat,staging}/*` and
  not `acme/obs/*` or `acme/prod/*`. Alert routing and admin passwords stay devops'.

When a shared credential is needed by two services, resist copying it into both paths. Copies
drift and rotation misses one. Give each service its **own** account on the underlying system
with permissions covering only what it uses, and store those under each service's own path.
The broker admin account is not a service credential; no pod should hold it.

## What may stay in git

Not everything in a values file is a secret. The test is: **does this string, on its own,
grant access?**

| Stays in git | Goes in the secret manager |
| ---| --- |
| broker/broker-list hostnames on a private network | any URI carrying `user:pass@` |
| database *name* | database connection string |
| bucket names, region, role ARNs | access keys |
| public base URLs, hostnames | signing keys, PEMs, JWT secrets |
| secret key *names* | secret values |

Keeping non-secrets in git is a real benefit, not a compromise: they are reviewable, diffable,
and greppable. A broker hostname hidden in a secret is an outage nobody can debug from the
repo. Say so in the comment when you make the call — `# not a secret: hostnames carry no
credential and the listener is reachable only from this cluster's SG` — because the next
reader will otherwise assume it was an oversight.

The awkward case is a URI that mixes both (`mongodb+srv://user:pass@host/db`). The operator
cannot slice a URI, so the whole string is a secret, and the database name inside it becomes
invisible to the repo. If your service takes the DB name as a separate variable, use it — a
per-env DB name in git is worth more than the tidiness of one connection string.

## Seeding, and the failure when you forget

An ExternalSecret whose path does not exist does not fail gracefully. It syncs nothing, the
target Secret is never created, and every pod that mounts it sits in
`CreateContainerConfigError` — which looks like an image or a chart problem, not a missing
secret.

So: **seed the path before merging the values file.** Make it a line in the onboarding
checklist, and when an environment is deliberately parked because its secrets were never
seeded, write that in the generator comment. A parked env and a broken env look identical
from the UI.

Note the all-or-nothing behaviour too: one missing *key* inside an otherwise-valid path fails
the whole sync, not just that key. Adding a key to `secrets.keys` before it exists in the
store takes the running service down at next refresh.

## Rotation

Rotation only works end to end if you know what caches the value:

- the operator re-reads on `refreshInterval` and updates the Kubernetes Secret;
- a container that read it via `envFrom` at start **does not** see the new value — env vars
  are fixed at process start. Something must restart the pod;
- an application that caches the credential in memory after connecting needs its own flush,
  and if that flush is an HTTP endpoint, that endpoint is now a security-relevant control
  surface. Keep it off the public route.

Write the rotation path down next to the keys — which restart, which endpoint, in what order.
A rotation runbook nobody wrote is a rotation nobody performs.
