# "Nee prashnalu neeve" chalk lyric shorts. Lyrics = user's text only (lines.json: [telugu, english]).
# Line times (song seconds) from Whisper large-v3 word times (first word moved later where Whisper
# stretched it over the music), 186-207 s re-transcribed separately.
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = sys.argv[1] if len(sys.argv) > 1 else HERE + '/data'
LY = json.load(open(HERE + '/lines.json'))
T = {0: (0.2, 4.3), 1: (8.0, 12.96), 2: (16.6, 20.62), 3: (21.8, 26.06), 4: (27.2, 31.54), 5: (32.9, 36.96),
     6: (37.9, 42.2), 7: (43.9, 47.9), 8: (49.3, 51.22), 9: (51.6, 54.26), 10: (54.26, 59.54), 11: (59.54, 65.22),
     12: (88.0, 92.78), 13: (93.4, 97.94), 14: (98.5, 103.74), 15: (103.74, 108.86), 16: (108.86, 111.54), 17: (111.54, 114.28),
     18: (114.28, 119.82), 19: (122.6, 124.84), 20: (127.4, 130.34),
     21: (159.0, 163.7), 22: (163.7, 168.94), 23: (169.4, 174.62), 24: (174.62, 179.76), 25: (179.76, 182.54), 26: (182.54, 185.26),
     27: (185.26, 190.66), 28: (190.66, 196.18), 29: (198.9, 201.62), 30: (202.3, 206.92)}
SCN = ['prashnalu', 'chikkulu', 'gaali', 'aagalo', 'amma', 'kanane', 'kusumam', 'gudiko', 'badi', 'suluva', 'porabadina', 'nimisham',
       'alalu', 'kalalu', 'nadireyi', 'gamyam', 'valapu', 'vayasu', 'gelupu', 'sudilo', 'vinaleva',
       'tarunam', 'paatham', 'ravi', 'chikati', 'payanalu', 'pranayalu', 'charitha', 'smruthi', 'vidhi', 'edureetha']
VIDEOS = [("1_nee_prashnalu", 0.0, 37.5, range(0, 6), 0.05), ("2_prathi_kusumam", 37.3, 67.5, range(6, 12), 0.4),
          ("3_alalundani", 86.8, 131.0, range(12, 21), 0.4), ("4_porapaatuna", 158.0, 207.0, range(21, 31), 0.4)]
os.makedirs(OUT, exist_ok=True)
for name, st, en, rng_, fin in VIDEOS:
    total = round(en - st, 2); sc = []
    for i in rng_:
        a0 = 0.3 if not sc else round(T[i][0] - st - 0.25, 2)
        if sc: sc[-1]["b"] = a0
        sc.append({"a": a0, "b": total, "key": SCN[i]})
    for fi, font in enumerate(("te", "en")):
        lines = [{"a": round(T[i][0] - st, 2), "b": round(T[i][1] - st, 2), "t": LY[i][fi]} for i in rng_]
        json.dump({"total": total, "start": st, "fadeIn": fin, "font": font, "color": True, "title": "Nee Prashnalu Neeve",
                   "scenesFile": "../scenes.js", "lines": lines, "scenes": sc}, open(f"{OUT}/{name}_{font}.json", "w"), ensure_ascii=False, indent=1)
    print(name, total, len(rng_))
