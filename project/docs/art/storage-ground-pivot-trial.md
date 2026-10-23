# Storage ground-pivot trial — 20 October 2026

## Installed scope

`CSC_BAKERS_Storage_L` now uses centered, unrotated storage geometry. Its final
district placement is held by the attachment in `CSC_BAKERS_Classical_Base_03`.
The delivery is a sibling attachment, `CSC_BAKERS_Storage_Delivery`, with the
same ground pivot. Its native model and clip are named `CSC_ALL_Delivery_Pivot`.
The original shared `CSC_ALL_Delivery` remains available for other assemblies.

This is a Base 03 trial, not a completed migration of the storage family.
Henno explicitly authorized changing the shared storage masters directly.
Other bases and storage variants that use these masters still need their
placements and props migrated. Water Mill attachments are not changed.

The four supplied Blender sources under `Working Files/3D Art/Storage/Storage_L`
have been updated in place:

- `CSC_Storage_L.blend`
- `CSC_Storage_L_CON+PIL.blend`
- `CSC_Storage_L_PIL_Decals.blend`
- `Delivery/CSC_TAILORS_Storage_Delivery.blend`

The editable delivery source retains its rig, controls and animation under
`CSC_Storage_Pivot_Frame`; the native export bakes that frame. The decal source
exports the five-plane layout actually used by the installed asset. Its
unpublished alternate layout is retained in `Alternate_Decal_Layout`.

## Coordinate contract

The pivot lies at ground Z = 0, centered in the foundation footprint after
removing the building's yaw. A downward ray from this XY position hits the
roof, establishing that the pivot is inside the building.

| Transform | X | Y | Z |
|---|---:|---:|---:|
| AE attachment position | -3.139355278 | 16.799298096 | 0 |
| AST attachment rotation, radians | 0 | 0 | -0.386454552 |
| AE displayed rotation, degrees | 0 | 0 | -22.142214825 |
| Attachment scale | 1 | 1 | 1 |

Blender coordinates are ten times the attachment position values. The AST
renderer uses negative Z rotation relative to Blender. The removed Blender
transform is translation `(-31.393552780, 167.992980957, 0)` and yaw
`+22.142214825°`.

Call that transform **T**. New storage mesh coordinates and static attachment
matrices are **T⁻¹ × old**; the district attachment is **T**. Therefore the
district-space placement is preserved. All 26 static/FX attachment points were
converted using full matrices, including props with X/Y tilt.

The delivery also uses **T⁻¹** for geometry and animated bone world poses.
Its district attachment uses **T** and Pivot Height, matching the storage.
The moving flour sack remains attached to `Cargo_TipUpright` inside the delivery
asset. Route, handoff and loop timing remain authored in the same district
positions. The storage no longer owns the delivery model or its animation binding.

The static FGX files retain their original vertex ordering, triangulation,
UVs, materials and bone bindings. Rebase conversion operates on decoded native
attributes because re-triangulating rotated source n-gons changed 19 diagonals.

## Validation and remaining checkpoint

- Native geometry comparison passes for intact, CON+PIL and pillage decals:
  restored positions differ by less than 0.000007 Blender units; UVs and topology
  are unchanged.
- All 26 static attachment world matrices match within 0.0001.
- Saved editable delivery comparison passes at 15 critical frames, below
  0.00007 Blender units. Converted native animation passes the existing crane,
  donkey and cargo handoff tolerances; the clip remains 68 seconds.
- Before/after saved-AST district, storage and top views were rendered. The
  inspected storage views retain the building and prop composition.
- Saved-source validation: intact and decals have no errors. CON+PIL retains
  the state-only scaffolding warning treated as an intact-scene error by the
  generic validator. Delivery retains its five previously documented animated
  contract findings; native animation validation supplies the relevant checks.
- ModBuddy Build Solution succeeded with zero failed projects. Installed
  Windows and MacOS `CSC_Tilebases.blp` were rebuilt at 17:16 on 20 October.
- Asset Editor launched, but its computer-use app approval timed out. Its live
  preview was not verified. The visual comparison above uses saved-AST renders.
- **Henno reports the trial looks good in game (20 October).** He observes
  slight donkey levitation on its return toward the riverside Wind Mill.
  This is consistent with the delivery sharing the storage ground pivot while
  its authored route has fixed vertical positions; terrain variation along
  the route has not been measured. No corrective animation change made.
  Separate construction/pillaged-state checks were not explicitly reported.

## Evidence and recovery

Review package:
`C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\pivot-trial-20261020`.

Original runtime files are in `before/`; the four original Blender sources
are in `before-sources/`. `transform.json`, `assembly-check.json`,
`native-geometry-check.json`, `delivery/native-check.json`,
`delivery-source-check.json`, `source-validation-comparison.json` and
`install-report.json` hold the measured checks. The first installation backup
also preserves the original live files; later installation backups capture
the resumed registration steps.

