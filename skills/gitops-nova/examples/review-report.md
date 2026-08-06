# Example — REVIEW mode output

A finished audit of a mid-sized GitOps repo (~90 files, one shared service chart,
nine services live in dev, prod scaffolded but not running). Names are
genericised. Use it as the shape of the deliverable, not as a checklist — the
findings that matter in your repo will be different.

What makes this report usable, and what to copy:

- **Scope is stated first**, including what could not be checked. A clean report
  gets quoted later as evidence, so its boundaries have to travel with it.
- **Findings are ordered by blast radius**, not by count. There are 24 findings
  and the four that matter lead.
- **Each finding names the mechanism**, not just the rule it violates. "This is a
  catchall route" is a lint message; "the credential-rotation lever is anonymous
  on the internet" is a finding.
- **What is working is named specifically.** An audit that reads as uniformly
  negative gets filed, and the tier-1 findings go with it.

---

# GitOps repo review — acme-gitops

## Scope

Read: every manifest under `bootstrap/`, `projects/`, `apps/`, `charts/`,
`envs/`, `platform/`, `observability/` (88 files), plus `git log -40`. Ran
`audit.py`, which produced 11 high / 5 medium / 8 low; each was verified by hand
before appearing below.

**Not checked, and not checkable from this repo:** the live cluster and what was
applied to it by hand; the IAM policies behind the role ARNs referenced in
values; the contents of any image; whether the secret paths exist or who can
write them; branch protection on this repo; and what each service's code
actually serves on its listener. Several findings below are *upper bounds* for
that last reason — I can see which paths are published, not which paths exist.

---

## Findings

### Tier 1 — reachable and dangerous

**F1. The identity service exposes 12 internal endpoints to the internet.**
`envs/dev/services/auth/values.yaml:31`

`INTERNAL_API_ENABLED: "true"` mounts every `/api/auth/internal/*` route. The
route is a public catchall (`route.enabled: true`, `paths: []`) with no edge
policy, so those routes are reachable anonymously from anywhere. Their only
intended authorization is a service-mesh IP allowlist that does not exist on
this cluster yet.

Two of them are credential primitives: `verify-credentials` is a
password/TOTP oracle for any named user, and `users/{id}/reset-links` mints a
one-hour credential-reset token for any employee.

The file's own comment says "TEMPORARY — revert as soon as the invite token is
minted" and "Do not leave it on", so this is known. It has been on for six
weeks.

*Closes it:* set `route.paths` to the public surface (login, refresh, JWKS,
health), which removes `/api/auth/internal/*` from the edge without an
application change — the pod keeps serving them in-cluster. Then flip
`INTERNAL_API_ENABLED` off once the invite flow lands.

**F2. The operator back-office trusts identity headers it does not verify.**
`envs/dev/services/admin-api/values.yaml:50`

This service uses the mesh-verifies model: its gate checks only that
`X-User-Id` / `X-Tenant-Id` / `X-Realm` are present and well-formed, by design,
because the edge is supposed to have verified a token already.

`route.jwt.enabled: true` is now set, which closes it. Recording it because the
window was real and the repo should keep the evidence: verified from the public
internet before the flip — no headers → 401, hand-sent headers → 404
`DATA_NOT_FOUND`. A 404 means the gate passed and the request reached the
handler. That was full admin impersonation of any tenant with three curl
headers.

*Generalise it:* every other service using this model needs the same check.
`storefront` is one (`MODE: development` wires a dev auth shim that injects the
headers itself) and it is public with no policy — see F3.

**F3. The customer-facing service runs a development auth shim on a public host.**
`envs/dev/services/storefront/values.yaml:22`

`MODE: development` wires an auth shim that injects `X-Username` / `X-Tenant-Id`
itself. With no edge policy, any caller can supply those headers and act as that
customer. Dev data only, and the file says so — but the same values file is the
template someone will copy for uat.

*Closes it:* the edge policy, or the mode flip. Until then, add `route.paths` so
at least the ops plane is not published alongside it.

**F4. A test harness with write access to a shared broker is public and
unauthenticated.** `envs/dev/services/ingest/values.yaml:166`

`POST /admin/rows` injects records into the shared store, `/admin/fail` drives
the fail-closed branch, and `/admin/flood` generates ≥100 msg/s onto the
message broker **shared with orders and billing**.

This one is a deliberate, dated decision recorded in the file, and the comment
names the pattern that would close it. Listing it because "deliberate" and
"safe" are different claims: the flood endpoint's blast radius reaches two other
services' queues, which is beyond what a dev harness decision normally covers.

*Closes it:* the edge basic-auth policy already used by the analytics chart in
this repo — `charts/analytics/templates/edge-auth.yaml` is a working example.

