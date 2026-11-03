# Modern medium and large storage — first Blender version

29 October 2026. Henno accepted both concept directions, requesting a more balanced large roof and a more compact delivery vehicle. These are editable Blender review candidates, not installed runtime assets.

## Sources

Relative to `Desktop/Working Files/3D Art/`:

| Role | Source |
|---|---|
| Medium building | `Storage/Storage_M/modern/revision-01/CSC_Storage_M_Modern.blend` |
| Large building | `Storage/Storage_L/modern/revision-01/CSC_Storage_L_Modern.blend` |
| Electric jib | `Storage/Props/modern/revision-01/CSC_ALL_Storage_Hoist_Modern.blend` |
| Compact flatbed | `Storage/Props/modern/revision-01/CSC_ALL_Flatbed_Compact_Modern.blend` |
| Pallet jack | `Storage/Props/modern/revision-01/CSC_ALL_Pallet_Jack_Modern.blend` |
| Ingredient drum | `Storage/Props/modern/revision-01/CSC_ALL_Ingredient_Drum_Modern.blend` |

Each building directory also contains standard and dispatch `CSC_BAKERS_Storage_{M,L}_Modern[_2]_Review.blend` proposals. Those compositions retain full underground foundations; clipping happens only in temporary render geometry. They are not export/placement authorities. Individual masters have relative external texture snapshots, Review/Export scenes, static Bone bindings and CN6 exports.

Existing flour pallet and sack-trolley masters are reused as references from `BAKERS/Props/Modern/revision-02`. Their source geometry and original files remain unchanged. The review placements account for each saved prop's actual support bounds. Stock is retained in dispatch scenes; the medium adds the pallet jack and the large adds the flatbed with cargo.

## Shape and materials

Historical storage sources were measured first. Medium height is 82 versus historical 81.756; large is 88.9 versus 88.630. Foundations reach Z=-22 and -18 respectively. Both preserve the compact gabled storehouse family and low receiving platform. The large loading cross-gable has a lower ridge than the main roof, narrower span and computed valley intersections. Roof undersides and gable ends are closed; only substantial trim is geometry. The front receiving edge is open for access.

The new truck is 37.3 × 18.8 × 24 Blender units, with a cab-over body and short open bed. The front painting is split between the actual windscreen and grille, avoiding a duplicate windscreen. Vehicle, jib, drum and pallet jack each have independent geometry/AO and source files. The jib is a static first version; no animated loading cycle is implemented.

Building surfaces use the shared modern atlas's storage quadrant (bottom right). Accepted registered brick, block, roofing, timber and trim maps are reused; storage doors/window and truck-bed/hoist details use new ImageGen painting constrained by surface guides. Door relief, window panes, bed ribs and hoist case relief are registered to structural features, not albedo noise. Brick sampling is consistent between walls and gables. Roof seams are deliberately broad. The large upper window has a soft E patch; the medium ground-level window remains dark. Daytime comparisons disable emission.

Candidate libraries are under `Textures/{CSC_Buildings_Modern,CSC_Props_Modern}/Candidates/2026-10-29_Storage_v001`. Published Current libraries are unchanged. The candidates preserve the Café's unpublished L3/prop patches as well as published human edits. New prop surface cells are 46 (bed panel), 47 (hoist face), 48 (recoloured painted metal). The new props' AO uses a documented candidate block in the currently unused right region; reconcile that future Quarter reservation when publishing. No occupied AO regions are overwritten.

## Verification and limits

Evidence package: `Desktop/Codex/modern-storage-v1-20261029/`.

- Saved-file checks for six independent masters and four review proposals.
- CN6 → FGX native readback checks topology, positions, normal/tangent/binormal, UV1/UV2/UV3 and static weights.
- Independent per-model AO, paint-only, neutral normals off/on under two light directions, AO-only, front/rear and concept-comparison images.
- Roof/jamb/string-course intersections reviewed; coplanar overlapping trim joins corrected and AO rebaked.
- Published atlas source hashes checked unchanged. Exact model and full-scene counts are recorded in `delivery.json` and `final-saved-validation.json`.

Conservative budget accounting includes every new prop even where reuse is intended. The large dispatch scene exceeds the 2,200 advisory target once the truck is included; this is reported, not treated as an engine limit. Existing shared flour props are excluded from that budget but included in whole-scene counts.

Final exported counts: medium building 1,144 vertices / 570 triangles; large building 1,688 / 844; hoist 192 / 96; truck 519 / 296; pallet jack 312 / 172; drum 256 / 160. Conservative new-geometry totals are medium standard 1,400, medium dispatch 1,712, large standard 2,136 and large dispatch 2,655 vertices. All ten saved files pass the automated authoring checks and all six native-format checks pass; visual/game limits above still apply.

AE installation, final district-road placement, CON/PIL variants, cooking and in-game validation are not part of this Blender handoff. Room/glass/night behavior is not claimed as native-engine verified. Preserve later human changes to these saved files; do not regenerate from the build script over edited masters.

Tools: `project/tools/art/modern_storage/`. New paint's original image, guide, semantic relief masks and prompt are in the evidence package's `sources/` folder.
