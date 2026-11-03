# CSC producer forecast: native valuation investigation

Follow-up qualification: the [property calibration and native cache trace](csc-ai-producer-property-calibration-20261029.md)
establish that UI GetBuildingPotentialYield reads cached vectors. The unchanged80
below is a valid UI observation, but by itself does not locate failure in the live
modifier or prove saved-instance binding. No AI contrast was established in either
attempt; the positive-preference observations remain valid independently.


29 October 2026. Closed bounded investigation; no shipping tuning change. This increment follows the first ordinary-building exposure and
uses the supplied GameCore linker map as a naming reference, with every current
address checked against the installed DLL. It investigates one practical question:
does the RH integration's producer forecast reach the native building valuation?

## What the static trace establishes

The ordinary building evaluator calls `ValueManager::NetValue`, which calls the
building `Value` overload. That overload iterates registered yield definitions and
reads city building yield changes. Positive changes enter yield normalization;
the loop is not restricted to the six ordinary yields. The returned net value is
stored in the building cache. `GetBestBuilding` later consumes that cache and the
effective building preference. Queue selection can instead honor an existing
contract, so successful input delivery, valuation and selection are separate tests.

The normalization code uses a yield-definition float and an optional strategic
yield multiplier. The float's identification with SQL `DefaultValue` has not yet
been independently proved through its loader. There is no need to establish a
complete engine catalog before testing this concrete route.

Current-build addresses were checked in both decompiled output and assembly:

| Native surface | Current RVA |
|---|---|
| Building Value overload | `52b900` |
| Building NetValue overload | `52a050` |
| NormalizeYields | `52b110` |
| City Buildings GetYieldChange | `10c0e0` |
| Ordinary evaluation call return | `3e419f` |
| GetBestBuilding | `3e4710` |
| QueueNextBuild | `3e8190` |

The ordinary building cache is reached through CityBuild+`4c8`, then+`28`.
`PresentValueOf` at`3e7e50` is its accessor; the similarly named
`CachedPresentValueOf` at`3df780` uses another array and is not interchangeable.
No specialization overwrite was found in the inspected building Value/evaluation
path; that is not a claim about every native specialization consumer. The pinned
XP2 DLL SHA256 is
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.

## Experiment contract

The saved turn100 world is rebased onto the current 604-file installed package in
both arms. It is not a continuation of the historical 518-file test package.
The primary case is AI3, Kobdo city458758, with an unbuilt Textile Workshop.

The control keeps the RH producer forecast at Base80 plus Both40. Treatment
changes only those two modifier Amount cells to zero. Both arms suspend new CSC
assisted purchases/foundations while retaining saved economic history. They use
the same source save and endpoint, at most five single-turn intervals to105.
No forced production, new world, unit/resource grants or RH Workshop edits occur.

Before treatment advancement, all captured initial world, queue, economic and
producer facts must match except private potential80 versus0. Runtime databases
must differ only in the declared two cells. Failure to deliver zero stops that arm;
it does not authorize modifier reattachment or a replacement experiment.

Four read-only hooks observe fresh Workshop NetValue, its nested private-yield
getter, best-building selection and the city's queue-selection call. Cache and
effective preference fields are read only when the native function actually
returns the target building. Otherwise those fields remain unobserved. Every
accepted trace must have complete pairs and no read errors, drops, identity changes
or unexpected detachment. Earlier computations feeding later choices retain their
observed intervals rather than being relabeled as same-turn evaluations.

## Interpretation boundary

This forecast currently exists in the RH integration, not Basic. Its material
presence condition accepts adjacent owned, visible, district-free mapped resources
with a valid improvement mapping. It does not establish an unlocked, reachable,
working improvement or available Builder capacity. Even a successful native value
response would validate a guidance channel, not the accuracy of that forecast or
the long-term benefit of its current amount.

## Preflight correction

The first control load reached inactive source100 but failed in the facts reader
before forecast delivery, hooks or autoplay. The reader incorrectly expected an
explicit false for an AI in `InitialHumanPlayers`; the pinned implementation returns
a sparse string-key set containing only true human entries. The session-only
assistance suspension had occurred. No complete initial world census was captured,
so the failure does not prove full-world equality or any forecast result.

Run01 remains preserved. Independent audit verified native exit0, no observer
daemon, exact145 mod IDs/148 subscription entries and AutoStart=false restoration,
all604 installed files,322 source pins and12 dependencies. A preceding dispatch
without a GO receipt also failed at its first guard before native actions.

Explicitly approved run02 corrects only the reader/evidence contract: validate the
sparse set, check configured player0 human/player3 AI, and require the UI and saved
original-human sets to match the archived source. The observer, treatment and
endpoint budget are unchanged. Thirty-five executor/role checks and15 observer
fixtures pass; independent review verified324 source pins and12 dependencies.
These checks validate the harness, not the forecast's native effect.

