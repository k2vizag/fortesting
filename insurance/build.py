"""Build a styled vertical short from cut segments of the raw insurance footage.
usage: python3 build.py bike|car
"""
import json, math, os, re, subprocess, sys
import uharfbuzz as hb

S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
R = S + "/ins"
FONTS = S + "/fonts"
KIND = sys.argv[1]
OUT = f"/home/user/fortesting/insurance_{KIND}.mp4"

# ---------------------------------------------------------------- content
TIPS = [
    ("T1", 177.10, 180.30, "మీరు ఇన్సూరెన్స్ చేసుకునే టైమ్‌లో"),
    ("T2", 181.35, 183.65, "ఫస్ట్ 5 ఇయర్స్ మొత్తం చేయించుకోండి"),
    ("T3", 185.10, 187.45, "పర్సనల్ యాక్సిడెంట్ కవర్ అనేది ఉంచుకోండి"),
    ("T4", 188.20, 191.30, "ఎందుకంటే మనం పే చేసేది 350 రూపాయలు"),
    ("T5", 191.45, 196.18, "మనకు కవర్ అయ్యేది 15 లక్షలు సో మనకి ఏమైనా అయినా కూడా"),
    ("T6", 196.18, 201.17, "సో ఇంటికి కొంచెం ఉంటది యాక్సిడెంట్‌లో మనకి ఏమైనా అయినప్పుడు"),
    ("T7", 201.60, 204.45, "ఉంచుకోవడం బెటర్"),
    ("T8", 212.95, 217.70, "ఇంకొకటి బండి ఓన్ డ్యామేజ్ అయితే ఫస్ట్ 5 ఇయర్స్ వరకు చేయించుకోండి"),
    ("T9", 218.15, 224.95, "5 ఇయర్స్ తర్వాత మీకు ఓకే అనుకుంటే మరీ ఎక్కువ ప్రీమియం ఏమీ ఉండదు 400 ఏదో ఉంటది సంవత్సరానికి"),
    ("T10", 225.90, 228.60, "ఇంక 10 ఇయర్స్ తర్వాత అంటారా ఇంక అవసరం లేదు"),
    ("T11", 230.75, 235.95, "నార్మల్‌గా ఆ IDV వాల్యూ కూడా తక్కువ ఇస్తారు మీకు సో 10 ఇయర్స్ తర్వాత అవసరం లేదు"),
    ("T12", 236.25, 240.30, "10 ఇయర్స్ లోపు అయితే మీరు కూడా చేయించుకోండి 5 ఇయర్స్ అయితే మస్ట్‌గా చేయించుకోండి"),
    ("T13", 241.70, 243.05, "అదే మీకిచ్చే టిప్స్ అన్నమాట"),
    ("T14", 243.05, 247.90, "సో మేము లాస్ట్ టూ ఇయర్స్ నుండి ఇన్సూరెన్స్ సర్వీసెస్ చేస్తున్నాము"),
]

