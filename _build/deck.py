#!/usr/bin/env python3
"""Создаёт _select/deck.json — витрину: одна работа на экран, с именем.

Засевается лучшими по лайкам, дальше по оценке яркости и контраста.
Имена пустые: их может дать только автор. Пока имени нет, работа
подписывается серией и номером кадра.

Файл заводится один раз и больше не перезаписывается.
"""
import json
from pathlib import Path

SITE = Path.home() / "Downloads" / "works-site"
SEL = SITE / "_select"
OUT = SEL / "deck.json"

if OUT.exists():
    print(f"{OUT} уже есть — не трогаю (там могут быть имена автора)")
    raise SystemExit

manifest = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}
series = json.loads((SEL / "series.json").read_text())
best = json.loads((SEL / "best.json").read_text())

series_of = {n: nm for nm, ns in series.items() for n in ns}

# 16 работ: столько же, сколько у ориентира, и столько ещё можно назвать
# руками за один присест
picked = [n for n in best if manifest[n]["kind"] == "image"][:16]

deck = [{
    "n": n,
    "series": series_of[n],
    # ↓ заполнить руками: имя работы и одна строка про то, что это
    "name": "",
    "note": "",
} for n in picked]

OUT.write_text(json.dumps(deck, ensure_ascii=False, indent=1))
print(f"создан {OUT} — {len(deck)} работ")
print("\nимена пустые. Заполнить так:")
print('  {"n": 158, "series": "KISSING", "name": "БЛИЗКО", "note": "midjourney, серия из 41 кадра"}')
print("\nпотом python3 _build/pages.py")
for d in deck:
    print(f"  {d['n']:>3}  {d['series']}")
