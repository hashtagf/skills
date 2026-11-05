# Design workflow — phases, references, ask points, exit criteria

The spine of this skill. Each phase lists what to do, what to read, whether
to stop and ask the user, and when the phase is done. Run only the phases the
mode needs (SKILL.md, "Route by mode"). Carry one **design context card**
([design context](../assets/design-context.md)) through every phase and update
it as facts replace assumptions.

Ask-point legend: **ASK** = stop and ask before continuing (unless the user
said to proceed without them — then pick the recommended option and log it as
an assumption). **ASK-IF** = ask only when the condition holds. **NO** = never
stop here; decide, label assumptions, continue.

---

## Phase 0 — Inspect

**Do.** Read what already exists before forming an opinion:
- Supplied artifacts: brief, screenshots, URLs, prototype, code.
- Project files: `DESIGN.md`, `PRODUCT.md`, `IDEA.md`, design context, PRDs.
- System: tokens (CSS vars, Tailwind theme), component library
  (`components.json`, `package.json`), existing screens of the same pattern.
- Available tools: browser/Playwright, Figma, installed specialist skills.

For each artifact record location, viewport, state and observed behavior. A
screenshot supports visual observations only, not keyboard, screen-reader,
server or conversion claims; a prototype supports only what it implements.

**Read.** [design memory](design-memory.md) §1–2 (what to look for, precedence).

**Ask.** ASK-IF docs and code disagree on a value that the task will touch
system-wide (report both, recommend one). Otherwise NO.

**Exit.** One line per source found/missing; conflicts listed; tools available.

## Phase 1 — Understand

**Do.** Fill the context card: product type, roles, primary job, main
action, entry context, device/input, language, data volume, risk, success
metric + guardrail. Set the **rigor tier** (Light / Standard / Critical) from
the worst plausible consequence of an error. Place the request on the
[framework](framework.md) level.

**Read.** [product discovery](product-discovery.md); [framework](framework.md)
for multi-level work; [back office](back-office.md) or
[customer UI](customer-ui.md) for role context; [sources](sources.md) when a
claim needs an external citation.

**Ask.**
- ASK if the **primary role or primary job** cannot be inferred from the
  artifacts and the tier is Standard or Critical — everything downstream depends on it.
- ASK for **business rules on Critical work** that must not be guessed: who
  may approve, limits and fees, what is reversible, legal/compliance text,
  data that roles may or may not see.
- ASK-IF the success metric changes the design (e.g. speed vs error rate
  trade-off) and none is given.
- NO for device, language, density, copy tone — infer from context and label *assumed*.

**Exit.** Context card filled; each field *evidence* or *assumed*; tier stated.

## Phase 2 — Architect

**Do.** Map the journey: entry → understand → act → feedback → recover →
finish, with the user's decision and required information at each step and at
least one failure/recovery path for the critical task. For multi-page work:
IA, page inventory with page types, navigation, URLs, deep links, role
handoffs and permissions across pages. Choose the **page pattern** for each
screen from the role's primary question; for admin pages classify the page
type first ([back office](back-office.md)).

**Read.** [experience architecture](experience-architecture.md),
[navigation grouping](navigation-grouping.md),
[design direction](design-direction.md) §1–2, [interaction](interaction.md);
[mobile native](mobile-native.md) and [notifications](notifications.md) when relevant.

**Ask.**
- ASK-IF the flow implies a **scope change**: extra pages, new roles, changed
  permissions, or removing a step the user described.
- ASK-IF two page patterns are equally plausible and they lead to different
  builds (e.g. table vs kanban for the same job) — show both in one line each.
- NO for IA labels, ordering, URL shapes — propose them.

**Exit.** Flow with failure path; page pattern per screen with a reason.

## Phase 3 — Explore

**Do.** Choose composition and direction.
- **Composition:** for complex pages sketch ≥ 2 compositions and choose by task
  success (scan path, steps to main action, what stays visible). Pick a
  [layout library](../assets/layouts/index.md) ID when one fits; adapt it to
  real content, states, permissions and widths.
