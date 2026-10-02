# Templates

Tested Hyperframes compositions from a real `/promo` run, with the copy replaced by placeholders. Timings,
asset names and crops come from that run; rewrite them for your app and keep the structure.

Set up a project per output shape (see `references/step-5-compose.md`):

```bash
C=<output-dir>/composition
mkdir -p $C/shared/assets && cp -R <skill-dir>/kit $C/shared/kit
for f in launch reel preview overlay hooks screens; do
  mkdir -p $C/$f && cp <skill-dir>/kit/templates/$f.html $C/$f/index.html
  ln -s ../shared/assets $C/$f/assets && ln -s ../shared/kit $C/$f/kit
  cp <skill-dir>/kit/templates/hyperframes.json $C/$f/ && echo "{\"id\":\"$f\",\"name\":\"$f\"}" > $C/$f/meta.json
done
cp <skill-dir>/kit/templates/box.template.html <skill-dir>/kit/templates/make_box.py $C/ && (cd $C && python3 make_box.py)  # feed + square
```

| File | Output | Notes |
|---|---|---|
| `launch.html` | 1920×1080 launch video | Hook → reveal → highlights → punchline/outro, sound effects wired in; cuts on a 100 BPM bar grid; audio goes between `<!-- AUDIO:BEGIN/END -->` via `scripts/audio_cues.py` (see `launch.cues.example.json`) |
| `reel.html` | 1080×1920 ad | `hook` variable picks the hook variant; footage at root level, captions z-indexed above |
| `box.template.html` + `make_box.py` | 1080×1350 feed, 1080×1080 square | one layout, sizes per format in `make_box.py` |
| `preview.html` | 886×1920 App Store preview | captures only, caption band, strongest frame at 5 s |
| `overlay.html` | transparent phone + feature | render `--format mov` and `--format webm` |
| `hooks.html` | transparent hook caption | one render per hook |
| `screens.html` | 1320×2868 screenshots | `n` variable; render `--format png-sequence --fps 1`, then strip alpha |
