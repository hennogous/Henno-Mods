# Producer property delivery and scorer diagnostics — 29 October 2026

Resolved follow-up: the [live-effect diagnostic](csc-ai-producer-live-effect-20261029.md)
verified Base1→0→1, bound requirement Met→NotMet→Met, and actual native removal/
reapplication of the Workshop's stored+80 adjustment while UI potential stayed80.
This establishes live delivery for the property gate, not AI scoring efficacy.
It also recovers matching remove/apply evidence in this earlier run's closed logs.
The original observations and their contemporaneous limits below remain preserved.


Follow-up to the [producer forecast probe](csc-ai-producer-forecast-probe-20261029.md).
The previous SQL-zero arm changed the loaded definitions but left the saved
Workshop potential at80. This probe tests the existing bound requirement instead
of assuming that another definition edit changes the actual forecast.

## Scope

One existing RH/CSC source100 save, SHA256
`2982b00a4c4d0c536ac7232e88c2c2b0fc2e56fd2ee7842aa22ad47b2ffb065d`,
under the current604-file installed package. This is a current-package rebase,
not exact continuation of the historical518-file source runtime. The target is
AI3 Kobdo/city458758, Tailors plot2781, Workshop building147/private yield7.

Only the existing `CSC_RH_WORKSHOP_BASE_PRESENT` plot property may change1→0→1
at inactive100. The original value is captured and restored. Three bounded
read-only samples may establish the off value; failure stops before AI play.
Queue, treasury, roles, materials, real potential yields and saved assisted
economic history must agree, with full known Core/UI parity after restoration.
Only then may two baseline turns100→102 diagnose the observer. No treatment is
held during those AI turns. The role bridge rewrites the property at turn/map
events, so this temporary calibration is not a persistent forecast experiment.

Future CSC assisted actions are suspended as the same declared common probe
condition used previously. Historical receipts remain intact. No installed files,
RH definitions, production orders, resources, units or buildings are changed.

## Diagnostic correction

The previous accepted-call counters incremented after all observer filters.
Zero accepted NetValue calls could therefore mean rejection rather than no native
execution. The new observer retains raw entries, rejection stages and bounded
caller/building histograms, including a separate Workshop counter so unrelated
buildings cannot consume its histogram capacity. Identity-gated value reads and
the four hooked functions remain unchanged. Raw Workshop counts alone are not
Kobdo-specific value evidence.

Strict schema and accounting checks run at every phase and freeze: exactly four
hooks; nonnegative integer counters; entries equal accepted plus rejected;
histograms limited to32 keys with explicit overflow; target counts are subsets;
accepted totals agree with event counters. Focused checks passed24 calibration,
11 diagnostic and15 preserved observer fixtures before launch. These verify the
harness, not native delivery or AI benefit.

## Static context

Current-build `CityBuildings::GetYieldChange` at RVA10c0e0 includes definition
contributions, shared adjustment and a stored city/building/yield tuple accessed
through FindYieldChange10aa90. It does not read ModifierArguments directly on
each call. This is compatible with unchanged active effect state after a SQL
Amount edit, but does not establish the cause of the previous80 readback.

DLL SHA256: `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The symbol map labels are transferred reference names; decompiler types are
estimates. Version-specific native evidence takes precedence over labels.

## Observed result: UI contrast not established

The initial source was legal/unbuilt, Base1/Spec0/configured-AI1, private
potential80, with treasury66.9921875. At inactive100 the exact existing Base
property changed to0. All three readbacks still returned UI potential80. All
other captured source/material/role/real-potential facts, major-city UI state and
saved economics matched the initial export exactly. The declared guard stopped
before101: no AI turns, replacement arm or wider treatment was attempted.

The original Base1 was restored and independently read back. Because the delivery
guard fired before the planned restored census, neither a complete80→0→80
roundtrip nor full restored Core/forecast parity is claimed. The unsaved probe
session then exited normally. The source save was not overwritten.

Every phase and final freeze recorded zero raw entries for all four hooks,
including zero Workshop-target entries, with no errors/drops and valid accounting.
Since no AI played, this does not explain the previous control's changing AI
caches or establish that the native scorer is unused. It only establishes that
these paused UI reads did not expose the selected entrypoints.

## Important correction from the symbol-assisted trace

Current-build exports establish the UI getter's actual path:

`Cache::Lua::ICity::lGetBuildingPotentialYield` (68a790)
→ `Cache::City::Instance::GetBuildingPotentialYield` (75aa0)
→ `GetBuildingPotentialYields` (75b30).

The last two functions select an already stored per-building yield vector and
return its selected yield. This path does not recompute through the hooked live
`City::Buildings::GetYieldChange` (10c0e0). Consequently repeated UI reads are
**not a positive control for that live hook**, and UI80 alone cannot distinguish
an unchanged live modifier from stale/not-yet-refreshed UI data. This refines the
earlier delivery-failure wording: the required observable contrast was absent;
the precise live delivery failure or delay is unlocated.

The current `PlotPropertyMatches::OnPlotPropertyChanged` handler (96b410) resolves
and compares the affected plot and, when its internal active gate permits, calls
the requirement test and SetState. This is a concrete event-driven update route,
not evidence that this particular saved modifier received the event or changed
state. Do not infer that a whole AI turn is intrinsically required, or that the
property cannot work. Requirement result types in decompiled C are estimates;
do not interpret its boolean-looking return as a confirmed public boolean API.

Six bounded exports, including the initializer/test and UI Lua bridge, are in
`Desktop/Codex/csc-native-ai-analysis-20261028/producer-cache-exports`.

## Decision and next useful boundary

Do not launch a persistent off/on production comparison until its actual live
input is observable. The next diagnostic should distinguish (1) the property,
(2) the bound requirement/effect state, (3) the live city building-yield value,
and (4) UI cache publication. Use the identified update route and validated
read-only identities; avoid treating UI polling as a forced refresh or calling
unverified native mutators. The two baseline AI diagnostic turns remain unrun.

No shipping forecast/preference is removed or strengthened on this result. The
previous directly observed positive-preference multiplier remains independent
evidence; this session says nothing about long-term producer benefit.

## Audit and restoration

Artifacts: `Desktop/Codex/csc-native-producer-property-calibration-20261029/run-01`.
Independent reports: `independent-audit.json`, `independent-audit.md` and
`independent-process-audit.json`. Raw phase exports, delivery-failure receipt,
property-restoration readback, observer freeze and cleanup remain preserved.

Independent audit verified322 source/RH pins,12 dependencies, all604 installed
files unchanged, fresh145 mod IDs/148 subscription entries/AutoStart=false
restored, and exact worker/native/daemon identities absent. Native10016 and
daemon21896 exited0; worker11984 exited1 at the deliberate delivery guard, not a
Civilization crash. No game, automation, deployment or follow-on arm is active.
