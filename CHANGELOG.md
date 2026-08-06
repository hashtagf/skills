# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
  - Benchmarked against a no-skill baseline on 4 realistic tasks (30 assertions, Sonnet
    subagents): 100% vs 51% pass rate. Split by assertion kind: quality criteria (edge/security
    coverage, measurable acceptance criteria, out-of-scope discipline) 96% vs 65%; SOP-format
    criteria 100% vs 0%. The clearest effect is depth calibration — the same skill produced
    2 files / 417 words for a bugfix and 14 files / 207 KB for a payment system, where the
    baseline wrote at roughly one length regardless of risk.
  - Eval findings folded back into the skill: no-placeholder rule promoted to a top-level rule
    with a `grep -rn TODO` check, risk-ordered wave delivery required above ~20 scenarios, and
    coverage audits must name the NFR section an item moves into.
- `.codex/` config with local Anthropic base URL.

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

[Unreleased]: https://github.com/hashtagf/skills/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/hashtagf/skills/releases/tag/v0.1.0
