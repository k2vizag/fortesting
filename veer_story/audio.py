"""Veer story audio: original clip audio (dialogue + music) + soft sticker pops + soft music bed under the end screen, -14 LUFS."""
import json, subprocess
import numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad"
W = S + "/work"; SR = 48000; END = 4.0
D = json.load(open(f"{W}/data.json")); T = D["total"]; ME = D["main_end"]; N = int(T * SR) + SR
rng = np.random.default_rng(7)
def sine(n, f): f = np.broadcast_to(np.asarray(f, float), (n,)); return np.sin(2 * np.pi * np.cumsum(f) / SR)
def soft(n, a, r):
    t = np.arange(n) / SR
    return np.where(t < a, 0.5 - 0.5 * np.cos(np.pi * t / max(a, 1e-4)), 1.0) * np.exp(-np.maximum(t - a, 0) / r)
def lp(y, fc):
    a = np.exp(-2 * np.pi * fc / SR); out = np.empty_like(y); z = 0.0
    for i in range(len(y)): z = (1 - a) * y[i] + a * z; out[i] = z
    return out
def mk(k):
    if k == "pop":     n = int(.10 * SR); return lp(sine(n, np.geomspace(300, 680, n)) * soft(n, .003, .025), 2200) * .16
    if k == "whoosh":  n = int(.22 * SR); return lp(sine(n, np.geomspace(220, 620, n)) * np.sin(np.linspace(0, np.pi, n)) ** 1.5, 1800) * .07
    if k == "impact":  n = int(.5 * SR); return lp(sine(n, np.geomspace(85, 42, n)) * soft(n, .004, .12), 400) * .22
    if k == "click":   n = int(.09 * SR); return sine(n, np.geomspace(1170, 900, n)) * soft(n, .002, .018) * .09
fx = np.zeros(N)
for ev in json.load(open(f"{W}/sfx.json")):
    y = mk(ev["k"]); i = int(ev["t"] * SR); fx[i:i + len(y)] += y[:N - i]
# soft music bed for the end screen only (the story clips carry their own score)
hz = lambda m: 440 * 2 ** ((m - 69) / 12); mus = np.zeros(N); beat = 60 / 84
for ci, ch in enumerate([[57, 60, 64, 67], [53, 57, 60, 64], [48, 55, 60, 64]]):
    n = int(4 * beat * SR); i = int((ME - 0.3 + ci * 4 * beat) * SR)
    if i >= N: break
    seg = sum((sine(n, hz(m)) + .35 * sine(n, 2 * hz(m))) * soft(n, .02, 1.6) * .05 for m in ch) + sine(n, hz(ch[0] - 12)) * soft(n, .01, .9) * .12
    mus[i:i + n] += seg[:N - i]
e0 = int((ME - 0.3) * SR); f = int(0.4 * SR); mus[e0:e0 + f] *= np.linspace(0, 1, f); e1 = int(T * SR); mus[e1 - SR:e1] *= np.linspace(1, 0, SR); mus[e1:] = 0
sf.write(f"{W}/fx.wav", np.stack([fx + mus * 0.6] * 2, 1).astype(np.float32), SR, subtype="FLOAT")
fc = ("[0:a]aresample=48000[v];[1:a]volume=1.0[f];[v][f]amix=inputs=2:normalize=0:duration=first,"
      "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/base.mov", "-i", f"{W}/fx.wav", "-filter_complex", fc,
                "-map", "[out]", "-c:a", "pcm_s16le", f"{W}/mix.wav"], check=True)
print("mixed")
