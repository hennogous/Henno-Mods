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

## Revised source selection after archive inspection

The next diagnostic should use archived source16, not source1. Source1 has zero
cities, so a raw resource signal would change initial settling. Source16 is before
both confirmed harvest jobs, after the capitals are established. No source5 save
was retained; do not invent one or replay1..15 to create it. Source16 prefix is
prepared OFFLINE in `offline-preparation/source016-prefix/preparation.json`.

Source16 includes exactly one confirmed turn15 paid assignment (25AI Gold, no
fallback), no assisted foundation and75 research rows1..15. Restore those records
once; do not count them as new diagnostic effects. Native saved token15 must be
confirmed and all original future tokens16+ absent. Verify source16 pre-cycle
Gold (player2 72.39453125), full world/production and unit inventory. A complete
original16 unit/world census was not archived, so first take a separate zero-turn
CONTROL load of this exact save with the unchanged v2 package; compare the
subsequent treatment load against that control. Each load is separately one-shot;
no new host, resource-pass replay or unit/economic mutation in the control phase.
No pre16 actionable care job existed, so resetting observed job age does not
invent or discard an actionable waiting interval. Earlier duplicate-callback
counts remain UNOBSERVED; do not claim the new counter recovers them.

The bounded treatment is now intentional16..75 counterfactual replay, not1..75.
Keep the original225 result separate and do not add overlapping purchases,
research or physical sites across trajectories. World/ledger/clock mismatch stops
before advancement; prepare concrete control/loader/package/pins/audit gates
before any native execution. Raw signals can still affect later settling and
other decisions; record those differences and require the reference Quarter to
exist before calling retention a supply-chain success.


## Terminal192 and revised next diagnostic

The accepted v2 game ended at192 after observer defeat, with shipped OneMoreTurn
disabled/no winner. It is independently audited terminal partial, not225. Original
failed job/supervisor remain unchanged. See terminal192-report.md and independent
audit. Require final-normal-exit-and-pretest510.json before another native owner.

After closure, the next zero-turn source16 control establishes the missing exact
world/unit/gold/production/private reference. Then use TWO matched reloads from
the same16 source: unchanged v2 reference16..75 and raw-resource treatment16..75.
An unreloaded accepted main timeline alone is not a matched control for load,
observer/cache/planner resets. These intentional diagnostic counterfactual
trajectories are neither new worlds nor independent world samples. Common pre16
economic/research prefixes are inherited once per trajectory and never summed
with accepted main outcomes. No resource pass or pre16 AI turns are replayed.

Prepare concrete loaders, strict parity gates, package/source pins, worker/job,
one-shot funding ledgers and independent diagnostic auditors before advancement.
The SQL experiment remains unregistered and uninstalled until its isolated native
branch. Test Cattle2533/1573 jobs and future loss, actual improvement and native
reservation/harvest logs, functioning producers and settlement differences. Keep
exact price/Gold receipts; no resource restoration or direct Builder commands.
End each branch by normal exit/allCivabsent/original510/prefs verification.

Concrete pair harness ready (28 focused checks + AST/import/source/closure checks passed). Reference016-075 launched supervisor19288/worker9316/nativeDX12 12104, exactCIM identities verified. ONE exact16load; source parity required before actions. Maintained worker/controller/guards frozen. Source readback/control remains reference for21units/world/gold/production/economic/private/nativeDB. LIGHT source16/25/50/75 outcomes;1 andBuilder1/5 explicitly inherited. Independent auditor project/tools/ai_baseline/material_forecast_audit.py verifies current510 after normal exit, nativeDB/pins/sourceparity/funding0percent/completion/work/log/research370 minusdefeats. Require actual75 plus job/sup complete0 and auditor receipt before launching H/start-material-forecast.py raw-resource. Matched reference uses v2 guidance+paidassignments, not future no-intervention baseline. No raw treatment loaded yet.


## Additional native decision-path evidence (24 October)

The unchanged-v2 reload matches the accepted main physical/world/research signature
at25. Its independent native operation + unique tree-target reconstruction confirms
the same Cattle2533 harvest21, Farm job value4661. This is useful reference evidence,
not proof that the full later trajectories or internal unit states are identical.

A separate offline decision-timing analyzer now corroborates a stronger late case:
Joao/player4 Sheep2269 was recorded working at52 and a native150 census shows an
unpillaged Pasture.
A matching same-city Farm reservation is logged at152, native Remove Improvement
173 and Harvest Resource174 are recorded at49,30 on the SAME Builder5111809.
The independent UnitOperations names/enum rows corroborate both native operation
starts. Thus this is active replacement of an existing material improvement,
not merely missing Builder capacity or a repair not being selected.

