"""Swap the male / female faces in the song photos with the user's own photos (inswapper_128) + GFPGAN v1.4 face restore.
Writes <scratchpad>/song/swap/<name>.png ; build.py uses these when present."""
import os, cv2, numpy as np, torch, insightface
from insightface.app import FaceAnalysis
from spandrel import ModelLoader
U = "/root/.claude/uploads/31472ba1-8ea5-51fc-a7e6-64ea60291e16/"
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/song/"
os.makedirs(S + "swap", exist_ok=True)
app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"]); app.prepare(ctx_id=-1, det_size=(640, 640))
swapper = insightface.model_zoo.get_model(S + "model/inswapper_128.onnx", providers=["CPUExecutionProvider"])
gfp = ModelLoader().load_from_file(S + "model/GFPGANv1.4.pth").eval()
big = lambda fs: max(fs, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))
def source(files):   # average identity over several photos of the same person
    fs = [big(app.get(cv2.imread(U + f))) for f in files]
    src = fs[0]; e = np.mean([f.normed_embedding for f in fs], 0); src.embedding = e / np.linalg.norm(e) * np.linalg.norm(fs[0].embedding)
    return src
MALE = source(["13cfe65a-image.jpg", "09e70d6e-image.jpg", "4ece7045-image.jpg"])   # biggest face in each selfie = the user
FEMALE = source(["b2805a1c-image.jpg", "6bbbf1de-image.jpg", "adc158f9-image.jpg"])  # Diwali photos
T512 = np.array([[192.98138, 239.94708], [318.90277, 240.1936], [256.63416, 314.01935], [201.26117, 371.41043], [313.08905, 371.15118]], np.float32)
def restore(img, face, w=0.6):
    M = cv2.estimateAffinePartial2D(face.kps.astype(np.float32), T512)[0]
    crop = cv2.warpAffine(img, M, (512, 512), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    x = torch.from_numpy(crop[:, :, ::-1].copy()).permute(2, 0, 1).float().unsqueeze(0) / 255
    with torch.no_grad(): y = gfp((x - 0.5) / 0.5)
    y = y[0] if isinstance(y, (tuple, list)) else y
    y = ((y.clamp(-1, 1) + 1) / 2)[0].permute(1, 2, 0).numpy()[:, :, ::-1] * 255
    out = cv2.addWeighted(y.astype(np.float32), w, crop.astype(np.float32), 1 - w, 0)
    Mi = cv2.invertAffineTransform(M); H, W = img.shape[:2]
    back = cv2.warpAffine(out, Mi, (W, H), flags=cv2.INTER_LINEAR)
    # blend only inside the real face outline (106 landmarks), so profile faces don't get a ghost face beside them
    mk = np.zeros((H, W), np.float32); hull = cv2.convexHull(face.landmark_2d_106.astype(np.int32))
    cv2.fillConvexPoly(mk, hull, 1.0); r = max(3, int((face.bbox[2] - face.bbox[0]) * 0.06))
    mk = cv2.erode(mk, np.ones((r, r), np.uint8)); mk = cv2.GaussianBlur(mk, (0, 0), r)[:, :, None]
    return (back * mk + img.astype(np.float32) * (1 - mk)).clip(0, 255).astype(np.uint8)
HQ = S + "hq/"
TARGETS = {"peanut": (U + "95fc2b4b-image.png", MALE), "pot": (HQ + "pot.png", MALE), "tamarind": (HQ + "tamarind.png", MALE),
           "moonman": (U + "f34ab5e4-image.png", MALE),
           "f_lachimi": (HQ + "f_lachimi.png", FEMALE), "f_white": (HQ + "f_white.png", FEMALE), "f_purple": (U + "0e74cace-image.png", FEMALE),
           "pasupu": (U + "d408a773-image.png", FEMALE), "f_yellow": (HQ + "f_yellow.png", FEMALE), "f_moon": (U + "73f382a6-image.png", FEMALE)}
import sys
for name, (path, src) in TARGETS.items():
    if len(sys.argv) > 1 and name not in sys.argv[1:]: continue
    img = cv2.imread(path); fs = app.get(img)
    if not fs: print(name, "NO FACE"); continue
    f = big(fs); img = swapper.get(img, f, src, paste_back=True)
    f2 = big(app.get(img)) if app.get(img) else f
    img = restore(img, f2)
    cv2.imwrite(S + f"swap/{name}.png", img); print(name, "ok", img.shape[1], "x", img.shape[0], flush=True)
