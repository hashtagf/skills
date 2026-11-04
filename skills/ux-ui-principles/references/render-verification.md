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
| `scripts/render_check.js` | Renders at 1440/768/390 px (+320 px with `--zoom`) in light and dark; reports JS/console errors, failed requests, horizontal page overflow with the offending elements, images without alt, unnamed buttons/links, unlabeled fields; saves full-page screenshots | `node scripts/render_check.js <url-or-file> --out <dir> [--zoom]` |
| `scripts/contrast.py` | WCAG contrast ratio for color pairs with per-pair minimums; `--css` reads token blocks (light, dark, palettes) from a page and checks role pairs automatically | `python3 scripts/contrast.py --css page.html` or `python3 scripts/contrast.py pairs.json` |

`render_check.js` needs Playwright. It is a smoke check: it does not prove
keyboard operability, screen-reader behavior, task success or WCAG conformance.

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
| render_check (8 viewports) | passed / failed (n issues) | output + screenshot paths |
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
