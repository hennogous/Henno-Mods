# What native AI forecasts about CSC materials and customers

Investigation: 3 November 2026. Question: does native Civ VI AI account for future
material supply and customer demand when placing Quarters and choosing their
production buildings, beyond ordinary BuildingPrereqs?

**Partly, through specific inputs; the inspected paths do not simulate the whole
future supply chain.** Existing material effects and deliberately supplied private
building-yield signals can reach valuation before a producer exists. Ordinary
customer-building gates, unsupported modifier collections, current-state Lua
returns and a simplified AI requirement interpreter prevent those individual
channels from being treated as a faithful forecast of a jointly missing chain.

This was an offline investigation. No game, autoplay, deployment, score change,
forced order, new planner or native-target mutation was performed. The older
broad AI campaign remains paused. This report follows the
[IZ architecture study](civ6-industrial-zone-planning-architecture-20261101.md) and
[its three-turn runtime check](civ6-industrial-zone-decision-boundary-20261101.md).

## Evidence boundary

Current Windows XP2 DLL SHA-256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The installed DLL and Ghidra target match. Native addresses below are RVAs from
image base `0x180000000`; recovered types/names remain estimates.

Live CSC source was read and copied with hashes on 3 November. This matters:
population sales now use a Lua/property bridge and City Center consumers. Some
older building-owned transaction definitions remain in SQL but are not attached.
Historical native observations describe their own packages/profiles, not an
execution of today's entire source tree.

