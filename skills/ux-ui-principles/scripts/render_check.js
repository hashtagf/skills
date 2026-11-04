#!/usr/bin/env node
/*
 * Render a page at several widths and color schemes, report problems, save screenshots.
 *
 * Usage:
 *   node render_check.js <url-or-file> [--out dir] [--widths 1440,768,390] [--schemes light,dark]
 *                         [--zoom] [--wait 800]
 *
 * Reports per viewport: JS errors, console errors, failed requests, horizontal page
 * overflow (and the widest offending elements), elements wider than the viewport,
 * images without alt, buttons/links without an accessible name, form controls
 * without a label. --zoom also renders at 320px width (approximates 400% zoom reflow
 * of a 1280px window). Exit code 1 when any problem is found.
 *
 * Requires Playwright (`npm i -D playwright` or a preinstalled copy). Set
 * PW_CHROMIUM=/path/to/chromium to use a specific browser binary.
 * This is a smoke check, not an accessibility audit: it does not test keyboard
 * flows, screen readers, contrast or task success.
 */
const path = require('path');
let chromium;
try { ({ chromium } = require('playwright')); } catch (e) {
  console.error('Playwright not found. Install with: npm i -D playwright'); process.exit(2);
}
const args = process.argv.slice(2);
if (!args[0] || args[0].startsWith('--')) { console.error('usage: node render_check.js <url-or-file> [--out dir] [--widths 1440,768,390] [--schemes light,dark] [--zoom]'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
let target = args[0];
if (!/^[a-z]+:\/\//i.test(target)) target = 'file://' + path.resolve(target);
const out = opt('--out', 'render-check');
const widths = opt('--widths', '1440,768,390').split(',').map(Number);
if (args.includes('--zoom')) widths.push(320);
const schemes = opt('--schemes', 'light,dark').split(',');
const wait = Number(opt('--wait', '800'));

(async () => {
  require('fs').mkdirSync(out, { recursive: true });
  const launch = process.env.PW_CHROMIUM ? { executablePath: process.env.PW_CHROMIUM } : {};
  const browser = await chromium.launch(launch);
  let problems = 0;
  for (const scheme of schemes) for (const w of widths) {
    const page = await browser.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme });
    const errs = [], cons = [], fails = [];
    page.on('pageerror', e => errs.push(e.message));
    page.on('console', m => { if (m.type() === 'error') cons.push(m.text()); });
    page.on('requestfailed', r => fails.push(r.url()));
    await page.goto(target, { waitUntil: 'load' });
    await page.waitForTimeout(wait);
    const r = await page.evaluate(() => {
      const vw = document.documentElement.clientWidth;
      const overflow = document.documentElement.scrollWidth > vw;
      const inScroller = el => { for (let p = el.parentElement; p; p = p.parentElement) { const s = getComputedStyle(p); if (/(auto|scroll|hidden)/.test(s.overflowX) && p !== document.body && p !== document.documentElement) return true; } return false; };
      const wide = [...document.querySelectorAll('body *')].filter(e => { const b = e.getBoundingClientRect(); return b.width && b.right > vw + 1 && !inScroller(e); })
        .slice(0, 5).map(e => `${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}${e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : ''} right=${Math.round(e.getBoundingClientRect().right)}`);
      const visible = e => { const s = getComputedStyle(e); const b = e.getBoundingClientRect(); return s.display !== 'none' && s.visibility !== 'hidden' && b.width > 0; };
      const name = e => (e.getAttribute('aria-label') || e.getAttribute('title') || e.textContent || '').trim() || (e.getAttribute('aria-labelledby') ? 'x' : '');
      const noAlt = [...document.images].filter(i => !i.hasAttribute('alt') && visible(i)).length;
      const noName = [...document.querySelectorAll('button,a[href],[role=button]')].filter(e => visible(e) && !name(e) && !e.querySelector('img[alt]:not([alt=""])')).map(e => e.outerHTML.slice(0, 80));
      const noLabel = [...document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]),select,textarea')].filter(e => {
        if (!visible(e)) return false; if (e.getAttribute('aria-label') || e.getAttribute('aria-labelledby')) return false;
        if (e.id && document.querySelector(`label[for="${CSS.escape(e.id)}"]`)) return false; return !e.closest('label');
      }).map(e => e.outerHTML.slice(0, 80));
      return { overflow, wide, noAlt, noName, noLabel };
    });
    const file = path.join(out, `${scheme}-${w}.png`);
    await page.screenshot({ path: file, fullPage: true });
    const issues = [];
    if (errs.length) issues.push(`JS errors: ${errs.join(' | ')}`);
    if (cons.length) issues.push(`console errors: ${cons.slice(0, 3).join(' | ')}`);
    if (fails.length) issues.push(`failed requests: ${fails.slice(0, 3).join(' | ')}`);
    if (r.overflow) issues.push(`horizontal page overflow; widest: ${r.wide.join(', ') || 'unknown'}`);
    if (r.noAlt) issues.push(`${r.noAlt} visible image(s) without alt`);
    if (r.noName.length) issues.push(`unnamed controls: ${r.noName.slice(0, 3).join(' | ')}`);
    if (r.noLabel.length) issues.push(`unlabeled fields: ${r.noLabel.slice(0, 3).join(' | ')}`);
    problems += issues.length;
    console.log(`${issues.length ? 'FAIL' : 'PASS'}  ${scheme} ${w}px  → ${file}`);
    issues.forEach(i => console.log('   - ' + i));
    await page.close();
  }
  await browser.close();
  console.log(problems ? `\n${problems} problem(s). Look at the screenshots too: overlap, clipping and hierarchy need human review.` : '\nNo automated problems. Review the screenshots for overlap, clipping and hierarchy.');
  process.exit(problems ? 1 : 0);
})();
