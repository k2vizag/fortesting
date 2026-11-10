# RC transfer – Telugu captions

- `RC_transfer_telugu.ass` – Telugu captions (speaker's own words) + auto-approval NOTE badge (15.4s–19.0s).
- Fonts: Ramabhadra (Telugu+Latin merged) for captions, Poppins ExtraBold for the NOTE tag (both OFL).
- Style matched to the reference video: short 2–3 word captions inside the video frame, white with hard black shadow, key words yellow/green.

Re-render:

    ffmpeg -i RC_transfer_styled.mp4 -vf "ass=captions/RC_transfer_telugu.ass:fontsdir=captions/fonts" \
      -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart RC_transfer_telugu_captions.mp4
- Hanging contact board (కాల్ చేయండి 7989615350) swings in the bottom band for the whole video.
- At the end screen (29.0s) the board slides up above the Like & Subscribe text so YouTube's title/description overlay can't hide it.
