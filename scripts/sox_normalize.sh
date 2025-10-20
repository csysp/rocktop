#!/usr/bin/env bash
set -euo pipefail

# Peak-normalize WAVs to -1 dBFS using SoX gain -n -1.
# Preserves relative directory structure under the input root.
#
# Usage:
#   scripts/sox_normalize.sh <input_dir> <output_dir>
#
# Example:
#   scripts/sox_normalize.sh data/processed data/normalized

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

find "$in_dir" -type f \( -iname '*.wav' -o -iname '*.wave' \) -print0 |
  while IFS= read -r -d '' src; do
    rel="${src#$in_dir/}"
    dest_dir="$out_dir/$(dirname "$rel")"
    mkdir -p "$dest_dir"
    dest="$out_dir/${rel%.*}.wav"
    echo "[sox-normalize] $src -> $dest"
    sox "$src" "$dest" gain -n -1
  done

echo "[sox-normalize] Done. Output at: $out_dir"

