"""Remove the AI tool's sparkle mark (bottom-right, 720x1280 clips) by reversing its alpha blend.
usage: python3 -I remove_sparkle.py <work_dir> test|full
needs <work_dir>/raw_orig/c01..c10.mp4 and wm_shape.npy (soft sparkle shape learned from the
high-pass average of ~400 frames; opacity measured on flat dark frames = 0.30). writes <work_dir>/raw/.
"""
import subprocess, sys, numpy as np, cv2
from PIL import Image
S = sys.argv[1]; X0, Y0, X1, Y1 = 560, 1120, 640, 1200; A0 = 0.30
shape = np.load(S + "/wm_shape.npy")
solid = (shape > 0.5).astype(np.uint8)
ff = solid.copy(); h, w = ff.shape; m = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(ff, m, (0, 0), 1)
holes = (ff == 0); shape[holes] = 1.0                     # fill the hole in the middle
A = (A0 * shape)[..., None].astype(np.float32)
edge = ((cv2.dilate(solid | holes.astype(np.uint8), np.ones((5, 5), np.uint8)) - cv2.erode(solid | holes.astype(np.uint8), np.ones((3, 3), np.uint8))) > 0).astype(np.uint8) * 255
def clean(f):
    r = f[Y0:Y1, X0:X1].astype(np.float32)
    b = np.clip((r - A * 255) / (1 - A), 0, 255).astype(np.uint8)
    b = cv2.inpaint(b, edge, 2, cv2.INPAINT_TELEA)              # hide any thin anti-aliasing seam
    f[Y0:Y1, X0:X1] = b; return f
if sys.argv[2] == "test":
    g = Image.new("RGB", (4 * 240, 2 * 240))
    for i, (c, t) in enumerate([(1, 5), (4, 3), (8, 4), (10, 6)]):
        b = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", f"{S}/raw_orig/c{c:02d}.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        f = np.frombuffer(b, np.uint8).reshape(1280, 720, 3).copy()
        g.paste(Image.fromarray(f[1080:1240, 520:680]).resize((240, 240)), (i * 240, 0))
        g.paste(Image.fromarray(clean(f)[1080:1240, 520:680]).resize((240, 240)), (i * 240, 240))
    g.save(S + "/wm_check.jpg")
else:
    for c in range(1, 11):
        src = f"{S}/raw_orig/c{c:02d}.mp4"; dst = f"{S}/raw/c{c:02d}.mp4"
        dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "720x1280", "-r", "24", "-i", "-", "-i", src,
                                "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "copy", dst], stdin=subprocess.PIPE)
        while True:
            b = dec.stdout.read(720 * 1280 * 3)
            if len(b) < 720 * 1280 * 3: break
            enc.stdin.write(clean(np.frombuffer(b, np.uint8).reshape(1280, 720, 3).copy()).tobytes())
        enc.stdin.close(); enc.wait(); dec.wait(); print("clip", c, flush=True)
