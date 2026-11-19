# "O Alasendra" lyrical short, 1080x1920. Audio follows the user's script only:
#   A = chorus x2 (song 39.6-72.85), B = verse (88.35-122.3), C = chorus x2 (171.8-207.3).
# Line times from Whisper large-v3 word timestamps (asr.json); chorus 3/4 = chorus 1/2 + 131.87 s
# (same recording repeated). Karaoke per word: user words mapped onto Whisper word times by char position.
# Usage: python3 build.py <src.mp4> whisper_words.json ../insurance/v2/fonts <outdir>
# (whisper_words.json from asr.py: faster-whisper large-v3, language te, word timestamps)
import json, subprocess, sys, os
SRC, ASR, FONTS, OUT = sys.argv[1:5]
os.makedirs(OUT, exist_ok=True)
SEG = [(39.6, 72.85), (88.35, 122.3), (171.8, 207.3)]          # audio, song seconds
def out_t(t):                                                    # song time -> video time
    o = 0
    for a, b in SEG:
        if a - 1 <= t <= b + 0.5: return o + t - a
        o += b - a
    raise ValueError(t)
TOTAL = sum(b - a for a, b in SEG)
# visuals: (src start, src end) in order, sums to TOTAL per section
VIS = [(32.9, 38.5), (45.25, 72.9),                              # A: colour smoke, festival dance
       (89.0, 94.5), (123.0, 144.0), (76.0, 83.45),              # B: searching, roses, girls laughing
       (171.8, 196.7), (207.0, 208.8), (215.8, 219.9), (222.5, 227.2)]   # C: film's own, bus, window smile
assert abs(sum(b - a for a, b in VIS) - TOTAL) < 0.02, (sum(b - a for a, b in VIS), TOTAL)
C = 131.87
CH1 = [40.14, 45.34, 49.42, 53.48, 56.4]; CH2 = [56.6, 61.52, 65.72, 69.86, 72.6]
VER = [89.9, 94.0, 98.1, 102.14, 106.5, 110.7, 114.26, 118.78, 122.3]
TE = {"c1": "ఓ అలసేంద్ర వంకోలే ఉన్నావే పిల్లా", "c2": "ఇలా వాకిలి మెరిసిందే నీ అందం వల్లా",
      "c3": "ముంగురు కురులా గాలం వేసావే పిల్లా", "c4": "ఊపిరి కుదిపేసావే", "c6": "నా మనసే మైమరిసే నీ అందం వల్లా",
      "c18": "ఇలా మెరిసి మురిసిందే నీ అందం వల్లా",
      "v1": "నీ కోసం నా కనులే", "v2": "రెప్పే వేయక తెరిచి గాలించే", "v3": "నీ చూపే సోకింగా",
      "v4": "నదిలా నా తనువే ఊయలలూగే", "v5": "నీతోనే జతగా నడవాలనే ఆశ", "v6": "తొలకరి మొలకోలే చిగురించిందే",
      "v7": "నా నీడే నీవై ఉండాలని తలచి", "v8": "చూసిన ప్రతిరాయికి నే మొక్కితినే"}
EN = {"c1": "O alasendra vankole unnaave pillaa", "c2": "Ilaa vaakili merisindhe nee andham vallaa",
      "c3": "Munguru kurulaa gaalam vesaave pillaa", "c4": "Oopiri kudhipesaave", "c6": "Naa manase maimarise nee andham vallaa",
      "c18": "Ilaa merisi murisindhe nee andham vallaa",
      "v1": "Nee kosam naa kanule", "v2": "Reppe veyaka therichi gaalinche", "v3": "Nee choope sokingaa",
      "v4": "Nadhilaa naa thanuve ooyalaloogey", "v5": "Neethone jathagaa nadavaalane aasha", "v6": "Tholakari molakole chigurinchindhe",
      "v7": "Naa neede neevai undaalani thalachi", "v8": "Choosina prathiraayiki ne mokkithine"}
def sec(keys, times, shift=0):
    return [(k, times[i] + shift, times[i + 1] + shift) for i, k in enumerate(keys)]
LINES = (sec(["c1", "c2", "c3", "c4"], CH1) + sec(["c1", "c6", "c3", "c4"], CH2) +
         sec(["v1", "v2", "v3", "v4", "v5", "v6", "v7", "v8"], VER) +
         sec(["c1", "c18", "c3", "c4"], CH1, C) + sec(["c1", "c6", "c3", "c4"], CH2, C))
# whisper words (chorus 3/4 use chorus 1/2 words shifted)
W = [(w[0], w[1], w[2].strip()) for s in json.load(open(ASR)) for w in s["w"]]
def words_in(a, b, shift=0):
    return [(s + shift, e + shift, t) for s, e, t in W if a - 0.05 <= s < b - 0.05 and t]
def karaoke(text, a, b, shift_src):
    ws = words_in(a - shift_src, b - shift_src, shift_src) if shift_src else words_in(a, b)
    uw = text.split()
    if len(ws) < 2:   # proportional
        tot = sum(len(u) for u in uw); t = a; st = []
        for u in uw: st.append(t); t += (b - a) * len(u) / tot
        return st
    # char-position -> time map from whisper words; first word start = line start
    pts, c = [(0.0, a)], 0; L = sum(len(t) for _, _, t in ws)
    for i, (s, e, t) in enumerate(ws):
        if i: pts.append((c / L, s))
        c += len(t)
    pts.append((1.0, min(ws[-1][1], b)))
    def m(f):
        for (f0, t0), (f1, t1) in zip(pts, pts[1:]):
            if f <= f1: return t0 + (t1 - t0) * (f - f0) / max(f1 - f0, 1e-6)
        return pts[-1][1]
    L2 = sum(len(u) for u in uw); c = 0; st = []
    for u in uw: st.append(m(c / L2)); c += len(u)
    return st
