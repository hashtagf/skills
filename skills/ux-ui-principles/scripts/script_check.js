#!/usr/bin/env node
/*
 * Static script check for built pages, no browser needed (Node only).
 *
 * Usage: node script_check.js page.html [more.html ...]
 *
 * For each page: every inline <script> (except JSON / templates) and every local <script src>
 * is compiled with Node's parser (syntax errors fail), and top-level declarations are checked
 * against names the browser already defines on window (top, name, status, parent, …). A classic
 * script that declares `const top` throws "Identifier 'top' has already been declared" and stops,
 * so the page silently loses its charts or handlers. Fix: wrap the script in an IIFE / block, or rename.
 *
 * Module scripts (type="module") are compiled as modules and are exempt from the global-name check.
 * Exit code 1 when any problem is found. Use render_check.js as well when a browser is available:
 * it catches runtime errors this static check cannot see.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const WINDOW_NAMES = new Set(['top', 'name', 'status', 'parent', 'self', 'length', 'origin', 'history', 'location',
  'event', 'close', 'open', 'print', 'scroll', 'frames', 'opener', 'closed', 'screen', 'external', 'navigator',
  'document', 'window', 'menubar', 'toolbar', 'stop', 'focus', 'blur', 'find', 'alert', 'confirm', 'prompt',
  'scrollX', 'scrollY', 'innerWidth', 'innerHeight', 'localStorage', 'sessionStorage', 'performance', 'crypto', 'caches']);

function scriptsOf(file) {
  const html = fs.readFileSync(file, 'utf8');
  const out = [];
  const re = /<script\b([^>]*)>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html))) {
    const attrs = m[1];
    const type = (/\btype\s*=\s*["']?([^"'\s>]+)/i.exec(attrs) || [])[1] || '';
    if (type && !/^(module|text\/javascript|application\/javascript)$/i.test(type)) continue; // JSON, templates
    const src = (/\bsrc\s*=\s*["']([^"']+)["']/i.exec(attrs) || [])[1];
    const line = html.slice(0, m.index).split('\n').length;
    if (src) {
      if (/^(https?:)?\/\//i.test(src) || src.startsWith('data:')) continue;
      const p = path.resolve(path.dirname(file), src.split(/[?#]/)[0]);
      if (!fs.existsSync(p)) { out.push({where: `${src} (line ${line})`, missing: true}); continue; }
      out.push({where: src, code: fs.readFileSync(p, 'utf8'), module: /module/i.test(type)});
    } else if (m[2].trim()) {
      out.push({where: `inline script at line ${line}`, code: m[2], module: /module/i.test(type)});
    }
  }
  return out;
}

// Top-level declarations: strip strings/comments roughly, then track brace depth.
function topLevelNames(code) {
  const clean = code.replace(/\/\*[\s\S]*?\*\//g, ' ').replace(/(^|[^:\\])\/\/.*$/gm, '$1')
    .replace(/`(?:\\[\s\S]|[^`\\])*`/g, '""').replace(/"(?:\\.|[^"\\\n])*"/g, '""').replace(/'(?:\\.|[^'\\\n])*'/g, "''");
  const names = [];
  let depth = 0;
  const tokens = clean.split(/(\{|\}|\n)/);
  let buf = '';
  for (const t of tokens) {
    if (t === '{') { if (depth === 0) collect(buf); buf = ''; depth++; continue; }
    if (t === '}') { depth = Math.max(0, depth - 1); continue; }
    if (depth === 0) buf += t;
  }
  collect(buf);
  function collect(s) {
    const re = /(?:^|[;\s(])(const|let|var|class|function\*?)\s+([A-Za-z_$][\w$]*)|(?:^|[;\s])(?:const|let|var)\s*\{([^}]*)\}/g;
    let m;
    while ((m = re.exec(s))) { if (m[2]) names.push(m[2]); }
    const multi = /(?:^|[;\s])(?:const|let|var)\s+([^;]+)/g;
    while ((m = multi.exec(s))) {
      m[1].split(',').forEach((part) => { const n = /^\s*([A-Za-z_$][\w$]*)\s*(=|$)/.exec(part); if (n) names.push(n[1]); });
    }
  }
  return [...new Set(names)];
}

let problems = 0;
for (const file of process.argv.slice(2)) {
  if (!fs.existsSync(file)) { console.log(`MISSING ${file}`); problems++; continue; }
  const scripts = scriptsOf(file);
  const issues = [];
  for (const s of scripts) {
    if (s.missing) { issues.push(`missing local script ${s.where}`); continue; }
    try {
      // modules: drop import/export lines and compile the body as a function (syntax only)
      new vm.Script(s.module ? `(async()=>{\n${s.code.replace(/^\s*(import|export)\b.*$/gm, '')}\n})` : s.code, {filename: s.where});
    } catch (e) {
      issues.push(`syntax error in ${s.where}: ${e.message}`);
      continue;
    }
    if (!s.module) {
      const clash = topLevelNames(s.code).filter((n) => WINDOW_NAMES.has(n));
      if (clash.length) issues.push(`${s.where} declares global ${clash.map((n) => `'${n}'`).join(', ')}, which clash${clash.length > 1 ? '' : 'es'} with window.${clash[0]}: wrap the script in an IIFE or rename`);
    }
  }
  if (issues.length) { problems += issues.length; console.log(`FAIL  ${file}`); issues.forEach((i) => console.log(`   - ${i}`)); }
  else console.log(`PASS  ${file} (${scripts.length} script${scripts.length === 1 ? '' : 's'})`);
}
process.exit(problems ? 1 : 0);
