#!/usr/bin/env python3
"""Заводит _select/prices.json и _select/shows.json.

Оба файла создаются пустыми и заполняются из админки. Пустой файл — это
осознанно: цена показывается только у той работы, которой её задали, а
страница показов не появляется в шапке, пока в ней нет ни одной даты.
Портфолио с ценниками на всём мгновенно читается как магазин.
"""
import json
from pathlib import Path

SEL = Path.home() / "Downloads" / "works-site" / "_select"

for name, seed, what in (
    ("prices.json", {}, "цены работ: {\"181\": {\"price\": \"2 400 €\", \"status\": \"available\"}}"),
    ("shows.json", [], "показы: [{\"date\": \"2026-11-14\", \"city\": \"Москва\", "
                       "\"venue\": \"...\", \"note\": \"...\"}]"),
):
    p = SEL / name
    if p.exists():
        print(f"{name} уже есть — не трогаю")
        continue
    p.write_text(json.dumps(seed, ensure_ascii=False, indent=1))
    print(f"создан {name} — {what}")
