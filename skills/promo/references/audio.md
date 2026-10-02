# Audio: music, voiceover, sound effects

Audio is the user's choice, per run. Each layer is `none`, `free` or `fal` (paid), or a file the user provides. If the invocation doesn't say, ask once in the plan step (a single question with all three layers) and record the answer in `promo-plan.md`. `none` means no track of that kind, not a quiet one: `finalize.py` still adds a silent stereo track because platforms expect one.

| Layer | `free` | `fal` (paid, needs `FAL_KEY`) | Own file |
|---|---|---|---|
| Music | `synth_music.py` (built in, instant), or see "Free music" below | `elevenlabs/music/v2.5` (~$0.60/min), `minimax/music-3` | `--music path/to/track.mp3` (user confirms they hold the license) |
| Voiceover | Kokoro, local (`npx hyperframes tts`), Apache 2.0 | `elevenlabs/tts/eleven-v4` | `--voice path/to/vo.wav` |
| Sound effects | Hyperframes' bundled 21-file library (Pixabay license: commercial use OK) | — | — |

Record every audio file in `work/licenses.md` with its source and license. Tell the user plainly which choices are **not** cleared for paid ads.

## Setup for the free local options (once per machine)

```bash
<skill-dir>/scripts/setup_free_audio.sh voice          # Kokoro TTS
<skill-dir>/scripts/setup_free_audio.sh voice music    # + MusicGen (~1 GB packages + ~2.4 GB model download on first use)
export HYPERFRAMES_PYTHON=~/.cache/promo-skill/venv/bin/python
```

It installs into a private environment (`~/.cache/promo-skill/venv`), never the system Python. Ask before running it the first time; voice is ~0.5 GB, music ~3.5 GB.

## Free music, in order of preference

1. **The user's own licensed track.** Best for ads.
2. **Synthesized by this skill** (default free option): an original instrumental bed generated from code in about a second, offline, no account, no model, safe for paid ads. Six moods; writes the beat grid for syncing the edit.
   ```bash
   python3 <skill-dir>/scripts/synth_music.py --out work/gen/music.wav --mood bright --bpm 100 --seconds 19.2 --seed 11
   # moods: bright, playful, calm, premium, cinematic, chaotic; work/gen/music.beats.json has beats + strongCues
   ```
   Pick the BPM so a bar (240/BPM seconds) matches your scene lengths, then cut on `strongCues`; bar 1 is a drum-free intro, so the drums drop on the reveal. It's a clean, simple bed, not a produced song; offer fal or the user's track when they want richer music. Try 2 seeds and let the user pick.
3. **HeyGen music catalog** (10k+ tracks, free account): the user installs the `heygen` CLI and signs in (`heygen auth login --oauth`; they do this, not you). Then resolve a track with Hyperframes' `media-use` skill (`bgm` with `mode: retrieve` and a mood query). Check HeyGen's terms for paid-ad use and note them in `licenses.md`.
4. **Lyria RealTime** (Google; free API key from Google AI Studio, `GEMINI_API_KEY`): `media-use`'s `lyria-recipe.py` with `--prompt`, `--bpm`, `--duration`. Check Google's terms for commercial use.
5. **MusicGen, fully local** (no account, no key; needs about 16 GB of RAM: on an 8 GB Mac it swaps and takes many minutes per second of audio):
   ```bash
   ~/.cache/promo-skill/venv/bin/python <skill-dir>/scripts/free_music.py \
     --prompt "bright modern pop, 112 bpm, plucky synth, soft claps, warm pads, no vocals" --seconds 20 --out work/gen/music.wav
   ```
   **Model license CC-BY-NC 4.0: drafts and organic posts only, not paid ads.** Say so in the delivery README.

## Paid music on fal

The user can give their own direction ("lo-fi, dreamy, 90 bpm, female hum, builds at the end"); otherwise write it from the tone. Always instrumental for ads with on-screen text, unless they ask for vocals.

