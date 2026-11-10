"""Plan overlays + SFX for the reference-style edit. usage: plan2.py bike|car -> work2_<kind>/data.json"""
import json, re, sys

S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
R = S + "/ins"
KIND = sys.argv[1]
W = f"{R}/work4_{KIND}"
T = json.load(open(f"{W}/timeline.json"))
TL, ME, TOT = T["timeline"], T["main_end"], T["total"]
SEGS = T["segs"]

def s(sid): return TL[sid][0]
def e(sid): return TL[sid][1]
def frac(sid, f): a, b = TL[sid]; return a + (b - a) * f

R_ = "₹"
KEY = ["ఇన్సూరెన్స్", "థర్డ్", "పార్టీ", "ఓన్", "డ్యామేజ్", "IDV", "CC", "ఇన్స్పెక్షన్", "ప్రీమియం", "కాంప్రహెన్సివ్",
       "మస్ట్‌గా", "బెటర్", "లక్షలు", "లక్షల", "ఫోటోలు", "వీడియోలు", "వీడియో", "టిప్స్", "రోడ్‌సైడ్", "అసిస్టెన్స్",
       "యాడ్-ఆన్స్", "కవరేజ్", "రీడింగ్", "సర్వీసెస్", "పర్సనల్", "యాక్సిడెంట్", "కవర్", "బైక్", "బైక్‌కైతే",
       "కార్స్‌కి", "కార్లు", "ఇంజిన్", "అవసరం", "టోటల్", "యాక్సెప్ట్", "5", "10"]
GREEN = ["అవసరం", "బెటర్", "యాక్సెప్ట్", "మస్ట్‌గా"]
SUBS = {"IDV": "ఇన్సూర్డ్ డిక్లేర్డ్ వాల్యూ", "CC": "ఇంజిన్ కెపాసిటీ"}

def is_key(w):
    c = w.rstrip(",")
    return bool(re.match(r"^[0-9][0-9,]*$", c)) or any(c.startswith(k) for k in KEY)

captions, sfx = [], []
for sid, a, b, text in SEGS:
    st, en = TL[sid]
    words = text.split()
    chunks, i = [], 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 24: n = 2
        if len(words) - i - n == 1: n = n + 1 if n < 3 else n - 1
        chunks.append(words[i:i+n]); i += n
    total = sum(len(" ".join(c)) for c in chunks)
    cur, span = st + 0.02, (en - st) - 0.04
    for c in chunks:
        dur = span * len(" ".join(c)) / total
        flags = [is_key(w) for w in c]
        lines = []
        if any(flags):
            k0 = flags.index(True); k1 = k0
            while k1 + 1 < len(c) and flags[k1 + 1] and k1 - k0 < 1: k1 += 1
            hero = " ".join(c[k0:k1+1]).rstrip(",")
            pre, post = " ".join(c[:k0]), " ".join(c[k1+1:])
            cls = "ch g" if any(hero.startswith(g) for g in GREEN) else "ch"
            if pre: lines.append({"cls": "cw", "t": pre})
            lines.append({"cls": cls, "t": hero})
            sub = SUBS.get(hero)
            if post: lines.append({"cls": "cs", "t": post})
            elif sub: lines.append({"cls": "cs", "t": sub})
        else:
            lines.append({"cls": "cw", "t": " ".join(c)})
        captions.append({"a": round(cur, 3), "b": round(cur + dur, 3), "lines": lines})
        cur += dur

