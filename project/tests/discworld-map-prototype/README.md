# Discworld map and Rimfall v0.1

An isolated Civilization VI Gathering Storm prototype. This does not change CSC.
Select **Discworld** in map setup after enabling **Discworld — Map Prototype**.
The schematic geography is original, not a recreation of a published Discworld map.
Use Tiny with four civilizations; the script deliberately fixes the grid at 48×56.

## What works

The map retains the engine's rectangular hex storage and disables wrapping. A
Euclidean circle in staggered hex-centre coordinates defines the playable region.
All exterior plots carry `FEATURE_DISC_VOID`, an unremovable, resource-free,
impassable feature. Terrain is warm towards the Rim and cold at the mountain Hub.
Stock utilities place rivers, resources, starting positions and huts.

The exterior currently reuses stock ice art. This makes the boundary readable,
but is a placeholder, not the final Discworld aesthetic. Rimfall v0.1 adds a
60-degree southern arc of stock waterfall particles using Firaxis's native
AssetPreview API. It is an **elevated spray/curtain study**, not a real terrain
drop: the exterior still has a flat sea surface and the rectangular map still
renders. No floating underside, abyss, terrain cutout or circular minimap exists.
The effects are transient preview instances; the UI addin recreates them on load.
They are not authored feature art, and performance/FOW/multiplayer shipping
behaviour has not been validated. The trial uses 228 effect instances.

## Evidence and scope

Live tests on 10 November 2026 used the installed game, native FireTuner APIs and
native `UI.Screenshot()` output. No desktop automation or simulated screenshot
was used. TGA-to-PNG conversion and preview resizing preserve the captured scene.

- Generation and post-fixture audits: 48×56, no X/Y wrapping, 1,678 interior
  tiles, 1,010 exterior tiles, 666 land tiles; zero mask errors, exterior resources
  or exterior units. All four major civilizations start inside the disc.
- Native naval path test: a destroyer with Cartography has a two-node path to
  adjacent ordinary ocean and a zero-node path to the exterior. Cartography is
  necessary even for this modern ship in the Ancient start. `CanStartOperation`
  returned true for the invalid target, so that broad operation predicate must
  not be treated as proof of target reachability. No movement order was issued.
- The diagnostic ship was removed and Cartography reset before the test save.
- Save/reload passed. After a fresh process and a further reload, the packaged
  addin recreated all 228 instances at finite, correct world coordinates and a
  native screenshot confirmed their appearance. Creation must wait for
  `LoadGameViewStateDone`; coordinates during UI construction are uninitialized.
- A five-turn autoplay attempt did not advance from turn 1; it was stopped.
  This is not evidence of successful multi-turn play or a diagnosed map fault.

The starting save is fully revealed for visual review. It is a test fixture, not
a pristine competitive start. Whole-campaign balance, all movement exceptions,
naval starts, late spawns, workability and multiplayer are outside this check.

## Reproduce

`build.py --output <package-dir> --install <Civ VI Mods/Discworld Prototype>`
packages source and derives an ice feature ArtDef from the local SDK pantry.
It references the game's existing art libraries and does not cook new art.

`tuner_command.py` discovers the native console and journals each command once
with an acknowledgement. `host.lua` starts the deterministic four-player trial.
`audit.lua`, `naval_fixture.lua` and `naval_check.lua` are diagnostic scripts.
Remove the test ship and restore Cartography after using the naval fixture.
`Discworld_Rimfall.lua` can also be sent explicitly to an in-game UI state.
Call `Discworld_CreateRimfall()` after that injection. Do not reinject it without
first calling `Discworld_ClearRimfall()` there.

Captured evidence, screenshots, package and save are in
`C:/Users/Shadow/Desktop/Codex/discworld-prototype-20261110/`.
Earlier native analysis is in `discworld-map-feasibility-20261109/` beside it.

## Grounding and next visual step

The shipped `Tilted_Axis.lua` demonstrates radial climate and nonwrapping maps;
`InlandSea.lua` uses an elliptical terrain mask. Prior REA analysis established
rectangular indexing and propagation of feature impassability to native plot
flags. It did not establish arbitrary renderer cutouts. Native offsets and binary
identities remain in the earlier evidence package, not in runtime prototype code.

The VFX calls follow `Base/Assets/UI/Tuner/TunerAssetPreviewPanel.lua`.
The fourth `SetInstancePosition` argument was experimentally verified through
`GetInstanceInfoByID`: it changes the instance's Z coordinate. The current assets
are `FX_Waterfall01`, `FX_Waterfall03`, and `FX_Waterfall07`, enumerated from the
running game. A convincing Rimfall next needs a water-lip/vertical-sheet asset
and an exterior visual mask; repeating stock spray alone cannot supply the drop.
