#!/usr/bin/env python3
"""Encode a rendered video to its delivery profile, add the music bed (or a silent track), and bake the poster.

Usage:
  finalize.py <in.mp4> <out.mp4> --profile ad|preview [--music bed.mp3] [--music-volume 0.8]
              [--music-start 0] [--poster-at 1.2] [--poster out.jpg]

Profiles:
  ad       H.264 High, CRF 17, 30 fps constant, yuv420p, AAC 192 kbps stereo 48 kHz, faststart.
           Meta, TikTok, YouTube and Google all accept this. --poster-at bakes that frame as frame 0
           (platform thumbnails grab frame 0) and writes it as a .jpg next to the video.
  preview  App Store app preview: H.264 High Profile Level 4.0, 30 fps, 11 Mbps CBR,
           AAC 256 kbps CBR stereo 48 kHz (AudioToolbox on macOS), faststart. Always has an audio track (silent if no music).
           Don't bake a poster: App Store Connect uses the frame at 5 s unless you pick another.

Music is trimmed to the video and faded out over the last second. Audio is loudness-normalized
(two-pass) to -14 LUFS for ads and -16 for previews (--lufs to override); silent tracks stay silent.
"""
import argparse, json, os, subprocess, sys, tempfile


def probe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("dst")
ap.add_argument("--profile", required=True, choices=["ad", "preview"])
ap.add_argument("--music"); ap.add_argument("--music-volume", type=float, default=0.8)
ap.add_argument("--music-start", type=float, default=0.0, help="offset into the music file (s)")
ap.add_argument("--poster-at", type=float); ap.add_argument("--poster")
ap.add_argument("--lufs", type=float, help="loudness target (default -14 ad, -16 preview)")
a = ap.parse_args()

info = probe(a.src)
dur = float(info["format"]["duration"])
has_audio = any(s["codec_type"] == "audio" for s in info["streams"])

def loudness(path):
    """Integrated loudness stats of a file's audio (ffmpeg loudnorm, first pass)."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    return json.loads(r[r.rindex("{"):r.rindex("}") + 1])


with tempfile.TemporaryDirectory() as tmp0:
    # 1. Build the soundtrack as a WAV: the render's own audio, plus the music bed if given.
    mixed = os.path.join(tmp0, "mixed.wav")
    acmd = ["ffmpeg", "-y", "-v", "error", "-i", a.src]
    if a.music:
        acmd += ["-ss", str(a.music_start), "-i", a.music]
        fade = max(dur - 1.0, 0)
        mus = f"[1:a]volume={a.music_volume},afade=t=out:st={fade}:d=1,apad"
        graph = f"{mus}[m];[0:a][m]amix=inputs=2:duration=first:normalize=0[a]" if has_audio else f"{mus}[a]"
        acmd += ["-filter_complex", graph, "-map", "[a]"]
    elif has_audio:
        acmd += ["-map", "0:a"]
    if a.music or has_audio:
        subprocess.run(acmd + ["-t", f"{dur:.3f}", "-ar", "48000", "-ac", "2", mixed], check=True)
    else:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-t", f"{dur:.3f}", mixed], check=True)

    # 2. Normalize loudness (two-pass, linear) unless the track is silent: -14 LUFS for social ads,
    #    -16 for App Store previews, true peak -1.5 dBTP.
    target = a.lufs if a.lufs is not None else (-14.0 if a.profile == "ad" else -16.0)
    st = loudness(mixed)
    if float(st["input_i"]) > -60:
        normed = os.path.join(tmp0, "normed.wav")
        ln = (f"loudnorm=I={target}:TP=-1.5:LRA=11:measured_I={st['input_i']}:measured_TP={st['input_tp']}:"
              f"measured_LRA={st['input_lra']}:measured_thresh={st['input_thresh']}:offset={st['target_offset']}:linear=true")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mixed, "-af", ln, "-ar", "48000", normed], check=True)
        mixed = normed
        print(f"loudness {float(st['input_i']):.1f} -> {target:g} LUFS")
    else:
        print("audio is silent; left as a silent stereo track")

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.src, "-i", mixed]
    amap = ["-map", "0:v", "-map", "1:a"]

    if a.profile == "ad":
        venc = ["-c:v", "libx264", "-profile:v", "high", "-crf", "17", "-preset", "slow"]
        aenc = ["-c:a", "aac", "-b:a", "192k"]
    else:
        # Constant bitrate: simple screen footage would otherwise undershoot Apple's 10-12 Mbps, and a silent
        # track would encode at ~2 kbps instead of 256. macOS's AudioToolbox AAC holds CBR even on silence.
        venc = ["-c:v", "libx264", "-profile:v", "high", "-level:v", "4.0", "-b:v", "11M", "-minrate", "11M",
                "-maxrate", "11M", "-bufsize", "11M", "-preset", "slow", "-x264-params", "nal-hrd=cbr"]
        has_at = "aac_at" in subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
        aenc = (["-c:a", "aac_at", "-aac_at_mode", "cbr", "-b:a", "256k"] if has_at
                else ["-c:a", "aac", "-b:a", "256k"])

    common = ["-r", "30", "-fps_mode", "cfr", "-pix_fmt", "yuv420p", "-ar", "48000", "-ac", "2",
              "-t", f"{dur:.3f}", "-movflags", "+faststart"]

    with tempfile.TemporaryDirectory() as tmp:
        mid = os.path.join(tmp, "enc.mp4")
        subprocess.run(cmd + amap + venc + aenc + common + [mid], check=True)

        if a.profile == "ad" and a.poster_at is not None:
            poster = a.poster or os.path.splitext(a.dst)[0] + ".jpg"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(a.poster_at), "-i", mid, "-frames:v", "1", "-q:v", "2", poster], check=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", mid, "-i", poster,
                            "-filter_complex", "[0:v][1:v]overlay=0:0:enable='eq(n,0)'[v]", "-map", "[v]", "-map", "0:a",
                            *venc, "-c:a", "copy", "-r", "30", "-fps_mode", "cfr", "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", a.dst], check=True)
            print(f"poster {poster}")
        else:
            os.makedirs(os.path.dirname(os.path.abspath(a.dst)), exist_ok=True)
            os.replace(mid, a.dst)

print(f"wrote {a.dst} ({os.path.getsize(a.dst) / 1e6:.1f} MB, {dur:.2f} s, profile {a.profile})")
