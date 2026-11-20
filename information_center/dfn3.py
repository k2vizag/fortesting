"""DeepFilterNet3 speech enhancement using the official 3-graph ONNX export (enc / erb_dec / df_dec).
usage: dfn3.py <model_dir> in.wav out.wav   (48 kHz mono)"""
import sys
import numpy as np, soundfile as sf, onnxruntime as ort

SR, N_FFT, HOP, NE, NDF, ORD, LA, CLA = 48000, 960, 480, 32, 96, 5, 2, 2
ALPHA = float(np.exp(-HOP / SR / 1.0))
NB = N_FFT // 2 + 1

def erb_widths(min_nb=2):
    f2e = lambda f: 9.265 * np.log1p(f / (24.7 * 9.265))
    e2f = lambda e: 24.7 * 9.265 * (np.exp(e / 9.265) - 1)
    lo, hi = f2e(0), f2e(SR / 2); step = (hi - lo) / NE; fw = SR / N_FFT
    w, prev, over = [], 0, 0
    for i in range(1, NE + 1):
        fb = int(round(e2f(lo + i * step) / fw)); n = fb - prev - over
        if n < min_nb: over = min_nb - n; n = min_nb
        else: over = 0
        w.append(n); prev = fb
    w[-1] += 1
    w[-1] -= sum(w) - NB
    return w

W = erb_widths()
band = np.repeat(np.arange(NE), W)                 # bin -> band
fwd = np.zeros((NB, NE)); fwd[np.arange(NB), band] = 1; fwd /= fwd.sum(0)   # mean power per band
inv = np.zeros((NE, NB)); inv[band, np.arange(NB)] = 1
n = np.arange(N_FFT)
win = np.sin(0.5 * np.pi * np.sin(np.pi * (n + 0.5) / N_FFT) ** 2)

def stft(x):
    x = np.concatenate([np.zeros(HOP), x, np.zeros(N_FFT)])
    m = (len(x) - N_FFT) // HOP + 1
    idx = n[None, :] + HOP * np.arange(m)[:, None]
    return np.fft.rfft(x[idx] * win, axis=1) / N_FFT

def istft(X, length):
    fr = np.fft.irfft(X * N_FFT, n=N_FFT, axis=1) * win
    out = np.zeros(HOP * (len(X) + 1))
    for t in range(len(X)):
        out[t * HOP:t * HOP + N_FFT] += fr[t]
    return out[HOP:HOP + length]

def features(X):
    T = len(X)
    erb = 10 * np.log10((X.real ** 2 + X.imag ** 2) @ fwd + 1e-10)
    st = np.linspace(-60, -90, NE); fe = np.empty_like(erb)
    for t in range(T):
        st = erb[t] * (1 - ALPHA) + st * ALPHA; fe[t] = (erb[t] - st) / 40.0
    Xs = X[:, :NDF]; us = np.linspace(0.001, 0.0001, NDF); fs = np.empty_like(Xs)
    for t in range(T):
        us = np.abs(Xs[t]) * (1 - ALPHA) + us * ALPHA; fs[t] = Xs[t] / np.sqrt(us)
    # conv lookahead: shift features 2 frames earlier (pad_feat in DfNet.forward)
    fe = np.concatenate([fe[CLA:], np.zeros((CLA, NE))]); fs = np.concatenate([fs[CLA:], np.zeros((CLA, NDF))])
    return (fe[None, None].astype(np.float32), np.stack([fs.real, fs.imag], 0)[None].astype(np.float32))

def enhance(x, S):
    X = stft(x); T = len(X)
    fe, fs = features(X)
    e0, e1, e2, e3, emb, c0, lsnr = S["enc"].run(None, {"feat_erb": fe, "feat_spec": fs})
    m = S["erb"].run(None, {"emb": emb, "e3": e3, "e2": e2, "e1": e1, "e0": e0})[0]
    co = S["df"].run(None, {"emb": emb, "c0": c0})[0][0].reshape(T, NDF, ORD, 2)
    Y = X * (m[0, 0] @ inv)
    c = (co[..., 0] + 1j * co[..., 1]).transpose(2, 0, 1)      # [ORD,T,F]
    pad = np.concatenate([np.zeros((ORD - 1 - LA, NDF), complex), X[:, :NDF], np.zeros((LA, NDF), complex)])
    df = np.zeros((T, NDF), complex)
    for i in range(ORD): df += c[i] * pad[i:i + T]
    Y[:, :NDF] = df
    return istft(Y, len(x))

if __name__ == "__main__":
    D = sys.argv[1].rstrip("/") + "/"
    S = {k: ort.InferenceSession(D + f, providers=["CPUExecutionProvider"])
         for k, f in [("enc", "enc.onnx"), ("erb", "erb_dec.onnx"), ("df", "df_dec.onnx")]}
    x, sr = sf.read(sys.argv[2]); x = x.mean(1) if x.ndim > 1 else x
    assert sr == SR, sr
    CH, OV = 30 * sr, sr
    out = np.zeros(len(x)); ws = np.zeros(len(x)); s = 0
    while s < len(x):
        e = min(len(x), s + CH + OV); y = enhance(x[s:e], S); w = np.ones(e - s)
        if s > 0: w[:OV] = np.linspace(0, 1, OV)
        if e < len(x): w[-OV:] = np.linspace(1, 0, OV)
        out[s:e] += y * w; ws[s:e] += w
        if e == len(x): break
        s += CH
    out /= np.maximum(ws, 1e-6)
    sf.write(sys.argv[3], out.astype(np.float32), sr, subtype="FLOAT")
    print("ok", len(x) / sr, "s")