```bash
python3 <skill-dir>/scripts/fal_run.py schema elevenlabs/music/v2.5        # current inputs
python3 <skill-dir>/scripts/fal_run.py elevenlabs/music/v2.5 --out work/gen --name music \
  --in prompt=@work/prompts/music.txt music_length_ms=20000 force_instrumental=true output_format=mp3_48000_192
```

Generate 2 options for the user to pick from when the budget allows. Record the provider's commercial-use terms in `licenses.md` and remind the user to confirm them.

## Voiceover

Write lines that add what the screen doesn't say, timed to the storyboard (~2.5 words per second), never just reading the on-screen text.

```bash
# free
HYPERFRAMES_PYTHON=~/.cache/promo-skill/venv/bin/python npx hyperframes tts @work/prompts/vo.txt --voice af_heart --output work/gen/vo.wav
npx hyperframes tts --list            # voices
# paid
python3 <skill-dir>/scripts/fal_run.py schema elevenlabs/tts/eleven-v4
python3 <skill-dir>/scripts/fal_run.py elevenlabs/tts/eleven-v4 --out work/gen --name vo --in text=@work/prompts/vo.txt
# word timestamps for captions (free, local)
npx hyperframes transcribe work/gen/vo.wav
```

Each engine speaks at its own pace (in testing, ElevenLabs lines ran ~20% longer than Kokoro's), so measure every line with `ffprobe` and place it so it ends before the next cut; never assume a duration.

Burn captions into the video (most viewers watch muted) and also deliver `.srt` in the UGC kit.

## Sound effects (free)

Find the bundled library, then read its `manifest.json` (names, durations, placement hints):

```bash
SFX=$(dirname "$(find ~/.claude/skills ~/.agents/skills ~/.codex/skills -path '*media-use/audio/assets/sfx/manifest.json' 2>/dev/null | head -1)")
cat "$SFX/manifest.json"; cp "$SFX"/{whoosh,pop,click-soft,chime,sparkle}.mp3 composition/shared/assets/sfx/
```

Use them sparingly, timed exactly to the motion: `whoosh` on a scene change, `pop` on a caption landing, `click-soft` on a simulated tap, `sparkle`/`chime` on the result reveal, `riser` into the payoff (it is 10 s: start it 10 s before the hit). Volume ~0.3–0.4, under music and voice. Repeated sounds (every caption) become annoying: pick the 3–5 moments that matter.

## Mixing in the composition

Put audio in the Hyperframes composition so it stays in sync with the picture. Write a cue sheet and let `audio_cues.py` write the tags between the `<!-- AUDIO:BEGIN -->` / `<!-- AUDIO:END -->` markers (an empty layer writes nothing, so "none" is truly silent):

```bash
python3 <skill-dir>/scripts/audio_cues.py work/cues/launch.json --inject composition/launch/index.html
```

Example cue sheet: `<skill-dir>/kit/templates/launch.cues.example.json`. The tags it writes look like:

```html
<audio id="music" src="assets/music.mp3" data-start="0" data-duration="15" data-volume="0.7" data-fade-in="0.3" data-fade-out="1.2"></audio>
<audio id="vo" src="assets/vo.wav" data-start="0.4" data-volume="1"></audio>
<audio id="sfx-whoosh-1" src="assets/sfx/whoosh.mp3" data-start="2.55" data-volume="0.35"></audio>
```

Every `<audio>` needs an `id` (or it is silently dropped). With voiceover, drop the music to ~0.15–0.25 under speech: use the volume automation or the voiceover carve from the `hyperframes-audio` skill. For beat sync, `npx hyperframes beats` on the music, then land 1–3 big moments on strong beats (±0.15 s) without hurting readability. `finalize.py` normalizes loudness (two-pass) to -14 LUFS for ads and -16 for previews and leaves silent tracks silent. Verify placement objectively when you can't listen: the difference between a render with and without a layer should carry energy only at that layer's cue times.
