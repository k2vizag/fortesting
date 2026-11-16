"""Veer story: captions (speaker-tagged), emoji stickers, title, end screen -> work/data.json + work/sfx.json"""
import json, re, subprocess
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad"
W = S + "/work"; SP = 1.1; END = 4.0
TOT = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", W + "/base.mov"],
                           capture_output=True, text=True).stdout)
MAIN = TOT - END
OFF = [0, 9.6, 19.6, 29.6, 39.6, 49.6]          # scene starts on the pre-speed timeline (base.py order)
WHO = {"K": "👑 రాజు", "V": "🦁 వీర్", "C": "🧒 చింటూ", "O": "🐆 షాప్ ఓనర్", "R": "కృష్ణ"}
# (scene, start, end, speaker, text) – times local to the scene, pre-speed (from transcription)
SENT = [
    (0, 0.00, 3.04, "K", "చింటూ చేసిన తప్పుకు ఈ రాజ్యంలో స్థానం లేదు!"),
    (0, 3.18, 4.68, "K", "వెంటనే రాజ్యం విడిచి వెళ్లాలి!"),
    (0, 4.68, 6.64, "V", "తమ్ముడిని ఒంటరిగా పంపించను నాన్నా"),
    (0, 6.64, 9.10, "V", "వాడితో పాటు నేను కూడా రాజ్యాన్ని వదిలి వెళ్తాను!"),
    (1, 2.60, 5.08, "C", "అన్నయ్యా! మనం ఎక్కడ ఉంటాం?"),
    (1, 5.08, 7.24, "V", "ఇక్కడే ఒక చిన్న ఇల్లు తీసుకుందాం తమ్ముడా"),
    (1, 7.24, 8.60, "V", "నిన్ను బాగా చూసుకుంటాను"),
    (2, 0.00, 3.20, "V", "నేను ఏ పనైనా కష్టపడి చేస్తాను సార్!"),
    (2, 3.20, 4.08, "O", "ఉద్యోగం ఇవ్వలేం!"),
    (2, 5.30, 7.12, "V", "ప్లీజ్ సార్... ప్లీజ్ సార్!"),
    (3, 2.10, 4.86, "V", "సార్! నాకు ఏదైనా చిన్న పని ఇప్పిస్తారా?"),
    (3, 5.20, 7.60, "R", "నువ్వు సింహానివి కదా! మా షాప్‌లో నీకు ఏం పని ఉంటుంది?"),
    (3, 9.16, 10.0, "R", "ఆగు... ఒకసారి ఇలా రా!"),
    (4, 0.00, 3.58, "V", "సార్! ఇన్ని షాపులు తిరిగినా ఎవ్వరూ నాకు పని ఇవ్వలేదు"),
    (4, 3.58, 5.00, "V", "మీరు నాకు సహాయం చేశారు"),
    (4, 5.00, 7.08, "V", "మీ మేలు ఎప్పటికీ మర్చిపోలేను!"),
    (4, 7.08, 8.18, "R", "బాధపడకు వీరా!"),
    (4, 8.18, 9.98, "R", "రేపటి నుంచి మనం కలిసి పనిచేద్దాం"),
    (5, 0.00, 3.00, "R", "వీరా! మన షాప్ సర్వీసుల గురించి నువ్వు YouTubeలో వీడియోలు చేయాలి!"),
    (5, 3.00, 4.52, "R", "నేను చేస్తే ఎక్కువ Views రావడం లేదు"),
    (5, 4.52, 5.54, "R", "నువ్వు చేస్తే బాగా వస్తాయి!"),
    (5, 5.65, 7.29, "V", "నేను చెప్తే జనాలు చూస్తారా?"),
    (5, 7.81, 9.71, "R", "సింహానికి మామూలు క్రేజ్ లేదు!"),
    (5, 9.71, 11.19, "R", "నువ్వు మా షాప్‌కి హీరోవు!"),
]
KEY = ["చింటూ", "తప్పు", "స్థానం", "వెంటనే", "రాజ్యం", "తమ్ముడ", "ఒంటరిగా", "నాన్నా", "అన్నయ్యా", "ఎక్కడ", "ఇల్లు", "బాగా",
       "కష్టపడి", "ఉద్యోగం", "ప్లీజ్", "పని", "సింహానివి", "ఆగు", "ఎవ్వరూ", "సహాయం", "మేలు", "మర్చిపోలేను", "బాధపడకు",
       "కలిసి", "YouTube", "జనాలు", "సింహానికి", "క్రేజ్", "హీరోవు", "సర్వీసుల", "Views", "బాగా"]
