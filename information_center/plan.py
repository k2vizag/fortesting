"""Overlay data: title bars + end screen only (user asked for no captions / stickers / cards)."""
import json
S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad"
W = S + "/w"
T = json.load(open(W + "/timeline.json"))
ME, TOT = T["main_end"], T["total"]
data = {"main_end": ME, "total": TOT, "captions": [], "stickers": [], "numbers": [],
        # B-roll: the RTO SMS screenshot (vehicle no. changed to ...1235) while he says the messages are coming
        "cards": [dict(type="shot", theme="dark", a=2.2, b=5.9, img="assets/rto_sms.png", w=576, h=1280,
                       hl=[30, 530, 440, 670], hlAt=1.2)],
        "intro": T.get("intro", 0), "board": {"name": "KRISHNA NET CENTER", "phone": "7989615350", "line": "RTO Works & Motor Insurance"},
        "title": ["RTO మెసేజ్ వచ్చిందా?", "INSURANCE • POLLUTION"]}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
# soft SFX only for the end screen (bloop + thump, plucks, clicks)
sfx = [{"t": 1.95, "k": "whoosh"}, {"t": 2.2, "k": "impact"}, {"t": 3.4, "k": "chime"}, {"t": 5.7, "k": "whoosh_out"}, {"t": 0.05, "k": "impact"}, {"t": 0.15, "k": "chime"}, {"t": ME - 0.25, "k": "whoosh"}, {"t": ME, "k": "impact"}, {"t": ME + 0.2, "k": "chime"},
       {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
json.dump(sfx, open(W + "/sfx.json", "w"), indent=1)
print("main", ME, "total", TOT)