Evidence package:
`C:\Users\Shadow\Desktop\Codex\csc-future-economy-forecast-20261103\`.
It contains the pinned `data-source-audit.md`, `source-snapshot/`, `source-pins.json`,
named Ghidra exports, raw collection-pointer chains and static disassembly,
`verification.json`, and `rea-evidence-bundle.json`. The bundle contains 33 records:
18 reused IZ records plus seven new complete function dossiers, their summary
receipts and one selected code view. REA/Ghidra 12.1.4 fresh analysis independently
corroborates the prepared Ghidra 12.2 exports. Seven new dossiers report no
value-flow truncation, but retain unresolved indirect calls and provider limits.
813 instructions from four decisive functions were checked byte-for-byte against
the pristine DLL. Small collection handlers missing analyzed function boundaries
were decoded statically with existing Capstone; no target code was executed.

## Answer by relationship

| Relationship | What is established | What is not established |
|---|---|---|
| Explicit building prerequisite | IZ work proves future Factory value can raise missing Workshop value. | A persistent Factory-rooted construction plan. |
| Existing material feeding an unbuilt producer | Native building valuation reads per-building yield adjustments; an earlier real trace captured private +80 for an unbuilt Textile Workshop. | That it schedules the improvement, protects the material or measures the chain's eventual benefit. |
| Unimproved mapped resource beside an existing Quarter | RH source deliberately supplies Workshop +80, plus +40 for Both material presence. | Actual improvement readiness, required improvement unlock, terrain legality or Builder capacity. |
| Existing customer district | Native ordinary adjacency rows supply co-location inputs; private forward/reverse sales hints use existing neighbors. | Search/reservation of a missing future customer district or coordinated completion. |
| Missing ordinary customer building behind a HasBuilding gate | Native AI tests actual ordinary building presence; it does not substitute its hypothetical building index. | Credit for completing both currently missing partners through that gate. |
| Producer benefit to material improvements | Current producer-owned wrapper uses PLAYER_IMPROVEMENTS, absent from the inspected AI collection registry. | Hypothetical value through that wrapper; other live-yield/forecast routes remain separate. |
| Population sales / later returns | Current Lua computes from actual functioning source/customer objects and writes properties. | Re-running that Lua with a hypothetical Quarter/producer/customer during native candidate evaluation. |

## 1. There is a real prospective-building input channel

Building Value (`52b900`) iterates dynamic YieldDefinitions and calls live city
Buildings::GetYieldChange (`10c0e0`); positive values enter normalization. It also
evaluates a precompiled modifier vector through ModifierValue (`529ed0`) and
GameEffectAnalyzer (`48e9e0`). These are distinct sources of value: currently
applied building adjustments need not rely on hypothetical modifier analysis.

The earlier [producer decision observation](csc-ai-producer-decision-20261030.md)
captured an unbuilt, legal Textile Workshop's fresh NetValue call 73, nested live
private-yield getter 74 returning 80, later best-building selection and actual
queue entry. Its off arm never ran, so this proves delivery and consumption, not
the marginal choice effect or economic benefit of 80. It also exposed a different
valid evaluator call site from an earlier observer's admitted return address.

Current RH source deliberately supplies that kind of input:

- `ModSupport_RH_AI.sql:206–270`: an existing Tailors Quarter owns private
  building-yield changes to Textile Workshop, BASE 80 plus BOTH_EXTRA 40.
- `ModSupport_RH_AI_Roles.lua:34–130`: scans six actual neighboring plots for
  owned, visible, district-free mapped resources. Global Improvement_ValidResources
  membership admits a resource type; it does not establish a currently legal,
  unlocked improvement or available Builder.
- The Lua writer itself does **not** require Quarter completion/unpillaged state
  or producer absence. The historical successful native case had a completed
  Quarter; that observed state must not be promoted into a writer gate.

This is a CSC-authored potential signal attached to an existing map object. It
does not prove that native AI discovered the economic dependency or searched for
all future objects itself. Profile/action eligibility still governs whether RH
integration is active; today's source inspection is not a newly loaded RH game.

There is a second source-level customer bridge at `ModSupport_RH_AI.sql:57–202`:
an existing functioning Wind/Water Mill supplies private +40 to Granary/direct
replacements through player districts and owned City Center selection, without
requiring Granary to exist. That deliberately differs from the real Mill→Granary
exchange, whose recipient gate requires Granary. This report establishes the
bridge's source topology, not a fresh native +40 contrast or production response.
Its owner gates also require the configured-AI property and inverse current-human
test; it is not an unconditional signal for every player or city.

## 2. Real exchanges and ordinary customer gates differ from prerequisites

For Bakers, live source attaches material-improvement→Quarter→Mill Food effects,
Mill→material Production effects, and Mill↔Granary effects. Tailors has analogous
but distinct Workshop↔Lighthouse/material and local-building relationships.
Exact active roots, effects, requirements and hashes are in the source audit.

The generic AI AdjustBuildingYieldEffect (`475a50`) can value an adjustment to
an absent target building, multiplying its normalized stream by **0.5** before
discounting. The constant was read from the pristine PE. That is some future
recipient capability, but it operates only after collection and requirements
admit the effect.

In the real Mill→Granary wrapper, subject requirement
`REQSET_CSC_ADJ_CITY_CENTER_GRANARY` contains CITY_HAS_BUILDING for Granary
(`CSC_Q_BAKERS.sql:829`, requirement definitions/arguments later in that file).
The AI handler at `490c90` tests actual HasBuilding for ordinary buildings and
never reads the hypothetical candidate building index at analysis+4. Its special
branch is for **IsWonder**, verified through the SQL loader, not ordinary
Granaries, Workshops or Lighthouses. Thus an absent Granary does not pass this
ordinary test merely because its future benefit would be useful.

The supported PLAYER_DISTRICTS iterator uses actual player districts when player
context is present. Its no-player fallback can yield one hypothetical district
index; that is not a search for future district locations. DistrictTypeMatches
(`492d00`) checks an actual district first and only falls back to the candidate
index if there is no actual district pointer.

Moreover, these AI approximations are not complete geographic simulation.
PlotAdjacentToOwner (`490660`) performs no plot-distance calculation in the
ordinary no-unit context; it accepts player presence there. Other gates may
still constrain an effect. Do not turn an admitted contribution into evidence
that exact same-owner adjacency and the recipient city's state were faithfully
simulated. The underlying gameplay requirement system is a different component.

## 3. The hypothetical modifier interpreter supports a subset of gameplay

GameEffectAnalyzer's constructor (`4891b0`) registers effect, collection and
requirement handlers. InitializeModifierAnalysis (`48eb10`) resolves dynamic
modifier details and looks up effect/collection handlers. A missing handler
leaves a null pointer and initialization fails; AnalyzeModifier also refuses
those nulls.

The explicit 27-collection registry does not contain
`COLLECTION_PLAYER_IMPROVEMENTS`. Current CSC producer→material wrappers use
exactly that collection (`CSC_Q_ALL.sql:26–29`; Bakers `:825`, Tailors `:791`
and later Fashion House roots). Hence the inspected hypothetical interpreter
does not value those wrappers through a supported player-improvements traversal.
This is not a claim that real gameplay modifiers fail or that materials have
zero value everywhere in AI.

Requirements fail differently. Constructor `48ca30` appends only registered
requirement types; unrecognized types are omitted. `48ef40` evaluates the resulting
ALL/ANY/NONE lists. An ALL set with no retained requirements succeeds. The
registry lacks `REQUIREMENT_PLOT_PROPERTY_MATCHES`; its nested-set registration
is the exact string `REQUIREMENTSET_IS_MET`, whereas CSC uses
`REQUIREMENT_REQUIREMENTSET_IS_MET`. No alias was established for that mismatch.

The modifier compiler fetches virtual definition slot +60, independently proved
to be **SubjectRequirementSetId**. OwnerRequirementSetId is slot +58 and is not
compiled by this body. These are observations about this AI interpreter, not
about actual modifier activation in gameplay.

Consequently, even a positive hypothetical value need not mean faithful economic
foresight: a supported/reachable effect may be approximated after owner/property
gates were omitted. Conversely an unsupported collection or missing context can
produce no contribution. We did not measure the score impact of today's
population-bit consumers or claim that every omitted gate overvalues a candidate.

Fresh REA dossier IDs, complete in the bundle:

| Native fact | Parent Evidence ID |
|---|---|
| Modifier compilation `48eb10` | `ev_a4460c2bd7ec08f31b6745cccc327811f43239d15bf2a2aa0cc0108da3b250af` |
| Requirement compilation `48ca30` | `ev_d1dd3bfdecf9c4c73d7a2472688adad998d2445bf82a7c4ab42ffc1632b345ef` |
| Requirement evaluation `48ef40` | `ev_ff93587eaf432be438a2c4e82b672c4622e4242e973f7314bbc149c0bc9e7fdc` |
| Modifier evaluation `48e9e0` | `ev_bd6cf8e8ae905d4e17cdafecf32ffd2574c2bd037ca8b78bc469513f762432f9` |
| Ordinary building-presence test `490c90` | `ev_49c494dd9ab5021ac4ef4159130f26d427ace3ed251f52953987eb65487ccc42` |
| Missing-recipient building effect `475a50` | `ev_fec59aa4e3461501f71416f48fa0cb47bf249a82ee35cd901db26d94a8c31b0c` |
| Aggregation of modifier values `529ed0` | `ev_0ac5b62241f43e75923a7b1a3ed25f33c3aaa3a29698b11a08b3b7a1d28540fc` |

## 4. Plot context: correction to an earlier native note

The exact current pointer chains are:

- PLAYER_PLOT_YIELDS: `b65bc8 → 9feea0`.
- SINGLE_PLOT_YIELDS: `b65bd8 → 9feea0`.
- Both use initializer `4637b0`, next `4636b0`, finalizer `8972d0`.
- OWNER: `b65ba0 → 9fee10`, a once-only flag iterator.

The shared plot handler consumes an already supplied analysis+88 plot exactly
once. It neither enumerates plots nor fills +88. OWNER also does not fill it.
The ordinary non-placement building branch passes sentinel (-9999,-9999)
coordinates into NetValue/Value; its guarded plot assignment remains empty.
The inspected DistrictValue (`52d500`) context also leaves +88 empty.
The plot-yield effect's no-subject callback (`9b1040`) returns true without
changing the accumulator. Thus these **direct top-level forecast paths** do not
gain a plot-yield contribution through that handler with an empty plot context.
Placement-specific/nested routes and live gameplay remain separate.

Earlier native notes mislabeled the `4634d0/4634f0` city iterator as
PLAYER_PLOT_YIELDS. Withdraw that mapping and its claimed city-enumeration
mechanism. The corrected limited omission above has a different, independently
verified pointer-chain/byte basis. The
[placement-weight report](csc-native-quarter-placement-weights-20261101.md)
now links this correction; no prior failed placement observation is relabeled
as a successful scoring experiment.

## 5. Lua returns are realized-state calculations, not candidate callbacks

Current CustomerPopulationReturns Lua requires actual functioning seller and
Quarter, actual same-owner adjacent functioning customer building, and current
population. It writes bit properties; SQL City Center consumers apply the
corresponding returns. Ordinary Stage 3 sales do not require the material supply
or civic Service gates; those belong to different mechanics. Missing materials
therefore cannot be treated as synonymous with zero building income.

Stage 3 seller/customer returns use OWNER/city-yield-per-population effects.
Stage 4 and export consumers can instead adjust named building yields, despite
being attached at City Centers. The AI does register the per-population effect
and OWNER collection, but lacks the property requirement described above.

The native candidate paths inspected here do not call CSC's Lua matcher or
population-return writer with a hypothetical proposed chain. Ordinary Stage 3
consumers are not attached as producer-owned roots. This prevents assuming that
building a hypothetical Bakery automatically recomputes all its future sales in
its own modifier vector. Which current Stage 4/export adjustments appear in a
particular live per-building getter remains a separate runtime question; this
investigation does not replace that with an assertion of universal zero value.

Similarly, the bundled adjacency engine writes from existing completed source
districts and current matching map facts. UI previews sharing its matcher do not
establish a native C++ call into those previews during AI placement. Standard
native adjacency/private co-location hints are a separate, verified route.

## What this resolves and what remains

**Answered at the code/source level:** CSC has distinct present-state delivery,
explicit prospective private inputs, prerequisite propagation and approximate
modifier-analysis channels. Current missing-building gates and collection/context
limits explain why none can be assumed to evaluate an entire jointly missing
material–producer–customer network. A positive private signal is not proof of
that network being planned or fulfilled.

**Still unmeasured:** today's exact total score response to future-customer
signals, the marginal contribution of every current property consumer, actual
completion/recovery of a newly selected chain, and economic benefit. No claim of
universal AI blindness, general absence of planning, or new tuning efficacy follows.

The useful implementation boundary is now clearer: native prerequisites and
already-delivered incremental building yields are usable inputs; credible
future material/customer development needs an explicit forecast contract rather
than reliance on gameplay gates being simulated automatically. Before choosing
weights or a broader planner, specify that forecast's availability, location,
cost/time and competing-opportunity assumptions. A later test should isolate one
such input at a fresh decision boundary, using an existing save and the shared
controller where possible. No game was needed for the distinctions established
in this report.
