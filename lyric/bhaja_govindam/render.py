"""Cinematic 9:16 lyric video: "ఉన్నంతలో మనకున్నంతలో" (Bhaja Govindam – Reality).

Visuals: the user's 8 scene-board images (upscaled 4x with Real-ESRGAN, depth from
Depth-Anything-V2) animated with 2.5D depth-parallax camera moves.

usage: python3 -I render.py <panels_dir> <song.mp4> <out.mp4> [silent_out.mp4] [--preview t1,t2,..]
panels_dir must contain u1..u8.png (upscaled images) and d1..d8.npy (depth, 0=far 1=near).
"""
import os, subprocess, sys
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS, TOTAL = 1080, 1920, 30, 60.0
FG_W, FG_H, FG_Y = 1080, 900, 300          # foreground (parallax) window
TXT_Y = 1420                               # lyric centre line
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, '..', '..', 'insurance', 'v2', 'fonts', 'TeluguCap800.ttf')

# ---- lyrics: (start, end, text, highlighted part) – timing from the song's own lyric video
LY = [
    (0.0, 1.8, 'ఉన్నంతలో మనకున్నంతలో', ''), (1.8, 4.4, 'బతికితే అదే సుఖము', 'అదే సుఖము'),
    (4.4, 6.6, 'ఎవరికి తలలొంచకా', ''), (6.6, 8.2, 'నువ్వు నీ కాళ్లపై', ''), (8.2, 10.0, 'నిలబడే గుణం వరము', 'గుణం వరము'),
    (10.0, 11.6, 'ఏదెలాగ రాసెనో', ''), (11.6, 13.1, 'అలాగే జరుగును', ''), (13.1, 15.1, 'మరెందుకో భయము', 'భయము'),
    (15.1, 16.9, 'అది అలాగ జరగక', ''), (16.9, 18.1, 'ఎలాగ జరిగిన', ''), (18.1, 20.6, 'వదులుకోకు ఎప్పుడు నమ్మకము', 'నమ్మకము'),
    (20.6, 22.6, 'ఏవో తెలియని', ''), (22.6, 24.6, 'పరుగులు తీసే', ''), (24.6, 25.6, 'తొందరలో', 'తొందరలో'),
    (25.6, 28.6, 'నీకే నువ్వే దొరకక', ''), (28.6, 29.6, 'సమయము గడపకు', ''), (29.6, 30.6, 'తెలివను భ్రమలో', 'తెలివను భ్రమలో'),
    (30.6, 33.6, 'చాలా ఆశల నడుమన', ''), (33.6, 36.1, 'చాల్లే అన్ని చూడు', 'చూడు'),
    (36.1, 39.1, 'ప్రాణం చిటికెలో తేలును', ''), (39.1, 41.3, 'ఆనందాల్లో...', 'ఆనందాల్లో...'),
    (41.3, 46.3, 'భజ గోవిందం భజ గోవిందం', '*'), (46.3, 51.3, 'బ్రతుకే కోలాహలం', '*'),
    (51.3, 56.3, 'భజ గోవిందం భజ గోవిందం', '*'), (56.3, 59.6, 'బరువే కాదే క్షణం', '*'),
]
# ---- scenes: (start, end, image, (cx0,cy0)->(cx1,cy1) as fractions, zoom0->zoom1, depth-zoom, depth-pan px)
SC = [
    (0.0, 4.4, 1, (0.40, 0.48), (0.46, 0.50), 1.10, 1.24, 0.07, -30),   # relaxed, content
    (4.4, 10.0, 2, (0.42, 0.55), (0.42, 0.36), 1.04, 1.24, 0.09, 0),    # standing on own feet – push in, tilt up
    (10.0, 15.1, 3, (0.50, 0.62), (0.52, 0.50), 1.04, 1.26, 0.06, 20),  # book of fate – toward the light
    (15.1, 20.6, 4, (0.38, 0.50), (0.72, 0.48), 1.10, 1.06, 0.05, -40), # pan right to the signboards
    (20.6, 25.6, 5, (0.55, 0.50), (0.58, 0.48), 1.04, 1.38, 0.14, 45),  # rushing crowd – fast push
    (25.6, 30.6, 6, (0.55, 0.45), (0.50, 0.50), 1.32, 1.06, 0.07, 25),  # lost in time – pull out
    (30.6, 36.1, 7, (0.50, 0.52), (0.52, 0.45), 1.06, 1.24, 0.06, -20), # family – what really matters
    (36.1, 41.3, 8, (0.50, 0.50), (0.56, 0.52), 1.28, 1.04, 0.05, -25), # joy – pull out to the sunset
]
# chorus montage: cut every 4 beats from 41.33, recap of all images, end on the bench
BEATS = [41.33, 43.24, 45.00, 46.90, 48.69, 50.60, 52.50, 54.27, 56.19]
MONT = [1, 2, 3, 4, 5, 6, 7, 2, 8]
for i, t0 in enumerate(BEATS):
    t1 = BEATS[i + 1] if i + 1 < len(BEATS) else TOTAL
    im = MONT[i]; d = 1 if i % 2 == 0 else -1
    if i == len(BEATS) - 1:
        SC.append((t0, t1, im, (0.48, 0.50), (0.55, 0.52), 1.30, 1.02, 0.06, -20))
    elif im == 4:
        SC.append((t0, t1, im, (0.66, 0.5), (0.72, 0.48), 1.04, 1.12, 0.08, 30 * d))
    else:
        SC.append((t0, t1, im, (0.5 - 0.04 * d, 0.5), (0.5 + 0.04 * d, 0.48), 1.08, 1.22, 0.10, 30 * d))
