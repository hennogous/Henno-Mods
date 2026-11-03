# Industrial Zone: observed prerequisite value and production boundary

Date: 1 November 2026. Follow-up to the
[offline architecture investigation](civ6-industrial-zone-planning-architecture-20261101.md).

The native AI **does add future Factory value to Workshop value while Workshop
is missing**. Three observed evaluations in Toulouse reproduce the exact integer
arithmetic identified offline. That establishes a working prerequisite-value
channel. It does not establish a persistent Factory-rooted construction plan.

The same short observation also separated a building-category selection from
actual production: after completing an existing Factory, Nicomedia's selector
returned Lighthouse, while a district contract started a Neighborhood.

## Scope and evidence

No fresh world was generated. The shared full-game controller loaded the existing
`CSC paired AI game 04 turn 250 20261016.Civ6Save`, advanced three one-turn
intervals to boundary 253, and closed the game normally. No production was forced,
technology granted, building added, queue cleared, or weight changed.

This was a **diagnostic rebase onto the currently installed CSC**, not a
reproduction of the historical performance arm or an unmodded-AI benchmark.
Current CSC contains 632 files and 156 loaded building definitions. The loaded
`CSC_AI_Profile` was OFF; assistance counters, pending work and turn records
remained unchanged. The callback-removal branch was therefore unnecessary and
did not run. Current custom buildings remained real competing alternatives.

