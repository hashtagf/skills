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