BIKE = [
    ("B1", 2.12, 6.80, "కాంప్రహెన్సివ్ అంటే ఇందులో మన పర్సనల్ యాక్సిడెంట్ కవర్ పెట్టుకోవచ్చు అంటే మనకు వర్తిస్తది"),
    ("B2", 7.15, 8.80, "అది 350 ఏదో ఉంటది"),
    ("B3", 9.00, 10.90, "దానికి 15 లక్షల వరకు కవర్ అవుతుంది"),
    ("B4", 18.20, 21.10, "ఇంకొకటి ఓన్ డ్యామేజ్ అంట వెహికల్ కూడా అవ్వాలి అంటే"),
    ("B5", 22.60, 27.55, "దానికి కూడా కవర్ చేసుకునేలాగా ఉంటది దానికి కూడా 400 500 ఉంటది మీకు"),
    ("B6", 28.00, 33.70, "బండిని బట్టి అంటే బండి ఎన్ని ఇయర్స్ నడిపామన్న దాన్ని బట్టి"),
    ("B7", 34.45, 37.70, "మనకి IDV వాల్యూ ఉంటది అన్నమాట"),
    ("B8", 38.05, 41.15, "మనం యూజ్ చేసుకునే కొద్దీ ఆ IDV వాల్యూ తగ్గిపోతా ఉంటది"),
    ("B9", 41.75, 48.75, "సో 30,000 40,000 50,000 ఇలాగా ఉంటాయి IDV లు సో కొత్త వాటికైతే కొంచెం ఎక్కువ ఉంటాయి"),
    ("B10", 50.20, 57.60, "మీరు ఇన్సూరెన్స్ చేసుకునేటప్పుడు చూడండి మీ థర్డ్ పార్టీ ఇస్తే 840 రూపాయలు అవుతుంది"),
    ("B11", 58.95, 63.75, "దానికి పర్సనల్ యాక్సిడెంట్ యాడ్ చేస్తే 350 యాడ్ చేస్తే మీకు 1200 అవుతుంది"),
    ("B12", 64.05, 68.60, "ఇంకో 400 యాడ్ చేస్తే బండికి కూడా కవర్ అవుతుంది సో మొత్తం కవర్ అవుతుంది"),
    ("B13", 69.30, 74.00, "టోటల్ 1500 టు 1600 ఉంటది బైక్‌కైతే"),
    ("B14", 74.00, 79.55, "అది కూడా CC ని బట్టి డిపెండ్ అయి ఉంటది 150 CC లోపల ఉన్నాయి అనుకోండి"),
    ("B15", 80.30, 82.05, "వాటికి 800 ఏదో ఉంటది థర్డ్ పార్టీ"),
    ("B16", 82.50, 84.40, "150 CC దాటి ఉంటే"),
    ("B17", 85.10, 87.25, "1600 ఉంటది థర్డ్ పార్టీ"),
    ("B18", 131.40, 134.38, "బైక్ అయితే ఇన్స్పెక్షన్ ఏమీ ఉండదు"),
] + TIPS

CAR = [
    ("C1", 94.65, 96.95, "కార్లు కూడా అంతే థర్డ్ పార్టీ"),
    ("C2", 99.00, 103.20, "1000 CC బిలో అనుకోండి 2400 ఏదో అవుతుంది"),
    ("C3", 109.50, 111.45, "1000 దాటితే 4000 ఉంటుంది"),
    ("C4", 111.70, 114.60, "1500 దాటితే అది 9000 దాకా అన్నమాట"),
    ("C5", 115.30, 117.50, "ఇన్సూరెన్స్ థర్డ్ పార్టీ అన్నీ సేమ్ ఉంటాయి"),
    ("C6", 118.55, 120.35, "ఈ ఓన్ డ్యామేజ్‌లో"),
    ("C7", 120.70, 123.25, "ఇంకా యాడ్-ఆన్స్ ఇంజిన్ కవరేజ్ అని"),
    ("C8", 123.85, 127.45, "రోడ్‌సైడ్ అసిస్టెన్స్ అని ఇవన్నీ సెపరేట్‌గా యాడ్ చేసుకుంటే"),
    ("C9", 128.08, 129.35, "ప్రీమియం పెరుగుతుంది"),
    ("C10", 131.40, 137.05, "బైక్ అయితే ఇన్స్పెక్షన్ ఏమీ ఉండదు కార్స్‌కి ఇన్స్పెక్షన్ ఉంటది"),
    ("C11", 140.78, 143.35, "ఎవరో వచ్చి ఇన్స్పెక్షన్ చేయాలి దానికి"),
    ("C12", 143.64, 146.70, "ఎలా అంటే నాలుగు సైడ్‌లు ఫోటోలు తీయాలి"),
    ("C13", 149.78, 154.45, "అదే ఫ్రంట్ కవర్ ఓపెన్ చేసి ఇంజిన్ అవన్నీ ఫోటోలు తీయాలి వీడియోలు తీయాలి"),
    ("C14", 154.88, 156.80, "గ్లాస్‌లు ఏమైనా ఫోటోలు తీయాలి"),
    ("C15", 157.29, 163.30, "ఇంకా ఇంజిన్ స్టార్ట్ చేసి వీడియో తీయాలి ఇంజిన్ రీడింగ్ మీటర్ రీడింగ్ అన్నీ ఫోటోలు తీసి పంపించాలి"),
    ("C16", 163.64, 165.95, "అవన్నీ ఓకే అనుకుంటే అప్పుడు వాళ్ళు"),
    ("C17", 166.35, 167.25, "యాక్సెప్ట్ చేస్తారు"),
] + [t for t in TIPS if t[0] != "T9"]

