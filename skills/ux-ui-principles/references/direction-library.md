# Direction library — pick a look from pictures, not adjectives

Every direction in `assets/directions/directions.json`, in four groups (company, premium, playful, atmospheric), each with
a rendered preview. Names and the idea of each direction follow the theme set of
the Hallmark skill (S97, see [sources](sources.md)); palettes, faces and surfaces here are our own approximations
for choosing a look, not copies of its files.

Users choose a look faster and more reliably from a picture than from a style
name. In testing, a user asked to see previews of every named direction three
times before choosing. Use this file in phase 3 when a public page, brand or
product needs a new look and DESIGN.md does not fix one. It complements
[design direction](design-direction.md) §7 (named directions), §8 (user words →
style) and §9 (interview).

Each entry is a **starting direction**, not a template. A direction sets
material, type voice and surface; it never changes the page pattern
([design direction](design-direction.md) §1–2). The dials (V · M · D = variance
· motion · density) are suggested starting values; tune them to the brief.

## 1. Procedure

1. **Filter by the subject**, not by taste: use the "Fits" and "Avoid for"
   columns. A company-marketing or B2B page usually starts from the *Company*
   rows; a consumer or youth brand from *Playful*; do not offer a direction in
   "Avoid for" unless the user asks for it.
2. **Shortlist 2-3 with pictures; six is only the cap of one picture sheet.** Previews are generated on demand (not committed; rebuild with
   `node scripts/build_previews.js --only directions` or
   `node scripts/direction_preview.js --ids <ids> --sheet`). Each
   direction has `assets/directions/previews/<id>.jpg`, plus labelled overviews
   per group (`sheet-company.jpg`, `sheet-premium.jpg`, `sheet-playful.jpg`,
   `sheet-atmospheric.jpg`) and `sheet.jpg` with all of them: read the images
   and show them (the sheets are for you to choose from; show the user 2-3 at a time). They
   are drawn from `assets/directions/directions.json` (tokens, type, surface,
   hero composition) on one neutral agency sample, so they compare fairly; they
   show colour, type voice, material and rhythm, **not photography**. Regenerate
   them with the user's own copy when it matters:
   `node scripts/direction_preview.js --ids dose,riso --brief "Headline|Sentence|Button" [--thai] [--out dir] [--sheet]`.
   Optional richer pictures: if the Hallmark skill is installed, its
   `<skills dir>/hallmark/references/themes/<slug>.jpg` (the *Preview slug*
   column) shows a bespoke first screen of a sample site. Without either, render a
   one-screen sketch yourself; never describe looks in words only.
3. **Say what each costs**: one line on risk for this subject, and which one you
   recommend and why. Lead with the recommendation.
4. **Ask once** (host question tool, ≤ 3 questions per [design workflow](design-workflow.md)
   "Asking well"). When the user asks for "more", show the next 2-3 from the
   other groups; never repeat shown ones.
5. **Record the choice** in the design context card: direction, dials, ground
   (light/dark), the Thai type pair ([design foundations](design-foundations.md)
   "Thai with Latin display faces") and one sentence on why it fits.
6. **Keep the previous version.** A direction change replaces the look; copy the
   existing files first ([design workflow](design-workflow.md) phase 5) so the
   user can compare.

Provide preview images only for the directions you actually offer; a preview of
a direction the user did not ask about is noise.

### Richer first screens

After reviewing 21st.dev ([study](../assets/21st-study.md)), the first screens
gained six compositions beyond the split hero: image fan, ring of thumbnails,
image accordion, full-bleed overlay with oversized type, centered headline over
a product mock, and a centered hero on a mesh background, plus an announcement
pill, avatar group with rating and a placeholder logo cloud. They are in
`assets/site/previews/sheet-hero-<group>.jpg` (`company`, `premium`, `playful`,
`atmospheric`) and in the `home` page. They are still drawn from palettes: real
photography, shaders and motion are what the reference pieces add on top.

### Beyond the first screen

A direction must be judged on a checkout, a dense table and a form, not only a
hero. `scripts/site_preview.js` renders the pages listed in [preview coverage](preview-coverage.md), every landing section and a
customer component sheet in six representative directions (`--all` for every direction), and
preview coverage maps the layout IDs to their
pictures and lists what is still missing. Compare the shortlisted looks on the
pages the project actually needs (`assets/site/previews/sheet-<page>.jpg`)
before choosing.

### Shape language

