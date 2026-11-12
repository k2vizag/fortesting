"""Pollution OTP short: captions (Telugu words in English letters), stickers, 2 cards, sfx -> work/data.json, work/sfx.json"""
import json, re
S = "/tmp/claude-0/-home-user-fortesting/f0703b19-2505-5b8b-b72d-114eb35464cd/scratchpad/pol"
W = S + "/work"
TL = json.load(open(W + "/timeline.json"))
P = TL["pieces"]; ME = TL["main_end"]; TOT = TL["total"]
# text spoken in each cut piece (same order as timeline pieces)
TXT = [
    "Pollution check cheyali",
    "Pollution cheyinchukovalante meeku oka OTP vasthundi",
    "Aa OTP ni pollution website lo enter chesina tharvathe pollution certificate vasthundi",
    "Oho!", "Avuna?",
    "Naa old mobile number naa daggara ledhu",
    "Ippudu new mobile number ekkada update cheyinchukovali?",
    "Mee daggara paatha mobile number lekapothe,", "net center lo", "ledha RTO agent daggara",
    "mee mobile number update cheyinchukondi",
    "Sare, naaku thelisina net center bro unnaru",
    "Akkadiki velli mobile number update cheyinchukuni malli vasthanu",
    "Krishna", "Bro, adhenti!", "Bandiki pollution aipoyindhi ani cheyinchukovadaniki velthe",
    "Pollution vaadu OTP adugutunnadu",
    "Avunu bro, ippudu pollution cheyali ante OTP velthundi",
    "Aa OTP ye number ki vasthundi bro?",
    "Bandi registration time lo edhaithe phone number ichamo adhe number ki velthundi",
    "Okavela ippudu aa mobile number mana daggara lekapothe em cheyali bro?",
    "Aa number lekapothe Vahan portal lo update cheyinchukovali. | Mobile number update cheyinchukune mundu KYC cheyinchukovali",
    "KYC ki online lo apply chesi, RTO office ki vellali approval ki,",
    "After that, mobile number update cheyali",
    "Ante ippudu paatha mobile number mana daggara lekapothe, kotha number update chesukune varaku pollution cheyinchukolemannamaata!",
    "Avunu.",
    "Inkoka update kuda undhi, next video lo chepthanu",
    "Ee information meeku konchem aina use ayyindhi anukunte", "like cheyandi", "maa channel content nachithe",
    "subscribe chesukondi", "Thank you",
]
assert len(TXT) == len(P), (len(TXT), len(P))
KEY = {"pollution": None, "otp": "One Time Password", "certificate": None, "website": None, "old": None, "new": None,
       "mobile": None, "net": None, "rto": "Regional Transport Office", "agent": None, "krishna": None, "vahan": "Govt vehicle portal",
       "kyc": "Know Your Customer", "approval": None, "registration": None, "update": None, "subscribe": None, "like": None,
       "lekapothe": None, "ledhu": None, "kotha": None, "paatha": None, "online": None, "oho!": None, "avuna?": None, "avunu.": None,
       "thank": None, "cheyinchukolemannamaata!": None}
PAIR = {("mobile", "number"), ("net", "center"), ("rto", "agent"), ("rto", "office"), ("vahan", "portal"), ("thank", "you"),
        ("pollution", "certificate"), ("phone", "number"), ("next", "video")}
RED = {"lekapothe", "ledhu", "cheyinchukolemannamaata!", "lekapothe,"}
norm = lambda w: w.lower().strip(",.?!")

def chunks(words):
    out, i = [], 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 22: n = 2
        if n == 3 and any("\u00a0" in w for w in words[i:i+3]): n = 2
        if n >= 2 and len(words[i]) + len(words[i+1]) > 26: n = 1
        if len(words) - i - n == 1 and n < 3 and sum(len(w) for w in words[i:]) <= 22: n += 1
        out.append(words[i:i+n]); i += n
    return out

caps, sfx = [], []
for p, text in zip(P, TXT):
    parts = [x.strip() for x in text.split("|")]
    span = p["t1"] - p["t0"]; tot = sum(len(x) for x in parts); cur = p["t0"]
    for part in parts:
        ps = span * len(part) / tot; ws0 = part.split(); ws = []
        for w in ws0:   # glue pair words so they never split across captions
            if ws and (norm(ws[-1].split("\u00a0")[-1]), norm(w)) in PAIR and "\u00a0" not in ws[-1]: ws[-1] += "\u00a0" + w
            else: ws.append(w)
        cs = [[x for w in c for x in w.split("\u00a0")] for c in chunks(ws)]
        ct = sum(len(" ".join(c)) for c in cs); c0 = cur + 0.02
        for c in cs:
            d = (ps - 0.04) * len(" ".join(c)) / ct
            k = [norm(w) in KEY or w.lower() in KEY for w in c]
            lines = []
            if any(k):
                a = k.index(True); b = a
                if b + 1 < len(c) and (norm(c[a]), norm(c[a+1])) in PAIR: b += 1
                hero = " ".join(c[a:b+1]).rstrip(",")
                pre, post = " ".join(c[:a]), " ".join(c[b+1:])
                if pre: lines.append({"cls": "cw", "t": pre})
                cls = "ch" + (" r" if norm(c[a]) in {norm(x) for x in RED} else "")
                lines.append({"cls": cls, "t": hero})
                sub = KEY.get(norm(c[a]))
                if post: lines.append({"cls": "cs" if sub is None else "cw", "t": post})
                if sub and not any(l["t"] == sub for l in lines) and not post: lines.append({"cls": "cs", "t": sub})
                sfx.append({"t": c0, "k": "tick_soft"})
            else:
                lines.append({"cls": "cw", "t": " ".join(c)})
            caps.append({"a": round(c0, 3), "b": round(c0 + d, 3), "lines": lines}); c0 += d
        cur += ps

