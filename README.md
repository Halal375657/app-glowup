# app-glowup

**Give your iOS app a glow-up.** Two [Claude Code](https://claude.com/claude-code) skills for iOS app owners:

- **[/onboard](#onboard)** builds animated, interactive onboarding in SwiftUI.
- **[/promo](#promo)** turns your app into marketing content: a product launch video (like [/brag](https://github.com/latent-spaces/brag)), video ads (9:16, 4:5, 1:1) with hook variants, an App Store preview, App Store screenshots, ad copy, and a UGC kit for creators and editors.

## /promo

`/promo receipt scanning, monthly report` records the real feature in the iOS Simulator, plans hooks and storyboards (and waits for your approval before spending credits), generates supporting art and licensed music on fal, composes with [Hyperframes](https://hyperframes.heygen.com), and finishes every file to its platform's spec:

| Output | Spec |
|---|---|
| Launch video (`--formats launch`) | 1920×1080 (or vertical/square), 15–25 s, hook → reveal → highlights → punchline, poster + share copy, 7 tones |
| Reel ads, one per hook | 1080×1920, 15 s, Reels/TikTok safe zones, poster baked as frame 0 |
| Feed and square ads | 1080×1350, 1080×1080 |
| App Store preview | 886×1920, 15–30 s, H.264 High 4.0, AAC 256k, screen capture only (Guideline 2.3.4), best frame at 5 s |
| App Store screenshots | 1320×2868, no alpha |
| UGC kit | clean clips, before/after moments, transparent phone overlay and hook captions (.mov ProRes 4444 + .webm), music, captions |
| `ad-copy.md` | Meta, TikTok, Google App campaign and App Store copy within character limits, every claim traced to the app's own copy |

**Audio is your choice, per run.** Each layer can be off, free, or paid:

| | Free | Paid (fal, `FAL_KEY`) |
|---|---|---|
| Music | your own track; HeyGen catalog (free account); Lyria (free Gemini key); MusicGen, fully local (non-commercial license: drafts/organic only) | ElevenLabs Music, MiniMax, with your own direction |
| Voiceover | Kokoro, fully local | ElevenLabs TTS |
| Sound effects | bundled library (Pixabay license, commercial OK) | — |

`/promo --music fal "lo-fi, dreamy, 90 bpm" --voice free --sfx free`, or say nothing and it asks. Free local audio needs a one-time `skills/promo/scripts/setup_free_audio.sh` (private Python environment).

`scripts/check_specs.py` verifies every file before delivery. Rules built in: no fake testimonials or AI "customers" (FTC 16 CFR 465), AI-content labels where platforms require them, music cleared for commercial ads, no prices or device frames in App Store previews.

Needs: macOS, Xcode + Simulator, ffmpeg, Node 18+ (`npx hyperframes`), Python 3 + Pillow, and the Hyperframes skills (`npx hyperframes skills update hyperframes-core hyperframes-animation hyperframes-creative hyperframes-keyframes hyperframes-cli media-use`). `FAL_KEY` for generated art, music, voice and avatars.

## /onboard

A skill that builds **animated, interactive onboarding for iOS apps**. It reads your app, plans the screens, generates brand-matched art with GPT Image 2.5 on [fal](https://fal.ai), writes the SwiftUI, wires it into your app, then builds it and checks every screen in the iOS Simulator.

## What it does

1. **Inspects your app:** what it does, its hook, brand colors and fonts, SwiftUI or UIKit, existing onboarding, permissions and paywall.
2. **Plans the flow** in `onboarding-plan.md`: copy, motion and every image with its prompt and a cost estimate. **It waits for your approval before spending any credits.**
3. **Generates art** on fal with one shared style. Before/after pairs are made by *editing* one image, so they line up exactly.
4. **Builds the screens** from tested SwiftUI templates, with motion, haptics, Reduce Motion, Dynamic Type and VoiceOver support.
5. **Checks it in the Simulator:** a screenshot of every page and frame bursts of each animation, fixing what's wrong.

## Motion templates

| Template | What it is |
|---|---|
| `DissolveHero` | Full-bleed photo dissolving between states (before/after or variants) with a synced light sweep and a state pill |
| `CompareSlider` | Drag-to-compare with an automatic hint wipe and haptics |
| `ParallaxHero` | Layered art drifting at different depths, following your finger |
| `StatReveal` | A ring filling while a number counts up |
| `ChoiceQuestion` | Personalization cards saved for the app to use |
| `PermissionPrimer` | Explains why, then shows the real camera, photos or notifications prompt |
| `LoopingVideo` | Muted looping clip as a background |
| `OnboardingFlow` + `UIKitHosting` | The pager, page dots, CTA and entrance animation, and hosting from UIKit |

It picks patterns that fit your kind of app: photo editors, fitness, finance, productivity, education, meditation, AI tools or games. See [motion-patterns.md](skills/onboard/references/motion-patterns.md).

## Install

In Claude Code:

```
/plugin marketplace add Halal375657/app-glowup
/plugin install app-glowup@app-glowup
```

That installs both `/onboard` and `/promo`. Or copy the skill folders into your personal skills:

```bash
git clone https://github.com/Halal375657/app-glowup && cp -R app-glowup/skills/onboard app-glowup/skills/promo ~/.claude/skills/
```

Or with [skills.sh](https://skills.sh):

```bash
npx skills add https://github.com/Halal375657/app-glowup
```

These skills run in **Claude Code on a Mac**: they drive Xcode and the iOS Simulator, so they don't work in claude.ai's cloud sandbox.

## Requirements

- macOS with Xcode and an iOS Simulator. The templates need iOS 17+.
- A fal API key in `FAL_KEY` for generated art (optional; without it, the skill uses your existing images). Set it without pasting it anywhere:

  ```bash
  printf 'Paste fal key: '; read -rs k; echo "export FAL_KEY=\"$k\"" >> ~/.zshrc; unset k; echo " saved"
  ```

  Use `~/.bash_profile` instead of `~/.zshrc` if your shell is bash. Then restart Claude Code.
- Python 3. Pillow (`pip install pillow`) is optional, for image checks.

## Use

Open Claude Code in your app's folder and run:

```
/onboard
/onboard 3 screens, soft 3D clay style
/onboard --no-art
```

## Costs and honesty

- Each generated image costs fal credits (about 25 seconds each). You approve the asset list before anything is generated, and only rejected images are regenerated.
- Generated before/after images imply "the app does this". The skill labels them "Illustrative example" and tells you to swap in real results from your app before shipping.

## Credits

`/promo` follows the workflow shape of [/brag](https://github.com/latent-spaces/brag) (MIT) by Shunit Haviv Hakimi: inspect, plan, compose with Hyperframes, gated delivery. Fonts: Inter and DM Serif Display (SIL OFL 1.1, licenses in `skills/promo/kit/fonts`).

## License

MIT
