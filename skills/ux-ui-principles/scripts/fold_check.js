#!/usr/bin/env node
/*
 * First-screen check for public pages: is the primary action above the fold, is the next
 * section hinted, is the offer (a price or the --offer element) on the first screen?
 *
 * Usage:
 *   node fold_check.js <url-or-file> [--cta ".selector"] [--offer ".selector"] [--next ".selector"]
 *                      [--sizes 1440x900,390x844] [--out dir] [--wait 800]
 *
 * Defaults: --cta is the first a.btn-primary / button.btn-primary / [data-cta] inside the first
 * <section>, <header> or the first child of <main>; --next is the first heading of the second <section>.
 * Per size: FAIL when the CTA's bottom edge is below the fold; NOTE when nothing of the next section
 * shows and the hero does not end at least 24px above the fold; NOTE when no offer is visible.
 * Screenshots: <out>/fold-<width>.png (default out: render-check next to a local page).
 * Exit 1 on any FAIL, 3 when no browser is available (report "not tested").
 */
const path = require('path');
const fs = require('fs');
const args = process.argv.slice(2);
if (!args[0] || args[0].startsWith('--')) { console.error('usage: node fold_check.js <url-or-file> [--cta sel] [--offer sel] [--next sel] [--sizes 1440x900,390x844] [--out dir]'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const { findModule, findBrowser } = require('./_pw');
const mod = findModule(args[0]);
const exe = mod ? findBrowser(mod.chromium) : undefined;
if (!mod || exe === undefined) { console.log('NOT TESTED: fold check skipped (no Playwright module or browser).'); process.exit(3); }

const isUrl = /^[a-z]+:\/\//i.test(args[0]);
const target = isUrl ? args[0] : 'file://' + path.resolve(args[0]);
const out = opt('--out', isUrl ? 'render-check' : path.join(path.dirname(path.resolve(args[0])), 'render-check'));
const sizes = opt('--sizes', '1440x900,390x844').split(',').map(s => s.split('x').map(Number));
const wait = Number(opt('--wait', '800'));
const sel = { cta: opt('--cta', ''), offer: opt('--offer', ''), next: opt('--next', '') };

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const browser = await mod.chromium.launch(exe ? { executablePath: exe } : {});
  let fails = 0;
  for (const [w, h] of sizes) {
    const page = await browser.newPage({ viewport: { width: w, height: h } });
    await page.goto(target, { waitUntil: 'load' });
    await page.waitForTimeout(wait);
    await page.evaluate(() => new Promise(r => { scrollTo({ top: 0, behavior: 'instant' }); requestAnimationFrame(() => requestAnimationFrame(r)); }));
    const r = await page.evaluate(sel => {
      const vis = e => { if (!e) return false; const b = e.getBoundingClientRect(), s = getComputedStyle(e); return b.width > 0 && b.height > 0 && s.display !== 'none' && s.visibility !== 'hidden'; };
      const sections = [...document.querySelectorAll('main section, body > section, section')];
      const hero = sections[0] || document.querySelector('header') || document.querySelector('main > *');
      let cta = sel.cta ? document.querySelector(sel.cta) : null;
      if (!cta) {
        const scopes = [document.querySelector('main section'), document.querySelector('section'), document.querySelector('header'), document.querySelector('main > *')].filter(Boolean);
        for (const s of scopes) { cta = [...s.querySelectorAll('a.btn-primary, button.btn-primary, [data-cta]')].find(vis); if (cta) break; }
      }
      let next = sel.next ? document.querySelector(sel.next) : null;
      if (!next) { const s2 = sections.find(s => s !== hero && !hero?.contains(s) && s.getBoundingClientRect().top >= (hero ? hero.getBoundingClientRect().bottom - 1 : 0)); next = s2 && (s2.querySelector('h1,h2,h3') || s2); }
      const fold = innerHeight;
      const ctaBox = cta && vis(cta) ? cta.getBoundingClientRect() : null;
      const heroBottom = hero ? hero.getBoundingClientRect().bottom : null;
      const nextTop = next ? next.getBoundingClientRect().top : null;
      let offer = null;
      if (sel.offer) { const o = document.querySelector(sel.offer); offer = o && vis(o) && o.getBoundingClientRect().top < fold ? o.innerText.trim().slice(0, 50) : null; }
      else {
        const re = /฿\s?\d|\$\s?\d|\d[\d,.]*\s?(บาท|THB)/;
        const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n;
        while ((n = tw.nextNode())) {
          if (!re.test(n.parentElement?.innerText || '') || !vis(n.parentElement)) continue;
          const rg = document.createRange(); rg.selectNodeContents(n); const b = rg.getBoundingClientRect();
          if (b.height && b.top >= 0 && b.bottom <= fold) { offer = (n.parentElement.closest('p,li,div,span') || n.parentElement).innerText.trim().slice(0, 50); break; }
        }
      }
      return { fold, cta: cta ? (cta.innerText || cta.getAttribute('aria-label') || '').trim().slice(0, 30) : null, ctaBottom: ctaBox ? Math.round(ctaBox.bottom) : null, heroBottom: heroBottom == null ? null : Math.round(heroBottom), nextTop: nextTop == null ? null : Math.round(nextTop), offer };
    }, sel);
    const file = path.join(out, `fold-${w}.png`);
    await page.screenshot({ path: file });
    const lines = [];
    let fail = false;
    if (r.ctaBottom == null) { fail = true; lines.push(`- no primary CTA found${sel.cta ? ` for ${sel.cta}` : ' (pass --cta)'}`); }
    else if (r.ctaBottom > r.fold) { fail = true; lines.push(`- CTA "${r.cta}" ends at ${r.ctaBottom}px, below the ${r.fold}px fold`); }
    else lines.push(`  CTA "${r.cta}" ends at ${r.ctaBottom}px of ${r.fold}px`);
    const hinted = (r.nextTop != null && r.nextTop < r.fold) || (r.heroBottom != null && r.heroBottom <= r.fold - 24);
    lines.push(hinted ? `  next section hinted (hero ends ${r.heroBottom}px, next heading at ${r.nextTop}px)` : `· note: next section not hinted: hero ends ${r.heroBottom}px, next heading at ${r.nextTop}px`);
    lines.push(r.offer ? `  offer on first screen: "${r.offer}"` : '· note: no offer or price on the first screen' + (sel.offer ? ` (${sel.offer})` : ''));
    if (fail) fails++;
    console.log(`${fail ? 'FAIL' : 'PASS'}  ${w}x${h}  → ${file}`);
    lines.forEach(l => console.log('   ' + l));
    await page.close();
  }
  await browser.close();
  process.exit(fails ? 1 : 0);
})();
