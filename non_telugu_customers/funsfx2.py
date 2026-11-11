"""Mix real CC0 comedy SFX (SFXMint, Hugging Face) under the cleaned voice. usage: funsfx2.py voice.wav libdir out.wav"""
import subprocess, sys, numpy as np, soundfile as sf
SR = 48000
voice, lib, outp = sys.argv[1:4]
def load(name, maxlen):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f"{lib}/{name}.mp3", "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True).stdout
    y = np.frombuffer(raw, np.float32).copy()
    nz = np.where(np.abs(y) > 0.01 * np.abs(y).max())[0]          # trim leading/trailing silence
    y = y[max(0, nz[0] - 200): nz[-1] + 2000]
    y = y[:int(maxlen * SR)]
    f = min(len(y) // 3, int(0.25 * SR)); y[-f:] *= np.linspace(1, 0, f)
    return y / (np.sqrt(np.mean(y ** 2)) + 1e-9)                    # unit RMS
# time, sound, max length (s), level relative to voice RMS (dB)
EVENTS = [
    (3.3, "cartoon-squeak-04", 0.6, -9),        # 😵‍💫 confused
    (9.7, "cartoon-pop-01", 0.5, -10),          # RTO office kaha?
    (16.3, "feedback-fail-04", 1.0, -9),        # telugu nahi aata
    (17.4, "crowd-laughter-22", 2.6, -15),
    (28.8, "cartoon-bonk-01", 0.8, -8),         # 🤯
    (37.3, "laugh-01", 1.8, -12),               # 😂
    (41.6, "cartoon-boing-01", 0.9, -9),        # 🤣
    (44.4, "cartoon-eye-blink-01", 0.8, -9),    # 🫣
    (51.8, "crowd-ooh-01", 1.6, -14),           # 😶 awkward
    (59.9, "clown-horn-01", 0.9, -10),          # telugu nahi... all English
    (61.2, "crowd-laughter-22", 2.6, -15),
    (69.0, "cartoon-pop-01", 0.5, -10),         # 🎬 part 2
    (75.1, "office-ringtone-01", 1.2, -14),     # 📞
    (78.7, "cartoon-splat-01", 0.8, -10),       # 😤
    (81.9, "ready-coin-04", 0.9, -10),          # kitna paisa lega? 💸
    (94.5, "office-camera-08", 0.6, -10),       # 📸 kitna photos
    (97.4, "cartoon-slide-whistle-01", 1.2, -12),  # 👋 bye
    (99.4, "crowd-laughter-22", 2.0, -15),      # ending laugh
]
v, sr = sf.read(voice); v = v if v.ndim == 1 else v.mean(1); assert sr == SR
speech = v[np.abs(v) > 0.02]; vr = np.sqrt(np.mean(speech ** 2))
fx = np.zeros(len(v) + 3 * SR)
for t, name, ml, db in EVENTS:
    y = load(name, ml) * vr * 10 ** (db / 20); i = int(t * SR); fx[i:i + len(y)] += y
fx = fx[:len(v)]
sf.write(outp, np.stack([v + fx, v + fx], 1).astype(np.float32), SR, subtype="FLOAT")
print("events", len(EVENTS))
