"""DeepFilterNet3 (ONNX graph) speech enhancement, 48 kHz mono.
usage: dfn.py in.wav out.wav [atten_lim_db]"""
import sys
import numpy as np, soundfile as sf, onnxruntime as ort

D = "/tmp/claude-0/-home-user-fortesting/4e589d33-8934-5dd9-a5c1-fec76296f99d/scratchpad/dfn/"
N_FFT, HOP, NB, NE, NDF, ORD, LA, ALPHA = 960, 480, 481, 32, 96, 5, 2, 0.99

aux = np.fromfile(D + "deepfilter-auxiliary.bin", dtype="<f4")
fwd = aux[:NB * NE].reshape(NB, NE)
inv = aux[NB * NE:2 * NB * NE].reshape(NE, NB)
win = aux[2 * NB * NE:2 * NB * NE + N_FFT]
assert len(aux) == 2 * NB * NE + N_FFT

def stft(x):
    x = np.concatenate([np.zeros(HOP), x, np.zeros(N_FFT)])  # analysis tail
    n = (len(x) - N_FFT) // HOP + 1
    idx = np.arange(N_FFT)[None, :] + HOP * np.arange(n)[:, None]
    return np.fft.rfft(x[idx] * win, axis=1) / N_FFT  # wnorm = 1/N

def istft(X, length):
    fr = np.fft.irfft(X * N_FFT, n=N_FFT, axis=1) * win
    out = np.zeros(HOP * (len(X) + 1))
    for t in range(len(X)):
        out[t * HOP:t * HOP + N_FFT] += fr[t]
    return out[HOP:HOP + length]

def features(X):
    T = len(X)
    pw = (X.real ** 2 + X.imag ** 2)
    erb = 10 * np.log10(pw @ fwd + 1e-10)
    st = np.linspace(-60, -90, NE)
    fe = np.empty_like(erb)
    for t in range(T):
        st = erb[t] * (1 - ALPHA) + st * ALPHA
        fe[t] = (erb[t] - st) / 40.0
    Xs = X[:, :NDF]
    us = np.linspace(0.001, 0.0001, NDF)
    fs = np.empty_like(Xs)
    for t in range(T):
        us = np.abs(Xs[t]) * (1 - ALPHA) + us * ALPHA
        fs[t] = Xs[t] / np.sqrt(us)
    feat_erb = fe[None, None].astype(np.float32)
    feat_spec = np.stack([fs.real, fs.imag], 0)[None].astype(np.float32)
    return feat_erb, feat_spec

def enhance(x, sess, atten_db=None):
    X = stft(x)
    fe, fs = features(X)
    mask, coefs = sess.run(None, {"feat_erb": fe, "feat_spec": fs})
    g = mask[0, 0] @ inv                      # [T,481]
    Y = X * g
    c = coefs[0, ..., 0] + 1j * coefs[0, ..., 1]  # [ORD,T,96]
    T = len(X)
    pad = np.concatenate([np.zeros((ORD - 1 - LA, NDF), complex), X[:, :NDF], np.zeros((LA, NDF), complex)])
    df = np.zeros((T, NDF), complex)
    for i in range(ORD):
        df += c[i] * pad[i:i + T]
    Y[:, :NDF] = df
    if atten_db is not None:  # mix back a little of the noisy signal
        lim = 10 ** (-atten_db / 20)
        Y = Y * (1 - lim) + X * lim
    return istft(Y, len(x))

if __name__ == "__main__":
    x, sr = sf.read(sys.argv[1])
    if x.ndim > 1: x = x.mean(1)
    assert sr == 48000, sr
    sess = ort.InferenceSession(D + "deepfilter.onnx", providers=["CPUExecutionProvider"])
    att = float(sys.argv[3]) if len(sys.argv) > 3 else None
    # process in ~60 s chunks with 1 s overlap to bound memory
    CH, OV = 60 * sr, sr
    out = np.zeros(len(x)); wsum = np.zeros(len(x))
    s = 0
    while s < len(x):
        e = min(len(x), s + CH + OV)
        y = enhance(x[s:e], sess, att)
        w = np.ones(e - s)
        if s > 0: w[:OV] = np.linspace(0, 1, OV)
        if e < len(x): w[-OV:] = np.linspace(1, 0, OV)
        out[s:e] += y * w; wsum[s:e] += w
        if e == len(x): break
        s += CH
    out /= np.maximum(wsum, 1e-6)
    sf.write(sys.argv[2], out.astype(np.float32), sr, subtype="FLOAT")
    print("ok", len(x) / sr, "s")
