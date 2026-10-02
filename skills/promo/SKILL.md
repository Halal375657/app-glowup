---
name: promo
description: Turn an iOS app, or one or more of its features, into marketing content. It produces a 15–25 s product launch video (like /brag), vertical, feed and square video ads with hook variants, an App Store preview video, App Store screenshots, ad copy, and a UGC kit (clean screen recordings, transparent phone overlays, before/after clips, hook overlays) for editing into creator-style ads. It records the real app in the iOS Simulator, optionally generates art on fal, and composes with Hyperframes. Music, voiceover and sound effects are each optional: none, free (local/bundled) or paid (fal). Use when someone says "/promo", "launch video for my app", "make ads for this feature", "marketing videos for my app", "App Store preview", "App Store screenshots", "UGC creatives", or wants campaign content for an iOS app.
---

# /promo

You own an app. Now sell one feature at a time. `/promo` turns a real feature of an iOS app into everything a campaign needs: ads that stop the scroll, App Store assets that pass review, and raw material an editor or creator can cut into UGC.

Everything is built from the **real app**: footage is recorded from the Simulator, claims come from the app's own copy, and generated art only supports what the app really does.

## Usage

`/promo [features] [options]`. Options can be flags or plain language ("just the reels, 3 hooks, playful").

| Option | Values | Default |
|---|---|---|
| features | Feature names or descriptions ("receipt scanning, monthly report") | Inferred: the 1–2 features that best show the app's core result. Ask if unclear. |
| `--formats` | any of `launch`, `reel`, `feed`, `square`, `preview`, `screenshots`, `ugc-kit` | all ad formats; `launch` only when asked ("launch video", "like /brag") |
| `--launch-format` | `landscape` (1920×1080), `vertical` (1080×1920), `square` | landscape |
| `--hooks <n>` | hook variants per feature for the reel | 3 |
| `--duration <s>` | ad length | 15 (preview: 20–28, always within Apple's 15–30) |
| `--tone` | preset from [references/tones.md](references/tones.md) or freeform | inferred |
| `--music` | `none`, `free` (synthesized by the skill, instant, ad-safe; or HeyGen/Lyria), `fal` (ElevenLabs/MiniMax with the user's direction, e.g. "lo-fi, 90 bpm"), or a path to the user's licensed track | ask in the plan |
| `--voice` | `none`, `free` (Kokoro, local), `fal` (ElevenLabs), or a path | ask in the plan |
| `--sfx` | `none` or `free` (bundled library) | ask in the plan |
| `--avatar` | AI presenter for UGC-style ads (see the rules in step 4) | off |
| `--lang <code>` | copy language; repeatable for localized sets | the app's development language |

Formats (exact specs in [references/specs.md](references/specs.md)):

| Format | Size | Use |
|---|---|---|
| `reel` | 1080×1920, 9:16 | Instagram/Facebook Reels and Stories, TikTok, YouTube Shorts |
| `feed` | 1080×1350, 4:5 | Facebook/Instagram feed |
| `square` | 1080×1080, 1:1 | Feed, Google App campaigns |
| `preview` | 886×1920, 15–30 s | App Store app preview (screen capture only) |
| `screenshots` | 1320×2868 PNG | App Store 6.9" set (scales to smaller iPhones) |
| `ugc-kit` | mixed | Clean clips, transparent overlays, music, captions for editors and creators |
| `launch` | 1920×1080 (or 1080×1920, 1080×1080), 15–25 s | Product launch video about the whole app, with poster and share copy (see [references/launch.md](references/launch.md)) |

## Output

Write to `promo-output/` in the app's repo root, or `promo-output-YYYY-MM-DD-HHmmss/` if it exists. Generate the timestamp once at the start and use it for every path in the run. Keep every intermediate file (raw recordings, generations, frames, scripts) in `<output-dir>/work/`.

```
<output-dir>/
  promo-plan.md             plan, storyboards, asset list, approvals
  ad-copy.md                copy per platform, within character limits
  README.md                 what each file is for and where to upload it
  launch/                   launch.mp4 + launch.jpg poster, share-copy.txt (only with --formats launch)
  <feature>/
    ads/                    <feature>-reel-hook-a.mp4 (+ .jpg poster), -feed.mp4, -square.mp4
    app-preview/            <feature>-preview.mp4
    ugc-kit/                clips/, overlays/ (.mov ProRes 4444 + .webm with alpha), reveal/, hooks/, audio/, captions/
  screenshots/              01-<slug>.png … (one ordered App Store set across features)
  composition/              the Hyperframes project
  work/                     everything intermediate, plus licenses.md
```

## Skill directory

`<skill-dir>` is the directory containing this `SKILL.md`. Claude Code prints it as "Base directory for this skill" when the skill loads; other agents put it wherever the skill was installed. Scripts are in `<skill-dir>/scripts/`, references in `<skill-dir>/references/`, composition templates and styles in `<skill-dir>/kit/`. Don't guess the install path.

## Requirements

- macOS with Xcode, an iOS Simulator runtime the app supports, `ffmpeg`/`ffprobe`, Node 18+ (`npx hyperframes`), Python 3.
- The Hyperframes skills for composing (`hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-cli`, `media-use`). If they aren't installed, tell the user the command (`npx hyperframes skills update hyperframes-core hyperframes-animation hyperframes-creative hyperframes-keyframes hyperframes-cli media-use`) and that the session needs a restart afterwards. Ask before running it: it writes to their agent config.
- `FAL_KEY` only for the paid options (art, music, voice, avatars). Never ask for the key in chat, never print it, never write it to a file. Without it, everything still works with real footage and the free audio options.
- Free local audio (Kokoro voice, MusicGen music) needs a one-time `scripts/setup_free_audio.sh` into a private environment; ask before running it. See [references/audio.md](references/audio.md).

---

## Step 1: Inspect the app and the features

**Read:** [references/step-1-inspect.md](references/step-1-inspect.md)

Find each feature in the code, how to reach it in the Simulator, what it changes, and every claim you're allowed to make about it.

**Gate:** for every feature you can answer the rubric (what it does in one sentence, who it's for, the before → after, the 2–3 beats of using it, the visual hook, the grounded claims list, the demo path in the Simulator, what demo content to use) and you have a working build on a booted Simulator.

## Step 2: Plan, and get approval

**Read:** [references/step-2-plan.md](references/step-2-plan.md)

Write `<output-dir>/promo-plan.md`: the angle per feature, `--hooks` hook variants, a beat-by-beat storyboard per format with durations, the screenshot set with captions, the shot list to record, the asset list with model and estimated cost, music direction, and the copy plan.

If the user hasn't said what they want for music, voiceover and sound effects, ask in one question with the options from [references/audio.md](references/audio.md) (none / free / fal / own file for each). Never add audio they didn't choose.

Show the plan and stop until the user approves it. Nothing is generated (no credits spent) before approval.

**Gate:** `promo-plan.md` exists; storyboard durations sum to the target for every format (preview within 15–30 s); every on-screen claim is in the grounded claims list; the user approved.

## Step 3: Capture the real app

**Read:** [references/step-3-capture.md](references/step-3-capture.md)

Record each shot on the shot list from the Simulator with a clean status bar and demo content, then trim to constant-frame-rate clips.

**Gate:** every planned shot exists in `work/capture/` as a trimmed CFR clip; a contact sheet of each clip has been reviewed (no personal data, no debug UI, no keyboard or alert you didn't plan, status bar shows 9:41).

## Step 4: Generate supporting assets

**Read:** [references/step-4-generate.md](references/step-4-generate.md)

Only what the plan lists: hook and end-card art, before/after pairs, and (only with `--avatar`) an AI presenter. Music, voiceover and sound effects follow [references/audio.md](references/audio.md), using exactly the options the user chose.

**Gate:** every generated asset was looked at or listened to, and rejected ones regenerated; `work/licenses.md` records the source and license of every music, voice, image and font file used.

## Step 5: Compose

**Read:** [references/step-5-compose.md](references/step-5-compose.md) and the Hyperframes skills listed under Requirements.

Write `<output-dir>/composition-brief.md`, then build one Hyperframes project per output shape in `<output-dir>/composition/`, starting from the tested templates in `<skill-dir>/kit/templates/`. `/promo` owns the angle, footage, copy, specs and safe zones; Hyperframes owns the implementation details.

**Gate:** `npx hyperframes check` passes with zero errors for every project, and you have looked at a `scripts/review_frames.py` sheet (safe zones drawn) of every hook, scene and mid-transition for each format, and fixed what it showed.

## Step 6: Render, finish and deliver

**Read:** [references/step-6-deliver.md](references/step-6-deliver.md)

Render, encode each file to its platform profile with `scripts/finalize.py`, export screenshots and transparent overlays, write `ad-copy.md` and the output `README.md`.

**Gate:** `python3 <skill-dir>/scripts/check_specs.py <output-dir>` reports zero failures; every ad has a poster baked as frame 0; the preview's strongest frame is at 5 s (Apple's default poster frame).

---

## Creative laws

- **Result first.** The first 1.5 seconds show the payoff (the after, the finished thing), not the app's logo or a setup. People decide in the first second.
- **One feature, one ad.** Each ad sells a single feature with a single promise. More features means more ads, not a longer one.
- **Show the real app.** The feature working on screen is the proof. Generated art can frame it, never replace it.
- **Grounded claims only.** Names, numbers, capabilities and quotes must come from the app, its store listing or its own copy. Hooks, jokes and framing are free to invent; claims are not. "Remove wrinkles in 1 tap" is fine only if it really is one tap.
- **Sound off by default.** Most feeds autoplay muted: every ad must work with captions and on-screen text alone, and better with sound.
- **Readable.** Any line meant to be read stays settled for about 0.3 s per word (at least 0.8 s). Pace comes from cuts and motion, never from yanking text away.
- **Respect the safe zones.** Text, faces and the product stay out of the areas the platform UI covers (see specs).
- **Native, not corporate.** For reels and UGC, it should feel like something a person would post. No stock-ad language ("revolutionize", "seamless", "unlock").
- **End on the action.** The last 2 seconds name the app and the next step ("Free on the App Store"). No prices in App Store assets.
- **Every frame postable.** Any frozen frame should be a decent ad on its own.

## Compliance rules (not optional)

- **App Store previews contain only screen captures of the app.** No device frames, hands, people, AI-generated footage or art. Text overlays and voiceover are fine. No prices. Say so on screen if the feature needs a subscription or in-app purchase.
- **Screenshots must show the app in use**, not just title art. Captions and backgrounds are fine. No prices, no other platforms.
- **No fake testimonials.** Never present an AI avatar or invented person as a real customer, never script first-person results ("I tried it and my lines disappeared"), never invent reviews or ratings. Real reviews only, quoted exactly, with permission.
- **Label AI content where platforms require it** (TikTok AIGC toggle; Meta adds "AI info" automatically). Tell the user in the delivery notes which files contain AI-generated people.
- **Music must be cleared for commercial ads.** Generate it (and record the provider's terms in `licenses.md`) or use the user's licensed track. Never use bundled or popular music of unknown license.
- **People's faces:** generated or used with consent. Never a real person's likeness without permission, never a celebrity.
