# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added (ux-ui: screen and text density)
- `visual-system.md` "Density" (owner): comfortable default + always available, compact opt-in app-wide (not per page), type scale and touch-target floor kept, alerts / small-target controls not fully compacted (Cloudscape, Material); text density per Tullis (overall/local density, grouping) and the "too much text" clutter item (Lewis & Sauro 2024).
- Thai measure: no published Thai line-length study found, so measured 10 Thai sites (article pages, 1440/390): desktop 53–95 graphemes/line, median ~70, ~1.75 graphemes/em; phone 30–43. Rule: Thai prose `max-width: 40em`, not `ch`; count per grapheme. Table in `assets/evidence.md` "Thai line length".
- `content-design.md` "Length caps": per-slot microcopy caps (button, label, helper, error, empty state, 25-word sentence), Thai word count with `Intl.Segmenter`, 30–40% translation headroom, counter rules.
- `measurement.md` "Perceived clutter": the five validated PCW items + overall item; content clutter → remove, design clutter → reorganize.
- `render_check.js` / `_composition.js` NOTEs: real characters per line (Thai per grapheme; > 90 Latin / > 80 Thai), > 8-line phone paragraph, running text > 50% of a public first screen, tables with different row heights (mixed density). Measure check now also sees `<p><span>…</span></p>` and sticky-wrapped content.
- Sources S110–S116; SKILL.md routes density / "แน่นไป" / copy length / "looks cluttered"; evals 127–130 (routing 4/4); 4 regression cases.

## [0.15.0] - 2026-11-08

