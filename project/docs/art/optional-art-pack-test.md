# Optional CSC Art Pack: alternate building art

The `CSC Art Pack` is an optional mod with a hard dependency on Civ Supply Chains. The 20 September 2026 Wind Mill trial established that a separate `Landmarks.artdef` can add a building variant to CSC's district when both root `Districts` and nested `BuildingVariants` use `m_ReplaceMergedCollectionElements=false`. The author confirmed the Wind Mill setup works in game. The other five expanded variants still need an in-game visual check after this broader split.

## Ownership

- CSC owns all gameplay buildings, Service effects, requirement sets, normal building models, and baseline ArtDef building sets and variants. It has no alternate-art property modifiers, Lua mirror, `GamePropertyRanges`, selection rules, expanded tilebase entries, or alternate-only model and prop sources.
- The Art Pack owns `Data/CSC_ArtPack_Properties.sql` (five property modifiers, six building attachments), `Lua_UI/ArtProperties/CSC_ArtProperties.lua`, `ArtDefs/CSC_GamePropertyRanges.artdef`, and `ArtDefs/CSC_ArtPack_Landmarks.artdef`. Its Landmarks ArtDef adds six expanded variants to the Bakers' and Tailors' districts: Wind Mill, Water Mill, Bakery, Café, Textile Workshop, and Tailor.
- Core Quarter contract validation owns the reusable Service requirement sets and verifies that alternate-art modifiers, attachments, and Lua mirrors do not leak back into CSC. Art Pack bridge implementation is validated with the Art Pack rather than treated as a core Quarter output.
- The Art Pack's TileBase XLP includes those six models plus alternate-only props. Its art folders contain the necessary local geometry, materials, and textures for an independent ModBuddy cook. Some source assets are copied from CSC because the cooker cannot read a sibling project as a source pantry by default; CSC keeps its copies wherever normal models still use them.
- The Art Pack `.civ6proj` declares `UpdateDatabase` at load order 200, `AddGameplayScripts`, and `UpdateArt`, with a hard mod dependency on CSC. Its `.Art.xml` has CSC as a required art ID and registers the property classifier under `WorldView_Translate`.

## Building in ModBuddy

1. Build **Civ Supply Chains**, then **CSC Art Pack** in ModBuddy. Reload either project in ModBuddy after an external edit to its `.civ6proj`.
2. Double-click `CSC Art Pack/Finish ModBuddy Build.cmd`. It checks the cooked tilebase, required Wind Mill textures, SQL, Lua, classifier and `.modinfo`, then restores all six `Tag_HeroBuilding` references in the built Landmarks ArtDef. Run it after **every** Art Pack build. Its optional command-line argument accepts another built mod folder.
3. A cook message saying `CSC_Buildings.artdef` is missing from the Art Pack source pantry is expected: the post-build step restores those cross-mod building references. Missing geometry/material/texture errors, zero-byte BLPs, or other substituted tilebases are not expected.

The source `CSC_Buildings.artdef` stays in CSC. Copying that whole ArtDef into the Art Pack would pull its other CSC ArtDefs into the dependency graph. Loose `.ast`, `.geo`, `.fgx`, `.mtl`, `.tex`, and `.dds` files are discovered from standard art folders without being individually added as ModBuddy project items. The `.Art.xml`, ArtDefs, XLP, SQL and Lua files are ModBuddy Content items.

## Verification

An isolated MSBuild run on 20 September 2026 compiled both projects. The Art Pack build produced a nonempty Windows tilebase BLP, SQL/Lua/classifier files, a `.dep`, and `.modinfo` actions; the finishing script restored all six building references. A local SQLite syntax check loaded five modifiers, ten arguments, and six building attachments. These are build checks, not proof that all five newly moved expanded variants select correctly in game.

With only CSC enabled, confirm every building stays on its normal model when its Service activates. With both mods enabled, confirm the six expanded models switch on at their corresponding active Service gates and revert when those gates stop. Check `Modding.log` for the Art Pack actions and the game logs for ArtDef or database errors.

The Tailors implementation contract and its validator still describe the former CSC-owned property bridge. They need a separate contract rebaseline before being used as the authority for future Tailors art bridge work; do not silently treat their old file paths or assertions as current output ownership.