def at(sid, frac=0.0):
    ps = [p for p in P if p["sid"] == sid]; a, b = ps[0]["t0"], ps[-1]["t1"]; return a + (b - a) * frac
# ---- cards (minimal b-roll)
cards = [
    dict(type="profile", theme="white", a=at("L9") + 0.1, b=at("L10") - 0.05, icon="phone", color="blue",
         kicker="OTP · WHICH NUMBER?", title="Registration No.", pill="OTP goes here",
         pillAt=1.3, desc="Bandi registration time lo ichina mobile number ki OTP velthundi", tiles=["bike", "phone", "otp"]),
    dict(type="timeline", theme="dark", a=at("L11a") + 0.05, b=at("L11b", 1.0) + 0.05, kicker="NEW MOBILE NUMBER · STEPS", gap=270,
         steps=[{"v": "Vahan Portal", "t": "Mobile number update", "s": "Govt vehicle portal", "icon": "gear", "at": 0.15},
                {"v": "KYC", "t": "Mundu KYC cheyinchukovali", "s": "Know Your Customer", "icon": "idc", "at": at("L11a", 0.52) - at("L11a")},
                {"v": "RTO Approval", "t": "Online apply → RTO office", "s": "", "icon": "check", "at": at("L11b") - at("L11a")},
                {"v": "Update", "t": "Kotha mobile number", "s": "", "icon": "phone", "at": P[[q["sid"] for q in P].index("L11b") + 1]["t0"] - at("L11a")}]),
]
# ---- stickers: (time, side, emoji, icon, label, color, dur)
ST = [
    (at("L1") + 0.1, "r", "", "user", "Navin", "blue", 2.4),
    (at("L2") + 0.1, "l", "", "user", "Checker", "green", 2.4),
    (at("L2") + 1.5, "r", "", "otp", "OTP", "purple", 2.6),
    (at("L2") + 3.4, "r", "", "doc", "Certificate", "orange", 2.2),
    (at("L3", 0.38), "l", "📵", "", "Old number", None, 2.4),
    (at("L4", 0.38), "l", "", "gear", "Net Center", "teal", 2.6),
    (at("L4", 0.5), "r", "", "idc", "RTO Agent", "red", 2.4),
    (at("L6") + 0.2, "r", "", "user", "Navin", "blue", 1.8),
    (at("L6", 0.85), "l", "🤔", "", "OTP?", None, 2.0),
    (at("L7") + 0.05, "l", "", "user", "Krishna", "orange", 2.6),
    (at("L8") + 0.1, "r", "📲", "", "", None, 1.4),
    (at("L10") + 0.2, "l", "😟", "", "", None, 2.0),
    (at("L12", 0.15), "r", "📵", "", "No old number", None, 2.0),
    (at("L12", 0.7), "l", "🚫", "", "No Pollution", None, 2.2),
    (at("L13b") + 0.1, "r", "🎬", "", "Next video", None, 1.6),
    (at("L13c", 0.38), "l", "👍", "", "Like", None, 1.6),
    (at("L13c", 0.62), "r", "🔔", "", "Subscribe", None, 1.8),
]
stickers = []
for t0, side, emo, icon, label, color, dur in ST:
    st = {"a": t0, "b": t0 + dur, "side": side, "label": label, "icon": icon or "check", "color": color or "blue"}
    if emo: st["emoji"] = emo
    stickers.append(st); sfx.append({"t": t0, "k": "pop"})
# ---- card sfx (soft bloop + thump in, soft tap out, soft taps/plucks per step)
for c in cards:
    sfx += [{"t": c["a"] - 0.2, "k": "whoosh"}, {"t": c["a"], "k": "impact"}, {"t": c["b"] - 0.2, "k": "whoosh_out"}]
    if c["type"] == "profile": sfx.append({"t": c["a"] + c["pillAt"], "k": "chime"})
    if c["type"] == "timeline":
        for s_ in c["steps"]: sfx.append({"t": c["a"] + s_["at"], "k": "tick"})
sfx += [{"t": ME, "k": "whoosh"}, {"t": ME + 0.2, "k": "chime"}, {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
data = {"main_end": ME, "total": TOT, "captions": caps, "stickers": stickers, "numbers": [], "cards": cards,
        "board": {"phone": "7989615350"}, "title": ["POLLUTION CERTIFICATE", "OLD NUMBER LEKAPOTHE?"]}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
json.dump(sorted(sfx, key=lambda x: x["t"]), open(W + "/sfx.json", "w"), indent=1)
print("main", round(ME, 2), "total", round(TOT, 2), "captions", len(caps), "stickers", len(stickers), "cards", len(cards))
for c in caps: print(round(c["a"], 2), " / ".join(l["t"] + ("*" if l["cls"].startswith("ch") else "") for l in c["lines"]))
