# Lion story on "Chal Chalo Chalo": slow-motion morning on the Rajyam intro,
# road scenes on the beat from the drop (49.0 s) through the chorus + verse 1.
# v3: chorus onwards, no face-wash scenes, clips ~0.9x.
# Usage: python3 build3.py <workdir with c1..c6.mp4 + song.wav> <out.mp4>
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
T0, DROP, END, BEAT = 58.9, 58.9, 91.45, 0.45   # song seconds

MORNING = []
# Road + home, from the chorus "Chal chalo chalo" (59.3) - clips ~0.9x (2x the v2 slow-mo), song normal
ROAD = [
 ("c3", 0.0, 1.25),  # hails an auto (vest)
 ("c2", 9.05, 10.0), # busy city from above
 ("c2", 0.0, 1.6),   # walks, hails
 ("c2", 1.7, 3.45),  # everyone rushes into the auto
 ("c3", 5.17, 6.0),  # squeezed inside the auto
 ("c2", 3.55, 5.4),  # packed auto
 ("c2", 5.5, 8.95),  # left standing beside it
 ("c5", 1.33, 2.75), # boards another auto
 ("c5", 4.05, 5.35), # holding the handle
 ("c5", 7.12, 8.38), # close-up in the auto
 ("c4", 0.0, 1.95),  # walking with his job file
 ("c4", 6.02, 7.6),  # file close-up
 ("c4", 4.02, 5.9),  # walking past shops
 ("c5", 5.45, 7.05), # running beside the auto
 ("c6", 0.0, 2.6),   # back home: little brother
 ("c6", 3.3, 5.95),  # elder pats him, smiles
 ("c6", 7.3, 8.75),  # elder close-up (end)
]
tot = sum(b - a for _, a, b in ROAD); acc = 0; t = DROP; road = []
for k, (c, a, b) in enumerate(ROAD):
    acc += b - a
    e = DROP + (END - DROP) * acc / tot
    e = END if k == len(ROAD) - 1 else DROP + round((e - DROP) / BEAT) * BEAT
    road.append((c, a, b, e))
shots = []; t = T0
for c, a, b, e in MORNING + road:
    shots.append((c, a, b, t, e)); t = e
tmp = os.path.join(W, "shots"); os.makedirs(tmp, exist_ok=True)
lst = []
for i, (c, a, b, s, e) in enumerate(shots):
    f = (e - s) / (b - a)   # slow-down factor
    o = f"{tmp}/s{i:02d}.mp4"; lst.append(o)
    print(f"{i:2d} {c} src {a:5.2f}-{b:5.2f} -> song {s:6.2f}-{e:6.2f}  speed {1/f:.2f}x")
    vf = (f"setpts={f:.5f}*(PTS-STARTPTS),scale=720:1280,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,"
          f"scale=1080:1920:flags=lanczos,setsar=1,tpad=stop_mode=clone:stop_duration=1,trim=duration={e-s:.4f},setpts=PTS-STARTPTS,format=yuv420p")
    # -t before -i (input duration), not as output option
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b-a}", "-i", f"{W}/{c}.mp4",
                    "-an", "-vf", vf, "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o], check=True)
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
D = END - T0
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt",
  "-ss", f"{T0}", "-t", f"{D}", "-i", f"{W}/song.wav",
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=0.3,fade=t=out:st={D-1.2:.2f}:d=1.2[v];"
  f"[1:a]afade=t=in:st=0:d=0.15,afade=t=out:st={D-1.5:.2f}:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
