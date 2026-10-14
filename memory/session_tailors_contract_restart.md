# Tailors contract-first restart

- Clean Tailors gameplay baseline committed as `0fcfe09`.
- Canonical Tailors design Markdown and existing art were retained.
- Existing optional-mod resource mappings to `CLASS_CSC_TAILORS_BASE` and
  `CLASS_CSC_TAILORS_SPEC` were retained and are validator-controlled inputs.
- Old Tailors gameplay SQL/localization/wiring and the first contract experiment
  were removed.
- Replacement workflow lives in `project/docs/quarters/QUARTER-CONTRACT-WORKFLOW.md`.
- Proposed contracts live in `project/specs/tailors/`.
- Contract validation command:
  `py -3 project/tools/quarter_contracts/validate_quarter.py tailors`.
- Existing Tailors SQL outputs are also checked against the Bakers-derived
  visual/architectural profiles in `bakers-sql-style.yaml`.
- Tailors is intended to become the normal Quarter reference after it passes
  static and runtime validation; Bakers then remains the specialized fallback.
- D.STAGE3 was implemented on 2026-09-07 and its gate is `ready_for_review`.
  The slice includes the Tailor, population-scaled Market/Temple exchanges,
  Sacristan, domestic trade-route effects, localization/UI previews, icons, and
  the Tailor alternate-art property bridge.
- Automated handoff validation passes with zero warnings; in-game acceptance
  remains user-owned under the contract.
- Stage 3 tooltip feedback on 2026-09-08 established a reusable presentation
  rule: authored building descriptions omit intrinsic Citizen slots,
  specialist yields, and local/regional Amenities because Civ VI renders them
  below the description. Cross-city transaction effects, including the Tailor
  trade route's +1 Amenity to the origin city, remain explicit.
- Quarter icon atlas positions are a reusable implementation convention rather
  than design data: district normal/FOW 0/1; stage 2/3/4 buildings 4/5/6; stage
  2/3/4 services 8/9/10. Tailors inherits the catalog default with no override.
- The Buildings ArtDef also requires a Quarter BuildingChain. Tailors uses
  CSC_TAILORS_BuildingChain with its district plus Textile Workshop/Tailor/
  Fashion House at Buildings Level 1/2/3 (corresponding to gameplay Stages
  2/3/4). Contract assertions are cumulative and permit only future levels to
  remain empty.
- Stage 3 Market and Temple sales stack by customer city and building family.
  A shared child Culture modifier and Lua deduplication by city alone collapsed
  a same-city Market/Temple pair to one transaction. The SQL now uses distinct
  Culture child modifiers and the shared population-return Lua deduplicates
  seller/transaction/customer-plot pairs, including in another city. The design, implementation,
  reusable customer-transaction contract, and Tailors validator encode this.
  The shared contract also requires future customer transactions to name their
  stacking unit; the generic contract validator checks that binding.
- Stage 3 population sales now use CSC_Stage3CustomerTransactions: one Bakery
  row and two Tailor rows. The shared Lua scanner reads these rows, expands
  direct customer replacements, and aggregates seller/customer population
  yields by the existing SQL property names. Stage 4 remains separate.
- 5 October 2026: Henno confirmed the current Cafe Lua plus SQL building-yield
  property-bit implementation as the canonical Stage 4 population-transaction
  reference. Both sides use floor(customer-city population / interval), rounded
  per customer site before summing. Do not revert to the original threshold SQL:
  its Culture side used the producer city's population. The Stage 4 implementation
  binding and generic validator now enforce the Cafe method and shared gameplay
  output; focused Lua fixtures exercise the unchanged Cafe script. Fashion House
  implementation and its Stage 4 semantic assertions remain pending under the
  existing phase gate. This contract amendment is not runtime acceptance.
- 5 October 2026 readiness review: Henno confirmed that the current design.yaml
  looks accurate while asking whether Fashion House gameplay can begin. Recorded
  approval of the current Stage 4 design slice and renewed the stale foundation
  and Stage 3 slice hashes against that reviewed design. Reconciled the canonical
  source hash after Henno's public-page edit shortened the Stage Manager slot
  sentence without changing the Theater-only slot rule. No runtime acceptance
  was recorded; Stage 4 implementation has not started in this readiness review.


## Fashion House implementation, 5 October 2026

