# Native harvest rule: partial results through turn 50

This is a counterfactual replay of the same turn-16 saved world used by the raw
resource-forecast control, not an independent world or untreated AI baseline.
The diagnostic continues unchanged toward75; its final audit is pending.

The only additional intervention is one explicit attachment of the shipped
`TRAIT_MAORI_PREVENT_HARVEST` to players1..5. Five active native instances,
observer0 exclusion and three stable readbacks are independently verified.
Initial world, funds, units, real yields, queues and direct citizen allocation
match the raw arm. Native eligibility changes are recorded: resource plots can
no longer be replaced by Quarters, and Hojo initially has no owned legal Tailors
site. This is a coarse all-resource rule, not targeted supply preservation.

| Observed at50 | Raw control | Native rule |
|---|---:|---:|
| Cities | 10 | 9 |
| Population | 62 | 58 |
| Quarters | 15 | 11 |
| Complete Quarters | 11 | 10 |
| Producer buildings | 1 | 1 |
| Functioning producers with improved owned Base proxy | 1 | 1 |
| Confirmed material harvest losses through50 | 3 | 0 |
| Matched repair episodes | 3 | 2 |

The zero loss count refers to observed material-care links through this closed
checkpoint, not all map resources or universal protection. Outcomes and economic
tradeoffs are descriptive; city and Quarter differences cannot be assigned to a
single internal native decision from these counts.

## Rejected work, then eventual adaptation

At25, protected Cattle2533 remains owned and unimproved. Builder327683 is on the
tile with one charge. On turns21–24, UnitOperations logs four rejected harvest
records and five rejected BuildImprovement records. The same-player/unit/turn
behavior tree has one reserved target:2533, with a Farm plan. Despite the native
`Can't Start` records, Clear Plot and Build Improvement nodes report SUCCESS.
Node SUCCESS is therefore not a reliable measure of actual native effects.

This loop continues through26: six observed rejection turns. A Pasture plan is
first recorded27. At28 the care ledger changes develop→working and a native
BUILD_IMPROVEMENT event identifies Builder589829 at the exact17,34 coordinates.
The turn50 census confirms a Pasture and the original Cattle. This is a verified
successful development after a bounded rejection episode, not permanent idling.

Joao's Sheep2269 is working from42 and remains under a Pasture50; the control
harvests that Sheep45. Two native build starts occur for Joao42, one with invalid
last-charge coordinates. Without a unique plot match, do not assign this Sheep
improvement to a specific Builder merely from the same player/turn coincidence.

At50 another repeated rejected Farm route targets non-CSC Stone1868. Builder
851974 is there with three charges. This illustrates the rule's broad scope;
protecting supply must account for wasted work and useful non-CSC development.

## Guidance implications and next hypothesis

The rule changes actual legality and preserves materials in these cases, but
native jobs can keep requesting a now-illegal harvest before selecting a valid
improvement. Merely adding Builder demand does not resolve this selection step.
Track repeated rejected native requests separately from behavior-tree failures,
and distinguish a bounded loop that resolves from a persistent unresolved one.
Do not use all-resource harvest prohibition as a finished targeted solution.

An uninstalled follow-up is staged in `offline-preparation/source016-pasture-forecast`.
It adds80 private YIELD_CSC_AI_PLACEMENT directly to native Improvement_YieldChanges
for Pastures, with no harvest ban. This tests whether the forecast representation
changes a fresh Farm-over-Cattle choice. Existing requirement-gated improvement
modifiers and direct forecast data may be evaluated differently; consumption is
unproven. No Pastures exist in the archived observed source16 census, so strict
source parity remains required. Only one additional native table differs from
raw control; all real resource/improvement yield rows stay unchanged and the SQL
is idempotent in the actual446-table schema. It is not installed or driver-ready.

This broad Pasture signal affects humans and all Pastures, and adds relative
value as well as changing representation. A positive result alone would not prove
a targeted, calibrated AI-only release design. Native testing must wait for
current75 completion/audit, owner absence, original510/preferences restoration,
archived executed sources and new distinct branch/driver provenance.

## Evidence and limits

Current branch: raw-resource016-075-native-harvest-live-v4c.
- independent-native-rule-startup-confirmation.json:418pins/source archives,
  exact measured legality response and direct citizen parity.
- independent-checkpoint025-comparison.json and checkpoint050 equivalent:
  exact native outcome clocks and closed log byte boundaries.
- independent-rejected-work025.json and rejected-work050.json with corresponding
  control reports preserve raw native rows and conservative target associations.
- Native care/Builder/primary records support the later development observations.

New unpinned H/material-rejected-work-intelligence.py has ten counterexample
checks plus actual25 schema/episode validation. Final comparison is extended to
include these paths and development evidence. Exact rejected log rows need not
be unique requests. A missing endpoint Builder does not prove death; a nearby
Builder is not free-worker or path proof. Actual Service payments remain
unobserved. All current native source pins and installed runtime stay frozen.
