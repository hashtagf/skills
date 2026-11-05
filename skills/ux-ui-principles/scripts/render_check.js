#!/usr/bin/env node
/*
 * Render a page at several widths and color schemes, report problems, save screenshots.
 *
 * Usage:
 *   node render_check.js <url-or-file> [--out dir] [--widths 1440,768,390] [--schemes light,dark]
 *                         [--zoom] [--fast] [--viewport-shots] [--reduced-motion] [--wait 800] [--timeout 30000]
 *                         [--toggle "<selector>"]
 *
 * The page is loaded once; widths and color schemes are switched in place
 * (viewport resize + prefers-color-scheme emulation), so each extra viewport
 * costs a relayout, not a reload. --fast = widths 1440,390, light only,
 * viewport-only screenshots. --viewport-shots skips full-page screenshots
 * (the slowest step on long pages).
 *
 * Reports per viewport: JS errors, console errors, failed requests, horizontal page
 * overflow (and the widest offending elements), elements wider than the viewport,
 * images without alt, buttons/links without an accessible name, form controls
 * without a label, form controls with different heights or misaligned rows,
 * invalid fields styled like valid ones, gaps before punctuation, and text
 * left at opacity 0 on the first screen. --reduced-motion emulates
 * prefers-reduced-motion and also reports animations still moving and any
 * content never revealed. Also reported: images that failed to load (lazy images
 * are forced eager first, so full-page shots are not blank), text touching the
 * viewport edge (no gutter), and h1/h2 wrapping to 3+ lines (a NOTE, not a failure).
 * --toggle "<selector>" clicks a language/theme switch after the first pass and
 * repeats every viewport (screenshots prefixed alt-), so both states are checked.
 * --zoom also renders at 320px width (approximates 400% zoom reflow
 * of a 1280px window). Exit code 1 when any problem is found.
 *
 * Setup is automatic and never downloads anything:
 *   - Playwright module: ./node_modules, the page's project, NODE_PATH, the global
 *     npm root, then playwright-core. Set PW_MODULE=/path/to/node_modules to force one.
 *   - Browser: PW_CHROMIUM, then Playwright's own build, then any cached
 *     chromium / headless shell build (any version), then installed Chrome / Edge.
 *   - A file without <!doctype>/<html> (a fragment) is wrapped in a doctype +
 *     viewport meta page next to the original, so relative assets still resolve.
 * --doctor prints what was found and exits. When no module or browser is found
 * the script exits 3 at once: report the render check as "not tested" and move
 * on; do not install browsers mid-task (`npx playwright install chromium` is a
 * one-time setup the user can run).
 * --timeout bounds the page load (no shell `timeout` needed; macOS lacks it).
 * This is a smoke check, not an accessibility audit: it does not test keyboard
 * flows, screen readers, contrast or task success.
 */
