#!/usr/bin/env node
/*
 * Static script check for built pages, no browser needed (Node only).
 *
 * Usage: node script_check.js page.html [more.html ...] [-h|--help]
 *
 * For each page: every inline <script> (except JSON / templates) and every local <script src>
 * is compiled with Node's parser (syntax errors fail), and top-level declarations are checked
 * against names the browser already defines on window (top, name, status, parent, …). A classic
 * script that declares `const top` throws "Identifier 'top' has already been declared" and stops,
 * so the page silently loses its charts or handlers. Fix: wrap the script in an IIFE / block, or rename.
 *
 * Module scripts (type="module") are compiled as modules and are exempt from the global-name check.
 * Top-level names are found by V8's own parser, so destructuring (const {top, left} = …, let [a, name] = …,
 * nested or renamed {x: top}) is caught like a simple name.
 * Exit code 1 when any problem is found; 2 for a missing file or a bad option. Use render_check.js as well when a browser is available:
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

// Top-level names that clash with window globals, found by the parser itself: compile `let <name>;` in front of
// the script; V8 reports "Identifier '<name>' has already been declared" exactly when the script declares <name>
// at top level, in any form (const/let/var/class/function, destructuring {top}, [a, name], nested or renamed
// {x: top}), and never for names in inner blocks or functions, or property keys ({top: x} declares x).
function globalClashes(code) {
  const found = [];
  for (const n of WINDOW_NAMES) {
    if (!new RegExp(`\\b${n}\\b`).test(code)) continue;
    try { new vm.Script(`let ${n};\n${code}`); }
    catch (e) { if (e instanceof SyntaxError && e.message.includes(`'${n}' has already been declared`)) found.push(n); }
  }
  return found;
}

const A = require('./_args');
const a = A.parse(process.argv.slice(2), { file: __filename, positional: [1, Infinity, 'page.html (one or more)'] });
for (const f of a._) if (!fs.existsSync(f) || !fs.statSync(f).isFile()) A.usageError(`file not found: ${path.resolve(f)}`, 'check the path');
let problems = 0;
for (const file of a._) {
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
      const clash = globalClashes(s.code);
      if (clash.length) issues.push(`${s.where} declares global ${clash.map((n) => `'${n}'`).join(', ')}, which clash${clash.length > 1 ? '' : 'es'} with window.${clash[0]}: wrap the script in an IIFE or rename`);
    }
  }
  if (issues.length) { problems += issues.length; console.log(`FAIL  ${file}`); issues.forEach((i) => console.log(`   - ${i}`)); }
  else console.log(`PASS  ${file} (${scripts.length} script${scripts.length === 1 ? '' : 's'})`);
}
process.exit(problems ? 1 : 0);
