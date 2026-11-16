# Chalkboard lyrics video style ("Chal Chalo Chalo" videos)

Start your message with **"Chalk lyrics video:"** and attach the song
(video/audio link) and the lyrics (text or screenshots).

```
Chalk lyrics video: make chalkboard lyric shorts from this song.
- Song: [Drive link – "Anyone with the link"]
- Lyrics: [paste / screenshots] – use ONLY this text
- Number of videos: [3–5], each 30–45 s, never repeat the same lyrics
  (chorus is used only once across all videos)
- Versions: Telugu script + Telugu in English letters (2 files per part)
```

## Style rules
1. 1080x1920, green chalkboard with wooden frame, chalk grain on everything.
2. Lyrics at the top, medium size (Telugu RamaCap 80 px / English letters
   Poppins Bold 64 px), max 2 rows. The line is "written" left→right by a
   chalk hand, then words fill yellow-orange as they are sung.
3. Middle area: hand-drawn stick-figure chalk sketch for every lyric line,
   drawn stroke by stroke with the chalk hand while the line plays; eraser
   wipe between sketches, faint ghost of the previous sketch stays.
4. Small "♪ song name ♪" tag under the drawing (no contact number).
5. Song audio as is (cut from the song, -14 LUFS, short fades).
6. Lyric timing: Whisper large-v3 word times on the song.

## Pipeline (`lyric_chalk/`)
- `lyrics.py` – lyric lines (Telugu, English letters) per song section
- `build.py`  – line times + sketch per line → `data/<part>_te.json`, `_en.json`
- `chalk.html` – sketch library (`LIB`) + chalk renderer; `prims.js` primitives
- `render.js` – `node render.js data/x.json preview 3,8,15 <dir>`
                `node render.js data/x.json full song.m4a out.mp4`
For a new song: new lyrics.py + build.py times, add new sketches to `LIB`.
