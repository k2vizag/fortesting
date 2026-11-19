# "Naa Koduka" cinematic silhouette lyrical video (Telugu + English letters), 1080x1920.
# 1) align the user's 53 lines to Whisper large-v3 words (char-level difflib, in order)
# 2) scene layer (sil.html via render.js, one scene per line, colour bloom at the end of each line)
# 3) lyric layer (text_layer.js PNG states, karaoke word fill) for te / en, overlaid; song audio from T0.
# Usage: python3 build.py <song.wav> <whisper_words.json> <fontsdir> <outdir> [--preview]
import json, subprocess, sys, os, difflib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lyrics import L
SONG, ASR, FONTS, OUT = sys.argv[1:5]; PREVIEW = "--preview" in sys.argv
HERE = os.path.dirname(os.path.abspath(__file__)); os.makedirs(OUT, exist_ok=True)
W = [(w[0], w[1], w[2].strip()) for s in json.load(open(ASR)) for w in s["w"] if w[2].strip()]
W = [w for w in W if 30.0 < w[0] < 258.0]          # 0-30 s intro music, >258 s silence (Whisper noise)
# Whisper stretches the first word of a segment over the music gap: keep only its last 0.6 s
W = [(max(s, e - 0.6) if e - s > 1.3 else s, e, t) for s, e, t in W]
# char stream with times
wc, wt = [], []
for s, e, t in W:
    for j, ch in enumerate(t): wc.append(ch); wt.append(s + (e - s) * j / max(1, len(t)))
# long/short vowel signs compared as equal; each char maps to exactly one char (keeps indices aligned)
norm = lambda ch: ch if ch not in "్ాీూేో" else {"ా": "~", "ీ": "ి", "ూ": "ు", "ే": "ె", "ో": "ొ", "్": "్"}[ch]
uc, uidx = [], []                                  # user chars -> (line, word)
for li, (te, en, key) in enumerate(L):
    for wi, w in enumerate(te.split()):
        for j, ch in enumerate(w): uc.append(ch); uidx.append((li, wi, j))
# global character alignment (Needleman-Wunsch, numpy rows): keeps every line in order, no drift
import numpy as np
UA = "".join(map(norm, uc)); WB = "".join(map(norm, wc)); n, m = len(UA), len(WB)
MATCH, MIS, GAP = 2, -1, -1
ub = np.frombuffer(UA.encode("utf-32-le"), dtype=np.uint32); wb = np.frombuffer(WB.encode("utf-32-le"), dtype=np.uint32)
score = np.zeros((n + 1, m + 1), np.int32); ptr = np.zeros((n + 1, m + 1), np.uint8)   # 0 diag 1 up 2 left
score[0, :] = np.arange(m + 1) * GAP; score[:, 0] = np.arange(n + 1) * GAP; ptr[0, 1:] = 2; ptr[1:, 0] = 1
for i in range(1, n + 1):
    diag = score[i - 1, :-1] + np.where(wb == ub[i - 1], MATCH, MIS)
    up = score[i - 1, 1:] + GAP
    best = np.maximum(diag, up); pt = np.where(diag >= up, 0, 1).astype(np.uint8)
    row = score[i]; row[1:] = best
    for j in range(1, m + 1):                       # left moves (sequential dependency)
        if row[j - 1] + GAP > row[j]: row[j] = row[j - 1] + GAP; pt[j - 1] = 2
    ptr[i, 1:] = pt
print("align", n, m, file=sys.stderr)
umap = {}; i, j = n, m
while i > 0 and j > 0:
    p = ptr[i, j]
    if p == 0:
        if ub[i - 1] == wb[j - 1]: umap[i - 1] = wt[j - 1]
        i -= 1; j -= 1
    elif p == 1: i -= 1
    else: j -= 1
# word start = time of its first matched char (interpolated if unmatched)
ws = {}
for k, (li, wi, j) in enumerate(uidx):
    if k in umap: ws.setdefault((li, wi), []).append((j, umap[k]))
