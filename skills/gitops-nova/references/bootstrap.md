# Day 0 — bootstrapping Argo CD

Contents:
- [The chicken and the egg](#the-chicken-and-the-egg)
- [1. Install by hand, once per cluster](#1-install-by-hand-once-per-cluster)
- [2. Give Argo CD the repo credential](#2-give-argo-cd-the-repo-credential)
- [3. Hand over to GitOps](#3-hand-over-to-gitops)
- [4. AppProjects](#4-appprojects)
- [5. First login, and closing it](#5-first-login-and-closing-it)
- [Argo CD's own values](#argo-cds-own-values)
- [RBAC that is a control](#rbac-that-is-a-control)
- [Bring-up order](#bring-up-order)

---

## The chicken and the egg

Argo CD installs the platform, but nothing installs Argo CD. Break it in two steps and write
both down: install by hand once, then let Argo CD adopt its own release so every later change
is a PR instead of a remembered `helm upgrade`.

The adoption works because Argo CD's self-Application uses the **same chart version and the
same values file** as the hand install, with the **same release name**. Any of those three
drifting produces a permanent diff that looks like a bug and is really a bookkeeping error.
Pin the chart version in three places and say so in each: the install command in the runbook,
a header comment in the values file, and `targetRevision` in the self-Application.

## 1. Install by hand, once per cluster

```bash
helm repo add argo https://argoproj.github.io/argo-helm && helm repo update
helm install argocd argo/argo-cd -n argocd --create-namespace \
  --version <PINNED> -f bootstrap/argocd/values.yaml
```

Check first whether the cluster already runs an Argo CD owned by another team. Two releases
fight over the same CRDs and webhooks. If one exists, the choice is to become a tenant of it
(an AppProject and an RBAC role) or to install yours in a separate namespace with
`crds.install=false` — and the first option is almost always right.

## 2. Give Argo CD the repo credential

A private repo needs a credential, and the shape of that credential is a security decision
worth making deliberately.

Use a **repo-scoped read-only deploy key**, not a personal access token. A personal token
carries one human's whole account and dies when they leave; a deploy key is scoped to one
repository, read-only, and revocable without touching anyone's access.

```bash
ssh-keygen -t ed25519 -f argocd-deploykey -N "" -C "argocd-<cluster>@<org>"

# register the PUBLIC half as a read-only deploy key
gh repo deploy-key add argocd-deploykey.pub \
  --repo <org>/<gitops-repo> --title "argocd-<cluster>-readonly"

# feed the PRIVATE half in as a Repository Secret. Prefer a file over an inline
# literal so the key never enters shell history.
kubectl -n argocd create secret generic gitops-repo \
  --from-literal=type=git \
  --from-literal=url=git@github.com:<org>/<gitops-repo>.git \
  --from-file=sshPrivateKey=argocd-deploykey
kubectl -n argocd label secret gitops-repo argocd.argoproj.io/secret-type=repository

shred -u argocd-deploykey    # or rm -P on macOS
```

The `url` must match the manifests **character for character**. Argo CD matches repository
credentials by exact URL string, so `git@github.com:org/repo.git` and
`https://github.com/org/repo.git` are two different repositories to it. Pick the SSH form,
use it everywhere, and the failure mode ("repository not accessible") never appears.

Argo CD ships GitHub's SSH host key in `argocd-ssh-known-hosts-cm`, so no extra known-hosts
setup for GitHub. Self-hosted git needs the host key added there first.

Longer term, move the private key into your secret manager and let External Secrets project
the Repository Secret — then cluster rebuild does not need a human with the key.

## 3. Hand over to GitOps

```bash
kubectl apply -f bootstrap/<cluster>/root-app.yaml
```

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: root-nonprod, namespace: argocd}
spec:
  project: nonprod
  source:
    repoURL: git@github.com:<org>/<gitops-repo>.git
    targetRevision: main
    path: apps/nonprod
    directory: {recurse: true}
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated: {prune: true, selfHeal: true}
```

The root app recurses `apps/nonprod/` and picks up the self-Application, which adopts the
release from step 1:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata: {name: argocd, namespace: argocd}
spec:
  project: nonprod
  sources:
    - repoURL: git@github.com:<org>/<gitops-repo>.git
      targetRevision: main
      ref: values
    - repoURL: https://argoproj.github.io/argo-helm
      chart: argo-cd
      targetRevision: <PINNED>          # same as the helm install
      helm:
        releaseName: argocd             # same as the helm install
        valueFiles: ["$values/bootstrap/argocd/values.yaml"]
  destination: {server: https://kubernetes.default.svc, namespace: argocd}
  syncPolicy:
    automated:
      selfHeal: true
      prune: false        # never prune Argo CD's own resources
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true   # argo-cd CRDs exceed the client-side last-applied limit
```

`prune: false` on the self-app is not caution for its own sake: if a bad render ever produces
an empty or partial manifest set, pruning would delete the controller that would otherwise
let you fix it. `selfHeal: true` still keeps its config converged. Losing the ability to
delete an obsolete Argo CD resource automatically is a cheap price.

Prune the root app's own `prune: true` mentally as well: it means **deleting a file from
`apps/<tier>/` deletes what it manages.** That is the intended behaviour, and it is also why
`platform/` (cluster-scoped things) lives outside that recursion.

## 4. AppProjects

The AppProject is the blast-radius boundary. Two tiers is the useful minimum.

```yaml
# projects/nonprod.yaml — broad, dev self-serve
spec:
  description: dev/uat/staging — dev-team self-serve
  sourceRepos:                     # exact URLs, not wildcards
    - git@github.com:<org>/<gitops-repo>.git
    - https://argoproj.github.io/argo-helm
    - https://charts.example.io
  destinations:
    - {server: https://kubernetes.default.svc, namespace: dev}
    - {server: https://kubernetes.default.svc, namespace: uat}
    - {server: https://kubernetes.default.svc, namespace: staging}
    - {server: https://kubernetes.default.svc, namespace: argocd}
    - {server: https://kubernetes.default.svc, namespace: obs}
  clusterResourceWhitelist:
    - {group: "*", kind: "*"}      # platform charts need CRDs; narrow after bring-up
```

Notes that cost time if learned the hard way:

- **List repo URLs exactly.** Argo CD's glob matching against scp-form SSH URLs
  (`git@host:org/repo.git`) is unreliable — the `:` is not a path separator — and the exact
  list is the tighter end state anyway.
- **`clusterResourceWhitelist: {"*","*"}` is a bring-up compromise, not a destination.**
  Platform charts install CRDs and ClusterRoles, so you need it on day one. Leave a `TODO`
  naming what it should narrow to, or it becomes permanent by default.
- **Namespace destinations are the real fence.** A missing namespace here fails a sync loudly
  at the project boundary, which is exactly what you want when a template renders a
  destination nobody intended.
- **Prod gets no wildcards at all** — sources added one at a time, and only after they soak
  on nonprod.

## 5. First login, and closing it

```bash
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Delete `argocd-initial-admin-secret` after first login — it is a static credential that
otherwise sits in etcd forever.

Before exposing the UI publicly at all, decide what guards it. Argo CD's built-in admin plus
a deny-by-default RBAC policy is the floor, and it is thin: the UI can sync anything the
account can reach, and it holds the repo credential. An identity-aware proxy in front (Cloudflare
Access, IAP, an OIDC gate) is the intended answer. If you go public before that lands, write
the exposure down as an accepted risk with the thing that closes it named — otherwise it is
indistinguishable from nobody having thought about it.

## Argo CD's own values

Two settings people get wrong:

```yaml
global:
  domain: argocd.example.com      # must match what the route serves

configs:
  params:
    server.insecure: true         # TLS terminates at the edge; no double-TLS behind it
  cm:
    url: https://argocd.example.com   # links and OIDC redirects are built from this
    exec.enabled: "false"             # the UI's pod-exec terminal; off unless you need it
```

`server.insecure: true` is correct **only** when something in front terminates TLS. Set it
without an edge and the API server is plaintext on the network. Set it *and* route to port
443 and every request fails a TLS handshake against a plaintext port — the most common
"the UI is broken after I exposed it" cause. With `insecure`, route to the Service's port
**80**.

## RBAC that is a control

```yaml
configs:
  rbac:
    policy.default: ""            # deny by default
    policy.csv: |
      p, role:dev, applications,    get, nonprod/*, allow
      p, role:dev, logs,            get, nonprod/*, allow
      p, role:dev, projects,        get, nonprod,   allow
      p, role:dev, applicationsets, get, nonprod/*, allow

      # sync + resource actions on SERVICE apps only — the project also holds
      # argocd itself, the root app, and the gateway. Keep these globs in lockstep
      # with the appset's `<service>-<env>` naming.
      p, role:dev, applications, sync,     nonprod/*-dev, allow
      p, role:dev, applications, action/*, nonprod/*-dev, allow

      g, alice, role:dev
```

`policy.default: role:readonly` — the setting most installs keep — grants every authenticated
account read over every application in the instance, including the ones holding platform
config. Deny by default and grant explicitly; a new account then sees nothing until someone
decides what it should see.

Two things worth recording in a comment next to the policy:

- **What you deliberately withheld.** `applications delete` (an app is deleted by removing it
  from git), `applications update` (editing live spec bypasses git), `applications override`
  (syncing to an off-git revision). Deny-by-default already covers them; naming them keeps
  the intent alive through the next edit.
- **`login` vs `apiKey`** on accounts. `login` is password auth for a human. `apiKey` mints
  long-lived bearer tokens — appropriate for CI, wrong for people.

Account passwords are set out of band (`argocd account update-password --account <name>`) and
live in `argocd-secret`. Adding a name to `configs.cm` creates the account with **no**
password: it exists and cannot log in until someone sets one. That is a safe default and
confuses everyone the first time.

## Bring-up order

Dependencies are real and the failures are misleading if you go out of order:

```
1. Argo CD                        (by hand)
2. Repo credential                 → without it every app is "repository not accessible"
3. Root app + AppProjects
4. Secret operator + its store     → services with ExternalSecrets stay red until this exists
5. Gateway / ingress controller    → routes exist but resolve nowhere until the data plane is up
6. Identity service, if edge auth  → an edge JWT policy with no JWKS behind it 401s EVERYTHING
7. Observability                   → before the service fleet, so bring-up is visible
8. Services, ONE first, to green
```

Step 6 fails closed and silently: the edge cannot fetch the key set, so every request 401s at
the gateway and the pod logs nothing at all, because it never sees a request. If you are
debugging a service that "returns 401 for every path including health", check the gateway's
JWKS fetch before you touch the service.
