from faster_whisper import WhisperModel
m=WhisperModel("medium",device="cpu",compute_type="int8")
import soundfile as sf; a,_=sf.read("src/a16.wav",dtype="float32"); segs,_=m.transcribe(a,language="te",word_timestamps=True,vad_filter=False)
for s in segs:
    print(f"{s.start:6.2f}-{s.end:6.2f} {s.text}")
    for w in s.words: print(f"   {w.start:6.2f}-{w.end:6.2f} {w.word}")
