---
name: design-system-builder
description: >-
  Build, extract, repair, or extend a complete design system — design tokens, a component
  library with full interaction states, and docs — delivered as CSS/Tailwind or as an
  installable package for React, Next.js, or Vue (auto-detected from the repo) — including
  publishing and sharing it as an npm package other repos can `npm i` (npm/GitHub
  Packages/private registry), plus an optional Storybook/Histoire docs site. Use this
  skill whenever the user mentions design systems, design tokens, theming, dark mode,
  component libraries, style guides, a Storybook for their components, "สร้าง design
  system", "ถอด design system จาก codebase", "ทำ theme", "ทำเป็น npm package", "publish
  ขึ้น npm", or wants consistent colors/spacing/typography across an app —
  even if they only ask for a single component but clearly need systematic foundations
  behind it.
---

# Design System Builder

Build production-grade design systems: token architecture, foundations, component specs
with full interaction states, and documentation — for one theme, structured so more themes
(e.g. dark mode) can be added later by swapping one token layer.

## Pick the mode first

Decide from the user's request; confirm only if genuinely ambiguous:

| Mode | Signal | Output |
|---|---|---|
| **CREATE** | No existing system; "start from scratch", new product | Interview → full system (tokens + components + docs) |
| **EXTRACT** | Existing codebase, no formal system; "audit", "ถอดออกมา" | Audit report → proposed consolidated tokens → component build plan |
| **REDESIGN** | A design system exists but is broken/inconsistent | Gap analysis → repaired architecture → migration notes |
| **EXTEND** | A healthy system exists; "add a Date Picker", "add dark mode", "add compact density" | New parts that conform to existing conventions |

Deliver only what the selected mode and user scope require. Decisions come from: the interview (CREATE), the codebase
(EXTRACT), the broken system plus its real-world usage (REDESIGN), or the existing
system's own conventions (EXTEND).

Scope: web design systems (CSS/Tailwind; React, Next.js, Vue). Native mobile
(React Native/Flutter/SwiftUI) is out of scope — for those, deliver only the
token JSON/CSS as a shared source and say so.

## Principles (all modes)

1. **Tokens follow roles.** Use primitive → semantic aliases; add component tokens when
   component-specific control is useful. Document deliberate invariant values. Validate
   aliases and themes; a three-tier diagram alone does not prove theme correctness.
2. **Respect existing scales.** Base-4 is a possible default, not an accessibility rule.
   Preserve deliberate spacing values; document exceptions rather than calling them bugs.
3. **Cover applicable states and behavior.** Use `references/states.md`; mark N/A states.
   Include keyboard, focus, accessible names and error associations, not only CSS.
4. **Accessible focus.** A shared focus contract may adapt to surrounding surfaces.
   WCAG 2.4.7 requires visible focus; 2.4.11 AA concerns focus not being entirely obscured;
   1.4.11 covers applicable non-text contrast. 2.4.13 focus appearance is AAA.
5. **Scope to demand.** Agree a useful component slice; even two complete components can
   be a valid MVP. Inventory tiers are planning examples, not minimum delivery counts.
6. **Validate languages.** For Thai, test actual fonts, stacked marks, wrapping, mixed
   scripts and zoom. Start with generous line-height (e.g. 1.6); adjust using rendered
   evidence. Avoid adding tracking by default, without treating it as a universal ban.

## Do / Don't — decisions during every mode

Use these pairs at the relevant decision point. Follow the user's scope and the
existing system; recommendations may have documented exceptions. Accessibility
requirements and claims about executed checks need evidence.

| Do | Don't |
|---|---|
| Read existing tokens, sibling components and consumer constraints before changing the system. | Introduce a competing scale, naming scheme or framework solely because an example uses it. |
| Deliver the requested component slice; in report-only EXTRACT, propose changes in the audit. | Expand a two-component request into the full inventory or modify audited code without implementation scope. |
| Use semantic roles and document deliberate invariant values and scale exceptions. | Hardcode theme-dependent values or silently remap intentional values such as 6px spacing. |
| Specify applicable states, keyboard behavior, focus and error associations; mark N/A explicitly. | Treat a default-state screenshot, an ARIA attribute or disabled-looking CSS as proof of usable behavior. |
| Render Thai content with actual fonts, stacked marks, mixed scripts, wrapping and zoom. | Present a fixed line-height or tracking value as a guarantee that Thai text renders correctly. |
| Preserve supported consumer APIs with aliases and migration notes when changing them. | Remove public tokens or props without assessing compatibility and explaining migration. |
| Build and inspect the packed artifact, then test it in a fresh supported consumer when packaging is requested. | Infer package correctness from workspace imports, or publish when only preparation/sharing was requested. |
| Report passed, failed and untested checks; prove a CI gate detects a known violation when configuring it. | Claim production readiness or WCAG conformance from unexecuted checks or automated accessibility results alone. |

