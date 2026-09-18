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

## 15 September — everyday Blender scene edits

CSC Scene Tools add-on at `project/tools/blender/csc_scene_tools.py` handles attachment
duplication with new instance IDs, fixed-mesh duplication, export inclusion/exclusion,
and catalogue prop imports at cursor with adjacent portable textures. Placement remains
on attachment Empties; keep transforms unapplied and use uniform positive scale.
The decoder omits render-hidden/CSC-excluded roots and fixed meshes. One authored
single-mesh CSC prop can use vertex-position edits while topology/UV/material layout
stays unchanged, emitting one updated asset definition for every placement in that
batch and reporting that AO was not rebaked. Native pantry assets stay exact; explicit
Quarter master blends must be edited alongside their scenes. Library reconciliation
after CSC scene edits is deliberate, not an automatic shared-drive write.
Blender 5.1.2 headless validation on a workshop copy verified direct add-on methods,
registration/dropdown/duplicate operator and saved scene stage-only export. Three
new native placements plus one fixed clone yielded 43 placements and 10 custom
identities; excluding/removing two yielded 41. A small CSC_ALL_Textile_Bale vertex
edit changed one GEO under the same ID with `ao_rebaked: false`; a native barrel
vertex edit was rejected. The current synced library has `CSC_ALL_Workbench_Narrow`
where the accepted revision11 scenes still use `CSC_ALL_Workbench_Long_Narrow`;
validation used a local historical-master snapshot. Reconcile scene/library IDs
before exporting accepted revision11 against the live catalogue.

## 15 September — Workbench Narrow add-on repair

`CSC_ALL_Workbench_Narrow.blend` contains a single mesh plus an armature rig;
the v1.0.0 importer's name-prefix lookup loaded both and rejected the non-mesh.
Version 1.0.1 prefers catalogue-declared mesh names, discards implicitly appended
orphan rigs after reparenting, and maps Windows `Working Files/3D Art` image paths
to the synced local art tree. Actual Blender add-on import and saved stage-only
export passed on a workshop copy. Installed Blender 5.1 add-on was replaced with
the tested source after backing up v1.0.0 under codex-outputs; a running Blender
session must reload scripts or restart to use the new module.
Reloaded scripts in Henno's open Blender session and used the actual CSC sidebar
import button. Blender reported one-mesh Workbench Narrow import and selected the
new `Attach_CSC_ALL_Workbench_Narrow_01` controller. The live scene was left unsaved
for Henno to position the prop before saving.

## 15 September — non-library asset-master import

CSC Scene Tools v1.1 adds Asset master / Add non-library asset master. One-scene
CSC prop masters can use explicit csc_export prop metadata or a unique armature
whose name is the asset ID. External masters are written as portable metadata
copies at the building revision folder's top level, retaining source geometry and
using the adjacent textures folder; one `Attach_` controller references the ID.
Tailors Sail Cutting Panel import and stage-only export passed on a disposable
revision11 copy. Spinning Wheel (no metadata, armature name = ID) imported and
decoded, but its Current shared AO differs from revision11's atlas: staging was
blocked, then the add-on was tightened to reject the mismatch before import and
verified to leave zero extra scenes, objects or master files. Source masters stay
unchanged.

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

## 14 September — approved reuse naming, revision 09

Henno requires reusable candidates to use CSC_ALL_ asset IDs; likely Quarter-specific
assets use CSC_<QUARTER>_. Before settling future final blends, propose the split
and ask his opinion; this thread's existing split is explicitly approved.
Seven shared workshop props were renamed into CSC_ALL (workbench, seating bench,
bale, folded cloth, canvas roll, teal bolt, rope coil). Sail drying rack and sail
cutting panel now use CSC_TAILORS and their standalone blends accompany revision09.
The latter has five blend inputs; loom/vats remain fixed meshes, no extra assets.
Asset IDs, source mesh identities and placement metadata were changed without
altering geometry, UVs, materials/AO bindings or world placements. Material names
stay unchanged because Windows material reuse bindings already depend on them.
Library changes are additive: auto-review rejected retirement of old synced blends,
so those nine legacy files/records are retained. Seven new CSC_ALL records are added
(49 records), while only 40 pantry/CSC_ALL entries appear on the contact sheets.

