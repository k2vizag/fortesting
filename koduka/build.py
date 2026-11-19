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
W = [w for w in W if w[0] > 30.0]                  # 0-30 s: intro music (Whisper noise)
# char stream with times
wc, wt = [], []
for s, e, t in W:
    for j, ch in enumerate(t): wc.append(ch); wt.append(s + (e - s) * j / max(1, len(t)))
norm = lambda ch: ch if ch not in "్ాీూేో" else {"ా": "", "ీ": "ి", "ూ": "ు", "ే": "ె", "ో": "ొ", "్": "్"}[ch]
uc, uidx = [], []                                  # user chars -> (line, word)
for li, (te, en, key) in enumerate(L):
    for wi, w in enumerate(te.split()):
        for j, ch in enumerate(w): uc.append(ch); uidx.append((li, wi, j))
sm = difflib.SequenceMatcher(None, "".join(map(norm, uc)), "".join(map(norm, wc)), autojunk=False)
umap = {}
for a, b, n in sm.get_matching_blocks():
    for k in range(n): umap[a + k] = wt[b + k]
# word start = time of its first matched char (interpolated if unmatched)
ws = {}
for k, (li, wi, j) in enumerate(uidx):
    if k in umap: ws.setdefault((li, wi), []).append((j, umap[k]))
keys = [(li, wi) for li, (te, _, _) in enumerate(L) for wi, _ in enumerate(te.split())]
times = []
for key in keys:
    v = ws.get(key); times.append(min(t - j * 0.08 for j, t in v) if v else None)
# fill gaps by linear interpolation between known words; enforce monotonic
known = [i for i, t in enumerate(times) if t is not None]
for i in range(len(times)):
    if times[i] is None:
        p = max([k for k in known if k < i], default=None); n = min([k for k in known if k > i], default=None)
        times[i] = times[p] + 0.35 * (i - p) if n is None else (times[n] - 0.35 * (n - i) if p is None else times[p] + (times[n] - times[p]) * (i - p) / (n - p))
for i in range(1, len(times)): times[i] = max(times[i], times[i - 1] + 0.12)
wt_of = dict(zip(keys, times))
line_start = [wt_of[(li, 0)] for li in range(len(L))]
lastw = lambda li: wt_of[(li, len(L[li][0].split()) - 1)]
line_end = [min(lastw(li) + 0.9, line_start[li + 1] - 0.05) if li + 1 < len(L) else lastw(li) + 1.6 for li in range(len(L))]
T0 = max(0.0, line_start[0] - 3.0); END = line_end[-1] + 3.5; TOTAL = END - T0
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
                    "-filter_complex", f"[1:v]fps=30,format=rgba[tx];[0:v][tx]overlay=0:0:format=auto,format=yuv420p[v];"
                    f"[2:a]afade=t=in:st=0:d=1.0,afade=t=out:st={TOTAL-2.5:.2f}:d=2.5,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[a]",
                    "-map", "[v]", "-map", "[a]", "-t", f"{TOTAL}", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", f"{OUT}/naa_koduka_lyrical_{lang}.mp4"], check=True)
print("done", round(TOTAL, 1))
