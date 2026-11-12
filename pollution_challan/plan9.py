"""Pollution challan short: captions (Telugu in English letters), stickers, 2 cards, sfx -> work/data.json, work/sfx.json, work/fun.json"""
import json
S = "/tmp/claude-0/-home-user-fortesting/f0703b19-2505-5b8b-b72d-114eb35464cd/scratchpad/ch"
W = S + "/work"
TL = json.load(open(W + "/timeline.json"))
QP = [q for q in TL["pieces"] if q["sid"] == "Q"][0]
P = [q for q in TL["pieces"] if q["sid"] != "Q"]; ME = TL["main_end"]; TOT = TL["total"]
R = "₹1,035/-"
TXT = {
    "S1": "Pollution bro! Mobile number update cheyinchukunnanu. Ippudu pollution cheyinchandi.",
    "S2": "Sare anna! Meeku OTP vasthundhi chudandi. Ippude pollution chesesthanu. | Okka nimisham anna... Shocking news! | Mee vehicle meedha challan undhi anna!",
    "S3": f"Challan pending lo unte pollution avvadhu. | Mundu challan kattandi. Mottham {R}",
    "S5": "Sir! Please sir! Fine veyakandi sir! | Juttu oodipothundhani helmet pettukoledhu sir! | Inka pelli kuda kaaledhu sir! | Please sir... ee okkasariki vadileyandi sir!",
    "S6": f"Odiyamma! | Fine vesesaadannamaata! | Ippudu kattala? | Aa khareedhaina photo ki {R}!",
    "S7": "Malli net center ki velli challan kattinchukuni randi anna!",
    "S8": "Krishna bro! Enti bro idhi? | Prabhutvam roju rojuki kotha kotha rules testhondhi! | Challan pending lo unte pollution kuda avvadhanta! | Twaraga challan katteyi bro!",
    "S9": "Helmet fine aa bro?",
    "S10a": f"Avunu bro! {R}",
    "S10b": "Inkosari nunchi helmet lekunda bayatiki vellanu bro! | Naa bodi juttu pothe poyindhi... | Fine kattalsina avasaram ledhu! | Ika nunchi naa thala kuda safe ga untundhi!",
    "S11": "Katteshanu bro!",
    "S12": "Challan website maarindhi bro! | Kotha website link description lo pedathanu. | Check chesukuni pay chesukondi.",
    "S13": "Ee samacharam meeku konchemaina upayogapadindhanipisthe video ni like cheyandi. | Maa channel content nachithe subscribe chesukondi bro! | Thank you!",
}
KEY = {"pollution": None, "otp": "One Time Password", "challan": None, "pending": None, R.lower(): None, "shocking": None,
       "fine": None, "helmet": None, "juttu": None, "pelli": None, "odiyamma": None, "photo": None, "net": None, "krishna": None,
       "rules": None, "website": None, "link": None, "description": None, "like": None, "subscribe": None, "safe": None,
       "mobile": None, "update": None, "avvadhu": None, "avvadhanta": None, "pettukoledhu": None, "kaaledhu": None,
       "veyakandi": None, "katteshanu": None, "thank": None, "avunu": None, "please": None, "bodi": None, "twaraga": None,
       "vadileyandi": None, "vesesaadannamaata": None, "kattala": None, "ledhu": None}
RED = {"avvadhu", "avvadhanta", "pettukoledhu", "kaaledhu", "veyakandi", "ledhu", "odiyamma", "shocking", "vesesaadannamaata"}
GREEN = {"katteshanu", "safe", "update", "subscribe", "like"}
PAIR = {("mobile", "number"), ("net", "center"), ("shocking", "news"), ("thank", "you"), ("bodi", "juttu"), ("challan", "pending"),
        ("pollution", "cheyinchandi"), ("fine", "veyakandi"), ("please", "sir")}
norm = lambda w: w.lower().strip(",.?!")

def chunks(words):
    out, i = [], 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 22: n = 2
        if n == 3 and any(" " in w for w in words[i:i+3]): n = 2
        if n >= 2 and len(words[i]) + len(words[i+1]) > 24: n = 1
        if len(words) - i - n == 1 and n < 3 and sum(len(w) for w in words[i:]) <= 22: n += 1
        out.append(words[i:i+n]); i += n
    return out

def span(sid):
    ps = [p for p in P if p["sid"] == sid]; return ps[0]["t0"], ps[-1]["t1"]

