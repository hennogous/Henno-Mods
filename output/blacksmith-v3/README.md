# Blacksmith workshop — textured version

The approved version-two geometry now uses one 1024×1024 painted material atlas, aligned companion maps, and geometry-baked AO. **1,491 CN6 vertices, 781 triangles, one material.**

Open `CSC_BLACKSMITH_Workshop_v3.blend`. Keep its `Textures` folder beside it: images use relative paths and are deliberately external, not packed. `blacksmith-render-v3.png` and `blacksmith-thumbnail-v3.png` show the actual Blender model.

## Texture set

- `_B`: artistic base-color atlas generated with the built-in imagegen tool; prompt below. The original generated image is retained as `Textures/blacksmith-atlas-source.png`.
- `_N`: restrained normal detail derived with the repository's `csc_generate_pbr_maps.mjs` at normal strength 0.45.
- `_G`, `_M`: pixel-aligned gloss and metalness, refined with explicit material regions in `refine_companion_maps.mjs`.
- `_E`: emissive color limited to the coals region; uses UV3.
- `_AO`: Cycles geometry AO, baked into a fresh non-overlapping UV2 smart-project pack at final mesh scale. 1024 pixels, 96 samples, 34 game-unit ray distance, 5-pixel margin. The studio and other models were absent during baking.

UV1 supplies visible materials and normals; UV2 supplies AO; UV3 supplies emissive. Blender preview multiplies AO into base color at 80% strength and converts gloss to roughness. The geometry was re-exported to CN6 after UV changes. FGX conversion, Asset Editor materials and cooking are outside this texture handoff.

`validation.json` records the external-map and mesh checks. `texture_and_bake.py` rebuilds from the v2 Blender file; `reload_and_render.py` explicitly reloads the external images; `final_check.py` performs the final verification and fixes the stump side-grain issue found in the render.

## Base-color prompt (built-in imagegen)

Use case: stylized-concept. Generate a flat square 1024 by 1024 base-color texture atlas for the low-poly Civilization VI blacksmith workshop we are making. This is a technical UV texture sheet, completely flat orthographic, edge-to-edge painted material regions, NOT a building illustration. NO borders, labels, text, wireframes, perspective, objects, cast shadows or ambient occlusion. Hand-painted Firaxis Civilization VI texture sensibility: bold readable low-frequency strokes, warm muted colors, subtle broad edge highlights and purposeful material variation, not photographic noise, not cartoon black outlines. STRICT ATLAS LAYOUT with clean straight boundaries: TOP LEFT QUARTER (x 0-50%, y 0-50%): terracotta roof shingles, 8 horizontal staggered rows with about 8 broad overlapping red-ochre clay tiles per row, slight uneven hand-crafted shapes, warm rusty orange/umber, subtle painted lower lips and shallow seams. The workshop roof explicitly requires these painted tile seams. TOP RIGHT QUARTER (x 50-100%, y 0-50%): chunky irregular warm gray-beige stone masonry, 7 horizontal courses with about 5 broad rough stone blocks per course, muted low-contrast mortar and softly painted broad stone face facets; no heavy black outlines. BOTTOM LEFT QUARTER (x 0-50%, y 50-100%): continuous uninterrupted dark warm oak material with vertical lengthwise grain, broad loose painterly streaks, a few faint knots; absolutely NO plank divisions, boards, frames, seams or individual object shapes. BOTTOM RIGHT QUARTER is divided as follows: its UPPER HALF (x 50-100%, y 50-75%) is continuous warm buff lime plaster with gentle painterly mottling, no bricks or cracks. Its LOWER HALF (x 50-100%, y 75-100%) is EIGHT equal square material swatches in a grid of FOUR columns by TWO rows. Upper swatch row, left to right: dark cool blue-gray forged iron; warm golden cut wood endgrain with soft irregular concentric rings; muted burnt-orange woven cloth; glowing orange-yellow coals texture. Bottom swatch row, left to right: almost black matte soot; dark desaturated teal water with minimal broad ripples; medium warm brown leather; dull gray steel. Keep each little swatch a flat continuous material patch. Keep layouts exactly aligned to half, quarter and eighth image divisions. No gutters. A production-ready artistic base-color sheet with readable materials and moderate saturation. All painted detail stays inside its stated material region.

The generated plaster/swatch boundary differed from the prompt; UVs and deterministic masks use the visually inspected output boundaries rather than assuming the requested coordinates.