For component usage docs, read `references/do-and-dont-examples.md` when authoring or
reviewing examples. Use relevant pairs with the reason and an observable check; adapt
the examples to the real component API rather than copying an invented API.

## Reference files — read before the relevant phase

- `references/foundations.md` — the 13 foundation token categories with recommended scales
  and values, plus token architecture and naming. Read when defining or restructuring tokens.
- `references/components.md` — full inventory (~140 items: 9 component categories + composed patterns), ship tiers,
  and the per-component spec template. Read when planning scope or writing component specs.
- `references/do-and-dont-examples.md` — component usage examples, failure reasons and
  verification checks. Read when writing usage guidance or reviewing misuse.
- `references/states.md` — complete state taxonomy (interactive, selection, validation,
  loading, structural), how major systems implement them, CSS/data-attribute patterns.
  Read when writing any component spec or reviewing state coverage.
- `references/interview.md` — CREATE-mode interview script. Read at the start of CREATE mode.
- `references/packaging.md` — framework detection (React / Next.js / Vue), package shapes
  (workspace vs published npm), and per-framework authoring rules. Read before implementing
  components in any framework or when the deliverable is a reusable package.
- `references/publishing.md` — making the package `npm i`-able outside its repo: registry
  choice (npm public/private, GitHub Packages, self-hosted, git/tarball), build pipeline,
  published package.json, pre-publish verification, Changesets release automation, consumer
  install docs. Read when the user wants to publish or share the system as an npm package.
- `references/theming.md` — second-theme (dark mode) playbook and density variants.
  Read in EXTEND mode for theme work, or when the user wants dark mode / compact.
- `references/guardrails.md` — Stylelint/ESLint/CI rules that stop token drift. Read when
  the project has CI, and always at the end of EXTRACT and REDESIGN.
- `references/operations.md` — package versioning & deprecation, testing strategy,
  Figma sync. Read when shipping a package or setting up infrastructure.
- `references/storybook.md` — optional Storybook/Histoire docs site: tool choice, scaffold,
  theme-toolbar preview config, story authoring rules (matrix/playground/interaction),
  CI test-runner, publishing the static site. Read when the user opts into a Storybook
  or when shipping a published package (offer it then).

## Mode 1: CREATE

1. **Interview.** Read `references/interview.md` and run the interview. If the user is not
   available to answer (background run), make explicit, conventional assumptions, record
   them in a `DECISIONS.md`, and proceed — a system built on stated assumptions is
   correctable; a stalled one is worthless.
2. **Token architecture.** Define role aliases, optional component tokens and naming conventions. Read `references/token-interoperability.md` for portable token exchange.
3. **Foundations.** Assess the 13 categories in `references/foundations.md`; implement relevant categories and mark others deferred or N/A. Populate primitives, then semantic aliases.
4. **System-wide specs.** Focus ring, state layer/interaction color strategy, motion rules,
   z-index scale — the cross-cutting decisions components will inherit.
5. **Components, Tier 1 first.** For each: anatomy (internal padding, gap, sizes) →
   variants → full state matrix, using the spec template in `references/components.md`.
   Detect the project's framework and package shape per `references/packaging.md`
   (React / Next.js / Vue from package.json — never ask what the repo can answer;
   default: plain CSS custom properties when no stack exists; add Tailwind only when requested or already used).
6. **Verify.** Build a preview/demo page per component exercising every state (both themes
   if two exist), render it (browser/screenshot where available), and check it against the
   quality gate. A design system that has never been rendered is a hypothesis, not a system.
7. **Docs.** Token reference + per-component usage (paired do/don't examples, reasons
   and checks per `references/do-and-dont-examples.md`) + the DECISIONS.md. Add CI
   guardrails per `references/guardrails.md` when the project has CI.

## Mode 2: EXTRACT

1. **Sweep the codebase** for de-facto tokens. Prefer spawning search subagents for the
   noisy part. Collect: every color literal (hex/rgb/hsl), font-family/size/weight values,
   spacing values (padding/margin/gap), border-radius, shadows, z-index values, breakpoints,
   animation durations. Count occurrences — frequency reveals which values are intentional
   and which are drift.
2. **Inventory existing components** and near-duplicates (three different Button
   implementations count as one component + a consolidation task).
