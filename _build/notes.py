#!/usr/bin/env python3
"""Создаёт _select/notes.json — тексты, которые встают между работами.

Засевается настоящими промптами серии, помеченными как промпты: они
показываются с подписью «промпт», потому что опечатка в чужом тексте
читается как ляп, а в подписанном промпте — как документ.

Формат записи в notes:
  "любая строка"                      → текст автора, без подписи
  {"kind": "prompt", "text": "..."}   → промпт, с подписью

Файл заводится один раз и больше не перезаписывается: правки автора
важнее пересборки.
"""
import json, re
from pathlib import Path

SITE = Path.home() / "Downloads" / "works-site"
SEL = SITE / "_select"
OUT = SEL / "notes.json"
manifest = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}
series = json.loads((SEL / "series.json").read_text())

if OUT.exists():
    print(f"{OUT} уже есть — не трогаю (там могут быть правки автора)")
    raise SystemExit

def clean(t):
    t = re.sub(r"[-–]?[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", "", t)
    t = re.sub(r"\s*\(\d+\)\s*$", "", t)
    t = re.sub(r"\s+\.?\d+$", "", t)
    return re.sub(r"\s+", " ", t).strip(" .-")

data = {}
for nm, ns in series.items():
    seen, uniq = set(), []
    for n in ns:
        t = clean(manifest[n]["title"]).lower()
        k = " ".join(t.split()[:6])
        if k and k not in seen:
            seen.add(k)
            uniq.append(t[:170])
    data[nm] = {
        # крупная строка под заголовком серии; заменить на свою мысль
        "lead": {"kind": "prompt", "text": uniq[0]} if uniq else "",
        # тексты, которые встают между работами по ходу ленты
        "notes": [{"kind": "prompt", "text": t} for t in uniq[1:7]],
    }

OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1))
print(f"создан {OUT}")
print('засеяно промптами. Свой текст — просто строкой вместо объекта:')
print('  "lead": "Скорость — единственное, что делает тело честным."')
print("потом python3 _build/pages.py")
for nm, d in data.items():
    print(f"  {nm:<10} lead + {len(d['notes'])} вставок")
