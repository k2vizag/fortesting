"""PAN card video: base (no trim/crop, 1.1x, denoised) + overlay plan + sfx."""
import json, re, subprocess
S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
R = S + "/run3"; W = R + "/work_pan"
SP = 1.10
DUR = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", R + "/dl/raw.mp4"],
                           capture_output=True, text=True).stdout)
END_LEN = 4.0
# ---- base video: full frame scaled to 1080x1920, 1.1x, cleaned voice + end screen
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", R + "/dl/raw.mp4", "-i", R + "/dn.wav",
    "-filter_complex", f"[0:v]scale=1080:1920:flags=lanczos,setsar=1,setpts=PTS/{SP},fps=30[v];[1:a]atempo={SP},aresample=48000,aformat=channel_layouts=stereo[a]",
    "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "pcm_s16le", W + "/main.mov"], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=0x0b0b14:s=1080x1920:r=30", "-f", "lavfi",
    "-i", "anullsrc=r=48000:cl=stereo", "-t", str(END_LEN), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
    "-c:a", "pcm_s16le", W + "/end.mov"], check=True)
open(W + "/list.txt", "w").write(f"file '{W}/main.mov'\nfile '{W}/end.mov'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", W + "/list.txt", "-c", "copy", W + "/base.mov"], check=True)
ME = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", W + "/main.mov"],
                          capture_output=True, text=True).stdout)
TOT = ME + END_LEN
T = lambda x: x / SP          # original time -> output time

SENT = [
    (0.72, 5.52, "అన్నా మన కస్టమర్స్‌కి పాన్ కార్డ్ గురించి అంటే ఏ డాక్యుమెంట్స్ కావాలి?"),
    (6.68, 11.35, "పాన్ కార్డ్‌కి ఆధార్ కార్డ్ ఉంటే చాలు దాన్ని మేము ఆన్‌లైన్‌లో అప్లై చేస్తాం"),
    (11.72, 14.92, "ఆన్‌లైన్ ప్రాసెస్ లేదా ఆఫ్‌లైన్ చేస్తాం దానికి"),
    (15.27, 17.14, "పాస్‌పోర్ట్ సైజ్ ఫోటోలు"),
    (17.52, 23.77, "ఆ ఫామ్ ఫిల్ చేసి ఎక్కడ సైన్ పెట్టాలో పెట్టించి మాకు ఇస్తే మేము అప్లై చేస్తాం"),
    (24.16, 26.07, "దానికి మేము 300 రూపాయలు ఛార్జ్ చేస్తాం"),
    (27.44, 29.07, "అన్నా ఆన్‌లైన్ గురించి చెప్పు"),
    (35.76, 42.41, "ఆన్‌లైన్‌కి OTP వస్తది ఆధార్ OTP చెప్పాలి"),
    (42.80, 44.36, "గట్టిగా చెప్పనా?"),
    (49.08, 53.03, "కొంచెం గట్టిగా ఆన్‌లైన్ అయితే"),
    (53.89, 60.73, "ఆధార్ కార్డ్‌కి OTP నంబర్ పంపిస్తారు ఆ OTP నంబర్ మాకు చెప్తారు"),
    (62.12, 65.30, "ఆఫ్‌లైన్ అయితే"),
    (65.72, 72.60, "అప్లికేషన్ ఇస్తాం అప్లికేషన్ నింపిస్తాం రెండు ఫోటోలు అంటిస్తాం సైన్ చేసి ఇస్తాం"),
    (78.07, 83.26, "మేము అప్లై చేస్తాం దానికి కూడా 300 రూపాయలు ఛార్జ్"),
]
KEY = ["పాన్", "ఆధార్", "OTP", "ఆన్‌లైన్", "ఆఫ్‌లైన్", "పాస్‌పోర్ట్", "ఫోటోలు", "సైన్", "అప్లికేషన్", "ఛార్జ్",
       "డాక్యుమెంట్స్", "కస్టమర్స్‌కి", "అప్లై", "నంబర్", "300", "రెండు"]
GREEN = ["చాలు", "అప్లై"]
SUBS = {"OTP": "వన్ టైమ్ పాస్‌వర్డ్", "పాన్ కార్డ్": "పర్మనెంట్ అకౌంట్ నంబర్"}
def is_key(w):
    c = w.strip("?,")
    return bool(re.match(r"^[0-9]", c)) or any(c.startswith(k) for k in KEY) or c in GREEN
caps, sfx = [], []
for a, b, text in SENT:
    st, en = T(a), T(b)
    words = text.split(); chunks = []; i = 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 24: n = 2
        if len(words) - i - n == 1: n = n + 1 if n < 3 else n - 1
        chunks.append(words[i:i+n]); i += n
    tot = sum(len(" ".join(c)) for c in chunks); cur = st + 0.02; span = en - st - 0.04
    for c in chunks:
        dur = span * len(" ".join(c)) / tot
        fl = [is_key(w) for w in c]; lines = []
        if any(fl):
            k0 = fl.index(True); k1 = k0
            while k1 + 1 < len(c) and fl[k1 + 1] and k1 - k0 < 1: k1 += 1
            hero = " ".join(c[k0:k1+1]).rstrip(",")
            pre, post = " ".join(c[:k0]), " ".join(c[k1+1:])
            if pre: lines.append({"cls": "cw", "t": pre})
            lines.append({"cls": "ch g" if any(hero.startswith(g) for g in GREEN) else "ch", "t": hero})
            if post: lines.append({"cls": "cs", "t": post})
            elif hero in SUBS: lines.append({"cls": "cs", "t": SUBS[hero]})
            sfx.append({"t": cur, "k": "tick_soft"})
        else:
            lines.append({"cls": "cw", "t": " ".join(c)})
        caps.append({"a": round(cur, 3), "b": round(cur + dur, 3), "lines": lines}); cur += dur

