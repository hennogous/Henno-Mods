# Blender scene decoder and asset exporter

Use `project/tools/blender/export_assets.py` for the reusable-prop workflow. It replaces
`csc_export_pipeline.ps1` for composed building scenes. The older script exports
whole scenes, handles multi-mesh GEO metadata incorrectly, and does not decode
attachment identities or transforms.

The tool reads saved Blender files without saving or applying transforms to them.
It stages CN6, GEO, AST, materials, texture descriptors/sources and an idempotent
XLP merge. Windows then converts CN6 to FGX (and PNG to DDS when explicitly using
material generation), and the normal run installs the converted files into the
mod with destination checks, backups and rollback on errors.

## Contracted building exports (September 2026)

The normal CSC defaults now set `strict_contracts: true`. Every exported building's
`Export` scene needs explicit `csc_export` metadata identifying its Quarter and
supply-chain stage. This is a preflight gate: missing metadata or a required shared
material/geometry stops discovery before conversion or installation. Example:

```json
{"kind":"building","asset_id":"CSC_TAILORS_Textile_Workshop","quarter":"TAILORS","supply_chain_stage":3}
```

These three contract fields can instead live in the blend folder's
`export-contract.json`, keeping an existing blend unchanged. The runner loads that
file automatically when present; `--contract PATH` selects a different file.
Declarations must match discovered building IDs and cannot conflict with Blender
metadata. For example:

```json
{"buildings":{"CSC_TAILORS_Textile_Workshop":{"quarter":"TAILORS","supply_chain_stage":3}}}
```

The run records the sidecar's path and hash in `contract-source.json`; the resolved
per-building contract is also in `job.json` and `discovery-report.json`.

An export contract may list expanded-model files in `optional_blends` and their
building IDs in `optional_buildings`. The normal runner skips those blends even
when they share the source folder with the standard model. Pass
`--include-optional` to export the complete optional group; the run then requires
every listed optional blend. Keep the standard files in `required_blends`. For
example, `project/art-export-contracts/tailor-revision09.json` exports the normal
Tailor by default and includes `Tailor_2` only on request. The optional flag
exports the standard files as well, so review the output and destination before
installing an expanded-model run.

The supply-chain stage maps to a building level: Stage 2 → Level 1, Stage 3 → Level 2,
Stage 4 → Level 3. Stage 2 additionally needs `construction_geometry` set to either
`CSC_Level_1_CON+PIL` or `CSC_Level_1_S_CON+PIL`. Stages 3 and 4 use
`CSC_Level_2_CON+PIL` and `CSC_Level_3_CON+PIL` respectively by default. A
contract may instead name an authored `construction_geometry` and map its
`shared_geometries` ID to a blend in the same folder. The exporter then creates
one GEO/FGX pair and binds it into both building variants. `required_blends`
can list the complete folder inventory; any missing, extra, ignored, or unused
building, prop master, shared ruin, or PIL decal blocks the run. The stages require
`CSC_ALL_Stage_3_Cobble_Decals` or `CSC_ALL_Stage_4_Cobble_Decals` in the mod's
Geometries directory. Existing shared GEO/FGX files are referenced unchanged.

The contract applies `CSC_<QUARTER>_E` to the building and lean-to, and
`CSC_ALL_Props_01` to fixed prop meshes in Bakers, Tailors, Apothecaries and
Stonemasons. Carpenters, Blacksmiths, Goldsmiths and Brewers use
`CSC_ALL_Props_02`. It applies `CSC_<QUARTER>_NE` to the shared construction/pillage
building groups, retains `Pillage_Construction_01` for scaffolding, and applies
`CSC_ALL_Cobble_Patch_Decal` to the stage 3/4 cobble model. Existing MTL and texture
files are reused without modification. Missing files block only a run that needs
them, so Stage 4 can wait until its shared assets are authored.

Main building and fixed prop groups are visible in Worked only. The shared ruin
building is visible in Construction and Pillaged; scaffolding is Construction only.
Cobble is visible in Worked and Construction. Unworked and Unbuilt are invisible.
Newly exported CSC prop assets are Worked only. Already installed CSC attachment
assets keep their own state tables; the validation report lists their IDs for
Henno's manual check. Pantry attachments keep their own materials and states.

After staging, the builder validates every generated group/state/material row
against the GEO, plus attachment identities and numeric transforms. It records
`contract_validation` in `report.json`. Run the same read-only check independently:

```powershell
python project/tools/blender/scene_export/asset_contract.py 'C:\path\to\export-runs\<timestamp>\job.json'
```

AE orientation uses radians. The exporter serializes Blender X/Y Euler angles in
the same direction and reverses Z; combined-axis visual parity needs an AE review
with a known reference before treating it as calibrated. Henno owns in-game
testing. XML, FGX presence, and conversion checks establish the asset package,
not its final appearance or runtime behavior.

Each rerun uses a fresh timestamped run and installs over the previous matching
outputs. When the previous installed run came from the same `export-runs` folder,
installation also retires outputs and XLP IDs that disappeared from the new run,
after checking their recorded hashes. The new run backs them up. A normal uninstall
restores its predecessor; a purge removes the latest run's outputs. To address the
newest installed run by its blend folder:

