# Reusable prop library

Initial export completed 13 September 2026 at
`C:\Users\Shadow\Desktop\Working Files\3D Art\Props\CSC_Prop_Library`.
The package contains 33 asset blends (26 base-game, 5 Rise and Fall, 2 shared CSC),
40 mesh components and 85 shared texture sets. Package manifests establish source
pack eligibility; pantry presence alone does not. No Gathering Storm asset appeared
in this inventory. `CSC_ALL_Prop_Library.ast` was the inventory; its arranged
attachment placements were not used as source geometry.

The delivered `catalogue.json` is the detailed record. `STATE_BEHAVIOR.md` describes
Construction/Pillaged visibility, materials and burn overlays from the source AST.
`verification.json` records reopening all 33 delivered blends in Blender 5.1.2 and
checking geometry, topology, UVs, material assignments, identities, transforms,
normal directions and external texture resolution. No Asset Editor or game check
was performed.

## Authored additions

The Textile Workshop reuse revision retains 7 authored CSC props, bringing
the library to 40 assets at that point. Henno classified the nearby, building-specific loom and
dye vats as fixed building geometry; their four draft standalone variants were
withdrawn before Windows registration. These entries use `origin=authored_blender`; their Blender
sources are verified, while Windows registration is explicitly pending. They keep
three UV channels, static Bone binding, local pivots, CSC painted maps and an
isolated-bake shared AO atlas. The original 33 blends are unchanged.

See [contact sheets and authored intake](prop-library-contact-sheets.md) for refresh
commands and the additive import tool. FGX-source details below describe converted
native entries; authored entries have their own catalogue provenance and state plan.

The uniform-scale correction adds `CSC_Attached_Workbench_Long_Narrow` and
`CSC_Attached_Seating_Bench`, bringing the current library to **42 assets**. These
are deliberate local-geometry variants of the existing CSC workbench, with
identity source transforms and a single static Bone binding. They retain its
existing Civ material and UV1/UV2; a neutral unused UV3 supplies the static export
format. Both are reused across the normal and sailmaking workshops.

See [scene export](blender-scene-export.md) for the current composition contract:
attachment scale must already be uniform in Blender. The exporter rejects stretched
placements and does not adjust proportions or positions automatically. Different
proportions require an explicit reusable asset identity.

## Current agreed contract

- Around 300 unique custom CSC assets is a flexible design goal. Repeated placements
  reference the same asset; no arbitrary asset cap or migration machinery.
- Reused assets retain source identity, geometry, original material bindings and UVs.
  Do not remap pantry props to CSC atlases or recolour them during library intake.
- Preserve location, rotation, scale, parent transforms, source-local frame and pivot.
  Do not apply transforms or bake placement into vertices.
- Single-mesh objects/datablocks use the exact asset ID. Multi-component assets have
  an asset-ID root and catalogue mapping. `source_asset_id` and `export_role` persist
  independently of Blender's duplicate names.
- Reusable CSC asset IDs start `CSC_ALL_`; Quarter-specific asset IDs start
  `CSC_<QUARTER>_` (for example `CSC_TAILORS_`). This supersedes the earlier
  `CSC_Attached_` asset prefix. Attachment/fixed behavior is an explicit export
  role, independent of reusability. Fixed mesh components may retain `CSC_Fixed_`
  names and do not become standalone assets.
- Terrain following depends on physical support: building, ground, or another prop.
  Distance is a review warning, not a classification rule.
- Observed future placement conversion: Blender XYZ / 10, reversed Z rotation for
  AE. Preserve scale and parents. This is not applied to library geometry.

## Import and preview details

FGX vertex coordinates remain unchanged at one Blender unit per source geometry
unit. UV V converts to `1-V`, matching the existing CN6 importer; no atlas remapping.
FGX InitialPlacement is an authoring-scene transform and remains recorded in source
metadata rather than placing the asset at that offset. Source bone hierarchy,
bind transforms and weights are retained; hidden skeleton collections are reference
empties, not animated armatures. These source assets contain no animation bindings,
timelines or nested attachments.

Original AST/GEO/FGX/MTL/TEX and DDS files accompany the blends. Full-resolution PNG
decodes drive the portable Blender previews. Effective asset AO overrides are included.
Blender Principled materials approximate Firaxis shaders. Burn, snow, FOW, tint and
decal-height effects are preserved as source records, not implemented shader parity.
Emission previews are disabled where a source lacks UV3 pending verification of
shader UV routing. Workbench source normals are non-unit; raw values remain in the
`source_normal` attribute and JSON, while Blender normalizes their shading directions.

## Export tooling

The inspected existing `FGXToCN6.cs` hardcodes triangle material index zero and a
dummy skeleton. CivAssetForge's early GLTF conversion shares those limitations.
This intake instead uses `project/tools/blender/ExtractPropFgx.cs` with the same
Firaxis/CivNexus6 DLLs, retaining triangle groups, raw vertex data and source models.
The managed Firaxis ScaleShear getter reads the wrong offset; bone scale uses the
CivNexus wrapper, and inactive model scale is explicitly identity. An active model
scale aborts extraction rather than silently corrupting it.

