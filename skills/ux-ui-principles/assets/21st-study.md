# 21st.dev study — what makes the gallery pieces look finished

Observed 2026-11-05 by browsing 21st.dev in a real browser: the home page, the
Templates grid, the component library (Heroes, Pricing, Galleries,
Testimonials, Dashboards) and their category lists. Screenshots were read by
eye; nothing was measured from live CSS, and no code or asset was copied. The
site is a gallery of community pieces, so it shows trends, not a standard.

## Scale and taxonomy

| Item | Count seen |
|---|---|
| Components | 12K (Heroes 1.2K, Buttons 1.7K–2K, Forms 1.5–1.7K, Cards 1.3–1.8K, Grids and Bento 620, Inputs 949, Dashboards 305–400) |
| Templates | 353 whole-site templates, each with a live demo |
| Themes | 962 (examples: Vercel, Catppuccin, Lime Frost, Claude) |
| Shaders / backgrounds | 363 to 609 shaders, 365 to 528 backgrounds |
| Icons, apps | 29,000 icons, 138 apps |

Marketing blocks listed: announcements, ASCII art, backgrounds, borders, calls
to action, clients, comparisons, docks, FAQs, features, footers, galleries,
gradients, heroes, hooks, images, maps, marquees, navigation menus, pricing,
scroll areas, shaders, stats and KPIs, steppers, team, testimonials, texts,
timelines, videos. UI components listed: accordions, AI chats, alerts, avatars,
badges, buttons, calendars, cards, carousels, charts, checkboxes, cursors,
dashboards, date pickers, dialogs, dropdowns, empty states, file trees, file
uploads, forms, globes, grids and bento, inputs, links, lists, menus,
notifications, numbers, onboarding, pagination, popovers, profiles, progress,
radio groups, search bars, selects, sidebars, sign-ins, sign-ups, sliders,
spinners, tables, tabs, tags, text areas, toasts, toggles, tooltips.

## Patterns that separate the strong pieces

1. **Imagery carries the page.** Most strong templates are built around one
   large photograph or generated visual, cropped into a rounded frame or run to
   the edge: soft natural light, macro textures (skin, water, glass, plaster),
   architecture, hands, products on plain grounds. A page without imagery looks
   like a wireframe whatever its type.
2. **Type laid over the picture.** Oversized display type sits on or against
   the image ("Skin, in good light.", "Architecture for everyday life.",
   a wordmark at poster size). The headline is part of the composition, not a
   box above it.
3. **Confident type pairs.** Large grotesk with a serif italic for emphasis;
   condensed display for agencies; tight tracking and 1.0 leading on display.
4. **Hero compositions beyond "text left, image right".** Image fan (3 to 5
   tilted cards), circular ring of thumbnails around the headline, image
   accordion (strips that expand), scroll-expanding media, centered headline
   over a product screenshot, full-bleed video or shader with a small caption.
5. **Backgrounds with depth.** Aurora and mesh gradients, grain, dither, dot
   fields, light beams, wireframe or particle shaders on dark grounds; on light
   grounds a soft radial glow. Used behind the hero only.
6. **Small proof details.** Announcement pill above the headline, avatar group
   with a star rating, logo cloud or marquee, big KPI cards ("99+"), sticker
   or doodle accents (arrows, scribbles) on playful brands.
7. **Pricing and cards with one emphasised tier.** A highlighted middle card
   (border, glow or inverted colour), monthly or yearly toggle, comparison
   table, usage slider; cards use a 1px border plus a very soft layered shadow.
8. **Galleries with depth.** Overlapping or rotated stacks, perspective walls,
   masonry with mixed crops, filmstrips, hover-expanding strips.
9. **Dashboards.** Light dashboards use a quiet sidebar, white cards on a
   tinted ground, area or bar charts in one hue and KPI cards with sparklines;
   dark and "fintech" dashboards use glass or gradient cards and a single
   saturated accent. Charts have soft gradients under lines.
10. **Interaction is part of the look.** Hover lifts, magnetic or liquid-glass
    buttons, scroll-linked reveals, number tickers. A still preview cannot show
    this; it needs motion specs ([motion](../references/motion.md)).

## What this means for our previews

- Our previews drew palette-coloured shapes. The gap to these pieces is
  imagery, depth (mesh, grain, glow, soft layered shadow), type laid over the
  picture and richer hero compositions, not more components.
- Added in `scripts/site_preview.js` (`--pages hero`, `home`): six hero
  compositions (fan, ring, accordion, overlay, product mock, centered), mesh
  and grain backgrounds, announcement pill, avatar group with rating and a
  placeholder logo cloud.
- Still missing: real photography (see [visual assets](../references/visual-assets.md)
  rung 1b), live shader or video backgrounds, and motion. Say so when
  presenting a preview.
- Conflicts: gradient, glow, glass and blur are banned by some other skills'
  house rules. Treat them as part of a chosen direction and record the override
  ([SKILL.md](../SKILL.md) "Working with other design skills").
