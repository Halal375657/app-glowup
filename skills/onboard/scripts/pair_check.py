#!/usr/bin/env python3
"""Check that an edited image lines up with its source, so dissolves and sliders don't shift.

Usage: pair_check.py <a.png> <b.png> [--box x0,y0,x1,y1] [--out side_by_side.png]
  --box is the region the edit was meant to change (in pixels of the source image).
  Prints the mean pixel difference (0-255) inside and outside that region.
  Outside should be small (under ~4); inside clearly larger.
Needs Pillow (pip install pillow).
"""
import argparse
from PIL import Image, ImageChops, ImageStat

ap = argparse.ArgumentParser()
ap.add_argument("a"); ap.add_argument("b")
ap.add_argument("--box", help="x0,y0,x1,y1 of the edited region")
ap.add_argument("--out")
args = ap.parse_args()

a = Image.open(args.a).convert("RGB")
b = Image.open(args.b).convert("RGB")
if a.size != b.size:
    print(f"sizes differ {a.size} vs {b.size}; resizing the second to match")
    b = b.resize(a.size)

diff = ImageChops.difference(a, b).convert("L")
total = ImageStat.Stat(diff).mean[0]
if args.box:
    box = tuple(int(v) for v in args.box.split(","))
    inside = ImageStat.Stat(diff.crop(box)).mean[0]
    mask = Image.new("L", a.size, 255)
    mask.paste(0, box)
    outside = ImageStat.Stat(diff, mask).mean[0]
    verdict = "OK" if outside < 4 and inside > outside * 1.5 else "CHECK: edit may have moved more than the target region"
    print(f"inside: {inside:.2f}  outside: {outside:.2f}  -> {verdict}")
else:
    print(f"mean difference: {total:.2f}")

if args.out:
    crop = tuple(int(v) for v in args.box.split(",")) if args.box else (0, 0, *a.size)
    ca, cb = a.crop(crop), b.crop(crop)
    s = Image.new("RGB", (ca.width * 2 + 10, ca.height), "white")
    s.paste(ca, (0, 0)); s.paste(cb, (ca.width + 10, 0))
    s.save(args.out)
    print(f"wrote {args.out}")
