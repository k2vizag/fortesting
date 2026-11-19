import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("large-v3", device="cpu", compute_type="int8", cpu_threads=4)
import numpy as np, subprocess
audio = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",sys.argv[1],"-ac","1","-ar","16000","-f","f32le","-"],capture_output=True).stdout, np.float32).copy()
segs, info = m.transcribe(audio, language="te", word_timestamps=True, vad_filter=False, beam_size=5)
out = []
for s in segs:
    out.append({"a": s.start, "b": s.end, "t": s.text, "w": [(w.start, w.end, w.word) for w in s.words]})
    print(f"{s.start:7.2f}-{s.end:7.2f} {s.text}", flush=True)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