### Tier 2 — unbounded

**F5. Both AppProjects allow every cluster-scoped kind.**
`projects/nonprod.yaml:31`, `projects/prod.yaml:22`

`clusterResourceWhitelist: [{group: "*", kind: "*"}]`. Expected during bring-up
and correctly commented as such in `prod.yaml` ("TODO: narrow to the CRDs the
platform charts actually install"); `nonprod.yaml` has no such note.

*Closes it:* enumerate what the platform charts install (`helm template ... |
grep '^kind:'`) and pin the list. Low urgency, but it will not get easier.

**F6. Deleting a file from `apps/nonprod/` deletes a cluster-scoped object.**
`bootstrap/nonprod/root-app.yaml:21`

The root app syncs with `prune: true` — correct for an app-of-apps. That
directory also holds a `GatewayClass` and a `ClusterSecretStore` as raw
manifests, so they inherit it. A `git mv` during a tidy-up deletes the secret
store every service depends on.

*Closes it:* fine if deliberate — say so in each manifest. If either object
should outlive a file move, give it its own Application at the observe-only
tier.

### Tier 3 — silently wrong

**F7. Ten of twelve public routes are catchalls.** (`audit.py --only RT`)

Every path each process serves is published, including `/metrics` and any
ops plane. F1 is the sharpest instance; the general fix is the same everywhere,
and the cost of getting a `paths` list slightly wrong is a 404 on one
integration and a one-line fix.

The one service that has narrowed its allowlist did the exercise properly —
enumerated actual out-of-cluster callers rather than assuming — and found that
one endpoint of the twelve it publishes has a real external caller. Expect
similar ratios elsewhere.

**F8. Three services reach each other through their own public hostnames.**
`envs/dev/services/{billing,orders}/values.yaml`

`CATALOG_BASE_URL: https://catalog.acme.example.com` from inside the cluster
hairpins pod → NAT → CDN → edge → back in. It works today and will start
returning 401 the day that host gets an edge policy — which F2's generalisation
makes likely soon.

One of the three is worse than it looks: `orders`' call to catalog was removed in
a refactor, so that variable is **dead config**. It reads as a live integration in
a grep and is not one.

*Closes it:* `http://catalog/api/v1` for the two live callers; delete the key
from `orders`.

### Tier 4 — will bite later

- **Four services point liveness and readiness at the same path.** Fine where
  the handler is static (three of them say so in a comment); the fourth does
  not, and if that path checks dependencies, a broker blip CrashLoops every
  replica rather than removing them from the endpoints.
- **`envs/prod/` carries an empty `image.tag` and a placeholder hostname** while
  being listed in the prod appset. Expected for an unbuilt environment; add one
  line saying so, since an empty directory and a deliberately-empty one look
  identical.
- **A prod values comment says the database lives in the *nonprod* cluster.**
  Almost certainly a copy-paste artifact from the staging file. Harmless while
  prod is unbuilt; dangerous the day it is not.

---

## Things done well

Worth naming, because these are the patterns to copy when fixing the rest.

- **The sync ladder is used deliberately.** The node-pool Application has no
  `automated:` block at all, and its header explains why
  `automated: {prune: false, selfHeal: false}` would not be equivalent. That
  distinction is missed in most repos.
- **The chart refuses unsafe renders.** `httproute.yaml` fails the render when a
  JWT-exempt path is not covered by the route allowlist, and it implements
  Gateway API's *segment* prefix semantics rather than a string prefix — so
  `/apiadmin` is correctly not covered by `/api`. That is the bypass this class
  of check usually waves through.
- **Helm's `false`-is-empty trap is handled** with a `kindIs "bool"` guard, in
  both places it applies. An explicit `enabled: false` actually works here.
- **CODEOWNERS gates machinery and deliberately leaves dashboards and alerts
  unowned**, with the reason written in the file. That reason is correct and it
  is the kind of decision someone tidies away without it.
- **The values files are the decision log.** Measurements, dates, verification
  results, and exit conditions. One comment records its own correction —
  "this used to say X, which was wrong twice" — which is how a stale comment is
  supposed to be handled. This is why the audit above could be specific: almost
  every risky value already had its reasoning attached.

---

## Suggested order

1. **F1** — one values change (`route.paths`), no application change, closes a
   credential-reset primitive on the internet. Do this today.
2. **F3** — same shape of fix, same day.
3. **F8** — delete the dead key, repoint the two live callers. Fifteen minutes,
   and it defuses the 401 that F2's rollout would otherwise cause.
4. **F7** — the remaining catchalls, one service per PR, each with the caller
   enumeration written into the values comment.
5. **F4** — the harness policy, using the existing edge-auth example.
6. **F6, F5** — before the next person reorganises directories.
