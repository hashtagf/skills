# Design tokens to code

Turns a chosen direction into files a project can use, with the contrast already checked.
Use it in phase 5 (Implement) after the direction is chosen, or to start `DESIGN.md` colors.

```
python3 scripts/export_tokens.py <direction-id> --out src/styles
python3 scripts/export_tokens.py --list
python3 scripts/export_tokens.py --json my-brand.json     # same keys as a directions.json entry
python3 scripts/export_tokens.py <direction-id> --only css,tailwind,shadcn   # subset of files
```

Default output directory is `./tokens-<id>/` when `--out` is omitted. Exit codes: 1 when a
color pair cannot pass, 2 for an unknown direction.

| File | For | Notes |
|---|---|---|
| `tokens.css` | any stack | `--color-*`, fonts, `--radius-*`, shadow, space, type, motion (`--dur-fast/base/slow`, `--ease-out/in/in-out`; names and meaning owned by [motion.md](motion.md) §2). Light and dark; `data-theme` or `prefers-color-scheme` switches. Reduced motion zeroes the durations. |
| `tailwind-theme.css` | Tailwind v4 | `@theme inline` onto `tokens.css`: `bg-paper`, `text-ink`, `bg-accent`, `rounded-card`, `font-display`. |
| `shadcn-globals.css` | shadcn/ui | `:root`, `.dark`, chart 1–5, sidebar, `--radius`, `@theme inline`. Replace the default blocks in `globals.css`. |

## Rules the script applies

- Dark theme is **derived** (or light, for a dark direction) and every pair is checked for
  WCAG AA; colors move in lightness until they pass. It exits 1 if one cannot.
- **Fill and text accents are separate**: `--color-accent` keeps the brand color for fills and
  buttons; `--color-accent-text` is the darker or lighter step for links and small text.
- Text on the accent fill is picked for contrast (`--color-accent-ink`). The script prints a
  `note` when it changes the direction's own value (many bright accents need dark text).
- Cards of the opposite tone get `--color-surface-ink` and `--color-surface-muted`.
- Status colors (ok, warn, bad, info) are derived per theme to 4.5:1. Never rely on color alone.
- Thai falls back to Noto Sans Thai in every font stack.

## After exporting

1. Add the Google Fonts links for the two families (Latin faces here are approximations).
2. Run `python3 scripts/contrast.py --css <page>` on the built page, not only on the tokens.
3. Read each `note`: they are the places where the direction was bent to pass.
4. Record the result in `DESIGN.md` (colors, dark theme, radius, why); see
   [design memory](design-memory.md).

Limits: tints are decorative, not text colors; shadows are one preset per surface rule;
no multi-brand or density tokens; check the dark theme by eye, it is derived, not designed.
