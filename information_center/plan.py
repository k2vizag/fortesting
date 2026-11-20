"""Overlay data (title bars, B-roll / graphic cards, end screen) + soft SFX list.
usage: plan.py <config module>   (after build.py)
Cards may be given in raw-source seconds (sa/sb, step 'sat', 'spill'); they are mapped onto the edited timeline."""
import copy, importlib, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
CFG = importlib.import_module(sys.argv[1] if len(sys.argv) > 1 else "rto_message")
S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad"
W = S + CFG.WORK
T = json.load(open(W + "/timeline.json"))
ME, TOT, P = T["main_end"], T["total"], T["pieces"]
SPEED = 1.10

def M(src):
    """raw-source second -> edited-video second (a time inside a cut snaps to the next kept piece)."""
    for a, b, oa, ob in P:
        if src < a: return oa
        if src <= b: return oa + (src - a) / SPEED
    return P[-1][3]

cards, sfx = [], []
for c in copy.deepcopy(CFG.CARDS):
    if "sa" in c:
        c["a"], c["b"] = M(c.pop("sa")), M(c.pop("sb"))
        if "spill" in c: c["pillAt"] = M(c.pop("spill")) - c["a"]
        for st in c.get("steps", []):
            if "sat" in st: st["at"] = max(0.3, M(st.pop("sat")) - c["a"])
    c["a"], c["b"] = round(c["a"], 3), round(c["b"], 3)
    cards.append(c)
    if not any(e["t"] == round(c["a"] - 0.25, 3) for e in CFG.SFX):
        sfx += [{"t": c["a"] - 0.25, "k": "whoosh"}, {"t": c["a"], "k": "impact"}, {"t": c["b"] - 0.2, "k": "whoosh_out"}]
        if c["type"] == "profile": sfx.append({"t": c["a"] + c.get("pillAt", 0.45), "k": "chime"})
        for st in c.get("steps", []): sfx.append({"t": c["a"] + st["at"], "k": "coin" if "₹" in st["v"] else "tick"})

data = {"main_end": ME, "total": TOT, "captions": [], "stickers": [], "numbers": [], "cards": cards,
        "intro": T.get("intro", 0),
        "board": {"name": "KRISHNA NET CENTER", "phone": "7989615350", "line": "RTO Works & Motor Insurance"},
        "title": CFG.TITLE}
json.dump(data, open(W + "/data.json", "w"), ensure_ascii=False, indent=1)
# soft SFX: title in, cards, end screen (bloop + thump, plucks, clicks)
sfx = CFG.SFX + sfx + [{"t": 0.05, "k": "impact"}, {"t": 0.15, "k": "chime"}, {"t": ME - 0.25, "k": "whoosh"},
                       {"t": ME, "k": "impact"}, {"t": ME + 0.2, "k": "chime"}, {"t": ME + 1.45, "k": "click"},
                       {"t": ME + 2.35, "k": "click"}, {"t": ME + 2.4, "k": "ding"}]
json.dump(sorted(sfx, key=lambda e: e["t"]), open(W + "/sfx.json", "w"), indent=1)
print("main", round(ME, 2), "total", round(TOT, 2), "cards", [(c["type"], c["a"], c["b"]) for c in cards])
