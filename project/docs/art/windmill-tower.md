# Windmill tower and storage atlas migration

## Current revision — wooden tower, 22 October 2026

Shared-library **r042** gives the sails weathered canvas: ImageGen sun fading,
soft edge grime, stitched panel seams and a subtle repair. Dedicated slot 39
(`900,516,1020,636` inner pixel bounds) preserves the existing shared ivory swatch.
Registered B/N/G/M sources and the original generated image are retained in the
canonical library. Fine normal relief derives from high-pass fabric detail;
broad discoloration remains albedo, with matte gloss and zero metalness.
Only the cloth's UV1 islands translate to the new slot. Native readback confirms
unchanged geometry, skeleton, weights, UV2/UV3 and 1,512 native vertices. Both
variants cook as RigidModel/24-byte; saved-source validation has zero errors or
warnings. AO, the eight-second clip, CON+PIL and AE placements are unchanged.
The saved-assembly preview was inspected; live AE/game appearance remains untested.
Evidence: `C:\Users\Shadow\Desktop\Codex\windmill-weathered-sails-20261022`.

The active identity is now `CSC_BAKERS_Wind_Mill_Tower`, including the CON+PIL
geometry and `CSC_BAKERS_Wind_Mill_Tower_Turn` animation. Editable sources live in
`Working Files/3D Art/BAKERS/Wind Mill/tower/`. The full turn takes **8 seconds**:
frames 1–241 at 30 fps, with linear rotation. Model datablocks, native skeleton
identities, parent references, XLP/project registration, source paths, shared-atlas
records, tools, documentation and AE cache references use the new name. The older
unused asset with that name was backed up and replaced; its duplicate XLP entry
was consolidated. Historical output/backup snapshots remain unchanged.

Shared-library r041 is a metadata/filename migration with identical texture pixels.
Native geometry and skeleton data compare exactly after name substitution.
All 241 native clip samples, both source validators and the isolated cook pass;
ANM and native clip duration are both 8 seconds. Evidence and backups:
`C:\Users\Shadow\Desktop\Codex\windmill-rename-8s-20261022`.

The preceding release was `2026-10-22_Shared_01_r040`. Henno's newer intact and CON+PIL
sources remove the window and revise the UVs. Those tower positions, topology and
UV1/UV3 are preserved exactly, including edits saved in Edit Mode. Both towers
receive fresh AO in their existing district-atlas cells. Their now-unused props
material slots are removed: the empty second slot caused the reported CivNexus
`createMaterials` index-1 exception. Both native conversions now complete.

Sail rung ends terminate inside the rails and the raised tie blocks are removed.
Their detail is transferred by a selected-to-active normal bake, with B/G/M baked
from the existing ImageGen-textured geometry, into previously free shared-props
slot 38 (`[772,516,892,636]` inner bounds). Only the rail long-face UV1 corners
change to use this patch; retained nonrail UV1 and all retained UV3 remain intact.
The cloth, hub and rail positions, taper, width and animation remain unchanged.
Native sail counts fall from 1,554 vertices / 816 triangles to 978 / 528. Complete
native counts are now 1,512 intact and 1,034 CON+PIL, both cooked RigidModel/24-byte.
Sail AO is rebaked; the two obsolete window/axle props-AO cells are cleared and
returned to free space. Other atlas cells and parent assembly edits are preserved.
Both masters and CN6/FGX/GEO files are installed, with canonical r040 textures.
Saved-assembly Worked/Construction/Pillaged previews, source preservation checks,
301 animation frames, clearance and isolated both-variant cook pass. Live AE/game
review remains pending. Evidence: `C:\Users\Shadow\Desktop\Codex\windmill-simplify-20261022`.

The subsequent sail cleanup publishes shared AO release `2026-10-22_Shared_01_r039`.
The thin billowed cloth's front and back quads had opposite triangle diagonals,
causing the surfaces to cross and bake black rectangular marks. Both surfaces now
use corresponding explicit triangles. Vertex positions, UV1/UV3, cloth artwork,
animation and native geometry counts are preserved. Only the sail AO cell
`[0,128,512,512]` was rebaked; its sampled front interiors now contain zero dark
pixels, down from 480. Natural frame contact shading remains on the backs.
The editable intact master, CN6, FGX and shared props AO DDS are updated; both
parent windmill assemblies reuse this asset. Native bindings and cooked formats,
301 animation frames, rotor clearance and saved-assembly preview pass. Live
AE/game review remains unverified. Evidence and backups:
`C:\Users\Shadow\Desktop\Codex\windmill-sail-cleanup-20261022`.

