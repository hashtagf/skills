#!/usr/bin/env node
/*
 * Screenshot the sites of a market study (assets/market/catalog.json) so you can look at the category
 * before choosing a direction (references/design-direction.md §9, Round B "research the market first").
 *
 * Usage:
 *   node scripts/market_fetch.js --kind clinic                 # (re)shoot every site listed for that kind
 *   node scripts/market_fetch.js --kind spa --urls urls.txt    # new study: one "slug url TH|intl" per line
 *   options: [--out assets/market/img] [--width 1440] [--height 900] [--only slug1,slug2]
 *
 * Writes <out>/<kind>-<slug>-1.jpg (first screen) and -2.jpg (scrolled one screen), JPEG quality 70.
 * The pictures are other businesses' pages: they stay local (git-ignored) as a study set and never go into
 * client work. A new study prints a catalog stub to fill in (category_look, designed_moves, gaps, facts,
 * a note and verdict per site) after you have looked at every picture.
 * Setup needs Playwright (see render_check.js --doctor); nothing is downloaded.
 */
const fs = require('fs');
const path = require('path');
const { findModule, findBrowser } = require('./_pw');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };

const root = path.resolve(__dirname, '..');
const kind = opt('--kind');
if (!kind) { console.error('usage: node scripts/market_fetch.js --kind <kind> [--urls file]'); process.exit(2); }
const out = path.resolve(opt('--out', path.join(root, 'assets/market/img')));
const W = Number(opt('--width', '1440')), H = Number(opt('--height', '900'));
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'assets/market/catalog.json'), 'utf8'));

let sites;
if (opt('--urls')) {
  sites = fs.readFileSync(opt('--urls'), 'utf8').split('\n').map(l => l.trim()).filter(l => l && !l.startsWith('#'))
    .map(l => { const [slug, url, region] = l.split(/\s+/); return { slug, url, region: region || '?' }; });
} else {
  const k = catalog.kinds[kind];
  if (!k) { console.error(`no study for '${kind}' in assets/market/catalog.json; pass --urls to start one. Studies: ${Object.keys(catalog.kinds).join(', ')}`); process.exit(2); }
  sites = k.sites;
}
if (opt('--only')) { const only = opt('--only').split(','); sites = sites.filter(s => only.includes(s.slug)); }

(async () => {
  const mod = findModule(process.cwd());
  const exe = mod ? findBrowser(mod.chromium) : undefined;
  if (!mod || exe === undefined) { console.log('NOT RUN: no Playwright module or browser (npm i -D playwright && npx playwright install chromium)'); process.exit(3); }
  fs.mkdirSync(out, { recursive: true });
  const browser = await mod.chromium.launch(exe ? { executablePath: exe } : {});
  const ok = [], failed = [];
  for (const s of sites) {
    const page = await browser.newPage({ viewport: { width: W, height: H }, locale: s.region === 'TH' ? 'th-TH' : 'en-US' });
    let done = false;
    for (let attempt = 0; attempt < 2 && !done; attempt++) {
      try {
        await page.goto(s.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
        await page.waitForTimeout(3500);
        // dismiss the most common cookie banners; harmless when absent
        for (const label of ['Accept', 'Accept all', 'Allow', 'I agree', 'OK', 'ยอมรับ', 'ยอมรับทั้งหมด', 'ตกลง']) {
          const b = page.getByRole('button', { name: label, exact: true }).first();
          if (await b.isVisible().catch(() => false)) { await b.click().catch(() => {}); await page.waitForTimeout(500); break; }
        }
        const base = path.join(out, `${kind}-${s.slug}`);
        await page.screenshot({ path: base + '-1.jpg', type: 'jpeg', quality: 70 });
        await page.evaluate(h => window.scrollTo(0, h), H);
        await page.waitForTimeout(1200);
        await page.screenshot({ path: base + '-2.jpg', type: 'jpeg', quality: 70 });
        ok.push(s); done = true;
        console.log(`ok    ${s.slug}  → ${base}-1.jpg`);
      } catch (e) {
        if (attempt === 1) { failed.push(s); console.log(`skip  ${s.slug}  ${String(e.message).split('\n')[0]}`); }
      }
    }
    await page.close();
  }
  await browser.close();
  console.log(`\n${ok.length} shot, ${failed.length} skipped. Open every -1 and -2 picture before writing the study.`);
  if (opt('--urls')) {
    const stub = { synonyms: [kind], studied: new Date().toISOString().slice(0, 10), category_look: '', designed_moves: '', gaps: ['', '', ''], facts: [],
      sites: ok.map(s => ({ slug: s.slug, url: s.url, region: s.region, verdict: 'category | designed', note: '' })) };
    console.log(`\nAdd to assets/market/catalog.json under kinds.${kind} after looking:\n` + JSON.stringify(stub, null, 2));
  }
})();
