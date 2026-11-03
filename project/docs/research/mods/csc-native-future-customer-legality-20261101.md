# Future customer district legality — 1 November 2026

Purpose: bound what the existing plot-level Lua query proves for the customer-aware planner. This is a static current-Windows-DLL investigation, not a runtime contrast or a new native interface.

## Verified static evidence

Program SHA256: 324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c. Image base 0x180000000. Ghidra mapped function names are labels; native signatures/types were not imported.

- Lua wrapper 0x18001c380 reads three numeric arguments after self. A missing numeric argument becomes zero. It does not read a fourth future/ignore flag. Existing use remains plot:CanHaveDistrict(districtIndex, playerID, cityID).
- The wrapper dispatches through Cities singleton virtual slot +0x58. Accessor 0x1803638b0 returns DAT_180b8e238. Constructor 0x1803634a0 stores vtable 0x1809f18a8 and the singleton. The recorded 104-byte vtable read has pointer 0x180363180 at offset0x58. The chain is therefore established from dispatch/data, not from matching names alone.
- Rules method 0x180363180 resolves context, calls GetValidFeatureForDistrict, CanCityRemoveFeature and CanCityAutoHarvestResource, then calls helper0x18025a360 with a fixed true flag and those answers.
- The helper tests district definitions, city/district occupancy, park/flood/wonder state, city range<=3, feature/resource-removal permissibility, terrain/water/improvement/fallout and other district geography restrictions. It contains some conditional ownership/city and uniqueness checks.
- Resource-bearing plots can pass through an auto-harvest path. A true result is not a preservation guarantee.

Raw evidence is retained in the small JSON files beside this note: wrapper, Rules method, full helper, constructor, singleton xrefs and vtable bytes. Master databases and game binary were not modified.

## Inference and implementation limits

Treat the result as native plot potential, not complete current city build permission. This packet does not establish a fourth flag, an arbitrary ignore-prerequisite query, an economic quote, a future unlock date or native district preference score. Feature removal and harvest subcalls may themselves depend on current technology; a false result must not be renamed permanent geographic impossibility.

Keep separate evidence for current city CanProduce, district/building unlocks, specialty capacity, exact immediate OperationTargets/CanStartOperation, ownership/treasury/route and footprint protection. A future customer promise is bookkeeping, not a native reservation or forced order. Essential unknowns defer the action/path; unrelated travel/opportunity cost uncertainty remains explicit.

Runtime contrasts for locked districts and population-limited cities remain unobserved in this investigation. No new game or extra live query was run to make this packet.

## Decision

Use the existing three-argument binding. Do not fabricate future legality from a successful plot query or write a fourth Lua argument. Protect mapped supply independently from native auto-harvest permissibility. The v2 adapter should label failed/unknown currently locked paths deferred and reconsiderable, rather than permanently illegal.


Local raw packet: `C:/Users/Shadow/.codex/visualizations/2026/10/11/01a12a24-6714-7540-8d23-154b092106fe/native-customer-legality-20261101`.

The local verifier checks the three-argument wrapper, constructor/vtable dispatch, expected current DLL identity and complete decompilation exports. It does not execute the game.

Shipped Gathering Storm `UI/Replacements/CitySupport.lua` uses `GetNumZonedDistrictsRequiringPopulation()` and `GetNumAllowedDistrictsRequiringPopulation()` for used/allowed specialty capacity. Prefer those native counts to a population-only approximation. Districts with `RequiresPopulation=0` do not consume that ordinary slot by definition; current permission remains a separate native check.
