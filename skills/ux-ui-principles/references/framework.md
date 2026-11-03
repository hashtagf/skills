# End-to-end product design framework

Use this file to place a request in the whole product lifecycle before choosing
a layout. It routes work to the focused references; it does not require every
project to run every activity. Source IDs resolve in [sources.md](sources.md).

## Six disciplines — keep the questions separate

| Discipline | Question it answers | Typical evidence | Primary reference |
|---|---|---|---|
| Product design | What should exist, for whom, and why? | Problem statement, user/role evidence, success metric, constraints | [product-discovery.md](product-discovery.md) |
| UX design | How will people complete their goal across the system? | Journey, flows, IA map, navigation model, permission flow | [experience-architecture.md](experience-architecture.md) |
| UI design | How should each screen be arranged and presented? | Page spec, layout ID, hierarchy, density, visual decisions | [visual.md](visual.md), [visual-craft.md](visual-craft.md), [back-office.md](back-office.md) |
| Interaction design | What does every action and state do? | Action contract, state matrix, validation, recovery | [patterns.md](patterns.md), [experience-patterns.md](experience-patterns.md) |
| Design engineering | Will the built UI match the intent and work in real conditions? | Tokens/components, accessibility, i18n, performance, security behavior | design-system-builder, [accessibility.md](accessibility.md), [i18n-performance.md](i18n-performance.md), [trust-security-privacy.md](trust-security-privacy.md) |
| Design validation | How do we know the design is good? | Usability findings, metrics, design QA, production data | [validation.md](validation.md), [measurement.md](measurement.md) |

An agent asked to "design a page" usually works in UI and interaction design.
Name upstream gaps (no evidence about users, no success metric, unclear IA) as
assumptions instead of silently inventing product strategy.

## Six levels of scope

| Level | Covers | Done when | Load |
|---|---|---|---|
| 1. Product strategy & research | Business goal, users/roles, problem evidence, constraints, success metrics | Problem, audience, measurable outcome and riskiest assumptions are written down | product-discovery, validation |
| 2. Experience architecture | Journeys, flows, IA, navigation, URLs, cross-page relationships, permission flows | Every page has a known entry, exit, parent and owner role; no orphan or dead-end flow | experience-architecture, back-office |
| 3. Page & interaction | Page type, layout, hierarchy, actions, forms, search, states, recovery | Page spec covers the applicable rows of [page-spec.md](../assets/page-spec.md) | back-office, patterns, layouts |
| 4. Visual & design system | Type, grid, spacing, color roles, components, tokens, motion, brand | Screens use project tokens/components; exceptions are justified | visual, visual-craft, design-system-builder |
| 5. Quality & engineering | Responsive, accessibility, localization, performance, privacy, security | Applicable checks are executed or explicitly listed as untested | accessibility, i18n-performance, trust-security-privacy |
| 6. Validation & improvement | Usability testing, analytics, experiments, design QA, iteration | Success measure is instrumented and a review point is scheduled | validation, measurement |

## Process — iterative, not linear

Human-centred design standards describe understanding context of use, specifying
requirements, producing solutions and evaluating them, repeated until the
requirements are met. [S37] Use the six phases below as a working loop; return
to an earlier phase when evidence contradicts an assumption.

| Phase | Activity | Output | Return when |
|---|---|---|---|
| 1. Discover | Learn users, roles, context, current workarounds, existing data | Evidence log, assumptions list | — |
| 2. Define | Agree problem, scope, constraints, success metric | Problem statement, metric definition, non-goals | Discovery shows the wrong user or problem |
| 3. Structure | Map journeys, IA, navigation and page inventory | Flow diagram, IA map, page list with page types | A flow cannot complete or a role has no path |
| 4. Design | Page specs, wireframes, interaction contracts, visual UI | Page specs, prototype or implemented UI | Structure forces a broken page |
| 5. Verify | Prototype tests, accessibility/responsive/performance checks, design QA | Findings with severity and evidence | Users fail a critical task |
| 6. Improve | Production metrics, feedback, support data, iteration | Change log and next hypotheses | Metrics or feedback contradict the design |

## Rigor tiers — scale effort by consequence

Do not run the same process for every screen. Pick a tier from the worst
plausible consequence of a design error; state the tier in the page spec.

| Tier | Typical pages | Required page-spec rows | Required verification |
|---|---|---|---|
| **Light** | Read-only info, low-traffic settings, internal tools for few expert users | 1–3, 5, 8–9, 11 | Rendered review at supported widths, keyboard pass on new controls |
| **Standard** | Main list/detail/forms, customer-facing flows, dashboards | Rows 1–13, 16 | Light + state fixtures, accessibility checks on changed components, one task walkthrough per primary task |
| **Critical** | Money movement, approvals, permissions, irreversible deletion, legal/consent, health or safety data | All 16 rows | Standard + security/privacy review, error-prevention review [S48], failure/unknown-outcome fixtures, usability session with representative users before launch, post-launch metric review |

Raise the tier when a page combines high frequency with high consequence.
Lowering a tier needs a stated reason.

## Shared design context

Multiple skills and agents should not make conflicting decisions. Keep one
project file using [design-context.md](../assets/design-context.md): product
purpose, roles, glossary, IA map, status vocabulary, token source, density
modes, chosen patterns and quality bars. Read it before designing; update it
when a decision changes. If the project has no such file, create it only when
the user asks for project documents; otherwise state the assumed context in
the answer.

## Readiness by goal

| Goal | Minimum coverage |
|---|---|
| Lay out one page in an existing product | Levels 3–4 plus applicable level-5 checks for that page |
| Build a new feature end to end | Levels 1–6 at the tier set by consequence |
| Establish a company design system | Level 4 with governance (design-system-builder), plus level 5 quality bars |
| Let an agent design from scratch | Level 1 inputs supplied or researched; otherwise outputs are proposals built on stated assumptions |

## Do / Don't

| Do | Don't |
|---|---|
| Identify which discipline and level the request belongs to before producing artifacts. | Answer a product-strategy question with a screen layout. |
| Record assumptions where upstream levels are missing and state their risk. | Invent personas, research findings or metrics to make a design look justified. |
| Choose the rigor tier from consequence and state it. | Apply a heavyweight process to a label change, or a lightweight one to a payout approval. |
| Loop back when evidence contradicts an earlier decision. | Treat the phases as a waterfall that cannot be revisited. |
