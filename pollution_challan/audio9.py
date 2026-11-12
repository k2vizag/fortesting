"""Synthesize soft SFX + lo-fi bed, comedy bed + CC0 comedy SFX on the funny parts, and mix with the cleaned voice. usage: audio2.py bike|car -> work2_<kind>/mix.wav"""
import json, subprocess, sys
import numpy as np, soundfile as sf

S = "/tmp/claude-0/-home-user-fortesting/f0703b19-2505-5b8b-b72d-114eb35464cd/scratchpad/ch"
W = f"{S}/work"
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
# ---- comedy bed for the funny parts: bouncy staccato oom-pah + pizzicato tune, 132 bpm, C major
FUN = json.load(open(f"{W}/fun.json"))
def pluckn(f, dur, g, bright=3):
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(np.sin(2 * np.pi * f * h * t) / h ** 1.6 for h in range(1, bright + 1)) * np.exp(-t / (dur * 0.35))
    return y * np.minimum(1, t / 0.004) * g
fb = 60 / 132; tune = [72, 76, 79, 76, 77, 74, 71, 74, 72, 76, 79, 84, 83, 79, 77, 74]
bassl = [(48, 55), (43, 50), (45, 52), (43, 50)]
funm = np.zeros(N)
for a0, b0 in FUN["music"]:
    t = a0; i = 0
    while t < b0:
        o = int(t * SR); bar = i // 8; ch = bassl[bar % 4]
        y = np.zeros(int(fb * SR) + SR)
        bn = pluckn(hz(ch[0] - 12 if i % 2 == 0 else ch[1] - 12), fb * 0.45, 0.20, 4)   # oom / pah
        y[:len(bn)] += bn
        if i % 2 == 1:                                                                   # off-beat chord stab
            for m in (ch[1], ch[1] + 4, ch[1] + 7):
                c = pluckn(hz(m), fb * 0.3, 0.035); y[:len(c)] += c
        mel = pluckn(hz(tune[i % 16]), fb * 0.4, 0.06, 2); y[:len(mel)] += mel
        if i % 4 == 3:                                                                   # little grace note
            g2 = pluckn(hz(tune[i % 16] + 2), fb * 0.25, 0.04, 2); h = int(fb / 2 * SR); y[h:h + len(g2)] += g2
        y = y[:N - o]; funm[o:o + len(y)] += y
        t += fb; i += 1
    # fades + duck the lo-fi bed under the comedy bed
    ia, ib = int(a0 * SR), int(b0 * SR); fd = int(0.35 * SR)
    funm[ia:ia + fd] *= np.linspace(0, 1, fd); funm[ib:ib + fd] *= np.linspace(1, 0, fd)[:len(funm[ib:ib + fd])]; funm[ib + fd:ib + 3 * SR] = 0
    env_ = np.ones(N); env_[ia:ib] = 0.0
    env_[max(0, ia - fd):ia] = np.linspace(1, 0, ia - max(0, ia - fd)); env_[ib:ib + fd] = np.linspace(0, 1, fd)[:len(env_[ib:ib + fd])]
    mus *= env_
mus += funm * 1.6
# ---- real CC0 comedy sfx from the repo's sfx_library
LIB = "/home/user/fortesting/sfx_library"
def libload(name, maxlen):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{LIB}/{name}.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    y = np.frombuffer(raw, np.float32).copy(); nz = np.where(np.abs(y) > 0.01 * np.abs(y).max())[0]
    y = y[max(0, nz[0] - 200): nz[-1] + 2000][:int(maxlen * SR)]
    f = min(len(y) // 3, int(0.25 * SR)); y[-f:] *= np.linspace(1, 0, f)
    return y / (np.sqrt(np.mean(y ** 2)) + 1e-9)
VR = 0.08   # approx. voice RMS after loudnorm -14
for t0, name, ml, dbv in FUN["events"]:
    y = libload(name, ml) * VR * 10 ** (dbv / 20); i = int(t0 * SR); y = y[:N - i]
    fx[i:i + len(y), 0] += y; fx[i:i + len(y), 1] += y
fade = int(1.5 * SR); mus[:fade] *= np.linspace(0, 1, fade); mus[int(T * SR) - fade:int(T * SR)] *= np.linspace(1, 0, fade); mus[int(T * SR):] = 0
sf.write(f"{W}/fx.wav", fx.astype(np.float32), SR, subtype="FLOAT")
sf.write(f"{W}/music.wav", np.stack([mus, mus], 1).astype(np.float32), SR, subtype="FLOAT")

# ---- mix: voice (loudnorm) + music ducked under voice + sfx
fc = ("[0:a]loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000,asplit=2[v][vs];"
      "[1:a]volume=0.42[m];[m][vs]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];"
      "[2:a]volume=0.75[f];[v][md][f]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9,aresample=48000[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{W}/base.mov", "-i", f"{W}/music.wav", "-i", f"{W}/fx.wav",
                "-filter_complex", fc, "-map", "[out]", "-c:a", "pcm_s16le", f"{W}/mix.wav"], check=True)
print("mixed", W)
