# Step 6: Render, finish and deliver

## Render

```bash
cd composition/reel && for h in a b c; do npx hyperframes render --quality delivery --variables "{\"hook\":\"$h\"}" -o ../../work/renders/reel-$h.mp4; done
cd ../feed && npx hyperframes render --quality delivery -o ../../work/renders/feed.mp4      # same for square, preview
cd ../overlay && npx hyperframes render --format mov -o ../../work/renders/phone-overlay.mov && npx hyperframes render --format webm -o ../../work/renders/phone-overlay.webm
cd ../screens && npx hyperframes render --format png-sequence --fps 1 --variables '{"n":"1"}' -o ../../work/renders/screen-1
```

A 15 s 1080×1920 render takes about 30–40 s on an M1. Batch them in one background script.

## Finish to platform profiles

```bash
S=<skill-dir>/scripts; F=<output-dir>/<feature>
python3 $S/finalize.py work/renders/reel-a.mp4 $F/ads/<feature>-reel-hook-a.mp4 --profile ad --music work/gen/music.mp3 --poster-at 1.6
python3 $S/finalize.py work/renders/feed.mp4   $F/ads/<feature>-feed.mp4   --profile ad --music work/gen/music.mp3 --poster-at 9.5
python3 $S/finalize.py work/renders/preview.mp4 $F/app-preview/<feature>-preview.mp4 --profile preview --music work/gen/music.mp3
```

- **Poster:** pick the strongest *settled* frame (text fully in, not mid-transition), usually the hook's payoff. `finalize.py` bakes it as frame 0 and writes the `.jpg` for platforms that accept a custom thumbnail.
- **Preview poster:** App Store Connect uses the frame at 5 s by default; the storyboard already put the strongest frame there. Mention it in the README so the user doesn't change it.
- **No music?** `finalize.py` adds a silent stereo track, so every file has the audio track platforms expect.

Screenshots: copy each rendered PNG to `screenshots/NN-<slug>.png` and remove alpha:

```bash
ffmpeg -v error -y -i work/renders/screen-1/frame_000000.png -pix_fmt rgb24 screenshots/01-<slug>.png   # use the actual frame file name
```

UGC kit (per feature):

```
ugc-kit/clips/    trimmed CFR captures, no text (from work/capture), H.264
ugc-kit/reveal/   before/after moments cut from the captures (the dissolve, the wipe), H.264
ugc-kit/overlays/ phone-overlay.mov (ProRes 4444, alpha) + .webm (VP9, alpha)
ugc-kit/hooks/    hook-a.mov/.webm … (transparent captions)
ugc-kit/audio/    music bed (+ voiceover if any)
ugc-kit/captions/ .srt for voiceover (from `npx hyperframes transcribe`)
```

Use `.mov` for Premiere/Final Cut/DaVinci/CapCut desktop, `.webm` for web tools and CapCut web.

## ad-copy.md

Per feature, every line marked with the grounded claim it uses:

- Meta: 3 primary texts (≤125 chars, the first 44 must work alone), 3 headlines (≤40), 1 description.
- TikTok: 3 ad texts (≤100, no hashtags, links or @).
- Google App campaigns: 5 headlines (≤30), 5 descriptions (≤90).
- App Store: preview overlay lines, screenshot captions, and suggested promotional text (≤170).
- UGC creator brief: the hook lines, the 3 beats to show, claims allowed, claims **not** allowed, the AI-disclosure note if relevant.

Count characters (`python3 -c "print(len('...'))"`), don't estimate.

## README.md in the output

A table of every deliverable: file, size/length, where to upload it, and notes (poster time, AI content present, music license, "Illustrative example" labels, anything that needs real app output before shipping).

## Gate

```bash
python3 <skill-dir>/scripts/check_specs.py <output-dir>
```

Zero FAILs. Then send the user a contact sheet of the ads' posters and the screenshots, and tell them: where everything is, the one-sentence creative angle per feature, what's AI-generated, what wasn't tested (for example: upload to a real ad account), and offer to re-cut a hook, try another tone, or localize.
