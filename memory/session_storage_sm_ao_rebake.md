# Storage S/M AO rebake — 12 October 2026

User requested AO rebakes of Storage S/M intact and CON+PIL sources, overwriting
their existing atlas regions and baking added state-model faces correctly.

Updated all four exact Working Files/3D Art/Storage source blends and canonical
Working Files/3D Art/Textures/CSC_Atlas_AO2.png. Intact UV2 preserved. CON+PIL UV2
had overlaps and collapsed added cut/thickness faces; smart-unwrapped within each
model's original bounding rectangle (no expansion). Geometry, all object/parent
transforms, assignments, weights, UV1 and UV3 hash-preserved. Native scaffold
material/UVs preserved; bake isolates the authored shell without scaffold shadows.

128-sample Cycles emission bake of AO node (distance 30, 128 AO samples), with
2-pixel padding. Compose only rasterized chart footprints plus padding, clipping
against protected other-model charts. Shared PNG comparison: 60,439 changed
pixels; every pixel outside the composed footprints unchanged. Storage L,
L CON+PIL, crane and lean-to mapped texels protected, zero collisions. No AO
overlaps or geometrically significant collapsed charts remain. Tiny authored
slivers can remain subpixel at the existing 1K resolution.

Exact saved-source scene checks and 3-UV CN6 export checks completed. Standalone
scene validator's STATE_GEOMETRY_IN_INTACT finding is inapplicable to separate
CON+PIL files; raw findings retained under inapplicable_intact_findings in reports.
No other scene errors. Material and AO-only views inspected for all models.

Output, backups and evidence:
C:/Users/Shadow/Desktop/Codex/CSC_Storage_SM/ao-rebake-20261012/
Tool: project/tools/art/rebake_storage_sm_ao.py. Script is task-specific and guards
original-source hashes; do not blindly rerun after further user edits.

Source-authoring delivery only: updated R8_UNORM DDS and CN6s are prepared in
the output folder. Production DDS, FGX/GEO and cook untouched. Re-export CON+PIL
geometry together with the new AO DDS before game use, because its UV2 changed.

Follow-up: Henno requested those exports. Converted all four checked CN6s to
3-UV static LandmarkModel FGX/GEO and installed under CSC Geometries, plus the
fresh 1024 R8_UNORM AO2 DDS with full mip chain under Textures. Refreshed the four
CN6s beside their Working Files blends. Native FGX readback matches all source
mesh names, vertex/triangle counts, positions, normals and UV1/UV2/UV3 within
conversion precision. All eight Bakers/Tailors model-instance bindings checked.
Bakers Storage S had five stale intact-mesh group references CSC_Storage_S;
updated only those identifiers to CSC_TAILORS_NE to match the exported GEO.
Existing materials, all state values, attachment transforms and sources preserved.
Static FGX templates have no material names (confirmed on previous native S);
material groups live in GEO and AST, checked independently.

Tool project/tools/art/export_storage_sm_ao.py; production-exports subfolder has
native readbacks, logs, export-install-report.json and before-install backups of
all overwritten files. Source blend hashes unchanged. No cook or in-game test
performed in this export-only follow-up; next normal ModBuddy build consumes it.
# Follow-up: AE crash repaired, 12 October 2026

The DDS installation from this rebake omitted the scene exporter's required AO
header normalization. Raw texconv R8 output on CSC_Atlas_AO2 caused AE's texture
cooker to call a null encoder, crashing assembled assets across Bakers/Tailors.
The full crash dump identified CSC_Atlas_AO2 and internal format 1009. The live
DDS header is now repaired with all rebaked pixels/mips preserved, and
export_storage_sm_ao.py now reuses normalize_ao_dds plus validate_dds before
installation. Henno and the fresh AE log confirm Wind Mill and Tailors Storage L
open successfully. See session_storage_asset_crash.md and the AO compatibility
section of project/docs/art/blender-scene-export.md. Do not reinstall the old raw
DDS from production-exports without applying normalization.
