# Design quality — avoiding the generic look

UX correctness does not make a page look designed. Pages produced quickly
(by people or by AI) tend to converge on the same defaults, and visitors read
those defaults as "template". This file is the skill's own checklist for
distinctive, intentional visual work, especially public pages (landing,
marketing, product). It complements [visual-craft.md](visual-craft.md) (focal
point, signal budget, feedback diagnosis) and [customer-ui.md](customer-ui.md)
(page structure and content).

It was written after a landing page went through three rounds: a "blueprint"
version full of template devices, a cleaner version that still had them, and
a final version built around working product fragments. The lessons below are
project recommendations; they are taste guidance, not research findings.

## 1. Plan before code, then review the plan

Write a short plan first, then compare it with what you would produce for any
similar brief. Change every part that would come out the same.

| Plan item | Write |
|---|---|
| Subject, audience, the one action | One line each |
| Subject inventory | 8–12 things that belong to this client and no competitor: name and its meaning, place, numbers, constraints, materials, rituals, printed artefacts of its world |
| The idea | "On this page, **[something from the inventory]** becomes **[the main visual device]**." |
| Competitor test | Put the nearest competitor's name in the sentence. If it still works, the idea is the category, not the client; strengthen it or record that the brief lacks the information |
| One live thing | One thing the visitor can do with real content (pick their problem and operate a fragment, choose an option and see the result), works on a phone and without script |
| Tokens | Ground, ink, one accent (plus at most one field colour); one typeface, two at most; 3–5 type sizes used ([design-foundations.md](design-foundations.md)) with a decisive jump from body to headline |
| Section argument | One line per section: the claim and its proof. Delete sections with no claim; don't default to hero → logos → three features → testimonial → pricing → CTA |

