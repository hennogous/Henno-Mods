# CSC material map assistance

CSC includes a one-time Lua pass that adds suitable material deposits on new maps at all vanilla and Truly Abundant Resources abundance levels. The setup option **Additional industry materials** defaults to On. **Version 4 retains the version-3 scope of Bakers and Tailors**, the two implemented Quarters. Bakers already exceed the calibrated coverage aim and receive no direct repair draws; Tailors retain their scaled missing-continent assistance, followed by a temporary site-density increase: twice the Base-only sites and four times the both-material sites relative to that map after its original repair. Existing deposits remain in place. Version 2's broader eight-Quarter research is historical; its abundance factors still define scaling for the implemented scope. See [the factors and scaling policy](../research/mods/csc-material-abundance-scaling-20261016.md).

## Temporary Tailor density emphasis (v4)

Henno requested **2× Base-only and 4× both-material placement sites** while
only two industries are implemented. The multipliers are separate: increasing
both-class supply can convert a Base-only site, so the planner creates both
connections first and then fills the Base-only target. They are map-wide
targets, not equal continent quotas or counts of independent settlements.
`C.SiteMultipliers` is the single tuning location to reduce this emphasis as
other Quarters join. Zero both-class counts receive an abundance-scaled minimum
target of roughly four (Sparse3, Standard4, Abundant4); this is an additional
policy to avoid multiplying zero. Native feasibility and safety bounds can
prevent a target, and `site_density.met` reports that explicitly.

Targets use the actual post-v3 map, so natural abundance already scales their
size across vanilla/TAR presets. Additional density deposits are capped at5%
of passable land × abundance scale map-wide and8% per continent (minimum8/2).
These are safety ceilings, not resource quotas. Existing v3 repair limits are
separate. Counts may overshoot by a few sites because one deposit can support
several placements. Palettes retain continental preferences and mapped modded
resources. The phase uses a separate CSC-owned RNG, empty native-eligible tiles,
and avoids exact starts, reserved centers and losses of Baker Base/both sites.
Bakers can gain incidentally from shared Flax; they receive no direct boost.

The15 captured vanilla Sparse/Standard/Abundant maps were replayed offline using
the real Lua planner and their captured native eligibility. All15 met their
targets. This validates the proposed pass on existing landscapes. V4 then passed [six fresh native maps](../research/mods/csc-tailor-density-native-20261017.md): three Standard and three Abundant, automatic turn1 execution, native quantities, independent census and exact Lua replay. This is not full map generation outside Civ. The installed native v3
evidence remains historical and unchanged. See [v4 density preview](../research/mods/csc-tailor-density-20261017.md).

## Runtime sequence

`CSC_MaterialMap` is registered through `AddGameplayScripts` at LoadOrder **999901**. Its two imported modules use 999900. The pass runs directly when the gameplay context loads, after native map/resource/start placement and before the in-game UI. This is a late part of map setup, not an override of the selected map script or ResourceGenerator. The five native checks observed initialization turn 1 and completion before the first in-game UI load.

The database, including conditional resource mappings and cleanup, is already loaded. Sukritact's Oceans uses a gameplay pass at LoadOrder 6, so its normal pass precedes CSC's. TAR/YnAMP map scripts finish their generation before gameplay scripts. These ordering facts do not certify arbitrary mod combinations; only CSC plus official content was used in this test batch. Another mod can choose a later load order and change the map afterward.

The `CSC_MATERIAL_MAP_ASSISTANCE_DONE` game property prevents re-entry and persists through saves. Saved games are skipped even without that flag; so are disabled assistance, unrecognized resource settings, late initialization and missing numeric map seeds. The pass does not subscribe to turns or keep adjusting resources during play. Failed native placement rolls back every resource added by this pass and records a failed audit.

## Selection policy

- Only Bakers and Tailors enter runtime matching, preservation and coverage. Tailors can receive direct help when their continent lacks an ordinarily clearable both-class site; at vanilla Abundant their chance remains 7/12. Other levels scale the desired coverage and estimated natural coverage before calculating the missing-continent chance. Bakers retain their existing geography, with possible incidental benefits from shared Tailor materials. No direct draws, resource pools, targets or preservation constraints are created for the six design-only Quarters.
- Each named continent has a soft palette: one preferred feasible resource per assisted Quarter/material class. Local resources are favoured, cross-continent reuse receives lower weight, and fallback types remain available.
- A repair creates an actual material arrangement around a candidate center: add a Specialty near an existing Base, a Base near an existing Specialty, or two different resource tiles if both classes are missing.
- A single safe deposit is preferred. If none is safe and feasible, the planner tries a pair. Each accepted repair updates the two implemented Quarters, accounting for shared materials. The audit records quantity=1 for each added deposit and the adapter verifies the native quantity readback.
- Native `CanHaveResource` supplies habitat eligibility. Added resources must be on empty passable land with no district or improvement, on the assisted continent. Every placement is checked again and read back. Starting plots are rejected by the native API. Quarter centers use the same ordinary-clearing material-geography filter as the viewer, not a complete city-specific district check.
- Preserve every existing resource and each continent's last ordinary Base-supported and both-class opportunity. Reserved planned centers cannot receive later additions. Vanilla Abundant limits remain four deposits per continent and ten per map; other levels scale both limits, rounded to the nearest integer. Broad calibration across other sizes is not yet done.

