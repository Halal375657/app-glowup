# Launch video (`--formats launch`)

A 15–25 second video that announces the **whole app**: what it is, the moment that makes people want it, and where to get it. The `/brag` idea, for iOS apps, built from real Simulator footage. One video, one poster, one share caption.

## Shape

Hook (2–3 s) → Reveal (2–4 s) → 2–3 highlights (2.5–4 s each) → Punchline and outro (2–4 s). A starting shape, not a template.

- **Hook:** the most surprising true thing about the app, or its result, in under 7 words. It decides whether anyone keeps watching.
- **Reveal:** the app's name and one-line promise, with the app on screen.
- **Highlights:** the features doing their job, real footage, one idea per highlight with a short label. Prefer the app working over describing it.
- **Punchline / outro:** a closing line that lands (funny, confident, or calm by tone), the name, "On the App Store".

Highlights come from the shot list in step 3; record one shot per highlight. The plan's storyboard must sum to 15–25 s (18–22 is the sweet spot).

## Tones

Presets set energy, pacing and type. A freeform direction ("fake 2009 keynote", "museum audio guide") refines or replaces them; map it to the nearest preset for pacing.

| Tone | Feel | Pacing | Transitions |
|---|---|---|---|
| `default` | Playful, clean, shareable | 4–5 scenes | Soft slides and fades |
| `polished` | Serious, elegant, restrained | 3–4 scenes, long holds | Slow fades, push-ins |
| `startup-parody` | Deadpan big-launch energy applied to a small app, played straight | 4–5 scenes, one claim each | Hard cuts |
| `chaotic` | FAST, LOUD, ALL CAPS | 6–8 scenes, some under 2 s | Flash and zoom cuts |
| `deadpan` | Calm, dry, the joke is that nothing is a joke | 3–4 scenes, lots of empty space | Slow fades |
| `cinematic` | Trailer scale, big type, epic framing | 4–5 scenes | Dramatic wipes, scale-ins |
| `app-store` | Clean feature cards | 4–6 scenes | Smooth slides |

Humor comes from the app's own situation, never from forced jokes. Every on-screen claim is still grounded (step 1).

## Layout

- **Landscape 1920×1080:** phone on one side, big type on the other; alternate sides between highlights so the eye moves. Keep the phone ≥ 60% of the frame height.
- **Vertical 1080×1920:** phone centered, type above it; respect the reel safe zones if it will be posted to Reels or TikTok.
- **Square 1080×1080:** smaller phone left, type right (the feed/square template layout).

Start from `<skill-dir>/kit/templates/launch.html`: 19.2 s on a 100 BPM bar grid (2.4 s bars), hook in the drum-free intro bar, every cut on a bar (`// beat-locked`). Change BPM and scene lengths together.

## Audio

Uses the user's choices from [audio.md](audio.md). For launch videos, music carries the energy: when it's on, land the reveal and the punchline on strong beats (`npx hyperframes beats`), add 3–5 sound effects at the moments that matter (whoosh into the reveal, click on a simulated tap, sparkle on a result, a soft impact on the logo). A voiceover is optional and should add what the screen doesn't say.

## Deliver

```
<output-dir>/launch/
  launch.mp4          finalize.py --profile ad --poster-at <the strongest settled frame>
  launch.jpg          the poster (also baked as frame 0)
  share-copy.txt      1–3 sentences, postable as-is, specific, in the tone; no "excited to share"
```

Optional `share-copy-variants.md` for X/LinkedIn/Product Hunt versions. Tell the user the creative angle in one sentence and offer to re-roll a scene or try another tone.