keys = [(li, wi) for li, (te, _, _) in enumerate(L) for wi, _ in enumerate(te.split())]
times = []
for key in keys:
    v = ws.get(key)
    if v and len(v) >= 2 or v and len(v) == 1 and len(L[key[0]][0].split()[key[1]]) <= 2:
        c = sorted(t - j * 0.08 for j, t in v); times.append(c[len(c) // 2])     # median: one stray char match can't pull it
    else: times.append(None)
# fill gaps by linear interpolation between known words; enforce monotonic
line_of = [li for li, _ in keys]
for i in range(len(times)):                         # unmatched word: from the nearest matched word of the same line
    if times[i] is None:
        nx = next((k for k in range(i + 1, len(keys)) if line_of[k] == line_of[i] and times[k] is not None), None)
        pv = next((k for k in range(i - 1, -1, -1) if line_of[k] == line_of[i] and times[k] is not None), None)
        if nx is not None: times[i] = ("n", nx)
        elif pv is not None: times[i] = ("p", pv)
for i in range(len(times)):
    if isinstance(times[i], tuple):
        m, k = times[i]; times[i] = times[k] - 0.4 * (k - i) if m == "n" else times[k] + 0.4 * (i - k)
known = [i for i, t in enumerate(times) if t is not None]
for i in range(len(times)):
    if times[i] is None:
        p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
        times[i] = times[p] + 0.35 * (i - p) if n is None else (times[n] - 0.35 * (n - i) if p is None else times[p] + (times[n] - times[p]) * (i - p) / (n - p))
for i in range(1, len(times)): times[i] = max(times[i], times[i - 1] + 0.12)
wt_of = dict(zip(keys, times))
# last line (final repeat of "అమ్మ దివేనిది నా కొడుకా") is sung after 242 s, in the outro Whisper did not transcribe
FINAL = 242.6
if wt_of[(len(L) - 1, 0)] < FINAL:
    for j in range(len(L[-1][0].split())): wt_of[(len(L) - 1, j)] = FINAL + 0.55 * j
line_start = [wt_of[(li, 0)] for li in range(len(L))]
lastw = lambda li: wt_of[(li, len(L[li][0].split()) - 1)]
line_end = [min(lastw(li) + 0.9, line_start[li + 1] - 0.05) if li + 1 < len(L) else lastw(li) + 2.5 for li in range(len(L))]
T0 = max(0.0, line_start[0] - 3.0); END = 257.5; TOTAL = END - T0      # song fades out by ~257 s
print(f"song {T0:.2f}-{END:.2f} ({TOTAL:.1f}s), unmatched words: {sum(1 for k in keys if k not in ws)}/{len(keys)}")
for li in range(len(L)): print(f"{li+1:2d} {line_start[li]:7.2f}-{line_end[li]:7.2f} {L[li][0]}")
json.dump({"T0": T0, "lines": [{"a": line_start[i], "b": line_end[i], "te": L[i][0], "en": L[i][1], "key": L[i][2],
           "w": [wt_of[(i, j)] for j in range(len(L[i][0].split()))]} for i in range(len(L))]}, open(f"{OUT}/timing.json", "w"), ensure_ascii=False, indent=1)
o = lambda t: t - T0
scenes = [{"a": round(max(0, o(line_start[i]) - 0.35), 3), "b": round(o(line_end[i]), 3), "key": L[i][2], "seed": i + 1} for i in range(len(L))]
scenes[0]["a"] = 0.0
json.dump({"total": TOTAL, "scenes": scenes}, open(f"{OUT}/scenes.json", "w"))
if PREVIEW: sys.exit()
# scene layer
sl = f"{OUT}/scenes_silent.mp4"
if not os.path.exists(sl):
    subprocess.run(["node", f"{HERE}/render.js", f"{OUT}/scenes.json", "full", sl, "30"], check=True)
# lyric states per language
for lang in ("te", "en"):
    states = []
    def push(t0, t1, words, fill, nxt):
        if states and t0 > states[-1]["t1"] + 0.01: states.append({"t0": states[-1]["t1"], "t1": t0, "words": [], "fill": 0, "next": ""})
        if states and t0 < states[-1]["t1"]: states[-1]["t1"] = t0
        if t1 - t0 > 0.005: states.append({"t0": round(t0, 3), "t1": round(t1, 3), "words": words, "fill": fill, "next": nxt})
    for i, (te, en, key) in enumerate(L):
        words = (te if lang == "te" else en).split(); tw = [o(wt_of[(i, j)]) for j in range(len(te.split()))]
        if len(words) != len(tw):                     # EN word count differs -> spread over the sung span
            a, b = tw[0], tw[-1] + 0.5; tot = sum(map(len, words)); tw = []; t = a
            for w in words: tw.append(t); t += (b - a) * len(w) / tot
        nxt = (L[i + 1][0] if lang == "te" else L[i + 1][1]) if i + 1 < len(L) and line_start[i + 1] - line_end[i] < 2.0 else ""
        a = max(0.0, o(line_start[i]) - 0.3); b = o(line_end[i])
        cuts = [a] + [max(a, x) for x in tw] + [b]
        for n in range(len(words) + 1): push(cuts[n], cuts[n + 1], words, n, nxt)
    states[0]["t0"] = 0.0
    if states[-1]["t1"] < TOTAL: states.append({"t0": states[-1]["t1"], "t1": TOTAL, "words": [], "fill": 0, "next": ""})
    json.dump({"lang": lang, "title": "♪ నా కొడుకా ♪" if lang == "te" else "♪ Naa Koduka ♪", "states": states},
              open(f"{OUT}/states_{lang}.json", "w"), ensure_ascii=False)
    d = f"{OUT}/png_{lang}"; os.makedirs(d, exist_ok=True)
    subprocess.run(["node", f"{HERE}/text_layer.js", f"{OUT}/states_{lang}.json", os.path.abspath(FONTS), d], check=True)
    lst = "".join(f"file '{d}/s{i:04d}.png'\nduration {x['t1']-x['t0']:.3f}\n" for i, x in enumerate(states)) + f"file '{d}/s{len(states)-1:04d}.png'\n"
    open(f"{d}/list.txt", "w").write(lst)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", sl, "-f", "concat", "-safe", "0", "-i", f"{d}/list.txt",
                    "-ss", f"{T0}", "-t", f"{TOTAL}", "-i", SONG,
                    "-filter_complex", f"[1:v]fps=30,format=rgba[tx];[0:v][tx]overlay=0:0:format=auto,hqdn3d=2:2:6:6,format=yuv420p[v];"
                    f"[2:a]afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL-2.5:.2f}:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
                    "-map", "[v]", "-map", "[a]", "-t", f"{TOTAL}", "-c:v", "libx264", "-preset", "slow", "-crf", "24",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{OUT}/naa_koduka_lyrical_{lang}.mp4"], check=True)
print("done", round(TOTAL, 1))
