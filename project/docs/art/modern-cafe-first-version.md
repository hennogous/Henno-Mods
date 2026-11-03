# Modern Café — Garden Café first version

29 October 2026. Henno selected **C — Garden Café**. This is a Blender review
candidate, not an installed Café asset or a published atlas release.

## Editable sources

Under `Desktop/Working Files/3D Art/`:

- `Level 3/modern/revision-01-garden/CSC_Level_3_Modern.blend` — reusable main
  building with three dormers, four upper front windows, arched shopfront,
  right shelter and underground foundation skirts.
- `BAKERS/Cafe/modern/revision-01-garden/CSC_BAKERS_Cafe_Modern_Review.blend`
  and `CSC_BAKERS_Cafe_Modern_2_Review.blend` — standard and coffee-van proposals.
- Same Café folder: independent `CSC_BAKERS_Cafe_Counter_Modern`,
  `CSC_BAKERS_Coffee_Van_Modern`, `CSC_BAKERS_Cafe_Parasol_Modern` and
  `CSC_BAKERS_Cafe_Valance_Modern` blend/CN6 masters.

The original L3 shell guides the silhouette directly. Its historical bounds,
including maximum height 112.949 and minimum foundation height -13.534, are
preserved. New surface painting replaces tiles with standing-seam metal and
adds green window/door frames, cream plaster and limestone trim. Registered
structural normals replace the obsolete dense historical window-grid relief.

Room furnishings are painted B/N/E artwork on four recessed five-face skins.
There are no modeled interior cups, shelves, machines, chairs or tables. The
serving counter also uses painted machine and pastry faces on simple silhouettes.

Historical garden furniture, flowers and curved walls are reference attachments
reconstructed from the saved AST and remain outside the new exports. Wooden
garden furniture is retained in this first version; the concept's green metal
chairs have not been authored. The van adds to the standard furniture layout,
with 3 units of depth clearance from the nearest front shrub. District road fit
still needs AE review. The counter sits under the original shelter; its striped
valance follows the measured outer eave near Z26.

## Dedicated modern interior atlases

Candidate library:
`Textures/CSC_Interiors_Modern/Candidates/2026-10-29_Garden_v001/`.

| Map | Size | Purpose |
|---|---:|---|
| `CSC_Interiors_Modern_B_BAKERS.png` | 1024² | Bright daytime room artwork |
| `CSC_Interiors_Modern_N.png` | 1024² | Registered broad relief |
| `CSC_Interiors_Modern_E_BAKERS.png` | 512² | Soft warm night lighting |

Same normalized 4×4 grid: UV1 samples B/N; UV3 samples matching positions in E.
Cells 0/1/2 hold Bakery rear/side/floor; 4/5/6 hold Café rear/side/floor. Ten
remaining cells are reserved. Fixed allocation on reusable geometry permits
quarter-specific B/E artwork later. Exterior upper windows retain the existing
quarter building E atlas; oven lighting retains props E. No Service logic changed.

Bakery migration candidates:

- `Level 2/modern/revision-07-interior-atlas-preview/`
- `BAKERS/Bakery/modern/revision-05-interior-atlas-preview/`

Only the three room objects' material and UV1/UV3 change. Geometry, UV2, other
UVs and placements are checked unchanged. Installed source blends and maps
remain untouched. Old room cells stay in live exterior atlases until installation
migrates all consumers together.

The L3 exterior uses the shared modern building atlas bottom-left quadrant,
retaining the historical L3 island layout inside it. New prop cells: 40 espresso,
41 pastries, 43 cup emblem, 44 dark green trim, 45 glass; 42 reserved. Existing
cells, including Henno's paint and oven emission, are preserved. Candidate AO
allocations do not overlap published silo CON+PIL or Bakery allocations.

## Verification and limits

Evidence: `Desktop/Codex/modern-cafe-v1-20261029/`.

- Saved-file validation for five Café masters and the migrated L2 base.
- CN6 → FGX → readback verifies topology, positions, normals, tangents,
  binormals, all three UV channels and static Bone weights for all six exports.
- Fresh independent AO, B-only/N-only interior diagnostics and standard/alternate
  day/night render demonstrations. Day views omit emission.
- Editable review files retain full foundations; only preview pixels use clipping.

No Café AST/ArtDef/XLP installation, cook, live AE or in-game validation is
claimed. Blender opacity and night lighting are native-shader approximations.
Per-model sources are authoritative; assembled reviews are placement proposals
and must not overwrite AE assembly edits.

Scripts: `project/tools/art/modern_cafe/`. Generated originals, UV guides and
structural relief masks are retained in the output package `sources/` directory.

## Separate authorized Bakery adjustment

Henno approved moving the alternate Bakery trolley clear of the deeper stand.
Only `CSC_Attach_Rack` X/Y in `CSC_BAKERS_Bakery_Modern_2.ast` changed:
(-16.919180, -6.597803) → (-17.310166, -7.137929), giving a 1-unit gap in the
aligned building frame. Other transforms and the standard assembly are unchanged.
Backup/receipt: `Desktop/Codex/modern-bakery-display-depth-20261029/trolley-clearance.json`.
