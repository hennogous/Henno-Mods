# Tailor lean-to atlas propagation — 12 October 2026

User requested the new default lean-to atlas mapping propagated to both Tailor scenes and their CON+PIL variants, plus a render confirming the master.

- Confirmed `Props/CSC_Storage_LeanTo.blend` and `TAILORS/Tailor/revision-10-vertex-budget/CSC_TAILORS_Tailor_LeanTo.blend` already had the new storage-quadrant UV1 and shelter AO UV2. Fresh renders verified both. The default has four posts; the Tailor master keeps its authored three-post shape.
- Updated both intact revision-10 scenes, their shared CON+PIL source and the embedded lean-to in the PIL-decal review. Also synchronized the three matching kit sources under `Level 2/Tailors/`.
- UV1 and UV2 now use the existing canonical atlas/material. Intact instances copy the Tailor master exactly. CON+PIL inherited surfaces transfer through old-to-new face correspondence; its added crossbeam uses the master's timber strip and existing beam AO island. No texture pixels were edited.
- Preserved all source geometry, object/parent transforms, weights and scene UV3. Removed pre-existing UV3 transfer roundoff (maximum 5.96e-8) from the standalone Tailor master by restoring the scene's original values, ensuring exact exporter mesh-signature parity between master and both instances.
- Both intact saved scenes pass authoring validation with zero errors. All five source-export decoder checks pass (two buildings, lean-to master, shared state geometry, PIL decals). Generic building validator findings for the state/decal/legacy-kit files are unchanged structural expectations; the applicable state/decal decoder checks pass. Fresh intact, Construction and Pillaged renders reviewed.
- Blender-source fix only: no runtime FGX/GEO export, installation, cook or in-game verification in this task.

Review package, scripts, original backups and validation evidence:
`C:\Users\Shadow\Desktop\Codex\Tailor_LeanTo_UV_20261012\`

## CON+PIL darkness follow-up

Henno noted overly dark AO. Diagnostic renders isolated a Blender normal-map wiring fault: `CSC_Level_2_CON+PIL_Bldg` connected its normal image Color directly to Principled Normal, with the image also marked sRGB. Adding a tangent-space Normal Map node (UV1) removes the blackened walls while retaining the original AO. The AO-only emission view shows mild surface/corner shading; no atlas brightening/rebake is warranted from this Blender evidence.

Fixed the state building/sign material in revision-10 CON+PIL, the PIL-decal embedded review and `Level 2/Tailors/CSC_TAILORS_Tailor_CON+PIL.blend`. Normal image uses Non-Color. Resolved missing old-host texture paths on that legacy Tailor kit source. Geometry, all UV layers, placements, weights, material assignments and AO data/strength remain unchanged. Saved-source checks passed; the legacy rigged state uses state-mesh decoding rather than the static-prop weight constraint. No runtime materials or textures changed.

Evidence and original backups: `C:\Users\Shadow\Desktop\Codex\Tailor_CONPIL_AO_20261012\`; final render `Tailor_CONPIL_corrected.png`.

## Square cobbles and complete re-export

Henno requested square-cobble previews matching his live AE edits and re-export of this task's updated scenes. Both live Tailor ASTs already selected `CSC_ALL_Stage_3_Cobbles_Sq` on the shared Stage 3 decal.

- Both intact scene previews, CON+PIL review, PIL review and Work Area decal source now use the canonical square B/H and single-quad footprint from `Decals/CSC_Stage_3_Cobbles_Two_Variants/square/CSC_ALL_Stage_3_Cobble_Decals.blend`. Replaced the old nine-card preview layout with the same native footprint; preview plane is lowered 24 units from its runtime projection height. All non-cobble content hash-preserved.
- Added explicit `cobble_material` contract support, retained in both scene metadata and `export-contract.json`; exporter now carries it through dependency checks, staging and validation. Existing defaults remain unchanged for other buildings. Lean-to validation accepts the Quarter NE building material, matching the existing AE prop. Revision defaults retain all seven existing prop masters' state templates and explicitly replace the alternate masters.
- Archived the earlier pre-atlas backup blend into the revision's `backups/` subfolder so top-level export discovery no longer treats it as a second active master.
- Standard folder runner with `--include-optional --no-install` staged and converted 11 geometries and 9 assets. All 11 native FGX readbacks match positions/normals/UV1–3 and triangles within conversion tolerance. Staged/live state comparison found only the required CON+PIL lean-to geometry-group rename; material/state values are preserved. Attachment differences are numerical serialization precision only (maximum observed 1.23e-6 AE units).
- Installed through the normal `--install` command: 22 FGX/GEO files, nine ASTs, and the merged XLP. All 31 content-file hashes match the installation receipt; nine XLP IDs are unique and present in AssetCloud's cache. Shared square-cobble geometry, current materials and texture DDSs are reused unchanged. Both Tailor variants retain the exact square material.
- 107 exporter tests pass (seven Blender-dependent skips). Fresh intact/alternate/Construction/Pillaged renders inspected. No cook or game run performed; normal ModBuddy build consumes installed assets.

Outputs, renders, original blend backups, staged files, native readbacks and install backups:
`C:\Users\Shadow\Desktop\Codex\Tailor_Reexport_20261012\`
Install job: `export-run-01/job.json`; final evidence `installation-validation.json`.
