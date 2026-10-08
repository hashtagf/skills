# Do / Don't examples for component usage

Read while writing usage docs or reviewing misuse. These are illustrative contracts,
not a complete component library or executed test suite. Adapt element names, IDs,
tokens and public APIs to the project. Behavior detail lives in `states.md`;
language/theme detail lives in `foundations.md` and `theming.md`.

## Writing a useful pair

Use this compact format in a component spec or docs:

| Do — intended usage | Don't — concrete misuse | Why | Verify |
|---|---|---|---|
| Example using the component's supported API. | Example showing the actual failure. | User or consumer consequence; label requirement versus recommendation. | Observable result, and whether it passed, failed or remains untested. |

Include the important context: submit versus navigation, modal versus non-modal,
manual versus automatic activation, native disabled versus focusable aria-disabled.
Document valid exceptions when a recommendation depends on context. Choose enough
pairs to explain likely misuse; a fixed number is not a completeness test.

## Button and Icon Button

| Do | Don't | Why | Verify |
|---|---|---|---|
| Use a native button for an action, with `type="button"` unless it should submit the form. Use a link with a destination for navigation. | Render an action as a clickable div, or let an incidental form action default to submit. | Native semantics and activation match the task; unintended submission interrupts input. | Tab to the action; exercise Enter/Space as appropriate; confirm only the intended action submits. |
| Give an icon-only button an accessible name, e.g. `<button type="button" aria-label="ปิด"><svg aria-hidden="true">…</svg></button>`. | Ship a close icon with no accessible name, relying on its shape or tooltip alone. | The action needs a name independent of visual recognition. | Inspect the accessibility tree: the button has the intended name; verify focus visibility. |
| Use native `disabled` when suitable. If using a focusable `aria-disabled="true"` button, block its activation path and retain visible focus. | Set opacity or aria-disabled and leave the action handler active. | aria-disabled supplies semantics, not activation prevention. | Mouse and keyboard activation perform zero actions while disabled; chosen tab-order behavior matches the spec. |
| During submission, prevent duplicate execution, retain an understandable label and expose loading status. | Replace the label with an unnamed spinner while allowing repeat submission. | Users need to understand progress; duplicate actions can produce duplicate bookings. | Repeated activation creates one pending action; name/status remain understandable, including under reduced motion. |

## Form Field

Do — when an error is present, associate it with the field while retaining a label:

```html
<label for="booking-name">ชื่อผู้จอง</label>
<input id="booking-name" name="bookingName"
       aria-invalid="true" aria-describedby="booking-name-error">
<p id="booking-name-error">กรอกชื่อผู้จองเพื่อดำเนินการต่อ</p>
```

Don't — rely on placeholder and a visual border to communicate the same information:

```html
<input placeholder="ชื่อผู้จอง" class="red-border">
```

**Why:** a disappearing placeholder is insufficient as the persistent label, and
border color alone does not explain the error. The Do example represents an already
invalid field; do not copy its invalid state onto untouched inputs.

**Verify:** inspect the field's name and description, read the error with assistive
technology, and test that valid/untouched input is not styled invalid. Confirm unique
IDs when multiple fields render. Test the documented failed-submit focus destination
(first field for a short form, or linked summary where that pattern is chosen).

## Tabs

| Do | Don't | Why | Verify |
|---|---|---|---|
| For manual activation, arrows move tab focus; Enter/Space activates and changes the panel. Style selection with `[aria-selected="true"]`. | Change a slow-loading panel on every arrow press, or use `[aria-selected]` to style selection. | Activation policy affects navigation; the presence selector also matches false values. | Arrow movement leaves the active panel unchanged; activation changes it; only the selected tab has selected styling. |
| Link tabs and panels with their IDs, preserve roving focus, and keep inactive content out of keyboard navigation. | Make every tab and hidden panel independently tabbable. | Keyboard navigation and the relationship between control and content must remain understandable. | Tab enters the tab list at its intended stop and proceeds to active content; hidden-panel controls receive no focus. |

Automatic activation is valid when panel display has no noticeable latency. Record
the selected policy and test that policy; do not impose manual activation universally.

## Dialog and Drawer

| Do | Don't | Why | Verify |
|---|---|---|---|
| For a modal, provide a name, an appropriate initial focus target, inert background, contained Tab navigation and documented close/focus-return behavior. | Set aria-modal on a visually floating panel while background controls remain operable. | Modal semantics must match actual interaction. | Open by keyboard; Tab/Shift+Tab stay inside; test close and return to the invoker or documented logical successor. |
| Specify a non-modal drawer's navigation and focus behavior separately. | Apply a modal focus trap to every drawer just because it slides in. | Non-modal panels may require interaction with the surrounding page. | Confirm the product's modal/non-modal contract and test whether background interaction behaves accordingly. |

## Theme-aware components and Thai labels

| Do | Don't | Why | Verify |
|---|---|---|---|
| Consume the existing semantic surface/text roles and verify relevant states in supported themes. | Put raw white/black values into component CSS for theme-dependent surfaces. | Those values can bypass theme mappings and break contrast. | Render the component under each supported theme and check resolved foreground/background pairs. |
| Start Thai text with suitable font metrics and generous leading; adjust using actual rendered labels, marks and zoom. | Mark typography complete solely because line-height equals 1.6. | Font, size and content determine clipping and readability; the number alone is insufficient evidence. | Render long Thai/Latin labels and stacked marks at normal size and zoom; inspect clipping, wrapping and truncation. |

## Reviewing the resulting docs

Confirm that the Do example matches the shipped API, the Don't demonstrates a likely
failure, and the check tests the stated reason. Link execution evidence when available;
otherwise mark the check untested. A docs example does not establish implementation
correctness without the corresponding behavior being checked.
