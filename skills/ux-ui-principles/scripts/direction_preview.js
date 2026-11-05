#!/usr/bin/env node
/*
 * Render one-screen preview pictures of the directions in assets/directions/directions.json,
 * so a user can choose a look from pictures (references/direction-library.md).
 *
 * Usage:
 *   node scripts/direction_preview.js [--ids dose,riso] [--group company|premium|playful|atmospheric]
 *        [--out dir] [--width 1440] [--height 1240] [--sheet] [--brief "Headline|Sentence|Button"]
 *        [--thai]   # use Thai sample copy (headings keep the direction's Latin faces + a Thai fallback)
 *
 * Each direction is drawn in its own composition (scripts/compositions.js: editorial, collage, full-bleed
 * photo, Swiss, soft product, poster, question, centred, magazine, board) on content from a real kind
 * of business (assets/directions/content-packs.json) with open-collection photographs (assets/photos/).
 * The pairing lives in directions.json (comp, subject, photoFilter); --comp c1..c10 and
 * --subject <pack> override it to try a direction in another arrangement. --legacy draws the old
 * single agency sample (palette and type compared on identical content). Fonts load
 * from Google Fonts (network); offline, generic fallbacks are used and the previews say so.
 * --sheet also writes sheet.jpg: every preview as a labelled thumbnail grid.
 * Setup needs Playwright; nothing is downloaded (see render_check.js --doctor).
 */
const fs = require('fs');
const path = require('path');
const { findModule, findBrowser } = require('./_pw');
const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const has = k => args.includes(k);

