# Tablet, right-to-left and dark customer pages

Pictures: back-office `previews/tablet/` (820 × 1366), `previews/rtl/` (mirrored layout),
customer dark sheets in `assets/site/previews/dark/`.

## Tablet (768–1024px; breakpoints in [design-foundations.md](design-foundations.md))
- Navigation: a side nav collapses to an icon rail (tooltips on hover/focus); top navs keep working or fold into a menu.
- Tables: hide secondary columns (account, dates) before shrinking text; row details open in a drawer. Never shrink below the minimum text size in [design-foundations.md](design-foundations.md#typography) (14px in tablet tables).
- Cards: KPI rows go to 2 columns; two-pane layouts stack, list first.
- Filter bars wrap onto two lines; bulk actions stay visible.
- Touch targets: project default in [accessibility.md](accessibility.md); support both portrait and landscape; no hover-only actions.
- Test at 768, 820 and 1024; both orientations.

## Right-to-left
- Set `dir="rtl"` and `lang` on the document; use CSS logical properties (`margin-inline-start`, `padding-inline`, `inset-inline`, `text-align: start`).
- Mirror layout and direction icons (chevrons, back, arrows, progress, send, undo, list bullets, sliders). Do **not** mirror logos, clocks, media controls, check marks, numbers or charts' time axis (time usually still runs as the reader expects; decide and state it).
- Numbers and Latin names inside RTL text need bidi isolation (`<bdi>` or `unicode-bidi: isolate`); IDs, emails and codes stay left-to-right. The preview shows the failure when this is missing (a trailing period jumping to the front).
- Inputs for numbers, emails, URLs and codes stay `dir="ltr"` even in RTL pages; table numeric columns align to the end.
- Test with real Arabic or Hebrew copy; the preview mirrors layout only, strings stay English.
- Fonts need the script: pick an Arabic or Hebrew face with matching weight; do not letter-space or uppercase.

## Dark pages for light directions
- Derive, then check: `python3 scripts/export_tokens.py <id> --print-dark` (see [tokens to code](tokens-export.md)); every pair passes AA.
- Surfaces step up in lightness (ground < surface < raised); no pure black or pure white; shadows give way to tone steps and a hairline border.
- Accent moves lighter to keep contrast; art and photos are dimmed or re-graded, not left glaring.
- Offer a toggle and honor `prefers-color-scheme`; do not make dark the only theme for light-leaning brands.
- Check images with transparent backgrounds and logos on the dark ground.
