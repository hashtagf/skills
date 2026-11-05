/* Shared Playwright / browser discovery for render_check.js and direction_preview.js.
 * Never downloads anything. See render_check.js for the search order. */
const path = require('path');
const fs = require('fs');
const os = require('os');

function findModule(startPath) {
  const dirs = [process.env.PW_MODULE, path.join(process.cwd(), 'node_modules')];
  if (startPath && !/^[a-z]+:\/\//i.test(startPath)) {
    for (let d = path.dirname(path.resolve(startPath)); d !== path.dirname(d); d = path.dirname(d)) dirs.push(path.join(d, 'node_modules'));
  }
  (process.env.NODE_PATH || '').split(path.delimiter).forEach(d => dirs.push(d));
  try { dirs.push(require('child_process').execSync('npm root -g', { stdio: ['ignore', 'pipe', 'ignore'], timeout: 5000 }).toString().trim()); } catch (e) {}
  for (const d of dirs.filter(Boolean)) for (const name of ['playwright', 'playwright-core', '@playwright/test']) {
    const p = path.join(d, name);
    if (fs.existsSync(p)) { try { const m = require(p); if (m.chromium) return { chromium: m.chromium, from: p }; } catch (e) {} }
  }
  for (const name of ['playwright', 'playwright-core']) { try { const m = require(name); return { chromium: m.chromium, from: name }; } catch (e) {} }
  return null;
}

function findBrowser(chromium) {
  const ok = p => p && fs.existsSync(p);
  if (ok(process.env.PW_CHROMIUM)) return process.env.PW_CHROMIUM;
  try { const p = chromium.executablePath(); if (ok(p)) return null; } catch (e) {}
  const caches = [process.env.PLAYWRIGHT_BROWSERS_PATH, path.join(os.homedir(), 'Library/Caches/ms-playwright'),
    path.join(os.homedir(), '.cache/ms-playwright'), process.env.LOCALAPPDATA && path.join(process.env.LOCALAPPDATA, 'ms-playwright')].filter(Boolean);
  const rel = ['chrome-headless-shell-mac-arm64/chrome-headless-shell', 'chrome-headless-shell-mac-x64/chrome-headless-shell',
    'chrome-headless-shell-linux64/chrome-headless-shell', 'chrome-headless-shell-win64/chrome-headless-shell.exe',
    'chrome-mac/Chromium.app/Contents/MacOS/Chromium', 'chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    'chrome-mac-x64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing',
    'chrome-linux/chrome', 'chrome-linux64/chrome', 'chrome-win/chrome.exe', 'chrome-win64/chrome.exe'];
  for (const c of caches) {
    if (!fs.existsSync(c)) continue;
    const builds = fs.readdirSync(c).filter(d => /^chromium(_headless_shell)?-\d+$/.test(d))
      .sort((x, y) => Number(y.split('-').pop()) - Number(x.split('-').pop()) || (x.includes('headless') ? -1 : 1));
    for (const b of builds) for (const r of rel) { const p = path.join(c, b, r); if (ok(p)) return p; }
  }
  const system = ['/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    'C:/Program Files/Google/Chrome/Application/chrome.exe'];
  return system.find(ok) || undefined;
}


module.exports = { findModule, findBrowser };
