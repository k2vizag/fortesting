"""Mix real CC0 comedy SFX (repo sfx_library/) into a finished mix at given edited-video times.
usage: comedy_sfx.py <config module> mix.wav out.wav       (config: COMEDY = [(t, sound, max_len_s, dB_vs_voice), ...])"""
import importlib, os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CFG = importlib.import_module(sys.argv[1]); mix_p, out_p = sys.argv[2:4]
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sfx_library")
SR = 48000

def load(name, maxlen):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{LIB}/{name}.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    y = np.frombuffer(raw, np.float32).copy()
    nz = np.where(np.abs(y) > 0.01 * np.abs(y).max())[0]
    y = y[max(0, nz[0] - 200): nz[-1] + 2000][:int(maxlen * SR)]
    f = min(len(y) // 3, int(0.2 * SR)); y[-f:] *= np.linspace(1, 0, f)
    return y / (np.sqrt(np.mean(y ** 2)) + 1e-9)

x, sr = sf.read(mix_p); assert sr == SR
mono = x.mean(1) if x.ndim > 1 else x
vr = np.sqrt(np.mean(mono[np.abs(mono) > 0.02] ** 2))
fx = np.zeros(len(mono) + 3 * SR)
for t, name, ml, db in CFG.COMEDY:
    y = load(name, ml) * vr * 10 ** (db / 20); i = int(t * SR); fx[i:i + len(y)] += y
fx = fx[:len(mono)]
out = x + (fx[:, None] if x.ndim > 1 else fx)
peak = np.abs(out).max()
if peak > 0.97: out *= 0.97 / peak
sf.write(out_p, out.astype(np.float32), SR, subtype="FLOAT")
print("comedy sfx", len(CFG.COMEDY))