The later angular correction uses six broad planar faces, matching the timber
concept's framed-wall construction. Each face receives one complete painted
brace; the brace no longer crosses several curved facets. The base, cap, roof
and CON+PIL shell follow the same hexagonal section. An export-only hard-edge
split prevents the legacy CN6 exporter from averaging the corner normals.
Native readback verifies the wall normals match their physical planes.
Source positions remain editable; the actual native counts are 2,202 intact
and 1,154 CON+PIL (the intact result is two vertices over the 2,200 advisory).
AO is refreshed in the existing cells as `2026-10-22_Shared_01_r038`.
The enlarged sails, skeleton, animation, both scaffold meshes, shared colour/PBR
artwork, XCFs and parent placements are unchanged by this shape correction.
Evidence: `C:\Users\Shadow\Desktop\Codex\windmill-angular-20261022`.
The following paragraphs describe the preceding wood/material revision.

The current tower uses warm ImageGen timber boards and a painted diagonal brace,
with an aligned, strong normal derived from the generated height map. The brace
adds no geometry. It replaces the plaster in the same 128×128 swatch, inside
`[512,614,644,746]` including padding. The four existing Bakers/Tailors B1/B2 XCFs
replace their plaster layer; shared B/N/G/M maps replace only that slot. Historical
asset names and source paths retain `Plaster_Tower` to preserve references.

Both tower meshes are 15% wider in their authored horizontal coordinates and
shifted three source units toward the shelter; the axle and rig stay fixed. Local
ground remains Z=0 and the foundation continues to Z=-30. Sails are 50% wider
than the previous revision, retaining the gentle taper. Cloth starts at radius
14.2 instead of 29.8, covering two additional rungs; the outer radius stays 47.8.
Existing per-corner UV1/UV3 edits are preserved. AO is rebaked into the same shared
quarter and props cells, published as `2026-10-22_Shared_01_r037`.

Rear scaffold sections are removed. The front scaffold from the shared Level 1
geometry is embedded in the windmill CON+PIL at its exact saved assembly position;
only the shared `Scaffolding` group's visibility is disabled in the two windmill
ASTs. This avoids altering other buildings using that geometry. Both remaining
front scaffolds appear only during Construction. Parent placements are unchanged.

Evidence and backups: `C:\Users\Shadow\Desktop\Codex\windmill-wood-20261022`.
Both masters validate with zero errors/warnings. Saved native meshes have one
intended binding each (`Root` or `Sails`), matching GEO counts, and both cooked
tower geometries use `RigidModel` (24-byte cooked stride): 2,154 intact and 1,118
CON+PIL vertices. The isolated cook of both assemblies succeeds; 301 animation
frames match, and 61 full-rotation clearance samples report no intersections.
The saved assembly's Worked, Construction and Pillaged previews were reviewed.
Live AE and in-game acceptance remain untested. No game build was deployed.

The sections below document the original delivery and subsequent revisions.

Delivered 21 October 2026. The approved plaster tower with four timber ladder
sails replaces the previous tower attachment in both `CSC_BAKERS_Wind_Mill`
and `CSC_BAKERS_Wind_Mill_2`. Every other saved assembly value is preserved.

## Asset and editable source

- Asset/model: `CSC_BAKERS_Wind_Mill_Tower`.
- Animation: `CSC_BAKERS_Wind_Mill_Tower_Turn`; ten seconds, 301 sampled
  frames at 30 FPS, bound to `Standard_Landmark / WORKED_A`.
- Rig: model root, stationary `Root`, rotating `Sails`.
- Source: `C:\Users\Shadow\Desktop\Working Files\3D Art\BAKERS\Wind Mill\tower\CSC_BAKERS_Wind_Mill_Tower.blend`.
- The source folder also contains CN6, animation FBX, historical private AO,
  original ImageGen plaster, packed B/N/G/M plaster patches and provenance.
- Current tower surfaces use `CSC_BAKERS_E`, matching the paired Level 1 building;
  sails and small timber pieces use `CSC_ALL_Props_01`. Active AO is shared.
- Worked/Unworked show the intact tower; Construction/Pillaged show its shell.
  The scaffold mesh copied from Henno's Level 1 CON+PIL master appears only in
  Construction. Unbuilt hides both models. See the revision sections below.