```powershell
python project/tools/blender/export_assets.py --list-latest-purge 'C:\path\to\blend-folder'
python project/tools/blender/export_assets.py --purge-latest 'C:\path\to\blend-folder'
```

The preview lists exact targets. Use `--force` only when deliberately purging
outputs subsequently changed or removed in AE. These commands do not remove
ArtDef wiring, cooked packages, or the AE dependency cache.

Installed custom props are safe to rerun from the same source bundle. Discovery
recognizes an output only when a prior install receipt names that exact blend and
the live AST still matches the receipt; unrelated or subsequently edited ID
collisions remain blocked.

## Windows: export a folder of Blender assets

Prerequisites: Python 3.10+, Blender (tested decoding with 5.1.2), the repository's
`project/tools/cn6libs/` folder and Microsoft DirectXTex `texconv.exe`. Python uses
only its standard library: PyYAML is not required by this exporter.

The runner uses `project/tools/directxtex/texconv.exe` by default when present,
then searches PATH. See [the pinned download and checksum](../../tools/directxtex/README.md).
`--texconv` overrides that selection. Shadow's old CivNexus6 copy fails to start;
the current standalone Microsoft release is used by the command cheatsheet.

Henno copies the complete revision folder into Google Drive himself and runs the
export locally on Windows, either directly or through the Windows agent. Do not
create a separate ZIP or attempt to connect from the Mac to Windows.

The exporter lives in the repository: `project/tools/blender/export_assets.py`, with
its helpers in `project/tools/blender/scene_export/`. Keep tools in the repo; the
revision folder holds the blends, textures and supporting art files. Referenced
library props must be present in the synced catalogue; explicitly declared custom
prop definitions in the input folder can also be exported and shared in that batch.
For already installed CSC assets, list their IDs under `reuse_existing_assets` in
the exporter defaults. Their `Attach_` placements still export, while their AST
and geometry remain untouched. The installed AST and CSC TileBase XLP entry must
exist. If the AST refers to its own GEO identity, its local GEO and FGX must also
exist. An asset such as `CSC_TAILORS_Rugs`, whose AST refers to pantry geometry
`WON_Great_Zimbabwe_RugsF`, needs no CSC-local Rugs GEO/FGX. Their master blends
are optional for this export; keep copies in a subfolder if useful, since
discovery scans only top-level `.blend` files. **Add non-library asset master** in
CSC Scene Tools imports and saves a top-level prop source; it does not by itself
declare that a same-ID installed asset should be reused. Put that ID in
`reuse_existing_assets` when its existing AST should supply the game geometry.
The attachment Empty's `source_asset_id` identifies the asset; it does not choose
whether the exporter references or replaces its files. For a previously installed
CSC prop, inspect that ID on the `Attach_` Empty, then add the exact ID to
`scene_export/csc.defaults.json` under `reuse_existing_assets`. This applies to
the whole folder export, regardless of how many placements use the prop. Use
`replace_existing_assets` instead only when the master is intentionally an updated
definition to install under the same ID. An asset in the synced prop catalogue
should be placed with **Add library prop**.
An explicitly authored prop update to an installed CSC identity must be listed in
`replace_existing_assets`; otherwise discovery blocks the replacement. This keeps
reference-only assets such as the Textile Workshop's basket and spinning wheel from
being overwritten by copied masters.

The Windows AO conversion uses the installed Firaxis 8-bit luminance DDS header
with texconv's mip pixels. For AO TEX files, `m_NumMipMaps` is the highest mip
index (2048 → 11; 1024 → 10), while the DDS header counts all levels (12 and 11).
On 15 September 2026, texconv's direct R8 output marked the channel as alpha and
the exporter wrote 12 into the 2048 AO TEX; Asset Editor crashed opening the
Textile Workshop. The corrected package opened and displayed in Asset Editor.

From the Henno-Mods repository root, run with the copied revision folder as input:

```powershell
python project/tools/blender/export_assets.py --blend-directory 'C:\path\to\revision-07-uniform-scale' --mod-root 'C:\path\to\Henno Mods\Civ Supply Chains' --library 'C:\path\to\CSC_Prop_Library' --blender 'C:\path\to\blender.exe' --texconv 'C:\path\to\texconv.exe'
```

`--converter` can override the default repository `project/tools/cn6libs/CN6ToFGX.exe`.
Keep the converter's existing DLLs alongside it. `--stage-only` skips FGX/DDS
conversion. Python itself needs no additional packages; Blender and the Windows
conversion tools remain separate prerequisites.

Every export discovers all top-level `.blend` files, rereads their saved scenes,
then builds and converts into a fresh
`export-runs/<timestamp>/` directory. `--output` selects another new directory.
`discovery-report.json` lists every discovered file and any classification/template
blockers. Reports and streamed logs are retained there; failures stop the run. Previous Mac
`export-job.json` and `export-validation/` files are evidence, not Windows inputs.
The script generates Windows-local paths and never edits the source blends.
If a transferred blend retains a missing absolute image path from another host,
the decoder may resolve the exact image basename from that blend folder's own
`textures/` directory. It reports the relocation in `decode.log` and leaves the
blend unchanged; it does not search unrelated folders or accept a missing bundle
texture.

