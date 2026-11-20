# K2 Vizag video editing – standing instructions

When the user uploads or links a raw video (or asks to "edit this video"),
edit it into YouTube Shorts following **prompts/video_edit_prompt.md**
exactly. That file is the user's approved style; apply every point even if the
user's message is short.

- If the message does not give the topic, number of videos (1 or 2), split
  between the videos, or the two title lines, work them out from the footage
  and state your choice in the reply; ask only if it is genuinely unclear.
- Contact number for the end screen: 7989615350 (end screen only).
- Reuse the pipeline in `insurance/v2/` (base2.py → plan2.py → audio2.py →
  render.js, denoise with dfn.py). Fonts and images are in `insurance/v2/fonts`
  and `insurance/v2/assets`. Update the hard-coded scratchpad paths, and write
  new per-video content (segments, captions, cards, stickers) for the new topic.
- Known pitfall: when speeding up with `setpts`/`atempo`, put `-t` before each
  `-i` (input duration). As an output option it reads past the cut point and
  brings back removed words.
- Google Drive links must be shared as "Anyone with the link"; if a download
  returns a sign-in page, ask the user to change sharing.
- Do not commit video files over ~90 MB (GitHub rejects files over 100 MB).

## Lyrical videos (song + lyrics → vertical 1080x1920, Telugu + English versions)

Always make two versions: Telugu script (font `RamaCap`) and Telugu in English
letters (font `PopB`, Poppins Bold), from `insurance/v2/fonts`. Lyrics = the
user's text exactly (only drop trailing ".." / "!"); write the English-letters
version yourself (th = త, dh = ద, aa/ee/oo for long vowels).

- Timing: faster-whisper large-v3 (`pip install faster-whisper`; pass the audio
  as a numpy array – the installed `av` breaks file loading), language `te`,
  word timestamps. Align the user's lines to Whisper with a global character
  alignment (see `koduka/build.py`): every char must map to exactly one char,
  and Whisper's stretched first word of a segment is trimmed to its last 0.6 s.
  Ignore Whisper text in intro music and silence (it hallucinates there).
- Text: render it with Chromium (Playwright) from a **file://** page
  (`--allow-file-access-from-files`). libass and `setContent` pages break
  Telugu conjuncts / fail to load the font. Karaoke: words fill yellow-orange
  as sung (`text_layer.js` PNG states overlaid with ffmpeg concat).
- User's current layout preference (Naa Koduka): sung line at the **top**,
  "♪ song name ♪" tag at the **bottom**, **no upcoming/next line**.
- Styles (pick the one that suits the song, say which):
  - film-video lyric (`alasendra/`): use the song's own video and audio, crop
    the letterbox, 16:9 picture over a blurred copy, best shots per section.
    "Script is final" = cut the audio to only the user's lyric sections, in the
    script's order, joining on matching musical points.
  - cinematic silhouette (`koduka/sil.html` + `render.js`): one animated scene
    per line, silhouettes rise in, then the last part of each line blooms into
    full colour (the user wants every line's last frame colourful).
  - chalkboard (`lyric_chalk/` on branch ccr-23c8d9c9-8ol8yd,
    `prompts/chalk_lyrics_prompt.md` there).
- Splitting into parts: cut at the user's timeline (or at section
  boundaries), fade each part in/out, and level every part to the same
  loudness; no lyric from another part on screen.
- Keep files small: film grain makes huge files – add `hqdn3d=2:2:6:6` and
  crf 23–24 (a 3:45 video ≈ 35 MB).
- Film songs (Think Music, Aditya Music…) will get YouTube Content ID claims;
  mention it once.

## Song montages from AI clips (e.g. `song_chal_chalo/`)

- Check every clip frame by frame and drop AI glitches (vanishing/ghost
  characters, tails through clothes, black/dark endings, flash frames at cuts –
  find exact cuts with ffmpeg `select='gt(scene,0.25)'`).
- "2x / 1.5x speed" means the clips play at exactly that speed; the song stays
  at normal speed. Slow motion = minterpolate (mci) at 720p, then upscale.
- Clips "as it is with dialogue" keep their own audio; fade the sound at every
  clip/music join (no sudden cuts) and start songs at a quiet point.
- Remove the AI ✦ sparkle mark in the bottom-right corner with
  `delogo=x=850:y=1690:w=94:h=94` (1080x1920 output) when asked.
- When a request is ambiguous ("trim to 32 sec"), ask with options.
