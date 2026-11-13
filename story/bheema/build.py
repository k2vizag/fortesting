"""Bheema (chekka shilpi) – animated moral story edited into one 9:16 Short.

usage: python3 -I build.py <work_dir>
needs in <work_dir>: raw/c01.mp4..c10.mp4, words.json (faster-whisper word times per clip),
                     sep/htdemucs/all/vocals.wav (demucs voice of all clips concatenated, 10.0267 s each)
writes: base.mov (1080x1920 30 fps, voice), data.json (overlay), sfx.json (soft UI sfx), cues.txt (comedy sfx)
"""
import json, os, subprocess, sys
import numpy as np
import soundfile as sf

W = sys.argv[1]
SPEED = 1.10
CLIP = 10.026667                      # every source clip is exactly this long
CARD = 2.8                            # moral card (frozen last frame under it)
END = 4.0                             # end screen

# source trims (seconds inside each clip): keep a short establishing beat before the first word
TRIM = {1: (0.8, 9.6), 2: (1.8, 9.6), 3: (0.4, 9.3), 4: (0.9, 10.0), 5: (0.2, 9.6),
        6: (1.0, 9.8), 7: (0.9, 9.9), 8: (1.6, 9.8), 9: (0.0, 9.8), 10: (0.0, 9.95)}
ZOOM = {2, 4, 6, 8, 10}                # gentle 4 % push-in on alternate clips

# ---------------------------------------------------------------- timeline
OFF, t = {}, 0.0
for c in range(1, 11):
    OFF[c] = t
    t += (TRIM[c][1] - TRIM[c][0]) / SPEED
STORY_END = t
MAIN_END = STORY_END + CARD
TOTAL = MAIN_END + END
def out(c, s):                         # source time in clip c -> output time
    return OFF[c] + (s - TRIM[c][0]) / SPEED

# ---------------------------------------------------------------- base video
def build_base():
    parts = []
    for c in range(1, 11):
        a, b = TRIM[c]
        vf = "scale=1188:2112:flags=lanczos,unsharp=5:5:0.6," + (
            "fps=30,zoompan=z='1+0.04*on/({n})':d=1:s=1080x1920:fps=30".format(n=int((b - a) / SPEED * 30))
            if c in ZOOM else "crop=1080:1920,fps=30")
        p = f"{W}/seg{c:02d}.mp4"
        # -ss/-t BEFORE -i (input options) so nothing past the cut point is read back in
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a}", "-t", f"{b - a}", "-i", f"{W}/raw/c{c:02d}.mp4",
                        "-filter_complex", f"[0:v]setpts=(PTS-STARTPTS)/{SPEED},{vf},format=yuv420p[v];"
                        f"[0:a]asetpts=PTS-STARTPTS,atempo={SPEED},loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,apad[a]",
                        "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-crf", "15", "-preset", "medium",
                        "-c:a", "pcm_s16le", "-t", f"{(b - a) / SPEED:.3f}", p], check=True)
        parts.append(p)
    # moral card + end screen sit on a frozen last frame with silence
    lst = f"{W}/segs.txt"; open(lst, "w").write("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-vf", f"tpad=stop_mode=clone:stop_duration={CARD + END}", "-af", f"apad=pad_dur={CARD + END}",
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-c:a", "pcm_s16le", "-t", f"{TOTAL:.3f}",
                    f"{W}/base.mov"], check=True)

# ---------------------------------------------------------------- captions (English letters)
words = json.load(open(f"{W}/words.json"))
voc, sr = sf.read(f"{W}/sep/htdemucs/all/vocals.wav")
voc = voc.mean(1) if voc.ndim > 1 else voc
hop = int(sr * 0.01)
vdb = np.array([20 * np.log10(np.sqrt((voc[i:i + hop] ** 2).mean()) + 1e-9) for i in range(0, len(voc), hop)])
def onset(c, s, e):
    """first voiced 10 ms frame at/after whisper start s (whisper starts often swallow the pause before a word)."""
    base = (c - 1) * CLIP
    i0, i1 = int((base + s - 0.05) * 100), int((base + e) * 100)
    idx = np.where(vdb[i0:i1] > -38)[0]
    return s if len(idx) == 0 else max(s - 0.05, (i0 + idx[0]) / 100 - base - 0.03)

