"""Put the matted person on the studio background, with a light grade + light wrap so it sits in the scene.
usage: composite.py base.mov alpha.mkv bg.png out.mov [dark|light] [foreground.png with alpha, e.g. desk edge]      (audio copied; black intro/end frames pass through)"""
import subprocess, sys
import cv2, numpy as np

W, H = 1080, 1920
base, alpha, bgp, dst = sys.argv[1:5]
bg = cv2.imread(bgp).astype(np.float32)
wrap_src = cv2.GaussianBlur(bg, (0, 0), 30)
# person grade: a touch darker, warmer and punchier to match the moody studio light
LOOK = sys.argv[5] if len(sys.argv) > 5 else "dark"
if LOOK == "light":   # white studio: keep natural brightness, just a little clarity and warmth
    lut = np.clip(((np.arange(256) / 255.0 - 0.5) * 1.04 + 0.5) * 1.02 * 255, 0, 255).astype(np.float32)
    warm, WRAP = np.array([0.98, 1.0, 1.02], np.float32), 0.35
else:                 # dark studio: a touch darker, warmer and punchier
    lut = np.clip(((np.arange(256) / 255.0 - 0.5) * 1.08 + 0.5) * 0.94 * 255, 0, 255).astype(np.float32)
    warm, WRAP = np.array([0.96, 1.0, 1.04], np.float32), 0.55   # BGR gains

FG = cv2.imread(sys.argv[6], cv2.IMREAD_UNCHANGED).astype(np.float32) if len(sys.argv) > 6 else None
if FG is not None: FGA = FG[..., 3:4] / 255.0; FGC = FG[..., :3]

YY = np.arange(H, dtype=np.float32)[:, None]
LOW = np.clip((YY - 1300) / 200, 0, 1)            # lower body only

def trousers_to_navy(f, a):
    """green-teal trousers (seen near the desk) -> dark navy, so they don't read as left-over office."""
    hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV).astype(np.float32)
    h, s_, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    m = ((h >= 30) & (h <= 98) & (s_ >= 18)).astype(np.float32) * (a > 0.4) * LOW
    m = cv2.GaussianBlur(m, (0, 0), 3)
    if m.max() < 0.05: return f
    nav = hsv.copy(); nav[..., 0] = 112; nav[..., 1] = np.clip(s_ * 0.9 + 25, 0, 140); nav[..., 2] = v * 0.62
    nav = cv2.cvtColor(nav.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    return (nav * m[..., None] + f.astype(np.float32) * (1 - m[..., None])).astype(np.uint8)

def comp(f, a):
    f = trousers_to_navy(f, a.astype(np.float32) / 255.0)
    f = lut[f] * warm
    a = a.astype(np.float32) / 255.0
    ab = cv2.GaussianBlur(a, (0, 0), 9)
    edge = np.clip(a * (1.0 - ab) * 2.2, 0, 1)[..., None]           # thin band just inside the silhouette
    f = f * (1 - WRAP * edge) + wrap_src * WRAP * edge            # light wrap
    # gentle rim from the warm glow behind the head (upper body only)
    a3 = a[..., None]
    out = f * a3 + bg * (1 - a3)
    if FG is not None: out = FGC * FGA + out * (1 - FGA)
    return np.clip(out, 0, 255).astype(np.uint8)

dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
dea = subprocess.Popen(["ffmpeg", "-v", "error", "-i", alpha, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-i", base, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "fast", "-crf", "14",
                        "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)
n = 0
while True:
    b = dec.stdout.read(W * H * 3); m = dea.stdout.read(W * H)
    if len(b) < W * H * 3 or len(m) < W * H: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    out = f if f.max() < 20 else comp(f, np.frombuffer(m, np.uint8).reshape(H, W))
    enc.stdin.write(out.tobytes()); n += 1
enc.stdin.close(); enc.wait(); print("frames", n)
