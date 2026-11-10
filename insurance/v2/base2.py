"""Full-bleed 9:16 base video (face-centred crop from 4K) + cleaned voice, for bike|car.
Writes work2_<kind>/base.mov and timeline.json."""
import json, os, subprocess, sys
import cv2, numpy as np

S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
R = S + "/ins"
KIND = sys.argv[1]
src = open(R + "/build.py").read().split("# ---------------------------------------------------------------- cut video")[0]
ns = {"__name__": "segs"}
sys_argv = sys.argv
exec(compile(src.replace("KIND = sys.argv[1]", f"KIND = {KIND!r}"), "build.py", "exec"), ns)
SEGS = ns["SEGS"]

work = f"{R}/work4_{KIND}"
os.makedirs(work, exist_ok=True)
casc = cv2.CascadeClassifier(S + "/cvpkg/cv2/data/haarcascade_frontalface_default.xml")
fc_path = R + "/faces.json"
faces = json.load(open(fc_path)) if os.path.exists(fc_path) else {}

def face_x(a, b):
    key = f"{a:.2f}-{b:.2f}"
    if key in faces:
        return faces[key]
    xs = []
    for t in np.linspace(a + 0.2, b - 0.2, 3):
        img = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", R + "/raw.mp4", "-frames:v", "1",
                              "-vf", "scale=960:540", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
        g = np.frombuffer(img, np.uint8).reshape(540, 960)
        f = casc.detectMultiScale(g, 1.1, 5, minSize=(80, 80))
        if len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3])
            xs.append((x + w / 2) * 4)
    cx = float(np.median(xs)) if xs else 1700.0
    faces[key] = cx
    json.dump(faces, open(fc_path, "w"))
    return cx

SPEED = 1.10
EDIT = {
    "B1": ([(2.12, 6.08)], "కాంప్రహెన్సివ్ అంటే ఇందులో మన పర్సనల్ యాక్సిడెంట్ కవర్ పెట్టుకోవచ్చు"),
    "B7": ([(34.45, 36.60)], "మనకి IDV వాల్యూ ఉంటది అన్నమాట"),
    "B6": ([(30.45, 33.70)], "బండి ఎన్ని ఇయర్స్ నడిపామన్న దాన్ని బట్టి"),
    "B11": ([(58.95, 60.0), (60.8, 63.75)], "దానికి పర్సనల్ యాక్సిడెంట్ 350 యాడ్ చేస్తే మీకు 1200 అవుతుంది"),
    "B12": ([(64.05, 67.10)], "ఇంకో 400 యాడ్ చేస్తే బండికి కూడా కవర్ అవుతుంది"),
    "T5": ([(191.80, 192.72), (193.30, 194.10)], "మనకు కవర్ అయ్యేది 15 లక్షలు"),
    "T6": ([(196.85, 200.05)], "సో ఇంటికి కొంచెం ఉంటది యాక్సిడెంట్‌లో మనకి ఏమైనా అయినప్పుడు"),
    "T7": ([(203.55, 204.45)], "ఉంచుకోవడం బెటర్"),
    "T9": ([(218.15, 218.98), (219.68, 224.95)], "5 ఇయర్స్ తర్వాత మీకు ఓకే అనుకుంటే మరీ ఎక్కువ ప్రీమియం ఏమీ ఉండదు 400 ఏదో ఉంటది సంవత్సరానికి"),
    "T13": ([(241.75, 243.22)], "అదే మీకిచ్చే టిప్స్ అన్నమాట"),
    "T14": ([(243.41, 247.90)], "లాస్ట్ టూ ఇయర్స్ నుండి ఇన్సూరెన్స్ సర్వీసెస్ చేస్తున్నాము"),
    "B18": ([(132.38, 134.38)], "బైక్ అయితే ఇన్స్పెక్షన్ ఏమీ ఉండదు"),
    "C10": ([(132.38, 137.05)], "బైక్ అయితే ఇన్స్పెక్షన్ ఏమీ ఉండదు కార్స్‌కి ఇన్స్పెక్షన్ ఉంటది"),
    "C8": ([(124.15, 127.45)], "రోడ్‌సైడ్ అసిస్టెన్స్ అని ఇవన్నీ సెపరేట్‌గా యాడ్ చేసుకుంటే"),
    "T11": ([(230.75, 233.40)], "నార్మల్‌గా ఆ IDV వాల్యూ కూడా తక్కువ ఇస్తారు మీకు"),
}
DB = np.load(R + "/db2.npy")   # 10 ms frames, from the DeepFilterNet-cleaned voice
TH = -48.0

