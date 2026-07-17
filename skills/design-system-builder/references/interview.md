# CREATE-mode Interview

Goal: extract enough decisions to build the whole system without guessing on anything
expensive to change later. Ask in batches (use AskUserQuestion when available), not one
at a time. Skip questions already answered by the conversation or repo context.

If the user is unavailable (background/autonomous run): choose the conventional default
for every unanswered item, record each choice in `DECISIONS.md` with a one-line rationale,
and proceed.

## Batch 1 — Product & brand (shapes everything)

1. **What is the product?** (SaaS dashboard / e-commerce / marketing site / mobile-web app / internal tool — native mobile is out of scope)
   → drives density, component priorities, tier scoping
2. **Brand color(s)?** Existing hex values, or a direction ("trustworthy blue", "energetic orange")?
   Any logo/brand assets to match?
3. **Personality on two axes**: serious ↔ playful, minimal ↔ expressive
   → drives radius (sharp vs round), shadow depth, motion amount
4. **Languages/scripts**: Thai? Thai+English? → typography rules (line-height ≥ 1.6, font pairing)

## Batch 2 — Technical (shapes deliverable format)

5. **Stack**: React/Next.js/Vue/plain HTML? Tailwind (v3/v4)/CSS modules/vanilla CSS/styled-components?
   Component lib in play (shadcn/Radix/none)?
   → default when unanswered: CSS custom properties + Tailwind v4 `@theme`
6. **Where does this live**: one app, or a shared package consumed by several apps?
7. **Figma needed too**, or code-only?

## Batch 3 — Scope & constraints

8. **Tier 1 component list** — show the MVP ~20 from `components.md`, ask what to add/remove;
   ask which of the 4 hard components (Data Grid, Date Picker, Combobox, RTE) are needed now
9. **Density**: comfortable / compact / both? (both = plan density tokens from day 1)
10. **Dark mode**: now, later, never? (architecture supports it regardless; "now" doubles the semantic layer work)
11. **Accessibility bar**: WCAG AA (default) or AAA?
12. **Existing UI to stay compatible with**, or greenfield?

## Conventional defaults (when unanswered)

| Question | Default |
|---|---|
| Product type | SaaS web app |
| Brand color | Blue-based, neutral gray with slight cool tint |
| Personality | Middle: radius md, shadows subtle, motion minimal |
| Stack | CSS custom properties + Tailwind v4 |
| Tier | MVP ~20 components |
| Density | Comfortable only |
| Dark mode | Architecture-ready, not built |
| A11y | WCAG AA |
