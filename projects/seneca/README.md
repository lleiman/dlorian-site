# The Death of Seneca / DLORIAN (public version 4)

URL: https://dlorian.art/seneca.html

## Current nine-image narrative, 2026-10-25
Revised order after author noted the previous eight-image arrangement was incorrect and supplied the original dark-crimson chamber image. Nine unique paintings are shown, with the newly uploaded crimson interior placed **fourth in the sequence** and used as the **homepage card and social preview**. The on-page title cover shows a cropped/toned preview of this image, followed by the full sequence; no numbered painting is duplicated.

01 The Villa (former frame-03.webp)
02 The Summons / soldiers (former frame-04.webp)
03 The Order / fictional inscription (former frame-07.webp)
04 The Last Hours / central crimson chamber (user upload 2026-10-25)
05 The Hand (former frame-08.webp)
06 Paulina / reclining woman (former frame-05.webp)
07 Seneca / portrait (former frame-02.webp)
08 The Bath (former frame-06.webp)
09 The Empty Room (former frame-01.webp)

Original historic named source files under assets/seneca/frame-XX.webp remain intact for provenance and easy rollback; scene-XX filenames are new aliases to the same existing Git objects, with scene-04 newly uploaded. Single origin 2048px WebP artwork rendered directly in HTML and navigable without JavaScript.

## Textual inserts
Four short **direct Latin extracts from Tacitus' Annals** are inserted only after scenes 02, 04, 06 and 08. They are not Seneca-authored quotations or material from the fabricated tablet image.

- after 02: 'illo propinqua vespera tribunus venit' / 'Near evening, the tribune arrived.' (XV.60)
- after 04: 'imaginem vitae suae relinquere' / 'to leave behind an image of his life' (XV.62)
- after 06: 'lenta effugia sanguini praebebat' / 'the blood could escape only slowly' (XV.63)
- after 08: 'exim balneo inlatus et vapore eius exanimatus' / 'Then he was carried into a bath and died from its steam.' (XV.64)

Chapter numbers follow the Latin Library's edition; other editions shift this sequence by one: https://www.thelatinlibrary.com/tacitus/tac.ann15.shtml

## Why art history appears
Rubens is not an artistic ancestor whose style this work must imitate, but a concrete demonstration of the creation of an image: the model for his Seneca was a sculpture later identified as a fisherman. David is a second contrast in scale and theatricality. The former separate sprawling sculpture and painting sections were condensed into a single clearly motivated paragraph with two attributed illustrations and a source footnote, after the artist's gallery.

- Rubens: https://www.sammlung.pinakothek.de/en/artwork/wE4KXQExZ5
- Nationalmuseum research on false identification: https://collection.nationalmuseum.se/en/collection/item/17743/
- David, 1773: https://www.parismuseescollections.paris.fr/fr/petit-palais/oeuvres/la-mort-de-seneque
- Manuscript: https://iiif.biblissima.fr/collections/manifest/7732b9be3e8d876682156a09a60aeb9b863c5e23

Note: fictional writing in **The Order** must not be treated as an actual Latin record. This series is not an archaeological reconstruction.

Files: seneca.html, assets/css/seneca.css, assets/seneca/gallery.json, _build/pages.py, assets/seneca/scene-*.webp.

The portfolio continues to count the existing 11 regular series separately from this editorial project.


## Interactive exhibition update — 2026-10-25

Light / luminosity (2026-10-25 revision): **removed the public global brightness slider and all global B / + / - / 0 brightness shortcuts**. The first brightness treatment is 120% for each of the nine art images. Visitors simply see the curated values; brightness settings are fetched from public read-only `GET /api/seneca/brightness`, while source WebP files remain unchanged. The cover and modal viewer share the brightness of scene 04 and of the currently selected scene, respectively. Art-historical third-party reproductions are not controlled.

