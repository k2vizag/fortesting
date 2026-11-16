"""Prepare the user's real photos of her for the repeated lyrics: find her face (closest to her identity),
trim empty sky/floor (full width kept), crop her out of group selfies. -> <scratchpad>/song/real/<id>.jpg"""
import os, cv2, numpy as np
from insightface.app import FaceAnalysis
U = "/root/.claude/uploads/31472ba1-8ea5-51fc-a7e6-64ea60291e16/"
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/song/real/"; os.makedirs(S, exist_ok=True)
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1, det_size=(640, 640))
ref = [max(app.get(cv2.imread(U + f)), key=lambda f: f.bbox[2] - f.bbox[0]).normed_embedding for f in ("4771e5fb-image.jpg", "6bbbf1de-image.jpg")]
ref = np.mean(ref, 0)
PHOTOS = ["4771e5fb", "0d4b2cdd", "4c97b472", "f39692e2", "6bbbf1de", "40b14343", "4349b72b", "adc158f9", "b2805a1c", "13cfe65a", "4ece7045"]
GROUP = {"13cfe65a", "4ece7045"}
for k in PHOTOS:
    img = cv2.imread(U + k + "-image.jpg"); H, W = img.shape[:2]
    f = max(app.get(img), key=lambda f: float(f.normed_embedding @ ref))   # her face
    x0, y0, x1, y1 = f.bbox; fw, fh = x1 - x0, y1 - y0; cx = (x0 + x1) / 2
    if k in GROUP:   # crop just her (no man / other girl): ~2.6 face widths wide, 9:14
        w = min(W, fw * 2.6); h = min(H, w / 0.62); left = int(np.clip(x0 - fw * 0.3, 0, W - w))   # start just left of her face (the man is close on the left)
        top = int(np.clip(y0 - fh * 1.0, 0, H - h))
        c = img[top:top + int(h), left:left + int(w)]
    else:            # keep full width, trim empty sky/floor so she is bigger
        h = min(H, W / 0.56); top = int(np.clip(y0 - fh * 1.6, 0, H - h)); c = img[top:top + int(h)]
    if c.shape[1] < 900: c = cv2.resize(c, None, fx=900 / c.shape[1], fy=900 / c.shape[1], interpolation=cv2.INTER_LANCZOS4)
    cv2.imwrite(S + k + ".jpg", c, [cv2.IMWRITE_JPEG_QUALITY, 94]); print(k, c.shape[1], "x", c.shape[0], "sim", round(float(f.normed_embedding @ ref), 2))
