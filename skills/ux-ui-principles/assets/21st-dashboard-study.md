# 21st.dev dashboard study — widget patterns

Observed 2026-11-05 on 21st.dev/community/components/s/dashboard (207 listed).
About 80 thumbnails were read by eye across the grid; none measured, nothing
copied. Community gallery: shows trends, not a standard.

## Widget types seen (most common first)

1. **Stat tile** — label, big number (tabular), delta pill (green/red, tiny arrow), a sparkline or "vs yesterday". Rows of 3–4.
2. **Area/line chart with an end dot** — soft gradient fill under a 2px line, last point marked with a glowing dot, light grid, month ticks only.
3. **Donut with centre total** — 2–5 parts, rounded caps, gap between arcs, total + caption inside; legend as dot + label + value + %.
4. **Data table** — hairline rows, avatar + two-line name cell, status dot-pill, progress bar column, row action "⋮", footer total row.
5. **Status/uptime strip** — 60–90 thin vertical bars per service (green, with amber/red incident bars), uptime % right-aligned, "all systems operational" pill on top.
6. **Ranked bars** — avatar, name, value, bar in palette colours, sorted; "bar race" playback control.
7. **Ring meters row** — 3–4 circular gauges with % inside, caption under; dark panel.
8. **Resource cards** — host name, status chip, CPU/memory/disk as thin labelled bars with threshold colour.
9. **Big number hero** — one KPI at display size over a faint area chart (orders, balance).
10. **Calendar / task list / activity feed** — dense month grid with event chips; checklist with due-date chips (Today / Yesterday / 1 week).
11. **Bento KPI grid** — mixed tile sizes, one tile dark or tinted to anchor the eye.
12. **Odd ones** — pixel/weather widget, isometric 3D chart, crypto cards each with own sparkline, brutalist bordered analytics. Novelty, rarely reusable.

## What makes them look finished

- One number is much larger than everything else in the card; labels are small and muted.
- Delta pills use a tinted background, not just coloured text.
- Charts drop axes and gridlines to a whisper; the data mark carries the colour.
- Cards use a large radius and one soft shadow; dark ones use a 1px lighter border, not shadow.
- A tile or panel in an accent or dark tone anchors a light page.
- Tables breathe: 48–56px rows, no vertical rules.
- Mono type for numbers and IDs in technical dashboards (infra, logs, API).
- Empty space inside cards is allowed; cards are not stretched to fill.

## What looks weak (seen often)

- Eight identical white tiles with a line chart each.
- Tiny unreadable labels in thumbnails (under 10px) — copy the layout, not the size.
- Donuts with 6+ segments or no legend.
- Dark panels with grey-on-black captions under 4.5:1.

## Use in this skill

Rules went into `references/back-office.md` ("Widget recipes") and
`references/data-visualization.md` (uptime strip, end-dot chart, ring meters).
