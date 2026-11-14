# Joins the missing last word "పడాలా" from the second clip onto the song.
# usage: python3 join_audio.py song.wav clip.wav out.wav   (both 44.1 kHz stereo)
# Offset between the two recordings was found by cross-correlation (2.568 s).
import sys, soundfile as sf, numpy as np
o, sr = sf.read(sys.argv[1]); c, _ = sf.read(sys.argv[2])
off, cut, xf = 2.568049886621317, 48.2, 0.15
a = o[:int(cut*sr)].copy(); b = c[int((cut+off-xf)*sr):].copy()*1.27   # 1.27 = level match
n = int(xf*sr); w = np.linspace(0, 1, n)[:, None]
a[-n:] = a[-n:]*(1-w) + b[:n]*w
out = np.concatenate([a, b[n:]]); fo = int(.35*sr); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
sf.write(sys.argv[3], np.clip(out, -1, 1), sr)