- Ground is local Z=0, with foundation to Z=-30. The ground-datum revision
  compensated both parent attachment heights; later UV/material changes preserve
  all parent AST bytes. The old tower asset remains available separately.

The current intact model has 2,154 exported vertices including UV splits: 600 in
the stationary mesh and 1,554 in the rotor. The CON+PIL model has 480 shell plus
588 scaffold vertices. The standard assembly's 928 existing main-building
vertices bring intact main/bespoke geometry to 3,082 against the advisory 2,200
target. The separate tower asset does not exempt it from the assembly budget.

## Storage quadrant

The bottom-right 512-by-512 quadrant of the 1,024 atlas now uses the
`storage-tower-v3` layout. Thirty occupied UV regions retain their exact painted
pixels, orientation and texel density. The new plaster receives a 128-by-128
region with two pixels of edge padding. Retained regions plus plaster occupy
182,900 of 262,144 pixels, leaving 79,244 pixels free.

`Textures/Storage_Tower_v3_layout.json` in Working Files records every original
rectangle, destination and UV translation. Do not apply these translations a
second time to the migrated sources.

Updated canonical colour sources:

- `CSC_Atlas_B_BAKERS.xcf` and `CSC_Atlas_B_BAKERS_2.xcf`;
- `CSC_Atlas_B_TAILORS.xcf` and `CSC_Atlas_B_TAILORS_2.xcf`;
- their matching DDS files.

Each XCF has a new storage group with 32 editable layers: a background, thirty
retained swatches and the ImageGen plaster. Previous storage layers and paths are
retained under `Legacy v2`. Current roof-tile and roof-beam paths are translated
and clipped into the new layout. Quarter-specific colours are preserved.

Shared `CSC_Atlas_N`, `CSC_Atlas_G`, `CSC_Atlas_M` and `CSC_Atlas_O` are migrated
with the same rectangles. Existing storage normal XY components are multiplied
by 1.65 and renormalized, strengthening tile joints, timber edges and masonry.
The plaster gets quieter relief derived from its ImageGen paint after removing
broad colour shading; its gloss is 28/255 and metalness is zero. New surface
colour was generated with ImageGen, not procedural painting.

All runtime pixels outside this quadrant are unchanged. Scalar DDS conversion
explicitly takes the red channel; automatic RGB luminance conversion would
otherwise alter a few previously authored gloss texels. Runtime R8 headers use
the proven Firaxis-compatible format; canonical source DDSs retain conventional
scalar encoding for authoring applications.

## Geometry migration

Nine existing native FGX files received UV1-only changes:

| Geometry | Purpose |
|---|---|
| `CSC_Storage_L`, `CSC_Storage_L_CON+PIL` | Large storage and state geometry |
| `CSC_Storage_M`, `CSC_Storage_M_CON+PIL` | Medium storage and state geometry |
| `CSC_Storage_S`, `CSC_Storage_S_CON+PIL` | Small storage and state geometry |
| `CSC_TAILORS_Tailor_LeanTo` | Current Tailors lean-to |
| `CSC_TAILORS_Tailor_CON+PIL` | Lean-to state geometry within the Tailor |
| `CSC_ALL_Delivery_Pivot` | Fixed crane parts sharing these swatches |

The native patch preserves every other vertex-buffer byte. Readback also proves
unchanged triangles, bone bindings, skeletons and model placements. UV2/AO and
UV3/emission are untouched in these existing geometries.

Twelve editable Blender masters are updated: the six current storage masters,
generic intact lean-to, current Tailors lean-to, both current Tailor CON+PIL
copies, the large-storage crane and its delivery source. Eight adjacent existing
CN6 files are re-exported. Archived layouts and the old standalone S construction
source remain on their own older textures and are excluded.

## Materials and AO

The plaster, roof and foundation use the shared quarter B/N/G/M/O maps through
`CSC_BAKERS_Wind_Mill_Plaster`. Timber, cloth, iron and ties reuse existing shared
prop swatches through `CSC_BAKERS_Wind_Mill_Sails`. No shared prop atlas pixels
were changed.

Both materials use the new 512-pixel `CSC_BAKERS_Wind_Mill_Tower_AO`.
This is a geometry bake for the new asset; it avoids disturbing the occupied
quarter AO atlas. Tower and rotor are baked separately so rotating sails do not
leave a fixed shadow on the plaster. Cloth has actual thickness rather than
coincident front/back faces.

