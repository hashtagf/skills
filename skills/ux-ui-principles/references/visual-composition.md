# Visual composition and localization

Use this reference when hierarchy, typography, color, layout, responsive
behavior, Thai/mixed-language text or charts affect comprehension or task
execution. Preserve an established visual system unless the requested change
includes it.

## Hierarchy and grouping

Start with content order and relationships. Give the critical task a readable
sequence: purpose, decision information, action, feedback, then supporting
detail. Use size, weight, contrast, spacing, and position to express priority;
use emphasis deliberately rather than making everything larger or putting
everything in cards. A decorative card around every element can obscure the
real relationships. [S23]

Nearby elements are read as related; common containers strengthen grouping.
Keep visual grouping consistent with semantic grouping. Use a consistent
alignment system and spacing relationships: related controls belong closer
together than unrelated sections. Reuse the project's tokens, grid and scale; a
4px or 8px scale is a project convention, not evidence that another scale is
unusable, so do not force a new base-4 system onto a working design merely to
follow a rule.

Judge empty space by whether it clarifies relationships and scanning. A dense
operations table and a focused onboarding screen have different needs. Neither
"more whitespace" nor "less scrolling" is a universal goal.

Project checks:
- Can a new user identify the page purpose and next action without reading all copy?
- Does prominence match task importance rather than marketing preference?
- Do headings, labels, hints, and controls form understandable groups?
- Does visual reading order agree with DOM and keyboard order?
- Are destructive and primary actions distinguishable without color alone?

These questions are inspection prompts, not proof of user comprehension.

## Typography and content

Use a small set of text roles: title, section heading, body, label, hint/supporting
text, numerical data. Prefer a few coherent roles over arbitrary sizes in each
component. Use tabular numerals where repeated numerical comparison benefits
from alignment.

Choose font size, weight, line-height and line length using realistic content,
language, viewport and font metrics. Body size around 16 CSS px and generous
line-height can be starting recommendations; WCAG has no universal 16px floor.
Avoid thin small text, low-contrast secondary information and truncated critical
labels. Check loaded fonts and fallback fonts.

Test realistic content: long names and titles, wrapped labels, unbroken
identifiers, missing/empty values, translated text, and user-entered strings.
Truncation needs a usable path to the complete value; a hover tooltip alone
excludes touch and keyboard users.

Write action labels that predict an effect. Distinguish "Save draft", "Submit",
and "Publish" when these are separate operations. Avoid internal error codes as
the sole explanation of a recoverable problem.

## Thai and mixed-language interfaces

Thai text includes combining marks above/below base characters and requires
language-aware line breaking. Inspect actual Thai strings, glyph rendering,
stacked marks, wrapping and fallback fonts for clipping, broken clusters and
unnatural breaks. [S24]

Project recommendations: use Thai-capable fonts; avoid forced or decorative
letter spacing that separates Thai characters or clips marks, unless a need is
demonstrated; begin with roomy line-height then inspect tone marks at small
sizes and in controls. No single line-height guarantees correctness; do not
impose a universal value without checking the actual text, font, and density.

Test Thai/Latin names, long addresses, dates, currency, phone formats and search.
Choose Buddhist/Gregorian calendar display and storage rules explicitly from
product needs; label them clearly rather than assuming the locale decides all
business rules. Preserve original user input where normalization changes meaning.

## Color and surface roles

Use semantic roles for action, selection, status (success, warning, error),
emphasis, surface, text, and borders. Do not reuse a warning color as decoration
where it confuses the status meaning. Keep text or shape cues alongside status
color: red/green, saturation and icons without text are insufficient for
critical state distinctions. Verify the actual foreground and background
combinations in each relevant theme and state. Contrast and text override checks
are in [accessibility.md](accessibility.md).

Borders, elevation, and containers should communicate grouping or layering.
Avoid stacking shadows and backgrounds merely to make a page look finished.
Do not flatten meaningful controls until their affordance disappears.

## Responsive transformation

Choose transformations from the task: stack related content, reprioritize
secondary metadata, move actions into reachable positions, or contain an
essential two-dimensional view. Shrinking every element is not a mobile design.
Let breakpoints respond to content failure rather than device names alone.

Specify how navigation, actions, tables, filters and dialogs adapt; preserve
the user's task when rearranging. Avoid horizontal page scrolling; give genuine
two-dimensional tables a bounded, discoverable region. Do not turn every table
into cards if row comparison is the user's task.

