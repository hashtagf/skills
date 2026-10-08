# Foundation Tokens — 13 Categories

Assess every category; implement those needed by the requested product slice and record deferred/N/A categories. Recommended values are defaults, not mandates — replace
them with interview/audit findings, but keep the *structure*.

## Token architecture (define before any values)

Use primitives and semantic roles. Component tokens are optional where they add control; document invariant exceptions rather than forcing redundant aliases.

```
primitive        blue-600: #2563eb              raw value, no meaning
semantic/alias   color-bg-brand: {blue-600}     meaning; the theme-swap layer
component        button-primary-bg: {color-bg-brand}
```

- Naming: `{component}-{variant}-{state}-{property}` → `button-primary-hover-bg`
- Semantic naming: `{category}-{role}-{modifier}` → `color-text-secondary`, `color-bg-brand-hover`
- Semantic roles make theme overrides manageable; verify resolved values, assets and component exceptions in each theme.

## 1. Color

**Primitives**: select only needed hue steps and status roles. An 11-step scale is one convention. OKLCH can help generate perceptual steps; gamut and rendered contrast still need verification.

**Semantic roles** (the layer components consume):

| Group | Tokens |
|---|---|
| Background | `bg-page`, `bg-surface`, `bg-surface-raised`, `bg-overlay`, `bg-brand`, `bg-brand-hover`, `bg-brand-active` |
| Text | `text-primary`, `text-secondary`, `text-tertiary`, `text-disabled`, `text-inverse`, `text-brand`, `text-on-brand` |
| Border | `border-default`, `border-strong`, `border-subtle`, `border-focus`, `border-error` |
| Status | `{success,warning,error,info}` each with `-bg`, `-text`, `-border` (subtle + solid variants) |
| Alpha | `overlay-scrim` (e.g. black 50%), `state-layer` opacities |
| Chart | `chart-1`…`chart-8` categorical + a sequential ramp; see below |

**Chart/data-viz palette** (define when the product has charts): 6–8 categorical colors
distinguishable by lightness as well as hue (colorblind-safe; start series 1 from brand),
a sequential ramp (neutral → brand) for magnitude, and a diverging pair for +/−. Do not
reuse status colors as categorical series — a red series reads as "error". Re-validate the
whole set on dark backgrounds when a dark theme exists.

## 2. Typography

- **Families**: families required by content; mono only where useful. For Thai products: verify the pair renders Thai+Latin
  at matched x-height (e.g. Noto Sans Thai / IBM Plex Sans Thai / Sarabun + a Latin match).
- **Scale**: 8–12 sizes, e.g. 12, 14, 16, 18, 20, 24, 30, 36, 48, 60 px (minor-third-ish).
- **Weights**: 400 / 500 / 600 / 700 (fewer is fine; every weight must exist in the font files).
- **Line-height**: tight 1.25 (headings) / normal 1.5 / relaxed 1.625. For Thai, start near 1.6 and verify stacked marks with actual fonts, sizes and zoom.
- **Letter-spacing**: only on Latin all-caps labels and large display; avoid adding tracking to Thai by default; verify any intentional tracking.
- **Composed type styles** (what designers/devs actually use): `display`, `h1`–`h6`,
  `body-lg/md/sm`, `label-lg/md/sm`, `caption`, `code`. Each = family+size+weight+line-height.

## 3. Spacing

One scale for padding, margin, and gap. Base-4:

```
0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96
```

Off-scale values need assessment and documented rationale. If audit data (EXTRACT mode) shows heavy use of e.g. 6px,
either adopt it into the scale deliberately or map it — never leave it ad hoc.

## 4. Sizing

- Control heights: `sm 32`, `md 40`, `lg 48` px (all interactive rows/inputs/buttons align to these).
- Icon sizes: 16, 20, 24, 32.
- WCAG 2.5.8 AA uses 24×24 CSS px or its defined exceptions. 44×44 is an enhanced target (2.5.5 AAA) and useful touch default; avoid overlapping expanded hit areas.
- Content max-widths: prose ~65ch; container widths per breakpoint.

## 5. Border

- Widths: 1 (default), 2 (emphasis/focus), 4 (rare/decorative).
- Color comes from semantic border tokens and changes per state (default/hover/focus/error/disabled) — specify all five for inputs.

## 6. Radius

