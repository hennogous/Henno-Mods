# Why weak Bakers sites receive large building forecasts

4 November 2026. **The dominant uplift is a phantom Mill adjacency forecast,
not a large measured return from a complete supply chain.** A read-only native
observation now attributes the building pass in Delhi and Majapahit. No scoring
correction or new policy was installed. [AI-C053]

## Answer in ordinary language

CSC uses ten switchable modifiers—1,2,4,…,512—to encode a building's real
adjacency bonus. Gameplay enables only the bits matching its hills or river
rule. Their combined capacity,1023, is not a promised building yield.

The native hypothetical modifier interpreter omits the owner property gates.
The generated Mill wrappers enumerate actual player districts and supply the
context needed by the supported district-yield analyzer. Consequently all ten
magnitudes enter its future-building forecast, independently of the intended
geography. This is an implementation mechanism being mistaken for economic
potential. The game is not actually paying those huge yields.

The Wind Mill supplies more than99.8% of the measured building uplift in each
city. Bakery and Café add much smaller values. Some smaller benefits are real,
but the remaining forecast terms have not all been independently itemised.
Removing every future-building benefit would discard useful reasoning too.

## What was observed

One existing Online-speed save from the previous soft-penalty experiment was
loaded once at80 and advanced through81 using the maintained shared controller.
No new world, second load, construction order, grant or queue edit occurred.
Only CSC was enabled. No CE proxy or old Python/Frida score writer was loaded.
Frida supplied **read-only research instrumentation**, not incentives; this
does not change the separate CE/Lua policy-parity result.

The save is an already treated historical world, not an untreated baseline.
Earlier requests and choices can retain prior influence. Recalculation at81 is
not a replay of every earlier86/89 component or a matched correction arm.

| Building forecast, stored Q8 utility | Delhi | Majapahit | Added to Bakers district? |
| --- | ---: | ---: | --- |
| River Access |0|0|No: implementation flag, MustPurchase |
| No River Access |0|0|No: implementation flag, MustPurchase |
| Wind Mill |1,356,033|1,589,150|Yes |
| Water Mill |1,407,663|1,407,663|No: lower-index mutually exclusive definitions canonicalise it out |
| Bakery |1,118|1,023|Yes |
| Café |invalid|1,640|Only Majapahit |
| **Total admitted building value** |**1,357,151**|**1,591,813**|**Exact observed district-pass addition** |

Delhi's Café raw input was the invalid sentinel−2,559,744 Q8; its ordinary
BuildingValue body was not captured as a successful forecast. Do not substitute
zero economic value or a proved reason for invalidity. Raw valid family inputs
matched the corresponding observed BuildingValue outputs. Hidden flags are
excluded directly by MustPurchase; a hidden prerequisite can still affect a
different earlier timing/depth path.

The building pass uses the center-row raw values, not the separately mutated
dependent-building vector. In this observation those pointers aliased, and
the before/after district rows reconciled exactly. The sum applied to9 positive
rows in Majapahit and18 in Delhi; other rows followed their existing sign gate.

| Target site | Before building pass | After building pass | Difference |
| --- | ---: | ---: | ---: |
| Delhi1429 |66,743|1,423,894|1,357,151 |
| Majapahit1829 |151,738|1,743,551|1,591,813 |

These recalculated initial values have **no current site penalty**. The original
Delhi trial had the same measured downstream difference; its65,536 penalty
accounts arithmetically for the different final total. That corroborates the
interpretation but does not turn this observation into a full historical replay.
Majapahit's older downstream difference was1,591,630,183 less than this new one.

## Isolating the phantom adjacency component

| Forecast | Ten encoded-bit effects | Entire modifier total | Other modifier remainder | Full building output |
| --- | ---: | ---: | ---: | ---: |
| Delhi Wind Mill |1,356,544|1,358,080|1,536|1,356,033 |
| Majapahit Wind Mill |1,589,504|1,591,552|2,048|1,589,150 |
| Water Mill, each city |1,408,256|1,409,792|1,536|1,407,663 |

The non-modifier residuals for those three rows are−2,047,−2,402 and−2,129 Q8.
They include other native processing, not a newly isolated maintenance formula.
The positive modifier remainders are **unattributed**, rather than certified
legitimate income. The ten-bit component alone accounts for99.96% and99.85% of
the respective admitted district sums before the small other terms net out.

All ten amounts were observed inside each Mill's ModifierValue interval, with
actual district contexts. Each amount repeated across9 player districts for
Majapahit and15 for Delhi. The nested attach handler assigns its child's result,
so the surviving last result for each wrapper is counted once. Summing every
district callback would overstate the forecast. Per-bit rounding also matters.

