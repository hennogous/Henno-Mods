# Bakers building benefits and the forecast audit

> Follow-up: the [component observation](csc-ai-bakers-forecast-components-20261104.md)
> subsequently confirmed the phantom encoding-bit forecast. This memo preserves
> the gameplay truth and initial measurement proposal; it is not the final result.

4 November 2026. Read-only source and cached-rules review for the question:
which future-building contributions at a weak Bakers site reflect real CSC
benefits? This memo supplies the gameplay half of the investigation. It does
not measure a new native score or explain the original Delhi/Majapahit totals
numerically. No game was launched, loaded, controlled or instrumented.

## A new, specific forecast suspect

Both Mill variants have ten generated building-owned adjacency wrappers, with
child Production amounts **1, 2, 4, 8, 16, 32, 64, 128, 256 and 512**. Their sum,
**1023**, is the encoding capacity, not the intended yield of a Mill.

In real gameplay Lua sets only the bits representing the actual bonus. The Wind
Mill rule gives +1 Production when its own plot is hills; Water Mill gives
`truncate(0.5 × river-edge count)` Production. The property gate belongs to the
child modifier's **OwnerRequirementSetId**. The parent enumerates
`COLLECTION_PLAYER_DISTRICTS` with no owner or subject requirement; the child
uses `COLLECTION_OWNER` and `EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE`. There is
no separate district-type condition in this generated parent/child pair: the
gameplay writer's plot-property key selects the intended Quarter.

The [earlier native interpreter study](csc-future-economy-forecast-20261103.md)
establishes that the inspected AI compiler reads SubjectRequirementSetId rather
than OwnerRequirementSetId and does not register the plot-property requirement.
This creates a concrete risk that a hypothetical Mill forecast counts all ten
encoding bits against iterated districts. That is a **source-grounded candidate
for measurement**, not a claim that 1023 Production, or a particular utility
amount, entered Delhi's score. Nested collection/effect context and native
discounting still need checking; an admitted modifier can also contribute zero
when required analysis context is absent.

Source anchors, relative to `Civ Supply Chains/`:

- `Lua_UI/Adjacencies/CSC_AdjacencyProcessor.sql:270–369`: Mill rules.
- `Lua_UI/Adjacencies/CSC_AdjacencySchema.sql:42–47,69–70`: SelfBonus provider
  and ten-bit ladder.
- `Lua_UI/Adjacencies/CSC_AdjacencyModifiers.sql:91–119`: generated property
  requirements, owner gate and child amounts.
- Same file `:133–152`: ungated player-district parent and building attachment.
- `Lua_UI/Adjacencies/CSC_AdjacencyCore.lua:366–388`: truncation, magnitude and
  bit-property writer. Fractional amounts are truncated before encoding.

## Real building benefits to preserve

Costs below are declared database base Production costs. They are not the
Online-speed quote, remaining queue work or a native utility subtraction.

| Building | Declared unlock / cost / maintenance | Real benefit and conditions |
|---|---|---|
| River Access / No River Access | Internal, cost 0, maintenance 0, MustPurchase 1 | District-granted implementation flags. River Access permits Water Mill; No River Access excludes it. Neither is a player investment or intrinsically productive building. |
| Wind Mill | Machinery; 80 / 2 Gold | +1 Quarter Production on a hills Quarter tile. Material/customer/local exchanges below. No intrinsic amenity or citizen slot. |
| Water Mill | Engineering plus River Access; 80 / 2 Gold | Quarter Production from river edges in half-point steps, truncated by the shared adjacency encoder. Material/customer/local exchanges below. Mutually exclusive with Wind Mill. |
| Bakery | Guilds plus either Mill; 160 / 2 Gold | One local amenity and one citizen slot. An assigned specialist gives 2 Food; that is not passive building Food. Local Mill exchange, ordinary Market sales, conditional Service and exports below. |
| Café | Humanism plus either Mill; 250 / 3 Gold | One amenity with RegionalRange 6 and one citizen slot. An assigned specialist gives 1 Food and 1 Culture. Local Mill/material/customer exchanges and conditional Services/exports below. Range 6 does not extend the one-hex transactions. |

The loaded DB contains **no Building_YieldChanges rows for any Bakers building**.
Do not describe Bakery specialist Food or Café specialist Food/Culture as free
flat yields. Real building income can nevertheless arrive through live
BuildingYieldChange modifiers and other effects.

