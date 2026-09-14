# Reusable prop library — 13 September 2026

Initial 33-asset package delivered and reopened successfully at Working Files/
3D Art/Props/CSC_Prop_Library. Durable contract, workflow and limitations:
`project/docs/art/reusable-prop-library.md`.

User's current preservation and reuse contract supersedes older shared-atlas remap,
applied-transform and building-scene-pilot prerequisites. No Asset Editor/game
verification claimed. Source Construction/Pillaged notes are included per asset.

Textile Workshop revision 06 now lives at Play/codex-outputs/CSC_TAILORS_Textile_Workshop/
revision-06-reusable-props/HANDOFF.md. It uses the latest shared-drive normal save
(including Henno's moved loom) and the latest sailmaking save. Both have 19 attachment
placements; custom scene CN6 totals are 1,791 normal / 2,007 sailmaking. Eleven authored
assets were added to the actual shared library, now 44; the previous 33 blends are
unchanged. New entries are verified_blender but pending_windows_asset_creation.
Contact sheets refreshed under Play/codex-outputs/csc-prop-library.

Export roots carry full world/basis/parent-inverse and support-relative matrices.
Keep parent inverses: nonuniform support scale makes naive relative decomposition
lossy. State/terrain integration remains Windows work. Building Review/Export share
objects; pillage Review has explicit projection proxies, Export keeps source cards.
Updated pantry tools preserve authored entries; add_authored_prop_assets.py installs
verified additive batches with collision checks. See durable contact-sheet docs.

Correction from Henno: the loom and dye vats are close enough to share building
height and have little expected reuse. Converted them to CSC_Fixed_ in both blends
without moving geometry. Current: 16 attachment placements each, 7 new shared
asset IDs across the pair, 40 live library assets. The four unregistered standalone
loom/vat variants are archived outside the live library. Building+fixed=1,603 verts;
custom scene totals remain 1,791 / 2,007. Do not equate ground-supported with needing
an attachment, or promote specialised props merely because reuse is conceivable.


## 14 September — composed scene exporter
- Implemented `project/tools/blender/scene_export/`: read-only Blender decode, deterministic static CN6 with transformed fixed geometry/per-corner frames, multi-mesh GEO, template-preserving AST, content-deduplicated materials/textures, exact native BLP attachments, unique XLP merge; explicit Windows convert/install commands with logs/backups.
- Usage and full contract: `project/docs/art/blender-scene-export.md`. `export_workshops.ps1` generates a host-local job from `workshops.example.json`.
- User chose **uniform scale/native proportions** over stretched new asset variants; min XYZ fit. Support contacts repositioned for fit, including sail-panel contact height, without saving changes to blends.
- User explicitly chose **independent Pivot Height and native reused asset state behavior** for this first version; check slope separation and states in game. Do not re-ask these choices for this job.
- Preserve template `CSC_Level_1_S_CON+PIL` + scaffolding and `CSC_Level_1_Decals`; replace primary intact geometry with six meshes; include shared PIL decal GEO once.
- Correct asset count: **9 AST identities (2 building + 7 prop), not 10**; shared PIL is geometry-only. Relative to the already registered normal building, 8 additional identities if all other seven props/sail variant remain new.
- Mac output: `codex-outputs/csc-scene-export/workshop-validation/`; 10 geometries, 32 placements, 3 generated materials plus external ruin-decal material, 13 texture maps. Source hashes and reuse mesh/UV signatures checked. Windows FGX/DDS conversion/cook/game review pending; no active mod asset files changed here.


## 14 September — uniform placement contract supersedes automatic fitting
- User clarified that Blender compositions must obey AE's single scalar scale. The earlier `uniform-min` exporter fitting decision is superseded: no silent resizing/repositioning. Distinct shapes can justify additional reusable assets.
- Current final pair: `codex-outputs/CSC_TAILORS_Textile_Workshop/revision-07-uniform-scale/`. Revision 06 remains historical and contains nonuniform placements; current exporter rejects it.
- Two explicit new definitions: `CSC_Attached_Workbench_Long_Narrow` (30×12×13) and `CSC_Attached_Seating_Bench` (16×6×8.5), placed at scale 1 in both variants. Original workbench unchanged. New sources have one Bone group at weight 1 (clear inherited native bone groups), retain UV1/2 and author neutral unused UV3.
- Crate scales now uniform, preserving height and contact offsets. User requested `WON_Great_Zimbabwe_RugsF` instead of RugsA for the normal workshop's far-right display. It is placed at uniform 0.42 with source pivot preserved and ground contact adjusted; textiles are larger. Sailmaking rack unchanged.
- Independent Pivot Height and native pantry state behavior remain accepted pending game test. Do not promise stacked props share sampled terrain elevation.
- Tool example now has `nonuniform_scale: reject`; remove automatic uniform fitting/support-offset rewriting. Decoded world positions and scales must match saved Blender placement and emitted AE bindings.
- Library has 42 entries after adding two bench variants. Pair uses 11 custom AST identities (2 buildings +9 props), 12 geometries including shared PIL, 32 attachment placements. No new registration for repeated placements or geometry-only PIL.

## 14 September — folder-copy handoff and local Python runner

Henno copies the whole revision folder into Google Drive himself; do not make ZIP
handoff packages by default or connect from Mac to Windows. Run `project/tools/blender/export_assets.py` from the repo, with its adjacent
`scene_export/` helpers. Pass the copied revision folder as `--blend-directory`;
do not include duplicate exporter files in the revision folder.
The Windows agent runs locally and inspects retained logs/report. Every run decodes
the saved blends anew into a fresh output directory; installation remains explicit.
Henno can edit `Attach_…` controllers in Object Mode: move, Z-rotate, positive uniform
scale, save without applying transforms. Preserve mesh children, source IDs and UVs.

## 14 September — filename-independent discovery

`project/tools/blender/export_assets.py` now scans top-level `.blend` files instead
of loading the workshop filename preset. `csc_export` JSON scene metadata defines
kind/identity/template/decals; existing building roles/IDs and unambiguous AST mesh
matches also work. Unknown/duplicate/ambiguous files block with discovery-report.json.
Buildings resolve their own templates and preserve auxiliary state geometry. Local
authored prop definitions are shared once per batch; native assets remain references.
The current synced normal workshop was discovered successfully but decoding found
`Drying_Display` mesh-child transform offset. Do not silently change Henno's placement.

## 14 September — revision 08 repairs and minimal art handoff

Fixed the normal RugsF display and sailmaking seating-bench mesh-child offsets by
moving their transforms onto attachment controllers. All mesh world matrices, local
geometry and UVs were preserved within float tolerance; transforms were not baked
into vertices. Original user-edited revision07 on Drive remains unchanged.
The corrected delivery is `codex-outputs/CSC_TAILORS_Textile_Workshop/revision-08-export-ready/`:
three final blends plus `textures/` (31 files), no tools/logs/ZIPs. Explicit csc_export
metadata is embedded in each Export scene, texture paths are portable, and fresh
discovery/decode/staging succeeded with zero blockers (11 assets, 12 GEOs, 32 placements).
Use the existing synced CSC_Prop_Library separately. Windows conversion/game checks
remain pending. Repair records and validation are outside the minimal art folder.
