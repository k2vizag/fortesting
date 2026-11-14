"""Bheema story as TWO 45 s Shorts, with movie-style music breaks (fused double-exposure shots).

usage: python3 -I build2.py <work_dir> [--no-video]
reads  <work_dir>/raw/c01..c10.mp4 (sparkle removed), words.json, sep/htdemucs/all/vocals.wav
writes <work_dir>/part1/, part2/: base.mov, data.json, sfx.json, cues.txt, breaks.json
Captions (CAPS) are reused from build.py.
"""
import ast, json, os, re, subprocess, sys
import numpy as np
import soundfile as sf

W = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
SPEED, CLIP, PART_LEN = 1.10, 10.026667, 45.0
CAPS = ast.literal_eval(re.search(r"\nCAPS = (\[.*?\n\])\n", open(f"{HERE}/build.py").read(), re.S).group(1))

# ---- parts: ("clip", n, src_a, src_b) or ("break", dur, (clip, src_start), (clip, src_start), [cinematic texts])
#      a break plays both shots at half speed, fused as a double exposure, letterboxed, with the music swelling
PARTS = {
    1: dict(items=[("clip", 1, 2.30, 9.40), ("clip", 2, 2.35, 9.30), ("clip", 3, 0.45, 9.05),
                   ("break", 3.2, (5, 2.0), (3, 6.0), []),                                  # Bheema's talent: carving + Meena's smile
                   ("clip", 4, 1.45, 10.0), ("clip", 5, 1.20, 8.00), ("clip", 6, 5.00, 9.55)],
            card=0.0, end_text="Part 2 lo chudandi! &#128073;", sticker_ids=range(0, 5)),
    2: dict(items=[("break", 4.0, (5, 7.6), (6, 7.0), [("PART 2", 150, 820, False), ("Bheema Chekka Shilpi", 54, 1010, True)]),
                   ("clip", 7, 1.30, 9.80), ("clip", 8, 2.30, 9.75), ("clip", 9, 0.00, 9.70),
                   ("break", 3.4, (9, 6.0), (4, 0.2), []),                                  # the win: trophy + festival crowd
                   ("clip", 10, 0.00, 8.55)],
            card=2.6, end_text=None, sticker_ids=range(5, 8)),
}
ZOOM = {2, 4, 6, 8, 10}

# ---- caption timing helpers (same as build.py)
words = json.load(open(f"{W}/words.json"))
WD = {int(k): [w for sg in v["segs"] for w in sg["w"]] for k, v in words.items()}
voc, sr = sf.read(f"{W}/sep/htdemucs/all/vocals.wav"); voc = voc.mean(1) if voc.ndim > 1 else voc
hop = int(sr * 0.01)
vdb = np.array([20 * np.log10(np.sqrt((voc[i:i + hop] ** 2).mean()) + 1e-9) for i in range(0, len(voc), hop)])
def onset(c, s, e):
    base = (c - 1) * CLIP; i0, i1 = int((base + s - 0.05) * 100), int((base + e) * 100)
    idx = np.where(vdb[i0:i1] > -38)[0]
    return s if len(idx) == 0 else max(s - 0.05, (i0 + idx[0]) / 100 - base - 0.03)

STK = [  # (clip, first caption word, icon, color, label, side)
    (2, 5, "rupee", "red", "No money", "l"), (2, 10, "star", "yellow", "Talent", "r"), (3, 10, "heart", "pink", "Manasu", "l"),
    (4, 5, "trophy", "orange", "Rs 1 Lakh", "r"), (5, 3, "hammer", "orange", "Kashtam", "l"),
    (7, 5, "star", "yellow", "Prathibha", "r"), (9, 0, "trophy", "yellow", "Winner", "r"), (10, 9, "heart", "pink", "Viluva", "l")]
COMEDY = {1: [((1, 5), "b", -0.05, "comedy_ref1/03_chicken_cluck", -9, "mocking 'navvosthondi!'"),
              ((6, 0), "a", 0.0, "comedy_ref1/17_deep_thud", -3, "'Ayyo!' – the statue is broken")],
          2: [((8, 0), "a", -0.1, "comedy_ref1/02_reaction_music_sting", -1, "'Adbhutham!' – judge amazed"),
              ((8, 11), "a", 0.0, "comedy_ref1/05_ding_boing", -4, "fox: 'nammaleka pothunnanu!'")]}

