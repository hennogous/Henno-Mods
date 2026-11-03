# Tailors basket replacement — 26 October 2026

`CSC_TAILORS_Basket` now uses the newer authored basket from
`Working Files/3D Art/TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao/CSC_TAILORS_Basket.blend`.
The active editable master is `Working Files/3D Art/Props/Tailors/CSC_TAILORS_Basket.blend`,
with portable texture snapshots and CN6/FGX/GEO exports alongside it.
The historical authored source remains unchanged.

The new model has 169 authoring vertices, 351 exported vertices and 260 triangles;
the superseded native model had 506 vertices and 353 triangles. Existing basket AST
identity, district attachment placements and all state flags are preserved. Only
its mesh/group bindings change to match the new model.

Shared prop atlas release `2026-10-26_Shared_01_r046` reclaims surface slot 41 and
the duplicate AO cell `[1408,384,1536,512]` introduced by the legacy migration.
The newer basket uses existing shared surfaces and its original AO allocation
`[1280,384,1408,512]`. Other surface/AO pixels, well tint, shared emissive textures,
XLP entries and materials remain unchanged. Current, Releases, manifests, masters,
source patches and the overlay rebuild recipe agree on the reclaimed cells.

The older canonical master, backup, exports and texture snapshots are archived at
`C:/Users/Shadow/Desktop/Archive/CSC-older-tailors-basket-20261026/sources-before/Props/Tailors`.
Earlier `CSC_ALL_Basket` source/paint files were moved from `Props/_archive` into
the corresponding archive subfolder. Original runtime files and the previous
complete shared atlas are included, with a hash manifest and restoration notes.

Validation: saved-file authoring checks passed; installed master exports exactly
match the staged source; native readback confirms one bone binding and source
parity; visual preview inspected; 537 unaffected runtime files are byte-identical.
Both isolated native Tilebases cooks passed, with package size falling from
5,310,464 to 5,305,344 bytes. No live AE/in-game review was performed. The existing
unrelated missing `CSC_BAKERS_Well` material reference remains.

Evidence: `C:/Users/Shadow/Desktop/Codex/Tailors-newer-basket-20261026`.
Preparation/publication tools: `project/tools/art/use_newer_tailors_basket.py`
and its `_blender.py` companion. These are guarded one-time migration tools;
do not replay their preparation/publication phases against the published release.