Definition evidence: `Data/CSC_Q_BAKERS.sql:390–566,619–663`. The cached DB confirms
all fields and the exact five prerequisite edges. Bakery and Café each list
Wind Mill before Water Mill in the SQL, but SQL text/row order alone does not
prove native first-prerequisite vector order. Café does not require Bakery.

## Exchanges, population returns and Services are different benefits

| Relationship | Actual benefit | Actual gates / forecast concern |
|---|---|---|
| Improved Base material → Mill | +1 Food to the relevant Mill per qualifying adjacent improvement | Real material improvement, tag, same-owner adjacency and functioning receiver. A currently applied per-building yield can reach native building valuation; an unbuilt Quarter is not a simulated future material network. |
| Mill → Base material | +1 Production and +1 Gold to qualifying adjacent improved Base plots | Producer building and adjacent improved material. Reverse wrapper uses PLAYER_IMPROVEMENTS, absent from the inspected AI collection registry. This is real gameplay value that may be missing from the hypothetical forecast. |
| Mill ↔ Granary | +1 Food to adjacent functioning Granary; +1 Production and +1 Gold to the relevant Mill | Ordinary exchange; no Service civic or improved-Base requirement. Native ordinary HasBuilding checks actual Granary presence, while its non-unit adjacency approximation does not itself calculate plot distance. |
| Local Mill ↔ Bakery | +1 Food to Bakery from Mill; +1 Production and +1 Gold to Mill from Bakery | Local buildings, independent of material supply or an adjacent Market. Both Mill type child definitions exist but actual yields apply to the built variant. Measure whether hypothetical missing-building effects credit both variants. |
| Bakery ↔ Market sale | +0.105 Food per customer citizen to customer's city; +0.105 Production and +0.105 Gold per customer citizen to Bakery's city | Actual functioning Bakery/Quarter and same-owner adjacent functioning Market. Current population, cross-city and multiple-seller sums calculated by Lua. **No improved-Base or Service civic gate** for this ordinary sale. |
| Improved Specialty material → Café | +1 Food to Café per qualifying adjacent improvement | Actual improved Specialty material and owned adjacency. Separate from Service full-supply requirements. |
| Café → Specialty material | +1 Production and +1 Gold to qualifying adjacent improved Specialty plots | PLAYER_IMPROVEMENTS hypothetical-support limitation as above. |
| Local Mill ↔ Café | +1 Food to Café; +1 Production and +1 Gold to Mill | Local buildings. Does not require Bakery, material supply, Urbanization or a Stage 4 customer. |
| Café ↔ Stage 4 sale | Each eligible adjacent Zoo/Ferris/Conservatory customer city supplies `floor(customer population / 5)` stacks: Culture to customer building, Production and Gold to Café | Actual functioning Café/Quarter, same-owner adjacent existing customer district with functioning customer building. No improved-material or Urbanization gate for the ordinary sale. Compatible customer families are loaded conditionally. |
| Mill Service | +10% growth, Storekeeper grant, +1 Great Engineer point at adjacent Granary city | Feudalism, improved Base beside the Mill and functioning adjacent Granary. The complete source gate is an owner requirement. Missing/omitted AI requirements could admit benefits without the real service conditions. |
| Bakery Service | Innkeeper grant/citizen slot, +2 Housing, +1 Great Merchant point at adjacent Market city | Medieval Faires, improved Base and adjacent Market presence through the SQL HasBuilding requirement. Separate from ordinary population sales and their explicit Lua functioning checks. |
| Café Service | +2 Tourism, appropriate service grant/citizen slot, +1 Great Engineer point at eligible adjacent customer | Urbanization, improved Base **and** Specialty, adjacent qualified Stage 4 customer through the SQL HasBuilding requirements. These conditions do not gate its ordinary amenity or sales. |
| Bakery/Café route exports | Production and Gold returns for qualifying import routes to supplied producers | Actual source supply properties plus Lua route counts. Bakery requires Base; Café Base and Specialty. City Center owns the bit consumers; they are not active building-owned roots in the candidate's modifier vector. |

Active roots: core `:674–780`; Gold companion `:24–103`. Modifier definitions and
arguments: core `:808–1195`; requirement members `:1348–1435`; Gold companion
`:117–264`. This table describes source topology and real rules, not observed
numeric utility or universal native visibility.

Ordinary Stage 3 and Stage 4 population transactions are maintained in
`Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua`:

- `:165–204` functioning building/district checks;
- `:401–430` actual seller/customer collection;
- `:437–501` same-owner, functioning building, customer population and stack sums;
- `:504–534` six-neighbor adjacency traversal;
- `:538–600` scaled rates / bit-property publication.

Their consumers attach to City Center, once per receiving city, to avoid paying
the Lua sum once again for every seller (`CSC_Q_BAKERS.sql:313–369` and Gold
companion `:70–104`). Current-state property consumers and a future candidate's
BuildingModifiers vector are different channels. A live building yield can
reflect realized transactions; that does not prove a hypothetical candidate
reruns the Lua network calculation.

The Lua customer-side district locator checks presence/location, while the
customer building receives the explicit functioning check. It does not
separately call the customer district's IsPillaged check. The seller explicitly
requires both functioning building and functioning Quarter. Keep these source
conditions precise rather than silently adding a symmetric customer gate.
Similarly, the inspected SQL sets MustBeFunctioning=1 explicitly for Granary;
it does not supply that argument for the Market/Zoo/Ferris HasBuilding leaves.
Do not copy the population Lua's explicit functioning test onto every SQL
Service requirement without checking the native gameplay default separately.

The old direct Bakery→Market wrapper and Café→customer children remain defined
but are **not active building attachments** in this source. They cannot be
listed as measured candidate contributions merely because their definitions
are present (`CSC_Q_BAKERS.sql:855–860,887–892`).

## Pinned rules evidence

Read-only SQLite URI inspection used the existing local
`AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite`.
Its exact SHA-256 is
`23e880dea5dafd26da27a8a91e60f917ffabf133791127fa45c2d667f1888be5`,
12,410,880 bytes. This is a cached **rules database**, not a saved world's city
state and not a measured native forecast.

Full SQL queries and rows are retained outside the repository in
`Desktop/Codex/csc-bakers-gameplay-components-20261104/rules-audit.json`:
SHA-256 `dc98f89129472f066adab85c976bdfa56fdea8c66e097d90a4a0cf0326e592b6`,
934,945 bytes. It includes 10 Buildings, 5 prerequisite edges, 3 exclusions,
0 flat-yield rows, 7 specialist rows, active roots, 458 Bakers-related modifier
definitions with collection/effect resolution, 922 argument rows, requirements,
17 Bakers adjacency rules, bit ladder, transaction registry and source pins.
This is a portable query receipt; the full game DB is not redistributed.

All eight inspected source files match the installed mod after UTF-8/BOM/newline
normalization. Seven also match exact bytes. Core Bakers SQL differs only in
line endings; its normalized text is identical. No installed file was changed.

Important source exact-byte SHA-256 pins:

| Path under Civ Supply Chains | SHA-256 |
|---|---|
| Data/CSC_Q_BAKERS.sql | ac9c01aadfad575e2269b8cbde3360a0488c5f4f432e4d37e2caab6196fb76e7 |
| Data/CSC_Q_BAKERS_GOLD.sql | ae289c5dd0e9d0382e4d8f4dcf19dee837b4589ac822ffaf688bda31acbc1f1c |
| Lua_UI/Adjacencies/CSC_AdjacencyModifiers.sql | 2fe744ca28d6525910e1a4fb2b0f06a5c9d961c721cdca9735eb69a0996fb084 |
| Lua_UI/Adjacencies/CSC_AdjacencyProcessor.sql | ba0dd259821e013ea1360f75523df9b13beb94084dad5570bb3baac2d0b91145 |
| Lua_UI/Adjacencies/CSC_AdjacencyCore.lua | 813acb3de6750922ada38f1baa898833f2ca5e04d34014c62e6926c5b93e9f2b |
| Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua | b196d4f94f0ff4e6740ee881f4276166d8974de4c328c66401a0abc16042cef7 |

## Smallest useful next measurement

Before changing scores, observe one native building-vector pass for a city with
a missing Bakers Quarter. Record each Mill/Bakery/Café's raw building value and
subsequent district propagation separately. For each Mill also record its
modifier-vector total and the nested generated-adjacency children with amounts,
actual district context and property value. Compare the ten-bit forecast to
the actual allowed geometry bonus. This distinguishes a phantom encoding sum
from legitimate amenities, local exchanges and city-dependent costs.

Do not subtract 1023, zero all building forecasts or remove the district uplift
on source suspicion alone. The decisive observation is the returned native
component, not the sum of declared modifier amounts. Preserve legitimate native
benefits and correct only the measured CSC discrepancy. Readiness, independent
competing sites, retained requests and later construction remain separate.
