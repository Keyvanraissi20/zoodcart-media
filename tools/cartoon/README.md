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
2026-11-25 REEL variant "grocery-tap" (scene_/build_/mix_2026-11-25-grocery-tap.*), mode حضوری, supermarket checkout abroad:
- `bgSupermarket()` (procedural product shelves "Aisle 1-3", ceiling lights, "Fresh Market" sign at y≈170), checkout counter with moving conveyor belt + groceries.
- `posTerminalX(x,y,sc,state,t,dt)` = posTerminal + state 3 "Declined" (red X, shake); `bankCard()` generic grey card attempt; `cardHold()`/`phoneHold()` props in hand;
  receipt strip printing from the counter POS after approval. 3 characters (friend slides in from left at E.minaIn). Looks: `hairQuiff`+`stubble`, `hairAuburn`(+headband)/`hairAuburnBack`, cashier `capRed`+`ponyBack`+`vestSvg`.
- Panel: POS close-up (card -> Declined x2 -> later phone -> Approved) and Wallet "Add to Wallet" page. SFX: declined buzz uses gt() (ffmpeg aevalsrc has no '>').
- Audio was long (~38 s): internal pauses compressed with silenceremove stop_periods=-1 (stop_silence=0.15) + atempo 1.18–1.24. Voices: Kore, Charon (Reza), Aoede (Mina), Zephyr (cashier).
2026-11-26 STORY variant "myth-vs-fact" (scene_story_myth.html + build_story_myth.py + mix_story_myth.py), format F4 quiz, mode آنلاین, coworking space:
- `bgCowork()` (big window with skyline, "Hub 9 · Cowork" sign at y≈940, pendant lamps, corner plants), wooden desk in front (y 1290+) with one shared `laptopBack(x,y,sc,lit)`
  between the characters (keep laptops OUT of the face area — a laptop in front of a character hid the mouth) + steaming mug.
- Panel pages: quiz hook (big "?" + pulsing باور/واقعیت buttons), myth card in HTML (`.myth`) + red `.stamp` "باور غلط!" slamming in (scale 2.2→1),
  foreign checkout (2 item rows AI plan / online course, card auto-fill, cursor, "Subscribe & Pay" → "Payment successful"), `giftCard()` + envelope with check,
  safety page: real "zoodcart.ir" row (lock + check) vs suspicious link row (shake, strike-through, red X) + shield line.
- `qCloud(x,y,k)` thought cloud with "?" over a confused character. New looks: `hairQuiffBrown`+`hoodStrings`+glasses (Behrad), headscarf `scarfBack(c)` (hairBack) + `scarfFront(c)` (hairSvg, with bangs) (Taraneh).
- Audio was ~39 s raw: internal pauses compressed (silenceremove stop_periods=-1 stop_silence=0.15) + atempo 1.10–1.30 → 33 s. Voices: Kore, Fenrir (Behrad), Leda (Taraneh). SFX: stamp thud.
2026-11-27 STORY variant "host" (scene_story_host.html + build_story_host.py + mix_story_host.py), format F2 host-to-viewer, mode حضوری:
- `bgStreet()` shopping street at dusk (sky gradient, far buildings, "Paper Moon Books" storefront left, street lamp, sidewalk), small street `vendingMachine()` right.
- `vendingMachine(x,y,sc,state 0 Tap|1 Processing|2 Approved,t,drop 0..1)` with contactless reader + can dropping into tray. `taxiInterior(t,state)` = back of front seat with TAXI strip, mounted posTerminal, side window with scrolling city.
- Host look: `hairCurlyTop` + `headset` mic + `jacketTrim` (option apron), counts places with a big yellow number bubble `#cnt` (۱/۲/۳) + pulsing highlight rect on the matching storefront (`#hl` layer).
- Panel pages: hook (phone + آنلاین check vs حضوری "?" flipping to check at E.no), 3 badges intro, Wallet "Add to Wallet", bookshop counter with small cashier `character()` inside the panel svg (sc .55, `hairRedBun`), vending close-up, taxi close-up. Keep the phone BESIDE the terminal screen, not over it.
- Audio ~35 s raw → pauses compressed + atempo 1.12–1.22 → 32.3 s. Voices: Kore, Orus (host Kian), Aoede (cashier).
2026-11-27 REEL variant "game-sofa" (scene_/build_/mix_2026-11-27-game-sofa.*), mode آنلاین, siblings on a living-room sofa at night buying a game on a foreign site:
- `bgLivingRoom()` (striped wallpaper, night window with moon/stars/skyline, floor lamp glow, abstract frame, plant, sofa back) + `sofaFront()` (seat cushions, arms, rug, coffee table with popcorn + game controller). Seated characters: torsos hidden by the seat, hands at y>200 disappear behind it.
- Panel pages: shop checkout (`gameCover()` invented "SKY DRIFT", card field, "Buy now", red "Payment failed" banner with shake x2, cursor), zoodcart.ir HTML page with 3 check rows (احراز هویت / شارژ با کارت بانکی / ویزا کارت آماده‌ست) ticking at E.k1..k3 + glowing card, checkout again with typed "VISA •••• 4826" autofill → "Payment successful" → `dlBar()` download progress.
- Looks: `hairTopBun` + hoodie strings (option apron) for Ava, `beanie` + `beardFull` + glasses for Pouya. Keep the phone hand y<200 so the arm is drawn in front of the torso (both hands >200 = arms behind body).
- Audio ~42 s raw → pauses compressed + atempo 1.12–1.2 → 38.3 s. Voices: Kore, Zephyr (Ava), Fenrir (Pouya). SFX: error buzz, check ticks, success beep.
