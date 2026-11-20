"""RTO message (insurance / pollution) info video -> 1080x1920 short.
Cuts pauses/repeats, 1.1x, face-centred crop, DeepFilterNet voice. Writes $W/base.mov + timeline.json.
usage: build.py   (run dfn3.py first -> $W/dn.wav, and faces.json / db.npy from the analysis step)"""
import json, os, subprocess
import numpy as np

S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad"
RAW, W = S + "/dl/raw.mp4", S + "/w"
OUT = W + "/cuts"; os.makedirs(OUT, exist_ok=True)
SPEED = 1.10
SRC_W, SRC_H = 2160, 3840          # after auto-rotation (phone portrait)

# source ranges kept (seconds in raw), with what is said
KEEP = [
    (0.45, 4.65,   "అందరికీ RTO నుండి కొన్ని మెసేజెస్ వస్తున్నాయి ఇలాగా"),
    (5.10, 9.70,   "ఇవేంటంటే మీరు ... మన దగ్గర చిన్న రోడ్డే కదా"),
    (10.20, 13.50, "మన దగ్గర ట్రాఫిక్ పోలీసులు ఉండరు"),
    (14.00, 18.80, "ఇక్కడ ఎవరూ అడగరు ... ఇన్సూరెన్స్ పొల్యూషన్ చేయకుండా ఉంటే"),
    (19.15, 20.55, "ఇలాంటి మెసేజెస్ వస్తున్నాయి"),
    (21.00, 26.60, "సో మీ బండికి ఇన్సూరెన్స్ ఉందా పొల్యూషన్ ఉందా లేదా అని వాళ్ళకి తెలిసిపోతుంది అన్నమాట"),
    (27.00, 31.70, "సో మీకు అడిషనల్ ఫైన్ ఛాన్సెస్ ఉంటాయి ప్రెజెంట్ అయితే మీకు ఇన్ఫార్మ్ చేస్తున్నారు"),
    (32.10, 35.70, "సో మీరు అప్డేట్ చేసుకుంటారని వాళ్ళు చేస్తున్నారు"),
    (36.10, 39.05, "మీరు అప్డేట్ చేసుకోకపోతే ఫ్యూచర్‌లో మీకు ఫైన్ వస్తది"),
    (39.85, 41.45, "ఇంకోటి"),        # cut 41.45-44.70: 'ప్రెజెంట్ టోల్ గేట్ / టోల్ గేట్లు మీరు' (restart, user: trim 32-34 s)
    (44.70, 48.90, "ఇది మన దగ్గర స్టార్ట్ అవ్వలేదు కానీ వేరే రాష్ట్రాల్లో స్టార్ట్ అయింది"),
    (49.20, 52.95, "అక్కడ ఏంటంటే మీరు టోల్ ప్లాజా క్రాస్ అవుతారు కదా"),
    (53.10, 57.75, "క్రాస్ అయినప్పుడు మీకు అప్డేట్ వస్తది ఇన్సూరెన్స్ లాప్స్ అయినా పొల్యూషన్ లాప్స్ అయినా"),
    (58.00, 61.20, "ఒకవేళ లాప్స్ అయితే మీకు మెసేజ్ వచ్చి అప్డేట్ చేస్తారు"),
    (61.95, 64.00, "ఫైన్ అయితే ఫ్యూచర్‌లో ఉంటది చూసుకోండి"),
    (66.62, 67.58, "సబ్‌స్క్రైబ్ చేయండి"),                # cut: 69.5-71.0 repeated 'subscribe చేయని వాళ్ళు'
    (74.17, 76.62, "బాగుంది అనిపిస్తే లైక్ చేయండి"),  # cut 72.6-74.17 drawn-out 'ఆ.. ఎవరైనా' (user: trim 51-52 s); 76.6+ off-mic
]

DB = np.load(W + "/db.npy")      # 10 ms frames of the denoised voice
TH = -45.0
FACES = [f for f in json.load(open(W + "/faces.json")) if f[1] is not None]

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
json.dump({"intro": INTRO, "pieces": tl, "main_end": t, "total": t + END}, open(f"{W}/timeline.json", "w"), indent=0)
print("pieces", len(pieces), "main", round(t, 2), "total", round(t + END, 2))
