#!/usr/bin/env python3
"""Free, offline background music: synthesizes an original instrumental bed from code.

No account, no API key, no model download, a few seconds on any Mac. Every run is original and
deterministic for a given --seed, so it is yours to use anywhere, including paid ads (MIT, like this skill).
It's a clean, simple bed (pads, bass, plucks, drums), not a produced song: for a richer track use fal or
the user's own music (references/audio.md).

Usage:
  synth_music.py --out work/gen/music.wav [--mood bright] [--seconds 18.5] [--bpm 112] [--key A] [--seed 7]

Moods: bright (pop, I-V-vi-IV), playful (bouncy, I-vi-IV-V), calm (soft, no kick), premium (maj7, minimal),
       cinematic (minor, big hits), chaotic (fast, busy).
Also writes <out>.beats.json: {"bpm", "beats": [...], "strongCues": [...]} for beat-syncing the edit.
The first bar is an intro (no drums); the drums drop in at bar 2, a natural spot for the reveal.
Needs only numpy.
"""
import argparse, json, math, wave
import numpy as np

SR = 44100
MOODS = {
    #            scale     progression (scale degrees)   bpm  sevenths kick  clap  hats   arp
    "bright":   ("major", [0, 4, 5, 3], 112, False, "pop", True, "8th", "16th"),
    "playful":  ("major", [0, 5, 3, 4], 120, False, "pop", True, "off", "8th"),
    "calm":     ("major", [5, 3, 0, 4], 88, True, None, False, "soft", "8th"),
    "premium":  ("major", [0, 5, 1, 4], 96, True, "soft", False, "8th", "8th"),
    "cinematic": ("minor", [0, 5, 2, 6], 96, False, "big", False, None, "16th"),
    "chaotic":  ("minor", [0, 6, 5, 4], 140, False, "four", True, "16th", "16th"),
}
SCALES = {"major": [0, 2, 4, 5, 7, 9, 11], "minor": [0, 2, 3, 5, 7, 8, 10]}
KEYS = {k: i for i, k in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}


