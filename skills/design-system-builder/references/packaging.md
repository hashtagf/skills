# Packaging & Framework Targets (React / Next.js / Vue)

Read this when the deliverable is a reusable package, or when implementing components in
the project's framework. Two decisions to make, in order: (1) which framework, (2) which
package shape.

## 1. Detect the framework — never ask if the repo can answer

Inspect `package.json` (root + workspaces) and config files, in this priority:

| Signal | Target |
|---|---|
| `next` in deps / `next.config.*` | **Next.js** (React rules + RSC rules below) |
| `nuxt` in deps / `nuxt.config.*` | **Vue** (author Nuxt-compatible: no app-level plugins required) |
| `vue` in deps / `*.vue` files / `vite` with `@vitejs/plugin-vue` | **Vue 3** |
| `react` / `react-dom` | **React** |
| none of the above | Ask the user; if unavailable, default React + note in DECISIONS.md |

Also detect: TypeScript (`tsconfig.json` → author in TS), Tailwind version (`tailwindcss`
dep → tokens via `@theme` for v4, `tailwind.config` for v3), monorepo (`workspaces` field,
`pnpm-workspace.yaml`, `turbo.json`).

## 2. Package shape

| Situation | Shape |
|---|---|
| Monorepo (workspaces detected) | Internal workspace package `packages/ui`, consumed as `@{org}/ui` via `workspace:*`. Ship **source directly** (no build step) — the consuming app's bundler compiles it; simplest to maintain |
| Single app, wants reuse later | Same structure under `src/ui/` or `packages/ui`, importable by path alias — promote to published package later without restructuring |
| Published npm package requested | Build with `tsup` or Vite library mode: ESM + `.d.ts`, `sideEffects: ["*.css"]`, framework in `peerDependencies` (never `dependencies`) |

Structure (framework-agnostic core, framework-specific components):

```
packages/ui/
├── package.json          exports map below
├── src/
│   ├── tokens/           tokens.css (primitive+semantic), theme.css (@theme for TW v4)
│   ├── components/       one dir per component: Button/Button.tsx|.vue + index
│   ├── lib/              cn/variant helpers
│   └── index.ts          re-exports everything
```

`exports` map — tokens must be importable WITHOUT the components (apps may adopt tokens first):

```json
{
  "name": "@org/ui",
  "exports": {
    ".": "./src/index.ts",
    "./tokens.css": "./src/tokens/tokens.css",
    "./theme.css": "./src/tokens/theme.css"
  },
  "peerDependencies": { "react": ">=18" }
}
```

Tokens stay **plain CSS custom properties** in every target — they are the
framework-independent layer; only component code differs per framework.

## 3. Framework authoring rules

### React
- `forwardRef` on every leaf interactive component (or plain `ref` prop on React 19) —
  consumers WILL need refs for focus management and form libs.
- Variants via `cva` (class-variance-authority) or a typed variant map; props:
  `variant`, `size`, `disabled`, `loading` + native props spread last.
- Controlled + uncontrolled where the native element has state (Input, Checkbox):
  support `value`/`defaultValue`.
- Compound components as namespace or dot-notation (`Tabs`, `Tabs.List`, `Tabs.Panel`).

### Next.js (adds to React rules)
- Default every component to **server-compatible** (no `'use client'`) — only add
  `'use client'` to components that use state/effects/event handlers (Modal, Tabs,
  Dropdown…). A design system that marks everything client poisons the consumer's tree.
- Split entries if needed: purely-presentational (Badge, Card, Divider) must stay
  server-safe. Never import a client component from a server-safe one.
- Fonts via `next/font` in docs/examples, not hardcoded `@font-face`.

### Vue 3
- SFC `<script setup lang="ts">`, `defineProps` with TS types + `withDefaults`.
- `v-model` on form components (`modelValue` prop + `update:modelValue` emit); support
  multiple models where natural (e.g. `v-model:checked`).
- Slots over render props: default slot for content, named slots for anatomy parts
  (`#icon`, `#footer`). Expose `defineExpose({ focus })` on inputs.
- Attrs fall through to the root interactive element (`inheritAttrs: false` + `v-bind="$attrs"` when the root isn't the interactive element).

### All frameworks
- Component tokens and states come from the same specs (`components.md`, `states.md`) —
  the framework changes the wiring, never the design decisions.
- Style with the token CSS variables (directly or via Tailwind utilities bound to tokens);
  no framework target may hardcode values.
- One story/demo page per component exercising every state — it doubles as the visual
  verification target.

## 4. Multi-framework requests

If the user needs two+ frameworks (e.g. React web + Vue admin): share `tokens/` and all
specs; implement components per framework under `packages/ui-react`, `packages/ui-vue`.
Build the full set in the PRIMARY framework first, then port — parallel half-finished
sets drift apart immediately.