Previews differ in shape, not only colour, so a look is not read as "boxes with
a different palette". `directions.json` carries, per direction: `radius` (cards),
`btn` (pill, round or square), `corner` (even, leaf with asymmetric corners,
arch, or cut with a clipped corner), `art` (blocks, circle, stack, grid, lines
and the curved set blob, arch, wave, tilt, dots, diag, rings, pill) and `hero`
(settled, split, band and giant type, full-bleed with a panel, staggered tilted
tiles, arch frame). About half the directions are sharp (radius 0) because
their material is print, poster or technical; the rest are rounded, arched,
wavy or tilted. A direction should state its shape rule on the context card
("pill buttons, leaf-cornered cards, arch hero") so soft or sharp is a decision,
not a default.

### Adding or changing a direction

Add an entry to `assets/directions/directions.json` (id, group, ground, surface,
ink, muted, accent, accentInk, four tints, display and body Google Fonts
families, weight, case, tracking, radius, `btn`, `corner`, `surf` = flat · outline ·
offset · lift · plastic · sticker · paper, `hero` and `art` (see Shape language)), run `scripts/direction_preview.js --ids <id> --sheet`,
look at the picture, and add a row to §2. A preview is a sketch of the material,
not a finished page: check the real direction on a rendered page of the
project before delivery. The faces in the file are Google-Fonts approximations
of each direction's real faces.

## 2. Directions

Group · name · idea · material (ground, ink, accent) · display voice · V·M·D ·
fits · avoid for · risk · Hallmark preview slug.

### Company and professional

| Direction | Idea and material | Display voice | V·M·D | Fits | Avoid for | Risk | Slug |
|---|---|---|---|---|---|---|---|
| **Dose** | Daylight on translucent tinted plastic bands; warm paper with fibre grain, green-black ink, one green | Grotesk bold, mono for times and labels | 4·3·4 | Care, family, calm B2C, an approachable company or agency | Aggressive or hard-sell brands | Reads soft if every band is a different tint; keep one green for all signals | `dose` |
| **Terrazzo** | Catalogue cards on a hard offset; off-white ground, outlined cards, mono codes | Wide grotesk | 4·2·6 | Catalogues, B2B, many services or projects | Emotional brand storytelling | Looks like a sample room if there is no real content | `terrazzo` |
| **Cobalt** | Cool near-white, hairlines, one blue; precise and technical | Neo-grotesk | 3·3·6 | SaaS, developer and data products | Consumer or craft brands | Generic SaaS look without a real product fragment | `cobalt` |
| **Studio** | Proof paper with ink dot grid and construction lines; the brand drawn as a spec | Serif or grotesk, measured | 4·3·5 | Identity and branding studios, design consultancies | Fast-moving retail | Gets precious; keep the guides to the hero | `studio` |
| **Grid** | Swiss poster blocks: white, one blue field, one red field, huge numerals | Heavy neo-grotesk, tight | 6·3·5 | Archives, institutions, bold corporate | Warm or friendly brands | Primary colours need real content to carry them | `grid` |
| **Almanac** | Cool slate stock, tables and data as the visual, one berry accent | Grotesk + serif | 3·2·7 | Reports, data, measurement-led services | Emotional brands | Dense; needs real numbers | `almanac` |
| **Midnight** | Midnight-blue ground to every edge, wide light type, one huge figure | Expanded light sans | 5·4·3 | Premium tech, finance, AI | Warm or analogue brands | Many dark-blue pages look alike | `midnight` |
| **Coral** | Warm grey felt desk, cotton paper stationery stacked in light | Soft grotesk | 3·3·4 | Calm SaaS, invoicing, services needing trust | Loud campaigns | Soft shadows everywhere; keep them to the paper | `coral` |

### Editorial and premium

| Direction | Idea and material | Display voice | V·M·D | Fits | Avoid for | Risk | Slug |
|---|---|---|---|---|---|---|---|
| **Editorial** | Warm white stock, heavy condensed heads, magazine rules and cover | Condensed heavy grotesk + text serif | 5·2·5 | Publishers, case-study-led agencies | Product dashboards | Needs strong photography | `editorial` |
| **Loom** | Ecru paper, a full-bleed photograph, light serif, a ruled timetable | Light high-contrast serif | 3·2·3 | Craft, luxury, hospitality; any firm with strong photos | Brands with no photography | Empty without a great photo | `loom` |
| **Specimen** | Oat paper, razor-hairline Didone, glyph grids | Didone display | 4·2·4 | Type, fashion, luxury editorial | Thai-first pages (no matching Thai) | Thai pairing is hard; test early | `specimen` |
| **Riso** | Two-colour drum overprint, one-tone photos, no black | Heavy grotesk in one blue | 5·3·4 | Studios, print, culture, premium-but-playful agencies | Brands that need many colours | Two inks only; every image must be one-toned | `riso` |

