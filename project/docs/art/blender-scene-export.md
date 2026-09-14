# Blender scene decoder and asset exporter

Use `project/tools/blender/export_assets.py` for the reusable-prop workflow. It replaces
`csc_export_pipeline.ps1` for composed building scenes. The older script exports
whole scenes, handles multi-mesh GEO metadata incorrectly, and does not decode
attachment identities or transforms.

The tool reads saved Blender files without saving or applying transforms to them.
It stages CN6, GEO, AST, materials, texture descriptors/sources and an idempotent
XLP merge. Windows then converts CN6 to FGX and PNG to DDS. Installation is a
separate explicit command with destination checks, backups and rollback on errors.

## Windows: export a folder of Blender assets

Prerequisites: Python 3.10+, Blender (tested decoding with 5.1.2), the repository's
`project/tools/cn6libs/` folder and Microsoft DirectXTex `texconv.exe`. Python uses
only its standard library: PyYAML is not required by this exporter.

Henno copies the complete revision folder into Google Drive himself and runs the
export locally on Windows, either directly or through the Windows agent. Do not
create a separate ZIP or attempt to connect from the Mac to Windows.

The exporter lives in the repository: `project/tools/blender/export_assets.py`, with
its helpers in `project/tools/blender/scene_export/`. Keep tools in the repo; the
revision folder holds the blends, textures and supporting art files. Referenced
library props must be present in the synced catalogue; explicitly declared custom
prop definitions in the input folder can also be exported and shared in that batch.

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

After reviewing the report and staged files, explicitly install that run:

```powershell
python project/tools/blender/export_assets.py --install 'C:\path\to\revision-07-uniform-scale\export-runs\<timestamp>\job.json'
```

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
{"kind": "prop", "asset_id": "CSC_Attached_New_Bench"}
```

```json
{"kind": "decal", "geometry_id": "CSC_New_Building_PIL_Decals"}
```

A building can specify the template and relevant model selectors explicitly:

```json
{
  "kind": "building",
  "asset_id": "CSC_New_Building",
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
`building_geometry` and their unique `source_asset_id`. It first tries the asset's
own AST; otherwise it requires a unique template/model match by main mesh name.
Ambiguity requires explicit template metadata. Existing `Shared PIL export` scenes
use their sole armature identity as the decal ID. Building/decal links can come
from template GEO IDs, with the legacy `PIL_geometry` path as a fallback. Existing
library prop scenes can be recognized by a unique catalogued armature identity.
No arbitrary filename suffix is used to invent an asset ID or state role.

Use `{"kind": "ignore"}` to explicitly exclude a scene; it remains listed in the
report. Existing pantry assets are reference-only: attach them from the library,
rather than exporting their source blends as new assets. Authored prop definitions
in the folder can be standalone or shared across buildings; geometry/UV matching
still verifies that placements reference those definitions verbatim.

Common CSC geometry/material/texture/prop templates and policies are stored in
`scene_export/csc.defaults.json`; `--defaults` selects another defaults file. Building
templates are resolved per file, so one run can contain different building types.
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
| `building_geometry`, `fixed_geometry`, or `CSC_Fixed_` mesh | Included in the primary building GEO/CN6 with its world placement serialized into a temporary vertex stream. No separate prop asset. |
| Attachment EMPTY with `instance_id`, `source_asset_id`, `support` | Placement from its world matrix. Direct mesh children must retain their library geometry/UVs and identity transforms relative to the root. |
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

Do not transform its mesh child, edit the reused mesh/UVs, or change source identity
properties. The child's transform relative to its controller must remain identity.
X/Y tilting, mirroring and axis-specific scaling are rejected. To change a prop's
proportions, author a separate library asset and bind it explicitly. Adding a new
instance also needs a unique `instance_id`; ordinary duplicate-and-save is not the
same as repositioning an existing controller.

Moving or uniformly scaling a table controller also affects props parented to it
in Blender. Check their contact afterward. The exporter reads the resulting world
placements, but their in-game Pivot Height samples remain independent.

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
Henno accepted testing that behavior in game before introducing assembly assets.
Pantry attachments retain their own native construction/pillaged appearances.

Unknown policies, negative/singular scale, shear and nonzero X/Y rotation remain
errors. The verified placement mapping is Blender XYZ divided by ten and Z rotation
negated, in degrees; scale is separate. Fixed geometry can retain editable object
transforms because the exporter serializes those into the building's vertex stream;
the exported shape must still match the Blender composition.

### Materials and textures

Authoring materials expose external image nodes labelled `B`, `N`, `AO`, `G`, `M`,
optionally `E`, `O`, `T`. Required maps must exist; packed-only or missing images fail.
An explicit `material_bindings` mapping or material `civ_material` property references
an existing Civ material instead, as used for `Ruin_Debris_Decal`.

Generated material/texture identities use content hashes to deduplicate shared maps
across the job. Original meshes retain UV0/UV1/UV2 and per-corner normal/tangent
splits. AO stays bound to the exported material rather than being replaced with a
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
