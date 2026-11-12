"""Pollution challan short: arrange best takes of 10 AI clips per script, cut pauses, 1.1x, 9:16 1080x1920.
Writes work/base.mov (with 4 s end screen) and work/timeline.json"""
import json, os, subprocess
import numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-fortesting/f0703b19-2505-5b8b-b72d-114eb35464cd/scratchpad/ch"
RAW, W = S + "/raw", S + "/work"
os.makedirs(W, exist_ok=True)
SP = 1.10
# (id, clip, start, end, speaker)  – best take of every script line
SEGS = [
    ("S1",  "d00", 10.40, 14.72, "N"),   # Pollution bro! mobile number update cheyinchukunnanu...
    ("S2",  "d04", 1.85, 11.12, "P"),    # Sare anna... OTP... okka nimisham... shocking news... challan undhi
    ("S3",  "d05", 1.04, 6.00, "P"),     # pending lo unte avvadhu, mundu challan kattandi, mottham 1035
    ("FB0", "d01", 0.00, 1.48, "-"),     # Navin shock face zoom
    ("FB1", "d01", 1.48, 5.37, "-"),     # flashback: riding without helmet, constable photo (no dialogue)
    ("S5",  "d02", 0.00, 9.50, "N"),     # Sir please sir...
    ("S6",  "d03", 0.30, 7.38, "N"),     # Odiyamma! ... khareedhaina photo ki  (garbled amount after it trimmed)
    ("S7",  "d05", 7.12, 9.40, "P"),     # Malli net center ki velli...
    ("S8",  "d06", 0.00, 9.20, "N"),     # Krishna bro! enti bro idhi?...
    ("S9",  "d08", 0.22, 1.24, "K"),     # Helmet fine aa bro?
    ("S10a", "d07", 0.10, 1.47, "N"),    # Avunu bro! 1035
    ("S11", "d08", 2.44, 3.33, "K"),     # Katteshanu bro!  (right after the amount)
    ("S10b", "d07", 1.50, 5.76, "N"),    # Inkosari nunchi helmet lekunda ... bodi juttu ... "Fine"
    ("S10b", "d07", 6.44, 10.02, "N"),   # ... kattalsina avasaram ledhu (repeated half removed) ... helmet pose
    ("Q", "TTS", 0.0, 0.0, "-"),         # Navin's "ee website lo pay chesaru?" has no take -> text screen + TTS voice
    ("S12", "d08", 4.40, 9.52, "K"),     # Challan website maarindhi...
    ("S13", "d09", 0.28, 9.24, "K"),     # ending
]
NOSPLIT = {"FB0", "FB1"}                       # keep the flashback shots whole (no speech inside)
# per-segment speed (default SP = 1.1x)
SPEED = {"S1": 0.9, "S2": 0.95, "S7": 0.9, "S8": 1.05, "S10a": 1.05, "S10b": 1.05, "S12": 0.9, "S13": 1.0}   # evens out the AI voices (~17.5 chars/s)
# flashback look (FB1 after the shock zoom, and the pleading scene)
GRADE = {"FB1": "eq=saturation=0.55:contrast=1.06,colorbalance=rs=0.06:bs=-0.06,vignette=PI/4.5",
         "S5": "eq=saturation=0.55:contrast=1.06,colorbalance=rs=0.06:bs=-0.06,vignette=PI/4.5"}