Normal export now installs automatically: FGX/GEO files go to `Geometries`, AST
files to `Assets`, and asset entries are merged into `XLPs/CSC_Tilebases.xlp`.
Source blends remain unchanged. Backups and reports remain in the timestamped run.
Use `--no-install` for a converted preview, or `--stage-only` to stop before both
conversion and installation. A conversion failure never triggers installation.

To install a previously converted `--no-install` run, use:

```powershell
python project/tools/blender/export_assets.py --install 'C:\path\to\revision-07-uniform-scale\export-runs\<timestamp>\job.json'
```

To uninstall every asset produced by one folder export, pass that run's `job.json`:

```powershell
py project/tools/blender/export_assets.py --list-purge 'C:\path\to\revision\export-runs\<timestamp>\job.json'
py project/tools/blender/export_assets.py --uninstall 'C:\path\to\revision\export-runs\<timestamp>\job.json' --purge --dry-run
py project/tools/blender/export_assets.py --uninstall 'C:\path\to\revision\export-runs\<timestamp>\job.json' --purge
py project/tools/blender/export_assets.py --uninstall 'C:\path\to\revision\export-runs\<timestamp>\job.json' --purge --force
```

`--list-purge` is a read-only shortcut for the purge preview. It lists the full
path of every file and each XLP entry ID that would be removed. `--purge` deletes this
run's AST/FGX/GEO and any material/texture files it actually installed, including
files that replaced earlier versions. It keeps an exact copy of the live files in
the run's `backups/uninstall-<timestamp>/` before deletion. Omit `--purge` to undo
just this installation: newly created files are deleted and overwritten files are
restored from the pre-install backup. Both modes preserve source `.blend` files,
unrelated XLP entries, existing materials reused by the run, and assets named in
`reuse_existing_assets`. If any installed output was modified or replaced by a
later export, uninstall stops without changing the mod. When the explicit intent
is to remove every output owned by the run, `--purge --force` accepts changed or
already-missing outputs. This is useful after Asset Editor reserializes an AST.
Force purge still validates recorded paths, preserves unrelated XLP entries, and
backs up every surviving live target before deleting it. Use `--list-purge ...
--force` for a read-only preview. The command affects one
timestamped export run; outputs installed by other runs require their own jobs.
ArtDefs, cooked packages and Asset Editor's dependency cache are outside the
exporter's installation record and are not changed by uninstall.

The modular `export_scene.py` commands and older workshop-specific PowerShell
wrapper remain available for development, but the repository Python entry point is the normal
workflow. `--blend-directory` is required for export; helpers resolve relative to
the script, regardless of the shell working directory.

Installation copies the generated assets/geometries/materials/textures and their
PNG sources, rewrites TEX source paths to the installed sources, and merges new
identities into the **current** XLP. It preserves unrelated registrations. Existing
destinations must still match their staging baseline. Exact replaced files and a
list of newly created files are kept under `backups/` in the output directory.

Refresh/rebuild Asset Editor's dependency browser after adding assets outside AE.
The exporter does not delete the AssetCloud cache, modify ArtDefs or run a cook.
Existing Textile Workshop ArtDef wiring remains; connecting the Sailmaking variant
to gameplay is separate from producing its asset. ModBuddy already includes the
CSC TileBase XLP; source AST/GEO/MTL/TEX dependencies are resolved through that XLP.

## Discovery and scene metadata

### Existing material reuse

The normal CSC defaults use `material_policy: "reuse_existing"`. The exporter
first reads a Blender material's `civ_material` custom property, then falls back
to `material_bindings` in `scene_export/csc.defaults.json`, then to an exact match
with an existing project MTL name. To author the binding in Blender, select a
mesh, open Material Properties, select its material, and add a string Custom
Property named `civ_material` with the existing Civ material ID as its value
(for example, `CSC_TAILORS_E` or `CSC_ALL_Props_01`). Save the blend file.
The exporter checks that a referenced CSC `.mtl` exists in the mod project.
No atlas/Quarter inference is used. Unbound materials block the run with a message
requesting an explicit binding, rather than generating hash-named MTLs/textures.

Current Textile Workshop bindings:

| Source | Existing material |
|---|---|
| Main building | `CSC_TAILORS_E` |
| Fixed textile geometry, loom/vats, textile/sail/rope props | `CSC_ALL_Props_01` |
| Custom CSC bench/workbench | `CSC_ALL_Props_01`; never select compatibility-only `CSC_ALL_Props` for new exports |
| Pillage decals | `Ruin_Debris_Decal` |

Reused asset instances keep the material bindings already declared by their own
installed ASTs; the scene exporter must not remap them to a Quarter or CSC atlas.
The table above applies only to geometry authored or merged into this export.
These bindings reuse existing materials and their textures unchanged. Blender
can make the material choice per authored material; the JSON mappings supply
defaults for older blend files without that property. The blend's
separate AO bakes and revised texture images are not exported in this mode;
appearance follows the existing MTL definitions. Each report records the effective
material mapping. Additional source materials need their own explicit mapping.
Development jobs without `reuse_existing` retain the older unbound-material
generation path; the normal CSC command does not use it.

