#!/usr/bin/env python3
"""Add an image to an Xcode asset catalog as an imageset. Uses macOS `sips`, no Python packages needed.

Usage: add_to_assets.py <image> <Assets.xcassets> <name> [--png] [--max 1536] [--quality 85]
  Photos become JPEG (smaller). Pass --png to keep transparency.
"""
import argparse, json, os, subprocess

ap = argparse.ArgumentParser()
ap.add_argument("image"); ap.add_argument("catalog"); ap.add_argument("name")
ap.add_argument("--png", action="store_true")
ap.add_argument("--max", type=int, default=1536, help="longest edge in pixels")
ap.add_argument("--quality", type=int, default=85)
a = ap.parse_args()

ext = "png" if a.png else "jpg"
d = os.path.join(a.catalog, f"{a.name}.imageset")
os.makedirs(d, exist_ok=True)
out = os.path.join(d, f"{a.name}.{ext}")
cmd = ["sips", "-Z", str(a.max), "-s", "format", "png" if a.png else "jpeg"]
if not a.png:
    cmd += ["-s", "formatOptions", str(a.quality)]
subprocess.run(cmd + [a.image, "--out", out], check=True, capture_output=True)
json.dump({"images": [{"filename": os.path.basename(out), "idiom": "universal"}],
           "info": {"author": "xcode", "version": 1}}, open(os.path.join(d, "Contents.json"), "w"), indent=2)
print(f"{out} ({os.path.getsize(out) // 1024} KB)")
