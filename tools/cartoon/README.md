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
2026-11-23 "uni-apply" variant (scene_/build_2026-11-23-uni-apply.*): library background (procedural bookshelves), female lead with long hair
(`hairBack` option drawn behind the body + `hairLong`), `hairSpiky`, glasses on lead. Voices: Leda (Sara), Puck (Nima).
Tip: if total > 38 s, use atempo≈1.18 on the longest clips.
2026-11-24 STORY variant (scene_story_cafe.html + build_story_cafe.py + mix_story_cafe.py), 1080x1920, safe zone y 250..1600:
- Café background (`room()`: bricks, window with city, cup shelf, pendant lamps, "Café Luna" sign), counter in front (y 1290+) with small POS + coffee cup.
- Top panel (y 270..910) with header pill (`#stp` step badge + `#ht` title) and pages switched by events: hook (card + POS + "?"), zoodcart.ir page with card,
  Wallet screen (Add to Wallet button press -> card flies into stack -> Added check), POS close-up, 3 place badges (café / shop / hotel & travel).
- Reusable helpers: `posTerminal(x,y,scale,state 0 Tap|1 Processing|2 Approved,t)`, `phoneBig()`, `phoneInHand()`, contactless `arcs()`,
  hair styles `hairBob`+`beret`, `hairShortCurl`+`beardGrey`, `apronSvg` (option `apron`), option `hold` (prop drawn with the arms).
- IMPORTANT: inline SVG inside an rtl parent renders text-anchor start on the wrong side -> CSS `svg text{direction:ltr}` is set.
- Subtitles at top:1335 (end above 1600). Voices: narrator Kore, host Negar Aoede, barista Orus. Format F3, mode حضوری.
2026-11-25 STORY variant "trip-day" (scene_story_trip.html + build_story_trip.py + mix_story_trip.py), format F5 montage, mode سفر:
- 3 crossfading backgrounds (reusable): `bgAirport()` (window + taxiing `plane(x,y,sc)` + DEPARTURES board), `bgMetro()` (tiles, blue stripe, M sign, Metro/Line board),
  `bgBazaar()` (arches, souvenir shelves, striped awning, lanterns, "Souvenir Corner" sign). Opacity driven by E.s2/E.s3.
- Panel pages: hook route map with 3 pins + flying plane, hotel booking checkout (card auto-fill, "Pay & Book" -> "Booking confirmed"),
  metro `ticketMachine(x,y,sc,state,t,ticketK)` close-up (Tap -> Processing -> Approved, ticket slides out), POS close-up, badges آنلاین/حضوری/توی سفر.
- Scene label pills ("صحنه ۱/۲/۳") flash at each scene change. New looks: `capBlue`+`backpackStraps` (traveler), `hairBunGrey`+`scarfSvg` (shopkeeper), `phoneInHandS(h,glow,skin)`.
- TTS lines started with "صحنه‌ی اول/دوم/سوم" -> cut off with atrim (pause found via RMS) to stay < 35 s; better: don't voice scene labels. Voices: Kore, Puck (Arash), Zephyr (shopkeeper).