### Added (test-design: Senior QA + PM / production readiness)
- `references/release-readiness.md`: Definition of Ready + numbered product questions for the PM, three-amigos pass, UAT script template (business language, per outcome) with sign-off and feedback triage (defect / change request / misunderstanding), go/no-go with named signers (PM, QA lead, engineering lead, security), deploy plan, feature-flag and migration-compatibility criteria, production smoke rules, rollback plan + staging drill (incl. what can't be reversed), watch window with numeric signals, analytics verification, hotfix path, per-level table.
- `references/execution.md`: scenario priority P0–P3 derived from the risk matrix, regression tiers (smoke / core / targeted / full) with impact analysis, test data plan (owner, reset, masking, time-dependent data), exploratory charters + debrief, bug lifecycle and severity vs priority, flaky / blocked / build-frozen rules, QA metrics (escape rate, reopen rate, blocked ratio) and a one-line stakeholder status.
- `checklist-library.md` §9b personal data / PDPA · GDPR, §9c analytics events, NFR "Production readiness"; `work-types.md` presets 13 (personal data, L4) and 14 (feature-flagged release).
- SKILL.md rules 11–14 (priority on every scenario; "tests passed" ≠ production-ready; QA recommends, PM + engineering decide; no real personal data in test data or tickets); workflow steps 8 Run and 9 Release; L1 gets a 3-line "After deploy" block.
- Evals 5–7: go/no-go, UAT script, bug report with personal data.

### Added (test-design: research pass — roadmap.sh QA + ISTQB CTFL v4.0.1, OWASP, WCAG 2.2, Fowler, Google SRE, Pact, chaos, Bolton/Bach, Android quality, PDPA)
- `checklist-library.md` §7c security baseline mapped to OWASP WSTG v4.2 / API Top 10 2023 / LLM Top 10 2025 (headers, CORS, XSS, SSRF, mass assignment, over-exposure, business-flow abuse, session, resource limits, SCA, secrets, prompt injection); NFR Accessibility rewritten to WCAG 2.2 AA with SC numbers (2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8, 1.4.10, 1.4.11); NFR Reliability (failover, pod kill, backlog, cache down, degradation, backup restore, cache invalidation); PDPA DSR deadline, 72-hour breach drill, cross-border transfer.
- `work-types.md` §15 AI / LLM feature (property-based criteria, golden set + pass-rate threshold, model/prompt versioning); contract testing and API4/API9 in §3; provider schema drift in §5; mobile §12 expanded (rotation, interruptions, process death, network switch, Doze, forced upgrade, crash/ANR).
- `taxonomy.md`: pyramid + agile testing quadrants; `planning-docs.md`: quadrant owners, layer per check, estimate basis, product vs project risk, test completion activities; `execution.md`: SFDIPOT and FEW HICCUPPS oracles; `release-readiness.md`: canary vs same-time control, SLO-burn alarms; Given/When/Then accepted as criteria syntax.

### Fixed (test-design: standards alignment)
- Test levels now the five of CTFL v4 (component integration and system integration added; acceptance forms incl. operational / regulatory); test types per v4 (functional, non-functional, black-box, white-box) with confirmation/regression separate; pairwise attributed to ISO 29119-4.
- **Renamed Test Summary Report → Test Completion Report** (ISO/IEC/IEEE 29119-3:2021, CTFL v4) everywhere; `scaffold.py` now writes `NN-test-completion-report.md`. Test Status Report = the one-line status.
- Personal-data auto-escalation narrowed to sensitive data or access to other people's data (eval showed a profile photo being pushed toward L4 → 16 scenarios at L2; re-run: 8).
- Sources: v3-era blog links replaced with the CTFL v4.0.1 syllabus, Fowler, roadmap.sh.

### Changed (test-design)
- Bug template: severity and priority as separate fields, environment, build, platform, account/data, reproducibility, evidence, impact; masking rule.
- Scenario table and spec carry Priority; traceability adds Priority and Build; test plan adds UAT, production verification, regression tier, exploratory, named roles and release exit criteria; summary report adds status line, results by priority, UAT, metrics, sign-off.
- `scaffold.py`: default priority per type, test data / product questions / exploratory / full bug template in the INDEX, L2 short-form release block, `NN-release-readiness.md` at L3+, roles and sign-off tables, L1 "After deploy" (en + th).

## [0.14.1] - 2026-11-08

### Fixed (ux-ui-principles scripts: 46 bugs from a bug hunt)
- Checkers: `slop_check` no longer hits RecursionError on deeply nested pages; `focus-removed` matches whole `outline` values only (`0.5px` is not removal, `0px` is) and `pure-black` ignores `border-color`. `contrast.py` reads selector lists spanning lines, treats `:root:not(.dark)` as light, resolves CSS named colours, opaque `/ 1` alpha and `!important`. `state_check --per-file/--matrix` scan every path; no sources → exit 2. `design_md_check` reads a UTF-8 BOM and no longer takes `15/10/2026` for a dial. `placeholders --md` and `review_report` give one `error:` line instead of tracebacks; review_report renders before an atomic write and bands fractional scores by their whole part.
- Tools: a corrupt `catalog.json` is an `error:` line, exit 2; `look.py` merges tag pools (templates before studies), accepts "ai chat", hints when pictures are not fetched, checks `--direction` first. `mobbin_fetch` validates its input and slugs (no writes outside `--out`). `design_md`/`export_tokens` treat null as missing, validate interview types, report `--out` problems, write atomically with normal file modes. `code_extract` parses `rgb(… / 50%)` and skips `href="#…"`. `halftone` rejects non-finite numbers; `photo_search` keeps Thai titles, de-duplicates names and protects `credits.json`; `tweaks_panel` inserts at the right place after case-changing characters; missing arguments print one `error:` line; `icons.py lucide` is case-insensitive.
- Node: `script_check` compiles modules with `node --check`, resolves `src="/…"` from the page folder, reads unquoted `src` and ignores `data-src`, reports unreadable or folder inputs as errors. `render_check` writes fragment wrappers to a temp folder and adds `--scroll-budget` (default 15 s, NOTE when cut). `flow_check` validates every step before the browser starts. `direction_preview --group/--width/--height` go to a temp folder (no longer overwrite library previews); `backoffice_preview --singles` works with `--out`; `build_previews` runs in the documented order with absolute `--out`. `market_fetch` accepts http(s) only; `_args.js` honours `--`; `_color.js` requires `#` for hex.
- Regression suites: 299 → 430 cases.

## [0.14.0] - 2026-11-07

### Added (one template library)
- `scripts/_library.py` reads every picture collection into one row shape: `kind`, `tags`, `verdict` (template / study), `take`, `comp`, `origin` (ours / generated / product), `local`, `source`. A new collection is one loader plus one row in `assets/LIBRARY.md`.
- `assets/LIBRARY.md`: schema, the collections with rights and rebuild commands, shared rules (take the move, never the look; local pictures stay local), how to add a collection.
- `look.py` prints one format for every picture: kind, composition, verdict, what it is (our build, designed page, real product screen), take, and a `from:` credit line; templates before studies, committed before local, one picture per app; warns when a listed picture is someone else's work.
- SKILL.md §3 step 2, `direction-library.md` and `design-workflow.md` point at the library instead of naming collections.

### Added (real product screens)
- `assets/mobbin/`: ranks 50–100 of Mobbin's latest web apps (51 apps × 4 screens, typed landing / product / auth): 11 template, 36 study, 4 skip, 57 tags (crm, finance, ai-chat, canvas, builder, inbox, marketplace, dev …), notes in our words. Pictures and signed URLs are git-ignored; `scripts/mobbin_fetch.py` rebuilds them (exit 0/1/2/3).
- `look.py <tag>` lists app screens by tag; synonyms login / signup / sign-in → auth, chat → ai-chat, การเงิน → finance, ล็อกอิน / สมัคร → auth.

### Changed
- Showcase *study* rows now load (before, only templates): new kinds `document`, `poster`, `social`, `careers`, `wireframe`, `motion`. `invoice` / `resume` / `เอกสาร` list the document studies first, then report and cover; "no pictures yet" prints only when none are on disk.
- `templates.md`: which output template per mode, depth per rigor tier, map of the other report formats; Phase 8 routes the deliverable by mode.
- Regression: library row shape, uniform `look.py` output, docs point at the library, Mobbin catalog integrity, tag lookup, `mobbin_fetch` usage error (299 cases).

## [0.13.0] - 2026-11-06

### Added (machine-readable checker output)
- `--json` on the Node checkers (`render_check`, `fold_check`, `admin_check`, `flow_check`, `script_check`): one JSON document on stdout (logs to stderr), same exit codes, also for usage errors, NOT RUN and load failures. Shared shape from `scripts/_report.js`: `script`, `target`, `result`, `exit`, `findings` (level/rule/message/where), `artifacts`. Text output unchanged.

### Changed (shared script contract)
- README "Script contract": exit 0 ok, 1 check failed, 2 usage/input error, 3 not run; levels PASS/FLAG/FAIL/NOTE/WARN/ERROR/N/A/NOT RUN; usage errors instead of tracebacks; `--help` everywhere; no output into cwd or the skill folder by default.
- Shared modules `_color.py`, `_color.js`, `_net.py` (curl `--fail`, atomic cache), `_args.js`; `_pw.js` safe goto/launch.
- `check.py` reads sub-script exit codes, flags `example.com` and `[..]` placeholders in meta, `--json`; `contrast`, `state_check`, `placeholders`, `review_report`, `design_md_check` move to argparse with `--json`.
- `look.py` real kinds first, Thai synonyms, nearest kind for document/invoice/resume; `code_extract.py` reads React Native/Expo; `tweaks_panel` contrast-safe accent text.

### Fixed (level-1 script bugs)
- `check.py` states can PASS, scans only linked sources, ERROR on a missing page; `admin_check`/`fold_check`/`render_check` real ERROR + exit 1 on a missing file or unreachable URL.
- `render_check`/`_composition` resolve oklab/oklch/color-mix to sRGB via canvas and wait for animations before measuring; `contrast.py` reads `[data-theme]`/`.dark`/`@theme` blocks, 0 pairs → exit 2 (N/A).
- `design_md.py` atomic write and quoted name; `design_md_check` errors on unsafe YAML and AA fails; one `shape_radii()` for `design_md` and `export_tokens` (`--shape`).
- `direction_preview` ad-hoc runs go to a temp folder (never overwrite library previews), errors on unknown ids/comp/subject.
- `slop_check`: icon-card-row ignores photos; new `mixed-icon-families` (flag), `mixed-icon-strokes` and `mixed-icon-fill` (note).
- `icons.py` brand marks use class `brand-mark` (`brand` clashed with the common logo-link class).
- Regression suites in `evals/regress/` (`run.py`): 292 cases across checkers, design, preview, Node, Python checkers and tools.

### Added (icon libraries)
- `iconography.md` "Icon libraries": Lucide for UI glyphs, Simple Icons for brand marks; delivery, version pinning, stroke rules, custom glyphs to Lucide's spec, trademark use, 3:1 brand colour check, missing Thai brands, no mixing in one row.
- `scripts/icons.py`: search both sets, paste Lucide SVG or sprite, brand SVG with contrast check and guideline/licence notes (pinned lucide 1.58.0, simple-icons 16.35.0). Sources S108–S109, eval #126.

### Added (market research, photo search)
- Round B always offers "research the market first" (`design-direction.md` §9). `assets/market/`: per-kind studies (category look, design-led moves, gaps, sourced facts), starting with a clinic study of 13 sites; screenshots rebuilt by `scripts/market_fetch.js`.
- `look.py` clinic/dental kind and prints the market study; `scripts/photo_search.py` searches Commons/Openverse with a licence filter and writes credits.
- `direction_preview.js`: shortlisted directions that share a composition get different ones; dental content pack.
- `export_tokens.py` without `--out` prints `tokens.css` to stdout and writes nothing.

### Changed (absorbed concepts from other design skills)
- No mentions of or routing to other skills; override and never-edit-a-checker rules restored in `design-memory.md` §2.
- Docs: verb playbooks, persona walk, new caps (`review-loop`); colour posture, accent budget, dark derivation (`color-palette`); surface layering, control tokens, wide-screen mechanics (`visual-system`); form lifecycle, copy tells, texture/scroll budgets, production-build gate.
- `slop_check.py` ~50 new rules (motion, layout, palette, type, controls, copy, headings, fake send); `render_check.js` composition checks (`_composition.js`); `state_check.py --per-file --matrix`.

### Changed (infographic lessons from the same café page)
- `visual-assets.md` §4: new recipe row "Choosing a physical product". Use a cross-section or anatomy infographic in the subject's vessel shape. Tell parts apart by fill and pattern, put a part list beside each item, and add a text summary. General proportions are labelled approximate; client facts are placeholders.
- `data-visualization.md` review checklist #11: no part may share its ground colour, and fills use theme tokens (a fixed dark fill vanishes in dark mode). Check both themes visually, because `contrast.py` does not test graphic parts.
- Reference `cafe-halftone-full.jpg` re-shot with the infographic.

### Changed (lessons from a café landing that went from correct to crafted)
- Diagnosis: the first build passed every check but read as unfinished because of boxed placeholders, a fake dot overlay, an empty photo slot, a heading-sized hero and flat bands with straight edges. A survey of 12 design-led roaster sites (Perc, Stumptown, Coava, Irving Farm, Tandem, Partners …) gave the fixes.
- New `scripts/halftone.py`: a real one-ink AM dot screen from a photo (`--size --cell --ink --paper --angle --bright --crop-x --eq`). `visual-assets.md` §2b: print-led directions print their pictures; dark or busy photos become a duotone band.
- Halftone direction (`directions.json`): an `images` rule and a Thai pair (Mitr 600 + Noto Sans Thai). `direction_recipe.py` prints `images` and uses a direction's `thai` value instead of always printing Noto Sans Thai.
- Placeholder mode (`marketing-copy.md`): `.ph` is now a dotted underline only, with no box, tint or outline.
- `design-quality.md` §1 adds **Subject edges**: one edge shape from the subject (awning scallop, perforation) at the hero bottom and the closing band. `visual-system.md` §13 adds poster-scale hero type for print directions and one break-out picture. `visual-assets.md` Do/Don't: a missing picture becomes a one-line spot drawing from the subject, not an empty box or a recropped photo.
- `SKILL.md` §3 step 2: when `look.py` lists fewer than three pages of the kind, screenshot 8–12 design-led sites of the category and take one move from each.
- Reference library: `cafe-halftone` (our own build).

### Changed (ux-ui-principles internal cleanup; each skill stays self-contained, no cross-skill links)
- **One value per topic inside the skill:** focus ring lives in `component-states.md` "Focus" (2px + 2px offset; 3px or two-tone on varied surfaces), referenced from `visual-system.md` and `design-system-benchmarks.md`; component token layer optional everywhere.
- **Merged:** `scoring-caps.md` → `review-loop.md` §8; `tablet-rtl-dark.md` split into `visual-system.md` Part B "Tablet", `i18n-performance.md` "Right-to-left", `color-palette.md` "Dark pages"; the duplicate Forms section in `patterns.md` now links to `forms.md`. Evals remapped.
- **README rewritten** as a per-file index (what / why / how) for all 90 files; new `evals/index_check.py` fails on a file without a row, a row without a file, or a broken markdown link.

### Added (enterprise back office)
- `scripts/admin_check.js` (+ `check.py --admin list|detail|form|dashboard`): rendered rules by page type — numeric columns right-aligned with tabular figures, disabled control with a reason, sticky bar that cannot stick, one primary action, table above the fold, row-height drift, read-only shown as input, long uppercase; `--states` renders every `?state=loading|empty|nomatch|error|denied|partial` and fails a state identical to the default page. `--admin` pages skip public metadata and the marketing fold rule.
- `assets/backoffice/styles.json`: every look gains `info` and `neutral` status tones (all ≥4.5:1) and a `compact` density; `backoffice_preview.js` maps pending → info, adds draft → neutral, and takes `--density compact`.
- Rules: permission treatment table, field-level read-only and audited Reveal, impersonation/tenant/environment banner, worklist vs list report (`back-office.md`); feedback timing table and five distinct empties (`component-states.md`); data type → filter → cell matrix and log-table histogram filter (`search-filter.md`); KPI tiers, definitions, thresholds, data-size and chart caps (`data-visualization.md`); URL-reachable states (`render-verification.md`); A05 import specifics and new **A08 Worklist** layout. Sources S103–S107 (secondary: published agent skills).

### Changed (lessons from a coffee-roaster storefront + back office, with Codex UI skills)
- `ux-ui-principles` shape: `design-quality.md` §1 adds **Subject shapes** (3–5 objects from the client's world decide corners, buttons, crops, signature); `direction_recipe.py` radius is a default, not a ban; `design-direction.md` §9 never skips the shape question; `direction-library.md` §4 checks the recipe against the subject; `design_md.py` philosophy line now matches the Shapes section and supports `shape_from_subject`; `slop_check.py` all-square becomes a flag (waive with `data-shape="sharp"`). Reason: a café was built square twice from Loom's radius 0.
- Placeholder mode (`marketing-copy.md`): facts as visible `.ph` placeholders when the user asks, proof never; new `scripts/placeholders.py` lists them into the hand-off.
- New checks: `scripts/fold_check.js` (CTA above 390×844 / 1440×900 fold, offer on the first screen), `scripts/flow_check.js` (JSON journey, fails on console errors), `check.py` public-page metadata line (title, description, canonical, OG, Twitter, one h1; skipped for `/admin/` and noindex), `slop_check.py` duplicate-image; `render_check.js` distorted images, decoration over text, Thai words split mid-word (note).
- False positives removed: `slop_check.py` (accent word on `.ph`, nested cards by class substring, validation on radio-only forms with defaults), `render_check.js` (hidden inputs measured by their label, closed drawers, sticky table headers, sticky/closed-details overlap, viewport shots now from the top, Thai heading line count), `state_check.py` (`aria-busy` / `submitting` / undo markers).
- `build-recipes.md` base CSS (`img{height:auto}`, `[hidden]{display:none!important}`, `.nw`), cascade trap; `i18n-performance.md` Thai loanword line breaks; `app-screen-rules.md` §9 (numbers from one source, answer in the title sentence, blocked action with visible reason, blockers first on phones, demo state switcher, checker marker names, noindex for admin).
- SKILL.md §3 (shape never skipped, recipe radius is a default, subject shapes in the plan, fold/flow/metadata/placeholders in delivery checks) and §5 (Codex `senior-ui-ux-orchestrator`, `webapp-ui-skill`, `marketing-site-skill`, `design-critic-skill`, `frontend-design` as second opinion and checkers; conflicts resolve to this skill).
- Reference library: `coffee-roaster-storefront` (kind `cafe`) and `coffee-roaster-backoffice` (product), our own builds; `look.py cafe` lists cafés first and no longer returns night-tour destinations. Evals 123–125.

### Added (coverage gaps + routing fixes from routing-v9, 89/100)
- `ux-ui-principles` new references: `search-filter.md` (Thai query handling, facets, URL state, saved views, no-results), `collaboration.md` (presence, locks/merge, conflict dialogs, comments, sharing, version history, offline sync), `email-design.md` (HTML email, Outlook/Gmail limits, Thai font fallbacks, dark mode), `print-documents.md` (invoices/ใบกำกับภาษี, print CSS, Thai PDF fonts, baht text, B.E. dates, PromptPay QR), `other-platforms.md` (kiosk/POS, desktop, watch, TV, voice, in-car, XR), `engagement.md` (fit test, streaks, loyalty, banned dark patterns), `research-methods.md` (method chooser, interview guide, survey, JTBD, blueprints, PDPA consent); `tokens-export.md` "Multi-brand and white-label theming". Unregistered sources sit in each file's "Sources (not yet in sources.md)" list.
- SKILL.md: routes for the new files; "listing `references/` is not opening a file"; empty-directory still routes; cross-cutting stack and change-existing-page rules; bold components-usage, navigation-grouping, mobile native for tab bars and RN/Flutter code, forms/patterns for checkout, design-quality §2 for redesigns, sources for "is there research" questions. Description trimmed to 981 chars.
- `evals.json`: ids 101–122 for the new routes.

### Added (Codex UI-skill study: orchestrator, webapp-ui, frontend-design)
- `ux-ui-principles`: `app-screen-rules.md` §7 operational-UI doctrine (scan-first, stable geometry, no nested cards, type caps, control-by-job, semantic palette, never-ship list, state matrix) from Codex `webapp-ui-skill`.
- `assets/backoffice/styles.json`: `canopy` look from the Canopy MongoDB-MCP dashboard (deep green #214f3e primary 9.3:1, warm off-white ground, light sidebar, muted text darkened to 6:1, separate status colors, line tables) with a records preview; `design_md.py --backoffice canopy` writes its DESIGN.md.
- Product-UI builds now follow the same must-do defaults as public pages (SKILL.md §3): pick a look from `styles.json`, load its real fonts, brand mark + one signature element, voiced empty/first-run states (`app-screen-rules.md` §8; hero allowed only as first-run). `assets/references/canopy-dashboard.jpg` added to the reference library. Reason: an A/B build produced generic system-font output.
- `scripts/state_check.py`: static state-coverage scan (loading/empty/error/disabled/focus/selected/submitting/success/hover); misses = unverified.
- `slop_check.py`: `viewport-scaled-font`, `nested-cards`, `hero-in-app` flags.
- `design-memory.md` §2: cross-domain conflict decision order with vetoes (from the Codex orchestrator council); `render-verification.md` + SKILL.md §6: Ran / Skipped / Planned / Manual evidence labels.

### Added (design-system study)
- `design_md_check.py` reports malformed token groups (non-map `rounded`/`spacing`/`typography`/`components`, non-string colors) instead of crashing; `ds_lookup.py` maps standard section names onto guides with another layout (Radix).
- `ux-ui-principles`: `references/design-system-benchmarks.md` from 126 public design systems (open-design.ai, S102): token layers and
  role ladder, composite type, scheme-switch dark mode, 3px focus ring and target norms, radius/breakpoint/density distributions,
  public-sector service flows (review + contextual Change links, retained answers, lookup outcomes), identity and provenance rules.
  `assets/design-systems/`: `scripts/ds_lookup.py` (outline / one section / `--find` across guides); all 126 full guides copied (Apache-2.0 source) + index (14 curated rows). Routed from SKILL.md; `forms.md` §7 gains the review step; `design-memory.md` marks token provenance; eval 19 added.

### Added (product-UI builds)
- `ux-ui-principles`: "Defaults for product UI builds" in SKILL.md. A dashboard/admin/ERP build with no DESIGN.md writes a draft first,
  and navigation, actions and status use icon + label from one family. Phase 5/7 and `iconography.md` carry the build checklist.
- `ux-ui-principles`: bounded product-UI polish pass (8 checks, one round, before/after renders) in review-loop; required once before phase 7 for dashboard/admin builds.
- `design_md.py --backoffice <look-id>` writes a draft DESIGN.md from `assets/backoffice/styles.json` (tokens, icon rules, data honesty).
- `slop_check.py` flags `nav-without-icons`, notes ▲▼ glyphs used as icons, and no longer flags `method="dialog"` forms as inert.
- `design_md.py --from-code` resolves `var(--x)` fonts and radius; `code_extract.py` maps `--line`/`--hair` to border and never guesses a lighter-than-canvas border.

### Changed (routing and triggering)
- `ux-ui-principles`: SKILL.md rewritten as a router (335 → ~140 lines, 30 KB → 11 KB): a "request → files to open
  first" table, modes, phases in one paragraph, must-not-skip defaults, asking rules, evidence and completion; it states
  that answering from SKILL.md alone is a defect. The full file catalog (descriptions + phases + terms) is now the single
  index at the end of `references/design-workflow.md`; the Do/Don't pairs moved to `do-and-dont.md`, the other-skills
  table to `design-memory.md` §5, host rules and the away-mode direction rule to `design-workflow.md`.
- Description rewritten: imperative "use whenever…", states the skill holds rules general knowledge gets wrong.
- Route table marks must-open files in **bold** (open every bold file of each matching row, not only the first);
  landing row requires design-direction, direction-library and marketing-copy before the first reply (the interview
  needs offer and proof) and visual-assets before building; page-spec is must-open for customer and back-office pages; new rows/wording for phone app screens (mobile-native), starting a design system (foundations,
  benchmarks, accessibility), "confirm it passes" (render verification), review/score (review-loop before caps).
  Description trimmed to 1012 chars (spec max 1024) and gains usability review, states, chart choice and Thai café/clinic
  landing triggers. Routing (Sonnet, 30 turns): 14/19 → 17/19, then #10/#14 2/2 after the last two row fixes; trigger 13/18 → 14/18.
  Then: bold files of *every* matching row are opened before the first reply, interview included (fixes landing +
  back-office requests); "this page" with nothing attached → look in the working directory first; description front-loads
  questions about the user's own component or code (states question 0/3 → 3/3), 1020 chars.
  Final routing v7 (Sonnet, 30 turns): 18/19 (the one miss, #2 shadcn-rules, passed in v4–v6).
  `trigger_eval.py --repeat N --match TEXT` reports per-prompt trigger rates: v6 40/54 (74%), all should-not prompts clean.
  Known misses: short WCAG fact questions (~25%, answered from memory), chart choice (goes to the `dataviz` skill),
  "extract DESIGN.md" (0/3 in the eval, loads when traced by hand).
  `route_eval.py`/`trigger_eval.py`: per-prompt progress, incremental save, timeout-safe, `--max-turns`.
- Merged overlapping references: `visual.md` → `visual-composition.md`, `experience-patterns.md` → `patterns.md`,
  `accessibility-verification.md` → `accessibility.md` (56 → 53 files); links updated.
- Away mode with no artifact: design from the brief with defaults instead of stopping.
- Content the router rewrite had dropped now has a home: evidence discipline (claim labels, browsing, dated register,
  no universal rules, px vs native units, user control) → `sources.md` "Evidence discipline"; scope and completion
  (no full audit for one label, self-contained, record deviations) → `design-workflow.md` phase 8; "make it beautiful"
  reading order → `design-quality.md`; how to use the pairs → `do-and-dont.md`. SKILL.md §6 links to them; the
  reference → phase index lists `design-workflow.md` itself.

### Changed (simplify: fewer files, one way to look, one way to check)
- Eval data showed 40 of 81 docs never opened in 100 routing runs. Merged: design-foundations + visual-composition +
  visual-benchmarks → `references/visual-system.md` (Parts A/B/C, Part C keeps its section numbers); visual-craft →
  `design-quality.md` §7; eight study files (gallery, 21st, 21st dashboard, site measurements, copy, nav, two Open Design
  studies) → `assets/evidence.md`; page-anatomy-by-job → `assets/layouts/index.md` "Page anatomy by job". Layout
  category files are now named in the admin, customer, chart and layout routes. Links and eval names updated.
- `scripts/look.py <kind> [--direction id]`: the single "look before you build" step; lists the reference, showcase and
  direction pictures to open. SKILL.md §3 step 2 and the landing route require it.
- `scripts/check.py <page> [--render]`: one command for script, slop, contrast, state and render checks (PASS / FLAG /
  FAIL / ERROR / N/A / MANUAL / NOT RUN). Run order, phase 7 and SKILL.md §3 step 6 use it.
- Removed the legacy palette-swatch previews: `site_preview.js`, `direction_preview.js --legacy`, build sets `site` and
  `dark`, and `preview-coverage.md` (preview sets now listed in direction-library.md).
- `slop_check.py`: fixed a crash on any page with a form (a form-rules flag shadowed the CSS rule list).

### Changed (one design system, real compositions, a reference library)
- `ux-ui-principles`: direction previews no longer paint one agency template 63 ways. `scripts/compositions.js` holds ten
  first-screen compositions (editorial, collage, full-bleed photo, Swiss, soft product, poster, question, centred, magazine,
  board), each distilled from a rendered reference page; every direction names its `comp` and `subject` in directions.json and
  is drawn on content from a real kind of business (`assets/directions/content-packs.json`, 14 packs) with licensed
  photographs (`assets/photos/`, 14 Wikimedia Commons files with credits). `direction_preview.js --comp/--subject/--brief`
  try other pairings; `--legacy` keeps the old palette comparison.
- One brand, one token set: `scripts/brand.js` derives a direction's product UI (same ground, ink, accent, faces, radius;
  structure and density from the closest back-office look), `backoffice_preview.js --direction <id|all>`, build set `brand`
  (`previews/product/`). `tokens-export.md` states the rule.
- `assets/references/`: 30 rendered pages from the Apache-2.0 Open Design templates (first screen + long view, NOTICE),
  each mapped to a composition, now the first thing to look at before building (SKILL.md §3 step 2, landing route).
- `open-design-visual-study.md`, `direction-library.md`, `visual-assets.md` and the reference → phase index updated.
- Open Design showcase (98 entries): `scripts/showcase_fetch.py` fetches pictures and design notes into a local, git-ignored
  study set; `assets/showcase/README.md` + `catalog.json` are our own catalog of the 65 distinct captures (21 template, 24 study,
  20 skip: shaders, videos, placeholder captures), each with a composition. Four compositions distilled from it: c11 nocturne,
  c12 portrait, c13 nature, c14 cover (14 in total); ten directions moved onto them.

### Changed (visual quality gate)
- `ux-ui-principles`: an A/B run (same task with and without the skill) showed the skill's landing page passing UX checks
  but looking plainer than the no-skill page: the build never opened design-quality, visual-benchmarks, direction-recipes
  or a preview image, and fell into the banned warm-cream + serif + terracotta default. SKILL.md §3 now requires, for
  public pages: look at the chosen direction's preview and run `direction_recipe.py` before building, a plan with one
  decisive move and values from visual-benchmarks, real photos or type-led (no clip-art hero), and before delivery
  `script_check.js` + `slop_check.py` (or a row-by-row walk of design-quality §2 without a shell), then the craft pass
  beside one benchmark page. The landing route makes design-quality, visual-benchmarks and direction-recipes must-open.
- `open-design-visual-study.md` no longer reads as an endorsement of warm paper + terracotta (it is also the most common
  generated look).
- New `scripts/script_check.js`: compiles every inline/local script without a browser and flags top-level names that
  clash with `window` (`const top` silently broke both dashboard runs). Wired into the run order and phase 7.
- `slop_check.py`: `nav-without-icons` applies to app navigation only (sidebar/aside or 7+ links), not a public page's
  short text menu.

### Added (evals)
- A/B tools: `evals/ab_run.py` (same task with the skill and with no skills, in temp dirs outside the plugin folder),
  `evals/ab_shots.js` (screenshots, reduced motion, console errors) and `evals/ab_report.py` (side-by-side HTML report).
- `evals.json` grows from 19 to 100 routing scenarios (64 greenfield, 36 brownfield), each tagged `field` and `category`;
  brownfield scenarios run inside 8 fixture projects in `evals/fixtures/` (React admin, Tailwind + shadcn site, legacy HTML
  admin, landing with an approved DESIGN.md, React Native app, checkout, chart dashboard, Thai form). Routing v8: 93/100
  (greenfield 61/64, brownfield 32/36, $18.67). `evals/export_dashboard_data.py` writes the results as JSON for the eval dashboard.
- `evals/route_eval.py`: runs each eval headless and scores opened files against `expected_reads` / `must_not_read`
  (new fields in `evals.json`; `fixture` for prompts about an existing page). Sonnet: 1/18 → 14/18.
- `evals/trigger_eval.py`: 12 should / 6 should-not prompts without a slash command. 0/12 → 8/12 trigger, 6/6 clean.

### Changed (consistency pass)
- `ux-ui-principles`: one owner per rule, others link to it. Thai headline length (design-foundations "Headline length"),
  motion baseline at any dial (motion §1), focus ring 3px (component-states), color role names with a DESIGN.md / CSS
  mapping table (color-palette), typeface count (two plus optional mono), accent ≤ 2 strong uses, line length 60–75ch.
- Asking: ≤ 3 questions per batch everywhere; the new-look interview (§9 rounds A/B/C) is the named exception (≤ 4 per round).
- Scoring: caps now apply to the visual and UX scorecards (out of 100); four-part weighting removed; report bands and
  P0/P1 mapped to the rubric and severity scale.
- Counts and catalog: 43 layouts, 101 sources, 51 OpenDesign templates; file → phase index lists every reference and script;
  context card gains language/entry context and direction/overrides rows; README covers 0.12.0 and Unreleased topics.
- Scripts: `contrast.py` and `direction_recipe.py` accept `--help`; `slop_check.py` does not count mono families as typefaces;
  `export_tokens.py` display size minimum 2.25rem (36px, matching mobile hero 32–40px); docstrings of `review_report.py`
  and `design_md_check.py` match behavior.

### Added (Tailwind, brownfield)
- `references/tailwind.md`: Tailwind v4 workflow tested with the real CLI (tokens build to utilities, dark via `data-theme`);
  `slop_check.py` notes arbitrary Tailwind colors; each tint has its own readable ink.
- `scripts/code_extract.py` and `design_md.py --from-code`: read an existing codebase's design language and draft its DESIGN.md.

### Added (brownfield onboarding)
- `ux-ui-principles`: ONBOARD mode and `references/brownfield.md` (inspect → page inventory →
  extract DESIGN.md → baseline audit → agree → scoped changes → verify and record).
- `scripts/code_extract.py`: scans an existing codebase (CSS/SCSS/Tailwind/JSX/Vue/Svelte) for stack,
  CSS variables (light and dark), color literals, fonts, sizes, radii, Tailwind usage; maps variables
  to DESIGN.md roles (found / guessed / derived) and reports drift (near-duplicate colors, hard-coded
  literals, conflicting variables across monorepo apps). `--json` for raw data.
- `scripts/design_md.py --from-code SRC`: writes a draft DESIGN.md from the extract (passes
  `design_md_check.py`), with an evidence table per color role and a Drift section.

### Changed (verification run order)
- `ux-ui-principles`: verification now has a mandatory run order
  (`references/render-verification.md` "Run order"): `--fast` baseline on all
  pages → one batch of all fixes → `--fast` confirm on changed pages + journey
  script once → full `--zoom` run once per page before delivery. Re-checking after
  each single fix is a process defect; known heuristic false positives are judged
  once; delivery reports fast/full/journey run counts. Linked from SKILL.md phase 7,
  `design-workflow.md` Phase 7 and `gate-tiers.md` §4.

### Added (OpenDesign templates study)
- `assets/open-design-visual-study.md`: 25 template pages rendered at 1440px and measured (display 72-106px, tracking -0.02 to -0.04em,
  section padding 96px+), what makes the best ones beautiful, the design-system library page; typographic-voice and
  editorial-furniture recipes in `direction-recipes.md`.
- `assets/open-design-templates-study.md`: 51 template skills read from the OpenDesign catalogue repo; patterns kept.
- `references/direction-recipes.md` + `scripts/direction_recipe.py`: per-direction hard rules, bans, required components,
  motion and pre-flight; component recipes (double-bezel, button-in-button, floating pill nav, hairline ink grid, uneven bento).
- `scripts/tweaks_panel.py` (live tweak panel on CSS custom properties) and `scripts/review_report.py` (radar, bands, Keep / Fix / Quick wins).
- New rules: section rhythm and one flourish (visual-composition), waitlist honesty (marketing-copy), pricing tiers and FAQ
  (layout M03), live data states (data-visualization), wireframe deliverables (prototyping), mobile archetypes (mobile-native),
  state the section list first (design-workflow).

### Added (interview, DESIGN.md)
- `ux-ui-principles`: three-round interview before any new look (business, taste with pictures, confirm) with a shape
  question that is not inferred from feel words; assumed answers are marked, never presented as the client's.
- DESIGN.md now follows the Google Labs design.md spec (alpha): YAML front matter tokens (`colors` incl. `dark-*`, `typography`,
  `rounded`, `spacing`, `components` with `{refs}`) plus the eight canonical sections, then our dials, interaction rules and
  decision log. `design_md_check.py` validates it (references, formats, order, duplicates, component contrast) and flags the
  older prose-only format as legacy.
- `scripts/design_md.py`: interview + direction to DESIGN.md (AA-checked light and dark roles, reasons, decision log)
  and a marked pointer block in `AGENTS.md` / `CLAUDE.md` so the next agent reads DESIGN.md first.

## [0.12.0] - 2026-11-05

### Changed (consistency audit)
- `ux-ui-principles`: four-agent audit of 53 references found 92 conflicts; fixed. One owner per rule
  (gate-tiers for rule classes, motion.md for durations and dials, design-foundations for type and breakpoints,
  review-loop for the score rubric, design-workflow for the fix-round budget); duplicated rules now point to the
  owner; hard-coded counts replaced by pointers; shared terms defined in SKILL.md; script flags and thresholds
  aligned (`export_tokens.py` motion tokens, Thai line-height 1.55, per-language fonts in `slop_check.py`).

### Added (tokens, soft directions, dashboard study)
- Back-office `advanced` screen (editable grid, drag reorder, color picker, rich text, mention/tag, notification centre,
  onboarding tour, autosave form, password recovery, interaction-state matrix), tablet mode (`--width 820`),
  `--rtl` mirroring, and `site_preview.js --dark` for customer pages; rules in `references/advanced-components.md`
  and `references/tablet-rtl-dark.md`.
- `ux-ui-principles`: **tokens to code** (`scripts/export_tokens.py`, `references/tokens-export.md`):
  any direction becomes `tokens.css`, a Tailwind v4 theme and shadcn variables; dark theme derived,
  every pair checked for AA, fill and text accents split, status colors derived. All 58 directions pass.
- 8 soft premium/playful directions (Petal, Linen, Opal, Honey, Mochi, Fjord, Velvet, Sorbet); the library now
  has 58, with a rule that every set of three recommendations includes a non-square one.
- Back-office `status` preview (uptime strips, resource cards, ring meters, ranked bars) and
  `assets/21st-dashboard-study.md`.
- Reveal-on-scroll rule in `motion.md`; `slop_check.py` flags `reveal-hides-content` and notes `all-square`;
  `render_check.js` scrolls before full-page shots and ignores off-screen skip links.

### Added (from the agency landing build: Thai + English, themes, other skills)
- `ux-ui-principles`: **direction library** (`references/direction-library.md`):
  58 named directions (50 at first release, 8 soft ones added later) with idea, material, fit, avoid-for, risk and
  optional preview slugs; procedure to show pictures (never names only), offer
  the next set on "more", and choose for company marketing.
- SKILL.md "Working with other design skills": which skill for which job
  (Hallmark, Taste Skill, Impeccable, Interface Design, shadcn) and a conflict
  order so one skill's house rules (no shadows or hairlines) do not fail a
  chosen direction that needs them; never edit a checker to pass it.
- Thai with Latin display faces (design-foundations): pairing table, per-language
  font switching, no tracking or uppercase for Thai, inline-block chunks so Thai
  headings do not break mid-word.
- Open-collection photographs (visual-assets rung 1b): licences, footer credit,
  honesty, one treatment, loading rules.
- Two-language static pages (i18n-performance): `<span lang>` pairs, toggle
  behaviour, font and line-count checks.
- Design workflow phase 5 "Keep the before": copy files and take before-shots so
  a redesign is reversible; IMPROVE mode row updated.
- `scripts/direction_preview.js` and `assets/directions/` (directions.json +
  50 rendered previews and group sheets): our own pictures of directions, drawn
  from data on one neutral sample (inspired by the Hallmark theme set; tokens and
  faces are our approximations, not copies of its files); `--thai`, `--brief`, `--sheet`, `--ids`, `--group`.
  `scripts/_pw.js` shares Playwright discovery with `render_check.js`.
- `scripts/backoffice_preview.js` and `assets/backoffice/` (styles.json + 26
  sheets and 32 single previews): ten back-office screens (A01–A07, D01, D03, D04)
  in sixteen looks that differ in nav (side/rail/top), table style, status tag,
  edges, density and colour, on one payments sample, with `--thai`, `--sheet`,
  `--singles`; back-office.md "Choosing density and tone from pictures".
  Now 21 screens: adds inbox (P01), workflow board (P02), create/edit form,
  analytics (D02), comparison (D05), heatmap (D06), sign-in, 403, 404, plus a
  full-page `components` sheet (every component with states) and a `states`
  sheet (loading, empty, error, no permission, bulk partial failure, offline).
  `--mobile` adds a 390 x 844 phone set (cards, FAB, bottom nav with badge,
  sticky decision bar, swipe action, drawer, filter bottom sheet, states and a
  mobile component sheet) in all sixteen looks.
  Dashboard polish from the 21st.dev study: soft layered card shadows and a
  faint ground glow, an emphasised gradient KPI card, KPI icon chip + delta pill
  + gradient sparkline, rounded gradient bars and gradient area lines, a donut
  with legend, segmented range control, avatar stack, workspace switcher,
  section label, month-end progress card and count tabs above the table.
  Previews fill the viewport with realistic data, one inline icon set, charts
  with axes/gridlines/average/peak label, sparklines with deltas, selection,
  row actions, pager, breadcrumbs and a user block.
- Shape language in previews: directions gain `btn`, `corner`, new curved arts
  (blob, arch, wave, tilt, dots, diag, rings, pill) and new heroes (giant, full,
  stagger, arch); back-office looks gain per-element radii (cards, buttons,
  fields, nav items, avatars, checkboxes). Previews regenerated.
- `scripts/site_preview.js` and `assets/site/previews/`: 34 customer pages
  (M01 to M05, C01 to C05, E01 to E05, P03 to P05, U02 to U05, B01 to B05 plus
  about, blog, case study, policy, order confirmation), a landing-sections sheet
  and a customer component sheet, in six looks (`--all` for 50), with `--thai`.
  `references/preview-coverage.md` maps all 43 layout blueprints to pictures and
  lists what is still not covered.
- `assets/21st-study.md`: observations from browsing 21st.dev (12K components,
  353 templates, 962 themes): what separates strong pieces (imagery, type over
  the picture, hero compositions, backgrounds with depth, proof details,
  emphasised pricing tier, galleries with depth, dashboards) and what it means
  for our previews. `site_preview.js` gains `--pages hero` and six hero
  compositions (fan, ring, accordion, overlay, product mock, centered) with mesh
  and grain backgrounds, announcement pill, avatar group with rating and a
  placeholder logo cloud; `home` uses them.
- Preview images are generated, not committed: `skills/*/assets/*/previews/` is
  git-ignored (about 30 MB) and `scripts/build_previews.js` rebuilds all sets
  (`--only directions|site|backoffice|mobile`). The skill stays small (about
  2 MB of text, data and scripts); agents generate only the pictures they need.
- Evals 16 and 17: bilingual agency landing and a mid-build theme switch.

### Changed (scripts)
- `render_check.js`: reports images that failed to load (lazy images forced
  eager so full-page shots are not blank), text touching the viewport edge, and a
  note when an h1/h2 wraps to 3+ lines; new `--toggle "<selector>"` repeats the
  whole viewport matrix after clicking a language or theme switch.
- `contrast.py --css`: reads `.css` files and follows local `@import` / `<link>`
  stylesheets; resolves `oklch()`, `rgb()`, `hsl()` and `var()`; understands
  `--color-ink` / `--color-paper` names (previously found 0 pairs on such pages).
- `slop_check.py`: language-variant spans (`<span lang>`) no longer count as
  styled accent words.

### Added (study of Hallmark, Taste Skill, Impeccable, Interface Design, shadcn)
- `ux-ui-principles`: references `gate-tiers`, `page-anatomy-by-job`, `scoring-caps`,
  `app-screen-rules`, `shadcn-rules`; new sections in `design-direction` (domain
  exploration, token names, swap/token/signature tests), `visual-craft` (bans vs
  refusals, finish details), `motion` (mechanics), `visual-assets`, `design-workflow`
  (questioning cadence). Eval 16.

### Added (build recipes)
- `ux-ui-principles`: `references/build-recipes.md` — surface modes (persuade /
  operate / read / experience) with shared tokens, no-JS live demo, explicit
  hero grid placement, honest placeholders, `mailto:` contact, headless
  verification, back-office mock before backend code, theme-offer etiquette.
  Wired into SKILL.md catalog and design-workflow phases 4, 5, 7. Eval 15.

### Fixed (from user testing: no interview, no motion, weak color, odd mobile)
- `ux-ui-principles`: SKILL.md "Defaults that must not be skipped" for public
  pages and new looks — interview before code, palette, motion baseline,
  mobile composition, render 1440 + 390. A background session no longer
  counts as "user away".
- Color: OKLCH recipe for attractive palettes and 8 contrast-checked starter
  palettes (light + dark) keyed to style keywords.
- Motion: baseline per page type; "no motion" needs a reason.
- Mobile: concrete mobile web composition rules (≤ 480px).
- `render_check.js` phone checks (targets < 44px, fields < 16px, text < 14px,
  > 1 fixed/sticky); `slop_check.py` notes > 2 saturated hues, pure black and
  pages with no motion. Form snippet sized for phones. Eval 14.

### Added (motion & direction)
- `ux-ui-principles`: motion reference — level per motion dial, ten motion
  types with durations, website choreography, reduced motion, performance,
  tooling (CSS/View Transitions first), motion spec template and checks;
  wired into phases 3, 4, 5 and 7.
- `ux-ui-principles`: design direction — Liquid glass added (18 styles),
  Thai/English style keywords → style base + dials, steering vocabulary, and a
  ≤3-question direction interview (feel, references, energy) for new looks.
- `render_check.js`: flags text left at opacity 0 on the first screen;
  `--reduced-motion` also flags animations still moving and content never
  revealed. Evals 12–13.

### Changed
- `ux-ui-principles`: `render_check.js` loads the page once and switches
  widths/color schemes in place (~2.5× faster on a long page: 11.4 s → 4.6 s);
  overflow culprit scan runs only when the page overflows; new `--fast`,
  `--viewport-shots`, `--timeout`; load errors reported once.
  `slop_check.py` icon-card rule ignores table rows and reports one finding.
- `ux-ui-principles`: `render_check.js` finds Playwright and any installed
  Chromium/headless shell or system Chrome itself (no version-matched download),
  wraps HTML fragments automatically, adds `--doctor`, and exits 3 with
  "NOT TESTED" at once when nothing is available; docs forbid installing or
  sleep-polling browsers mid-task.
- `ux-ui-principles`: forms — placeholders now have positive rules (example
  values for non-obvious formats, Thai examples, ≥ 4.5:1, never the only label)
  instead of only a prohibition; new §6b implementation contract with a tested
  vanilla pattern (rules in markup, own messages on blur/submit, error summary
  with focus, pending submit, server errors mapped, input kept). Forms are now
  mandatory in phases 4, 5 and 7 (empty submit, invalid value, request
  failure); new hard gate for forms without validation; `slop_check.py` flags
  forms without validation or messages and format fields without an example;
  eval 11.
- `ux-ui-principles`: form layout and error-state rules from a real defect —
  multi-column only for related pairs with top alignment and downward-growing
  errors, one control height, required/optional marking, border + icon +
  message driven by `[aria-invalid]`, Thai-keyboard-in-Latin-field message.
  `render_check.js` now flags unequal control heights, misaligned rows,
  invalid fields styled like valid ones, and spaces/over-wide glyphs before
  punctuation.

### Added
- `ux-ui-principles`: phased design workflow as the skill's spine — phases
  0–8 (inspect, understand, architect, explore, design, implement, critique,
  verify, deliver) with the references to use, ask points and exit criteria
  per phase (`references/design-workflow.md`); route-by-mode table (adds
  ANSWER and BUILD modes); when-to-ask rules incl. away/defaults mode;
  framework process mapped to phases; evals 9–10.
- `ux-ui-principles`: ideas from Hallmark, Impeccable, Hue, Taste Skill and
  Interface Design (as described in a user-supplied guide; sources S96–S101,
  not independently verified) — structural slop, one strong idea, variety
  across products vs consistency within one, respect existing design
  (design-quality §2b); brand extraction procedure (design-memory §3b);
  2–3 named directions before build (design-direction §7); `scripts/slop_check.py`
  (deterministic template-look heuristics) and `scripts/design_md_check.py`
  (DESIGN.md validator); evals 7–8.
- `ux-ui-principles`: design direction reference — eight design dimensions,
  page pattern chosen by the user's primary question (16 patterns), layout
  compositions, visual style catalog with one-base/one-accent mixing rule, and
  variance/motion/density dials with presets per product context.
- `ux-ui-principles`: design memory reference — Phase 0 project inspection,
  source-of-truth precedence and docs-vs-code conflict handling, DESIGN.md
  template with rationale, anti-patterns and decision log, specialist-skill
  routing (only when actually available), reuse before invent.
- `ux-ui-principles`: review loop reference — 14 refinement verbs with Thai
  complaint mapping, critique format, visual and UX scorecards (internal
  rubric), hard gates that block delivery, state coverage list. New REFINE
  mode, design context card, and `evals/evals.json` (6 benchmark prompts).
- `ux-ui-principles`: visual benchmarks reference — measured type (weight,
  tracking and line-height by size, scale ratio by intent, named text styles),
  tone, spacing tiers, radius camps, elevation, motion, content realism, Thai
  metrics, presets and a craft pass; evidence files for 35 measured live sites
  and a gallery study (18 curated.design sites, 18 Dribbble shots, 14 Behance
  projects, 19 21st.dev templates). Adapts selected rules from
  elayadesign/ai-design-skills (MIT).
- `ux-ui-principles`: navigation grouping reference — grouping methods, counts,
  order, labels, settings scope ladder, permissions, mega menus, mobile tabs,
  anti-patterns and Thai/English before-after menus, from 21 products' public
  navigation (nav study); sources S94 (Material 3 navigation bar) and S95
  (Apple HIG tab bars).
- `ux-ui-principles`: marketing copy reference — headline types, subheadline
  jobs, CTA and risk-reducer wording, proof placement, section copy, formulas,
  Thai marketing register and filler → specific rewrites, from 30 public pages
  (copy study).
- `ux-ui-principles`: "Displaying values" in data visualization — empty vs zero
  vs unknown, number precision and abbreviation, deltas and percentage points,
  relative vs absolute time, truncation of IDs, detail pages, KPI tiles.

- `ux-ui-principles`: self-contained design coverage — design foundations
  (tokens, type, spacing, sizing, radius, elevation, motion, breakpoints,
  density, focus, theming), component selection and usage for ~60 components,
  component states with keyboard contracts, and prototyping deliverables.
- `ux-ui-principles`: sources S88–S93 (WCAG 1.4.13, 2.1.1, 2.4.3, 4.1.2, 2.2.2;
  ARIA APG patterns verified from w3c/aria-practices).

- `ux-ui-principles`: heatmap/matrix rules (data visualization), signal budget
  and a visual-feedback diagnosis table (visual craft), data-ramp guidance
  (color palette), layout D06 Matrix / heatmap (43 blueprints) and the SkillMap
  worked example.
- `ux-ui-principles`: design-quality reference — plan-then-review with subject
  inventory, idea sentence and competitor test, template devices to avoid,
  substance over restraint, frame and rhythm, screenshot critique loop.
- `ux-ui-principles`: customer-facing UI reference (page taxonomy, onboarding,
  trust, metrics) and UX for AI features (human control by consequence, output
  states, feedback).
- `ux-ui-principles`: `contrast.py --css` reads `:root` token blocks (light,
  dark, palette variants) from a page and checks role and naming-pattern pairs.

### Changed
- `ux-ui-principles`: reference index in SKILL.md regrouped by framework level
  with one entry per file and a visual-file routing table; description trimmed
  to the 1024-character limit; display line-height note in design foundations;
  removed README link to the undistributed `evals/` folder.
- `ux-ui-principles`: no longer depends on `design-system-builder` or
  `figma-cli`; all routing points to the skill's own references.

## [0.11.0] - 2026-11-04

### Added
- `ux-ui-principles`: form design, iconography, native mobile (iOS/Android),
  cross-channel notifications, data visualization and color-palette references.
- `ux-ui-principles`: render verification procedure with `scripts/render_check.js`
  (viewports, themes, overflow, unnamed controls, unlabeled fields, screenshots)
  and `scripts/contrast.py` (WCAG contrast pairs).
- `ux-ui-principles`: layouts A06 Audit log and A07 Settings with save behavior
  (42 blueprints); back-office worked examples for a payments operations product.
- `ux-ui-principles`: trigger eval set and recorded results (`evals/`).
- `ux-ui-principles`: sources S63–S87 (WCAG form/icon/color criteria, GOV.UK form
  components and patterns, Apple HIG, Android developer guidance, FT Visual
  Vocabulary, W3C WAI complex images; NN/g, Baymard, Notify marked partial).
- `ux-ui-principles`: end-to-end product design framework — six disciplines,
  six levels (strategy & research → experience architecture → page & interaction
  → visual & design system → quality & engineering → validation & improvement),
  an iterative Discover → Improve process and Light / Standard / Critical rigor
  tiers. New DISCOVER and ARCHITECT modes.
- `ux-ui-principles`: new references — product discovery, experience
  architecture (IA, navigation, URLs, permission flows), back-office page
  taxonomy and pattern fit, content design / UX writing, trust-security-privacy
  UX, localization and performance, visual craft, and measurement / design QA.
- `ux-ui-principles`: 16-row page design specification template scaled by tier,
  with a worked Critical example, and a shared design-context template read by
  both `ux-ui-principles` and `design-system-builder`.
- `ux-ui-principles`: source register extended with verified standards and
  design-system sources (ISO 9241-210, WCAG 2.2 timing/error-prevention/language,
  OWASP cheat sheets, GOV.UK patterns, Ant Design, Carbon, Material 3, HEART).
- `ux-ui-principles`: compact task-focused reference guides for experience
  patterns, visual composition, and accessibility verification. Preserve the
  existing research and layout workflow; add explicit host/lifecycle authority
  boundaries for portable use and Change Loop integration.

## [0.10.0] - 2026-10-09

### Added
- `ux-ui-principles`: paired workflow Do / Don’t and ten flow/screen examples
  linked to layout IDs, plus a Thai worked pair with rationale and observable checks.
- `design-system-builder`: component Do / Don’t examples, dated official-source
  research audit, and token interoperability guidance.

### Changed
- `design-system-builder`: add paired workflow Do / Don't guidance and component
  usage examples with failure reasons, context/exception notes and observable checks.
- `design-system-builder`: correct WCAG focus/target guidance, ARIA state behavior,
  Next server/client composition, npm packing lifecycle and manager-specific exports.
  Scope components and typography defaults to product needs; document Storybook
  accessibility CI setup, token interchange, governance and research evidence limits.

## [0.9.2] - 2026-10-09

### Added
- `ux-ui-principles`: dated OpenDesign reference research with 16 site candidates
  and 8 template references mapped to the original layout IDs; machine-readable
  selection metadata, attribution, evidence depth and adaptation checks.
  Identifies error/verification captures and overlay-only evidence; no external
  implementations, fonts, images or complete specifications are bundled.

### Changed
- Layout workflow can consult external references with explicit source/surface
  scope and distinguishes catalog-only candidates from reviewed detail text.

## [0.9.1] - 2026-10-08

### Added
- `ux-ui-principles`: 40 original layout blueprints in eight task categories,
  a selection index, shared responsive/state/accessibility specification, and
  three Thai worked examples (checkout, record management, booking). Examples
  are adaptable proposals with tradeoffs and acceptance checks, not validated UIs.

### Changed
- Skill workflow selects layout IDs and loads only relevant category references.

## [0.9.0] - 2026-10-08

### Added
- `ux-ui-principles`: evidence-based UX/UI research, design, audit and improvement
  workflow with six reference guides, output templates and three evaluation cases.
  Research register contains 36 authoritative sources verified online on 2026-10-08.
  Covers interaction heuristics, cognitive-model limitations, visual hierarchy,
  forms/recovery, dashboards, Thai text, WCAG 2.2 levels/exceptions, and validation.
  Separates observed evidence, standard requirements and project recommendations;
  does not infer runtime accessibility or conversion impact from screenshots.

## [0.8.0] - 2026-08-20

### Added
- `design-system-builder`: **`references/storybook.md`** — optional Storybook/Histoire
  docs-site deliverable: tool choice per stack, scaffold + addons, the `preview.ts`
  theme/density toolbar wired to the `data-theme` contract, story authoring rules
  (matrix / playground / interaction stories, generated token reference page), CI
  test-runner + visual regression, and publishing the static site alongside the npm
  package. Explicitly optional: offered when shipping a published package, never a
  blocker for the core deliverable, and never a substitute for the render-verify step.

### Changed
- `design-system-builder`: Storybook content moved out of `operations.md` (now a pointer);
  SKILL.md lists the docs site as an optional deliverable and triggers on Storybook asks.

## [0.7.0] - 2026-08-20

### Added
- `design-system-builder`: **`references/publishing.md`** — full workflow for making the
  design system an `npm i`-able package consumed outside its own repo: sharing-channel
  decision table (npm public/private, GitHub Packages, self-hosted registry, git/tarball
  stopgap), dist build pipeline per framework (tsup / Vite lib mode, `'use client'`
  preservation check), the complete published package.json (files/exports/types-first/
  sideEffects/peerDependencies/prepublishOnly), the four mandatory pre-publish checks
  (`npm pack --dry-run`, publint, arethetypeswrong, tarball smoke-install), publish
  mechanics (provenance, dist-tags, deprecate-never-unpublish), Changesets release
  automation, registry-specific consumer `.npmrc` setup, and the consumer README contract.
- `design-system-builder`: eval #6 covering the workspace-package → published-package
  upgrade path (evals are dev-only, not distributed).

### Changed
- `design-system-builder`: SKILL.md description and reference list now cover publishing/
  sharing as an npm package (triggers like "ทำเป็น npm package", "publish ขึ้น npm");
  `packaging.md`'s published-shape row points at `publishing.md`.

## [0.6.0] - 2026-08-19

### Added
- **`figma-cli`** — a project-neutral workflow for compiling figma-ds-cli JSX into live,
  editable Figma Desktop nodes. Covers project discovery, safe and patched bridge modes,
  the seven core DSL node types, source-file rendering, token collection binding, visual
  verification, non-destructive canvas arrangement, token import, and HTML conversion when
  requested. The guidance is aligned with the installed CLI's source documentation and calls
  out silent failure modes such as clipped text, incorrect CSS-style props, numeric `var:`
  bindings, wrapper auto-splitting, and ambiguous variable collections.

## [0.5.3] - 2026-08-06

### Changed
- `gitops-nova`: the example services now use a domain-neutral cast — `api`, `worker`, `auth`,
  `orders`, `billing`, `catalog`, `ingest`, `storefront`, `admin-api`, `analytics`. They
  previously carried the business vocabulary of the platform the skill was distilled from
  (`agent`, `member`, `office`, `bank`, `deposit`, `payin`), which quietly narrowed who the
  examples read as being for and made them awkward to lift into a project of a different shape.
  `agent` was doubly bad: in a skill read by an LLM it collides with the other meaning of the
  word. The skill name is unchanged.

## [0.5.2] - 2026-08-06

### Changed
- `gitops-nova`: replaced seven identifiers carried over from the private repo the skill was
  distilled from with generic equivalents — a secret-manager path, a database name (x2), three
  internal ADR/debt id formats, a real CI commit sha, a provider-specific env var name, a mock
  image name, a chart name in a docstring, and `scaffold.py`'s `--gateway` default (now `edge`,
  which is also a better name than a platform codename). No credentials, hostnames, account ids,
  ARNs, or endpoints were ever present — these were identifiers, not secrets — but this
  repository is public and none of them earned their place in a reusable skill.

## [0.5.1] - 2026-08-06

### Added
- `gitops-nova` `audit.py`: **RT007** — `jwtExemptPaths` declared while `route.jwt.enabled` is
  unset. The list is inert (nothing is exempted because nothing is enforced) and, worse, the
  values then *read* as a protected route with a carve-out, which is how a reviewer concludes
  auth is handled. Found by running the skill against a real repo: one service carried this in
  all four environments.

### Fixed
- `gitops-nova` `audit.py`: RT002/RT003 no longer assert "no edge authentication" when the
  consuming chart ships its own auth-policy template — a chart-level `SecurityPolicy` is
  invisible in the release's values. The finding now names the chart and asks for the binding to
  be checked. Values files are mapped to their chart from the Applications and ApplicationSets
  themselves, not guessed from the path, so the shared-chart layout resolves correctly.

## [0.5.0] - 2026-08-06

### Added
- **`gitops-nova`** — SOP for designing, bootstrapping, extending, and auditing an Argo CD
  GitOps repository. Distilled from a production app-of-apps repo (9 services, one shared
  chart, LGTM stack, Gateway API edge), so the rules carry the reason and the measurement
  rather than the convention.

  Four modes — BOOTSTRAP / ONBOARD / REVIEW / PROMOTE — organised around one question: what
  can a single bad merge destroy? Ten reference files cover layout and ApplicationSet
  generators, the two-step Argo CD bootstrap, the shared service chart and its Helm traps,
  the three-tier sync ladder, secrets by reference, digest promotion, exposure and edge auth,
  observability, the review checklist, and the values-file-as-decision-log convention.

  Two scripts, both verified against a real repo:
  - `scripts/audit.py` — static audit. Credentials committed as values, unpinned charts and
    images, `prune` on cluster-scoped paths, catchall public routes, JWT-exempt paths that
    bypass their own allowlist (with Gateway API *segment* prefix semantics, not string
    prefix), probes on portless components, generator entries whose values file is missing,
    wildcard project sources, apps sourcing repos their project forbids, duplicate hostnames,
    and east-west calls routed through the repo's own public hostnames. `--fail-on` makes it
    a merge gate; it reads commented-out generator entries so a parked environment is not
    reported as a broken one.
  - `scripts/scaffold.py` — repo skeleton with the traps pre-handled: the `kindIs "bool"`
    guard (Helm's `default` swallows `false`), per-component resource fallback, port-driven
    Service/probes/scrape, and templates that `fail` rather than render an unauthenticated
    path. `helm lint` and `helm template` clean.

## [0.4.0] - 2026-08-06

### Changed
- **Renamed `test-sop` → `test-design`** (breaking for anyone who installed 0.3.0 — invoke
  `/test-design`). "SOP" said nothing about what the skill decides, and nobody types it when
  asking for help; "test design" is the standard term for choosing what to verify (ISTQB /
  ISO 29119 use it for exactly this activity).
- Its description now states explicitly that the skill covers deciding and documenting *what*
  to verify, not writing or debugging automated test code (jest / vitest / playwright specs,
  mocks, flaky CI). The new name invites that misreading, so the boundary is spelled out.
  This wording is unmeasured — the trigger eval was run against the old name.

## [0.3.0] - 2026-08-06

### Added
- **test-sop** skill — SOP for designing and running software tests at the right depth,
  reusable across projects.
  - 4 levels: L1 smoke (bugfix) → L2 module (feature) → L3 system (release) → L4 critical
    (auth / payment / permission / migration), with an auto-escalation rule when work
    touches money, permissions, personal data, or authentication.
  - 12 work-type presets (feature, bugfix, API-only, UI-only, 3rd-party integration,
    auth/payment, data migration, refactor, performance, report/export, realtime, mobile),
    each listing the path types it must cover and the edge cases teams forget most.
  - 5 path types (Happy / Alternate / Error / Edge / Security) with tie-break rules,
    grounded in ISTQB test levels/types, ISO/IEC 25010 quality characteristics, and
    ISO/IEC/IEEE 29119-3 test documentation.
  - Reference library: templates (module / scenario / checklist / bug / API-only / smoke),
    planning docs (test plan, risk matrix, traceability matrix, summary report),
    a domain checklist library (CRUD, list/search, upload, money, notification, export,
    realtime, RBAC, cron, NFR), a coverage-audit method, and ClickUp/Jira task-tree mapping.
  - `scripts/scaffold.py` generates the whole doc set for a chosen level with 6 domain
    presets (auth, payment, crud, api, integration, migration), English by default and
    `--lang th` for Thai-speaking teams.
  - Worked L4 example: 12-module / 64-scenario authentication set.
  - Skill instructions are in English; the description carries both English and Thai trigger
    phrases, and deliverables are written in the team's own language.
  - `scripts/checklist.py` generates the per-scenario checklists from the acceptance criteria
    and verifies they stay 1:1 (`--check`, non-zero exit on drift).
  - Benchmarked against a no-skill baseline on 4 realistic tasks (33 mechanical assertions,
    single run each, Sonnet subagents): **97% with the skill vs 48% without**. An earlier
    iteration of the skill scored 91% on the same ruler. The clearest effect is depth
    calibration — the same skill produced 2 files / 438 words for a bugfix and 10 files /
    10k words for a payment system, where the baseline wrote at roughly one length regardless
    of risk. Numbers are one run per task on one model; treat them as directional.
  - Eval findings folded back into the skill: no-placeholder rule promoted to a top-level rule
    (`grep -rn TODO`, and any placeholder that must stay has to be disclosed in the reply),
    risk-ordered wave delivery required above ~20 scenarios, coverage audits must name the NFR
    section an item moves into, and checklists are generated rather than hand-copied — hand
    copying drifted from the criteria in 64–100% of scenarios, losing conditions in both
    directions, which the generated + verified flow eliminated entirely.
  - Trigger measurement: 20-query eval (3 runs each, 3 optimizer iterations) found perfect
    precision but 8–17% recall on deliberately advisory phrasings, and two machine-written
    descriptions scored worse than the original, so the description is unchanged. Advisory
    questions get answered directly instead of dispatched to a skill, so **invoke it explicitly
    (`/test-sop`)** rather than relying on auto-trigger.

### Changed
- `.codex/` config with local Anthropic base URL.

## [0.2.0] - 2026-07-28

### Added
- **kimi-k3** skill and the `kimi-k3` / `kimi-k3-implement` agents — delegate a prompt or a
  scoped coding task to Moonshot's Kimi K3 and relay the result. Needs `MOONSHOT_API_KEY`.

## [0.1.0] - 2026-07-17

Initial release of the hashtagf skill warehouse, installable as a Claude Code
plugin or via the `skills` CLI.

### Added
- **design-system-builder** skill — build, extract, or repair a complete design
  system (tokens + component library with full interaction states + docs).
  - 4 modes: CREATE, EXTRACT, REDESIGN, and extend.
  - Output as CSS/Tailwind or an installable package for React, Next.js, or Vue
    (auto-detected from the repo).
  - Packaging, guardrails, and eval suites with fixtures.
  - Foundations: keyframe animation tokens (spin / shimmer / enter-exit / slide),
    toast queue + stagger rules, and image loading rules.
  - States: placeholder and validation-timing rules.
- Claude Code plugin manifest and `skills` CLI packaging.

### Changed
- Eval suites excluded from distribution (dev-only).

[Unreleased]: https://github.com/hashtagf/skills/compare/v0.15.0...HEAD
[0.15.0]: https://github.com/hashtagf/skills/compare/v0.14.1...v0.15.0
[0.14.1]: https://github.com/hashtagf/skills/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/hashtagf/skills/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/hashtagf/skills/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/hashtagf/skills/compare/v0.10.0...v0.12.0
[0.10.0]: https://github.com/hashtagf/skills/compare/026626b...v0.10.0
[0.9.2]: https://github.com/hashtagf/skills/compare/v0.9.1...v0.9.2
[0.9.1]: https://github.com/hashtagf/skills/compare/v0.9.0...v0.9.1
[0.9.0]: https://github.com/hashtagf/skills/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/hashtagf/skills/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/hashtagf/skills/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/hashtagf/skills/compare/v0.5.3...v0.6.0
[0.5.3]: https://github.com/hashtagf/skills/compare/v0.5.2...v0.5.3
[0.5.2]: https://github.com/hashtagf/skills/compare/v0.5.1...v0.5.2
[0.5.1]: https://github.com/hashtagf/skills/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/hashtagf/skills/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/hashtagf/skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/hashtagf/skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/hashtagf/skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/hashtagf/skills/releases/tag/v0.1.0
