"""Pollution OTP short: arrange best takes of 11 AI clips per script, cut pauses, 1.1x, 9:16 1080x1920.
Writes work/base.mov (with 4 s end screen) and work/timeline.json"""
import json, os, subprocess
import numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-fortesting/f0703b19-2505-5b8b-b72d-114eb35464cd/scratchpad/pol"
RAW, W = S + "/raw", S + "/work"
os.makedirs(W, exist_ok=True)
SP = 1.10
# (id, clip, start, end, speaker)  – best take of every script line
SEGS = [
    ("L1",  "c00", 0.28, 1.48, "N"),
    ("L2",  "c03", 0.12, 6.45, "P"),
    ("L3",  "c00", 2.12, 9.58, "N"),
    ("L4",  "c02", 0.36, 8.40, "P"),
    ("L5",  "c01", 4.85, 8.84, "N"),
    ("L6",  "c10", 0.30, 10.02, "N"),
    ("L7",  "c09", 1.40, 4.42, "K"),
    ("L8",  "c04", 0.20, 1.80, "N"),
    ("L9",  "c06", 0.06, 3.01, "K"),
    ("L10", "c04", 2.17, 4.90, "N"),
    ("L11a", "c07", 3.90, 10.02, "K"),
    ("L11b", "c06", 3.03, 7.93, "K"),
    ("L12", "c04", 5.23, 9.92, "N"),
    ("L13a", "c09", 1.40, 1.73, "K"),
    ("PAUSE", "BLACK", 0.0, 2.0, "-"),     # 2 s black screen with topic text
    ("L13b", "c06", 7.94, 9.82, "K"),
    ("L13c", "c05", 1.06, 9.52, "K"),
]
# per-segment speed (default SP): Krishna's KYC part + ending at normal speed, "Avunu" slowed to the max (0.5x)
SPEED = {"L11a": 1.0, "L11b": 1.0, "L13b": 1.0, "L13c": 1.0, "L13a": 0.5}
# per-clip framing: (crop_w, crop_h, x, y) in source 478x850, None = full frame
CROP = {"c05": (377, 670, 50, 0),      # hide burned-in subtitles at the bottom
        "c04": (422, 750, 40, 100)}    # hide "Inside - Right Side" text at the top
dbc = {}
def db(clip):
    if clip not in dbc:
        x, sr = sf.read(f"{RAW}/{clip}.wav"); f = sr // 100
        dbc[clip] = 20 * np.log10(np.sqrt(np.mean(x[:len(x)//f*f].reshape(-1, f) ** 2, 1)) + 1e-9)
    return dbc[clip]
def split(clip, a, b, gap=0.15, pad=0.05):
    d = db(clip); th = d.max() - 32
    i0, i1 = int(a * 100), min(int(b * 100), len(d))
    sp = d[i0:i1] > th; out, cur, i = [], a, 0
    while i < len(sp):
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if i > 0 and j < len(sp) and (j - i) / 100 >= gap:
                x, y = (i0 + i) / 100 + pad, (i0 + j) / 100 - pad
                if x - cur >= 0.35 and b - y >= 0.35: out.append((cur, x)); cur = y
            i = j
        else: i += 1
    out.append((cur, b)); return out
pieces = [(sid, clip, p, q, spk) for sid, clip, a, b, spk in SEGS
          for p, q in ([(a, b)] if clip == "BLACK" or sid == "L13a" else split(clip, a, b))]
tl, lst, t = [], [], 0.0
zs, prev = [], None
for sid, clip, a, b, spk in pieces:      # punch in only on a jump cut inside the same clip
    zs.append((1.07 if zs[-1] == 1.0 else 1.0) if prev == clip else 1.0); prev = clip
for i, (sid, clip, a, b, spk) in enumerate(pieces):
    d = round(b - a, 3); z = zs[i]; sp = SPEED.get(sid, SP)
    if clip == "BLACK":
        f = f"{W}/p{i:02d}.mov"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1920:r=30", "-f", "lavfi",
            "-i", "anullsrc=r=48000:cl=stereo", "-t", str(d), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
            "-c:a", "pcm_s16le", f], check=True)
        tl.append({"sid": sid, "clip": clip, "a": a, "b": b, "spk": spk, "t0": round(t, 3), "t1": round(t + d, 3)})
        t += d; lst.append(f); continue
    cw, ch, x0, y0 = CROP.get(clip, (478, 850, 0, 0))
    cw2, ch2 = int(cw / z) // 2 * 2, int(ch / z) // 2 * 2
    x0 += (cw - cw2) // 2; y0 += int((ch - ch2) * 0.3)
    f = f"{W}/p{i:02d}.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", f"{RAW}/{clip}.mp4",
        "-filter_complex", f"[0:v]delogo=x=383:y=750:w=32:h=36,crop={cw2}:{ch2}:{x0}:{y0},scale=1080:1920:flags=lanczos,unsharp=5:5:0.6,setsar=1,setpts=(PTS-STARTPTS)/{sp},fps=30[v];"
        f"[0:a]aresample=48000,afade=t=in:d=0.015,afade=t=out:st={d-0.03:.3f}:d=0.03,atempo={sp},aformat=channel_layouts=stereo[a]",
        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "pcm_s16le", f], check=True)
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
    tl.append({"sid": sid, "clip": clip, "a": a, "b": b, "spk": spk, "t0": round(t, 3), "t1": round(t + real, 3)})
    t += real; lst.append(f)
END = 4.0
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=0x0b0b14:s=1080x1920:r=30", "-f", "lavfi",
    "-i", "anullsrc=r=48000:cl=stereo", "-t", str(END), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
    "-c:a", "pcm_s16le", f"{W}/end.mov"], check=True)
lst.append(f"{W}/end.mov")
open(f"{W}/list.txt", "w").write("".join(f"file '{x}'\n" for x in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/list.txt", "-c", "copy", f"{W}/base.mov"], check=True)
json.dump({"pieces": tl, "main_end": t, "total": t + END}, open(f"{W}/timeline.json", "w"), indent=1)
print("main", round(t, 2), "pieces", len(tl))
for p in tl: print(p)
