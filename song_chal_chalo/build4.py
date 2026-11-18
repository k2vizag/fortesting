# v4: every clip at exactly 2x speed; song at normal speed from "Chal chalo chalo" (59.3)
# through the end of the chorus. No face-wash scenes.
# Usage: python3 build4.py <workdir with c2..c6.mp4 + song.wav> <out.mp4> [speed, default 2]
# At 1.5x three extra shots are dropped so the video ends in the music gap after the chorus.
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
SPEED, T0 = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0, 58.85
SHOTS = [
 ("c3", 0.0, 1.25),  ("c2", 9.05, 10.0), ("c2", 0.0, 1.6),   ("c2", 1.7, 3.45),
 ("c3", 5.17, 6.0),  ("c2", 3.55, 5.4),  ("c2", 5.5, 8.95),  ("c4", 8.35, 10.0),
 ("c5", 0.05, 1.25), ("c5", 1.33, 2.75), ("c5", 4.05, 5.35), ("c5", 7.12, 8.38),
 ("c5", 8.45, 10.0), ("c4", 0.0, 1.95),  ("c5", 2.8, 3.95),  ("c4", 4.02, 5.9),
 ("c4", 6.02, 7.6),  ("c5", 5.45, 7.05), ("c6", 0.0, 2.6),   ("c6", 3.3, 5.95),
 ("c6", 6.0, 7.2),   ("c6", 7.3, 8.75),
]
if SPEED < 2:
    SHOTS = [x for x in SHOTS if x not in [("c5", 0.05, 1.25), ("c5", 2.8, 3.95), ("c6", 6.0, 7.2)]]
tmp = os.path.join(W, f"shots4_{SPEED}"); os.makedirs(tmp, exist_ok=True); lst = []; D = 0
for i, (c, a, b) in enumerate(SHOTS):
    o = f"{tmp}/s{i:02d}.mp4"; lst.append(o); d = (b - a) / SPEED; D += d
    # -t before -i (input duration)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b-a}", "-i", f"{W}/{c}.mp4", "-an",
      "-vf", f"setpts=PTS/{SPEED},fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o], check=True)
print(f"video {D:.2f}s -> song {T0}-{T0+D:.2f}")
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
  "-ss", f"{T0}", "-t", f"{D}", "-i", f"{W}/song.wav",
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.2,fade=t=out:st={D-0.6:.2f}:d=0.6[v];"
  f"[1:a]afade=t=in:st=0:d=0.1,afade=t=out:st={D-0.8:.2f}:d=0.8,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