- **Direction:** if DESIGN.md fixes the look, work inside it and skip
  exploration. Otherwise translate the user's words with the keyword table
  ([design direction](design-direction.md) §8), set the three dials and, for a
  new look or a public page, run the direction interview (§9, user present)
  and propose 2–3 named directions (§7).
- **Motion level:** the motion dial sets what may move ([motion](motion.md) §1).
- Brand from references: [design memory](design-memory.md) §3b.

**Read.** [direction library](direction-library.md) when a new look is needed, [design direction](design-direction.md) §3–9,
[design quality](design-quality.md) §1–2b,
[visual composition](visual-composition.md), layout library category +
[specification](../assets/layouts/specification.md); depth in
[worked examples](../assets/layouts/worked-examples.md) and
[back-office worked examples](../assets/layouts/worked-examples-back-office.md);
external [OpenDesign references](../assets/layouts/opendesign.md) (verify before
importing tokens). After brand extraction run
`python3 scripts/design_md_check.py DESIGN.md` on the draft.

**Ask.**
- ASK the **direction interview** (≤ 3 multiple-choice questions: feel, references,
  energy) for every new look / public page without DESIGN.md or a stated direction,
  **before writing code**. Skip only when the user said they are away or to use
  defaults (then infer via §8 and mark *assumed*); a background session is not "away".
- ASK to **pick a direction** when 2–3 are proposed for a new look — this is
  taste and brand, the user's call. Lead with the recommendation. Show
  pictures, not only names ([direction library](direction-library.md) §1); when
  the user asks for more, show the next 2-3 rather than repeating.
- ASK-IF the best direction conflicts with DESIGN.md or the existing product
  language (do not redesign unrequested areas).
- NO when DESIGN.md already decides, or for the composition of an internal
  task screen — choose by task success and state the rejected option.

**Exit.** Composition chosen with rejected option noted; direction + dials set
(user words → interpretation stated in one line).

## Phase 4 — Design (specify)

**Do.** Specify the screen so it can be built and checked: content priority,
real copy, labels, controls, component choices, every applicable state,
keyboard/focus, responsive behavior, error recovery. Answer the
[page spec](../assets/page-spec.md) rows the tier requires. Hard components (editable grid, drag reorder, pickers, rich text, mention input,
notification centre, tour, autosave form, password recovery) follow
[advanced components](advanced-components.md); every interactive part defines
default, hover, focus-visible, pressed and disabled. Use project
tokens; a new font, scale or aesthetic needs a reason. Critical work adds
security/privacy rows. External references: name source and inspected
surface, keep attribution, state what is adapted; never infer a private app
from its landing page.

**Read.** By the decision at hand, one or two files:
[components usage](components-usage.md), [component states](component-states.md),
[forms](forms.md), [advanced components](advanced-components.md), [patterns](patterns.md), [experience patterns](experience-patterns.md),
[content design](content-design.md) or [marketing copy](marketing-copy.md),
[data visualization](data-visualization.md), [ai features](ai-features.md),
[trust/security/privacy](trust-security-privacy.md);
visual: [visual](visual.md) (hierarchy, grouping, Thai text), [design foundations](design-foundations.md), [color palette](color-palette.md),
[visual craft](visual-craft.md), [visual assets](visual-assets.md),
[visual benchmarks](visual-benchmarks.md) §13 craft pass, [iconography](iconography.md).
Evidence behind values and wording, open only to justify or check a choice:
[site measurements](../assets/site-measurements.md), [gallery study](../assets/gallery-study.md),
[copy study](../assets/copy-study.md), [nav study](../assets/nav-study.md).

**Ask.**
- ASK-IF real content is required and cannot be drafted honestly: prices,
  legal text, claims, customer logos, statistics (never invent proof).
- ASK-IF the spec needs **new design-system values** (new color role, font,
  radius scale) on a project that has an approved system.
- NO for draft copy, state wording, spacing, component choice — decide and
  mark drafts for confirmation.

