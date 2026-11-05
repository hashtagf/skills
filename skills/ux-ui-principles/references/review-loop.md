# Review loop — refinement verbs, scorecards, hard gates

Separate building from reviewing. Name the problem precisely before fixing
it; "make it nicer" is not a fix. Review the **render**, not the code alone
([render verification](render-verification.md)). The verb vocabulary and the
split between review and build are adapted from Impeccable's command set and
its deterministic anti-pattern rules (S96); `scripts/slop_check.py` is this
skill's own detector.

## 1. Refinement verbs

When the user (or your own critique) asks for a change, map it to one verb,
change only what that verb covers, and check its result.

| Verb | Use when | Change | Check after |
|---|---|---|---|
| critique | Need to know what's wrong | Nothing — list findings by severity | Each finding has evidence + fix |
| audit | Technical quality unknown | Nothing — run `render_check.js`, `contrast.py --css`, `slop_check.py`, state and perf checks | Pass / fail / not tested per check |
| polish | Near done | Alignment, spacing rhythm, icon weight, borders, optical alignment | Side-by-side render shows no regressions |
| bolder | Page reads flat / generic | Stronger focal point, scale contrast, one brand move | Focal point identifiable in 1 s |
| quieter | Too loud, too many effects | Remove shadows/gradients/colors; signal budget ≤ 2 per element | Fewer competing signals, hierarchy intact |
| distill | Dense, confusing | Cut or defer elements, progressive disclosure | Main task needs the same or fewer steps; nothing required was hidden |
| typeset | Weak type hierarchy | Scale, weight, leading, measure, Thai line-height | Headings vs body distinct; line length 45–75 ch (Latin) |
| layout | Proportions off | Grid, composition, spacing steps | Edges align; related items grouped |
| colorize | Color decorative or unclear | Map color to roles and statuses | Every color has a role; contrast passes |
| animate | No interaction feedback | Purposeful transitions (durations in [motion](motion.md) §2), reduced-motion path | Motion explains change; nothing blocks input |
| harden | Breaks on real data | Long text, empty, error, overflow, permissions, slow network | Each state rendered once |
| adapt | Mobile/tablet poor | Reflow, touch targets, nav collapse | 320 px and 200% zoom usable |
| optimize | Slow | Image sizes, lazy load, skeletons, bundle | LCP/INP/CLS measured, not guessed |
| clarify | Copy confuses | Labels, errors, empty states, glossary | One name per object/status — [content design](content-design.md) |

Thai shorthand mapping: "ดูธรรมดา / ไม่มีอะไรเด่น" → bolder; "รก / ลายตา" →
quieter or distill; "อ่านยาก" → typeset; "ไม่ลงตัว" → layout; "สีมั่ว" →
colorize; "พังบนมือถือ" → adapt. Diagnosis detail: [visual craft](visual-craft.md).

## 2. Critique format

```
[severity] where — what is observed (evidence: screenshot/state/viewport)
  impact: which task or user is affected
  fix: verb + concrete change
  verify: how to see it is fixed
```

Severity: **blocker** (hard gate, §5) · **major** (task slowed or error-prone)
· **minor** (polish) · **note** (taste, optional). Fix blockers and majors before polish.

Mapping to the scale in [validation](validation.md) and
[templates](../assets/templates.md): blocker → Critical or High; major →
Medium; minor → Low; note → Low (taste). "Critical" here is a severity, not the
Critical rigor tier ([framework](framework.md)).

## 3. Visual scorecard (final score, internal rubric)

| Criterion | Weight |
|---|---|
| Typography | 20 |
| Spacing & alignment | 20 |
| Visual hierarchy | 20 |
| Color & contrast | 15 |
| Component consistency | 15 |
| Responsive polish | 10 |

## 4. UX scorecard (internal rubric)

| Criterion | Weight |
|---|---|
| Task & goal alignment | 25 |
| Workflow efficiency | 20 |
| Information clarity | 20 |
| Interaction & feedback | 15 |
| Accessibility & error recovery | 20 |

Score each criterion 0–10, multiply by weight/10, sum to 100. Score visual and
UX separately — a beautiful page can fail its task and a usable page can look
unfinished. Bands: 90+ excellent · 85–89 ready for review · 70–84 refine · < 70 rework.
This is the one final score to report; apply the caps and the real-site
calibration in [scoring caps](scoring-caps.md) (strong real sites sit near
75–80, so 85+ is rare and needs evidence).

These are this skill's own rubric, not an industry standard. A score is a
reviewer's judgment, not evidence of usability; it never replaces testing with
representative users ([validation](validation.md)). Report the score with the
two or three findings that cost the most points.

## 5. Hard gates — block delivery regardless of score

| Gate | Failure class |
|---|---|
| A primary action cannot be activated | Functional |
| Success shown before the backend confirms (money, approval, submit) | Incorrect state |
| A role without permission sees sensitive data | Security / privacy |
| The main action is unusable on the supported mobile width | Responsive |
| A critical function is unreachable by keyboard or has no visible focus | Accessibility |
| An error state has no recovery path | Workflow |
| A form submits with no validation, shows no field messages, or clears input on error | Workflow |
| A financial amount, fee or total is wrong or misleading | High-risk information |
| A check is reported as passed without having been run | Verification |

## 6. State coverage before review

A default-state-only design is incomplete. For each page, render or specify
the states that apply: default · loading · empty (first use) · no results ·
validation error · request error · partial failure · permission denied ·
timeout / unknown outcome · offline / reconnect · conflict (edited elsewhere) ·
success · disabled / unavailable. Details per state:
[patterns](patterns.md), [experience patterns](experience-patterns.md),
[component states](component-states.md).

## 7. Loop

Critique → fix blockers/majors → re-render → audit → polish → re-render →
score → report. Stop when gates pass and remaining findings are minor or
notes; list those as known limitations rather than silently dropping them.