The conditional `CSC_MaterialMap_TAR` database action (999899, `ModSupport_TAR` criterion) loads `ModSupport_TAR_MAP.sql` only with TAR enabled. It records TAR's standard density 29 in `GlobalParameters`; otherwise the adapter uses vanilla 30. TAR's scripts remain untouched. Random uses the expected Standard density because the native generator's private resolved random roll is unavailable at this phase. Every v2 audit records the setting, density, scale, target fractions, selection probabilities and limits, including the Random approximation.

## Deterministic Lua planner

`CSC_MaterialMapCore.lua` contains a pure planner. It receives plots, definitions, native eligibility and the map seed; it makes no engine writes. All selection arrays are ordered before drawing. A CSC-owned Park–Miller stream (48271, modulus 2147483647, four warm-up steps) uses a versioned seed derived from the map seed; a separate keyed stream supplies each continent/industry assistance roll. No `TerrainBuilder.GetRandomNumber` or other engine RNG is used by the planner.

This stream replaces Python's MT19937, so its exact choices differ from the earlier Python prototype. The installed Lua planner is itself executable offline: with the same captured eligibility, all five native plans reproduce exactly. This does not implement external native terrain generation or Civ's global RNG.

## Definitions and source boundaries

`CSC_MaterialMapDefinitions.lua` resolves Bakers/Tailors from their actual loaded `CLASS_CSC_*_BASE/SPEC` resource tags. Its retained design data for the other six Quarters is inactive in v4: the resolver iterates only the two runtime Quarters. Research tools can merge the six reference definitions for observational statistics, without including them in the live planner. Resources absent from the loaded database or without map frequency cannot be placed.

This is an interim boundary while six Quarters are unfinished. When a Quarter's resource contract is implemented, change its resolver branch to use the complete runtime classes and update the shared survey definitions/fixtures together. Optional resource packs have a resolver test but have not received a native compatibility batch.

The live audit is `Game:GetProperty('CSC_MATERIAL_MAP_ASSISTANCE_AUDIT')`. It stores status, version/seed, phase, selection draws, preferred palettes, exact additions with quantity, intended centers and coverage counts. It does not persist an entire map. The test-only configuration `CSC_MATERIAL_MAP_DIAGNOSTICS` exposes a pre-pass world (including native resource quantities) and eligibility table inside the gameplay context; normal play leaves this disabled. The test runner explicitly clears it afterward.

## Files and build

| File | Role |
|---|---|
| `Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMap.lua` | Native adapter and once-only entry point |
| `Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapCore.lua` | Pure deterministic planner |
| `Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMapDefinitions.lua` | Runtime/designed material resolution |
| `Civ Supply Chains/Settings/Settings.xml`, `Settings_Text.xml` | Player option and explanation |
| `project/modbuddy/CivSupplyChains.actions.json` | Canonical action registrations; generated into `.civ6proj` |

Normal ModBuddy builds include the new files. The test deployment used `deploy_material_map.py` to copy only the three Lua files and two setting files, then generated the installed manifest with Firaxis's **Civ6.Tasks.GenerateModInfo** task. This preserved unrelated installed gameplay, art, action trees, dependencies and references. It did not invoke Clean or the art cooker. Backups and a deployment inventory remain with the test evidence.

## Validation and results

Current v3 native evidence: [fifteen-map implemented-Quarter study](../research/mods/csc-implemented-materials-native-20261016.md). Five each at vanilla Sparse/Standard/Abundant added 5/6/6 individual resource copies. Tailor both-class continent coverage changed 1→6, 4→9 and 3→9 out of15 per level; Bakers stayed11/15,11/15 and12/15. All original quantities survived, all17 additions have native quantity1, and every map passed automatic startup and exact offline replay. Original preferences are restored. The older v1/v2 reports below retain their historical broader scope.

See [automatic Lua native results](../research/mods/csc-continental-helper-lua-20261016.md).

`test_lua_material_map.py` executes the actual entry point in a native-fixture environment: repeatability, re-entry/script-reload guards, saved/disabled/unknown-setting/late-game skips, original-resource rollback after injected failure, independent coverage census, the two-resource Tailor repair path, optional resource mappings and the implemented-only runtime scope. It checks all ten vanilla/TAR abundance profiles. A trap fails the test if the planner attempts to draw from the engine RNG.

`automatic_assist.py` starts the five paired games and reads audits/maps. It invokes neither the planner nor resource setters through FireTuner. `verify_automatic_assist.py` checks the automatic log completion once per map, completion before the UI, exact original controls, source/deployment fingerprints, unchanged existing resources, coverage invariants and absence of observer placement commands. The viewer retains the original maps, Python previews, Python API tests and automatic Lua results for comparison.

The original five-seed batch remains historical v1 evidence. Version 2 is checked separately against those five fixtures and all ten vanilla/TAR profiles, including both Random cases. Native Sparse and TAR Plentiful smoke tests passed with 2 and 8 automatic additions respectively, exact offline replay, no loss of existing resources/last coverage, and restored preferences. Native save/reload, multiplayer, other map sizes/scripts and optional resource packs remain outside this validation. The approximate coverage targets are not guarantees or quotas.
