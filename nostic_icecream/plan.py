"""Captions, name tags, stickers and SFX cues -> work/data.json"""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from segs import W, END_SCREEN, timeline, to_out

starts, MAIN = timeline()
caps, stk, sfx = [], [], []


def C(seg, a, b, *ls, seg_b=None, tag=False):
    """caption on source times a..b of segment seg (b may lie in seg_b)"""
    A, B = to_out(seg, a), to_out(seg if seg_b is None else seg_b, b)
    caps.append({"a": round(A, 3), "b": round(B, 3), "tag": tag, "lines": [{"cls": c, "t": t} for c, t in ls]})
    sfx.append({"t": A, "k": "tap"})


def ST(seg, t, side, emoji, label="", d=1.9):
    A = to_out(seg, t)
    stk.append({"a": round(A, 3), "b": round(A + d, 3), "side": side, "emoji": emoji, "label": label, "color": "blue"})
    sfx.append({"t": A, "k": "pop"})


# ---------- AI voice part (script order)
C(0, 1.62, 2.68, ("cw", "మీకు"), ("ch", "ఐస్ క్రీమ్ 🍦"))
C(0, 2.68, 3.52, ("cw", "అంటే"), ("ch", "ఇష్టమేనా? 😋"))
C(1, 0.08, 1.40, ("cw", "ఐతే"), ("ch", "ఇది చూడండి 👀"), seg_b=2)
C(2, 1.40, 2.08, ("ch", "నోస్టిక్"), ("cs", "NOSTIC"))
C(2, 2.08, 3.42, ("cw", "ఫ్రూట్ నేచురల్"), ("ch g", "ఐస్ క్రీమ్స్ 🍦"))
C(3, 6.15, 7.02, ("cw", "ఈ ఐస్ క్రీమ్స్ ని"))
C(3, 7.02, 8.32, ("ch", "ఫ్రూట్స్ పల్ప్ తో 🍓"), ("cw", "చేస్తారు"))
C(4, 3.62, 4.42, ("ch", "ప్రిజర్వేటివ్స్"), ("cw", "ఏమీ"))
C(4, 4.42, 5.15, ("ch", "యాడ్ చేయకుండా 🚫"))
C(4, 5.15, 6.12, ("ch g", "నేచురల్ గా 🌿"), ("cw", "చేస్తారు"))
C(5, 8.66, 9.62, ("ch g", "షుగర్ ఫ్రీ"), ("cw", "ఐస్ క్రీమ్స్"))
C(5, 9.62, 10.35, ("ch", "కూడా ఉంటాయి ✅"))
C(6, 6.36, 7.30, ("cw", "ఇవి"), ("ch", "₹20 నుండి 💰"))
C(6, 7.30, 7.95, ("ch", "స్టార్ట్ అవుతాయి"))
C(7, 0.05, 1.40, ("cw", "చాలా రకాల"), ("ch", "వెరైటీస్ ఉన్నాయి 🍨"))
C(7, 1.40, 2.68, ("cw", "ఇది ఎక్కడ"), ("ch", "ఉంది అంటే? 🤔"))
C(7, 2.68, 3.36, ("cw", "మన"), ("ch", "మాధవధార"))
C(7, 3.36, 4.22, ("ch", "జంక్షన్ 🚦"), ("cw", "ఉంది కదా"))
C(7, 4.22, 4.95, ("cw", "ఇంకొంచెం"), ("ch", "ముందుకి ➡️"))
C(7, 4.95, 6.20, ("cw", "న్యూ రామ్ సాయి"), ("ch", "రెస్టారెంట్ 🍛"))
C(7, 6.20, 7.10, ("cw", "వైపు వెళ్ళే"), ("ch", "దారిలో"))
C(7, 7.10, 8.15, ("cw", "ఉంటుంది"), ("ch", "కార్నర్ లో 📍"))
C(7, 8.30, 9.02, ("ch", "అటువైపు వెళ్తే"))
C(7, 9.02, 10.05, ("cw", "ఒకసారి"), ("ch g", "ట్రై చేయండి 👍"))

ST(0, 2.70, "r", "😋")
ST(2, 1.45, "l", "🍦", "NOSTIC")
ST(3, 7.05, "r", "🍓", "ఫ్రూట్ పల్ప్")
ST(4, 3.70, "l", "🚫", "నో ప్రిజర్వేటివ్స్", 1.6)
ST(4, 5.20, "r", "🌿", "నేచురల్")
ST(5, 8.75, "l", "🍬", "షుగర్ ఫ్రీ", 1.6)
ST(6, 6.50, "r", "💰", "₹20 నుండి", 1.45)
ST(7, 0.15, "l", "🍨", "వెరైటీస్")
ST(7, 2.75, "r", "📍", "మాధవధార", 1.6)
ST(7, 4.98, "l", "🍛", "రామ్ సాయి", 1.6)
ST(7, 7.30, "r", "↪️", "కార్నర్", 1.4)
ST(7, 9.10, "l", "👍", "", 1.4)