## Verification and remaining review

- Final installed editable tower passes the saved-file authoring validator with
  zero errors or warnings. Export/Review scenes and canonical texture paths exist.
- All twelve migrated sources preserve geometry, weights, transforms, materials,
  UV2 and UV3; only the planned UV1 coordinates move.
- Native conversion preserves all three UV maps and rigid bone weights.
- All 301 native animation frames were compared against authored motion. Maximum
  vertex error is 0.03152 model units (0.0285% of the model span); loop seam error
  is 0.00462 model units. The stationary root has zero motion.
- Sail/body/assembly intersection checks at 61 poses find no collisions outside
  the intentional axle/hub contact area.
- Both assembly replacements are exact old-to-new asset-name substitutions;
  154 unrelated AST files are byte-identical to the publication baseline.
- All four installed XCFs reopen. The storage composite matches the runtime
  paint exactly; export rounding outside the edited quadrant is at most 1/255.
- XLP, ModBuddy content entries and focused AssetCloud dependencies include the
  new asset, two materials, model, AO and animation.
- The source-texture watcher regenerated one Bakers DDS header/mip payload after
  publication; its full-resolution pixels still match staging exactly.

Appearance and motion previews reconstruct the saved native assembly in Blender.
Live AE playback, a fresh cook and in-game terrain/appearance acceptance have not
been performed. No build/deployment or game session was disturbed.

Evidence, before-files and the full rollback manifest:
`C:\Users\Shadow\Desktop\Codex\windmill-tower-20261021`.
The main previews are `Windmill-Tower.png` and
`Windmill-Native-Motion.gif`; `publication-backup/manifest.json` maps each changed
file to its exact prior bytes. This folder is a historical delivery record, not
a new source-of-truth location for editable art.

Task tools live in `project/tools/art/windmill_tower_*.py`,
`publish_windmill_tower.py`, `register_windmill_tower.py`, `PatchAtlasUV.cs`, and
the matching windmill/migration scripts in `project/tools/blender/`. Their
staging and migration commands expect the original audit inputs; do not rerun
the publication or UV translation against the already migrated production tree.

## Wider sail revision — 21 October 2026

Henno requested broader sails to match the concept. The four ladder frames and
cloth panels are now 35% wider: rung span increases from 10.5 to 14.175 model
units, and cloth span from 8.6 to 11.61. Rail and tie thickness, sail length,
hub, stationary tower, UVs, rig and ten-second animation remain unchanged.
Only the rotor AO was rebaked, with the stationary tower's AO texels protected.

The editable master, adjacent CN6, source AO PNG, runtime FGX and runtime AO DDS
were replaced. Parent ASTs, shared atlases, animation and GEO retain their exact
previous bytes. Native readback confirms the stationary mesh/rig and the rotor's
UV and weight attributes are unchanged. All 301 motion frames pass validation;
61 sampled poses show no sail collisions. The source validator reports zero
errors and warnings. Live AE/cook/game review remains pending.

Revision preview, validation and five-file rollback copies are in
`Desktop/Codex/windmill-tower-20261021/wide-sails`; the still is
`Windmill-Wider-Sails.png`. `widen_windmill_sails.py` is a guarded one-time
revision tool; `build_windmill_tower.py` now incorporates the same widths.

## Taper and geometry-loading repair — 21 October 2026

The current sails retain the 11.61-unit cloth-tip width and narrow gently toward
the hub. Rail spacing at radius 5.5 is 60% of its outer spacing; the sides flare
linearly to radius 47.8. Beam cross sections, hub, tower surfaces, UVs and clip
are preserved. Rotor AO was rebaked within its existing layout, preserving the
stationary tower's AO allocation. The installed Blender master, CN6, FGX and AO
source/runtime files carry this revision.

