// Screenshots for ab_run.py output: node evals/ab_shots.js OUT_DIR
// For each task/arm (and the fixture as "before"), shoots the opened page at 1440 (full page, capped) and 390.
const path = require('path');
const fs = require('fs');
const {findModule, findBrowser} = require('../scripts/_pw.js');
const found = findModule(__filename);
if (!found) { console.error('playwright not found'); process.exit(2); }
const chromium = found.chromium;

(async () => {
  const out = path.resolve(process.argv[2]);
  const skill = path.resolve(__dirname, '..');
  const tasks = JSON.parse(fs.readFileSync(path.join(out, 'tasks.json'), 'utf8'));
  const exe = findBrowser(chromium);
  const browser = await chromium.launch(exe ? {executablePath: exe} : {});
  const jobs = [];
  for (const t of tasks) {
    for (const arm of ['with', 'without']) jobs.push({t, arm, dir: path.join(out, t.id, arm)});
    if (t.fixture) jobs.push({t, arm: 'before', dir: path.join(skill, t.fixture)});
  }
  for (const j of jobs) {
    const file = path.join(j.dir, j.t.open);
    if (!fs.existsSync(file)) { console.log(j.t.id, j.arm, 'missing', j.t.open); continue; }
    for (const [w, h, name] of [[1440, 900, 'desk'], [390, 844, 'phone']]) {
      const page = await browser.newPage({viewport: {width: w, height: h}, reducedMotion: 'reduce'});
      const errs = []; page.on('pageerror', (e) => errs.push(e.message)); page.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
      try {
        await page.goto('file://' + file, {waitUntil: 'load', timeout: 20000});
        await page.waitForTimeout(2500);
        await page.evaluate(async () => { for (let y = 0; y < document.body.scrollHeight; y += 600) { window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } window.scrollTo(0, 0); });
        await page.waitForTimeout(400);
        const full = await page.evaluate(() => document.documentElement.scrollHeight);
        const clipH = Math.min(full, name === 'desk' ? 3600 : 3200);
        await page.screenshot({path: path.join(out, `${j.t.id}-${j.arm}-${name}.jpg`), type: 'jpeg', quality: 70, fullPage: true, clip: {x: 0, y: 0, width: w, height: clipH}});
        console.log(j.t.id, j.arm, name, full + 'px', errs.length ? 'ERR ' + errs[0].slice(0, 120) : '');
      } catch (e) { console.log(j.t.id, j.arm, name, 'error', e.message.split('\n')[0]); }
      await page.close();
    }
  }
  await browser.close();
})();
