"""Soft music bed + soft SFX + cleaned AI voice -> work/mix.wav (-14 LUFS). Other clips' audio stays muted."""
import json, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from segs import W

SR = 48000
rng = np.random.default_rng(7)
D = json.load(open(f"{W}/data.json"))
T = D["total"]
N = int(T * SR) + SR


def sine(n, f):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return np.sin(2 * np.pi * np.cumsum(f) / SR)


def soft(n, a, r):
    t = np.arange(n) / SR
    att = np.where(t < a, 0.5 - 0.5 * np.cos(np.pi * t / max(a, 1e-4)), 1.0)
    return att * np.exp(-np.maximum(t - a, 0) / r)


def smooth(y, k=8):
    return np.convolve(y, np.ones(k) / k, "same")


def mk(k):
    if k == "pop":    # soft bubble pop (stickers)
        n = int(0.10 * SR); return smooth(sine(n, np.geomspace(300, 680, n)) * soft(n, 0.003, 0.025)) * 0.16
    if k == "tap":    # soft tap (captions)
        n = int(0.09 * SR); return smooth(sine(n, np.geomspace(1170, 900, n)) * soft(n, 0.002, 0.018)) * 0.05
    if k == "cut":    # soft low bloop on shot change
        n = int(0.22 * SR); return smooth(sine(n, np.geomspace(220, 520, n)) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, 20) * 0.05
    if k == "end":    # wooden pluck pair for the end screen
        def pl(f):
            n = int(0.6 * SR); return smooth(sine(n, f) * soft(n, 0.003, 0.22) + 0.25 * sine(n, 4 * f) * soft(n, 0.002, 0.04)) * 0.10
        a, b = pl(523.25), pl(659.25); d = int(0.08 * SR); a[d:] += b[:-d]; return a
    raise KeyError(k)


fx = np.zeros(N)
for ev in D["sfx"]:
    y = mk(ev["k"]); i = int(ev["t"] * SR); y = y[:N - i]; fx[i:i + len(y)] += y

# cheerful soft music bed, 96 bpm, C - G - Am - F
bpm = 96; beat = 60 / bpm; bar = 4 * beat
chords = [[48, 55, 60, 64], [43, 55, 59, 62], [45, 57, 60, 64], [41, 57, 60, 65]]
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
env = lambda n, a, d: np.minimum(1, np.arange(n) / SR / a) * np.exp(-np.arange(n) / SR / d)
mus = np.zeros(N); t = 0.0; ci = 0
while t < T:
    n = int(bar * SR) + SR; seg = np.zeros(n); ch = chords[ci % 4]
    for m in ch[1:]:
        f = hz(m); seg += (sine(n, f) + 0.3 * sine(n, 2 * f)) * env(n, 0.02, 1.4) * 0.045
    seg += sine(n, hz(ch[0] - 12 + 12)) * env(n, 0.01, 0.8) * 0.11
    for b in range(8):  # light marimba arpeggio on eighths
        o = int(b * beat / 2 * SR); m = ch[1:][b % 3] + 12; kn = int(0.3 * SR)
        seg[o:o + kn] += sine(kn, hz(m)) * env(kn, 0.003, 0.12) * 0.035
        if b % 4 == 0:
            seg[o:o + kn] += sine(kn, np.geomspace(120, 45, kn)) * env(kn, 0.002, 0.07) * 0.22
    i = int(t * SR); seg = seg[:N - i]; mus[i:i + len(seg)] += seg
    t += bar; ci += 1
mus = smooth(mus, 6)
fade = int(1.5 * SR); e = int(T * SR)
mus[:fade] *= np.linspace(0, 1, fade); mus[e - fade:e] *= np.linspace(1, 0, fade); mus[e:] = 0
sf.write(f"{W}/fx.wav", fx.astype(np.float32), SR, subtype="FLOAT")
sf.write(f"{W}/music.wav", mus.astype(np.float32), SR, subtype="FLOAT")

fc = ("[0:a]loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,asplit=2[v][vs];"
      "[1:a]volume=1.7[m];[m][vs]sidechaincompress=threshold=0.02:ratio=10:attack=20:release=400[md];"
      "[2:a]volume=0.8[f];[v][md][f]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.9[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/voice.wav", "-i", f"{W}/music.wav", "-i", f"{W}/fx.wav",
                "-filter_complex", fc, "-map", "[out]", "-ac", "2", "-c:a", "pcm_s16le", f"{W}/mix_raw.wav"], check=True)
# set the whole mix to -14 LUFS (measured gain + limiter)
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", f"{W}/mix_raw.wav", "-af", "ebur128", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
I = float(r.split("Integrated loudness:")[1].split("I:")[1].split("LUFS")[0])
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/mix_raw.wav", "-af",
                f"volume={-14 - I + 0.3}dB,alimiter=limit=0.84:level=false", "-c:a", "pcm_s16le", f"{W}/mix.wav"], check=True)
print("mixed, was", I, "LUFS")