const path = require('path');
const fs = require('fs');
const os = require('os');
const args = process.argv.slice(2);
const doctor = args.includes('--doctor');
if (!doctor && (!args[0] || args[0].startsWith('--'))) { console.error('usage: node render_check.js <url-or-file> [--out dir] [--widths 1440,768,390] [--schemes light,dark] [--zoom] [--fast] [--viewport-shots] [--toggle selector] [--timeout ms] | --doctor'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };

const { findModule: findModuleFrom, findBrowser } = require('./_pw');
const findModule = () => findModuleFrom(args[0]);

const mod = findModule();
const exe = mod ? findBrowser(mod.chromium) : undefined;
if (doctor || !mod || exe === undefined) {
  console.log(`playwright module: ${mod ? mod.from : 'NOT FOUND'}`);
  console.log(`browser: ${exe === null ? "Playwright's bundled build" : exe || 'NOT FOUND'}`);
  if (!mod || exe === undefined) {
    console.log('NOT TESTED: render check skipped (no Playwright module or browser). One-time setup: npm i -D playwright && npx playwright install chromium');
    process.exit(3);
  }
  process.exit(0);
}
const chromium = mod.chromium;

let target = args[0];
if (!/^[a-z]+:\/\//i.test(target)) {
  const file = path.resolve(target);
  const head = fs.readFileSync(file, 'utf8').slice(0, 2000);
  if (!/<!doctype|<html[\s>]/i.test(head)) {
    const wrapped = path.join(path.dirname(file), `.render-check-${path.basename(file, path.extname(file))}.html`);
    fs.writeFileSync(wrapped, '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>\n' + fs.readFileSync(file, 'utf8') + '\n</body></html>');
    process.on('exit', () => { try { fs.unlinkSync(wrapped); } catch (e) {} });
    console.log(`note: ${path.basename(file)} is a fragment; rendered inside a doctype wrapper`);
    target = 'file://' + wrapped;
  } else target = 'file://' + file;
}
const out = opt('--out', 'render-check');
const fast = args.includes('--fast');
const widths = opt('--widths', fast ? '1440,390' : '1440,768,390').split(',').map(Number);
if (args.includes('--zoom')) widths.push(320);
const schemes = opt('--schemes', fast ? 'light' : 'light,dark').split(',');
const wait = Number(opt('--wait', '800'));
const timeout = Number(opt('--timeout', '30000'));
const fullPage = !(fast || args.includes('--viewport-shots'));

(async () => {
  fs.mkdirSync(out, { recursive: true });
  const launch = exe ? { executablePath: exe } : {};
  const browser = await chromium.launch(launch);
  const reduced = args.includes('--reduced-motion');
  const page = await browser.newPage({ viewport: { width: widths[0], height: 900 }, colorScheme: schemes[0], reducedMotion: reduced ? 'reduce' : 'no-preference' });
  const errs = [], cons = [], fails = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error') cons.push(m.text()); });
  page.on('requestfailed', r => fails.push(r.url()));
  try { await page.goto(target, { waitUntil: 'load', timeout }); }
  catch (e) { console.log(`WARN  load did not finish in ${timeout}ms; checking what rendered`); }
  await page.waitForTimeout(wait);
  await page.evaluate(async () => {
    document.querySelectorAll('img[loading=lazy]').forEach(i => { i.loading = 'eager'; });
    await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.addEventListener('load', r, { once: true }); i.addEventListener('error', r, { once: true }); setTimeout(r, 8000); })));
  });
  // Scroll through once so reveal-on-scroll content (IntersectionObserver) is shown in full-page shots.
  const reveal = async () => {
    await page.evaluate(async () => {
      const h = document.documentElement.scrollHeight, step = Math.max(300, innerHeight * 0.5);
      for (let y = 0; y < h; y += step) { scrollTo(0, y); await new Promise(r => setTimeout(r, 300)); }
      scrollTo(0, 0); await new Promise(r => setTimeout(r, 400));
    });
  };
  const settle = async () => { await reveal(); await page.evaluate(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))); };
  let problems = 0, reported = { errs: 0, cons: 0, fails: 0 };
  async function matrix(prefix) {
  for (const scheme of schemes) {
    await page.emulateMedia({ colorScheme: scheme });
    for (const w of widths) {
      await page.setViewportSize({ width: w, height: 900 });
      await settle();
      const r = await page.evaluate(() => {
        const vw = document.documentElement.clientWidth;
        const overflow = document.documentElement.scrollWidth > vw;
        let wide = [];
        if (overflow) {
          const clips = new Set();
          for (const p of document.querySelectorAll('body *')) {
            if (/(auto|scroll|hidden|clip)/.test(getComputedStyle(p).overflowX)) clips.add(p);
          }
          const inScroller = el => { for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) if (clips.has(p)) return true; return false; };
          for (const e of document.querySelectorAll('body *')) {
            const b = e.getBoundingClientRect();
            if (b.width && b.right > vw + 1 && !inScroller(e)) {
              wide.push(`${e.tagName.toLowerCase()}${e.id ? '#' + e.id : ''}${e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/).join('.') : ''} right=${Math.round(b.right)}`);
              if (wide.length >= 5) break;
            }
          }
        }
        const visible = e => { const b = e.getBoundingClientRect(); if (!b.width) return false; const s = getComputedStyle(e); return s.display !== 'none' && s.visibility !== 'hidden'; };
        const name = e => (e.getAttribute('aria-label') || e.getAttribute('title') || e.textContent || '').trim() || (e.getAttribute('aria-labelledby') ? 'x' : '');
        const noAlt = [...document.images].filter(i => !i.hasAttribute('alt') && visible(i)).length;
        const noName = [...document.querySelectorAll('button,a[href],[role=button]')].filter(e => !name(e) && !e.querySelector('img[alt]:not([alt=""])') && visible(e)).map(e => e.outerHTML.slice(0, 80));
        const noLabel = [...document.querySelectorAll('input:not([type=hidden]):not([type=submit]):not([type=button]),select,textarea')].filter(e => {
          if (e.getAttribute('aria-label') || e.getAttribute('aria-labelledby') || e.closest('label')) return false;
          if (e.id && document.querySelector(`label[for="${CSS.escape(e.id)}"]`)) return false; return visible(e);
        }).map(e => e.outerHTML.slice(0, 80));
        // Forms: control heights, row alignment, invalid styling
        const formIssues = [];
        for (const f of document.querySelectorAll('form')) {
          const ctrls = [...f.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]):not([type=submit]):not([type=button]),select')].filter(visible);
          const hs = [...new Set(ctrls.map(c => Math.round(c.getBoundingClientRect().height)))];
          if (hs.length > 1 && Math.max(...hs) - Math.min(...hs) > 2) formIssues.push(`single-line controls have different heights: ${hs.join('/')}px`);
          const rects = ctrls.map(c => [c, c.getBoundingClientRect()]);
          for (let i = 0; i < rects.length; i++) for (let j = i + 1; j < rects.length; j++) {
            const [a, ra] = rects[i], [b, rb] = rects[j];
            const sameRow = ra.right <= rb.left + 1 || rb.right <= ra.left + 1 ? Math.min(ra.bottom, rb.bottom) - Math.max(ra.top, rb.top) > -40 : false;
            if (sameRow && Math.abs(ra.top - rb.top) > 2) formIssues.push(`fields in one row not top-aligned: ${a.name || a.id} vs ${b.name || b.id} (${Math.round(Math.abs(ra.top - rb.top))}px)`);
          }
          for (const c of f.querySelectorAll('[aria-invalid="true"]')) {
            const sib = [...f.querySelectorAll('input,select,textarea')].find(x => x !== c && x.getAttribute('aria-invalid') !== 'true' && visible(x));
            if (sib && getComputedStyle(c).borderTopColor === getComputedStyle(sib).borderTopColor) formIssues.push(`invalid field ${c.name || c.id} has the same border as valid fields`);
          }
        }
        // Gap before punctuation: real spaces, or glyph gaps from font fallback / letter-spacing
        const punct = [];
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        let tn, seen = 0;
        while ((tn = walker.nextNode()) && seen < 400) {
          const t = tn.nodeValue; if (!t || !/[.,:;!?]/.test(t) || !tn.parentElement || !visible(tn.parentElement)) continue;
          seen++;
          const m1 = t.match(/[A-Za-z0-9฀-๿)]\s+[.,:;!?](?=\s|$)/);
          if (m1) { punct.push(`space before "${m1[0].trim().slice(-1)}": "${t.trim().slice(0, 40)}"`); continue; }
          const re = /[A-Za-z0-9][.,:;](?=\s|$)/g; let m;
          while ((m = re.exec(t))) {
            // A period/comma/colon normally advances ~0.25-0.3em; much wider means
            // letter-spacing or a fallback font with wide punctuation (reads as "word .")
            const r = document.createRange(); r.setStart(tn, m.index + 1); r.setEnd(tn, m.index + 2);
            const w = r.getBoundingClientRect().width; const fs = parseFloat(getComputedStyle(tn.parentElement).fontSize) || 16;
            if (w > fs * 0.45) { punct.push(`wide "${t[m.index + 1]}" glyph (${(w / fs).toFixed(2)}em; letter-spacing or fallback font?): "${t.trim().slice(0, 40)}"`); break; }
          }
          if (punct.length >= 3) break;
        }
        // Motion: content left invisible after load; movement under reduced motion
        const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
        const hidden = [];
        for (const e of document.querySelectorAll('body *')) {
          if (hidden.length >= 3) break;
          if (e.closest('[aria-hidden="true"],[hidden],dialog:not([open])')) continue;
          const st = getComputedStyle(e); if (st.opacity !== '0' || st.display === 'none') continue;
          const b = e.getBoundingClientRect(); if (!b.width || !b.height) continue;
          if (!reduce && b.top > innerHeight) continue; // below the fold may reveal on scroll
          if ((e.innerText || '').trim().length > 2) hidden.push(`${e.tagName.toLowerCase()}${e.className && typeof e.className === 'string' ? '.' + e.className.trim().split(/\s+/)[0] : ''} "${e.innerText.trim().slice(0, 30)}"`);
        }
        const moving = reduce ? document.getAnimations().filter(a => a.playState === 'running' && a.effect && a.effect.getKeyframes()
          .some(k => k.transform || k.translate || k.scale || k.rotate || k.left || k.top || k.backgroundPosition)).length : 0;
        // Phone composition (<= 480px)
        const mobile = [];
        if (vw <= 480) {
          const small = [...document.querySelectorAll('a[href],button,[role=button],input:not([type=hidden]),select,summary')]
            .filter(visible).filter(e => { const r = e.getBoundingClientRect(); const inText = e.tagName === 'A' && e.closest('p,li') && getComputedStyle(e).display === 'inline'; return !inText && (r.height < 44 || r.width < 44); });
          if (small.length) mobile.push(`${small.length} tap target(s) under 44px (project default; WCAG floor is 24px), e.g. ${small.slice(0, 3).map(e => `${e.tagName.toLowerCase()} "${(e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 15)}" ${Math.round(e.getBoundingClientRect().width)}x${Math.round(e.getBoundingClientRect().height)}`).join(', ')}`);
          const zoomy = [...document.querySelectorAll('input:not([type=hidden]):not([type=checkbox]):not([type=radio]),select,textarea')].filter(visible).filter(e => parseFloat(getComputedStyle(e).fontSize) < 16);
          if (zoomy.length) mobile.push(`${zoomy.length} field(s) with font-size < 16px (iOS zooms on focus)`);
          const tiny = [...document.querySelectorAll('p,li,td,dd')].filter(visible).filter(e => (e.innerText || '').trim().length > 40 && parseFloat(getComputedStyle(e).fontSize) < 14);
          if (tiny.length) mobile.push(`${tiny.length} text block(s) under 14px`);
          const stuck = [...document.querySelectorAll('body *')].filter(e => /fixed|sticky/.test(getComputedStyle(e).position) && visible(e) && e.getBoundingClientRect().height > 30);
          if (stuck.length > 1) mobile.push(`${stuck.length} fixed/sticky elements; keep one`);
        }
        // Images that failed to load (blank slot), text with no gutter, 3+ line headings
        const broken = [...document.images].filter(i => (visible(i) || i.parentElement && visible(i.parentElement)) && i.complete && !i.naturalWidth).map(i => (i.currentSrc || i.src).split('/').pop().slice(0, 40));
        const edge = [];
        for (const e of document.querySelectorAll('h1,h2,h3,h4,p,li,a,button,label,summary,figcaption,dt,dd')) {
          if (edge.length >= 3) break;
          if (e.closest('[aria-hidden="true"],[hidden]') || !visible(e)) continue;
          const own = [...e.childNodes].some(n => n.nodeType === 3 && n.nodeValue.trim().length > 1);
          if (!own) continue;
          const b = e.getBoundingClientRect();
          if (b.right < 0 || b.left > vw) continue; // off-screen (skip links)
          if (b.left < 6 || b.right > vw - 6) edge.push(`${e.tagName.toLowerCase()} "${e.innerText.trim().slice(0, 24)}" left=${Math.round(b.left)} right=${Math.round(vw - b.right)}`);
        }
        const notes = [];
        for (const h of document.querySelectorAll('h1,h2')) {
          if (!visible(h) || h.closest('[aria-hidden="true"]')) continue;
          const cs = getComputedStyle(h); const fs = parseFloat(cs.fontSize);
          const lh = parseFloat(cs.lineHeight) || fs * 1.2;
          const lines = Math.round(h.getBoundingClientRect().height / lh);
          if (lines > 2) notes.push(`${h.tagName.toLowerCase()} wraps to ${lines} lines: "${h.innerText.trim().slice(0, 36)}"`);
        }
        return { overflow, wide, noAlt, noName, noLabel, formIssues: [...new Set(formIssues)], punct, hidden, moving, reduce, mobile, broken, edge, notes, lang: document.documentElement.lang };
      });
      const file = path.join(out, `${prefix}${scheme}-${w}.png`);
      await page.screenshot({ path: file, fullPage });
      const issues = [];
      const fresh = (arr, k) => { const n = arr.slice(reported[k]); reported[k] = arr.length; return n; };
      const e1 = fresh(errs, 'errs'), c1 = fresh(cons, 'cons'), f1 = fresh(fails, 'fails');
      if (e1.length) issues.push(`JS errors: ${e1.slice(0, 3).join(' | ')}`);
      if (c1.length) issues.push(`console errors: ${c1.slice(0, 3).join(' | ')}`);
      if (f1.length) issues.push(`failed requests: ${f1.slice(0, 3).join(' | ')}`);
      if (r.overflow) issues.push(`horizontal page overflow; widest: ${r.wide.join(', ') || 'unknown'}`);
      if (r.noAlt) issues.push(`${r.noAlt} visible image(s) without alt`);
      if (r.noName.length) issues.push(`unnamed controls: ${r.noName.slice(0, 3).join(' | ')}`);
      if (r.noLabel.length) issues.push(`unlabeled fields: ${r.noLabel.slice(0, 3).join(' | ')}`);
      r.formIssues.slice(0, 4).forEach(x => issues.push(`form: ${x}`));
      r.punct.forEach(x => issues.push(`text: ${x}`));
      if (r.hidden.length) issues.push(`content invisible after load (opacity 0${r.reduce ? ', reduced motion' : ', first screen'}): ${r.hidden.join(' | ')}`);
      r.mobile.forEach(x => issues.push(`phone: ${x}`));
      if (r.broken.length) issues.push(`image(s) failed to load: ${[...new Set(r.broken)].slice(0, 3).join(', ')}`);
      if (r.edge.length) issues.push(`text touches the viewport edge (no gutter): ${r.edge.join(' | ')}`);
      if (r.moving) issues.push(`${r.moving} animation(s) still moving under prefers-reduced-motion`);
      problems += issues.length;
      console.log(`${issues.length ? 'FAIL' : 'PASS'}  ${prefix}${scheme} ${w}px${r.lang ? ' [' + r.lang + ']' : ''}  → ${file}`);
      issues.forEach(i => console.log('   - ' + i));
      r.notes.forEach(i => console.log('   · note: ' + i));
    }
  }
  }
  await matrix('');
  const toggle = opt('--toggle', '');
  if (toggle) {
    try { await page.click(toggle, { timeout: 5000 }); await page.waitForTimeout(wait); }
    catch (e) { console.log(`WARN  --toggle ${toggle} could not be clicked: ${e.message.split('\n')[0]}`); }
    await matrix('alt-');
  }
  await browser.close();
  console.log(problems ? `\n${problems} problem(s). Look at the screenshots too: overlap, clipping and hierarchy need human review.` : '\nNo automated problems. Review the screenshots for overlap, clipping and hierarchy.');
  process.exit(problems ? 1 : 0);
})();
