#!/usr/bin/env node
/*
 * Click through a page's main task from a JSON list of steps and check each result.
 *
 * Usage:
 *   node flow_check.js <url-or-file> <steps.json> [--width 1440] [--height 900] [--wait 600]
 *
 * steps.json is an array. Action steps: {"do": "click"|"fill"|"check"|"uncheck"|"select"|"press"|"wait", "sel": "...", "value": "..."}
 *   click  sel may be a CSS selector or "text=..." (Playwright text selector); falls back to a forced click
 *          when an invisible input covers the target (visually hidden radios with a label overlay)
 *   fill / select  value is the text or option value; press  value is a key ("Escape"), sel optional
 *   wait   value is milliseconds
 * Expect steps: {"expect": "text"|"visible"|"hidden"|"disabled"|"enabled"|"attr", "sel": "...", "value": "...", "attr": "..."}
 *   text   substring of the element's text (whitespace collapsed); attr  attribute `attr` equals `value`
 *
 * Example for the coffee-shop bean picker:
 * [
 *   {"do": "click", "sel": "#b2"},
 *   {"do": "click", "sel": "text=500 g"},
 *   {"do": "click", "sel": "#add"},
 *   {"expect": "text", "sel": "#bagCount", "value": "1"},
 *   {"expect": "text", "sel": "#status", "value": "ใส่"}
 * ]
 *
 * Prints PASS/FAIL per step, then any page errors and console errors. Exit 1 on any failure or error,
 * 3 when no browser is available (report "not tested").
 */
const path = require('path');
const fs = require('fs');
const args = process.argv.slice(2);
if (args.length < 2 || args[0].startsWith('--')) { console.error('usage: node flow_check.js <url-or-file> <steps.json> [--width 1440] [--height 900]'); process.exit(2); }
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const { findModule, findBrowser } = require('./_pw');
const mod = findModule(args[0]);
const exe = mod ? findBrowser(mod.chromium) : undefined;
if (!mod || exe === undefined) { console.log('NOT TESTED: flow check skipped (no Playwright module or browser).'); process.exit(3); }
const target = /^[a-z]+:\/\//i.test(args[0]) ? args[0] : 'file://' + path.resolve(args[0]);
const steps = JSON.parse(fs.readFileSync(args[1], 'utf8'));

(async () => {
  const browser = await mod.chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage({ viewport: { width: Number(opt('--width', '1440')), height: Number(opt('--height', '900')) } });
  const errs = [], cons = [];
  page.on('pageerror', e => errs.push(e.message));
  page.on('console', m => { if (m.type() === 'error') cons.push(m.text()); });
  await page.goto(target, { waitUntil: 'load' });
  await page.waitForTimeout(Number(opt('--wait', '600')));
  let failed = 0;
  const T = { timeout: 5000 };
  const norm = s => (s || '').replace(/\s+/g, ' ').trim();
  for (const [i, s] of steps.entries()) {
    const label = `${String(i + 1).padStart(2)} ${s.do ? s.do : 'expect ' + s.expect} ${s.sel || ''}${s.value != null ? ' ' + JSON.stringify(s.value) : ''}`;
    try {
      if (s.do === 'click') {
        try { await page.click(s.sel, { timeout: 2500 }); }
        catch (e) { if (/intercepts pointer events|not visible|Timeout/i.test(e.message)) await page.click(s.sel, { force: true, timeout: 2500 }); else throw e; }
      } else if (s.do === 'fill') await page.fill(s.sel, String(s.value), T);
      else if (s.do === 'check') await page.check(s.sel, { ...T, force: true });
      else if (s.do === 'uncheck') await page.uncheck(s.sel, { ...T, force: true });
      else if (s.do === 'select') await page.selectOption(s.sel, String(s.value), T);
      else if (s.do === 'press') { if (s.sel) await page.press(s.sel, s.value, T); else await page.keyboard.press(s.value); }
      else if (s.do === 'wait') await page.waitForTimeout(Number(s.value || 300));
      else if (s.expect === 'text') {
        const got = norm(await page.textContent(s.sel, T));
        if (!got.includes(norm(String(s.value)))) throw new Error(`text is "${got.slice(0, 80)}"`);
      } else if (s.expect === 'visible') { if (!(await page.isVisible(s.sel))) throw new Error('not visible'); }
      else if (s.expect === 'hidden') { if (!(await page.isHidden(s.sel))) throw new Error('visible'); }
      else if (s.expect === 'disabled') { if (!(await page.isDisabled(s.sel, T))) throw new Error('enabled'); }
      else if (s.expect === 'enabled') { if (!(await page.isEnabled(s.sel, T))) throw new Error('disabled'); }
      else if (s.expect === 'attr') { const v = await page.getAttribute(s.sel, s.attr, T); if (v !== String(s.value)) throw new Error(`${s.attr}="${v}"`); }
      else throw new Error('unknown step');
      if (s.do && s.do !== 'wait') await page.waitForTimeout(120);
      console.log(`PASS  ${label}`);
    } catch (e) {
      failed++;
      console.log(`FAIL  ${label}  → ${e.message.split('\n')[0].slice(0, 140)}`);
    }
  }
  if (errs.length) console.log(`FAIL  page errors: ${errs.slice(0, 3).join(' | ')}`);
  if (cons.length) console.log(`FAIL  console errors: ${cons.slice(0, 3).join(' | ')}`);
  await browser.close();
  const bad = failed + (errs.length ? 1 : 0) + (cons.length ? 1 : 0);
  console.log(bad ? `\n${bad} failure(s).` : `\nAll ${steps.length} steps passed.`);
  process.exit(bad ? 1 : 0);
})();
