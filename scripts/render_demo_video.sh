#!/bin/zsh
set -euo pipefail

if (( $# < 4 )); then
  print -u2 "Usage: render_demo_video.sh <output.mp4> <narration.txt> <WIDTHxHEIGHT> <image> [image ...]"
  exit 1
fi

OUTPUT=$1
NARRATION=$2
VIDEO_SIZE=$3
shift 3
IMAGES=("$@")

if [[ ! -s "$NARRATION" ]]; then
  print -u2 "Narration is missing or empty: $NARRATION"
  exit 1
fi

for image in "${IMAGES[@]}"; do
  if [[ ! -s "$image" ]]; then
    print -u2 "Image is missing or empty: $image"
    exit 1
  fi
done

WIDTH=${VIDEO_SIZE%x*}
HEIGHT=${VIDEO_SIZE#*x}
if [[ -z "$WIDTH" || -z "$HEIGHT" || "$WIDTH" == "$VIDEO_SIZE" ]]; then
  print -u2 "Video size must use WIDTHxHEIGHT format."
  exit 1
fi

mkdir -p "${OUTPUT:h}"
WORK_DIR=$(mktemp -d)
trap 'rm -rf "$WORK_DIR"' EXIT INT TERM

say -v Samantha -r 185 -f "$NARRATION" -o "$WORK_DIR/narration.aiff"
ffmpeg -hide_banner -loglevel error \
  -i "$WORK_DIR/narration.aiff" \
  -c:a aac -b:a 160k \
  "$WORK_DIR/narration.m4a"

DURATION=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$WORK_DIR/narration.m4a")
COUNT=${#IMAGES[@]}
SEGMENT=$(awk -v duration="$DURATION" -v count="$COUNT" 'BEGIN { printf "%.6f", duration / count }')
SLIDES="$WORK_DIR/slides.ffconcat"

: > "$SLIDES"
for index in {1..$COUNT}; do
  escaped_image=${IMAGES[$index]//\'/\'\\\'\'}
  print -r -- "file '$escaped_image'" >> "$SLIDES"
  print -r -- "duration $SEGMENT" >> "$SLIDES"
done
escaped_last=${IMAGES[$COUNT]//\'/\'\\\'\'}
print -r -- "file '$escaped_last'" >> "$SLIDES"

ffmpeg -hide_banner -loglevel error \
  -f concat -safe 0 -i "$SLIDES" \
  -i "$WORK_DIR/narration.m4a" \
  -vf "scale=$WIDTH:$HEIGHT:force_original_aspect_ratio=decrease,pad=$WIDTH:$HEIGHT:(ow-iw)/2:(oh-ih)/2:black,fps=10,format=yuv420p" \
  -map 0:v -map 1:a \
  -c:v libx264 -preset medium -crf 20 -r 10 \
  -c:a aac -b:a 160k \
  -t "$DURATION" -movflags +faststart \
  -y "$OUTPUT"

ffprobe -v error \
  -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate \
  -of compact=p=0:nk=1 \
  "$OUTPUT"