All four confirmed Farm-harvest cases had prior care observations:2533 at18 before
matching reservation20;1573 at19 before26;1688 at73 before135;2269 at52 before152.
These are first observed same-player/plot/system reservations, not hidden queue
creation timestamps. The Sheep job was observed repeatedly over a long interval;
matching player/plot/system alone does not identify one persistent unit/job.
No private-yield value at the actual decision instant is invented from care logs.

Guidance implication: test native valuation of keeping the resource/improvement,
and inspect replacement/preparation operations. Raising blanket Builder output
cannot alone resolve a Builder removing a Pasture for a Farm. Raw resource yields
could affect representation AND earlier/broader signal timing; a positive paired
result will not distinguish those mechanisms by itself. Unowned resources and
later settlement can also change. Care activation predating observed reservations
makes an explanation based only on noticing materials too late insufficient.

New independent tools: material_decision_intelligence.py (6 counterexample tests),
material_forecast_comparison.py (6 tests separating endpoint retention, same physical
Quarter, own improved materials and functioning producers). Comparison refuses to
run as a completed pair without both independently audited75 trajectories.
No live executed source, native coefficients or assets were changed by this analysis.
Source evidence: run-01/offline-analysis/material-decision-timing192.json and
reference016-075/offline-analysis/loss-attribution25.json.

## 24 October: raw forecast startup reconciliation and citizen allocation

The reloaded reference completed75 and passed independent audit/cleanup:
136pins,370research rows,4foundations(2complete),7paid tiles260=121own139fallback,
including the inherited turn15 purchase25own. New effects are6tiles235=96own139fallback.
Both Cattle-to-Farm harvests21/26 were reproduced. Physical/world/research signatures
and counts match the unreloaded main25/50, but diverge75. Do not substitute the
unreloaded main for the matched reference.

The first raw-resource trajectory stopped at16 BEFORE AI advancement, purchasing
or placement because its source gate found observer0GDP production-.8984375 and
culture+.90234375. Independent source16 review verifies full world/21units/allGold/
AI1..5cityGDP+production/149realplotyields unchanged, expected private40/20, loaded
nativeDB onlyResource_YieldChanges, and normal exit/original510/prefs144false.
The original failure remains intact in raw-resource016-075.

Two subsequent zero-turn citizen investigations (source016-citizen-reference-v2,
source016-citizen-raw-v2) directly read shipped PlotInfo/CitySupport GetWorkerCount
and purchased-city plots. Both completed one source16 load and ZERO AI turns,
purchases, foundations or citizen orders; native packages/preferences restored.
Independent source16-citizen-allocation-audit.json confirms observer0 moved one
worker from2868(2Food/1Production/noresource) to3016Flax(2Food/1Culture/private+40).
Worked-yield delta(-1Production/+1Culture) corresponds to the derived city change.
All other cities' allocations/outputs were unchanged, as were all real plot inputs.
The original helper's full-packet equality flags were false because care refresh
changed private values; actual workers and city outputs were stable within each
arm. Offline semantic audit corrected this false negative without native reruns.
The first citizen-helper preparation typo Falseand occurred before runtime copy or
native launch; independent review proves zero effects, and its files were preserved.

Important correction to interpretation: a hidden yield with no currency conversion
is NOT necessarily economically inert for human players: it can change automatic
citizen allocation. The raw global resource signal is a broad mechanism diagnostic,
not AI-only release-ready tuning. Do not erase the signal or zero its DefaultValue
just to pass a gate: historical percent-bias experiments retain DefaultValue1, and
zero might also disable desired AI valuation. No ResourceModifiers table or native
Improvements AIList examples were found in this446-table snapshot; unsupported
systems must not be invented as fixes. Queue source-comment correction about human
inertness after the experiment; existing registered/native source remains archived.

Next: preserve before/after harness provenance, harden the reusable source gate to
record the directly proven observer allocation effect while retaining exact source
world/units/Gold/AIcityGDP/production/realplot/nativeDB/private guards. Collect actual
worked plots at the next startup. No explicit economic commands before parity is
true; no derived effects would be false. Use a new raw-resource016-075-allocation-v2
branch, never overwrite/retry the failed folder. Preserve matched reference sources
and its prior independent audit; any metadata-only controller updates need explicit
provenance and unchanged native-play AST. Fix reusable stale endpoint250/status
labels and make failure exports/log capture independent before the new worker.
The prepared raw513 package/20private rows remains unchanged; no new weights,
resource pass, Builder/citizen orders, economic grants or research/production forcing.
Compare actual endpoint75 plus logs, including valid alternative Quarter placements,
own improved supplies and producer/customer links; actual payments remain unobserved.
Goal/15-minute monitor stay ACTIVE; the test has not yet proved material preservation.


