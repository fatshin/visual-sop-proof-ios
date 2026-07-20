#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

frames=(
  artifacts/screenshots/01-hero.png
  artifacts/screenshots/02-birth-context.png
  artifacts/screenshots/03-memory-consent.png
  artifacts/screenshots/04-synthesis.png
  artifacts/screenshots/05-ten-readings.png
  artifacts/screenshots/06-obsidian-export.png
)

for frame in "${frames[@]}"; do
  test -s "$frame"
done

work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

say -v Samantha -r 190 -f artifacts/demo/narration.txt -o "$work/narration.aiff"
audio_duration="$(
  ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$work/narration.aiff"
)"
clip_duration="$(
  python3 - "$audio_duration" "${#frames[@]}" <<'PY'
import math
import sys

audio = float(sys.argv[1])
count = int(sys.argv[2])
print(f"{math.ceil((audio + 1.5) / count * 10) / 10:.1f}")
PY
)"

for index in "${!frames[@]}"; do
  ffmpeg -hide_banner -loglevel error -y \
    -loop 1 -t "$clip_duration" -i "${frames[$index]}" \
    -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fade=t=in:st=0:d=0.45,fade=t=out:st=$(python3 -c "print(max(0, float('$clip_duration') - 0.45))"):d=0.45,format=yuv420p" \
    -r 30 -an "$work/clip-$index.mp4"
done

for index in "${!frames[@]}"; do
  printf "file '%s'\n" "$work/clip-$index.mp4"
done >"$work/concat.txt"

ffmpeg -hide_banner -loglevel error -y \
  -f concat -safe 0 -i "$work/concat.txt" \
  -i "$work/narration.aiff" \
  -c:v copy -c:a aac -b:a 192k -shortest \
  artifacts/demo/oracle-council-demo.mp4

ffprobe -v error \
  -show_entries format=duration,size \
  -of default=nw=1 \
  artifacts/demo/oracle-council-demo.mp4
