# Scoring, caps and critique format

Make self-critique comparable and stop scores drifting upward. Source: Taste
Skill critique and research files (S98, see [sources](sources.md)).

This file is a calibration and cap addendum to the final score in
[review loop](review-loop.md) §3–4; it is not a second rubric. Report the two
review-loop scores (visual and UX, each out of 100); apply the caps below and show which cap applied.
The 1–5 pre-emit check in [gate tiers](gate-tiers.md) §2 is plan-only.

## 1. Calibration and caps

Calibrate to strong real sites at about 75–80 on each 100-point scorecard; 85+ is rare.
Caps override the arithmetic:

| Condition | Cap |
|---|---|
| Automated check failed, or a headline runs past its line limit ([visual system](visual-system.md) Part A "Headline length") | Visual and UX 60–65 |
| Fewer than 4 real pictures on a page that needs them | Visual 65 |
| Blank stretches taller than half a screen, or unequal outer margins | Visual 65 |
| Placeholder or invented content shipped as real | UX 50 |
| No primary action on the first screen | UX 70 |
| Anything covers a headline | UX 60 |
| A reveal that never fires leaves a blank band | UX 50 |

## 2. Report format (same every round)

One-second view · idea sentence · the one live thing · one layout word per
section · scores · caps applied · top 3 problems, each with the screenshot and
the fix. **Fix in this order:** idea → hierarchy → composition → type → imagery
→ colour → detail → motion. Never refill a gap with an ornament.

## 3. Layout-word sameness

Write one word per section (split, list, grid, statement, table…). The same
word twice in a row, or three times on the page, means the template is showing.

## 4. Headline arithmetic

Characters per line ≈ container width ÷ (font size × k): k = 0.40 condensed,
0.50 grotesk/serif, 0.58 wide or all-caps; test Thai separately. A 390px phone
at 36px holds about 40 characters over two lines. Use `max-width` in `ch` and
`text-wrap: balance`; cut words before shrinking type. A statement or quote is
a `<p>` of ≤ 25 words at ≤ 36px.

## 5. Frame checks

Equal left and right margins; no section keeps its text in one half with the
other half empty; no empty stretch taller than half a screen; a hero that is
only an oversized motif with nothing to read counts as a hole.

## 6. Evidence for the bans (optional)

Top vs weak sites in the study: icon-topped cards 1% vs 28%, 3+ tracked
uppercase labels 6% vs 43%, gradient fills 22% vs 52%. Hero headlines: median
5 words, 70% fit in two lines.
