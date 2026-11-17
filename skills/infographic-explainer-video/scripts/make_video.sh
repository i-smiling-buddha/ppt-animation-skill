#!/usr/bin/env bash
# One-shot pipeline: build -> parallel render -> concat -> audio mix -> final MP4
# Usage: make_video.sh video.html vo_dir out.mp4 [chunks=nproc]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="$(realpath "$1")"; VO="$(realpath "$2")"; OUT="$3"; CH="${4:-$(nproc)}"
WORK="$(dirname "$SRC")/_work"; mkdir -p "$WORK"
python3 "$HERE/build.py" "$SRC" "$VO/dur.json" "$WORK/build.html"
V=""; grep -q 'viewBox="0 0 1080 1920"' "$WORK/build.html" && V="--vertical"
N=$(python3 -c "import json;t=json.load(open('$WORK/timeline.json'));print(int(round((t[-1]['start']+t[-1]['dur'])*30)))")
STEP=$(( (N + CH - 1) / CH )); : > "$WORK/list.txt"
for ((i=0; i<CH; i++)); do
  F0=$((i*STEP)); F1=$(( F0+STEP < N ? F0+STEP : N ))
  python3 "$HERE/render.py" "$WORK/build.html" "$WORK/chunk_$i.mp4" --from $F0 --to $F1 $V &
  echo "file 'chunk_$i.mp4'" >> "$WORK/list.txt"
done; wait
ffmpeg -y -loglevel error -f concat -safe 0 -i "$WORK/list.txt" -c copy "$WORK/video.mp4"
python3 "$HERE/mix_audio.py" "$WORK/timeline.json" "$VO" "$WORK/mix.wav"
ffmpeg -y -loglevel error -i "$WORK/video.mp4" -i "$WORK/mix.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest "$OUT"
if [ -n "$V" ]; then TILE="fps=1/2.5,scale=216:-1,tile=8x2"; else TILE="fps=1/3,scale=384:-1,tile=6x5"; fi
ffmpeg -y -loglevel error -i "$OUT" -vf "$TILE" -frames:v 1 "${OUT%.mp4}_sheet.png"
python3 "$HERE/captions.py" "$WORK/captions.json" "${OUT%.mp4}.srt" >/dev/null
echo "Done: $OUT  (QA sheet: ${OUT%.mp4}_sheet.png, subtitles: ${OUT%.mp4}.srt)"