Supporting scripts in `project/tools/blender/`:

- `export_prop_library.py`: snapshot inventory, package provenance, resolve sources
  and texture dependencies; `--prepare` builds the temporary package.
- `ExtractPropFgx.cs`: compile with .NET Framework C# compiler, reference
  `System.Web.Extensions.dll` and `project/tools/cn6libs/Firaxis*.dll`; native DLLs
  must be beside the executable. Invocation: library-directory, input FGX, output JSON.
- `build_prop_library_blends.py`: Blender background script; package directory follows `--`.
- `verify_prop_library.py`: reopen package files in Blender; package directory follows `--`.
- `finalize_prop_catalogue.py`: ordinary Python; package directory argument; writes
  state summaries and README after Blender verification.

Temporary `project/prop-library-export` staging was removed after delivery. The
delivered package retains all source records needed for inspection and reconstruction.

## Reuse classification and approval

Before finalizing future building blends, propose a short list of new props split
into shared reuse candidates and likely Quarter-specific props. Explain the reuse
case, fixed-versus-attachment treatment, and resulting unique-asset count. Ask Henno
for his opinion and wait before settling final classifications/names and publishing
new shared assets. Continue independent preparation while awaiting his reply. Prior
approval applies: he explicitly approved the existing workshop decisions in this
thread, so revision 09 does not need another confirmation.

Shared `CSC_ALL_` definitions go into CSC_Prop_Library and its contact sheets.
Quarter-specific custom definitions travel with their owning building/Quarter and
are excluded from the reusable-library sheets. Pantry entries keep exact native
identities and remain available on the library sheets. Mark source/placement
`reuse_scope` and `reuse_approved` alongside the existing export-role metadata.

Revision 09 renames the seven approved shared assets to `CSC_ALL_Workbench_Long_Narrow`,
`CSC_ALL_Seating_Bench`, `CSC_ALL_Textile_Bale`, `CSC_ALL_Folded_Cloth_Teal`,
`CSC_ALL_Cloth_Roll_Canvas`, `CSC_ALL_Cloth_Bolt_Teal` and `CSC_ALL_Rope_Coil`.
The two specialized attachments become `CSC_TAILORS_Sail_Drying_Rack` and
`CSC_TAILORS_Sail_Cutting_Panel`; their standalone blends accompany the workshop
blends and are discovered in the same batch. Loom/vats remain fixed meshes in the
building asset. Renaming does not create additional intended assets: the pair still
uses 11 custom identities (two buildings, seven shared props, two Tailors props).
Keep material IDs/bindings and AO unchanged when renaming asset identities.

The nine old CSC_Attached library definitions are retained for older revisions.
They do not appear in the new reusable contact sheets. There are 49 catalogue
records but 40 current reusable-sheet entries after this additive rename.

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

### Workshop AO capacity and pantry interiors — revision 11

Both workshop variants now use one pantry crate and one classical barrel on each
side inside the entrance. These replace the two fixed custom interior goods meshes.
They retain native identities, geometry, UVs, materials and states, with uniform
placement transforms. All other placements are preserved.

Custom prop AO follows the two-sheet Quarter plan: 2048×2048 per sheet, four
1024×1024 Quarter quadrants per sheet. Tailors uses Sheet 01's upper-right quadrant.
The Textile Workshop family, **both variants combined**, must consume no more than
one third of that quadrant. Keep its existing 512×512 family reservation (25%) rather
than treating the ceiling as a target. Reserve the other 75% for the two remaining
hero families and storage.

Revision 11 allocates twelve 128×128 cells including padding: **18.75% of the
Tailors quadrant**, with four cells (6.25%) still free inside the family block.
Six shared custom props, two Tailors attachments, two loom versions and two vats
receive isolated self-AO bakes. Shared masters use the same cell at every placement,
including in future Quarters; do not allocate a new copy per placement or Quarter.
All these props sample `CSC_Props_Shared_01_AO.png` through UV2. Base-building AO
stays separate; pantry props retain their native AO and consume no custom atlas space.
UV1, UV3, geometry, pivots and retained placements are unchanged by this migration.

`CSC_Props/Current/atlas/quarter-ao-manifest.json` records stable rectangles, source
bakes and capacity. Rebuild an explicit working snapshot using
`project/tools/blender/pack_csc_prop_ao.py <CSC_Props/Current>` with Pillow. Its
registered cells must not overlap or exceed their family budget; all occupied
regions are rebuilt from independent sources. Promote the reviewed snapshot and
migrate master/scene UV2 together, preserving old final bundles.

The current accepted `2026-09-14_Shared_01_r006` AO atlas extends the revision-11
workshop's twelve cells with `CSC_TAILORS_SpinningWheel`, `CSC_ALL_Workbench`, and
`CSC_TAILORS_Basket`. It occupies fifteen cells (23.4375% of Tailors), leaving one
128×128 cell inside the 25% family reservation. On 15 September the synced
revision-11 workshop and reusable-prop library AO image copies explicitly adopted
r006 so either newly migrated master can join the same export batch. All older
occupied pixels match the r004 image exactly; the six shared surface maps did not
change. Earlier export-run manifests remain historical records of their original
texture snapshots.
