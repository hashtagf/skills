# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.3] - 2026-08-06

### Changed
- `gitops-nova`: the example services now use a domain-neutral cast — `api`, `worker`, `auth`,
  `orders`, `billing`, `catalog`, `ingest`, `storefront`, `admin-api`, `analytics`. They
  previously carried the business vocabulary of the platform the skill was distilled from
  (`agent`, `member`, `office`, `bank`, `deposit`, `payin`), which quietly narrowed who the
  examples read as being for and made them awkward to lift into a project of a different shape.
  `agent` was doubly bad: in a skill read by an LLM it collides with the other meaning of the
  word. The skill name is unchanged.

## [0.5.2] - 2026-08-06

### Changed
- `gitops-nova`: replaced seven identifiers carried over from the private repo the skill was
  distilled from with generic equivalents — a secret-manager path, a database name (x2), three
  internal ADR/debt id formats, a real CI commit sha, a provider-specific env var name, a mock
  image name, a chart name in a docstring, and `scaffold.py`'s `--gateway` default (now `edge`,
  which is also a better name than a platform codename). No credentials, hostnames, account ids,
  ARNs, or endpoints were ever present — these were identifiers, not secrets — but this
  repository is public and none of them earned their place in a reusable skill.

## [0.5.1] - 2026-08-06

### Added
- `gitops-nova` `audit.py`: **RT007** — `jwtExemptPaths` declared while `route.jwt.enabled` is
  unset. The list is inert (nothing is exempted because nothing is enforced) and, worse, the
  values then *read* as a protected route with a carve-out, which is how a reviewer concludes
  auth is handled. Found by running the skill against a real repo: one service carried this in
  all four environments.

### Fixed
- `gitops-nova` `audit.py`: RT002/RT003 no longer assert "no edge authentication" when the
  consuming chart ships its own auth-policy template — a chart-level `SecurityPolicy` is
  invisible in the release's values. The finding now names the chart and asks for the binding to
  be checked. Values files are mapped to their chart from the Applications and ApplicationSets
  themselves, not guessed from the path, so the shared-chart layout resolves correctly.

## [0.5.0] - 2026-08-06

