# v8 = slow-motion morning from v2 (face wash + brothers, Rajyam intro, song 7.0-49.0)
#    + v2 slow-motion road start at the beat drop (hail, city, walk, rush into auto)
#    + v7 at 1.5x from "squeezed in" onwards. Song continuous from 7.0, fades at the end.
# Needs the per-shot files already rendered by build2.py (<W>/shots) and build7.py (<W>/w3/shots7_1.5).
# Usage: python3 build8.py <workdir> <out.mp4>  (then audio -1.5 dB, video copy, to land at -14 LUFS)
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
T0 = 7.0
MORNING_ENDS = [11.6, 16.9, 21.6, 26.2, 32.0, 38.6, 43.4, 49.0]   # song times (v2 schedule)
dur = lambda f: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                     capture_output=True, text=True).stdout)
tmp = os.path.join(W, "shots8"); os.makedirs(tmp, exist_ok=True); lst = []; t = T0
for i, e in enumerate(MORNING_ENDS):   # pad each slow-mo shot (clone last frame) to its exact length
    src, o = f"{W}/shots/s{i:02d}.mp4", f"{tmp}/m{i:02d}.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"tpad=stop_mode=clone:stop_duration=2,trim=duration={e-t:.4f},setpts=PTS-STARTPTS",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o], check=True)
    lst.append(o); t = e
lst += [f"{W}/shots/s{i:02d}.mp4" for i in range(8, 12)]                     # slow-mo road start
v7 = os.path.join(W, "w3", "shots7_1.5")
lst += [f"{v7}/s{i:02d}.mp4" for i in range(4, 28)]                          # v7 from "squeezed in"
D = (MORNING_ENDS[-1] - T0) + sum(dur(f) for f in lst[8:])
print(f"video {D:.2f}s, song {T0}-{T0+D:.2f}")
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
  "-ss", f"{T0}", "-t", f"{D}", "-i", f"{W}/song.wav",
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=1.0,fade=t=out:st={D-0.8:.2f}:d=0.8[v];"
  f"[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={D-1.0:.2f}:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
