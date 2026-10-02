# Step 4: Generate supporting assets

Use `<skill-dir>/scripts/fal_run.py` for everything. Check model names first; fal's catalog changes:

```bash
python3 <skill-dir>/scripts/fal_run.py models "image-to-video"
python3 <skill-dir>/scripts/fal_run.py schema elevenlabs/music/v2.5      # input fields
python3 <skill-dir>/scripts/fal_run.py check <endpoint> ...              # key works + prices
```

Save outputs under `work/gen/`, prompts under `work/prompts/`. Look at or listen to every result before using it.

## Images (demo photos, hook art, end-card backgrounds, before/after pairs)

GPT Image 2.5 (`openai/gpt-image-2.5/flare/text-to-image`, `.../flare/edit`). Rules from `/onboard`'s art direction apply: one style lock for the set, the brand hex in the lighting or palette, room left for text, and **pairs made by editing one image**, never two separate generations.

**Demo photos** that go *into* the app (so the app produces real output from them) are the best use: the before is generated, the after is the app's real result. Make them look like real phone photos (natural light, slight imperfection), not studio ads, so the app's result is believable.

```bash
python3 <skill-dir>/scripts/fal_run.py openai/gpt-image-2.5/flare/text-to-image --out work/gen --name demo-01 \
  --in prompt=@work/prompts/demo-01.txt 'image_size={"width":1024,"height":1536}' quality=high
```

## Music (on unless `--no-music`)

One bed per tone, ~30 s, instrumental, with a clear lift where the result lands. Candidates: `elevenlabs/music/v2.5`, `minimax/music-3`. Prompt with mood, BPM, instruments, structure ("0–3 s sparse pluck intro, lift at 3 s, steady groove, soft ending at 15 s, no vocals"). Generate 2 options, pick one. Record the provider and the terms that allow commercial use in `work/licenses.md`, and tell the user to confirm those terms for paid ads.

## Voiceover (only with `--voice`)

- Free and local: `npx hyperframes tts "<line>" --voice af_heart --output work/gen/vo-01.wav` (Kokoro; `--list` for voices).
- Higher quality: `elevenlabs/tts/eleven-v4` on fal.

Write lines that add what the screen doesn't say. Get word timestamps for captions with `npx hyperframes transcribe work/gen/vo-01.wav`.

## B-roll motion (optional)

Image-to-video (`bytedance/seedance-2.5/us/image-to-video`, others via `models`) to animate hook art: a slow push-in on a generated scene, a product-moment loop. Never use it to fake the app's output or UI.

## AI presenter (only with `--avatar`)

Talking-avatar models (`fal-ai/kling-video/ai-avatar/v2/pro`, `fal-ai/longcat-single-avatar/...`) from a generated presenter image + voiceover audio. Hard rules:

- The presenter **demonstrates or explains**; they never claim personal results or pose as a customer ("This app lets you…", not "I fixed my photos with…").
- Generated face only. No real person's or celebrity's likeness.
- Never in App Store previews or screenshots.
- List every file with an AI person in the delivery README, and remind the user to switch on TikTok's AIGC label (Meta labels automatically).

Composite the presenter over the app footage in compose, or deliver it as its own clip in the UGC kit. `npx hyperframes remove-background` can cut the presenter out for overlay.

## licenses.md

For each non-original asset: file, source (model/provider or the user), date, and the license or terms that allow commercial ad use. Fonts too (the app's own fonts, or open-license fonts like Inter).
