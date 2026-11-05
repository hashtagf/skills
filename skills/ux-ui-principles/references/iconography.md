# Iconography — using icons correctly

Icons speed recognition only when people already know their meaning. Most
icons are ambiguous without a label. Source IDs resolve in [sources.md](sources.md).

## When to use an icon

| Situation | Use |
|---|---|
| Universally recognized action in context (search, close, menu on mobile, print, home) | Icon may stand alone if it also has an accessible name; still test with your users [S81] |
| Any other action or navigation item | Icon **with** visible text label, or text only |
| Status (success, warning, error) | Icon + text; icon reinforces meaning, color is never the only cue [S67] |
| Decoration next to a heading | Usually unnecessary; if used, hide from assistive technology [S63] |
| Dense toolbars for expert users | Icon-only acceptable when labels appear on hover **and** focus, the set is small and consistent, and users use it daily |

Default to icon + label. Icons without labels make people guess, and different
icon sets use the same glyph for different meanings. [S81]

## Choosing glyphs

- Use **one icon family** across the product (same grid, stroke width, corner
  radius, fill style). Mixing outline and filled sets reads as inconsistent.
- One meaning per glyph, one glyph per meaning. Record them in the design
  context (e.g. "trash = delete permanently; archive box = archive").
- Prefer established metaphors over clever ones. A metaphor nobody shares is a
  puzzle.
- Avoid culture-specific gestures, text inside icons, currency symbols that
  assume one market, and flags for languages.
- Filled vs outline can show selected vs unselected state (e.g. bottom tab bar),
  but pair it with another cue such as a label color or indicator.
- On native platforms, prefer the platform's symbol set (SF Symbols on Apple
  platforms, Material Symbols on Android). Apple asks for recognizable,
  highly simplified icons with accessibility labels, and suggests text when a
  short label communicates more clearly than an icon. [S75]

## Size, alignment and contrast

| Rule | Detail |
|---|---|
| Size from the type scale | Common pairs: 16 px icon with 14–16 px text, 20 px with 16–18 px, 24 px for standalone controls, 32 px for large markers (sizes: [design-foundations.md](design-foundations.md)) |
| Optical alignment | Center the icon on the text's x-height or cap height, not the line box; check Thai text with ascenders/descenders |
| Spacing | Consistent gap between icon and label (e.g. 6–8 px) from spacing tokens |
| Hit target | The **target** meets minimums even if the glyph is small: WCAG 2.5.8 24×24 CSS px (AA, with exceptions), iOS default 44×44 pt (HIG minimum 28×28 pt), Android at least 48×48 dp [S07, S74, S78] |
| Contrast | Icons that convey information or are the only identifier of a control need 3:1 against adjacent colors (WCAG 1.4.11) [S04] |
| Color | Inherit text color (`currentColor`) by default; use semantic colors only for status |

## Accessibility implementation

| Case | Markup |
|---|---|
| Decorative icon next to visible text | `aria-hidden="true"` on the SVG; text provides the name [S63] |
| Icon-only button | `<button aria-label="ลบรายการ">` with `aria-hidden` SVG inside; accessible name describes the action, not the picture ("ลบ" not "ถังขยะ") |
| Icon that conveys status alone | Give it a text alternative (`role="img"` + `aria-label`, or visually hidden text) |
| Icon + visible label | Accessible name must include the visible label text (WCAG 2.5.3) [S64] |
| Tooltip on icon-only button | Shows on hover **and** keyboard focus, is dismissible, and does not replace the accessible name |

## Icon inventory in the design system

Keep an icon list with: name, glyph, meaning, allowed contexts, sizes, and
whether it may appear without a label. Add new icons through review so
meanings don't drift. Record the inventory in the design context; component
states are in [component-states.md](component-states.md).

## Review checklist

1. Every icon-only control is from the "universally recognized" list or has a visible label.
2. One family, one stroke style, consistent sizes from the scale.
3. Each glyph has one meaning across the product.
4. Decorative icons are hidden from assistive technology; meaningful ones are named.
5. Targets meet the platform minimum; informative icons meet 3:1 contrast.
6. Status icons are paired with text; color is not the only cue.
7. Icons align optically with Thai and Latin text.

## Do / Don't

| Do | Don't |
|---|---|
| Pair icons with text labels by default. | Ship a toolbar of unlabeled icons for occasional users. |
| Name icon buttons by action ("แก้ไขที่อยู่"). | Name them by picture ("ดินสอ"). |
| Use one icon family and one meaning per glyph. | Use a star for "favorite" on one page and "rating" on another. |
| Keep the hit area large even when the glyph is small. | Make a 16 px icon the whole tap target. |
| Use icons to reinforce status alongside text. | Show a red dot as the only signal of an error. |
