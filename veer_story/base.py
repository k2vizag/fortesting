"""Veer story: pick best take per scene, fix speaker mismatch, 1.1x, 1080x1920, + 4 s end hold -> work/base.mov"""
import subprocess, os
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad"
R, W = S + "/raw", S + "/work"; os.makedirs(W, exist_ok=True)
SP, END = 1.1, 4.0
# scene clips chosen (better take per scene):
#  1 c738447e  2 a6ae9954  3+4 7e77685c (0-10 / 10-20; has the complete scene-4 dialogue)  5 b607df99 (has Krishna's reply)  6 1d49aee6
# video pieces: (clip, in, out, zoom) ; audio pieces: (clip, in, out)
V, A = [], []
# Scene 1 fix: king's 2nd sentence (3.58-5.08) played over Veer's moving lips -> keep the king on screen
# for his whole line (repeat of the pointing shot, punched-in), then Veer's lip-sync shot under Veer's line.
# Also drop the 0.5 s pause 3.1-3.5.
A += [("c738447e", 0, 3.1), ("c738447e", 3.5, 10.0)]
V += [("c738447e", 0, 2.66, 1.0), ("c738447e", 0.62, 2.64, 1.08), ("c738447e", 3.0, 6.9, 1.0), ("c738447e", 7.0, 8.02, 1.0)]
for c, a, b in [("a6ae9954", 0, 10), ("7e77685c", 0, 10), ("7e77685c", 10, 20.0), ("b607df99", 0, 10), ("1d49aee6", 0, 10)]:
    A.append((c, a, b)); V.append((c, a, b, 1.0))
assert abs(sum(b - a for _, a, b, _ in V) - sum(b - a for _, a, b in A)) < 0.02
fc, ins = [], []
for i, (c, a, b, z) in enumerate(V):
    ins += ["-ss", str(a), "-t", str(b - a), "-i", f"{R}/{c}.mp4"]
    sc = f"scale={int(1080*z)}:{int(1920*z)}:flags=lanczos,crop=1080:1920" if z != 1 else "scale=1080:1920:flags=lanczos"
    fc.append(f"[{i}:v]{sc},fps=30,setsar=1,setpts=PTS-STARTPTS[v{i}]")
n = len(V)
for j, (c, a, b) in enumerate(A):
    ins += ["-ss", str(a), "-t", str(b - a), "-i", f"{R}/{c}.mp4"]
    # each clip normalised so scenes sit at the same level; tiny fades avoid clicks at cuts
    fc.append(f"[{n+j}:a]aresample=48000,loudnorm=I=-16:TP=-2:LRA=11,aresample=48000,asetpts=PTS-STARTPTS,"
              f"afade=t=in:d=0.02,afade=t=out:st={b-a-0.03:.3f}:d=0.03[a{j}]")
fc.append("".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,setpts=PTS/{SP},tpad=stop_mode=clone:stop_duration={END}[vo]")
fc.append("".join(f"[a{j}]" for j in range(len(A))) + f"concat=n={len(A)}:v=0:a=1,atempo={SP},apad=pad_dur={END}[ao]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[vo]", "-map", "[ao]",
                "-c:v", "prores_ks", "-profile:v", "1", "-c:a", "pcm_s16le", "-ar", "48000", "-shortest", f"{W}/base.mov"], check=True)
d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"{W}/base.mov"], capture_output=True, text=True).stdout
print("base", d)
