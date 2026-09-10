#!/usr/bin/env python3
"""Собирает index.html и страницы серий."""
import html, json, re
from pathlib import Path

# Пути настраиваются переменными окружения: тот же скрипт запускается
# и локально, и на сервере из админки, где данные лежат на томе.
import os
SITE = Path(os.environ.get("SITE_OUT", str(Path.home() / "Downloads" / "works-site")))
SEL = Path(os.environ.get("CONTENT_DIR", str(SITE / "_select")))
SITE.mkdir(parents=True, exist_ok=True)
manifest = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}
series = json.loads((SEL / "series.json").read_text())
# обложки подобраны covers.py по яркости и контрасту — первая работа серии
# почти всегда проваленная в чёрное и миниатюрой не читается
covers = json.loads((SEL / "covers.json").read_text())
# тексты между работами; правятся руками в _select/notes.json
notes = json.loads((SEL / "notes.json").read_text()) if (SEL / "notes.json").exists() else {}
# запасной порядок слайдшоу на главной, пока лайков нет
best = json.loads((SEL / "best.json").read_text())
# витрина: 16 работ по одной на экран, имена даёт автор в deck.json
deck = json.loads((SEL / "deck.json").read_text()) if (SEL / "deck.json").exists() else []
# Цены. Пустой файл — норма: цена показывается только у той работы, которой
# её задали. Портфолио с ценником на каждой работе читается как магазин.
prices = json.loads((SEL / "prices.json").read_text()) if (SEL / "prices.json").exists() else {}
# Показы. Пока пусто, ссылка на страницу в шапке не появляется.
shows = json.loads((SEL / "shows.json").read_text()) if (SEL / "shows.json").exists() else []

# ↓ заполнить, когда будут контакты; пустые строки просто не отрисуются
SITE_NAME = "DLORIAN"
LINKS = [
    # ("INSTAGRAM", "https://instagram.com/..."),
    # ("TELEGRAM",  "https://t.me/..."),
    # ("MAIL",      "mailto:..."),
]
YEAR = "2026"
# og:image обязан быть абсолютным — по относительному пути площадки
# картинку не забирают
SITE_URL = os.environ.get("SITE_URL", "https://dlorian.art")

# версия в ссылках на css/js: Caddy отдаёт статику с длинным кешем,
# без неё правки стилей не доедут до тех, кто уже открывал сайт
VER = os.environ.get("ASSET_VER", "30")

SLUG = {
    "VELOCITY": "velocity", "BODY": "body", "KISSING": "kissing",
    "ORGANISM": "organism", "THRONE": "throne", "MYTH": "myth",
    "RITUAL": "ritual", "CITY": "city", "TATTOO": "tattoo",
    "BRAND": "brand", "CREATURE": "creature",
}

E = html.escape

def works_word(n):
    return f"{n} work" + ("" if n == 1 else "s")


def series_word(n):
    return f"{n} series"




def text_of(v):
    """Запись из notes.json → (текст, это_промпт).
    Строка — текст автора, объект с kind:prompt — засеянный промпт."""
    if not v:
        return "", False
    if isinstance(v, str):
        return v, False
    return v.get("text", ""), v.get("kind") == "prompt"

# мысль автора набирается гротеском, промпт — моноширинным:
# человеческий текст и машинный видно с первого взгляда
def lead_html(v):
    t, is_prompt = text_of(v)
    if not t:
        return ""
    src = '<span class="src">prompt</span>' if is_prompt else ""
    p = " data-prompt" if is_prompt else ""
    return f'<p class="lead"{p}>{src}{E(t)}</p>'

def note_html(v, side):
    t, is_prompt = text_of(v)
    if not t:
        return ""
    src = '<span class="src">prompt</span>' if is_prompt else ""
    p = " data-prompt" if is_prompt else ""
    return f'<div class="note" data-side="{side}"><p{p}>{src}{E(t)}</p></div>'


