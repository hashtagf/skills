# Data visualization

Charts exist to answer a question someone will act on. Start from the question,
then choose the form. Source IDs resolve in [sources.md](sources.md). Dashboard
page structure is in [back-office.md](back-office.md); color in [color-palette.md](color-palette.md).

## Start from the question

| Question type | Chart forms that usually fit | Avoid |
|---|---|---|
| Change over time | Line, area (single series), column for few periods | Pie; many overlapping lines |
| Magnitude / comparison | Bar (horizontal for long labels), dot plot | 3D bars, radial bars |
| Ranking | Ordered bar, lollipop | Unordered bars |
| Part-to-whole | Stacked bar (few parts), 100% bar, treemap; pie only for 2–3 parts | Pie with many slices; donut with a big number hiding the parts |
| Deviation from target | Diverging bar, line with target band | Separate charts for actual and target |
| Distribution | Histogram, box plot, strip plot | Averages alone |
| Correlation | Scatter, connected scatter | Dual-axis lines implying causation |
| Flow | Sankey, funnel (ordered steps) | Funnel for non-sequential categories |
| Spatial | Map only when location matters | Maps for data that is really a ranking |

These categories follow established chart vocabularies that classify charts by
the relationship they show. [S85]

Often a **number with context** or a **table** is better than a chart: one KPI
with target and trend, or exact values users must copy.

## Make it readable

- Title states the finding or question ("Success rate fell below target after 13:00"),
  subtitle states the metric, unit, scope and time window.
- Label directly on lines/bars instead of a distant legend where possible.
- Axes start at zero for bars; lines may use a focused range but must show the scale.
- One axis per unit; avoid dual axes unless users are trained on them.
- Show targets, thresholds and comparison periods as reference lines/bands.
- Emphasize the data that matters (latest value, anomaly); mute the rest.
- Round sensibly; use tabular figures; include units and currency.
- Annotate events that explain changes (deploy, outage, campaign).

## Color in charts

- Categorical palette with distinct hues and similar lightness; limit to ~6
  categories, group the rest as "อื่น ๆ".
- Sequential palette (light → dark) for ordered magnitude; diverging palette
  around a meaningful midpoint (target, zero).
- Don't reuse semantic colors (success/error) for ordinary categories.
- Don't rely on color alone: direct labels, patterns or shapes. [S67]
- Graphical objects needed to understand the chart need 3:1 contrast against
  adjacent colors (WCAG 1.4.11). [S04]
- Check both light and dark themes.

## Data states

| State | Show |
|---|---|
| Loading | Skeleton in chart dimensions; keep axes stable |
| No data for period | Explain ("ยังไม่มีธุรกรรมในช่วงนี้") — not a flat zero line |
| Zero | A real zero, plotted |
| Missing / partial | Gap in the line, with a note; don't interpolate silently |
| Stale | "อัปเดตล่าสุด 14:44" and a warning when older than expected |
| Error | Message and retry; keep last good data visible if labeled as stale |

## Interaction

- Tooltips show exact values and are reachable by keyboard; don't hide essential
  information only in tooltips.
- Filters and time ranges show current state and are reflected in the URL.
- Drill-down goes from summary to the records behind the number.
- Provide "view as table" or download for exact values.

## Accessibility

Complex images such as charts need a short text alternative and access to the
full information, e.g. a data table or long description. [S86]

- `role="img"` with an `aria-label` summarizing the key finding for simple charts.
- A data table (visible or toggled) for exact values.
- Keyboard access to interactive points; focus visible.
- Respect reduced motion for animated transitions.

## Dashboards

- Order by the role's decision (see [back-office.md](back-office.md)).
- Every KPI: value, unit, comparison, time window, freshness.
- Few charts that answer different questions beat many charts of the same metric.
- Align chart widths and axes when users compare across charts.

## Review checklist

1. The question the chart answers is written in its title.
2. Chart form matches the relationship (time, comparison, part-to-whole…).
3. Scales are honest; bars start at zero.
4. Units, time window, source and freshness are visible.
5. Color is not the only cue; contrast meets 3:1 for needed graphics.
6. Zero, missing, stale and error states are distinct.
7. A text summary and table/alternative exist.

## Do / Don't

| Do | Don't |
|---|---|
| Title the chart with the finding. | Title it "Chart 1" or with the metric name only. |
| Use a bar chart for comparing categories. | Use a pie chart with eight slices. |
| Show a target line on performance charts. | Make users remember the target. |
| Show missing data as a gap with a note. | Draw missing data as zero. |
