#!/usr/bin/env python3
"""Собирает контактный лист всех работ Midjourney: манифест + превью."""
import json, os, re, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HOME = Path.home()
ROOTS = [HOME / "Downloads", HOME / "Desktop", HOME / "Pictures"]
OUT = HOME / "Downloads" / "works-site" / "_select"
THUMBS = OUT / "thumbs"
THUMBS.mkdir(parents=True, exist_ok=True)

UUID = re.compile(r"_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}(_\d+)?$", re.I)
MJRUN = re.compile(r"httpss?\.mj\.run\S*?(?=_|$)", re.I)
FLAG = re.compile(r"--\w+(_[\w.:/]+)?")

def pretty(stem: str) -> str:
    s = stem[len("Dlorian_"):] if stem.startswith("Dlorian_") else stem
    s = UUID.sub("", s)
    s = MJRUN.sub("", s)
    s = FLAG.sub("", s)
    s = s.replace("_", " ")
    s = re.sub(r"\s+", " ", s).strip(" -.")
    return s or "untitled"

# --- сбор файлов ---
files = []
seen = set()
for root in ROOTS:
    if not root.exists():
        continue
    for p in root.rglob("Dlorian_*"):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".png", ".jpg", ".jpeg", ".mp4", ".gif"}:
            continue
        key = (p.name, p.stat().st_size)
        if key in seen:          # одинаковые копии в разных папках
            continue
        seen.add(key)
        files.append(p)

files.sort(key=lambda p: (p.stat().st_mtime, p.name))
print(f"найдено файлов: {len(files)}")

def make_thumb(job):
    i, p = job
    out = THUMBS / f"{i:03d}.jpg"
    if out.exists() and out.stat().st_size > 0:
        return True
    try:
        if p.suffix.lower() == ".mp4":
            subprocess.run(
                ["ffmpeg", "-v", "error", "-ss", "1", "-i", str(p), "-frames:v", "1",
                 "-vf", "scale=560:-2", "-q:v", "4", "-y", str(out)],
                check=True, capture_output=True, timeout=60)
            if not out.exists() or out.stat().st_size == 0:   # видео короче 1с
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-i", str(p), "-frames:v", "1",
                     "-vf", "scale=560:-2", "-q:v", "4", "-y", str(out)],
                    check=True, capture_output=True, timeout=60)
        else:
            subprocess.run(
                ["sips", "-s", "format", "jpeg", "-s", "formatOptions", "70",
                 "--resampleWidth", "560", str(p), "--out", str(out)],
                check=True, capture_output=True, timeout=60)
        return out.exists() and out.stat().st_size > 0
    except Exception as e:
        print(f"  ошибка {p.name}: {e}", file=sys.stderr)
        return False

jobs = list(enumerate(files, 1))
with ThreadPoolExecutor(max_workers=8) as ex:
    results = list(ex.map(make_thumb, jobs))
print(f"превью готово: {sum(results)}/{len(results)}")

# --- размеры оригиналов ---
def dims(p):
    try:
        if p.suffix.lower() == ".mp4":
            r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0",
                                "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", str(p)],
                               capture_output=True, text=True, timeout=30)
            w, h = r.stdout.strip().split("x")[:2]
            return int(w), int(h)
        r = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", str(p)],
                           capture_output=True, text=True, timeout=30)
        w = int(re.search(r"pixelWidth:\s*(\d+)", r.stdout).group(1))
        h = int(re.search(r"pixelHeight:\s*(\d+)", r.stdout).group(1))
        return w, h
    except Exception:
        return 0, 0

with ThreadPoolExecutor(max_workers=8) as ex:
    all_dims = list(ex.map(dims, files))

manifest = []
for (i, p), (w, h), ok in zip(jobs, all_dims, results):
    manifest.append({
        "n": i,
        "file": str(p),
        "name": p.name,
        "title": pretty(p.stem),
        "kind": "video" if p.suffix.lower() == ".mp4" else "image",
        "w": w, "h": h,
        "bytes": p.stat().st_size,
        "mtime": int(p.stat().st_mtime),
        "thumb": f"thumbs/{i:03d}.jpg" if ok else None,
    })

(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1))
print(f"манифест: {OUT/'manifest.json'}")
print(f"видео: {sum(1 for m in manifest if m['kind']=='video')}, картинок: {sum(1 for m in manifest if m['kind']=='image')}")