STATUS = {
    "available": None,          # показываем саму цену
    "sold": "sold",
    "reserved": "reserved",
    "request": "price on request",
}


def price_html(n):
    """Мелкая строка рядом с номером кадра — как этикетка в галерее,
    а не ценник. Нет записи — нет и строки."""
    d = prices.get(str(n)) or prices.get(n)
    if not d:
        return ""
    if isinstance(d, str):
        d = {"price": d, "status": "available"}
    st = d.get("status", "available")
    word = STATUS.get(st, None)
    text = word if word else (d.get("price") or "")
    if not text:
        return ""
    return f'<span class="cost" data-st="{E(st)}">{E(text)}</span>'


names = list(series.keys())
# Серии с живой обложкой уходят вниз: верх главной должен быть спокойнее.
# sort устойчив, поэтому внутри каждой группы порядок по размеру сохраняется.
names.sort(key=lambda nm: 1 if "vid" in covers[nm] else 0)
total = sum(len(v) for v in series.values())
tvid = sum(1 for ns in series.values() for n in ns if manifest[n]["kind"] == "video")

def clip(t, n=155):
    t = " ".join(str(t or "").split())
    return t if len(t) <= n else t[:n - 1].rsplit(" ", 1)[0] + "…"


def head(title, desc, depth, og="index", canon="", img_url=""):
    up = "../" if depth else ""
    img = img_url or f"{SITE_URL}/assets/og/{og}.jpg"
    canonical = f'<link rel="canonical" href="{SITE_URL}/{canon}">' if canon is not None else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<meta name="theme-color" content="#000000">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{img}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{E(title)}">
