#!/usr/bin/env python3
"""Lay screenshots side by side to review screens or animation frames at a glance.

Usage: contact_sheet.py <img> [<img> ...] --out sheet.png [--scale 0.35] [--cols N] [--crop x0,y0,x1,y1]
Needs Pillow (pip install pillow).
"""
import argparse
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("images", nargs="+"); ap.add_argument("--out", required=True)
ap.add_argument("--scale", type=float, default=0.35)
ap.add_argument("--cols", type=int, default=0, help="0 = all in one row")
ap.add_argument("--crop", help="x0,y0,x1,y1 applied to every image first")
ap.add_argument("--gap", type=int, default=16)
a = ap.parse_args()

ims = [Image.open(p).convert("RGB") for p in a.images]
if a.crop:
    box = tuple(int(v) for v in a.crop.split(","))
    ims = [im.crop(box) for im in ims]
ims = [im.resize((int(im.width * a.scale), int(im.height * a.scale))) for im in ims]
cols = a.cols or len(ims)
rows = -(-len(ims) // cols)
w, h = max(i.width for i in ims), max(i.height for i in ims)
sheet = Image.new("RGB", (cols * w + (cols - 1) * a.gap, rows * h + (rows - 1) * a.gap), "white")
for n, im in enumerate(ims):
    sheet.paste(im, ((n % cols) * (w + a.gap), (n // cols) * (h + a.gap)))
sheet.save(a.out)
print(f"wrote {a.out} ({sheet.width}x{sheet.height})")