## Run02 control observations

The corrected control passed source100: AI3 Kobdo city458758, Workshop147 unbuilt
and legal, cost40, private potential80 and Culture potential2. Original-human
evidence agreed and the common assistance suspension preserved saved economic
history. It advanced exactly100 to105, then closed normally.

The observer retained seven complete pairs with no errors, drops, identity changes
or unfinished pairs. Six GetBestBuilding calls returned the Workshop. Each safely
observed preference scalar was+1, and the returned value was exactly twice the
cached value. For example, at100→101 the cached Q8 value290985 (1136.66015625)
became581970 (2273.3203125). This is actual evidence of the preference multiplier
in this path, not a claim that adding another positive definition compounds it.

The scoped fresh NetValue and nested private-yield getter were not captured.
Caches changed between observations; this does not establish either staleness or
a waiting-period explanation. An unobserved route/filter remains possible. No
fresh forecast-to-valuation attribution is accepted from the cached data alone.

The native log selected existing Harbor contract1988 at101; UI at102 and105
confirmed Harbor in the queue. A new Workshop contract2114 was submitted at102
with logged VALUE1167.0. Proposal, best-building status, queue selection and physical
completion are distinct: the Workshop was still unbuilt at105. The executor's
`choice_observed=false` combines fresh-input and choice predicates; it does not
erase the observed Harbor choice. Cumulative trace snapshots are counted once.

## Treatment delivery failed before AI advancement

The zero arm loaded the same source100 and exported the same known Core state,
UI queues, economic history and producer facts. Crucially, private potential was
still80, not0. The predeclared guard stopped the arm before observer attachment
or AI advancement. There was no workaround, additional arm or window extension.

The last-loaded gameplay database was archived read-only after supported exit.
Comparing every table with the control found exactly the two intended
ModifierArguments changes: Base80→0 and Both40→0, with all other rows unchanged.
Thus the new definitions loaded, but the intended change to this saved city's
forecast did not occur. The actual initial exports were identical, including80.
Saved modifier-instance state is a plausible explanation, not an established
engine-wide rule or proof of the internal cause.

This is **not a forecast efficacy comparison**. It cannot show that the forecast
is ignored, unnecessary, or successful. The control's preference multiplier and
new producer request are valid observations independent of that failed contrast.

## Practical consequences

1. Keep the effective positive producer preference provisionally: it is observed
   in a genuine CSC city and the native best-building result is exactly2× its
   cache value. Raising a numeric Buildings Value or adding more positive rows is
   not supported as a way to multiply that effect further.
2. Treat proposal and follow-through separately. The AI requested this producer
   while honoring another commitment; a best-building result is not a promise of
   immediate queue promotion. The Harbor is not established to be a bad choice.
3. Do not remove or strengthen the producer forecast on this evidence. First use
   a scenario where the actual signal can be changed and independently verified,
   such as a modifier instance created under the intended definition. Establish
   delivery before interpreting production or comparing outcomes.
4. Before another scorer experiment, resolve the bounded hook's non-exposure
   through read-only caller/filter diagnostics. Cache changes alone cannot name
   the route that updated them. No further game is launched by this report.
5. Any later producer forecast should distinguish credible supply development
   from merely adjacent mapped resources. That concerns forecast quality and
   planner sequencing, separately from whether the native channel responds.

## Evidence and restoration

Artifacts: `Desktop/Codex/csc-native-producer-forecast-20261029/run-02`.
Key files are control boundaries100–105, classified traces, raw CityBuild deltas,
`control/trace-counts.json`, `forecast-zero/boundary-100.json`,
`forecast-zero/aborted-treatment-runtime-provenance.json`, each arm's cleanup,
and the root package-restoration receipt. Run01 retains the preflight failure.
Static exports are in `Desktop/Codex/csc-native-ai-analysis-20261028/producer-path-exports`.

Both games exited normally. Each arm restored its freshly captured145 mod IDs,
148 subscription entries and AutoStart=false. The current604-file package was
restored, including the sole temporarily edited installed SQL file; no historical
AI/art package was overlaid. The worker exited1 because the deliberate delivery
guard fired, not because Civilization crashed. No test owner or automation is
left running. Independent audit verified324 source pins,12 dependencies,473 archived database
tables, the observed native/log evidence and exact process closure. Restoration
passed; the intended paired forecast experiment did not. The daemon reported native
absence with no explicit detach receipt; no separate detach-journal claim is made.

Related: [roadmap](../../integrations/csc-ai-roadmap.md),
[first evaluator/building exposure](csc-ai-planner-and-building-step-20261029.md),
[GameCore symbol resource](csc-ai-gamecore-symbol-resource-20261029.md).