### Scene identity

The template examples below describe legacy source metadata and template
selection. With normal strict defaults, also supply the contracted Quarter,
stage, and (for Stage 2) construction geometry, either in Blender or the sidecar.
The builder replaces the contracted shared construction/cobble models using their
declared geometry identities and validates their exact state tables.

The normal entry point no longer uses `workshops.example.json`. Filenames are
arbitrary: identity comes from the saved scene, so renaming a blend does not rename
its game asset. Scan is nonrecursive to avoid exporting library backups and working
revisions in subfolders. `.blend1` backups are excluded; `.BLEND` is accepted.
Duplicate identities (including case differences) block the batch. Unknown or
ambiguous files also block it rather than disappearing from the output.

New scenes should carry a `csc_export` custom property on their Export scene,
containing a JSON string. One explicitly marked scene is selected; otherwise the
named `Export` scene is used (a sole scene is also eligible). Minimal examples:

```json
{"kind": "prop", "asset_id": "CSC_ALL_New_Bench"}
```

```json
{"kind": "decal", "geometry_id": "CSC_New_Building_PIL_Decals"}
```

A new building uses the exporter's bundled TileBase template. It does not need an
existing output AST or a matching mesh in another building. For the small Level 1
kit, select the profile that includes its shared construction/pillage and base
decal models:

```json
{
  "kind": "building",
  "asset_id": "CSC_TAILORS_New_Building",
  "quarter": "TAILORS",
  "supply_chain_stage": 2,
  "construction_geometry": "CSC_Level_1_S_CON+PIL",
  "template_profile": "level1_small",
  "decals": ["CSC_New_Building_PIL_Decals"]
}
```

Profiles ship in `project/tools/blender/scene_export/templates/`, outside generated
mod content. `tilebase` (the default) is a bare TileBase shell with the main model's
five state settings; it has no construction/pillage auxiliary models or base
decals. `level1_small` adds `CSC_Level_1_S_CON+PIL` and `CSC_Level_1_Decals`, retaining
their state tables and referencing their existing shared geometry. Choose this
profile only for that kit; other kits need their own profile or explicit template.
Neither profile contains Workshop geometry, props or material bindings.

The existing revision-08 metadata referencing
`Assets/CSC_TAILORS_Textile_Workshop.ast` maps explicitly to `level1_small`, even
when that old output is absent. Legacy main-model selectors are replaced with
the bundled template's placeholders; scene decal and preservation requirements
remain in effect. Both normal and Sailmaking blends work without resaving them.
Discovery reports record the selected profile and actual template path.

For bespoke behavior, a building can instead specify an existing input template
and relevant model selectors explicitly (do not also specify `template_profile`):

```json
{
  "kind": "building",
  "asset_id": "CSC_TAILORS_New_Building",
  "quarter": "TAILORS",
  "supply_chain_stage": 2,
  "construction_geometry": "CSC_Level_1_S_CON+PIL",
  "template_asset": "Assets/CSC_Existing_Building.ast",
  "replace_model": "CSC_Existing_Building",
  "state_template_mesh": "CSC_Existing_Building_Bldg",
  "decals": ["CSC_New_Building_PIL_Decals"]
}
```

The template supplies construction, pillage and base decal behavior; other model
instances are preserved. The selected intact model is replaced with the scene's
building/fixed geometry. Listed decal IDs refer to discovered decal blends and are
emitted once as geometry, without a separate asset/XLP entry. `decals: []` explicitly
keeps the template's existing decal geometry. New declared decal IDs add model
instances; existing matching GEO IDs are replaced.

Scene attachment roots replace template attachment points owned by the selected
main model. Points owned by other models remain. Advanced metadata can override
`replace_owned_attachments` (boolean), `replace_attachment_assets` (asset ID list)
and `preserve_models` (required model names). Keep these selectors explicit when
a template has behavior that is not fully represented by the composition.

For existing scenes, discovery can infer a building from meshes marked
`building_geometry` and their unique `source_asset_id`. Without an explicit input
template, discovery uses the bundled profile, never the output AST or a scan of
unrelated assets. Explicit custom templates must exist and identify a unique
model; unknown missing paths remain errors. Existing `Shared PIL export` scenes
use their sole armature identity as the decal ID. Building/decal links can come
from template GEO IDs, with the legacy `PIL_geometry` path as a fallback. Existing
library prop scenes can be recognized by a unique catalogued armature identity.
No arbitrary filename suffix is used to invent an asset ID or state role.

Use `{"kind": "ignore"}` to explicitly exclude a scene; it remains listed in the
report. Treat an ignored intact building as a hard integration boundary: a run that
only exports its decals has not replaced the building shown in Asset Editor. Before
installing a final handoff, confirm every intended intact variant resolves as
`kind: building` in `discovery-report.json`. Existing pantry assets are reference-only: attach them from the library,
rather than exporting their source blends as new assets. Authored prop definitions
in the folder can be standalone or shared across buildings; geometry/UV matching
still verifies that placements reference those definitions verbatim.

