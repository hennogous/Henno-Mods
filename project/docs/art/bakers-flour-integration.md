# Bakers flour integration and vertex savings

Integrated on 7 October 2026 from `Bakers_Flour_FINAL`.

## Runtime integration

The replacement files retain `CSC_BAKERS_Flour`, `CSC_BAKERS_Flour_Closed` and `CSC_BAKERS_Flour_Open`. The handoff's `CSC_ALL_Flour_*` names map to these existing identities; those temporary runtime entries were removed. The old AST/FGX/GEO files are archived at `C:\Users\Shadow\Desktop\Archive\CSC Bakers Flour - retired 2026-10-07`.

All 156 placements across 23 recipient assets were updated, including normal and expanded Bakers buildings. Positions, rotations, parent/bone assignments and state settings were retained. The pile has a baked 0.2 geometry scale, so its attachment scales changed from 0.2 to 1.0 and 0.15 to 0.75 to keep the same effective size. Sack attachment scales were retained.

All three replacements reuse `CSC_ALL_Props_01` and the authoritative Shared 01 r021 textures. No extra material, texture or runtime asset registration is needed. Source handoff blends/CN6 files remain unchanged.

## Exported vertex savings

Counts come from reading the old and replacement FGX files back to CN6; they include exported vertex splits.

| Prop | Old vertices | New vertices | Saved | Reduction |
|---|---:|---:|---:|---:|
| CSC_BAKERS_Flour | 138 | 66 | 72 | 52.2% |
| CSC_BAKERS_Flour_Closed | 304 | 140 | 164 | 53.9% |
| CSC_BAKERS_Flour_Open | 248 | 122 | 126 | 50.8% |
| **Three unique meshes** | **690** | **328** | **362** | **52.5%** |

Triangles across the three meshes fall from **576 to 480** (16.7% fewer).

## Savings across authored placements

Across all 156 authored flour placements: **42,986 to 19,980 vertices**, saving **23,006 (53.5%)**. Triangles fall from **35,490 to 26,586**.

These totals sum flour instances across all asset definitions. District base alternatives and normal/expanded building alternatives are mutually exclusive; the total is not one simultaneously rendered scene. Actual visible savings depend on which assets and states are active. No FPS improvement was measured. The table below covers flour only, not each whole building.

| Recipient asset | Flour placements | Old vertices | New vertices | Saved |
|---|---:|---:|---:|---:|
| CSC_BAKERS_Ancient_Base_01 | 2 | 276 | 132 | 144 |
| CSC_BAKERS_Ancient_Base_02 | 5 | 1,132 | 534 | 598 |
| CSC_BAKERS_Ancient_Base_03 | 2 | 276 | 132 | 144 |
| CSC_BAKERS_Bakery | 2 | 552 | 262 | 290 |
| CSC_BAKERS_Bakery_2 | 6 | 1,712 | 804 | 908 |
| CSC_BAKERS_Cafe | 1 | 304 | 140 | 164 |
| CSC_BAKERS_Cafe_2 | 1 | 304 | 140 | 164 |
| CSC_BAKERS_Classical_Base_01 | 3 | 414 | 198 | 216 |
| CSC_BAKERS_Classical_Base_02 | 7 | 1,574 | 740 | 834 |
| CSC_BAKERS_Classical_Base_03 | 3 | 746 | 346 | 400 |
| CSC_BAKERS_Classical_Base_04 | 6 | 1,492 | 692 | 800 |
| CSC_BAKERS_Classical_Base_05 | 8 | 2,432 | 1,120 | 1,312 |
| CSC_BAKERS_Classical_Base_06 | 3 | 746 | 346 | 400 |
| CSC_BAKERS_Classical_Base_07 | 6 | 1,492 | 692 | 800 |
| CSC_BAKERS_Classical_Base_08 | 8 | 2,432 | 1,120 | 1,312 |
| CSC_BAKERS_Classical_Base_09 | 3 | 414 | 198 | 216 |
| CSC_BAKERS_Storage_L | 22 | 6,576 | 3,044 | 3,532 |
| CSC_BAKERS_Storage_M | 8 | 2,432 | 1,120 | 1,312 |
| CSC_BAKERS_Storage_S | 3 | 912 | 420 | 492 |
| CSC_BAKERS_Water_Mill | 13 | 3,840 | 1,784 | 2,056 |
| CSC_BAKERS_Water_Mill_2 | 16 | 4,752 | 2,204 | 2,548 |
| CSC_BAKERS_Wind_Mill | 12 | 3,480 | 1,626 | 1,854 |
| CSC_BAKERS_Wind_Mill_2 | 16 | 4,696 | 2,186 | 2,510 |

## Verification

- Blender source structure, portable textures and original hashes verified.
- FGX readback matches the supplied vertex attributes and triangle indices; renaming preserves the geometry payload.
- Effective bounds, attachment transforms and visibility/state settings verified.
- Standard ModBuddy build and Windows/MacOS cooks passed; no cooker errors found.
- The verified build is installed in the normal game Mods folder. All 449 installed files match the build output; the previous installation is retained in the evidence folder.
- AssetCloud still lists the old material dependencies: reopen/refresh Asset Editor before its visual review. The cache was not patched manually.
- Asset Editor appearance and in-game terrain/state review remain pending.

Evidence and recovery snapshots: `C:\Users\Shadow\Desktop\Codex\bakers-flour-integration-20261007`.
