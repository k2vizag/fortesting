"""Synthesize soft SFX + lo-fi music bed and mix with the voice. usage: audio.py <work_dir> -> <work_dir>/mix.wav
(copied from insurance/v2/audio2.py; only the work-dir argument differs)"""
import json, subprocess, sys
import numpy as np, soundfile as sf

W = sys.argv[1]   # work dir with base.mov, data.json, sfx.json
SR = 48000
rng = np.random.default_rng(7)
T = json.load(open(f"{W}/data.json"))["total"]
N = int(T * SR) + SR

def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)

def bandnoise(n, f0, f1, q=6.0):
    """noise through a swept resonant band-pass (state-variable filter)."""
    x = rng.standard_normal(n)
    f = np.geomspace(f0, f1, n)
    y = np.zeros(n); lp = bp = 0.0
    for i in range(n):
        F = 2 * np.sin(np.pi * f[i] / SR)
        hp = x[i] - lp - bp / q
        bp += F * hp; lp += F * bp
        y[i] = bp
    return y / (np.abs(y).max() + 1e-9)

def sine(n, f, ph=0):
    f = np.broadcast_to(np.asarray(f, float), (n,))
    return np.sin(2 * np.pi * np.cumsum(f) / SR + ph)

def lowpass(y, fc):
    """one-pole low-pass, run twice for a gentle 12 dB/oct roll-off."""
    a = np.exp(-2 * np.pi * fc / SR)
    for _ in range(2):
        out = np.empty_like(y); z = 0.0
        for i in range(len(y)):
            z = (1 - a) * y[i] + a * z; out[i] = z
        y = out
    return y

def soft(n, a, r):
    """smooth attack (raised cosine) + exponential release."""
    t = np.arange(n) / SR
    att = np.where(t < a, 0.5 - 0.5 * np.cos(np.pi * t / max(a, 1e-4)), 1.0)
    return att * np.exp(-np.maximum(t - a, 0) / r)

def tap(f=900, g=0.10):
    n = int(0.09 * SR)
    y = sine(n, np.geomspace(f * 1.3, f, n)) * soft(n, 0.002, 0.018)
    return lowpass(y, 2500) * g

def pluck(f=523.25, g=0.12, d=0.22):
    """soft wooden marimba-like pluck (no metallic partials)."""
    n = int(0.6 * SR)
    y = sine(n, f) * soft(n, 0.003, d) + 0.25 * sine(n, 4 * f) * soft(n, 0.002, d / 6)
    return lowpass(y, 3000) * g

def mk(k):
    if k == "whoosh":            # card in: soft rising bloop
        n = int(0.22 * SR)
        y = sine(n, np.geomspace(220, 620, n)) * np.sin(np.linspace(0, np.pi, n)) ** 1.5
        return lowpass(y, 1800) * 0.07
    if k == "impact":            # card in: deep soft thump, no noise
        n = int(0.5 * SR)
        y = sine(n, np.geomspace(85, 42, n)) * soft(n, 0.004, 0.12)
        return lowpass(y, 400) * 0.22
    if k == "whoosh_out":
        return tap(500, 0.05)
    if k == "swish":              # big number in
        return tap(420, 0.12)
    if k == "pop":                # sticker: soft bubble pop
        n = int(0.10 * SR)
        y = sine(n, np.geomspace(300, 680, n)) * soft(n, 0.003, 0.025)
        return lowpass(y, 2200) * 0.16
    if k in ("tick", "click", "shutter"):
        return tap(900, 0.09)
    if k == "tick_soft":
        return tap(1100, 0.035)
    if k == "key":
        n = int(0.025 * SR)
        y = rng.standard_normal(n) * soft(n, 0.0005, 0.003)
        return lowpass(y, 1800) * rng.uniform(0.05, 0.09)
    if k == "ding":               # number settles
        return pluck(392.0, 0.10)
    if k == "chime":              # badge / pill: two soft plucks
        a = pluck(523.25, 0.10); b = pluck(659.25, 0.09)
        d = int(0.08 * SR); y = a.copy(); y[d:] += b[:-d]; return y
    if k == "coin":               # price steps
        return pluck(587.33, 0.10, 0.16)
    if k == "rise":
        return np.zeros(10)
    raise KeyError(k)

cache = {}
fx = np.zeros((N, 2))
for ev in json.load(open(f"{W}/sfx.json")):
    k = ev["k"]
    if k not in cache or k in ("key",):
        cache[k] = mk(k)
    y = cache[k]
    i = int(max(0, ev["t"]) * SR)
    if i >= N: continue
    y = y[:N - i]
    pan = rng.uniform(-0.25, 0.25) if k in ("pop", "key", "tick") else 0
    fx[i:i+len(y), 0] += y * (1 - pan); fx[i:i+len(y), 1] += y * (1 + pan)

# ---- music bed: soft lo-fi, 84 bpm, Am7 - Fmaj7 - C - G
bpm = 84; beat = 60 / bpm; bar = 4 * beat
chords = [[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64], [55, 59, 62, 67]]
mus = np.zeros(N)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
t = 0.0; ci = 0
while t < T:
    n = int(bar * SR) + SR
    seg = np.zeros(n)
    for m in chords[ci % 4]:
        f = hz(m)
        tone = (sine(n, f) + 0.35 * sine(n, 2 * f) + 0.12 * sine(n, 3 * f)) * env(n, 0.02, 1.6)
        seg += tone * 0.05
    bass = sine(n, hz(chords[ci % 4][0] - 12)) * env(n, 0.01, 0.9) * 0.12
    seg += bass
    for b in range(4):  # soft kick on 1 & 3, hat on offbeats
        o = int(b * beat * SR)
        if b % 2 == 0:
            kn = int(0.25 * SR); seg[o:o+kn] += sine(kn, np.geomspace(120, 45, kn)) * env(kn, 0.002, 0.08) * 0.25
        ho = o + int(beat / 2 * SR); hn = int(0.05 * SR)
        seg[ho:ho+hn] += rng.standard_normal(hn) * env(hn, 0.0005, 0.01) * 0.04
    i = int(t * SR); seg = seg[:N - i]; mus[i:i+len(seg)] += seg
    t += bar; ci += 1
# lowpass-ish smoothing
k = np.ones(6) / 6; mus = np.convolve(mus, k, "same")
fade = int(1.5 * SR); mus[:fade] *= np.linspace(0, 1, fade); mus[int(T * SR) - fade:int(T * SR)] *= np.linspace(1, 0, fade); mus[int(T * SR):] = 0
sf.write(f"{W}/fx.wav", fx.astype(np.float32), SR, subtype="FLOAT")
sf.write(f"{W}/music.wav", np.stack([mus, mus], 1).astype(np.float32), SR, subtype="FLOAT")

# ---- mix: voice (loudnorm) + music ducked under voice + sfx
fc = ("[0:a]loudnorm=I=-15:TP=-1.5:LRA=9,aresample=48000,asplit=2[v][vs];"
      "[1:a]volume=0.42[m];[m][vs]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
      "[2:a]volume=0.75[f];[v][md][f]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/base.mov", "-i", f"{W}/music.wav", "-i", f"{W}/fx.wav",
                "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", f"{W}/mix.wav"], check=True)
print("mixed", W)