# ---------------------------------------------------------------- per-video plan
if KIND == "bike":
    stickers = [
        ("B1", 0.35, "l", "shield", "PA కవర్", "purple"),
        ("B4", 0.2, "r", "bike", "ఓన్ డ్యామేజ్", "orange"),
        ("B6", 0.1, "l", "cal", "ఇయర్స్", "teal"),
        ("B7", 0.1, "r", "rupee", "IDV", "green"),
        ("B10", 0.0, "l", "doc", "థర్డ్ పార్టీ", "blue"),
        ("B14", 0.1, "r", "gauge", "CC", "pink"),
        ("T1", 0.1, "r", "shield", "ఇన్సూరెన్స్", "blue"),
        ("T4", 0.2, "r", "rupee", "₹350", "green"),
        ("T5", 0.1, "l", "plus", "₹15 లక్షలు", "red"),
        ("T14", 0.1, "r", "star", "2 ఇయర్స్", "yellow"),
    ]
    numbers = [("T2", "1"), ("T3", "2"), ("T8", "3")]
    cards = [
        dict(type="profile", theme="white", a=s("B2") - 0.1, b=e("B3"), icon="shield", color="purple",
             kicker="PERSONAL ACCIDENT COVER", title=f"{R_}350 పే చేస్తే", pill=f"{R_}15 లక్షల కవర్",
             pillAt=s("B3") - s("B2") + 0.15, desc="యాక్సిడెంట్‌లో మనకి ఏమైనా అయితే", tiles=["shield", "plus", "user"]),
        dict(type="chart", theme="dark", a=s("B8"), b=e("B9"), kicker="IDV VALUE", title="బండి వాల్యూ",
             min=20000, max=60000, pillAt=s("B9") - s("B8") + 0.3, pill="పాతదైతే IDV తగ్గుతుంది",
             points=[{"v": 50000, "l": "50,000", "x": "కొత్త బండి"}, {"v": 40000, "l": "40,000", "x": "3 ఇయర్స్"},
                     {"v": 30000, "l": "30,000", "x": "పాత బండి"}]),
        dict(type="timeline", theme="dark", a=s("B10"), b=e("B13"), kicker="BIKE INSURANCE COST", gap=250,
             steps=[{"v": f"{R_}840", "t": "థర్డ్ పార్టీ", "s": "బేసిక్ – మస్ట్", "icon": "doc", "at": frac("B10", .75) - s("B10")},
                    {"v": f"+ {R_}350", "t": "పర్సనల్ యాక్సిడెంట్", "s": "మొత్తం 1200", "icon": "shield", "at": s("B11") - s("B10") + 0.3},
                    {"v": f"+ {R_}400", "t": "ఓన్ డ్యామేజ్", "s": "బండికి కూడా కవర్", "icon": "bike", "at": s("B12") - s("B10") + 0.2},
                    {"v": f"{R_}1500–1600", "t": "టోటల్ – ఫుల్ కవర్", "s": "బైక్‌కి", "icon": "star", "at": s("B13") - s("B10") + 0.3}]),
        dict(type="timeline", theme="dark", a=s("B15") - 0.15, b=e("B17"), kicker="THIRD PARTY · BY CC", gap=330,
             steps=[{"v": f"{R_}800", "t": "150 CC లోపు", "s": "", "icon": "gauge", "at": 0.25},
                    {"v": f"{R_}1600", "t": "150 CC పైన", "s": "", "icon": "gauge", "at": s("B17") - s("B15") + 0.15}]),
        dict(type="photo", theme="dark", a=s("B18"), b=e("B18") + 0.1, img="../assets/scooter.png",
             label="ఇన్స్పెక్షన్ లేదు ✓"),
        dict(type="journey", theme="white", a=s("T10"), b=e("T12"), kicker="INSURANCE JOURNEY",
             nodes=[{"t": "0–5 ఇయర్స్", "s": "ఫుల్ కవర్ – మస్ట్", "icon": "shield", "color": "blue", "at": 0.25, "tag": "బెస్ట్"},
                    {"t": "5–10 ఇయర్స్", "s": "OD ఆప్షనల్", "icon": "cal", "color": "purple", "at": 0.7},
                    {"t": "10+ ఇయర్స్", "s": "OD అవసరం లేదు", "icon": "x", "color": "orange", "at": 1.15}]),
    ]
