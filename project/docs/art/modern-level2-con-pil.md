# Modern Level 2 construction and pillage states

29 October 2026. The modern L2 main building now has its own reusable state
geometry, replacing the historical placeholder in `CSC_Level_2_Modern`,
`CSC_BAKERS_Bakery_Modern` and `CSC_BAKERS_Bakery_Modern_2`.

## Editable source

`C:\Users\Shadow\Desktop\Working Files\3D Art\Level 2\modern\CON+PIL\revision-01\CSC_Level_2_Modern_CON+PIL.blend`

The adjacent CN6 and validation/wood-UV reports accompany the master. Start from
this saved file for subsequent edits; the producer is the initial authoring recipe.
The source is already in the historical district frame, like the revision-06-ae
worked modern master. Do not register it a second time.

The shell follows the worked main footprint, door/window opening positions and
30-unit underground foundations. Lower masonry sheets were rebuilt with closed
inward thickness because the worked interior cut-outs had T junctions. The upper
walls are incomplete, with an open roof frame. There is no extension, shelter,
floor, interior room box, sign or stock prop in this state geometry.

## Materials and state behavior

- The shell appears in Construction and Pillaged. Pillaged binds
  `DefaultBurnMaterial`. The native timber scaffold appears only in Construction.
- The completed main building, extension, prop attachments and placements are
  unchanged. Existing pillage decal rows are preserved; no new prop debris is
  authored. Historical geometry and historical assets are unchanged.
- The two meshes contain 1,462 exported shell vertices and 588 scaffold vertices:
  2,050 total. Triangle counts are 908 and 272 respectively.
- The scaffold reuses the historical L2 native surface/UVs with uniform scale and
  main-wall placement. The bounded Firaxis modern-scaffold survey is recorded in
  [the modern L1 state report](modern-level1-con-pil.md#firaxis-scaffolding-check).
- Main masonry uses existing modern L2 cells 0 and 1. Texture sampling matches
  the worked model: 3.875 pixels/unit horizontally, 4.127 vertically for upper
  brick, 3.875 vertically for stone. UV boundary cuts do not change the silhouette.
- Exposed structural wood uses L2 cell 9 with U along each member, including
  rotated rafters. The saved timber audit verifies long-face grain alignment.
  Existing painted base colour and aligned normal artwork are reused unchanged.
- UV3 remains dark. No state emissive or Service lighting variant is added.

## AO and release

Buildings atlas **2026-10-29_Modern_r015** adds one independent 512-square AO cell
at `[1024,512,1536,1024]` in the 2048-square shared AO atlas. Every pixel outside
that rectangle is preserved, including all worked building AO. B/N/G/M/E/O maps
are unchanged; the approved active roof colours from r014 remain current.

Closed wall winding and positive signed volume were checked before baking.
Scaffolds and finished-model geometry were excluded, Normal was disconnected,
and UV2 was explicitly selected for the 128-sample bake. Native AO-only renders
were checked from both sides. The immutable release includes the previous AO,
baked patch and reproduction script. R8 DDS headers were normalized to the
known-good Firaxis convention before installation.

## Verification and limits

Saved-file validation has no errors or warnings. Native FGX readback verifies all
positions, normals, tangents, UVs, topology and single-Bone weights. All five states
resolve in all three consuming assets; the extension is hidden in CON/PIL.
Non-state model rows and attachment/placement behavior remain semantically exact.
The isolated SDK cook succeeds with no cooker errors; its usual advisory vertex
ratio and mostly-solid texture messages remain. AE dependency cache is updated.

Evidence: `C:\Users\Shadow\Desktop\Codex\modern-l2-states-20261029`.
Producer scripts: `project/tools/art/modern_level2_states/`.
`Modern_L2_Worked_CON_PIL.png` uses the fixed L2 icon camera on dark. The Pillaged
panel displays the shell; Blender does not reproduce native burn overlays,
particles or projected debris. No live AE viewport or in-game test is claimed,
and this work does not deploy to the game.
