# Cafe regular concept — prop delivery

## Saved wall fit — 18 October 2026

Revision09 reshapes the existing limestone decal to Henno's saved `CSC_ALL_Stage_4_Wall` assembly attached to `CSC_BAKERS_Cafe.ast`: eleven wall sections at their saved positions/scales, plus road layout05. The paving follows the wall centreline with a narrow inward fade, and a broader feathered apron stops before the front road. Native road triangle UV/alpha sampling supplies a five-world-unit clearance from its smoothed visible edge, followed by a soft paving fade. Wall/road geometry and AE assembly files were not changed; concurrent café prop edits were inspected and preserved.

The base colour RGB is byte-identical to revision08. Only its alpha footprint changed; the matching height map was rederived with the existing RGB86–99 settings and identical new alpha. Both source PNGs and runtime DDS files are updated. Shared atlas r035 remains unchanged. Exact DDS comparisons, zero road-core overlap, and the relocated saved-master validator passed. Before/after top and hero renders reconstruct the saved AE geometry; they are Blender previews, not live AE/cook verification.

**Active source is now `C:/Users/Shadow/Desktop/Working Files/3D Art/Decals/CSC_ALL_Stage_4_Cobble_Decals.blend`, with B/H PNGs beside it.** Henno moved these from the earlier Café source folder. Broken relative image links caused by that move were repaired in place; geometry, UVs and transforms were verified unchanged. Do not rerun the historical bulk Café builder against the old location. The fitting workflow is `prepare_cafe_wall_fit.py`, `review_cafe_wall_fit.py`, `cafe_wall_fit.py` and `install_cafe_wall_fit.py`; the sampled boundary contract is `cafe_courtyard_fit.json`.

Review package and backups: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-09-wall-fit/`. The review is a saved snapshot; Henno continued editing unrelated props during the task. AE remains the assembly authority.

## Warm limestone paving — 18 October 2026

Henno selected the warm limestone concept. The existing `CSC_ALL_Stage_4_Cobble_Decals` identity now uses larger dressed limestone slabs with narrow joints, replacing the small straight cobbles. New base-colour artwork was generated with built-in ImageGen (`exec-8e627e2a-0495-4380-a434-d56c1f208617`); the exact prompt is in `project/tools/art/cafe_limestone_prompt.txt`. Four slab widths and eight courses repeat over 60 world units: approximately 15 × 7.5-unit slabs, aligned to the façade by the existing rigid mapping.

Canonical shared release **2026-10-18_Shared_01_r035**, new vacant slot **31** (`cafe_warm_limestone`), retains all occupied surface pixels and every existing AO/opacity/emission map. The full-resolution ImageGen source, prompt, packed B/N/G/M patches and deterministic packer are retained in the canonical release. Slot30's earlier cobbles remain available.

The dedicated 512px decal base colour and matching `CSC_ALL_Stage_4_Cobbles_H` are installed and the material's Heightmap slot is connected. The technical height retains the original square cobbles' linear RGBA settings, full mip chain and restrained RGB86–99 range. Its alpha matches the base exactly. Courtyard footprint, feathering, geometry coordinates and all AE assembly placements are preserved. Existing asset names remain stable to preserve references.

Saved-source validation, native round-trip (zero error), installed DDS colour/height/alpha comparisons (zero error), shared atlas rebuild and occupied-pixel checks passed. Blender hero/top previews were inspected; live AE/game appearance and cooking remain unverified. Reload the existing material/decal in AE to inspect the update.

Outputs, backups, provenance and reports: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-08-warm-limestone/`; height evidence in `height-map/`. Editable master remains `C:/Users/Shadow/Desktop/Working Files/3D Art/Props/Bakers/Cafe_Regular_20261017/CSC_ALL_Stage_4_Cobble_Decals.blend`; external base/height PNGs and full-resolution limestone source are in its `textures/` directory. Earlier sections below are historical revisions.

## Height map connected — revision 07, 18 October 2026

`CSC_ALL_Stage_4_Cobble_Decals` now binds **`CSC_ALL_Stage_4_Cobbles_H`** in its Heightmap slot. The 512×512 technical map derives recessed mortar and subtle surface relief from the current registered ImageGen cobbles. RGB uses the original square-cobbles map's 86–99 height range; alpha is copied exactly from the current base colour. Base colour, footprint, geometry, source blend and AE assembly placements are unchanged.

The TEX wrapper copies `CSC_ALL_Stage_3_Cobbles_Sq_H` settings: `Decal_Heightmap`, `R8G8B8A8_UNORM`, linear gamma, `FT_B_SPLINE`, complete mip chain, MinHeight0 / MaxHeight255. Source PNG and DDS sit in the Café master's `textures/` folder; the DDS is the AE source, matching the original material's import setup. Installed DDS pixels match RGBA exactly. AE dependency cache includes the new texture and material dependency. Latest AE/game visual review remains pending; no geometry displacement or Blender shader parity is claimed.