## 14 September — revision 10 removes seating-bench redundancy

User explicitly requested removing Seating_Bench and updating its usages. Replaced
Loom_Seat in both workshop variants with CSC_ALL_Workbench_Long_Narrow at uniform
0.5333333 to preserve seat length and root placement; native height becomes ~6.93.
Other placements and source revision09 were preserved. Removed both CSC_ALL and
legacy CSC_Attached seating-bench definitions from active library/catalogue, with
backups outside the synced library; no live AST/XLP/GEO/ArtDef references existed
in the repo. New output: codex-outputs/CSC_TAILORS_Textile_Workshop/revision-10-shared-bench.
Six shared props + two Tailors props + two buildings = 10 unique custom assets.

2026-09-14 current work: revision 11 replaces entrance custom goods with pantry
DIS_COM_Crate + PROP_Barrel_Classical, two props each side per workshop. Migrates
custom AO into shared Sheet01 Tailors Stage2. Henno's explicit ceiling: BOTH
workshop variants together <=1/3 of Tailors quadrant; keep 512² reservation (25%)
where possible. Twelve padded 128² cells occupy18.75%,6.25% spare inside family,
75% reserved for other hero families/storage. Shared props get one self-AO cell
where first allocated, reused across scenes/Quarters. Pantry retains native AO.
Skill1.3.11 records ceiling. Exporter must retain explicit civ_ao_texture even when
civ_material is used; stage stable named AO sources and use AO-only material
variants when necessary, preserving base surfaces. No AO bake during export.

Revision11 completed at codex-outputs/CSC_TAILORS_Textile_Workshop/revision-11-pantry-interiors-shared-ao:
5 blends plus36 textures, no ZIP/tools. Published AO Current/release
2026-09-14_Shared_01_r004 and six CSC_ALL masters to the existing Drive library.
Prior sources retained in entrance-props/ao-work/pre-migration-library and prior
atlas releases; no unrelated assets removed. Contact sheets refreshed:39 reusable
entries,8 CSC_ALL. Final export stage:10 ASTs,11 GEOs (one geometry-only sharedPIL),
40 placements,4 runtime materials,2 AO texture sources,0 blockers. Extra materials
are AO-only variants preserving current surface bindings for the building and
legacy narrow bench. Windows conversion/game still pending. New exporter contract
checks pass;31 unit tests ran,7 optional integrations skipped. Specific current
Blender/CN6/XML integration verified separately in entrance-props/export-final.

2026-09-14 follow-up: user explicitly requested UV1/material/AO migration of
Working Files/3D Art/Props/Tailors/Spinning Wheel/CSC_TAILORS_SpinningWheel.blend and
Props/CSC_ALL_Workbench.blend. Both exact originals now use CSC_ALL_Props_01 with
portable relative paths to CSC_Props/Current; geometry, topology, rig weights,
transforms and UV3 retained. Source backups and portable preview bundles are at
codex-outputs/csc-prop-material-migration. r005 adds AO cells [1024,384,1152,512]
and [1152,384,1280,512];14cells=21.875% Tailors quadrant used,2cells=3.125% still
free in Stage2,75% reserved outside it. Existing12cells/all other pixels and all
surface maps preserved. Current manifest/independent bake sources/release updated.
No new catalogue/asset registration; these are the two exact provided sources,
not replacements for similarly named library entries. Older workshop bundles and
library image snapshots remain unchanged; unify AO snapshots before a mixed batch
export to avoid conflicting images under the same stable texture ID.
Decoder now triangulates n-gons only on its temporary export mesh; source stays
editable. Both sources decode with the shared existing material and explicit AO.

2026-09-14 basket replacement: user requested exact Props/Tailors/CSC_TAILORS_Basket.blend
be replaced by a lower-poly large basket of pale cotton-like raw fibre using shared
prop material. Installed new source with same asset ID, identity transforms, ~28.8×34.2×29
bounds, 169 mesh positions/260 triangles; same decoder measures351 vertices vs506
for old270-position/353-triangle source. CSC_ALL_Props_01, existing sackcloth/rope/canvas
patches, UV1/UV2/UV3 and static Bone. Original backed up in
codex-outputs/csc-tailors-cotton-basket/originals. Shared atlas r006 adds self-AO cell
[1280,384,1408,512]; all prior pixels preserved.15cells=23.4375% Tailors quadrant,
one cell free within25% family block. Exact installed blend reopened/decoder verified;
local portable copy/renders/report/internal CN6 in task folder. No FGX/game update.

