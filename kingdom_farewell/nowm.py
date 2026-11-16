"""Remove the AI generator's ✦ corner mark: inpaint a star-shaped mask on every frame (OpenCV), keep audio.
usage: python3 nowm.py in.mp4 out.mp4   (mark sits at the same spot in every clip after scaling to 1080x1920)"""
import sys, subprocess, cv2, numpy as np
src, dst = sys.argv[1], sys.argv[2]
CX, CY, RX, RY = 899, 1742, 37, 36
x0, y0, x1, y1 = CX - 70, CY - 70, CX + 70, CY + 70          # work on a small region only
m = np.zeros((y1 - y0, x1 - x0), np.uint8)
cx, cy = CX - x0, CY - y0
cv2.fillConvexPoly(m, np.array([[cx, cy - RY], [cx + RX, cy], [cx, cy + RY], [cx - RX, cy]], np.int32), 255)
m = cv2.dilate(m, np.ones((7, 7), np.uint8))
cap = cv2.VideoCapture(src); fps = cap.get(cv2.CAP_PROP_FPS); W = int(cap.get(3)); H = int(cap.get(4))
ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
                       "-i", src, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy",
                       "-movflags", "+faststart", dst], stdin=subprocess.PIPE)
n = 0
while True:
    ok, f = cap.read()
    if not ok: break
    roi = f[y0:y1, x0:x1]
    f[y0:y1, x0:x1] = cv2.inpaint(roi, m, 9, cv2.INPAINT_TELEA)
    ff.stdin.write(f.tobytes()); n += 1
ff.stdin.close(); ff.wait(); print("frames", n)
