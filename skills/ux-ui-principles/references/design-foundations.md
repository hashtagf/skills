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
| 3 | Spacing | One scale for padding, gap, margin | 0, 2, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80 px; marketing sections add 96, 128, 160 |
| 4 | Sizing | Control heights, icon sizes, content widths | Controls 32/40/48 px; icons 16/20/24/32; prose ~65ch |
| 5 | Border | Widths and state colors | 1 default, 2 focus/emphasis |
| 6 | Radius | Per component class | 0 / 4 / 8 / 12 / 16 / full; controls one value, containers one value |
| 7 | Elevation | Levels mapped to roles | 0 flat · 1 card · 2 popover/menu · 3 dialog · 4 toast |
| 8 | Opacity | Disabled, scrim | Disabled 0.4–0.5 (one value); scrim 0.5–0.6 |
| 9 | Layering | z-order ladder | dropdown < sticky < drawer/dialog < popover < toast < tooltip |
| 10 | Motion | Durations, easing, named animations | Durations, easing and token names: [motion.md](motion.md) §2 |
| 11 | Breakpoints | Content-driven widths | e.g. compact < 600, medium 600–1023, expanded ≥ 1024 px; tablet band 768–1024 ([tablet-rtl-dark.md](tablet-rtl-dark.md)); set by content, not devices |
| 12 | Density | Comfortable / compact modes | Row heights e.g. 48 / 36 px; same type scale |
| 13 | Focus | One focus ring contract | 3 px ring, 2 px offset, focus color with ≥3:1 against adjacent colors [S04]; owner: [component-states.md](component-states.md) |

Record which categories are deferred or N/A for the current scope.

## Typography

- **Families:** one UI family that covers Thai and Latin well (e.g. IBM Plex Sans
  Thai, Noto Sans Thai, Sarabun, Anuphan) plus an optional display family and an
  optional mono for IDs/code. Check matched x-height and that every weight used
  exists in the font files.
- **Scale (owner of the rule):** 6–9 steps defined, e.g. 12, 14, 16, 18, 20, 24, 30, 36 px;
  a public page uses only 3–5 of them, with a decisive body-to-headline jump.
  Marketing may extend upward (48–128). Product UIs need fewer large steps.
- **Minimum text size:** body 16 px on public pages at phone width, 14 px in product UI
  (13 only in dense tables); meta, captions and labels 12 px, 13 on public phone pages;
  nothing below 12. WCAG sets no text-size floor; this is a project default.
- **Composed styles:** `display`, `h1`–`h4`, `body-lg/md/sm`, `label-md/sm`,
  `caption`, `numeric` (tabular figures), `code`. Screens use styles, not raw sizes.
- **Line height:** headings ~1.25–1.3 (Latin display ≥48px is set tighter, 0.85–1.15 — see [visual-benchmarks.md](visual-benchmarks.md) §1); body ~1.5; Thai body 1.55–1.7, and ≤1.35 is a defect (rules below) —
  verify stacked tone marks and vowels with real fonts and zoom (see [visual-composition.md](visual-composition.md#thai-and-mixed-language-interfaces)).
- **Letter spacing:** only for Latin uppercase labels; don't track Thai by default.
- **Numbers:** tabular figures in tables, amounts and timers.

### Thai with Latin display faces

Most display faces in a direction ([direction library](direction-library.md))
have no Thai glyphs; the browser then falls back to a system Thai font that does
not match. Choose the Thai pair deliberately and write it in the design context.

| Latin display voice | Thai display pair | Thai body pair | Notes |
|---|---|---|---|
| Condensed caps (League Gothic, Anton, Six Caps) | Kanit 500, or Noto Sans Thai 700 | IBM Plex Sans Thai, Noto Serif Thai | Thai has no case: drop `text-transform: uppercase`; Kanit is the closest in weight |
| Grotesk or geometric sans (Schibsted, Jost, Outfit) | Noto Sans Thai 700, IBM Plex Sans Thai 600 | IBM Plex Sans Thai 400/500 | The safest pair |
| Rounded sans | Noto Sans Thai Looped, Sarabun | IBM Plex Sans Thai | Check the loops against the Latin shapes at display size |
| Heavy slab or serif display | Noto Serif Thai 600–700, Mitr | Noto Serif Thai | Mitr is heavy and rounded; compare before choosing |
| Light high-contrast serif | Noto Serif Thai 400–500, Pridi, Taviraj | Noto Serif Thai | Thai has no hairline-contrast equivalent; expect less contrast |
| Mono for times and codes (DM Mono) | none | the Thai body font | Keep mono for numerals and Latin codes only; never for Thai words |

Verified in rendering: Kanit 500, Noto Sans Thai 700, IBM Plex Sans Thai 400–600
and Noto Serif Thai 400–600 paired with League Gothic, Schibsted Grotesk,
Instrument Sans and Newsreader. The others are suggestions; render a headline
and a paragraph before committing.

Rules:

- Put the Latin family first and the Thai family second in the stack, and switch
  the whole family per language: `html[lang=th] h1 { font-family: "Kanit", sans-serif; }`,
  so a toggle does not leave Latin metrics on Thai text. `slop_check.py` skips
  `:lang`/`[lang]` rules, so this pair does not count toward its two-typeface flag.
- Thai display: `letter-spacing: 0`, line-height 1.15–1.25 (Latin display: the 0.85–1.15 range above,
  by size band in [visual-benchmarks.md](visual-benchmarks.md) §1); body 1.55–1.7. Never track or uppercase Thai.
- Thai has no spaces between words, so a narrow heading breaks in the middle of
  a word. Wrap phrases that must stay together in an inline-block chunk
  (`<span class="nb">…</span>` with `display:inline-block`) with a real space
  between chunks; `word-break: keep-all` does not help for Thai.
- **Headline length (owner of this rule).** Latin headlines fit ≤ 2 lines at every
  width. Thai headlines may take ≤ 3 lines at 1440 and ≤ 4 at 390, breaking only
  at the chunks above; past that, cut words — never shrink the type to force 2.
- Match optical size, not font-size: set the Thai display about 0.85–0.95× the
  Latin clamp so a Thai headline and its English version fill a similar width.

## Spacing and layout

- One spacing scale for everything; larger gaps between sections than inside
  groups so grouping reads by proximity. [S30]
- **Layout grid:** define columns and gutters per breakpoint (e.g. 4/8/12
  columns), page max width, and side gutters (≥16 px on phones).
- **Content widths (owner of the measure):** reading text 60–75 characters, ~65ch default (Latin); tables and dashboards
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
- Durations, easing and token names: [motion.md](motion.md) §2.
- One named set of animations (spin, skeleton shimmer or pulse, enter/exit,
  slide from edge); no ad-hoc animations per screen.
- Reduced motion and the 5 s pause rule: [motion.md](motion.md) §4. [S16] [S92]
- Full guidance (levels, types, choreography, spec, checks): [motion](motion.md).

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
