"""Recolour the green plaid shirt (hue shift) in a 1080x1920 base video.
usage: recolor.py in.mov out.mov blue|darkblue|red        (audio is copied)
Mask = shirt hue band (excludes teal painting), not too dark (excludes beard),
and only regions connected to the bottom of the frame (drops hair edges / wall specks)."""
import subprocess, sys
import cv2, numpy as np

W, H = 1080, 1920
TARGET = {"blue": 108, "darkblue": 113, "red": 177}      # OpenCV hue (0-180)
SRC_H = 70
LO, HI = 56, 82

def shirt_mask(hsv):
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    # wall is grey-green too (S~15-20) but much brighter (V>210): cap V to keep it out
    m = ((h >= LO) & (h <= HI) & (s >= 24) & (v >= 36) & (v <= 205)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, cen = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    bottom = set(np.unique(lab[H - 120:, :])) - {0}
    for i in range(1, n):
        a = st[i, cv2.CC_STAT_AREA]
        # shirt pieces: touching the bottom, or big and below the face (sleeve cut off by a raised arm)
        if (i in bottom and a > 15000) or (a > 2500 and cen[i][1] > 1000):
            keep[i] = True
    m = keep[lab].astype(np.uint8)
    # grow inside the shirt-hue band so dark folds / low-sat threads also shift
    band = ((h >= 36) & (h <= HI + 8) & (v >= 14) & (((s >= 18) & (v <= 212)) | ((s >= 23) & (v <= 245)))).astype(np.uint8)
    for _ in range(9):
        m = cv2.dilate(m, np.ones((9, 9), np.uint8)) & band
    return cv2.GaussianBlur(m.astype(np.float32), (9, 9), 0)

def recolor(bgr, color):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    a = shirt_mask(hsv)
    if a.max() == 0: return bgr
    out = hsv.astype(np.float32)
    # set the hue to the target (keeping a little of the original variation): a fixed shift turned the
    # warm-lit yellow-green parts of the shirt (H 37-55) cyan instead of blue
    out[..., 0] = (TARGET[color] + 0.25 * (out[..., 0] - SRC_H)) % 180
    out[..., 1] = np.clip(out[..., 1] * {"blue": 1.9, "darkblue": 2.6, "red": 2.2}[color] + 10, 0, 255)
    if color == "red": out[..., 2] = np.clip(out[..., 2] * 0.92, 0, 255)
    if color == "darkblue": out[..., 2] = np.clip(out[..., 2] * 0.55, 0, 255)   # navy: darker, richer
    new = cv2.cvtColor(out.astype(np.uint8), cv2.COLOR_HSV2BGR).astype(np.float32)
    a3 = a[..., None]
    return (new * a3 + bgr.astype(np.float32) * (1 - a3)).astype(np.uint8)

if __name__ == "__main__":
    src, dst, color = sys.argv[1:4]
    if src.endswith(".jpg"):
        cv2.imwrite(dst, recolor(cv2.imread(src), color)); sys.exit()
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", "30",
                            "-i", "-", "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "fast",
                            "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)
    n = 0
    while True:
        b = dec.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        enc.stdin.write(recolor(np.frombuffer(b, np.uint8).reshape(H, W, 3), color).tobytes()); n += 1
    enc.stdin.close(); enc.wait()
    print("frames", n)
