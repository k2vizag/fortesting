# v9 = 20 s slow-motion face wash (song 6.0-26.2, Rajyam intro lines 1-2)
#    -> straight cut to "Chal chalo chalo" (song 58.82) with v7 at 1.5x. Build-up music skipped.
# Needs per-shot files from build2.py (<W>/shots) and build7.py (<W>/w3/shots7_1.5).
# Usage: python3 build9.py <workdir> <out.mp4>  (then audio -1.8 dB, video copy, for -14 LUFS)
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
A0, A1, B0 = 6.0, 26.2, 58.82          # song: intro part [A0, A1], then chorus from B0
# face-wash slow-mo shots (v2 shots) and the length used of each: total = A1 - A0
FACE = [(0, 3.6), (1, 5.17), (2, 4.57), (3, 4.0), (7, 2.86)]   # walk in, wash, mirror, close-up, "What should I do with my life?"
assert abs(sum(d for _, d in FACE) - (A1 - A0)) < 0.01
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                     capture_output=True, text=True).stdout)
tmp = os.path.join(W, "shots9"); os.makedirs(tmp, exist_ok=True); lst = []
for i, d in FACE:
    o = f"{tmp}/f{i:02d}.mp4"; lst.append(o)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/shots/s{i:02d}.mp4", "-vf",
                    f"tpad=stop_mode=clone:stop_duration=1,trim=duration={d},setpts=PTS-STARTPTS",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o], check=True)
v7 = os.path.join(W, "w3", "shots7_1.5")
rest = [f"{v7}/s{i:02d}.mp4" for i in range(28)]
lst += rest
DB = sum(dur(f) for f in rest); D = (A1 - A0) + DB
print(f"video {D:.2f}s: face wash {A1-A0:.1f}s + chal chalo {DB:.2f}s (song {B0}-{B0+DB:.2f})")
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
XF = 0.25   # short audio crossfade at the jump
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
  "-ss", f"{A0}", "-t", f"{A1-A0+XF}", "-i", f"{W}/song.wav",
  "-ss", f"{B0-XF}", "-t", f"{DB+XF}", "-i", f"{W}/song.wav",
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.8,fade=t=out:st={D-0.8:.2f}:d=0.8[v];"
  f"[1:a][2:a]acrossfade=d={XF}:c1=tri:c2=tri,afade=t=in:st=0:d=0.3,afade=t=out:st={D-1.0:.2f}:d=1.0,"
  f"loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
