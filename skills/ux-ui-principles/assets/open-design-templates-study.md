# OpenDesign templates study (51 template skills)

Read 2026-11-05 from the OpenDesign plugin catalogue (`open-design.ai/plugins/templates/`, 265 entries: prototype 85,
slides 81, image 46, video 22, hyperframes 25, live artifact 5, audio 1). The detail pages only carry metadata, so the
rules were read from the `SKILL.md` of 51 web, dashboard, mobile, wireframe, document and utility templates in the public
repo (`nexu-io/open-design`, `plugins/_official/examples/`). Rules are paraphrased; nothing was copied. Slides, image,
video and audio templates were left out (outside this skill). Earlier, narrower review: `../layouts/opendesign.md`.

## What the template skills have in common

1. **Seed plus library, not a blank page.** Each reads a seed template, a section-layout library and a checklist before writing; tokens map to a handful of CSS variables and no new tokens are invented.
2. **A DESIGN.md is the input.** Several stop and ask when it is missing and treat its "agent prompt guide" as overriding the skill. (Our DESIGN.md follows the same spec: `references/design-memory.md`.)
3. **P0 / P1 / P2 checklists, "pass P0 or do not emit".** P0 examples: no raw hex outside the token block, accent at most twice per screen, no emoji as feature icons, no invented metrics, no filler copy, no remote image dependencies, mobile reflow works.
4. **State the plan in one sentence first.** The section list or layout choice is announced before any code, so it can be redirected cheaply.
5. **Honest placeholders.** `—` or a labelled placeholder where a number is unknown; plausible, specific sample data, never "Metric A".
6. **Pre-flight per aesthetic.** The three "taste" web prototypes (soft premium, editorial minimalism, industrial brutalist) each list hard rules, bans, required components, motion and a tick-box pre-flight.

## Patterns worth keeping (now in the skill)

| Pattern | Where it landed |
|---|---|
| Per-direction recipe: hard rules, banned, required components, motion, pre-flight | `references/direction-recipes.md`, `scripts/direction_recipe.py` |
| Component recipes: double-bezel card, button-in-button CTA, floating pill nav, 1px-gap ink grid, uneven bento, register strip, marquee | `references/direction-recipes.md` |
| Live tweak panel bound to CSS custom properties (curated accents, scale, density, mode, motion), persisted, `T` hides, `R` resets | `scripts/tweaks_panel.py` |
| Review as a report: scores with band names, evidence, Keep / Fix / Quick wins, radar; "do not average away interesting failures" | `scripts/review_report.py`, `references/review-loop.md` |
| Section rhythm alternates; one decisive flourish; one image style per page; accent at most twice per screen | `references/visual-composition.md` |
| Pricing: tier shapes, recommended tier marked once, grouped comparison with sticky header, no-JS FAQ | `assets/layouts/marketing.md` M03 |
| Waitlist honesty: one CTA, no countdown or fake proof, announced success | `references/marketing-copy.md` |
| Live data states: live pill (synced / syncing / stale), refresh on open, changed-row flash, source line | `references/data-visualization.md` |
| Wireframe family: greybox, annotated, mobile flow, sketch | `references/prototyping.md` |
| Six mobile screen archetypes | `references/mobile-native.md` |

## Observations about the catalogue

- Most "template" value is the checklist, not the markup: the strongest entries are the ones with a concrete pre-flight.
- Dashboards come in three flavors: static analytics, interactive (tabs, tooltips, export, dark toggle) and live (connector, refresh, diff). Only the live one defines data freshness states.
- Decks outnumber web templates; their craft rules (kicker/chrome vocabulary stays in one register) are the same as our direction-consistency rule.
- Source and attribution matter: several templates distill other open skills and say so; do the same when adapting.
