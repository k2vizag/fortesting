"""Dialogue intro (~14 s) before the song: king's order -> Veer's reply (with Chintu) -> Veer asks for the blessing.
Then joined with the 45 s song cut -> veer_kingdom_farewell_full.mp4."""
import subprocess
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/emo"
I = S + "/intro"
# (video clip, v in, v out, audio clip, a in, a out)  – audio duration defines the piece; video is stretched to fit
P = [
    ("i1", 0.00, 5.55, "i1", 0.00, 5.55),   # King: "చింటూ చేసిన తప్పుకు ... వెంటనే రాజ్యం విడిచి వెళ్లాలి" (on the king's close-up)
    ("i4", 5.05, 6.80, "i4", 5.05, 7.00),   # Veer: "తమ్ముడిని ఒంటరిగా పంపించను నాన్నా" (Veer speaking)
    ("i1", 5.50, 7.40, "i4", 7.00, 9.30),   # Veer: "వాడితో పాటు నేను కూడా రాజ్యాన్ని వదిలి వెళ్తాను" – over Veer holding Chintu's hand
    ("i2", 5.70, 8.95, "i2", 5.70, 9.95),   # Veer: "నాన్నగారు, నేను బయలుదేరుతున్నాను, నీ ఆశీర్వాదం కావాలి" + the king blesses him (cut before he walks away; song starts)
]
ins, fc = [], []
for k, (vc, va, vb, ac, aa, ab) in enumerate(P):
    ins += ["-t", f"{vb - va:.3f}", "-ss", str(va), "-i", f"{I}/{vc}.mp4", "-t", f"{ab - aa:.3f}", "-ss", str(aa), "-i", f"{I}/{ac}.mp4"]
    d = ab - aa; sp = (vb - va) / d
    mi = ",minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1" if sp < 0.95 else ",fps=30"
    fc.append(f"[{2*k}:v]setpts=(PTS-STARTPTS)/{sp:.4f}{mi},scale=1080:1920:flags=lanczos,setsar=1,trim=duration={d:.3f},setpts=PTS-STARTPTS[v{k}]")
    fc.append(f"[{2*k+1}:a]aresample=48000,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st={d-0.04:.3f}:d=0.04[a{k}]")
n = len(P)
fc.append("".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca]")
fc.append("[cv]eq=contrast=1.06:saturation=1.08:gamma=0.98,colorbalance=rs=0.03:bs=-0.03,vignette=PI/5,fade=t=in:d=0.5,format=yuv420p[v]")
fc.append("[ca]loudnorm=I=-15:TP=-1.5:LRA=11,aresample=48000[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]", "-c:v", "libx264",
                "-crf", "18", "-r", "30", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "../veer_kingdom_intro.mp4"], check=True)
# join: intro + 45 s song cut, short dissolve
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", "../veer_kingdom_intro.mp4"],
                         capture_output=True, text=True).stdout)
X = 0.4
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "../veer_kingdom_intro.mp4", "-i", "../veer_kingdom_farewell_45s.mp4", "-filter_complex",
                f"[0:v]fps=30,settb=AVTB[a0];[1:v]fps=30,settb=AVTB[b0];[a0][b0]xfade=transition=fade:duration={X}:offset={d - X:.3f},format=yuv420p[v];"
                f"[0:a][1:a]acrossfade=d={X}[a]", "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "18", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", "../veer_kingdom_farewell_full.mp4"], check=True)
print("intro", round(d, 2), "done")
