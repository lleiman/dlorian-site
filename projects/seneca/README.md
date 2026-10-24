# The Death of Seneca — public edition

Live page: https://dlorian.art/seneca.html
Repository: lleiman/dlorian-site

## Authorial intent and delivery
The work is a single dark, crimson-lit imagined Roman chamber. The supplied PDF *Seneca_Visual_Sequence_Handoff_RU.pdf* (24 Oct 2026) originally describes a seven-frame visual sequence (one frame approved, six pending) with an exact visual rhythm: WIDE → DETAIL → WIDE → OBJECT → MEDIUM → CLOSE → WIDE. Reference B (the dark painting) outranks the historical drawing A.

In a subsequent chat the author clarified that **seven further images are expected**. Therefore the publication currently says “Seven further images are in preparation”, and the manifest reserves slots 02–08. Subject 08 is unassigned. Do not invent that image. When the intended final total is confirmed, adjust manifest and label without changing the source brief.

## Display principles
- The artist's works appear FIRST, uninterrupted and not mixed with historical paintings or text quotes.
- The first approved work is shown once, at full browser width, followed by future approved works from a manifest.
- Production storyboard texts and prompt engineering are preserved in the source brief, not presented as a public exhibition.
- Historical context, the Tacitus passage, historical paintings, the black-marble statue, and the digitised witness of Tacitus form distinct SECONDARY editorial sections.
- Do not invent seven pictures, publish a placeholder as an artwork, or quietly replace the existing approved work with a generated interpretation.
- Avoid switching back to a sepia illustration style. The approved look is dense dark oil painting, predominantly black with smouldering crimson.
- Prefer the artist's original high-resolution file when obtained. Frame 01 is currently extracted from the PDF and may contain compression.

## How to add new images
1. Upload the finished approved file to assets/seneca/frame-NN.webp or .jpg. Keep it 16:9 unless the author deliberately chooses another ratio.
2. Edit assets/seneca/gallery.json: for that frame set status to published, src to same-origin assets/seneca/frame-NN.webp, title, and descriptive alt.
3. Commit: the client-side gallery in assets/js/seneca-gallery.js automatically displays all newly approved frames, without editing seneca.html.
4. Verify responsive behavior on the published page. The pending counter updates automatically.
5. Keep image-specific authorship and captions accurate; the archive and history illustrations must not be mistaken for DLORIAN work.

## Sources
Tacitus, Annales XV.60-64 (Latin: https://www.thelatinlibrary.com/tacitus/tac.ann15.shtml; English Perseus: https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0078%3Abook%3D15%3Achapter%3D60). XV.62 contains “imaginem vitae suae relinquere” in indirect speech as Tacitus' account.

Peter Paul Rubens, The Death of Seneca, c.1612/13, Alte Pinakothek, Munich: https://www.sammlung.pinakothek.de/en/artwork/wE4KXQExZ5. Gallery image from Wikimedia Commons (public-domain painting); the institution's images have their own credit/license information.

Jacques-Louis David, La Mort de Sénèque, 1773, Petit Palais, Paris: https://www.parismuseescollections.paris.fr/fr/petit-palais/oeuvres/la-mort-de-seneque. Image is the completed PDUT1154 painting rather than the PDUT1166 sketch; Paris Musées marks this digital photograph CC0.

Old Fisherman, traditionally Dying Seneca, Roman copy now Louvre MR314: https://collections.louvre.fr/ark:/53355/cl010275490; Nationalmuseum's evidence for Rubens' use and historic mistaken attribution: https://collection.nationalmuseum.se/en/collection/item/17743/. Embedded photograph from https://commons.wikimedia.org/wiki/File:Old_Fisherman_Louvre_Ma1354.jpg (Jastrow, public domain).

Laurentianus Mediceus Plut. 68.2: 11th century, Biblioteca Medicea Laurenziana, Florence. Digital catalogue and viewer https://iiif.biblissima.fr/collections/manifest/7732b9be3e8d876682156a09a60aeb9b863c5e23. No specific manuscript folio image has been included because none was identified and verified for Annales XV.60–64.

## Deployment integration
Flask route OPEN_FILES includes seneca.html. Dockerfile COPY *.html /srv and COPY assets /srv/assets bring all additions into deploy. Existing site generator _build/pages.py generates home link; adjust its editorial teaser to reflect the seven forthcoming images. This page is a standalone editorial exhibition and does NOT change counts for the site's established 11 gallery series.
