# CSC AI roadmap

The [CSC objectives](../integrations/csc-ai-objectives.md) cover all eight
Quarters, their suppliers, customers and Services. CSC values the chain.
Civ compares eligible actions, allocates production and workers, and manages
research, treasury and commitments. The numbered problems below retain the
order of the original decision list. Their identifiers stay fixed as we add
evidence.

## Current milestone and active problem

**Boston fixture achieved — one working, retained Bakers Stage 2 chain.**
The reusable milestone is to repeat the sequence from normal starts across
multiple AI cities and close the dependencies as they arise.
Choose and complete a Bakers Quarter with viable Base supply and an adjacent
Granary host (**1.1–1.4, 1.6**). Get the appropriate Mill and a functioning
Granary in place (**4.1–4.2, 5.1**). Improve the Base tile and match the job
to a reachable Builder (**3.1–3.3**). Verify the ordinary exchange and keep
the supplier intact (**2.2**). Then verify the Feudalism goal and Storekeeper
when the chain is ready (**6.1**). Existing buildings, Builders and unlocks
can satisfy dependencies. Tile purchase (**1.5**) and a new customer district
(**2.1**) are optional for this first fixture. Repair (**13**) enters if a
failure occurs and is a later explicit resilience check. Run the same
decision sequence for Tailors once the Bakers chain works.

**Verified for this fixture — 1.6, district selection through completion.**
The game started with Craftsmanship locked. London had four estimated turns
left on the civic at turn 8, but its Holy Site plan occupied the district
selection slot. Boston's first observed qualifying choice came on turn 22,
after Craftsmanship had unlocked naturally. One diagnostic bid switched the
district selector from Campus to Bakers, and Boston completed Bakers at plot
721 with its Base deposit still present. The control later founded Bakers
on a different plot. [Exact match and timeline](../research/mods/csc-ai-bakers-natural-research-20261106.md).

