"""Non-Telugu customers (part 1 + 2 joined): original video/audio, captions for clear lines + emoji stickers."""
import json, subprocess
S = "/tmp/claude-0/-home-user-fortesting/004c5537-9f09-5aeb-bf62-7697570324f1/scratchpad"
W = S + "/run6/work"
TOT = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", W + "/base.mov"],
                           capture_output=True, text=True).stdout)
# (start, end, lines) – foreign words in Telugu script (white + gradient), Telugu meaning as small italic line
C = lambda a, b, *ls: {"a": a, "b": b, "lines": [{"cls": c, "t": t} for c, t in ls]}
caps = [
    C(9.6, 11.6, ("cw", "యహా పర్"), ("ch", "RTO ఆఫీస్"), ("cs", "ఇక్కడ RTO ఆఫీస్...")),
    C(11.6, 13.7, ("ch", "కహా హై? 🤔"), ("cs", "ఎక్కడ ఉంది?")),
    C(16.0, 19.3, ("cw", "తెలుగు"), ("ch g", "నహీ ఆతా హై 😅"), ("cs", "తెలుగు రాదు")),
    C(59.8, 61.9, ("cw", "తెలుగు"), ("ch g", "నహీ... 🙅")),
    C(61.9, 64.6, ("ch", "ఆల్ ఇంగ్లీష్ 😂")),
    C(81.85, 83.7, ("cw", "కిత్నా"), ("ch", "పైసా లేగా? 💸"), ("cs", "ఎంత తీసుకుంటారు?")),
    C(86.0, 88.0, ("cw", "అచ్ఛా"), ("ch", "ఫోటో ఫ్రేమ్"), ("cs", "చాహియే – కావాలి")),
    C(88.0, 90.1, ("cw", "వో వాలా ఫోటో ఫ్రేమ్"), ("ch", "కిత్నా? 🤔"), ("cs", "ఆ ఫ్రేమ్ ఎంత?")),
    C(92.56, 94.1, ("cw", "ఐసా"), ("ch", "డిజైన్ చాహియే"), ("cs", "ఇలాంటి డిజైన్ కావాలి")),
    C(94.43, 95.6, ("cw", "కిత్నా"), ("ch", "ఫోటోస్ చాహియే?"), ("cs", "ఎన్ని ఫోటోలు కావాలి?")),
]
ST = [  # time, side, emoji, label, duration
    (0.4, "r", "🗣️", "తమిళ్ కస్టమర్", 2.6),
    (3.3, "l", "😵‍💫", "", 2.6),
    (7.2, "r", "🤷", "", 1.8),
    (9.7, "l", "🏢", "RTO ఆఫీస్?", 3.6),
    (14.2, "r", "🤔", "", 1.8),
    (16.2, "l", "🙅", "తెలుగు రాదు", 3.0),
    (20.0, "r", "😅", "", 2.4),
    (24.3, "l", "👋", "", 2.0),
    (28.8, "r", "🤯", "", 2.4),
    (32.3, "l", "🙏", "", 2.2),
    (37.3, "r", "😂", "", 2.4),
    (41.6, "l", "🤣", "", 2.2),
    (44.4, "r", "🫣", "", 2.2),
    (51.8, "l", "😶", "", 1.8),
    (57.0, "l", "🧐", "", 2.6),
    (59.9, "r", "🇬🇧", "ఆల్ ఇంగ్లీష్", 4.6),
    (65.7, "l", "😆", "", 2.6),
    (69.0, "r", "🎬", "పార్ట్ 2", 2.6),
    (72.5, "l", "🤔", "", 2.0),
    (75.1, "r", "📞", "", 2.6),
    (78.7, "l", "😤", "", 2.6),
    (81.9, "r", "💸", "కిత్నా?", 2.0),
    (86.1, "l", "🖼️", "ఫోటో ఫ్రేమ్", 3.8),
    (92.6, "r", "🎨", "డిజైన్", 1.9),
    (94.5, "l", "📸", "ఎన్ని ఫోటోలు?", 2.2),
    (97.4, "r", "👋", "", 2.2),
    (99.4, "l", "😂", "", 2.0),
]
stk = [{"a": t, "b": t + d, "side": s, "label": lb, "emoji": e, "color": "blue", "icon": "check"} for t, s, e, lb, d in ST]
data = {"main_end": TOT + 100, "total": TOT, "captions": caps, "stickers": stk, "numbers": [], "cards": [],
        "board": {"phone": "7989615350"}, "title": None}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
print("total", round(TOT, 2), "captions", len(caps), "stickers", len(stk))