def mtof(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def additive(freq, dur, nharm=8, decay=3.0, hdecay=0.0, attack=0.005, release=0.05, detune=0.0):
    """Band-limited saw-like tone: harmonics at 1/k, higher ones decaying faster (pluck) or not (pad)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    f = freq * 2 ** (detune / 1200)
    for k in range(1, nharm + 1):
        if k * f > 14000:
            break
        out += np.sin(2 * np.pi * k * f * t) / k * np.exp(-t * (decay + hdecay * k))
    env = np.minimum(1, t / max(attack, 1e-4))
    tail = int(release * SR)
    if tail and tail < n:
        env[-tail:] *= np.linspace(1, 0, tail)
    return out * env


def kick(kind):
    dur = 0.45 if kind == "big" else 0.3
    t = np.arange(int(dur * SR)) / SR
    f = 45 + 110 * np.exp(-t * 28)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (6 if kind == "big" else 11))
    click = np.exp(-t * 400) * 0.3
    return (body + click) * (1.3 if kind == "big" else 1.0) * (0.55 if kind == "soft" else 1.0)


def noise_hit(rng, dur, decay, hp=1):
    x = rng.standard_normal(int(dur * SR))
    for _ in range(hp):
        x = np.diff(x, prepend=0)
    t = np.arange(len(x)) / SR
    return x * np.exp(-t / decay)


def place(buf, sig, at, gain=1.0, pan=0.0):
    i = int(at * SR)
    if i >= buf.shape[0]:
        return
    sig = sig[: buf.shape[0] - i] * gain
    buf[i:i + len(sig), 0] += sig * math.cos((pan + 1) * math.pi / 4)
    buf[i:i + len(sig), 1] += sig * math.sin((pan + 1) * math.pi / 4)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--mood", default="bright", choices=MOODS)
    ap.add_argument("--seconds", type=float, default=18.0)
    ap.add_argument("--bpm", type=float)
    ap.add_argument("--key", default="A", choices=KEYS)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()

    scale_name, prog, bpm, sevenths, kick_kind, clap_on, hats, arp = MOODS[a.mood]
    bpm = a.bpm or bpm
    rng = np.random.default_rng(a.seed)
    beat = 60 / bpm
    bar = 4 * beat
    nbars = math.ceil(a.seconds / bar) + 1
    total = nbars * bar + 2.0
    mix = np.zeros((int(total * SR), 2))
    pads = np.zeros_like(mix)          # pad + bass bus, ducked by the kick
    scale = SCALES[scale_name]
    root = 57 + (KEYS[a.key] - KEYS["A"])  # around A3
    kicks = []

    def degree(d, octave=0):
        return root + scale[d % 7] + 12 * (d // 7 + octave)

    for b in range(nbars):
        t0 = b * bar
        d = prog[b % len(prog)]
        chord = [degree(d), degree(d + 2), degree(d + 4)] + ([degree(d + 6)] if sevenths else [])
        intro, last = b == 0, b == nbars - 1

        # Pad: soft, stereo-detuned, whole bar.
        for m in chord:
            for det, pan in ((-7, -0.6), (7, 0.6)):
                place(pads, additive(mtof(m), bar + 0.4, nharm=6, decay=0.15, attack=0.35, release=0.4, detune=det),
                      t0, 0.05, pan)
        # Bass: root, 8th notes (quarter notes in calm/premium).
        step = beat if a.mood in ("calm", "premium") else beat / 2
        if not intro:
            for i in range(int(bar / step)):
                place(pads, additive(mtof(degree(d, -2)), step * 0.95, nharm=3, decay=4, release=0.02), t0 + i * step, 0.32)
        # Arp: chord tones up an octave, bright plucks.
        astep = beat / 4 if arp == "16th" else beat / 2
        tones = [m + 12 for m in chord]
        for i in range(int(bar / astep)):
            m = tones[i % len(tones)] + (12 if (i // len(tones)) % 2 and a.mood != "calm" else 0)
            place(mix, additive(mtof(m), 0.35, nharm=10, decay=7, hdecay=1.4), t0 + i * astep,
                  0.06 if a.mood == "calm" else 0.08, pan=0.35 if i % 2 else -0.35)
        if intro or last:
            continue
        # Drums.
        if kick_kind:
            hits = {"pop": [0, 2, 2.5], "four": [0, 1, 2, 3], "soft": [0, 2], "big": [0]}[kick_kind]
            for h in hits:
                kicks.append(t0 + h * beat)
                place(mix, kick(kick_kind), t0 + h * beat, 0.8)
        if clap_on:
            for h in (1, 3):
                body = additive(190, 0.25, nharm=2, decay=30)  # same length as the noise burst
                place(mix, noise_hit(rng, 0.25, 0.06, hp=2) * 0.45 + body * 0.5, t0 + h * beat, 0.16)
        if hats:
            hs = {"8th": [i / 2 for i in range(8)], "16th": [i / 4 for i in range(16)], "off": [0.5, 1.5, 2.5, 3.5],
                  "soft": [0.5, 1.5, 2.5, 3.5]}[hats]
            for h in hs:
                place(mix, noise_hit(rng, 0.05, 0.012, hp=3), t0 + h * beat, 0.018 if hats == "soft" else 0.03,
                      pan=0.25)
        if kick_kind == "big" and b % 2 == 1:
            place(mix, noise_hit(rng, 1.2, 0.25, hp=3), t0, 0.05)  # soft air on every other bar

    # Final chord rings out.
    end_t = (nbars - 1) * bar
    for m in [degree(prog[0]), degree(prog[0] + 2), degree(prog[0] + 4)]:
        place(mix, additive(mtof(m + 12), 2.0, nharm=10, decay=1.5, hdecay=0.6), end_t, 0.12)

    # Sidechain the pad/bass bus to the kick, then add it in.
    if kicks:
        t = np.arange(pads.shape[0]) / SR
        duck = np.ones_like(t)
        for k in kicks:
            i = int(k * SR)
            seg = t[i:i + int(0.3 * SR)] - k
            duck[i:i + len(seg)] = np.minimum(duck[i:i + len(seg)], 1 - 0.45 * np.exp(-seg / 0.12))
        pads *= duck[:, None]
    mix += pads

    # Simple stereo echo for space.
    for dl, dr, g in ((0.11, 0.17, 0.18), (0.23, 0.31, 0.09)):
        il, ir = int(dl * SR), int(dr * SR)
        mix[il:, 0] += mix[:-il, 1] * g
        mix[ir:, 1] += mix[:-ir, 0] * g

    # Trim, fade, soft-clip, normalize with headroom.
    n = int(a.seconds * SR)
    mix = mix[:n]
    fade = min(n, int(1.2 * SR))
    mix[-fade:] *= np.linspace(1, 0, fade)[:, None]
    mix[: int(0.03 * SR)] *= np.linspace(0, 1, int(0.03 * SR))[:, None]
    mix = np.tanh(mix * 1.2)
    mix = mix / max(1e-6, np.abs(mix).max()) * 0.79  # about -2 dBFS: headroom for true peaks after encoding

    with wave.open(a.out, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())

    beats = [round(i * beat, 3) for i in range(int(a.seconds / beat) + 1)]
    strong = [round(b * bar, 3) for b in range(1, nbars) if b * bar < a.seconds]
    json.dump({"bpm": bpm, "mood": a.mood, "key": a.key, "seed": a.seed, "bar_seconds": round(bar, 3),
               "beats": beats, "strongCues": strong, "note": "bar 1 is an intro; drums enter at strongCues[0]"},
              open(a.out.rsplit(".", 1)[0] + ".beats.json", "w"), indent=1)
    print(f"wrote {a.out} ({a.seconds:.1f} s, {bpm:g} bpm, {a.mood}, key {a.key}); beats in .beats.json")


if __name__ == "__main__":
    main()
