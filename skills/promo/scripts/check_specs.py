#!/usr/bin/env python3
"""Check every deliverable in a /promo output folder against platform specs (references/specs.md).

Usage: check_specs.py <output-dir>
Exit code 1 if anything FAILs. WARNs are worth reading but don't block.

Files are recognized by location and name:
  launch/*.mp4 (1920x1080 | 1080x1920 | 1080x1080, 15-25 s, poster, share-copy.txt)
  */ads/*-reel*.mp4 (1080x1920)  */ads/*-feed*.mp4 (1080x1350)  */ads/*-square*.mp4 (1080x1080)
  */app-preview/*.mp4            screenshots/*.png|jpg
  */ugc-kit/overlays/*.mov|webm  */ugc-kit/clips|reveal/*.mp4
"""
import json, os, subprocess, sys
from fnmatch import fnmatch

root = sys.argv[1] if len(sys.argv) > 1 else sys.exit(__doc__)
fails = warns = checked = 0


def report(level, path, msg):
    global fails, warns
    fails += level == "FAIL"
    warns += level == "WARN"
    print(f"  {level}  {os.path.relpath(path, root)}: {msg}")


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
                         capture_output=True, text=True).stdout
    d = json.loads(out or "{}")
    v = next((s for s in d.get("streams", []) if s["codec_type"] == "video"), {})
    a = next((s for s in d.get("streams", []) if s["codec_type"] == "audio"), None)
    return d, v, a


def fps(v):
    n, d = v.get("avg_frame_rate", "0/1").split("/")
    return float(n) / float(d) if float(d) else 0


def moov_first(path):
    with open(path, "rb") as f:
        head = f.read(1 << 20)
    m, d = head.find(b"moov"), head.find(b"mdat")
    return m != -1 and (d == -1 or m < d)


def check_video(path, size, dur_range, max_fps=None, cfr=30, audio=True, extra=None):
    d, v, a = probe(path)
    if not v:
        return report("FAIL", path, "no video stream")
    w, h, dur = v.get("width"), v.get("height"), float(d["format"].get("duration", 0))
    mb = os.path.getsize(path) / 1e6
    if (w, h) != size:
        report("FAIL", path, f"size {w}x{h}, expected {size[0]}x{size[1]}")
    if not dur_range[0] <= dur <= dur_range[1]:
        report("FAIL", path, f"duration {dur:.2f}s outside {dur_range[0]}-{dur_range[1]}s")
    if v.get("codec_name") != "h264":
        report("FAIL", path, f"codec {v.get('codec_name')}, expected h264")
    if v.get("pix_fmt") != "yuv420p":
        report("FAIL", path, f"pixel format {v.get('pix_fmt')}, expected yuv420p")
    f = fps(v)
    if cfr and abs(f - cfr) > 0.05:
        report("FAIL", path, f"frame rate {f:.2f}, expected constant {cfr}")
    if max_fps and f > max_fps + 0.01:
        report("FAIL", path, f"frame rate {f:.2f} above {max_fps}")
    if audio:
        if not a:
            report("FAIL", path, "no audio track")
        elif a.get("codec_name") != "aac" or a.get("channels") != 2:
            report("FAIL", path, f"audio {a.get('codec_name')} {a.get('channels')}ch, expected AAC stereo")
    if mb > 500:
        report("FAIL", path, f"{mb:.0f} MB, over 500 MB")
    if not moov_first(path):
        report("WARN", path, "not faststart (moov after mdat); slower to start streaming")
    if extra:
        extra(path, d, v, a)
    return dur


def preview_extra(path, d, v, a):
    if v.get("profile") != "High" or int(v.get("level", 99)) > 40:
        report("FAIL", path, f"H.264 {v.get('profile')} level {v.get('level')}, expected High <= 4.0")
    br = int(d["format"].get("bit_rate", 0)) / 1e6
    if not 8 <= br <= 14:
        report("WARN", path, f"bitrate {br:.1f} Mbps, Apple asks for 10-12")
    if a and (int(a.get("bit_rate", 0)) < 240_000 or a.get("sample_rate") not in ("44100", "48000")):
        report("FAIL", path, f"audio {int(a.get('bit_rate', 0)) // 1000} kbps {a.get('sample_rate')} Hz, expected 256 kbps 44.1/48 kHz")


def check_alpha(path):
    _, v, _ = probe(path)
    if path.endswith(".mov"):
        ok = v.get("codec_name") == "prores" and "a" in v.get("pix_fmt", "").replace("yuv", "")
        if not ok:
            report("FAIL", path, f"{v.get('codec_name')} {v.get('pix_fmt')}, expected ProRes 4444 with alpha")
    else:
        tags = {k.lower(): val for k, val in v.get("tags", {}).items()}
        if v.get("codec_name") != "vp9" or tags.get("alpha_mode") != "1":
            report("FAIL", path, f"{v.get('codec_name')} alpha_mode={tags.get('alpha_mode')}, expected VP9 with alpha")


