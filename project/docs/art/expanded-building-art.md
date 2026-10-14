# Expanded building art in CSC

Current setup: 7 October 2026. The optional Art Pack trial is retired; normal
and expanded building art now ship together in Civ Supply Chains.

## Ownership and activation

| Building | Expanded asset | Source property | Shared Service gate |
|---|---|---|---|
| Wind Mill / Water Mill | `CSC_BAKERS_Wind_Mill_2` / `CSC_BAKERS_Water_Mill_2` | `CSC_BAKERS_STAGE_2_EFFECT_GROWTH` | `REQSET_CSC_STAGE_2_EFFECT_PREREQ` |
| Bakery | `CSC_BAKERS_Bakery_2` | `CSC_BAKERS_STAGE_3_EFFECT_HOUSING` | `REQSET_CSC_STAGE_3_EFFECT_PREREQ` |
| Café | `CSC_BAKERS_Cafe_2` | `CSC_BAKERS_STAGE_4_EFFECT_TOURISM` | `REQSET_CSC_STAGE_4_EFFECT_PREREQ` |
| Textile Workshop | `CSC_TAILORS_Textile_Workshop_2` | `CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION` | `REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ` |
| Tailor | `CSC_TAILORS_Tailor_2` | `CSC_TAILORS_STAGE_3_CUSTOMERS` | `REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ` |

Five property modifiers, attached to six Quarter buildings, live in
`Civ Supply Chains/Data/CSC_Q_BAKERS.sql` and `CSC_Q_TAILORS.sql`. Each uses the
same complete OwnerRequirementSetId as its related gameplay Service.
There are no parallel art-only requirement sets or inverse customer attaches.
Ordinary customer transactions retain their independent gates.

One shared `Civ Supply Chains/Lua_UI/ArtProperties/CSC_ArtProperties.lua` mirrors
each positive SQL source value to a binary direct city property ending in `_ART`.
It reads the SQL state and does not evaluate material, adjacency or unlock
criteria. The `CSC_ArtProperties` AddGameplayScripts action loads it at 501.

`CSC_GamePropertyRanges.artdef` maps each `_ART` value to the existing `_ACTIVE`
interval. It is registered with `WorldView_Translate` in
`Civ Supply Chains.Art.xml`. Six priority-1 entries in `CSC_Landmarks.artdef`
select expanded models through CITYPROP; the existing priority-0 baseline
variants and current district layouts remain intact. All models belong to
`XLPs/CSC_Tilebases.xlp`, package `Landmarks/CSC_Tilebases`.

The Fashion House has no alternate model yet. Its art property, mapping and
variant remain deferred. An alternate export is still optional in the exporter.

## Build in ModBuddy

1. Reload `Civ Supply Chains/Henno Mods.civ6sln` if it was open during migration.
2. Build Civ Supply Chains normally.
3. Restart Civilization VI before testing the new Lua action and art package.

No custom targets or Art Pack finishing CMD are needed. Source AST, geometry,
material and texture files are discovered by the cooker through XLP dependencies;
they do not need individual project Content rows. The classifier ArtDef and Lua
script are registered in the project. The existing UpdateArt dependency-file
placeholder resolves to the generated `Civ_Supply_Chains.dep`.

The separate Art Pack project was removed from the solution and its source and
installed output moved to `C:/Users/Shadow/Desktop/Codex/art-pack-merge-20261007/`
under `retired-source/` and `retired-installed/`. It should not be enabled alongside
CSC. The previous CSC installation is retained under `installed-before/`.

No dependency on a particular asset-limit fix was added.

## Sources and re-export

Bakers' four alternate ASTs, their two unique materials and six texture files
were transferred unchanged. This preserves the golden Wind Mill roof textures.
Existing identical geometry and shared CSC resources are reused; old Art Pack
copies did not overwrite newer CSC atlases or shared art.

Tailors' normal and alternate groups were regenerated from these Working Files
sources:

- `C:/Users/Shadow/Desktop/Working Files/3D Art/TAILORS/Tailor/revision-10-vertex-budget`
- `C:/Users/Shadow/Desktop/Working Files/3D Art/TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao`

Both folders have an export contract; `--include-optional` includes the alternate
models and their props. The Workshop folder now also has saved export defaults.
Use an explicit fresh output directory under Desktop Codex:

```powershell
py project/tools/blender/export_assets.py "C:/Users/Shadow/Desktop/Working Files/3D Art/TAILORS/Tailor/revision-10-vertex-budget" --include-optional --output "C:/Users/Shadow/Desktop/Codex/Tailor-next-export"
py project/tools/blender/export_assets.py "C:/Users/Shadow/Desktop/Working Files/3D Art/TAILORS/Textile Workshop/revision-11-pantry-interiors-shared-ao" --include-optional --output "C:/Users/Shadow/Desktop/Codex/Workshop-next-export"
```

Use a new output name per run, then rebuild CSC in ModBuddy.

The Workshop required native attachment metadata repairs on 15 controllers
across its two building scenes. Native crates and other pantry pieces remain
native references. Geometry, UVs and placements were preserved. Corrected
metadata and relative texture paths were saved to the source scenes; original
blends are backed up under `source-before/Textile Workshop/` in the migration
output folder.

The exporter was corrected to honor its explicit independent-pivot support
policy during export, choose the small Workshop template, treat an unset authored
construction flag as false, and scope stale-file retirement to the source group.
The last fix prevents one building export from deleting another group's outputs
when both use a shared Desktop output directory. Authoring support-height warnings
remain visible; these placements still need an in-game slope check.

## Verification and remaining game checks

The stock ModBuddy targets cooked the merged source successfully for Windows and
MacOS, with zero warnings or errors. All six expanded asset names occur in both
TileBase packages. Cooked hero-building references, selection rules, classifier
intervals, package paths and the single Lua action were checked. All 105 TileBase
entries resolve to local ASTs. Tailors contracts and Stage 2/3 handoff checks pass.
Focused export and contract tests passed; seven existing export tests were skipped.

The verified build is installed in the local Mods folder. Logs, export stages,
receipts, backups and `verification.json` live outside the repository at
`C:/Users/Shadow/Desktop/Codex/art-pack-merge-20261007/`.

Runtime acceptance is still user-owned: after restarting the game, check each
expanded model with its Service active, then deactivate/reactivate the unlock,
material or eligible customer conditions as applicable. Check reversion to the
normal model, pillage/repair, save/reload and supported placements on slopes.
Do not record runtime acceptance from cook or offline checks alone.

The [historical split trial](optional-art-pack-test.md) retains the evidence about
additive ArtDef merging between separate mods. The current package uses one
CSC Landmarks file, so it no longer depends on that cross-mod merge behavior.
