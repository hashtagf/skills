# Building and checking a color palette

Use when a product has no palette, when changing brand color, or when adding a
theme (dark mode, alternate brand). Token structure is in [design-foundations.md](design-foundations.md); this
file covers color decisions and checks. Run
`scripts/contrast.py` for the numeric checks. Source IDs resolve in [sources.md](sources.md).

## Roles before hues

Define roles first, then pick values. Components use roles, never raw hex.

| Role | Purpose | Typical count |
|---|---|---|
| Background, surface, sunken | Page, panels, wells | 3 |
| Line, line-strong | Dividers, input borders | 2 |
| Text, text-muted, text-faint | Primary, secondary, disabled/meta | 3 |
| Accent, accent-soft, on-accent | Primary action, selection, focus links; tint; text on accent | 3 |
| Semantic: success, warning, critical, info (+ soft) | Status only | 8 |
| Data palette | Charts (categorical, sequential, diverging) | separate set |
| Focus | Focus indicator if not the accent | 1 |

Rules:
- **Semantic colors stay fixed across brand palettes** so status meaning never
  changes when the brand does.
- **One accent.** If two colors compete for "click here", neither works.
- **Neutrals carry a slight hue** toward the accent; pure grey looks unconsidered.
- **Accent is not a status.** Don't use the brand color to mean success.

## Choosing the accent

- Start from brand or domain meaning (finance: trust, calm; health: clean,
  reassuring; consumer: energetic), then test against semantic colors: a red
  brand next to error red, or a green brand next to success green, needs
  separation in lightness or a different status treatment.
- Check that accent text/icons on background meet 4.5:1 for text and 3:1 for
  UI components; on-accent text on accent fills meets 4.5:1. [S03, S04]
- Prepare an accent-soft tint for selected rows and highlights that still keeps
  text at 4.5:1.

## Contrast requirements to check

| Pair | Minimum | Source |
|---|---|---|
| Body text on its background | 4.5:1 (AA); large text 3:1 | WCAG 1.4.3 [S03] |
| Muted/secondary text that must be read | 4.5:1 | WCAG 1.4.3 [S03] |
| Input borders, focus indicators, informative icons, chart elements | 3:1 against adjacent colors | WCAG 1.4.11 [S04] |
| Text on accent buttons | 4.5:1 | WCAG 1.4.3 [S03] |
| Disabled controls | Exempt, but should still look like controls | WCAG 1.4.3 exception [S03] |
| Placeholder text | Treated as text if it conveys information | — |

Contrast alone doesn't guarantee meaning: never use color as the only cue. [S67]

## Data ramps with text on top

For heatmaps, level badges and status cells where numbers sit on the color:
- Choose the text color first (one for the whole ramp), then build ramp steps
  that each pass 4.5:1 against it.
- Keep steps visibly different in lightness (e.g. 4–5 steps from very light to
  medium), and keep the darkest step for the most important level only.
- In dark themes, invert: dark ramp, one light text color, check every step.
- Check every pair with `scripts/contrast.py --css <page>`; ramp tokens named
  `--l1`/`--l1i` (fill/ink) or `--x`/`--on-x` are paired automatically.

## Dark theme

- Define it as a second set of the same roles, not an inversion.
- Use dark surfaces that are not pure black; raise elevation with lighter surfaces.
- Desaturate and lighten accents and semantic colors so they don't vibrate.
- Recheck every contrast pair; values that pass in light often fail in dark.
- Images, charts and illustrations need dark-aware variants.

## Procedure

1. List roles and write light values; write dark values for the same roles.
2. Run `python3 scripts/contrast.py --css page.html` to check the role pairs
   it finds in every theme block, or list custom pairs in a JSON file and run
   `python3 scripts/contrast.py pairs.json`; fix failures.
3. Render key screens in both themes (see [render-verification.md](render-verification.md))
   and look at: selection states, disabled, error fields, charts, focus rings.
4. Simulate color vision deficiency (browser devtools) for status and chart colors.
5. Record the palette and decisions in the design context.

## Comparing palette options

When stakeholders want to "try colors", offer 2–3 complete palettes that swap
only brand roles (accent, neutrals bias, navigation) and keep semantic colors
fixed. Show them on the same real screen, in both themes, and report the
contrast results for each. Choose by brand fit and legibility, not by a single
swatch.

## Do / Don't

| Do | Don't |
|---|---|
| Define roles, then values. | Pick ten hex codes and assign them ad hoc. |
| Keep semantic colors fixed across brand themes. | Let "success" turn purple in the purple theme. |
| Check every pair in both themes with a tool. | Eyeball contrast on a bright monitor. |
| Pair color with text or icons for meaning. | Use red/green alone to show pass/fail. |
