#!/usr/bin/env python3
"""Бэкенд портфолио: отдаёт статику, считает голоса, хранит комментарии.

Раньше сайт был чистой статикой на Caddy. Голоса и комментарии требуют
состояния, поэтому статику теперь отдаёт тот же процесс, что и API —
один контейнер, одна точка отказа, никакого прокси между ними.

Данные лежат на диске Railway, смонтированном в DATA_DIR: база и картинки
из комментариев. Без тома они переживут ровно один деплой.
"""
import io
import json
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from flask import (Flask, abort, g, jsonify, redirect, request,
                   send_from_directory)
from PIL import Image

SITE_DIR = Path(os.environ.get("SITE_DIR", "/srv"))
DATA_DIR = Path(os.environ.get("DATA_DIR", "/data"))
UPLOADS = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "site.db"

# Фото от посторонних по умолчанию ждут одобрения: открытая загрузка
# картинок на публичный адрес — это приглашение для мусора и хуже.
# Текст публикуется сразу. Поменять: PHOTOS_NEED_APPROVAL=0
PHOTOS_NEED_APPROVAL = os.environ.get("PHOTOS_NEED_APPROVAL", "1") != "0"
# Токен для модерации. Без него админские ручки просто выключены.
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")

MAX_BODY = 2000
MAX_NAME = 60
MAX_UPLOAD = 8 * 1024 * 1024
MAX_SIDE = 1600
COMMENTS_PER_WINDOW = 5
WINDOW_SECONDS = 600

UPLOADS.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD + 64 * 1024

# ---------- контент, который правится из админки ----------
# Исходные данные запечены в образ (CONTENT_SRC) и при первом запуске
# копируются на том (CONTENT_DIR). Дальше правится только копия на томе —
# иначе правки исчезали бы при каждом деплое.
CONTENT_SRC = Path(os.environ.get("CONTENT_SRC", "/app/content"))
CONTENT_DIR = DATA_DIR / "content"
BUILT_DIR = DATA_DIR / "site"
RENDER = Path(os.environ.get("RENDER_SCRIPT", "/app/pages.py"))

# что разрешено править: тексты, витрина, состав серий, цены и показы
EDITABLE = {"notes.json", "deck.json", "series.json", "prices.json", "shows.json"}


def ensure_content():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    if not CONTENT_SRC.exists():
        return
    for f in CONTENT_SRC.glob("*.json"):
        dst = CONTENT_DIR / f.name
        if not dst.exists():
            shutil.copy2(f, dst)


ensure_content()


def load_content(name):
    p = CONTENT_DIR / name
    if not p.exists():
        p = CONTENT_SRC / name
    return json.loads(p.read_text()) if p.exists() else None


def rebuild():
    """Пересобирает страницы из данных на томе. Тот же самый pages.py,
    что и локально, только с другими путями."""
    if not RENDER.exists():
        return False, "нет скрипта сборки"
    env = dict(os.environ)
    env["SITE_OUT"] = str(BUILT_DIR)
    env["CONTENT_DIR"] = str(CONTENT_DIR)
    try:
        r = subprocess.run([sys.executable, str(RENDER)],
                           capture_output=True, text=True, timeout=180, env=env)
    except Exception as e:
        return False, str(e)
    return r.returncode == 0, (r.stdout + r.stderr)[-3000:]


