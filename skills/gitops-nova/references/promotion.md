# Promotion — from a commit to production

Contents:
- [The image flow](#the-image-flow)
- [Promote the digest, never a rebuild](#promote-the-digest-never-a-rebuild)
- [The CI contract](#the-ci-contract)
- [What makes prod different](#what-makes-prod-different)
- [Parking an environment](#parking-an-environment)
- [Onboarding a service](#onboarding-a-service)
- [Registry retention](#registry-retention)

---

## The image flow

Branch-driven, so the branch a developer pushes to decides where the artifact lands and
nobody has to remember a convention:

| Branch / event | Tag | Committed to |
| ---| ---| --- |
| push `develop` | `dev-<sha>` | `envs/dev/services/<svc>/values.yaml` |
| push `uat` | `uat-<sha>` | `envs/uat/...` |
| push `main` | `staging-<sha>` | `envs/staging/...` |
| tag `v*` | retag of the staging image, **same digest** | opens a PR against `envs/prod/...` |

Dev, uat and staging land as direct commits with auto-sync. Prod lands as a **pull request**
against a CODEOWNERS-gated path, so a human reviews it and a human syncs it.

Non-image values — env vars, replicas, secret key names, routes — are dev self-serve on
dev/uat/staging via PR, and devops-reviewed on prod. Same directory split, same review rule;
nothing extra to remember.

## Promote the digest, never a rebuild

A release tag **retags an existing image**. It does not rebuild from the same commit.

Rebuilding from an identical commit produces a different artifact: base-image security
patches have moved, transitive dependencies resolved differently, the build environment
changed. If you soak artifact A on staging and ship artifact B to prod, the soak measured
nothing. The whole reason to have a staging environment is that the thing you tested and the
thing you ship are byte-identical.

This has a consequence for the chart: a component that *is* the service must run the service's
image. A per-component image override is for components that are **not** the service — a
dev-only mock, a test harness. Otherwise "the promoted digest" stops being a single thing.

If you want a stronger guarantee than a tag, pin by digest in prod values
(`repository@sha256:…`). The cost is that the values file no longer tells a human which
version is running, so pair it with the tag in a comment.

## The CI contract

The service repo's pipeline writes **exactly one field** into this repo:

```
envs/<env>/services/<svc>/values.yaml   →   image.tag
```

Nothing else. The discipline pays off in one specific way: `git log` on the gitops repo stays
readable, because `ci(payment): dev -> dev-a1b2c3d` is visibly a robot and everything else is
visibly a decision. The moment CI edits env vars or replicas, you can no longer tell what a
human chose, and the repo stops being a record of intent.

Things worth writing into the CI job:

- **Fail if the target file does not exist**, rather than creating it. A created file has no
  route, no resources, no secrets — a broken app that looks onboarded.
- **Commit message convention** — a `ci(<svc>):` prefix makes the bot commits filterable.
- **Never write to `envs/prod/`.** Prod is a PR, always. If the job can push to prod paths,
  CODEOWNERS is decorative.
- **Bump only when the key already exists.** A pipeline that silently skips because a key is
  missing should say so in its log; one that has been skipping for weeks is a service everyone
  believes is deploying.

## What makes prod different

Prod is not nonprod with different values. Enumerate the differences and keep them visible:

| Axis | Nonprod | Prod |
| ---| ---| --- |
| AppProject | broad; several namespaces | one namespace; sources added one at a time, no wildcards |
| Sync | `automated {prune, selfHeal}` | manual — human presses sync after review |
| Review | dev self-serve | CODEOWNERS on every path |
| Versions | current | promoted only after soaking on nonprod |
| Argo CD instance | shared with dev accounts | ideally its own, with **no dev accounts at all** |
| Availability | single replica, cheap | HA — redundant controllers, redundant redis |

The strongest control on that list is the cheapest: **if dev accounts do not exist on the prod
Argo CD instance, prod is out of reach by deployment, not by policy.** RBAC is a configuration
you must keep correct through every future edit; a missing account requires no maintenance and
fails safe.

Prod also needs its own Argo CD values file (HA settings differ), which means the version pin
appears in one more place. Add it to the same lockstep note.

### The promotion PR

Include in the description, or generate it:

- the diff of `envs/prod/<svc>/values.yaml` against `envs/staging/<svc>/values.yaml`, so
  drift between the environment you tested and the one you are changing is visible;
- what the tag is a retag **of**, and where it soaked and for how long;
- whether any secret key was added — if so, the path must be seeded in the prod store
  **before** merge, or the service goes down at next refresh.

## Parking an environment

Environments often exist in the values tree before they exist for real. Park them explicitly:

```yaml
generators:
  - matrix:
      generators:
        - list:
            elements:
              - env: dev
              # uat/staging are deliberately parked: their secrets were never seeded
              # (ExternalSecret SecretSyncedError) and no image tag is pinned, so both
              # only ever produced a red app — noise for the dev team.
              # Re-enable AFTER seeding acme/<env>/<service> and pinning image.tag.
              # - env: uat
              # - env: staging
```

Park the **generator**, keep the values tree. The values stay reviewable and re-enabling is one
line. Deleting the tree loses the work and the intent.

An unparked-but-broken environment is worse than no environment: a permanently red app in the
dashboard trains the whole team to ignore red, which costs far more than the environment was
worth.

## Onboarding a service

Order matters — each step's failure mode is caused by doing it too early:

```
1. values.yaml exists in EVERY enabled env      generator entry first = red app, looks like a platform fault
2. secret path seeded in the store              unseeded = CreateContainerConfigError, looks like a chart bug
3. image.tag pinned to a REAL built image       empty = renders `repo:` → InvalidImageName
4. exposure decided                             default no route; a route needs a paths allowlist
5. scrape decided                               no /metrics handler? opt out WITH a comment naming what is missing
6. resources reviewed                           the chart default is a floor, not a fit
7. generator entry added                        last
8. watch it go green before onboarding the next
```

Step 5's opt-out matters more than it looks: leaving scrape on for a service with no metrics
endpoint creates a permanently failing target, which fires a scrape-down alert every day until
someone mutes the whole rule. One un-opted-out service can disable your alerting.

## Registry retention

If the registry prunes old tags (most do), the pin in a values file can outlive the image.
Consequences to design around:

- **Do not pin an old dev tag expecting it to survive** a retention sweep. A rollback target
  older than the window does not exist.
- **Release tags must be excluded from retention**, or prod cannot roll back. Verify this
  rather than assuming — it is a registry setting, not a default.
- Say what the policy is in the repo README. "Why did my rollback fail" is otherwise answered
  by reading a registry console at 2am.
