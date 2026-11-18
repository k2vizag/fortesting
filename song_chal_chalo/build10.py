# v10: song continuous from 7.0 (Rajyam intro) to the end of the 1.5x part.
#   outside: walks home with brother -> inside: hug + brothers in the room   (slow motion, ~0.7x)
#   -> face wash 20.2 s slow-mo (build9 files) -> beat drop / chal chalo music: slow-mo road start
#   (build2 shots 8-11) -> "Chal chalo chalo" at 1.5x (build7 shots 4..27).
# Needs <W>/shots (build2), <W>/shots9 (build9), <W>/w3/shots7_1.5 (build7). c6/c8 in <W>/w3.
# Usage: python3 build10.py <workdir> <out.mp4>   (then audio gain to land at -14 LUFS)
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
T0, FACE_START = 7.0, 28.8          # song; face wash runs 28.8-49.0, beat drop at 49.0
HOME = [("c8", 3.0, 7.04, "walks home with brother"), ("c8", 7.12, 10.0, "hug inside"),
        ("c6", 0.0, 2.6, "little brother"), ("c6", 3.3, 5.95, "elder pats him"), ("c6", 7.3, 8.75, "elder smiles")]
src = sum(b - a for _, a, b, _ in HOME); f = (FACE_START - T0) / src
dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                     capture_output=True, text=True).stdout)
tmp = os.path.join(W, "shots10"); os.makedirs(tmp, exist_ok=True); lst = []; t = T0
for i, (c, a, b, note) in enumerate(HOME):
    d = (b - a) * f; o = f"{tmp}/h{i:02d}.mp4"; lst.append(o)
    print(f"{c} {a:5.2f}-{b:5.2f} song {t:6.2f}-{t+d:6.2f} speed {1/f:.2f}x {note}"); t += d
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b-a}", "-i", f"{W}/w3/{c}.mp4", "-an", "-vf",
      f"setpts={f:.5f}*(PTS-STARTPTS),scale=720:1280,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
      f"scale=1080:1920:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=1,trim=duration={d:.4f},setpts=PTS-STARTPTS,format=yuv420p",
      "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o], check=True)
lst += [f"{W}/shots9/f{i:02d}.mp4" for i in (0, 1, 2, 3, 7)]                 # face wash, 20.2 s
lst += [f"{W}/shots/s{i:02d}.mp4" for i in range(8, 12)]                     # slow-mo road on the build-up music
lst += [f"{W}/w3/shots7_1.5/s{i:02d}.mp4" for i in range(4, 28)]             # 1.5x from "squeezed in"
D = sum(dur(p) for p in lst)
print(f"video {D:.2f}s, song {T0}-{T0+D:.2f}")
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
  "-ss", f"{T0}", "-t", f"{D}", "-i", f"{W}/song.wav",
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=1.0,fade=t=out:st={D-0.8:.2f}:d=0.8[v];"
  f"[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={D-1.0:.2f}:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
