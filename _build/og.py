#!/usr/bin/env python3
"""Рисует альбомные превью 1200×630 для ссылок: главная и каждая серия.

Без og:image ссылка на сайт в мессенджере и соцсети показывается голым
текстом. 1200×630 — размер, который понимают все площадки.
"""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

SITE = Path.home() / "Downloads" / "works-site"
SEL = SITE / "_select"
OUT = SITE / "assets" / "og"
OUT.mkdir(parents=True, exist_ok=True)

series = json.loads((SEL / "series.json").read_text())
covers = json.loads((SEL / "covers.json").read_text())
best = json.loads((SEL / "best.json").read_text())

W, H = 1200, 630
FONT = "/System/Library/Fonts/Menlo.ttc"
SITE_NAME = "DLORIAN"

SLUG = {
    "VELOCITY": "velocity", "BODY": "body", "KISSING": "kissing",
    "ORGANISM": "organism", "THRONE": "throne", "MYTH": "myth",
    "RITUAL": "ritual", "CITY": "city", "TATTOO": "tattoo",
    "BRAND": "brand", "CREATURE": "creature",
}


def tracked(draw, xy, text, font, fill, space):
    """PIL не умеет межбуквенный интервал, а он у нас несущий элемент стиля."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + space
    return x


def card(src_n, title, sub, dest):
    im = Image.open(SITE / "assets/img" / f"{src_n:03d}.jpg").convert("RGB")

    # заполняем кадр целиком, лишнее срезаем по центру
    ratio = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.LANCZOS)
    left = (im.width - W) // 2
    top = (im.height - H) // 2
    im = im.crop((left, top, left + W, top + H))

    # затемнение снизу, иначе текст утонет в светлых работах
    scrim = Image.new("L", (1, H))
    for y in range(H):
        t = y / H
        scrim.putpixel((0, y), int(255 * max(0, (t - 0.35) / 0.65) ** 1.4 * 0.88))
    scrim = scrim.resize((W, H))
    im = Image.composite(Image.new("RGB", (W, H), (0, 0, 0)), im, scrim)

    d = ImageDraw.Draw(im)
    f_big = ImageFont.truetype(FONT, 64, index=1)   # Menlo Bold
    f_sub = ImageFont.truetype(FONT, 24, index=0)

    tracked(d, (64, H - 168), title, f_big, (242, 242, 242), 9)
    tracked(d, (66, H - 74), sub, f_sub, (154, 154, 154), 3)

    im.save(dest, "JPEG", quality=86, optimize=True)
    return dest.stat().st_size


total = sum(len(v) for v in series.values())
size = card(best[0], SITE_NAME, f"{total} РАБОТ · {len(series)} СЕРИЙ", OUT / "index.jpg")
print(f"index.jpg — {size/1024:.0f} KB")

for nm, ns in series.items():
    n = covers[nm]["img"]
    size = card(n, nm, f"{len(ns)} РАБОТ · {SITE_NAME}", OUT / f"{SLUG[nm]}.jpg")
    print(f"{SLUG[nm]}.jpg — {size/1024:.0f} KB")

print(f"\nготово: {OUT}")
