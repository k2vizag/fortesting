"""Shared timeline for the Nostic ice cream short.
Sources (scratchpad/raw): v5,v6,v7 = AI videos (voice kept), v1 = YouTube clip (2x, muted, text covered),
v2,v3,v4 = real shop clips (muted, enhanced)."""
S = "/tmp/claude-0/-home-user-fortesting/4e589d33-8934-5dd9-a5c1-fec76296f99d/scratchpad"
RAW = S + "/raw"
W = S + "/work"
FPS = 30

# (src, start, end, speed, kind, zoom) – source seconds; AI parts follow the script order exactly
SEGS = [
    ("v7", 1.60, 3.52, 1, "ai", 1.00),   # Meeku ice cream ante istamena?
    ("v5", 0.08, 0.45, 1, "ai", 1.00),   # Aithe
    ("v5", 0.80, 3.42, 1, "ai", 1.07),   # idi chudandi Nostic natural fruit ice creams (pause removed)
    ("v7", 6.15, 8.32, 1, "ai", 1.00),   # E ice creams ni fruits pulp tho chestaru
    ("v5", 3.62, 6.12, 1, "ai", 1.00),   # preservatives emi add cheyakunda natural ga chestaru
    ("v7", 8.66, 10.35, 1, "ai", 1.07),  # sugar free ice creams kuda untai
    ("v5", 6.36, 7.95, 1, "ai", 1.07),   # ivi 20 rupees nundi start avutai
    ("v6", 0.05, 10.05, 1, "ai", 1.00),  # chala rakala varieties ... try cheyandi
    ("v1", 0.00, 6.85, 2, "yt", 1.00),   # ice cream shots only (crowd shot 6.87-8.62 skipped)
    ("v1", 8.65, 27.00, 2, "yt", 1.00),
    ("v2", 1.00, 5.00, 1, "real", 1.00),  # shop inside
    ("v4", 0.50, 3.50, 1, "real", 1.00),  # freezer
    ("v4", 16.50, 19.50, 1, "real", 1.00),  # wall menu
    ("v3", 7.00, 10.50, 1, "real", 1.00),   # price standee
    ("v3", 19.50, 25.00, 1, "real", 1.00),  # shop front at night
]
END_SCREEN = 4.0


def frames(seg):
    _, a, b, sp, _, _ = seg
    return round((b - a) / sp * FPS)


def timeline():
    """output start time (s) of each segment"""
    t, out = 0, []
    for s in SEGS:
        out.append(t / FPS)
        t += frames(s)
    return out, t / FPS


def to_out(i, src_t):
    """map a source time inside segment i to output time"""
    starts, _ = timeline()
    _, a, _, sp, _, _ = SEGS[i]
    return starts[i] + (src_t - a) / sp