**Verified for this fixture — 2.2, 3.1–3.3, 4.1–4.2 and 5.1.**
On the same turn-31 save, the control covered Boston's only mapped Base
deposit with a Campus. One measured deduction redirected Campus to plot 720.
Boston's existing Builder job put a Pasture on the retained Cattle. Engineering,
Granary and Water Mill followed through native research and production.
The Quarter, both buildings and the working supply were present at turn 45.
[Protection and follow-through](../research/mods/csc-ai-bakers-natural-research-20261106.md#a-matched-deduction-protected-the-only-base).

**Verified for this fixture — 13.3 and 6.1.**
A Feudalism boost Farm job removed the working Cattle Pasture and harvested
the deposit. Protecting that boost choice alone exposed a separate ordinary
Farm job. The final replay guarded both decisions before reservation.
Boston kept the same working Pasture, Water Mill and Granary through
natural Feudalism. The actual exchange, Storekeeper marker and Growth
property were present at turns 63 and 66. The saved turn-66 state closes the
Boston milestone. The tested policy is scoped to one city and supplier.
[Final retained chain and evidence](../research/mods/csc-ai-bakers-natural-research-20261106.md#retained-stage-2-chain-verified-at-turns-63-and-66).

**Verified duration — 2.2 and 6.1.** A separate continuation kept Boston's
original chain working for 152 consecutive turns from turn 90 to 242. The
original continuation worked for 141 turns before the Pasture failed near a
Crippling Blizzard on turn 207. That break reproduced from the turn-186 save.
Repair after disaster damage remains open under **13.1**.
[Long-run observations](../research/mods/csc-ai-bakers-natural-research-20261106.md#the-same-chain-passed-152-turns-in-a-separate-continuation).

**Verified for the Boston replay — 2.2, automatic district material protection.**
Main CSC now has a gameplay publisher for the CE district-score capability.
It reads owned, visible Bakers suppliers, distinguishes a usable deposit
from a working improvement, and prices legal district pairs for the city
that could cover each tile. A fixture verifies publication for a supplier
owned by a different city and refresh after pillage or removal. The corrected
CE compatibility build loaded the previously failing DX11 save, and the
score API reproduced the early and late writes in a separate replay. In the
matched Boston replay the control covered Cattle 796 with Campus. With the
automatic main CSC policy, Campus went on 720 and Boston worked the original
Cattle Pasture by turn 37. The penalty is finite and needs wider calibration.
[Automatic publisher evidence](../research/mods/csc-ai-bakers-natural-research-20261106.md#automatic-district-protection-replay).

**Active placement integration — 1.1–1.4 and 1.6.** The main CSC publisher
now adds one positive owned-site bid per eligible city alongside its existing
material deductions. The scanner uses native build targets and legality,
requires a viable Base and an adjacent friendly City Center, and forecasts
the site using loaded CSC adjacency rules and the local Mill branch.
The two initial Q8 bands passed offline checks. The first normal-start run
exposed the Gameplay versus UI build-queue API difference. The publisher
now reads readiness via the UI bridge and rechecks plot state in Gameplay.
The repeat verified positive native score changes and a higher proposal
on Ancyra's same site in a clean untuned comparison. Both arms queued that
Quarter on turn 44. Continue through completion and look for improved site
or investment choices. Future customer sites and affordable land acquisition
are still open. [Matched development run](../research/mods/csc-ai-bakers-natural-research-20261106.md#owned-site-placement-publishing).

**Active normal-start problem — 5.1, following the 4.2 Mill replay.** The
turn-100 development run had four complete and two unfinished AI
Bakers Quarters, and zero observed Storekeepers. All five original
AI majors unlocked Feudalism. In Alexandria Troas only the
Pasture was missing. The bounded supplier bid reached the native
scorer but the tile stayed unimproved. The read-only replay found
an occupied job slot on nine checks. On the three open checks
another Pasture site beat the Bakers supplier by 5,888 Q8. The
matched increase redirected all three choices and the city found
a Builder. The matched turn-112 continuation kept the extra bid
through reassignment. Both arms built a Pasture at 118. Only the
treatment improved the Bakers supplier and activated Storekeeper
on 119–121. The integrated CSC publisher and widened CE cap
reproduced those three Service turns without an external score
writer. A fresh calibrated game reached turn 125 with six active
Alexandria Storekeeper turns, nine completed Quarters and no
other active major-AI chain. Melbourne still has working Rice,
Granary and Feudalism with only its Wind Mill missing. The Mill
passed native eligibility and lost ordinary nomination to
Amphitheater by 112,232 Q8. The matched nomination preference
produced a valid Wind Mill offer at its lower native cache value.
The follow-up refreshed that offer, entered production on 135
and finished the Mill on 137 without another adjustment.
Storekeeper operated on 138–143. The matched control finished
Amphitheater with Melbourne's Mill still absent. The main CSC
policy and CE review build reproduced the Wind Mill nomination
and construction from the same turn-125 save, with active
Storekeeper on 138. **4.2** still needs calibration across ordinary
starts and the Water Mill route. **5.1** is the next missing link
to join to it.
Ancyra's legal Granary lost ordinary nominations to Castle.
Cuirassier took the observed production opening. Ancyra still
needs both buildings. In Trebizond, where a Water Mill could
immediately supply the Granary, Library won ordinary nomination.
The matched **5.1** diagnostic produced a valid Granary offer,
which Trebizond bought at its ordinary value. The exchange worked
before the later Mill damage. The native forecast returned zero
for the outgoing exchange roots. The initial reusable bid credits
the incoming Food at 18 points. The clean replay confirmed
that CE applied the exact preference and Library kept the
nomination. Production and Gold calibration brings the full
ordinary exchange bid to 52 points. The matched replay delivered
it and Library kept the nomination. The next check is a frozen
development setup from turn one.
Use the existing Small Continents development seed, keep the
three validation seeds in reserve, and sample missing links
at turns 100, 150, 200 and 240. Use those gaps to prioritise
the next tuning problem. At the default Online horizon, each
qualifying chain needs to operate by roughly turn 150 to leave
100 turns before the score limit. Lapses require an earlier start.
Charleston supplied another **3.2** follow-through case. It received
an exact Maize Farm bid and operated Storekeeper on 176–177.
[Turn-100 census](../research/mods/csc-ai-bakers-natural-research-20261106.md#normal-start-follow-through-to-turn-100).
[Fresh calibrated game](../research/mods/csc-ai-bakers-natural-research-20261106.md#the-fresh-calibrated-game-activated-one-storekeeper).
[Melbourne building trace](../research/mods/csc-ai-bakers-natural-research-20261106.md#melbournes-available-wind-mill-lost-the-ordinary-building-nomination).
[Melbourne production and payout](../research/mods/csc-ai-bakers-natural-research-20261106.md#melbourne-executed-the-wind-mill-offer-at-its-native-refreshed-value).
[Integrated Mill replay](../research/mods/csc-ai-bakers-natural-research-20261106.md#integrated-ce-nomination-reproduced-melbournes-wind-mill-and-service).

**Supplier recovery evidence — 3.1–3.2 and 13.1–13.2.**
The CE score-stage policy now reads live CSC material rules and protects
critical supplier sites in the matched Boston replay. With the same district
policy in both arms, the control lost its Cattle. The treatment kept its
working Pasture and reached Storekeeper at turns 63 and 66. Verify protection
from already assigned jobs and direct harvests, plus safe alternatives in
ordinary games under **13.3**. Boston's stock recovery baseline reached turn
234 without rebuilding the Pasture or repairing the Water Mill. A Wonder
reservation competed for the damaged Cattle site while a Spaceport occupied
city production. Check whether preserving site access enables the Pasture
job, and measure the Mill repair at an actual production decision. The
matched Wonder policy redirected that claim to a different Wonder and tile.
Boston still rebuilt neither link by turn 222. The stock follow-up found that
the damaged Mill could win the building comparison and still yield the
production slot to an admitted Theater Square contract. The Mill remained
pillaged at turn 252. Boston also submitted a repair contract on turn 249
and queued an Encampment on turn 250. The repeat confirmed the Mill passed
validation and refreshed to 639,408 Q8. Encampment executed at 3,694,136 Q8.
The cold continuation queued the same Mill contract on turn 252 after the
Encampment finished. Repair completed on turn 253 and building yields
returned. A separate earlier state with only the Mill pillaged also
recovered through stock fallback production. Working supply, exchange and
Storekeeper were verified together after repair. Keep building and Quarter
recovery in fresh-seed qualification. For the missing Pasture, trace
reservation, admission and assignment. Verify the legal Builder operation
and actual Storekeeper output when both links work again.
The controlled Pasture loss at turn 66 left the tile legal and valued.
An occupied job held the ordinary slot. When the slot reopened, an
Irrigation boost claimed and harvested the Cattle. The matched turn-72
comparison logged the intended Farm score suppression, but both arms
still lost the deposit. Protection from turn 69 reached the native
selector before the boost reservation. The Cattle survived through
turn 81, while Camp beat the legal Pasture at two ordinary admissions.
With protection in both arms, the matched 8,192 Q8 Pasture bid changed
the ordinary selection, led to legal construction, and restored
Storekeeper and the Mill's supplier output at turns 75 and 78.
The control had no Pasture at turn 87. The main CSC publisher and
the reusable CE preference reproduced the recovery without Frida.
Native growth was active on Boston's exact City Center recipient.
Next test pillaged improvements and worker shortages. A separate
one-shot guard stopped the committed harvest and the AI later
rebuilt the Pasture on the released site. The reusable CE gate and
main CSC publisher reproduced this outcome. Extend coverage to
other destructive operations and working improvements.
The archived naturally damaged branch kept Cattle through turn 264
with no Mill or Pasture recovery. Production went to existing
Spaceport, building and district commitments, then Orbital Lasers.
The Mill passed native requirements in the turn-258 replay, and
Military Academy won the building ranking. A repeat at turn 261
measured the effective Mill and Academy operands. The queue ranked
a project above both, rejected it, then trained Modern Armor through
generic offense without reconsidering its building. The bounded Mill
preference won the ordinary building ranking and still hit the same
unadvanceable project. A matched diagnostic screened candidates using
native project eligibility. Boston queued a valid Terrestrial Laser
and the chain stayed down. In a separate Mill-only replay starting
at 114, stock AI finished its Theater Square before repairing the
Mill. Storekeeper and exchange were working again at 126. Keep
recovery under **13.1–13.2** and **14.1** in fresh-game observation.
Prioritise normal-start follow-through under **1.6** and **3–6**
before adding a Mill bonus for a loss that has yet to recur there.
[Project eligibility replay](../research/mods/csc-ai-bakers-natural-research-20261106.md#project-eligibility-preserved-a-valid-terrestrial-laser).
[Mill-only contract and payouts](../research/mods/csc-ai-bakers-natural-research-20261106.md#boston-repaired-the-mill-after-theater-square).
The CE performance review branch indexes policy lookups by city and
district-site pair and separates routine policy limits from detailed trace
retention. Its native self-tests passed. Qualify the optional summary mode
and measure its cost in a mature live game before enabling it in CSC.

The separate CSC and CE development packages loaded from normal setup
with the main CSC publisher active on all eight observed turns. The
native Storekeeper logger covered every interior turn of one continuous
autoplay window. Use a strict expected turn range for qualification.
[Package and clock smoke evidence](../research/mods/csc-ai-bakers-natural-research-20261106.md#separate-local-csc-and-ce-packages).
[Current CE startup evidence](../research/mods/csc-ai-xp2-november-hotfix-20261106.md#corrected-shared-ce-loads-and-accepts-district-scores).
[Builder candidate replay](../research/mods/csc-ai-bakers-natural-research-20261106.md#builder-candidate-filtering-before-native-ranking).
[Automatic CE Builder replay](../research/mods/csc-ai-bakers-natural-research-20261106.md#automatic-builder-protection-in-the-matched-ce-replay).
[Natural recovery baseline](../research/mods/csc-ai-bakers-natural-research-20261106.md#natural-recovery-after-the-boston-blizzard).
[Matched Wonder protection](../research/mods/csc-ai-bakers-natural-research-20261106.md#matched-wonder-protection-changed-the-reservation).
[Mill repair and city contract ordering](../research/mods/csc-ai-bakers-natural-research-20261106.md#the-mill-won-the-building-comparison-and-missed-the-queue).
[Mill-only recovery and payouts](../research/mods/csc-ai-bakers-natural-research-20261106.md#mill-only-damage-restored-the-full-service).
[Supplier decision and harvest](../research/mods/csc-ai-bakers-natural-research-20261106.md#isolating-the-missing-pasture).
[Matched supplier protection failure](../research/mods/csc-ai-bakers-natural-research-20261106.md#the-turn-72-protection-arms-both-lost-the-cattle).
[Earlier matched protection and Camp competition](../research/mods/csc-ai-bakers-natural-research-20261106.md#earlier-protection-redirected-the-boost-and-preserved-the-deposit).
[Matched Pasture recovery](../research/mods/csc-ai-bakers-natural-research-20261106.md#a-bounded-pasture-bid-restored-storekeeper-in-the-matched-replay).
[Committed-harvest recovery](../research/mods/csc-ai-bakers-natural-research-20261106.md#a-committed-harvest-failed-safely-and-boston-used-the-plot-again).
[Integrated supplier publisher](../research/mods/csc-ai-bakers-natural-research-20261106.md#the-main-csc-supplier-publisher-uses-the-existing-ce-score-hook).
[Simultaneous damage and competing production](../research/mods/csc-ai-bakers-natural-research-20261106.md#preserving-the-natural-supplier-did-not-resolve-simultaneous-damage).
[The eligible Mill lost the building comparison](../research/mods/csc-ai-bakers-natural-research-20261106.md#military-academy-beat-the-eligible-mill-in-building-selection).

For the reusable Stage 2 goal, use these preselected fresh Standard-size,
Online games with normal starts. All three use CSC and its CE dependency
with stock Civ VI AI. Run the integrated tuning and record every result.
Match the untuned arm's gameplay content, starting settings and seeds.
Review RHAI5 compatibility separately after stock AI qualification.

| Map | Map seed | Game seed | Configuration |
| --- | ---: | ---: | --- |
| Continents | 17260413 | 27410653 | CSC, matched untuned arm |
| Pangaea | 18431267 | 28681391 | CSC |
| Fractal | 19672039 | 29812257 | CSC |

Each qualification game needs three distinct AI Bakers chains with 100
cumulative active Service turns each. Count operation per chain through
lapses and demonstrate legal recovery from supplier disruption and from
producer or customer damage. Record material scarcity and lost opportunities
alongside successes. Mill repair is in scope where it prevents recovery.

For each update, name the active problem and report the furthest stage actually
observed, the blocker if any, and the next check. Keep later problems queued
until the active check closes or an explicit dependency needs attention.

## Numbered problems to solve

### 1. Quarter placement

- **1.1 Materials.** Favor legal sites beside at least one viable mapped Base
  source, ideally with viable Specialty as well. Distinguish deposits from
  working supply and include enabled compatibility mappings.
- **1.2 Neighbors.** Value mapped customer districts and City Lights goods
  providers. Credit a future neighbor only where a specific legal adjacent
  footprint can serve it.
- **1.3 Rivers.** Value the river effects the Quarter can actually realise,
  including the local Mill geometry where applicable.
- **1.4 Adjacency.** Combine the actual sources and favor sites around +4 or
  higher. Calibrate against competing native investments and weaker viable sites.
- **1.5 Tile purchase.** Price an affordable unowned Quarter footprint or
  a supplier needed by a viable plan. These can require different native
  decisions. First trace an exact district purchase request through its
  debit and acquiring city, and a separate supplier acquisition through
  its improvement. Preserve native legality and treasury checks.
  [Native purchase routes](topics/native/district-choice.md#buying-a-future-site).
- **1.6 Construction readiness and follow-through.** Check unlocks, legal
  siting, capacity and the preparation window before committing. Trace the
  proposal through production, foundation and completion. Distinguish a new
  score from a retained request.

### 2. Other district placement

- **2.1 Customer placement.** Favor a site adjacent to a provider Quarter
  or a credible specific future Quarter footprint. Preserve the district's
  standalone value when comparing placements.
- **2.2 Material protection.** Price covering mapped Base or Specialty
  deposits, including unimproved ones. Protect the last viable deposit of
  either class per Quarter and account for lost Services when the last
  working supplier is threatened. Apply this to any district consuming the
  tile. Verify an absolute exclusion separately from a finite bid penalty.

### 3. Material work and Builder capacity

- **3.1 Exact job and timing.** Prioritize Base work when the Stage 2 buyer
  functions and Specialty work when the Stage 4 buyer functions. Put the
  intended plot and improvement into native job allocation and observe the work.
- **3.2 Assignment and supply.** Use a reachable Builder with charges,
  including across cities. Value another Builder when useful work exceeds
  available capacity.
- **3.3 Improvement unlocks.** Value missing technologies early enough for
  a viable supplier to be ready when needed.

### 4. Stage 2 producer

- **4.1 Unlock.** Favor the needed tech or civic when two or more viable
  Base sources are adjacent.
- **4.2 Build.** Favor the legal producer under that same condition. One
  viable Base can still justify a producer. Confirm the bid reaches the
  native queue and the building completes.

### 5. Stage 2 customer

- **5.1 Build.** Favor the mapped building in an adjacent customer district,
  including a valid unique replacement. Verify the customer contributes
  the actual exchange when the producer operates.

### 6. Stage 2 Service

- **6.1 Unlock.** Favor the unlock when the required working materials,
  producer and customer are ready. Combine the value of distinct ready
  chains and observe the Service in operation.
- **6.2 Strategy.** Later, adjust the priority for empire needs and victory
  direction.

### 7. Stage 3 producer

- **7.1 Unlock.** Favor the tech or civic from population 7 when the
  investment is worthwhile.
- **7.2 Build.** Favor construction from population 10, subject to expected
  benefit and competing uses of production.

### 8. Stage 3 customer

- **8.1 Build.** Favor the mapped building in an adjacent customer district
  and verify the corresponding exchange.

### 9. Stage 3 Service

- **9.1 Unlock.** Favor the unlock when the required chain is ready, combining
  distinct ready chains.
- **9.2 Strategy.** Later, value its effects according to empire needs and
  victory direction.

### 10. Stage 4 producer

- **10.1 Unlock.** Favor the tech or civic from population 7 with viable
  adjacent Base and Specialty sources.
- **10.2 Build.** Favor construction from population 10 with both sources
  viable. Include the cost and timing of developing Specialty supply.

### 11. Stage 4 customer or Wonder

- **11.1 Customer building.** Favor the mapped building in an adjacent
  customer district.
- **11.2 Wonder.** Favor a legal adjacent Wonder footprint where the Quarter
  has the required materials. Verify the decision that chooses its tile.

### 12. Stage 4 Service

- **12.1 Unlock.** Favor the unlock when the required chain is ready, combining
  distinct ready chains.
- **12.2 Strategy.** Later, value its effects according to empire needs and
  victory direction.

### 13. Recovery and retention

- **13.1 Repair.** Restore pillaged material improvements, Quarters and
  customer assets when the chain merits it. Verify actual repair and resumed
  benefits. Check whether the stock Mill-only recovery repeats in ordinary
  games and when it fails with another link down.
- **13.2 Replan.** Reassess after capture, lost supply, or destructive harvest
  and other work. Distinguish a repairable interruption from permanent loss.
- **13.3 Preserve supply in Builder decisions.** Account for removing a
  mapped improvement or harvesting its deposit before the job is reserved.
  Apply the protection to boost work as well as ordinary improvement jobs.
  Verify the alternative or deferral and the working supplier afterward.

### 14. Competing uses and shared plans

- **14.1 Sequence investment.** Compare finishing or repairing a chain,
  opening a new one, and deferring. Include treasury, upkeep, production,
  unlock time, Builder travel and charges.
- **14.2 Resolve conflicts.** Two plans can compete for the same footprint.
  One supplier can serve multiple Quarters. Count each real lost or enabled
  benefit once.

### 15. Quarter investment and trade

Later milestone, after Bakers Stage 2 qualification.

- **15.1 Price lost import benefits before building.** When a local Quarter
  would remove eligibility for same-family trade bonuses, compare its
  credible local return with the benefits the city could actually import
  through existing routes and credible new routes to supplied destinations.
  Discourage weak local Quarters whose construction would sacrifice a
  better trade option. Account for route capacity, reach and how long the
  alternative is likely to operate.
- **15.2 Value supplied Quarter destinations.** In native route selection,
  value the actual CSC yields and Amenities each eligible destination can
  deliver to the origin, alongside the normal reasons to choose a route.
  Check the destination's producer and materials and the origin's
  eligibility. Verify route choice, completion of the trade setup and the
  benefits actually received.

## Tooling, delivery and evidence

Use the shared controller on stock GameCore for matched live tests. The
guarded Frida writer already reached native selection and preparation on
Steam build 26407122. It supports the current 1.6 experiment. Construction,
building, job and unlock bids each need evidence at their own native decision
boundary. The offline Stage 2 replay checks policy and mappings separately.
[District adapter](topics/native/native-placement-extension.md) ·
[Stage 2 replay](topics/csc/site-planner.md#stage-2-decision-replay).

Dev-CE 0.8.1 is an experimental single-player option if we need a specific
extra Lua getter or debugger. Its release qualifies the bridge and terrain
views on the patched build. The debugger and Lua hooks still need their own
patched-build checks. Its generated Lua bindings are separate from CSC's
guarded district-score API, and Dev-CE uses the GameCore replacement slot.
Use the verified stock route for 1.6. Review Dev-CE in isolation if a later
problem needs a capability it actually exposes.
[Dev-CE 0.8.1 release](https://github.com/cru121/civ6-dev-ce/releases/tag/v0.8.1-experimental) ·
[Tagged generated bindings](https://github.com/cru121/civ6-dev-ce/blob/v0.8.1-experimental/DevNativeTable.cpp).

Packaged CSC delivery still needs the guarded score API on a CE base
qualified against the patched host. Keep that carrier work separate from
testing the decisions themselves. Reuse the shared runtime and observe the
CE contribution review requirements before upstream submission.
[CE hotfix qualification](../research/mods/csc-ai-xp2-november-hotfix-20261106.md).

### Reverse engineering each decision

1. Start with the shipped game data and the relevant handbook finding. Use
   REA and Ghidra to trace the native consumer, prerequisites, return or score
   units, and the transition into the next decision. Identify the exact
   GameCore build and check the target bytes before reusing offsets.
2. Use the shared controller, read-only game queries and guarded Frida
   traces to observe the path on a pinned save. When testing a bid, change
   one scoped input against a matched control. Record the winner, request,
   queue, execution and retained benefit as distinct outcomes.
3. Save the build identity, function locations, input facts and runtime
   receipts. Put the mechanism, evidence limits and unresolved questions
   in the handbook. Update the active roadmap problem with the highest
   stage actually verified.

The annotated Ghidra project uses the earlier XP2 image. Its code section
matches the patched image, as verified in the hotfix comparison. The
installed patched binary remains the identity for live tests.
[Handbook evidence workflow](maintenance.md) ·
[GameCore comparison](../research/mods/csc-ai-xp2-november-hotfix-20261106.md).

For each new adapter verify eligibility, timing, score scale and the actual
consumer. Start with bounded preferences. Retain the native standalone
value of shared vanilla assets and add the signed CSC contribution.
Qualify a full valuation for CSC-only assets when useful. Measure forecast
overlap where it changes choices. Cache local relationships and refresh
affected scopes with periodic reconciliation. Track runtime overhead and
worst turns in a developed empire. Compare working supply, Service uptime,
costs and displaced investments in matched standalone CSC and RH tests.
[Production and prerequisites](topics/native/production-and-prerequisites.md) ·
[Material work](topics/csc/materials-and-builders.md) ·
[Research guidance](topics/csc/research-and-strategies.md).