If the brief lacks subject facts (as with a company whose site can't be read),
say so; a page built on category ideas will look like the category.

## 2. Template devices to avoid by default

This section owns the device list; other files link here. The devices are Reflex
rules ([gate-tiers.md](gate-tiers.md) §1): use one only when the brief asks for it
or you can defend it in one sentence, which is the waiver line. This list removes
defaults; it does not remove visuals. Every device you drop must be replaced by
a visual anchor from [visual-assets.md](visual-assets.md), not by empty space.

| Device | Use instead |
|---|---|
| Small uppercase or monospace label above every heading ("eyebrow") | Put the information in the heading or first sentence |
| Monospace for captions, labels and numbers outside code | The text face with tabular figures |
| Index numbering (01 / 02 / 03) on content that is not a sequence | Position, size and words; a real ordered list only for real sequences |
| One word in the headline in a different color, italic or weight | Let the words carry emphasis; one face, one colour |
| Rows of identical rounded cards with an icon in a tinted square | Varied compositions: bento with one large fragment, icon-led lists, splits. Icons themselves are fine with labels in one family ([visual-assets.md](visual-assets.md) §3) |
| Hero-metric template (big number + label + supporting stat); sparkline or progress-ring filler | The one number that matters, in its sentence or a real chart |
| Coloured `border-left/right` over 1px on cards or alerts; hard offset shadows (outside neobrutalism); gradient text; emoji or Unicode glyphs as icons | A tone step, a leading icon from one family, plain text |
| Hairline borders and grid lines everywhere | Space and tone steps between surfaces |
| Gradients as decoration; glows; soft grey shadows on resting elements | Flat colour; shadows only on things that float (menus, dialogs) |
| Dark navy or near-black with one neon accent, blueprint grids | A palette taken from the subject; a light or mid ground is fine |
| Warm cream background with serif display and terracotta accent | Same: choose from the subject |
| Middle-dot meta strings ("A · B · C") and "→" appended to links | Plain sentences and labels |
| Fake interfaces made of grey bars, browser/laptop frames | Real, working interface fragments with real labels and numbers, composed into a scene; a simple phone outline is fine on app pages ([visual-assets.md](visual-assets.md) §5) |
| Headlines of three or more lines | Cut words to fit two lines at every width (roughly 25–35 Thai/Latin characters at display size) |

## 2b. Structural slop — beyond surface devices

Ideas adapted from Hallmark's structural-variety and anti-slop approach
(S97). Surface devices (§2) are styling; structural slop is the *shape* of
the page coming out the same whatever the brief.

| Structural slop | Sign | Fix |
|---|---|---|
| Same skeleton for every brief | Hero → logo strip → 3 features → testimonial → pricing → CTA, regardless of subject | Section argument (§1): order sections by what this audience must believe, in what order |
| Every section the same composition | Centered heading + grid of N, repeated | Neighbouring sections use different compositions (§4) |
| Every heading decorated the same way | Eyebrow + heading + subline on all sections | Decorate none, or only the one that carries the idea |
| Forms with no behavior | Inputs and a button, no submit, validation, error, success | Specify the whole loop or show it as non-interactive |
| Components without states | Only default shown; no hover, focus, loading, empty | [component states](component-states.md) |
| Interchangeable dashboards | KPI tiles + one line chart + a table for every product | Start from the role's question — [design direction](design-direction.md) §2 |

**One strong idea.** One idea sentence per page (§1), not a collection of
trends. If two ideas compete, pick one and drop the other.

**Variety across products, consistency within one.** Two different products
should not share a skeleton. Pages inside one product must share tokens,
navigation, components and patterns; variety there is a defect.

**Respect an existing design.** If the product already has a recognizable
language, work inside it. Do not redesign unrequested pages or swap the style
to look "fresh"; propose it separately if you think it is warranted.

**Detect, then look.** `python3 scripts/slop_check.py page.html` flags §2 and
§2b patterns deterministically (eyebrow labels, accent-word headlines,
gradient text, identical icon-card rows, too many typefaces or radii, filler
copy, inert forms, removed focus, motion without reduced-motion). Each hit is
a prompt to inspect the render, not a verdict.

## 3. Substance — don't trade it for restraint

Removing ornaments leaves space. Fill it with **scale** (make the main thing
larger), **full content** (every section delivers its information), **real
pictures** of the subject's world or **working fragments** of the product, or
a **field of flat colour**. A clean but thin page loses to a richer page.

For software companies and apps, the strongest picture is the product doing its
job: small, believable, working fragments at real interface size (an approval
card you can approve, a table whose total updates, a booking slot you can pick),
not screenshots shrunk until unreadable.

## 4. Frame and rhythm

- Equal outer margins at every width; text blocks share two or three left edges.
- Gaps between sections clearly larger than any gap inside one.
- No section leaves half the width empty; close every void with its picture,
  list or figure.
- Neighbouring sections use different compositions.
- Carry the idea past the first screen: process, pricing, FAQ and footer too.
- The footer is a designed close (for example the name at full width), not a sitemap.

## 5. Look at the render and critique it

Use screenshots at desktop and phone width, not the code. Make each pass on its own:

1. One second: is there exactly one thing you remember? Five seconds: what is
   it, for whom, what to do?
2. Squint: two or three masses with clear size differences?
3. Cover the logo: could this belong to a competitor?
4. Edges: how many distinct left edges? (Two or three is composed.)
5. Space: accidental holes, empty half-widths, sections that look the same?
6. Type: decisive headline jump, ≤5 sizes, headlines ≤2 lines, no orphan word?
   No gap before punctuation ("address .") from letter-spacing or a fallback font?
7. Colour: where is the accent? Only on the action and perhaps one detail?
8. Pictures: real and doing a job, or decoration and placeholders? Does every
   content section have a visual anchor? More than a third text-only fails
   ([visual-assets.md](visual-assets.md) §1).
9. Phone: its own composition, or the desktop squeezed?
10. Template devices from §2 still visible?

Score honestly (design, usability, creativity, content); fix the top three
problems; look again. Three rounds at most. Report what still falls short.

## 6. Honest content

- Sample interface data and sample details are fine for showing density;
  list them for the client to confirm.
- Never invent proof: customers, logos, quotes, reviews, statistics or awards.
- Placeholders that must be replaced belong in a short note and the hand-off,
  not as decorative badges all over the page.

## Do / Don't

| Do | Don't |
|---|---|
| Write the idea sentence and run the competitor test before code. | Start from a hero-features-testimonial template. |
| Show the product working at real size. | Draw a dashboard of grey bars in a laptop frame. |
| Use one accent on the action. | Colour headings, icons, borders and one headline word with the accent. |
| Fit headlines in two lines at every width. | Let a 40-character headline wrap to four lines on a phone. |
| Fill space with scale, content or real pictures. | Fill space with labels, rules, gradients or blobs. |
| Replace each removed device with a visual anchor. | Answer the avoid-list with a page of text. |
