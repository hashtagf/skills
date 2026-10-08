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
| Disabled | `:disabled`, `[aria-disabled="true"]` | `aria-disabled` changes semantics only; focusability is a deliberate choice and JS must prevent activation |
| Visited | `:visited` | links only; CSS restricts styleable properties |

**Ordering rule**: base → hover → focus → active → disabled. Disabled must win — guard
hover/active with `:not(:disabled):not([aria-disabled="true"])` so specificity accidents can't resurrect hover styles.

## 2. Selection / value states

- Checked/Selected: `:checked`, `[aria-selected="true"]`, `[aria-pressed="true"]` (toggle buttons), `[aria-current="page"]` or another documented current value; presence selectors also match false
- Indeterminate: `:indeterminate` (partial checkbox, unknown progress)
- Activated (Material): persistent "you are here" state, distinct from transient selected
- Dragged: elevated + state layer (Material treats it as a first-class state)

## 3. Form / validation states

- `:user-invalid` / `:user-valid` — fire only after interaction; prefer over `:invalid`,
  which marks required fields red on page load
- `:required`, `:read-only`, `:placeholder-shown`, `:out-of-range`
- Semantic layer on top: **error / warning / success / info** with message + icon + border
  color. Wire `[aria-invalid="true"]` and use it as the styling hook — associate a persistent label and error text (e.g. aria-describedby); ARIA styling alone does not provide accessibility.
- **Placeholder rules**: a placeholder is never the label and never carries required
  information — it vanishes on typing. Always pair with a persistent label (or helper
  text for format hints). Style it clearly lighter than value text but still ≥ 4.5:1.
- **Validation timing**: choose timing by task; avoid premature errors while users compose input. After a failed submit, focus a linked error summary for long forms, or the first invalid field for short forms; document the chosen behavior. Error
  messages sit at the field and say how to fix it, not just "invalid".

## 4. Loading / content states

- Loading/Busy (`[aria-busy="true"]`), per-component Skeleton, Empty state, Error state — the
  container-level states product screens actually spend time in.

## 5. Structural states (compound components)

- Open/Closed, Expanded/Collapsed: `[aria-expanded="true"]`, `[open]`, or `data-state="open|closed"`
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
2. Style off ARIA attributes (`[aria-expanded="true"]`, `[aria-invalid="true"]`) where possible —
   keep semantics and visuals aligned, then separately test names, relationships and behavior.
3. State must never be color-only (WCAG 1.4.1): supply a meaningful non-color cue, such as text or a recognizable icon; a border color change alone is insufficient.
4. Visible focus: 2.4.7; non-obscuration: 2.4.11 AA; applicable non-text contrast: 1.4.11. Focus appearance 2.4.13 is AAA. Use a shared contract with surface adaptations.
5. Test states under `forced-colors: active` (Windows High Contrast) — state layers and
   subtle backgrounds disappear there; borders and outlines survive.

## Keyboard interaction contracts (per component family)

States and keyboard behavior ship together — a focus style without the keys that reach it
is decoration. These follow the ARIA Authoring Practices; put them in each component's
spec and test them in interaction tests.

| Family | Keys |
|---|---|
| Modal Dialog / modal Drawer | Background inert; Tab contained; `Esc` closes; focus returns to the trigger on close |
| Menu / Dropdown / Context menu | `Enter`/`Space`/`ArrowDown` opens; arrows navigate; `Esc` closes; type-ahead jumps |
| Tabs | Arrows move tab focus; auto-activate only with low latency, otherwise Enter/Space activates. Home/End optional. Tab proceeds into the active panel |
| Custom Listbox / Combobox | Follow the specific APG popup pattern; editable listbox combobox typically retains DOM focus with aria-activedescendant. Preserve native select behavior |
| Checkbox / Switch | `Space` toggles |
| Radio group | Arrows generally move and select; toolbar radio groups have different contracts |
| Slider | Arrows step; `PageUp`/`PageDown` big step; `Home`/`End` min/max |
| Accordion | `Enter`/`Space` toggles the focused header |
| Data grid (`role=grid`) | Arrows move cell focus; `Home`/`End` row edges; `PageUp`/`PageDown` scroll |
| Toast / status region | Never steals focus; announced via `aria-live`; interactive actions remain reachable; any optional hotkey is a product contract, not an APG requirement |
