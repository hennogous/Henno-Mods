# Blacksmith workshop — iteration 2

Second primitive-built interpretation of `../imagegen/blacksmith-concept-v1.png`. Version one remains in `../blacksmith-v1/`.

## Changes

- Bowed the main ridge and roof along their length, preserving the swept gable profile.
- Broadened the chimney base and increased its taper.
- Changed the canopy pitch and slightly splayed the posts.
- Increased and brought forward the anvil; added an open quenching trough.
- Simplified small door fittings and removed timber faces buried against the front wall to fund the larger forms.
- Added provisional grain and surface variation, softened mortar lines, and mapped the roof tiles by surface distance to eliminate stretching.

## Verified budget

58 editable primitive-derived mesh objects, 581 source vertices. The joined export-check mesh has explicit hard face splits and three UV layers. The written CN6 contains **1,491 vertices and 781 triangles**, four vertices fewer than version one. Vertex values are finite and triangle indices are within range.

## Files

- `CSC_BLACKSMITH_Workshop_v2.blend`: saved working scene with editable source, hidden export-check geometry, and preview studio. Earlier scenes are preserved.
- `CSC_BLACKSMITH_Workshop_v2.cn6`: measured budget-check export.
- `blacksmith-render-v2.png`: Cycles preview of the real model.
- `blender-viewport-v2.png`: live Blender viewport screenshot.
- `budget.json`: counts.
- `build_blacksmith.py`: complete rebuild script; runs in GUI Blender, replacing only its own generated scene.

Materials are still procedural Blender previews. Final image atlases, companion maps, geometry-baked AO, final UV packing, clean export-only scene, FGX conversion and game testing remain. The provisional CN6 material names do not constitute a game material setup.
