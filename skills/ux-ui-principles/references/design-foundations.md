# Design foundations — tokens, type, space, layout, motion

Everything a designer needs to define a coherent visual system for a product,
at design level. If the project already has a design system, use it and record
exceptions; otherwise define the foundations below before drawing screens.
Values are starting points, not requirements; keep the **structure**, adjust
values to the product. Color roles and contrast are in [color-palette.md](color-palette.md).
Source IDs resolve in [sources.md](sources.md).

## Token layers

| Layer | Example | Purpose |
|---|---|---|
| Primitive | `teal-700: #0f6e64` | Raw palette and scales, no meaning |
| Semantic | `color-accent: {teal-700}`, `space-section: {space-8}` | Meaning; the layer themes swap |
| Component (optional) | `button-primary-bg: {color-accent}` | Only where a component needs separate control |

Screens and components use semantic tokens, never raw values. Name by role:
`color-text-muted`, not `color-grey-500`. When tokens must move between tools,
the Design Tokens Format Module is a stable Community Group format. [S58]

## Categories to define

| # | Category | Define | Starting point |
|---|---|---|---|
| 1 | Color | Roles, light/dark values, semantic + data palettes | [color-palette.md](color-palette.md) |
| 2 | Typography | Families, scale, weights, line-heights, composed styles | Below |
| 3 | Spacing | One scale for padding, gap, margin | 0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80 px |
| 4 | Sizing | Control heights, icon sizes, content widths | Controls 32/40/48 px; icons 16/20/24/32; prose ~65ch |
| 5 | Border | Widths and state colors | 1 default, 2 focus/emphasis |
| 6 | Radius | Per component class | 0 / 4 / 8 / 12 / 16 / full; controls one value, containers one value |
| 7 | Elevation | Levels mapped to roles | 0 flat · 1 card · 2 popover/menu · 3 dialog · 4 toast |
| 8 | Opacity | Disabled, scrim | Disabled 0.4–0.5 (one value); scrim 0.5–0.6 |
| 9 | Layering | z-order ladder | dropdown < sticky < drawer/dialog < popover < toast < tooltip |
| 10 | Motion | Durations, easing, named animations | 100 / 200 / 300 ms; standard, enter (decelerate), exit (accelerate) |
| 11 | Breakpoints | Content-driven widths | e.g. compact < 600, medium 600–1023, expanded ≥ 1024 px; set by content, not devices |
| 12 | Density | Comfortable / compact modes | Row heights e.g. 48 / 36 px; same type scale |
| 13 | Focus | One focus ring contract | 2 px ring, 2 px offset, focus color with ≥3:1 against adjacent colors [S04] |

Record which categories are deferred or N/A for the current scope.

## Typography

- **Families:** one UI family that covers Thai and Latin well (e.g. IBM Plex Sans
  Thai, Noto Sans Thai, Sarabun, Anuphan) plus an optional display family and an
  optional mono for IDs/code. Check matched x-height and that every weight used
  exists in the font files.
- **Scale:** 6–9 steps, e.g. 12, 14, 16, 18, 20, 24, 30, 36 px. Product UIs need
  fewer large steps than marketing pages.
- **Composed styles:** `display`, `h1`–`h4`, `body-lg/md/sm`, `label-md/sm`,
  `caption`, `numeric` (tabular figures), `code`. Screens use styles, not raw sizes.
- **Line height:** headings ~1.25–1.3; body ~1.5; Thai body often needs ~1.6 —
  verify stacked tone marks and vowels with real fonts and zoom (see [visual.md](visual.md)).
- **Letter spacing:** only for Latin uppercase labels; don't track Thai by default.
- **Numbers:** tabular figures in tables, amounts and timers.

## Spacing and layout

- One spacing scale for everything; larger gaps between sections than inside
  groups so grouping reads by proximity. [S30]
- **Layout grid:** define columns and gutters per breakpoint (e.g. 4/8/12
  columns), page max width, and side gutters (≥16 px on phones).
- **Content widths:** reading text ~60–75 characters (Latin); tables and dashboards
  may use full width.
- **App shell:** sidebar width, header height, page header structure and
  content padding are tokens too, so every page aligns.
- **Reflow:** content must work at 320 CSS px width without two-dimensional
  scrolling except for data tables, maps and similar. [S05]

## Elevation and surfaces

- Use elevation for things that float (menus, popovers, dialogs, toasts, sticky
  bars); use borders or background contrast for sections.
- In dark themes, show elevation with lighter surfaces rather than shadows alone.

## Motion

- Motion explains change: where something came from, what updated, what opened.
- Short durations for small changes (≈100 ms), medium for surfaces (≈200–300 ms).
- One named set of animations (spin, skeleton shimmer or pulse, enter/exit,
  slide from edge); no ad-hoc animations per screen.
- Respect reduced-motion preferences; keep state feedback understandable without
  movement. [S16]
- Anything that moves, blinks or scrolls automatically for more than 5 seconds
  needs pause/stop/hide (WCAG 2.2.2). [S92]

## Theming

- Themes (light/dark, brand variants, high contrast) redefine semantic tokens only.
- Every theme is checked: contrast pairs, focus visibility, charts, images.
- Forced-colors / high-contrast modes drop backgrounds and shadows; state must
  survive as borders, outlines or text.

## Foundations checklist

1. Token layers defined; screens use semantic tokens only.
2. Type scale and composed styles exist; Thai rendering checked.
3. Spacing scale used everywhere; no one-off values without a note.
4. Control heights, icon sizes and radii assigned by component class.
5. Elevation ladder and layering order defined.
6. Breakpoints and grid defined from content; reflow checked at 320 px.
7. Focus ring contract defined and visible on every surface.
8. Motion set defined with reduced-motion behavior.
9. Every theme passes contrast checks ([color-palette.md](color-palette.md)).
10. Decisions recorded in the design context.
