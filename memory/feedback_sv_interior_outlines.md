# SV interior outlines

19 October 2026: Bakery and Cafe painted sprites received a directional-shadow study. Henno rejected the first strong top-left lighting pass as too much and requested a midpoint. Keep readable, moderate dormer/eave shadows and natural original highlight brightness; avoid deep navy side walls, yellow rim light and dramatic contrast. The medium-strength review PNGs and editable XCFs are under `C:\Users\Shadow\Desktop\Codex\art-work\sv-painted-20261019\medium-shadows-02\`; user acceptance is still pending. Original paintings remain in sibling `bakery-01` and `cafe-01` folders.

14 October 2026: Henno asked for thicker black outlines around the interior objects in both the Tailor and Fashion House painted SV sprites.

Henno accepted the thick interior outline treatment as the standard for all CSC SV sprites, and chose the Tailor's restrained saturation/tonal balance as the colour standard. The installed CSC skill now owns the directive in `references/art-strategic-view-production.md` and bundles the approved Tailor PNG in `assets/sv-style/CSC_TAILORS_SV_Tailor.png`. Preserve each Quarter's intended hues while matching that saturation and tonal treatment.

Use bold black boundaries around significant whole props and architectural masses, with the outside silhouette slightly heavier. Keep roof tiles, garment seams/folds, stone joints and other surface detail quiet. Preserve source scene contents, palette and framing. The line weight must remain legible at the final SV sprite size.

Review paintings are generated non-destructively under Desktop/Codex; keep existing Working Files masters intact until the selected revision is accepted.

Delivered both transparent painted PNGs and 1600px editable XCFs under `C:\Users\Shadow\Desktop\Codex\art-work\sv-painted-20261014\revision-01\`. GIMP saved/reopened both XCFs and retained the live Brightness +5 filter. PNGs are RGBA with transparent margins and no clipping. `manifest.json` retains the built-in ImageGen prompts and sources. User review remains open; no runtime states or installed assets changed.

Fashion House palette normalisation is in sibling `revision-02`, with a new PNG/XCF and prompt manifest. Strong outlines remain; electric purple, orange, greens and garment colours were moderated against the approved Tailor. GIMP saved/reopened the new XCF and retained Brightness +5.

15 October: Henno manually moved the Fashion House painted SV image **up 30px in its 1600px XCF**. Preserve this asset-specific placement correction when reproducing that composition: Y offset -30 relative to the packaged placement (revision-02 layer origin changes from 378,378 to 378,348, retaining the 843px art square). Scale the offset proportionally if canvas resolution changes (-4.8px equivalent at 256). This is an XCF placement correction, not a Blender camera adjustment or a new offset for all SV buildings. Do not apply it twice to Henno's already-corrected XCF.

Textile Workshop also painted from Henno's supplied `CSC_TAILORS_Textile_Workshop_Icon_SV_Input.png`, using the bundled Tailor reference. Deliverables are under sibling `textile-workshop-01`: transparent PNG, verified 1600px XCF with live Brightness +5, and prompt manifest. Source props retained; alpha bounds are clear of canvas edges. Runtime integration remains outside this painting request.
