# Theming & Density

Read this when adding a second theme (dark mode) or density variants.
Both work the same way: they re-point the **semantic** token layer only. If any
component token references a primitive directly, fix that first — grep for it before
starting, because one leaked primitive breaks every variant silently.

## Second theme (dark mode) playbook

1. **Audit the semantic layer.** Every color a component uses must resolve through a
   semantic token. Grep component CSS for raw hex and primitive names; fix leaks first.
2. **Choose the switching mechanism** (all three together):
   - `@media (prefers-color-scheme: dark)` as default
   - explicit `[data-theme="dark"]` / `[data-theme="light"]` on the root that WINS over
     the media query (user toggle beats OS)
   - `color-scheme: dark` on root so native widgets (scrollbars, inputs) follow
   - set the attribute in an inline `<head>` script to avoid a flash of wrong theme
3. **Write the dark value set — dark is not inverted light:**
   - Elevation flips medium: shadows are weak in dark; raised surfaces get **lighter**
     (step up the neutral scale or overlay white at 4–12% per level)
   - Reduce saturation of large filled areas; brand fills often need a lighter, less
     saturated dark-mode variant to hold contrast
   - Text: pure white on dark vibrates — use off-white (~90% luminance) for primary text
   - Status colors need their own dark variants (the light ones usually fail contrast on dark bg)
   - Disabled/overlay opacities usually differ between themes — re-tune, don't copy
4. **Images/illustrations**: provide dark variants or wrap in a dimming filter token.
5. **Re-verify everything**: contrast check every semantic text/bg pair per state in the
   new theme, and re-render the component preview pages in both themes.

## Density variants

- Density tokens cover **size only**: control heights, paddings/gaps, type sizes — never colors.
- Implement as `[data-density="compact"]` re-pointing semantic size tokens
  (e.g. `--control-height-md: 40px → 32px`, paddings one step down the spacing scale).
- Precondition: components consume sizes via tokens, not literals. Do NOT model density
  as per-component props — it becomes unmixable and drifts.
- Touch targets still ≥ 44px on touch devices even in compact (extend hit area, not the visual).
