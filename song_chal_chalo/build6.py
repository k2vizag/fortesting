# v6: job rejections start at 8 s of the video. 1.5x clips, song normal. Road/autos on the chorus, job rejections (shops incl. K2 Vizag
# Net Center) in the middle, walk home + hug with little brother on "andhuko hatthuko".
# The video ends at song 99.1 (end of verse 1); start = END - video length.
# Usage: python3 build5.py <workdir with c2..c8.mp4 + song.wav> <out.mp4> [speed]
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
SPEED = float(sys.argv[3]) if len(sys.argv) > 3 else 1.5
END = 99.1
SHOTS = [
 # first 8 s: road + crowded autos (chorus)
 ("c3", 0.0, 1.25, "hails auto"), ("c2", 9.05, 10.0, "city above"), ("c2", 0.0, 1.6, "walks, hails"),
 ("c2", 1.7, 3.45, "rush into auto"), ("c3", 5.17, 6.0, "squeezed in"), ("c2", 3.55, 5.4, "packed auto"),
 ("c2", 5.5, 8.95, "left beside it"),
 # from 8 s: job hunt with rejections
 ("c7", 0.0, 2.95, "shop 1: asks for job"), ("c7", 3.04, 3.88, "shopkeeper"), ("c7", 4.29, 5.08, "arms crossed - rejected"),
 ("c7", 5.29, 6.2, "shop 2: manager"), ("c7", 6.3, 7.38, "lion close-up"),
 ("c3", 8.04, 9.75, "walks on"), ("c4", 8.35, 10.0, "city above"),
 ("c5", 1.33, 2.75, "boards auto"), ("c5", 4.05, 5.35, "handle"), ("c5", 7.12, 8.38, "close-up in auto"),
 ("c7", 7.46, 10.04, "walks on the street"), ("c5", 8.45, 10.0, "city above"),
 ("c5", 0.05, 1.25, "walking, file"), ("c4", 0.0, 1.95, "walking with file"), ("c5", 2.8, 3.95, "file close-up"),
 ("c4", 2.02, 3.92, "past shops"), ("c4", 4.02, 5.9, "past shops"), ("c4", 6.02, 7.6, "file close-up"),
 ("c7", 10.12, 14.92, "K2 Vizag Net Center"), ("c7", 15.0, 16.92, "owner talks"), ("c7", 17.0, 18.5, "lion close-up"),
 ("c7", 18.62, 20.0, "owner"),
 # padesi parugu -> home
 ("c5", 5.45, 7.05, "runs beside auto"), ("c8", 0.0, 2.92, "city aerial"), ("c8", 3.0, 7.04, "walks home with brother"),
 ("c8", 7.12, 10.0, "hug (andhuko hatthuko)"),
]
D = sum(b - a for _, a, b, _ in SHOTS) / SPEED; T0 = END - D
tmp = os.path.join(W, f"shots6_{SPEED}"); os.makedirs(tmp, exist_ok=True); lst = []; t = T0
for i, (c, a, b, note) in enumerate(SHOTS):
    o = f"{tmp}/s{i:02d}.mp4"; lst.append(o); d = (b - a) / SPEED
    print(f"{i:2d} {c} {a:5.2f}-{b:5.2f} song {t:6.2f}-{t+d:6.2f} {note}"); t += d
    # -t before -i (input duration)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b-a}", "-i", f"{W}/{c}.mp4", "-an",
      "-vf", f"setpts=PTS/{SPEED},fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p",
      "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o], check=True)
print(f"video {D:.2f}s, song {T0:.2f}-{END}")
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
  "-ss", f"{T0}", "-t", f"{D}", "-i", f"{W}/song.wav",
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.2,fade=t=out:st={D-0.8:.2f}:d=0.8[v];"
  f"[1:a]afade=t=in:st=0:d=0.1,afade=t=out:st={D-1.0:.2f}:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
