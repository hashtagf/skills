# Scoring, caps and critique format

Make self-critique comparable and stop scores drifting upward. Source: Taste
Skill critique and research files (S98, see [sources](sources.md)).

This file is a calibration and cap addendum to the final score in
[review loop](review-loop.md) §3–4; it is not a second rubric. Report one score
(the review-loop rubric); apply the caps below to it and show which cap applied.
The 1–5 pre-emit check in [gate tiers](gate-tiers.md) §2 is plan-only.

## 1. Calibration and caps

The four-part weighting (design 40%, usability 30%, creativity 20%, content 10%)
is a way to place the review-loop result on a 10-point scale for comparison
with real sites. Calibrate to strong real sites at about 7.5–8.0 (75–80 on the
100-point rubric); 8.5 is rare. Caps override the arithmetic:

| Condition | Cap |
|---|---|
| Automated check failed, or a headline runs 3+ lines | Overall 6.0–6.5 |
| Fewer than 4 real pictures on a page that needs them | Design 6.5 |
| Blank stretches taller than half a screen, or unequal outer margins | Design 6.5 |
| Placeholder or invented content shipped as real | Content 5 |
| No primary action on the first screen | Usability 7 |
| Anything covers a headline | Usability 6 |
| A reveal that never fires leaves a blank band | Usability 5 |

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
at 44px holds about 32 characters over two lines. Use `max-width` in `ch` and
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
