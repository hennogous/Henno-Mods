# CSC AI lessons from installed RH v5.097

Reviewed18October2026. Source: C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/3792072489. README and manifest identify5.097 Patreon Beta. Source SHA256 inventory is in csc-rh-v5097-source-inventory-20261018.json. Independent Astra review covered adjacencies/modifiers and dynamic strategies; primary review covered Builder demand/purchasing, activation and application limits. This is static source analysis, not a native performance validation. No game, FireTuner connection, CSC gameplay change or Workshop edit was made.

The relevant change from the old4.34 reference is architectural: lower general improvement valuation, no old global Builder900 boost, and substantial Lua intervention in purchase supply. No exact Builder improvement/repair dispatcher emerged. RH does not supply a proven universal resource-improvement or preservation switch.

## Current source facts

| Area | Installed v5.097 source | Implication for CSC |
|---|---|---|
| General improvement demand | core/Main/RH_LAI_Main.sql:7 sets PSEUDOYIELD_IMPROVEMENT30. This was the only base-update statement found in registered UpdateDatabase SQL. Leader/era/strategy percentage biases remain separate. | Our90 is inherited from older RH, not the installed current base. Test30 separately if recalibrating; do not change it silently. |
| General Builder priority | core/Ops/RH_Ops.sql has no UNIT_BUILDER entry, unlike old global900. Leader-specific Builder preferences can still exist elsewhere. | Our current100 is a CSC experiment; it is not the new RH global default. |
| Movement | core/Main/RH_LAI_Main3.sql:234–259 grants AI Builders+1 friendly-territory starting movement. | Actual gameplay advantage; not evidence of better job selection. |
| Improvement-type preferences | core/Ops/RH_Ops.sql:87–114 has Mines40, Pastures9, Quarries-8, plus others. | Does not meet Henno's aim of avoiding a skew among improvement types. Do not import these weights. |
| Improvement event | core/Main/RH_LAI_Main2.sql:358 changes DefaultCityBuilds/CITY_EVENT_IMPROVEMENT Value to1. | Event preference is not demonstrated repair/task throughput; needs isolated testing. |
| Resource value | Supporting_Systems/RH_Improvements.sql:7–28 adds a private yield to raw strategic resources and luxuries; no bonus-resource rows. | A possible plot-value/preservation signal, but supplies zero improvement-vs-unimproved yield difference by itself. |
| Reciprocal district adjacency | Supporting_Systems/RH_Districts.sql:38–51,193–209 uses private native reciprocal IZ/infrastructure bonuses. | Supports the data pattern CSC already uses for sales. Not proof of multi-step planning. |
| Approximate material location | RH_Districts.sql:515–545 replaces plantation incentive with luxury-class and flat-grass/plains proxies for Observatory. | No exact resource-tag, ownership or Base+Specialty AND solution. |

Relevant core SQL is registered unconditionally in RH_AI_MAIN order600 and RH_AI_VICT order630. Advanced Lua has separate activation gates. ImportFiles is not proof of execution.

## What its new Builder logic actually does

core/Strategies/Advanced_Thinking/Features/AutoPurchase/RH_AutoPurchase.lua:

-1356–1425: classifies resources and obtains their valid improvement types from Improvement_ValidResources; checks improvement prereq tech/civic.
-1473–1610: scans owned city plots and scores potential work. Strategic resources receive high scores, then luxuries and bonus resources; empty hills/farmable tiles have other scores. Resource scores are not reduced by the population-minus-improved-plot slack factor used for generic work.
-1628–1665: ranks cities by improvement need.
-5561–5576: counts existing Builders; other sections apply era caps, cooldowns and purchase-budget gates.
-4521–4528 and6330: include Builder demand in purchasing and select the best-scoring city as spawn location.
-2576–2595: creates a unit and subtracts a script-calculated price. This is a scripted purchase path with its own pricing rules, not the normal production queue or necessarily a native purchase quote.
-7236–7291: another purchasing tier uses city ranking, Builder caps/cooldowns, era limits and reserves.
-Event registration near file end invokes the cycle for AI majors; AddGameplayScripts861 is gated to RH_AI_CONFIG_MP_COMPAT0or4 via RH_MPCOMPAT_MUTATORS_OK. Runtime MP gating applies too.

Important distinction: selecting the city in which to buy a Builder does not select a resource plot for an existing Builder to work. Package-wide searches found no BUILD_IMPROVEMENT / UNITOPERATION_REPAIR dispatch. Do not describe this as a replacement Builder job planner.