Apply principles selectively: for each decision connect evidence → affected
task → principle → proposed behavior → verification; no list of laws
disconnected from the UI. Finish with a visual pass (focal point,
containers, density, color roles — [visual craft](visual-craft.md)) and the
craft pass with measured values ([visual benchmarks](visual-benchmarks.md) §13).

**Any form on the page** (sign-up, checkout, settings, filters with
input, create/edit) makes [forms](forms.md) mandatory: per-field rules
(required, format, length, range, cross-field), placeholder examples (§3),
messages for each rule, validation timing (§6) and submission states (§7).

**Public pages also need:** a palette from the keyword ([color palette](color-palette.md)
"Making it look good" + starter palettes), the mobile composition
([visual composition](visual-composition.md) "Mobile web composition") and a motion spec.

**Motion spec** for every page at or above the motion baseline ([motion](motion.md) §1): one table of
element · trigger · motion · duration/easing · reduced-motion behavior within
the dial budget ([motion](motion.md) §7).

**Exit.** Required page-spec rows answered or N/A with reason; states listed.

## Phase 5 — Implement (only when asked to build)

**Do.** Build with the real stack, reusing components and tokens
([design memory](design-memory.md) §6). Include actions, all specified
states, responsive behavior and accessibility. Use a specialist skill only if
it is installed. Prototype rules: [prototyping](prototyping.md); page-build practices: [build recipes](build-recipes.md). Turn the chosen direction into tokens with
`scripts/export_tokens.py` ([tokens to code](tokens-export.md)): CSS, Tailwind v4 or shadcn variables, dark derived and contrast-checked.

**Keep the before.** Before changing an existing page, copy the files you will
touch (for example `index.html` → `index.v1.html`, `page.css` → `page.v1.css`)
or confirm the tree is committed, and save before-screenshots at 1440 and 390.
A redesign or direction change must always be reversible and comparable; say in
the hand-off where the previous version is and what changed.

**Ask.**
- ASK before **expanding scope**: touching pages not requested, adding a
  dependency or component library, changing tokens system-wide, migrating a stack.
- ASK before writing project documents (DESIGN.md, design context) unless asked
  or owned by the host workflow.
- NO for implementation details inside the agreed scope.

Motion follows the spec with CSS / View Transitions first; a motion library
only if the project has one ([motion](motion.md) §5–6). Reduced-motion is the
first branch written.

Forms implement the [forms](forms.md) §6b contract (rules in markup, own
messages on blur and submit, error summary with focus, pending submit,
server errors mapped, input kept), using the project's form library if any.

**Exit.** Builds and runs; specified states reachable; every form validates.

## Phase 6 — Critique

**Do.** Switch from builder to reviewer. Look at the render, not the code.
Run `slop_check.py`, then critique with severity (blocker/major/minor/note),
evidence, impact, fix and verify. Check UX (task, flow, states, recovery) and
visual (hierarchy, type, spacing, color, consistency) separately; apply the
specific refinement verb for each issue. Report one final score from the
[review loop](review-loop.md) §3–4 rubric, capped and calibrated by
[scoring caps](scoring-caps.md); run the fresh-context reviews in
[gate tiers](gate-tiers.md) §3 when subagents exist.

