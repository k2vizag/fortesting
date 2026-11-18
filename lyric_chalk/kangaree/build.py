# "Kangaree Padaku Ra" chalk lyric shorts – Telugu only (user's lyrics, lines.json).
# Line times (song seconds) from Whisper large-v3 word times; first word moved later
# where Whisper stretched it over the music. Chorus used once (video 2).
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1] if len(sys.argv) > 1 else HERE + '/data'
LY = json.load(open(HERE + '/lines.json'))
T = {0: (25.9, 29.9), 1: (31.3, 35.64), 2: (47.6, 51.54), 3: (52.9, 57.16), 4: (57.9, 62.86), 5: (63.6, 68.66), 6: (69.4, 73.88),
     7: (74.5, 80.18), 8: (80.18, 83.98), 9: (85.4, 88.42), 10: (88.42, 91.16), 11: (91.16, 95.04),
     12: (102.3, 107.24), 13: (107.24, 112.32), 14: (113.2, 115.14), 15: (115.14, 117.88), 16: (118.4, 120.94), 17: (120.94, 123.48),
     18: (124.3, 128.98), 19: (129.9, 134.2), 20: (135.2, 140.06), 21: (141.0, 145.28),
     22: (189.8, 195.3), 23: (195.3, 200.54), 24: (201.3, 206.36), 25: (206.9, 211.86), 26: (212.8, 217.2), 27: (218.3, 222.84),
     28: (223.8, 228.34), 29: (229.3, 233.82)}
SCN = ['kangaru', 'katha', 'kanneellu', 'kallolam', 'daivam', 'pustakam', 'yuddham', 'neeke', 'chettu', 'chikkulu', 'ekkillu', 'dhairyam',
       'paduthu', 'pareeksha', 'neduthu', 'vidhivala', 'tenchuku', 'sankelle', 'charitha', 'odidudukulu', 'gattu', 'sisiram',
       'guvvalu', 'chotu', 'mabbu', 'chinuku', 'gelupu', 'edureetha', 'malupu', 'kanuvippu']
VIDEOS = [("1_kangaree_padakura", 24.6, 57.5, range(0, 4)), ("2_neeke_ila", 57.3, 96.5, range(4, 12)),
          ("3_paduthu_paduthu", 100.9, 145.5, range(12, 22)), ("4_kanipetti", 188.9, 233.9, range(22, 30))]
os.makedirs(OUT, exist_ok=True)
for name, st, en, rng_ in VIDEOS:
    total = round(en - st, 2); sc = []
    for i in rng_:
        a0 = 0.3 if not sc else round(T[i][0] - st - 0.25, 2)
        if sc: sc[-1]["b"] = a0
        sc.append({"a": a0, "b": total, "key": SCN[i]})
    lines = [{"a": round(T[i][0] - st, 2), "b": round(T[i][1] - st, 2), "t": LY[i][0]} for i in rng_]
    json.dump({"total": total, "start": st, "font": "te", "color": True, "title": "Kangaree Padaku Ra",
               "scenesFile": "../scenes.js", "lines": lines, "scenes": sc}, open(f"{OUT}/{name}_te.json", "w"), ensure_ascii=False, indent=1)
    print(name, total, len(rng_))