Editor: sign in at `/admin.html` using the existing admin token, then follow **Seneca · яркость** to `/seneca.html?edit=1`. The page requests `GET /api/admin/seneca/brightness` with the X-Admin header before rendering any editor controls. The secret is never placed in query parameters. Each image has its own slider, visible only after authorization. Edits preview instantly and auto-save when released via protected `PUT /api/admin/seneca/brightness` with JSON body `{"id":"01".."09","brightness":0.8..1.85}`, with 5% increments. Neutral reset 100% per image. The server atomically stores settings in `/data/seneca-brightness.json` on Railway's persistent volume. Visitors cannot write these values. If editing isn't authorized, a link to `/admin.html` is shown and no sliders are rendered.


Artwork viewer: click any of the nine series paintings for a modal with a whole-image contain-fit presentation, interpretive description, title, count, arrow buttons, keyboard navigation and Esc. Touch swipe also works. External paintings in the historical section retain their institution links.

Artist's statement: author affirms that before this series he read Seneca's philosophical writings, his letters, and Tacitus. The note expresses a pursuit of historical and psychological fidelity where sources permit, while explicitly distinguishing visual invention from historical fact.

Audio: assets/seneca/seneca-study-01.mp3 is an original 48-second procedural ambient study in D minor. It is a **placeholder original composition, not a Suno-generated track**. The fixed page player has actual play/pause, progress and volume, starts only after user interaction, loops while playing. Replace the sound file or change the player's src when a finished Suno export is approved.

Suno instrumental brief: Dark, intimate neoclassical ambient for a nine-image visual narrative about Seneca's final hours, AD 65. Four to five minutes; continuously evolving deep bowed double bass and cello harmonics, shadowed viola drones, distant bronze resonance, faint granular air, long stone-chamber reverberation. D minor with occasional modal inflections, unresolved sparse dissonance, almost imperceptible rhythm, no climax, grief without melodrama, deliberate fade into silence. No vocals, no spoken words, no heroic trailer scoring, no percussion beat, no bright modern piano, no arpeggios or EDM elements.

New client script: assets/js/seneca-experience.js.


## 2026-10-25 — audio drama prototype and bottom cinema strip

The new full-width, black/white, film-style soundtrack strip uses modes:
- DIALOGUE: `assets/seneca/seneca-dialogue-study.mp3`, 185.76 seconds. Contains two distinct **synthetic rehearsal voices** (Seneca, Pompeia Paulina) mixed with a new original, procedurally generated ambient score; 21 lines.
- SCORE: `assets/seneca/seneca-score-study.mp3`, identical 185.76-second instrumental timeline, with no voices.
- SILENCE: stops audio immediately; page and controls stay usable. Changing between dialogue and score preserves the playhead.

No autoplay. Caption/subtitle lane belongs to the **player strip at the bottom of the screen**, and never overlays the painting. Synchronized per-line metadata is at `assets/seneca/seneca-dialogue.json`; standalone subtitle file `assets/seneca/seneca-dialogue.vtt`. The archived full transcript is on the exhibition page, below historical context, and source labels distinguish the ancient Latin originals from English reconstructions.

Historicity:
- The dialogue is a dramatic *reconstruction*, NOT a transcription of historical speech.
- Seneca's prior Latin writings quoted verbatim: `Incertum est quo loco te mors exspectet; itaque tu illam omni loco exspecta.` (Epistulae morales 26.7); `Accipio condicionem, non reformido iudicium.` (Epistulae morales 26.6).
- Tacitus reports Seneca's words in Annals XV.63 as `Vitae delenimenta monstraveram tibi, tu mortis decus mavis.` This is attributed to Tacitus, *not* separately authenticated as a verbatim recording.
- Paulina's original words are not preserved; her dialogue here is all fictionalized in reference to her choice as described by Tacitus in XV.63. Tacitus XV.64 records her survival. The dramatic coda does not depict Paulina's death.
- English versions of Latin lines are original editorial renderings.

Production warning: eSpeak speech voices are **rough demo-quality**, intentionally labelled as synthetic rehearsal voices. They are not definitive actor-grade performances. Replace both original mp3s with time-aligned professionally voiced/mixed versions once approved; align captions to final timings. Keep `dialogue.json` and `dialogue.vtt` in sync.

