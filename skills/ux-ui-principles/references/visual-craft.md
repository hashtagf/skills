# Visual craft — from correct to well-made

A screen can satisfy every UX rule and still look unfinished: every section in
an identical box, every element the same weight, generic color, no focal
point. This file covers the composition decisions that separate a correct
wireframe from a credible product UI. It complements [visual.md](visual.md)
(hierarchy, type, grouping) and [visual-composition.md](visual-composition.md)
(task-led layout); token structure is in [design-foundations.md](design-foundations.md)
and component choice in [components-usage.md](components-usage.md).

These are project recommendations for craft quality, not research findings.
Visual polish never overrides task evidence, accessibility or the project's
existing design system; within those, it is part of the job.

## Start from the existing system

1. Use the project's tokens, components and patterns when they exist.
2. If none exist, define a compact token set first (4–6 color roles, 2 type
   roles + optional data face, spacing scale, radius, elevation) and build only
   from it. Record it in [design-context.md](../assets/design-context.md).
3. A new aesthetic needs a reason tied to the product, brand or audience.
4. When tokens move between tools, the Design Tokens Format Module 2025.10 is a
   stable Community Group report (not a W3C Standard) [S58]; Figma variable
   modes can hold theme, language or device values [S59]. Token structure is in
   [design-foundations.md](design-foundations.md).

## One focal point per screen

Decide the single most important thing on each screen (the decision, the
amount, the next action) and give it the strongest contrast of size, weight or
color. Everything else steps down. If three elements compete equally, the
hierarchy is undecided. [S23]

Examples: the appointment time on a booking ticket; the amount and decision on
an approval; the exception list for an operator dashboard.

## Containers by role, not by habit

| Problem | Fix |
|---|---|
| Every section wrapped in an identical bordered card | Use whitespace and a heading to separate sections; reserve a container for an object users act on or compare |
| Cards inside cards inside cards | One level of containment per region; use dividers or spacing inside |
| Same radius, shadow and border on everything | Elevation marks what floats (menus, drawers, sticky bars); borders mark selectable or separate objects |
| Accent stripe on every card | Use color stripes only to encode state (severity, selection) |

## Color roles

- **Neutral base** with a slight hue bias toward the brand; avoid pure mid-grey
  everywhere.
- **One accent** for primary actions, selection and focus links. Use it
  sparingly so it signals "act here".
- **Semantic colors** (success, warning, critical, info) are separate from the
  accent and always paired with text or icon. [S03, S04]
- **Data colors** for charts come from a validated categorical/sequential set,
  not the accent repeated.
- Design light and dark themes deliberately; don't simply invert.

## Typography

- Two families at most (display/heading + body), plus a monospace or tabular
  face for IDs and numbers if useful. For Thai, choose fonts with good Thai
  glyph design and test real copy (see [visual.md](visual.md)).
- A small type scale used consistently (step count and sizes:
  [design-foundations.md](design-foundations.md)). Large size jumps for
  the focal element, small steps elsewhere.
- Labels quieter than values in data displays; numbers in tabular figures.
- Line length: measure in [design-foundations.md](design-foundations.md); test
  Thai with real paragraphs.

## Space and alignment

- Use a spacing scale from tokens; larger gaps between sections than within
  groups so grouping is visible (proximity). [S30]
- Align to a small number of vertical edges. Ragged starts make even simple
  forms look careless.
- Repeated items (cards, rows, KPI tiles) share identical padding, internal
  alignment and baseline positions.
- Fill the layout with real content; sparse placeholder data hides density
  problems and makes layouts look emptier than they will be.

## Density

| Mode | Use for | Notes |
|---|---|---|
| Comfortable | Customer UI, infrequent tasks, touch | Larger targets and spacing |
| Compact | Expert back-office lists and queues | Smaller row height, still meeting target-size and contrast criteria [S07] |
| Expanded | Reading detail, onboarding | More explanation, larger type |

Back-office screens usually need more information per view than marketing
pages. Increase density by removing decoration, not by shrinking text below
legibility.

## Selection and state styling

Selected, hover, focus, disabled and error must be visually distinct and not
rely on color alone. Selected options in a choice group should look clearly
chosen (filled or strongly outlined), not just slightly tinted. Focus
indicators remain visible on every surface.

## Data display

- Charts: one scale per axis, labels that name values the chart reaches, target
  or comparison lines where they help decisions, emphasized latest value.
- KPI tiles: value + unit + comparison + time window; highlight only abnormal ones.
- Status: pill or text label with consistent vocabulary; severity stripes for
  queues and alerts.

## Motion

