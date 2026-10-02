#!/usr/bin/env bash
# One-time setup for the FREE local audio options, in a private Python environment
# (nothing is installed into the system Python).
#
# Usage: setup_free_audio.sh [voice] [music]      (default: voice)
#   voice  Kokoro text-to-speech (kokoro-onnx, Apache 2.0; ~350 MB model on first use)
#   music  MusicGen small (transformers + torch ~1 GB, plus ~2.4 GB model on first use). Model license is CC-BY-NC 4.0:
#          fine for organic posts and drafts, NOT cleared for paid ads.
#
# Location: $PROMO_VENV or ~/.cache/promo-skill/venv; models cache in ~/.cache/huggingface (MusicGen) and Hyperframes' cache (Kokoro).
# Remove with: rm -rf ~/.cache/promo-skill  (and ~/.cache/huggingface/hub/models--facebook--musicgen-small)
set -euo pipefail
VENV=${PROMO_VENV:-$HOME/.cache/promo-skill/venv}
want=${*:-voice}
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --quiet --upgrade pip
pkgs="soundfile numpy"
[[ $want == *voice* ]] && pkgs="$pkgs kokoro-onnx"
[[ $want == *music* ]] && pkgs="$pkgs transformers torch scipy"
"$VENV/bin/python" -m pip install --quiet $pkgs
echo "ready: $VENV"
echo "Hyperframes TTS uses it via: export HYPERFRAMES_PYTHON=$VENV/bin/python"
