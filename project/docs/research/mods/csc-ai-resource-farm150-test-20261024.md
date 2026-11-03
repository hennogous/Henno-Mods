# Resource-only Farm and Plantation test to150

Human24October: test an incentive like the promising Pasture signal on Farms and
Plantations, run to150, give terrain-only Farms no extra value, and inspect AI
logs both for value application and for changed decisions. This scoped test is
authorized; the broader overnight investigation remains paused.

## Treatment

Keep the existing Pasture/Camp/Plantation private80 and raw-material40/20 settings,
careLua3, Builder50/improvement30/urgency, own-first shortfall funding and legal0%
foundations. Add one Farm ImprovementModifier private80 with a native resource
predicate. Eligible resources are Farm's Improvement_ValidResources vocabulary:
Rice, Wheat, Maize and CSC Flax in this build. A Farm on terrain alone receives
zero extra; a Farm over Niter or a proposed Farm replacing harvested Cattle does
not qualify. Flax counts once despite its use by two Quarters. No flat Farm
Improvement_YieldChanges row is added.

Farm is not natively resource-bound like Pasture/Plantation, so simply copying
the flat80 row would violate the user's restriction. The conditional modifier
must be separately tested for native application and hypothetical AI forecasting.
SQL registration or offline predicates do not establish either behavior.

Candidate516 changes eight paths relative to the archived original510 runtime.
Native schema replay/idempotence, source counterexamples, native-style Lua value
controls and finite-driver checks pass15 focused checks. No real yield, native
improvement legality, Farm resource list, harvest ban or technology rule changed.
All-owner private signals can indirectly alter ordinary citizen allocation;
this is not an AI-only production deployment.

## Starting point

The source16 preflight loaded the new conditional rows correctly but every
existing resource Farm retained its prior value. It stopped before any AI turn,
purchase or foundation. Independent review verified original source16 physical,
Gold, unit, private and production parity and normal exit/original510/prefs144.
Existing serialized improvement attachments are a hypothesis, not a proven cause.

The test therefore uses the preserved initial1 save, before any city or
improvement exists. SHA256:
`9a9e94c37183710663dae7b2a47db95c197f1e0ed571033e688c43927a9cefb2`.
No map is generated and the resource pass is not reapplied. Same map830405 /
game940411, Ancient/Online/Prince/Continents Small, Tomyris0 and the five AI majors
Amanitore/Tamar/Genghis/João/Hojo. Full initial world/hash/AI cash, setup before-
after units/world/Gold, native446 DB and516 runtime checks precede advancement.
Historical full non-Builder1 inventory is missing; fresh setup censuses do not
fill that historical reference. No old outcomes or purchases are inherited.

The new rule is present before natural Farm construction. At1 there is no native
positive Farm control yet: report application pending, not zero or success.
Starting at1 also changes the first15 turns' treatment timing versus the old
source16 arms. Historical comparisons are descriptive, not a pure Farm effect.

## Logs and outcome evidence

Every turn retains fresh native readiness, compact work/research/Builder observers
and exact one-shot funding/zero-progress receipts. LIGHT full outcomes1/25/50/75/
100/125/150, Builder5 extra, no deep per-turn profiling. Expected745 unique AI
research observations1..149 minus explicit defeats. All current censuses are
post-action safe boundaries, with first1 explicitly a reload census.

Read-only UI controls at closed outcomes identify isolated unpillaged Farms:
no care property and no adjacent CSC Quarter. An eligible resource Farm must
report raw-resource private value plus80; a terrain-only Farm must report0.
Control absence is unobserved. A contradictory control preserves the exact save
and stops before another AI turn. Gameplay and UI getter domains remain distinct.

AI_Behavior_Trees reservations and job values are parsed separately from native
Builder starts, care transitions and physical checkpoints. Track Farm/Plantation
job choice, reservation and execution; preserve rejected routes; watch harmful
harvest/removal/replacement, improvement/pillage/repair and working Base/Both
chains. NodeSUCCESS, callbacks, nearby Builders and loaded rows are not proof of
execution or incentive consumption. Customer-building links and Service flags
are not logged payments. Closed byte boundaries exclude later same-turn logs.

Reviewer: H/resource-farm150-review.py R --through CLOSED --output report.json.
Baseline overlap16..75 is explicitly labelled; first-log timing is not hidden
job creation time. Do not merge overlapping trajectories as independent samples.

## Run and closeout

R: Desktop study `resource-farm001-150-v9`. Read study active-run, current context,
job/supervisor/live/active-command and short logs. Canonical maintained Controller,
finite autoplay and one-shot transport only. Worker exclusively owns Tuner, all
executed imports/tests/helpers/provenance/SQL/Lua frozen while alive. No forced
research/production/improvement/unit/building orders or grants, no competing client,
Computer Use, subagents, live asset edits, rehost, new seed or deployment.