### Added
- **`gitops-nova`** — SOP for designing, bootstrapping, extending, and auditing an Argo CD
  GitOps repository. Distilled from a production app-of-apps repo (9 services, one shared
  chart, LGTM stack, Gateway API edge), so the rules carry the reason and the measurement
  rather than the convention.

  Four modes — BOOTSTRAP / ONBOARD / REVIEW / PROMOTE — organised around one question: what
  can a single bad merge destroy? Ten reference files cover layout and ApplicationSet
  generators, the two-step Argo CD bootstrap, the shared service chart and its Helm traps,
  the three-tier sync ladder, secrets by reference, digest promotion, exposure and edge auth,
  observability, the review checklist, and the values-file-as-decision-log convention.

  Two scripts, both verified against a real repo:
  - `scripts/audit.py` — static audit. Credentials committed as values, unpinned charts and
    images, `prune` on cluster-scoped paths, catchall public routes, JWT-exempt paths that
    bypass their own allowlist (with Gateway API *segment* prefix semantics, not string
    prefix), probes on portless components, generator entries whose values file is missing,
    wildcard project sources, apps sourcing repos their project forbids, duplicate hostnames,
    and east-west calls routed through the repo's own public hostnames. `--fail-on` makes it
    a merge gate; it reads commented-out generator entries so a parked environment is not
    reported as a broken one.
  - `scripts/scaffold.py` — repo skeleton with the traps pre-handled: the `kindIs "bool"`
    guard (Helm's `default` swallows `false`), per-component resource fallback, port-driven
    Service/probes/scrape, and templates that `fail` rather than render an unauthenticated
    path. `helm lint` and `helm template` clean.

## [0.4.0] - 2026-08-06

### Changed
- **Renamed `test-sop` → `test-design`** (breaking for anyone who installed 0.3.0 — invoke
  `/test-design`). "SOP" said nothing about what the skill decides, and nobody types it when
  asking for help; "test design" is the standard term for choosing what to verify (ISTQB /
  ISO 29119 use it for exactly this activity).
- Its description now states explicitly that the skill covers deciding and documenting *what*
  to verify, not writing or debugging automated test code (jest / vitest / playwright specs,
  mocks, flaky CI). The new name invites that misreading, so the boundary is spelled out.
  This wording is unmeasured — the trigger eval was run against the old name.

## [0.3.0] - 2026-08-06

### Added
- **test-sop** skill — SOP for designing and running software tests at the right depth,
  reusable across projects.
  - 4 levels: L1 smoke (bugfix) → L2 module (feature) → L3 system (release) → L4 critical
    (auth / payment / permission / migration), with an auto-escalation rule when work
    touches money, permissions, personal data, or authentication.
  - 12 work-type presets (feature, bugfix, API-only, UI-only, 3rd-party integration,
    auth/payment, data migration, refactor, performance, report/export, realtime, mobile),
    each listing the path types it must cover and the edge cases teams forget most.
  - 5 path types (Happy / Alternate / Error / Edge / Security) with tie-break rules,
    grounded in ISTQB test levels/types, ISO/IEC 25010 quality characteristics, and
    ISO/IEC/IEEE 29119-3 test documentation.
  - Reference library: templates (module / scenario / checklist / bug / API-only / smoke),
    planning docs (test plan, risk matrix, traceability matrix, summary report),
    a domain checklist library (CRUD, list/search, upload, money, notification, export,
    realtime, RBAC, cron, NFR), a coverage-audit method, and ClickUp/Jira task-tree mapping.
  - `scripts/scaffold.py` generates the whole doc set for a chosen level with 6 domain
    presets (auth, payment, crud, api, integration, migration), English by default and
    `--lang th` for Thai-speaking teams.
  - Worked L4 example: 12-module / 64-scenario authentication set.
  - Skill instructions are in English; the description carries both English and Thai trigger
    phrases, and deliverables are written in the team's own language.
  - `scripts/checklist.py` generates the per-scenario checklists from the acceptance criteria
    and verifies they stay 1:1 (`--check`, non-zero exit on drift).
  - Benchmarked against a no-skill baseline on 4 realistic tasks (33 mechanical assertions,
    single run each, Sonnet subagents): **97% with the skill vs 48% without**. An earlier
    iteration of the skill scored 91% on the same ruler. The clearest effect is depth
    calibration — the same skill produced 2 files / 438 words for a bugfix and 10 files /
    10k words for a payment system, where the baseline wrote at roughly one length regardless
    of risk. Numbers are one run per task on one model; treat them as directional.
  - Eval findings folded back into the skill: no-placeholder rule promoted to a top-level rule
    (`grep -rn TODO`, and any placeholder that must stay has to be disclosed in the reply),
    risk-ordered wave delivery required above ~20 scenarios, coverage audits must name the NFR
    section an item moves into, and checklists are generated rather than hand-copied — hand
    copying drifted from the criteria in 64–100% of scenarios, losing conditions in both
    directions, which the generated + verified flow eliminated entirely.
  - Trigger measurement: 20-query eval (3 runs each, 3 optimizer iterations) found perfect
    precision but 8–17% recall on deliberately advisory phrasings, and two machine-written
    descriptions scored worse than the original, so the description is unchanged. Advisory
    questions get answered directly instead of dispatched to a skill, so **invoke it explicitly
    (`/test-sop`)** rather than relying on auto-trigger.

### Changed
- `.codex/` config with local Anthropic base URL.

## [0.2.0] - 2026-07-28

### Added
- **kimi-k3** skill and the `kimi-k3` / `kimi-k3-implement` agents — delegate a prompt or a
  scoped coding task to Moonshot's Kimi K3 and relay the result. Needs `MOONSHOT_API_KEY`.

## [0.1.0] - 2026-07-17

Initial release of the hashtagf skill warehouse, installable as a Claude Code
plugin or via the `skills` CLI.

### Added
- **design-system-builder** skill — build, extract, or repair a complete design
  system (tokens + component library with full interaction states + docs).
  - 4 modes: CREATE, EXTRACT, REDESIGN, and extend.
  - Output as CSS/Tailwind or an installable package for React, Next.js, or Vue
    (auto-detected from the repo).
  - Packaging, guardrails, and eval suites with fixtures.
  - Foundations: keyframe animation tokens (spin / shimmer / enter-exit / slide),
    toast queue + stagger rules, and image loading rules.
  - States: placeholder and validation-timing rules.
- Claude Code plugin manifest and `skills` CLI packaging.

### Changed
- Eval suites excluded from distribution (dev-only).

[Unreleased]: https://github.com/hashtagf/skills/compare/v0.5.3...HEAD
[0.5.3]: https://github.com/hashtagf/skills/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/hashtagf/skills/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/hashtagf/skills/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/hashtagf/skills/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/hashtagf/skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/hashtagf/skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/hashtagf/skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hashtagf/skills/releases/tag/v0.1.0
