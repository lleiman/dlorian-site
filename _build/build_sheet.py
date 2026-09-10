#!/usr/bin/env python3
"""Генерирует контактный лист: группировка по промптам, отметка кликом."""
import json, re, html
from pathlib import Path

OUT = Path.home() / "Downloads" / "works-site" / "_select"
manifest = json.loads((OUT / "manifest.json").read_text())

def norm(t):
    t = t.lower()
    t = re.sub(r"[^a-zа-я0-9 ]+", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return " ".join(t.split()[:8])

groups, order = {}, []
for m in manifest:
    k = norm(m["title"])
    if k not in groups:
        groups[k] = []
        order.append(k)
    groups[k].append(m)

blocks = []
for k in order:
    items = groups[k]
    label = html.escape(items[0]["title"][:96]) or "untitled"
    cells = []
    for m in items:
        ar = (m["w"] / m["h"]) if m["w"] and m["h"] else 1
        badge = "▶" if m["kind"] == "video" else ""
        cells.append(
            f'<figure class="c" data-n="{m["n"]}" style="--ar:{ar:.4f}">'
            f'<img loading="lazy" src="{m["thumb"]}" alt="">'
            f'<figcaption>{m["n"]:03d}<span>{badge}</span></figcaption></figure>'
        )
    blocks.append(
        f'<section class="g"><h2>{label}<em>{len(items)}</em></h2>'
        f'<div class="row">{"".join(cells)}</div></section>'
    )

doc = f"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Contact Sheet — 390</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box}}
html{{background:#000}}
body{{margin:0;background:#000;color:#f2f2f2;
 font:400 13px/1.5 "IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
 -webkit-font-smoothing:antialiased;padding-bottom:20vh}}
header{{position:sticky;top:0;z-index:10;background:rgba(0,0,0,.94);
 backdrop-filter:blur(8px);border-bottom:1px solid #1c1c1c;
 padding:14px 20px;display:flex;gap:22px;align-items:baseline;flex-wrap:wrap}}
h1{{font-size:13px;font-weight:500;letter-spacing:.32px;margin:0;text-transform:uppercase}}
#count{{color:#8a8a8a;letter-spacing:.32px}}
#count b{{color:#f2f2f2;font-weight:500}}
nav{{margin-left:auto;display:flex;gap:16px;flex-wrap:wrap}}
button{{background:none;border:0;color:#8a8a8a;font:inherit;letter-spacing:.32px;
 cursor:pointer;padding:0;text-transform:uppercase}}
button:hover{{color:#f2f2f2}}
button.on{{color:#f2f2f2}}
.g{{padding:30px 20px 6px}}
.g h2{{font-size:11px;font-weight:400;letter-spacing:.9px;color:#6e6e6e;margin:0 0 10px;
 text-transform:uppercase;display:flex;gap:10px;align-items:baseline}}
.g h2 em{{font-style:normal;color:#3a3a3a}}
.row{{display:flex;flex-wrap:wrap;gap:6px}}
.c{{margin:0;position:relative;height:132px;width:calc(132px * var(--ar));
 cursor:pointer;overflow:hidden;background:#0c0c0c;flex:0 0 auto;
 opacity:.4;transition:opacity .18s ease,outline-color .18s ease;
 outline:1px solid transparent;outline-offset:-1px}}
.c:hover{{opacity:.75}}
.c.sel{{opacity:1;outline-color:#f2f2f2}}
.c img{{width:100%;height:100%;object-fit:cover;display:block}}
.c figcaption{{position:absolute;left:0;bottom:0;padding:2px 5px;font-size:10px;
 letter-spacing:.5px;color:#f2f2f2;background:rgba(0,0,0,.65);display:flex;gap:5px}}
.c figcaption span{{color:#8a8a8a}}
body.only .c:not(.sel){{display:none}}
body.only .g:not(:has(.sel)){{display:none}}
footer{{padding:40px 20px;color:#4a4a4a;letter-spacing:.32px}}
</style></head><body>
<header>
 <h1>Contact sheet</h1>
 <span id="count">[ <b>0</b> / {len(manifest)} ]</span>
 <nav>
  <button id="only">только выбранные</button>
  <button id="clear">снять всё</button>
  <button id="save">[ сохранить выбор ]</button>
 </nav>
</header>
{"".join(blocks)}
<footer>клик — отметить · выбор хранится в браузере · «сохранить выбор» скачает selection.json в ~/Downloads</footer>
<script>
const KEY='mj-selection';
let sel=new Set(JSON.parse(localStorage.getItem(KEY)||'[]'));
const cells=[...document.querySelectorAll('.c')];
const countEl=document.querySelector('#count b');
function paint(){{
  cells.forEach(c=>c.classList.toggle('sel',sel.has(+c.dataset.n)));
  countEl.textContent=sel.size;
  localStorage.setItem(KEY,JSON.stringify([...sel]));
}}
document.addEventListener('click',e=>{{
  const c=e.target.closest('.c'); if(!c)return;
  const n=+c.dataset.n; sel.has(n)?sel.delete(n):sel.add(n); paint();
}});
document.querySelector('#clear').onclick=()=>{{sel=new Set();paint()}};
document.querySelector('#only').onclick=e=>{{
  document.body.classList.toggle('only');
  e.target.classList.toggle('on',document.body.classList.contains('only'));
}};
document.querySelector('#save').onclick=()=>{{
  const blob=new Blob([JSON.stringify([...sel].sort((a,b)=>a-b))],{{type:'application/json'}});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob); a.download='selection.json'; a.click();
}};
paint();
</script></body></html>"""

(OUT / "index.html").write_text(doc)
print(f"страница: {OUT/'index.html'}")
print(f"групп: {len(order)}, работ: {len(manifest)}")
print("\n--- 12 самых больших групп ---")
for k in sorted(order, key=lambda k: -len(groups[k]))[:12]:
    print(f"  {len(groups[k]):>3}  {groups[k][0]['title'][:64]}")
