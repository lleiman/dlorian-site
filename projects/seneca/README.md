# The Death of Seneca / DLORIAN (public edition)

Published project: https://dlorian.art/seneca.html
Status: **complete eight-image visual sequence**, October 2026.

## Source and sequence

Eight image files were supplied by the author in the project conversation. Files are stored in `assets/seneca/frame-01.webp` through `frame-08.webp`, optimized at WebP quality 80, without cropping. Seven files retain 2048 × 1147 pixels; the sixth has 1456 × 816 pixels.

**Exhibition order approved 24 October 2026:**
01 The Chamber (empty hall, drapery and bronze basin; opening hero)
02 Seneca (portrait)
03 The Villa (monumental exterior)
04 The Summons (Roman soldiers)
05 The Witnesses (attendants around a reclining person)
06 The Bath (figure in steaming bath)
07 The Tablet (a generated inscription)
08 The Hand (hand over a basin)

This is an associative visual sequence, not minute-by-minute chronology. The tablet lettering is an AI-generated pictorial element, **not a historically authenticated Latin inscription**.

The earlier single red-crimson master image appeared in the initial PDF handoff. It remains recoverable in Git history at commit `d175c5f201f7048c40db0fb1bc1d56dcc6fb2ba6`; the new user-supplied first image supersedes it by explicit editorial decision.

## Implementation

`seneca.html` contains all eight images in actual HTML (hero 01, gallery 02–08). No JavaScript or network manifest is required to show them. `assets/seneca/gallery.json` is kept as machine-readable project metadata with explicit sizes, alt text and ordering. The previous pending-images script is no longer loaded.

`_build/pages.py` generates the homepage project preview using `frame-01.webp`, whose new subject is the empty chamber. All gallery images remain under the same origin.

Keep the artist's complete eight-image gallery before the archival section. Historical paintings from Rubens and David, the Old Fisherman sculpture and Tacitus' textual witness are editorial context, not works by DLORIAN.

## Historical sources

Tacitus, *Annales* XV.60–64: https://www.thelatinlibrary.com/tacitus/tac.ann15.shtml
Perseus: https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0078%3Abook%3D15%3Achapter%3D60

Rubens, *The Death of Seneca*: https://www.sammlung.pinakothek.de/en/artwork/wE4KXQExZ5

Jacques-Louis David, *La Mort de Sénèque*: https://www.parismuseescollections.paris.fr/fr/petit-palais/oeuvres/la-mort-de-seneque

Old Fisherman / formerly called Dying Seneca: https://collections.louvre.fr/ark:/53355/cl010275490

11th-century Codex Laurentianus Mediceus, Plut. 68.2: https://iiif.biblissima.fr/collections/manifest/7732b9be3e8d876682156a09a60aeb9b863c5e23

## Future additions

When the series changes, update both the page and the JSON manifest. Do not restore provisional “forthcoming” language unless there is a new genuinely unfinished cycle. Do not silently alter the eight works or their sequence.