def run(cmd): subprocess.run(cmd, check=True)

def clip_seg(c, a, b, out):
    d = (b - a) / SPEED
    vf = ("fps=30,zoompan=z='1+0.04*on/({n})':d=1:s=1080x1920:fps=30".format(n=int(d * 30)) if c in ZOOM else "crop=1080:1920,fps=30")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b - a}", "-i", f"{W}/raw/c{c:02d}.mp4",   # input-side -ss/-t
         "-filter_complex", f"[0:v]setpts=(PTS-STARTPTS)/{SPEED},scale=1188:2112:flags=lanczos,unsharp=5:5:0.6,{vf},format=yuv420p[v];"
         f"[0:a]asetpts=PTS-STARTPTS,atempo={SPEED},loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,apad[a]",
         "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-c:a", "pcm_s16le", "-t", f"{d:.3f}", out])
    return d

def break_seg(d, A, B, out):
    """two shots at half speed, B fades in as a screen-blend double exposure; letterbox, warm grade, dips to black."""
    src = d * 0.5 + 0.05; n = int(d * 30)
    lay = lambda i, z0, z1: (f"[{i}:v]setpts=(PTS-STARTPTS)*2,fps=30,scale=1188:2112:flags=lanczos,"
                             f"zoompan=z='{z0}+({z1}-{z0})*on/{n}':d=1:s=1080x1920:fps=30,format=gbrp[l{i}];")
    fused = (f"[l0][l1]blend=all_expr='A+(255-(255-A)*(255-B)/255-A)*0.8*min(1,T/{d * 0.45:.2f})',format=yuv420p,"
             "eq=contrast=1.08:saturation=0.92:gamma=0.97,colorbalance=rs=0.06:gs=0.02:bs=-0.06:rm=0.04:bm=-0.04,vignette=PI/4.5,"
             "drawbox=x=0:y=0:w=iw:h=230:color=black:t=fill,drawbox=x=0:y=ih-230:w=iw:h=230:color=black:t=fill,"
             f"fade=t=in:st=0:d=0.35,fade=t=out:st={d - 0.35:.2f}:d=0.35[v]")
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{A[1]}", "-t", f"{src}", "-i", f"{W}/raw/c{A[0]:02d}.mp4",
         "-ss", f"{B[1]}", "-t", f"{src}", "-i", f"{W}/raw/c{B[0]:02d}.mp4", "-f", "lavfi", "-t", f"{d}", "-i", "anullsrc=r=48000:cl=stereo",
         "-filter_complex", lay(0, 1.0, 1.08) + lay(1, 1.12, 1.02) + fused,
         "-map", "[v]", "-map", "2:a", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-c:a", "pcm_s16le", "-t", f"{d:.3f}", out])
    return d

