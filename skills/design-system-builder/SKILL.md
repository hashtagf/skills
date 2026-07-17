---
name: design-system-builder
description: >-
  Build, extract, repair, or extend a complete design system — design tokens, a component
  library with full interaction states, and docs — delivered as CSS/Tailwind or as an
  installable package for React, Next.js, or Vue (auto-detected from the repo). Use this
  skill whenever the user mentions design systems, design tokens, theming, dark mode,
  component libraries, style guides, "สร้าง design system", "ถอด design system จาก
  codebase", "ทำ theme", or wants consistent colors/spacing/typography across an app —
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
| **EXTRACT** | Existing codebase, no formal system; "audit", "ถอดออกมา" | Audit report → consolidated tokens → component build plan |
| **REDESIGN** | A design system exists but is broken/inconsistent | Gap analysis → repaired architecture → migration notes |
| **EXTEND** | A healthy system exists; "add a Date Picker", "add dark mode", "add compact density" | New parts that conform to existing conventions |

All four modes converge on the same deliverable format (see "Deliverables" below); they
differ in where the design decisions come from: the interview (CREATE), the codebase
(EXTRACT), the broken system plus its real-world usage (REDESIGN), or the existing
system's own conventions (EXTEND).

Scope: web design systems (CSS/Tailwind; React, Next.js, Vue). Native mobile
(React Native/Flutter/SwiftUI) is out of scope — for those, deliver only the
token JSON/CSS as a shared source and say so.

## Non-negotiable principles (all modes)

1. **Three-tier tokens.** `primitive → semantic → component`. Components never reference
   primitives directly — the semantic layer is what makes a second theme a one-layer swap
   instead of a rewrite. Naming: `{component}-{variant}-{state}-{property}`.
2. **One spacing scale.** Base-4 scale used for padding, margin, and gap alike. Any value
   outside the scale is a bug, not a design decision.
3. **Every component ships with its full state matrix.** A button without hover, focus-visible,
   disabled, and loading specs is not done. Read `references/states.md` for the checklist —
   it is the most commonly skipped part and the reason most design systems fail review.
4. **One focus-ring spec for the whole system** (color, width, offset; contrast ≥ 3:1 per
   WCAG 2.4.11). Never per-component focus styles.
5. **Ship in tiers.** MVP (~20 components) → Growth (~50) → Full (100+). Never attempt the
   full inventory in one pass; deliver Tier 1 working end-to-end first, because a complete
   Button proves the token architecture in a way that 50 half-specified components cannot.
6. **Thai-language support when relevant** (Thai user text, Thai fonts in the codebase):
   body line-height ≥ 1.6 to clear stacked vowels/tone marks, Thai+Latin font pairing,
   no letter-spacing on Thai text.

## Reference files — read before the relevant phase

- `references/foundations.md` — the 13 foundation token categories with recommended scales
  and values, plus token architecture and naming. Read when defining or restructuring tokens.
- `references/components.md` — full inventory (~140 items: 9 component categories + composed patterns), ship tiers,
  and the per-component spec template. Read when planning scope or writing component specs.
- `references/states.md` — complete state taxonomy (interactive, selection, validation,
  loading, structural), how major systems implement them, CSS/data-attribute patterns.
  Read when writing any component spec or reviewing state coverage.
- `references/interview.md` — CREATE-mode interview script. Read at the start of CREATE mode.
- `references/packaging.md` — framework detection (React / Next.js / Vue), package shapes
  (workspace vs published npm), and per-framework authoring rules. Read before implementing
  components in any framework or when the deliverable is a reusable package.
- `references/theming.md` — second-theme (dark mode) playbook and density variants.
  Read in EXTEND mode for theme work, or when the user wants dark mode / compact.
- `references/guardrails.md` — Stylelint/ESLint/CI rules that stop token drift. Read when
  the project has CI, and always at the end of EXTRACT and REDESIGN.
- `references/operations.md` — package versioning & deprecation, testing strategy,
  Storybook/Histoire setup with story-authoring rules (matrix/playground/interaction
  stories), Figma sync. Read when shipping a package or setting up infrastructure.

## Mode 1: CREATE

1. **Interview.** Read `references/interview.md` and run the interview. If the user is not
   available to answer (background run), make explicit, conventional assumptions, record
   them in a `DECISIONS.md`, and proceed — a system built on stated assumptions is
   correctable; a stalled one is worthless.
2. **Token architecture.** Define the three tiers and naming convention before any values.
3. **Foundations.** Define all 13 categories from `references/foundations.md` for the one
   theme. Populate primitives, then semantic aliases.
4. **System-wide specs.** Focus ring, state layer/interaction color strategy, motion rules,
   z-index scale — the cross-cutting decisions components will inherit.
5. **Components, Tier 1 first.** For each: anatomy (internal padding, gap, sizes) →
   variants → full state matrix, using the spec template in `references/components.md`.
   Detect the project's framework and package shape per `references/packaging.md`
   (React / Next.js / Vue from package.json — never ask what the repo can answer;
   default: CSS custom properties + Tailwind v4 `@theme` when no stack exists).
6. **Verify.** Build a preview/demo page per component exercising every state (both themes
   if two exist), render it (browser/screenshot where available), and check it against the
   quality gate. A design system that has never been rendered is a hypothesis, not a system.
7. **Docs.** Token reference + per-component usage (do/don't) + the DECISIONS.md. Add CI
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

## Deliverables (all modes end here)

- **Tokens as code**: CSS custom properties (and Tailwind `@theme` / config when the
  project uses Tailwind), organized primitive → semantic → component.
- **Component specs/implementations** per the template, each with its full state matrix,
  authored for the detected framework (React / Next.js / Vue) and shaped as a consumable
  package (`@org/ui` workspace or published — see `references/packaging.md`) whenever the
  system will be consumed by more than one place in the repo.
- **Docs**: `README.md` (structure + how to consume), token reference table,
  `DECISIONS.md` (CREATE) / `AUDIT.md` (EXTRACT) / `MIGRATION.md` (REDESIGN).

## Quality gate before declaring done

Run through this list and state the result honestly:

- [ ] No component token references a primitive directly
- [ ] Every shipped component covers its applicable states (checklist in `references/states.md`)
- [ ] Focus ring identical everywhere, ≥ 3:1 contrast
- [ ] Text contrast ≥ 4.5:1 (normal) / 3:1 (large); state not conveyed by color alone
- [ ] All spacing values on-scale
- [ ] Disabled styles win over hover/active (`:not(:disabled)` guards or ordering)
- [ ] `prefers-reduced-motion` respected wherever motion tokens are used
- [ ] Thai text rules applied if the product has Thai content