def ensure_built():
    """Пересобирает страницы при старте, если образ приехал новее.

    Собранные админкой страницы лежат на томе и в выдаче главнее образа.
    Без этой проверки любой деплой обновлял бы только стили, скрипт и
    картинки, а вёрстка страниц навсегда осталась бы такой, какой её
    собрал прежний генератор. Ровно это и случилось однажды.
    """
    stamp = BUILT_DIR / ".built"
    try:
        key = str(RENDER.stat().st_mtime_ns) if RENDER.exists() else "0"
    except OSError:
        return
    try:
        if stamp.exists() and stamp.read_text().strip() == key:
            return
    except OSError:
        pass

    # воркеров несколько, собрать должен один
    lock = DATA_DIR / ".build.lock"
    try:
        if lock.exists() and time.time() - lock.stat().st_mtime > 300:
            lock.unlink(missing_ok=True)      # чужой воркер умер, не ждём вечно
    except OSError:
        pass
    try:
        fd = os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.close(fd)
    except FileExistsError:
        return
    except OSError:
        return

    try:
        ok, log = rebuild()
        if ok:
            BUILT_DIR.mkdir(parents=True, exist_ok=True)
            stamp.write_text(key)
        else:
            print(f"пересборка при старте не удалась: {log}", flush=True)
    finally:
        lock.unlink(missing_ok=True)


# какие номера работ вообще существуют — чтобы не копить мусор по любым id
def valid_set():
    s = load_content("series.json") or {}
    return {n for ns in s.values() for n in ns}


# при старте: если образ новее — пересобрать страницы на томе
ensure_built()
VALID = valid_set()


# Один сайт — один адрес. Пока оба домена отдают одно и то же, поиск делит
# вес между ними, а ссылки расходятся. Старый railway-адрес отправляем на
# основной постоянным редиректом.
CANON_HOST = os.environ.get("CANON_HOST", "dlorian.art")


@app.before_request
def force_canonical_host():
    if not CANON_HOST or request.method not in ("GET", "HEAD"):
        return None
    host = (request.host or "").split(":")[0]
    if host == CANON_HOST or not host.endswith(".up.railway.app"):
        return None
    return redirect(f"https://{CANON_HOST}{request.full_path.rstrip('?')}", code=301)


# ---------- база ----------