**Read.** [review loop](review-loop.md), [scoring caps](scoring-caps.md), [gate tiers](gate-tiers.md), [design quality](design-quality.md) §5,
[visual craft](visual-craft.md), [do and don't](do-and-dont.md); admin pages also
the page review in [back office](back-office.md).

**Ask.** NO — critique is internal. Fix within scope; surface taste-level
notes in the report instead of asking.

**Exit.** Findings ranked; blockers and majors have fixes.

## Phase 7 — Verify

**Do.** At the depth tools allow: `node scripts/render_check.js <page> --zoom`
(use `--fast` for re-checks between fixes, the full run once before
delivery; add `--reduced-motion` when the page animates; `--doctor` exit 3 → mark *not tested*, run the static checks,
never install or wait for browsers mid-task) and inspect the screenshots; drive the critical journey plus one failure path — for each form: empty
submit, one invalid value (also Thai typed into email), one request failure,
and look at the error state at desktop and phone width (rows stay aligned); when the brief covers them, also check tablet, right-to-left and dark (ranges, test widths and rules: [tablet, RTL and dark](tablet-rtl-dark.md));
judge the 390px screenshot as its own design (header, hero, CTA in first
screen, targets, stacking);
`python3 scripts/contrast.py --css <page>`; keyboard, zoom/reflow, language,
assistive technology as relevant; the design QA list in
[measurement](measurement.md) — each item passed, failed or not tested. Check
every **hard gate** ([review loop](review-loop.md) §5).

**Read.** [render verification](render-verification.md),
[accessibility verification](accessibility-verification.md),
[accessibility](accessibility.md), [i18n & performance](i18n-performance.md).

**Ask.**
- ASK-IF a **hard gate fails and cannot be fixed within scope** (e.g. the
  backend can't confirm success, a permission leak in an API) — report and ask
  whether to proceed, block, or change scope.
- ASK-IF verification needs access you don't have (login, test data, device);
  otherwise state "not tested" and continue.

**Exit.** Results recorded as observed, separate from proposed tests.

## Phase 8 — Refine and deliver

**Do.** Fix, re-render, re-check what changed (≤ 3 rounds: the single fix-round budget; [gate tiers](gate-tiers.md) §4 and [design direction](design-direction.md) §7 link here). Report: user
outcome first; decisions with rationale; findings by task impact with
severity, confidence and effort; what was tested vs not; assumptions and
decisions to confirm; success metric, guardrail and when to review after
release. Record approved decisions in DESIGN.md/design context only when asked
or host-owned; re-run `design_md_check.py` after editing DESIGN.md. [Validation](validation.md) before claiming success;
templates in [output templates](../assets/templates.md).

**Ask.**
- ASK to **approve decisions that become system rules** (new token, pattern
  for all pages, DESIGN.md status draft → approved).
- Publishing, committing, deploying follow host rules; a design or preview
  grants no authority to do them.

**Exit.** Completion criteria in SKILL.md met; open items listed, not dropped.

---

## Asking well

- **One batch per checkpoint**, at most 3 questions, each with a recommended
  default and what changes depending on the answer. Use the host's question
  tool when available; otherwise a short numbered list.
- Ask only what changes the design and cannot be read from artifacts, the
  repo or convention. Never ask for something you could inspect.
- Never stop for reversible choices (spacing, draft copy, component choice);
  decide and label.
- **Away / "use defaults" mode:** do not stop. Take the recommended option at
  every ASK, mark it *assumed* on the context card, and end the report with
  "Decisions to confirm" listing each one and its impact.
- Match the user's language; Thai questions keep technical identifiers in English.
- **Shape before code:** usually one round of 2–3 questions; state the likely
  reading and invite correction. Ask only what changes the result: purpose,
  people, outcome, what only this product can claim, content ranges
  (min/typical/max), states, constraints, what must stay untouched. Never ask
  for CSS values. Return a brief, not code.

Example (Phase 1, Critical, Thai):

```
ก่อนออกแบบหน้าอนุมัติ payout ขอยืนยัน 2 เรื่องที่เดาไม่ได้:
1. ใครอนุมัติได้ — ผู้อนุมัติคนเดียว หรือ maker-checker 2 คน? (แนะนำ maker-checker สำหรับยอดเกินเกณฑ์) → เปลี่ยน flow และ permission
2. ยอดที่ต้องอนุมัติ 2 ชั้นเริ่มที่เท่าไร? → เปลี่ยนการแสดงสถานะและการยืนยัน
เรื่องอื่น (ความหนาแน่น, ข้อความ, layout) จะเสนอเป็นค่าเริ่มต้นให้ตรวจทีหลัง
```

---

## Reference → phase index

Every file in this skill and the phases that open it. A file not listed here
is reached through the one that links it (layout category files via the
layout index).

| File | Phases |
|---|---|
| [design memory](design-memory.md) | 0 (§1–2), 3 (§3b), 5 (§6), 8 (§3) |
| [product discovery](product-discovery.md), [framework](framework.md) | 1 |
| [sources](sources.md) | 1, RESEARCH, any external claim |
| [back office](back-office.md) | 1, 2, 6 |
| [customer UI](customer-ui.md) | 1, 2 |
| [experience architecture](experience-architecture.md), [navigation grouping](navigation-grouping.md), [interaction](interaction.md), [mobile native](mobile-native.md), [notifications](notifications.md) | 2 |
| [design direction](design-direction.md), [direction library](direction-library.md), [preview coverage](preview-coverage.md) | 2 (§1–2), 3 (§3–9: styles, dials, directions, keywords, interview; library and preview coverage for pictures) |
| [design quality](design-quality.md) | 3 (§1–2b), 6 (§5) |
| [visual composition](visual-composition.md) (also 4 and 7: mobile web composition), layout [index](../assets/layouts/index.md), [specification](../assets/layouts/specification.md), [worked examples](../assets/layouts/worked-examples.md), [back-office worked examples](../assets/layouts/worked-examples-back-office.md), [OpenDesign](../assets/layouts/opendesign.md) | 3 |
| [page spec](../assets/page-spec.md), [components usage](components-usage.md), [component states](component-states.md), [forms](forms.md), [patterns](patterns.md), [experience patterns](experience-patterns.md), [content design](content-design.md), [marketing copy](marketing-copy.md), [data visualization](data-visualization.md), [ai features](ai-features.md), [trust/security/privacy](trust-security-privacy.md) | 4 |
| [visual](visual.md), [design foundations](design-foundations.md), [color palette](color-palette.md) (recipe + starter palettes), [visual assets](visual-assets.md), [visual benchmarks](visual-benchmarks.md), [iconography](iconography.md) | 4 |
| [visual craft](visual-craft.md) | 4, 6 |
| Evidence: [21st.dev study](../assets/21st-study.md), [21st.dev dashboard study](../assets/21st-dashboard-study.md), [site measurements](../assets/site-measurements.md), [gallery study](../assets/gallery-study.md), [copy study](../assets/copy-study.md), [nav study](../assets/nav-study.md) | 4 (to justify a value), RESEARCH |
| [motion](motion.md) | 3 (§1 level), 4 (§7 spec), 5 (§5–6), 7 (§8) |
| [prototyping](prototyping.md), [tokens to code](tokens-export.md) | 5 |
| [build-recipes](build-recipes.md) | 4, 5, 7 |
| [gate-tiers](gate-tiers.md) | 6, 7, 8 |
| [page-anatomy-by-job](page-anatomy-by-job.md) | 2, 3 |
| [scoring-caps](scoring-caps.md) | 6 |
| [app-screen-rules](app-screen-rules.md) | 4, 6 |
| [shadcn-rules](shadcn-rules.md) | 5 |
| [review loop](review-loop.md), [do and don't](do-and-dont.md) | 6 (and REFINE) |
| [render verification](render-verification.md), [accessibility](accessibility.md), [accessibility verification](accessibility-verification.md), [i18n & performance](i18n-performance.md), [measurement](measurement.md) | 7 |
| [validation](validation.md), [output templates](../assets/templates.md) | 8 |
| [design context](../assets/design-context.md) | all (context card) |

| Script | Phase |
|---|---|
| `scripts/design_md_check.py` | 3 (after brand extraction), 8 (after editing DESIGN.md) |
| `scripts/slop_check.py` | 6 |
| `scripts/render_check.js`, `scripts/contrast.py` | 7 |
| `scripts/direction_preview.js`, `scripts/build_previews.js` | 3 (pictures of directions; build_previews regenerates all preview sets) |
| `scripts/export_tokens.py` | 5 (direction to CSS, Tailwind, shadcn tokens) |
| `scripts/backoffice_preview.js` | 3 (pictures of back-office density and tone) |
| `scripts/site_preview.js` | 3 (a direction on every page type, section and component) |