SEGS = BIKE if KIND == "bike" else CAR

TITLES = {
    "bike": ("బైక్ ఇన్సూరెన్స్ ఎంత అవుతుంది?", "{\\fnPopX}₹{\\fnRamaCap}1500 లో ఫుల్ కవర్ + టిప్స్"),
    "car": ("కార్ ఇన్సూరెన్స్ పూర్తి వివరాలు", "ఇన్స్పెక్షన్ ఎలా? + టిప్స్"),
}

R_ = "{\\fnPopX}₹{\\fnTeluguCap800}"  # rupee glyph inside card rows
# cards: (header, start_seg, end_seg, [(row_text, appear_seg, kind)])  kind: ok|warn|no|plain
CARDS = {
    "bike": [
        ("PERSONAL ACCIDENT", "B1", "B3", [(f"{R_}350 పే చేస్తే", "B2", "ok"), (f"{R_}15 లక్షల కవర్", "B3", "ok")]),
        ("IDV VALUE", "B7", "B9", [("కొత్త బండి → ఎక్కువ IDV", "B9", "ok"), ("పాత బండి → తక్కువ IDV", "B9+", "warn")]),
        ("BIKE INSURANCE", "B10", "B13", [
            (f"థర్డ్ పార్టీ  {R_}840", "B10", "ok"),
            (f"+ పర్సనల్ యాక్సిడెంట్  {R_}350", "B11", "ok"),
            (f"+ ఓన్ డ్యామేజ్  {R_}400", "B12", "ok"),
            (f"టోటల్  {R_}1500 – 1600", "B13", "star")]),
        ("థర్డ్ పార్టీ – CC బట్టి", "B14", "B17", [(f"150cc లోపు  {R_}800", "B15", "ok"), (f"150cc పైన  {R_}1600", "B17", "ok")]),
        ("NOTE", "B18", "B18", [("బైక్‌కి ఇన్స్పెక్షన్ లేదు", "B18", "ok")]),
        ("TIPS", "T2", "T12", [
            ("ఫస్ట్ 5 ఇయర్స్ ఫుల్ కవర్", "T2", "ok"),
            ("పర్సనల్ యాక్సిడెంట్ కవర్ మస్ట్", "T3", "ok"),
            ("10 ఇయర్స్ తర్వాత OD అవసరం లేదు", "T10", "no")]),
    ],
    "car": [
        ("CAR థర్డ్ పార్టీ", "C1", "C5", [
            (f"1000cc లోపు  {R_}2400", "C2", "ok"),
            (f"1000cc పైన  {R_}4000", "C3", "ok"),
            (f"1500cc పైన  {R_}9000", "C4", "ok")]),
        ("ADD-ONS", "C6", "C9", [
            ("ఇంజిన్ కవరేజ్", "C7", "ok"),
            ("రోడ్‌సైడ్ అసిస్టెన్స్", "C8", "ok"),
            ("ప్రీమియం పెరుగుతుంది", "C9", "warn")]),
        ("CAR INSPECTION", "C10", "C17", [
            ("4 సైడ్స్ ఫోటోలు", "C12", "ok"),
            ("ఇంజిన్ ఫోటోలు & వీడియో", "C13", "ok"),
            ("గ్లాస్ ఫోటోలు", "C14", "ok"),
            ("ఇంజిన్ స్టార్ట్ వీడియో", "C15", "ok"),
            ("మీటర్ రీడింగ్ ఫోటో", "C15+", "ok")]),
        ("TIPS", "T2", "T12", [
            ("ఫస్ట్ 5 ఇయర్స్ ఫుల్ కవర్", "T2", "ok"),
            ("పర్సనల్ యాక్సిడెంట్ కవర్ మస్ట్", "T3", "ok"),
            ("10 ఇయర్స్ తర్వాత OD అవసరం లేదు", "T10", "no")]),
    ],
}

