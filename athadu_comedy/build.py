"""Athadu comedy reel: black header with the best dialogue (covers the old movie-details text), scene band in the
middle, Telugu captions under it, rotating scene photos at the bottom. Writes work/base.mov, work/data.json, work/audio.wav.
Then: node render.js <work> full  -> work/video.mp4, and mux with audio.wav."""
import json, os, subprocess

S = "/tmp/claude-0/-home-user-fortesting/4e589d33-8934-5dd9-a5c1-fec76296f99d/scratchpad/mv"
SRC, W = S + "/m.mp4", S + "/work"
os.makedirs(W, exist_ok=True)
T = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", SRC],
                         capture_output=True, text=True).stdout)

# base: black 1080x1920; source scene band (rows 379-899) -> 1080x780 at y=560. Old header text + bottom still dropped.
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-f", "lavfi", "-i", f"color=black:s=1080x1920:r=30:d={T}",
                "-filter_complex",
                "[0:v]crop=720:520:0:379,scale=1080:780:flags=lanczos,hqdn3d=1:1:3:3,unsharp=5:5:0.7:3:3:0.2,"
                "eq=contrast=1.05:saturation=1.12,fps=30[b];[1:v][b]overlay=0:560:shortest=1,setsar=1,format=yuv420p[v]",
                "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "14", "-preset", "medium", f"{W}/base.mov"], check=True)
# audio: original dialogue, -14 LUFS
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000",
                "-ac", "2", f"{W}/audio.wav"], check=True)
# scene stills for the photo strip (crop of the scene band at these times)
STILLS = [(2, "80%"), (8, "60%"), (13, "35%"), (24, "55%"), (40, "45%"), (46, "40%"), (50, "50%"), (56, "45%"), (29.5, "40%")]
photos = []
for i, (t, pos) in enumerate(STILLS):
    out = f"{W}/st{i}.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(t), "-i", SRC, "-vf",
                    "crop=720:520:0:379,unsharp=5:5:0.6", "-frames:v", "1", "-q:v", "2", out], check=True)
    photos.append({"src": "file://" + out, "pos": f"{pos} 40%"})
cols = [photos[0::3], photos[1::3], photos[2::3]]

C = lambda a, b, *ls: {"a": a, "b": b, "top": 1362, "lines": [{"cls": c, "t": t} for c, t in ls]}
caps = [  # Telugu captions: large-v3 on music-removed audio, timed to the speech bursts
    C(0.10, 1.80, ("cw", "సార్,"), ("ch", "ఖాళీ గిన్నెలతో వెళ్ళాలా?")),
    C(1.95, 2.90, ("ch", "ఖాళీగా ఎందుకెళ్ళాలి? 🤔")),
    C(3.10, 4.30, ("cw", "పది రోజుల్లో"), ("ch", "కలిసే చల్దాం")),
    C(6.20, 7.05, ("cw", "అమ్మా,"), ("ch", "రైలు టికెట్ తీసావా?")),
    C(7.05, 8.00, ("ch", "తీసాను ✅")),
    C(8.00, 10.05, ("cw", "రైల్వే స్టేషన్ కి"), ("ch", "ప్లాట్‌ఫామ్ టికెట్ కూడా 😂")),
    C(11.55, 12.68, ("cw", "ఏవండీ,"), ("ch", "బాగున్నారా? 🙏")),
    C(12.68, 13.55, ("ch", "బాగున్నానండి")),
    C(13.70, 15.20, ("cw", "BP, షుగర్"), ("ch", "ఇంకా రాలేదు 😅")),
    C(16.30, 17.28, ("cw", "శనివారం"), ("ch", "వస్తానన్నారు")),
    C(17.28, 18.40, ("ch", "శుక్రవారమే వచ్చారేంటి? 🤨")),
    C(18.45, 19.60, ("ch", "ఇటివ్వండి")),
    C(20.10, 22.05, ("cw", "స్టేషన్ లో పడుకుని"), ("ch", "పొద్దున్నే వస్తాను 😴")),
    C(22.80, 23.80, ("cw", "నాన్నకి"), ("ch", "నీళ్ళు పెట్టించు")),
    C(23.95, 24.85, ("ch", "ఎందుకు?")),
    C(24.85, 26.00, ("cw", "బయటికెళ్ళి"), ("ch", "నూతిలో దూకేస్తా 😂")),
    C(26.00, 28.20, ("ch", "సాయంత్రం వస్తా")),
    C(28.45, 30.70, ("cw", "సారీ అమ్మా,"), ("ch", "ఎంగేజ్‌మెంట్ కి రాలేకపోయాను")),
    C(30.70, 31.80, ("cw", "పెళ్ళికొడుకు"), ("ch", "యావరేజ్ అంట కదా?")),
    C(33.60, 34.90, ("cw", "వాడు పారిపోయిన రోజే"), ("ch", "నీకు పెళ్ళైంది")),
    C(34.95, 37.40, ("cw", "ఇంకా నయం,"), ("ch", "వచ్చిన రోజు అవ్వలేదు 😅")),
    C(37.90, 40.25, ("ch", "Knowledge is Divine"), ("cw", "అంటే...")),
    C(40.50, 41.90, ("ch", "జ్ఞానం వైన్ లాంటిది 🍷")),
    C(41.95, 43.85, ("cw", "ఎంత తాగితే"), ("ch", "అంత మంచిది 😂")),
    C(45.00, 46.20, ("ch", "ఏంటి అలా చూస్తున్నారు? 👀")),
    C(46.75, 47.60, ("ch", "ఇంగ్లీష్ రాదా? 😏")),
    C(48.10, 49.85, ("cw", "Divine అంటే"), ("ch", "వైన్, విస్కీ కాదు 🙅")),
    C(50.70, 52.10, ("ch", "చాలా గొప్పది అని 🙏")),
    C(52.15, 55.15, ("ch", "ఇప్పుడు అలా రాస్తున్నారా? ✍️")),
    C(55.55, 56.70, ("ch", "ఆఁ")),
    C(57.65, 59.55, ("ch", "అలాగే రాస్తాను 😂")),
]
ST = [(1.0, "r", "🚗", ""), (8.0, "l", "🚉", ""), (13.8, "r", "😅", ""), (17.3, "l", "🤨", ""), (20.2, "r", "😴", ""),
      (28.5, "l", "💍", ""), (33.7, "r", "🏃", ""), (37.9, "l", "📚", ""), (40.5, "r", "🍷", ""), (42.0, "l", "🤣", ""),
      (45.0, "r", "👀", ""), (48.1, "l", "🥃", ""), (50.8, "r", "🙏", ""), (53.3, "l", "✍️", ""), (57.7, "r", "😂", "")]
stk = [{"a": t, "b": t + 1.8, "side": s, "emoji": e, "label": lb, "color": "blue", "y": 1170} for t, s, e, lb in ST]
hook = [{"cls": "chip", "t": "😂 బ్రహ్మి కామెడీ"}, {"cls": "en", "t": "Knowledge is Divine"},
        {"cls": "te", "t": "అంటే... జ్ఞానం వైన్ లాంటిది 🍷"}, {"cls": "te2", "t": "ఎంత తాగితే అంత మంచిది! 🤣"}]
data = {"main_end": T + 100, "total": T, "captions": caps, "stickers": stk, "numbers": [], "cards": [],
        "board": {"phone": ""}, "title": None, "loc": False, "hook": hook, "photos": cols, "photo_period": 3.0}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
print("ok", round(T, 2))