For example, the Wind Mill's512 child produced3,109 whole utility per actual
Majapahit district context and2,655 in Delhi, including City Centers. All24
captured owner district plots had that512 gameplay property disabled. The
native effect credited it anyway. The effect accumulator is whole utility;
ModifierValue restores Q8. These are not512 real Production already received.

The shared gameplay evaluator independently reports the actual candidate rules:

- Delhi1429: planned Water Mill river bonus1 Production, Specialty adjacency1
  Production and city-sales adjacency1 Gold; total3.
- Majapahit1829: no Mill geometry bonus, Specialty adjacency1 Production and no
  city-sales Gold; total1.

The district aggregation chooses the canonical Wind forecast even in the Delhi
case where our site evaluator plans Water. This is another reason to distinguish
a city/type building sum from a site-specific future-chain calculation.

## Which benefits should we preserve?

The [gameplay ledger](csc-ai-bakers-gameplay-component-review-20261104.md) pins the
actual rules. There are no flat Building_YieldChanges rows for these buildings.

| Relationship | Real CSC benefit | What this observation establishes |
| --- | --- | --- |
| Appropriate Mill geometry | Actual hills/river Production under the intended property gates | Generated encoding bits are being forecast without those gates; correct this mismatch rather than the actual adjacency rules. |
| Bakery/Café amenities | One amenity each; Café range6 | Real benefits remain. Their exact marginal contribution was not separately hooked. |
| Specialists | Bakery2 Food; Café1 Food/1 Culture for an assigned specialist | Not free passive building yields; no separate numerical attribution here. |
| Local producer exchanges and ordinary customers | Actual Mill/Bakery/Café exchanges and correctly gated customer sales | Do not require material/Service gates that the real ordinary sale does not have; the small modifier residuals are not fully identified. |
| Material reciprocity, Services and exports | Real effects with their own supply, civic, recipient or route conditions | Some forecast channels omit collections/gates or depend on current-state Lua. They need their own accounting, not an assumption that all are included. |
| Research, construction delay and maintenance | Real investment constraints | Native forecasts handle these through several paths; preserve them rather than subtracting a second invented cost. |

The prerequisite-depth heuristic is **not** the source of the dominant term:
it acts on an earlier income subtotal, before the later modifier sum. It does
not multiply the phantom bit contribution. Exact smaller subcomponents remain
unmeasured.

## Implication for tuning and CE

We now have a specific, measured CSC forecast mismatch. A correction should
exclude or replace this encoding-artifact contribution while retaining justified
building benefits. The existing district hook is earlier than building
aggregation; a large opposing early subtraction can cross the positive gate
and remove legitimate later benefits as well. A precise repair may therefore
need a building/modifier forecast boundary or an explicit final-component
contract. No such repair or additional CE API was implemented by this study.

The common city/type uplift does not independently reorder every same-Quarter
site. It changes district competitiveness and interacts with sign gates and
existing site adjustments. Candidate coverage and retained requests remain
separate causes of poor placement. A future controlled correction test must
measure the resulting choice and follow-through, not just the lower forecast.

## Evidence and closure

- Exact original XP2 SHA-256:
  `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
- Save SHA-256:
  `6569b8b97489c558212e361772f126ae8c04c054983e83ce88409d8716a65a7c`.
- Artifacts: `Desktop/Codex/csc-bakers-components-20261104/run-01/` and
  `analysis-02/`. Full source pins, raw commands/replies, loaded module proof,
  source/endpoint worlds, complete trace, closed logs and cleanup receipts remain.
- Frozen trace SHA-256:
  `7cb7eedac76b7e2d937441d50ebb8e687b727d062feceb3d22bf73ed5fd59310`.
- Source-world SHA-256:
  `0a015856734ccc98953572babd80117f39324a2619290664186dee977e66e8c0`.
- 504 complete pairs:11 building returns,11 modifier totals,480 district-base-yield
  effects and2 district aggregation calls.83,778 global callbacks; zero faults,
  no budget exhaustion and no pending frames/pairs at freeze.
- Normal native exit0; all152 subscription entries/149 IDs and original
  autostartfalse restored; CSC/stock CE file manifests unchanged; owners absent.
- 23 isolated observer checks;15 Python checks covering actual Lua, source
  guards and the offline analyzer. Four loaded entry fingerprints verified before
  hook installation. Instrumentation was retained until native exit, not detached
  from a running game.

Code: [observer and reproduction tools](../../../tools/native_ai/bakers_components/README.md).
Static path: [native review](csc-ai-bakers-native-component-review-20261104.md).
Gameplay truth: [rules ledger](csc-ai-bakers-gameplay-component-review-20261104.md).

Scope is the pinned Windows GS build and these two city evaluations. No claim
of corrected decisions, net economic benefit, RH/multiplayer compatibility or
an automatically safe native repair follows.
