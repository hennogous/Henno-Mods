# Smaller Mills and the other CSC building forecasts

5 November 2026. **The new Mill payouts and local scope pass 20 native cases.
One direct Quarter-repair case remains failed.** The separate building probe
accounts for all 19 loaded CSC building definitions in two controlled AI cities.
Later-building amenities dominate these forecasts; several other CSC benefits
are omitted, mis-gated or credited to mutually exclusive alternatives.

This investigation changes no AI weights, scores or CE API. It supplies the
evidence for choosing the next correction rather than another large blanket
Quarter incentive.

## What we tested

The maintained shared controller creates a Small Continents/Prince/Online test
world. Player0 has two isolated, bare Mill-test cities. AI1 and AI2 receive
controlled population15, research unlocks and workable hills; AI1 also receives
materials, improvements and customer districts/buildings. AI2 has only its City
Center. These are explicit diagnostic grants, not naturally developed cities,
legal construction scenarios or a clean causal rich-versus-poor counterfactual.

The fresh-world fixture stays at turn1. The read-only native observer then
captures one ordinary AI interval1→2. A second clean process loads the exact
saved2 for read-only persistence checks. No live instrumented module reload is
used. The endpoint is2, within Henno's maximum100, and no score policy or CE
carrier is enabled. Human CSC and stock CE files remain untouched.

Only Bakers and Tailors are loaded gameplay implementations. Their seven
ordinary buildings and twelve hidden flag/Service buildings form this scope;
the other six Quarter projects are inactive. The source ledger contains22
contribution groups plus four common native components. It distinguishes real
recipient, supply, civic, resource, population, route and building gates from
the forecast's treatment of them.

## Actual Mill payouts: 20 passes and one retained failure

The test compares native `District:GetYield(YIELD_PRODUCTION)` before and after
each change. Its oracle uses native geometry and actual building/district health,
not CSC's own adjacency calculation. Separate commands establish stable baseline
and post-change readings before checking the expected difference.

| Case | Native result |
| --- | --- |
| Wind on flat land / hills | 0 / +1 Production |
| Water with0,1,2,3,4,5,6 river edges | 0,0,1,1,2,2,3 Production |
| A Mill in the other city only | Does not activate this Quarter |
| Mills in both cities | Each activates only its own eligible Quarter |
| Mill removal or building pillage | Bonus clears |
| Building repair | Bonus returns |
| Quarter pillage | Bonus clears |
| Direct Quarter `SetPillaged(false)` | **Failed: native Production stays0 instead of returning+1** |

The passing cases also verify exact building location, the new Boolean steps,
actual/encoded amounts and all twenty retired numeric flags cleared to zero.
The forced zero-edge Water building tests its effect, not inland availability;
CSC's River/NoRiver flags still govern availability.

### The repair failure is not hidden by the properties

After direct Quarter repair, the Quarter is complete/unpillaged, the Wind Mill
is present/unpillaged at the correct plot, hills are present, and
ACTUAL/ENCODED/STEP1 all read1. Native district Production nevertheless reads0.
It remains0 after the ordinary turn and in the exact reloaded save.

The initial fixture recreated and pillaged the building in one command. A
corrected paired case retained the same Mill and Quarter from the preceding
pillage case. That also failed, so attachment-admission timing during fresh
construction is not a sufficient explanation. The +1 oracle was never relaxed.
The failed assertion is retained as a failed, explicitly record-only diagnostic;
the driver reports `mill_contracts_passed=false` and exits nonzero after completing
the independent observations and cleanup.

The shipped Debug panel toggles `District:SetPillaged` directly. Normal UI repair
queues a district BUILD operation. We have not yet proved that these entry paths
perform the same completion work. This is an unresolved native reactivation
discrepancy, not a confirmed normal-production repair regression or permission
to work around it by granting/recreating buildings. A real repair-completion
comparison is the next focused check.

## The smaller graph reaches the native AI

The active Wind graph has one +1 root and Water three. All four execute in the
hypothetical forecast; none of the retired1,2,4,…,512 Mill roots is active or
reached. Each surviving step contributes2,560Q8 in AI1 and2,304Q8 in AI2.
Those differences follow native timing: readiness13/14 versus15/16, horizon50.
They are not actual yields or a geographic preference.

The child analyzer iterates five actual districts in AI1 and one in AI2, but the
outer Attach consumes the final nested result. Summing every child callback
would count the same root repeatedly and give the wrong answer.

