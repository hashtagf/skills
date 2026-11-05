#!/usr/bin/env node
/*
 * Rebuild every preview image of the ux-ui-principles skill. The images are generated, not
 * committed (they are git-ignored); the data and generators are the source of truth.
 *
 * Usage:
 *   node scripts/build_previews.js [--only directions,site,backoffice,mobile,tablet,rtl,dark] [--thai]
 *
 * Runs, in order (needs Playwright; see render_check.js --doctor; fonts need network):
 *   directions   direction_preview.js --sheet            assets/directions/previews   (~1 min)
 *   site         site_preview.js --all --pages hero --sheet, then the default six directions for every
 *                page --sheet                            assets/site/previews         (~5 min)
 *   backoffice   backoffice_preview.js --sheet           assets/backoffice/previews   (~2 min)
 *   mobile       backoffice_preview.js --mobile --sheet --singles none                  (~1 min)
 *   tablet       backoffice_preview.js --width 820 --height 1366 (records, overview, approval, detail)
 *   rtl          backoffice_preview.js --rtl (layout mirroring)
 *   dark         site_preview.js --dark (derived dark themes of light directions)
 * Total about 10 minutes and 30 MB. Use --only to rebuild one set, or call a generator directly
 * with --ids / --pages / --styles / --screens for a few pictures.
 */
const { spawnSync } = require('child_process');
const path = require('path');
const args = process.argv.slice(2);
const only = (args.includes('--only') ? args[args.indexOf('--only') + 1] : 'directions,site,backoffice,mobile,tablet,rtl,dark').split(',');
const thai = args.includes('--thai') ? ['--thai'] : [];
const run = (script, a) => {
  console.log(`\n> node scripts/${script} ${a.join(' ')}`);
  const r = spawnSync('node', [path.join(__dirname, script), ...a], { stdio: 'inherit' });
  if (r.status === 3) { console.log('NOT RUN: no Playwright module or browser (npm i -D playwright && npx playwright install chromium)'); process.exit(3); }
  if (r.status) process.exit(r.status);
};
if (only.includes('directions')) run('direction_preview.js', ['--sheet', ...thai]);
if (only.includes('site')) { run('site_preview.js', ['--all', '--pages', 'hero', '--sheet', ...thai]); run('site_preview.js', ['--sheet', ...thai]); }
if (only.includes('backoffice')) run('backoffice_preview.js', ['--sheet', ...thai]);
if (only.includes('tablet')) run('backoffice_preview.js', ['--screens', 'records,overview,approval,detail', '--width', '820', '--height', '1366', '--sheet', '--out', 'assets/backoffice/previews/tablet', ...thai]);
if (only.includes('rtl')) run('backoffice_preview.js', ['--screens', 'records,overview,approval', '--rtl', '--sheet', '--out', 'assets/backoffice/previews/rtl']);
if (only.includes('dark')) run('site_preview.js', ['--all', '--dark', '--pages', 'home,pricing,service,product', '--sheet', '--out', 'assets/site/previews/dark', ...thai]);
if (only.includes('mobile')) run('backoffice_preview.js', ['--mobile', '--sheet', '--singles', 'none', ...thai]);
console.log('\nPreviews rebuilt.');