## 24 October: measured-allocation gate running; closed checkpoint25 comparison

The new raw-resource016-075-allocation-v2 trajectory passed exact source16,
149 real plots/private values,21units/all Gold/AI-city output/production/queues,
native446DB and saved economic-ledger checks. The only allowed derived city
output change is the previously measured observer0 citizen reallocation, backed
by direct worked-plot evidence. This is recorded as a treatment spillover, not
economic inertness. No explicit economic command or AI advance preceded parity.

Supervisor5856/worker19648/nativeDX1211564 were independently CIM-verified;
native39 was read back during this check and later progress is in live-status.
Endpoint75. All executed source/proof/archive pins are now frozen. The shared
controller endpoint status now respects study_endpoint; other native controls
and the worker action loop have unchanged ASTs. Failure exporters preserve
telemetry, nativeDB and logs independently.80 controller,25 focused,8 archived
native-schema checks and preservation fault injection pass. The before/after
provenance is H/forecast-allocation-v2-provenance.json. No live tuning edits.

Closed25 comparison: both trajectories have2foundations,5paid tiles170Gold=
76AIown94fallback (including inherited15tile25own),6cities/7Quarters4complete/
0producers. Population differs: reference28/raw30. Cattle2533 was still harvested
at21 in BOTH; care observation18 and Farm reservation20 occur in both, although
the logged Farm score changes4661->3858. This signal has not protected that case;
the score difference is not currency or proof of an isolated causal pathway.
Both show55care calls/0errors and the same urgent-strategy transitions through25.
Detailed immutable-checkpoint hashes/evidence are in current R/offline-analysis/
checkpoint025-comparison.json. Later turns remain sparsely captured by design.

Monitor csc-material-care-v2-test updated ACTIVE15minutes with actual live owner
identities/new source gate and audit instructions; exact returned receipt saved
in current R/monitor.json. At actual75+job/supervisor complete0 and native/owners
absent, independently audit accepted schema and original510/preferences cleanup,
then compare matched reference75. Do not rerun native for reporter assumptions.
Overall overnight investigation remains active; this early negative case is not
a release decision or universal preservation result. Preserve all art/unrelated work.


### Closed50: new native Mine/technology-boost losses

Both exact50 saves/checkpoints are verified. Current raw endpoint census has
10cities62pop/15Quarters11complete/1producer(1workingBase0Both); reference has
10cities60pop/14Quarters12complete/2producers(1workingBase0Both). Economics remain
2assisted foundations/5tiles170=76own94fallback through50 (shared15 included).
Both care exports205calls/0errors. Raw still harvested Cattle2533 at21, but does
not record the reference Cattle1573 harvest26 through50. This is not full endpoint
preservation proof.

Two new native confirmed harvest paths: Joao Sheep2269/turn45 and Tamar Sheep1647/
turn49. Matching Mine reservations were43/45 respectively, explicitly under
Seek Tech Boost TECH_APPRENTICESHIP; care had already observed develop36/28.
This is direct evidence of a competing technology-boost improvement pathway;
no hidden job creation time, private yield at decision instant, or isolated causal
utility effect is inferred. Raw signal has not made materials reliably safe.
Reference50 losses are Cattle2533/21, Cattle1573/26 and Maize2563/district occupancy47.
Broader citizen/production/settlement effects remain confounders. Current run
continues UNCHANGED to75; all native executed pins frozen. Evidence/hashes:
current R/offline-analysis/checkpoint050-comparison.json. Final independent75
comparison remains required before interpreting endpoint supply outcomes.


##24October: matched forecast75 audited; next scheduling hypothesis prepared

C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\docs\research\mods\csc-ai-material-resource-forecast75-20261024.md

Both source16..75 trajectories completed/audited/normal exit/original510/prefs144false. Raw globalBase40/Spec20 is NOT a preservation fix:3harvests vs2;0district-associated removals vs4, but cities12vs16/producers7vs8/workingBase5vs6,0workingBoth both. Raw retained Cattle1573UNIMPROVED, still harvested2533, and lostSheep2269/1647 to Apprenticeship Mine3 boost jobs despite ACTIVEcarestrategy. Current repair episodes4vs2 are descriptive/censored, not causal. Both370research/355carecalls/0errors. All native owners ABSENT. New union-loss comparator10tests+job-origin9testsPASS, no live native-source edits. Candidate514 boost/backlog preference SQL prepared/in-memory446table exact4table scope+idempotence, NOTinstalled/tested. Next branchboost-gate-v3 requires preserved harness provenance/current514auditor/strict source16measuredcitizenparity before one75counterfactual; no newworld. Overall goal/monitorACTIVE.


