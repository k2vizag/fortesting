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
caps = [  # Telugu captions (written from the dialogue's meaning; English words kept as spoken)
    C(0.00, 1.90, ("cw", "సార్,"), ("ch", "ఖాళీ చేతులతో వెళ్ళాలా?")),
    C(1.95, 3.05, ("ch", "ఎందుకు ఖాళీగా? 🤔")),
    C(3.10, 4.60, ("cw", "10 రోజుల్లో"), ("ch", "కలిసే వెళ్దాం")),
    C(5.80, 7.25, ("cw", "అమ్మా,"), ("ch", "రైలు టికెట్ తెచ్చావా?")),
    C(7.28, 7.95, ("ch g", "తెచ్చాను ✅")),
    C(7.96, 10.10, ("cw", "ప్లాట్‌ఫామ్ టికెట్"), ("ch", "కూడా తీసుకో 😂")),
    C(11.55, 12.65, ("ch", "ఎలా ఉన్నారు? 🙏")),
    C(12.66, 13.60, ("ch g", "బాగున్నాను")),
    C(13.65, 15.10, ("cw", "BP, షుగర్"), ("ch", "ఇంకా రాలేదు 😅")),
    C(16.20, 17.20, ("cw", "శనివారం"), ("ch", "వస్తానన్నావ్")),
    C(17.22, 18.80, ("ch", "శుక్రవారమే ఎందుకొచ్చావ్? 🤨")),
    C(18.85, 19.95, ("ch", "ఇటివ్వు")),
    C(20.00, 21.40, ("cw", "స్టేషన్ లో పడుకుని"), ("ch", "పొద్దున్నే వస్తా 😴")),
    C(22.80, 24.30, ("cw", "నాన్నకి"), ("ch", "నీళ్ళు తేనా?")),
    C(24.35, 24.85, ("ch", "ఎందుకు?")),
    C(26.00, 26.85, ("ch", "నువ్వు రెస్ట్ తీసుకో")),
    C(27.92, 30.20, ("cw", "సారీ అమ్మా,"), ("ch", "ఎంగేజ్‌మెంట్ కి రాలేకపోయా 🙏")),
    C(32.45, 33.50, ("ch", "వాడేమంటున్నాడు? 🤔")),
    C(33.60, 36.35, ("cw", "వాడు పారిపోయిన రోజే"), ("ch", "పెళ్ళి అయిపోయింది 😅")),
    C(37.70, 39.80, ("ch", "Knowledge is Divine 📚")),
    C(39.95, 41.80, ("cw", "అంటే..."), ("ch", "జ్ఞానం వైన్ లాంటిది 🍷")),
    C(41.90, 43.80, ("cw", "ఎంత తాగితే"), ("ch g", "అంత కిక్ 😂")),
    C(44.60, 46.10, ("ch", "ఏంటి అలా చూస్తున్నావ్? 👀")),
    C(46.60, 47.70, ("ch", "ఇంగ్లీష్ రాదా? 😏")),
    C(47.95, 49.70, ("cw", "Divine అంటే"), ("ch", "వైన్, విస్కీ కాదు 🙅")),
    C(50.70, 52.00, ("cw", "అంటే"), ("ch g", "చాలా గొప్పది 🙏")),
    C(53.20, 54.95, ("ch", "ఇప్పుడు అలా రాస్తున్నారా? ✍️")),
    C(55.40, 56.20, ("ch", "అవును")),
    C(57.60, 58.60, ("cw", "సరే..."), ("ch", "అలాగే రాయండి 😂")),
]
ST = [(1.0, "r", "🚗", ""), (8.2, "l", "🚉", ""), (13.8, "r", "😅", ""), (17.4, "l", "🤨", ""), (20.2, "r", "😴", ""),
      (28.0, "l", "💍", ""), (34.0, "r", "🏃", ""), (37.8, "l", "📚", ""), (40.2, "r", "🍷", ""), (42.0, "l", "🤣", ""),
      (44.7, "r", "👀", ""), (48.1, "l", "🥃", ""), (50.8, "r", "🙏", ""), (53.3, "l", "✍️", ""), (57.7, "r", "😂", "")]
stk = [{"a": t, "b": t + 1.8, "side": s, "emoji": e, "label": lb, "color": "blue", "y": 1170} for t, s, e, lb in ST]
hook = [{"cls": "chip", "t": "😂 బ్రహ్మి కామెడీ"}, {"cls": "en", "t": "Knowledge is Divine"},
        {"cls": "te", "t": "అంటే... జ్ఞానం వైన్ లాంటిది 🍷"}, {"cls": "te2", "t": "ఎంత తాగితే అంత కిక్! 🤣"}]
data = {"main_end": T + 100, "total": T, "captions": caps, "stickers": stk, "numbers": [], "cards": [],
        "board": {"phone": ""}, "title": None, "loc": False, "hook": hook, "photos": cols, "photo_period": 3.0}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
print("ok", round(T, 2))
