# Design memory — source of truth, DESIGN.md, routing, reuse

Agents drift between sessions: a new run picks a different radius, padding,
font or density. Fix it by deciding once, writing the decision down with its
reason, and reading it before every design task.

> Make decisions once, apply them consistently, change them intentionally.

## 1. Inspect before designing (Phase 0)

Look for, in this order, and note what exists:

1. Product docs: `PRODUCT.md`, `IDEA.md`, PRDs, the [design context](../assets/design-context.md) file.
2. Design language: `DESIGN.md`, `.interface-design/system.md`, `docs/design*`, Figma library links.
3. Tokens: CSS variables, Tailwind `@theme`/config, token JSON.
4. Component system: `components.json` (shadcn), `package.json` deps (Radix, MUI,
   Ant, Chakra, Vuetify, PrimeVue, Element Plus, Naive UI, shadcn-vue, Reka UI),
   local `components/ui/`.
5. Existing screens for the same pattern; reuse their structure.

Report what was found in one line each. Missing ≠ permission to invent a full
system; propose defaults and label them unapproved.

## 2. Precedence when sources disagree

| Rank | Source | Wins over lower ranks because |
|---|---|---|
| 1 | User request and safety/legal constraints | Explicit instruction and harm prevention |
| 2 | Product goal and the role's job | The page exists for this |
| 3 | Approved DESIGN.md / design context | Agreed brand and system decisions |
| 4 | Existing code and components | What actually ships today |
| 5 | Specialist skill guidance | General craft, not project facts |
| 6 | Creative defaults | Unapproved proposals |

Rules:
- A lower rank never silently overrides a higher one. Example: a creative
  skill wants visual variety, DESIGN.md says operations pages are dense
  tables → keep the dense table; propose variety only where DESIGN.md allows.
- **Docs vs code conflict** (DESIGN.md says 8px radius, code uses 6px):
  report both values and where each lives, recommend one, change neither
  system-wide without approval. Scoped work follows the code for consistency
  and records the deviation.
- A user request that conflicts with rank 3 is followed for the scope asked,
  and the answer names the deviation so DESIGN.md can be updated or not.

## 3. DESIGN.md — design language with reasons

`design-context.md` holds product facts (roles, vocabulary, statuses,
patterns decided). `DESIGN.md` holds the look and its rationale. Projects may
merge them; keep one source per fact. Write or edit either only when the user
asks or the host workflow owns the file.

What makes it useful is the *why* and the *never*, not a hex list. Ask:
what should the brand feel like; what does typography express; what density
fits the users; why these shapes and this whitespace; what does the brand
deliberately avoid.

```markdown
# DESIGN.md — <product>
Status: draft | approved (<date>, <owner>)

## Personality
3–5 adjectives, each with what it means on screen.
e.g. Calm — one accent, no motion except feedback.

## Philosophy (ranked)
1. Clarity over decoration  2. Information first  3. Consistent interaction

## Direction dials
Variance <n>/10 · Motion <n>/10 · Density <n>/10 (per area if they differ)

## Typography
Display / body / mono / Thai families; scale; weights; Thai body line-height per [design foundations](design-foundations.md) "Thai with Latin display faces" (1.55–1.7; ≤ 1.35 is a defect).

## Color roles
canvas, surface, text, muted, border, primary, focus, success/warning/danger/info
— values for light and dark, and which pairs are contrast-checked.

## Space, shape, depth
Spacing scale; radius per component class; border vs shadow policy; elevation levels.

## Layout rules
Which page pattern and composition each area uses
(e.g. operations = dense table + detail drawer; marketing = editorial; bento only on feature overview).

## Components
Library + version; approved variants; local overrides with reason.

## Interaction rules
Loading visibility, destructive confirmation, validation timing, keyboard support, motion limits.

## Anti-patterns (never)
e.g. decorative KPI cards · gradients behind data · low-contrast controls · mixed radii · glass on forms.

## Decision log
| Date | Decision | Reason | Replaces |
```

This is a starter structure, not values to impose. Example values in any
template are placeholders until the project approves them. The idea of keeping
decisions in a project file read every session follows Interface Design's
`.interface-design/system.md` (S100) and the DESIGN.md draft format (S101).

Validate before handing it on: `python3 scripts/design_md_check.py DESIGN.md`
(required sections, reasons, color roles and dark values, anti-patterns,
dials in range, status line, placeholders). Then check the built tokens with
`python3 scripts/contrast.py --css <page>`.