##24October: boost-gate-v3 native source16 passed, running to75

Branch raw-resource016-075-boost-gate-v3 launched ONCE with maintained diagnostic
harness, supervisor16660/worker18560/trueDX12Civ11500 (created01:35:13.811621+02:00).
Exact identities independently CIM-verified. All172executed sources/archives/
contracts/preparation/proofs/tests are now FROZEN; exclusive worker Tuner. No new
world, same source16 SHA, pre16 prefix inherited once, no recreated foundations.
Native16 source matched original validation and also matched the completed RAW
control exactly for world/21units/Gold/AI and observer city output/production/private
plot values/direct worked plots. Only loaded DB Resource_YieldChanges over512 plus
four declared AI-preference tables; same raw20resource40/20 in both control/gate.
Native18/inactive read back. See currentR/independent-boost-source16-confirmation.json.
Registration/application is NOT proof of native handler suppression or preservation.

H/forecast-boost-v3-provenance.json and H/before-boost-gate-v3 preserve exact ended
harness and offline auditor versions before extension. Sharedcontroller unchanged;
actual driver native action-loop AST IDENTICAL.34offline contracts/reporting tests+
actual446table expected-schema/six-runtime-delta/idempotence checks PASS; no native
calls during those tests. Source16 has zero AI advance/explicit economic commands
before parity. Original raw/reference audits remain executed-version receipts,
not a claim that their old pins equal the later harness. Temporary514candidate,
original510 final restoration after ALLCivabsent required; no production release.

New unpinned offline boost-gate comparison and native boost-log reader/tests ready;
24focused reporting checks PASS. It compares UNION losses of all classes in both
arms, maps actual helpful-boost log records while retaining native Progress labels,
and marks missing endpoint plots UNOBSERVED. No invented Mine counts, initial
boost states or attribution of a boost to one Builder job. Native control log has
no matching Apprenticeship boost record16..75 for the two Sheep-harvest players;
this is bounded log absence, not proof of an unboosted initial state or causality.
After ACTUAL75+job/supcomplete0/ownersabsent/original510/prefs144false, run updated
material_forecast_audit.py currentR then material_boost_gate_comparison.py rawControl
currentR --output S/boost-gate-comparison. No native reruns for reporter errors.
Overall goal/15minute monitor ACTIVE. Do not tune live pins or coefficients.


### Live boost-v3: exact checkpoint log boundaries and native strategy evidence

Native AI_Victories.csv directly records material-backlog Following2at20/1+3at21.
The offline boost-route analysis now records nativeFollowing/Stopped separately
from Lua callback results; unknown/future/same-turn ordering remain explicit.
Native Following does not by itself prove consumption of the false TechBoosts
preference. Some improvement-count boost routes occur while Following; existing
hidden commitments remain possible, so wait for actual75 comparisons.

Found and corrected an OFFLINE reporting edge: selecting completed-control logs
by numeric turn25 alone leaked rows after that checkpoint's next AI activation.
New material_checkpoint_logs reads the exact outcome byteEND with gap/conflict/
size/UTF8 checks. Both exact25routecounts are5 (not unbounded6vs5),2firstobserved
whilenativeFollowing. Actualworldsignature/economiccityoutputs identical25;
6cities30pop7Quarters4complete0producers, same CityFarm harvest2533at21. Original
pre-byte-bound report preserved; corrected receipt currentR/offline-analysis/
checkpoint025-boost-activity.json.19focused offline boundary/activity/comparison
testsPASS, no native rerun/calls/source edits. All172livepins still match.

Current R/monitor.json holds ACTIVE15minute automation exact returned receipt.
Later actual status/checkpoint50 if complete are in it; source16 job anchor is
not latest progress. New offline helpers/comparison are UNPINNED, nativeworker/
candidate/shared sources remainFROZEN. Do not rerun H native-schema test while
alive because it rewrites the pinned provenance receipt. Overall goal ACTIVE.


##24October: boost-gate75 closed/audited with no observed benefit

C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\docs\research\mods\csc-ai-material-boost-gate75-20261024.md

