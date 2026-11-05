# Visual benchmarks — measured craft values

Numbers for the visual decisions that make a correct UI look designed: type
metrics, tone, spacing rhythm, radius, elevation, motion and content realism.
Read with [visual-craft.md](visual-craft.md) (focal point, containers, signal
budget, feedback diagnosis) and [design-quality.md](design-quality.md) (idea
sentence, competitor test, template devices, render critique). This file gives
the **values**; those files decide **what** to show and **why**.

An existing design system wins. Use these values to fill gaps, critique, or
start a project that has none. They describe observed practice, not standards.

Contents: §1 Typography · §2 Color and tone · §3 Space and rhythm ·
§4 Radius, borders, elevation · §5 Component metrics · §6 Composition (hero
patterns, signature moves, current template look, section order) · §7 Motion ·
§8 Content realism · §9 Thai · §10 Gallery vs shippable · §11 Plain-UI tells ·
§12 Presets · §13 Craft pass · Credits.

## Evidence base (2026-11-04)

| Corpus | N | Method | Detail |
|---|---|---|---|
| Live product, brand, docs and Thai sites | 35 | Computed styles via script, 1456px, logged out | [site-measurements](../assets/site-measurements.md) |
| curated.design live sites | 18 | Computed styles + 12 screenshots | [gallery-study](../assets/gallery-study.md) |
| Dribbble trending web-design shots | 18 | Opened each shot, screenshot review (images; values estimated) | [gallery-study](../assets/gallery-study.md) |
| Behance featured web-design projects | 14 | Opened each case study; 3 live sites measured | [gallery-study](../assets/gallery-study.md) |
| 21st.dev community website templates | 19 | Live previews measured + 1–3 screenshots each | [gallery-study](../assets/gallery-study.md) |
| elayadesign/ai-design-skills (MIT) | 2 skills | Rule review; adapted where evidence agrees | Credits below |

Measured values (live CSS) outrank estimated ones (shots). Gallery work is
optimised to be looked at, not used; see §10 before copying from it.

## How this fits the "avoid the generic look" rules

[design-quality.md](design-quality.md) lists template devices: eyebrows, mono
labels, two-tone or italic headline words, hairlines everywhere, dark +
neon accent, cream + serif + terracotta. The galleries show these devices
**everywhere** — which is exactly why they read as template when used by default.

Resolve it this way:

- **Baseline craft** (§1–§5: type metrics, tone steps, gap bands, radius
  discipline, restrained elevation) is never a template device. Apply it always.
- **Signature moves** (§6 list) are allowed **one per page**, only when the idea
  sentence or the subject justifies it. Two or more = template look.
- The palette and imagery come from the subject, not from the presets in §12.

## 1. Typography

**Voices.** One grotesk carries the UI on nearly every measured site. Optional
second voice: a serif for display or emphasis (Anthropic, Cursor, Notion,
6/18 curated, 8/14 Behance). Optional third: mono for code, data or meta labels.
Never more than three; most strong sites use one or two. The single most
generic curated site used Inter + Poppins + mono with no reason for any of them.

**Faces.** Inter is the most common family among measured product sites, so it
is not banned — but at default weight it reads stock. Curated sites mostly use
foundry grotesks (Suisse, Söhne, ABC Diatype, Neue Montreal, Switzer, Die
Grotesk); Geist is the common free choice. Inter at a variable weight like
550–580 (Inflight) or Inter Display for headings avoids the default look.

**Display weight.** 400–500 on 12/18 curated sites; Stripe 300, Vercel 400,
Linear 510, Figma 400, Ramp 400, Attio 600. 700 on a headline ≥48px appeared on
**zero** curated sites. Labels and buttons 500–550.

**Scale ratio (display ÷ body), choose by intent:**

| Intent | Ratio | Typical display |
|---|---|---|
| Product UI, dashboards, docs | 2–3 | 24–40px over 14px |
| SaaS / product marketing hero | 3–4 | 48–64px over 16px |
| Brand or agency hero | 5–7 | 77–116px |
| Single statement / wordmark | 8–13 | 130–215px |

