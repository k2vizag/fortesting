"""PAN card – funny version: original video/audio (no trim/speed), captions + emoji stickers only."""
import json, re, subprocess
S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
W = S + "/run3/work_fun"
TOT = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", W + "/base.mov"],
                           capture_output=True, text=True).stdout)
SENT = [
    (0.72, 5.52, "అన్నా మన కస్టమర్స్‌కి పాన్ కార్డ్ గురించి అంటే ఏ డాక్యుమెంట్స్ కావాలి? 🤔"),
    (6.68, 11.35, "పాన్ కార్డ్‌కి ఆధార్ కార్డ్ ఉంటే చాలు దాన్ని మేము ఆన్‌లైన్‌లో అప్లై చేస్తాం"),
    (11.72, 14.92, "ఆన్‌లైన్ ప్రాసెస్ లేదా ఆఫ్‌లైన్ చేస్తాం దానికి"),
    (15.27, 17.14, "పాస్‌పోర్ట్ సైజ్ ఫోటోలు 📸"),
    (17.52, 23.77, "ఆ ఫామ్ ఫిల్ చేసి ఎక్కడ సైన్ పెట్టాలో పెట్టించి మాకు ఇస్తే మేము అప్లై చేస్తాం"),
    (24.16, 26.07, "దానికి మేము 300 రూపాయలు ఛార్జ్ చేస్తాం 💸"),
    (27.44, 29.07, "అన్నా ఆన్‌లైన్ గురించి చెప్పు"),
    (35.76, 42.41, "ఆన్‌లైన్‌కి OTP వస్తది ఆధార్ OTP చెప్పాలి"),
    (42.80, 44.36, "గట్టిగా చెప్పనా? 😅"),
    (49.08, 53.03, "కొంచెం గట్టిగా 🔊 ఆన్‌లైన్ అయితే"),
    (53.89, 60.73, "ఆధార్ కార్డ్‌కి OTP నంబర్ పంపిస్తారు ఆ OTP నంబర్ మాకు చెప్తారు"),
    (62.12, 65.30, "ఆఫ్‌లైన్ అయితే"),
    (65.72, 72.60, "అప్లికేషన్ ఇస్తాం అప్లికేషన్ నింపిస్తాం రెండు ఫోటోలు అంటిస్తాం సైన్ చేసి ఇస్తాం"),
    (78.07, 83.26, "మేము అప్లై చేస్తాం దానికి కూడా 300 రూపాయలు ఛార్జ్ 💸"),
]
KEY = ["పాన్", "ఆధార్", "OTP", "ఆన్‌లైన్", "ఆఫ్‌లైన్", "పాస్‌పోర్ట్", "ఫోటోలు", "సైన్", "అప్లికేషన్", "ఛార్జ్",
       "డాక్యుమెంట్స్", "అప్లై", "300", "రెండు", "గట్టిగా"]
GREEN = ["చాలు", "అప్లై", "గట్టిగా"]
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
    (1.0, "r", "🤔", None, "", None, 3.0),
    (7.2, "l", None, "idc", "పాన్ కార్డ్", "blue", 2.6),
    (9.0, "r", None, "idc", "ఆధార్", "orange", 2.4),
    (15.3, "r", "📸", None, "", None, 2.2),
    (24.3, "l", "💸", None, "₹300", None, 2.6),
    (27.5, "r", "🙋", None, "", None, 1.8),
    (33.0, "r", "😂", None, "", None, 2.6),
    (36.2, "l", None, "otp", "OTP", "purple", 2.6),
    (42.8, "r", "😅", None, "", None, 2.0),
    (45.3, "l", "🤭", None, "", None, 3.4),
    (49.1, "r", "🔊", None, "", None, 2.2),
    (54.5, "l", "📱", None, "OTP", None, 2.6),
    (62.2, "r", None, "doc", "ఆఫ్‌లైన్", "orange", 2.6),
    (69.0, "l", "📸", None, "2 ఫోటోలు", None, 2.4),
    (73.9, "r", "🤣", None, "", None, 3.6),
    (79.5, "l", "💸", None, "₹300", None, 2.6),
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
