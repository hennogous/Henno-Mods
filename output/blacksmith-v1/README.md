# Blacksmith workshop — first Blender blockout

Built 2026-09-09 from the approved `../imagegen/blacksmith-concept-v1.png` concept.

- `CSC_BLACKSMITH_Workshop_v1.blend`: editable primitive source, hidden joined export-check collection, studio camera and lights. The original startup scene is preserved separately.
- `blacksmith-render-v1.png`: Cycles render of the actual model.
- `blender-viewport-v1.png`: screenshot captured from the live Blender viewport.
- `CSC_BLACKSMITH_Workshop_v1.cn6`: budget-check export using the repository's Blender 4/5-compatible CN6 exporter.
- `budget.json`: source and export counts.

56 primitive-derived source objects: 566 source vertices. Explicit face splitting and three UV channels produce **1,495 CN6 vertices and 783 triangles**, counted from the written CN6 file. Export-check geometry is scaled into mesh data at 30 game units per authoring unit (approximately 171 units high).

This is a shape/material blockout, not a game-ready asset. Materials are provisional Blender shaders, including procedural roof and stone patterns. Final atlas, companion maps, geometry-baked AO, UV layout refinement, state variants, FGX conversion and in-game checks remain. Current UV2 allocates individual face slots for the budget check; its final packing and texel density need refinement before AO baking. No final texture quality or in-game performance is claimed.

Rebuild in a GUI Blender session by executing `build_blacksmith.py`, then `finish_preview.py` once. The first script replaces only its own generated scene; the second is a one-time presentation adjustment following a rebuild. `blender_bridge.py` sends these scripts to the installed add-on's local socket. The material preview is not portable to Civ VI until baked to an atlas.
