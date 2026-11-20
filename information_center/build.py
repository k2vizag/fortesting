"""RTO message (insurance / pollution) info video -> 1080x1920 short.
Cuts pauses/repeats, 1.1x, face-centred crop, DeepFilterNet voice. Writes $W/base.mov + timeline.json.
usage: build.py <config module, e.g. rto_message>   (run dfn3.py first -> $W/dn.wav, and faces.json / db.npy from the analysis step)"""
import importlib, json, os, subprocess, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CFG = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "rto_message")

S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad"
RAW, W = S + CFG.RAW, S + CFG.WORK
KEEP = CFG.KEEP
OUT = W + "/cuts"; os.makedirs(OUT, exist_ok=True)
SPEED = 1.10
SRC_W, SRC_H = 2160, 3840          # after auto-rotation (phone portrait)

DB = np.load(W + "/db.npy")      # 10 ms frames of the denoised voice
TH = -45.0
FACES = [f for f in json.load(open(W + "/faces.json")) if f[1] is not None and f[2] < 1900]

def split_pauses(a, b, min_gap=0.14, pad=0.05):
    i0, i1 = int(a * 100), int(b * 100)
    sp = DB[i0:i1] > TH; idx = np.where(sp)[0]
    if len(idx) == 0: return []
    a2 = max(a, (i0 + idx[0]) / 100 - 0.05); b2 = min(b, (i0 + idx[-1] + 1) / 100 + 0.07)
    pieces, cur, i = [], a2, idx[0]
    while i < idx[-1]:
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if (j - i) / 100 >= min_gap:
                x, y = (i0 + i) / 100 + pad, (i0 + j) / 100 - pad
                if x - cur >= 0.12: pieces.append((cur, x)); cur = y
            i = j
        else: i += 1
    pieces.append((cur, b2))
    return pieces

def face(a, b):
    fs = [f for f in FACES if a - 0.5 <= f[0] <= b + 0.5] or FACES
    return float(np.median([f[1] for f in fs])), float(np.median([f[2] for f in fs]))

ZOOM = 1.14            # light zoom so the face can be centred; still shows shoulders + room
INTRO = 1.0           # black screen with the title before the video starts
intro_f = f"{OUT}/intro.mov"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1920:r=30", "-f", "lavfi",
                "-i", "anullsrc=r=48000:cl=stereo", "-t", str(INTRO), "-c:v", "libx264", "-preset", "fast",
                "-crf", "12", "-c:a", "pcm_s16le", intro_f], check=True)
lst, t, tl, pieces = [intro_f], INTRO, [], []
for a, b, txt in KEEP:
    for p, q in split_pauses(a, b): pieces.append((p, q, txt))
for i, (a, b, txt) in enumerate(pieces):
    d = round(b - a, 3)
    fx, fy = face(a, b)
    z = ZOOM * (1.07 if i % 2 else 1.0)
    cw, ch = int(SRC_W / z) // 2 * 2, int(SRC_H / z) // 2 * 2
    x0 = int(min(max(fx - cw / 2, 0), SRC_W - cw))
    y0 = int(min(max(fy - 0.36 * ch, 0), SRC_H - ch))
    f = f"{OUT}/s{i:03d}.mov"
    subprocess.run(["ffmpeg", "-v", "error", "-y",
                    "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", RAW,
                    "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", W + "/dn.wav",
                    "-filter_complex",
                    f"[0:v]crop={cw}:{ch}:{x0}:{y0},scale=1080:1920:flags=lanczos,setsar=1,"
                    f"unsharp=5:5:0.55:5:5:0.0,eq=contrast=1.04:saturation=1.08,"
                    f"setpts=(PTS-STARTPTS)/{SPEED},fps=30[v];"
                    f"[1:a]afade=t=in:d=0.02,afade=t=out:st={d - 0.035:.3f}:d=0.035,atempo={SPEED}[a]",
                    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "fast", "-crf", "12",
                    "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f], check=True)
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
    tl.append([round(a, 2), round(b, 2), round(t, 2), round(t + real, 2)])
    t += real; lst.append(f)
END = 4.0
end_f = f"{OUT}/end.mov"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=0x0b0b14:s=1080x1920:r=30", "-f", "lavfi",
                "-i", "anullsrc=r=48000:cl=stereo", "-t", str(END), "-c:v", "libx264", "-preset", "fast",
                "-crf", "12", "-c:a", "pcm_s16le", end_f], check=True)
lst.append(end_f)
open(f"{OUT}/list.txt", "w").write("".join(f"file '{x}'\n" for x in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{OUT}/list.txt", "-c", "copy",
                f"{W}/base.mov"], check=True)
if getattr(CFG, "SHIRT", None):   # recolour the shirt on the cut video (cards/title are overlaid later)
    os.replace(f"{W}/base.mov", f"{W}/base_green.mov")
    subprocess.run([sys.executable, os.path.join(os.path.dirname(os.path.abspath(__file__)), "recolor.py"),
                    f"{W}/base_green.mov", f"{W}/base.mov", CFG.SHIRT], check=True)
json.dump({"intro": INTRO, "pieces": tl, "main_end": t, "total": t + END}, open(f"{W}/timeline.json", "w"), indent=0)
print("pieces", len(pieces), "main", round(t, 2), "total", round(t + END, 2))