caps, sfx = [], []
for sid, text in TXT.items():
    a0, b0 = span(sid); parts = [x.strip() for x in text.split("|")]
    tot = sum(len(x) for x in parts); cur = a0
    for part in parts:
        ps = (b0 - a0) * len(part) / tot; ws = []
        for w in part.split():   # glue pair words so they never split across captions
            if ws and " " not in ws[-1] and (norm(ws[-1]), norm(w)) in PAIR: ws[-1] += " " + w
            else: ws.append(w)
        cs = [[x for w in c for x in w.split(" ")] for c in chunks(ws)]
        ct = sum(len(" ".join(c)) for c in cs); c0 = cur + 0.02
        for c in cs:
            d = (ps - 0.04) * len(" ".join(c)) / ct
            k = [norm(w) in KEY or w.lower() in KEY for w in c]
            lines = []
            if any(k):
                a = next((i for i, w in enumerate(c) if R in w), k.index(True)); b = a
                if b + 1 < len(c) and (norm(c[a]), norm(c[a+1])) in PAIR: b += 1
                hero = " ".join(c[a:b+1]).rstrip(",")
                pre, post = " ".join(c[:a]), " ".join(c[b+1:])
                if pre: lines.append({"cls": "cw", "t": pre})
                n0 = norm(c[a]); cls = "ch" + (" r" if n0 in RED else " g" if n0 in GREEN else "")
                lines.append({"cls": cls, "t": hero})
                sub = KEY.get(n0)
                if post: lines.append({"cls": "cs", "t": post})
                elif sub: lines.append({"cls": "cs", "t": sub})
                sfx.append({"t": c0, "k": "tick_soft"})
            else:
                lines.append({"cls": "cw", "t": " ".join(c)})
            caps.append({"a": round(c0, 3), "b": round(c0 + d, 3), "lines": lines}); c0 += d
        cur += ps

def at(sid, frac=0.0):
    a, b = span(sid); return a + (b - a) * frac
def src(sid, t):      # source-clip time -> output time (inside one segment)
    for p in P:
        if p["sid"] == sid and p["a"] <= t <= p["b"] + 1e-6:
            return p["t0"] + (t - p["a"]) / ((p["b"] - p["a"]) / (p["t1"] - p["t0"]))
    raise ValueError((sid, t))
# ---- cards (minimal b-roll)
cards = [
    dict(type="profile", theme="white", a=at("S3", 0.48), b=at("S3", 1.0) - 0.03, icon="doc", color="red",
         kicker="CHALLAN PENDING", title=R, pill="Mundu challan kattandi", pillAt=0.25,
         desc="Challan pending lo unte pollution certificate raadhu", tiles=["bike", "doc", "rupee"]),
    dict(type="profile", theme="white", a=at("S12") + 0.05, b=at("S12", 1.0) - 0.03, icon="eye", color="blue",
         kicker="CHALLAN WEBSITE CHANGED", title="New Website", pill="Link in description", pillAt=at("S12", 0.36) - at("S12"),
         desc="Check chesukuni pay chesukondi", tiles=["phone", "rupee", "check"]),
]
cards.append(dict(type="blacktext", theme="black", a=QP["t0"], b=QP["t1"], hideTitle=True,   # Navin's question (no take)
                  lines=[{"t": "NAVIN 🤔", "cls": "w", "at": 0.05},
                         {"t": "Ee website lo", "cls": "w", "at": 0.25},
                         {"t": "pay chesaru?", "cls": "h", "at": 0.45}]))