Output, backup, contrast inspection image and verification report: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-07-heightmap/`. Reproducible derivation and installation: `project/tools/art/add_cafe_cobble_height.py`. If the colour artwork or layout changes again, regenerate its registered height map as well. This is a technical companion map, not new painted artwork; shared atlas r034 is unchanged.

## New cobble artwork — revision 06, 17 October 2026

Henno rejected the inherited skew in the old square-cobble painting and explicitly requested a new texture. **The current decal uses new built-in ImageGen artwork:** straight orthographic running-bond limestone cobbles, horizontal courses, rectangular stones, warm grey/buff palette. It replaces the old artwork, not the courtyard layout. The revision05 alpha mask is byte-identical, so the side extension, half-depth rear and feathering are preserved.

Current output: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-06-new-cobbles/`. `Straight_Cobbles_ImageGen.png` is the full generated source, `ImageGen_Prompt.txt` records the exact prompt, and `After_Top_Front_Up.png` / `After_Hero.png` show the mapped result. The editable master remains `Working Files/3D Art/Props/Bakers/Cafe_Regular_20261017/CSC_ALL_Stage_4_Cobble_Decals.blend`; its adjacent `textures/CSC_Cafe_Straight_Cobbles_Source.png` is the local source snapshot. Placement remains zero position/rotation and scale1.

The straight tile is mapped along the facade with a rigid 30-degree orientation and a 60-unit square repeat, giving approximately 6×5-unit stones. No shearing or perspective correction is applied. The runtime decal keeps its dedicated 512px feathered layout texture; its new surface artwork is also registered for reuse in the canonical shared atlas.

Canonical release **2026-10-17_Shared_01_r034** adds `cafe_straight_cobbles` to verified empty slot30 (inner bounds `[772,388,892,508]`, four-pixel padding). The full ImageGen source, exact prompt, packed base colour and technical N/G/M companions are in `Current/atlas/sources/`. All previously occupied pixels, all AO, opacity and emission were preserved; deterministic rebuild and release/Current hashes passed. The new decal is installed, saved-source validation passed, native round-trip has zero numeric error, and runtime DDS RGBA/alpha match the source exactly. AE assembly files and placements were preserved. Blender previews are verified; latest AE/game visual review remains pending.

ImageGen provenance: `exec-ec1fa6d9-7c45-41ca-bedd-0554b19306cf`. Earlier sections below are historical and do not describe the current painting.

## AE top-view refinement — revision 05, 17 October 2026

Current output package: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-05-courtyard-fit/`.

Henno's AE screenshot requested rows parallel to the facade, paving extended to the road on the screen-right side (front of building at the top), and half the previous depth behind the building. The current decal implements all three. A 75-degree clockwise trial was refined to **68 degrees clockwise**, because the source artwork already contains skewed rows. The existing square-cobble artwork is retained at its previous world density. Henno also authorized ImageGen replacement artwork if the inherited skew proves troublesome; no new painting was needed for this revision.

In building-local coordinates, screen right is negative U. The outline there now reaches U=-109.3, meeting the inside edge of the road. Rear outline depth is compressed by 0.5 beyond the back wall at V=27: the maximum V changes from 86.5 to 56.75. Front/left boundaries remain in their previous positions except where they join the extended side or shortened rear. The 7-unit feather remains. Card bounds are now X32..264/Y-42..190; identity placement still aligns it with generic L3. The shared wall geometry and all AE assembly placements are unchanged.

The same separate `.blend` master and installed decal identity were updated. It remains 4 vertices / 2 triangles with a 512px texture. Saved-source validation, native round-trip (zero error), and installed DDS RGBA/alpha comparison (zero error) passed. The canonical shared atlas and XLPs were preserved. A concurrent save of `CSC_BAKERS_Bakery_2.ast` was detected and its latest bytes preserved. Native AE/game appearance of this latest revision remains for review.

`Before_Top_Front_Up.png` and `After_Top_Front_Up.png` use the same camera with the building front at the top. `After_Hero.png` and `Cafe_Courtyard_Review.blend` show the actual building and road context without a proposed wall/prop layout obscuring the paving. The source master remains at the path below. Earlier sections describe prior revisions.

## Courtyard correction — 17 October 2026

The current `CSC_ALL_Stage_4_Cobble_Decals.blend` replaces the detached hard-edged disk. Its geometry now shares the generic L3 building's baked coordinate frame: **position `(0,0,0)`, rotation `(0,0,0)`, uniform scale `1`** aligns it beneath the building. Do not apply the previous review-only translation `(159,62)` in Blender or `(15.9,6.2)` in AE. Existing AE attachment transforms and building assemblies were preserved; clear a manual offset on the decal itself if one was added to compensate for the old model.

The courtyard follows the inner crescent wall and broadens into a shallow rounded forecourt at the road. A 7-unit inward feather with slight irregularity softens its boundary. The 512 × 512 RGBA texture reuses Henno's `CSC_Stage_3_Cobbles_Two_Variants/square/textures/CSC_ALL_Stage_3_Cobbles_Sq_B.png`, tiled/resampled at the previous stone density. Only the layout alpha is newly derived; no new painted artwork or shared-atlas changes. The original Stage3 sources remain unchanged.

The revised master has **4 exported vertices / 2 triangles**. Saved-source validation and native round-trip passed with zero numeric error. Installed DDS colour and alpha exactly match the source PNG. GEO/FGX/material/texture files and the reusable catalogue were updated; all ASTs, XLPs and canonical atlas files were verified unchanged. Reload the decal in AE to see the geometry update. AE/game appearance still requires review; the images below are Blender previews.

Current source: `C:/Users/Shadow/Desktop/Working Files/3D Art/Props/Bakers/Cafe_Regular_20261017/CSC_ALL_Stage_4_Cobble_Decals.blend`.

Current review, before-fix backups, provenance and installation report: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-04-courtyard/`. `Cafe_Regular_Hero.png`, `Cafe_Regular_Top.png` and `Cafe_Regular_Review.blend` show the corrected zero-offset decal against the original building and roads. The earlier circular-decal description and counts below are historical, superseded by this section.

