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

## One focal point per view

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
- A small type scale (e.g. 5–6 steps) used consistently. Large size jumps for
  the focal element, small steps elsewhere.
- Labels quieter than values in data displays; numbers in tabular figures.
- Keep reading text near 60–75 characters per line for Latin scripts; test
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

Use motion to explain change (where something went, what updated), keep it
short, and respect reduced-motion preferences. [S16] Avoid decorative motion
on operational screens.

## Avoid the generic look

Unconsidered defaults make products look templated: identical rounded boxes,
centered everything, a purple-to-blue gradient hero, emoji as section markers,
one stock font for everything, numbered markers on content that is not a
sequence. Choose deliberately from the product's own world (its units,
documents, vocabulary) and keep boldness in one place per screen.

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