Common CSC geometry/material/texture/prop templates and policies are stored in
`scene_export/csc.defaults.json`; `--defaults` selects another defaults file. Building
templates are resolved per file, so one run can contain different building types.

Verified on Shadow on 14 September 2026 with the revision-08 Workshop handoff:
both buildings discover and build while the old Workshop AST/GEO/FGX outputs are
absent. The integration suite checks shared state preservation, 32 placements,
geometry metadata, staged XLP entries and isolated installation/backup behavior.
The full run also passed Windows conversion (11 assets, 12 FGX geometries and 13
DDS textures), converted-file hash checks and DDS dimensions/mipmap validation.
Source blend hashes were unchanged. Asset Editor/cook/in-game review remains a
separate step; the test run did not install into the live mod.
The defaults contain no building filenames or building identity preset. Discovery
and decode verify source hashes and never save or apply transforms to the blends.

## General jobs

Copy `workshops.example.json`, change the input files, identities and template
selectors, then run:

```powershell
python project/tools/blender/scene_export/export_scene.py decode job.json --blender 'C:\path\to\blender.exe'
python project/tools/blender/scene_export/export_scene.py build job.json
python project/tools/blender/scene_export/export_scene.py convert job.json --converter 'C:\path\to\CN6ToFGX.exe' --texconv 'C:\path\to\texconv.exe'
```

Paths in a job resolve relative to the job file. `build` may rerun in an untouched
staging directory. If its files were edited or converted, use a fresh output
directory; it refuses to erase those changes. A failed build can leave a partial
stage without a manifest; use a fresh directory for that case too.

### Geometry and state selection

| Input | Output treatment |
|---|---|
| `building_geometry`, `fixed_geometry`, or `CSC_Fixed_` mesh | Included in the primary building GEO/CN6 with its world placement serialized into a temporary vertex stream. Compatible fixed pieces are merged in that temporary stream by material/state to keep CivNexus6 stable; the editable Blender objects remain separate. No separate prop asset. |
| Attachment EMPTY with `instance_id`, `source_asset_id`, `support` | Placement from its world matrix. Direct mesh children retain the standalone asset's exact asset-local transforms, including deliberate multi-mesh or off-origin assemblies. Native meshes and local transforms match their library source exactly; a controlled single-mesh CSC vertex edit can define one updated asset for the whole batch without changing its local transform. |
| Reused catalogue asset | Exact existing BLP binding copied from `CSC_ALL_Prop_Library.ast`; no duplicate geometry/material/XLP registration. |
| Catalogue `origin: authored_blender` | One new prop asset/GEO per exact identity, shared across all buildings in the job. |
| Explicit decal input | DecalGeometry referenced as a model instance; **no standalone AST/XLP registration**. |
| Other existing model instances | Preserved from the template. Required auxiliary names can be asserted with `preserve_models`. |
| Review objects, unclassified meshes, invalid weights/UVs, unsupported modifiers/animation | Rejected. Only the selected `Export` scene is decoded. A single-scene library prop is also supported. |

The template's selected main mesh supplies the five state parameter sets, including
FOW/burn/snow settings. Generated base and fixed geometry is visible Worked,
Unworked and Unbuilt. New standalone props are visible Worked/Unworked and hidden
Pillaged/Construction/Unbuilt. Decal inputs are visible Pillaged only. Arbitrary
animation, per-placement state overrides and new construction mesh authoring are
outside this static exporter; existing construction models are preserved.

For the Textile Workshop specifically, both asset definitions contain:

- New intact building plus five fixed meshes, including loom and both dye vats.
- Existing `CSC_Level_1_S_CON+PIL`, unchanged: ruin geometry in Construction and
  Pillaged, scaffolding only in Construction, existing burn/material bindings.
- `CSC_TAILORS_Textile_Workshop_PIL_Decals` **once**, with all eleven mesh groups
  including the four base groups. Preserve original projection geometry, including
  elevated/slanted cards; exclude Review's planar preview proxies.
- Existing `CSC_Level_1_Decals`, unchanged, including its visibility in all five states.

Only the explicitly listed old attachment asset references are removed; unrelated
attachment points and behavior data in the building template remain.

### Editing a delivered scene

In the Outliner, select the `Attach_<instance>` Empty, in Object Mode. Move it
(`G`), rotate about Z (`R`, `Z`), or scale uniformly (`S`, without an axis). Keep
positive equal scale components; do not apply transforms. Save the blend and rerun
`export_assets.py` so the new placements are decoded. Review and Export share
the same asset objects, so either scene can be used for these edits.

The mesh child must remain at identity relative to its controller. X/Y tilting,
mirroring and axis-specific scaling are rejected. To change proportions, author a
distinct library asset and place it with uniform scale.

For everyday editing, install `project/tools/blender/csc_scene_tools.py` in Blender
via Preferences → Add-ons → Install from Disk. Its **CSC** tab in the 3D View
sidebar works on the saved building scene; Review and Export share the asset
objects. For placement edits, click a prop mesh, then **Select prop controller**
(CSC Scene Tools 1.2.1) before moving, Z rotating or uniformly scaling it. This
selects its `Attach_` Empty; moving a mesh child in Object Mode creates an offset
that the exporter rejects. Edit Mode is for deliberate geometry edits, subject to
the CSC/pantry rules below.

