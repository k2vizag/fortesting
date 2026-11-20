"""Overlay data: title bars + end screen only (user asked for no captions / stickers / cards)."""
import importlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CFG = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "rto_message")
S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad"
W = S + CFG.WORK
T = json.load(open(W + "/timeline.json"))
ME, TOT = T["main_end"], T["total"]
data = {"main_end": ME, "total": TOT, "captions": [], "stickers": [], "numbers": [],
        "cards": CFG.CARDS,
        "intro": T.get("intro", 0), "board": {"name": "KRISHNA NET CENTER", "phone": "7989615350", "line": "RTO Works & Motor Insurance"},
        "title": CFG.TITLE}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
# soft SFX only for the end screen (bloop + thump, plucks, clicks)
sfx = CFG.SFX + [{"t": 0.05, "k": "impact"}, {"t": 0.15, "k": "chime"}, {"t": ME - 0.25, "k": "whoosh"}, {"t": ME, "k": "impact"}, {"t": ME + 0.2, "k": "chime"},
       {"t": ME + 1.45, "k": "click"}, {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
json.dump(sfx, open(W + "/sfx.json", "w"), indent=1)
print("main", ME, "total", TOT)