## Additional wall section — 17 October 2026

`CSC_ALL_Garden_Wall_Curve_2.blend` is now available beside the original masters: a shallower 15-degree segment with radius 192, retaining the original segment's arc length, height, thickness and stonework. It exports 148 vertices / 104 triangles and has its own isolated AO. It is installed and registered in the reusable library; existing wall and building assemblies are preserved. Atlas release r033 adds only its AO cell `[384,640,512,768]`. Preview and validation: `C:/Users/Shadow/Desktop/Codex/Cafe/revision-03-shallow-wall/`. The original ten-model delivery below remains its historical record.

Editable sources: `C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Bakers\Cafe_Regular_20261017`

Review package: `C:\Users\Shadow\Desktop\Codex\Cafe\revision-02-production`

One .blend per independently exported model. Export contains only that model and its static rig; Review supplies lighting/camera. The combined Cafe_Regular_Review.blend is a placement proposal, not an export source.

## Files

| Model | Exported vertices | Triangles |
|---|---:|---:|
| CSC_BAKERS_Cafe_Chair | 240 | 120 |
| CSC_BAKERS_Cafe_Counter | 144 | 72 |
| CSC_BAKERS_Cafe_Brewing_Set | 1164 | 968 |
| CSC_BAKERS_Cafe_Pastry_Tray | 128 | 70 |
| CSC_BAKERS_Cafe_Table_Service | 851 | 712 |
| CSC_BAKERS_Cafe_Reading_Set | 267 | 220 |
| CSC_ALL_Garden_Wall_Curve | 150 | 104 |
| CSC_ALL_Stage_4_Cobble_Decals | 64 | 62 |
| CSC_ALL_Oval_Table | 280 | 188 |
| CSC_ALL_Flour_Sack_Closed | 140 | 178 |

## Reuse and placement

The oval table and closed sack preserve their existing source geometry and UVs. Eight copies of the new 30-degree wall segment form the proposed crescent. Each segment has its own ground pivot. The cobbles reuse the exact square-variant base-colour PNG named by Henno; the existing Stage3 opacity/height sheet is tied to another building layout, so the new circular decal uses a geometry footprint and a new material using a colour-identical copy with only the old layout alpha cleared. No cobble artwork was generated.

The brewing set uses the counter ground pivot and has its contents at counter height 17.8. The table service and reading set use the table ground pivot and tabletop height 13. Apply the same placement/rotation/scale as their support. The pastry tray rests on its own local Z=0 contact plane. Plants and pots remain for Henno to place from existing assets.

## Atlas and validation

Shared atlas 2026-10-17_Shared_01_r032: six ImageGen-painted surfaces in previously vacant slots 10–15; seven isolated AO cells in Bakers Stage4. All pre-existing surface pixels, other AO allocations, opacity/emission and sheet02 preserved. Source artwork, companion maps, manifests, hashes and reproducible packer are in the canonical release.

All ten saved blends pass automated source validation. All ten CN6→FGX→CN6 comparisons preserve geometry, normals, UVs and triangles within 5e-6 numeric error. Runtime AST/GEO/MTL and XLP registrations are installed. Props are visible in Worked/Unworked and hidden in Construction/Pillaged/Unbuilt. Existing building ASTs were not rewritten; final assembly, duplicates and plants remain in AE. No new base building geometry is exported.

Geometry accounting for the proposed scene: building plus bespoke props 4,927 exported vertices versus the advisory 2,200 target; full scene including reused furniture, sacks, wall copies and decal 7,031. Counts are reported rather than hidden by the per-file checks. The coffee sets and repeated chairs account for most of the excess.

The unchanged generic L3 reference retains its inherited static-weight validation issue. That reference is excluded from the new exports. Blender renders are appearance previews; AE decal projection/terrain behavior, cooking and in-game appearance are not yet verified. Final icon/SV work should use the saved AE AST after placement.

Source and review provenance: source-parity.json in revision-01-base, native-verification.json, individual *-validation.json and *-export.json, cobbles-provenance.json, review-placements.json and install-report.json.
