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
