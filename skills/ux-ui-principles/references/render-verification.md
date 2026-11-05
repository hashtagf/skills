# Render verification — check the built page, not the intent

Most defects in generated UI appear only when the page is rendered: horizontal
overflow on phones, class-name collisions, stretched grid rows, overlapping
chart labels, wrong fonts for Thai, hidden elements that still show, failing
contrast in dark mode. Reading the code does not find them reliably. Run this
procedure whenever you build or change UI and tools allow it. Record results as
passed, failed or not tested.

## Tools in this skill

| Script | Checks | Run from the skill root |
|---|---|---|
| `scripts/render_check.js` | Renders at 1440/768/390 px (+320 px with `--zoom`) in light and dark; reports JS/console errors, failed requests, horizontal page overflow with the offending elements, images without alt, unnamed buttons/links, unlabeled fields, form controls with different heights, fields in one row not top-aligned, invalid fields styled like valid ones, spaces or over-wide glyphs before punctuation, text left at opacity 0 on the first screen, **images that failed to load** (lazy images are forced eager first), **text touching the viewport edge** (no gutter), phone tap targets, and a NOTE when an h1/h2 wraps to 3+ lines; `--reduced-motion` adds animations still moving and content never revealed; `--toggle "<selector>"` clicks a language or theme switch after the first pass and repeats every viewport (screenshots prefixed `alt-`); saves full-page screenshots | `node scripts/render_check.js <url-or-file> --out <dir> [--zoom]`; while iterating `--fast` (1440 + 390, light, viewport shots) |
| `scripts/direction_preview.js` | Renders one-screen previews of the directions in `assets/directions/directions.json` (and `--sheet`, `--thai`, `--brief`) so a look can be chosen from pictures; not a verification of a built page | `node scripts/direction_preview.js [--ids a,b] [--group company] [--sheet]` |
| `scripts/site_preview.js` | Renders the customer-facing pages listed in [preview coverage](preview-coverage.md), every landing section and a customer component sheet in six directions (`--all` for every direction in `assets/directions/directions.json`), with `--pages`, `--ids`, `--sheet`, `--thai`; not a verification of a built page | `node scripts/site_preview.js [--ids dose,editorial] [--pages home,checkout] [--sheet]` |
| `scripts/backoffice_preview.js` | Renders previews of the back-office screens (pages plus component, advanced and page-states sheets) in every back-office look from `assets/backoffice/styles.json`, with `--mobile` (390 x 844 phone set), `--thai`, `--sheet`, `--style-sheets` and `--singles`, so density and tone can be chosen from pictures; not a verification of a built screen | `node scripts/backoffice_preview.js [--styles a,b] [--screens records,approval] [--sheet]` |
| `scripts/slop_check.py` | Template-look and slop heuristics in HTML + local CSS: eyebrow labels, accent-word headlines, gradient text, identical icon-card rows, >2 typefaces, >4 raw radii, raw hex count, filler copy, generic CTAs, inert forms, forms without validation or own error messages, format fields without example/hint, removed focus, motion without reduced-motion; flag vs note | `python3 scripts/slop_check.py page.html [--json]` |
| `scripts/design_md_check.py` | DESIGN.md structure: required sections, reasons, color roles + dark values, anti-patterns, dials 1–10, status line, Thai line-height, placeholders | `python3 scripts/design_md_check.py DESIGN.md` |
| `scripts/export_tokens.py` | Direction → `tokens.css`, Tailwind v4 theme, shadcn variables; derives dark, checks AA, prints notes where it bent a color (see [tokens to code](tokens-export.md)) |
| `scripts/contrast.py` | WCAG contrast ratio for color pairs with per-pair minimums; `--css` reads token blocks (light, dark, palettes) from a page and checks role pairs automatically | `python3 scripts/contrast.py --css page.html` (or a `.css` file) or `python3 scripts/contrast.py pairs.json`; follows local `@import` and `<link>` stylesheets and resolves `#hex`, `rgb()`, `hsl()`, `oklch()` and `var()`; understands `--color-ink`/`--color-paper` style names and `--X`/`--X-ink`/`--on-X` pairs |

**Setup budget — never stall on tooling.** Run `node scripts/render_check.js --doctor`
once. It finds a Playwright module (project, NODE_PATH, global, `PW_MODULE`)
and any installed Chromium/headless shell or system Chrome, whatever the
version. Exit 3 means none is available: record the render check as
**not tested**, run the static checks (`slop_check.py`, `contrast.py --css`)
and continue. Do not download browsers, install packages, or sleep/poll for
a download mid-task; give the user the one-time setup command instead. Use
`--timeout` rather than a shell `timeout` (absent on macOS). Fragments
(no doctype/html) are wrapped automatically.

`render_check.js` needs Playwright. It loads the page once and switches widths
and color schemes in place; full-page screenshots are the slow part on long
pages — use `--viewport-shots` or `--fast` while iterating and the full run
(with `--zoom`) once before delivery. Load errors and failed requests are
reported once, at the first viewport. It is a smoke check: it does not prove
keyboard operability, screen-reader behavior, task success or WCAG conformance.
`slop_check.py` and `design_md_check.py` use the standard library only; their
hits are prompts to inspect, not verdicts on taste.

## Procedure