SC[7] = SC[7][:1] + (41.33,) + SC[7][2:]

ease = lambda v: float(np.clip(v, 0, 1)) ** 2 * (3 - 2 * float(np.clip(v, 0, 1)))


def load(panels):
    imgs, deps, bgs = {}, {}, {}
    for n in range(1, 9):
        f = os.path.join(panels, f'u{n}.png')
        im = cv2.imread(f if os.path.exists(f) else os.path.join(panels, f'u{n}.jpg')).astype(np.float32)
        f = os.path.join(panels, f'd{n}.npy')   # repo copy: 16-bit PNG
        d = np.load(f).astype(np.float32) if os.path.exists(f) else cv2.imread(os.path.join(panels, f'd{n}.png'), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535
        d = cv2.GaussianBlur(d, (0, 0), 3)                       # soften depth edges -> fewer tears
        imgs[n], deps[n] = im, d
        # blurred, darkened full-frame background
        h, w = im.shape[:2]; s = max(W / w, H / h) * 1.15
        bg = cv2.resize(im, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        y0, x0 = (bg.shape[0] - H) // 2, (bg.shape[1] - W) // 2
        bg = cv2.GaussianBlur(bg[y0:y0 + H, x0:x0 + W], (0, 0), 45) * 0.42
        bgs[n] = bg
    return imgs, deps, bgs


GX, GY = np.meshgrid(np.arange(FG_W, dtype=np.float32) - FG_W / 2, np.arange(FG_H, dtype=np.float32) - FG_H / 2)
FEATHER = np.ones((FG_H, 1), np.float32)
for i in range(140):
    FEATHER[i] = FEATHER[FG_H - 1 - i] = (i / 140) ** 1.5
FEATHER = FEATHER[..., None]


def scene_frame(sc, t, imgs, deps, bgs, punch=0.0):
    t0, t1, n, c0, c1, z0, z1, kz, kd = sc
    p = ease((t - t0) / (t1 - t0))
    im, D = imgs[n], deps[n]; h, w = im.shape[:2]
    z = (z0 + (z1 - z0) * p) * (1 + punch)
    s = FG_H / h * z
    hw, hh = FG_W / 2 / s, FG_H / 2 / s
    cx = np.clip((c0[0] + (c1[0] - c0[0]) * p) * w, hw + 4, w - hw - 4)
    cy = np.clip((c0[1] + (c1[1] - c0[1]) * p) * h, hh + 4, h - hh - 4)
    u = (cx + GX / s).astype(np.float32); v = (cy + GY / s).astype(np.float32)
    d = cv2.remap(D, u, v, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # 2.5D: near pixels (d~1) get extra zoom and opposite pan -> parallax
    k = 1 + kz * p * d
    u2 = cx + (u - cx) / k - kd * (p - 0.5) * d
    v2 = (cy + (v - cy) / k).astype(np.float32); u2 = u2.astype(np.float32)
    fg = cv2.remap(im, u2, v2, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    # background drifts slowly
    bg = bgs[n]
    sh = int(20 * (p - 0.5))
    bg = np.roll(bg, sh, axis=1)
    out = bg.copy()
    reg = out[FG_Y:FG_Y + FG_H]
    out[FG_Y:FG_Y + FG_H] = reg * (1 - FEATHER) + fg * FEATHER
    return out


# ---- effects ----
R = np.random.default_rng(7)
DUST = [(R.random() * W, R.random() * H, 1.5 + R.random() * 4.5, 8 + R.random() * 30, R.random() * 6.28, 0.25 + R.random() * 0.6) for _ in range(70)]
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.55 * np.clip(((XX - W / 2) ** 2 / (W * 0.75) ** 2 + (YY - H / 2) ** 2 / (H * 0.62) ** 2), 0, 1) ** 1.3)[..., None]
GRAIN = [R.normal(0, 5, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]


def effects(img, t, flash):
    # warm light leak drifting across the top
    lx = W * (0.2 + 0.6 * (0.5 + 0.5 * np.sin(t * 0.35))); ly = H * 0.22
    leak = np.exp(-(((XX - lx) / 520) ** 2 + ((YY - ly) / 420) ** 2))[..., None]
    img = img + leak * np.array([40, 110, 190], np.float32) * (0.35 + 0.9 * flash)
    if flash > 0:
        img = img + flash * np.array([150, 205, 255], np.float32)
    # floating golden dust
    ov = np.zeros((H, W), np.float32)
    for (x, y, r, sp, ph, a) in DUST:
        yy = (y - t * sp) % H; xx = (x + 25 * np.sin(t * 0.6 + ph)) % W
        cv2.circle(ov, (int(xx), int(yy)), int(r), a * (0.6 + 0.4 * np.sin(t * 2 + ph)), -1, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 2.2)[..., None]
    img = img + ov * np.array([120, 200, 255], np.float32)
    # grade: gentle S-curve + vignette + grain
    img = np.clip(img, 0, 255) / 255
    img = img * img * (3 - 2 * img) * 0.35 + img * 0.65
    img = img * 255 * VIG
    g = cv2.resize(GRAIN[int(t * FPS) % len(GRAIN)], (W, H), interpolation=cv2.INTER_NEAREST)[..., None]
    return np.clip(img + g, 0, 255)


# ---- lyric text sprites (Telugu shaping via raqm) ----
def sprite(text, hl):
    size = 96 if hl == '*' else 84
    while True:
        f = ImageFont.truetype(FONT, size, layout_engine=ImageFont.Layout.RAQM)
        if f.getlength(text) < 960 or size < 50:
            break
        size -= 4
    tw = int(f.getlength(text)) + 120; th = size * 2 + 80
    gold, white = (255, 200, 90, 255), (255, 250, 240, 255)
    parts = [(text, gold if hl == '*' else white)]
    if hl and hl != '*' and hl in text:
        a = text.index(hl); parts = [(text[:a], white), (hl, gold), (text[a + len(hl):], white)]
    txt = Image.new('RGBA', (tw, th), (0, 0, 0, 0)); dr = ImageDraw.Draw(txt)
    x = 60; y = th // 2
    for s, col in parts:
        if s:
            dr.text((x, y), s, font=f, fill=col, anchor='lm'); x += f.getlength(s)
    a = txt.split()[3]
    shadow = Image.new('RGBA', txt.size, (0, 0, 0, 0)); shadow.putalpha(a.filter(ImageFilter.GaussianBlur(14)).point(lambda v: min(255, v * 2)))
    glow = Image.new('RGBA', txt.size, (255, 190, 90, 0)); glow.putalpha(a.filter(ImageFilter.GaussianBlur(26)).point(lambda v: v * 0.7))
    outl = Image.new('RGBA', txt.size, (0, 0, 0, 0)); outl.putalpha(a.filter(ImageFilter.MaxFilter(5)).point(lambda v: v * 0.55))
    im = Image.alpha_composite(Image.alpha_composite(Image.alpha_composite(shadow, glow), outl), txt)
    arr = np.array(im).astype(np.float32)
    return arr[..., [2, 1, 0]], arr[..., 3:] / 255


def put_text(img, t, sprites):
    for (a, b, text, hl), (rgb, al) in zip(LY, sprites):
        if not (a <= t < b):
            continue
        u = t - a; k = ease(u / 0.25) * ease((b - t) / 0.2)
        sc = 1.0 + 0.06 * (1 - ease(u / 0.35))
        if sc != 1.0:
            rgb = cv2.resize(rgb, None, fx=sc, fy=sc); al = cv2.resize(al, None, fx=sc, fy=sc)[..., None]
        h, w = al.shape[:2]
        y0 = int(TXT_Y - h / 2 + 24 * (1 - ease(u / 0.35))); x0 = int(W / 2 - w / 2)
        xs, xe = max(0, x0), min(W, x0 + w); ys, ye = max(0, y0), min(H, y0 + h)
        A = al[ys - y0:ye - y0, xs - x0:xe - x0] * k
        img[ys:ye, xs:xe] = img[ys:ye, xs:xe] * (1 - A) + rgb[ys - y0:ye - y0, xs - x0:xe - x0] * A
    return img


def frame(t, imgs, deps, bgs, sprites):
    i = max(j for j, s in enumerate(SC) if s[0] <= t + 1e-6)
    sc = SC[i]
    chorus = sc[0] >= 41.3
    punch = 0.05 * (1 - ease((t - sc[0]) / 0.35)) if chorus else 0.0
    img = scene_frame(sc, t, imgs, deps, bgs, punch)
    flash = 0.0
    if not chorus and i + 1 < len(SC) and t > sc[1] - 0.45:        # crossfade into the next scene
        k = ease((t - (sc[1] - 0.45)) / 0.45)
        img = img * (1 - k) + scene_frame(SC[i + 1], t, imgs, deps, bgs) * k
    for s in SC[1:]:                                                # golden flash on every cut
        dt = t - s[0]
        if -0.12 < dt < 0.35:
            amp = 0.55 if s[0] < 41.3 else 0.75
            flash = max(flash, amp * (1 - abs(dt) / (0.12 if dt < 0 else 0.35)))
    img = effects(img, t, flash)
    img = put_text(img, t, sprites)
    if t > TOTAL - 0.7:
        img = img * (1 - ease((t - (TOTAL - 0.7)) / 0.7))
    if t < 0.3:
        img = img * ease(t / 0.3)
    return np.clip(img, 0, 255).astype(np.uint8)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    panels, song, out = args[0], args[1], args[2]
    silent = args[3] if len(args) > 3 else out.replace('.mp4', '_nomusic.mp4')
    imgs, deps, bgs = load(panels)
    sprites = [sprite(x[2], x[3]) for x in LY]
    if '--preview' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--preview') + 1].split(',')]
        for t in ts:
            cv2.imwrite(os.path.join(out, f'f_{t:05.2f}.jpg'), frame(t, imgs, deps, bgs, sprites))
        return
    ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(FPS),
                           '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', silent], stdin=subprocess.PIPE)
    N = int(TOTAL * FPS)
    for i in range(N):
        ff.stdin.write(frame(i / FPS, imgs, deps, bgs, sprites).tobytes())
        if i % 150 == 0:
            print(f'frame {i}/{N}', flush=True)
    ff.stdin.close(); ff.wait()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', silent, '-i', song, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-t', str(TOTAL), '-movflags', '+faststart', out], check=True)
    print('done', out, silent)


if __name__ == '__main__':
    main()