def check_image(path, sizes):
    _, v, _ = probe(path)
    w, h, pf = v.get("width"), v.get("height"), v.get("pix_fmt", "")
    if (w, h) not in sizes:
        report("FAIL", path, f"size {w}x{h}, expected one of {sizes}")
    if "a" in pf.replace("yuv", "") or pf in ("rgba", "ya8", "pal8a"):
        report("FAIL", path, f"has alpha ({pf}); App Store screenshots must not")


AD_SIZES = {"reel": (1080, 1920), "feed": (1080, 1350), "square": (1080, 1080)}
SHOT_SIZES = [(1320, 2868), (2868, 1320), (1290, 2796), (2796, 1290), (1260, 2736), (2736, 1260)]
LAUNCH_SIZES = {(1920, 1080), (1080, 1920), (1080, 1080)}
PREVIEW_SIZES = {(886, 1920), (1920, 886), (1080, 1920), (1920, 1080)}

screens = []
for dp, dirs, files in os.walk(root):
    dirs[:] = [x for x in dirs if x not in ("work", "composition", "node_modules")]
    for fn in sorted(files):
        p = os.path.join(dp, fn)
        rel = os.path.relpath(p, root)
        kind = None
        if fnmatch(rel, "launch/*.mp4"):
            checked += 1
            _, v, _ = probe(p)
            size = (v.get("width"), v.get("height"))
            check_video(p, size if size in LAUNCH_SIZES else (1920, 1080), (15, 25))
            if not os.path.exists(os.path.splitext(p)[0] + ".jpg"):
                report("FAIL", p, "no poster .jpg (bake it with finalize.py --poster-at)")
            share = os.path.join(os.path.dirname(p), "share-copy.txt")
            if not os.path.exists(share):
                report("FAIL", share, "missing share copy")
            elif not 0 < len(open(share).read().strip()) <= 400:
                report("WARN", share, "share copy should be 1-3 sentences")
        elif fnmatch(rel, "*/ads/*.mp4"):
            kind = next((k for k in AD_SIZES if f"-{k}" in fn), None)
            if not kind:
                report("WARN", p, "ad file name doesn't say reel/feed/square; skipped")
                continue
            checked += 1
            check_video(p, AD_SIZES[kind], (5, 60))
            if not os.path.exists(os.path.splitext(p)[0] + ".jpg"):
                report("FAIL", p, "no poster .jpg next to the ad (bake it with finalize.py --poster-at)")
        elif fnmatch(rel, "*/app-preview/*.mp4") or fnmatch(rel, "*/app-preview/*.mov"):
            checked += 1
            _, v, _ = probe(p)
            size = (v.get("width"), v.get("height"))
            check_video(p, size if size in PREVIEW_SIZES else (886, 1920), (15, 30), max_fps=30, cfr=None, extra=preview_extra)
        elif fnmatch(rel, "screenshots/*.png") or fnmatch(rel, "screenshots/*.jp*g"):
            checked += 1
            screens.append(p)
            check_image(p, SHOT_SIZES)
        elif fnmatch(rel, "*/ugc-kit/overlays/*.mov") or fnmatch(rel, "*/ugc-kit/overlays/*.webm") or fnmatch(rel, "*/ugc-kit/hooks/*.mov") or fnmatch(rel, "*/ugc-kit/hooks/*.webm"):
            checked += 1
            check_alpha(p)
        elif fnmatch(rel, "*/ugc-kit/clips/*.mp4") or fnmatch(rel, "*/ugc-kit/reveal/*.mp4"):
            checked += 1
            _, v, _ = probe(p)
            check_video(p, (v.get("width"), v.get("height")), (0.5, 600), audio=False)

if len(screens) > 10:
    report("FAIL", os.path.join(root, "screenshots"), f"{len(screens)} screenshots; the App Store allows 10")
for need in ("ad-copy.md", "README.md"):
    if not os.path.exists(os.path.join(root, need)):
        report("FAIL", os.path.join(root, need), "missing")
if os.path.isdir(os.path.join(root, "work")) and not os.path.exists(os.path.join(root, "work", "licenses.md")):
    report("FAIL", os.path.join(root, "work/licenses.md"), "missing: record the source and license of every asset")

print(f"\n{checked} files checked: {fails} fail, {warns} warn")
sys.exit(1 if fails else 0)