KEY_Y = ["ఇన్సూరెన్స్", "థర్డ్", "పార్టీ", "ఓన్", "డ్యామేజ్", "IDV", "CC", "ఇన్స్పెక్షన్", "ప్రీమియం",
         "కాంప్రహెన్సివ్", "మస్ట్‌గా", "బెటర్", "ఫుల్", "లక్షలు", "లక్షల", "ఫోటోలు", "వీడియోలు", "వీడియో",
         "టిప్స్", "రోడ్‌సైడ్", "అసిస్టెన్స్", "యాడ్-ఆన్స్", "కవరేజ్", "రీడింగ్", "సర్వీసెస్"]
KEY_G = ["పర్సనల్", "యాక్సిడెంట్", "కవర్", "బైక్", "బైక్‌కైతే", "కార్లు", "కార్స్‌కి", "బండి", "బండికి",
         "ఇంజిన్", "అవసరం", "లేదు", "ఇయర్స్", "టోటల్", "యాక్సెప్ట్"]

# ---------------------------------------------------------------- cut video
ZOOM = 1.12
def run(cmd):
    subprocess.run(cmd, check=True)

work = f"{R}/work_{KIND}"
os.makedirs(work, exist_ok=True)
timeline = {}  # seg id -> (out_start, out_end)
t = 0.0
lst = []
for i, (sid, a, b, _) in enumerate(SEGS):
    d = round(b - a, 3)
    zoom = (i % 2 == 1)
    vf = "setpts=PTS-STARTPTS"
    if zoom:
        vf = (f"crop=iw/{ZOOM}:ih/{ZOOM}:(iw-iw/{ZOOM})/2:ih*0.02,scale=1080:1148:flags=lanczos,setsar=1,"
              + vf)
    f = f"{work}/s{i:02d}.mov"
    if not os.path.exists(f):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-i", f"{R}/crop.mov", "-ss", f"{a:.3f}", "-i", f"{R}/dn.wav",
             "-t", f"{d:.3f}", "-map", "0:v", "-map", "1:a",
             "-vf", vf + ",fps=30", "-af", f"afade=t=in:d=0.025,afade=t=out:st={d-0.04:.3f}:d=0.04",
             "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", f])
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
    timeline[sid] = (t, t + real)
    t += real
    lst.append(f)
END_LEN = 3.6
end_f = f"{work}/end.mov"
if not os.path.exists(end_f):
    run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1148:r=30", "-f", "lavfi",
         "-i", "anullsrc=r=48000:cl=stereo", "-t", str(END_LEN), "-c:v", "libx264", "-preset", "veryfast", "-crf", "12",
         "-c:a", "pcm_s16le", end_f])
lst.append(end_f)
MAIN_END = t
TOTAL = t + END_LEN
with open(f"{work}/list.txt", "w") as fh:
    fh.write("".join(f"file '{x}'\n" for x in lst))
run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{work}/list.txt", "-c", "copy", f"{work}/cut.mov"])

def seg_time(ref, which=0):
    plus = ref.endswith("+")
    sid = ref.rstrip("+")
    s, e = timeline[sid]
    if plus:
        return s + (e - s) * 0.55
    return (s, e)[which]

# ---------------------------------------------------------------- ASS
blob = hb.Blob.from_file_path(FONTS + "/RamaCap.ttf"); face = hb.Face(blob); hfont = hb.Font(face)
def width(txt, size):
    b = hb.Buffer(); b.add_str(txt); b.guess_segment_properties(); hb.shape(hfont, b)
    return sum(p.x_advance for p in b.glyph_positions) / face.upem * size

