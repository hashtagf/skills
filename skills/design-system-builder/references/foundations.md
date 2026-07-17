# Foundation Tokens — 13 Categories

Define every category below for the theme. Skipping one means components invent their own
values later and the system drifts. Recommended values are defaults, not mandates — replace
them with interview/audit findings, but keep the *structure*.

## Token architecture (define before any values)

Three tiers. Components must only reference semantic (or their own component tokens);
semantic references primitives; nothing skips a tier downward.

```
primitive        blue-600: #2563eb              raw value, no meaning
semantic/alias   color-bg-brand: {blue-600}     meaning; the theme-swap layer
component        button-primary-bg: {color-bg-brand}
```

- Naming: `{component}-{variant}-{state}-{property}` → `button-primary-hover-bg`
- Semantic naming: `{category}-{role}-{modifier}` → `color-text-secondary`, `color-bg-brand-hover`
- One theme today, but a correct 3-tier structure makes dark mode = re-pointing the
  semantic layer only.

## 1. Color

**Primitives**: each hue as a 50–950 scale (11 steps). Minimum hues: 1 brand, 1 neutral
(gray), plus red/amber/green/blue for status. Generate scales with consistent perceived
lightness steps (OKLCH is the reliable way).

**Semantic roles** (the layer components consume):

| Group | Tokens |
|---|---|
| Background | `bg-page`, `bg-surface`, `bg-surface-raised`, `bg-overlay`, `bg-brand`, `bg-brand-hover`, `bg-brand-active` |
| Text | `text-primary`, `text-secondary`, `text-tertiary`, `text-disabled`, `text-inverse`, `text-brand`, `text-on-brand` |
| Border | `border-default`, `border-strong`, `border-subtle`, `border-focus`, `border-error` |
| Status | `{success,warning,error,info}` each with `-bg`, `-text`, `-border` (subtle + solid variants) |
| Alpha | `overlay-scrim` (e.g. black 50%), `state-layer` opacities |

## 2. Typography

- **Families**: sans + mono minimum. For Thai products: verify the pair renders Thai+Latin
  at matched x-height (e.g. Noto Sans Thai / IBM Plex Sans Thai / Sarabun + a Latin match).
- **Scale**: 8–12 sizes, e.g. 12, 14, 16, 18, 20, 24, 30, 36, 48, 60 px (minor-third-ish).
- **Weights**: 400 / 500 / 600 / 700 (fewer is fine; every weight must exist in the font files).
- **Line-height**: tight 1.25 (headings) / normal 1.5 / relaxed 1.625. **Thai body ≥ 1.6.**
- **Letter-spacing**: only on Latin all-caps labels and large display; **never on Thai text**.
- **Composed type styles** (what designers/devs actually use): `display`, `h1`–`h6`,
  `body-lg/md/sm`, `label-lg/md/sm`, `caption`, `code`. Each = family+size+weight+line-height.

## 3. Spacing

One scale for padding, margin, and gap. Base-4:

```
0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96
```

Off-scale values are bugs. If audit data (EXTRACT mode) shows heavy use of e.g. 6px,
either adopt it into the scale deliberately or map it — never leave it ad hoc.

## 4. Sizing

- Control heights: `sm 32`, `md 40`, `lg 48` px (all interactive rows/inputs/buttons align to these).
- Icon sizes: 16, 20, 24, 32.
- Minimum touch target 44×44 px (a 32px-tall control needs padding/hit-area extension on touch).
- Content max-widths: prose ~65ch; container widths per breakpoint.

## 5. Border

- Widths: 1 (default), 2 (emphasis/focus), 4 (rare/decorative).
- Color comes from semantic border tokens and changes per state (default/hover/focus/error/disabled) — specify all five for inputs.

## 6. Radius

`none 0 / sm 4 / md 8 / lg 12 / xl 16 / full 9999`. Assign per component class:
controls (buttons/inputs) one value, containers (cards/modals) one value, pills/avatars `full`.
Consistency here is what makes a UI look "designed".

## 7. Shadow / Elevation

Levels 0–5 mapped to component classes: 0 flat, 1 card, 2 dropdown/popover, 3 modal,
4 toast. Include a **focus ring** spec here (it is system-wide, not per component):
color (`border-focus`), width 2px, offset 2px, contrast ≥ 3:1 against adjacent colors.

## 8. Opacity

- `disabled`: 0.38–0.5 (pick one, use everywhere)
- `overlay-scrim`: 0.5–0.6
- State-layer opacities if using the Material approach: hover 0.08, focus 0.10, pressed 0.10, dragged 0.16.

## 9. Z-index

Fixed ladder; components never invent values:

```
dropdown 1000 / sticky 1100 / fixed 1200 / modal-backdrop 1300 / modal 1400 / popover 1500 / toast 1600 / tooltip 1700
```

## 10. Motion

- Durations: `fast 100ms` (hover/small), `base 200ms` (most), `slow 300ms` (large surfaces/modals).
- Easings: `standard cubic-bezier(0.2,0,0,1)`, `enter` decelerate, `exit` accelerate.
- Rule: color/opacity transitions on state change use `fast`; layout/transform use `base`.
- Always pair with `prefers-reduced-motion: reduce` → transitions ~0ms, no auto-motion.

## 11. Layout

- Breakpoints: `sm 640 / md 768 / lg 1024 / xl 1280 / 2xl 1536` (or the project's existing ones — don't introduce a second set).
- Container paddings per breakpoint; grid columns/gutter if the product uses a column grid.

## 12. Iconography

One icon set (e.g. Lucide/Phosphor/Material Symbols), one stroke width, sizes from §4.
Mixing sets reads as broken faster than any color mistake.

## 13. Assets

Logo variants (full/mark, on-light/on-dark), illustration style notes, image radius/aspect defaults.

## Output format

Emit tokens as CSS custom properties grouped by tier, with the semantic layer in a
`:root` block components consume. When the project uses Tailwind v4, mirror the semantic
layer in `@theme`. Example skeleton:

```css
:root {
  /* primitives */
  --blue-600: oklch(0.55 0.18 260);
  /* semantic */
  --color-bg-brand: var(--blue-600);
  --color-bg-brand-hover: var(--blue-700);
  /* component */
  --button-primary-bg: var(--color-bg-brand);
}
```