### Playful and bold

| Direction | Idea and material | Display voice | V·M·D | Fits | Avoid for | Risk | Slug |
|---|---|---|---|---|---|---|---|
| **Paste-up** | Kraft board, copy-paper sheets on lifted shadows, one fluorescent sheet, B&W photos | Condensed caps + serif | 5·3·4 | Zines, events, creative collectives, craft-minded agencies | Corporate or finance | Reads punk; keep tilt to three surfaces a screen | `pasteup` |
| **Sticker** | Warm paper, tilted rounded tiles with white edge and hard shadow | Heavy rounded caps | 7·5·3 | Consumer, youth, retail | Enterprise trust | Reads young | `sticker` |
| **Hum** | Grainy paper, torn edges, pillowy moulded controls, several soft accents | Rounded sans | 5·5·3 | Kids, learning, friendly apps | Premium or serious brands | Many colours; hold the accent rule | `hum` |
| **Halftone** | Butter cream, red slab and dot screen, back-of-the-can facts | Ultra slab serif | 6·3·4 | Food, drink, consumer products | Technical products | Heavy; use for one hero and one table | `halftone` |
| **Carnival** | Poster condensed caps, one full-bleed red band of numbers | Condensed caps | 7·4·4 | Events, food, bold claims by the numbers | Quiet professional services | Loud; numbers must be real | `carnival` |
| **Werkstatt** | Putty ground, Bauhaus primary blocks, weekly timetable | Geometric caps | 6·3·5 | Workshops, education, process-led agencies | Gentle premium | Primary colours need a rule for each | `werkstatt` |
| **Squeeze** | Forest green, rounded plan cards, giant price | Rounded bold sans | 4·4·4 | Subscriptions, food, plans | B2B | Reads like a food subscription | `squeeze` |
| **Overprint** | Dark photo hero, wide heavy caps, a printed ticket | Extended heavy caps | 7·4·3 | Venues, music, events | Services with no photos | Needs dark, atmospheric photography | `overprint` |
| **Brutal** | Black rules, boxed cells, one yellow highlight, B&W photography | Heavy grotesk | 7·2·5 | Design studios, bold portfolios | Trust-first services | Hard edges tire on long pages | `brutal` |

### More directions (the rest of the set)

Directions already in a table above are not repeated here. Same columns, shorter: material is in `assets/directions/directions.json` (`note`).
Dials are not listed; start from V 4 · M 3 · D 4 for light directions and tune.

