"""Extract sound effects from a reference video into a named SFX pack.

Usage:
  python3 -I sfx/tools/extract_sfx.py <reference.mp4> <pack_dir> [work_dir]

Steps:
  1. Demucs separates the voice from the background (music + SFX).
  2. Energy detection on the background track finds each sound event.
  3. The AudioSet classifier (MIT/ast-finetuned-audioset, from Hugging Face)
     labels each event and gives it a draft name.
  4. Camera cuts are detected, so the notes say how each sound relates to a cut.
  5. Each event is cut from the voice-free track (fade in/out, -16 LUFS) into
     <pack_dir>/NN_<label>.mp3, and the data goes to <pack_dir>/events.json.

Then review the clips, rename/merge/drop where needed, and write README.md
(see sfx/comedy_ref1/README.md for the format).

Needs: pip install demucs transformers librosa  (torch comes with demucs)
"""
import json, os, re, subprocess, sys

import librosa
import numpy as np
import torch
from transformers import ASTFeatureExtractor, ASTForAudioClassification

ref, pack = sys.argv[1], sys.argv[2]
work = sys.argv[3] if len(sys.argv) > 3 else os.path.join(pack, "_work")
os.makedirs(pack, exist_ok=True)
os.makedirs(work, exist_ok=True)

wav = os.path.join(work, "ref.wav")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", ref, "-ar", "44100", wav], check=True)
subprocess.run([sys.executable, "-m", "demucs", "-n", "htdemucs", "--two-stems=vocals",
                "-o", os.path.join(work, "sep"), wav], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
bg_path = os.path.join(work, "sep", "htdemucs", "ref", "no_vocals.wav")

# camera cuts
p = subprocess.run(["ffmpeg", "-i", ref, "-vf", "select='gt(scene,0.25)',showinfo",
                    "-an", "-f", "null", "-"], capture_output=True, text=True)
cuts = [float(x) for x in re.findall(r"pts_time:([0-9.]+)", p.stderr)]

# events on the background track (50 ms frames, threshold = 40th percentile + 9 dB)
sr = 16000
bg, _ = librosa.load(bg_path, sr=sr, mono=True)
mix, _ = librosa.load(wav, sr=sr, mono=True)
h = int(sr * 0.05)
db = np.array([20 * np.log10(np.sqrt((bg[i:i + h] ** 2).mean()) + 1e-9) for i in range(0, len(bg), h)])
on = db > np.percentile(db, 40) + 9
segs, i = [], 0
while i < len(on):
    if on[i]:
        j = i
        while j < len(on) and (on[j] or on[j:j + 6].any()):
            j += 1
        if (j - i) * 0.05 >= 0.1:
            segs.append((i * 0.05, j * 0.05))
        i = j
    else:
        i += 1

name_id = "MIT/ast-finetuned-audioset-10-10-0.4593"
fe = ASTFeatureExtractor.from_pretrained(name_id)
model = ASTForAudioClassification.from_pretrained(name_id).eval()
GENERIC = {"Music", "Speech", "Sound effect", "Television", "Male speech, man speaking",
           "Musical instrument", "Narration, monologue", "Vehicle", "Inside, small room", "Animal"}


def labels(x):
    with torch.no_grad():
        pr = torch.sigmoid(model(**fe(x, sampling_rate=sr, return_tensors="pt")).logits)[0]
    t = pr.topk(6)
    return [(model.config.id2label[int(k)], round(float(v), 2)) for v, k in zip(t.values, t.indices)]


events = []
for n, (a, b) in enumerate(segs, 1):
    s, e = int(max(0, a - 0.05) * sr), int((b + 0.1) * sr)
    lb, lm = labels(bg[s:e]), labels(mix[s:e])
    specific = [l for l, _ in lb + lm if l not in GENERIC]
    base = specific[0] if specific else ("music_sting" if b - a < 3 else "music")
    slug = re.sub(r"[^a-z0-9]+", "_", base.lower()).strip("_")
    fname = f"{n:02d}_{slug}"
    near = min(cuts, key=lambda c: abs(c - a)) if cuts else None
    start, end = max(0, a - 0.08), b + 0.15
    d = end - start
    fo = min(0.25, d / 3)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.2f}", "-t", f"{d:.2f}", "-i", bg_path,
                    "-af", f"afade=t=in:d=0.01,afade=t=out:st={d - fo:.2f}:d={fo:.2f},"
                           "loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k",
                    os.path.join(pack, fname + ".mp3")], check=True)
    events.append(dict(file=fname + ".mp3", start=round(start, 2), end=round(end, 2),
                       peak_db=round(float(db[int(a / 0.05):int(b / 0.05) + 1].max()), 1),
                       nearest_cut=near, offset_from_cut=None if near is None else round(a - near, 2),
                       bg_labels=lb, mix_labels=lm))
    print(fname, f"{a:.2f}-{b:.2f}", lb[:3])

json.dump(dict(reference=os.path.basename(ref), cuts=cuts, events=events),
          open(os.path.join(pack, "events.json"), "w"), ensure_ascii=False, indent=1)
print(f"{len(events)} clips -> {pack}  (delete _work/ before committing)")