R_ = "₹"
cards = [
    dict(type="profile", theme="white", a=T(6.6), b=T(11.4), icon="idc", color="blue",
         kicker="PAN CARD · DOCUMENTS", title="ఆధార్ కార్డ్ ఉంటే చాలు", pill="ఆన్‌లైన్‌లో అప్లై",
         pillAt=T(9.2) - T(6.6), desc="పాన్ కార్డ్ కోసం వేరే డాక్యుమెంట్స్ అవసరం లేదు", tiles=["idc", "otp", "check"]),
    dict(type="timeline", theme="dark", a=T(15.1), b=T(26.2), kicker="PAN CARD · HOW WE APPLY", gap=250,
         steps=[{"v": "ఫోటోలు", "t": "పాస్‌పోర్ట్ సైజ్ ఫోటోలు", "s": "", "icon": "user", "at": 0.2},
                {"v": "ఫామ్", "t": "ఫిల్ చేసి సైన్ పెట్టాలి", "s": "", "icon": "pen", "at": T(17.6) - T(15.1)},
                {"v": "అప్లై", "t": "మేము అప్లై చేస్తాం", "s": "", "icon": "check", "at": T(21.6) - T(15.1)},
                {"v": f"{R_}300", "t": "ఛార్జ్", "s": "", "icon": "rupee", "at": T(24.3) - T(15.1)}]),
    dict(type="profile", theme="white", a=T(53.8), b=T(60.8), icon="phone", color="green",
         kicker="ONLINE · AADHAAR OTP", title="ఆధార్ OTP తో", pill="OTP చెప్తే చాలు",
         pillAt=T(57.6) - T(53.8), desc="ఆధార్ కార్డ్‌కి లింక్ అయిన మొబైల్‌కి OTP వస్తుంది", tiles=["phone", "otp", "check"]),
    dict(type="terminal", theme="dark", a=T(65.6), b=T(72.8), head="OFFLINE · PAN CARD",
         lines=[{"t": "అప్లికేషన్ ఫామ్ ఇస్తాం", "at": 0.3},
                {"t": "ఫామ్ నింపిస్తాం", "at": T(67.6) - T(65.6)},
                {"t": "2 ఫోటోలు అంటిస్తాం", "at": T(69.0) - T(65.6)},
                {"t": "సైన్ చేసి ఇవ్వాలి", "at": T(70.9) - T(65.6)}]),
    dict(type="journey", theme="white", a=T(78.0), b=T(83.5), kicker="PAN CARD · ONLINE / OFFLINE",
         nodes=[{"t": "ఆన్‌లైన్", "s": f"ఆధార్ OTP · {R_}300", "icon": "phone", "color": "blue", "at": 0.25},
                {"t": "ఆఫ్‌లైన్", "s": f"ఫామ్ + 2 ఫోటోలు · {R_}300", "icon": "doc", "color": "orange", "at": 0.8}]),
]
stk = [(1.0, "r", "idc", "పాన్ కార్డ్", "blue"), (12.0, "l", "phone", "ఆన్‌లైన్", "green"), (13.5, "r", "doc", "ఆఫ్‌లైన్", "orange"),
       (36.2, "r", "otp", "OTP", "purple"), (75.0, "r", "rupee", f"{R_}300", "yellow")]
stickers = []
for t0, side, icon, label, color in stk:
    stickers.append({"a": T(t0), "b": T(t0) + 2.6, "side": side, "icon": icon, "label": label, "color": color}); sfx.append({"t": T(t0), "k": "pop"})
numbers = [{"a": T(49.1), "b": T(53.0), "n": "1"}, {"a": T(62.1), "b": T(65.4), "n": "2"}]
for m in numbers: sfx += [{"t": m["a"] - 0.12, "k": "swish"}, {"t": m["a"] + 0.12, "k": "ding"}]
for c in cards:
    sfx += [{"t": c["a"] - 0.25, "k": "whoosh"}, {"t": c["a"], "k": "impact"}, {"t": c["b"] - 0.2, "k": "whoosh_out"}]
    if c["type"] == "profile": sfx.append({"t": c["a"] + c["pillAt"], "k": "chime"})
    if c["type"] == "timeline":
        for s_ in c["steps"]: sfx.append({"t": c["a"] + s_["at"], "k": "coin" if "₹" in s_["v"] else "tick"})
    if c["type"] == "journey":
        for nd in c["nodes"]: sfx.append({"t": c["a"] + nd["at"], "k": "tick"})
    if c["type"] == "terminal":
        for ln in c["lines"]:
            for k in range(0, len(ln["t"]), 2): sfx.append({"t": c["a"] + ln["at"] + k / 28, "k": "key"})
sfx += [{"t": ME, "k": "whoosh"}, {"t": ME + 0.2, "k": "chime"}, {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
data = {"main_end": ME, "total": TOT, "captions": caps, "stickers": stickers, "numbers": numbers, "cards": cards,
        "board": {"phone": "7989615350"}, "title": None}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
json.dump(sorted(sfx, key=lambda x: x["t"]), open(W + "/sfx.json", "w"), indent=1)
print("main", round(ME, 2), "total", round(TOT, 2), "captions", len(caps), "cards", len(cards))
