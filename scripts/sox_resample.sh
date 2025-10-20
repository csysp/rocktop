#!/usr/bin/env bash
set -euo pipefail

# Resample WAVs to 48 kHz, 32-bit float using SoX's very high quality linear-phase SRC.
# Preserves relative directory structure under the input root.
#
# Usage:
#   scripts/sox_resample.sh <input_dir> <output_dir>
#
# Example:
#   scripts/sox_resample.sh raw_audio data/processed

if [ $# -ne 2 ]; then
  echo "Usage: $0 <input_dir> <output_dir>" >&2
  exit 2
fi

in_dir=$1
out_dir=$2

if ! command -v sox >/dev/null 2>&1; then
  echo "Error: sox is not installed or not on PATH" >&2
  exit 1
fi

sr=48000

# Find WAV files case-insensitively and process.
find "$in_dir" -type f \( -iname '*.wav' -o -iname '*.wave' \) -print0 |
  while IFS= read -r -d '' src; do
    rel="${src#$in_dir/}"
    dest_dir="$out_dir/$(dirname "$rel")"
    mkdir -p "$dest_dir"
    dest="$out_dir/${rel%.*}.wav"
    echo "[sox-resample] $src -> $dest"
    sox "$src" -b 32 -e float -r "$sr" "$dest" rate -v -s "$sr"
  done

echo "[sox-resample] Done. Output at: $out_dir"