Use motion to explain change, avoid decorative motion on operational screens;
durations, reduced motion and all other rules: [motion.md](motion.md). [S16]

## Avoid the generic look

See [design-quality.md](design-quality.md) for the full plan-review process,
template-device list and critique loop. In short, unconsidered defaults make
products look templated: identical rounded boxes,
centered everything, a purple-to-blue gradient hero, emoji as section markers,
one stock font for everything, numbered markers on content that is not a
sequence. Choose deliberately from the product's own world (its units,
documents, vocabulary) and keep boldness in one place per screen.

## Signal budget

Every visual property you use (fill, text color, border, ring, icon, badge,
opacity, dashed line, size, weight) is a signal. Small elements — cells, chips,
list rows, table status columns — can carry **one value and at most one status**.
When more information is needed, move it to the row/column header, a tooltip
plus detail view, or a separate column. Prefer text ("−1", "เกินกำหนด") over
abstract marks. Never use opacity as a state on informative content.

## Diagnosing visual feedback

When people say a screen is hard to read or "not beautiful", diagnose before
repainting:

| Feedback | Likely causes | First fixes |
|---|---|---|
| "ดูยาก / อ่านยาก" (hard to read) | Too many signals per element; text color changes with background; low contrast; faded states; small type | Apply the signal budget; one text color per ramp; check pairs with `scripts/contrast.py`; remove opacity states |
| "สีดูยาก / สีแรง" (colors are hard) | Saturated or dark fills dominate; semantic colors used for decoration; ramp steps too similar or too extreme | Lighter ramp, darkest step reserved; semantic colors only for exceptions; test both themes |
| "รก" (cluttered) | Every section boxed; repeated metadata; equal emphasis everywhere | Containers by role; move repeated facts to headers; choose one focal point |
| "ไม่สวย / ดูเหมือน wireframe" (plain, unfinished) | No focal point; default fonts and greys; placeholder data; identical boxes; template devices (eyebrows, mono labels, card rows, hairlines, gradients) | Write the idea sentence and run the competitor test ([design-quality.md](design-quality.md)); focal point, real content or working fragments, decisive type scale |
| "หาไม่เจอ" (can't find it) | Weak hierarchy, action far from context, unlabeled icons | Move action next to its object, label icons, strengthen heading hierarchy |

Change the cause, re-render, re-run contrast, and show before/after. When the
right direction is unclear, offer 2–3 complete variants side by side
([prototyping.md](prototyping.md)).

## Visual review checklist

1. Is there one clear focal point, and is it the most important thing for the task?
2. Are containers used only where they mean something?
3. Is the accent used sparingly and semantic color paired with text?
4. Do type sizes follow a scale with clear steps?
5. Do repeated elements align and share padding?
6. Is density appropriate to the role and frequency?
7. Are selected/focus/error states unmistakable without color alone?
8. Does it look intentional in both light and dark themes?
9. Does it still look composed at the narrowest supported width?
10. Would a user mistake it for a wireframe? If so, what is missing: hierarchy, real content, or tokens?

## Do / Don't

| Do | Don't |
|---|---|
| Choose the focal element first, then step everything else down. | Give every heading, number and button the same weight. |
| Separate sections with space and headings. | Box every section with identical borders and shadows. |
| Reserve the accent for action and selection. | Color every icon, border and heading with the brand color. |
| Use real content and production-like data volume. | Judge a layout with three placeholder rows. |
| Build from tokens and record new ones. | Introduce one-off colors and spacings per screen. |

## Bans vs refusals, and finish details

**Reflex rules** (waivable on the record, see [gate-tiers.md](gate-tiers.md) §1;
the device list is owned by [design-quality.md](design-quality.md) §2): eyebrow/kicker
above a heading; coloured `border-left/right` over 1px on cards or alerts;
gradient text; hard offset shadows (outside neobrutalism); emoji or Unicode
glyphs as icons; hero-metric template, 01/02/03 section numbers, sparkline
or progress-ring filler, monospace as "technical" costume. The Floor is
only what gate-tiers lists as Floor.

**Finish details:** concentric radius (outer = inner + padding); `tabular-nums` on
dynamic numbers; extend hit areas with a pseudo-element; `text-wrap: balance` on
headings and `pretty` on body; image outlines at 10% black/white; theme the
surfaces you did not draw (`::selection`, `caret-color`, `scrollbar-color`,
`accent-color`, focus rings, `text-underline-offset`) from the palette. Type
scale ratio about 1.2 for dense UI, 1.25 general, 1.33 expressive; build text
levels from weight and opacity at one size.