Select an attachment Empty or its child and click **Duplicate selected
prop**. The tool creates a new controller with a unique `instance_id`, preserves
source/support/state metadata, and shares the source mesh datablock with the
existing placement. Move the selected new Empty and save without applying
transforms. Duplication adds a placement, not another asset or AO allocation.

Attachment placement names are the `Attach_<instance_id>` controller names; the
controller's custom `instance_id`, direct mesh children's names and `instance_id`s,
and any dependent attachment `support` references must agree. With CSC Scene Tools
1.2.0, rename a controller in the Outliner or use **Rename selected prop** in the
CSC sidebar; the add-on synchronizes these fields. The mesh child follows its
controller name, so rename the controller rather than its generated mesh name.
The rename dialog rejects an ID already in use. If Blender produces a `.001`
suffix after an Outliner name collision, the add-on selects the next available
placement name instead of storing `.001` as an export ID. Lettered placements
such as `Rear_Crate_A` duplicate to the next unused letter; numbered asset
placements advance `_01`, `_02`, `_03` without accumulating numeric tails.
**Clean up attachment names** migrates older tool-generated lettered duplicates
and repairs stale mesh IDs in the open scene. Save the scene after reviewing its
renamed controllers. Mesh geometry and placement transforms are unchanged.

**Include / exclude from export** sets render visibility and a CSC exclusion flag
on a selected attachment and its mesh children, or on a fixed mesh. The exporter
also respects Blender's `Hide in Renders` on an attachment root or fixed mesh. An
excluded attachment contributes no Asset Editor point; an excluded fixed mesh
contributes no building GEO mesh. Keep at least one intact building mesh visible.
Blender viewport hiding alone does not mean exclusion.

**Remove selected prop** deletes an attachment root with its direct meshes from
both scenes, or a fixed mesh. It refuses removal if another attachment uses that
root as support or it has non-mesh children. Blender Undo reverses the operation.

To add a prop, set **Library** to the synced `CSC_Prop_Library` folder, choose an
asset ID and click **Add library prop at cursor**. The tool imports the visible
mesh components and copies required textures to the saved blend's adjacent
`textures/` folder. It creates a new `Attach_` controller at the 3D cursor with
`support: ground`; move, Z-rotate or scale that controller uniformly. The imported
mesh retains its library-local geometry, UVs and pivot. Duplicate it with the
same button. A prop with an unusual support/state relationship may need an
intentional follow-up edit to the controller metadata.
Rigged static library masters import their declared mesh components; the add-on
removes the preview rig after rebinding the mesh to its attachment controller.
For CSC masters saved on Windows, texture paths inside the synced `Working Files/3D Art`
tree resolve to the matching local files before they are copied beside the scene.

Fixed `CSC_Fixed_` meshes can be moved, Z-rotated, uniformly scaled, duplicated
with the button, or have their vertices adjusted in Edit Mode. Each fixed
duplicate is a new building GEO mesh and receives no new asset ID. Existing AO
UVs stay in place; review whether the edited shape still suits its baked AO.

For an authored, **single-mesh CSC library prop**, adjusting only vertex
positions in the scene is supported without an automatic AO rebake. The exporter
checks that topology, all UV layers and material assignments still match the
library master. One edited geometry definition is emitted for that asset ID and
affects **every placement** of that ID in the batch, including placements still
showing the old mesh in Blender. Different edited definitions conflict and block.
The run report records `scene_geometry_edits` with the master SHA, edited placement
count and `ao_rebaked: false`. Reconcile the library master and any other scenes
before later batches; this exporter does not silently write to the shared library.
For a Quarter prop with an explicit local master blend in the revision folder,
edit that master too. Pantry geometry, UVs and materials must remain verbatim;
make a new custom asset if a native prop needs a different shape.

### Adding a non-library asset master

Use **Asset master → Add non-library asset master** in the CSC sidebar when the
prop already exists as its own static `.blend` master. The add-on accepts a master
with one scene, one or more meshes, UV1/UV2/UV3, identity mesh placement and either
`csc_export` prop metadata or a single `CSC_…` armature whose name is the intended
asset ID. It uses that ID as the attachment's `source_asset_id`; no custom property
editing is needed in the building scene. Place, Z-rotate and uniformly scale the
new `Attach_` Empty, then save.

If the source master is outside the building's revision folder, the add-on writes
an export-ready **copy** named `<asset ID>.blend` at the top level of that folder.
Its `csc_export` metadata declares `kind: prop` and the ID; its image paths point
to the same adjacent `textures/` directory as the building blend. The original
master remains unchanged. The exporter then discovers the local master and stages
one custom prop asset, regardless of how many placements use it. If that ID is
already in the active catalogue, use **Add library prop** instead. An existing
in-folder master needs its own `csc_export` prop metadata; the tool will not
overwrite it. AO allocation, UVs, materials and static weights must already be
prepared in the source master.

