# Comedy SFX reference pack 1 – "Some Modern Day Politicians be like"

These sound effects come from the reference comedy short (108 s, beach "press-meet" sketch).
Each clip was cut from the **voice-removed** track (Demucs separation), so the clips have no
dialogue. Each clip has a 10 ms fade-in and a short fade-out, and is loudness-normalised
(−16 LUFS, peak ≤ −1.5 dB).

Names come from an AudioSet sound classifier plus the on-screen action. Nobody has
listened to the clips yet, so rename any that sound different from their label.

## Clips and where they fire in the reference

| # | File | Ref time (s) | Length | What it is | When it is used |
|---|------|-------------|--------|------------|-----------------|
| 01 | `01_intro_news_music.mp3` | 0.20–2.70 | 2.5 s | TV/news-style music bed | Opening line under the title card ("Some Modern Day Politicians be like:") |
| 02 | `02_reaction_music_sting.mp3` | 9.88–11.55 | 1.7 s | Short comic music sting | On the **cut to the reporter's shocked close-up** (cut at 9.90) |
| 03 | `03_chicken_cluck.mp3` | 17.52–18.15 | 0.6 s | Chicken cluck / tick | Mocking a silly answer, just after the cut (17.43) |
| 04 | `04_squeaky_comedy_tune.mp3` | 20.70–22.40 | 1.7 s | Squeaky cartoon tune | Fills an **awkward pause** (no dialogue at 20.7–22.2) |
| 05 | `05_ding_boing.mp3` | 27.98–28.95 | 1.0 s | Ding + boing | Punchline hit in the middle of a shot |
| 06 | `06_chicken_boing.mp3` | 31.12–32.65 | 1.5 s | Cluck + boing | On the cut (31.17) to the politician's reaction |
| 07 | `07_guitar_pluck.mp3` | 39.35–39.85 | 0.5 s | Plucked-string "twang" | Lands just before the cut (39.57) |
| 08 | `08_whoosh_hit.mp3` | 41.05–41.55 | 0.5 s | Whoosh / bang | Exactly on the cut (41.13) |
| 09 | `09_beep.mp3` | 47.52–47.90 | 0.4 s | Beep / bleep | Just after the cut (47.47); censor-style beep |
| 10 | `10_slap.mp3` | 50.35–50.75 | 0.4 s | Slap / snap | Hits a line just before the cut (50.77) |
| 11 | `11_wood_block_roll.mp3` | 53.20–54.75 | 1.5 s | Wood-block percussion roll | Plays **with no dialogue** over the cut (53.67); a "thinking…" beat |
| 12 | `12_violin_squeak.mp3` | 57.60–59.20 | 1.6 s | Violin squeak / comic strings | On the cut (57.73) |
| 13 | `13_ding_whistle.mp3` | 65.98–66.50 | 0.5 s | Ding / whistle / boing | Punchline hit in the middle of a shot |
| 14 | `14_crash_hit.mp3` | 68.45–68.95 | 0.5 s | Crash / TV hit | On the cut (68.43) |
| 15 | `15_slam_hit.mp3` | 81.55–82.10 | 0.55 s | Slam / door hit | Emphasis on a loud line |
| 16 | `16_typing.mp3` | 91.45–93.00 | 1.5 s | Keyboard typing | Running gag ("noting it down") before the big beat |
| 17 | `17_deep_thud.mp3` | 93.90–94.45 | 0.55 s | Deep heartbeat thud | Big drop: followed by **~5 s of total silence** (94.2–99.2) |
| 18 | `18_outro_comedy_music.mp3` | 99.40–107.90 | 8.5 s | Comic outro music | Plays loud over the ending to the last frame |

## Timing patterns to copy

1. **Put the sound on the cut.** 11 of the 18 sounds start within ±0.2 s of a camera cut,
   usually the cut to a reaction close-up. Start the SFX 0–3 frames after the cut.
2. **Gap-fillers.** When nobody speaks for more than ~1 s, a sound fills the gap (04, 11).
   Dialogue never runs on in silence.
3. **About one hit every 3–6 s** in the middle section (10–70 s). Hits are short (0.4–0.6 s) stings,
   with a longer 1.5 s tune every so often.
4. **Level:** in the reference mix the SFX peak about 8–12 dB *below* the dialogue, so they never
   hide a word. The outro music (18) is the only part louder than the voice.
5. **Silence before the ending.** Use a hard thud (17), then ~5 s of no background at all, then
   the outro music (18) comes in loud.
6. A quiet music bed (~30 dB below the voice) runs under the whole sketch.

## Using a clip in ffmpeg

```bash
# drop 08_whoosh_hit at 12.40 s, at -10 dB under the voice
ffmpeg -i video.mp4 -i sfx/comedy_ref1/08_whoosh_hit.mp3 -filter_complex \
 "[1:a]adelay=12400|12400,volume=-10dB[s];[0:a][s]amix=inputs=2:normalize=0[a]" \
 -map 0:v -map "[a]" -c:v copy out.mp4
```

`events.json` holds the raw detection data (classifier labels and peak levels) for every event.