Source utilities:
`project/tools/art/storage_pivot_trial.py`,
`storage_pivot_trial_blender.py`, `storage_pivot_review_blender.py`.
`export_storage_delivery.py` accepts explicit source, output, bridge and
optional rebase transform paths. When exporting the now-centered editable
delivery source, **do not apply the rebase transform again**.

For subsequent bases, compose **old district attachment × T**, rather than
blindly copying Base 03's numbers. Each separately authored storage AST must
also inverse-transform its own props and separate its delivery before use.

## Separate donkey terrain experiment — 20 October

After reporting that the storage looks good in game, Henno requested a Base 03
trial separating the donkey/sled while leaving cargo behavior unchanged.

Base 03 now references `CSC_TRIAL_BAKERS_Delivery_Split` in place of
`CSC_BAKERS_Storage_Delivery`. The trial references the same
`CSC_ALL_Delivery_Pivot` model and animation. Its existing donkey mesh is hidden
in all five states, and `CSC_TRIAL_Delivery_Donkey` is attached to the existing
animated `DonkeyPath` bone with zero offset/rotation, scale 1 and Pivot Height.
The crane geometry, native parent clip and cargo attachment are unchanged.
The original combined delivery AST and binaries remain available.

The separated child has its own 68-second local animation. At each sampled
frame, its bone poses are expressed relative to the native DonkeyPath transform,
so the parent supplies travel and the child supplies local body/gait motion.
This follows the native Mine's moving-parent/separate-donkey structure.
It does **not** yet establish that the engine samples terrain at the moving
attachment every frame.

Both trial participants use `Standard_LandmarkNoRandomOffset`, with attachment
randomization disabled. This removes independent random start phases.

Validation:

- 508 donkey/sled vertices and three UV channels; native converter verifies
  positions, UVs, triangles and skin weights against the exported CN6.
- Local factoring reconstructs the original poses within 0.000217 Blender units
  at 15 sampled frames. Reimported child plus original parent route differs by
  at most 0.279 Blender units, within the 0.4 trial gate.
- Converted native walking and pickup poses were visually inspected.
- Saved single-model source validation has one static-building rule mismatch:
  `STATIC_WEIGHTS`, expected for the existing animated donkey skin. The native
  skinning and pose checks above are the applicable checks.
- Parent animation binding and cargo attachment compare unchanged. Baseline
  model, clip and original delivery AST remain byte-identical.
- Normal CSC SDK build succeeded with zero warnings/errors. Windows and MacOS
  tilebase packages rebuilt at 19:55 on 20 October; the cooker log contains no
  reported failures.
- **Henno's in-game review, 20 October:** the current split-donkey behavior
  looks “pretty much spot on.” Retain this setup as the accepted Base 03 visual
  reference, with cargo unchanged. This is user-reported visual acceptance;
  exact engine terrain-sampling behavior and untested placements are not inferred.

Evidence and editable child master:
`Desktop/Codex/CSC_Storage_L/donkey-terrain-trial-20261020/`.
The master is `CSC_TRIAL_Delivery_Donkey.blend`; snapshots and reports are in the
same folder. Existing authored storage/delivery Blender sources were not changed.
Source utilities are `donkey_terrain_trial_blender.py` and
`install_donkey_terrain_trial.py` under `project/tools/art`.

When extending this setup to other placements, check ground contact, visibility
and timing over multiple loops. Cargo retains its original height behavior;
Henno's accepted Base 03 result does not require a cargo-system change.

To return Base 03 to the combined delivery, change its delivery Asset reference
back to `CSC_BAKERS_Storage_Delivery` and rebuild. The previous Base 03 AST is
also preserved under the trial's `before/Assets/` directory.

## Storage L family rollout — 20 October

Henno confirmed that the storage no longer sinks and its props remain correctly
placed, and requested the same setup across all Storage L combinations.
The rollout covers all six assets using `CSC_Storage_L` geometry and all twelve
district attachments:

| Quarter | Classical bases | Storage | Delivery |
|---|---|---|---|
| Bakers | 03, 04, 05 | Storage_L | Accepted split setup |
| Bakers | 06, 07, 08 | Storage_L_No_Delivery | None |
| Bakers | 10 | Storage_L_2 | Split setup, original flour cargo |
| Bakers | 11 | Storage_L_No_Delivery_2 | None |
| Tailors | 03, 04, 05 | Storage_L | Split setup, original textile cargo |
| Tailors | 06 | Storage_L_2 | Split setup, original textile cargo |

Five remaining storage ASTs have their 114 static/FX attachment transforms
rebased into the centered building's local coordinates. Props remain children
of storage. Eleven remaining district placements compose their existing
transform with T, including Tailors Base 03's small existing offset. Tailors
Base 04 changes from Average Height to Pivot Height. Accepted Bakers Base 03,
its storage AST and both accepted split assets remain byte-identical.