`none 0 / sm 4 / md 8 / lg 12 / xl 16 / full 9999`. Assign per component class:
controls (buttons/inputs) one value, containers (cards/modals) one value, pills/avatars `full`.
Consistency here is what makes a UI look "designed".

## 7. Shadow / Elevation

Levels 0–4 mapped to component classes: 0 flat, 1 card, 2 dropdown/popover, 3 modal,
4 toast. Include a **focus ring** spec here (it is system-wide, not per component):
color (`border-focus`), width 2px and offset 2px are starting values. Adapt rings to surfaces; verify visibility (2.4.7), non-obscuration (2.4.11 AA), applicable 3:1 adjacent non-text contrast (1.4.11) and, if targeted, focus appearance (2.4.13 AAA).

## 8. Opacity

- `disabled`: 0.38–0.5 (pick one, use everywhere)
- `overlay-scrim`: 0.5–0.6
- State-layer opacities if using the Material approach: hover 0.08, focus 0.10, pressed 0.10, dragged 0.16.

## 9. Z-index

Example ladder; adopt the existing scale. Stacking contexts and native dialog/popover top layers cannot be fixed merely by raising a z-index:

```
dropdown 1000 / sticky 1100 / fixed 1200 / modal-backdrop 1300 / modal 1400 / popover 1500 / toast 1600 / tooltip 1700
```

## 10. Motion

- Durations: `fast 100ms` (hover/small), `base 200ms` (most), `slow 300ms` (large surfaces/modals).
- Easings: `standard cubic-bezier(0.2,0,0,1)`, `enter` decelerate, `exit` accelerate.
- Rule: color/opacity transitions on state change use `fast`; layout/transform use `base`.
- Always pair with `prefers-reduced-motion: reduce` → remove nonessential movement and provide static status alternatives; preserve understandable state feedback.

**Keyframe animations** (named, reused system-wide — components never write ad-hoc `@keyframes`):

| Token | Use | Spec |
|---|---|---|
| `spin` | Spinner, loading icons | 360° rotate, linear, ~800ms loop |
| `shimmer` / `pulse` | Skeleton | pick ONE for the whole system; ~1.5–2s loop, subtle (opacity 0.5–1 or gradient sweep) |
| `enter` / `exit` | Modal, popover, toast | fade + small translate/scale (4–8px, 0.96–1); `enter` uses enter easing at `base`, `exit` accelerates at `fast` — tune to the actual task |
| `slide-in-{side}` | Toast, drawer, bottom sheet | translate from the edge it belongs to |

- Toast queue choreography: new toasts push existing ones (animate the stack offset, `base`);
  removal collapses the gap — never let siblings jump.
- Stagger (list/menu items entering): 20–30ms per item, cap total ≤ 300ms; skip stagger
  entirely under reduced motion.
- Under reduced motion, replace spin/shimmer with static loading text or another understandable status; do not assume status animations must continue.

## 11. Layout

- Breakpoints: `sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536` (or the project's existing ones — don't introduce a second set).
- Container paddings per breakpoint; grid columns/gutter if the product uses a column grid.

## 12. Iconography

One icon set (e.g. Lucide/Phosphor/Material Symbols), one stroke width, sizes from §4.
Mixing sets reads as broken faster than any color mistake.

## 13. Assets

Logo variants (full/mark, on-light/on-dark), illustration style notes, image radius/aspect defaults.

**Image rules**: every image slot reserves its box (`aspect-ratio` or explicit dimensions)
so loading never shifts layout; lazy-load below the fold (`loading="lazy"`); define the
fallback (skeleton → placeholder icon on error) and require meaningful `alt` (empty `alt`
only for decorative images).

## Output format

Emit tokens as CSS custom properties grouped by tier, with the semantic layer in a
`:root` block components consume. When the project uses Tailwind v4, mirror the semantic
layer using Tailwind namespaces. For aliases to existing scoped CSS variables, use `@theme inline` and verify generated utilities under theme overrides. Example skeleton:

```css
:root {
  /* primitives */
  --blue-600: oklch(0.55 0.18 260);
  --blue-700: oklch(0.48 0.18 260);
  /* semantic */
  --color-bg-brand: var(--blue-600);
  --color-bg-brand-hover: var(--blue-700);
  /* component */
  --button-primary-bg: var(--color-bg-brand);
}
```
