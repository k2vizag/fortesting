"""Refine the RVM person matte with a clean-plate difference key (static phone camera).
 - removes left-over office pieces that RVM kept near the person (pixel == empty office -> background)
 - adds back fast-moving / blurred hands that RVM dropped (pixel != empty office, touching the person)
usage: refine.py base.mov alpha.mkv timeline.json plate_stack.npz out_alpha.mkv
For every cut a time-local clean plate is built from the stack (frames within +-WIN s of the cut, person masked out),
because the office changed during the recording; the cut's crop from timeline.json is then applied to it.
Pixels never seen empty near that time are left to RVM alone."""
import json, subprocess, sys
import cv2, numpy as np

W, H = 1080, 1920
base, alpha_in, tl_path, stack_path, out = sys.argv[1:6]
T = json.load(open(tl_path)); P = T["pieces"]
ST = np.load(stack_path)
SF, SM, STM = ST["frames"], ST["masks"].astype(bool), ST["times"]      # half-res RGB (540x960), person masks, raw secs
WIN, MIN_SEEN = 25.0, 4

def ss(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1); return t * t * (3 - 2 * t)

cache = {}
def plate_for(k):
    if k not in cache:
        a, b, _, _, x0, y0, cw, ch = P[k]
        sel = (STM >= a - WIN) & (STM <= b + WIN)
        F = SF[sel].astype(np.float32); F[SM[sel]] = np.nan
        with np.errstate(all="ignore"):
            pl = np.nanmedian(F, axis=0)
        seen = (~SM[sel]).sum(0).astype(np.float32)
        pl = cv2.cvtColor(np.nan_to_num(pl).clip(0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
        s4 = 4.0                                   # stack is raw/4; crop numbers are in raw (2160x3840) pixels
        M = np.float32([[W / (cw / s4), 0, -(x0 / s4) * W / (cw / s4)], [0, H / (ch / s4), -(y0 / s4) * H / (ch / s4)]])
        pl = cv2.warpAffine(pl, M, (W, H), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
        sn = cv2.warpAffine(seen, M, (W, H), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_REPLICATE)
        lab = cv2.cvtColor(cv2.GaussianBlur(pl, (0, 0), 2.0), cv2.COLOR_BGR2LAB).astype(np.float32)
        cache.clear(); cache[k] = (lab, sn >= MIN_SEEN)
    return cache[k]

def piece_at(t):
    for k, p in enumerate(P):
        if p[2] <= t < p[3]: return k
    return None

K_CORE = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31))
K_RING = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (81, 81))
prev_gate = None; prev_k = None

def refine(f, a8, k):
    global prev_gate, prev_k
    a = a8.astype(np.float32) / 255.0
    lab_p, valid = plate_for(k)
    lab_f = cv2.cvtColor(cv2.GaussianBlur(f, (0, 0), 2.0), cv2.COLOR_BGR2LAB).astype(np.float32)
    # exposure match on sure-background pixels (phone auto-exposure drifts a little)
    bgsure = (a < 0.01) & valid
    if bgsure.sum() > 5000:
        lab_f[..., 0] += float(np.median(lab_p[..., 0][bgsure] - lab_f[..., 0][bgsure]))
    d = lab_f - lab_p
    dist = np.sqrt(0.5 * d[..., 0] ** 2 + d[..., 1] ** 2 + d[..., 2] ** 2)
    core = cv2.erode((a > 0.6).astype(np.uint8), K_CORE).astype(bool)
    ring = cv2.dilate((a > 0.03).astype(np.uint8), K_RING).astype(bool) & ~core & valid
    # 1) remove: near-identical to the empty office -> background
    gate = ss(dist, 7.0, 17.0)
    if prev_gate is not None and prev_k == k: gate = 0.6 * gate + 0.4 * prev_gate    # calm flicker
    prev_gate, prev_k = gate, k
    a_new = a.copy()
    a_new[ring] = np.minimum(a[ring], gate[ring])
    # 2) add back: clearly different from the office, attached to the person (blurred moving hands)
    near = cv2.dilate((a > 0.5).astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (41, 41))).astype(bool)
    add = ss(dist, 22.0, 40.0) * ring * ((a > 0.03) | near)
    cand = (add > 0.5).astype(np.uint8) | (a_new > 0.5).astype(np.uint8)
    n, lab = cv2.connectedComponents(cand, connectivity=8)
    body = np.unique(lab[core]); body = body[body > 0]
    attached = np.isin(lab, body)
    a_new = np.where(attached & ring, np.maximum(a_new, add), a_new)
    # tidy: drop tiny islands of background that survived, light feather
    isl = (a_new > 0.5).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(isl, connectivity=8)
    big = np.zeros(n, bool); big[1:] = st[1:, cv2.CC_STAT_AREA] > 4000
    keep = big[lab] | (a_new <= 0.5)
    a_new = np.where(keep, a_new, 0)
    a_new = cv2.GaussianBlur(a_new, (0, 0), 0.8)
    return (a_new * 255 + 0.5).clip(0, 255).astype(np.uint8)

if __name__ == "__main__":
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", base, "-f", "rawvideo", "-pix_fmt", "bgr24", "-"], stdout=subprocess.PIPE)
    dea = subprocess.Popen(["ffmpeg", "-v", "error", "-i", alpha_in, "-f", "rawvideo", "-pix_fmt", "gray", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30",
                            "-i", "-", "-c:v", "ffv1", out], stdin=subprocess.PIPE)
    n = 0
    while True:
        b = dec.stdout.read(W * H * 3); m = dea.stdout.read(W * H)
        if len(b) < W * H * 3 or len(m) < W * H: break
        f = np.frombuffer(b, np.uint8).reshape(H, W, 3); a8 = np.frombuffer(m, np.uint8).reshape(H, W)
        k = piece_at((n + 0.5) / 30)
        enc.stdin.write((refine(f, a8, k) if (k is not None and f.max() >= 20) else a8).tobytes()); n += 1
        if n % 300 == 0: print(n, flush=True)
    enc.stdin.close(); enc.wait(); print("done", n)