Stage 4 and the foundation type obligations are ready_for_review; no runtime acceptance is recorded. Implemented Humanism Fashion House, local and Specialty input yields including M&C totals, customer-population integer bit transactions for Amphitheater/direct replacement and three named Wonders, independent domestic trade channel and both previews, persistent Stage Manager services, exact Wonder placement and actual-location UI, localization, icons and ModBuddy actions. Added executable Stage 4 assertions and production Lua scenarios; 91 regression tests passed. User-owned runtime review is documented in project/docs/quarters/tailors-stage4-review.md. Existing user art changes were preserved.

## Wonder Stage Manager correction, 7 October 2026

Henno reported supplied Fashion Houses beside Wonders failing to establish Stage Managers. The deployed Lua log confirms startup city collections were unavailable and unset native GetProperty calls returned zero values, causing tonumber(value expected) to abort reconciliation. Production placement now captures property results before conversion, defers until city collections exist, and refreshes on additional improvement/district/ownership events. Regression tests reproduce both failures before the fix.

Henno clarified that the four venue-specific Stage Manager icons should remain separate for now and that Fashion Houses belonging to different cities must stack at each adjacent venue. Split Culture and Artist-point attachment wrappers into Theater Square, Bolshoi, Broadway and Sydney subject gates, with one real Culture presentation anchor per venue. Each anchor uses its own existing icon (Tailors atlas 12–15) and notification text family; multiple sellers stack within a family. Canonical service Civilopedia target remains shared. No aggregate wrapper also delivers Culture. Contract, validator and review guide amended; 95 regression tests and Stage 4 handoff pass with zero warnings. Production MCUIS scripts are exercised with mocked GameEffects district subjects, including separate venues, two sellers, unchanged refresh, loss/restoration and persistence. This is not live-game acceptance.

No FireTuner listener was available. Installed icon mappings still use old index 10, and the deployed/cooked icon BLPs date from 5 October; a full ModBuddy build/cook is needed for the newer four-icon atlas and this source correction. No partial deployment was made.

## Wonder grant follow-up, 8 October 2026

Henno reports Ballet Dancer absent while the conventional Stage Manager works. The deployed placement script includes the 7 October fix and latest logs show no reconciliation exceptions. Found two remaining silent player-scan flaws: GetWasEverAliveCount was treated as an ID bound, and any player whose GetCities returned nil aborted the entire global pass. Added two failing regression scenarios, then switched to actual GetAlive player objects sorted by ID, independently skipping unavailable city collections. Retain previous markers for temporarily unavailable owners; ready markers for removed owners still clear. All 97 regression tests and Stage 4 handoff pass. Contract/review guide updated and a read-only live inspector added at project/tools/firetuner/inspect_wonder_services.lua. Live cause and successful grant remain pending inspection; no deployment or runtime acceptance is claimed.

Henno is loading a game for diagnosis. The game process has established debugger connections on 4318 (FireTuner2.exe) and 4319 (AssetEditor.exe), so a separate client cannot attach on the usual port. Requested that Henno disconnect FireTuner2 while leaving Civ running; do not kill or restart his test game or the tools to force access.

Henno disconnected FireTuner2 and live inspection succeeded. Pokrovka (player 0, city 65536) had supply=1, Opera and Ballet and adjacent Bolshoi/Broadway, but no services. Alive IDs were 0–14, 62, 63 despite count=17. Also found the native gameplay district collection lacks IsPillaged: use GetDistrict(index):IsPillaged() on the district instance. Added a regression fixture without the UI collection method; all 98 tests pass. Hotloaded the corrected production Lua into CSC_WonderServicePlacement (state 8): Ballet Dancer granted at Bolshoi plot 796 and Musical Actor at Broadway plot 794, exact matching host plots, with ready/established=1. UI GameEffects confirms active Culture attachment/leaf subjects for each. MCUIS yields separate correct venue icons and +10% Culture/+1 Artist point tooltips. Notification cache contains one stack each and remains stable after refresh. Sydney absent from save; shared path covered offline. User asked why these differ from working services: conventional Stage Manager is SQL granted; Wonder variants need Lua CreateBuilding(index, exactHostPlot), because SQL chooses the first Wonder district. Gameplay effects/presentation still use shared SQL/MCUIS.

Final Stage 4 handoff passes with zero warnings. Copied only the corrected Wonder placement Lua into the installed local CSC mod; source and deployed SHA256 match (9730EA8DCEA9CF7B0174F56C90044D82A7DDE3772D3DDF479963001BE30B7628). The running game already has the corrected reconciler and successful grants; no restart was forced. Full phase acceptance remains user-owned.
