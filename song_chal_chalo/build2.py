# Lion story on "Chal Chalo Chalo": slow-motion morning on the Rajyam intro,
# road scenes on the beat from the drop (49.0 s) through the chorus + verse 1.
# Usage: python3 build2.py <workdir with c1..c6.mp4 + song.wav> <out.mp4>
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
T0, DROP, END, BEAT = 7.0, 49.0, 99.1, 0.45   # song seconds

# Morning (soft Rajyam intro, lines at 9.1 / 17.2 / 26.4 / 36.7): (clip, src a, src b, song end)
MORNING = [
 ("c1", 0.0, 1.95, 11.6),   # walks into bathroom
 ("c1", 2.02, 3.95, 16.9),   # opens tap, splashes face   (Rajyam gelisinodu...)
 ("c1", 4.02, 5.95, 21.6),   # looks into mirror          (Rajyam idisinode...)
 ("c1", 6.02, 7.95, 26.2),   # close-up, wipes face
 ("c6", 0.0, 2.6, 32.0),   # little brother at home     (Yuddham gelisetodu...)
 ("c6", 3.3, 5.95, 38.6),   # elder pats him, smiles     (Yuddham idiseyyodey...)
 ("c6", 7.3, 8.75, 43.4),   # elder close-up
 ("c1", 8.05, 9.95, DROP), # mirror: "What should I do with my life?" -> beat drop
]
# Road (beat section): (clip, src a, src b); length shared by source length, cuts snapped to beats
ROAD = [
 ("c3", 0.0, 1.25),  # hails an auto (same vest look as at home)
 ("c2", 9.05, 10.0), # busy city from above
 ("c2", 0.0, 1.6),  # walks, hails
 ("c2", 1.7, 3.45), # everyone rushes into the auto
 ("c3", 5.17, 6.0), # squeezed inside the auto   (chorus: Chal chalo chalo)
 ("c2", 3.55, 5.4), # packed auto
 ("c2", 5.5, 8.6), # left standing beside it
 ("c5", 1.33, 2.75), # boards another auto
 ("c5", 4.05, 5.35),  # holding the handle
 ("c4", 0.0, 1.95),  # walking with his job file
 ("c4", 6.02, 7.6),  # file close-up
 ("c4", 4.02, 5.9),  # walking past shops
 ("c5", 5.45, 7.05), # running beside the auto  (padesi parugu...)
 ("c5", 7.12, 8.38),  # close-up, end            (andhuko hatthuko ee kshanaanni)
]
tot = sum(b - a for _, a, b in ROAD); acc = 0; t = DROP; road = []
for c, a, b in ROAD:
    acc += b - a
    e = DROP + (END - DROP) * acc / tot
    e = END if acc == tot else DROP + round((e - DROP) / BEAT) * BEAT
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
  "-filter_complex", f"[0:v]fade=t=in:st=0:d=1.0,fade=t=out:st={D-1.2:.2f}:d=1.2[v];"
  f"[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={D-1.5:.2f}:d=1.5,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
  "-map", "[v]", "-map", "[a]", "-t", f"{D}", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
  "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT], check=True)
