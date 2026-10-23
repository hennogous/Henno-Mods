# Water Mill flour fixed to building geometry

20 October 2026. Henno requested that building-side flour move with the Water
Mill's procedural riverside placement. Both Water Mill variants now reference
the same updated `CSC_BAKERS_Water_Mill` geometry; flour meshes are part of that
model instead of independent terrain-following attachments.

## Assembly and materials

- The standard mill's thirteen flour placements are baked at their saved AE
  positions, rotations and scales. This preserves the existing duplicate sack
  placement rather than redesigning the scene.
- Water_Mill_2 shares those placements and adds one building-side sack. Its mesh,
  `CSC_Fixed_Mill_Flour_Variant_2`, is hidden in the standard asset.
- Water_Mill_2 actually contains two native cart attachments. Both remain
  unchanged. Its two sacks on the quarry cart (`newAttachmentPoint_43` and
  `newAttachmentPoint_44`) also remain separate, preserving their existing
  relationship to the terrain-following cart.
- Wheel, organic patches, effects, CON+PIL geometry and all other attachment
  settings remain unchanged.
- The flour keeps its current `CSC_ALL_Props_01` material, native group name
  `CSC_ALL_Props_01_TextureReuseTrial`, all three UV channels, and existing
  state settings. It is visible in Worked, Unworked and Unbuilt, and hidden in
  Construction and Pillaged.
- The mill retains `CSC_BAKERS_E` in the standard variant and
  `CSC_BAKERS_E_2` in the alternate. Foundation/floor mappings remain
  `Foundation_Ancient_Cobblestone` and `DIS_CTY_RE_Ground`. All remaining
  original state/material records are preserved.

Both ASTs previously retained fifty obsolete state rows for ten flour meshes
that no longer existed in the native mill geometry. Those rows are removed.
The current attached flour meshes supply the replacement geometry and bindings;
the obsolete source flour is not reintroduced.

## Editable source and export

Updated master:
`C:\Users\Shadow\Desktop\Working Files\3D Art\Level 1\Bakers\CSC_BAKERS_Water_Mill.blend`.

This is one editable model with Export and Review scenes, three original mill
meshes and fourteen fixed flour meshes. Per-mesh native material group names
are retained. Portable texture previews are alongside it in `textures/`;
runtime materials and textures are unchanged.

The old master contained the retired flour layout. The updated master matches
the installed native mill geometry and the current AE flour placements.
Original source and runtime files are backed up in the evidence directory.
The shared source contains the variant-only sack; the ASTs own its visibility.

Tools:
`project/tools/art/water_mill_fixed_flour.py` and
`project/tools/art/water_mill_fixed_flour_blender.py`.
The native export preserves existing vertex ordering, triangulation, shading
vectors and UVs rather than retriangulating the building.

## Verification and limits

- Saved Blender master: zero authoring errors, with the advisory 2,200-vertex
  building target exceeded. The shared superset has 2,974 vertices and 3,267
  triangles; the standard intact model displays 2,834 vertices. These are
  existing flour instances consolidated into the model, not newly added props.
- All seventeen native meshes match planned positions, normals, tangents,
  binormals and UV1/2/3 within 0.0001 units, with exact triangle indices.
  The three original mill meshes preserve their native attributes.
- Both saved AST assemblies resolve in all five states. Their fixed flour
  visibility matches the original prop states.
- Before/after saved-asset previews were inspected with the carts, wheel and
  patches present. Flour placement is preserved. These are material-color,
  bind-pose checks; they do not simulate procedural riverside placement.
- The normal SDK build succeeded with zero reported build warnings/errors.
  Windows and MacOS tilebase packages rebuilt at 20:44 and contain both variant
  entries. Runtime files, the installed editable source and its portable
  textures match staging; the native model placement and root bone are unchanged.
  Cooker diagnostics still identify two degenerate triangles in the unchanged
  CON+PIL shell; that pre-existing geometry was outside this flour change.
- In-game terrain behavior remains to be reviewed after rebuilding.

Evidence, backups, native/source/state checks and previews:
`C:\Users\Shadow\Desktop\Codex\CSC_Water_Mill\fixed-flour-20261020`.
