# Overnight material-access investigation —23 October

Objective: run evidence-directed tests and improvements to secure/protect Quarter
materials, with enough native data to diagnose AI decisions. Goal remains active.
The previous goal turn was a verified wait (exact live process identities); this
turn made progress by recovering the native harvest decision path and adding a
tested, offline-only attribution tool. Do not call the goal complete from tests,
partial progress or a finished game alone.

## Current phase: preserve the v2 outcome game

Complete the current frozen run to225, unless an actual blocker requires
preserve/reconcile recovery. Worker10500/supervisor18868/DX12Civ16996 were verified.
No competing FireTuner, live source/asset edits, new host or midrun coefficients.
Human-requested15-minute progress updates remain active. The monitor reads actual
artifacts; generic live-state endpoint250 is stale, declared225 is authoritative.
Perform the full independent audit/report/normal exit/pretest510/preferences
restoration before any follow-up diagnostic. Do not overwrite the current branch.

## Evidence recovered during the run

Through100, the9 supply-loss records separate into2 confirmed native harvests,
6 resource removals with native district occupancy at the loss, and1 ownership
change with the resource still present. District occupancy is not proof of a
permanent Wonder or completed building. Two exact cases:

- Player1 Cattle2533 at21: native improvement job FARM/value4661, reserve/move to
  17,34, Clear Plot with Builder327683, native HARVEST_RESOURCE, then Farm built.
- Player2 Cattle1573 at26: FARM/value5288, reserve/move to19,21, Clear Plot with
  Builder458755, native HARVEST_RESOURCE, then Farm built.

Both Builders had spent their last charge and reported position-9999,-9999 in
UnitOperationStarted. Direct coordinate-only matching falsely left these unknown.
The native event, unique tree target and UnitOperations log now establish the
path. Queued requests alone never prove completion; ambiguous unit targets stay
unresolved. Seven counterexample tests cover these attribution boundaries.

Native schema also exposes an AI behavior-tree Lua condition, but only passes
player, not plot. It therefore is not a verified spatial harvest guard. The Maori
prevent-harvest modifier is COLLECTION_OWNER/player-wide with Enable1, not a
per-material plot predicate. Do not present either as an implemented targeted fix.

## Next bounded mechanism diagnostic, after closure

Hypothesis, NOT established: native improvement/clear forecasting may handle
raw Resource_YieldChanges differently from conditional plot modifiers. Current
native yield application and saved-turn recommendation checks do not prove
forecast response. RH's direct resource-yield approach motivates the test; its
strategic/luxury examples do not themselves prove bonus-resource harvest safety.

Prepared isolated SQL: project/tools/ai_baseline/experiments/material_resource_forecast.sql.
It adds raw private Base40/Specialty20 (Base wins overlap) through the existing
UI-filtered YIELD_CSC_AI_PLACEMENT. It is NOT registered in CSC's project, installed
or activated. Three boundary tests pass; twice-replayed native-schema copy gives
20 private rows and preserves all57 economic resource-yield rows. These are
preparation tests, not native AI or preservation proof.

After full current closure, prepare a NEW diagnostic output branch using the
current run's exact post-cycle1 save. First verify no economic/foundation action
occurred at1, full world/treasury/material/unit/production/source identity, expected
private-yield delta and native DB delta limited to Resource_YieldChanges. Reuse
canonical controller and acquisition/planner; do not create a new host. Declare
this an intentional counterfactual replay of1..75, separate from accepted v2
outcomes, not a recovery with zero raw replay or additional independent world.
Keep the resource pass already saved at1; never reapply it. No ambiguous economic
retries, new weights/orders/research or direct material restoration.

Endpoint75 is bounded around the two harvest cases and early district replacements.
Capture exact economic/placement receipts, primary1/25/50/75, Builder1/5/50/75,
material-work/strategy histories and archived tree/unit-operation logs. Compare
whether the original Cattle are retained/improved, job choice and value, harvest
attempts, other resource loss, functioning producers, settlement/city differences
and overall work backlog. Raw resource signals affect unowned/other planning too;
this is a mechanism diagnostic, not a targeted production-ready rule or causal
comparison of the whole mod. Do not silently adopt it. Preserve all sources and
restore the original pretest package/preferences after normal exit.

Do not launch the diagnostic from this plan alone: prepare concrete loader,
package, pinning, parity gates and audit first. If the native delta/parity fails,
stop/preserve and diagnose; no blind load or reroll. Additional coefficient tests
need new evidence from the bounded result; no unbounded trial sweep.

## Completion evidence still required

Current225 complete+independent audit/restoration; exact log attribution across
observed checkpoints; native evidence for the forecast hypothesis; documented
improvement or documented failure/limits with the next defensible guidance;
reusable tests/data capture; final report and all normal cleanup. A passing SQL
fixture or a single repaired tile is not the full objective.
