#!/usr/bin/env python3
"""Write a composition's <audio> tags from a cue sheet, so audio is one clean, switchable block.

Usage: audio_cues.py <cues.json> --inject <composition/index.html>
       audio_cues.py <cues.json>                  (print the tags)

The composition marks where audio goes:  <!-- AUDIO:BEGIN --> ... <!-- AUDIO:END -->
Everything between the markers is replaced. An empty or missing layer writes nothing, which is how
"no music" / "no voiceover" / "no sound effects" stays truly silent.

cues.json:
{
  "music": {"src": "assets/music.wav", "start": 0, "duration": 19.2, "volume": 0.8,
            "volume_under_voice": 0.3, "fade_in": 0.2, "fade_out": 1.2},
  "voice": [{"src": "assets/vo-1.wav", "start": 2.6, "volume": 1.0}],
  "sfx":   [{"src": "assets/sfx/pop.mp3", "start": 1.0, "volume": 0.35}]
}
With any voice lines, music plays at volume_under_voice (default 0.3) so speech stays clear;
for per-line ducking use the hyperframes-audio skill's voiceover carve.
"""
import argparse, json, os, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("cues"); ap.add_argument("--inject")
a = ap.parse_args()
c = json.load(open(a.cues))


def tag(id_, src, start, volume, duration=None, fade_in=None, fade_out=None):
    attrs = [f'id="{id_}"', f'src="{src}"', f'data-start="{start:g}"']
    if duration is not None:
        attrs.append(f'data-duration="{duration:g}"')
    attrs.append(f'data-volume="{volume:g}"')
    if fade_in:
        attrs.append(f'data-fade-in="{fade_in:g}"')
    if fade_out:
        attrs.append(f'data-fade-out="{fade_out:g}"')
    return f"      <audio {' '.join(attrs)}></audio>"


lines = []
voice = c.get("voice") or []
m = c.get("music")
if m:
    vol = m.get("volume_under_voice", 0.3) if voice else m.get("volume", 0.8)
    lines.append(tag("music", m["src"], m.get("start", 0), vol, m.get("duration"), m.get("fade_in"), m.get("fade_out")))
for i, v in enumerate(voice, 1):
    lines.append(tag(f"vo-{i}", v["src"], v["start"], v.get("volume", 1.0)))
for i, s in enumerate(c.get("sfx") or [], 1):
    name = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(s["src"]))[0].lower())
    lines.append(tag(f"sfx-{i}-{name}", s["src"], s["start"], s.get("volume", 0.35)))
block = "\n".join(lines)

if not a.inject:
    print(block)
    sys.exit()
html = open(a.inject).read()
pat = re.compile(r"(<!-- AUDIO:BEGIN -->)(.*?)(\s*<!-- AUDIO:END -->)", re.S)
if not pat.search(html):
    sys.exit("no <!-- AUDIO:BEGIN --> ... <!-- AUDIO:END --> markers in " + a.inject)
html = pat.sub(lambda mt: mt.group(1) + ("\n" + block if block else "") + mt.group(3), html)
open(a.inject, "w").write(html)
print(f"{a.inject}: {len(lines)} audio tag(s) — music: {'yes' if m else 'no'}, voice: {len(voice)}, sfx: {len(c.get('sfx') or [])}")
