"""Lyric video data: Telugu-script and English-letter (transliterated) versions -> data_te.json / data_en.json"""
import json, sys
I = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/song/img/"
TOTAL = 59.6
# (start, end, telugu, english letters, image, focus-y %, zoom-in?)   timings from the song audio
L = [
 (0.00, 2.88, "యేరుశనగ కోసం మట్టిని తవ్వితే..", "Yerushanaga kosam mattini thavvithe..", "peanut", 45, 1),
 (2.88, 5.52, "ఏకంగ తగిలిన లంకె బిందెలాగ", "Ekanga thagilina lanke bindhelaaga", "pot", 40, 1),
 (5.52, 8.40, "ఎంత సక్కగున్నావే.. లచ్చిమి,", "Entha sakkagunnaave.. Lachchimi,", "f_lachimi", 15, 0),
 (8.40, 10.86, "ఎంత సక్కగున్నావే", "Entha sakkagunnaave", None, 0, 0),
 (10.86, 13.72, "సింతసెట్టు ఎక్కి సిగురు కొయ్యబోతె..", "Sinthasettu ekki siguru koyyabothe..", "moonman", 20, 1),
 (13.72, 16.42, "చేతికి అందిన సందమామలాగ", "Chethiki andhina sandhamaamalaaga", None, 0, 0),
 (16.42, 19.34, "ఎంత సక్కగున్నావే.. లచ్చిమి,", "Entha sakkagunnaave.. Lachchimi,", "f_moon", 15, 0),
 (19.34, 21.18, "ఎంత సక్కగున్నావే", "Entha sakkagunnaave", None, 0, 0),
 (21.40, 24.62, "మల్లెపూల మద్దె ముద్దబంతిలాగ", "Mallepoola maddhe muddhabanthilaaga", "jasmine", 50, 1),
 (24.62, 27.26, "ఎంత సక్కగున్నావే..", "Entha sakkagunnaave..", "f_purple", 20, 0),
 (27.26, 30.30, "మత్తైదువ మెళ్లో పసుకుకొమ్ములాగ", "Matthaidhuva mello pasukukommulaaga", "pasupu", 35, 1),
 (30.30, 32.78, "ఎంత సక్కగున్నావే..", "Entha sakkagunnaave..", "f_yellow", 15, 0),
 (32.78, 35.22, "సుక్కల సీర కట్టుకున్న వెన్నెలలాగ", "Sukkala seera kattukunna vennelalaaga", "moonsaree", 30, 1),
 (35.22, 37.48, "ఎంత సక్కగున్నావే..", "Entha sakkagunnaave..", "f_white", 15, 0),
]
L += [(a + 37.48, b + 37.48, *r) for a, b, *r in L[:8]]   # second round: lines 1-2 + chorus, as in the song
lines = {"te": [], "en": []}; shots = []
for a, b, te, en, img, fy, zin in L:
    lines["te"].append({"a": a, "b": b, "t": te}); lines["en"].append({"a": a, "b": b, "t": en})
    if img: shots.append({"a": a, "src": "file://" + I + img + ".jpg", "fy": fy, "zin": zin})
for k, s in enumerate(shots): s["b"] = shots[k + 1]["a"] if k + 1 < len(shots) else TOTAL
lines["te"][-1]["b"] = lines["en"][-1]["b"] = 59.4
imgs = sorted({s["src"] for s in shots})
for lang, font in [("te", "te"), ("en", "en")]:
    json.dump({"total": TOTAL, "font": font, "lines": lines[lang], "shots": shots, "images": imgs},
              open(f"data_{lang}.json", "w"), ensure_ascii=False, indent=1)
print(len(lines["te"]), "lines", len(shots), "shots")