Keep a small UI band (12–14px dominates text-node counts on product sites) and
use the 20–32px middle band sparingly (card titles only). Few steps, large
jumps: 64 / 48 / 20 / 16 / 14 (PT1), 145 / 26 / 16 / 12 (Mosby's Files).

**Tracking by size (Latin sans display):**

| Size | Tracking |
|---|---|
| ≤20px body/UI | 0 |
| 24–32px | −0.01em |
| 48px | −0.02em |
| 64px | −0.03em |
| 88–100px | −0.04 to −0.05em |
| 120px+ | −0.03 to −0.05em |

Exceptions: fonts already tightly fitted (Die Grotesk, condensed faces) stay
at 0 to +0.01em; uppercase labels and caps serif display go **positive**
(+0.05em caps serif, +0.06–0.12em labels). Never track Thai (§9).

**Line-height by size:** body 1.5 (editorial/luxury 1.6–1.85); headings
24–40px 1.2–1.3; display 48–64px 1.0–1.15; display ≥80px 0.85–1.0. The default
1.5 on a 64px headline is the most common amateur tell.

**Named text styles.** Every text element uses a named style, never a loose
size + weight. A workable set (adapted from elayadesign): `heading-1…6`,
`title-1…5` (card/list/nav titles, weight 500), `body-1…6` (16 and 14px at
600/500/400), `button-lg/md/sm`, `caption-1…5` (12–14px meta). Sizes snap to
one scale (steps and how many are used: [design-foundations.md](design-foundations.md) Typography;
marketing extends upward, e.g. 48, 60, 72, 96, 128); new
styles extend a group (`body-7`) rather than inventing a size.

**Line breaks.** `text-wrap: balance` on headings, `text-wrap: pretty` on body,
so no single word sits alone on the last line. Hero heading and subline max
~640–680px; break where the thought breaks; headlines fit two lines at every
width ([design-quality.md](design-quality.md) §5).

## 2. Color and tone

- **Ink, not black.** Primary text rgb(23,23,23) Vercel · (20,20,19) Anthropic ·
  (31,35,40) GitHub · navy (12,35,52) PT1 · deep green or burgundy on Behance
  brand work. Dark grounds use near-black #0b0b0b–#1c1c1c or a tinted ink
  (8,9,10 Linear; 13,17,23 Inflight), never pure #000 behind body text.
- **Ground, not white.** Off-white or tinted: (250,250,250) Vercel ·
  (250,249,245) Anthropic · oklch(.982 .002 84) Kobbe; 10/14 Behance projects.
  Keep white for cards/surfaces on top of it.
- **Three text tones.** Primary, secondary (~45–55% L, or ink at 45–60% alpha),
  tertiary meta. 7/18 curated sites use **ink alpha** for secondary text, which
  keeps the hue consistent across surfaces. Verify secondary/tertiary contrast.
- **One accent, ≤3 elements per viewport.** 14/18 Dribbble, 11/14 Behance,
  6/18 curated with exactly one saturated accent; on ~¼ of measured sites the
  primary button is ink, not brand color. Accent goes to the action and one
  data highlight (a grey chart with one accent bar).
- **Color from imagery.** Full color lives in photography, 3D or illustration,
  not UI chrome; sample the accent from the hero image when the brand has none.
- **Status color only in chips and dots**, as tinted pills (bg ~12% alpha, text
  full) — never on buttons or headings.
- **Dark mode:** elevation by white alpha overlays (.02/.05/.08), borders
  white .06–.12, text off-white (247,248,248) with secondary ≈ (138,143,152),
  inset 1px top highlight instead of drop shadows.

## 3. Space and rhythm

- **Closed spacing scale:** the scale in [design-foundations.md](design-foundations.md), plus 96, 128, 160
  for marketing sections. Snap stray values to the nearest step.
- **Three gap bands, each ≈2–3× the previous:** inside a component 4–12 · between
  related groups 24–48 · between page sections 48–72 mobile, 96–160 desktop (Linear 128, Attio 152,
  Notion 96, Figma 80). 8px is the most frequent gap on nearly every site.
- **Airy sections, tight clusters.** The contrast between generous section
  padding and dense 8–12px meta clusters is what reads as designed (Dribbble).
- **Containers:** page chrome 1200–1440px; prose 680–800px (≈ the 60–75ch measure in design-foundations); docs sidebar 240–300px.
- **Shared alignment across siblings:** in side-by-side cards, titles, prices,
  lists and buttons start at the same Y.

## 4. Radius, borders, elevation

- **Pick a radius camp** — it is a brand decision, and no curated site mixes them:
  - *Tool / SaaS:* pill buttons and tags + 12–24px cards + 6–8px controls.
  - *Editorial / luxury / agency:* 0–4px everywhere.
  - *Middle:* 8–10px everywhere (Kobbe, UX Folio).
  Don't default to 8px on everything without choosing.
- **Nested radius:** inner = outer − gap, when the gap is under 32px and the
  result is above 2px; otherwise leave the inner shape square.
- **Hairlines over shadows, used for meaning.** 1px (Linear 0.5px) at
  rgba(0,0,0,.05–.10) light or white .06–.12 dark, or a 1px ring shadow
  (`0 0 0 1px rgba(0,0,0,.16)`). Borders go all the way around a card or not at all.
  Per design-quality, don't put hairlines on everything — separate with space first.
- **Shadows only on floating layers** (menus, popovers, dialogs, product mockups),
  layered and faint: `0 0 0 1px rgba(0,0,0,.02), 0 2px 6px rgba(0,0,0,.04)` (Airbnb);
  Notion alpha .01–.02.
- **No decorative background gradients.** Gradient is acceptable as subject
  imagery (sky, material) or texture, not as section fill.

## 5. Component metrics (measured)

| Element | Range | Default |
|---|---|---|
| Body (marketing) | 16–18 / 1.5 | 16/24 |
| Body (product UI, docs chrome) | 14 / 1.4–1.5 (13 only in dense tables) | 14/20 |
| Prose | 16 / 1.6–1.75, 680–800px | 16/28 |
| Meta, labels | 12px minimum (floor: design-foundations); caps +0.06–0.12em | 12px |
| Compact control | h 28–36, pad 0 10–16, 14px/500 | h32 |
| Primary CTA | h 40–48, pad 0 20–24, 14–16px/500 | h44 |
| Input | h 32–44, 1px border, control radius | h40 |
| Card | pad 16–32, hairline **or** tint (not both + shadow) | pad 24 |
| Code | mono 12–14 / 1.4–1.6 | 13px |

Primary on dark grounds: inverted white pill + ghost pill secondary. A trailing
glyph (→ ↗) on the CTA is common; it is also listed as a template device — use
only when the link genuinely navigates onward.

Every interactive component ships hover, active (`scale(.98)` or 1px down),
focus ring, disabled, loading (skeleton shaped like the content) and error.

## 6. Composition

**Hero patterns observed:** centered stack (statement products); headline
anchored bottom-left/right over full-bleed media (brand/editorial); 50/50 split
(commerce); asymmetric offset column (calm SaaS); app-shell (tools, docs).
Choose by subject; avoid the default centered stack when nothing calls for it.

**Every strong hero has one bespoke visual** — product UI working at real size,
product UI composited over photography, real photography, illustration or 3D
made for the subject. Zero curated sites used gradient blobs + icon grids.
**Test: remove the imagery.** If the layout collapses into plain, the craft was
in the image, not the system.

**Signature moves (pick at most one per page, with a reason).** They overlap
the devices in [design-quality.md](design-quality.md) §2 (italic word, glow):
they are Reflex rules, so one needs the waiver line from
[gate-tiers.md](gate-tiers.md) §1.


- headline interacts with an object (selection box around a word, icon replacing
  a letter, product overlapping the type)
- one phrase in a different tone or face (ink + grey continuation; italic serif word)
- microtype as ornament (local time, coordinates, counts in nav, status dot)
- texture (grain, glow behind a product frame)
- radical restraint (one weight or one size across the site; small type in a corner)
- deliberate asymmetry once (offset column, 1-wide + 2-narrow split, index rail)

**Current template look (2026 SaaS kits, seen near-identically on 5/19 templates)** —
the device list is owned by [design-quality.md](design-quality.md) §2; this is the observed
kit. Treat as defaults to avoid unless the idea demands one piece:
eyebrow pill → two-line headline with a grey or accent second line (9/19) →
grey subhead → ink + ghost buttons → "no credit card" micro-line → product mock
fading into a pastel aurora; Tiempos/Instrument Serif headline over Geist;
blueprint frames (dashed rails, "+" corner marks, hatch bands, dot-grid cards);
library effects (orbiting integration icons, shimmer/star-border buttons, dual
marquees, container-scroll hero); avatar stack + "Rated 4.8" pills; dark + neon
shader blob; particle vortex.

**Moves that read as designed (best-rated templates):**
- bottom-anchored photo hero: real full-bleed photo/video, h1 bottom-left, offer
  and CTA bottom-right (6/19)
- domain artifacts instead of generic cards: pricing as membership cards,
  a class schedule with "2 spots left" and Book/Waitlist, real team portraits,
  kanban column totals, stickers for a taco bar
- coded micro-UIs with believable data (event stream, workflow graph, inbox
  with AI draft) instead of screenshots; mask-fade their edges
- tactile button: inset 1px top highlight `inset 0 1px 0 rgb(255 255 255 / .9)`
  (light) or `/ .28` (dark)
- hairline depth `0 0 0 1px rgb(0 0 0 / .04), 0 1px 2px rgb(0 0 0 / .05)`
- one light→dark section shift mid-page for rhythm without decoration
- text-link CTA with underline and arrow on brand sites instead of a filled button

**Section order observed by page type** — a description of what templates do,
not a recipe. Build the order from the section argument in
[design-quality.md](design-quality.md) §1; use these only to check nothing
the visitor needs is missing.
- SaaS: hero → proof → features → how it works → testimonials → pricing → FAQ → CTA.
  This is the default skeleton design-quality warns against; 11 sections (SalesHook) is too long.
- Local service: hero + offer → why → services → schedule → pricing → people →
  reviews → location → FAQ → offer again (people before reviews).
- Brand / agency: wordmark or photo hero → selected work → manifesto → stats → contact.

**Data and dashboards:** card titles as plain-language sentences plus a one-line
subtitle saying what the chart shows; direct labels instead of legends; status
pills that state the consequence ("$2.9M short at commit"). The most
production-ready Dribbble shot was the least flashy one built this way.

## 7. Motion

Durations, easing, token names, reduced motion and the reveal-must-not-hide
rule live in [motion.md](motion.md) (§2, §4, §7); this section keeps only
what the sites showed.

- Observed: scroll reveals rise 24–32px and fade, once; staggered lists ~60ms
  per item.
- Reveal-on-scroll left whole viewports blank on two templates when landing
  mid-page (anchor link, refresh, print); see motion.md §7.
- Motion that earned its place: hero image growing with scroll, statements
  filling with ink, letter-rise on a wordmark, physics on playful brand stickers.
- Operational screens: motion only to explain change ([motion.md](motion.md) §1).

## 8. Content realism

- Real draft copy in the product's voice; no lorem or "Your headline here".
- Sample data for prototypes uses believable, non-round numbers, varied dates,
  region-appropriate names; never stock "Acme".
- **Never invent proof** on a real product's page: prices, customer counts,
  testimonials, logos come from the user; otherwise a marked placeholder `{{price}}`.
- Avoid filler: "revolutionize", "supercharge", "cutting edge", "effortless",
  "seamless", "next level", "harness the power", "world class"; Thai equivalents
  such as "ยกระดับ", "ไร้รอยต่อ", "ครบจบในที่เดียว" without a concrete claim.
- Sentence case for headings and buttons (Latin).
- System messages are calm and specific: "ส่งใบแจ้งหนี้ถึง Dana แล้ว";
  "อัปโหลดไม่สำเร็จ ไฟล์เกิน 20 MB".

## 9. Thai and mixed-script typography

Measured on Wongnai, LINE MAN Wongnai, SCB, Agoda, Nike TH, Apple TH.

- Thai display faces with small x-height (DB Heavent, Sukhumvit) are set 2–4px
  larger than the Latin equivalent.
- Thai body line-height as observed (rule: [design-foundations.md](design-foundations.md) Typography; LMWN 16/26, Wongnai 16/24 and 18/28, SCB
  14/25.2, Nike TH 16/28). Agoda's 14/18 (≈1.3) crowds stacked marks — treat
  ≤1.35 on Thai body as a defect to inspect.
- Thai display line-height follows design-foundations (never the 0.85–1.0 Latin
  display values; check marks don't clip). Set `:lang(th)` overrides.
- No negative tracking on Thai; none of the Thai sites tighten Thai text.
- For product UI choose one family covering both scripts (IBM Plex Sans Thai,
  Noto Sans Thai, LINE Seed Sans TH, Anuphan); pair a looped body face with a
  loopless display face only for brand voice.

## 10. Gallery work vs shippable UI

Learn the restraint and scale contrast; don't copy:

- device mockups, tilt, motion blur, scenes (12/14 Behance, 7/18 Dribbble)
- body or UI text at 8–10px; scattered micro-copy over busy images
- text on photos without contrast checks; dimmed half-paragraphs below 4.5:1
- fake or impossible data, placeholder logos, invented social proof
- single-viewport compositions with no mobile reflow (ghost wordmarks, 160px text)
- justified narrow columns, long all-caps body text
- AI hero art as the whole design idea

Only 4/14 Behance projects showed interaction or error states; galleries are
evidence of visual direction, never of usability.

## 11. Correct-but-plain tells

| Tell | Fix |
|---|---|
| 1.5 line-height and 0 tracking on big headlines | §1 tables (Latin only) |
| Bold 700 on headlines and every label | display 400–500, labels 500 |
| #000 on #fff | ink on off-white ground |
| Many sizes in the 13–24px band | named styles on one scale; drop the middle band |
| Many greys | three tones or ink alpha |
| Brand color on every button, icon, heading | ink primary; accent ≤3 per viewport |
| Equal 16px gaps everywhere | three gap bands |
| Mixed radii; 8px on everything by default | choose a radius camp; nested formula |
| Bordered + shadowed card for every block | space first; hairline or tint; shadows only on floats |
| Gradient blob / icon-in-tinted-square grids | one bespoke visual from the subject |
| Two or more signature moves at once | keep one |
| Orphan word on headline last line | `text-wrap: balance`, manual meaningful breaks |
| Round fake numbers, "Acme", filler verbs | §8 |
| Thai at 1.3 line-height with tracking | §9 |

## 12. Starter presets

Only when no design system exists, after the idea sentence. Swap palette and
face for the subject; a preset is a metric bundle, not a look to ship as-is.

**A. Neutral product (light)**
```css
--font: "Geist", "IBM Plex Sans Thai", system-ui; --mono: "Geist Mono", ui-monospace;
--ground: #fafafa; --surface: #fff; --surface-2: #f4f4f5;
--ink: #171717; --ink-2: rgb(23 23 23 / .62); --ink-3: rgb(23 23 23 / .45);
--line: rgb(0 0 0 / .08); --accent: oklch(.58 .2 258);
--r-control: 8px; --r-card: 16px; --r-pill: 9999px;
--shadow-float: 0 0 0 1px rgb(0 0 0 / .04), 0 8px 24px -6px rgb(0 0 0 / .10);
--ease: cubic-bezier(.22,1,.36,1);
/* 12/16 · 14/20 · 16/24 · 20/28 −.01em · 30/36 −.015em · 48/52 −.02em · 64/66 −.03em; 400/500/600 */
```

**B. Dark technical**
```css
--ground: #0b0b0c; --surface: rgb(255 255 255 / .03); --surface-2: rgb(255 255 255 / .06);
--ink: #f4f4f2; --ink-2: rgb(244 244 242 / .6); --ink-3: rgb(244 244 242 / .4);
--line: rgb(255 255 255 / .08); --highlight: inset 0 1px 0 rgb(255 255 255 / .06);
```

**C. Editorial / brand**
```css
--display: a text serif or foundry grotesk at 400; --ui: grotesk;
--ground: tinted off-white from the subject; --ink: dark tint of the brand hue;
--r-*: 0–4px; shadows: none; labels caps 12px +.08em; body 17/28.
```

**D. Thai-first** — add to any preset
```css
:lang(th) { letter-spacing: 0; line-height: 1.6; }            /* body 1.55–1.7 */
:lang(th) :is(h1, h2, h3) { line-height: 1.25; }             /* display 1.15–1.25 */
```

## 13. Craft pass

After UX decisions and the idea sentence are settled:

1. Map project tokens (or a preset) onto §1–§4 roles; define named text styles.
2. Reduce: one radius camp, three text tones, one accent, few type steps.
3. Set display type: weight, tracking, line-height by size; balance line breaks.
4. Apply the gap bands; replace containers that spacing can do.
5. Shadows only on floats; hairlines only where they carry meaning.
6. One bespoke hero visual plus a visual anchor in most sections
   ([visual-assets.md](visual-assets.md)); at most one signature move.
7. Content realism pass (§8).
8. Render desktop + 390px; run the design-quality critique and
   `scripts/contrast.py`; compare side by side with one benchmark site of the
   same category from the evidence files.

Ship checks (marketing pages): skip link, focus rings, current nav item, no `#`
links, 404, legal links, favicon, title/meta/OG, alt text, form validation,
no horizontal overflow at 390px with the primary action in the first screen.

## Credits

Content realism, nested-radius threshold, named text-style groups, motion
easing and ship checklist adapted from
[elayadesign/ai-design-skills](https://github.com/elayadesign/ai-design-skills)
(MIT, © 2026 Elaya; parts derived from Leonxlnx/taste-skill, MIT). Not adopted
as rules, because the measurements contradict them or they conflict with
design-quality: banning Inter/Helvetica, banning italics, gradient-filled hero
headings, a mandatory word-by-word tagline reveal section, a fixed list of
dark backgrounds.

Do not cite these measurements as proof that a design converts or is accessible.