for pn, P in PARTS.items():
    PW = f"{W}/part{pn}"; os.makedirs(PW, exist_ok=True)
    t, segs, OFF, breaks = 0.0, [], {}, []
    for k, it in enumerate(P["items"]):
        if it[0] == "clip":
            _, c, a, b = it; d = (b - a) / SPEED; OFF[c] = (t, a, b)
        else:
            d = it[1]; breaks.append((t, t + d, it))
        segs.append((t, d, it)); t += d
    story_end = t; main_end = story_end + P["card"]; end = PART_LEN - main_end
    assert 2.8 <= end <= 4.5, f"part {pn}: end screen would be {end:.2f}s – adjust trims"
    def out(c, s): t0, a, _ = OFF[c]; return t0 + (s - a) / SPEED
    # captions of this part's clips
    caps, CAPT = [], {}
    for c, i0, i1, lines in CAPS:
        if c not in OFF: continue
        ws = WD[c]; s = onset(c, ws[i0][0], ws[i0][1]); e = ws[i1][1]
        cp = {"a": round(out(c, s), 3), "b": round(out(c, e) + 0.12, 3), "lines": [{"cls": k, "t": v} for k, v in lines]}
        caps.append(cp); CAPT[(c, i0)] = cp
    for k in range(len(caps) - 1):
        nx = caps[k + 1]["a"]; caps[k]["b"] = round(nx if nx - caps[k]["b"] < 0.35 else min(caps[k]["b"], nx), 3)
    seg_end = {c: OFF[c][0] + (OFF[c][2] - OFF[c][1]) / SPEED for c in OFF}
    stickers = []
    for c, i0, icon, color, label, side in STK:
        if c in OFF and (c, i0) in CAPT:
            a = CAPT[(c, i0)]["a"]; stickers.append({"a": a, "b": round(min(a + 2.2, seg_end[c]), 3), "icon": icon, "color": color, "label": label, "side": side, "y": 1290})
    texts = []
    for b0, b1, it in breaks:
        for txt, size, y, sub in it[4]:
            texts.append({"a": round(b0 + (0.35 if not sub else 0.8), 3), "b": round(b1 - 0.25, 3), "t": txt, "size": size, "y": y, "sub": sub})
    cards = []
    if P["card"]:
        cards = [{"a": round(story_end, 3), "b": round(main_end, 3), "theme": "white", "type": "profile", "color": "orange", "icon": "heart",
                  "kicker": "KATHA LO NEETHI", "title": "Manishi viluva", "pill": "Prathibha + Kashtam", "pillAt": 0.6,
                  "desc": "Dabbulo kaadu &mdash; prathibhalo, kashtamlo untundhi!", "tiles": ["star", "hammer", "trophy"]}]
    data = {"total": round(PART_LEN, 3), "main_end": round(main_end, 3), "title": [], "board": None, "end_text": P["end_text"],
            "cards": cards, "numbers": [], "stickers": stickers, "captions": caps, "texts": texts}
    sfx = [{"t": s["a"], "k": "pop"} for s in stickers]
    if P["card"]: sfx += [{"t": story_end, "k": "whoosh"}, {"t": story_end + 0.05, "k": "impact"}, {"t": story_end + 0.6, "k": "chime"}]
    sfx += [{"t": main_end, "k": "whoosh"}] + [{"t": round(main_end + x, 3), "k": "click"} for x in (1.45, 2.35)]
    cues = [(CAPT[key][ab] + dt, clip, g, note) for key, ab, dt, clip, g, note in COMEDY[pn]]
    json.dump(data, open(f"{PW}/data.json", "w"), ensure_ascii=False, indent=1)
    json.dump(sfx, open(f"{PW}/sfx.json", "w"), indent=1)
    json.dump([[round(b0, 3), round(b1, 3)] for b0, b1, _ in breaks], open(f"{PW}/breaks.json", "w"))
    open(f"{PW}/cues.txt", "w").write(f"# Bheema story part {pn} – comedy SFX\n" + "".join(f"{t:.2f} {c} {g}   # {m}\n" for t, c, g, m in cues))
    print(f"part {pn}: story {story_end:.2f}s  card {P['card']}  end screen {end:.2f}s  captions {len(caps)}  stickers {len(stickers)}  breaks {[(round(a,2), round(b,2)) for a, b, _ in breaks]}")
    if "--no-video" in sys.argv: continue
    files = []
    for k, (t0, d, it) in enumerate(segs):
        f = f"{PW}/seg{k:02d}.mp4"
        clip_seg(it[1], it[2], it[3], f) if it[0] == "clip" else break_seg(it[1], it[2], it[3], f)
        files.append(f)
    open(f"{PW}/segs.txt", "w").write("".join(f"file '{f}'\n" for f in files))
    tail = PART_LEN - story_end
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{PW}/segs.txt", "-vf", f"tpad=stop_mode=clone:stop_duration={tail + 0.5}",
         "-af", f"apad=pad_dur={tail + 0.5}", "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-c:a", "pcm_s16le", "-t", f"{PART_LEN:.3f}", f"{PW}/base.mov"])
    print(f"part {pn}: base.mov written")