Original generated audio source and cue generator: `/mnt/data/seneca_drama/produce.py` in the current work container (not committed). The two output mp3s and supporting transcript are committed to the site repository.

## 2026-10-25 — compact sound archive and art history extension

- Full 21-reply transcript defaults **collapsed** (<details> without open) for quieter reading. Supplemental description of reconstructed audio is also collapsed.
- Film subtitle lane displays only actual spoken words and speaker name (and Latin translation when appropriate); it is blank in pauses, with no DRAMATIZED/RECONSTRUCTED filler. "DRAMATIC RECONSTRUCTION" stays on the player label and in the expanded commentary.
- Historical context expanded to six works: Rubens (Alte Pinakothek), workshop of Gerard van Honthorst (Centraal Museum 4498, 1623–27), Jacques de l'Ange (c.1640–50; attribution based on catalogue records), Luca Giordano (Louvre MI 871, c.1684–85), David (Petit Palais PDUT1154, 1773), and Manuel Domínguez Sánchez (Prado, 1871). Public-domain historical artworks are served from Wikimedia Commons and credited to their source collections.
- No fabricated "ancient scrolls" used. Actual manuscript: Codex Laurentianus Mediceus Plut.68.2 fol.6v, 11th century. The photographed folio depicts Annals XI/XII, NOT the Seneca passage XV.60–64. The other image is the incipit of the printed first edition of Annals XI–XVI (Venice c.1471–72), NOT the actual paragraph describing Seneca.
- The record section contains six collapsible verified Latin selections from Tacitus XV.60–64 with brief editorial English translations, distinguished from the fictional dialogue.

Reference records:
- Honthorst: https://www.centraalmuseum.nl/en/collection/4498-de-dood-van-seneca-gerard-van-honthorst
- Giordano: https://collections.louvre.fr/ark:/53355/cl010059591
- Domínguez Sánchez: https://www.museodelprado.es/aprende/enciclopedia/voz/dominguez-sanchez-manuel/112973e3-a8cd-4533-a027-ec250d94725c
- Jacques de l'Ange file: https://commons.wikimedia.org/wiki/File:Jacques_de_l%27Ange_-_Death_of_Seneca.jpeg
- Tacitus manuscript: https://commons.wikimedia.org/wiki/File:Tacitus,_Annals,_Florence,_Plut._68,2.jpg
- Printed first edition: https://commons.wikimedia.org/wiki/File:Tacitus,_Annales_XI-XVI,_editio_princeps,_ca._1471-72,_incipit.jpg


## 2026-10-25 — eight-image rearrangement (latest editorial decision)

The author requested the *eighth painting (The Bath) removed* from the public Seneca sequence, the old central red painting (The Last Hours, previously fourth) moved into slot eight, and the Seneca portrait (previously seventh) moved into slot four. To avoid duplicate artworks and keep a contiguous eight-picture gallery, the former ninth painting (The Empty Room) moves to slot seven. **The cover and homepage continue showing the red Last Hours painting**; only the order within the sequence changes.

Current display order:
01 The Villa / scene-01-villa.webp
02 The Summons / scene-02-soldiers.webp
03 The Order / scene-03-tablet.webp
04 Seneca portrait / scene-07-seneca.webp
05 The Hand / scene-05-hand.webp
06 Paulina / scene-06-paulina.webp
07 The Empty Room / scene-09-empty-room.webp
08 The Last Hours / scene-04-last-hours.webp

The Bath asset scene-08-bath.webp is retained in Git history/source assets but is **not rendered anywhere in the public gallery**. The bath remains a subject mentioned in Tacitus' historical record; no image is falsely described as The Bath. The interlude formerly placed after The Bath was removed. The other three selected Tacitus excerpts remain after images 02, 04 and 06.

The per-image brightness settings on the Railway volume migrate from the old 9-position map to version 2. New 04 inherits former 07 (Seneca), new 07 inherits former 09 (Empty Room), and new 08 inherits former 04 (red tableau); edits to the six unchanged paintings persist. Frontend brightness API only reports 8 frames. Audio dialogue and transcript remain unchanged.
