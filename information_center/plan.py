"""Overlay data: title bars + end screen only (user asked for no captions / stickers / cards)."""
import json
S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad"
W = S + "/w"
T = json.load(open(W + "/timeline.json"))
ME, TOT = T["main_end"], T["total"]
data = {"main_end": ME, "total": TOT, "captions": [], "stickers": [], "numbers": [], "cards": [],
        "board": {"phone": "7989615350"},
        "title": ["RTO మెసేజ్ వచ్చిందా?", "INSURANCE • POLLUTION"]}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
# soft SFX only for the end screen (bloop + thump, plucks, clicks)
sfx = [{"t": ME - 0.25, "k": "whoosh"}, {"t": ME, "k": "impact"}, {"t": ME + 0.2, "k": "chime"},
       {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
json.dump(sfx, open(W + "/sfx.json", "w"), indent=1)
print("main", ME, "total", TOT)
