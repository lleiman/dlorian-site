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