W_ = {int(k): [w for sg in v["segs"] for w in sg["w"]] for k, v in words.items()}
# (clip, first word index, last word index, [(class, text), ...])  cw = white, ch = big gradient key word, cs = small italic
CAPS = [
    (1, 0, 2, [("cw", "Nee battalu"), ("ch", "chudu")]), (1, 3, 4, [("cw", "Nee"), ("ch", "pedarikam")]),
    (1, 5, 6, [("cw", "chusthene"), ("ch", "navvosthondi!")]), (1, 7, 8, [("cw", "Ilanti vaadiki")]), (1, 9, 10, [("cw", "ee"), ("ch", "pani?")]),
    (2, 0, 1, [("cw", "Ee chinna"), ("ch", "chekka bomma")]), (2, 2, 4, [("cw", "tho nuvvu potilo"), ("ch", "gelusthava?")]),
    (2, 5, 7, [("cw", "Naa daggara"), ("ch", "dabbu")]), (2, 8, 9, [("cw", "lekapovachu kaani")]),
    (2, 10, 12, [("cw", "naaku"), ("ch", "prathibha"), ("cs", "undi!")]),
    (3, 0, 1, [("ch", "Bheema anna")]), (3, 2, 3, [("cw", "nuvvu chekkatho")]), (3, 4, 6, [("cw", "intha andamaina"), ("ch", "bommalu")]),
    (3, 7, 9, [("cw", "ela tayaru chesthavu?")]), (3, 10, 12, [("ch", "Manasu"), ("cw", "petti pani chesthe")]),
    (3, 13, 14, [("cw", "chekkalo kuda")]), (3, 15, 17, [("ch", "andanni"), ("cw", "chudagalam Meena")]),
    (4, 0, 2, [("cw", "Adavi kala"), ("ch", "potiki")]), (4, 3, 3, [("ch", "swagatham!")]), (4, 4, 4, [("cw", "Vijethaku")]),
    (4, 5, 6, [("ch", "1 laksha"), ("cw", "rupayala bahumathi!")]), (4, 7, 8, [("cw", "Ee potilo nannu")]),
    (4, 9, 9, [("ch", "odinchadam")]), (4, 10, 12, [("cw", "evari valla"), ("ch", "kaadu!")]),
    (5, 0, 2, [("cw", "Ee"), ("ch", "shilpamlo")]), (5, 3, 4, [("cw", "naa"), ("ch", "kashtam")]), (5, 5, 6, [("cw", "maatrame kaadu")]),
    (5, 7, 10, [("cw", "naa"), ("ch", "manasu"), ("cs", "kuda undi")]),
    (6, 0, 0, [("ch", "Ayyo!")]), (6, 1, 3, [("cw", "Evaru"), ("ch", "ila chesaru?")]),
    (7, 0, 2, [("ch", "Bheema anna")]), (7, 3, 4, [("cw", "odipoyanani"), ("ch", "anukoku")]), (7, 5, 6, [("cw", "nee"), ("ch", "prathibha")]),
    (7, 7, 9, [("cw", "inka neethone undi")]), (7, 10, 12, [("cw", "Nenu venakki"), ("ch", "thaggaanu")]),
    (7, 13, 16, [("cw", "Meena, naa"), ("ch", "kashtamthone")]), (7, 17, 17, [("ch", "gelusthanu!")]),
    (8, 0, 0, [("ch", "Adbhutham!")]), (8, 1, 2, [("cw", "intha"), ("ch", "bhavodvegamga")]), (8, 3, 4, [("cw", "chekkina shilpanni")]),
    (8, 5, 7, [("cw", "nenu eppudu"), ("ch", "choodaledhu!")]), (8, 8, 10, [("cw", "Idhi Bheema"), ("ch", "chesaada?")]),
    (8, 11, 12, [("ch", "Nammaleka"), ("cw", "pothunnanu!")]),
    (9, 0, 1, [("cw", "Ee yedadi"), ("ch", "vijetha")]), (9, 2, 3, [("cw", "mana"), ("ch", "Bheema!")]), (9, 4, 5, [("cw", "athani"), ("ch", "prathibhaku")]),
    (9, 6, 8, [("cw", "idhe nijamaina"), ("ch", "gurthimpu")]), (9, 9, 11, [("cw", "Ee gelupu naa"), ("ch", "kashtaniki")]),
    (9, 12, 14, [("cw", "nannu nammina"), ("ch", "Meenaku")]), (9, 15, 15, [("ch", "ankitham!")]),
    (10, 0, 2, [("cw", "Bheema, mammalni"), ("ch", "kshaminchu")]), (10, 3, 4, [("cw", "nee"), ("ch", "prathibhanu")]),
    (10, 5, 8, [("cw", "memu thakkuvaga"), ("ch", "anchana vesam")]), (10, 9, 10, [("cw", "Manishi"), ("ch", "viluva")]),
    (10, 11, 13, [("cw", "athani"), ("ch", "dabbulo kaadu")]), (10, 14, 15, [("cw", "athani"), ("ch", "prathibhalo")]),
    (10, 16, 18, [("ch", "kashtamlo"), ("cw", "untundhi!")]),
]
caps = []
for c, i0, i1, lines in CAPS:
    ws = W_[c]; s = onset(c, ws[i0][0], ws[i0][1]); e = ws[i1][1]
    caps.append({"a": round(out(c, s), 3), "b": round(out(c, e) + 0.12, 3), "lines": [{"cls": k, "t": v} for k, v in lines]})
