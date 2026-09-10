# Раньше здесь был caddy:2-alpine и чистая статика. Голоса, комментарии и
# правка текста из админки требуют состояния, поэтому статику и API отдаёт
# один процесс на Flask.
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    SITE_DIR=/srv \
    DATA_DIR=/data \
    CONTENT_SRC=/app/content \
    RENDER_SCRIPT=/app/pages.py

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server/app.py .
# генератор страниц: тот же самый, что и локально, пути берёт из окружения.
# Нужен на сервере, чтобы админка могла пересобрать сайт после правки.
COPY _build/pages.py .
# исходные данные; при первом запуске копируются на том и дальше правятся там
COPY _select/manifest.json _select/series.json _select/covers.json \
     _select/best.json _select/notes.json _select/deck.json \
     _select/prices.json _select/shows.json /app/content/

# в образ едет только сам сайт: контактный лист и CLAUDE.md наружу не отдаём
# shows.html есть не всегда: страница создаётся, только когда заведены показы.
# Звёздочка в шаблоне не роняет сборку, если файла нет.
COPY *.html /srv/
COPY robots.txt sitemap.xml /srv/
COPY s /srv/s
# страница каждой работы
COPY w /srv/w
COPY assets /srv/assets

# том Railway монтируется в /data; без него база и правки переживут один деплой
RUN mkdir -p /data/uploads /data/content /data/site

CMD ["sh", "-c", "gunicorn -w 3 -k gthread --threads 4 -t 120 -b 0.0.0.0:${PORT:-8080} app:app"]
