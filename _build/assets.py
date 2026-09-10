#!/usr/bin/env python3
"""Пережимает отобранные работы для веба: JPEG через sips + H.264 через ffmpeg."""
import json, subprocess, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SITE = Path.home() / "Downloads" / "works-site"
SEL = SITE / "_select"
manifest = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}
series = json.loads((SEL / "series.json").read_text())

for d in ("assets/img", "assets/thumb", "assets/vid", "assets/poster"):
    (SITE / d).mkdir(parents=True, exist_ok=True)

def run(cmd, timeout=300):
    try:
        return subprocess.run(cmd, capture_output=True, timeout=timeout).returncode == 0
    except Exception:
        return False

def jpeg(src, dst, maxpx, q):
    if dst.exists() and dst.stat().st_size > 0:
        return True
    return run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", str(q),
                "--resampleHeightWidthMax", str(maxpx), str(src), "--out", str(dst)])

def do_image(n):
    src = Path(manifest[n]["file"])
    a = jpeg(src, SITE / "assets/img" / f"{n:03d}.jpg", 1600, 80)
    b = jpeg(src, SITE / "assets/thumb" / f"{n:03d}.jpg", 760, 72)
    return a and b

def do_video(n):
    src = Path(manifest[n]["file"])
    vid = SITE / "assets/vid" / f"{n:03d}.mp4"
    poster = SITE / "assets/poster" / f"{n:03d}.jpg"
    ok = True
    if not (vid.exists() and vid.stat().st_size > 0):
        ok &= run(["ffmpeg", "-v", "error", "-i", str(src), "-an",
                   "-vf", "scale='min(1280,iw)':-2:flags=lanczos",
                   "-c:v", "libx264", "-preset", "medium", "-crf", "26",
                   "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                   "-y", str(vid)])
    if not (poster.exists() and poster.stat().st_size > 0):
        ok &= run(["ffmpeg", "-v", "error", "-i", str(src), "-frames:v", "1",
                   "-vf", "scale='min(760,iw)':-2:flags=lanczos",
                   "-q:v", "4", "-y", str(poster)])
    return ok

picks = [n for ns in series.values() for n in ns]
images = [n for n in picks if manifest[n]["kind"] == "image"]
videos = [n for n in picks if manifest[n]["kind"] == "video"]
print(f"картинок {len(images)}, видео {len(videos)}", flush=True)

t0 = time.time()
with ThreadPoolExecutor(max_workers=6) as ex:
    ri = list(ex.map(do_image, images))
print(f"картинки: {sum(ri)}/{len(ri)}  ({time.time()-t0:.0f}s)", flush=True)

t1 = time.time()
with ThreadPoolExecutor(max_workers=4) as ex:
    rv = list(ex.map(do_video, videos))
print(f"видео: {sum(rv)}/{len(rv)}  ({time.time()-t1:.0f}s)", flush=True)

if not all(ri):
    print("ПРОВАЛ картинки:", [n for n, ok in zip(images, ri) if not ok][:10], flush=True)
if not all(rv):
    print("ПРОВАЛ видео:", [n for n, ok in zip(videos, rv) if not ok][:10], flush=True)

print("\nвес:", flush=True)
total = 0
for d in ("assets/img", "assets/thumb", "assets/vid", "assets/poster"):
    fs = list((SITE / d).glob("*"))
    b = sum(f.stat().st_size for f in fs)
    total += b
    print(f"  {d:<16} {len(fs):>4} файлов  {b/1048576:>7.1f} MB", flush=True)
print(f"  {'ИТОГО':<16} {'':>4}          {total/1048576:>7.1f} MB", flush=True)
print("DONE", flush=True)
