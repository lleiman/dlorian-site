#!/usr/bin/env python3
"""Раскладывает отобранные работы по сериям."""
import json, re
from pathlib import Path

SEL = Path.home() / "Downloads" / "works-site" / "_select"
m = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}

picks = ([24] + list(range(27, 52)) + list(range(53, 68)) + list(range(70, 77))
         + list(range(78, 101)) + list(range(102, 179)) + list(range(180, 206))
         + list(range(207, 269)) + [270] + list(range(272, 276))
         + list(range(277, 335)) + list(range(340, 369)) + [371, 385, 387, 388, 389, 390])
P = sorted(set(picks))
assert len(P) == 334, len(P)

# порядок важен: первое совпавшее правило выигрывает
RULES = [
    ("THRONE",   r"throne"),
    ("KISSING",  r"kissing"),
    ("TATTOO",   r"tatto"),
    ("VELOCITY", r"bike|racing|lamborgin|speed|drifter|sport"),
    ("ORGANISM", r"macro|organism|copper tube|lips flower|shaman|gauge|flower"),
    ("CREATURE", r"creature"),
    ("MYTH",     r"shiva|myth|mytholog|totem|heads|iconostasis|atleans|david"),
    ("RITUAL",   r"dancer|dancing|dance|techno|warehouse|ritual|anime"),
    ("CITY",     r"skyscraper|scyscraper|nameless cit|city|architect|arcitect|brutalism|undergro|abandoned|station|road|alleyway|digital sk"),
    ("BODY",     r"body|polaroid|model show"),
    ("BRAND",    r"oil|happin|yellow|plastic|snow|high fashion|brand ads|colors"),
]

series, unmatched = {}, []
for n in P:
    t = m[n]["title"].lower()
    for name, pat in RULES:
        if re.search(pat, t):
            series.setdefault(name, []).append(n)
            break
    else:
        unmatched.append(n)

order = sorted(series, key=lambda k: -len(series[k]))
print(f"отобрано: {len(P)}\n")
print(f"{'СЕРИЯ':<10} {'работ':>6} {'видео':>6}")
print("-" * 26)
tot = totv = 0
for k in order:
    ns = series[k]
    v = sum(1 for n in ns if m[n]["kind"] == "video")
    tot += len(ns); totv += v
    print(f"{k:<10} {len(ns):>6} {v:>6}")
print("-" * 26)
print(f"{'ИТОГО':<10} {tot:>6} {totv:>6}")

if unmatched:
    print(f"\nне разложены ({len(unmatched)}):")
    for n in unmatched:
        print(f"  {n:>3}  {m[n]['title'][:60]}")

out = {k: series[k] for k in order}
(SEL / "series.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
print(f"\nсохранено: {SEL/'series.json'}")
