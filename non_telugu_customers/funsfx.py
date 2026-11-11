"""Synthesize cartoon comedy SFX and mix them under the cleaned voice. usage: funsfx.py voice.wav out.wav"""
import sys, numpy as np, soundfile as sf
SR = 48000; rng = np.random.default_rng(3)
def sine(n, f):
    f = np.broadcast_to(np.asarray(f, float), (n,)); return np.sin(2*np.pi*np.cumsum(f)/SR)
def env(n, a, d):
    t = np.arange(n)/SR; return np.minimum(1, t/max(a,1e-4))*np.exp(-t/d)
def lp(y, fc):
    a = np.exp(-2*np.pi*fc/SR); o = np.empty_like(y); z = 0.0
    for i in range(len(y)): z = (1-a)*y[i] + a*z; o[i] = z
    return o
def saw(n, f):
    f = np.broadcast_to(np.asarray(f, float), (n,)); ph = np.cumsum(f)/SR; return 2*(ph % 1) - 1
def boing():
    n = int(0.6*SR); t = np.arange(n)/SR
    f = 180 + 260*np.exp(-t*5) * (1 + 0.35*np.sin(2*np.pi*18*t))
    return sine(n, f)*env(n, 0.003, 0.22)*0.5
def slide(up=True, dur=0.55):
    n = int(dur*SR); t = np.linspace(0, 1, n)
    f = (500 + 1100*t**1.3) if up else (1600 - 1150*t**0.8)
    f = f*(1 + 0.012*np.sin(2*np.pi*6*np.arange(n)/SR))
    return (sine(n, f) + 0.15*sine(n, 2*f))*np.sin(np.linspace(0, np.pi, n))**0.6*0.28
def trombone():
    out = []
    for i, (f0, d) in enumerate([(311, .32), (293, .32), (277, .32), (262, .9)]):
        n = int(d*SR); t = np.arange(n)/SR
        vib = 1 + (0.03*np.sin(2*np.pi*5.5*t) if i == 3 else 0)
        y = lp(saw(n, f0*vib), 1500)*np.minimum(1, t/0.03)*np.minimum(1, (d - t)/0.06)
        out.append(y)
    return np.concatenate(out)*0.32
def scratch():
    n = int(0.45*SR); t = np.arange(n)/SR
    sp = np.abs(np.sin(2*np.pi*3.3*t))
    y = rng.standard_normal(n); y = lp(y, 2500) - lp(y, 300)
    return y*sp*np.exp(-t*2)*1.4 + 0.25*sine(n, 220 + 380*sp)*np.exp(-t*3)
def bonk():
    n = int(0.35*SR)
    return (sine(n, np.geomspace(320, 110, n))*env(n, 0.001, 0.07) + lp(rng.standard_normal(n), 1200)*env(n, 0.0005, 0.01))*0.6
def boom():
    n = int(0.9*SR)
    return (sine(n, np.geomspace(90, 35, n))*env(n, 0.004, 0.3) + lp(rng.standard_normal(n), 600)*env(n, 0.002, 0.15)*0.8)*0.6
def pop():
    n = int(0.11*SR); return sine(n, np.geomspace(380, 1100, n))*env(n, 0.002, 0.03)*0.45
def ticktock():
    out = np.zeros(int(1.3*SR))
    for k in range(4):
        n = int(0.04*SR); s = int(k*0.32*SR)
        out[s:s+n] += sine(n, 2000 if k % 2 == 0 else 1500)*env(n, 0.0005, 0.006)*0.45
    return out
def crickets():
    out = np.zeros(int(1.6*SR))
    for k in range(3):
        s = int((0.1 + k*0.5)*SR)
        for j in range(6):
            n = int(0.025*SR); p = s + int(j*0.035*SR)
            out[p:p+n] += sine(n, 4300)*np.sin(np.linspace(0, np.pi, n))*0.18
    return out
def clack():
    n = int(0.08*SR); return lp(rng.standard_normal(n), 5000)*env(n, 0.0003, 0.008)*0.9
def ring():
    n = int(0.9*SR); t = np.arange(n)/SR
    gate = ((t % 0.1) < 0.05) * ((t < 0.4) | (t > 0.5))
    return (sine(n, 1400) + sine(n, 1750))*gate*0.13
def kaching():
    n = int(0.9*SR)
    a = lp(rng.standard_normal(int(0.06*SR)), 4000)*0.5
    b = sum(sine(n, f)*env(n, 0.001, 0.35)/(i+1) for i, f in enumerate([2093, 2637, 3136]))*0.25
    y = b.copy(); y[:len(a)] += a; return y
def shutter():
    n = int(0.16*SR); y = rng.standard_normal(n)*env(n, 0.0005, 0.01)
    d = int(0.07*SR); y[d:] += rng.standard_normal(n - d)*env(n - d, 0.0005, 0.02)*0.8; return lp(y, 5000)*0.7
def wobble():
    n = int(0.8*SR); t = np.arange(n)/SR
    return sine(n, 400 + 150*np.sin(2*np.pi*7*t) - 200*t)*np.sin(np.linspace(0, np.pi, n))*0.25
FX = dict(boing=boing, up=lambda: slide(True), down=lambda: slide(False), trombone=trombone, scratch=scratch,
          bonk=bonk, boom=boom, pop=pop, ticktock=ticktock, crickets=crickets, clack=clack, ring=ring,
          kaching=kaching, shutter=shutter, wobble=wobble)
EVENTS = [(0.3, "scratch"), (3.3, "wobble"), (7.2, "boing"), (9.7, "pop"), (14.2, "ticktock"), (16.3, "trombone"),
          (20.0, "down"), (24.3, "pop"), (28.8, "boom"), (32.3, "pop"), (37.3, "boing"), (41.6, "up"),
          (44.4, "scratch"), (51.8, "crickets"), (57.0, "ticktock"), (59.9, "scratch"), (60.5, "boing"),
          (65.7, "pop"), (69.0, "clack"), (72.5, "ticktock"), (75.1, "ring"), (78.7, "bonk"), (81.9, "kaching"),
          (86.1, "pop"), (92.6, "pop"), (94.5, "shutter"), (97.4, "up"), (99.4, "boing")]
v, sr = sf.read(sys.argv[1]); v = v if v.ndim == 1 else v.mean(1); assert sr == SR
fx = np.zeros(len(v) + SR)
for t, k in EVENTS:
    y = FX[k](); i = int(t*SR); fx[i:i+len(y)] += y[:len(fx)-i]
fx = fx[:len(v)]
peak_v = np.percentile(np.abs(v), 99.5)
fx *= 1.4*peak_v/max(np.abs(fx).max(), 1e-9)       # SFX peaks ~5 dB under the voice
out = np.stack([v + fx, v + fx], 1)
sf.write(sys.argv[2], out.astype(np.float32), SR, subtype="FLOAT")
print("events", len(EVENTS))
