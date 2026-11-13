"""Print how far below the voice each cue sits (target: 9-12 dB; a cue placed in a pause can be closer).

Usage: python3 -I sfx/tools/check_levels.py <original_video.mp4> <cues.txt>
Renders the SFX-only track with the same gains and compares the RMS per cue window.
"""
import os, subprocess, sys
import numpy as np

video, cues = sys.argv[1], sys.argv[2]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sr = 16000


def pcm(args):
    raw = subprocess.run(["ffmpeg", "-v", "error", *args, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


voice = pcm(["-i", video])
rows = [l.split("#")[0].split()[:3] for l in open(cues) if l.split("#")[0].strip()]
for t, f, g in rows:
    clip = os.path.join(root, f)
    clip = clip if os.path.isfile(clip) else clip + ".mp3"
    s = pcm(["-i", clip, "-af", f"volume={g}dB"])
    a = int(float(t) * sr)
    seg_v = voice[a:a + len(s)]
    r = lambda x: 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-9)
    print(f"{float(t):7.2f}  {os.path.basename(f):30s} voice {r(seg_v):6.1f}  sfx {r(s[:len(seg_v)]):6.1f}"
          f"  -> {r(seg_v) - r(s[:len(seg_v)]):5.1f} dB under voice")