2026-09-15 AO/import repair: the synced revision-11 Textile Workshop and
CSC_Prop_Library local `CSC_Props_Shared_01_AO.png` copies explicitly adopted
Current r006. Pixel comparison against the old r004 workshop image found changes
only in the three new 128×128 cells for SpinningWheel, original Workbench and
Basket; prior occupied cells and all other pixels remained identical. Both exact
Tailors SpinningWheel/Basket source masters now use portable relative paths to
`Textures/CSC_Props/Current/textures` for all six shared PNGs. The Blender add-on
1.1.1 has a bounded fallback for previously saved missing CSC production-map
paths, including the Basket's missing `Props/Tailors/textures` path. Headless
imports of both masters into a disposable revision-11 scene passed and retained
matching r006 AO. The user's open unsaved Blender scene was not overwritten;
backups and validation copy are in codex-outputs/csc-ao-basket-fix.

2026-09-15 attachment rename repair: saved revision-11 workshop had
`Rear_Crate_A_01` and `Rear_Crate_A_01_01_01` from repeated duplication, with
their mesh child `instance_id` still `Rear_Crate_A`; `Attach_Loom_Seat` retained
the old Workbench Narrow root ID. CSC Scene Tools 1.2.0 now uses controller names
as placement IDs, synchronizes direct mesh names/IDs and dependent support IDs,
preflights collisions, and chooses unused letters for lettered duplicates. An
explicit rename to an occupied ID is rejected; an Outliner `.001` collision
resolves to the next unused placement name. The sidebar cleanup action maps the
old rear crate duplicates to `Rear_Crate_C` and `Rear_Crate_D` while B remains
occupied. Headless Blender checks on a disposable saved-scene copy exercised
cleanup, repeated lettered/numbered duplicates, raw Outliner rename, collision,
mesh rename and support update. The live unsaved Blender scene was not saved or
overwritten; validation scene is in codex-outputs/csc-attachment-rename.

2026-09-15 Windows placement repair: repaired six mesh-child offsets in the saved
revision-11 `CSC_TAILORS_Textile_Workshop_FINAL.blend` by transferring their world
transforms to Attach_ controllers and resetting child local transforms. All mesh
world vertices were preserved within 0.000016 Blender units. Original backup beside
the blend: `CSC_TAILORS_Textile_Workshop_FINAL.before-controller-repair-20260915-123521.blend.bak`.
CSC Scene Tools 1.2.1 adds Select prop controller (installed and tested in the open
Blender); click a mesh then this button for placement edits. Full folder decode,
build and Windows conversion passed in `%LOCALAPPDATA%/Temp/csc-export-controller-repair-20260915`;
no installation into the mod was performed. CN6ToFGX required sandbox escalation
for its Firaxis Projects registry key; this was not an asset/exporter defect.

2026-09-15 reference-only correction after Asset Editor crash: basket and spinning
wheel already existed in CSC and are used by district bases. Restored their AST,
GEO and FGX from the 12:37 exporter backup. The two copied `.blend` masters were
moved into revision-11 `existing-asset-masters/` (top-level-only discovery now
ignores them). `reuse_existing_assets` in CSC defaults lists both IDs; discovery
requires installed AST/GEO/FGX and XLP registration, and build uses their TileBase
bindings without staging replacements. The 5-blend batch builds 10 custom assets
rather than 12, with 42 placements. The decoder also excluded a basket attachment
child that had leaked into the Workshop's fixed geometry. Rebuilt, converted and
installed from `%LOCALAPPDATA%/Temp/csc-export-workshop-no-duplicate-20260915`;
Asset Editor opening and game behavior remain to be checked.

