"""'TO BE CONTINUED…' movie-style title at 57 s (render title frames with title.js first), hold to 59 s, soft deep boom."""
import subprocess, numpy as np, soundfile as sf
S = "/tmp/claude-0/-home-user-fortesting/31472ba1-8ea5-51fc-a7e6-64ea60291e16/scratchpad/emo"
T0, END, SR = 57.0, 59.0, 48000
src = "../veer_kingdom_farewell_full.mp4"
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src], capture_output=True, text=True).stdout)
# deep cinematic boom (sine sweep + soft noise tail)
n = int(3.0 * SR); t = np.arange(n) / SR
boom = np.sin(2 * np.pi * np.cumsum(np.geomspace(70, 32, n)) / SR) * np.exp(-t / 0.9) * 0.55
rng = np.random.default_rng(3); tail = rng.standard_normal(n); k = np.exp(-np.arange(400) / 80); tail = np.convolve(tail, k / k.sum(), "same")
boom += tail * np.exp(-t / 0.7) * 0.06 * np.minimum(1, t / 0.02)
sf.write(S + "/boom.wav", np.stack([boom, boom], 1).astype(np.float32), SR)
fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={END - d + 0.05:.3f},trim=duration={END},"
      f"eq=brightness=0:enable='gte(t,{T0 - 0.6})',setpts=PTS-STARTPTS[bv];"
      f"[1:v]setpts=PTS-STARTPTS+{T0}/TB[tv];"
      # darken the picture behind the title
      f"[bv]drawbox=x=0:y=0:w=iw:h=ih:color=black@0.55:t=fill:enable='gte(t,{T0})'[dv];"
      f"[dv][tv]overlay=0:0:eof_action=repeat,format=yuv420p[v];"
      f"[0:a]apad=pad_dur={END - d + 0.1:.3f},atrim=0:{END}[ma];[2:a]adelay={int((T0 + 0.25) * 1000)}|{int((T0 + 0.25) * 1000)},volume=0.9[ba];"
      f"[ma][ba]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-framerate", "30", "-i", S + "/title/t_%04d.png", "-i", S + "/boom.wav",
                "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", str(END), "-c:v", "libx264", "-crf", "18", "-r", "30",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "../veer_kingdom_farewell_part1.mp4"], check=True)
print("done", d)
