#!/usr/bin/env python3
"""Контактный лист как самодостаточная страница: превью inline, отметки в db."""
import base64, html, json, re
from pathlib import Path

SEL = Path.home() / "Downloads" / "works-site" / "_select"
OUT = Path("/private/tmp/claude-501/-usr-local-lib-node-modules--anthropic-ai-claude-code/2ed9b2f1-3e23-4251-be6b-e94cbecad68d/scratchpad/contact-sheet.html")
manifest = json.loads((SEL / "manifest.json").read_text())

def norm(t):
    t = re.sub(r"[^a-zа-я0-9 ]+", " ", t.lower())
    return " ".join(re.sub(r"\s+", " ", t).strip().split()[:8])

def clean_title(t):
    t = re.sub(r"[-–]?[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "", t)
    t = re.sub(r"\s*\(\d+\)\s*$", "", t)
    t = re.sub(r"\s+\.?\d+$", "", t)
    return re.sub(r"\s+", " ", t).strip(" .-") or "untitled"

groups, order = {}, []
for m in manifest:
    k = norm(m["title"])
    groups.setdefault(k, []) or order.append(k) if k not in groups else None
    groups.setdefault(k, []).append(m)
order = list(dict.fromkeys(norm(m["title"]) for m in manifest))

blocks, total_bytes = [], 0
for gi, k in enumerate(order, 1):
    items = groups[k]
    label = html.escape(clean_title(items[0]["title"])[:88]).upper()
    cells = []
    for m in items:
        b = (SEL / "thumbs_md" / f"{m['n']:03d}.jpg").read_bytes()
        total_bytes += len(b)
        uri = "data:image/jpeg;base64," + base64.b64encode(b).decode()
        ar = (m["w"] / m["h"]) if m["w"] and m["h"] else 1
        kind = ' data-v="1"' if m["kind"] == "video" else ""
        cells.append(
            f'<button class="f" type="button" data-n="{m["n"]}"{kind} style="--ar:{ar:.4f}" '
            f'aria-pressed="false" aria-label="кадр {m["n"]:03d}">'
            f'<img loading="lazy" src="{uri}" alt="">'
            f'<span class="n">{m["n"]:03d}</span></button>'
        )
    blocks.append(
        f'<section class="roll" data-g="{gi}">'
        f'<h2><span class="lb">{label}</span>'
        f'<span class="ct"><i data-gsel>0</i>/{len(items)}</span></h2>'
        f'<div class="strip">{"".join(cells)}</div></section>'
    )

N = len(manifest)
doc = f"""<title>Контактный лист Dlorian</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500&display=swap">
<style>
:root{{
  --ground:#000; --panel:#0b0b0b; --edge:#1a1a1a;
  --ink:#f2f2f2; --dim:#7a7a7a; --faint:#3a3a3a;
  --mark:#e2402b;                     /* цанговый карандаш по контактному листу */
  --mono:"IBM Plex Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  --sans:"IBM Plex Sans",system-ui,-apple-system,sans-serif;
  --row:132px;
}}
*{{box-sizing:border-box}}
html{{background:var(--ground)}}
body{{margin:0;background:var(--ground);color:var(--ink);font:400 13px/1.5 var(--mono);
 -webkit-font-smoothing:antialiased;padding-bottom:24vh}}

header{{position:sticky;top:0;z-index:20;background:rgba(0,0,0,.93);
 backdrop-filter:blur(10px);border-bottom:1px solid var(--edge);
 padding:13px 22px;display:flex;gap:24px;align-items:baseline;flex-wrap:wrap}}
h1{{margin:0;font:500 12px/1 var(--mono);letter-spacing:1.6px;text-transform:uppercase}}
.tally{{color:var(--dim);letter-spacing:.6px;font-variant-numeric:tabular-nums}}
.tally b{{color:var(--mark);font-weight:600}}
nav{{margin-left:auto;display:flex;gap:18px;align-items:baseline;flex-wrap:wrap}}
button.act{{background:none;border:0;color:var(--dim);font:400 12px/1 var(--mono);
 letter-spacing:.6px;cursor:pointer;padding:4px 0;text-transform:uppercase}}
button.act:hover{{color:var(--ink)}}
button.act[aria-pressed="true"]{{color:var(--mark)}}
button.act:focus-visible,.f:focus-visible{{outline:2px solid var(--mark);outline-offset:2px}}
.sync{{color:var(--faint);font-size:11px;letter-spacing:.5px}}
.sync[data-on="1"]{{color:var(--dim)}}

.roll{{padding:26px 22px 4px}}
.roll h2{{margin:0 0 9px;display:flex;gap:12px;align-items:baseline;
 border-bottom:1px solid var(--edge);padding-bottom:7px}}
.lb{{font:400 11px/1.35 var(--sans);letter-spacing:.7px;color:var(--dim);
 overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.ct{{margin-left:auto;font:400 11px/1 var(--mono);color:var(--faint);
 font-variant-numeric:tabular-nums;flex:0 0 auto}}
.ct i{{font-style:normal}}
.roll[data-has] .ct i{{color:var(--mark)}}

.strip{{display:flex;flex-wrap:wrap;gap:5px}}
.f{{position:relative;flex:0 0 auto;height:var(--row);width:calc(var(--row) * var(--ar));
 padding:0;border:0;background:var(--panel);cursor:pointer;overflow:hidden;display:block;
 opacity:.38;transition:opacity .16s ease}}
.f img{{width:100%;height:100%;object-fit:cover;display:block}}
.f:hover{{opacity:.8}}
.f[aria-pressed="true"]{{opacity:1}}
.f[aria-pressed="true"]::after{{content:"";position:absolute;inset:0;
 border:2px solid var(--mark);pointer-events:none}}
.n{{position:absolute;left:0;bottom:0;padding:2px 5px;font:400 10px/1.3 var(--mono);
 letter-spacing:.5px;color:var(--ink);background:rgba(0,0,0,.68);
 font-variant-numeric:tabular-nums}}
.f[data-v]::before{{content:"";position:absolute;right:5px;top:5px;z-index:2;
 width:0;height:0;border-left:7px solid var(--ink);
 border-top:4.5px solid transparent;border-bottom:4.5px solid transparent;
 filter:drop-shadow(0 0 2px rgba(0,0,0,.9))}}

body.only .f:not([aria-pressed="true"]){{display:none}}
body.only .roll:not([data-has]){{display:none}}
body.only .empty{{display:block}}
.empty{{display:none;padding:60px 22px;color:var(--faint);letter-spacing:.5px}}
footer{{padding:44px 22px 0;color:var(--faint);letter-spacing:.5px;
 border-top:1px solid var(--edge);margin:40px 22px 0;font-size:11px}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important}}}}
</style>

<header>
 <h1>Контактный лист</h1>
 <span class="tally">[ <b id="k">0</b> / {N} ]</span>
 <nav>
  <button class="act" id="only" aria-pressed="false">только отмеченные</button>
  <button class="act" id="clear">снять всё</button>
  <span class="sync" id="sync">локально</span>
 </nav>
</header>

{"".join(blocks)}

<p class="empty">Ничего не отмечено.</p>
<footer>Клик по кадру — отметить. {N} работ, {len(order)} серий съёмки, 55 из них видео (помечены треугольником).
Отметки сохраняются автоматически — можно закрыть и вернуться с другого устройства.</footer>

<script>
const N={N}, KEY='dlorian-picks';
let sel=new Set(), db=null, firstSnap=true, timer=null;
try{{sel=new Set(JSON.parse(localStorage.getItem(KEY)||'[]'))}}catch(e){{}}

const frames=[...document.querySelectorAll('.f')];
const rolls=[...document.querySelectorAll('.roll')];
const kEl=document.getElementById('k'), syncEl=document.getElementById('sync');

function paint(){{
  for(const f of frames) f.setAttribute('aria-pressed', sel.has(+f.dataset.n)?'true':'false');
  for(const r of rolls){{
    const on=[...r.querySelectorAll('.f')].filter(f=>sel.has(+f.dataset.n)).length;
    r.querySelector('[data-gsel]').textContent=on;
    on?r.setAttribute('data-has',''):r.removeAttribute('data-has');
  }}
  kEl.textContent=String(sel.size).padStart(3,'0');
}}
function persist(){{
  try{{localStorage.setItem(KEY,JSON.stringify([...sel]))}}catch(e){{}}
  if(!db) return;
  clearTimeout(timer);
  timer=setTimeout(()=>{{
    db.doc('selection/current').set({{
      picks:[...sel].sort((a,b)=>a-b), count:sel.size, total:N,
      updatedAt:new Date().toISOString()
    }}).then(()=>{{syncEl.textContent='сохранено';syncEl.dataset.on='1'}})
      .catch(()=>{{syncEl.textContent='сохранено локально';syncEl.dataset.on=''}});
  }},400);
}}

document.addEventListener('click',e=>{{
  const f=e.target.closest('.f'); if(!f) return;
  const n=+f.dataset.n;
  sel.has(n)?sel.delete(n):sel.add(n);
  paint(); persist();
}});
document.getElementById('clear').onclick=()=>{{sel=new Set();paint();persist()}};
document.getElementById('only').onclick=e=>{{
  const on=document.body.classList.toggle('only');
  e.currentTarget.setAttribute('aria-pressed',on?'true':'false');
}};
paint();

Promise.resolve(window.claude&&window.claude.use&&window.claude.use('db')).then(d=>{{
  if(!d) return;
  db=d;
  syncEl.textContent='синхронизируется'; syncEl.dataset.on='1';
  db.doc('selection/current').onSnapshot(s=>{{
    const remote=s.exists?(s.data().picks||[]):[];
    if(firstSnap){{
      firstSnap=false;
      for(const n of remote) sel.add(n);      // не терять то, что отмечено до подключения
      paint();
      if(sel.size!==remote.length) persist(); else syncEl.textContent='сохранено';
      return;
    }}
    if(s.metadata.hasPendingWrites) return;
    sel=new Set(remote); paint();
    syncEl.textContent='сохранено';
  }}, ()=>{{syncEl.textContent='сохранено локально';syncEl.dataset.on=''}});
}});
</script>"""

OUT.write_text(doc)
print(f"файл: {OUT}")
print(f"размер: {OUT.stat().st_size/1048576:.2f} MB (превью {total_bytes/1048576:.2f} MB)")
print(f"кадров: {N}, серий: {len(order)}")