**Small steps contain the magnitude; they do not fix eligibility.** Every
BuildingValue call has site-unspecified coordinates `{-9999,-9999}`. Neither AI
city has a Quarter. The declared candidates are flat, with only AI2 on a river,
yet both forecasts credit every Wind/Water step. The native owner-property gates
remain omitted. This is a city/type building forecast, not a separate future
building plan for each candidate tile.

These are new cities and timing inputs, with a changed collection scope. Do not
subtract their scores from the earlier Delhi/Majapahit values and call that a
matched intervention effect. The earlier graph's1023 capacity and the new1/3
capacity are independently verified implementation facts.

## What the ordinary buildings contribute

Scores below are stored **Q8 utility:256Q8 equals one utility unit**. They are
neither Production nor Gold. The native output includes modifiers, amenities and
other investment/timing processing; a negative remainder is not independently
identified maintenance or an invented cost formula.

| Ordinary building | AI1 full Q8 | AI2 full Q8 |
| --- | ---: | ---: |
| Wind Mill |1,838|1,311|
| Water Mill |6,980|6,133|
| Bakery |14,269|10,616|
| Café |10,980|8,419|
| Textile Workshop |−722|−481|
| Tailor |14,232|12,061|
| Fashion House |12,909|10,946|

Direct amenities are the largest positive terms in the four later-building
forecasts in these cities:

| Building | AI1 own amenity Q8 | AI2 own amenity Q8 |
| --- | ---: | ---: |
| Bakery |13,525|10,464|
| Café |11,010|8,757|
| Tailor |15,031|12,853|
| Fashion House |12,233|10,464|

For example, AI1 Bakery reconciles exactly:
`14,269 = 3,072 own modifiers + 13,525 own amenities − 2,328 other terms`.
Each observed amenity forecast has one own recipient; this does not measure a
multi-city regional Café benefit. The deliberately large populations and their
amenity conditions also limit generalisation to ordinary games.

### Some relationships are represented; others are wrong or missing

| CSC relationship | Native observation | Interpretation |
| --- | --- | --- |
| Ordinary local producer exchanges | Nonzero `BuildingYieldChange` results | The AI does represent some real relationships. Conditions and alternative recipients still need accounting. |
| Bakery/Café returns to Mills | Gold and Production are credited to **both** Wind and Water | Double counts the two alternative recipient forecasts in these scenarios; actual gameplay has one mutually exclusive Mill variant. |
| Fashion House Wonder-linked GPP | Bolshoi, Broadway and Sydney roots each return768Q8 in **both** cities | Neither has those Wonders; even bare AI2 has no Theater. Intended eligibility is not faithfully represented. |
| Material-improvement reciprocity |20 parent Attach calls returnfalse with null collection `Next` | These material collection paths have no contribution through this inspected native channel. |
| Tourism |23 child descriptors have null effect `Analyze` and returnfalse | Missing native effect consumers in this build/path, rather than merely a numerical zero. |
| Service building grants |5 child descriptors have null effect `Analyze` and returnfalse | The grant path does not forecast its full downstream Service benefit here. |
| City-property writers |24 calls are accepted with zero result | Native handling exists, but that is not evidence that it forecasts the later property-consumer income. |
| Dockmaster naval-production roots | Accepted with zero result | Zero in these contexts; do not label the effect universally unsupported. |
| City Center population/export consumers | Outside these building-root intervals | Remain a separate accounting boundary; absence here is not proof they are never valued. |
| Specialists / remaining income and cost terms | Source rows and a residual, without a separate native attribution | Remain unresolved; do not relabel them as free passive yields or definitely ignored effects. |

The exact four reciprocal roots are
`MOD_CSC_BAKERS_{GOLD,PROD}_TO_{WIND,WATER}_MILL`. They have Amount1 and no
owner/subject requirement in the loaded definitions. Bakery credits3,072Q8
in AI1 and2,048Q8 in AI2 across the two alternatives, with an equal half for
each. Café credits2,048Q8 in both cities. The loaded Wind/Water definitions
exclude each other, so both recipient forecasts cannot represent simultaneous
income from the actual Quarter. This does not claim all reciprocal effects
are universally doubled.

## District choice and building construction use different vectors

The district pass uses positive **raw** building values, canonical mutually
exclusive definitions and the `MustPurchase` exclusion. It adds one common
city/type sum to positive district-site rows:

| Raw building uplift added to eligible sites | AI1 Q8 | AI2 Q8 |
| --- | ---: | ---: |
| Bakers: Wind + Bakery + Café |27,087|20,346|
| Tailors: Tailor + Fashion House |27,141|23,007|