The add-on checks for conflicting pixels under the same shared AO atlas filename
before importing. A newer `CSC_Props_Shared_01_AO.png` cannot be mixed with an
older one in the same scene batch; reconcile the AO release first. Blender's
viewport may show a prop correctly even when that shared atlas mismatch would
make the exporter reject it.
For CSC production maps, the add-on also resolves an old or missing master image
path to the exact matching filename under synced `3D Art/Textures/CSC_Props/Current/textures`.
New Tailors masters should instead save portable paths to that folder; imported
copies then bind to the building revision's adjacent `textures/` snapshot.

Moving or uniformly scaling a table controller also affects props parented to it
in Blender. Check their contact afterward. The exporter reads the resulting world
placements, but their in-game Pivot Height samples remain independent.

### Reparenting copied fixed geometry to the building rig

When copying a static mesh such as `CSC_Fixed_Dye_Vat_Madder` from another building
blend, preserve its mesh data and vertex groups. For the current Workshop vats,
every vertex belongs to the one `Bone` group at weight `1`. In Object Mode,
parent the copied object to the new building armature with **Object (Keep
Transform)**, then point its existing Armature modifier at that new armature.
This changes the parent and rig target without calculating new weights. Avoid
**Armature Deform → With Automatic Weights** for a fully weighted static mesh;
that command computes new, distance-based weights and can replace the exact static
binding. If in doubt, select every vertex in Edit Mode, select the `Bone` vertex
group, set Weight to `1.000`, and click **Assign**. Check that no extra deforming
groups or modifiers were added before saving. The decoder rejects vertices that
do not have exactly one deforming weight at `1`.

### Placement contract — revised with Henno, 14 September 2026

Blender compositions must already use **uniform attachment scales**. The exporter
preserves saved positions and uniform scales exactly; it must not shrink, stretch
or reposition props to make them fit. Nonuniform scale is rejected, including old
jobs that request the retired `uniform-min` policy. Author a distinct reusable asset
when a different proportion is necessary, and place that asset uniformly.

The revised workshop pair uses `CSC_Attached_Workbench_Long_Narrow` (30 × 12 × 13)
and `CSC_Attached_Seating_Bench` (16 × 6 × 8.5), both at scale 1. They retain the
previous table and seat shapes as explicit new local geometry definitions. Crates
use uniform scaling chosen to preserve their height and stack contacts. The normal
workshop's right-hand display now references `WON_Great_Zimbabwe_RugsF` at uniform
scale 0.42, with its original pivot preserved and the placement adjusted for ground
contact. The sailmaking rack remains its existing custom asset.

The example job records `nonuniform_scale: reject`, `supported_props:
independent-pivot`, and `reused_states: native`. Support parenting in Blender remains
useful for composition, but all exported attachments independently sample Pivot
Height. **Stacked objects are not guaranteed to rise and fall together on slopes.**
Henno accepted testing that behavior for the first Workshop export; it is not the
default for subsequent contents that must move with a support.
Pantry attachments retain their own native construction/pillaged appearances.

For the Tailor support correction (18 September), group tabletop contents as one
custom attachment and folded bench stock as another. Parent each controller to its
support controller at identity and set `support` to that controller's `instance_id`,
`terrain_follow: shared-support-pivot` and `component_transforms: true`. The contents
and support must have coincident world XYZ origins. Both exported points then use
the same `Pivot Height` sample, while content offsets remain in the standalone
master's component transforms. The exporter rejects mismatched pivots even under
the historical `independent-pivot` policy. This avoids dependence on unverified
nested asset terrain inheritance; actual AE/game slope and water behavior still
needs visual verification.

Component masters declare `csc_export.component_transforms: true` and retain local
mesh coordinates plus authored object transforms. Each part has a stable
`source_component` key. No transform application or vertex repivoting occurs in
the authoritative Blender files; only temporary exported vertex streams use the
master's relative frame. The add-on preserves this structure on import and duplicate.

Building metadata may declare `decal_states` keyed by a listed decal geometry ID.
Unspecified decals retain the historical Pillaged-only default. Normal paving must
explicitly name its intact states; it also needs a real registered material binding.
When replacing a PIL model, matching model instance identity replaces the legacy
geometry reference too, preventing duplicate base debris after a geometry rename.

Unknown policies, negative/singular scale, shear and nonzero X/Y rotation remain
errors. The verified placement mapping is Blender XYZ divided by ten and Z rotation
negated. AST `m_orientation` values are **radians**, although the AE UI displays
degrees. Convert the decoded degree value to radians when serializing the AST.
For example, Blender Z = 56.419046 degrees must serialize as approximately
-0.984698 radians, which AE displays as -56.419046 degrees. The earlier exporter
wrote -56.419046 directly and AE displayed -3232.573 degrees, visibly rotating
props incorrectly. This affected all rotated attachment types, not only pantry
assets. Values within 0.000001 of unit scale serialize as exactly 1; intentional
non-unit scales are retained. Scale is separate. Fixed geometry can retain editable object
transforms because the exporter serializes those into the building's vertex stream;
the exported shape must still match the Blender composition.

### Materials and textures

