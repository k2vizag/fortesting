"""Lyric video data: 57.2 s cut of the song (raw 47.5 -> 104.7 s; the lyrics run unbroken 50 -> 103.8), lines with word timings, one still per line.
Times are seconds in the cut (raw - 47.5). Word times from the Whisper pass on the song, tidied by hand."""
import json, sys
import cv2
S = "/tmp/claude-0/-home-user-fortesting/c8da1d15-5414-57cb-a7d5-c0ca68b3b8d8/scratchpad/song"
START, TOTAL = 47.5, 57.2
LINES = [  # (line start, line end, [(word, start)])
    (2.6, 5.1,  [("Chitti", 2.6), ("Chitti", 3.9), ("Cheema", 4.4)]),
    (5.1, 7.3,  [("Chitti", 5.1), ("Chitti", 5.4), ("Laa", 5.7), ("Ayyo", 6.2), ("Raama", 6.7)]),
    (7.3, 11.6, [("Vandha", 7.3), ("Tannula", 7.9), ("Chakkera", 8.3), ("Mosthundhamma", 9.0)]),
    (11.6, 15.5, [("Kondapalli", 11.6), ("Bomma", 13.0), ("Konda", 13.7), ("Kona", 14.1), ("Daatindhamma", 14.7)]),
    (15.5, 19.0, [("Thana", 15.9), ("Kalala", 16.3), ("Vaipu", 16.7), ("Nadichindhamma", 17.4)]),
    (19.0, 23.7, [("Em", 19.0), ("Antaaru", 21.0), ("Emito", 21.6), ("Evito", 22.6)]),
    (23.7, 26.9, [("Emo", 23.7), ("Kadaa", 24.3), ("Jante", 24.9), ("Kani", 25.3), ("Jantane", 26.0)]),
    (26.9, 30.3, [("Em", 26.9), ("Antaaru", 27.5), ("Emo", 28.1), ("Kadaa", 28.6), ("Emautundho", 29.2)]),
    (30.3, 33.5, [("Evito", 30.3), ("Evito", 31.3), ("Emo", 32.3), ("Kadaa", 32.9)]),
    (33.5, 37.5, [("Atu", 33.5), ("Itu", 33.9), ("Payaname", 34.4), ("Ettelutundho", 35.6), ("Emo", 36.7), ("Kadaa", 37.1)]),
    (37.5, 41.4, [("Rivvu", 37.5), ("Rivvu", 37.9), ("Mani", 38.3), ("Egaralanukunte", 38.8), ("Chaalaa", 40.5)]),
    (41.4, 45.9, [("Rivvu", 41.4), ("Rivvu", 42.1), ("Mani", 42.6), ("Paatikave", 43.1), ("Pichchuka", 44.2), ("Rekkalilaa", 44.8)]),
    (45.9, 50.0, [("Rivvu", 45.9), ("Rivvu", 46.4), ("Mani", 46.9), ("Egaralanukunte", 47.4), ("Chaalaa", 49.0)]),
    (50.0, 52.7, [("Rivvu", 50.0), ("Rivvu", 50.5), ("Mani", 51.1), ("Paatikave", 51.7)]),
    (52.7, 57.2, [("Vannelu", 52.7), ("Kooti", 53.2), ("Pichchuka", 53.6), ("Rekkalilaa", 54.5)]),
]
STILLS = [(0.0, 47, 0, -2), (2.6, 9, -2, 0), (5.1, 3, 2, 0), (7.3, 13, 0, 0), (11.6, 51, 0, -2), (15.5, 14, 2, 0),
          (19.0, 16, -2, 0), (23.7, 36, 0, -2), (26.9, 45, 2, 0), (30.3, 46, -2, 0), (33.5, 40, 0, -2), (37.5, 6, 2, 0), (41.4, 1, -2, 0),
          (45.9, 48, 0, 2), (50.0, 52, 0, -2), (54.6, 47, 2, 0)]
data = {"total": TOTAL,
        "lines": [{"a": a, "b": b, "words": [{"t": w, "a": s} for w, s in ws]} for a, b, ws in LINES],
        "stills": [{"a": a, "img": f"file://{S}/pick/p{k:03d}.jpg", "dx": dx, "dy": dy,
                    "ar": (lambda im: im.shape[1] / im.shape[0])(cv2.imread(f"{S}/pick/p{k:03d}.jpg"))}
                   for a, k, dx, dy in STILLS]}   # ar: the frame takes the photo's own shape (whole photo visible)
json.dump(data, open(f"{S}/lyric_data.json", "w"), indent=1)
print("lines", len(LINES), "stills", len(STILLS))