const root = path.resolve(__dirname, '..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'assets/directions/directions.json'), 'utf8')).directions;
const out = path.resolve(opt('--out', path.join(root, 'assets/directions/previews')));
const W = Number(opt('--width', '1440')), H = Number(opt('--height', '1240'));
let list = data;
if (opt('--ids')) { const ids = opt('--ids').split(','); list = data.filter(d => ids.includes(d.id)); }
if (opt('--group')) list = list.filter(d => d.group === opt('--group'));
if (!list.length) { console.error('no directions matched'); process.exit(2); }

const thai = has('--thai');
const legacy = has('--legacy');
const comps = require('./compositions');
const packs = JSON.parse(fs.readFileSync(path.join(root, 'assets/directions/content-packs.json'), 'utf8')).packs;
const photoDir = path.join(root, 'assets/photos');
const photos = {};
if (fs.existsSync(photoDir)) for (const f of fs.readdirSync(photoDir)) if (/\.jpe?g$/i.test(f)) photos[f.replace(/\.jpe?g$/i, '')] = 'data:image/jpeg;base64,' + fs.readFileSync(path.join(photoDir, f)).toString('base64');
// --brief "Headline|Sentence|Button" replaces the pack's headline, sentence and action with the user's copy
const withBrief = (p) => (brief[0] ? Object.assign({}, p, { h1: [brief[0], '', ''], sub: brief[1] || p.sub, cta: brief[2] || p.cta }) : p);
const pageFor = (d) => (legacy || !d.comp) ? html(d)
  : comps.render(d, opt('--comp', d.comp), withBrief(packs[opt('--subject', d.subject)] || packs.cafe), photos, { width: W, height: H, photoFilter: d.photoFilter, subject: opt('--subject', d.subject) });
const brief = (opt('--brief', '') || '').split('|');
const copy = thai
  ? { h1: brief[0] || 'แบรนด์ที่คนจำได้ ไม่ใช่แค่คนเห็น', sub: brief[1] || 'กลยุทธ์ ออกแบบ คอนเทนต์ และโฆษณา ในทีมเดียว', cta: brief[2] || 'นัดคุย 30 นาที', cta2: 'ดูผลงาน', work: 'ผลงานที่ตัวเลขขยับจริง', steps: ['ทำความเข้าใจ', 'วางทิศทาง', 'ออกแบบและผลิต', 'ปล่อยและต่อยอด'], weeks: ['สัปดาห์ที่ 1', 'สัปดาห์ที่ 2 ถึง 3', 'สัปดาห์ที่ 3 ถึง 8', 'สัปดาห์ที่ 6 เป็นต้นไป'], cases: [['2.4×', 'ยอดสมัคร', 'Mango Soda'], ['+61%', 'ลูกค้าสั่งซ้ำ', 'Baan Lanna'], ['−42%', 'ต้นทุนต่อลีด', 'Northwind']] }
  : { h1: brief[0] || 'Brands people remember, not just notice.', sub: brief[1] || 'Strategy, design, content and paid media in one team.', cta: brief[2] || 'Book a 30-min call', cta2: 'See the work', work: 'Work where the numbers moved.', steps: ['Discover', 'Define', 'Make', 'Grow'], weeks: ['Week 1', 'Weeks 2 to 3', 'Weeks 3 to 8', 'Week 6 onward'], cases: [['2.4×', 'sign-ups', 'Mango Soda'], ['+61%', 'repeat orders', 'Baan Lanna'], ['−42%', 'cost per lead', 'Northwind']] };

function css(d) {
  const t = d.tints, up = d.case === 'uppercase';
  const surf = {
    flat: `.tile,.card{background:var(--s)}`,
    outline: `.tile,.card{background:var(--s);border:1.5px solid var(--i)}`,
    offset: `.tile,.card{background:var(--s);border:2px solid var(--i);box-shadow:6px 6px 0 var(--i)}`,
    lift: `.tile,.card{background:var(--s);box-shadow:0 1px 2px rgba(0,0,0,.08),0 24px 40px -24px rgba(60,40,30,.35)}`,
    plastic: `.tile,.card{background:linear-gradient(rgba(255,255,255,.4),transparent 18%),var(--tint);box-shadow:inset 0 1.5px 0 rgba(255,255,255,.9),inset 0 -24px 36px -28px rgba(20,60,40,.35)}`,
    sticker: `.tile,.card{background:var(--s);border:4px solid #fff;box-shadow:5px 6px 0 var(--i);rotate:var(--rot,0deg)}.tile:nth-child(odd){--rot:-1.2deg}.tile:nth-child(even){--rot:1deg}`,
    paper: `.tile,.card{background:var(--s);box-shadow:0 1px 0 rgba(30,20,10,.25),0 10px 24px rgba(30,20,10,.28);rotate:var(--rot,0deg)}.tile:nth-child(odd){--rot:-.8deg}.tile:nth-child(even){--rot:.7deg}`
  }[d.surf];
  return `
:root{--g:${d.ground};--s:${d.surface};--i:${d.ink};--m:${d.muted};--a:${d.accent};--ai:${d.accentInk};--r:${d.radius}px;--t0:${t[0]};--t1:${t[1]};--t2:${t[2]};--t3:${t[3]};--ci:${d.cardInk || d.ink};--cm:${d.cardMuted || d.muted}}
*{box-sizing:border-box;margin:0}
body{background:var(--g);color:var(--i);font:400 18px/1.5 "${d.body}","Noto Sans Thai",system-ui,sans-serif;width:${W}px;min-height:${H}px;overflow:hidden;${d.dots ? 'background-image:radial-gradient(rgba(23,32,43,.22) 1px,transparent 1px);background-size:18px 18px;' : ''}}
.wrap{padding:0 64px}
nav{display:flex;align-items:center;gap:32px;height:76px;padding:0 64px}
.logo{font:${d.dw} 28px/1 "${d.display}","Kanit",sans-serif;letter-spacing:${d.track};text-transform:${d.case}}
nav a{font-size:16px;color:var(--m);text-decoration:none}nav .sp{margin-left:auto}
.btn{display:inline-flex;align-items:center;height:52px;padding:0 26px;background:var(--a);color:var(--ai);font:600 16px "${d.body}","Noto Sans Thai",sans-serif;border-radius:${({ pill: 999, round: 10, square: 0 })[d.btn || (d.radius >= 14 ? 'pill' : d.radius ? 'round' : 'square')]}px;${d.surf === 'offset' || d.surf === 'sticker' || d.surf === 'paper' ? 'box-shadow:4px 4px 0 var(--i);' : ''}${d.surf === 'outline' ? 'border:1.5px solid var(--i);' : ''}text-decoration:none}
.btn.o{background:var(--s);color:var(--i);${d.surf === 'outline' ? '' : 'border:1.5px solid var(--i);'}}
h1,h2,.n{font-family:"${d.display}","Kanit",sans-serif;font-weight:${d.dw};letter-spacing:${d.track};text-transform:${d.case};line-height:1.0}
h1{font-size:${d.hero === 'split' ? 76 : 84}px;max-width:${d.hero === 'split' ? 640 : 1100}px;margin-bottom:24px}
h2{font-size:52px;margin-bottom:28px}
.lead{font-size:21px;color:var(--m);max-width:520px}
.hero{padding:36px 64px 56px}
.hero .cta{display:flex;gap:16px;margin-top:28px}
.art{position:relative;overflow:hidden;border-radius:var(--r);background:var(--t0)}
.art i{position:absolute;display:block}
[data-art=blocks] i:nth-child(1){left:6%;top:12%;width:46%;height:70%;background:var(--t1)}
[data-art=blocks] i:nth-child(2){left:40%;top:30%;width:34%;height:60%;background:var(--t2)}
[data-art=blocks] i:nth-child(3){right:6%;top:8%;width:22%;height:38%;background:var(--t3);border-radius:50%}
[data-art=circle] i:nth-child(1){left:12%;top:14%;width:52%;aspect-ratio:1;border-radius:50%;background:var(--t0);${d.dark ? '' : 'mix-blend-mode:multiply;'}}
[data-art=circle] i:nth-child(2){left:36%;top:22%;width:52%;aspect-ratio:1;border-radius:50%;background:var(--t1);${d.dark ? 'opacity:.85;' : 'mix-blend-mode:multiply;'}}
[data-art=circle] i:nth-child(3){left:0;bottom:0;width:100%;height:14%;background:var(--t2);opacity:.9}
[data-art=stack] i:nth-child(1){left:8%;top:12%;width:50%;height:64%;background:var(--t1);border-radius:var(--r)}
[data-art=stack] i:nth-child(2){left:30%;top:26%;width:50%;height:60%;background:var(--s);border-radius:var(--r);box-shadow:0 10px 28px rgba(0,0,0,.2)}
[data-art=stack] i:nth-child(3){left:52%;top:10%;width:34%;height:30%;background:var(--t2);border-radius:var(--r)}
[data-art=grid] i{background:var(--t1)}
[data-art=grid] i:nth-child(1){left:8%;top:10%;width:38%;height:34%}
[data-art=grid] i:nth-child(2){left:50%;top:10%;width:42%;height:34%;background:var(--t2)}
[data-art=grid] i:nth-child(3){left:8%;top:50%;width:84%;height:38%;background:var(--t3)}
[data-art=lines] i{border:1.5px solid var(--a);background:transparent}
[data-art=lines] i:nth-child(1){left:8%;top:10%;width:60%;height:70%}
[data-art=lines] i:nth-child(2){left:30%;top:30%;width:60%;height:60%;border-color:var(--i)}
[data-art=lines] i:nth-child(3){left:0;top:50%;width:100%;height:0;border-width:1px 0 0}
.settled .art{height:230px;margin-top:32px}
.split .row{display:grid;grid-template-columns:1.1fr 1fr;gap:56px;align-items:center}
.split .art{height:420px}
.band{display:grid;grid-template-columns:1fr 1fr}
.band .l{padding:56px 64px}
.band .art{border-radius:0;min-height:420px;background:var(--a)}
.band .art i:nth-child(1){background:var(--t1)}
.work{padding:20px 64px 60px}
.tile:nth-child(1),.card:nth-child(1){--tint:var(--t0)}.tile:nth-child(2),.card:nth-child(2){--tint:var(--t1)}.tile:nth-child(3),.card:nth-child(3){--tint:var(--t2)}.card:nth-child(4){--tint:var(--t3)}
.tiles{display:grid;grid-template-columns:1.3fr 1fr 1fr;gap:28px}
.tile{border-radius:var(--r);padding:26px;display:flex;flex-direction:column;justify-content:space-between;min-height:190px}
.tile .n{font-size:64px}
.tile,.card{color:var(--ci)}
.tile small{display:block;font-size:16px;color:var(--cm)}
.tile b{font:600 18px "${d.body}","Noto Sans Thai",sans-serif}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:20px;padding:0 64px 40px}
.card{border-radius:var(--r);padding:20px 22px}
.card .w{font:${d.dw} 26px/1.1 "${d.display}","Kanit",sans-serif;text-transform:${d.case};letter-spacing:${d.track}}
.card p{font-size:16px;color:var(--cm);margin-top:6px}
.th h1,.th h2,.th .n,.th .card .w{line-height:1.2;letter-spacing:0;text-transform:none}
.tag{position:absolute;right:14px;bottom:10px;font:500 12px "${d.body}",sans-serif;opacity:.55}
.art svg{position:absolute;inset:0;width:100%;height:100%}
${(() => { const R = Math.max(d.radius, 18); return ({ leaf: `.tile,.card{border-radius:${R}px 6px ${R}px 6px}.art{border-radius:${R}px 6px ${R}px 6px}`, arch: `.tile{border-radius:150px 150px ${R}px ${R}px / 110px 110px ${R}px ${R}px}.art{border-radius:${R}px}`, cut: `.tile,.card,.art{clip-path:polygon(0 0,calc(100% - 28px) 0,100% 28px,100% 100%,0 100%)}`, even: '' })[d.corner || 'even']; })()}
.giant h1{font-size:${Math.min(132, Math.round(1340 / Math.max(10, 9)))}px;max-width:none;line-height:.95;margin-bottom:28px}
.giant .grow{display:grid;grid-template-columns:1fr 1.25fr;gap:48px;align-items:end}
.giant .art{height:270px}
.fullh{position:relative;height:560px;padding:0}
.fullh .art{position:absolute;inset:0;border-radius:0}
.pnl{position:absolute;left:64px;bottom:52px;max-width:640px;background:var(--s);color:var(--ci);border-radius:${Math.max(d.radius, 4)}px;padding:34px 38px}
.pnl h1{font-size:58px;margin-bottom:14px;max-width:none}.pnl .lead{color:var(--cm)}
.arch .row{display:grid;grid-template-columns:1.1fr 1fr;gap:56px;align-items:end}
.arch .art{height:520px;width:78%;margin-left:auto;border-radius:999px 999px 20px 20px}
.stagger .art{overflow:visible;background:transparent}

${surf}
`;
}


function artSvg(d) {
  const t = d.tints, a = d.accent, ink = d.ink, sf = d.surface, R = Math.max(d.radius, 14);
  const svg = b => `<svg viewBox="0 0 600 400" preserveAspectRatio="xMidYMid slice" aria-hidden="true">${b}</svg>`;
  switch (d.art) {
    case 'blob': return svg(`<path d="M110 300C50 230 85 120 190 88C292 58 384 112 412 192C442 272 362 352 258 352C196 352 150 336 110 300Z" fill="${t[1]}"/><path d="M326 118C378 66 482 78 524 152C566 224 524 304 452 324C390 340 328 292 308 230C298 190 298 150 326 118Z" fill="${t[2]}" opacity=".92"/><circle cx="478" cy="106" r="44" fill="${a}"/><circle cx="130" cy="92" r="22" fill="${t[3]}"/><path d="M60 360C140 330 220 370 300 350" stroke="${ink}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".5"/>`);
    case 'arch': return svg(`<rect x="0" y="330" width="600" height="70" fill="${t[3]}"/><path d="M70 340V210a110 110 0 0 1 220 0V340Z" fill="${t[1]}"/><path d="M240 340V150a130 130 0 0 1 260 0V340Z" fill="${t[2]}"/><path d="M300 340V190a70 70 0 0 1 140 0V340Z" fill="${sf}" opacity=".85"/><circle cx="500" cy="80" r="40" fill="${a}"/>`);
    case 'wave': return svg(`<circle cx="470" cy="100" r="52" fill="${a}"/><path d="M0 220Q75 170 150 220T300 220T450 220T600 220V400H0Z" fill="${t[1]}"/><path d="M0 265Q75 215 150 265T300 265T450 265T600 265V400H0Z" fill="${t[2]}"/><path d="M0 315Q75 265 150 315T300 315T450 315T600 315V400H0Z" fill="${t[3]}"/>`);
    case 'tilt': return svg(`<g transform="rotate(-9 200 210)"><rect x="70" y="90" width="270" height="200" rx="${R}" fill="${t[1]}"/></g><g transform="rotate(7 390 210)"><rect x="250" y="120" width="270" height="200" rx="${R}" fill="${sf}" stroke="${ink}" stroke-opacity=".18" stroke-width="2"/><rect x="274" y="148" width="120" height="14" rx="7" fill="${ink}" opacity=".7"/><rect x="274" y="174" width="190" height="10" rx="5" fill="${ink}" opacity=".25"/></g><g transform="rotate(-3 460 90)"><rect x="400" y="50" width="130" height="70" rx="${Math.round(R * 0.8)}" fill="${a}"/></g>`);
    case 'dots': { let c = ''; for (let y = 0; y < 9; y++) for (let x = 0; x < 15; x++) { const r = Math.max(1.5, 14 - (x * 0.62 + (8 - y) * 0.2)); c += `<circle cx="${30 + x * 38}" cy="${34 + y * 41}" r="${r.toFixed(1)}" fill="${t[1]}"/>`; } return svg(`${c}<circle cx="450" cy="150" r="92" fill="${a}" opacity=".9"/>`); }
    case 'diag': return svg(`<polygon points="0,400 0,250 400,0 540,0 140,400" fill="${t[1]}"/><polygon points="200,400 600,70 600,190 330,400" fill="${t[2]}"/><polygon points="390,400 600,230 600,400" fill="${a}"/>`);
    case 'rings': return svg(`<circle cx="360" cy="200" r="170" fill="none" stroke="${t[1]}" stroke-width="26"/><circle cx="360" cy="200" r="118" fill="${t[2]}" opacity=".9"/><circle cx="360" cy="200" r="66" fill="none" stroke="${t[3]}" stroke-width="18"/><circle cx="150" cy="300" r="46" fill="${a}"/>`);
    case 'pill': return svg(`<g transform="rotate(-24 300 200)"><rect x="40" y="120" width="300" height="76" rx="38" fill="${t[0]}"/><rect x="200" y="214" width="330" height="76" rx="38" fill="${t[1]}"/><rect x="70" y="308" width="220" height="76" rx="38" fill="${t[2]}"/><rect x="320" y="30" width="200" height="76" rx="38" fill="${t[3]}"/><rect x="300" y="308" width="76" height="76" rx="38" fill="${a}"/></g>`);
    default: return '';
  }
}
const NEWART = ['blob', 'arch', 'wave', 'tilt', 'dots', 'diag', 'rings', 'pill'];

function html(d) {
  const fams = [...new Set([d.display, d.body, 'Kanit', 'Noto Sans Thai'])].map(f => 'family=' + f.replace(/ /g, '+')).join('&');
  const tile = (c, i) => `<div class="tile ${i === 0 ? 'big' : ''}"><div><b>${c[2]}</b><small>${c[1]}</small></div><div class="n">${c[0]}</div></div>`;
  const artDiv = `<div class="art" data-art="${d.art}">${NEWART.includes(d.art) ? artSvg(d) : '<i></i><i></i><i></i>'}</div>`;
  const ctaH = `<div class="cta"><a class="btn">${copy.cta}</a><a class="btn o">${copy.cta2}</a></div>`;
  const hero = ({
    band: `<header class="hero band" style="padding:0"><div class="l"><h1>${copy.h1}</h1><p class="lead">${copy.sub}</p>${ctaH}</div>${artDiv}</header>`,
    split: `<header class="hero split"><div class="row"><div><h1>${copy.h1}</h1><p class="lead">${copy.sub}</p>${ctaH}</div>${artDiv}</div></header>`,
    stagger: `<header class="hero split stagger"><div class="row"><div><h1>${copy.h1}</h1><p class="lead">${copy.sub}</p>${ctaH}</div>${artDiv}</div></header>`,
    arch: `<header class="hero arch"><div class="row"><div><h1>${copy.h1}</h1><p class="lead">${copy.sub}</p>${ctaH}</div>${artDiv}</div></header>`,
    giant: `<header class="hero giant"><h1>${copy.h1}</h1><div class="grow"><div><p class="lead">${copy.sub}</p>${ctaH}</div>${artDiv}</div></header>`,
    full: `<header class="hero fullh">${artDiv}<div class="pnl"><h1>${copy.h1}</h1><p class="lead">${copy.sub}</p>${ctaH}</div></header>`,
    settled: `<header class="hero settled"><h1>${copy.h1}</h1><p class="lead">${copy.sub}</p>${ctaH}${artDiv}</header>`
  })[d.hero] || '';
  return `<!doctype html><html${thai ? ' class="th"' : ''}><head><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?${fams}&display=swap" rel="stylesheet"><style>${css(d)}</style></head><body>
<nav><span class="logo">Plume</span><a>Work</a><a>Services</a><a>Process</a><span class="sp"></span><a class="btn" style="height:44px;padding:0 20px">${copy.cta}</a></nav>
${hero}
<section class="work"><h2>${copy.work}</h2><div class="tiles">${copy.cases.map(tile).join('')}</div></section>
<section class="steps">${copy.steps.map((s, i) => `<div class="card"><div class="w">${copy.weeks[i]}</div><p>${s}</p></div>`).join('')}</section>
<span class="tag">${d.name} · preview</span></body></html>`;
}

(async () => {
  const mod = findModule(process.cwd());
  const exe = mod ? findBrowser(mod.chromium) : undefined;
  if (!mod || exe === undefined) { console.log('NOT RUN: no Playwright module or browser (npm i -D playwright && npx playwright install chromium)'); process.exit(3); }
  fs.mkdirSync(out, { recursive: true });
  const browser = await mod.chromium.launch(exe ? { executablePath: exe } : {});
  const page = await browser.newPage({ viewport: { width: W, height: H } });
  for (const d of list) {
    await page.setContent(pageFor(d), { waitUntil: 'load', timeout: 30000 }).catch(() => {});
    await page.evaluate(() => document.fonts && document.fonts.ready).catch(() => {});
    await page.waitForTimeout(legacy ? 400 : 900);
    const file = path.join(out, `${d.id}${thai ? '-th' : ''}.jpg`);
    await page.screenshot({ path: file, type: 'jpeg', quality: 82, clip: { x: 0, y: 0, width: W, height: H } });
    console.log(`${d.id}  ${d.group}  → ${file}`);
  }
  if (has('--sheet')) {
    const makeSheet = async (items, name) => {
      const cols = 4, tw = 480, th = Math.round(tw * H / W);
      const cells = items.map(d => `<figure style="margin:0"><img src="data:image/jpeg;base64,${fs.readFileSync(path.join(out, `${d.id}${thai ? '-th' : ''}.jpg`)).toString('base64')}" width="${tw}" height="${th}" style="display:block;border:1px solid #ccc"><figcaption style="font:600 16px system-ui;padding:6px 2px">${d.name} <span style="font-weight:400;color:#666">${d.group}</span></figcaption></figure>`).join('');
      await page.setViewportSize({ width: cols * (tw + 24) + 24, height: 400 });
      await page.setContent(`<body style="margin:0;padding:24px;background:#fff"><div style="display:grid;grid-template-columns:repeat(${cols},${tw}px);gap:20px 24px">${cells}</div></body>`, { waitUntil: 'load' });
      await page.waitForTimeout(300);
      await page.screenshot({ path: path.join(out, `${name}${thai ? '-th' : ''}.jpg`), type: 'jpeg', quality: 78, fullPage: true });
      console.log(`${name} → ${path.join(out, name + '.jpg')}`);
    };
    await makeSheet(list, has('--group') ? `sheet-${opt('--group')}` : 'sheet');
    if (!has('--group') && !opt('--ids')) for (const g of [...new Set(list.map(d => d.group))]) await makeSheet(list.filter(d => d.group === g), `sheet-${g}`);
  }
  await browser.close();
})();