Actual75/job/supcomplete0;172pins/446DB/370research/355carecallbacks0errors; original510/prefs144autostartfalse/ALLCiv+ownersabsent verified. Same12cities92pop19Q18complete7producers5workingBase0Both4customerlinks3flags; same3harvests2533/21+2269/45+1647/49; same5tiles170=76own94fallback,3foundations2complete. Native strategyFollowing confirmed but false handler preference does not protect the cases; engine-ignore NOTproved. World/city-output equality allobserved16/25/50/75; research/boost exact equality in decision.json. New coarse native-harvest guard prepared only, selected5uniqueAItraits exclude0/all446tables only3modifiertables differ; NOTinstalled/tested. See native-harvest-guard diagnosticdoc; nextnewbranch requires preserved endedsourceversions and strictsourceparity, legalchanges investigated0advancebefore any actions. Do NOTrerunoldaudits ascurrentpinclaims after futureharness edits; archivedreceipts/sourceversions authoritative. Goal/monitorACTIVE.


## 24 October: native-rule startup and canonical-order repair

The existing shipped no-harvest rule attached once to the five selected AI owners
in both zero-turn v4/v4b preparations; five active native instances and three
stable owner readbacks were verified, excluding observer 0. No AI turn or new
purchase, donation or foundation occurred. The rule removed eight owned
Quarter/plot combinations across six resource plots and changed twelve source
projections. Hojo had no suitable owned Tailors location afterward. Resources,
units, treasuries, real yields, city output and queues stayed unchanged; direct
post-rule citizen allocation remained unobserved because validation stopped first.
This proves a placement-legality effect, not harvested-material retention.

The second preparation stopped only because Lua enumerated identical Bakers and
Tailors transitions in a different order. The original failure and 207 executed
pins are preserved. Independent review verifies semantic equality with v4 and
normal original-510/runtime/preferences restoration, all Civ and controller owners
absent, and zero AI/economic/foundation actions. The reusable validator now sorts
unique transition identities; duplicates, unknown changes, queue/gold/resource
and legality changes remain strict. Seventy-two checks pass, including both actual
archived source16 packets and actual Lua 5.1 safety fixtures. Native play and the
per-turn action loop AST are unchanged. Ended sources are archived under
H/before-native-rule-order-v4c.

Current same-save branch: raw-resource016-075-native-harvest-live-v4c, supervisor
9388 at dispatch. Read active-run and its job/supervisor/source-validation/current
handoffs for actual progress. It loads the exact original turn16 source once,
with no pre16 replay or recreated sites; previous two preparations advanced zero
AI turns. Runtime remains raw513; existing native rule is a coarse all-resource
counterfactual, not targeted preservation tuning or release-ready AI-only design.
Direct post-rule citizen parity and all source/economic gates are still required.
Planner obeys reduced native placement eligibility. CanProduce false can mean no
suitable owned location rather than a locked Quarter; this possible acquisition
chicken-and-egg gate is a later investigation, not a live policy change.

All current executed pins are frozen, including H/test-measured-rule-v4c-schema.py
and its generated provenance: do not rerun it while the worker lives. Worker owns
Tuner exclusively. ACTIVE 15-minute monitor receipt is in current monitor.json.
After actual75 and complete0/owner absence, independent offline audit and a new
native-rule outcome comparison are required. Compare all loss classes, working
materials, repair failures, helpful harvest/boost/growth/placement tradeoffs against
audited raw control; retained-but-unimproved Cattle1573 is a useful sentinel.
Overall overnight goal remains active; no native harvest benefit is yet proven.


### First native-rule checkpoint25: retention, not yet working supply

Current v4c source startup independently verified all418 source pins/archives,
five active owner1..5 instances with three stable samples, original world/funds/
queues/units/real-yield parity and direct post-rule citizen-allocation parity.
The worker progressed beyond16; exact25 outcome and closed log byte boundaries
are in independent-checkpoint025-comparison.json. Raw control has one confirmed
Cattle2533 harvest at21; rule arm has no observed supply-loss cases or harvest
operation starts through25 and still owns the Cattle. It is unimproved, as is
retained Cattle1573. Both arms6cities7Quarters4complete/3unfinished/0producers and
0working chains; population30 control versus29 rule. This is an early retention
result with growth difference, not a complete or universal preservation claim.

New UNPINNED artifact-only H/material-native-rule-comparison.py and
H/material-native-rule-checkpoint.py are ready. Five counterexample checks plus
actual completed-control schema dryrun passed; the final comparison dryrun used
a MOCKED rule audit and is explicitly NOT native-rule evidence. Real final
comparison requires both actual independently audited75 trajectories. It reports
union losses of all classes, seven sentinel plots, same physical and alternative
Quarter Base/Specialty links, working-improvement/producer proxies, missingness,
native boost records, repairs and exact-byte-bounded failed reserved-plot routes.
Failure routes do not identify hidden persistent jobs or prove their cause.
No current pinned sources were edited. Keep frozen worker running unchanged.
Goal and15-minute monitor ACTIVE; exact receipt/current monitor.json updated.


