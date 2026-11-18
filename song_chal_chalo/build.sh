#!/bin/bash
# Lion story clips cut to the "Chal Chalo Chalo" chorus (song 56.8s-99.1s, 42.3s).
# Song audio is taken from lyric_chalk/videos/chal_chalo_2_chal_chalo_te.mp4
# (branch ccr-23c8d9c9-8ol8yd). Clips: c1..c6 = the six uploaded 10 s clips.
# Usage: build.sh <workdir with c1..c6.mp4 + chorus.wav> <out.mp4>
set -e
W=$1; OUT=$2
# clip  src_start  duration   (song time in comment)
SEG=(
 "c1 2.30 7.60"   # 0.00-7.60  wash face, mirror, "What should I do with my life?"  | chal chalo chalo life se milo / new chapter
 "c2 0.00 5.45"   # 7.60-13.05 hails auto, crowded                                    | just say hello
 "c3 0.00 6.85"   # 13.05-19.90 squeezes into crowded auto                            | chalinchu daarilo / face every challenge
 "c4 0.00 7.39"   # 19.90-27.29 walking job search with file                          | teepitho paatuga kottha chedu
 "c5 2.00 7.12"   # 27.29-34.41 file close-up, auto handle, city                      | zindagi / guarantee ledu
 "c6 0.80 7.89"   # 34.41-42.30 two brothers, smile                                   | padesi parugu / andhuko hatthuko ee kshanam
)
IN=""; FC=""; i=0
for s in "${SEG[@]}"; do set -- $s
  IN="$IN -ss $2 -t $3 -i $W/$1.mp4"
  FC="$FC[$i:v]scale=1080:1920:flags=lanczos,setsar=1,fps=30,format=yuv420p,setpts=PTS-STARTPTS[v$i];"
  i=$((i+1))
done
FC="${FC}[v0][v1][v2][v3][v4][v5]concat=n=6:v=1:a=0,fade=t=in:st=0:d=0.3,fade=t=out:st=41.6:d=0.7[v];"
FC="${FC}[6:a]afade=t=in:st=0:d=0.2,afade=t=out:st=41.3:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]"
ffmpeg -v error -y $IN -i $W/chorus.wav -filter_complex "$FC" -map "[v]" -map "[a]" \
  -t 42.3 -c:v libx264 -preset slow -crf 20 -c:a aac -b:a 192k -movflags +faststart "$OUT"
