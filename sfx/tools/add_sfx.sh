#!/usr/bin/env bash
# Mix SFX clips into a video from a cue sheet. The picture is copied, not re-encoded.
#
# Usage: sfx/tools/add_sfx.sh <in.mp4> <cues.txt> <out.mp4>
#
# cues.txt has one cue per line:  <seconds> <path to clip, relative to sfx/> <gain dB>
#   7.85  comedy_ref1/02_reaction_music_sting  -2
# The .mp3 extension is optional. Lines starting with # are ignored.
#
# Level guide (pack clips are -16 LUFS; speech is about -14 LUFS):
# aim for the SFX 9-12 dB under the voice. Short hits use about -3..-6 dB,
# stings/strings about -2..-7 dB, and a quiet bed under speech about -11 dB.
# Check the levels with sfx/tools/check_levels.py.
set -euo pipefail
in=$1; cues=$2; out=$3
dir=$(cd "$(dirname "$0")/.." && pwd)
dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$in")
args=(-i "$in"); fc=""; mix="[0:a]"; n=1
while read -r t f g; do
  [[ -z "${t:-}" || "$t" == \#* ]] && continue
  clip="$dir/$f"; [[ -f "$clip" ]] || clip="$clip.mp3"
  [[ -f "$clip" ]] || { echo "missing clip: $f" >&2; exit 1; }
  ms=$(awk "BEGIN{printf \"%d\", $t*1000}")
  args+=(-i "$clip")
  fc+="[$n:a]aresample=48000,volume=${g}dB,adelay=${ms}|${ms}[s$n];"
  mix+="[s$n]"; n=$((n+1))
done < "$cues"
ffmpeg -v error -y "${args[@]}" -filter_complex \
  "${fc}${mix}amix=inputs=$n:normalize=0:duration=first,alimiter=limit=0.95[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart -t "$dur" "$out"
echo "wrote $out ($((n-1)) cues)"
