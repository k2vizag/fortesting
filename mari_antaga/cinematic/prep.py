# Cut the collage into panels, paint out the baked-in text, upscale, make blurred backgrounds.
# usage: python3 prep.py collage.png outdir
import sys, os, cv2, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
img = cv2.imread(src)
# name: (crop x0,y0,x1,y1), [text boxes to inpaint]  (collage coordinates, 941x1672)
P = {
 'A': ((0,0,292,286),     [(190,55,305,118)]),
 'B': ((335,0,602,286),   [(488,58,600,122)]),
 'C': ((652,0,941,286),   [(800,48,925,130)]),
 'D': ((0,296,296,590),   [(215,340,308,432)]),
 'E': ((345,296,612,590), [(528,345,630,428)]),
 'F': ((655,296,941,590), [(828,340,935,432)]),
 'G': ((0,600,276,850),   [(140,600,240,692),(198,625,252,668,'full')]),
 'H': ((292,600,568,792), []),
 'I': ((598,600,941,850), [(688,600,832,672),(678,620,702,646,'full')]),
 'J': ((0,858,296,1048),  [(165,865,292,928)]),
 'K': ((322,868,642,1048),[(482,873,645,936)]),
 'L': ((666,858,941,1048),[(797,862,938,967),(800,926,822,966,'full')]),
 'M': ((0,1058,262,1278), [(90,1060,240,1100),(138,1095,200,1126)]),
 'N': ((316,1058,580,1286),[(420,1060,605,1118),(388,1060,420,1098),(412,1074,448,1116,'full'),(524,1082,562,1126,'full')]),
 'O': ((610,1058,941,1286),[(708,1065,912,1104)]),
 'P': ((0,1292,941,1672), [(565,1315,885,1452)]),
}
mask = np.zeros(img.shape[:2], np.uint8)
for _, boxes in P.values():
    for b in boxes:
        x0,y0,x1,y1 = b[:4]
        if len(b) > 4: mask[y0:y1, x0:x1] = 255; continue
        roi = img[y0:y1, x0:x1]
        dark = (roi.max(2) < 120).astype(np.uint8)*255
        light = (roi.min(2) > 175).astype(np.uint8)*255
        halo = cv2.dilate(dark, np.ones((13,13),np.uint8)) & light      # white outline around letters
        m = cv2.dilate(dark | halo, np.ones((5,5),np.uint8), iterations=2)
        mask[y0:y1, x0:x1] |= m
clean = cv2.inpaint(img, mask, 6, cv2.INPAINT_TELEA)
# put texture back into the filled patches: rain streaks (B,E), snow dots (C,F), grain everywhere
rng = np.random.default_rng(4)
tex = clean.astype(np.float32).copy()
grain = np.repeat(rng.normal(0, 4, clean.shape[:2])[...,None], 3, 2).astype(np.float32)
tex += grain * (mask[...,None] > 0)
layer = np.zeros(clean.shape, np.float32); alpha = np.zeros(clean.shape[:2], np.float32)
for key in 'BE':
    x0,y0,x1,y1 = P[key][1][0]
    for _ in range(140):
        x = rng.uniform(x0-10, x1+10); y = rng.uniform(y0-20, y1); L = rng.uniform(14, 34)
        cv2.line(alpha, (int(x), int(y)), (int(x - L*0.12), int(y + L)), float(rng.uniform(.25,.6)), 1, cv2.LINE_AA)
for key in 'CF':
    x0,y0,x1,y1 = P[key][1][0]
    for _ in range(70):
        cv2.circle(alpha, (int(rng.uniform(x0,x1)), int(rng.uniform(y0,y1))), int(rng.integers(1,3)), float(rng.uniform(.5,.95)), -1, cv2.LINE_AA)
alpha *= cv2.GaussianBlur((mask>0).astype(np.float32), (15,15), 0)
layer[:] = (235, 235, 235)
tex = tex*(1-alpha[...,None]) + layer*alpha[...,None]
clean = np.clip(tex, 0, 255).astype(np.uint8)
cv2.imwrite(os.path.join(out,'_clean.png'), clean)
pil = Image.fromarray(cv2.cvtColor(clean, cv2.COLOR_BGR2RGB))
for k,((x0,y0,x1,y1),_) in P.items():
    c = pil.crop((x0,y0,x1,y1)); W = 960; H = round(c.height*W/c.width)
    up = c.resize((W,H), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=2.2, percent=90, threshold=2))
    up = ImageEnhance.Color(up).enhance(1.08)
    up.save(os.path.join(out,f'{k}.jpg'), quality=93)
    bg = c.resize((270, round(270*c.height/c.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(14))
    bg = ImageEnhance.Brightness(bg).enhance(.62)
    bg.save(os.path.join(out,f'{k}_bg.jpg'), quality=90)
print('ok')
