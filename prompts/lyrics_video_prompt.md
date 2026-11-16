# Lyrics video style (approved – "Entha sakkagunnave" video)

Use this for any song lyrics video. Start your message with **"Lyrics video:"**
and attach the song (video or audio), the lyrics text and the photos.

```
Lyrics video: make a lyrics video in my saved lyrics style.
- Song: [attach video / audio file]
- Lyrics: [paste lyrics – use ONLY this text, not the words in the song video]
- Photos: [attach] – one photo per lyric line, in order.
  On every chorus line (e.g. "ఎంత సక్కగున్నావే"), a female photo that matches the line before it.
- Real photos for the repeated part (optional): [attach] – shown from the exact
  start of the repeated lyrics, each photo once, no male photos.
- Face swap (optional): male photos = [attach], female photos = [attach]
- Versions: Telugu only  /  Telugu + English letters
```

## Style rules
1. Format: 1080x1920 (9:16), song audio as is, same length as the song.
2. Lyrics at the top only: small single line in a compact dark glass box
   (Telugu TE9 font 64px / English letters Poppins 54px). Words pop in and fill
   yellow-orange as they are sung. No "next line" preview.
3. Lyric timing from the song audio (Whisper word times; repeats found by
   matching the music, e.g. chroma match) – each line appears exactly when sung.
4. Photos in a rounded box in the middle (thin gold border, soft glow); the
   WHOLE photo is always visible – never crop/zoom-cut the photo. A blurred,
   darkened copy of the same photo fills the 9:16 background.
5. Every photo has a visible smooth zoom-in of the box (86% → 100%), smooth
   crossfades between photos (0.6–0.7 s). No whip / flash / punch effects.
6. Soft golden sparkles floating (a bit brighter on female photos), soft vignette.
7. Small / screenshot photos: crop off any burned-in text, then AI-upscale 4x
   (Real-ESRGAN x4plus) so they are sharp.
8. Same photo on two lines in a row → keep it on screen (no cut).
9. Repeated lyrics with real photos: start exactly when the repeated line
   starts, each photo only once, evenly spread (~3 s each), no male photos,
   drop look-alike / poor photos, crop only empty sky/floor (or the person
   alone from group photos – no other faces).
10. Face swap (when asked): inswapper_128 with several clear photos of each
    person; CodeFormer face restore inside the face outline only; for the
    female face keep the original photo's sharp eyes (blend eye area back).
    Show a close-up preview before rendering. Only with the person's consent.
11. Send one preview frame sheet before the full render when photos change.

## Pipeline (repo folder `lyrics_song/`)
- `upscale.py` – crop burned-in text + Real-ESRGAN x4 for small photos
- `faceswap.py` – face swap + CodeFormer + keep crisp eyes (optional)
- `real.py` – prepare real photos (find her face, trim sky/floor, crop from groups)
- `build.py` – lyrics + timings + photo order → `data_te.json` / `data_en.json`
- `lyrics.html` + `render.js` – renders the video (Playwright → ffmpeg)
  `node render.js data_te.json out.mp4 song.mp4`  (preview: add `preview 5,12,30`)
Update the hard-coded upload / scratchpad paths and the lyric lines for each new song.