| Direction | Group | Fits | Avoid for | Risk | Slug |
|---|---|---|---|---|---|
| **Petal** | Premium | Beauty, wellness, boutique agencies, gifting | Technical products | Rose accent turns saccharine without real photography | `petal` |
| **Linen** | Premium | Interiors, craft, slow brands, hospitality | Fast retail | Needs real daylight photographs | `linen` |
| **Opal** | Premium | SaaS, fintech, modern agencies that need trust | Heritage | Indigo plus rings drifts generic; keep one idea | `opal` |
| **Honey** | Premium | Food, craft, family services, friendly B2B | Cold technical | Amber on cream fails contrast for small text; use ink | `honey` |
| **Mochi** | Premium | Consumer apps, community, education | Formal finance | Chunky tiles can read childish; tighten copy | `mochi` |
| **Fjord** | Premium | Health, clean energy, consultancies, logistics | Loud campaigns | Teal-on-pale needs tested contrast | `fjord` |
| **Velvet** | Premium | Luxury services, culture, events, premium agencies | Fast utilitarian tools | Serif display needs a Thai face that matches | `plum2` |
| **Sorbet** | Playful | Friendly agencies, food, youth, creative studios | Trust-first finance | Reads playful; premium only if type and spacing are disciplined | `sorbet` |
| **Atelier** | Premium | Galleries, studios, interiors, boutique consultancies | Fast retail | Needs real daylight photographs | `atelier` |
| **Garden** | Premium | Wellness, food, sustainability, family brands | Tech or finance | Cosy; keep one leaf-green signal | `garden` |
| **Hedgerow** | Premium | Heritage, food and drink, estates | Data products | Dark green on every section tires | `hedgerow` |
| **Ink** | Premium | Plain publishers, tools with state, documentation | Brand storytelling | Can look unstyled; needs real type scale | `ink` |
| **Newsprint** | Premium | Newsletters, local media, long reading | Product marketing | Dense columns on phones | `newsprint` |
| **Solstice** | Premium | Hospitality, wedding, culture | Technical products | Gold hairlines look dated if overused | `solstice` |
| **Vellum** | Premium | Heritage, legal, history | Modern tech | Blackletter heads need very short copy | `vellum` |
| **Broadside** | Premium | Announcements, auctions, events | Services pages | Heavy; one hero line only | `broadside` |
| **Formwork** | Premium | Construction, architecture, materials | Soft consumer brands | Reads cold without photographs of the material | `formwork` |
| **Blueprint** | Company | Engineering, infrastructure, B2B technical | Warm brands | White line only; hard on long text | `blueprint` |
| **Console** | Company | Operations, monitoring, dev tools | Consumer brands | Dark dashboards all look alike | `console` |
| **Dusk** | Company | Product companies with one strong product shot | Services with no product | Needs a real landscape or product image | `dusk` |
| **Furrow** | Company | Field work, logistics, maps, surveys | Luxury | Map art must be real | `furrow` |
| **Rim** | Company | Space, earth, geo, data from above | Warm retail | Needs real imagery | `rim` |
| **Ultraviolet** | Company | Modern SaaS and creative tools | Heritage brands | Violet is a trend; check against competitors | `ultraviolet` |
| **Vantage** | Company | Security, scanning, discovery products | Soft brands | Needs a live data visual | `vantage` |
| **Wayfind** | Company | Technical and civic services, wayfinding | Warm consumer | Mono for everything reads austere | `wayfind` |
| **Bloom** | Atmospheric | Hardware, devices, product studios | Services with no product | Generated visuals must be real, not stock | `bloom` |
| **Darkroom** | Atmospheric | Photography, film, studios | Bright consumer brands | Needs strong black-and-white work | `darkroom` |
| **Kiln** | Atmospheric | Craft, restaurants, makers | B2B SaaS | Needs photographs lit by the work | `kiln` |
| **Lumen** | Atmospheric | AI, tools, creative technology | Warm brands | Many dark serif tool sites exist | `lumen` |
| **Refract** | Atmospheric | Water, clean tech, light | Dense data | The live light effect is the page | `refract` |
| **Ribbon** | Atmospheric | Time, scheduling, devices | Heritage | The generated canvas carries the page | `ribbon` |
| **Spore** | Atmospheric | Hospitality, food, wine | Technical products | Dark warm pages need good lamps-and-candles photography | `spore` |
| **Terminal** | Atmospheric | Developer tools, CLIs | Everyone else | Hard to read for non-developers | `terminal` |
| **Arcade** | Playful | Games, youth, creative technology | Trust-first services | Reads gaming-only | `arcade` |
| **Manifesto** | Playful | Campaigns, petitions, causes | Soft brands | Loud; claims must be true | `manifesto` |
| **Piste** | Playful | Sport, outdoor, fitness | Quiet premium | One cobalt only | `piste` |
| **Sport** | Playful | Sport, performance, timing | Gentle brands | Volt fill is a strong signal | `sport` |

The previews of atmospheric directions show palette and type only; their live
or generated visual (point cloud, caustics, canvas) must be built separately.

## 3. Choosing for company marketing

When the user says "company", "corporate" or "marketing company" without more:

- **Premium and friendly (the usual agency brief: "premium + playful")**: start
  here, with rounded or mixed shapes: Petal, Opal, Honey, Fjord, Velvet, Sorbet,
  Dose, Atelier. A sharp print look (Riso, Werkstatt, Grid) is not the answer to
  "friendly".
- **Professional with warmth** (most agencies): Dose, Terrazzo, Studio, Editorial.
- **Professional with a point of view**: Riso, Werkstatt, Grid, Loom (if photos exist).
- **Techy or data-led**: Cobalt, Almanac, Midnight.
- **Every set of three recommendations includes at least one rounded or mixed
  direction.** Do not offer three square ones, and say which of the three is the
  softest.
- Offer one playful option (Paste-up or Sticker) only to show the range, and say
  that it trades trust for personality.

## 4. After the choice

- Map the chosen direction to tokens before writing markup: ground, ink, one
  accent, type pair (Latin + Thai), radius camp, surface rule (tone steps,
  hairlines or shadows), motion level.
- Write the rules the direction forbids on the context card (for example
  "no soft shadows on controls", "red is never a warning").
- External skills may carry the same directions with stricter rules; follow the
  precedence in [SKILL.md](../SKILL.md) "Working with other design skills".
