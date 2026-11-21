# Producer and customer follow-through

The corresponding engine model is [prerequisite value and production](https://github.com/hennogous/civ6-ai/blob/main/references/engine/production-and-prerequisites.md)
and [prospective modifier evaluation](https://github.com/hennogous/civ6-ai/blob/main/references/engine/modifier-forecasts.md). These
separate missing-prerequisite foresight from an actual customer-building gate.

The AI can value a missing building and complete useful work in individual cases. The question is how that work passes caches, contracts and competing production, then keeps functioning supply.

```mermaid
flowchart LR
 D[Definition] --> V[Fresh value] --> R[Accepted request] --> Q[Queue selected] --> B[Completed building] --> W[Working retained path] --> E[Benefit]
```

## Lugdunum's Wind Mill path starts before construction

In both ordinary November 20 Continents games, Lugdunum held a completed
inland Bakers Quarter by turn 75. Cattle and Rice were adjacent and neither
had a working improvement at that census. The city was still missing a
producer. Machinery was first logged as researching on 95 and owned on 98.

On turn 94, Lugdunum's native Build City Building tree decoded a Wind
Mill at value 86 and submitted Machinery through Add Goal Tech.
Research contract 1546 appears in the tree and technology logs through 97.
The city submitted construction contract 1645 on 98, then started it on
104 and completed it on 107. Six turns elapsed between the request and
the production start. These were separate native requests.

The original turn-95 publication logged the previous native comparison
for player 4, city 262147, building 206. The locked-producer checkpoint
confirmed that 206 is the Wind Mill in this loadout. The integrated CSC
preference changed the comparison from 22,248 to 136,936 Q8. The native
preparation tree still carried its own value of 86 into the technology
contract. This establishes that an ordinary building nomination can
reach the native preparation path while its technology is missing.
The matched Problem 4 tests measure timeline changes against the
existing guidance.

The turn-50 saves are retained for preparing a locked-producer fixture.
In the turn-100 saves, Machinery is owned, the Wind Mill is still
missing and Rice is working. These provide an unlocked production
fixture close to the original selection. See the
[ordinary Continents run identities](../../../research/mods/csc-ai-axum-builder-availability-20261120.md#same-seed-control-through-turn-250).

### Producer investment in the shared economy

The candidate evaluates one Stage 2 producer against leaving the
Quarter without one. It uses the loaded alternative buildings,
material income, stock unlock and production timing, operating customer
exchanges, and investment costs. The two Mills compete for the same
investment. Unimproved suppliers enter at their forecast work date.
Later stages, Services and future customer construction use separate
decisions.

The publisher can offer a still-locked producer to the native building
selector with two viable adjacent Base suppliers. An unlocked producer
needs the actual city queue eligibility check and either a working
supplier or two viable suppliers. The new preference is capped at 64
native score points for qualification. A previously calibrated
working-chain offer can still supply the stronger preference. Each
Quarter offers one producer at a time. The native preparation tree
retains the prerequisite request, and native production still handles
the queue decision. The guidance follows a supplier's ordinary
development path once the producer enters production.

The turn-75 matched starting point came from repeating the turn-50
checkpoint with integrated 3.2 guidance. The replay differs from the
original continuous run in some cities. Lugdunum has the completed
Quarter, a working Rice Farm, a viable Cattle site and a locked Wind
Mill. Both comparison arms load this same new checkpoint, SHA-256
`51907dae006feb6eb5743bac8607b4174669ac1103ac62e9442fc08d8a35dd19`.
The UI readback at the checkpoint returns false for
`CanProduce(millHash, true)` and true for `CanProduce(millHash, false, true)`
while Machinery is unowned. The policy therefore checks prerequisite
timing from the live player and loaded building definition as well as
the UI queue query.

### Lugdunum matched producer replay

Both arms reloaded the same turn-75 save, matched all 55 opening
structural records and ran through turn 112. The control kept the prior
integrated CSC guidance. The investment arm changed the three Lua files
that price and publish producer nominations, with the same CE and game
build in both arms.

| Lugdunum Wind Mill | Prior guidance | Producer investment |
| --- | ---: | ---: |
| First staged nomination | 78 | 75 |
| First native comparison and Machinery request | 80 | 80 |
| Machinery selected for research | 91 | 91 |
| Machinery owned and first Mill contract submitted | 95 | 95 |
| Replacement Mill contract submitted | 102 | 102 |
| Mill selected | 108 | 105 |
| Supplier planner detected the Mill under construction | 109 | 106 |
| Working Mill observed | 110 | 106 |

The early preference was 10,745 Q8 on turn 75, about 42 score points.
No comparison of this candidate occurred in either arm on turns 75–79.
By turn 80 both arms offered the established working-chain preference.
The recorded candidate rose from 10,061 to 124,749 Q8 in both arms,
and the native tree asked for Machinery. The two turn-102 replacements
also had the same recorded candidate change, 58,398 to 173,086 Q8.
Both contracts entered the queue at the tree's value of 228. The
control then selected a Courser before the Mill. The investment run
selected the Mill while the Courser request was still active. Several
cities received new bids in the investment arm, and the two city
production paths had already diverged. The four-turn gain is a
whole-policy result. The early Lugdunum offer had no native comparison
during the three extra turns.

The supplier planner requested the Cattle Pasture while the Mill was
being built in both arms. Cattle was still unimproved at turn 112.
Both arms retained the Rice Farm and the adjacent Stage 2 customer.
The investment arm also had a working Barley improvement at the
endpoint. The checkpoint census verifies the buildings and plots.
Transaction payouts were not sampled in this replay.

The publisher's mean and maximum wall time over the 38 measured
turns were 0.929 s and 1.083 s with the previous guidance and 0.939 s
and 1.388 s with investment. These samples include the whole publisher,
with different game states after the arms diverged. They give the run
cost, rather than the isolated cost of the added producer quote.

### Axum's producer and supplier share a technology

Axum's turn-50 Tailors had a working Flax Farm and unimproved Bamboo.
Construction unlocks both the Textile Workshop and the Bamboo
Sawmill. The prior policy counted only sources with currently
executable improvement prerequisites when qualifying producer
preparation. This left the Bamboo out of the two-deposit test.

The new check runs for locked producer candidates in completed
Quarters. The loaded transaction must accept the exact improvement
as a producer input, the plot must pass native improvement placement,
and the producer must cover every outstanding tech and civic for that
improvement. This lets Bamboo contribute to preparation eligibility.
Material work remains on its ordinary unlock and assignment path.
The preparation quote still uses the existing supplier ledger, so
co-unlocked Bamboo contributes no speculative income.

The matched opening readback confirmed that
`IMPROVEMENT_RES2_SAWMILL` passed
`ImprovementBuilder.CanHaveImprovement` on Bamboo plot 1977 while
Construction was missing. The live publisher's supplier reader
marked it viable and unready. The new producer-only predicate marked
it eligible to count with the working Flax on 1828.

The turn-50 control matched all 41 opening structural records. The
Games and Recreation civic-boost tree already requested Construction
on turn 50. Axum's district tree also requested it on turn 78.
Research started on 85 and finished on 87. Default Specialization
started the Workshop on 90, and the end-of-player-turn read showed it
working on 92. At turn 132, the UI showed native Workshop Culture
inputs and improvement Production returns on both Flax and Bamboo.

The investment arm before the shared-unlock change reproduced that
timeline. It staged a 64-point Workshop preference on turns 88–90.
The ordinary nomination hook recorded zero comparisons for the three
offers. Default Specialization queued the Workshop on turn 90 in both
arms. The supplier adapter detected Bamboo on 91 and 92 while the
Workshop was in production in both. The turn-132 readback showed both
material exchanges operating in the two replays. This separates the
stock path that built the Workshop from the preparation path under
test in the dedicated shared-unlock arm.

Ghidra's XP2 reference (SHA `324c51e9`) shows that
`QueueNextBuild` itself calls `GetBestBuilding` and can log a
choice under Default Specialization. The tested Steam XP2 DLL
(SHA `4de40abf`) has the corresponding queue calls at RVAs
`3e7d57` and `3e7e59`. Both target the same selector at
`3e3fd0` as the ordinary nomination call at `3e0ec5`.
CE's nomination comparison is restricted to the latter call's
return address `3e0eca`. A building can therefore reach the queue
through Default Specialization with a zero nomination receipt.

The shared-unlock arm staged the Workshop from turn 50, starting at
1,918 Q8 (about 7.5 points). CE applied the preference at native
comparisons on turns 55, 65, 72 and 84, all before Construction.
The building tree picked Walls, a City Lights rural infrastructure
building twice, and Castle at those openings. At turn 55 the Workshop
rose from 623 to 3,990 Q8. Walls led at about 47 whole points.
The city's choice held through the wider replay. Construction still
started on 85, the stock queue selected the Workshop on 90, and the
Workshop worked on 92. The native effect readback confirmed both
material exchanges again at 132.

| Axum replay | Locked Workshop comparisons | Working Workshop | Publisher mean / max |
| --- | ---: | ---: | ---: |
| Prior guidance | 0 | 92 | 1.852 s / 3.890 s |
| Producer investment | 0 | 92 | 1.727 s / 3.085 s |
| Shared unlock | 4 | 92 | 1.780 s / 3.339 s |

The positive price came from sources already represented in the
ordinary ledger. Bamboo's co-unlock made the offer eligible.

## The integrated producer policy in a fresh Continents game

The Small Online game used map seed 1420359491, game seed 299464842,
Steam XP2 build 26595377 and the integrated shared-unlock package.
The shared controller verified the turn-200 save and a clean native
exit. The save SHA-256 is
`90e62b4d81b6da25265f0634ca59a581e0f16eb0c9b59db56280385cf01b6498`.

| Turn 200 | Bakers | Tailors |
| --- | ---: | ---: |
| Completed, functioning Quarters | 17 | 4 |
| Working Stage 2 producers | 16 | 4 |
| Working Stage 2 producers with at least one working Base improvement | 15 | 3 |
| Working Stage 2 producer with a functioning adjacent customer building | 10 | 0 |
| Positive Stage 2 Service property | 9 | 0 |

The Wind Mill tree in Montreal requested Machinery on turn 91, with
research starting on 93 and ownership on 95. Linköping's Wind Mill
tree also requested Machinery on 96 for a different player. That
player started it on 102, owned it on 105, and Linköping selected
the Mill through Default Specialization on 124.

Stockholm's Textile Workshop bid wrote at the native comparison on
turn 159. The candidate moved from 164,259 to 173,322 Q8, a 35.4-point
preference. The tree picked the Workshop and submitted contract 3264
at its native value of 641. The build began on 161 and completed on
163. The turn-175 census confirmed the Workshop and working Sheep
Pasture at the same Quarter. Axum supplies the separate matched test
of the Workshop's before-unlock comparison and paid supplier effects.

Opango's Water Mill was selected on 138 and completed on 141. The
publisher recognized the producer under construction and offered a
Base Flax Farm job on turns 139–141. The Flax was working by 175.
Lugdunum supplies the matched Wind Mill queue comparison. These cases
cover both Mills, the Workshop and the handoff to supplier planning.

The Lua publisher averaged 1.471 s per turn and peaked at 3.384 s,
with 200 complete packets and zero failed publication attempts.
The separate native managed-cell measurement averaged 11.2 ms and
peaked at 28.0 ms per turn. These times cover all integrated
guidance in this game.

## A retained Bakers Stage 2 chain in Boston

The matched tests kept Boston's exact Cattle Pasture next to a working Water
Mill and Granary. Engineering and Feudalism advanced through normal research.
At turns 63 and 66, the Granary produced 2 Food against a base of 1, the Water
Mill produced 1 Production and 1 Gold, and the Storekeeper marker and Growth
property were active. The earlier replay also showed the ordinary exchange
still producing after the supplier was lost, while Storekeeper stayed absent.
[AI-C061](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c061) [AI-C062](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c062)
[Boston evidence and turn-66 checkpoint](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#retained-stage-2-chain-verified-at-turns-63-and-66).

The first long continuation kept the same chain working for 141 full turns.
The Pasture first failed on turn 207, when a blizzard was logged nearby. The
turn-210 save showed Cattle without a Pasture, a pillaged Water Mill, an intact
Granary and zero Storekeeper Growth even though its marker still existed.
[AI-C063](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c063) [Retention and damage evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-chain-stayed-active-for-141-turns-before-damage).

In a separate continuation from turn 90, the same chain worked through the
turn-242 save. The original supplier, Mill, Granary and Storekeeper held
through 152 completed turns, with Granary and Mill Food verified separately.
The earlier Boston blizzard did not recur in this playthrough.
[AI-C064](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c064) [152-turn audit](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-same-chain-passed-152-turns-in-a-separate-continuation).

The late Boston chain's stock Mill repair waited behind Encampment and
restored its building yields. The Pasture remained missing. In a separate
early test with only the Mill pillaged, the city repaired it after finishing
University. The existing Pasture and Granary then supported the restored
exchange and Storekeeper. [AI-C069](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c069)
[Mill-only recovery evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#mill-only-damage-restored-the-full-service).

## The Wind Mill needed an ordinary nomination in Melbourne

Melbourne already had a working Rice supplier, an adjacent
Granary and Feudalism. An ordinary nomination preference changed
the offer from Amphitheater to Wind Mill. The offer kept the
native building cache value, and the queue refreshed and accepted
it at the next opening. Melbourne completed the Mill and operated
Storekeeper on turns 138–143. The matched control completed the
Amphitheater and had no working Storekeeper in Melbourne.
[AI-C090](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c090) [AI-C091](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c091) [AI-C092](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c092)
[Matched production and payout](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#melbourne-executed-the-wind-mill-offer-at-its-native-refreshed-value).

The main CSC publisher now bids for an unlocked, missing Mill when
the working Base, customer and Feudalism are in place. The CE review
build changed the ordinary nomination once and reproduced the offer,
completion and Storekeeper at the same checkpoint without an external
writer. The amount is an initial calibration. [AI-C093](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c093)
[Integrated replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#integrated-ce-nomination-reproduced-melbournes-wind-mill-and-service).

A City Center building that replaces Granary can serve as a
Bakers customer. CSC copies the
Granary's outgoing exchange attachments to those building definitions.
The native functioning-building requirement and receiving Food modifier
both resolve the target through the owning player's replacement table.
This has been checked in the executable. The matched payout tests used
the ordinary Granary. [AI-N102](https://github.com/hennogous/civ6-ai/blob/main/references/engine/findings.md#ai-n102)
[Replacement trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#granary-exchange-resolves-the-receiving-players-building-replacement).

## Ancyra still needed both buildings

From an earlier turn-120 checkpoint, both legal Bakers buildings lost
their ordinary comparisons to Walls. The Wind Mill had the closer
scores. In both read-only replays the AI finished Art Museum, then
used production for Walls and Line Infantry. Ancyra still needed
both buildings at 135, with the Rice Farm working. Pricing the first
investment requires its immediate benefits and an estimate of when
the second building could arrive. [AI-C125](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c125)

Ancyra's Granary was legal but lost twice to Castle in ordinary
nomination. Its available production slot went to a Cuirassier
contract. The missing Mill meant the Granary would still be one
step short of completing the exchange. The comparison margins
measure the competition in this city. [AI-C094](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c094)
[Granary decision trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#ancyras-legal-granary-lost-nomination-and-a-military-contract-took-production).

In Trebizond a working Water Mill could supply the Granary as
soon as it existed. The legal Granary lost its ordinary
nomination to Library, and neither earlier queue opening
included a Granary offer. The Wheat Farm remained a separate
Storekeeper requirement. [AI-C095](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c095)
[Trebizond control trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#trebizonds-working-mill-gave-a-closer-granary-comparison).

A matched test changed the nomination to Granary, and the game
validated that offer at its own cache value. Theater Square still
occupied production at the endpoint. [AI-C096](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c096)
[Trebizond nomination replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#a-matched-trebizond-nomination-produced-a-valid-granary-offer).

Trebizond bought that exact Granary offer through its ordinary
Gold budget. It used its open production slots for Library and
Encampment. The Water Mill was pillaged by the late endpoint.
A shorter replay captured the exchange before the damage.
The Granary gained one Food, and the Mill gained one Production
and one Gold. [AI-C097](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c097) [AI-C099](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c099)
[Purchase trace](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#trebizond-bought-the-granary-through-the-admitted-contract).

The native Granary forecast returned zero for its four CSC
exchange roots. Civ's Food weighting and income timing put the
incoming Food at about 18–19 score points in this city. The
initial reusable preference credits 18 points for that Food
when an adjacent working Mill can already supply it. Production,
Gold and future Service are separate terms. [AI-C100](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c100)
[Forecast calibration](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#native-granary-valuation-priced-food-and-returned-zero-for-the-exchange-roots).

The clean CE replay applied the 18-point preference to the
correct Granary. Library kept the nomination at this opening.
The qualification uses CE telemetry because an exit hook on
the selector changes the return address used by CE's caller
guard. [AI-C101](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c101)
[Clean integration replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-clean-replay-applied-the-calibrated-granary-food-bid).

Same-player native Production and Gold samples added about
17.5 points each in the observed income window. CSC now rounds
all three terms down to a 52-point preference for the immediate
exchange. The integrated replay delivered the full bid and
Library still won this opening. [AI-C102](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c102) [AI-C103](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c103)

In the ordinary Small Continents development game, Melbourne's
Wind Mill bid reached native nomination. The city queued a Knight
and later an Industrial Zone, then spent Gold on a later Mill offer
on turn 113. The native Storekeeper effect operated from turn 114.
Nomination, production choice and economic purchase are separate
observations. The run lacks a matched no-bid arm. [AI-C104](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c104)

In the same game, Launceston bought its Water Mill first. The
52-point bid then reached its Granary nomination. The city bought
the resulting offer and Storekeeper operated from turn 189.
This closes live follow-through for one customer. A matched
comparison would be needed to attribute the nomination to the bid.
[AI-C105](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c105)

A customer city can sit beside more than one working Mill. The
publisher now emits a single calibrated preference for each
legal Granary variant in that city. An offline two-Mill fixture
reproduced the duplicate and verifies the corrected packet.
The reviewed CE already kept the largest bid per native key.
CSC's change saves duplicate work and packet space. The
incremental benefits from a second Mill remain unpriced.
[AI-C109](https://github.com/hennogous/Henno-Mods/blob/main/project/docs/civ6-ai/findings.md#ai-c109)

[Full exchange calibration](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#native-player-weights-calibrate-the-full-ordinary-granary-exchange).

## A completed Harbor was waiting for its Lighthouse

The November 18 control game records a naturally occurring Stage 2
customer opening for Problem 5. At turn 150, player 3's Tailors at plot
545 had a working Textile Workshop, Flax Farm and Silver improvement.
The Harbor on plot 546 was complete and unpillaged, with the Lighthouse
absent. By turn 175 the Lighthouse and positive Dockmaster property were
present. The two censuses bound the observed change to turns 151–175.

The turn-150 game file is
`CSC_AI_HARMONISED_150_0d2b7e2ea4b6.Civ6Save`, SHA-256
`15e9be36612e60407b88a3b5eacb747fb9d1357ba2e5791389e186c467626ae2`.
The archived opening census is `control250/full-census-150.json`.
Match the live district and building facts when loading the checkpoint
for a comparison.

The current CE and CSC packages reproduced all opening structural
records. The Harbor belongs to Québec, city 131073, and the Workshop
belongs to the neighboring city 65536. Both native queue queries
allowed the Lighthouse. The prior 52-point preference was published
on turns 150–154. The native production fallback took the building
through to a working Lighthouse on 154 without an ordinary nomination
comparison. The control reached and verified turn 176. Its optional
UI per-building yield read was unavailable, so the proof of payments
will come from the underlying transaction modifiers.

The candidate customer bid now uses the loaded Stage 2 fixed exchange.
It values each leg in its actual receiving city from the estimated
completion of the missing customer. The publisher uses the resolved
building variant in a completed district and checks native queue
eligibility. It sums exchanges with distinct working producers into
one preference per city/building and caps that preference at 64 native
points. The normal building valuation retains its intrinsic yields,
upkeep and production or purchase cost. Future producers, materials
and Service effects make no contribution to this quote.

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