## Native-rule50: bounded action loops can resolve

See project/docs/research/mods/csc-ai-native-harvest-rule-progress50-20261024.md.
Exact50: control10cities62pop15Q11complete1functioningBase vs rule9/58/11/10/1;
confirmed material harvest losses3vs0; matchedrepairs3vs2. Protected Cattle2533
rejected HARVEST/BuildImprovement21..26 despite tree SUCCESS, then Pasture plan27
and exact-plot nativeBuild by DIFFERENT Builder589829 at28, working+Pasture50.
Not permanent idle. Sheep2269 working42/Pasture50 vs controlharvest45, but lastcharge
unit attribution remains ambiguous (2nativeBuildstarts). NonCSCStone1868 has
rejectedFarmroute43..49 with Builder851974 onplot/3charges50. Broadhardbantradeoffs.
New UNPINNED H/material-rejected-work-intelligence.py +test10checksPASS; finalH
native-rule-comparison extended with rejections/development/currentcarestate;
5comparisonchecks+actualcontrol-mockedschemaPASS, NOTnativefinalresult. Do NOTedit
livepins. PreppedUNINSTALLED source016-pasture-forecast (+80privatePasture direct
Improvement_YieldChanges, nativeBanOFF) is schema/idempotence/real-yields verified,
0observedPasturessource16; NOTdriver-ready/installed/native-tested. After75audit,
restoration, ownerabsence and preserving418sources, evaluate next experiment.
Goal/monitorACTIVE. Do not claim native working chain success from resourcealone.


##24October native-rule75 complete/audited; next forecast test prepared only

See project/docs/research/mods/csc-ai-native-harvest-rule75-20261024.md and
S/native-harvest-rule-comparison/decision.json. Actual75/job+supcomplete0/all
owners+Civabsent/original510hashes/prefs144autostartfalse/418pins/446DB/370research/
355carecallbacks0errors verified. Control3materialharvests vsrule0; rule6functioning
Base producers vs5/structuralsales5vs4, but Both0both, Q16vs19/completed16vs18;
cities13vs12/pop97vs92, not consistentgrowthcostclaim. MatchedCOMPLETEDrepairs3vs4,
1pendingeach (do NOTcountallrepair-episode rows ascompleted).2foundations2complete
vscontrol3/2; same5tiles170=76own94fallback, including15shared25own. Sheep2269
retained/Pasture/functioningproducer75; Cattle2533Pasture28 butBakerspillaged/no
producer75; Sheep1647+Cattle1573retainedUNIMPROVED. Native87rejectionlogrecords
vs65/7multiturnroutesvs3; notuniquejobs/requests. Do notshipcoarseallharvestban.
Promoted3maintainedoffline tools +2testfiles: material_native_rule_comparison.py,
material_native_rule_checkpoint.py, material_rejected_work_intelligence.py;
15counterexamplechecksPASS, actualschema/pathproofs retained. Canonical comparison
S/native-harvest-rule-comparison/maintained-report; originalHreport preserved.
Nextsource016-pasture-forecast (+80private directPasture Improvement_YieldChanges,
BanOFF) schema/idempotence/real-yields scopePASS, notinstalled/wired/native tested.
Nextactionpreservecurrent418sourceversions/receipt thenwireNEWv5branch through
canonicaldriver/variants/auditor/AST+sourcegates; no newworld or blind oldlaunch.
Overallgoal/15minmonitorACTIVE; no liveworker owns current sources afterexit0.


##24October directPasture v5 started; native source16 passed

R=raw-resource016-075-pasture-forecast-v5, sup16880/worker7228/DX12Civ4216;
identities verified. Native source16 world/gold/units/private/economic/queues/
production/legality/citizens EXACTLY rawcontrol;1load/0AI+economic beforeparity/
no reconstructed sites. Loaded native446DB only Improvement_YieldChanges extra
one Pasture+80private row; current514/sixruntime deltas, BanOFF/no legalityexception.
99offlinechecksPASS; sharedController/play/perturnloopASTsame. One read-only final75
private snapshot outside loop preserves rawUI74or75 inside separated inactive
Core75 boundaries and exact endpoint ownership/resource; not isolated80 proof.
All live176pins and ALLimports/tests/provenance frozen. Unused imported
native_harvest_rule.py missed conditional pin branch but unchanged from ended418
snapshot: supplemental-import-provenance.json/extra source-version copy cover it.
Do not hotfix live; independently verify final, then fix FUTURE pin builder.
Startup independent receipt verifies both. Never rerun H/test-pasture-forecast-v5-
schema.py while alive (rewrites pinned metadata). Goal/15minmonitor ACTIVE;
actual receipt R/monitor.json. Native choice-response remains PENDING.
Design csc-ai-pasture-forecast-diagnostic-20261024.md. Need new unpinned forecast
comparator; native-rule comparator requires ruleON. After75+complete0/ownerabsence
adapted audit plus supplemental provenance check, usual370research/censuses/native
funding/physical/material/source/private/DB/original510prefs cleanup. No native
rerun for reporters or new world.


