---
name: Level 1 open ground interior
description: 12 October 2026 requested threshold/floor removals and inward foundation extensions in two kit sources, FGX/GEO installed.
type: project
---

Edited the exact requested Working Files/3D Art/Level 1 sources:
CSC_Level_1.blend and CSC_Level_1_S_CON+PIL.blend. Removed three faces
per file: entrance threshold, transition ramp, and ground interior floor.
Added eight vertical inward-facing foundation quads around the combined room
and doorway perimeter, down to the original main foundation minimum depths
(-15.2422924 intact, -18.3780460 S CON+PIL). Interior remains open to terrain.
Retained vertex positions, face corners, all three UV channels and scaffolding
verified unchanged. New faces reuse existing foundation atlas charts. No AO bake.
Standard exporter repaired 18 already-unweighted intact vertices to Bone weight 1.

Saved originals and installed both named FGX/GEO pairs in CSC Geometries.
Native FGX readback verified mesh names, triangle indices, positions and UVs:
intact 1042 exported vertices / 791 triangles; S CON+PIL 1718 / 1034,
including Scaffolding. Max position error <0.00005, UV error <0.00000006.
Saved originals reopened and matched staged geometry, UVs and weights exactly.
Preserved original image paths and packed images (legacy missing external source
paths still print packing warnings). Other Level 1 kit sources remain unchanged.

These legacy armature kits have one Scene scene, not composed-scene Review/Export
metadata. Ran the saved-file authoring validator; its only errors are the two
inapplicable missing-scene findings. Native static-kit geometry/UV/weight checks
pass; no scene restructure or preview-only metadata added. Solid intact and
temporary cutaway renders inspected. Cooking/in-game appearance not tested.

Backups, staged sources, renders, native readback and receipts:
Desktop/Codex/CSC_Level_1_Foundation_20261012. Original blend and installed
geometry backups use `.before` suffixes. Task scripts were temporary files;
do not blindly replay the face-index edits against changed sources.

## Textile Workshop instances — same-day follow-up

User requested the same treatment for
Working Files/3D Art/TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao,
with full asset scene export. Updated both `CSC_TAILORS_Textile_Workshop_FINAL.blend`
and `CSC_TAILORS_Textile_Workshop_2_FINAL.blend`: removed triangles 447,448,
463,464,471,472 (threshold, ramp, floor), added eight inward foundation quads
at original depth -15.2422924. Preserved all retained UVs and object transforms,
all other meshes, shared materials, texture paths, props and placements.

Cutaway exposed pre-existing malformed lean-to foundation corners: two bottom
vertices had never followed shortened post positions and stretched triangles
across the room. Aligned buried vertices 1072/1123 XY to post corners 1070/1121,
retained Z depths and UVs, recalculated affected face normals. No post/prop move.
Both final sources have 1151 mesh vertices / 692 faces. Direct exported building
plus fixed props: 1577 vertices / 930 triangles each. Authoring budget totals
2097 standard and 2149 alternate, including bespoke attachments.

Full `export_assets.py --include-optional` discovery/decode/build/conversion
passed with zero blockers; native readback passed all ten FGX outputs, GEO mesh
counts, positions, triangle indices and UV1/2/3. Preserved 42 attachment placements.
Installed 30 files with matching installation receipt hashes, including AST/FGX/GEO
and XLP merge. Shared CON+PIL remains a reference to the already updated kit model.
No AO bake, texture changes, cook, ArtDef or AssetCloud update. Saved-file validator
ran after edits: pre-existing lighting and independent-pivot support findings stay
warnings under the revision's existing export policy. Geometry/UV/weight/parity and
asset/state checks passed. Texture and solid cutaway previews inspected.

Evidence: Desktop/Codex/CSC_Textile_Workshop_Foundation_20261012.
Use `final-scene-export/job.json` for the installed run; `full-scene-export` is
the superseded uninstalled run before buried-corner repair. Original blend backups
are `*.before.blend`; installed file backups are in final-scene-export/backups.
Reopening backup files elsewhere and saving with default relative remapping changes
texture paths: preserve original relative paths (`relative_remap=False`) when
publishing from those backups. This was corrected before final export.

## 13 October correction — open doorway foundations, all four Level 1 kits

The earlier perimeter repair incorrectly retained the original foundation face
across the entrance and added a second inward-facing face there. Henno explicitly
requested Storage_L-style foundations that follow walls and doorway sides, with
no threshold or foundation spanning the opening.

Updated all four exact Level 1 sources (normal, S, CON+PIL, S_CON+PIL), plus only
the standard revision-11 `CSC_TAILORS_Textile_Workshop_FINAL.blend`. Removed both
cross-doorway faces in previously repaired sources. In the two untouched kits,
removed threshold/ramp/interior floor and the crossing foundation, then added
seven inward-facing wall/doorway-side foundation quads. Repaired two stretched
buried post corners in Level_1_S; one required splitting a vertex shared with the
main wall, retaining that wall's geometry. All unaffected objects, transforms,
material names, image paths and retained UVs verified unchanged. Storage_L and
the alternate workshop were read-only/untouched.

Saved all five actual requested sources and installed five FGX/GEO pairs only.
Workshop export contains Bldg (1155 vertices/696 triangles) and Fixed (414/230),
with both dye vats and loom; zero attachments exported. Native FGX readback checks
passed for positions, triangles and all three UV sets. Existing mesh/group names
preserved. Hash audit confirms Assets/Materials/Textures/XLPs/ArtDefs unchanged,
preserving AE-owned assembly. No full scene export or AST regeneration.

Saved-file workshop validation passes under its existing independent-pivot export
policy (five pre-existing lighting/support warnings). Four legacy kits report only
inapplicable missing Review/Export scenes; static-kit/native checks pass. Inspected
all five cutaway renders and intact views. No cook/in-game check. Evidence/backups:
`Desktop/Codex/CSC_Foundation_Repair_20261013`, authoritative receipt
`export-install-report.json`; `*.final-saved-authoring.json` supersede staging
reports whose relative textures resolved incorrectly from the staging folder.
Do not blindly replay indexed edits against the now-repaired sources.
