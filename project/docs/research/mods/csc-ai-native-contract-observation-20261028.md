# Native production-request observation — 28 October 2026

## Result

A separate, bounded field-reading trace completed on the same existing vanilla
Gathering Storm turn-1 save, advancing once to turn 6. The independently checked
initial/final Core and UI exports match the unhooked loaded baseline, and all
17 closed AI CSVs are byte-identical, including contract IDs. This is bounded
observed parity, not a guarantee of instrument neutrality in every scenario.

We can now connect verified native request identities to priority, present value,
city validation and execution. No CSC/RH tuning was loaded or changed. This
research observer is not a shipping mod dependency or a production override.

## Actual AI observations

Original human player 0 is reported separately from actual AI player 1. The
following rows belong to player 1, Uruk; unit indices were resolved through a
scheduled native GameInfo.Units Index/UnitType mapping and joined by type to the
archived runtime database, never inferred from SQLite row IDs.

| Request | Initial request priority | Observed preference addition | Initial present value | Initial required city |
|---|---:|---:|---:|---|
| Settler, contract 3 | 4 → 5 | +1 | 175 | Unrestricted (-1) |
| Builder, contract 5, Build City Improvement | 2 → 2 | 0 | 74 | Unrestricted (-1) |
| Builder, contract 10, Build Trigger Unit | 2 → 2 | 0 | 13 | Unrestricted (-1) |
| War Cart, contract 7 | 2 → 2 | 0 | 24 | Uruk (65536) |

The runtime database contains UnitPriorityBoosts/UNIT_SETTLER Value=1 and no
CSC_AI_Profile table. The Settler's observed +1 is consistent with the statically
traced additive Units path and the loaded definition; it is not a separate on/off
causal test. The vanilla Builder rows do not test CSC Basic's Value=50.

Both Builder requests passed observed city validation. Contract 5 executed in
Uruk and matches the native CityBuild selection at turn 3. Within that execution
call, requiredCity changed from -1 to 65536 and the raw status changed 3→5. This
shows an initially unrestricted request becoming bound to its selected city.
There is only one AI city in this case: it does not demonstrate recruitment
across two cities or prove the CSC any-city override is always redundant.

War Cart contract 7 later had present value 12272/256 = **47.9375**, while its
priority stayed 2. Its execution matches the native selection at turn 4.
Builder contract 10 remained at observed present value 13 and had no captured
execution. Thus same-priority requests can carry different, changing values;
request priority must not be conflated with queue value. The trace does not
capture every alternative scorer or establish a complete causal explanation
for the selection. Execution/selection is not physical unit completion.

The original-human autoplay requests are kept separate: Settler 12 showed
4→5, and Builder 13 showed priority 2/value 81 and city binding on execution.
They are not counted as actual-AI outcomes.

## Observation design and coverage

Three exact Windows entry points were observed: unit-request Initialize at
RVA 3f9300, city Validate at 3fa8e0 and city Execute at 3f8310. Arguments and
bounded scalar fields use assembly-verified layouts; the observer makes no
GameCore calls and changes no arguments, return values or gameplay fields.
Hooks themselves alter executable code and may affect timing. Original role
classification comes from the frozen initial census, not autoplay role flags.

The observer checks vtables, readable scalar spans, handle and player/contract
identity, candidate-city identity and per-initialization address generations.
Failed fields remain null with reasons. Actual entry/leave sequence numbers are
separate from paired-record commit order. A legitimate native desired-unit
clearing branch is recorded separately from handle corruption. Synthetic tests
exercise the actual pointer-check and Windows argument-decoder code as well as
identity, overflow, missing-field and budget behavior. All 28 observer fixtures
and the 11 collector rejection fixtures passed before launch; source review was
independent of the sole native operator.

Observed: **36 calls, 34 retained enter/leave pairs (68 events), 2 budget drops**.
There were zero read errors, reentrant skips, identity changes or handle
mismatches; no saturation or pending reserved pair remained at freeze. Coverage
is explicitly **incomplete** because of the drops and the three-function scope.
Missing events are not rejected native decisions. The two absent call IDs are
22 and 33. The prototype's pre-initialization budget shares a null-identity key,
so it can censor distinct new contracts; original-human contracts 18 and 20 lack
initialization captures and their deltas must not be inferred. A future observer
should distinguish provisional budget keys while retaining the same hard total
bound. The frozen experiment was not edited or replayed to expand the cap or
manufacture missing observations.

The final exports contain 2 cities, 13 units and 1,144 plots, with valid positive
queues in both cities. Optional unavailable/error getters remain explicit;
charges, promotions, pillage state and hidden simulation/RNG state are outside
this census. The extra initial unit-mapping read is documented separately from
the unchanged baseline collector sequence. Raw log comparisons retain startup
prefix presence and turn-6 boundaries without contract-ID normalization.

## Lifecycle and evidence

Root: `Desktop/Codex/csc-native-contract-trace-20261028/run-01`.
Key records: `independent-audit.json`, `independent-audit.md`,
`independent-process-check.json`, `comparison.json`, `worker-terminal.json`,
`instrumented/trace-counts.json`, `trace-coverage.json`, `runtime-data-pins.json`,
`native-unit-index-mapping.json`, `runtime-gameplay.sqlite`, `cleanup.json` and
closed-generation raw logs. Static layout provenance is in the pinned field
reference/spec files. The prior unhooked baseline remains separately archived.

Independent verification: all 130 source/evidence pins, 12 dependency pins and
598 installed-package files match; native mapping/database pins match; worker,
native and daemon exited zero. Supported Menu/ExitOK restored exactly 145 mod IDs,
148 subscription/file entries and AutoStart=false. The trace session remained
attached but inert until native termination. A final read-only process check
found no study owners remaining. No installation overlay or art rollback occurred.

## Consequence for CSC development

The current useful calibration target is the relationship between request
priority, updated present value and actual queue competition. The traced vanilla
Builder priority was 2; CSC Basic's additional 50 is a different scale and must be
tested as an additive request input, not described as a 50% production preference
or assumed to raise the logged value by 50. We have not selected a replacement
amount or established an optimal policy.

Some unrestricted-city behavior already exists in vanilla requests. Diagnose the
specific constrained request before adding or crediting a cross-city override.
Similarly, a successfully validated request need not be the request selected.
The next focused calibration should compare those stages under a declared input
change, retaining a genuine competing request and physical follow-through. It
should not add a blanket Builder bias to RH without evidence of the binding gap.

This completes a small instrumentation step in the workbench, not the roadmap's
full district/building decision explanation, a tuned planner, or whole-chain
benefit validation. No further arm, automation or old campaign was started.

Related: [loaded count control](csc-ai-native-loaded-control-20261028.md),
[static Builder priority path](csc-ai-native-builder-priority-20261028.md),
[AI roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md).
