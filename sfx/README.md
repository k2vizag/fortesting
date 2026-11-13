# SFX library

Sound effects taken from reference videos the user likes, for use in new videos.
The full workflow is in `CLAUDE.md` → "Sound effects (SFX) – standing workflow".

## Packs

| Pack | Source | Clips | Style |
|------|--------|-------|-------|
| `comedy_ref1/` | "Some Modern Day Politicians be like" (Telugu comedy short) | 18 | Comic stings, ding/boing, chicken cluck, whoosh, slap, thud, outro music |

## Tools

- `tools/extract_sfx.py <ref.mp4> <pack_dir> [work_dir]`: separates the voice, detects and labels events, and cuts draft clips plus events.json.
- `tools/add_sfx.sh <in.mp4> <cues.txt> <out.mp4>`: mixes cues into a video (the picture is copied, not re-encoded).
- `tools/check_levels.py <in.mp4> <cues.txt>`: shows how far each cue sits below the voice (target 9–12 dB).

## Cue sheets used in finished videos

- `cues/pollution_certificate.txt`: Pollution Certificate "old number lekapothe?" (approved)
- `cues/challan_kattalsindhena.txt`: Pollution cheyalante challan kattalsindhena? (part 2)
