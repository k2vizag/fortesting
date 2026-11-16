"""Lyric video data: Telugu-script and English-letter (transliterated) versions -> data_te.json / data_en.json
Whole photo (never cropped) in a centred box over a blurred copy, smooth zoom + crossfades, glass lyric card at the top."""
import json
from PIL import Image
U = "/root/.claude/uploads/31472ba1-8ea5-51fc-a7e6-64ea60291e16/"
HQ = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/song/hq/"
# full-size originals; small screenshots are cropped + AI-upscaled by upscale.py; pot photo: burned-in caption cropped off
SRC = {"peanut": U + "95fc2b4b-image.png", "moonman": U + "f34ab5e4-image.png", "jasmine": U + "b6f2920c-image.png",
       "f_moon": U + "73f382a6-image.png", "moonsaree": U + "28c9b7ac-image.png", "pasupu": U + "d408a773-image.png",
       "f_purple": U + "0e74cace-image.png", "pot": HQ + "pot.png",
       "f_lachimi": HQ + "f_lachimi.png", "f_yellow": HQ + "f_yellow.png", "f_white": HQ + "f_white.png", "tamarind": HQ + "tamarind.png"}
# face-swapped versions (faceswap.py) replace the originals when present
import os
SW = HQ.replace("/hq/", "/swap/")
for k in SRC:
    if os.path.exists(SW + k + ".png"): SRC[k] = SW + k + ".png"
im = Image.open(U + "7400b341-image.png"); im.crop((0, 0, im.width, 1520)).convert("RGB").save(HQ + "pot.png")
TOTAL = 59.6
BEATS = [0.19, 0.91, 1.53, 2.23, 2.93, 3.6, 4.27, 4.97, 5.64, 6.32, 7.01, 7.64, 8.36, 9.06, 9.73, 10.43, 11.1, 11.77, 12.45, 13.12,
         13.84, 14.49, 15.19, 15.86, 16.53, 17.23, 17.9, 18.58, 19.27, 19.95, 20.64, 21.32, 21.99, 22.69, 23.36, 24.03, 24.73, 25.4,
         26.1, 26.77, 27.45, 28.14, 28.82, 29.49, 30.19, 30.86, 31.53, 32.23, 32.9, 33.6, 34.27, 34.95, 35.64, 36.32, 36.99, 37.69,
         38.36, 39.06, 39.73, 40.43, 41.1, 41.77, 42.47, 43.12, 43.82, 44.49, 45.19, 45.84, 46.53, 47.23, 47.9, 48.58, 49.27, 49.95,
         50.62, 51.32, 51.99, 52.69, 53.36, 54.06, 54.73, 55.4, 56.1, 56.75, 57.45, 58.14, 58.82, 59.49]   # librosa, ~89 bpm
