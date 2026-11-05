#!/usr/bin/env python3
"""Add a live tweak panel to an HTML page that reads its look from CSS custom properties.

Usage:
  python3 tweaks_panel.py page.html [--out page.tweaks.html] [--accent-var --color-accent]
         [--presets "Rust:#c96442,Cobalt:#2c4d8e,Sage:#4a7a3f,Plum:#7a3f6a,Graphite:#3a3a3a"]

Knobs: accent (curated swatches, no free color picker), text scale, density (sets --density 0.85 / 1 / 1.2;
use it in your CSS with calc), color mode (sets data-theme light/dark, matching tokens.css from export_tokens.py)
and motion (off sets data-motion=off and zeroes --dur-*). Choices persist in localStorage per page; T hides or
shows the panel, R resets. The accent text color is chosen for contrast automatically. For client reviews and
for finding the last 20% of a look; remove the panel before shipping. Standard library only.
"""
import json
import os
import sys

PRESETS = "Rust:#c2410c,Cobalt:#2c4d8e,Sage:#4a7a3f,Plum:#7a3f6a,Rose:#b4405f,Graphite:#3a3a3a"

PANEL = r"""
<style id="tw-style">
#tw{position:fixed;right:16px;bottom:16px;z-index:2147483000;width:260px;max-width:calc(100vw - 32px);font:14px/1.4 system-ui,sans-serif;color:#16181d;background:#fff;border:1px solid #d6d9de;border-radius:14px;box-shadow:0 12px 40px rgba(0,0,0,.18);padding:14px 16px}
#tw[hidden]{display:none}
#tw h2{font:700 13px/1 system-ui;margin:0 0 10px;letter-spacing:.02em}
#tw label,#tw .tl{display:block;font-weight:600;font-size:12px;margin:10px 0 6px;color:#4a5160}
#tw .sw{display:flex;gap:8px;flex-wrap:wrap}
#tw .sw button{width:44px;height:44px;border-radius:50%;border:2px solid #fff;box-shadow:0 0 0 1px #c4c8cf;cursor:pointer;padding:0}
#tw .sw button[aria-pressed=true]{box-shadow:0 0 0 3px #16181d}
#tw input[type=range]{width:100%;min-height:44px;font-size:16px}
#tw .seg{display:flex;gap:4px}
#tw .seg button{flex:1;min-height:44px;border:1px solid #c4c8cf;background:#fff;border-radius:8px;font:600 12px system-ui;cursor:pointer;color:#16181d}
#tw .seg button[aria-pressed=true]{background:#16181d;color:#fff;border-color:#16181d}
#tw .ft{display:flex;justify-content:space-between;margin-top:12px;font-size:12px;color:#5b6270}
#tw button:focus-visible,#tw input:focus-visible{outline:3px solid #2a6df4;outline-offset:2px}
html[data-motion=off] *{animation:none!important;transition:none!important}
</style>
<aside id="tw" aria-label="Tweaks"><h2>Tweaks</h2>
<div class="tl">Accent</div><div class="sw" id="tw-acc"></div>
<label for="tw-scale">Text size <span id="tw-sv"></span></label><input id="tw-scale" type="range" min="90" max="120" step="2" value="100">
<div class="tl">Density</div><div class="seg" id="tw-den"><button data-v="0.85">Compact</button><button data-v="1">Normal</button><button data-v="1.2">Roomy</button></div>
<div class="tl">Mode</div><div class="seg" id="tw-mode"><button data-v="light">Light</button><button data-v="dark">Dark</button></div>
<div class="tl">Motion</div><div class="seg" id="tw-mot"><button data-v="on">On</button><button data-v="off">Off</button></div>
<div class="ft"><span><kbd>T</kbd> hide</span><span><kbd>R</kbd> reset</span></div></aside>
<script id="tw-script">
(function(){
var ACC=__ACC__,PRE=__PRE__,KEY='tweaks:'+location.pathname,root=document.documentElement,P=document.getElementById('tw');
var D={accent:null,scale:100,density:1,mode:null,motion:'on'},S=Object.assign({},D);
try{Object.assign(S,JSON.parse(localStorage.getItem(KEY)||'{}'))}catch(e){}
function lum(h){var c=[1,3,5].map(function(i){var v=parseInt(h.substr(i,2),16)/255;return v<=.03928?v/12.92:Math.pow((v+.055)/1.055,2.4)});return .2126*c[0]+.7152*c[1]+.0722*c[2]}
function apply(){
 if(S.accent){root.style.setProperty(ACC,S.accent);root.style.setProperty(ACC+'-text',S.accent);root.style.setProperty('--color-focus',S.accent);
  root.style.setProperty('--color-accent-ink',lum(S.accent)>.4?'#111111':'#ffffff')}
 else{[ACC,ACC+'-text','--color-focus','--color-accent-ink'].forEach(function(k){root.style.removeProperty(k)})}
 root.style.fontSize=S.scale+'%';document.getElementById('tw-sv').textContent=S.scale+'%';
 root.style.setProperty('--density',S.density);
 if(S.mode){root.setAttribute('data-theme',S.mode)}else{root.removeAttribute('data-theme')}
 root.setAttribute('data-motion',S.motion);
 if(S.motion==='off'){['--dur-fast','--dur-base','--dur-slow'].forEach(function(k){root.style.setProperty(k,'0.01ms')})}else{['--dur-fast','--dur-base','--dur-slow'].forEach(function(k){root.style.removeProperty(k)})}
 document.querySelectorAll('#tw-acc button').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.v===S.accent))});
 [['tw-den','density'],['tw-mode','mode'],['tw-mot','motion']].forEach(function(p){document.querySelectorAll('#'+p[0]+' button').forEach(function(b){b.setAttribute('aria-pressed',String(String(S[p[1]])===b.dataset.v))})});
 document.getElementById('tw-scale').value=S.scale;
 try{localStorage.setItem(KEY,JSON.stringify(S))}catch(e){}
}
var sw=document.getElementById('tw-acc');
PRE.forEach(function(p){var b=document.createElement('button');b.type='button';b.dataset.v=p[1];b.title=p[0];b.setAttribute('aria-label',p[0]);b.style.background=p[1];b.onclick=function(){S.accent=p[1];apply()};sw.appendChild(b)});
document.getElementById('tw-scale').oninput=function(e){S.scale=+e.target.value;apply()};
[['tw-den','density',Number],['tw-mode','mode',String],['tw-mot','motion',String]].forEach(function(p){document.querySelectorAll('#'+p[0]+' button').forEach(function(b){b.onclick=function(){S[p[1]]=p[2](b.dataset.v);apply()}})});
document.addEventListener('keydown',function(e){if(/INPUT|TEXTAREA|SELECT/.test((e.target.tagName||''))||e.metaKey||e.ctrlKey||e.altKey)return;
 if(e.key==='t'||e.key==='T'){P.hidden=!P.hidden}
 if(e.key==='r'||e.key==='R'){S=Object.assign({},D);apply()}});
apply();
})();
</script>
"""


def main():
    a = sys.argv[1:]
    files = [x for x in a if not x.startswith("--") and x not in [a[i + 1] for i, v in enumerate(a[:-1]) if v.startswith("--")]]
    if not files:
        print(__doc__)
        sys.exit(2)
    src = files[0]
    opt = lambda k, d: a[a.index(k) + 1] if k in a else d
    out = opt("--out", os.path.splitext(src)[0] + ".tweaks.html")
    pre = [p.split(":", 1) for p in opt("--presets", PRESETS).split(",") if ":" in p]
    html = open(src, encoding="utf-8").read()
    if 'id="tw"' in html:
        sys.exit("a tweak panel is already present in %s" % src)
    panel = PANEL.replace("__ACC__", json.dumps(opt("--accent-var", "--color-accent"))).replace("__PRE__", json.dumps(pre))
    i = html.lower().rfind("</body>")
    html = html[:i] + panel + html[i:] if i != -1 else html + panel
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out)


if __name__ == "__main__":
    main()
