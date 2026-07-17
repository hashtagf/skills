# Component States — Taxonomy & Implementation

The most common failure in design systems is shipping components with only the default
state designed. Use this file when writing any component spec and when auditing coverage.

## Full checklist for one component

```
default → hover → focus-visible → active/pressed → selected/checked → disabled
→ loading → error/invalid → read-only → skeleton (+ open/closed for compound components)
```

Not every state applies to every component — a Divider has one state — but the spec must
say which states apply, so "missing" is distinguishable from "not applicable".

## 1. Interactive states

| State | Selector | Notes |
|---|---|---|
| Default / Rest | base style | |
| Hover | `:hover` | Guard with `@media (hover: hover)` — touch devices fire sticky hovers |
| Focus | `:focus-visible` (keyboard), `:focus-within` (container) | Plain `:focus` only when pointer focus should also show |
| Active / Pressed | `:active` | |
| Disabled | `:disabled`, `[aria-disabled="true"]` | `aria-disabled` stays focusable — better for discoverability |
| Visited | `:visited` | links only; CSS restricts styleable properties |

**Ordering rule**: base → hover → focus → active → disabled. Disabled must win — guard
hover/active with `:not(:disabled)` so specificity accidents can't resurrect hover styles.

## 2. Selection / value states

- Checked/Selected: `:checked`, `[aria-selected]`, `[aria-pressed]` (toggle buttons), `[aria-current]` (current nav item)
- Indeterminate: `:indeterminate` (partial checkbox, unknown progress)
- Activated (Material): persistent "you are here" state, distinct from transient selected
- Dragged: elevated + state layer (Material treats it as a first-class state)

## 3. Form / validation states

- `:user-invalid` / `:user-valid` — fire only after interaction; prefer over `:invalid`,
  which marks required fields red on page load
- `:required`, `:read-only`, `:placeholder-shown`, `:out-of-range`
- Semantic layer on top: **error / warning / success / info** with message + icon + border
  color. Wire `[aria-invalid="true"]` and use it as the styling hook — accessibility for free.
- **Placeholder rules**: a placeholder is never the label and never carries required
  information — it vanishes on typing. Always pair with a persistent label (or helper
  text for format hints). Style it clearly lighter than value text but still ≥ 4.5:1.
- **Validation timing**: validate on blur or on submit — never per-keystroke before the
  first submit (red-while-typing punishes users mid-word). On failed submit, focus the
  first invalid field; long forms add an error summary linking to each field. Error
  messages sit at the field and say how to fix it, not just "invalid".

## 4. Loading / content states

- Loading/Busy (`[aria-busy]`), per-component Skeleton, Empty state, Error state — the
  container-level states product screens actually spend time in.

## 5. Structural states (compound components)

- Open/Closed, Expanded/Collapsed: `[aria-expanded]`, `[open]`, or `data-state="open|closed"`
- On/Off (switch), Highlighted (`data-highlighted`), Drop target (`data-drop-target`)

## How major systems model states (for calibration)

| System | Official states | Mechanism |
|---|---|---|
| Material 3 | enabled, disabled, hovered, focused, pressed, dragged | **State layer**: on-surface overlay at 8% hover / 10% focus / 10% pressed / 16% dragged |
| Carbon | enabled, hover, focus, active, selected, disabled, error, warning, read-only, skeleton | Explicit token per state (`$button-primary-hover`) |
| Fluent 2 | rest, hover, pressed, focused, disabled, selected | Per-state color tokens |
| Radix/shadcn | open/closed, checked, disabled, highlighted… | `data-state` attributes styled via `data-[state=open]:` |

Pick ONE interaction-color strategy for the whole system:
- **State layer** (Material): scales automatically to any base color — fewer tokens, good default for a new system.
- **Explicit per-state tokens** (Carbon): more control, more tokens to maintain — good when brand colors need hand-tuned hover shades.

## Implementation rules

1. Native elements → CSS pseudo-classes; JS-driven state → `data-state` attributes.
2. Style off ARIA attributes (`[aria-expanded="true"]`, `[aria-invalid]`) where possible —
   it forces correct markup and keeps a11y in sync with visuals by construction.
3. State must never be color-only (WCAG 1.4.1): pair color with icon, underline, weight, or border.
4. Focus indicator contrast ≥ 3:1 (WCAG 2.4.11); one spec system-wide.
5. Test states under `forced-colors: active` (Windows High Contrast) — state layers and
   subtle backgrounds disappear there; borders and outlines survive.

## Keyboard interaction contracts (per component family)

States and keyboard behavior ship together — a focus style without the keys that reach it
is decoration. These follow the ARIA Authoring Practices; put them in each component's
spec and test them in interaction tests.

| Family | Keys |
|---|---|
| Dialog / Drawer | Tab trapped inside; `Esc` closes; focus returns to the trigger on close |
| Menu / Dropdown / Context menu | `Enter`/`Space`/`ArrowDown` opens; arrows navigate; `Esc` closes; type-ahead jumps |
| Tabs | Arrows switch tabs (roving tabindex); `Home`/`End` first/last; `Tab` exits into the panel |
| Select / Listbox / Combobox | Arrows navigate options; `Enter` selects; `Esc` closes; type-ahead; combobox keeps focus in the input |
| Checkbox / Switch | `Space` toggles |
| Radio group | Arrows move AND select (one tab stop for the group) |
| Slider | Arrows step; `PageUp`/`PageDown` big step; `Home`/`End` min/max |
| Accordion | `Enter`/`Space` toggles the focused header |
| Data grid (`role=grid`) | Arrows move cell focus; `Home`/`End` row edges; `PageUp`/`PageDown` scroll |
| Toast / status region | Never steals focus; announced via `aria-live`; a hotkey or F6 reaches the region |
