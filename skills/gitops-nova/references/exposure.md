# Exposure — routes, edge auth, and the paths you did not mean to publish

Contents:
- [Default deny](#default-deny)
- [The catchall problem](#the-catchall-problem)
- [Enumerate callers, do not assume them](#enumerate-callers-do-not-assume-them)
- [Edge auth and the mesh-verifies model](#edge-auth-and-the-mesh-verifies-model)
- [Exempt paths, and how they bypass the allowlist](#exempt-paths-and-how-they-bypass-the-allowlist)
- [East-west never uses the public name](#east-west-never-uses-the-public-name)
- [The gateway itself](#the-gateway-itself)
- [Recording an accepted exposure](#recording-an-accepted-exposure)

---

## Default deny

`route.enabled: false` is the chart default and it is the right one. A service is reachable
in-cluster the moment it has a Service; a public route is an additional, deliberate act.

When a route is enabled, the second default should also be deny: **list the path prefixes the
edge may forward.** Everything else 404s at the gateway and the pod never sees the request.

```yaml
route:
  enabled: true
  hostnames: [payment.example.com]
  paths:
    - /api/v2/orders
    - /healthz
```

## The catchall problem

An `HTTPRoute` with no `matches` forwards **every** path on that hostname. That publishes not
just the API, but everything else the process happens to serve on the same listener:

- `/metrics` — internal topology, queue names, tenant identifiers, request volumes;
- `/debug/pprof` — heap and goroutine dumps if the framework mounts them;
- an ops or admin plane the author only ever expected on localhost;
- cache-flush, config-reload and seeding endpoints, which are frequently the lever that makes
  a credential rotation take effect — and therefore the lever that keeps a rotated credential
  working.

The pod's own authorization is then the only thing standing there, and it was written by
someone who assumed it was not on the internet.

Narrowing to an allowlist costs nothing to reverse: being wrong means a 404 on one integration
and a one-line fix. Being wrong the other way means finding out from someone else.

Keep in-cluster access unaffected — the allowlist removes paths from the **edge**, not from the
Service. Debugging still works via `kubectl port-forward`, which is also the right way to probe
anything sensitive: no CDN, no accelerator, no edge policy in the path to confuse the result.

## Enumerate callers, do not assume them

Before writing `paths`, find who actually calls the service **from outside the cluster**. Grep
the other services' values for this service's public hostname and for its in-cluster name. The
result is usually much smaller than expected — most "public" APIs turn out to have one external
caller and a dozen in-cluster ones.

Watch for the third category: **dead config.** A service still sets `PEER_BASE_URL` to your
public hostname, but the code path that used it was removed. It looks like a caller in a grep
and it is not one. Check the consuming code, not just the values, and flag the dead key rather
than routing for it.

The money-out routes are the ones this exercise is for. A withdrawal endpoint that no external
system calls should not be on the internet, and the only way to know is to look.

## Edge auth and the mesh-verifies model

The pattern: verify the token **once** at the gateway, inject identity as headers, and let
services trust the headers.

```yaml
route:
  jwt:
    enabled: true
    jwksURI: ""              # defaults to the in-cluster identity service
    claimToHeaders:
      - {claim: sub,       header: X-User-Id}
      - {claim: tenant_id, header: X-Tenant-Id}
```

It is a good pattern with one dangerous property: **the services stop verifying anything.**
A gate that only checks the identity headers are present and well-formed is exactly as strong
as the assumption that something upstream verified a token. Turn the route on before the policy
exists and the service is as open as its headers are guessable — three curl headers become full
impersonation, and the service logs will show a perfectly normal authenticated request.

So:

- **Never enable a public route on a mesh-verifies service before its edge policy exists.**
  If they must be separate PRs, the route comes second.
- **Fetch JWKS in-cluster**, never through your own public hostname. Through the CDN it is
  slower, billed, and fails during exactly the outage you need it most.
- **Bring-up order**: the identity service must be live and serving JWKS before any policy
  references it. It fails closed and silently — the gateway cannot fetch the key set, so
  *every* request 401s including health checks, and the pod logs nothing because it never sees
  a request.
- A login endpoint cannot sit behind the token it issues. Login, refresh, and JWKS are exempt
  by necessity — which brings us to the trap.

## Exempt paths, and how they bypass the allowlist

Exempt paths (webhooks, callbacks, login) are usually implemented as a **second, policy-free
route** carrying just those prefixes, because Gateway API resolves the most specific path match
across routes.

The trap: that second route has its **own** `matches` and carries no policy. If an exempt path
is not also covered by the main `paths` allowlist, it reaches the pod **around** the allowlist,
unauthenticated. The allowlist you added for safety is silently not applied to it.

Two rules, and both are worth enforcing in the template with `fail`:

**1. Every exempt path must be covered by an allowlisted prefix.** "Covered" follows Gateway
API `PathPrefix` semantics, which are **segment-based, not string-based**: `/api` matches
`/api/v2` but *not* `/apiadmin`. A naive `hasPrefix` check calls `/apiadmin` covered by `/api`
and waves through exactly the bypass the check exists to stop.

```gotemplate
{{/* covered = equal after trimming a trailing slash, or starts with prefix + "/" */}}
{{- $e := trimSuffix "/" $exempt }}
{{- $p := trimSuffix "/" $allowed }}
{{- if eq $e $p }}{{ $equal = true }}
{{- else if hasPrefix (printf "%s/" $p) $e }}{{ $covered = true }}{{ end }}
```

**2. An exempt path exactly equal to an allowlisted prefix must be rejected.** Two routes then
carry the same prefix — one with the policy, one without — and Gateway API breaks that tie on
**route creation timestamp**. Whether authentication applies becomes a coin flip that nobody
reading the values could predict, and it can flip on a resync. If the whole surface really
should be policy-free, set `jwt.enabled: false` and say so.

Filtering a bad entry silently is worse than failing: an auth-exempt webhook would start
401-ing with nothing pointing at the cause.

## East-west never uses the public name

```yaml
env:
  CATALOG_URL: http://catalog/api/v1        # right — ClusterIP
  # CATALOG_URL: https://catalog.example.com  # wrong — hairpins out and back
```

The public hostname sends a pod-to-pod call out through NAT, to the CDN, to the accelerator, to
the edge, and back into the same cluster. Slower, billed on both legs, dependent on external
DNS, and — the part that bites later — **it starts returning 401 the day edge auth is enabled**,
for a call that never needed to leave the cluster.

Two details that cause bugs:

- **Put the version/group prefix in the base URL** (`http://catalog/api/v1`), because clients
  typically append bare paths. Getting this wrong yields `/api/api/v1/...` and a 404 that looks
  like a routing problem.
- **Trailing slashes and duplicated segments** are the second most common cause of the same
  symptom. Write the resulting full URL in the comment.

Audit for this by grepping every values file for `https://` env values and checking whether the
host appears as a `route.hostnames` entry anywhere in the same repo. `scripts/audit.py` does
this; it is one of the highest-yield checks in it.

## The gateway itself

- **Internal load balancer, always**, with the public entry point in front of it. Never
  internet-facing directly — one misconfigured route otherwise skips every control you built.
- **TLS at the edge.** If your CDN is in a non-strict origin-validation mode, a self-signed
  origin certificate works but nothing validates it. Note that as a known gap with the fix
  named (an origin certificate and strict mode), or it reads as done.
- **`allowedRoutes.namespaces.from: All`** is what lets each environment namespace own its own
  routes. That is the intended design, and it also means any namespace on the cluster can
  attach a route to your gateway. On a shared cluster, restrict by selector.
- **Provisioning order**: the data plane is often created only once a Gateway exists. Do not
  debug a missing load balancer before checking that the Gateway resource is accepted.

## Recording an accepted exposure

Some exposures are deliberate — a test harness, an internal tool, a dev-only surface. The
decision is fine; leaving it unwritten is not, because the next reader cannot distinguish a
decision from an oversight and will either "fix" it or assume someone already approved it.

Write it where the route is declared, and include all four:

```yaml
# ⚠️ PUBLIC, UNAUTHENTICATED — decided deliberately 2026-08-04.
# WHAT is reachable: /admin/rows (inject records), /admin/flood (≥100 msg/s onto the
#   broker SHARED with orders and billing).
# WHY it is acceptable: dev-only harness, dev data, no production dependency.
# WHAT CHANGES IT: if that stops being acceptable, copy the pattern in
#   charts/<x>/templates/edge-auth.yaml — basic-auth SecurityPolicy bound to the route.
# WHEN IT GOES: delete with the harness when the real upstream reaches dev.
route: {enabled: true, hostnames: [harness.example.com]}
```

What / why / what changes it / when it goes. A reader six months later can then act, rather
than escalate.