The scorer is not a complete CSC job feasibility check: a pillaged improvement is counted as already improved; improvement-unlock tests are not actual plot legality/path checks; it does not reserve jobs against nearby existing Builder charges. Map visibility/accessibility and feature-clearing requirements need explicit handling in a CSC scan. These are code observations, not claims that RH performs badly. README itself notes midgame idle units remain a beta issue.

## Other techniques and limits

RH_Economy.sql:39–80 and RH_MicroStrategies.lua:1384–1393,1476–1528 show a Call Lua Function strategy condition, GameEvents boolean callback and strategy-specific native AI lists. This is a useful pattern for switching preferences on only while a live need exists. A callback can know exact plots, but a player-level boolean/preference does not transmit a plot assignment to the native Builder planner. Repair priority and Improvements-system consumption in such a strategy need testing.

RH_General_Buildings.sql:126–134 attaches Engineer-GPP modifiers to Mines; RH_Culture.sql:89–99 adds positive/negative improvement GPP signals. Their RH_AI_ANCIENT_ONLY_REQ_S gate (RH_Congress.sql:134–147) requires AI, Ancient-or-later, before Medieval and Future Civic. They are normally inactive scoring shims, not ordinary real bonuses. Their existence does not establish that the AI forecasts CSC's valid conditional material bonuses. We have already tried a related conditional approach with inconclusive results.

Korea's RH_Districts.sql:494–513 defines Farm and Mine district-adjacency modifiers but attaches only Mine. It scores district adjacency; does not establish prospective Builder/repair behaviour. A named modifier is not evidence that it is attached.

Raw-resource private-yield rows are removed late by core/Other/Mod_Support/RH_Overhaul_Yields.sql:6–15 with BBG or StartBiasNegatives present, action order300000000. Claimed loaded outcomes must be checked after all compatibility passes.

No general improved-resource preservation guarantee was found. The old game facts remain: an intact Farm at100 preceded Wonder113; a Pasture was pillaged125 before HolySite135; the third Farm was already gone225 before Tailor236 and Theater240. These do not estimate conditional loss rates.

## Proposed route for CSC

1. Build a resource-work diagnostic first. Include all visible owned resources, using actual valid improvements and clearing prerequisites. Distinguish missing improvement, pillaged repair, locked tech/civic, unsafe/unreachable, and non-Builder improvements. Add CSC urgency for material resources beside an existing Quarter and for Services whose other gates are satisfied. Keep the scoring independent of Farm/Mine/LumberMill identity. Compare actionable work with nearby available Builders and charges; do not infer work demand from citizen count alone, since supplies can support Services even on unworked tiles.
2. Run a small prospective-scoring probe before another250-turn comparison. Does a private signal present only after an improvement increase the native value of that action? Does it affect repair? Compare a native yield-data case, a valid conditional resource case and the old-style modifier shim; inspect loaded rows and action outcomes. If the engine does not read it, stop tuning its magnitude. This is a renewed narrow hypothesis test, not a claim the earlier modifier issue is solved.
3. Independently test a modest raw-resource private signal as a preservation experiment. It can cover CSC-mapped bonus supplies as well as modded mappings without favouring one improvement type. Measure resource destruction, Quarter placement, citizen allocation and settlement side effects. It does not itself pay for improvement, and must not be presented as the fix for idle Builders.
4. If a native job signal works, use a Lua backlog strategy to activate it only while actionable resource/repair jobs exist. Keep Builder production at100 initially and general valuation90 as the current control. Try30 as a separate calibration arm, reflecting new RH, not simultaneously with the first targeting experiment. No type-skew weights.
5. Only if the native evaluator cannot target the work, prototype a small independent job helper for existing Builders. Validate the Lua context's ability to request legal native movement/build/repair actions first; RH does not supply that proof. Preserve ordinary costs, charges, turn ownership and pathfinding; skip unsafe or reserved units. No teleporting, free improvements or automatic replacement resources. This would be an explicit stronger intervention requiring separate review/testing.

Keep reciprocal sales guidance. The new RH code does not remove the native exact-material/AND-placement limitation. Preserve stage2/3 Base-supported access as the main objective; stage4 Specialty remains deliberately rare. Acquisition of more Builders is not currently the first intervention justified by our latest data.

For a first concrete development step, the diagnostic and scoring probe provide the most information at low test cost. Source patterns establish mechanisms to investigate, not comparative effectiveness. A Lua helper remains a contingency, not a promised turnkey solution.

Review boundary: RH code remains read-only and is not reproduced in CSC. Its beta license reserves copying/reuse; any implementation here should be independently authored, with permission sought before reusing RH material. No permission question is needed for this read-only review.
