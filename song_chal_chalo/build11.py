# v11: clip 1 (outside, walks home + hug) and clip 2 (brothers inside) as they are, with their own dialogue;
# then face wash in slow motion on the chal chalo music before the lyrics (song 43.8-58.82: starts in the quiet gap after the intro, fades in; c6 dialogue fades out),
# then "Chal chalo chalo" with the 1.5x part (build7 shots 0..27). Song continuous from 43.06.
# Needs <W>/w3/c6.mp4, c8.mp4, song.wav, <W>/shots9 (build9 face-wash files), <W>/w3/shots7_1.5 (build7).
# Sound fades at both clip joins (10 s, 19 s); delogo removes the corner sparkle mark (same spot in all clips).
# Usage: python3 build11.py <workdir> <out.mp4>  (song part -2.1 dB: single-pass loudnorm lands it ~-12)
import subprocess, sys, os
W, OUT = sys.argv[1], sys.argv[2]
S0 = 43.8                                        # song: last intro line ends -> instrumental build-up, beat drop 49.0
FACE = [(0, 2.4), (1, 2.8), (2, 3.6), (3, 3.4), (7, 2.82)]    # = 15.02 s; cut after the wash lands on the drop
DIALOGUE = [("c8", 0.0, 10.0), ("c6", 0.0, 9.25)]            # as they are (c6 tail after 9.3 is black)
run = lambda *a: subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)
dur = lambda p: float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                     capture_output=True, text=True).stdout)
tmp = os.path.join(W, "shots11"); os.makedirs(tmp, exist_ok=True)
VF = "fps=30,scale=1080:1920:flags=lanczos,setsar=1,format=yuv420p"
# part A: original clips with their own audio
for c, a, b in DIALOGUE:
    run("-ss", f"{a}", "-t", f"{b-a}", "-i", f"{W}/w3/{c}.mp4", "-vf", VF, "-af", (f"aresample=48000,afade=t=in:st=0:d=0.4,afade=t=out:st={b-a-0.6:.2f}:d=0.6" if c == "c6"
               else f"aresample=48000,afade=t=out:st={b-a-0.45:.2f}:d=0.45"),
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-c:a", "pcm_s16le", f"{tmp}/{c}.mov")
LA = sum(b - a for _, a, b in DIALOGUE)
run("-i", f"{tmp}/c8.mov", "-i", f"{tmp}/c6.mov", "-filter_complex",
    "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a];[a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a2]",
    "-map", "[v]", "-map", "[a2]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-c:a", "pcm_s16le", f"{tmp}/A.mov")
# part B: face wash slow-mo + 1.5x part, on the song
lst = []
for i, d in FACE:
    o = f"{tmp}/f{i:02d}.mp4"; lst.append(o)
    run("-i", f"{W}/shots9/f{i:02d}.mp4", "-vf", f"trim=duration={d},setpts=PTS-STARTPTS",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", o)
lst += [f"{W}/w3/shots7_1.5/s{i:02d}.mp4" for i in range(28)]
DB = sum(dur(p) for p in lst)
open(f"{tmp}/list.txt", "w").write("".join(f"file '{p}'\n" for p in lst))
run("-f", "concat", "-safe", "0", "-i", f"{tmp}/list.txt", "-ss", f"{S0}", "-t", f"{DB}", "-i", f"{W}/song.wav",
    "-filter_complex", f"[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={DB-1.0:.2f}:d=1.0,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
    "-map", "0:v", "-map", "[a]", "-t", f"{DB}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-c:a", "pcm_s16le", f"{tmp}/B.mov")
D = dur(f"{tmp}/A.mov") + DB
print(f"dialogue part {dur(tmp + '/A.mov'):.2f}s + face wash/chal chalo {DB:.2f}s = {D:.2f}s (song {S0}-{S0+DB:.2f})")
run("-i", f"{tmp}/A.mov", "-i", f"{tmp}/B.mov", "-filter_complex",
    f"[1:a]volume=-2.1dB[b];[0:v][0:a][1:v][b]concat=n=2:v=1:a=1[v][a];[v]delogo=x=850:y=1690:w=94:h=94,fade=t=out:st={D-0.8:.2f}:d=0.8[v2]",
    "-map", "[v2]", "-map", "[a]", "-c:v", "libx264", "-preset", "slow", "-crf", "20",
    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT)