# ---- stickers: (time, side, emoji, icon, label, color, dur)
ST = [
    (at("S1") + 0.1, "r", "", "user", "Navin", "blue", 2.2),
    (at("S1", 0.35), "l", "📲", "", "Number updated", None, 2.2),
    (at("S2") + 0.1, "l", "", "user", "Checker", "green", 2.2),
    (at("S2", 0.18), "r", "", "otp", "OTP", "purple", 2.0),
    (at("S2", 0.56), "r", "😱", "", "Shocking news", None, 2.0),
    (at("S2", 0.8), "l", "🚨", "", "Challan!", None, 2.2),
    (at("S3") + 0.1, "r", "🚫", "", "No pollution", None, 2.2),
    (at("FB0") + 0.05, "r", "😨", "", "", None, 1.2),
    (at("FB1") + 0.1, "l", "🎞️", "", "Flashback", None, 3.4),
    (src("FB1", 3.5), "r", "📸", "", "Click!", None, 1.6),
    (at("S5") + 0.1, "r", "🙏", "", "Please sir", None, 2.0),
    (at("S5", 0.3), "l", "💇", "", "Juttu", None, 2.0),
    (at("S5", 0.58), "r", "💍", "", "Pelli kaaledhu", None, 2.2),
    (at("S6") + 0.05, "l", "😩", "", "Odiyamma!", None, 2.0),
    (at("S6", 0.78), "r", "💸", "", "₹1,035", None, 2.2),
    (at("S7") + 0.1, "l", "🏪", "", "Net Center", None, 2.2),
    (at("S8") + 0.2, "r", "", "user", "Navin", "blue", 1.6),
    (at("S8", 0.3), "l", "📜", "", "New rules", None, 2.2),
    (at("S9") + 0.05, "l", "", "user", "Krishna", "orange", 0.85),
    (at("S10b", 0.05), "r", "⛑️", "", "Helmet", None, 2.2),
    (at("S10b", 0.4), "l", "😂", "", "", None, 1.6),
    (src("S10b", 8.3), "r", "😎", "", "Safe!", None, 2.0),
    (at("S11") + 0.05, "r", "✅", "", "Paid", None, 1.6),
    (at("S13", 0.4), "l", "👍", "", "Like", None, 1.6),
    (at("S13", 0.68), "r", "🔔", "", "Subscribe", None, 1.8),
]
stickers = []
for t0, side, emo, icon, label, color, dur in ST:
    st = {"a": t0, "b": t0 + dur, "side": side, "label": label, "icon": icon or "check", "color": color or "blue"}
    if emo: st["emoji"] = emo
    stickers.append(st); sfx.append({"t": t0, "k": "pop"})
for c in cards:
    if c["type"] == "blacktext":
        sfx += [{"t": c["a"], "k": "impact"}] + [{"t": c["a"] + l["at"], "k": "tick"} for l in c["lines"]]; continue
    sfx += [{"t": c["a"] - 0.2, "k": "whoosh"}, {"t": c["a"], "k": "impact"}, {"t": c["b"] - 0.2, "k": "whoosh_out"},
            {"t": c["a"] + c["pillAt"], "k": "chime"}]
sfx += [{"t": ME, "k": "whoosh"}, {"t": ME + 0.2, "k": "tick"}, {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
# ---- funny parts: comedy music bed + real CC0 comedy sfx (sfx_library)
fun = {"music": [[at("FB0"), at("S6", 1.0)], [at("S10b"), at("S10b", 1.0)]],
       "events": [  # time, sound, max length, dB vs voice
           (at("S2", 0.56), "crowd-ooh-01", 1.6, -16),          # shocking news
           (at("FB0") + 0.05, "cartoon-eye-blink-01", 0.8, -11), # shock face zoom
           (at("FB1"), "cartoon-slide-whistle-01", 1.2, -15),   # into flashback
           (src("FB1", 3.5), "office-camera-08", 0.6, -9),      # constable takes the photo
           (at("S5", 0.62), "laugh-01", 1.6, -16),              # pelli kuda kaaledhu
           (at("S6") + 0.05, "crowd-groan-01", 1.4, -16),       # Odiyamma!
           (at("S6", 0.8), "ready-coin-04", 0.9, -12),          # 1035 photo
           (at("S10b", 0.42), "cartoon-boing-01", 0.9, -13),    # bodi juttu
           (src("S10b", 8.3), "tada-04", 1.4, -13),             # helmet pose
           (at("S11") + 0.05, "ready-coin-04", 0.9, -12),       # katteshanu
       ]}
data = {"main_end": ME, "total": TOT, "captions": caps, "stickers": stickers, "numbers": [], "cards": cards,
        "board": {"phone": "7989615350"}, "title": ["POLLUTION CHEYALANTE", "CHALLAN KATTALSINDHENA?"]}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
json.dump(sorted(sfx, key=lambda x: x["t"]), open(W + "/sfx.json", "w"), indent=1)
json.dump(fun, open(W + "/fun.json", "w"), indent=1)
print("main", round(ME, 2), "total", round(TOT, 2), "captions", len(caps), "stickers", len(stickers), "cards", len(cards))
for c in caps: print(round(c["a"], 2), " / ".join(l["t"] + ("*" if l["cls"].startswith("ch") else "") for l in c["lines"]))
