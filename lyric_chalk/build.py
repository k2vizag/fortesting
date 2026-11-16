# Builds data JSON for each chalkboard lyric video (Telugu script + English letters).
# Line times (song seconds) from Whisper large-v3 word timestamps; first word of a line
# started late when Whisper stretched it over the music gap.
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__)); from lyrics import SEC
OUT = sys.argv[1] if len(sys.argv) > 1 else '.'
VIDEOS = [
 # name, start, end, [(section, idx, a, b, scene or None)]
 ("1_rajyam", 6.4, 44.6, [("intro",0,9.1,14.38,"raja"),("intro",1,17.2,24.18,"rama"),("intro",2,26.4,34.7,"veera"),("intro",3,36.7,43.06,"deva")]),
 ("2_chal_chalo", 56.8, 99.1, [("chorus",0,59.3,62.68,"chal"),("chorus",1,62.68,66.38,"chapter"),("chorus",2,70.1,73.48,"daari"),("chorus",3,73.48,76.84,"challenge"),
   ("v1",0,81.0,84.34,"sweetbitter"),("v1",1,84.34,87.54,"zindagi"),("v1",2,87.54,91.46,"guarantee"),("v1",3,91.46,94.78,"parugu"),("v1",4,95.4,99.04,"kshanam")]),
 ("3_kanneellu", 144.6, 188.65, [("v2",0,146.9,149.12,"tears"),("v2",1,149.12,152.4,"teeya"),("v2",2,153.0,156.3,"heavy"),("v2",3,156.3,160.0,"light"),
   ("v2",4,160.0,162.96,"edhure"),("v2",5,162.96,166.5,"nippu"),("v2",6,166.5,170.1,"thadakha"),("v2",7,170.1,174.44,"gadapa"),
   ("v2b",0,174.6,177.64,"padda"),("v2b",1,177.64,180.88,"ugra"),("v2b",2,181.6,184.86,"kaana"),("v2b",3,184.86,188.62,"jeevitham")]),
 ("4_madathe", 240.6, 285.4, [("v3",0,242.3,245.36,"shirt"),("v3",1,245.36,248.84,"almarah"),("v3",2,249.5,252.42,"paper"),("v3",3,252.42,254.82,"chedalu"),("v3",4,254.82,256.64,None),
   ("v3",5,257.0,259.66,"baby"),("v3",6,259.66,263.54,"kotthem"),("v3",7,263.9,266.56,"komma"),("v3",8,266.56,270.94,"gaalipatam"),
   ("v3b",0,271.2,277.44,"plusminus"),("v3b",1,277.6,283.1,"nerchuko"),("v3b",2,283.1,285.08,"gelupu")]),
]
for name, st, en, L in VIDEOS:
    total = round(en - st, 2)
    sc = []
    for k, (_, _, a, b, key) in enumerate(L):
        if key is None: continue
        a0 = 0.3 if not sc else round(a - st - 0.25, 2)
        if sc: sc[-1]["b"] = a0
        sc.append({"a": a0, "b": total, "key": key})
    for fi, font in enumerate(("te", "en")):
        lines = [{"a": round(a - st, 2), "b": round(b - st, 2), "t": SEC[s][i][fi]} for s, i, a, b, _ in L]
        d = {"total": total, "start": st, "font": font, "title": "Chal Chalo Chalo", "lines": lines, "scenes": sc}
        json.dump(d, open(f"{OUT}/{name}_{font}.json", "w"), ensure_ascii=False, indent=1)
    print(name, total, len(L), "lines", len(sc), "scenes")