# (start, end, telugu, english letters, shot) ; shot = (image, focus-x %, focus-y %, transition, her?, punch-in?)
L = [
 (0.00, 2.88, "యేరుశనగ కోసం మట్టిని తవ్వితే..", "Yerushanaga kosam mattini thavvithe..", ("peanut", 50, 40, "fade", 0, 0)),
 (2.88, 5.52, "ఏకంగ తగిలిన లంకె బిందెలాగ", "Ekanga thagilina lanke bindhelaaga", ("pot", 45, 55, "zoom", 0, 0)),
 (5.52, 8.40, "ఎంత సక్కగున్నావే.. లచ్చిమి,", "Entha sakkagunnaave.. Lachchimi,", ("f_lachimi", 40, 30, "flash", 1, 0)),
 (8.40, 10.86, "ఎంత సక్కగున్నావే", "Entha sakkagunnaave", ("f_lachimi", 42, 26, "punch", 1, 1)),
 (10.86, 13.72, "సింతసెట్టు ఎక్కి సిగురు కొయ్యబోతె..", "Sinthasettu ekki siguru koyyabothe..", ("tamarind", 72, 40, "whip", 0, 0)),
 (13.72, 16.42, "చేతికి అందిన సందమామలాగ", "Chethiki andhina sandhamaamalaaga", ("moonman", 55, 35, "zoom", 0, 0)),
 (16.42, 19.34, "ఎంత సక్కగున్నావే.. లచ్చిమి,", "Entha sakkagunnaave.. Lachchimi,", ("f_white", 50, 30, "flash", 1, 0)),
 (19.34, 21.18, "ఎంత సక్కగున్నావే", "Entha sakkagunnaave", ("f_white", 52, 22, "punch", 1, 1)),
 (21.40, 24.62, "మల్లెపూల మద్దె ముద్దబంతిలాగ", "Mallepoola maddhe muddhabanthilaaga", ("jasmine", 50, 50, "leak", 0, 0)),
 (24.62, 27.26, "ఎంత సక్కగున్నావే..", "Entha sakkagunnaave..", ("f_purple", 45, 25, "flash", 1, 0)),
 (27.26, 30.30, "మత్తైదువ మెళ్లో పసుకుకొమ్ములాగ", "Matthaidhuva mello pasukukommulaaga", ("pasupu", 50, 45, "whip", 0, 0)),
 (30.30, 32.78, "ఎంత సక్కగున్నావే..", "Entha sakkagunnaave..", ("f_yellow", 45, 25, "flash", 1, 0)),
 (32.78, 35.22, "సుక్కల సీర కట్టుకున్న వెన్నెలలాగ", "Sukkala seera kattukunna vennelalaaga", ("moonsaree", 50, 40, "zoom", 0, 0)),
 (35.22, 37.48, "ఎంత సక్కగున్నావే..", "Entha sakkagunnaave..", ("f_moon", 45, 30, "flash", 1, 0)),
]
# second round (song repeats lines 1-2 + chorus); vary transitions so it doesn't feel copied
REP = {"fade": "leak", "zoom": "whip", "whip": "zoom"}
L += [(a + 37.48, b + 37.48, te, en, (s[0], s[1], s[2], REP.get(s[3], s[3]), s[4], s[5])) for a, b, te, en, s in L[:8]]
lines = {"te": [], "en": []}; shots = []
# repeated lyrics (2nd round): the user's real photos of her, 2-3 per line, no male photos (prepared by real.py)
RD = HQ.replace("/hq/", "/real/")
REAL = [["4771e5fb", "0d4b2cdd"], ["4c97b472", "13cfe65a"], ["6bbbf1de", "40b14343"], ["adc158f9", "4ece7045"],
        ["b2805a1c", "4349b72b", "f39692e2"], ["4771e5fb", "13cfe65a"], ["0d4b2cdd", "6bbbf1de"], ["40b14343", "adc158f9"]]
for i, (a, b, te, en, (img, fx, fy, tr, her, punch)) in enumerate(L):
    lines["te"].append({"a": a, "b": b, "t": te}); lines["en"].append({"a": a, "b": b, "t": en})
    if i >= 14:
        ps = REAL[i - 14]; e = b if i < len(L) - 1 else TOTAL
        for j, p in enumerate(ps):
            w, h = Image.open(RD + p + ".jpg").size
            shots.append({"a": a + (e - a) * j / len(ps), "img": p, "src": "file://" + RD + p + ".jpg", "w": w, "h": h, "her": 1, "xf": 0.35, "z0": 0.9})
        continue
    if shots and shots[-1]["img"] == img: continue          # same photo continues (no cut)
    w, h = Image.open(SRC[img]).size
    shots.append({"a": a, "img": img, "src": "file://" + SRC[img], "w": w, "h": h, "her": her})
for k, s in enumerate(shots): s["b"] = shots[k + 1]["a"] if k + 1 < len(shots) else TOTAL
lines["te"][-1]["b"] = lines["en"][-1]["b"] = 59.4
for lang in ("te", "en"):
    json.dump({"total": TOTAL, "font": lang, "lines": lines[lang], "shots": shots, "beats": BEATS},
              open(f"data_{lang}.json", "w"), ensure_ascii=False, indent=1)
print(len(lines["te"]), "lines", len(shots), "shots")
