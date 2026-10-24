# The Death of Seneca

**DLORIAN visual project · 2026 · WIP**

Published URL: https://dlorian.art/seneca.html  
HTML: /seneca.html · CSS: /assets/css/seneca.css · approved artwork: /assets/seneca/frame-01.webp

## Status (24 October 2026)

1 approved master image; remaining 6 images still to be produced and selected. The project page must never imply those six images exist.

## Concept

One invented Roman chamber; the last hours of Seneca. Seven frames alternate scale and attention:

1. Wide establishing view: Seneca in the hall, surrounding witnesses, statue and bronze basin. **Approved.**
2. Extreme detail: aged wrist over basin, folds of fabric and water. **Planned.**
3. Side wide: the same hall and statues, figures dissolving in darkness. **Planned.**
4. Object macro: small ceramic cup with poison. **Planned.**
5. Medium: three witnesses react without melodrama. **Planned.**
6. Portrait: Seneca's tired, composed face. **Planned.**
7. Empty wide: same opening geometry, now without people, basin remains. **Planned.**

**Scale rhythm:** WIDE → DETAIL → WIDE → OBJECT → MEDIUM → CLOSE → WIDE.

## Locked art direction

The approved reference is the dark burnt-crimson image embedded on pp. 1–2 of the source handoff PDF. The sketch on p. 2 is a compositional reference ONLY. Do not revert to sepia paper or white gouache.

Look: dense Old Master painterly brushwork; black and restrained red; subdued reflected firelight; nearly invisible figures; dramatic architectural symmetry; no glossy digital look, modern objects, neon, typography, fantasy armour or excessive gore. 16:9.

Keep Seneca's face, the room, the statue, basin, clothing and lighting consistent across frames. Use authentic Midjourney image/style references (do not invent URLs). Produce 02, 03 and 04 first; compare against 01 for palette, texture, darkness, anatomy and architecture before continuing.

## Historical source

Tacitus, *Annals*, XV.60–64, on Seneca's final hours in 65 CE. The architecture, camera angles, placement of witnesses and empty-room epilogue are artistic inventions; the shot order is not an exact minute-by-minute reconstruction. Historical source:
https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.02.0078%3Abook%3D15%3Achapter%3D64

## Project origin

Supplied PDF: *Seneca_Visual_Sequence_Handoff_RU.pdf*, dated 24 Oct 2026. Full Midjourney prompts for all seven shots are in its pp. 4–7; two optional inserts (Paulina, steam) are on p. 7. The source brief explicitly says not to expand beyond seven frames without artistic necessity.

## Publishing notes

- Keep the master frame visible on the public page.
- Do not fabricate or silently replace missing images.
- When frames 02–07 have been approved, add individual image assets and promote planned text cards into illustrated spreads.
- This project is separate from the existing 11 artwork series and does not change the 334-work count.
- Home and all gallery pages link to the project through generated navigation in _build/pages.py; the homepage also features it as an editorial band.
- Flask static file allowlist in server/app.py includes seneca.html; Dockerfile's COPY *.html and COPY assets include this page/assets.