All eight placements that already used delivery now have it as a sibling of
storage on the district base. Three added ASTs preserve the variants' original
crane materials, cargo bones, offsets, rotations and scales:
`CSC_BAKERS_Storage_Delivery_2_Split`,
`CSC_TAILORS_Storage_Delivery_Split`, and
`CSC_TAILORS_Storage_Delivery_2_Split`.
They reuse the centered parent model/clip and accepted
`CSC_TRIAL_Delivery_Donkey` child, with the same phase settings as Base 03.
The trial identifiers are retained to reuse the exact accepted assets.
Two No_Delivery ASTs had orphan cargo attachments and animation bindings
referencing a nonexistent delivery model; these are removed.

No further Blender source, geometry or animation edits are required for this
rollout. The earlier centered masters and separated donkey source remain the
editable sources. Do not apply the pivot transform to them again.

Validation and pillaged visibility:

- All authored prop transforms reconstruct their previous district positions
  and rotations within 0.000000181 Blender matrix units.
- All twelve assemblies resolve in all five states (60 checks), including their
  asset, material and geometry dependencies. The damaged storage shell is
  enabled in Pillaged and Construction, with scaffolding only in Construction.
- Saved-AST Tailors Base 03 renders were inspected in Worked, Pillaged and
  Construction. The shell is visible and aligned in the damaged-state preview.
  These are material-color, bind-pose assembly checks; they do not simulate
  engine terrain or animation. Review jobs explicitly retain hidden-owner
  skeletons so cargo anchors can still be resolved.
- The original cargo records compare unchanged, and all variants' donor donkey
  material/state records match the accepted child source. Reused FGX/animation
  hashes and the accepted Base 03 files remain unchanged.
- Normal SDK build completed with zero warnings/errors. Windows and MacOS
  tilebase packages rebuilt at 20:26; all 24 affected asset/geometry identifiers
  are present in each package. All 19 staged ASTs match live source; the three
  new loose installed AST copies match as well. Existing ASTs are cooked from
  the workspace pantry even when they are not copied as loose Content files.
- Henno reported the storage missing in Pillaged **in game**, then asked to
  prioritize repositioning if no clear defect emerged. No source defect was
  established: the shell's state records, material bindings and native geometry
  are present. Pillaged visibility after rebuilding still needs in-game review;
  do not describe it as fixed on the strength of the offline preview.

Evidence and recovery:
`Desktop/Codex/CSC_Storage_L/storage-family-pivot-20261020/` contains guarded
before snapshots, the staged 19-AST payload, placement/state reports, three-state
review images, installation backups and the build log. The migration utility is
`project/tools/art/storage_family_pivot.py`. It is a one-time migration; do not
run its staging phase against already migrated assets.

## Cafe wall assembly pivot — 20 October

Henno requested the same placement separation for `CSC_ALL_Stage_4_Wall`,
with the overall offset on its attachments to `CSC_BAKERS_Cafe` and
`CSC_BAKERS_Cafe_2`.

This asset is an assembly of eleven reusable Garden Wall Curve segments around
an empty district-base model. Its displacement was in the child attachment
positions, so no Blender or FGX changes were needed. The native wall geometry's
assembled XY bounding-box center, at ground Z=0, defines the new local origin:

- Offset removed from each segment, AE units:
  `(15.2981458249, 8.3288062046, 0)`.
- Compensated wall attachment in both Cafe variants, AE units:
  `(15.351223825, 8.289325205, 0)`, including their existing small offsets.
- Rotation, scale, TerrainFollowMode, culling, states, materials, all other
  Cafe attachments and the fitted courtyard paving are unchanged.

The eleven wall sections remain children of the wall assembly; the wall
assembly remains a child of each Cafe. Their final world transforms reconstruct
the previous layout within 2.85e-14 Blender matrix units. XML comparisons allow
only the thirteen affected attachment positions to change. Before/after
saved-AST previews, including paving geometry, were inspected; the top views
have only fourteen changed pixels out of 1,080,000 from numerical rendering
differences. The preview uses material colors, not the engine's terrain shader.
The normal SDK build succeeded with zero warnings/errors; both Windows and
MacOS tilebase packages were rebuilt and contain the three affected assets.
All staged/live AST hashes match and all preview geometry hashes are unchanged.
Terrain contact with the relocated assembly pivot still needs in-game review.

Evidence, original ASTs, staged files and build log:
`Desktop/Codex/CSC_Cafe_Wall/ground-pivot-20261020/`.
The guarded one-time tool is `project/tools/art/cafe_wall_pivot.py`.
Future paving fitting must compose the wall's parent attachment transform;
its segment positions now describe the centered local assembly, not Cafe-space
coordinates. The already fitted paving requires no change.