def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=10)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA busy_timeout=5000")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.executescript("""
    PRAGMA journal_mode=WAL;
    CREATE TABLE IF NOT EXISTS votes (
      work   INTEGER NOT NULL,
      voter  TEXT    NOT NULL,
      dir    INTEGER NOT NULL,
      at     TEXT    NOT NULL,
      PRIMARY KEY (work, voter)
    );
    CREATE TABLE IF NOT EXISTS comments (
      id       INTEGER PRIMARY KEY AUTOINCREMENT,
      work     INTEGER NOT NULL,
      name     TEXT,
      body     TEXT    NOT NULL,
      photo    TEXT,
      approved INTEGER NOT NULL DEFAULT 1,
      hidden   INTEGER NOT NULL DEFAULT 0,
      ip       TEXT,
      at       TEXT    NOT NULL
    );
    CREATE INDEX IF NOT EXISTS ix_comments_work ON comments (work, hidden, id);
    CREATE INDEX IF NOT EXISTS ix_votes_work ON votes (work);

    -- Подписка на новые работы. Единственный способ владеть аудиторией,
    -- а не арендовать её у инстаграма, который может выключить охват.
    CREATE TABLE IF NOT EXISTS subs (
      email TEXT PRIMARY KEY,
      at    TEXT NOT NULL,
      ip    TEXT
    );

    -- Посещения. Без счётчика любая стратегия — гадание. Считаем по дню,
    -- странице и домену-источнику: ни адресов, ни кук, ни личных данных.
    CREATE TABLE IF NOT EXISTS hits (
      day  TEXT NOT NULL,
      path TEXT NOT NULL,
      ref  TEXT NOT NULL,
      n    INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY (day, path, ref)
    );
    """)
    conn.commit()
    conn.close()


init_db()


# ---------- вспомогательное ----------

def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def client_ip():
    fwd = request.headers.get("X-Forwarded-For", "")
    return (fwd.split(",")[0].strip() or request.remote_addr or "?")[:64]


def voter_id():
    """Кто голосует. Токен генерит браузер и хранит у себя; это не защита
    от накрутки, а защита от случайного двойного клика."""
    v = (request.headers.get("X-Voter") or "").strip()
    return v[:64] if re.fullmatch(r"[A-Za-z0-9_-]{8,64}", v or "") else ""


def valid_work(n):
    return n in VALID if VALID else isinstance(n, int) and 0 < n < 10000


def tally(work):
    r = db().execute(
        "SELECT COALESCE(SUM(dir=1),0) up, COALESCE(SUM(dir=-1),0) down "
        "FROM votes WHERE work=?", (work,)).fetchone()
    # считаем все нескрытые: одобрения ждёт фото, а текст виден сразу,
    # поэтому счётчик должен совпадать с тем, что видно в списке
    c = db().execute(
        "SELECT COUNT(*) n FROM comments WHERE work=? AND hidden=0", (work,)).fetchone()
    return {"up": r["up"], "down": r["down"], "comments": c["n"]}


def is_admin():
    return bool(ADMIN_TOKEN) and request.headers.get("X-Admin", "") == ADMIN_TOKEN


# ---------- API: голоса ----------

@app.get("/api/summary")
def summary():
    """Счётчики по всем работам разом — лента рисует их без запроса на кадр."""
    out = {}
    for r in db().execute(
            "SELECT work, COALESCE(SUM(dir=1),0) up, COALESCE(SUM(dir=-1),0) down "
            "FROM votes GROUP BY work"):
        out[str(r["work"])] = {"up": r["up"], "down": r["down"], "comments": 0}
    for r in db().execute(
            "SELECT work, COUNT(*) n FROM comments WHERE hidden=0 GROUP BY work"):
        out.setdefault(str(r["work"]), {"up": 0, "down": 0, "comments": 0})
        out[str(r["work"])]["comments"] = r["n"]
    return jsonify(out)


@app.get("/api/mine")
def mine():
    """Что этот браузер уже отметил — чтобы кнопки поднялись нажатыми."""
    v = voter_id()
    if not v:
        return jsonify({})
    rows = db().execute("SELECT work, dir FROM votes WHERE voter=?", (v,))
    return jsonify({str(r["work"]): r["dir"] for r in rows})


@app.post("/api/vote")
def vote():
    data = request.get_json(silent=True) or {}
    work, direction = data.get("work"), data.get("dir")
    if not isinstance(work, int) or not valid_work(work):
        return jsonify({"error": "no such work"}), 400
    if direction not in (1, -1, 0):
        return jsonify({"error": "invalid vote"}), 400
    v = voter_id()
    if not v:
        return jsonify({"error": "no voter token"}), 400

    conn = db()
    if direction == 0:
        conn.execute("DELETE FROM votes WHERE work=? AND voter=?", (work, v))
    else:
        conn.execute(
            "INSERT INTO votes (work, voter, dir, at) VALUES (?,?,?,?) "
            "ON CONFLICT(work, voter) DO UPDATE SET dir=excluded.dir, at=excluded.at",
            (work, v, direction, now()))
    conn.commit()
    out = tally(work)
    out["mine"] = direction
    return jsonify(out)


# ---------- API: комментарии ----------

def shape(row, admin=False):
    d = {
        "id": row["id"],
        "name": (row["name"] or "").strip() or "anonymous",
        "body": row["body"],
        "at": row["at"],
        "photo": f"/uploads/{row['photo']}" if row["photo"] and row["approved"] else None,
    }
    if row["photo"] and not row["approved"]:
        d["photoPending"] = True
    if admin:
        d["approved"] = bool(row["approved"])
        d["hidden"] = bool(row["hidden"])
        d["rawPhoto"] = f"/uploads/{row['photo']}" if row["photo"] else None
    return d


@app.get("/api/comments")
def get_comments():
    try:
        work = int(request.args.get("work", ""))
    except ValueError:
        return jsonify({"error": "no such work"}), 400
    if not valid_work(work):
        return jsonify({"error": "no such work"}), 400
    admin = is_admin()
    sql = ("SELECT * FROM comments WHERE work=? "
           + ("" if admin else "AND hidden=0 ")
           + "ORDER BY id ASC LIMIT 300")
    rows = db().execute(sql, (work,)).fetchall()
    return jsonify({"comments": [shape(r, admin) for r in rows],
                    "photosNeedApproval": PHOTOS_NEED_APPROVAL})


def save_photo(f):
    """Пересобирает картинку заново: так из файла уходят и EXIF, и всё,
    что могли дописать в конец под видом картинки."""
    raw = f.read(MAX_UPLOAD + 1)
    if len(raw) > MAX_UPLOAD:
        raise ValueError("file over 8 MB")
    try:
        im = Image.open(io.BytesIO(raw))
        im.load()
    except Exception:
        raise ValueError("that is not an image")
    im = im.convert("RGB")
    im.thumbnail((MAX_SIDE, MAX_SIDE), Image.LANCZOS)
    name = f"{int(time.time())}-{secrets.token_hex(8)}.jpg"
    im.save(UPLOADS / name, "JPEG", quality=82, optimize=True)
    return name


@app.post("/api/comments")
def post_comment():
    try:
        work = int(request.form.get("work", ""))
    except ValueError:
        return jsonify({"error": "no such work"}), 400
    if not valid_work(work):
        return jsonify({"error": "no such work"}), 400

    body = (request.form.get("body") or "").strip()
    name = (request.form.get("name") or "").strip()[:MAX_NAME]
    if not body:
        return jsonify({"error": "empty comment"}), 400
    if len(body) > MAX_BODY:
        return jsonify({"error": f"longer than {MAX_BODY} characters"}), 400

    ip = client_ip()
    recent = db().execute(
        "SELECT COUNT(*) n FROM comments WHERE ip=? AND at > ?",
        (ip, datetime.fromtimestamp(time.time() - WINDOW_SECONDS,
                                    timezone.utc).isoformat(timespec="seconds"))
    ).fetchone()["n"]
    if recent >= COMMENTS_PER_WINDOW:
        return jsonify({"error": "too often, wait a little"}), 429

    photo, approved = None, 1
    f = request.files.get("photo")
    if f and f.filename:
        try:
            photo = save_photo(f)
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        approved = 0 if PHOTOS_NEED_APPROVAL else 1

    conn = db()
    cur = conn.execute(
        "INSERT INTO comments (work, name, body, photo, approved, hidden, ip, at) "
        "VALUES (?,?,?,?,?,0,?,?)",
        (work, name, body, photo, approved, ip, now()))
    conn.commit()
    row = conn.execute("SELECT * FROM comments WHERE id=?", (cur.lastrowid,)).fetchone()
    return jsonify({"comment": shape(row), "tally": tally(work)}), 201


# ---------- API: модерация ----------

@app.post("/api/admin/comment/<int:cid>")
def moderate(cid):
    if not is_admin():
        abort(404)
    action = (request.get_json(silent=True) or {}).get("action")
    conn = db()
    if action == "approve":
        conn.execute("UPDATE comments SET approved=1, hidden=0 WHERE id=?", (cid,))
    elif action == "hide":
        conn.execute("UPDATE comments SET hidden=1 WHERE id=?", (cid,))
    elif action == "show":
        conn.execute("UPDATE comments SET hidden=0 WHERE id=?", (cid,))
    elif action == "delete":
        row = conn.execute("SELECT photo FROM comments WHERE id=?", (cid,)).fetchone()
        if row and row["photo"]:
            (UPLOADS / row["photo"]).unlink(missing_ok=True)
        conn.execute("DELETE FROM comments WHERE id=?", (cid,))
    else:
        return jsonify({"error": "неизвестное действие"}), 400
    conn.commit()
    return jsonify({"ok": True})


@app.post("/api/subscribe")
def subscribe():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email") or "").strip().lower()[:120]
    if not EMAIL_RE.match(email):
        return jsonify({"error": "check the address"}), 400

    ip = client_ip()
    recent = db().execute(
        "SELECT COUNT(*) n FROM subs WHERE ip=? AND at > ?",
        (ip, datetime.fromtimestamp(time.time() - 3600,
                                    timezone.utc).isoformat(timespec="seconds"))
    ).fetchone()["n"]
    if recent >= 5:
        return jsonify({"error": "too often"}), 429

    conn = db()
    conn.execute("INSERT INTO subs (email, at, ip) VALUES (?,?,?) "
                 "ON CONFLICT(email) DO NOTHING", (email, now(), ip))
    conn.commit()
    return jsonify({"ok": True}), 201


@app.get("/api/admin/subs")
def list_subs():
    if not is_admin():
        abort(404)
    rows = db().execute("SELECT email, at FROM subs ORDER BY at DESC LIMIT 2000")
    return jsonify({"subs": [dict(r) for r in rows]})


@app.get("/api/admin/stats")
def stats():
    """Сколько людей, откуда и что смотрят."""
    if not is_admin():
        abort(404)
    days = db().execute(
        "SELECT day, SUM(n) n FROM hits GROUP BY day ORDER BY day DESC LIMIT 60").fetchall()
    pages = db().execute(
        "SELECT path, SUM(n) n FROM hits GROUP BY path ORDER BY n DESC LIMIT 40").fetchall()
    refs = db().execute(
        "SELECT ref, SUM(n) n FROM hits WHERE ref != '' "
        "GROUP BY ref ORDER BY n DESC LIMIT 40").fetchall()
    total = db().execute("SELECT COALESCE(SUM(n),0) n FROM hits").fetchone()["n"]
    subs = db().execute("SELECT COUNT(*) n FROM subs").fetchone()["n"]
    return jsonify({
        "total": total, "subs": subs,
        "days": [dict(r) for r in days],
        "pages": [dict(r) for r in pages],
        "refs": [dict(r) for r in refs],
    })


@app.get("/api/admin/content")
def get_content():
    """Отдаёт правимый файл целиком: тексты, витрину или состав серий."""
    if not is_admin():
        abort(404)
    name = request.args.get("file", "")
    if name not in EDITABLE:
        return jsonify({"error": "этот файл не правится"}), 400
    data = load_content(name)
    if data is None:
        return jsonify({"error": "файла нет"}), 404
    return jsonify({"file": name, "data": data})


@app.put("/api/admin/content")
def put_content():
    if not is_admin():
        abort(404)
    name = request.args.get("file", "")
    if name not in EDITABLE:
        return jsonify({"error": "этот файл не правится"}), 400
    body = request.get_json(silent=True)
    if not isinstance(body, (dict, list)):
        return jsonify({"error": "нужен объект или список"}), 400

    if name == "series.json":
        # состав серий определяет, какие номера вообще существуют;
        # пустая или битая структура уронила бы весь сайт
        if not isinstance(body, dict) or not body:
            return jsonify({"error": "серии не могут быть пустыми"}), 400
        known = {x["n"] for x in (load_content("manifest.json") or [])}
        for nm, ns in body.items():
            if not isinstance(ns, list) or not all(isinstance(n, int) for n in ns):
                return jsonify({"error": f"серия {nm}: нужен список номеров"}), 400
            bad = [n for n in ns if known and n not in known]
            if bad:
                return jsonify({"error": f"нет таких работ: {bad[:5]}"}), 400

    (CONTENT_DIR / name).write_text(json.dumps(body, ensure_ascii=False, indent=1))
    if name == "series.json":
        global VALID
        VALID = valid_set()

    ok, log = rebuild()
    return jsonify({"saved": name, "rebuilt": ok, "log": log}), (200 if ok else 500)


@app.post("/api/admin/rebuild")
def do_rebuild():
    if not is_admin():
        abort(404)
    ok, log = rebuild()
    return jsonify({"rebuilt": ok, "log": log}), (200 if ok else 500)


@app.get("/api/admin/catalog")
def catalog():
    """Все существующие работы — чтобы в админке было из чего выбирать."""
    if not is_admin():
        abort(404)
    man = load_content("manifest.json") or []
    series = load_content("series.json") or {}
    where = {n: nm for nm, ns in series.items() for n in ns}
    return jsonify({"works": [
        {"n": x["n"], "kind": x["kind"], "title": x["title"][:70],
         "series": where.get(x["n"])}
        for x in man
    ]})


@app.get("/api/admin/pending")
def pending():
    if not is_admin():
        abort(404)
    rows = db().execute(
        "SELECT * FROM comments WHERE (photo IS NOT NULL AND approved=0) OR hidden=1 "
        "ORDER BY id DESC LIMIT 200").fetchall()
    return jsonify({"comments": [shape(r, True) for r in rows]})


# ---------- статика ----------

@app.get("/uploads/<path:name>")
def uploaded(name):
    if not re.fullmatch(r"[0-9]+-[0-9a-f]{16}\.jpg", name):
        abort(404)
    return send_from_directory(UPLOADS, name, max_age=31536000)


EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s.]{1,63}(\.[^@\s.]{1,63})+$")


def note_hit(path):
    """Считает просмотр страницы. Никогда не роняет выдачу: счётчик —
    не та вещь, ради которой стоит показать посетителю ошибку."""
    try:
        ref = ""
        r = request.headers.get("Referer", "")
        if r:
            m = re.match(r"https?://([^/:]+)", r)
            host = m.group(1) if m else ""
            if host and host != request.host.split(":")[0]:
                ref = host[:80]          # только домен, без пути и меток
        conn = db()
        conn.execute(
            "INSERT INTO hits (day, path, ref, n) VALUES (?,?,?,1) "
            "ON CONFLICT(day, path, ref) DO UPDATE SET n = n + 1",
            (datetime.now(timezone.utc).strftime("%Y-%m-%d"), path[:120], ref))
        conn.commit()
    except Exception:
        pass


def page_root(path):
    """Пересобранная админкой страница на томе главнее запечённой в образ."""
    return BUILT_DIR if (BUILT_DIR / path).is_file() else SITE_DIR


def html_response(path):
    note_hit(path)
    """HTML не кешируем: страницы пересобираются при каждом деплое и после
    каждой правки в админке, а длинный кеш означал бы, что посетитель
    неделю видит старое."""
    resp = send_from_directory(page_root(path), path)
    resp.headers["Cache-Control"] = "no-cache"
    return resp


@app.get("/")
def home():
    return html_response("index.html")


# Наружу отдаётся только сайт. В боевом образе в /srv и так нет ничего
# лишнего, но при запуске с SITE_DIR на папку проекта без этого списка
# уехали бы и исходники сервера, и _select с путями к оригиналам.
# w/ — страница каждой работы: её можно дать ссылкой и она попадает в поиск
OPEN_DIRS = ("assets/", "s/", "w/")
OPEN_FILES = {"index.html", "deck.html", "shows.html",
              "favicon.ico", "robots.txt", "sitemap.xml"}


@app.get("/<path:path>")
def static_files(path):
    if path not in OPEN_FILES and not path.startswith(OPEN_DIRS):
        abort(404)
    full = (SITE_DIR / path).resolve()
    if not str(full).startswith(str(SITE_DIR.resolve())):
        abort(404)
    if full.is_dir():
        full = full / "index.html"
        path = f"{path}/index.html"
    if path.endswith(".html"):
        # страница могла появиться только на томе — например, новая серия,
        # созданная из админки; в образе её нет
        if not full.is_file() and not (BUILT_DIR / path).is_file():
            abort(404)
        return html_response(path)
    if not full.is_file():
        abort(404)
    # css и js версионированы через ?v= в ссылках, поэтому им можно долго;
    # картинки и видео не меняются между деплоями вовсе
    age = 604800 if path.startswith(("assets/css", "assets/js")) else 31536000
    resp = send_from_directory(SITE_DIR, path, max_age=age)
    return resp


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "not found"}), 404


@app.errorhandler(413)
def too_big(_e):
    return jsonify({"error": "file over 8 MB"}), 413


if __name__ == "__main__":
    app.run("0.0.0.0", int(os.environ.get("PORT", 8080)))
