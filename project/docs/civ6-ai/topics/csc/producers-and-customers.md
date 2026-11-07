# Producer and customer follow-through

The corresponding engine model is [prerequisite value and production](../native/production-and-prerequisites.md)
and [prospective modifier evaluation](../native/modifier-forecasts.md). These
separate missing-prerequisite foresight from an actual customer-building gate.

The AI can value a missing building and complete useful work in individual cases. The question is how that work passes caches, contracts and competing production, then keeps functioning supply.

```mermaid
flowchart LR
 D[Definition] --> V[Fresh value] --> R[Accepted request] --> Q[Queue selected] --> B[Completed building] --> W[Working retained path] --> E[Benefit]
```

## A retained Bakers Stage 2 chain in Boston

The matched tests kept Boston's exact Cattle Pasture next to a working Water
Mill and Granary. Engineering and Feudalism advanced through normal research.
At turns 63 and 66, the Granary produced 2 Food against a base of 1, the Water
Mill produced 1 Production and 1 Gold, and the Storekeeper marker and Growth
property were active. The earlier replay also showed the ordinary exchange
still producing after the supplier was lost, while Storekeeper stayed absent.
[AI-C061] [AI-C062]
[Boston evidence and turn-66 checkpoint](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#retained-stage-2-chain-verified-at-turns-63-and-66).

The first long continuation kept the same chain working for 141 full turns.
The Pasture first failed on turn 207, when a blizzard was logged nearby. The
turn-210 save showed Cattle without a Pasture, a pillaged Water Mill, an intact
Granary and zero Storekeeper Growth even though its marker still existed.
[AI-C063] [Retention and damage evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-chain-stayed-active-for-141-turns-before-damage).

In a separate continuation from turn 90, the same chain worked through the
turn-242 save. The original supplier, Mill, Granary and Storekeeper held
through 152 completed turns, with Granary and Mill Food verified separately.
The earlier Boston blizzard did not recur in this playthrough.
[AI-C064] [152-turn audit](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-same-chain-passed-152-turns-in-a-separate-continuation).

The late Boston chain's stock Mill repair waited behind Encampment and
restored its building yields. The Pasture remained missing. In a separate
early test with only the Mill pillaged, the city repaired it after finishing
University. The existing Pasture and Granary then supported the restored
exchange and Storekeeper. [AI-C069]
[Mill-only recovery evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#mill-only-damage-restored-the-full-service).

## The Wind Mill needed an ordinary nomination in Melbourne

Melbourne already had a working Rice supplier, an adjacent
Granary and Feudalism. An ordinary nomination preference changed
the offer from Amphitheater to Wind Mill. The offer kept the
native building cache value, and the queue refreshed and accepted
it at the next opening. Melbourne completed the Mill and operated
Storekeeper on turns 138–143. The matched control completed the
Amphitheater and had no working Storekeeper in Melbourne.
[AI-C090] [AI-C091] [AI-C092]
[Matched production and payout](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#melbourne-executed-the-wind-mill-offer-at-its-native-refreshed-value).

The main CSC publisher now bids for an unlocked, missing Mill when
the working Base, customer and Feudalism are in place. The CE review
build changed the ordinary nomination once and reproduced the offer,
completion and Storekeeper at the same checkpoint without an external
writer. The amount is an initial calibration. [AI-C093]
[Integrated replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#integrated-ce-nomination-reproduced-melbournes-wind-mill-and-service).

A City Center building that replaces Granary can serve as a
Bakers customer. CSC copies the
Granary's outgoing exchange attachments to those building definitions.
The native functioning-building requirement and receiving Food modifier
both resolve the target through the owning player's replacement table.
This has been checked in the executable. The matched payout tests used
the ordinary Granary. [AI-N102]
[Replacement trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#granary-exchange-resolves-the-receiving-players-building-replacement).

## Ancyra still needed both buildings

Ancyra's Granary was legal but lost twice to Castle in ordinary
nomination. Its available production slot went to a Cuirassier
contract. The missing Mill meant the Granary would still be one
step short of completing the exchange. The comparison margins
measure the competition in this city. [AI-C094]
[Granary decision trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#ancyras-legal-granary-lost-nomination-and-a-military-contract-took-production).

In Trebizond a working Water Mill could supply the Granary as
soon as it existed. The legal Granary lost its ordinary
nomination to Library, and neither earlier queue opening
included a Granary offer. The Wheat Farm remained a separate
Storekeeper requirement. [AI-C095]
[Trebizond control trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#trebizonds-working-mill-gave-a-closer-granary-comparison).

A matched test changed the nomination to Granary, and the game
validated that offer at its own cache value. Theater Square still
occupied production at the endpoint. [AI-C096]
[Trebizond nomination replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#a-matched-trebizond-nomination-produced-a-valid-granary-offer).

Trebizond bought that exact Granary offer through its ordinary
Gold budget. It used its open production slots for Library and
Encampment. The Water Mill was pillaged by the late endpoint.
A shorter replay captured the exchange before the damage.
The Granary gained one Food, and the Mill gained one Production
and one Gold. [AI-C097] [AI-C099]
[Purchase trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#trebizond-bought-the-granary-through-the-admitted-contract).

## AI-C024 — Private producer value reached an unbuilt Workshop decision

A bounded trace captured a legal unbuilt Textile Workshop’s fresh NetValue and nested private getter 80, later best-building selection and queue entry. This is stronger than a UI preview or loaded row.

Scope: Historical Kobdo 110/111 RH package and current-build native consumer investigation.

Limits: The OFF arm never ran. Delivery, consumption and one choice do not prove 80 caused that choice, completion or economic benefit. Today’s population/property-consumer source is not the historical package.

Sources: [Producer decision](../../../research/mods/csc-ai-producer-decision-20261030.md), [live effect](../../../research/mods/csc-ai-producer-live-effect-20261029.md), [current source distinction](../../../research/mods/csc-future-economy-forecast-20261103.md).

## AI-C025 — Accepted work can wait behind another queue

The exact target district request was accepted 103/105 while Builder production continued, selected/Execute at 109 when the queue emptied, and completion-censored at 110. Native construction can use a prepared foundation without an immediate queue replacement.

Scope: Single-target existing-city observation and static contract trace.

Limits: Priority, PresentValue, retained contract value, best-building fallback and final queue arbitration differ. No general finish-first override was proved.

Sources: [Foundation observation](../../../research/mods/csc-ai-foundation-observation-20261029.md), [decision path](../../../research/mods/csc-ai-foundation-decision-path-20261029.md).

## AI-C026 — Strategy building inputs loaded without the hoped response

Twenty-seven CSC counterparts added to RH strategy Buildings lists had verified definitions/adoption but V 7’s physical state, finance and scoped construction/strategy/tree logs matched V 6 through 150. A conditional Granary strategy later reported true/Following while the observed ordinary building path still received preference 0.

Scope: Fixed-A RH package comparison and separate bounded Granary delivery probe.

Limits: These are route/context non-responses, not unsupported Buildings everywhere or proof that another Value increase would help. Specialization probes also lacked a responsive positive control.

Sources: [RH campaign](../../../research/mods/csc-ai-rh5-parity-campaign-20261024.md), [conditional Granary](../../../research/mods/csc-ai-granary-priority-20261031.md), [mechanism controls](../../../research/mods/csc-ai-mechanism-tests-20261025-results.md).

## AI-C027 — Direct Granary preference worked without controlling the target

Direct trait binding delivered preference 1 in 20/20 captured evaluations and two exact 2× Granary winners. The prescribed city still lacked Granary/Bakery after 21 intervals; Choir elsewhere completed Granary and began Bakery. Its Food 2 versus database base 1 is compatible with an additional CSC effect.

Scope: Genghis trait-wide experimental 110→131 control.

Limits: Instrumentation/recovery differences prevent isolated causality; Walls and military allocation changed. The wider gain was not free, and Choir lacked a full retained-chain material/effect census.

Sources: [Direct preference](../../../research/mods/csc-ai-granary-direct-priority-20261101.md), [earlier measured decision](../../../research/mods/csc-ai-granary-decision-20261031.md).

## AI-C028 — Customer geometry was a concrete repeated failure

All four selective-assisted sites had working Both and upstream producers at 150 but no operating customer path. Three lacked Stage 2 geography; Choir had an adjacent City Center without Granary. All four also lacked registered Stage 3 customer geometry.

Scope: Four precisely identified assisted investments in the selective RH screen.

Limits: More Both starts alone would not address the diagnosed customer-path gap. Partial extraction/producer benefits do not require the full operating milestone, so these cases are not automatically zero-income.

Sources: [Selective result](../../../research/mods/csc-ai-paired-selective-chain-screen-results-20261101.md), [customer reconstruction](../../../research/mods/csc-ai-customer-comparison-20261023.md).

## AI-C029 — Current future inputs are explicitly authored

An existing Tailors Quarter supplies Workshop private 80 for BASE plus 40 with SPEC. The RH role bridge does not itself check Quarter completion/pillage. An existing functioning Bakers Mill can target Granary private 40 before Granary exists; the real Mill→Granary exchange instead requires actual recipient Granary.

Scope: Pinned November 3 source and native analysis.

Limits: Fact flags use mapped-resource presence, ownership, reveal and district-free checks, not full improvement buildability or Builder availability. Do not describe historical getter 80 as a run of the whole current source tree or evidence of complete native network simulation.

Sources: [Current forecast investigation](../../../research/mods/csc-future-economy-forecast-20261103.md).

## AI-C030 — Current population returns are realized-state calculations

Stage 3 per-population seller/customer consumers attach to City Centers; Lua computes actual functioning same-owner adjacent relationships and writes bits. Stage 4/export consumers can instead adjust named building yields. Legacy producer-owned definitions can remain present but unattached.

Scope: November 3 source, after consumer changes.

Limits: Native unsupported collections, omitted property gates and missing plot context prevent assuming faithful arbitrary future-chain forecasting. Missing material is not equivalent to no ordinary Stage 3 sales.

Sources: [Forecast/source audit](../../../research/mods/csc-future-economy-forecast-20261103.md).

[Complete source map](source-map.md).