# ---------- YouTube ice cream shots (2x): burned-in text is blurred, our name tag sits on top of it
YT = [  # (segment, src start, src end, Telugu name, English name)
    (8, 0.00, 1.53, "నోస్టిక్ ఫ్రూట్ పాప్స్", "Nostic Fruit Pops"),
    (8, 1.53, 3.60, "జామ • పైనాపిల్ • పుచ్చకాయ", "Guava · Pineapple · Watermelon"),
    (8, 3.60, 5.40, "మామిడి • అవకాడో", "Mango · Avocado"),
    (8, 5.40, 6.85, "బ్లాక్ ఫారెస్ట్ • ఓరియో", "Black Forest · Oreo"),
    (9, 8.65, 10.92, "ఫ్రూట్ పాప్స్", "Fruit Pops"),
    (9, 10.92, 12.43, "క్రీమీ పాప్స్", "Creamy Pops"),
    (9, 12.43, 13.90, "జామ • సపోటా • పుచ్చకాయ", "Guava · Sapota · Watermelon"),
    (9, 13.90, 15.67, "మామిడి • మిక్స్‌డ్ ఫ్రూట్", "Mango · Mixed Fruit"),
    (9, 15.67, 17.15, "బ్లాక్ ఫారెస్ట్ • ఓరియో", "Black Forest · Oreo"),
    (9, 17.15, 18.18, "నోస్టిక్ ఫ్రూట్ పాప్స్", "Nostic Fruit Pops"),
    (9, 18.18, 19.30, "స్ట్రాబెర్రీ • అవకాడో", "Strawberry · Avocado"),
    (9, 19.30, 20.30, "బ్లూబెర్రీ • మిక్స్‌డ్ ఫ్రూట్", "Blueberry · Mixed Fruit"),
    (9, 20.30, 21.18, "బ్లాక్ ఫారెస్ట్ • రెడ్ వెల్వెట్", "Black Forest · Red Velvet"),
    (9, 21.18, 22.23, "ఓరియో • రెడ్ వెల్వెట్", "Oreo · Red Velvet"),
    (9, 22.23, 23.32, "మలాయ్ కుల్ఫీ • స్పానిష్ డిలైట్", "Malai Kulfi · Spanish Delight"),
    (9, 23.32, 24.33, "లోటస్ బిస్కాఫ్ • మోజిటో", "Lotus Biscoff · Mojito"),
    (9, 24.33, 25.83, "ఐస్ క్రీమ్ కప్స్ 🍨", "Ice Cream Cups"),
    (9, 25.83, 27.00, "సీతాఫలం", "Sitaphal"),
]
for seg, a, b, te, en in YT:
    C(seg, a, b, ("ch", te), ("cs", en), tag=True)

# ---------- real shop clips (muted)
C(10, 1.0, 5.0, ("cw", "మన"), ("ch", "నోస్టిక్ షాప్ 🏪"))
C(11, 0.5, 3.5, ("cw", "ఫ్రెష్"), ("ch g", "ఫ్రూట్ పాప్స్ 🍓"))
C(12, 16.5, 19.5, ("cw", "చాలా రకాల"), ("ch", "వెరైటీస్ 🍨"))
C(13, 7.0, 10.5, ("cw", "ధరలు"), ("ch", "₹20 నుండి 💰"))
C(14, 19.5, 22.3, ("cw", "మాధవధార జంక్షన్"), ("ch", "రామ్ సాయి"), ("cs", "రెస్టారెంట్ దారిలో"))
C(14, 22.3, 25.0, ("cw", "ఒకసారి"), ("ch g", "ట్రై చేయండి 👍"))
ST(10, 1.3, "r", "🏪", "షాప్")
ST(12, 16.8, "l", "😍")
ST(13, 7.3, "r", "💰", "₹20+")
ST(14, 19.8, "l", "📍", "మాధవధార", 2.4)

for s in starts[1:]:
    sfx.append({"t": s, "k": "cut"})
sfx.append({"t": MAIN, "k": "end"})

data = {"main_end": MAIN, "total": MAIN + END_SCREEN, "captions": caps, "stickers": stk, "numbers": [], "cards": [],
        "board": {"phone": "7989615350"}, "title": None, "sfx": sfx}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
print("main", round(MAIN, 2), "captions", len(caps), "stickers", len(stk))
