# Operations: Versioning, Testing, Docs Site, Figma

Read this when the system ships as a package, when setting up its test/docs infrastructure,
or when the user asks how to run the system over time.

## Versioning (semver for a design system)

| Change | Level |
|---|---|
| Visual-identical fixes, doc changes | patch |
| New component, new token, new additive state/variant/prop | minor |
| Intentional value change on an existing semantic/component token (brand tweak) | minor, but flag prominently in changelog — screens will visibly change |
| Rename/remove a token, class, prop, or component; change component DOM structure | **major** |

**Deprecation before removal, always:** keep the old name as an alias resolving to the new
token (CSS) or a re-export with a console warning in dev (JS), note it in the changelog
with a removal version, and remove no sooner than the next major. This is the same
alias discipline REDESIGN mode uses — it's how consumers survive upgrades.

Changelog: keep-a-changelog format; CI requires an entry on any PR that touches `tokens/`.

## Testing strategy

Stories are the backbone: **one story per component per state per theme** (the same
preview pages the verify step renders). They serve as demo, docs, and test corpus at once —
see the Storybook/Histoire section below for how to author them.

1. **Accessibility (automated)**: axe (`vitest-axe` / `@axe-core/playwright`) against every story.
2. **Interaction**: Testing Library tests for the keyboard contracts in `states.md`
   (dialog trap+Esc, menu arrows, tabs roving tabindex…).
3. **Visual regression**: Playwright screenshots of every story in both themes; diff on PR.
   This is what actually catches token regressions — a changed semantic value shows up as
   a wall of diffs, which is correct behavior (see versioning above).
4. **Types**: public prop types tested with `expect-type`/`tsd` if the package is TS.

## Storybook / Histoire (docs site + test corpus in one)

React/Next → Storybook (framework preset matching the bundler); Vue → Histoire (or
Storybook with the Vue renderer). Set this up as part of the package deliverable — it is
the demo, the docs, and the test corpus simultaneously, which is why it pays for itself.

**Story authoring rules** (CSF3, colocated `Button.stories.tsx` next to the component):

- **Matrix story first**: one story per component rendering the full variant × state grid
  (default/hover/focus-visible/disabled/loading…, hover/focus forced via
  `storybook-addon-pseudo-states`). This is the visual-regression target — one screenshot
  catches every cell.
- **Playground story**: one interactive story with controls (args) for every public prop.
- **Interaction stories**: `play` functions implementing the keyboard contracts from
  `states.md` (dialog trap + Esc, menu arrows…) — the Storybook test-runner executes them
  in CI, so keyboard behavior is tested where it's documented.

**Setup essentials:**

- Global decorator imports `tokens.css` and adds a toolbar switch that stamps
  `data-theme` / `data-density` on the preview root — every story instantly viewable in
  every theme without story changes.
- Addons: `a11y` (axe on every story), `interactions`, `pseudo-states`.
- Token reference page: an MDX/autodocs page generated from `tokens.css` by a small
  parser script — hand-maintained token tables go stale in a week.
- Each component's docs page: examples per state, props table, and the do/don't from its
  spec — the spec is the source, the story imports it, no duplication.

Visual regression (Playwright or Chromatic) runs against the matrix stories in both themes.

## Figma

If the session has Figma tooling available (Figma MCP `use_figma`, or a figma-ds-cli
project), offer a code→Figma sync: generate the Figma library from the shipped tokens and
component specs using that tool's own workflow/skill — do not duplicate its instructions
here. Record the Figma file link in the README. If no Figma tooling is connected, note it
as a follow-up instead of blocking.
