# Tailor wall clothing rack — 13 October 2026

User requested the wall-side rack plus its three hanging garments from
`Working Files/3D Art/TAILORS/Tailor/revision-10-vertex-budget/CSC_TAILORS_Tailor_2.blend`
as one installed asset. Installed `CSC_TAILORS_Tailor_Garment_Rack` AST/GEO/FGX,
one CSC_Tilebases XLP entry and AssetCloud records. One mesh, 312 exported
vertices / 268 triangles; shared `CSC_ALL_Props_01`. Worked/Unworked visible;
Construction/Pillaged/Unbuilt hidden; PERMANENT culling.

Extracted all 25 components under `Place_Wall_Garment_Rack`. Editable components
retain transforms and UVs in a standalone master. Ground pivot is the source
controller XY plus minimum geometry Z; original facing retained. Source blend
hash unchanged; all 127 pre-existing ASTs preserved. Saved-file authoring check
passes. Native FGX roundtrip agrees within 0.00000489 for positions/UVs/normals;
triangles exact. Render inspected. AE was closed; dependency registration merged
with backup. No cook or in-game check.

Editable blend, preview, CN6, native readback, reports and backups:
`C:/Users/Shadow/Desktop/Codex/Tailor-wall-garment-rack-20261013/`.
Repeatable source tooling: `project/tools/art/extract_tailor_garment_rack.py`
and `install_tailor_garment_rack.py`. Current source assemblies still contain
their original rack geometry; this request only added the standalone asset for
Henno's AE placement.

## Moved master and black garment follow-up

Authoritative master is now
`C:/Users/Shadow/Desktop/Working Files/3D Art/Props/Tailors/CSC_TAILORS_Tailor_Garment_Rack.blend`.
Henno remapped all leftmost-garment UV1 components to the new r023 coach black
leather block (atlas slot 6). The saved UV edits were correct, but installed FGX
still dated from extraction, and the shader nodes used the extraction's older
atlas snapshot. UV editor had the new atlas separately loaded.

Updated this moved master's shader images to canonical Current, repaired missing
static Bone weights, and re-exported/installed only rack FGX/GEO. Preserved saved
mesh coordinates, component transforms and all UV sets exactly. ASTs, materials,
runtime textures, XLPs and ArtDefs unchanged. Runtime base-color and normal DDS
pixels match Current exactly. Saved-file validation passes; native readback error
below 0.000005; 312 vertices/268 triangles. Black garment render inspected.
Backup of Henno's input and evidence: prior output folder's `black-r023/`.
Tool: `project/tools/art/update_tailor_garment_rack.py`. Reopen asset in AE to
reload geometry; no AE visual check or cook performed in this follow-up.
