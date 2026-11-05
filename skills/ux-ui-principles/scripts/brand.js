/*
 * One brand, one token set. A direction (assets/directions/directions.json) is the single source for a
 * product's public pages AND its product UI: the same ground, ink, accent, faces and radius. What differs by
 * surface is structure and density (navigation, table style, row height), which comes from the closest
 * back-office look in assets/backoffice/styles.json.
 *
 *   productStyle(direction, styles) -> a back-office style object (same keys as styles.json), so
 *   backoffice_preview.js --direction <id> draws the admin screens of that brand.
 *
 * The base look is chosen from the direction's character unless the direction names one in
 * `product.base`; `product` may also override nav, tbl, density (comfortable | compact).
 * Standard library only.
 */

function hex(h) { const m = /^#?([0-9a-f]{6})$/i.exec(h || ''); return m ? parseInt(m[1], 16) : null; }
function lum(h) {
  const n = hex(h); if (n == null) return 1;
  const c = [(n >> 16) & 255, (n >> 8) & 255, n & 255].map((v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; });
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
function mix(a, b, t) { // a*(1-t) + b*t
  const x = hex(a), y = hex(b); if (x == null || y == null) return a;
  const ch = (n, s) => (n >> s) & 255;
  const v = [16, 8, 0].map((s) => Math.round(ch(x, s) * (1 - t) + ch(y, s) * t));
  return '#' + v.map((n) => n.toString(16).padStart(2, '0')).join('');
}
const contrast = (a, b) => { const [x, y] = [lum(a), lum(b)].sort((p, q) => q - p); return (x + 0.05) / (y + 0.05); };

function baseFor(d) {
  if (d.product && d.product.base) return d.product.base;
  const dark = lum(d.ground) < 0.2;
  const mono = /mono/i.test(d.display + d.body);
  const print = d.radius <= 2 && (d.btn === 'square' || !d.btn);
  if (dark) return mono ? 'graphite' : 'night';
  if (mono) return 'mono';
  if (print) return d.group === 'playful' ? 'contrast' : 'ledger';
  if (d.radius >= 20) return 'calm';
  return 'harbor';
}

function productStyle(d, styles) {
  const baseId = baseFor(d);
  const b = styles.find((s) => s.id === baseId) || styles[0];
  const dark = lum(d.ground) < 0.2;
  // product UI wants a quieter ground than a poster: keep the hue, pull it toward the surface
  const ground = dark ? d.ground : mix(d.ground, d.surface, 0.35);
  const surface = d.surface;
  const r = Math.min(d.radius, 14);
  const accentInk = contrast(d.accentInk, d.accent) >= 4.5 ? d.accentInk : (contrast('#ffffff', d.accent) >= contrast('#111111', d.accent) ? '#ffffff' : '#111111');
  const p = d.product || {};
  const compact = p.density === 'compact' || (!p.density && b.rowH <= 44);
  return Object.assign({}, b, {
    id: d.id, name: `${d.name} (product)`, note: `Product UI of the ${d.name} direction on the ${b.name} structure.`,
    dark, ground, surface, side: dark ? mix(d.ground, d.surface, 0.5) : surface, sideDark: false,
    ink: d.ink, muted: d.muted, line: mix(surface, d.ink, dark ? 0.18 : 0.12),
    accent: d.accent, accentInk, accentSoft: mix(surface, d.accent, dark ? 0.22 : 0.14),
    font: d.body, displayFont: d.display,
    radius: r, cr: Math.min(r + 4, 18), br: d.btn === 'pill' ? 999 : Math.min(r, 10), fr: Math.min(r, 10), nr: Math.min(r, 10),
    chip: d.btn === 'square' ? 'square' : (b.chip || 'pill'),
    edge: r <= 2 ? 'line' : b.edge,
    nav: p.nav || b.nav, tbl: p.tbl || b.tbl,
    rowH: compact ? Math.min(b.rowH, 44) : Math.max(b.rowH, 48),
    direction: d.id, base: b.id,
  });
}

module.exports = { productStyle, baseFor, mix, lum, contrast };
