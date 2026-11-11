"""Build base.mov (1080x1920, 30 fps, no overlays) and voice.wav (cleaned AI voice only; all other audio muted)."""
import os, subprocess, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.dirname(__file__))
from segs import SEGS, RAW, W, S, FPS, END_SCREEN, frames, timeline

os.makedirs(W, exist_ok=True)
SHARP = "unsharp=5:5:0.55:5:5:0"


def vf_for(i, seg):
    src, a, b, sp, kind, z = seg
    if kind == "ai" and src == "v7":   # landscape AI clip: 3:4 centre crop on a blurred fill
        cw, ch = int(540 / z) // 2 * 2, int(720 / z) // 2 * 2
        return (f"split[bg][fg];[bg]scale=-2:1920,crop=1080:1920,boxblur=40:2,eq=brightness=-0.08[bg2];"
                f"[fg]crop={cw}:{ch}:(iw-{cw})/2:(ih-{ch})/2,scale=1080:1440:flags=lanczos,{SHARP}[fg2];"
                f"[bg2][fg2]overlay=0:250,fps={FPS},setsar=1")
    if kind == "ai":
        return (f"scale={int(1080*z)//2*2}:{int(1920*z)//2*2}:flags=lanczos,crop=1080:1920,{SHARP},fps={FPS},setsar=1")
    if kind == "yt":   # 2x, then blur the burned-in text band at the bottom
        return (f"setpts=PTS/{sp},fps={FPS},scale=1080:1920:flags=lanczos,{SHARP},split[m][c];"
                f"[c]crop=1080:470:0:1370,boxblur=28:3,eq=brightness=-0.18[bl];[m][bl]overlay=0:1370,setsar=1")
    # real phone clips: 4K -> 1080p, stabilise, denoise, sharpen, colour
    trf = f"{W}/stab{i}.trf"
    col = ("eq=brightness=0.035:gamma=1.12:contrast=1.04:saturation=1.22" if src == "v3"
           else "eq=contrast=1.06:saturation=1.2:gamma=1.03")
    return (f"scale=1080:1920:flags=lanczos,fps={FPS},vidstabtransform=input={trf}:smoothing=18:zoom=4,"
            f"hqdn3d=1.5:1.5:4:4,unsharp=5:5:0.8:3:3:0.3,{col},setsar=1")


parts = []
for i, seg in enumerate(SEGS):
    src, a, b, sp, kind, z = seg
    n = frames(seg)
    out = f"{W}/seg{i:02d}.mp4"
    inp = ["-ss", str(a), "-t", str(b - a + 0.5), "-i", f"{RAW}/{src}.mp4"]   # -t before -i (input option)
    if kind == "real":
        subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-vf",
                        f"scale=1080:1920,fps={FPS},vidstabdetect=shakiness=6:accuracy=12:result={W}/stab{i}.trf",
                        "-frames:v", str(n), "-f", "null", "-"], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", vf_for(i, seg), "-an",
                    "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-pix_fmt", "yuv420p", out],
                   check=True)
    parts.append(out)
    print("seg", i, src, n, "frames")

with open(f"{W}/list.txt", "w") as f:
    for p in parts:
        f.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", f"{W}/list.txt",
                "-vf", f"tpad=stop_mode=clone:stop_duration={END_SCREEN}", "-c:v", "libx264", "-preset", "medium",
                "-crf", "14", "-pix_fmt", "yuv420p", "-r", str(FPS), f"{W}/base.mov"], check=True)

# voice: cleaned (DeepFilterNet) AI audio only, placed on the same frame-exact timeline
SR = 48000
starts, total = timeline()
N = int((total + END_SCREEN) * SR)
voice = np.zeros(N)
for i, seg in enumerate(SEGS):
    src, a, b, sp, kind, z = seg
    if kind != "ai":
        continue
    x, sr = sf.read(f"{S}/{src}_clean.wav")
    n = int(frames(seg) / FPS * SR)
    y = x[int(a * SR):int(a * SR) + n].copy()
    f = int(0.008 * SR)
    y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    o = int(starts[i] * SR)
    voice[o:o + len(y)] += y
sf.write(f"{W}/voice.wav", voice.astype(np.float32), SR, subtype="FLOAT")
print("total", round(total, 2), "+ end", END_SCREEN)