def split_pauses(a, b, min_gap=0.12, pad=0.05):
    """trim dead air at the edges and cut every internal pause longer than min_gap."""
    i0, i1 = int(a * 100), int(b * 100)
    sp = DB[i0:i1] > TH
    idx = np.where(sp)[0]
    if len(idx) == 0:
        return [(a, b)]
    a2 = max(a, (i0 + idx[0]) / 100 - 0.04)
    b2 = min(b, (i0 + idx[-1] + 1) / 100 + 0.06)
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

PIECES = []
NEWSEGS = []
for sid, a, b, txt in SEGS:
    rngs, txt = EDIT.get(sid, ([(a, b)], txt))
    for (x, y) in rngs:
        for (p, q) in split_pauses(x, y):
            PIECES.append((sid, p, q))
    NEWSEGS.append((sid, rngs[0][0], rngs[-1][1], txt))
SEGS = NEWSEGS
CW = 1736  # 30% wider than the old 1215 crop -> face 30% smaller
timeline = {}
lst = []
t = 0.0
for i, (sid, a, b) in enumerate(PIECES):
    d = round(b - a, 3)
    cx = face_x(a, b)
    zoom = 1.07 if i % 2 else 1.0
    cw, ch = int(CW / zoom) // 2 * 2, int(2160 / zoom) // 2 * 2
    x0 = int(min(max(cx - cw / 2, 0), 3840 - cw))
    y0 = int((2160 - ch) * 0.2)
    f = f"{work}/s{i:02d}.mov"
    if not os.path.exists(f):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", R + "/raw.mp4",
                        "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", R + "/dn.wav",
                        "-filter_complex", (f"[0:v]crop={cw}:{ch}:{x0}:{y0},setsar=1,split[a][b];"
                        f"[a]scale=-2:1920,crop=1080:1920,boxblur=30:2,eq=brightness=-0.10:saturation=1.0[bg];"
                        f"[b]scale=1080:1344:flags=lanczos[fg];[bg][fg]overlay=0:288,setpts=(PTS-STARTPTS)/{SPEED},fps=30[v]"),
                        "-map", "[v]", "-map", "1:a",
                        "-af", f"afade=t=in:d=0.02,afade=t=out:st={d-0.035:.3f}:d=0.035,atempo={SPEED}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "13", "-c:a", "pcm_s16le", "-ar", "48000",
                        "-ac", "2", f], check=True)
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
    if sid in timeline: timeline[sid][1] = t + real
    else: timeline[sid] = [t, t + real]
    t += real
    lst.append(f)
END_LEN = 4.0
end_f = f"{work}/end.mov"
if not os.path.exists(end_f):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=0x0b0b14:s=1080x1920:r=30", "-f", "lavfi",
                    "-i", "anullsrc=r=48000:cl=stereo", "-t", str(END_LEN), "-c:v", "libx264", "-preset", "veryfast",
                    "-crf", "13", "-c:a", "pcm_s16le", end_f], check=True)
lst.append(end_f)
open(f"{work}/list.txt", "w").write("".join(f"file '{x}'\n" for x in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/list.txt", "-c", "copy",
                f"{work}/base.mov"], check=True)
json.dump({"timeline": timeline, "main_end": t, "total": t + END_LEN,
           "segs": [[s, a, b, txt] for s, a, b, txt in SEGS]}, open(f"{work}/timeline.json", "w"), ensure_ascii=False, indent=1)
print(KIND, "main", round(t, 2), "total", round(t + END_LEN, 2))
