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
- Future custom attachments start `CSC_Attached_`; geometry incorporated into the
  building starts `CSC_Fixed_`. Existing shared CSC assets remain references.
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
