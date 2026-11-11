"""PAN card – funny version: original video/audio (no trim/speed), captions + emoji stickers only."""
import json, re, subprocess
S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
W = S + "/run4/work"
TOT = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", W + "/base.mov"],
                           capture_output=True, text=True).stdout)
SENT = [
    (1.73, 2.53, "రాజన్నా! 🙋"),
    (3.07, 10.07, "మన RTO వర్క్ చేస్తుంటావ్ కదా మన కస్టమర్స్‌కి LLR అంటే ఏంటి ఎలా అప్లై చేయాలో చెప్పు"),
    (10.07, 11.69, "నీతోని వింత నాటకం 🤣"),
    (23.87, 26.33, "DL కావాలంటే ఈ టెస్ట్ పాస్ అవ్వాలి"),
    (28.45, 31.31, "ముందు LLR తర్వాత డ్రైవింగ్ టెస్ట్ LLR అంటే లెర్నర్ లైసెన్స్"),
    (31.88, 35.27, "ఇది డ్రైవింగ్ టెస్ట్‌కి ఫస్ట్ స్టెప్ ఆన్‌లైన్‌లో అప్లై చేయాలి"),
    (35.92, 36.78, "ఎగ్జామ్ ఉంటుంది"),
    (37.34, 38.91, "కంప్యూటర్ బేస్డ్ టెస్ట్ ఉంటది"),
    (39.41, 40.90, "మల్టిపుల్ ఛాయిస్ ఉంటుంది"),
    (41.34, 43.95, "ట్రాఫిక్ సిగ్నల్స్ గురించి క్వశ్చన్స్ 🚦"),
    (45.56, 47.27, "దీనికి సంబంధించిన క్వశ్చన్స్ ఆన్సర్స్"),
    (47.63, 48.25, "యూట్యూబ్‌లో ఉంటాయి"),
    (48.74, 49.65, "వాటిని బాగా ప్రిపేర్ అయితే"),
    (50.08, 50.86, "టెస్ట్ బాగా రాయొచ్చు"),
    (53.06, 55.76, "LLR పాస్ అయితే"),
    (56.20, 58.37, "దాన్ని డౌన్‌లోడ్ చేసుకుని వాడుకోవచ్చు"),
    (58.78, 60.31, "సిక్స్ మంత్స్ వరకు వాలిడిటీ ఉంటుంది"),
    (61.11, 65.26, "కానీ మీ వెనకాల లైసెన్స్ ఉన్నవాళ్ళు ఉండాలి"),
    (71.82, 76.19, "ఇప్పుడు DL ప్రాసెస్ చెప్తాను LLR వచ్చిన వన్ మంత్ తర్వాత డ్రైవింగ్ టెస్ట్‌కి వెళ్ళొచ్చు"),
    (76.91, 78.33, "అది కూడా స్లాట్ బుక్ చేసుకోవాలి"),
    (78.90, 80.19, "ఏ రోజు బుక్ చేస్తే ఆ రోజు వెళ్ళాలి"),
    (80.85, 82.73, "ముందుగా మీరు బాగా డ్రైవింగ్ నేర్చుకోండి"),
    (83.36, 87.62, "అప్లై చేసేటప్పుడు మీకు ఏ రోజు వీలుంటుందో ఆ రోజు వెళ్ళండి"),
    (88.70, 90.60, "నేను మరి అంత ఎదవలా కనపడుతున్నానా? 😂"),
    (90.60, 91.70, "డ్రైవింగ్ టెస్ట్ బాగా చేస్తే"),
    (92.40, 96.35, "పాస్ అయితే వన్ వీక్‌లో కార్డ్ కొరియర్ చేస్తారు అది 20 ఇయర్స్ వాలిడిటీ ఉంటుంది"),
    (96.70, 97.71, "అది ఏజ్ బట్టి ఉంటుంది"),
]
KEY = ["RTO", "LLR", "DL", "లెర్నర్", "డ్రైవింగ్", "టెస్ట్", "ఆన్‌లైన్‌లో", "ఎగ్జామ్", "కంప్యూటర్", "మల్టిపుల్", "ట్రాఫిక్",
       "క్వశ్చన్స్", "యూట్యూబ్‌లో", "ప్రిపేర్", "పాస్", "డౌన్‌లోడ్", "సిక్స్", "వాలిడిటీ", "లైసెన్స్", "వన్", "స్లాట్",
       "కొరియర్", "20", "ఏజ్", "ఎదవలా", "రాజన్నా!", "నాటకం", "ఫస్ట్"]
