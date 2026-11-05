# App-screen rules (Operate surface)

Pages people work in: dashboards, admin, settings, inboxes. Complements
[back-office](back-office.md). Source: Taste Skill app-screen study.

## 1. One question per page

Write the page's one question in one line. The biggest element answers it;
the largest figure matches the title row's sentence; blocks that do not serve
it are cut. Three numbers beat a chart when three numbers suffice.

## 2. Quiet chrome, with numbers

Marketing-page bans relax here, within limits:
- 1px decorative container, card and row borders at about 1.1–1.3:1 against
  the ground; a border **or** a shadow, never both. Input and control
  boundaries keep ≥ 3:1 ([forms.md](forms.md), [accessibility.md](accessibility.md)). Shadows only on floating elements (menus, dialogs).
- Row rules 3–7% darker than the surface; prefer lines over zebra and a header
  band unless the chosen back-office look sets them (the look in
  `assets/backoffice/styles.json` wins; see [back-office.md](back-office.md)).
- Pills 16–24px tall, tinted, inside rows. At most one tracked uppercase label
  per screen.
- Accent only for state that needs attention and the primary action.

## 3. Grid arithmetic closes

Write the sum down (3 × 372 + 2 × 17 = 1152). Choose the column count from the
item count. Cards in a row share a bottom edge; a stretched card gets only a
pinned action or total. Tables of 5 columns or fewer run about 760px wide at
1440 and pair with another block, never float alone in an empty canvas.

## 4. Data honesty

- List every fact shown twice and check the copies agree.
- Recompute totals and deltas from the displayed values; every relative figure
  names its base.
- A zero looks like a zero, a missing value like a dash.
- No vanity totals or growth on a week-old account.

## 5. Generated-dashboard tells

KPI values at 24–30px, not 48; no sparkline on every KPI; no icon in a tinted
circle per KPI; line charts 2px straight with 3–5 faint gridlines and no legend
for one series; thin donuts without a legend carrying label, value and percent (see [data-visualization.md](data-visualization.md#dashboard-widgets)); an empty chart shows the zero
line and one sentence, not an illustration.

## 6. Modal needs a reason

Use a modal only when the task needs interruption or protected focus (a
destructive confirm, a required decision). Otherwise inline, a sheet or a page.

## 7. Operational UI doctrine (dashboards, admin, CRM, internal tools)

Source: Codex `webapp-ui-skill`, kept where it adds to the rules above.

- **Scan, compare, repeat.** Optimize for scanning rows, comparing values and
  repeating an action; not for composition. Open on the task, never on a hero.
- **Stable geometry.** Buttons, controls, table columns and row heights keep
  their size on hover, loading and selection; a spinner replaces the icon, not
  the width. Filters and sticky headers never move the data under the cursor.
- **Frames.** A card is for repeated items, a modal or a genuinely framed tool.
  No card inside a card (use spacing or a divider); no page section as a card.
- **Type.** Panel and page headings ≤ 24px in dense layouts; no viewport-scaled
  font sizes (`vw` without `clamp`); no negative tracking.
- **Control by job.** Segmented = mode switch (2–5 options); toggle = binary
  setting applied now; menu = option set; stepper/slider/input = numbers; icon
  alone only for familiar tool actions, label for destructive or ambiguous ones.
- **Layout.** Predictable shell (sidebar, topbar, tabs, split pane, command
  menu); high-frequency filters beside the data they change; detail pane for
  repeated inspect/edit; full-width operational layouts over decorative sections.
- **Palette.** One neutral ground, one brand hue, a semantic set (success,
  warning, danger, info) that never doubles as decoration. A one-note palette
  cannot show status.
- **Never ship:** empty state without a next action; error that discards the
  user's input; hidden keyboard focus; disabled control with no reason when the
  user could reasonably expect it to work; hero as the first screen.
- **State matrix.** Per surface, fill loading · empty (no data / filtered /
  no permission) · error (network / validation / auth / unknown) · disabled ·
  focus · selected · submitting · success. Each cell: designed, N/A with
  reason, or unverified. `scripts/state_check.py <src>` finds markers only; a
  hit is not proof the state is reachable, so label it Manual.
- **Checks:** `slop_check.py` flags `viewport-scaled-font`, `nested-cards`,
  `hero-in-app`; `render_check.js` covers overflow and tap targets.