2026-09-15 Asset Editor crash resolution: coherent pre-export Workshop package opened.
An attachment-only hybrid also opened; new Workshop models plus AO/PIL crashed;
new PIL with old AO opened. The direct R8 texconv AO DDS used alpha pixel-format
flags (`0x20000`) and the exporter wrote 12 AO TEX mips for 2048; the working
Firaxis DDS used luminance (`0x40`) and TEX mip index 11. Exporter now replaces
texconv's AO header with a compatible installed Firaxis AO DDS header (retaining
converted mip pixels) and writes TEX mip index 11/10 for 2048/1024. New package
at `%LOCALAPPDATA%/Temp/csc-export-ae-ao-fix-2-20260915` was converted and
installed; shared AO DDS header matched yesterday's byte-for-byte. Henno reopened
CSC_TAILORS_Textile_Workshop in Asset Editor and confirmed it works fine. This is
AE validation only; no cook or in-game review was done.

2026-09-15 material reuse decision: Henno confirmed the installed Textile Workshop
opens and looks right with existing `CSC_TAILORS_E` for the main building and
`CSC_ALL_Props_01` for the authored props. CSC defaults now use
`material_policy: reuse_existing` and `ao_policy: reuse_existing`; the successful
5-blend export stages no material or texture payload. Blender material custom
property `civ_material` now takes precedence over JSON `material_bindings`, which
remain a fallback for older blend files. An explicit AO map requires switching
to `ao_policy: stage_explicit`; source AO bakes alone do not alter the installed
material. Asset Editor confirmed the installed material-only version opens and
looks fine; cooking and in-game appearance are unverified.

2026-09-15 export uninstall: `export_assets.py --uninstall RUN/job.json` now uses
the install receipt and backup to undo the whole folder run, checking current
installed file hashes before touching anything. Default restores overwritten
files and deletes files created by the run; `--purge` removes all file outputs
and XLP entries authored by that run, even when previous versions existed.
`--dry-run` shows the full plan. Legacy runs without the new receipt derive
expected output hashes from their saved stage and backup. The current successful
Textile Workshop run dry-run reported 32 restorable files in default mode, or
32 deletions and 10 XLP removals with `--purge`. Neither dry-run changed the live
mod; no uninstall was executed.

`export_assets.py --list-purge RUN/job.json` is a read-only shortcut to the purge
preview. It now prints full destination paths and each XLP entry ID, rather than
only an XLP removal count. A file-hash mismatch still blocks the listing so it
cannot imply a purge is ready when installed outputs have changed.

2026-09-15 Rugs import: CSC Scene Tools' Add non-library asset master saved
`CSC_TAILORS_Rugs.blend` at the top level and created its `Attach_` placement, so
discovery treated the master as a prop output. `CSC_TAILORS_Rugs.ast` already
exists and binds native `WON_Great_Zimbabwe_RugsF` geometry; CSC has no local
Rugs GEO/FGX. Discovery now permits explicit reuse of such pantry-backed ASTs
with a valid CSC TileBase XLP entry, while still requiring own GEO/FGX when the
AST names its own identity. Added Rugs to CSC defaults `reuse_existing_assets`.
Real 8-blend discovery classified Rugs as `existing_asset_reference`, with no
Rugs staged output and a representable Rug placement in the Workshop AST.
Workshop 2's Madder fixed vat had malformed Bone weights from 0.3359 to 1.0010;
the matching main Workshop vat had Bone=1 throughout. Backed up the Workshop 2
blend beside its source as `CSC_TAILORS_Textile_Workshop_2_FINAL.before-weight-repair-20260915.blend.bak`,
then set its 76 vat vertices to Bone=1 without changing coordinates. The full
folder passed decode/build (10 assets, 42 placements, 3 existing materials, 0
textures, 0 blockers), converted with SDK registry access, and installed from
`%LOCALAPPDATA%/Temp/csc-export-rugs-reference-converted-20260915-1634` with its
normal backup. Rug AST/GEO/FGX and existing materials were not replaced. Asset
Editor and game appearance remain to be reviewed by Henno.

The pre-repair Workshop 2 vat had a newly named `Armature` modifier targeting the
new building rig and one `Bone` group with varied weights. The source Workshop
vat had a `Building static binding` modifier and `Bone=1` throughout. This is
consistent with using Blender's automatic armature weights while parenting, but
the exact UI action cannot be recovered from the blend. For copied fixed geometry,
use Object (Keep Transform) parenting, retarget the existing Armature modifier,
and confirm all vertices remain in the one Bone group at weight 1. The `Attach_`
Empty's `source_asset_id` only chooses the asset identity; installed CSC reuse is
selected for the batch through `scene_export/csc.defaults.json`.
