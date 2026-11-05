# OpenDesign templates: what was rendered and measured

Captured 2026-11-05 (Apache-2.0 repo `nexu-io/open-design`). 25 `example.html` files were rendered at 1440px with
Playwright (full page, scrolled so reveals show) and measured from computed styles; the design-system library page
(`open-design.ai/design-system/`, 269 entries) was read and its 52 style-named `DESIGN.md` files sampled. Pictures are
local only (`assets/site/previews/open-design/`, git-ignored); nothing was copied into the skill.
Companion text study: [open-design-templates-study.md](open-design-templates-study.md).

## Measured (first fold, 1440px)

| Template | H1 | Weight / face | Tracking | Radius (button / card) | Section padding |
|---|---|---|---|---|---|
| Kami landing | 106px | 500 serif (Source Serif) | -1.2px | n/a | 44px+ |
| Soft premium | 92px | 700 geometric (Plus Jakarta) | -3.5px (-0.038em) | pill / 36px | 96-112px |
| Editorial minimal | 96px | 400 serif (Instrument Serif) | -2.4px (-0.025em) | pill / n/a | 96px |
| Waitlist | 96px | 800 (Syne) | -2.9px (-0.03em) | 2px | 60px |
| Email marketing | 96px | 400 condensed (Anton) | -0.5px | n/a | 44-56px |
| Digital e-guide | 92px | 700 serif (Cormorant) | -0.9px | n/a | n/a |
| Open Design landing | 72px | 800 (Inter Tight) | -2px (-0.028em) | pill / 0 | 26px+ |
| SaaS landing / web prototype | 76px | 700 system sans | -1.5px (-0.02em) | 8px / n/a | 96-100px |
| Pricing page | 60px | 700 system sans | -1.2px | 0 / n/a | n/a |
| Dashboards | 20-40px page title | 600-700 | about -0.01em | 4-8px / 6-16px | n/a |

Typical: display 72-106px, weight 400 for serif and 700-800 for sans, tracking -0.02 to -0.04em, section padding 96px or
more. This matches our token defaults (display up to about 84px, -0.03em, 96px), so the gap is not scale.

## What makes the best ones beautiful (observed, not assumed)

1. **One decisive move per page.** A full-bleed photograph with a giant wordmark (luxury real estate), a single "04" numeral at viewport scale (Swiss), a two-line serif headline with one italic word (warm paper). Everything else is quiet.
2. **A typographic voice, not a font choice.** Roman plus *italic emphasis* inside one headline, tiny uppercase mono labels, oversized numerals, serif for numbers that matter. The pairing carries the identity before color does.
3. **Editorial furniture.** Register strips (issue, volume, date, coordinates), vertical text rails, plate numbers, "Vol. 01 / No. 26", crop-mark corners, filed-under labels, marginalia. Tiny, mono, low contrast; it makes a page feel authored.
4. **Real imagery or none.** Where a photograph appears it carries the page; where there is none, type and rules do all the work. They avoid weak generic illustration.
5. **Restrained palette.** Ground, ink and one accent taken from the subject (the studied set used warm paper with terracotta, coral, hazard red or cobalt); dark dashboards add one highlight color for the single bar or number that matters. Warm cream + serif + terracotta is also the most common generated look ([design quality](../references/design-quality.md) §2): use it only when the subject is paper or craft, and then change at least two of ground, face and accent from the obvious choice.
6. **Dashboards with a point of view.** One editorial example sets large serif numerals on tan with sparse labels and a single accent bar in a black bar chart; the dark social dashboard leads with a sentence ("shipped 9 posts this week") before the numbers.
7. **Objects with weight.** Pinned paper notes at a slight tilt with a soft shadow, a phone or device frame, a floating pill nav. Depth is used rarely and on purpose.
8. **Honest scale.** Product pages (docs, pricing, blog) are plain and crisp, not decorated; beauty comes from spacing and type, not effects.

## Where we differ

- Our previews draw art from the palette; the best references use a photograph or pure typography. See [visual assets](../references/visual-assets.md) for sourcing real pictures.
- We have the tokens and shapes; we lacked "furniture" and typographic-voice recipes. Added to [direction recipes](../references/direction-recipes.md).
- The library page ships 52 style-named DESIGN.md files, but many keep default placeholder palettes (the same blue and violet repeat in about half); only a few (Warm Editorial, Kami, Atelier, the brand-inspired ones) are specific enough to learn from.

## Design-system library page (the site's own design)

Giant two-line grotesque H1 ending in one lime dot; a wide-tracked uppercase eyebrow with a short leading rule; pill search
field with a `/` key hint; segmented "All / New (126)" control; a left category list with counts (Enterprise & SaaS 51,
Public services & education 38, UI libraries 36); cards that show a 4-swatch palette, a one-line description and a
"N-chapter guide" tag. Useful pattern: palette chips plus a one-sentence purpose on every card.