GREEN = ["బాగా", "సహాయం", "కలిసి", "హీరోవు", "మేలు", "ఆగు"]
T = lambda sc, t: (OFF[sc] + t) / SP
def is_key(w):
    c = w.strip("?!,.")
    return any(c.startswith(k) for k in KEY)
caps = []
for sc, a, b, who, text in SENT:
    a, b = T(sc, a), T(sc, b)
    words = text.split(); chunks = []; i = 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 22: n = 2
        if len(words) - i - n == 1: n = n + 1 if n < 3 else n - 1
        chunks.append(words[i:i+n]); i += n
    tot = sum(len(" ".join(c)) for c in chunks); cur = a + 0.02; span = b - a - 0.04
    for ci, c in enumerate(chunks):
        dur = span * len(" ".join(c)) / tot
        fl = [is_key(w) for w in c]; lines = []
        if any(fl):
            k0 = fl.index(True); k1 = k0
            hero = " ".join(c[k0:k1+1]); pre, post = " ".join(c[:k0]), " ".join(c[k1+1:])
            if pre: lines.append({"cls": "cw", "t": pre})
            lines.append({"cls": "ch g" if any(hero.strip("?!,.").startswith(g) for g in GREEN) else "ch", "t": hero})
            if post: lines.append({"cls": "cw", "t": post})
        else:
            lines.append({"cls": "cw", "t": " ".join(c)})
        lines.append({"cls": "cs", "t": "– " + WHO[who]})
        caps.append({"a": round(cur, 3), "b": round(cur + dur, 3), "lines": lines}); cur += dur
# stickers: (scene, local time, side, emoji, label, duration) – beside the characters, never on a face
ST = [
    (0, 0.3, "r", "👑", "రాజు ఆజ్ఞ", 2.6),
    (0, 5.0, "l", "🤝", "అన్న త్యాగం", 3.0),
    (0, 8.4, "r", "😢", "", 1.6),
    (1, 0.3, "l", "🏙️", "విశాఖపట్నం", 2.6),
    (1, 5.3, "r", "🏠", "చిన్న ఇల్లు", 2.2),
    (1, 7.8, "l", "❤️", "", 2.0),
    (2, 3.2, "r", "🙅", "ఉద్యోగం లేదు", 2.0),
    (2, 7.6, "l", "😞", "", 2.2),
    (3, 0.3, "r", "🖥️", "K2 వైజాగ్", 2.4),
    (3, 5.4, "l", "🤔", "", 2.0),
    (3, 9.2, "r", "✋", "ఆగు!", 1.4),
    (4, 0.4, "l", "😭", "", 2.4),
    (4, 3.8, "r", "🤗", "థాంక్యూ సార్", 3.0),
    (4, 8.3, "l", "🤝", "కలిసి పని", 1.7),
    (5, 1.9, "r", "🎥", "YouTube", 2.0),
    (5, 3.2, "l", "📉", "Views లేవు", 1.6),
    (5, 5.8, "r", "🤔", "", 1.6),
    (5, 9.8, "r", "🦁", "K2 హీరో", 2.0),
]
stk = [{"a": T(sc, t), "b": min(T(sc, t) + d / SP, MAIN - 0.05), "side": s, "label": lb, "emoji": e, "color": "blue", "icon": "check"}
       for sc, t, s, e, lb, d in ST]
data = {"main_end": MAIN, "total": TOT, "captions": caps, "stickers": stk, "numbers": [], "cards": [],
        "board": {"phone": "7989615350"}, "title": ["సింహం వీర్ కథ 🦁", "K2 వైజాగ్ హీరో"]}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
sfx = [{"t": s["a"], "k": "pop"} for s in stk] + [{"t": MAIN, "k": "whoosh"}, {"t": MAIN, "k": "impact"},
       {"t": MAIN + 1.45, "k": "click"}, {"t": MAIN + 2.35, "k": "click"}]
json.dump(sfx, open(W + "/sfx.json", "w"))
print("total", round(TOT, 2), "main", round(MAIN, 2), "captions", len(caps), "stickers", len(stk))
