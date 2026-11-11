"""PAN card – funny version: original video/audio (no trim/speed), captions + emoji stickers only."""
import json, re, subprocess
S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
W = S + "/run5/work"
TOT = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", W + "/base.mov"],
                           capture_output=True, text=True).stdout)
SENT = [
    (0.56, 2.70, "జిరాక్స్ కాస్ట్ ఎంత? ప్రింట్ కాస్ట్ ఎంత? 🤔"),
    (3.29, 4.96, "జిరాక్స్ పేజీ 2 రూపీస్"),
    (5.55, 7.32, "ప్రింట్ కాస్ట్ 3 రూపీస్"),
    (7.62, 9.92, "జిరాక్స్ అంటే ఏదైనా పేపర్ గానీ"),
    (10.26, 12.26, "ఆధార్ కార్డ్ గానీ తెచ్చిస్తే"),
    (12.84, 14.99, "దాన్ని కాపీ తీసి ఇస్తాం"),
    (15.69, 16.59, "మరి ప్రింట్ ఏంటి? 🧐"),
    (18.22, 20.80, "కంప్యూటర్ లేదా PC నుంచి ప్రింట్"),
    (20.80, 22.40, "ఇందులో డిఫరెన్స్ ఏంటి?"),
    (22.40, 23.90, "అది జిరాక్స్ ఇది ప్రింట్"),
    (23.90, 25.76, "సార్ సార్ ఏంటి సార్ అది? 😂"),
    (26.16, 29.49, "అది జిరాక్స్ ఇది ప్రింట్ ప్రింట్ చేయాలంటే"),
    (30.06, 31.37, "ప్రింట్ అయితే కంప్యూటర్ ఉండాలి"),
    (32.43, 35.22, "కంప్యూటర్ వచ్చిన ఆపరేటర్ ఉండాలి"),
    (36.20, 38.64, "దానికి మళ్ళీ సపరేట్ ప్రింటర్ కొనాలి"),
    (39.12, 41.40, "కేబుల్స్ వేసి కనెక్ట్ చేయాలి"),
    (41.40, 44.59, "అదే జిరాక్స్ అయితే జిరాక్స్ మెషిన్ ఉంటే సరిపోతుంది"),
    (44.98, 47.32, "ఎవరైనా తీయొచ్చు ఆటోమేటిక్‌గా ⚡"),
    (50.09, 52.95, "పెన్ డ్రైవ్ తీసుకొస్తారు లేదా వాట్సాప్ చేస్తారు"),
    (56.42, 58.90, "పెన్ డ్రైవ్ మెయిల్ 📧"),
]
KEY = ["జిరాక్స్", "ప్రింట్", "కాస్ట్", "2", "3", "పేపర్", "ఆధార్", "కాపీ", "కంప్యూటర్", "PC", "డిఫరెన్స్", "ఆపరేటర్",
       "ప్రింటర్", "కేబుల్స్", "మెషిన్", "ఆటోమేటిక్‌గా", "పెన్", "వాట్సాప్", "మెయిల్", "సార్", "సరిపోతుంది"]
GREEN = ["సార్", "సరిపోతుంది", "ఆటోమేటిక్‌గా"]
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
        cp = {"a": round(cur, 3), "b": round(cur + dur, 3), "lines": lines}
        if cur > 53.5: cp["top"] = 640
        caps.append(cp); cur += dur
# emoji + icon stickers: (time, side, emoji or None, icon, label, color, duration)
ST = [
    (0.7, "r", "🤔", None, "", None, 2.0),
    (3.3, "l", "💰", None, "జిరాక్స్ ₹2", None, 2.0),
    (5.6, "r", "🖨️", None, "ప్రింట్ ₹3", None, 2.0),
    (10.3, "l", None, "idc", "ఆధార్", "orange", 2.2),
    (15.7, "r", "🧐", None, "", None, 1.6),
    (18.3, "l", "💻", None, "PC", None, 2.4),
    (24.0, "r", "😂", None, "", None, 3.0),
    (30.1, "l", "💻", None, "కంప్యూటర్", None, 2.2),
    (32.5, "r", "👨‍💻", None, "ఆపరేటర్", None, 2.6),
    (36.2, "l", "🖨️", None, "ప్రింటర్", None, 2.4),
    (39.2, "r", "🔌", None, "కేబుల్స్", None, 2.2),
    (41.6, "l", "📠", None, "జిరాక్స్ మెషిన్", None, 2.8),
    (45.0, "r", "⚡", None, "ఆటోమేటిక్", None, 2.2),
    (50.1, "l", "💾", None, "పెన్ డ్రైవ్", None, 2.0),
    (51.8, "r", "📱", None, "WhatsApp", None, 1.9),
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
