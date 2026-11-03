# Delivery assets

Canonical source identities after the 24 October 2026 cleanup:

| Asset | Purpose | District consumers |
|---|---|---|
| `CSC_BAKERS_Delivery` | Crane, route, flour cargo and separate donkey | Bakers Classical 03, 04, 05, 10 |
| `CSC_TAILORS_Delivery` | Same working delivery setup with textile cargo | Tailors Classical 03, 04, 05, 06 |
| `CSC_ALL_Delivery_Donkey` | Shared independently terrain-following donkey/sled | Both delivery assets above |

The accepted `CSC_TRIAL_BAKERS_Delivery_Split` and
`CSC_TRIAL_Delivery_Donkey` supply the behavior. The user's temporary canonical
copies were removed before cleanup; those copies had `Standard_Landmark`, whereas
the accepted trial versions use `Standard_LandmarkNoRandomOffset`. The canonical
assets preserve the accepted no-random-offset behavior, child attachment phase
settings, cargo transforms, materials, state visibility and the 68-second clips.

The numbered Bakers delivery and both Tailors deliveries were semantically
identical within their Quarter. They now share one parent asset per Quarter.
No district placements were changed.

## Geometry and animation identities

The active geometry and animation resources are:

- `CSC_ALL_Delivery` — the accepted centered crane/route model and clip,
  previously named `CSC_ALL_Delivery_Pivot`.
- `CSC_ALL_Delivery_Donkey` — the accepted separate donkey model and clip,
  previously named `CSC_TRIAL_Delivery_Donkey`.

All four FGX binaries are byte-identical to the accepted inputs. Internal native
model, mesh, bone and animation-track identifiers remain unchanged, including
historical TRIAL strings inside the donkey's native binding names. These are
compatibility identifiers, not additional browser assets. GEO/AST binding fields
retain matching internal identifiers; public resource names, descriptors,
filenames and references use the canonical names above. Do not globally replace
internal strings or regenerate the animation solely to remove those labels.

Editable masters remain at the locations recorded in
[the original pivot and donkey work](storage-ground-pivot-trial.md). Historical
migration/export scripts contain the old trial names and must not be rerun as
current installers. A future export must target the canonical public identities
while preserving the matched native model/clip bindings.

## Cleanup and validation

Removed eighteen obsolete source files: the old combined Bakers delivery AST,
duplicate/renamed parent and donkey ASTs, superseded Pivot/TRIAL resource files,
and four unreferenced `CSC_TEST_TAILORS_Delivery_*` geometry files. The original
unused `CSC_ALL_Delivery` model/clip pair was replaced by the accepted centered
pair under that canonical identity. All former files are backed up.

The two `Storage_L_No_Delivery` assets remain: they are used storage variants,
not obsolete delivery systems. Authored Blender sources and historical review
packages were retained.

Updated eight district references, the Tilebases XLP, ModBuddy Content entries
and AssetCloud records/dependencies. Checks confirm:

- duplicate equivalence and exact behavioral preservation under the rename;
- byte-for-byte parity of the four accepted FGX files;
- all three canonical assets resolve in all five states;
- Windows and MacOS isolated tilebase cooks pass and contain the canonical
  entries, without the retired parent entries;
- no retired public asset/geometry/animation references remain in the active
  graph;
- every installed game file retains its original hash.

The source cleanup is complete. **It has not been deployed over the installed
mod**, because the current human-owned game is protected by the project handoff.
The separate art cook does not deploy the pending gameplay changes in the working
tree. A later authorized normal build will install the renamed source assets.

Evidence, before snapshots, isolated platform packages and verification reports:
`C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-cleanup-20261024`.
Utility: `project/tools/art/cleanup_delivery_assets.py`.
