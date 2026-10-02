#!/usr/bin/env python3
"""Pull frames from a rendered video into one review sheet, with the platform safe zone drawn on.

Usage: review_frames.py <video> --out sheet.png [--at 0.5,2,4.5 | --every 1.0] [--zone reel|stories|none] [--width 300] [--cols 6]
  --zone reel     Reels/TikTok: top 14%, bottom 35%, sides 6% (red shading = keep text, faces and logos out)
  --zone stories  Stories: top 14%, bottom 20%, sides 6%
Each tile is labeled with its timestamp. Needs ffmpeg and Pillow.
"""
import argparse, os, subprocess, tempfile
from PIL import Image, ImageDraw

ZONES = {"reel": (0.14, 0.35, 0.06), "stories": (0.14, 0.20, 0.06), "none": None}

ap = argparse.ArgumentParser()
ap.add_argument("video"); ap.add_argument("--out", required=True)
ap.add_argument("--at", help="comma-separated seconds")
ap.add_argument("--every", type=float, default=1.0)
ap.add_argument("--zone", default="reel", choices=ZONES)
ap.add_argument("--width", type=int, default=300)
ap.add_argument("--cols", type=int, default=6)
a = ap.parse_args()

dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.video],
                           capture_output=True, text=True, check=True).stdout)
times = [float(t) for t in a.at.split(",")] if a.at else [round(i * a.every + a.every / 2, 2) for i in range(int(dur / a.every))]

tiles = []
with tempfile.TemporaryDirectory() as tmp:
    for t in times:
        p = os.path.join(tmp, f"{t:.2f}.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(min(t, dur - 0.05)), "-i", a.video, "-frames:v", "1", p], check=True)
        im = Image.open(p).convert("RGB")
        W, H = im.size
        if ZONES[a.zone]:
            top, bottom, side = ZONES[a.zone]
            ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(ov)
            for box in [(0, 0, W, H * top), (0, H * (1 - bottom), W, H), (0, 0, W * side, H), (W * (1 - side), 0, W, H)]:
                d.rectangle(box, fill=(255, 0, 0, 60))
            im = Image.alpha_composite(im.convert("RGBA"), ov).convert("RGB")
        im = im.resize((a.width, int(H * a.width / W)))
        ImageDraw.Draw(im).text((8, 8), f"{t:.2f}s", fill=(255, 255, 0))
        tiles.append(im)

cols = min(a.cols, len(tiles))
rows = -(-len(tiles) // cols)
w, h = tiles[0].size
sheet = Image.new("RGB", (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), "white")
for i, im in enumerate(tiles):
    sheet.paste(im, ((i % cols) * (w + 8), (i // cols) * (h + 8)))
sheet.save(a.out)
print(f"wrote {a.out} ({len(tiles)} frames)")