for k in range(len(caps) - 1):           # never overlap; hold until the next caption if the gap is short
    nx = caps[k + 1]["a"]
    caps[k]["b"] = round(nx if nx - caps[k]["b"] < 0.35 else min(caps[k]["b"], nx), 3)
    caps[k]["b"] = min(caps[k]["b"], nx)
CAPT = {(c, i0): caps[k] for k, (c, i0, _, _) in enumerate(CAPS)}

# ---------------------------------------------------------------- stickers (key words) and the moral card
def stk(c, i0, icon, color, label, side, dur=2.2):
    a = CAPT[(c, i0)]["a"]; return {"a": a, "b": round(min(a + dur, OFF[c + 1] if c < 10 else STORY_END), 3), "icon": icon, "color": color, "label": label, "side": side, "y": 1290}
stickers = [stk(2, 5, "rupee", "red", "No money", "l"), stk(2, 10, "star", "yellow", "Talent", "r"),
            stk(3, 10, "heart", "pink", "Manasu", "l"), stk(4, 5, "trophy", "orange", "Rs 1 Lakh", "r"),
            stk(5, 3, "hammer", "orange", "Kashtam", "l"), stk(7, 5, "star", "yellow", "Prathibha", "r"),
            stk(9, 0, "trophy", "yellow", "Winner", "r"), stk(10, 9, "heart", "pink", "Viluva", "l")]
cards = [{"a": round(STORY_END, 3), "b": round(MAIN_END, 3), "theme": "white", "type": "profile", "color": "orange", "icon": "heart",
          "kicker": "KATHA LO NEETHI", "title": "Manishi viluva", "pill": "Prathibha + Kashtam", "pillAt": 0.7,
          "desc": "Dabbulo kaadu &mdash; prathibhalo, kashtamlo untundhi!", "tiles": ["star", "hammer", "trophy"]}]
data = {"total": round(TOTAL, 3), "main_end": round(MAIN_END, 3), "title": [], "board": None,  # no title bars / call board (user request)
        "cards": cards, "numbers": [], "stickers": stickers, "captions": caps}

# ---------------------------------------------------------------- soft UI sfx (synthesised by audio.py) and comedy cues
sfx = [{"t": s["a"], "k": "pop"} for s in stickers]
sfx += [{"t": STORY_END, "k": "whoosh"}, {"t": STORY_END + 0.05, "k": "impact"}, {"t": STORY_END + 0.7, "k": "chime"}, {"t": MAIN_END, "k": "whoosh"}]
sfx += [{"t": round(MAIN_END + x, 3), "k": "click"} for x in (1.45, 2.35)]
cues = [  # time  clip  gain   (comedy pack from the reference video)
    (CAPT[(1, 5)]["b"] - 0.05, "comedy_ref1/03_chicken_cluck", -7, "mocking 'navvosthondi!'"),
    (CAPT[(6, 0)]["a"], "comedy_ref1/17_deep_thud", -6, "'Ayyo!' – the statue is broken"),
    (CAPT[(8, 0)]["a"] - 0.1, "comedy_ref1/02_reaction_music_sting", -6, "'Adbhutham!' – judge amazed"),
    (CAPT[(8, 11)]["a"], "comedy_ref1/05_ding_boing", -6, "fox: 'nammaleka pothunnanu!'"),
]
json.dump(data, open(f"{W}/data.json", "w"), ensure_ascii=False, indent=1)
json.dump(sfx, open(f"{W}/sfx.json", "w"), indent=1)
open(f"{W}/cues.txt", "w").write("".join(f"{t:.2f} {c} {g}   # {m}\n" for t, c, g, m in cues))
print(f"story {STORY_END:.2f}s  card -> {MAIN_END:.2f}s  end -> {TOTAL:.2f}s   captions {len(caps)}  stickers {len(stickers)}")
if "--no-video" not in sys.argv:
    build_base()
    print("base.mov written")
