# Ember 28 s demo video

Everything is drawn from shapes, text and the real test points (`points.js`, from `data/processed/tests.csv`). No photos, no stock footage, no NASA logos or imagery. Numbers used: 24 investigations, 255 claims, 643 mapped tests, 48 tests inside lunar-base air (all 0 g), 0 partial-gravity tests in PSI, and the oxygen-margin values for Mylar, Ultem and Nomex from NTRS 20130010991 (-5.75, -2.8, -2.35). The Ask answer is the site's real output for the query.

| File | What it is |
|---|---|
| `ember_demo.mp4` | 1920x1080, 30 fps, H.264, AAC audio (voice plus quiet music), burned-in subtitles, "AI-assisted video and voice" watermark. Metadata comment: "Voice generated with AI text-to-speech". |
| `ember_voiceover.wav` / `.mp3` | Voice track only, 28.0 s, last speech ends at about 27.8 s. |
| `ember_demo.srt` | Subtitles, word for word the voice-over. |
| `ember_thumbnail.png` | Thumbnail (the map scene). |
| `ember_demo.html` | The animation. Open in Chrome: `?play` plays in real time (screen-record at 1920x1080), `?t=12.5` freezes on one moment. |
| `render.mjs`, `make_voice.ps1`, `make_audio.py` | Rebuild: render frames with headless Chrome, synthesise the voice, mix voice and music. |

Voice: the Windows built-in text-to-speech voice (Microsoft Mark), clearly synthetic. Music: a soft ambient pad synthesised from sine tones, set 24 LU under the voice. Replace the voice by recording your own over `ember_demo.srt`.

Rebuild: `node render.mjs <frames dir>`, `powershell -File make_voice.ps1 -Out <dir>`, `python make_audio.py <ffmpeg> <voice dir> <audio dir>`, then `ffmpeg -framerate 30 -i f%04d.jpg -i mix.wav -c:v libx264 -crf 16 -pix_fmt yuv420p -c:a aac -t 28 ember_demo.mp4`.
