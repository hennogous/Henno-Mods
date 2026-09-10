# Blacksmith v5 texture refinement — 2026-09-10

Henno authorized pulling Henno-Mods and improving the blacksmith toward the Firaxis
watermill/commercial texture references. Main fast-forwarded from 2c53597 to d5cb69e;
local shape-feedback memory was preserved. No commit/push performed.

Latest preview: `output/blacksmith-v5/CSC_BLACKSMITH_Workshop_v5.blend`.
Clean export: same folder, `CSC_BLACKSMITH_Workshop_v5_export.blend`.
Portable handoff: `blacksmith-v5-textured.zip`, includes external Textures and CN6.
Editable primitive geometry remains in the sibling v4 source blend.

Repainted B with imagegen using the prior atlas layout and supplied Firaxis style
references. Authored aligned H from selected seams with distance bevels and sparse
grain. Stronger structural N, calmer material faces, semantic G/M, new coals E.
Geometry/UVs unchanged: 1491 CN6 vertices, 781 triangles, one material. Reused v4 AO
byte-identically. Blender N is OpenGL, node strength 1.0. Game conversion/cook and
destination normal convention remain unvalidated on Windows.

Subsequent user confirmation: Henno reported that **1,491 vertices in Blender also
appeared as 1,491 in Asset Editor**. CN6 was already measured at 1,491. Count parity
is therefore confirmed for the blacksmith; the destination figure is user-reported.
He also supplied an in-game placement screenshot. This does not independently verify
the full normal/tangent convention, exact destination triangle count or all states.

Generator gained --height, --regions, --reference-size and --normal-y; broken AO
flags replaced with a geometry-bake explanation. Four focused Node tests passed.
Workflow/art findings promoted to `project/docs/textures-and-uvs.md`.

Read-back validation passed for all external paths, dimensions, color spaces and
unchanged CN6 sections. `texture-comparison-v4-v5.png` compares textured renders;
`relief-comparison.png` isolates normals off/on with a neutral material.
