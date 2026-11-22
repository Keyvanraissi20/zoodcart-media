# Cartoon post engine (zoodcart)
Reference implementation of the 2026-11-22 "friend-helps" Reel (reels/2026-11-22-friend-helps.mp4).
- scene.html: HTML/SVG scene rendered deterministically by `render(t)`: room background, cartoon characters
  (`character()` with expressions brow/mouth, lip-sync from audio amplitude, hand poses, anger/sweat/cloud/bulb/sparkles),
  browser checkout panel with cursor/clicks/errors/success, zoodcart virtual card, confetti, Persian subtitles with speaker pills, CTA end card.
  Fonts are loaded from ./font/package/fonts/ttf (run `npm pack vazirmatn` + extract in the work dir).
- build.py <workdir> preview <t1,t2,...> | video : computes timeline from clip durations (aud/<key>_f.wav), injects CUES/AMPS, renders frames with Playwright -> silent.mp4.
- mix.py: places dialogue clips + synthesized SFX -> final.mp4 (H.264 High, yuv420p, AAC).
Audio clips: one Gemini TTS request per line (tts/requests/DATE-<slug>-<key>.json), then trim silence + atempo=1.08.
Voices used: narrator Kore, main character Fenrir, friend Charon.