AE's 11:48 session reported `InstanceSet::LoadByName failed to deserialize from
file`, followed by the missing `CSC_BAKERS_Wind_Mill_Tower` geometry
dialog. Its GEO root was `AssetObjects.GeometryInstance`, with one dot. The
renderer normalizes a legacy unbound colon into that spelling for XML parsing;
the one-off integration writer had incorrectly serialized the normalized tag.
The native registered type is `AssetObjects..GeometryInstance`. Both parent
windmills share this wrapper. It is now corrected, and the writer normalizes
native type names before saving. A regression test covers this legacy input.

The rotor also retained an unused plaster material slot: native topology group
0 was empty and sail faces used group 1, while the GEO described one group.
The unused slot is removed, leaving native group 0 and the one sail descriptor
in agreement. Exact native comparisons prove that cleanup changed neither
vertices nor triangle vertex indices, UVs, normals, rig or weights. The builder
now omits the unused slot, and export validation rejects empty native groups.
GEO group names are taken from CN6 material lists; Granny readback does not
always provide material-binding names. Final counts remain 428 tower + 1554
sail vertices, 1982 total.

Evidence is under `Desktop/Codex/windmill-tower-20261021/taper-and-ae-repair`:

- Original malformed-wrapper controls crash the native cooker with access
  violation `0xC0000005`. The corrected wrapper loads successfully.
- A focused isolated XLP contains the tower and **both complete windmill
  assemblies**, including construction/pillage geometry and materials. Four
  final cleaned-model cooks complete without entity errors or error-asset
  substitution. No mod build, deployment or live game was changed.
- Early repaired-wrapper cooks had intermittent post-load failures. The three
  later old-group controls also passed, so removing the empty group is a verified
  consistency repair, **not a proven explanation of those intermittent failures**.
  A diagnostic launch under ProcDump exited successfully and produced no dump.
- Warnings include two pre-existing degenerate triangles in the shared
  `CSC_Level_1_S_CON+PIL_Bldg`, high split-vertex ratios and near-solid scalar
  atlases. Those unrelated sources are preserved.
- Final saved-source validator: zero errors/warnings. All 301 animation frames
  and 61 clearance samples pass. The material cleanup preserves the tested
  geometry exactly. Two export regression tests pass.
- All parent ASTs, material files, shared atlases and animation bytes are
  preserved. AE's watcher regenerated the tower AO DDS; its red pixels and
  Firaxis-compatible scalar header were verified, and that regenerated file
  was retained. Focused AssetCloud entries were refreshed.

`publication-report.json` records six installed files and rollback copies;
`before-group-cleanup` retains the intermediate exports. The still is
`Windmill-Tapered-Sails.png`. Restart AE before retrying the two windmill assets:
fresh-session AE loading/playback and in-game acceptance remain unverified.

## Ground datum and CON+PIL revision — 21 October 2026

The tower now uses local **Z=0 as ground level**, with a closed stone foundation
continuing to **Z=-30** in three courses. Its former ground was Z=27.2. All intact
above-ground geometry and the rotor pivot move down by 27.2; a newly exported
ten-second clip uses the rebased pivot. The wider, gently tapered sails remain.
Both parent windmills compensate with attachment `newAttachmentPoint_11` Z
changing from -3.128043 to -0.136043. AE positions are in ten-unit increments:
the correction is `27.2 * 1.1 / 10 = 2.992`. Every other byte in those two parent
ASTs is preserved, retaining the existing above-ground assembly placement.

`CSC_BAKERS_Wind_Mill_Tower_CON+PIL` is a second geometry model inside
the existing tower asset. It shares the ground datum and buried foundation,
with a roofless plaster shell, thick irregular masonry rim and inner wall/floor.
It retains the window but has no roof, axle or rotor. The intact model appears
in Worked/Unworked; the shell appears in Construction/Pillaged. Pillaged uses
the normal `DefaultBurnMaterial` binding. `PROP_Scaffold_A` remains an unchanged
native TileBase attachment from `landmarks/tilebases`, uniformly scaled 1.45 and
bound to the static synthetic tower model bone. Its own native visibility states
make it visible only in Construction. The scaffold is not merged into either
custom mesh.

Both editable masters and CN6s are in the existing Working Files
`3D Art/BAKERS/Wind Mill/tower` directory. Each geometry has a fresh
512px AO bake and UV2 layout; the ruin's two material siblings point at its own
AO. Painted shared atlases, G/M/N textures and XCFs are unchanged by this
geometry revision. Native counts are 2,154 vertices for the intact tower/rotor
and 480 for the shell. New files are registered in the ModBuddy project; focused
AssetCloud records were refreshed.

Evidence and rollback copies: `Desktop/Codex/windmill-tower-20261021/ground-and-states`.
`publication-report.json` lists the 22 installed files. Both installed masters
pass source validation with zero errors/warnings; 301 native animation frames
pass comparison and 61 rotor poses have no blade collisions outside the hub.
The isolated native cook of the tower and both complete windmill assemblies
passes without entity errors or error-asset substitution. Existing shared-base
degenerate-triangle and split-vertex/near-solid-texture advisories remain.
AE's texture watcher updated the intact AO TEX export timestamp and regenerated
compatible AO DDS data; semantic settings and top-mip red pixels were verified.

`Windmill-Worked.png`, `Windmill-Construction.png` and `Windmill-Pillaged.png`
are terrain-clipped Blender review renders reconstructed from saved ASTs.
The underlying exports retain the complete foundations. Pillaged previews show
the shell geometry; they do not simulate the game's burn shader. Live AE
loading/playback and in-game terrain/state behavior still require review.

Revision tools: `build_windmill_ground_states.py` (guarded pre-rebase source
input), `integrate_windmill_ground_states.py`,
`readback_windmill_ground_animation.py` and `review_windmill_ground_states.py`.
Do not rerun the one-time authoring/publication steps on already rebased masters.

## Shared materials, AO and supplied scaffold — 21 October 2026

This revision starts from Henno's saved UV-edited masters (12:38 intact and
12:47 CON+PIL), not from the earlier procedural builder. The installed files
preserve vertex positions, face membership, weights, transforms and per-corner
UV1/UV3 texture assignments. UV2 changes implement the shared AO allocations.

The first isolated bake exposed inward-facing sail solids: 404 of 436 polygon
normals were reversed. Recalculating closed-component normals outward fixes
the solid-black beam AO, without changing geometry shape or surface texture
placement. The fresh bake uses 128 Cycles samples, 16 AO rays and twice final
resolution, with 2px dilation. It captures rotor self-occlusion, without baking a
stationary tower/ground shadow into the rotating sails. Animation is unchanged.

Allocations below use top-left pixel coordinates, with exclusive right/bottom:

| Geometry | Shared AO map | Rectangle |
|---|---|---|
| Intact tower masonry | `CSC_Atlas_AO2` (1024²) | `[516,976,580,1020]` |
| CON+PIL masonry | `CSC_Atlas_AO2` | `[584,976,648,1020]` |
| Sails | `CSC_Props_Shared_01_AO` (2048²) | `[0,128,512,512]` |
| Intact small timber | `CSC_Props_Shared_01_AO` | `[384,0,448,128]` |
| CON+PIL small timber | `CSC_Props_Shared_01_AO` | `[448,0,512,128]` |

Both tower cells are in the district map's bottom-right quadrant. The prop cells
are in the top-left Bakers/Stage2 reservation. Native AO2 consumers were
rasterized with a 3px protection border before allocating; Granny V is already
top-origin and must not be flipped again for image-space occupancy. All pixels
outside the new cells, in both source PNGs and runtime DDS top mips, are preserved.
Building cells provide compact low-frequency AO; painted relief stays in the
unchanged normal map. The prop cells, raw supersampled bakes, manifest and
deterministic cell packer are published in `CSC_Props` release
`2026-10-21_Shared_01_r036`, its `Current` tree and `CURRENT.json`.

The earlier `PROP_Scaffold_A` attachment is removed. The exact `Scaffolding`
mesh from `Working Files/3D Art/Level 1/CSC_Level_1_S_CON+PIL.blend` is now a
separate mesh inside the tower's CON+PIL geometry. It retains all source topology,
three UV channels and `Pillage_Construction_01` binding. Its geometry is uniformly
scaled 0.70 and placed around the tower, then weighted to static `Root`.
The original Level 1 file is unchanged. Its group is visible only in Construction.

Evidence/backups: `Desktop/Codex/windmill-tower-20261021/shared-materials`.
The 12-file publication manifest and shared-library backup cover the installed
revision. Source comparison verifies every preserved surface UV assignment and
the exact scaffold transform. Both installed masters have zero validator
errors/warnings; 23 validator regressions pass, 301 animation frames and 61 blade
clearance samples pass. The native cook accepts both complete parent assemblies
without entity errors/error substitution. Release/staged/Current hashes match;
both parent ASTs and the animation FGX remain byte-identical. AE's watcher may
refresh scalar DDS metadata; compatible headers and identical AO pixels are
accepted and recorded. Live AE playback and in-game review remain unverified.

Tools: `revise_windmill_shared_materials.py`, `audit_windmill_shared_ao.py`,
`integrate_windmill_shared_materials.py`, `verify_windmill_shared_sources.py`.
The authoring tool is a one-time migration using the recorded user-input hashes.
Reload the saved masters in Blender to see their new UV2 and material bindings.
