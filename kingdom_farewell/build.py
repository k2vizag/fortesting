"""Veer leaves the kingdom – emotional montage of AI clips on the reference song (first verse + 'దండాలయ్యా' chorus).
Clips muted; cuts snapped to the song's beats; emotional shots slowed with motion interpolation; soft dissolves."""
import subprocess, os
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/emo"
C, W = S + "/clips", S + "/work"; os.makedirs(W, exist_ok=True)
REF = S + "/ref/ref.mp4"
END = 54.75           # stop before the spoken line at 54.8 s in the reference
BEATS = [0.1, 0.83, 1.54, 2.18, 2.85, 3.49, 4.1, 4.8, 5.44, 6.08, 6.72, 7.42, 8.1, 8.7, 9.34, 10.02, 10.66, 11.33, 11.97, 12.64,
         13.28, 13.92, 14.56, 15.23, 15.9, 16.54, 17.18, 17.86, 18.53, 19.17, 19.81, 20.48, 21.12, 21.76, 22.37, 23.07, 23.71, 24.38,
         25.02, 25.66, 26.3, 26.98, 27.62, 28.29, 28.96, 29.6, 30.24, 30.91, 31.58, 32.22, 32.86, 33.54, 34.18, 34.82, 35.49, 36.13,
         36.77, 37.41, 38.08, 38.72, 39.39, 40.03, 40.7, 41.38, 42.02, 42.66, 43.26, 43.9, 44.58, 45.22, 45.89, 46.53, 47.2, 47.87,
         48.51, 49.15, 49.79, 50.46, 51.1, 51.74, 52.42, 53.06, 53.7, 54.37]
# (clip, src in, src out, planned end on the song timeline)  – story order
SHOTS = [
    ("c02", 8.2, 10.0, 2.85),    # palace from above, the whole kingdom
    ("c06", 0.0, 1.5, 4.8),      # Veer & Chintu walk into the throne hall
    ("c06", 1.5, 3.0, 7.42),     # kneels before the king
    ("c06", 3.0, 4.7, 10.02),    # places his crown on the floor – gives up the kingdom
    ("c02", 1.6, 3.0, 12.64),    # the king watches, silent
    ("c04", 3.0, 5.8, 15.9),     # touches his father's feet
    ("c06", 6.0, 7.6, 18.53),    # king's tearful hand on his head
    ("c03", 7.0, 9.6, 21.12),    # Veer's face
    ("c07", 3.0, 5.0, 24.38),    # mother holds his face   ('తడిసిన కన్నుల్లో…')
    ("c07", 5.0, 7.0, 26.98),    # hugs his mother
    ("c07", 7.0, 9.2, 29.6),     # elder of the family embraces him
    ("c02", 3.0, 5.6, 32.22),    # family and relatives standing, watching
    ("c09", 0.5, 4.0, 35.49),    # walks down the palace steps   ('నీ అడుగులకే…')
    ("c08", 3.0, 5.0, 38.08),    # friends say goodbye
    ("c01", 5.0, 7.6, 41.38),    # people reach out to touch him
    ("c03", 3.0, 5.6, 43.9),     # Chintu holds his hand, looks up
    ("c08", 5.0, 6.6, 45.89),    # soldiers salute   ('దండాలయ్యా…')
    ("c05", 7.0, 10.0, 48.51),   # the people fold their hands
    ("c03", 0.0, 3.0, 51.74),    # walks out towards us, palace behind (leaving, not going in) ('మాతో నువ్వుండాలయ్యా')
    ("c05", 4.0, 7.0, END),      # walks out towards us, the palace behind him – fade out
]
XF = 0.35
ins, fc = [], []
t0 = 0.0
for i, (c, a, b, e) in enumerate(SHOTS):
    tgt = e - t0 + (XF if i < len(SHOTS) - 1 else 0)          # extra for the dissolve overlap
    sp = (b - a) / tgt                                        # <1 = slow motion
    ins += ["-t", f"{b - a + 0.05:.3f}", "-ss", str(a), "-i", f"{C}/{c}.mp4"]
    mi = ",minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" if sp < 0.92 else ",fps=30"
    fc.append(f"[{i}:v]setpts=(PTS-STARTPTS)/{sp:.4f}{mi},scale=1080:1920:flags=lanczos,setsar=1,trim=duration={tgt:.3f},setpts=PTS-STARTPTS[v{i}]")
    print(f"{i:2d} {c} {a:4.1f}-{b:4.1f} -> {t0:5.2f}-{e:5.2f}  speed {sp:.2f}")
    t0 = e
# dissolve chain
cur, off = "v0", 0.0
for i in range(1, len(SHOTS)):
    off = SHOTS[i - 1][3] - 0 if i == 1 else SHOTS[i - 1][3]
    fc.append(f"[{cur}][v{i}]xfade=transition=fade:duration={XF}:offset={off - 0:.3f}[x{i}]"); cur = f"x{i}"
# warm cinematic grade, vignette, fade in/out
fc.append(f"[{cur}]eq=contrast=1.06:saturation=1.08:gamma=0.98,colorbalance=rs=0.03:gs=0.0:bs=-0.03,vignette=PI/5,"
          f"fade=t=in:st=0:d=0.6,fade=t=out:st={END - 1.4:.2f}:d=1.4,trim=duration={END},format=yuv420p[v]")
n = len(SHOTS)
fc.append(f"[{n}:a]atrim=0:{END},asetpts=PTS-STARTPTS,afade=t=in:d=0.3,afade=t=out:st={END - 1.6:.2f}:d=1.6,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-i", REF, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", "30", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", f"{W}/out.mp4"], check=True)
print("done")