def make_states(lang):
    """Lyric layer as a list of states (constant images): current line with k words filled + next line."""
    T = TE if lang == "te" else EN
    lines = []
    for i, (k, a, b) in enumerate(LINES):
        shift = C if a > 160 else 0
        st = karaoke(TE[k], a, b, shift)           # word times from the Telugu words
        oa, ob = out_t(a), out_t(b)
        ws = T[k].split()
        if len(ws) != len(st):                       # EN word count differs -> spread over the sung span
            span = out_t(st[-1]) + 0.5 - oa; tot = sum(len(u) for u in ws); t = oa; ost = []
            for u in ws: ost.append(t); t += span * len(u) / tot
        else:
            ost = [out_t(x) for x in st]
        lines.append((k, oa, ob, ws, ost))
    states = []; LEAD = 0.25
    for i, (k, oa, ob, ws, ost) in enumerate(lines):
        nxt = T[lines[i + 1][0]] if i + 1 < len(lines) else ""
        t0 = max(0.0, oa - LEAD)
        cuts = [t0] + [max(t0, x) for x in ost] + [ob]
        for n in range(len(ws) + 1):                 # n words filled during [cuts[n], cuts[n+1])
            if cuts[n + 1] - cuts[n] > 0.005:
                states.append({"t0": round(cuts[n], 3), "t1": round(cuts[n + 1], 3), "words": ws, "fill": n, "next": nxt})
    # first line: start at 0
    states[0]["t0"] = 0.0
    for x, y in zip(states, states[1:]): x["t1"] = y["t0"]
    states[-1]["t1"] = TOTAL
    json.dump({"lang": lang, "title": "♪ అలసేంద్ర ♪" if lang == "te" else "♪ O Alasendra ♪", "states": states},
              open(f"{OUT}/states_{lang}.json", "w"), ensure_ascii=False, indent=0)
    return states
for lang in ("te", "en"): make_states(lang)
# visuals: trims of the cinemascope area (640x268 at y=46) joined; blurred fill behind
n = len(VIS)
fc = f"[0:v]crop=640:268:0:46,setsar=1,split={n}" + "".join(f"[s{i}]" for i in range(n)) + ";"
fc += "".join(f"[s{i}]trim={a}:{b},setpts=PTS-STARTPTS,fps=30[t{i}];" for i, (a, b) in enumerate(VIS))
fc += "".join(f"[t{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0,split[m1][m2];"
fc += "[m1]crop=151:268,scale=270:480,boxblur=18:2,scale=1080:1920,eq=brightness=-0.18:saturation=1.2[bg];"
fc += "[m2]crop=476:268,scale=1080:608:flags=lanczos,unsharp=5:5:0.6[fg];"
fc += "[bg][fg]overlay=0:470,drawbox=x=0:y=466:w=1080:h=4:color=white@0.85:t=fill,drawbox=x=0:y=1078:w=1080:h=4:color=white@0.85:t=fill[base]"
af = ";".join(f"[1:a]atrim={a}:{b},asetpts=PTS-STARTPTS" + (",afade=t=in:d=0.08" if i else ",afade=t=in:d=0.3")
              + (f",afade=t=out:st={b-a-0.08:.3f}:d=0.08" if i < len(SEG) - 1 else f",afade=t=out:st={b-a-2.5:.3f}:d=2.5") + f"[a{i}]"
              for i, (a, b) in enumerate(SEG))
af += ";" + "".join(f"[a{i}]" for i in range(len(SEG))) + f"concat=n={len(SEG)}:v=0:a=1,loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]"
base = f"{OUT}/base.mp4"
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-i", SRC, "-filter_complex", fc + ";" + af,
                "-map", "[base]", "-map", "[aout]", "-t", f"{TOTAL}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
                "-c:a", "aac", "-b:a", "192k", base], check=True)
HERE = os.path.dirname(os.path.abspath(__file__))
for lang in ("te", "en"):
    d = f"{OUT}/png_{lang}"; os.makedirs(d, exist_ok=True)
    subprocess.run(["node", f"{HERE}/text_layer.js", f"{OUT}/states_{lang}.json", os.path.abspath(FONTS), d], check=True)
    # concat demuxer: one transparent PNG per state with its duration
    st = json.load(open(f"{OUT}/states_{lang}.json"))["states"]
    lst = "".join(f"file '{d}/s{i:04d}.png'\nduration {x['t1']-x['t0']:.3f}\n" for i, x in enumerate(st)) + f"file '{d}/s{len(st)-1:04d}.png'\n"
    open(f"{d}/list.txt", "w").write(lst)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", base, "-f", "concat", "-safe", "0", "-i", f"{d}/list.txt",
                    "-filter_complex", f"[1:v]fps=30,format=rgba[tx];[0:v][tx]overlay=0:0:format=auto,fade=t=in:st=0:d=0.5,fade=t=out:st={TOTAL-1.2:.2f}:d=1.2,format=yuv420p[v]",
                    "-map", "[v]", "-map", "0:a", "-t", f"{TOTAL}", "-c:v", "libx264", "-preset", "slow", "-crf", "20", "-c:a", "copy",
                    "-movflags", "+faststart", f"{OUT}/alasendra_lyrical_{lang}.mp4"], check=True)
print("total", round(TOTAL, 2))
