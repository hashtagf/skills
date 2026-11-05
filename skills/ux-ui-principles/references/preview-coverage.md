# Preview coverage — which page, section and component has a picture

Pictures help a team choose a direction and judge a design system on every kind of
page, not only a hero. This file maps the layout library's 43 blueprints, the
landing sections and the components to the previews shipped with the skill, and
says what is still missing. Previews are sketches of layout, type, shape and
component states drawn from a direction's tokens; they are not tested screens
(keyboard, focus order, loading, error and permission flows need a rendered
build) and use invented sample content.

Previews are **generated, not committed** (the `previews/` folders are
git-ignored; about 30 MB). The data (`assets/directions/directions.json`,
`assets/backoffice/styles.json`) and the generators are the source of truth.
Rebuild everything with `node scripts/build_previews.js` (about 10 minutes,
needs Playwright and network for fonts), one set with `--only
directions|site|backoffice|mobile|tablet|rtl|dark`, or a few pictures by calling a generator
with `--ids`, `--pages`, `--styles` or `--screens`. An agent that needs a
picture should generate just those instead of rebuilding all.

| Set | Generator | Output | Directions or styles |
|---|---|---|---|
| First screen per direction | `scripts/direction_preview.js` | `assets/directions/previews/` | every direction in `directions.json` |
| First screen with richer compositions (fan, ring, accordion, overlay, product mock, centered) | `scripts/site_preview.js --all --pages hero` | `assets/site/previews/sheet-hero-<group>.jpg` | 50 |
| Site pages, landing sections, customer components | `scripts/site_preview.js` | `assets/site/previews/` | 6 by default (`--all` for every direction) |
| Back office (desktop, phone), component library, page states | `scripts/backoffice_preview.js` | `assets/backoffice/previews/` | every back-office look in `styles.json` |

## 1. Pages: all 43 layout blueprints

`sheet-<page>.jpg` shows the directions side by side; `<direction>-<page>.jpg` is a full
single for the first direction. Back-office files are `sheet-<screen>.jpg` and
`sheet-m-<screen>.jpg`.

| ID | Blueprint | Preview |
|---|---|---|
| M01 | Product landing | site `home` |
| M02 | Service overview | site `service` |
| M03 | Pricing comparison | site `pricing` |
| M04 | Campaign landing | site `campaign` |
| M05 | Help or contact hub | site `help` |
| C01 | Product listing | site `listing` |
| C02 | Product detail | site `product` |
| C03 | Cart review | site `cart` |
| C04 | Checkout | site `checkout` |
| C05 | Booking | site `booking` |
| D01 | Operational overview | back office `overview` |
| D02 | Analytical exploration | back office `analytics` |
| D03 | Finance reporting | back office `finance` |
| D04 | Monitoring and incidents | back office `incidents` |
| D05 | Comparison workspace | back office `compare` |
| D06 | Matrix or heatmap | back office `heatmap` |
| — | Service status (uptime strips, resource cards, ring meters, ranked bars; widget patterns from `assets/21st-dashboard-study.md`) | back office `status` |
| A01 | Record management | back office `records` |
| A02 | Record detail | back office `detail` |
| A03 | Approval workbench | back office `approval` |
| A04 | Access management | back office `access` |
| A05 | Import wizard | back office `import` |
| A06 | Audit log | back office `audit` |
| A07 | Settings with save behaviour | back office `settings` |
| E01 | Article or documentation | site `article` |
| E02 | Knowledge base | site `kb` |
| E03 | Search results | site `search` |
| E04 | Course learning | site `course` |
| E05 | Community discussion | site `community` |
| P01 | Inbox master-detail | back office `inbox` |
| P02 | Kanban board | back office `kanban` |
| P03 | Calendar workspace | site `calendar` |
| P04 | Document editor | site `editor` |
| P05 | Collaboration workspace | site `workspace` |
| U01 | Sign-in and recovery | back office `signin` (recovery flow not drawn) |
| U02 | Setup onboarding | site `onboarding` |
| U03 | Profile settings | site `profile` |
| U04 | Security settings | site `security` |
| U05 | Subscription management | site `subscription` |
| B01 | Mobile task home | site `mtask` |
| B02 | Mobile detail and action | site `mdetail` |
| B03 | Appointment self-service | site `mbook` |
| B04 | Location search | site `mstore` |
| B05 | Upload or capture | site `mupload` |

