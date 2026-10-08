# Storybook / Histoire — optional docs-site deliverable

Read this when the user opts into a Storybook ("เพิ่ม storybook", "ทำ docs site", "อยาก
เห็น component ทุก state"), or when shipping a published package (offer it — the docs site
is the demo, docs, and test corpus at once). It is **optional**: never block the core
deliverable on it, and skipping it does not skip verification — the per-component preview
pages from the verify step are still mandatory. If the user hasn't asked and the system is
single-app CSS-only, just offer it as a follow-up line, don't build it.

## 1. Pick the tool

| Stack | Tool |
|---|---|
| React / Next.js | **Storybook** (`@storybook/nextjs-vite` for compatible Next projects, or the existing supported framework — match installed versions) |
| Vue 3 / Nuxt | **Histoire** (Vite-native, lighter) — or Storybook Vue3 renderer if the team already knows Storybook |

## 2. Scaffold

- For new projects, verify supported versions before `npx storybook@latest init` from the package root; preserve existing major versions — it detects the framework preset.
  Pin whatever major it installs; don't hand-mix Storybook major versions across addons.
- Addons: `@storybook/addon-a11y` (axe on every story), interactions (bundled in 8+),
  `storybook-addon-pseudo-states` (forces `:hover`/`:focus-visible` in matrix stories).
- Histoire: `npm i -D histoire @histoire/plugin-vue`, `histoire.config.ts` with the Vue
  plugin, `histoire.setup.ts` importing the token CSS.

**`.storybook/preview.ts` is where the design system plugs in** — this part is not optional
once Storybook exists:

```ts
import '../src/tokens/tokens.css';           // + theme.css when Tailwind v4

export const globalTypes = {
  theme:   { toolbar: { items: ['light', 'dark'] } },
  density: { toolbar: { items: ['default', 'compact'] } },   // only if densities exist
};

export const initialGlobals = { theme: "light", density: "default" };
export const parameters = { a11y: { test: "error" } }; // compatible current a11y integration

export const decorators = [
  (Story, { globals }) => {
    document.documentElement.dataset.theme = globals.theme;
    document.documentElement.dataset.density = globals.density;
    return Story(); // adapt decorator to the renderer, e.g. React JSX
  },
];
```

Import the actual token CSS; Tailwind theme.css additionally requires the consumer's Tailwind pipeline. Set story globals explicitly for deterministic screenshots.

Every story becomes viewable in every theme with zero per-story work — same
`data-theme` contract as `theming.md`.

`.storybook/main.ts`: stories glob colocated with components
(`../src/**/*.stories.@(ts|tsx)`), addons listed above. Monorepo: Storybook lives inside
`packages/ui`, not a separate app — stories import source directly, so HMR covers token
edits.

## 3. Story authoring rules (CSF3, colocated `Button.stories.tsx`)

- **Matrix story first**: one story per component rendering the full variant × state grid
  (default/hover/focus-visible/disabled/loading…, hover/focus forced via pseudo-states
  addon). This is the visual-regression target — one screenshot catches every cell.
- **Playground story**: one interactive story with controls (args) for every public prop.
- **Interaction stories**: `play` functions implementing the keyboard contracts from
  `states.md` (dialog trap + Esc, menu arrows, tabs roving tabindex…) — the test-runner
  executes them in CI, so keyboard behavior is tested where it's documented.
- **Token reference page**: an MDX/autodocs page generated from `tokens.css` by a small
  parser script — hand-maintained token tables go stale in a week.
- Each component's docs page shows examples per state, the props table, and the do/don't
  from its spec — the spec is the source, the story imports it, no duplication.

## 4. Scripts & CI

```json
"scripts": {
  "storybook": "storybook dev -p 6006",
  "storybook:build": "storybook build",
  "storybook:test": "test-storybook"
}
```

- Prefer the Vitest addon for compatible Vite frameworks; check framework, Vitest and
  Storybook compatibility before choosing it. Otherwise install the test-runner and its
  browsers, build and serve Storybook, wait for readiness, run against its URL, then teardown.
- Installing the a11y addon alone is not a failing CI gate. Current integration uses
  `parameters.a11y.test: 'error'`; older runners require their documented axe hooks.
  Prove the gate by temporarily introducing a known violation and observing nonzero exit.
- Pseudo-focus screenshots do not verify keyboard focus. Use actual interaction tests.
  Keep critical stories isolated with unique IDs; use representative matrices rather
  than forcing every variant × state combination into one enormous story.
- Visual regression (Playwright screenshots or Chromatic) targets the **matrix stories in
  both themes** — a changed semantic token shows up as a wall of diffs, which is correct
  behavior per the versioning rules.

## 5. Publish the site (share the docs, not just the package)

- `storybook build` → static `storybook-static/` → host anywhere static: GitHub Pages
  (Actions artifact deploy), Vercel, or Chromatic (which also gives VRT + PR review links).
- Put the URL in the package README next to the install instructions — an `npm i`-able
  package (`publishing.md`) plus a browsable Storybook is the full sharing story: consumers
  evaluate components before installing.
- Stories and `.storybook/` never ship in the npm package — the `files: ["dist"]` allowlist
  from `publishing.md` already guarantees this; don't undo it.