3. **Consolidate.** Cluster the found values into proposed scales (e.g. 14 grays → one
   9-step scale; 23 spacing values → the base-4 scale, with a mapping table old → new).
   Every collapsed value must appear in the mapping table — silent drops break UIs.
4. **Report.** Produce `AUDIT.md`: found values with counts, proposed token set, component
   inventory with state-coverage gaps, a prioritized build plan (which components to
   build/merge first, based on usage frequency), and a drift-prevention section from
   `references/guardrails.md` — without enforcement the codebase regrows the mess.
5. Stop after the report unless the user asked to also build — EXTRACT's deliverable is
   the plan, and the user decides what gets built.

## Mode 3: REDESIGN

1. **Gap analysis against this skill's checklists**: token tiers present? components
   referencing primitives directly? state matrix coverage per component (use
   `references/states.md`)? focus-ring consistency? values outside the spacing scale?
   Produce a findings table: issue → severity → affected components.
2. **Fix architecture first** (token tiers, naming, semantic layer), because component
   fixes done before the architecture is right get redone.
3. **Fill state gaps** component by component, worst-used-most first.
4. **Preserve working usage.** Keep old token names as deprecated aliases pointing at new
   tokens rather than deleting them, and note each in a migration table — the goal is a
   system that works, not a big-bang rename that breaks every screen.
5. **Verify**: render/screenshot key components in every state where the project has a
   runnable app; otherwise diff computed CSS before/after for a sample of components.
6. **Guard**: add CI guardrails per `references/guardrails.md` (ratchet mode on legacy
   code) so the repaired system stays repaired.

## Mode 4: EXTEND

For adding to a system that already works. The prime directive: **conform, don't invent**.

1. **Read the existing system first** — tokens, an existing sibling component's spec/code,
   naming conventions, focus-ring spec, story format. The new part must look like it was
   always there.
2. **New component**: pick the closest existing component as the template; reuse semantic
   tokens (a new primitive/semantic token requires a documented gap, not convenience);
   full state matrix per `references/states.md`; stories for every state; changelog entry
   (minor). Follow the spec template in `references/components.md`.
3. **New theme / density**: follow `references/theming.md`.
4. **Verify like CREATE step 6** — render the new part next to existing components; visual
   inconsistency with siblings is a failure even when the component is fine in isolation.

## Deliverables (adapt to mode and requested scope)

EXTRACT without implementation ends at `AUDIT.md`; the following code/package items
apply only when implementation is requested. External publication requires a user
request to publish; preparing a tarball and consumer instructions does not require a release.

- **Tokens as code**: CSS custom properties (and Tailwind `@theme` / config when the
  project uses Tailwind), organized by primitives, semantic roles and optional component tokens.
- **Component specs/implementations** per the template, each with its full state matrix,
  authored for the detected framework (React / Next.js / Vue) and shaped as a consumable
  package (`@org/ui` workspace or published — see `references/packaging.md`) whenever the
  system will be consumed by more than one place in the repo. If consumers live outside
  the repo, prepare a distributable per `references/publishing.md`; publish when requested.
- **Docs**: `README.md` (structure + how to consume), token reference table,
  `DECISIONS.md` (CREATE) / `AUDIT.md` (EXTRACT) / `MIGRATION.md` (REDESIGN).
- **Optional — Storybook/Histoire docs site** per `references/storybook.md`: build when
  the user opts in; offer it when shipping a published package. Never block the core
  deliverable on it.

## Quality gate before declaring done

Run through this list and state the result honestly:

- [ ] Token aliases resolve without cycles; role mappings and documented invariants work in each supported theme
- [ ] Every shipped component covers its applicable states (checklist in `references/states.md`)
- [ ] Component usage guidance includes relevant Do / Don't pairs with a reason and an observable check
- [ ] Focus is visible, not entirely obscured, and meets applicable non-text contrast; AAA focus appearance checked only if targeted
- [ ] Text contrast ≥ 4.5:1 (normal) / 3:1 (large); state not conveyed by color alone
- [ ] Spacing follows the agreed scale or documented exceptions
- [ ] Disabled styles win over hover/active (native and aria-disabled guards plus activation prevention)
- [ ] `prefers-reduced-motion` respected wherever motion tokens are used
- [ ] Thai glyphs, wrapping and zoom rendered and checked if relevant
- [ ] Packed package passes a fresh consumer build if packaging is in scope
- [ ] Record passed, failed and untested checks; automated accessibility checks alone are not conformance

## Research and operation references

- `references/token-interoperability.md` — DTCG exchange and alias validation.
- `references/research-audit-2026-10-09.md` — official-source findings and remaining evidence limits.
- `references/operations.md` — ownership, contribution review, adoption and testing evidence.