else:
    stickers = [
        ("C1", 0.1, "l", "car", "కార్", "blue"),
        ("C5", 0.1, "r", "doc", "సేమ్ రేట్", "green"),
        ("C6", 0.0, "l", "shield", "ఓన్ డ్యామేజ్", "purple"),
        ("C16", 0.0, "r", "check", "ఓకే", "green"),
        ("T1", 0.1, "r", "shield", "ఇన్సూరెన్స్", "blue"),
        ("T4", 0.2, "r", "rupee", "₹350", "green"),
        ("T5", 0.1, "l", "plus", "₹15 లక్షలు", "red"),
        ("T14", 0.1, "r", "star", "2 ఇయర్స్", "yellow"),
    ]
    numbers = [("T2", "1"), ("T3", "2"), ("T8", "3")]
    cards = [
        dict(type="timeline", theme="dark", a=s("C2"), b=e("C4"), kicker="CAR THIRD PARTY · BY CC", gap=300,
             steps=[{"v": f"{R_}2400", "t": "1000 CC లోపు", "s": "", "icon": "car", "at": 0.3},
                    {"v": f"{R_}4000", "t": "1000 CC పైన", "s": "", "icon": "car", "at": s("C3") - s("C2") + 0.3},
                    {"v": f"{R_}9000", "t": "1500 CC పైన", "s": "", "icon": "car", "at": s("C4") - s("C2") + 0.5}]),
        dict(type="profile", theme="white", a=s("C7"), b=e("C9"), icon="gear", color="orange",
             kicker="OWN DAMAGE · ADD-ONS", title="ఇంజిన్ + రోడ్‌సైడ్", pill="ప్రీమియం పెరుగుతుంది ↑",
             pillAt=s("C9") - s("C7"), desc="ఇంజిన్ కవరేజ్, రోడ్‌సైడ్ అసిస్టెన్స్ – సెపరేట్‌గా యాడ్ చేసుకోవచ్చు",
             tiles=["gear", "wrench", "road"]),
        dict(type="carcam", theme="dark", a=frac("C10", 0.45), b=e("C11"), kicker="CAR INSPECTION",
             title="కార్స్‌కి ఇన్స్పెక్షన్", pill="బైక్‌కి అవసరం లేదు", pillAt=1.5),
        dict(type="terminal", theme="dark", a=s("C12"), b=e("C15") + 0.2,
             head="INSPECTION · CAR · CHECKLIST",
             lines=[{"t": "4 సైడ్స్ ఫోటోలు", "at": 0.5},
                    {"t": "ఇంజిన్ ఫోటోలు + వీడియో", "at": s("C13") - s("C12") + 0.4},
                    {"t": "గ్లాస్ ఫోటోలు", "at": s("C14") - s("C12") + 0.2},
                    {"t": "ఇంజిన్ స్టార్ట్ వీడియో", "at": s("C15") - s("C12") + 0.3},
                    {"t": "మీటర్ రీడింగ్ ఫోటో", "at": frac("C15", .55) - s("C12")}]),
        dict(type="journey", theme="white", a=s("T10"), b=e("T12"), kicker="INSURANCE JOURNEY",
             nodes=[{"t": "0–5 ఇయర్స్", "s": "ఫుల్ కవర్ – మస్ట్", "icon": "shield", "color": "blue", "at": 0.25, "tag": "బెస్ట్"},
                    {"t": "5–10 ఇయర్స్", "s": "OD ఆప్షనల్", "icon": "cal", "color": "purple", "at": 0.7},
                    {"t": "10+ ఇయర్స్", "s": "OD అవసరం లేదు", "icon": "x", "color": "orange", "at": 1.15}]),
    ]

stk = []
for sid, f, side, icon, label, color in stickers:
    a = frac(sid, f)
    stk.append({"a": a, "b": a + 2.6, "side": side, "icon": icon, "label": label, "color": color})
    sfx.append({"t": a, "k": "pop"})
nums = []
for sid, n in numbers:
    a = s(sid) + 0.05
    nums.append({"a": a, "b": e(sid), "n": n})
    sfx += [{"t": a - 0.12, "k": "swish"}, {"t": a + 0.12, "k": "ding"}]
for c in cards:
    c["a"], c["b"] = round(c["a"], 3), round(c["b"], 3)
    sfx += [{"t": c["a"] - 0.25, "k": "whoosh"}, {"t": c["a"], "k": "impact"}, {"t": c["b"] - 0.2, "k": "whoosh_out"}]
    if c["type"] in ("profile", "chart", "carcam"):
        sfx.append({"t": c["a"] + c.get("pillAt", 0.45), "k": "chime"})
    if c["type"] == "timeline":
        for st in c["steps"]:
            sfx.append({"t": c["a"] + st["at"], "k": "coin" if "₹" in st["v"] else "tick"})
    if c["type"] == "journey":
        for nd in c["nodes"]:
            sfx.append({"t": c["a"] + nd["at"], "k": "tick"})
    if c["type"] == "terminal":
        for ln in c["lines"]:
            n = len(ln["t"])
            for k in range(0, n, 2):
                sfx.append({"t": c["a"] + ln["at"] + k / 28, "k": "key"})
            sfx.append({"t": c["a"] + ln["at"] + n / 28 + 0.05, "k": "tick"})
    if c["type"] == "chart":
        sfx.append({"t": c["a"] + 0.3, "k": "rise"})
    if c["type"] == "photo":
        sfx.append({"t": c["a"] + 0.5, "k": "shutter"})
for c in captions:
    if any(l["cls"].startswith("ch") for l in c["lines"]):
        sfx.append({"t": c["a"], "k": "tick_soft"})
sfx += [{"t": ME, "k": "whoosh"}, {"t": ME + 0.2, "k": "chime"}, {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"},
        {"t": ME + 2.4, "k": "ding"}]

data = {"main_end": ME, "total": TOT, "captions": captions, "stickers": stk, "numbers": nums, "cards": cards,
        "board": {"phone": "7989615350"},
        "title": ["BIKE COMPREHENSIVE", "INSURANCE"] if KIND == "bike" else ["CAR COMPREHENSIVE", "INSURANCE"]}
json.dump(data, open(f"{W}/data.json", "w"), ensure_ascii=False, indent=1)
json.dump(sorted(sfx, key=lambda x: x["t"]), open(f"{W}/sfx.json", "w"), indent=1)
print(KIND, "captions", len(captions), "cards", len(cards), "sfx", len(sfx))
