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

## Sound effects (SFX) – standing workflow

The user collects SFX from reference videos they like and wants them used in
every new video. Library: `sfx/` (see `sfx/README.md`). Packs: `sfx/comedy_ref1/`, …

**When the user sends a reference video "for its sound effects":**
1. `python3 -I sfx/tools/extract_sfx.py <ref.mp4> <scratchpad>/pack <scratchpad>/work`
   (pip install demucs transformers librosa if missing). This gives draft clips + events.json.
2. Curate: drop weak/duplicate events (peak below about -33 dB, or ones that are just background music), merge
   pieces of one sound, look at frames at each event, give clear names
   (`NN_what_it_is.mp3`). Copy the result into the next free `sfx/<style>_refN/`.
3. Write that pack's README.md: clip table (file, ref time, length, what it is, when it
   is used) + timing patterns (relation to cuts, pauses, hit rate, level vs voice).
   Use `sfx/comedy_ref1/README.md` as the template. Add the pack to `sfx/README.md`. Commit + push.

**When editing any new video (always, unless the user says no SFX):**
1. Look at what the edit already has (sticker pops, whooshes, card music, end-screen
   music); separate it with demucs if needed. Don't stack new SFX on top of existing ones.
2. Choose 6–10 cues from the packs, following the pack READMEs: put each sound on a camera cut / reaction
   close-up (0–3 frames after the cut), on shocked/worried/"Avuna?" moments, fill
   pauses > 1 s, a punch hit on "like"/"next video" lines, a deep thud before a
   reveal. Vary the clips; prefer the user's most recent pack if they say so.
3. Write `sfx/cues/<video_name>.txt` (`time clip gain_dB`), then
   `sfx/tools/add_sfx.sh <in.mp4> <cues.txt> <out.mp4>` and check with
   `python3 -I sfx/tools/check_levels.py <in.mp4> <cues.txt>`: keep each cue 9–12 dB under
   the voice (a cue in a pause can be closer). Example: `sfx/cues/pollution_certificate.txt`.
4. In the reply, list each cue (time, sound, moment) and say you haven't listened to the mix.
