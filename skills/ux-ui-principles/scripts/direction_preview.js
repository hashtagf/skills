#!/usr/bin/env node
/*
 * Render one-screen preview pictures of the directions in assets/directions/directions.json,
 * so a user can choose a look from pictures (references/direction-library.md).
 *
 * Usage:
 *   node scripts/direction_preview.js [--ids dose,riso] [--group company|premium|playful|atmospheric]
 *        [--out dir] [--width 1440] [--height 1240] [--sheet] [--brief "Headline|Sentence|Button"] [--comp c1..c14] [--subject <pack>]
 *        [--same-comp]
 *
 * A shortlist (--ids) must differ in layout, not only colour: when two listed directions share a composition,
 * the later ones are drawn in the next unused composition and the script says so (--same-comp keeps them).
 * For a client, add --subject <their kind> (e.g. dental) so every option shows their world.
 *
 * Each direction is drawn in its own composition (scripts/compositions.js: editorial, collage, full-bleed
 * photo, Swiss, soft product, poster, question, centred, magazine, board) on content from a real kind
 * of business (assets/directions/content-packs.json) with open-collection photographs (assets/photos/).
 * The pairing lives in directions.json (comp, subject, photoFilter); --comp c1..c10 and
 * --subject <pack> override it to try a direction in another arrangement. Fonts load
 * from Google Fonts (network); offline, generic fallbacks are used and the previews say so.
 * --sheet also writes sheet.jpg: every preview as a labelled thumbnail grid.
 * Setup needs Playwright; nothing is downloaded (see render_check.js --doctor).
 */
const fs = require('fs');
const path = require('path');
const { findModule, findBrowser } = require('./_pw');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const has = k => args.includes(k);

const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'assets/directions/directions.json'), 'utf8')).directions;
const out = path.resolve(opt('--out', path.join(root, 'assets/directions/previews')));
const W = Number(opt('--width', '1440')), H = Number(opt('--height', '1240'));
let list = data;
if (opt('--ids')) { const ids = opt('--ids').split(','); list = data.filter(d => ids.includes(d.id)); }
if (opt('--group')) list = list.filter(d => d.group === opt('--group'));
if (!list.length) { console.error('no directions matched'); process.exit(2); }

const thai = has('--thai');
const comps = require('./compositions');
const packs = JSON.parse(fs.readFileSync(path.join(root, 'assets/directions/content-packs.json'), 'utf8')).packs;
const photoDir = path.join(root, 'assets/photos');
const photos = {};
if (fs.existsSync(photoDir)) for (const f of fs.readdirSync(photoDir)) if (/\.jpe?g$/i.test(f)) photos[f.replace(/\.jpe?g$/i, '')] = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(photoDir, f)).toString('base64');
// --brief "Headline|Sentence|Button" replaces the pack's headline, sentence and action with the user's copy
const withBrief = (p) => (brief[0] ? Object.assign({}, p, { h1: [brief[0], '', ''], sub: brief[1] || p.sub, cta: brief[2] || p.cta }) : p);
// shortlist: give directions that share a composition different ones, so the user compares layouts, not swatches
const ORDER = ['c5', 'c1', 'c2', 'c3', 'c8', 'c13', 'c12', 'c14', 'c4', 'c6', 'c9', 'c7', 'c10', 'c11'];
const compOf = {};
if (opt('--ids') && !opt('--comp') && !has('--same-comp')) {
  const used = new Set();
  for (const d of list) {
    let c = d.comp;
    if (used.has(c)) {
      const alt = ORDER.find(x => !used.has(x) && x !== d.comp);
      if (alt) { console.log(`${d.id} shares ${c} with an earlier pick; drawn in ${alt} so the shortlist differs in layout (--same-comp to keep ${c})`); c = alt; }
    }
    used.add(c); compOf[d.id] = c;
  }
}
const pageFor = (d) => comps.render(d, opt('--comp', compOf[d.id] || d.comp), withBrief(packs[opt('--subject', d.subject)] || packs.cafe), photos, { width: W, height: H, photoFilter: d.photoFilter, subject: opt('--subject', d.subject) });
const brief = (opt('--brief', '') || '').split('|');

(async () => {
  const mod = findModule(process.cwd());
  const exe = mod ? findBrowser(mod.chromium) : undefined;
  if (!mod || exe === undefined) { console.log('NOT RUN: no Playwright module or browser (npm i -D playwright && npx playwright install chromium)'); process.exit(3); }
  fs.mkdirSync(out, { recursive: true });
  const browser = await mod.chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  for (const d of list) {
    await page.setContent(pageFor(d), { waitUntil: 'load', timeout: 30000 }).catch(() => {});
    await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
    await page.waitForTimeout(900);
    const file = path.join(out, `${d.id}${thai ? '-th' : ''}.jpg`);
    await page.screenshot({ path: file, type: 'jpeg', quality: 82, clip: { x: 0, y: 0, width: W, height: H } });
    console.log(`${d.id}  ${d.group}  → ${file}`);
  }
  if (has('--sheet')) {
    const makeSheet = async (items, name) => {
      const cols = 4, tw = 480, th = Math.round(tw * H / W);
      const cells = items.map(d => `<figure style="margin:0"><img src="data:image/jpeg;base64,${fs.readFileSync(path.join(out, `${d.id}${thai ? '-th' : ''}.jpg`)).toString('base64')}" width="${tw}" height="${th}" style="display:block;border:1px solid #ccc"><figcaption style="font:600 16px system-ui;padding:6px 2px">${d.name} <span style="font-weight:400;color:#666">${d.group}</span></figcaption></figure>`).join('');
      await page.setViewportSize({ width: cols * (tw + 24) + 24, height: 400 });
      await page.setContent(`<body style="margin:0;padding:24px;background:#fff"><div style="display:grid;grid-template-columns:repeat(${cols},${tw}px);gap:20px 24px">${cells}</div></body>`, { waitUntil: 'load' });
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(out, `${name}${thai ? '-th' : ''}.jpg`), type: 'jpeg', quality: 78, fullPage: true });
      console.log(`${name} → ${path.join(out, name + '.jpg')}`);
    };
    await makeSheet(list, has('--group') ? `sheet-${opt('--group')}` : 'sheet');
    if (!has('--group') && !opt('--ids')) for (const g of [...new Set(list.map(d => d.group))]) await makeSheet(list.filter(d => d.group === g), `sheet-${g}`);
  }
  await browser.close();
})();