## 3b. Brand extraction — from references to a design language

Adapted from Hue's brand-to-design-language approach (S99). The goal is the
brand's *philosophy*, not a copied palette.

1. **Collect.** The brand's own site and product (several pages and states),
   logo, printed or physical artefacts, 2–5 references the user likes, and what
   they dislike. Record the URL/screenshot and date for each.
2. **Observe values.** Read computed styles or measure screenshots: colors by
   role (not by frequency), type families and the scale, spacing steps,
   radius, border vs shadow, density, motion, imagery, icon style, copy voice.
   Mark each value *observed* or *inferred*.
3. **Interpret.** Answer the five questions above (feel, typography's job,
   density, shape/whitespace reasons, what it avoids), each with the
   observation that supports it.
4. **Translate.** Map observations to roles and tokens; add the states the
   source never showed (focus, error, disabled, dark) so they belong to the
   same language; check contrast and fix by shifting lightness, not hue.
5. **Write DESIGN.md** (§3) as *draft*, with the dials and anti-patterns, and
   validate it with `design_md_check.py`.
6. **Prove it.** Render two different page patterns (e.g. a table page and a
   form) with the language. If they don't read as one product, the language is
   under-specified; tighten §3 and repeat.

Never copy another company's logo, trademarked assets or distinctive layout
into a different brand; extract principles, then design original output.

## 4. Changing an approved decision

Change a token, radius, density or component default only with a reason
tied to rank 1–2 (a task fails, a constraint changed, an a11y defect). Write
the old value, new value, reason and affected screens in the decision log. Taste
alone is not a reason.

## 5. Routing to specialist skills

Use a specialist only if it is **actually available** in this session (listed
skills, installed plugins, files in the repo). If it is not, apply the
matching reference in this skill instead. Never write that a tool or skill was
run when it was not.

| Need | Prefer, if available | Fallback in this skill |
|---|---|---|
| New design language / tokens / component library | `design-system-builder` | [design foundations](design-foundations.md), [color palette](color-palette.md) |
| Brand extraction from a site or references | A brand/design-language skill (e.g. Hue) | §3b procedure + [visual benchmarks](visual-benchmarks.md) |
| Expressive landing or creative direction | `frontend-design`, Taste Skill or Hallmark | [design direction](design-direction.md) §7, [design quality](design-quality.md) |
| Admin / SaaS product UI craft | Interface Design | [back office](back-office.md), [visual craft](visual-craft.md) |
| React components on a shadcn project | shadcn tooling (`components.json` present) | [components usage](components-usage.md) |
| Vue components | The project's Vue library | same |
| Figma output | Figma MCP / figma-cli skill | [prototyping](prototyping.md) |
| Charts | `dataviz` | [data visualization](data-visualization.md) |
| Test cases for the flow | `test-design` | [validation](validation.md) |
| Critique, polish, audit | Impeccable | [review loop](review-loop.md), `scripts/slop_check.py` |

Named skills (Hallmark, Impeccable, Hue, Taste Skill, Interface Design) are
third-party; their ideas are adapted into this skill's references, so they are
optional. Check that one is installed before naming it as used.

**Direction versus another skill's house rules** (extension of §2, which owns the
precedence): House rules differ: Taste Skill bans resting shadows, hairlines and
gradients; some Hallmark themes (paper lift, plastic, hard offsets) require
them. Within ranks 3–5 the order is: approved DESIGN.md → the chosen direction's
own rules (from the [direction library](direction-library.md)) → this skill's
defaults → another skill's house rules. The user's job and the hard gates in the
[review loop](review-loop.md) §5 sit above all of them. A chosen direction is a
decision: state the rules it overrides ("shadows are allowed because the
direction's material is paper") and report the other skill's resulting findings
as accepted, not as failures. Never edit one skill's checker to pass it.

This skill stays the orchestrator: it owns dimensions 1–3 and the quality
gates; specialists may own 4–7 but cannot override the page pattern.

## 6. Reuse before invent

| Exists in project | Do |
|---|---|
| Button, input, dialog, drawer | Use them; add a variant only with a reason |
| Data table pattern | Extend it (columns, filters, bulk) rather than build a new table |
| Form components | Wire validation and states into them |
| Tokens | Reference tokens; no raw hex/px in new code |
| Theme (light/dark) | Support both through the existing mechanism |

A component library does not make UI good, and is not a reason to change a
project's stack. shadcn/ui fits React/Next projects already on Tailwind; for
Vue use a Vue-native library the project already has.
