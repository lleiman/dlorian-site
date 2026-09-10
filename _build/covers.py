#!/usr/bin/env python3
"""Выбирает обложку каждой серии: не самый тёмный кадр, с живым контрастом.

Отдельно ищет видео-обложку — на главной серия показывается зациклённым
роликом, если он в серии есть, как на ashthorp.art.
"""
import json
from pathlib import Path
from PIL import Image, ImageStat

SITE = Path.home() / "Downloads" / "works-site"
SEL = SITE / "_select"
manifest = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}
series = json.loads((SEL / "series.json").read_text())

def score(n):
    """Обложка должна читаться миниатюрой: не проваленная в чёрное,
    с разбросом яркости и заметным цветом."""
    p = SEL / "thumbs_sm" / f"{n:03d}.jpg"
    if not p.exists():
        return -1e9
    st = ImageStat.Stat(Image.open(p).convert("RGB"))
    r, g, b = st.mean
    lum = 0.2126 * r + 0.7152 * g + 0.0722 * b
    spread = sum(st.stddev) / 3
    chroma = max(r, g, b) - min(r, g, b)
    # штраф за удаление от комфортной яркости миниатюры (~95 из 255)
    return -abs(lum - 95) * 1.6 + spread * 1.5 + chroma * 0.6

covers = {}
print(f"{'СЕРИЯ':<10} {'кадр':>5} {'видео':>6}")
print("-" * 24)
for nm, ns in series.items():
    imgs = [n for n in ns if manifest[n]["kind"] == "image"] or ns
    vids = [n for n in ns if manifest[n]["kind"] == "video"]
    entry = {"img": max(imgs, key=score)}
    if vids:
        entry["vid"] = max(vids, key=score)
    covers[nm] = entry
    print(f"{nm:<10} {entry['img']:>5} {entry.get('vid', '—'):>6}")

(SEL / "covers.json").write_text(json.dumps(covers, ensure_ascii=False, indent=1))
print(f"\nсохранено: {SEL/'covers.json'}")

# Порядок слайдшоу на главной, пока лайков нет или их мало.
# Не больше двух работ из серии, иначе первый экран покажет одну тему.
best, per = [], {}
ranked = sorted(
    ((n, nm) for nm, ns in series.items() for n in ns if manifest[n]["kind"] == "image"),
    key=lambda t: score(t[0]), reverse=True)
for n, nm in ranked:
    if per.get(nm, 0) >= 2:
        continue
    per[nm] = per.get(nm, 0) + 1
    best.append(n)
    if len(best) >= 16:
        break

(SEL / "best.json").write_text(json.dumps(best))
print(f"запасной порядок слайдшоу ({len(best)} кадров): {best}")