Existing scoped monitor is active every15minutes, with a human update each check.
Stop at actual150; no automatic extension or revival of the paused broad goal.
After job/supervisor complete0 and owner absence run independent offline
`material_farm_start1_audit.py`. Report values landing, AI choices and actual
actions as separate findings, plus material retention and chain outcomes.
Repair reporters offline, never rerun native for a report assumption. Supported
normal Menu exit/all Civ absent, original510/eight paths restored and native144
preferences/autostartfalse verified. Preserve art-source fixes and unrelated work.
Then report and pause/stop this scoped monitor with its actual receipt.

## First closed25 native evidence

Initial1 source/pins/516 runtime/native446 definition scope and exact live process
identities were independently verified. The run progressed past25. Native UI
positive controls: Maize1459, Rice1531 and Flax2604 each report120, comprising
raw resource40 plus new resource-Farm80. Three isolated terrain-only Farms report0.
All six controls pass; no value is inferred from missing observations. Plantation
construction/value controls have not yet been observed at25.

Exact closed AI logs show Hojo's Maize1459 Farm job at2 value5448 versus4644 in the
historical original512 run at the same turn. Amanitore's Flax2604 Farm first logs
at11/value5451 versus13/value4634. Hojo's Rice1531 Farm logs at13/value5479; none
is observed through25 in that historical log. All three plots physically have
working resource Farms by25. Actual native Builder start records through25:
16 build-improvement,2 repair,0 harvest-resource,0 remove-improvement. These are
operation-start records, not unique completed material jobs.

The reference differs by the whole forecast bundle and treatment timing; these
are observed job-value/reservation changes, not isolated proof that Farm80 caused
the entire numeric difference. Existing Farm jobs can remain the same type with
higher score. The next question is how selections/execution/supply chains persist
through150. Do not call the first positive value check a completed test.

At25:6 AI cities29population,6Quarters2complete, no producer buildings yet;
2assisted foundations and4quoted acquisitions145Gold=63own82fallback. Early Quarter
completion is not an established win; broader material/city-production tradeoffs
remain in the150 outcome. Exact logs/receipts and raw comparisons are retained.


## Host poweroff and bounded same-save134 continuation (24 October)

The host powered off at07:55:13UTC (System1074 winlogon, EventLog6006), then booted
at08:13:22UTC. The original supervisor8872, worker13492 and DX12Civ13544 were absent;
no Civilization Application fault was observed. Their stale running artifacts are
preserved unchanged. Last actual read134 was active toward135. All213 source pins
and candidate516 runtime hashes matched; all17 paid effects and7 foundation begins
were closed. Costs830=448AI own+382fallback. Turn134 intervention actions were empty.

The human said 'sorry for interruptions, go ahead'. A separate same-world branch,
resource-farm001-150-v9/resume-134-poweroff-v10, loads the latest autosave134 once,
SHA69a4f267b5401386995999dfaf933ea7ebe150bd9d150f909b6c68c5013e33bd.
The controller, SQL/Lua, planner, funding and all original sources are unchanged.
Known-fact readback already matches all5 AI treasuries,29 city identities,27 fresh
city scopes and1621 plot-scope records. Two stale scopes and unavailable134 full
building/unit/UI-progress references are explicitly not represented as exact
full-world parity. All17 saved Game-property economic ledgers and7 physical sites,
native446/candidate516 and resource/terrain Farm controls gate any new advancement.
Read the child resume-validation/job/live artifacts for the later gate result.

Source134 had no intervention actions; first new cycle135. The interrupted raw
134->135 interval is discarded/replayed and disclosed; accepted outcomes count
once. Research/Builder/care observer125..133 records were not exported before
poweroff:45 research observations are UNOBSERVED, never manufactured. Existing
620 research rows1..124 and observer prefixes are inherited once; care ages reset
on reload under the existing design. Completion events in the gap can be missing
even if later physical completion is observed. No site recreation or purchase
resend is permitted. Source134 known-fact tests6 pass offline; no new native world.

Final offline continuation auditor is H/farm134_final_audit.py CHILD. It checks
actual150, parent provenance, known134 parity, ledger/0%proofs/pins/native controls,
observed coverage and restoration, while retaining the45-row gap and refusing a
full dense-observation pass. Do not use the pinned fresh-only auditor unchanged.
Native logs after reload form a separate byte generation; an offline report must
merge parent records through133 with child134..150 and discard old partial134.
Do not mix overlapping gzip offsets or invent continuous care observations.
Endpoint remains150, then normalexit/original510/prefs144/audit/report and stop
the scoped monitor. The broader overnight goal remains paused; no extension.


## Final150 completed and independently checked


