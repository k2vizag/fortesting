"""Person matting with Robust Video Matting (ONNX, recurrent -> temporally stable edges).
usage: matte.py <rvm.onnx> in.mov out_alpha.mkv [timeline.json]
With timeline.json the recurrent state is reset at every cut (new framing) and the first frame of each
cut is run 3x so the state settles before it is used.   writes the alpha matte as a gray video (FFV1, lossless)"""
import subprocess, sys, time
import numpy as np, onnxruntime as ort

W, H = 1080, 1920
model, src, dst = sys.argv[1:4]
import json
ss = []
STARTS = set()
if len(sys.argv) > 4:
    STARTS = {int(round(p[2] * 30)) for p in json.load(open(sys.argv[4]))["pieces"]}
so = ort.SessionOptions(); so.intra_op_num_threads = 4
sess = ort.InferenceSession(model, so, providers=["CPUExecutionProvider"])
rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
ds = np.array([0.375], np.float32)
dec = subprocess.Popen(["ffmpeg", "-v", "error", *ss, "-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}", "-r", "30", "-i", "-",
                        "-c:v", "ffv1", dst], stdin=subprocess.PIPE)
n, t0, prev_black = 0, time.time(), True
while True:
    b = dec.stdout.read(W * H * 3)
    if len(b) < W * H * 3: break
    f = np.frombuffer(b, np.uint8).reshape(H, W, 3)
    if f.max() < 20:                       # black intro / end frames: no person, reset the recurrent state
        a = np.zeros((H, W), np.uint8); rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
    else:
        x = (f.astype(np.float32) / 255).transpose(2, 0, 1)[None]
        reps = 1
        if any(abs(n - s0) <= 1 for s0 in STARTS):          # first frames of a cut: fresh state, let it settle
            if n in STARTS or n - 1 in STARTS or n + 1 in STARTS:
                if n in STARTS: rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4
                reps = 3 if n in STARTS else 1
        for _ in range(reps):
            fgr, pha, *rec = sess.run(None, {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ds})
        a = (pha[0, 0] * 255 + 0.5).clip(0, 255).astype(np.uint8)
    enc.stdin.write(a.tobytes()); n += 1
    if n % 300 == 0: print(f"{n} frames {time.time() - t0:.0f}s", flush=True)
enc.stdin.close(); enc.wait(); print("done", n)