GREEN = ["పాస్", "ఎదవలా", "నాటకం", "రాజన్నా!"]
EMO = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")
def is_key(w):
    c = w.strip("?,")
    return bool(re.match(r"^[0-9]", c)) or any(c.startswith(k) for k in KEY) or c in GREEN
caps = []
for a, b, text in SENT:
    words = text.split(); chunks = []; i = 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 24: n = 2
        if len(words) - i - n == 1: n = n + 1 if n < 3 else n - 1
        chunks.append(words[i:i+n]); i += n
    tot = sum(len(" ".join(c)) for c in chunks); cur = a + 0.02; span = b - a - 0.04
    for c in chunks:
        dur = span * len(" ".join(c)) / tot
        fl = [is_key(w) and not EMO.fullmatch(w) for w in c]; lines = []
        if any(fl):
            k0 = fl.index(True); k1 = k0
            while k1 + 1 < len(c) and fl[k1 + 1] and k1 - k0 < 1: k1 += 1
            hero = " ".join(c[k0:k1+1])
            pre, post = " ".join(c[:k0]), " ".join(c[k1+1:])
            if pre: lines.append({"cls": "cw", "t": pre})
            lines.append({"cls": "ch g" if any(hero.startswith(g) for g in GREEN) else "ch", "t": hero})
            if post: lines.append({"cls": "cw", "t": post})
        else:
            lines.append({"cls": "cw", "t": " ".join(c)})
        caps.append({"a": round(cur, 3), "b": round(cur + dur, 3), "lines": lines}); cur += dur
# emoji + icon stickers: (time, side, emoji or None, icon, label, color, duration)
ST = [
    (1.8, "r", "🙋", None, "", None, 2.2),
    (10.1, "l", "🤣", None, "", None, 2.0),
    (12.4, "r", "🏍️", None, "పట్ పట్ 💨", None, 6.5),
    (23.9, "l", None, "idc", "DL", "blue", 2.6),
    (28.6, "r", "📝", None, "LLR", None, 2.8),
    (33.4, "l", "💻", None, "ఆన్‌లైన్", None, 2.4),
    (37.4, "r", "🖥️", None, "కంప్యూటర్ టెస్ట్", None, 2.4),
    (41.4, "l", "🚦", None, "", None, 2.6),
    (47.6, "r", "📺", None, "YouTube", None, 2.6),
    (53.1, "l", "✅", None, "పాస్", None, 2.4),
    (56.3, "r", "📥", None, "డౌన్‌లోడ్", None, 2.2),
    (58.8, "l", "📅", None, "6 నెలలు", None, 2.6),
    (67.4, "r", "🤨", None, "", None, 3.4),
    (71.9, "l", "🚗", None, "DL టెస్ట్", None, 2.8),
    (76.9, "r", "📅", None, "స్లాట్ బుక్", None, 2.6),
    (80.9, "l", "🚘", None, "", None, 2.0),
    (88.7, "r", "😂", None, "", None, 3.0),
    (92.5, "l", "📦", None, "కొరియర్", None, 2.4),
    (95.0, "r", "🗓️", None, "20 ఇయర్స్", None, 2.6),
    (98.3, "l", "🙏", None, "", None, 1.7),
]
stk = []
for t0, side, emo, icon, label, color, d in ST:
    s = {"a": t0, "b": t0 + d, "side": side, "label": label, "color": color or "blue", "icon": icon or "check"}
    if emo: s["emoji"] = emo
    stk.append(s)
data = {"main_end": TOT + 100, "total": TOT, "captions": caps, "stickers": stk, "numbers": [], "cards": [],
        "board": {"phone": "7989615350"}, "title": None}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
print("total", round(TOT, 2), "captions", len(caps), "stickers", len(stk))