The exact save SHA-256 was
`ea818368130273e02e70e31449a6f24a54e34486b8bfa402dd34b62255443e48`.
The loaded XP2 GameCore SHA-256 was
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`,
matching the Ghidra/REA target used in the offline investigation.

Raw evidence is under
`C:\Users\Shadow\Desktop\Codex\csc-iz-boundary-20261101\`:

| Evidence | Location relative to that directory |
|---|---|
| Declared probe, exact inputs and archived source | `run-02/protocol.json`, `source-pins.json`, `source-version/`, `dependency-pins.json` |
| Loaded definitions and source eligibility | `run-02/source-loaded.json`, `source-gate.json`, `loaded-module.json` |
| Physical state at every boundary | `run-02/boundary-251.json` through `boundary-253.json`, `final-boundary.json` |
| Paired native calls, frozen before menu | `run-02/observer/trace-snapshot-003-turn-253.json`, `trace-counts.json` |
| Native logs after normal exit | `run-02/logs/closed/` |
| Closed gameplay database and query receipt | `run-02/database/DebugGameplay.sqlite`, `queries.json` |
| Recomputed arithmetic, catalog mapping and parsed CSV rows | `analysis.json`, produced by `analyze_observation.py` |
| Independent native/call audit | `offline/independent-run02-final253.json`, caller extracts alongside it |
| Independent preservation/closure audit | `offline/independent-run02-closure-audit.json` |
| Closure and restoration | `run-02/result.json`, `session-closed.json`, `preferences-restored.json`, `final-inventory.json` |

The first launch, retained as `run-01`, failed during its source read because
Gameplay CityDistricts lacks the UI `Members()` iterator. It advanced no AI turns
and attached no hooks, then closed normally. The corrected reader uses the
documented `GetNumDistricts`/`GetDistrictByIndex` API. Thus this work involved two
loads, one useful three-interval observation, and zero fresh worlds. The failure
is retained rather than counted as a negative AI result.

## Two deliberately different city states

Always join a city by **player and city ID**; this save reuses IDs across players.

| Source fact at boundary 250 | Toulouse | Nicomedia |
|---|---|---|
| Identity | Player 4, city 262147, center (52,40) | Player 2, city 589832, center (46,18) |
| Industrial Zone | Plot 3160; complete, unpillaged | Plot 1304; complete, unpillaged |
| Workshop | Missing | Present, unpillaged |
| Factory | Missing | Missing, already in production |
| Current production | Flood Barrier | Factory |
| Apprenticeship / Industrialization / Electricity | All researched | All researched |
| Class Struggle | Not owned; boost getter returned false | Owned |

The current database retains Factory's Workshop prerequisite and both buildings'
Industrial Zone prerequisite. It also contains Japan's Electronics Factory as a
Workshop dependent and Factory replacement; its trait belongs to Japan. The
observed players are the historical France/Byzantium pair, rather than Japan.
The measured integer equality below is direct observation, independent of an
assumed contribution from an unrecorded replacement score.

Toulouse was suitable for testing propagation into a missing Workshop, but its
occupied production slot did not provide an immediate construction decision.
Its unowned Class Struggle also leaves a possible civic-boost motive uncontrolled.
Nicomedia supplied a natural completion/queue-opening boundary. Its Factory had
been selected before this probe and cannot be attributed to the observation.

## Exact backward-value arithmetic

The observer paired entry and return of `CalculateDistrictValues` at RVA `3dfee0`
for these two cities. It checked owner/ID, city coordinates, the first cache row's
building-vector alias, bounds and return identity. Values below are the raw signed
fixed-point score integers labelled Q8 by the observer; they are not yield totals.
Boundary 251 contains the preceding native AI turn 250, and so on.

| Boundary | City | Workshop entry | Factory entry | Workshop return | Workshop change | Factory return |
|---|---|---:|---:|---:|---:|---:|
| 251 | Toulouse | 29,833 | 219,970 | 249,803 | **219,970** | 293,017 |
| 252 | Toulouse | 29,833 | 219,970 | 249,803 | **219,970** | 293,017 |
| 253 | Toulouse | 29,833 | 230,875 | 260,708 | **230,875** | 314,503 |
| 251 | Nicomedia | −2,559,744 | 997,520 | −1,562,224 | **997,520** | 1,517,790 |
| 252 | Nicomedia | −2,559,744 | 1,039,845 | −1,519,899 | **1,039,845** | 1,609,047 |
| 253 | Nicomedia | −2,559,744 | −2,559,744 | −2,559,744 | **0** | −1,505,906 |

All six calls satisfy:

`Workshop_return − Workshop_entry = max(0, Factory_entry)`

This matches the direct-dependent pass decoded offline. In Toulouse the future
Factory contribution enters Workshop's score despite Workshop being absent.
In Nicomedia it is also added to the already-built Workshop's sentinel-like
entry, `−9999 × 256`. Aggregation and construction eligibility are separate
operations; adding value to a cache entry does not make that building available
or desirable to build again. After Factory completion, its negative entry adds
nothing to Workshop.

Factory's value also changes during this function, but Workshop receives
Factory's **entry** value, not its larger return value. This is consistent with
the definition-order pass: Workshop is index 17 and Factory index 24. It supplies
a concrete example of why this pass must not be described as a fully recursive
solution of the entire prerequisite chain. The additional components of Factory's
own change were not individually instrumented.

The observer does not independently establish how freshly every input was
calculated before entry. Repeated entry resets and the completion transition
support interpretation of these observed evaluations; they are not a general
cache-freshness invariant. This was observation, not a score intervention or an
estimate of how much Factory causally changes production choices.

## Selection and actual production

There were six target `GetBestBuilding` calls. Five returned to RVA `3ea73b` in
`UpdateBuildQueueForThreat`, with raw flags 1/0. Archived assembly proves that
caller and register setup. These calls are not the ordinary
`CheckForUnitOrBuilding(...,0,0)` route inspected offline.

Toulouse's three update-route calls selected index 139,
`BUILDING_CSC_BAKERS_WIND_MILL`, score 6,569,594. Its production remained index
112, `BUILDING_FLOOD_BARRIER`, throughout. A selector return is not evidence that
the selected item was ordered, nor that Workshop would have won with an empty
queue. There was no target Toulouse `QueueNextBuild` or `BuildBuilding` call.

Nicomedia's first two update-route calls selected index 8, Lighthouse, while its
existing Factory continued. At native turn 252 the production log records
Factory reaching 178.7 of 165 production, with 13.7 overflow. The city log marks
Factory contract 6200 completed. Boundary 253 independently shows Factory present
and unpillaged.

That turn provides the one observed target queue boundary:

1. `CalculateDistrictValues` call 9 completed for Nicomedia.
2. `QueueNextBuild` call 10 enclosed `GetBestBuilding` call 11 on the same thread
   and city. This selector returned at `3e849c` with flags 1/0, selecting Lighthouse
   at 610,313 Q8.
3. The native city log records **Neighborhood through Build City District,
   contract 6381**. Boundary 253 shows `DISTRICT_NEIGHBORHOOD` in production.

Thus a building-category result did not become the production choice: a district
contract started instead. The contract's score and other competing values were
not captured, so this does not establish a numerical inequality between the
Neighborhood and Lighthouse scores. The observed queue return itself is not
interpreted as a Boolean success result. No target `BuildBuilding` attempt was
captured, consistent with the observed district production.

## Validation and restoration

The frozen collector contains 904 entry/return callbacks across four hooked functions,
13 completed target pairs (six calculations, six building selectors, one queue),
zero read errors, identity changes, suppressed callbacks or pending pairs. It
did not saturate its 64-pair/10,000-callback caps. Final frozen records exactly
match the boundary-253 snapshot. Out-of-scope cities were rejected by identity.
This limited trace does not cover every contract callback or AI subsystem.

The four observation hooks were `CalculateDistrictValues`, `GetBestBuilding`,
`QueueNextBuild` and `BuildBuilding`. Entry fingerprints, installed/loaded DLL,
dynamic building mapping, imported code and dependencies were pinned. The hooks
read values and pair calls; they do not invoke native functions, alter return
values, tune scores or issue construction commands. Instrumentation itself is
not an overhead-free or perfectly neutral performance benchmark.

Before launch, validation passed 28 JavaScript mock-memory checks, 33 observer-host
tests, eight source-gate tests and 11 independent Lua 5.1 reader mock cases. The
failed first launch exposed a missing native API in the initial reader; the
corrected native read and three identical source exports passed before any AI
advancement in run-02.

Normal shared-controller closure returned native exit code 0. It restored 145 mod
preference IDs / 148 installed entries and AutoStart=false, preserved the exact
632-file installed manifest and original save hash, and verified owner absence.
The collector froze before returning to menu; its retained daemon exited after
the native process, with no explicit detach or script unload. The asynchronous
process-terminated callback's immediate alive probe is not used as the final
absence proof; subsequent handle/inventory/daemon receipts establish closure.

Only after closure was the quiescent gameplay database copied. No WAL/SHM sidecars
were present, source/copy hashes matched, and SQLite integrity_check returned ok.
Its SHA-256 is
`e1a73e2d113acae5a74f43df9a5a467847da6abc16945da3aaae718054040d60`.
No new save or mod deployment was made by the probe.

## Architectural consequence and remaining question

The offline account now has runtime support for **future-value propagation into
an earlier prerequisite**, and for the separation between category selection and
production through contracts. Native prerequisites already carry useful future
value; a missing Workshop is not simply invisible because Factory is unavailable.

This run did not observe Toulouse's ordinary 0/0 next-building selection, a new
Workshop request, Workshop completion followed by a new Factory request, or an
enduring Factory-rooted plan. Its existing Flood Barrier occupied the queue
throughout the short window. The static eligibility/one-item request findings
therefore retain their stated static scope; the absence of a new Workshop order
here is not a failure-rate measurement.

For CSC, the next distinct architectural question is whether **future material
and customer relationships enter Quarter/producer forecasts before those
relationships exist**, and where that forecast ends. They are different
relationships from a declared BuildingPrereqs edge. Trace those consumers offline
before designing another game experiment or adding a planner; this result alone
does not authorize prerequisite, weight or assistance changes.
