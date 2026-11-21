"""Video 3, ORIGINAL shirt version (user's pick): same cut as pollution_otp.py plus
 - B-roll photo (pollution-check van) for ~1 s at 'సిక్స్ మంత్స్‌కి / వన్ ఇయర్‌కి'
 - hook 'OTP ముఖ్యం బిగిలు' louder with an auditorium echo, and a short beat after it so the echo rings out."""
from pollution_otp import RAW, KEEP as _KEEP, TITLE, CARDS as _CARDS, SFX, HOOK
WORK = "/w3o"
INTRO = 0.0
SHIRT = None
# hook piece kept whole (no pause trimming) and extended into the silence after it -> room for the echo tail
KEEP = [(97.62, 99.30, "OTP ముఖ్యం బిగిలు", "nosplit")] + list(_KEEP[1:])
HOOK_FX = True          # audio.py: +5 dB + auditorium echo on the first piece
CARDS = [dict(type="photo", theme="dark", sa=107.45, sb=108.65, img="assets/pollution_van.jpg",
              label="6 నెలలు / 1 సంవత్సరం", labelAt=0.12)] + list(_CARDS)
# comedy sounds in the opening gaps (user request), edited-video seconds
COMEDY = [
    (1.05, "cartoon-boing-01", 0.7, -11),        # after 'OTP ముఖ్యం బిగిలు' (with the echo)
    (7.60, "cartoon-pop-01", 0.4, -10),          # after '...పొల్యూషన్ అయిపోతుంది కదా'
    (10.46, "crowd-ooh-01", 1.2, -15),           # after '...OTP అడుగుతారు' (surprise)
    (16.12, "cartoon-eye-blink-01", 0.6, -11),   # after 'ఆ నంబర్‌కి వెళ్తుంది' (check your number!)
]