##24October audited Pasture75 result; next staged only
Native75/job+supervisor complete0, owners/Civ absent, original510/144prefs restored.
Matched control5->7workingBase,4->7structural sales,3->0observed harvest losses;
Both0both. Cattle2533 first logged Farm20->Pasture20/working21/physical25+75.
No universal/AI-only claim; broad private80/allowners/human spillovers disclosed.
5foundations1complete/8tiles345=206own139fallback; ages/exposure differ.
Next Camp+Plantation extension staged uninstalled, driver/native proof pending.
Current176pins preserved; future helper pin fix made AFTERaudit, no oldcurrentpins
claim. See csc-ai-pasture-forecast75-results-20261024.md and maintained comparator.


##24October resource-improvement v6 ready offline
Pasture80 retained; add Camp80/Plantation80 only.515files/7runtime deltas, exact native table/scope/resource validity/source gates,116checksPASS. Canonical Controller/perturnloop ASTunchanged. Same exact16counterfactual75/no newworld, noharvestban/FarmMinebonus. Native response pending. Design csc-ai-resource-improvement-forecast-diagnostic-20261024.md. Allsources freeze after launch; do not rerun schema script alive because it writes pinned provenance.


##24October resource-improvement v6 launched
Current R raw-resource016-075-resource-improvement-forecast-v6, supervisor11316/worker15708/DX12Civ18472 exactidentities verified. Native loading; no sourceparity/advanceclaimed yet. All imported/executed sources/tests/provenance FROZEN. WorkerexclusivelyTuner. Sameoriginal16counterfactual to75/newworld0, Pasture+Camp+Plantation80/noFarmMinebonus/ban.116checksPASS; no nativebehaviorclaimfromofflinefixtures. Original510restoration pending whilecandidate515live. Goal/monitorACTIVE15min; exact updatereturn R/monitor.json.


##24October resource-improvement v6 launched
Current R raw-resource016-075-resource-improvement-forecast-v6, supervisor11316/worker15708/DX12Civ18472 exactidentities verified. Independent strictsource16/rawcontrol/world/private/citizen/gold/production/units andthreeactualnativeimprovementrows VERIFIED;180executed pins+archives exact. Native laterprogress mustreadliveartifacts. All imported/executed sources/tests/provenance FROZEN. WorkerexclusivelyTuner. Sameoriginal16counterfactual to75/newworld0, Pasture+Camp+Plantation80/noFarmMinebonus/ban.116checksPASS; no nativebehaviorclaimfromofflinefixtures. Original510restoration pending whilecandidate515live. Goal/monitorACTIVE15min; exact updatereturn R/monitor.json.


##24October v6 native progress and closed25 comparison
Independent startup verifies strict16/world/gold/units/production/private/citizen
equality versusrawcontrol, native446exactthreeimprovementrows,180pins/archives,
unused imported rulehelper nowpinned. Actualnative17inactive then36archived;
at36twofoundations/5tiles170=76own94fallback, nofault/stderr. Currentliveartifacts
may be later. All executedsources/testfixture/provenance FROZEN/exclusiveTuner.
New unpinned H/material-resource-forecast-comparison.py compares raw/v5/v6 only
at exactclosed25/50/75 snapshots/logbytebounds/research packets;9testsPASS.
Checkpoint25 validates repeated Cattle2533Pasture20/working21/retained25 with
harvestlegal, rawFarm20/oneconfirmedharvest. V5/v6eachoneworkingcareplot,
same7Q4complete/0producer, allarmsSugarlocked/Cattle1573nojob/Honeydevelop.
No extra Camp/Plantation improvement response yet25; don'textrapolate final75.
Reporter retains priorplans/physicalobs for resource plots missing currentlinks;
UNOBSERVED remains unknown, not falsezero/destruction. Finalauditpending.

Additional artifact-only v5 endpoint allocation review confirms Cattle1573
worked1/private100/3Food/purchasedcapital65536 while serving Bakers1648/city131073.
This excludes an unworkable/unworked-tile explanation at75; crosscitystructure
is NOT a proven cause of jobomission.10worked/actionabledevelop materialplots,
26unique ownedcareplots total; nearbyBuilders notidle/available/pathproof.
Evidence Rv5/material-allocation75-review/{review.json,review.md}.
No live edits/newnativeclient/newworld/probe/restart. MonitorACTIVE15min,
latest actual updatereturn Rv6/monitor.json. Overallgoal remainsACTIVE.


