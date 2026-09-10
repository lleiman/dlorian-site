#!/usr/bin/env python3
"""Собирает зацикленный монтаж для первого экрана из видеоработ."""
import json, subprocess, tempfile
from pathlib import Path
from PIL import Image, ImageStat

SITE = Path.home() / "Downloads" / "works-site"
SEL = SITE / "_select"
manifest = {x["n"]: x for x in json.loads((SEL / "manifest.json").read_text())}
series = json.loads((SEL / "series.json").read_text())

CUT = 1.1          # секунд с ролика
W, H = 1280, 720

def brightness(n):
    p = SEL / "thumbs_sm" / f"{n:03d}.jpg"
    if not p.exists():
        return 0
    r, g, b = ImageStat.Stat(Image.open(p).convert("RGB")).mean
    return 0.2126 * r + 0.7152 * g + 0.0722 * b

# берём по паре самых светлых роликов из каждой серии — монтаж должен
# читаться, а не быть чёрным прямоугольником; порядок серий сохраняем
picked = []
for nm, ns in series.items():
    vids = [n for n in ns if manifest[n]["kind"] == "video"]
    vids.sort(key=brightness, reverse=True)
    picked.extend(vids[:2])

print(f"роликов в монтаже: {len(picked)}  (~{len(picked)*CUT:.0f}s)")

tmp = Path(tempfile.mkdtemp())
parts = []
for i, n in enumerate(picked):
    src = SITE / "assets/vid" / f"{n:03d}.mp4"
    out = tmp / f"{i:03d}.mp4"
    # середина ролика: на старте часто ещё нет движения
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(src)], capture_output=True, text=True).stdout.strip() or 2)
    ss = max(0, (dur - CUT) / 2)
    ok = subprocess.run([
        "ffmpeg", "-v", "error", "-ss", f"{ss:.2f}", "-t", f"{CUT}", "-i", str(src),
        "-an", "-vf",
        f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
        f"crop={W}:{H},fps=24,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-y", str(out)
    ], capture_output=True).returncode == 0
    if ok and out.exists():
        parts.append(out)

lst = tmp / "list.txt"
lst.write_text("".join(f"file '{p}'\n" for p in parts))

hero = SITE / "assets/vid/hero.mp4"
subprocess.run([
    "ffmpeg", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
    "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "25",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-y", str(hero)
], capture_output=True)

subprocess.run([
    "ffmpeg", "-v", "error", "-i", str(hero), "-frames:v", "1",
    "-vf", f"scale={W}:-2", "-q:v", "4", "-y",
    str(SITE / "assets/poster/hero.jpg")
], capture_output=True)

d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                    "-of", "csv=p=0", str(hero)], capture_output=True, text=True).stdout.strip()
print(f"склеено {len(parts)} кусков → {hero.name}  "
      f"{hero.stat().st_size/1048576:.1f} MB, {float(d or 0):.1f}s")
