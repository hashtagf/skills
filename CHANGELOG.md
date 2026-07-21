# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
