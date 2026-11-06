#!/usr/bin/env node
/*
 * Rebuild every preview image of the ux-ui-principles skill. The images are generated, not
 * committed (they are git-ignored); the data and generators are the source of truth.
 *
 * Usage:
 *   node scripts/build_previews.js [--only directions,brand,backoffice,mobile,tablet,rtl] [--thai] [-h|--help]
 *
 * Runs, in order (needs Playwright; see render_check.js --doctor; fonts need network):
 *   directions   direction_preview.js --sheet            assets/directions/previews   (~2 min; each direction in its
 *                composition on a subject's content with photographs)
 *   brand        backoffice_preview.js --direction all   assets/directions/previews/product (~3 min; the same
 *                directions as product UI: one token set for public pages and admin)
 *   backoffice   backoffice_preview.js --sheet           assets/backoffice/previews   (~2 min)
 *   mobile       backoffice_preview.js --mobile --sheet --singles none                  (~1 min)
 *   tablet       backoffice_preview.js --width 820 --height 1366 (records, overview, approval, detail)
 *   rtl          backoffice_preview.js --rtl (layout mirroring)
 * Total about 10 minutes and 30 MB. Use --only to rebuild one set, or call a generator directly
 * with --ids / --pages / --styles / --screens for a few pictures (direction_preview.js with --ids/--subject/
 * --comp/--brief writes to a temp folder or --out, never over these library pictures).
 */
const { spawnSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const args = process.argv.slice(2);
if (args.includes('-h') || args.includes('--help')) {
  const m = fs.readFileSync(__filename, 'utf8').match(/\/\*([\s\S]*?)\*\//);
  console.log(m ? m[1].split('\n').map(l => l.replace(/^ \* ?/, '').replace(/^ \*$/, '')).join('\n').trim() : '');
  process.exit(0);
}
const SETS = ['directions', 'brand', 'backoffice', 'mobile', 'tablet', 'rtl'];
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--only') { i++; continue; }
  if (args[i] !== '--thai') { console.error(`unknown argument ${JSON.stringify(args[i])} (see --help)`); process.exit(2); }
}
const only = (args.includes('--only') ? (args[args.indexOf('--only') + 1] || '') : 'directions,brand,backoffice,mobile,tablet,rtl').split(',');
const badSet = only.filter(x => !SETS.includes(x));
if (badSet.length) { console.error(`unknown --only ${badSet.join(',')}; choose from ${SETS.join(',')}`); process.exit(2); }
const thai = args.includes('--thai') ? ['--thai'] : [];
const run = (script, a) => {
  console.log(`\n> node scripts/${script} ${a.join(' ')}`);
  const r = spawnSync('node', [path.join(__dirname, script), ...a], { stdio: 'inherit' });
  if (r.status === 3) { console.log('NOT RUN: no Playwright module or browser (npm i -D playwright && npx playwright install chromium)'); process.exit(3); }
  if (r.status) process.exit(r.status);
};
if (only.includes('directions')) run('direction_preview.js', ['--sheet', ...thai]);
if (only.includes('brand')) run('backoffice_preview.js', ['--direction', 'all', '--screens', 'overview,records', '--singles', 'all', '--sheet', '--out', 'assets/directions/previews/product', ...thai]);
if (only.includes('backoffice')) run('backoffice_preview.js', ['--sheet', ...thai]);
if (only.includes('tablet')) run('backoffice_preview.js', ['--screens', 'records,overview,approval,detail', '--width', '820', '--height', '1366', '--sheet', '--out', 'assets/backoffice/previews/tablet', ...thai]);
if (only.includes('rtl')) run('backoffice_preview.js', ['--screens', 'records,overview,approval', '--rtl', '--sheet', '--out', 'assets/backoffice/previews/rtl']);
if (only.includes('mobile')) run('backoffice_preview.js', ['--mobile', '--sheet', '--singles', 'none', ...thai]);
console.log('\nPreviews rebuilt.');
