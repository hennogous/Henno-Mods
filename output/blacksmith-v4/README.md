# Blacksmith workshop — stronger shape hierarchy

Revision responding to Henno's 2026-09-10 feedback: the building and particularly the gable-edge timber were too thin compared with the approved concept and Firaxis's shape examples.

The sloping timber is the **bargeboard**. Earlier versions offset its lower edge vertically, which made the board's visible width shrink on steep roof sections. This version uses a mitered perpendicular offset, varying slightly along the curve, and increases its depth. The ridge, canopy fascia, posts and braces also have more weight. The house widens 12% away from the attached bay, and overall height reduces 5%.

The existing painted atlas is reused. UVs are updated for the revised forms, the swept boards' grain follows their curves, and AO is freshly baked from the new geometry. No detail geometry was added: **1,491 CN6 vertices, 781 triangles, one material**, unchanged from version three.

## Review

- `blacksmith-render-v4.png`: textured render.
- `shape-comparison-v3-v4.png`: clay comparison, **v3 left / v4 right**. Judge the large and intermediate forms here, without painted tiles and masonry.
- `CSC_BLACKSMITH_Workshop_v4.blend`: textured working scene; keep `Textures/` beside it.
- `CSC_BLACKSMITH_Workshop_v4.cn6`: budget-check export.
- `CSC_BLACKSMITH_Workshop_v4_source.blend`: editable primitive source.
- `build_source.py`, `texture_and_bake.py`, `render_comparison.py`: reproducible construction, texture/AO, and comparison steps.

All six 1024px texture maps are external. UV1 is material mapping; UV2 is a fresh unique AO pack; UV3 is emissive mapping. AO uses Cycles, 96 samples, 34 game-unit distance, with the preview studio excluded. FGX conversion and game cooking remain outside this art-review handoff.

The Firaxis 3:2:1 reference guides visual hierarchy, not a literal vertex allocation. A low vertex count alone does not establish the style; silhouette, structural weight and readable changes of direction must carry it before texture detail is added.
