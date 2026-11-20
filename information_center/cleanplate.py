"""Clean background plate of the (static) phone shot: per-pixel median over frames where RVM says 'no person'.
usage: cleanplate.py <rvm.onnx> raw.mp4 out_plate.png [fps]
Also saves out_plate_stack.npz (half-res frames + person masks + raw times) so refine.py can build a
time-local plate per cut (the office changes during the recording: items moved on the shelf).
Works on the full uncropped frame at 1080x1920 (raw 2160x3840 / 2), same sharpen/eq as build.py."""
import subprocess, sys
import cv2, numpy as np, onnxruntime as ort

W, H = 1080, 1920
model, raw, out = sys.argv[1:4]
fps = sys.argv[4] if len(sys.argv) > 4 else "2"
sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])
dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", raw, "-vf",
                        f"fps={fps},scale={W}:{H}:flags=lanczos,unsharp=5:5:0.55:5:5:0.0,eq=contrast=1.04:saturation=1.08",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
frames, masks = [], []
rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
ds = np.array([0.375], np.float32)
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    x = (f.astype(np.float32) / 255).transpose(2, 0, 1)[None]
    for _ in range(2):   # sparse frames: run twice so the recurrent state settles on this frame
        _, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ds})
    person = cv2.dilate((pha[0, 0] > 0.02).astype(np.uint8), np.ones((61, 61), np.uint8))   # keep well away from the person
    frames.append(cv2.resize(f, (W // 2, H // 2), interpolation=cv2.INTER_AREA))
    masks.append(cv2.resize(person, (W // 2, H // 2), interpolation=cv2.INTER_NEAREST))
np.savez(out.replace(".png", "_stack.npz"), frames=np.stack(frames), masks=np.stack(masks),
         times=np.arange(len(frames)) / float(fps))
F = np.stack(frames).astype(np.float32); M = np.stack(masks).astype(bool)
print("frames", len(F))
F[M] = np.nan
plate = np.nanmedian(F, axis=0)
cover = (~M).sum(0)
hole = np.isnan(plate[..., 0]).astype(np.uint8)
plate = np.nan_to_num(plate).clip(0, 255).astype(np.uint8)
plate = cv2.inpaint(plate, hole, 9, cv2.INPAINT_TELEA)            # never-seen area (behind the torso)
plate = cv2.resize(plate, (W, H), interpolation=cv2.INTER_CUBIC)
cv2.imwrite(out, cv2.cvtColor(plate, cv2.COLOR_RGB2BGR))
cv2.imwrite(out.replace(".png", "_cover.png"), cv2.resize((np.clip(cover / max(1, cover.max()), 0, 1) * 255).astype(np.uint8), (W, H)))
print("never-seen fraction", round(float(hole.mean()), 3))
