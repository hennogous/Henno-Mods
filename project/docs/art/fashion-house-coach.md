# Fashion House coach

Delivered 13 October 2026 as standalone `CSC_TAILORS_Fashion_Coach` for Henno's
Fashion House alternate assembly. AE owns final placement, rotation and scale.
No existing building assembly was rewritten or given an automatic placement.

## Current source and geometry

- Editable master: `C:/Users/Shadow/Desktop/Working Files/3D Art/Props/Tailors/Fashion Coach/revision-02/CSC_TAILORS_Fashion_Coach.blend`.
- Reference: `Props/Tailors/_sources/fashion_coach.png` under Working Files/3D Art.
- 937 actual CN6/FGX vertices; 771 triangles; one `CSC_ALL_Props_01` material group.
- Editable source: 746 positions in 94 named components, with Review and Export scenes.
- Ground-centred support pivot `(0,0,0)`; shafts/front point along `+X`.
- Worked/Unworked visible; Construction/Pillaged/Unbuilt hidden; PERMANENT culling.
- AST, GEO, FGX, Tilebases XLP entry and AssetCloud dependency records installed.
- Revision 01 remains available as history; revision 02 is the current source.

The defining forms are the burgundy cabin, cambered leather roof, spoked wheels,
open door, interior cloth display, lanterns, driver's seat, shafts and supported
entry step. Fine ornament is painted. At Henno's request, revision 02 removes
the thin seat rails, door-frame rods and roof-edge strips: 52 fewer exported
vertices. Keep this division for future props even when the budget has spare room.

## Shared atlas

Current release: `2026-10-13_Shared_01_r023`, in the canonical
`Working Files/3D Art/Textures/CSC_Props` library. Permanent runtime filenames
and material bindings are retained.

Four surface patches were introduced in r022: claret coach panel (slot 5), black
leather (6), curtained coach window (7), and antique brass (50). Previous occupied
surface rectangles remain unchanged. R023 changes only the coach AO relative to
r022 after the geometry simplification.

Coach self-AO occupies `[1280,896,1536,1024]` on Shared 01, inside the existing
Tailors Stage 4 reservation. Cycles 128-sample isolated self-AO was baked at
1024×512 and reduced to the 256×128 cell. No ground/building shadow is baked in.
Other shared AO pixels are preserved.

Henno's pre-existing live AO edits were reconciled into five registered source
cells before r022: Textile Bale, Folded Cloth Teal, Cloth Roll Canvas, Rope Coil
and Sail Drying Rack. Previous source cells were retained as BeforeHenno copies;
deterministic page rebuilding reproduces the edited production pixels.

The four new painted patches use built-in ImageGen. Its complete source image,
exact prompt and processing notes are retained under the release's
`atlas/sources/coach-paint-source.png` and `coach-paint-provenance.json`.
Normal patches are flat; gloss/metalness are semantic constant patches. Existing
cloth, timber and embroidery patches are reused. Geometry supplies the larger
relief. Portable source blends keep exact relative texture snapshots.

## Verification and remaining review

The final saved-file authoring validator passes. Native FGX readback preserves
all 937 vertices and 771 triangles; maximum position/UV/normal attribute residual
is below 0.000005. DDS formats, mip counts and scalar-map pixels were checked;
R8 files use the established Firaxis-compatible headers. Release/Current and
installed geometry hashes match. AE subsequently re-imported all five updated
DDS maps, rewriting headers and lower mip levels. Every full-resolution pixel
remains identical to the verified staged output, and the live formats, mip counts
and canonical TEX paths pass validation. All 127 pre-existing ASTs were
preserved during installation.

Front/rear/side/top, clay and mapped-AO views were inspected. These are Blender
reviews, not calibrated game-camera or native rendering parity. AE appearance,
package cooking and in-game review remain unverified. An already-open AE may
retain its previous mapped DDS data until the asset/material is reloaded.

Review images, CN6, native readback, validation reports, raw bake and publication
backups: `C:/Users/Shadow/Desktop/Codex/Fashion-coach-20261013/`.

Production scripts live in `project/tools/art/`: `fashion_coach_atlas.py`,
`build_fashion_coach.py`, `finish_fashion_coach.py`, and
`publish_fashion_coach.py`. They capture this task's staged workflow and paths;
do not rerun the generator over a later Henno-edited master. Preserve immutable
release snapshots and check the live atlas before any subsequent publication.
