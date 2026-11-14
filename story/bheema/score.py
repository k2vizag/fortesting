"""Cinematic score + mix for one part. usage: python3 -I score.py <part_dir>   -> <part_dir>/mix.wav
Soft string pad under the dialogue (ducked by the voice), swelling with piano arpeggios, a riser and a low boom
in each music break (breaks.json). Soft UI sfx come from audio.py's synth (sfx.json)."""
import json, subprocess, sys, os
import numpy as np, soundfile as sf

PW = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
# reuse audio.py's synth helpers + soft UI sfx track (everything before its lo-fi music bed)
src = open(f"{HERE}/audio.py").read().split("# ---- music bed")[0]
ns = {"__name__": "sfxsynth"}; sys_argv = sys.argv; sys.argv = ["audio.py", PW]; exec(compile(src, "audio.py", "exec"), ns); sys.argv = sys_argv
SR, N, T, fx, sine, soft, lowpass = ns["SR"], ns["N"], ns["T"], ns["fx"], ns["sine"], ns["soft"], ns["lowpass"]
rng = np.random.default_rng(11)
breaks = json.load(open(f"{PW}/breaks.json"))

hz = lambda m: 440 * 2 ** ((m - 69) / 12)
CH = [[57, 60, 64, 69], [53, 57, 60, 65], [48, 55, 60, 64], [55, 59, 62, 67]]      # Am  F  C  G
BAR = 2.4
def strings(n, f):                     # warm detuned string-ish tone (few odd/even partials, slow attack)
    y = sum((0.55 / k) * (sine(n, f * k * (1 + 0.0015 * (k % 2))) + sine(n, f * k * (1 - 0.0012 * (k % 3)))) for k in range(1, 6))
    return y * soft(n, 0.7, 9.0)
pad = np.zeros(N); t, ci = 0.0, 0
while t < T + BAR:
    n = int((BAR + 1.5) * SR); seg = np.zeros(n)
    for m in CH[ci % 4]: seg += strings(n, hz(m)) * 0.022
    seg += sine(n, hz(CH[ci % 4][0] - 12)) * soft(n, 0.4, 3.0) * 0.06
    rel = np.ones(n); r0 = int(BAR * SR); rel[r0:] = np.exp(-np.arange(n - r0) / (0.5 * SR)); seg *= rel
    i = int(t * SR); seg = seg[:max(0, N - i)]; pad[i:i + len(seg)] += seg; t += BAR; ci += 1
pad = lowpass(pad, 2600)

# swell automation: pad +9 dB inside breaks (with ramps), piano arpeggio, riser into and boom at each break
gain = np.full(N, 1.0)
piano = np.zeros(N); hits = np.zeros(N)
for b0, b1 in breaks:
    i0, i1 = int(b0 * SR), int(b1 * SR); ramp = int(0.5 * SR)
    g = np.ones(i1 - i0) * 2.8; g[:ramp] = np.linspace(1, 2.8, ramp); g[-ramp:] = np.linspace(2.8, 1, ramp); gain[i0:i1] = np.maximum(gain[i0:i1], g)
    k = 0; tt = b0 + 0.15                # gentle piano arpeggio, 3 notes per beat
    while tt < b1 - 0.4:
        ch = CH[int(tt / BAR) % 4]; m = ch[k % 4] + 12 * (1 if k % 8 < 4 else 2)
        nn = int(1.6 * SR); y = (sine(nn, hz(m)) + 0.3 * sine(nn, 2 * hz(m)) + 0.08 * sine(nn, 3 * hz(m))) * soft(nn, 0.004, 0.55)
        j = int(tt * SR); y = y[:N - j]; piano[j:j + len(y)] += lowpass(y, 3200) * 0.075; tt += 0.27; k += 1
    if b0 > 0.5:                         # soft riser (filtered noise swell) into the break
        rn = int(1.0 * SR); y = rng.standard_normal(rn) * np.linspace(0, 1, rn) ** 2.5; y = lowpass(y, 1400) * 0.05
        j = max(0, int(b0 * SR) - rn); hits[j:j + rn] += y[:len(hits[j:j + rn])]
    bn = int(1.4 * SR); boom = sine(bn, np.geomspace(70, 34, bn)) * soft(bn, 0.004, 0.45)
    j = int(b0 * SR); hits[j:j + bn] += lowpass(boom, 300)[:N - j] * 0.32
# simple reverb on piano + pad (exponential noise IR via FFT convolution)
ir_n = int(1.6 * SR); ir = rng.standard_normal(ir_n) * np.exp(-np.arange(ir_n) / (0.45 * SR)); ir /= np.abs(ir).sum() / 6
def verb(x):
    L = len(x) + ir_n; F = 1 << (L - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, F) * np.fft.rfft(ir, F), F)[:len(x)]
mus = pad * gain + piano; mus = 0.75 * mus + 0.25 * verb(mus) + hits
fade = int(1.2 * SR); end = int(T * SR); mus[:int(0.4 * SR)] *= np.linspace(0, 1, int(0.4 * SR)); mus[end - fade:end] *= np.linspace(1, 0, fade); mus[end:] = 0
mus /= max(1e-9, np.abs(mus).max()) / 0.5
sf.write(f"{PW}/music.wav", np.stack([mus, mus], 1).astype(np.float32), SR, subtype="FLOAT")
sf.write(f"{PW}/fx.wav", fx.astype(np.float32), SR, subtype="FLOAT")
fc = ("[0:a]aresample=48000,asplit=2[v][vs];"
      "[1:a]volume=0.55[m];[m][vs]sidechaincompress=threshold=0.02:ratio=6:attack=20:release=450[md];"
      "[2:a]volume=0.75[f];[v][md][f]amix=inputs=3:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11,alimiter=limit=0.95[out]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"{PW}/base.mov", "-i", f"{PW}/music.wav", "-i", f"{PW}/fx.wav",
                "-filter_complex", fc, "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", f"{PW}/mix.wav"], check=True)
print("mixed", PW)