Authoring materials expose external image nodes labelled `B`, `N`, `AO`, `G`, `M`,
optionally `E`, `O`, `T`. Required maps must exist; packed-only or missing images fail.
An explicit `material_bindings` mapping or material `civ_material` property references
an existing Civ material instead, as used for `Ruin_Debris_Decal`.

Generated material/texture identities use content hashes to deduplicate shared maps
across the job. Original meshes retain UV0/UV1/UV2. To match the established CN6
exporter, the decoded vertex key is the source vertex plus its UV coordinates; loop
normal/tangent/bitangent values are averaged per source vertex. Do not key output
vertices on the full per-corner frame, which needlessly inflates Civ VI vertex
counts. AO stays bound to the exported material rather than being replaced with a
scene-wide placeholder. Scalar DDS maps use R8; colour and normal maps use RGBA8.
This first version prioritizes fidelity over block compression.

DDS conversion retains sRGB input/output for colour maps and linear scalar/normal
maps, with a full mip chain. See Microsoft's [texconv options](https://github.com/microsoft/DirectXTex/wiki/Texconv)
for the documented format, gamma and mip flags. Full converter logs are retained.
Fresh output presence is checked even if the CN6 converter exits zero after failure;
DDS headers, dimensions, pixel format, mip counts and payload lengths are checked.

## Validation and current result

The latest inputs are **revision-07-uniform-scale**. Revision 06 is retained as
history and may contain stretched attachment placements that the current exporter
correctly rejects. The revised pair has **11 custom asset definitions** (2 buildings
+ 9 prop identities), including the two new bench variants. Shared PIL is still
geometry-only. This adds two identities compared with the previous pair; individual
placements do not create additional registrations.

The two primary geometries and shared pillage geometry remain unchanged. The saved
Blender files are reopened and checked against the attachment XML: positions, Z
rotation and scalar scale must agree, with no hidden fitting step. Original library
assets are preserved and the two explicit variants are added to the catalogue.

These are Blender/CN6/XML checks. Windows FGX/DDS conversion, cooking, render
appearance and attachment behavior on slopes remain separate runtime checks.

Run the contract tests, optionally enabling integration tests with actual decoded
workshop inputs:

```powershell
$env:CSC_EXPORT_TEST_JOB = 'C:\path\to\workshop-export\job.json'
python -m unittest discover -s project/tools/blender/scene_export -v
```

On Windows, review intact, unworked, construction and pillaged appearances and test
flat and sloped tiles. Check especially pantry native states, independent supports,
attachment culling and the new uniform proportions. These are the remaining runtime
checks after successful conversion and cook.

Asset naming reflects reuse scope: `CSC_ALL_` for approved shared-library props,
`CSC_<QUARTER>_` for Quarter-specific assets. Export roles remain separate. The
revision-09 workshop folder includes its two CSC_TAILORS prop-definition blends;
the seven CSC_ALL definitions resolve through the updated shared library. All five
top-level blends are inputs to a single discovery/export run.

## Revision 10 — one shared bench definition

Henno removed the redundant seating-bench asset. Both workshop Loom_Seat placements
now reference CSC_ALL_Workbench_Long_Narrow at uniform scale 0.5333333, preserving
the prior 16-unit length, pivot and Z rotation. Native proportions give a 6.4-unit
width and approximately 6.93-unit height. Finishing-table placements are unchanged.
The CSC_ALL_Seating_Bench and legacy CSC_Attached_Seating_Bench definitions were
removed from the active library/catalogue, with recovery copies outside it.
The pair now uses 10 custom assets: two buildings, six shared props and two
Tailors-specific props. The reusable sheets contain 39 entries, including eight
CSC_ALL assets; 47 catalogue records remain including other historical definitions.
Use revision-10-shared-bench (five blends and textures) for the current workshop.

### Explicit custom AO bindings

The normal CSC `ao_policy: "reuse_existing"` keeps the AO map already assigned in
the existing Civ material. A Blender AO image or `civ_ao_texture` property does
not replace it during export. For a new AO map that should become a game texture,
use `ao_policy: "stage_explicit"`, set the Blender material's `civ_ao_texture` to
the stable CSC texture ID, and provide an external image node labelled `AO`.
The decoder retains this binding even when `civ_material` references an existing
material. In that mode, the exporter stages the actual PNG and a TEX with the
same identity for Windows DDS conversion. Different source pixels claiming the
same texture ID in a batch are an error.

If the existing material already samples that AO ID, reuse it. Otherwise create a
stable AO-only material variant, preserving its surface maps and other parameters;
do not overwrite a material used by assets with another AO layout. This introduces
no additional asset/XLP entry. Native pantry attachments keep their source bindings.
This explicit handling fixes the former path that silently skipped AO source images
when reusing a material. It does not bake AO during export.

Revision 11 workshop source checks cover Blender, CN6, XML, native source signatures,
shared AO staging and retained construction/pillage/decal models. Windows conversion,
cooking and in-game slope/stack behavior remain to be checked on Windows.

User-authored meshes may contain n-gons. The decoder triangulates those faces only
on its temporary export copy before calculating tangents; the saved source topology,
UV3, weights and transforms remain unchanged. This was checked with the supplied
CSC_TAILORS_SpinningWheel source during its shared-material migration.
