---
name: design-system-builder
description: >-
  Build, extract, or repair a complete design system (tokens + components + states + docs)
  for one theme. Three modes: (1) CREATE — interview the user, then build a full system from
  scratch; (2) EXTRACT — audit an existing codebase, inventory its de-facto design decisions,
  and produce a token/component plan; (3) REDESIGN — fix an existing design system so it
  actually works (broken token architecture, missing states, inconsistent components).
  Use this skill whenever the user mentions design systems, design tokens, theming, component
  libraries, style guides, "สร้าง design system", "ถอด design system จาก codebase",
  "ทำ theme", "design tokens", "ปรับ design system", standardizing UI styles, or wants
  consistent colors/spacing/typography across an app — even if they only ask for "a button
  component" but clearly need systematic foundations behind it.
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

All three modes converge on the same deliverable format (see "Deliverables" below); they
differ in where the design decisions come from: the interview, the codebase, or the broken
system plus its real-world usage.

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
- `references/components.md` — full inventory (~140 components in 10 categories), ship tiers,
  and the per-component spec template. Read when planning scope or writing component specs.
- `references/states.md` — complete state taxonomy (interactive, selection, validation,
  loading, structural), how major systems implement them, CSS/data-attribute patterns.
  Read when writing any component spec or reviewing state coverage.
- `references/interview.md` — CREATE-mode interview script. Read at the start of CREATE mode.

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
   Implement in the user's stack (default: CSS custom properties + Tailwind v4 `@theme`
   if no stack is specified).
6. **Docs.** Token reference + per-component usage (do/don't) + the DECISIONS.md.

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
   inventory with state-coverage gaps, and a prioritized build plan (which components to
   build/merge first, based on usage frequency).
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

## Deliverables (all modes end here)

- **Tokens as code**: CSS custom properties (and Tailwind `@theme` / config when the
  project uses Tailwind), organized primitive → semantic → component.
- **Component specs/implementations** per the template, each with its full state matrix.
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