def ts(x):
    x = max(0, x)
    return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"

YEL, GRN, WHT = "&H0AD9F5&", "&H6AE35B&", "&HFFFFFF&"
ev = []
def add(layer, a, b, style, text):
    ev.append(f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{text}")

def is_num(w):
    return bool(re.match(r"^[0-9][0-9,]*$", w))

# chunk captions
card_spans = []
for hdr, s0, s1, rows in CARDS[KIND]:
    card_spans.append((seg_time(s0, 0), seg_time(s1, 1)))

def in_card(x):
    return any(a - 0.05 <= x <= b + 0.35 for a, b in card_spans)

CAP_Y_LOW, CAP_SIZE = 1372, 120
for sid, a, b, text in SEGS:
    s, e = timeline[sid]
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        n = 3 if len(words) - i >= 3 else len(words) - i
        if n == 3 and sum(len(w) for w in words[i:i+3]) > 26:
            n = 2
        if len(words) - i - n == 1:
            n += 1 if n < 3 else -1
        chunks.append(words[i:i+n]); i += n
    total = sum(len(" ".join(c)) for c in chunks)
    cur = s + 0.03
    span = (e - s) - 0.06
    for ci, c in enumerate(chunks):
        dur = span * len(" ".join(c)) / total
        parts = []
        for w in c:
            col = None
            core = w.rstrip(",")
            if is_num(core) or any(core.startswith(k) for k in KEY_Y):
                col = YEL
            elif any(core.startswith(k) for k in KEY_G):
                col = GRN
            parts.append(f"{{\\1c{col}}}{w}{{\\1c{WHT}}}" if col else w)
        plain = " ".join(c)
        sc = min(100, int(960 / max(1, width(plain, CAP_SIZE)) * 100))
        pop = (f"\\fscx{int(sc*.8)}\\fscy{int(sc*.8)}\\t(0,110,\\fscx{int(sc*1.06)}\\fscy{int(sc*1.06)})"
               f"\\t(110,180,\\fscx{sc}\\fscy{sc})")
        add(20, cur, cur + dur, "Cap", f"{{\\pos(540,{CAP_Y_LOW}){pop}}}" + " ".join(parts))
        cur += dur

# title bars (top black area)
t1, t2 = TITLES[KIND]
def fit(txt, size, maxw):
    plain = re.sub(r"\{[^}]*\}", "", txt)
    return min(100, int(maxw / max(1, width(plain, size)) * 100))
f1, f2 = fit(t1, 116, 940), fit(t2, 116, 940)
add(30, 0, TOTAL, "Title1", f"{{\\pos(540,104)\\fscx{f1}\\fscy{f1}\\fad(250,0)}}{t1}")
add(30, 0, TOTAL, "Title2", f"{{\\pos(540,226)\\fscx{f2}\\fscy{f2}\\fad(250,0)}}{t2}")

# progress bar
add(31, 0, TOTAL, "Draw", f"{{\\an7\\pos(0,0)\\1c&H2B30D8&\\bord0\\clip(0,0,0,12)\\t(0,{int(TOTAL*1000)},\\clip(0,0,1080,12))\\p1}}m 0 0 l 1080 0 l 1080 12 l 0 12")
add(32, 0, TOTAL, "Draw", f"{{\\an7\\move(-70,0,1010,0)\\1c&H0AD9F5&\\bord0\\p1}}m 0 0 l 70 0 l 70 12 l 0 12")

def rr(x0, y0, x1, y1, r):
    k = r * 0.45
    return (f"m {x0+r} {y0} l {x1-r} {y0} b {x1-k} {y0} {x1} {y0+k} {x1} {y0+r} l {x1} {y1-r} "
            f"b {x1} {y1-k} {x1-k} {y1} {x1-r} {y1} l {x0+r} {y1} b {x0+k} {y1} {x0} {y1-k} {x0} {y1-r} "
            f"l {x0} {y0+r} b {x0} {y0+k} {x0+k} {y0} {x0+r} {y0}")
def circ(cx, cy, r):
    k = r * 0.552
    return (f"m {cx} {cy-r} b {cx+k} {cy-r} {cx+r} {cy-k} {cx+r} {cy} b {cx+r} {cy+k} {cx+k} {cy+r} {cx} {cy+r} "
            f"b {cx-k} {cy+r} {cx-r} {cy+k} {cx-r} {cy} b {cx-r} {cy-k} {cx-k} {cy-r} {cx} {cy-r}")

# info cards
ROW_H, CX0, CX1, CARD_BOTTOM = 70, 80, 1000, 1290
for hdr, s0, s1, rows in CARDS[KIND]:
    first = min(seg_time(r[1]) if r[1].endswith("+") else seg_time(r[1], 0) for r in rows)
    a = max(seg_time(s0, 0) + 0.05, first - 0.6)
    b = seg_time(s1, 1) + 0.3
    n = len(rows)
    top = CARD_BOTTOM - (96 + n * ROW_H + 14)
    fade = "\\fad(180,220)"
    grow = "\\fscx92\\fscy92\\t(0,160,\\fscx100\\fscy100)"
    org = f"\\org(540,{(top+CARD_BOTTOM)//2})"
    add(10, a, b, "Draw", f"{{\\an7\\pos(6,8)\\1c&H000000&\\1a&H90&\\blur10\\bord0{fade}\\p1}}" + rr(CX0, top, CX1, CARD_BOTTOM, 34))
    add(11, a, b, "Draw", f"{{\\an7\\pos(0,0)\\1c&HF7F7F7&\\1a&H18&\\bord0{fade}\\p1}}" + rr(CX0, top, CX1, CARD_BOTTOM, 34))
    hw = max(300, width(hdr, 42) * 1.05 + 80)
    add(12, a, b, "Draw", f"{{\\an7\\pos(0,0)\\1c&H0AD9F5&\\bord0{fade}\\p1}}" + rr(540 - hw/2, top + 18, 540 + hw/2, top + 78, 30))
    add(13, a, b, "CardHdr", f"{{\\an5\\pos(540,{top+48}){fade}}}{hdr}")
    for ri, (txt, appear, kind) in enumerate(rows):
        ra = max(a, seg_time(appear) if appear.endswith("+") else seg_time(appear, 0)) + 0.1
        y0 = top + 96 + ri * ROW_H
        y1 = y0 + ROW_H - 10
        cy = (y0 + y1) // 2
        rf = "\\fad(160,220)"
        bg = "&HC8F3FF&" if kind in ("warn", "no", "star") else "&HFFFFFF&"
        add(14, ra, b, "Draw", f"{{\\an7\\move(30,0,0,0,0,180)\\1c{bg}\\bord0{rf}\\p1}}" + rr(CX0 + 20, y0, CX1 - 20, y1, 14))
        add(15, ra, b, "Draw", f"{{\\an7\\move(30,0,0,0,0,180)\\1c&H3A1F14&\\bord0{rf}\\p1}}" + circ(CX0 + 58, cy, 21))
        add(16, ra, b, "CardNum", f"{{\\an5\\move({CX0+88},{cy},{CX0+58},{cy},0,180){rf}}}{ri+1}")
        add(16, ra, b, "CardRow", f"{{\\an4\\move({CX0+122},{cy},{CX0+92},{cy},0,180){rf}}}{txt}")
        icx = CX1 - 62
        if kind in ("ok", "star"):
            col = "&H50AF4C&" if kind == "ok" else "&H0AA0F5&"
            add(15, ra, b, "Draw", f"{{\\an7\\pos(0,0)\\1c{col}\\bord0{rf}\\p1}}" + rr(icx - 22, cy - 22, icx + 22, cy + 22, 8))
            add(16, ra, b, "Draw", f"{{\\an7\\pos(0,0)\\1a&HFF&\\3c&HFFFFFF&\\bord4{rf}\\p1}}m {icx-11} {cy+1} l {icx-3} {cy+10} l {icx+12} {cy-9}")
        elif kind == "warn":
            add(15, ra, b, "Draw", f"{{\\an7\\pos(0,0)\\1c&H00B4FF&\\3c&H1A1A1A&\\bord2{rf}\\p1}}m {icx} {cy-22} l {icx+24} {cy+20} l {icx-24} {cy+20}")
            add(16, ra, b, "CardNum", f"{{\\an5\\pos({icx},{cy+6})\\1c&H000000&\\fs32{rf}}}!")
        else:  # no
            add(15, ra, b, "Draw", f"{{\\an7\\pos(0,0)\\1c&H3A3AE5&\\bord0{rf}\\p1}}" + rr(icx - 22, cy - 22, icx + 22, cy + 22, 8))
            add(16, ra, b, "Draw", f"{{\\an7\\pos(0,0)\\1a&HFF&\\3c&HFFFFFF&\\bord4{rf}\\p1}}m {icx-10} {cy-10} l {icx+10} {cy+10} m {icx+10} {cy-10} l {icx-10} {cy+10}")

# end screen
es = MAIN_END
add(40, es, TOTAL, "EndTxt", f"{{\\pos(540,950)\\fad(200,0)\\fscx80\\fscy80\\t(0,200,\\fscx100\\fscy100)}}లైక్ & సబ్‌స్క్రైబ్ చేయండి")
add(40, es + 0.3, TOTAL, "Draw", f"{{\\an7\\pos(0,0)\\1c&HF0821A&\\bord0\\fad(150,0)\\p1}}" + rr(180, 1030, 470, 1130, 50))
add(41, es + 0.3, TOTAL, "Btn", f"{{\\an5\\pos(325,1080)\\fad(150,0)}}LIKE")
add(40, es + 0.5, es + 1.8, "Draw", f"{{\\an7\\pos(0,0)\\1c&H1C1CE0&\\bord0\\fad(150,0)\\p1}}" + rr(510, 1030, 900, 1130, 50))
add(41, es + 0.5, es + 1.8, "Btn", f"{{\\an5\\pos(705,1080)\\fad(150,0)}}SUBSCRIBE")
add(40, es + 1.8, TOTAL, "Draw", f"{{\\an7\\pos(0,0)\\1c&H606060&\\bord0\\p1}}" + rr(510, 1030, 900, 1130, 50))
add(41, es + 1.8, TOTAL, "Btn", f"{{\\an5\\pos(705,1080)\\fs42}}SUBSCRIBED")

# hanging contact board
A_, P_ = 3.5, 2.6
TM, MV, DY = MAIN_END, 0.55, -1030
PX, PY = 540, 1490
X0, X1, Y0, Y1 = 230, 850, 1590, 1820
def swing(t0, t1, py, delay=0.0, settle=False):
    s_ = f"\\org({PX},{py})\\frz0"; tt = t0 + delay; step = 0.13
    while tt < t1 - 1e-6:
        t2 = min(tt + step, t1); ang = A_ * math.sin(2 * math.pi * (t2 - t0 - delay) / P_)
        if settle and t2 > t1 - 0.25: ang = 0
        s_ += f"\\t({int((tt-t0)*1000)},{int((t2-t0)*1000)},\\frz{ang:.2f})"; tt = t2
    return s_
parts = [
    (50, "Draw", "\\an7\\1a&HFF&\\bord5\\3c&HC8E0F0&\\p1", f"m {PX} {PY} l {X0+60} {Y0+24} m {PX} {PY} l {X1-60} {Y0+24}", (0, 0)),
    (51, "Draw", "\\an7\\1c&H000000&\\1a&H60&\\bord0\\blur8\\p1", rr(X0, Y0, X1, Y1, 30), (10, 12)),
    (52, "Draw", "\\an7\\1c&H2B30D8&\\bord0\\p1", rr(X0, Y0, X1, Y1, 30), (0, 0)),
    (53, "Draw", "\\an7\\1c&H0AD9F5&\\bord0\\p1", rr(X0+12, Y0+12, X1-12, Y1-12, 22), (0, 0)),
    (54, "Draw", "\\an7\\1c&H1A2A3A&\\bord0\\p1", circ(X0+60, Y0+26, 9) + " " + circ(X1-60, Y0+26, 9), (0, 0)),
    (54, "Draw", "\\an7\\1c&HC0C0C0&\\3c&H202020&\\bord3\\p1", circ(PX, PY, 12), (0, 0)),
    (55, "HangTe", "\\an5", "కాల్ చేయండి", (540, 1660)),
    (55, "HangTxt", "\\an5", "7989615350", (540, 1758)),
]
# split the long swing into windows so each line stays a sane length
win = 26.0  # 10 swing periods, so phase stays continuous
w0 = 0.0
while w0 < TM - 1e-6:
    w1 = min(TM, w0 + win)
    sw = swing(w0, w1, PY, settle=(w1 == TM))
    # keep phase continuous: swing() restarts at angle 0 each window; windows are multiples of P_/2 apart
    for L, st, tg, tx, (ox, oy) in parts:
        add(L, w0, w1, st, f"{{{tg}\\pos({ox},{oy}){sw}}}{tx}")
    w0 = w1
sw_top = swing(TM, TOTAL, PY + DY, delay=MV)
for L, st, tg, tx, (ox, oy) in parts:
    add(L, TM, TOTAL, st, f"{{{tg}\\move({ox},{oy},{ox},{oy+DY},0,{int(MV*1000)}){sw_top}}}{tx}")

HDR = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,RamaCap,120,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,6,7,5,40,40,0,1
Style: Title1,RamaCap,116,&H00FFFFFF,&H00FFFFFF,&H002B30D8,&H00000000,0,0,0,0,100,100,0,0,3,18,0,5,30,30,0,1
Style: Title2,RamaCap,116,&H00000000,&H00000000,&H000AD9F5,&H00000000,0,0,0,0,100,100,0,0,3,18,0,5,30,30,0,1
Style: Draw,PopX,20,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1
Style: CardHdr,TeluguCap800,42,&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: CardNum,PopX,30,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: CardRow,TeluguCap800,48,&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,4,0,0,0,1
Style: EndTxt,RamaCap,124,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Btn,PopX,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: HangTxt,PopX,100,&H00000000,&H00000000,&H00000000,&H00000000,0,0,0,0,100,100,2,0,1,0,0,5,0,0,0,1
Style: HangTe,RamaCap,104,&H002B30D8,&H00000000,&H002B30D8,&H00000000,0,0,0,0,100,100,0,0,1,1,0,5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ass = f"{work}/overlay.ass"
open(ass, "w").write(HDR + "\n".join(ev) + "\n")
json.dump(timeline, open(f"{work}/timeline.json", "w"), indent=1)
print(f"main {MAIN_END:.2f}s total {TOTAL:.2f}s, events {len(ev)}")

if "--no-render" in sys.argv:
    sys.exit(0)
# ---------------------------------------------------------------- final render
fc = ("[0:v]split=2[a][b];"
      "[a]scale=1806:1920,crop=1080:1920,boxblur=40:3,eq=brightness=-0.18:saturation=1.1[bg];"
      f"[bg][b]overlay=0:300:shortest=1,drawbox=0:0:1080:300:black:t=fill,"
      f"drawbox=0:300:1080:1620:black:t=fill:enable='gte(t,{MAIN_END:.3f})',"
      f"ass={ass}:fontsdir={FONTS}[v];"
      "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[au]")
run(["ffmpeg", "-v", "error", "-y", "-i", f"{work}/cut.mov", "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
     "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-r", "30",
     "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", OUT])
print("wrote", OUT)
