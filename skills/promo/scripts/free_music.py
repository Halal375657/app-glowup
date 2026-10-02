#!/usr/bin/env python3
"""Generate a music bed locally and free with MusicGen (no API key, runs offline after the first model download).

Run it with the private environment from setup_free_audio.sh:
  ~/.cache/promo-skill/venv/bin/python free_music.py --prompt "..." --seconds 18 --out work/gen/music.wav

  --prompt   mood, tempo, instruments: "bright modern pop, 112 bpm, plucky synth, soft claps, no vocals"
  --seconds  target length; MusicGen makes up to ~28 s per pass, longer beds are crossfade-looped
  --model    facebook/musicgen-small (default, ~2.4 GB download to ~/.cache/huggingface on first run) or facebook/musicgen-medium (better, slower, larger)

LICENSE: MusicGen weights are CC-BY-NC 4.0. Use the result for drafts and organic posts, not paid ads.
For ads use the user's licensed track, HeyGen's catalog, Lyria, or fal (see references/audio.md).
"""
import argparse, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--prompt", required=True)
ap.add_argument("--seconds", type=float, default=18)
ap.add_argument("--out", required=True)
ap.add_argument("--model", default="facebook/musicgen-small")
ap.add_argument("--device", help="cpu, cuda or mps (default: cuda if available, else cpu)")
a = ap.parse_args()

try:
    import torch, soundfile as sf
    from transformers import AutoProcessor, MusicgenForConditionalGeneration
except ImportError:
    sys.exit("Missing packages. Run setup_free_audio.sh music, then use ~/.cache/promo-skill/venv/bin/python")

# Apple's MPS backend is very slow for MusicGen generation; CPU is faster on Apple silicon. CUDA when present.
device = a.device or ("cuda" if torch.cuda.is_available() else "cpu")
proc = AutoProcessor.from_pretrained(a.model)
model = MusicgenForConditionalGeneration.from_pretrained(a.model).to(device)
sr = model.config.audio_encoder.sampling_rate
frame_rate = model.config.audio_encoder.frame_rate  # tokens per second (50)

seg = min(a.seconds, 28.0)
inputs = proc(text=[a.prompt], padding=True, return_tensors="pt").to(device)
with torch.no_grad():
    audio = model.generate(**inputs, do_sample=True, guidance_scale=3.0, max_new_tokens=int(seg * frame_rate))
clip = audio[0, 0].float().cpu().numpy()

# Loop with a 2 s crossfade until long enough, then trim and fade out.
need, fade = int(a.seconds * sr), int(2 * sr)
out = clip.copy()
while len(out) < need and len(clip) > 2 * fade:
    ramp = np.linspace(0, 1, fade)
    out[-fade:] = out[-fade:] * (1 - ramp) + clip[:fade] * ramp
    out = np.concatenate([out, clip[fade:]])
out = out[:need]
tail = min(len(out), sr)
out[-tail:] *= np.linspace(1, 0, tail)
out = out / max(1e-6, np.abs(out).max()) * 0.89  # normalize to about -1 dBFS
sf.write(a.out, np.stack([out, out], axis=1), sr)
print(f"wrote {a.out} ({len(out) / sr:.1f} s, {sr} Hz, {device}); license CC-BY-NC: not for paid ads")