##24October v6 audited75; material-viability v7 offline next
All v6owners exited0/native75; independent180pins/native446/515/gold/0%/370research/
physical/log/private/census/original510/144prefs auditPASS. Six paired arms complete,
one source16world. Camp/Plantation add NOobserved material work benefit75 vsPasture;
physicalsignature/research/carehistorysame but AI1citizen allocation and ordinary
output/GDP changed (Silk2318private20->100), so NOTeconomicallyidentical/AI-only.
Finalnativecounts7Base0Both7sales;8tiles345=206own139fallback/5found1complete.
Newexactprecommit auditor covers5assistedsites, finds1falseBoth: Tailors2165 at69
relied on Silk2091 underCityCenter0. NaturalTailors2494 similarly Flax2421covered.
Stage1 attaches to improvements; careexcluded these, plannerdidnot. Fixed after
allownersended in observations/fundedLua/nativepurchase/nativefoundation plan+
commit/UIpreflight; futurelockedIrrigation opportunity retained.256checksPASS,
actualLua51/actualprecommit69, noNativecalls/installedchanges. NativefixPENDING.
S/offline-preparation/source016-material-viability cloned515/nativeDB unchanged,
readyfalse/driverunwired. NeedNEWv7variant/driver/auditor/sourceallowlist+pins,
notblindoldlauncher (oldmainpinallowlistrejects intentionalchanges). No v7 load/
newworld/reconstruction. Keepgoal+monitorACTIVE15min; sourceversions archived
H/after-resource-improvement-v6-preserved and before-material-viability-v7.
Design/results csc-ai-resource-improvement-forecast75-results-20261024.md;
canonicalcomparison and retrospective-material-viability.json authoritative.


## Final offline material viability checks and retrospective scope
256checksPASS/0nativecalls/0installedchanges. Exactprecommit audit covers everyplacement: main1920/7falseBoth, reference0/4,raw0/3,boost0/3,nativerule0/2,Pasture1/5,v6 1/5,allunknown0. The latter is the SAME2165/Silk2091turn69case acrosscounterfactuals, notindependentduplicatedoutcomes. BugdoesnotexplainallolderpoorBothrates. S/viability-retrospective-series.json preservesmatrix. v7same16prep existsUNWIRED/readyfalse; no nativeissued. Goal/monitorACTIVE; actuallatestreceipt Rv6/monitor.json.


## Material-viability v7 declared and launch-ready
Distinct same-source16 counterfactual to75; unchanged515runtime/nativeDB/funding/Controller/perturnloop. Only necessary district-free material eligibility/fresh guards change; future technology locks stillallowed.256guard+compat checks current;38additional source/config/schema checksPASS. Explicit oldmain-pin overrides classified against preservedv6/guard sources; notblanketpermission. Readycheck passes, native0atthispreparationstage. Design csc-ai-material-viability-diagnostic-20261024.md. Freezeallimports/tests/provenance afterlaunch; independentnative/auditproof remainspending.


##24October v7 strict native source16 passed
Current R raw-resource016-075-material-viability-v7, supervisor1712/worker11664/DX12Civ5728 exactidentities verified. Source16 equalparent fullworld/Gold/units/production/private/citizen, same515runtime/native446DB, exact3forecasts;192currentpins/archives and materialguards verified independently.1load/0pre16replay/0reconstruction. All executedsources/tests/provenance FROZEN, exclusiveworkerTuner. Native laterprogress mustreadliveartifacts; fixingfalseBoth nativeeffect pending untilactualplacements andlatecase/audit. No oldv6currentpin claim. Goal/monitorACTIVE15min.


##24October v7 positive native placements and closed25 comparison
Actual28inactive recorded;2native0%foundations have exactprecommit district-freeBoth, nativeexport require_both_materials=true, positiveunchangedcost/queue proof. early-native-positive-foundations.json preservespositiveevidence. This verifiesvalidsitesstillwork, NOTlate69falsecaseprevention/universalsafety. Closed25comparison countsidenticalparent:6cities29pop7Q4complete0producer; exactsource/runtime/DB/pins stillverified. NewH/material-viability-comparison.py prepared/tested3counterexamples (zeroactions cannotprovefix, missing/failedprecommitnevergreen). Alllive192pins remainFROZEN, no competingnativeclient or sourceedits. Currentgoal/15minmonitorACTIVE, actual75+audit/latecase/cleanup/synthesispending.