Keep reading order and keyboard order coherent after reflow. Test long titles,
translated strings, empty values, zoom, orientation, sticky headers, footers,
dialogs, and mobile keyboards for overlap with controls and messages. Do not
remove required information or recovery actions to make the layout fit.

## Mobile web composition (≤ 480px) — design it, don't shrink it

| Area | Rule |
|---|---|
| Gutters | 16–20px side padding; nothing touches the edge except full-bleed images |
| Header | Logo + one primary action or a menu button; ≤ 56–64px tall; menu opens as a full-height sheet with large targets, not a squeezed desktop bar |
| Hero | Headline `clamp()` ≈ 32–40px (Thai 28–36px, line-height per [design-foundations.md](design-foundations.md)), ≤ 2 lines at every width (Thai ≤ 3/4: [design-foundations.md](design-foundations.md) "Headline length"); supporting line ≤ 3 lines; primary CTA visible in the first screen, full-width or ≥ 48px tall; the visual goes **after** the text or is cropped to a purposeful detail |
| Type | Body ≥ 16px (inputs ≥ 16px or iOS zooms), meta ≥ 13px (minimum text size: [design-foundations.md](design-foundations.md)); display sizes scale down, body does not |
| Sections | Vertical padding 48–72px (desktop 96–160px); one column; neighbouring sections still vary (image/text order, full-bleed band) |
| Grids | 3–4 card rows → stacked list or a horizontal scroller with a visible peek of the next card; never 2 tiny columns of text |
| Tables / comparison | Becomes cards per row or a scroll container with the first column sticky (keep rows when row comparison is the task, see Responsive transformation); pricing tiers stack with the recommended one first |
| Targets | Project default for web mobile: tap targets ≥ 44×44px with ≥ 8px between neighbours (WCAG AA floor is 24×24, see [accessibility.md](accessibility.md); form controls 48px); links in text have generous line-height |
| Sticky | At most one sticky element (header or a bottom CTA bar), never covering inputs when the keyboard is open |
| Imagery | Art-directed crops (`<picture>`/`object-position`), not desktop images scaled to 30% |
| Hover-only | Anything shown on hover is visible or tap-reachable |

Check at 390px and 320px (`render_check.js --zoom`), then look at the phone
screenshot as its own design: one focal point per screen, clear reading order,
the action reachable with the thumb.

## Charts and evidence

Choose a chart from the question: trend, category comparison, distribution, or
relationship. Show meaningful units and time range. Label missing, estimated,
or stale values instead of treating them as zero. Make axis changes and truncated
scales clear when they alter interpretation.

Provide an accessible way to obtain the same information, such as an appropriately
structured table or textual interpretation. A decorative chart must not invent
business data. Color should support comparison, not be its only carrier.

## Motion and layout stability

Motion rules live in [motion.md](motion.md). Layout stability: reserve space for
asynchronously loaded media and avoid moving a target just as the user activates it.

## Aesthetic quality

Coherent rhythm, alignment, density and restrained decoration support reading.
Brand expression may vary widely. Explain an aesthetic choice as a proposal
and evaluate it with users when consequential; do not claim a favorite style,
font pairing or palette is a universal principle.

## Review questions

- Can the intended actor find the task, its prerequisites, and the next action?
- Do typography and spacing express consistent roles and relationships?
- Does realistic content survive narrow widths, zoom, and localization?
- Do charts and statuses communicate actual data without hiding uncertainty?
- Does distinctive styling support the product rather than obscure its controls?

Record a concrete location and consequence for a finding. "Looks bland" or
"needs more whitespace" is insufficient without describing the task it harms.

## Page rhythm and flourish (from the OpenDesign template study)

- Section types alternate: never two stat rows, two feature triplets or two quote blocks in a row; break a run with a different composition.
- One decisive flourish per page (a pull quote, a striking stat, a real photograph, one hero micro-motion), not three.
- One image style per page: do not mix square headshots, widescreen product shots and vertical phone mockups.
- Accent color: the solid fill (primary CTA) once per view, with a nav CTA outlined or demoted; other uses stay small (link, focus ring, one true-fact label). A third strong use is demoted to ink or muted.
- Replace one generic feature cell with something specific to the product (a screenshot, a real example, a sample of the output).