Water has a larger own forecast, but lower-index mutually exclusive definitions
canonicalise it out of this district sum. Negative raw Workshop is also omitted.
All148 observed mutable district cells reconcile, including the existing sign
and center-row gates. This common uplift changes district competitiveness and
can interact with site values; it does not independently rank every tile of the
same district type by its future Mill geography.

The routine separately propagates descendants into a **mutable construction
vector**. Negative raw Workshop does not mean the AI has no incentive to build it:

- AI1 Workshop: `−722 + 14,232 Tailor + 12,909 Fashion House = 26,419Q8`.
- AI2 Workshop: `−481 + 12,061 + 10,946 = 22,526Q8`.
- Mutable Wind reaches27,087/20,346Q8; mutable Water reaches32,229/25,168Q8.
- River Access has raw0 but receives raw Water6,980/6,133Q8 through prerequisite
  propagation. This is distinct from directly adding a hidden flag to a district.

All twelve hidden definitions are `MustPurchase`; none enters the direct district
sum. However, that flag is not a blanket exclusion from prerequisite propagation.
Both River flags have own raw0. Several absent, zero-cost Service buildings have
raw20,595Q8 exactly where their prerequisite district already exists and readiness
is1. Their own modifier/amenity terms are0. That remainder is **unattributed**;
an era/status income path is a candidate, not a measured explanation. It is not
a measured Service benefit. Those Service values do not feed these CSC producer
chains in the captured pass.

## What this means for tuning and CE

The immediate giant Mill encoding artifact is bounded, and much of the remaining
later-building uplift is a real kind of benefit: amenities. Replacing the whole
building sum with our own bonus would throw that useful native reasoning away.
There are also specific false forecasts and missing channels worth correcting.

The current early site hook remains useful for geography. A later correction or
component diagnostic may be justified by the exact alternative-recipient,
Wonder-GPP or missing-material case. We should choose one measured mismatch,
preserve justified native contributions and trace a resulting decision. This
study adds no CE API, opens no upstream PR and changes no tuning weights.

Separately, resolve the direct Quarter-repair reactivation discrepancy against
normal production repair. Existing source and turn2 checkpoints allow follow-up
without another fresh map. New-package reload preserves the observed facts; it
does not establish migration of an old MAB save or repair the failed state.

## Evidence, checks and restoration

Exact original XP2 SHA-256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Isolated CSC GUID ends2a09;618 files, only the four reviewed adjacency source
files overlaid on the unchanged human package. No native carrier or score writer.

Artifacts are under `Desktop/Codex/csc-mill-building-study-20261105/`:

- `run-01`:20 cases pass; initial repair case fails, followed by a secondary
  pre-launch log-generation error. A labeled recovery receipt cites normal
  native exit0 and exact restored preferences. No native observer was reached.
- `run-02`: paired repair still fails; a Windows slash-spelling mismatch stops
  the module guard before attachment. Normal closure/restoration is verified.
- `run-03`: prepared-source checkpoint, complete observation, endpoint checkpoint
  and clean-process exact reload. The failed repair is never counted as passed.
- `run-03/independent-analysis/`:361 complete pairs,28,132 callbacks, no observer
  faults/stops/suppression.38 building forecasts,38 modifier totals,251 generic
  modifier records,24 base-yield records,8 direct amenities and2 district passes.
  All88 active building roots are observed in both cities; all totals and148
  district cells reconcile. Input hashes and source-state limitations retained.
- `staging.json`, package receipts and `restoration.json`: the new study folder
  is retired by hash; human CSC/stock CE unchanged. Each final process exits0,
  restores all153 installed preference entries/150 IDs and autostartfalse, with
  no remaining native/Tuner owner.

Thus three fresh attempts occurred in total; the first two stopped before
instrumentation. Only the final attempt contains the forecast observation and
one exact reload. No economic or historical-outcome comparison is claimed.

Offline checks:38 Node observer cases; root Python suite50 cases with48 passes
and two optional full-database cases skipped. Both optional cases were also run
successfully with the actual cached rules and shared Core. The new fixture,
transport, nested accounting, signed values, output identity, scope/budget and
failure-preservation contracts are covered. Static ABI receipts for the six
boundaries are in `Desktop/Codex/csc-mill-building-study-static-20261105/`.

Code and reproduction: [study harness](../../../tools/native_ai/mill_building_study/README.md),
[controlled fixture](../../../tools/native_ai/mill_building_study/fixture_readme.md),
[source contribution ledger](../../../tools/native_ai/mill_building_study/ledger/README.md).