The game reached actual150, both controller processes exited0, Civilization
exited normally, and an independent offline audit verified the observed checks.
The original510-file runtime and144 mod preferences/autostartfalse are restored.
The test is finished; no extension or new game is scheduled.

| AI1–5 outcome at150 | Result |
|---|---:|
| Cities / population |31 /324|
| Quarters / complete / unfinished |49 /46 /3|
| Producer buildings |41|
| Functioning producers with improved Base |13|
| Functioning producers with Both |5|
| Functioning producers with structural sales links |13|
| Service-property instances |10|
| Assisted foundations / complete |7 /6|
| Acquired tiles |17|
| Quoted cost / AI funds / fallback donation |830 /448 /382 Gold|

Acquisitions remain assisted Gameplay city assignment plus exact native-quoted
treasury debit. They are not proof of native AI PURCHASE authority. All17
economic effects and seven zero-progress foundations have matching proofs;
no purchase or foundation was repeated during recovery. The final immature
Tailors foundation127 is censored at150, not scored as an eventual failure.

## What landed, and what the AI did

At150 seven isolated eligible resource-Farm controls have their expected private
value;81 isolated terrain-only Farm controls have zero extra. No control fails.
Across the run this verifies actual application of conditional Farm80 on valid
Rice/Wheat/Maize/Flax and excludes an extra blanket terrain-Farm reward. These are
value controls, not81 uniquely tracked decisions or a ban on normal terrain Farms.

Closed logs show higher Farm job values and earlier/new resource-Farm reservations
than the historical512 same-initial-map run (examples remain in the initial-map
first-jobs25 receipt). Native Builder starts matched actual supporting Rice/Flax/
Wheat Farms and Silk/Sugar/Banana Plantations. The accepted log report separates
355 build-improvement Adding records and24 repair Adding records from completed
work; neither count is a unique successful job count. The whole forecast bundle
and first15 treatment timing differ, so an isolated causal Farm80 gain is unproven.

Six assisted Quarters had producer buildings; four had a working Base proxy
(4/6). Naturally placed Quarters had9/35 producer buildings with this proxy.
This is descriptive within one intervention pilot, with different site selection
and ages. It is not a controlled gain estimate or a substitute for the future
zero-intervention baseline. Six assisted sites still owned Both resources, but
ownership alone did not guarantee improved, unpillaged material supply.

## Preservation and repair remain the constraint

Tamar and Amanitore harvested Cattle for Farm jobs; Hojo harvested Bananas for a
Mine task under the Apprenticeship boost. Those earlier cases have matching
native operations, AI tree targets and resource disappearance. Other supporting
resources were removed with district placement. Joao's Flax2489 is absent at150
with Wonder-district occupancy; no permanent completed Wonder or exact removal
turn in the shutdown gap is inferred.

There is a clear repair response: Genghis's Rice1619 has a native repair start at
139 at the exact plot and a repair-to-working transition. It was pillaged again
by143 and remains pillaged at150. Amanitore's Cattle2533 Pasture is also still
pillaged at150. These are observed AI repairs/maintenance failures, not proof
that our incentive caused a decision or that nearby Builders were idle.

Of10 working owned material links observed at75,6 are working at150 and at each
sampled75/100/125/150 checkpoint. Of21 such links at125,18 remain working at150;
the three lost links are the Rice1619 and Flax2316/Wheat2389 pillages. Links count
per Quarter, so a shared resource can count more than once. Samples do not prove
uninterrupted retention between checkpoints, and the cohorts are small.

## Coverage and interpretation

The host powered off during134->135. Exact saved134 passed five-wallet,29-city,
27-fresh-scope/1621-plot-record, seven-site,17-native-ledger, native446 and Farm
value-control checks before continuation. Full134 unit/building/UI-progress
reference was unavailable; no full-world exact-parity claim is made. The raw
interrupted partial134 interval was discarded/replayed; accepted outcomes count
once. No site reconstruction or economic resend occurred.

Research observers retain700 actual rows;45 rows125..133 are UNOBSERVED. Builder,
care and some completion-event observations in that interval are also missing.
Earlier closed1/25/50/75/100/125 and final150 outcomes are retained, with care
ages reset on reload by the existing design. Thus observed audit checks passed,
but full_dense_observation_pass=false. Parent<=133 and child>=134 native logs are
merged as separate byte generations; the old partial134 log interval is excluded.

Service-property flags and structural customer-building links are not measured
monetary transactions. Actual Service payments remain UNOBSERVED. The practical
result is encouraging resource development and functioning Both chains, with
harvest/district competition and repeated pillaging still defeating soft care.

Evidence: independent-continuation150-audit.json, accepted-log-review150.json,
final-report.json, final-restoration.json and preferences-restoration.json.

Final scoped monitor csc-material-care-v2-test deleted after report and verified restoration; actual deleteStatus=deleted receipt retained in the child monitor.json. No extension or replacement monitor.