1. **Automated pass.** Run `render_check.js` with `--zoom`. Fix every reported
   problem before visual review.
2. **Look at the screenshots** (at least widest and narrowest, both themes).
   Check, in order:
   - Overlap and clipping: labels over labels, text cut off, chart labels
     outside the plot, sticky bars covering content.
   - Unexpected visibility: elements meant to be hidden appear (often a
     `display` rule overriding the `hidden` attribute).
   - Stretching: grid/flex children stretched to sibling height, leaving large
     gaps inside cards or lists.
   - Name collisions: a generic class (`.done`, `.active`, `.row`) styled for one
     component leaking into another.
   - Fonts: Thai rendered in the intended face (not a monospace or fallback),
     tone marks not clipped, line height adequate.
   - Hierarchy: one focal point, consistent alignment, density as specified
     ([visual-craft.md](visual-craft.md)).
3. **Drive the critical journey** with a script or manually: the happy path
   plus at least one failure path from the page spec (validation error,
   server failure, permission denial). Assert the visible result, not only the
   absence of errors.
4. **Keyboard pass** on changed areas: Tab order follows reading order, focus is
   visible, dialogs trap and return focus, Escape closes overlays.
5. **Contrast**: run `contrast.py --css <page>` to check role pairs in every
   theme block; add a JSON pairs file for pairs the script can't infer.
6. **Content stress**: longest real Thai and English values, empty values,
   large numbers, many rows.
7. **Fix → re-run steps 1–2.** Limit to what changed; report what was not re-checked.

## Example: a flow check with Playwright

```js
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  await p.goto('file:///path/to/page.html');
  await p.click('[data-act=reject]');                 // failure path: reject without a reason
  if (!(await p.isVisible('#noteErr'))) throw new Error('missing field error');
  await p.fill('#note', 'ชื่อบัญชีไม่ตรง');
  await p.click('[data-act=reject]');
  await p.click('[data-act=commit]');
  await p.waitForSelector('.toast:not([hidden])');
  console.log('reject path ok');
  await b.close();
})();
```

## Common defects and fixes

| Symptom | Usual cause | Fix |
|---|---|---|
| Text touches the screen edge at every width | A later shorthand (`.section{padding:96px 0}`) overrides the container's side padding | Use `padding-block` for vertical section spacing; keep the gutter on `.container` |
| Empty image slots in a full-page screenshot | `loading="lazy"` images never entered the viewport, or the URL failed | Load the first-screen pictures eagerly; confirm URLs resolve; `render_check.js` reports failures |
| Thai heading breaks mid-word | No spaces in Thai; the heading column is narrow | Wrap phrases in `display:inline-block` chunks ([design foundations](design-foundations.md)) |
| English headline wraps to 3 lines on phones while Thai fits | Latin display faces are wider per character than the Thai text implies | Check both languages (`--toggle`); shorten the English line or lower its size at 390 px |
| Page scrolls sideways on phone | Grid track sized by content (`grid` without `minmax(0,1fr)`), long unbroken strings, fixed widths | `grid-template-columns: minmax(0,1fr)`; `min-width:0` on flex/grid children; `overflow-wrap:anywhere` for IDs; tables in their own `overflow-x:auto` |
| Hidden element still visible | Component sets `display:grid/flex`, overriding `[hidden]` | Global `[hidden]{display:none !important}` |
| Big gaps inside a list or card | `align-items: stretch` with grid rows | `align-content:start` / `align-self:start` |
| Styles appear in unrelated component | Generic class names reused | Scope classes by component (`.queue-row`, `.stepper-item`) |
| Chart labels overlap | Labels positioned without collision rules | Move one label, reduce ticks, add right padding inside the viewBox |
| Thai text in monospace | Mono font applied to a container with mixed text | Apply mono only to IDs/numbers spans |
| Dark mode text unreadable | Literal colors outside the token system | Use tokens only; check pairs in both themes |
| Focus ring invisible on accent buttons | Focus color equals button color | Offset outline or a contrasting focus token |
| White text on a light semantic color in dark mode | Badge text hard-coded to white while the dark theme lightens the badge | Give badges an `--on-<color>` token per theme |
| Cells or rows faded to show state become unreadable | Opacity used as a state | Use a text badge or header label instead ([visual-craft.md](visual-craft.md)) |
| Users say colors are hard to read | Too many encodings per element | Apply the signal budget; one text color per ramp |

## Reporting

| Check | Result | Evidence |
|---|---|---|
| render_check (8 viewports; ×2 with `--toggle` on bilingual pages) | passed / failed (n issues) | output + screenshot paths |
| Visual review | issues found and fixed | before/after screenshots |
| Critical journey + failure path | passed / failed | script name or steps |
| Keyboard | passed / not tested | notes |
| Contrast | n/m pairs pass | contrast.py output |
| Not tested | screen reader, real API, real users… | — |

## Do / Don't

| Do | Don't |
|---|---|
| Render and screenshot before saying a page is done. | Report "built" from code that was never rendered. |
| Test the narrowest width and dark theme. | Check only a desktop light screenshot. |
| Drive at least one failure path. | Count "no console errors" as a passing flow. |
| Re-run checks after fixes and say what wasn't re-checked. | Assume a fix worked because the edit applied. |