<meta name="twitter:description" content="{E(desc)}">
<meta name="twitter:image" content="{img}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400&display=swap">
<link rel="stylesheet" href="{up}assets/css/style.css?v={VER}">
{canonical}
</head>
<body>"""

def links_html():
    return "".join(f'<a href="{E(u)}" rel="me noopener" target="_blank">[{E(l)}]</a>'
                   for l, u in LINKS)

def menu_html(depth, current=None):
    """Список всех серий под шапкой. Страница серии — это 30-60 работ и
    десятки экранов; без этого списка перейти к соседней серии можно
    только через низ страницы или через главную."""
    # путь одинаково верен и с /s/, и с /w/: раньше считался только от /s/
    # и на страницах работ вёл в никуда
    up = "../s/" if depth else "s/"
    items = []
    for nm in names:
        cls = ' class="here"' if nm == current else ""
        items.append(f'<a{cls} href="{up}{SLUG[nm]}.html">{E(nm)}'
                     f'<i>{len(series[nm])}</i></a>')
    return f'<div class="menulist" id="menulist" hidden>{"".join(items)}</div>'


def bar(depth, meta, current=None):
    up = "../" if depth else ""
    # длинный счётчик главной на телефоне прячется (класс wide),
    # короткий «[ 30 ]» на странице серии остаётся
    cls = "meta" if depth else "meta wide"
    return (f'<div class="bar"><a class="mark" href="{up}index.html">{E(SITE_NAME)}</a>'
            f'<button class="menu" type="button" aria-expanded="false" '
            f'aria-controls="menulist">series</button>'
            f'<a class="pick" href="{up}deck.html">selected</a>'
            + (f'<a class="pick" href="{up}shows.html">shows</a>' if shows else '')
            + f'<span class="{cls}">{meta}</span><nav>{links_html()}</nav></div>'
            + menu_html(depth, current))

def foot(depth):
    up = "../" if depth else ""
    # Подписка — единственный способ владеть аудиторией, а не арендовать
    # её у площадки, которая может выключить охват в любой момент.
    sub = ('<form class="sub" novalidate>'
           '<span class="sublab">New work, by email</span>'
           '<span class="subrow">'
           '<input type="email" name="email" placeholder="email" '
           'autocomplete="email" maxlength="120">'
           '<button type="submit">subscribe</button>'
           '</span><span class="submsg"></span></form>')
    return (f'<footer><span>{E(SITE_NAME)} — {YEAR}</span>{links_html()}'
            f'{sub}</footer>'
            f'<script src="{up}assets/js/main.js?v={VER}"></script></body></html>')

# ---------- главная ----------
bands = []
for i, nm in enumerate(names):
    ns = series[nm]
    cv = covers[nm]
    vids = sum(1 for n in ns if manifest[n]["kind"] == "video")
    meta = works_word(len(ns)) + (f" · {vids} video" if vids else "")
    lead = lead_html((notes.get(nm) or {}).get("lead", ""))
    side = "right" if i % 2 else "left"

    # Обложки — только картинками. Видеоработы всего 832x464 и 624x624:
    # растянутые во всю ширину полосы они выглядели мутно, да и девять
    # автоиграющих роликов на главной — лишний трафик.
    c = cv["img"]
    shot = (f'<img loading="lazy" decoding="async" src="assets/img/{c:03d}.jpg" '
            f'srcset="assets/thumb/{c:03d}.jpg 760w, assets/img/{c:03d}.jpg 1600w" '
            f'sizes="100vw" alt="{E(nm)}" width="1600" height="900">')

    bands.append(
        f'<section class="band">'
        f'<a class="shot" href="s/{SLUG[nm]}.html" aria-label="{E(nm)}">{shot}</a>'
        f'<div class="say" data-side="{side}">'
        f'<h2><a href="s/{SLUG[nm]}.html">{E(nm)}</a></h2>'
        f'<span class="meta">{meta}</span>' + lead
        + f'<a class="go" href="s/{SLUG[nm]}.html">view series →</a>'
        f'</div></section>')

# ---------- слайдшоу на первом экране ----------
# Раньше здесь был смонтированный ролик, но исходные видео всего 832x464
# и 624x624: растянутые на всю ширину они превращались в кашу. Кадры
# лежат в честных 1600 px, поэтому первый экран собран из них.
slug_of = {n: SLUG[nm] for nm, ns in series.items() for n in ns}
hero_data = {"best": best, "slug": {str(n): sl for n, sl in slug_of.items()}}


def hero_html():
    """Первый слайд отрисован сразу, без скрипта: страница должна быть
    видна с первого кадра, а не ждать загрузки счётчиков."""
    n = best[0]
    return ('<div class="hero"><div class="slides">'
            f'<a class="slide on" href="s/{slug_of[n]}.html">'
            f'<img src="assets/img/{n:03d}.jpg" alt="" '
            f'width="1600" height="900" fetchpriority="high"></a>'
            '</div>'
            f'<div class="over"><h1>{E(SITE_NAME)}</h1>'
            f'<span class="meta">{works_word(total)} · {series_word(len(names))} · {YEAR}</span>'
            '</div></div>')


idx = (head(f"{SITE_NAME} — {works_word(total)} in {len(names)} series",
            clip(notes.get("_manifest") or f"{works_word(total)} in {len(names)} series."),
            0, "index", "index.html")
       + bar(0, f"[ {series_word(len(names))} · {works_word(total)} ]")
       + hero_html()
       + (f'<section class="manifest"><p>{E(notes["_manifest"])}</p></section>'
          if notes.get("_manifest") else "")
       + f'<main class="bands">{"".join(bands)}</main>'
       + f'<script id="heroData" type="application/json">{json.dumps(hero_data)}</script>'
       + foot(0))
(SITE / "index.html").write_text(idx)

# ---------- серии ----------
(SITE / "s").mkdir(exist_ok=True)
for i, nm in enumerate(names):
    ns = series[nm]
    nd = notes.get(nm) or {}
    txts = [v for v in nd.get("notes", []) if text_of(v)[0]]
    vids = sum(1 for n in ns if manifest[n]["kind"] == "video")

    # тексты раскидываем по ленте равномерно, попеременно вправо и влево
    slots = {}
    if txts:
        step = max(2, len(ns) // (len(txts) + 1))
        for j, t in enumerate(txts):
            pos = min(len(ns) - 1, step * (j + 1))
            slots.setdefault(pos, []).append((t, "right" if j % 2 == 0 else "left"))

    rows, data = [], []
    for k, n in enumerate(ns):
        m = manifest[n]
        w, h = (m["w"] or 3), (m["h"] or 2)
        data.append({"n": n, "k": m["kind"], "w": w, "h": h})
        if m["kind"] == "video":
            rows.append(
                f'<figure class="work" data-kind="video" data-n="{n}">'
                f'<video data-auto muted loop playsinline preload="none" '
                f'width="{w}" height="{h}" poster="../assets/poster/{n:03d}.jpg">'
                f'<source src="../assets/vid/{n:03d}.mp4" type="video/mp4"></video>'
                f'<figcaption class="bot">'
                f'<a class="no" href="../w/{n:03d}.html">{n:03d}</a>'
                f'{price_html(n)}</figcaption></figure>')
        else:
            rows.append(
                f'<figure class="work" data-kind="image" data-n="{n}">'
                f'<img loading="lazy" decoding="async" width="{w}" height="{h}" '
                f'src="../assets/img/{n:03d}.jpg" '
                f'srcset="../assets/thumb/{n:03d}.jpg 760w, ../assets/img/{n:03d}.jpg 1600w" '
                f'sizes="(max-width: 1800px) 100vw, 1800px" alt="{E(nm)} {n:03d}">'
                f'<figcaption class="bot">'
                f'<a class="no" href="../w/{n:03d}.html">{n:03d}</a>'
                f'{price_html(n)}</figcaption></figure>')
        for v, side in slots.get(k, []):
            rows.append(note_html(v, side))

    prev, nxt = names[i - 1], names[(i + 1) % len(names)]
    meta = works_word(len(ns)) + (f" · {vids} video" if vids else "")
    lead_txt = text_of(nd.get("lead", ""))[0]
    page = (head(f"{nm} — {SITE_NAME}",
                 clip(lead_txt or f"Series {nm}: {meta}."),
                 1, SLUG[nm], f"s/{SLUG[nm]}.html")
            + bar(1, f"[ {len(ns)} ]", nm)
            + f'<div class="head" data-series="{E(nm)}"><h1>{E(nm)}</h1>'
              f'<span class="meta">{meta}</span>'
            + lead_html(nd.get("lead", ""))
            + '</div>'
            + f'<main class="stack">{"".join(rows)}</main>'
            + f'<div class="ends">'
              f'<a href="{SLUG[prev]}.html">← {E(prev)}</a>'
              f'<a class="nx" href="{SLUG[nxt]}.html">{E(nxt)} →</a></div>'
            + f'<script id="works" type="application/json">{json.dumps(data)}</script>'
            # имена из витрины нужны карточке для инстаграма
            + f'<script id="deckShare" type="application/json">{json.dumps([{k: d[k] for k in ("n", "name", "note")} for d in deck])}</script>'
            + foot(1))
    (SITE / "s" / f"{SLUG[nm]}.html").write_text(page)

print(f"index.html + {len(names)} страниц серий")
print(f"работ {total}, видео {tvid}")
print("обложки серий: только картинки")
print(f"текстов между работами: {sum(len([t for t in (notes.get(nm) or {}).get('notes', []) if t]) for nm in names)}")
if not LINKS:
    print("\nконтактов нет — блок ссылок пустой, заполнить LINKS в pages.py")

# ---------- витрина ----------
# Одна работа на экран, переход стрелками, прокрутки нет. Столько работ,
# сколько можно назвать руками; весь архив остаётся за ней.
if deck:
    frames, data = [], []
    for i, d in enumerate(deck):
        n = d["n"]
        m = manifest[n]
        data.append({"n": n, "series": d["series"], "slug": SLUG[d["series"]],
                     "name": d.get("name", ""), "note": d.get("note", "")})
        # первые два кадра грузим сразу, остальные — по мере перелистывания,
        # иначе на входе прилетит 16 картинок разом
        src = (f'src="assets/img/{n:03d}.jpg"' if i < 2
               else f'data-src="assets/img/{n:03d}.jpg"')
        frames.append(
            f'<figure class="fr{" on" if i == 0 else ""}" data-i="{i}">'
            f'<img {src} alt="{E(d["series"])} {n:03d}" '
            f'width="{m["w"] or 16}" height="{m["h"] or 9}"></figure>')

    first = data[0]
    title0 = first["name"] or f'{first["series"]} · {first["n"]:03d}'
    note0 = first["note"] or ""

    dpage = (head(f"Selected — {SITE_NAME}",
             f"{works_word(len(deck))}, one to a screen — what to see first.",
             0, "index", "deck.html")
             + '<body class="deckpage">'
             + bar(0, f"[ {len(deck)} ]")
             + '<div class="deck">'
               f'<div class="frames">{"".join(frames)}</div>'
               '<button class="arw" data-d="-1" type="button" aria-label="Previous">←</button>'
               '<button class="arw" data-d="1" type="button" aria-label="Next">→</button>'
               '<div class="cap">'
               f'<h2>\'{E(title0)}\'</h2>'
               f'<p class="mat">{E(note0)}</p>'
               f'<a class="src" href="s/{first["slug"]}.html">'
               f'view series {E(first["series"])} →</a>'
               '</div>'
               f'<div class="tick">01 / {len(deck):02d}</div>'
               '</div>'
             + f'<script id="deckData" type="application/json">{json.dumps(data)}</script>'
             + foot(0))
    # head() уже открыл <body>, поэтому убираем лишний
    dpage = dpage.replace("<body><body class=\"deckpage\">", '<body class="deckpage">')
    (SITE / "deck.html").write_text(dpage)
    print(f"deck.html — витрина из {len(deck)} работ, "
          f"имён задано: {sum(1 for d in deck if d.get('name'))}")

# ---------- показы ----------
# Страница появляется только когда есть хотя бы одна дата. Тон намеренно
# сухой: список, а не афиша.
if shows:
    def show_key(x):
        return str(x.get("date") or "")

    rows = []
    today = __import__("datetime").date.today().isoformat()
    for x in sorted(shows, key=show_key):
        d = str(x.get("date") or "")
        past = bool(d) and d < today
        when = d
        if len(d) == 10 and d[4] == "-":
            when = f"{d[8:10]}.{d[5:7]}.{d[0:4]}"
        rows.append(
            f'<div class="show"{" data-past" if past else ""}>'
            f'<span class="when">{E(when)}</span>'
            f'<span class="where">{E(str(x.get("city") or ""))}</span>'
            f'<span class="venue">{E(str(x.get("venue") or ""))}</span>'
            f'<span class="snote">{E(str(x.get("note") or ""))}</span>'
            f'</div>')

    spage = (head(f"Shows — {SITE_NAME}",
             "Where and when the work can be seen in person.", 0, "index", "shows.html")
             + bar(0, f"[ {len(shows)} ]")
             + '<div class="head"><h1>Shows</h1></div>'
             + f'<main class="shows">{"".join(rows)}</main>'
             + foot(0))
    (SITE / "shows.html").write_text(spage)
    print(f"shows.html — {len(shows)} показов")
else:
    # старую страницу убираем, иначе она останется висеть без ссылки
    (SITE / "shows.html").unlink(missing_ok=True)
    print("показов нет — страница и ссылка не создаются")

# ---------- robots.txt и sitemap.xml ----------
# Без них поиск по имени автора не находит сайт вовсе, а это единственный
# сценарий, в котором поиск для портфолио вообще важен: человек увидел
# работу, запомнил имя, вбил его.
(SITE / "robots.txt").write_text(
    "User-agent: *\nAllow: /\n"
    f"Sitemap: {SITE_URL}/sitemap.xml\n"
)

urls = ["", "deck.html"] + [f"s/{SLUG[nm]}.html" for nm in names]
if shows:
    urls.append("shows.html")
urls += [f"w/{n:03d}.html" for ns in series.values() for n in ns]

body = "".join(
    f"<url><loc>{SITE_URL}/{u}</loc></url>" for u in urls)
(SITE / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    f"{body}</urlset>"
)
print(f"robots.txt и sitemap.xml — {len(urls)} адресов")

# ---------- страница каждой работы ----------
# Раньше работу нельзя было дать ссылкой: она жила внутри ленты серии.
# Теперь у каждой свой адрес — это и репост конкретного кадра, и 334
# страницы для поиска вместо тринадцати.
(SITE / "w").mkdir(exist_ok=True)
where = {n: nm for nm, ns in series.items() for n in ns}
made = 0
for nm, ns in series.items():
    nd = notes.get(nm) or {}
    lead_txt = text_of(nd.get("lead", ""))[0]
    for i, n in enumerate(ns):
        m = manifest[n]
        w, h = (m["w"] or 3), (m["h"] or 2)
        if m["kind"] == "video":
            media = (f'<video data-auto muted loop playsinline controls '
                     f'width="{w}" height="{h}" poster="../assets/poster/{n:03d}.jpg">'
                     f'<source src="../assets/vid/{n:03d}.mp4" type="video/mp4"></video>')
        else:
            media = (f'<img decoding="async" width="{w}" height="{h}" '
                     f'src="../assets/img/{n:03d}.jpg" '
                     f'srcset="../assets/thumb/{n:03d}.jpg 760w, ../assets/img/{n:03d}.jpg 1600w" '
                     f'sizes="(max-width: 1800px) 100vw, 1800px" alt="{E(nm)} {n:03d}">')

        prev_n = ns[i - 1]
        next_n = ns[(i + 1) % len(ns)]
        title = f"{nm} · {n:03d}"
        # og:image — сама работа: отдельные карточки на 334 страницы
        # весили бы десятки мегабайт и ничего бы не добавили
        og_img = f"{SITE_URL}/assets/img/{n:03d}.jpg"

        page = (head(f"{title} — {SITE_NAME}",
                     clip(lead_txt or f"Work {n:03d} from the series {nm}."),
                     1, SLUG[nm], f"w/{n:03d}.html", og_img)
                + bar(1, f"[ {n:03d} ]", nm)
                + f'<div class="head" data-series="{E(nm)}"><h1>{E(title)}</h1>'
                  f'<span class="meta">'
                  f'<a href="../s/{SLUG[nm]}.html">series {E(nm)}</a></span>'
                + (f'<p class="lead">{E(lead_txt)}</p>' if lead_txt else "")
                + '</div>'
                + f'<main class="stack"><figure class="work" '
                  f'data-kind="{m["kind"]}" data-n="{n}">{media}'
                  f'<figcaption class="bot"><span class="no">{n:03d}</span>'
                  f'{price_html(n)}</figcaption></figure></main>'
                + f'<div class="ends">'
                  f'<a href="{prev_n:03d}.html">← {prev_n:03d}</a>'
                  f'<a class="nx" href="{next_n:03d}.html">{next_n:03d} →</a></div>'
                + f'<script id="works" type="application/json">'
                  f'{json.dumps([{"n": n, "k": m["kind"], "w": w, "h": h}])}</script>'
                + f'<script id="deckShare" type="application/json">'
                  f'{json.dumps([{k: d[k] for k in ("n", "name", "note")} for d in deck])}</script>'
                + foot(1))
        (SITE / "w" / f"{n:03d}.html").write_text(page)
        made += 1

print(f"страниц работ: {made}")
