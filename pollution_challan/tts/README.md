`q_website.wav` – Navin's missing line "ఈ వెబ్‌సైట్‌లో పే చేశారు బ్రో?" (no take in the AI clips), synthesized with
Piper TTS, voice te_IN-venkatesh-medium (rhasspy/piper-voices), length-scale 0.85:

    echo "ఈ వెబ్‌సైట్‌లో పే చేశారు బ్రో?" | python3 -m piper -m te_IN-venkatesh-medium.onnx --length-scale 0.85 -f q_website.wav