Beyond the 43: site `about`, `blog`, `case`, `legal`, `order` (confirmation);
back office `denied` (403), `notfound` (404), phone set (`--mobile`: records,
approval, overview, inbox, detail, form, drawer menu, filter sheet, states,
components) and the page-states sheet.

## 2. Landing sections (site `sections`, one tall image per direction)

Announcement bar · navigation (bar; centered logo with mega menu) · hero (split;
centered with form) · proof strip (placeholders only; real logos need written
permission) · feature grid with icons · feature deep-dive (alternating) · bento ·
how it works · stats band · testimonials (sample; replace with real quotes) ·
case studies · gallery · pricing · FAQ · team · timeline · newsletter · contact
with map · CTA band · footer · cookie banner. The first-screen hero
compositions (settled, split, band, giant, full, stagger, arch) are in the
directions set.

## 3. Components

| Where | Covers |
|---|---|
| Site `components` (customer) | buttons (default, hover, focus, disabled, loading, danger, icon, link); text fields (default, focus, error with message, disabled, textarea with counter); select, autocomplete, date; checkbox, radio, switch, slider; quantity, size, colour, rating; tags, chips, badges; breadcrumb, tabs, stepper, pagination; accordion; alerts; toast, tooltip, popover; modal; cart drawer; dropdown menu; carousel, video; product, post and person cards; price display; table, code, quote; comments and chat; upload and progress; search with suggestions and filters; empty, error, skeleton; share and avatars; map and store list |
| Back office `components` | buttons and states, split button and menu, command palette, text inputs, select and combobox, multi-select chips, checkbox/radio/switch/slider, date picker, file upload, navigation, sortable table, list/card/key-value, accordion and tree, avatars/badges/KPI/progress, timeline, banners, toast, skeleton, empty and error, destructive dialog, drawer, popover, tooltip, filter bar and bulk actions, share dialog, profile menu, consent banner, notification matrix |
| Back office `states` | loading, empty, error, no permission, bulk partial failure, stale or offline |
| Phone `m-components` | app bars, bottom navigation with badge, FAB, 48px buttons and fields, filter chips, segmented control, swipe item, bottom sheet, snackbar with undo, pull to refresh, settings rows, confirm dialog |

## 4. Not covered yet

Hover and focus of customer-page components beyond the back-office matrix · RTL with real
Arabic or Hebrew strings (the RTL previews mirror the layout only) · RTL and tablet of customer
pages · rich-text editor beyond a toolbar and bubble menu · tablet previews of every back-office screen
(records, overview, approval, detail are shown). Photography is never shown: art is drawn from the
palette; see [visual assets](visual-assets.md) for sourcing real pictures.

Covered since the last list (back office `advanced`, `tablet/`, `rtl/`; customer `dark/`): editable
grid cell, drag reorder, color picker, rich-text toolbar, mention and tag input, notification
centre, onboarding tour, multi-step autosave form, password recovery flow, interaction-state
matrix for 12 components, tablet layout, RTL mirroring, dark customer pages. Rules:
[advanced components](advanced-components.md), [tablet, RTL and dark](tablet-rtl-dark.md).

## 5. Use

1. Pick the page IDs the project needs ([layout library](../assets/layouts/index.md)).
2. Open the matching `sheet-<page>.jpg` and compare directions on that page, not
   only on the hero; a direction that looks right on a landing may fail on a
   dense table or a checkout.
3. Record the chosen direction and the rules it overrides on the design context card
   ([direction library](direction-library.md) §4).
4. Regenerate with the project's own copy and palette when the sample content
   hides a problem: `node scripts/site_preview.js --ids <direction> --pages <pages> [--thai]`.
