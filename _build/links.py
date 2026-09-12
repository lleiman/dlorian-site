#!/usr/bin/env python3
"""Заводит _select/links.json — связи с другими проектами автора.

Два назначения у каждой ссылки:
  site  — видна посетителям в подвале сайта
  admin — видна только в админке, как личный пульт

Заводится один раз и дальше правится из админки.
"""
import json
from pathlib import Path

SEL = Path.home() / "Downloads" / "works-site" / "_select"
OUT = SEL / "links.json"

if OUT.exists():
    print(f"{OUT} уже есть — не трогаю")
    raise SystemExit

seed = [
    {"name": "ADEPT · Канва", "url": "https://adept-canvas-production-8754.up.railway.app", "where": "admin"},
    {"name": "ADEPT · Регламенты", "url": "", "where": "admin"},
    {"name": "THE RESONANCE", "url": "https://the-resonance-production.up.railway.app", "where": "admin"},
    {"name": "Синопсис", "url": "https://synopsis-site-production-804c.up.railway.app", "where": "admin"},
    {"name": "Карта города", "url": "https://lleiman.github.io/city-map-site", "where": "admin"},
    {"name": "Глава I", "url": "https://lleiman.github.io/chapter-site", "where": "admin"},
    {"name": "$BOAR", "url": "https://lleiman.github.io/nikitaboar", "where": "admin"},
]

OUT.write_text(json.dumps(seed, ensure_ascii=False, indent=1))
print(f"создан {OUT} — {len(seed)} связей")
print("все пока admin: на публику попадут только те, где поставишь site")