CROP = {}
SRC_W, SRC_H = 720, 1280
dbc = {}
def db(clip):
    if clip not in dbc:
        x, sr = sf.read(f"{RAW}/{clip}.wav"); f = sr // 100
        dbc[clip] = 20 * np.log10(np.sqrt(np.mean(x[:len(x)//f*f].reshape(-1, f) ** 2, 1)) + 1e-9)
    return dbc[clip]
def split(clip, a, b, gap=0.15, pad=0.05):
    d = db(clip); th = d.max() - 32
    i0, i1 = int(a * 100), min(int(b * 100), len(d))
    sp = d[i0:i1] > th; out, cur, i = [], a, 0
    while i < len(sp):
        if not sp[i]:
            j = i
            while j < len(sp) and not sp[j]: j += 1
            if i > 0 and j < len(sp) and (j - i) / 100 >= gap:
                x, y = (i0 + i) / 100 + pad, (i0 + j) / 100 - pad
                if x - cur >= 0.35 and b - y >= 0.35: out.append((cur, x)); cur = y
            i = j
        else: i += 1
    out.append((cur, b)); return out
pieces = [(sid, clip, p, q, spk) for sid, clip, a, b, spk in SEGS
          for p, q in ([(a, b)] if clip in ("BLACK", "TTS") or sid in NOSPLIT else split(clip, a, b))]
tl, lst, t = [], [], 0.0
zs, prev = [], None
for sid, clip, a, b, spk in pieces:      # punch in only on a jump cut inside the same clip
    zs.append((1.07 if zs[-1] == 1.0 else 1.0) if prev == clip else 1.0); prev = clip
for i, (sid, clip, a, b, spk) in enumerate(pieces):
    d = round(b - a, 3); z = zs[i]; sp = SPEED.get(sid, SP)
    if clip in ("BLACK", "TTS"):
        f = f"{W}/p{i:02d}.mov"
        if clip == "TTS":   # black screen carrying the synthesized line, 0.15 s lead-in + 0.25 s tail
            tts = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tts/q_website.wav")
            td = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", tts],
                                      capture_output=True, text=True).stdout)
            d = round((td + 0.4) * 30) / 30
            ain = ["-i", tts]; af = ["-af", f"aresample=48000,aformat=channel_layouts=stereo,adelay=150:all=1,apad,atrim=0:{d}"]
        else:
            ain = ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]; af = []
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=black:s=1080x1920:r=30", *ain, *af,
            "-t", str(d), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "pcm_s16le", f], check=True)
        tl.append({"sid": sid, "clip": clip, "a": a, "b": b, "spk": spk, "t0": round(t, 3), "t1": round(t + d, 3)})
        t += d; lst.append(f); continue
    cw, ch, x0, y0 = CROP.get(clip, (SRC_W, SRC_H, 0, 0))
    cw2, ch2 = int(cw / z) // 2 * 2, int(ch / z) // 2 * 2
    x0 += (cw - cw2) // 2; y0 += int((ch - ch2) * 0.3)
    f = f"{W}/p{i:02d}.mov"; nf = max(1, round(d / sp * 30))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", f"{RAW}/{clip}.mp4",
        "-filter_complex", f"[0:v]delogo=x=570:y=1128:w=62:h=62,crop={cw2}:{ch2}:{x0}:{y0},scale=1080:1920:flags=lanczos,unsharp=5:5:0.4,{GRADE.get(sid, 'null')},setsar=1,setpts=(PTS-STARTPTS)/{sp},fps=30[v];"
        f"[0:a]aresample=48000,afade=t=in:d=0.015,afade=t=out:st={d-0.03:.3f}:d=0.03,atempo={sp},aformat=channel_layouts=stereo,"
        f"apad,atrim=0:{nf/30:.6f}[a]",            # audio exactly as long as the video -> no a/v drift after concat
        "-map", "[v]", "-map", "[a]", "-frames:v", str(nf), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14", "-c:a", "pcm_s16le", f], check=True)
    real = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f],
                                capture_output=True, text=True).stdout)
    tl.append({"sid": sid, "clip": clip, "a": a, "b": b, "spk": spk, "t0": round(t, 3), "t1": round(t + real, 3)})
    t += real; lst.append(f)
END = 4.0
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=0x0b0b14:s=1080x1920:r=30", "-f", "lavfi",
    "-i", "anullsrc=r=48000:cl=stereo", "-t", str(END), "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
    "-c:a", "pcm_s16le", f"{W}/end.mov"], check=True)
lst.append(f"{W}/end.mov")
open(f"{W}/list.txt", "w").write("".join(f"file '{x}'\n" for x in lst))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/list.txt", "-c", "copy", f"{W}/base.mov"], check=True)
json.dump({"pieces": tl, "main_end": t, "total": t + END}, open(f"{W}/timeline.json", "w"), indent=1)
print("main", round(t, 2), "pieces", len(tl))
for p in tl: print(p)
