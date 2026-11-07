# CSC AI roadmap

The [CSC objectives](../integrations/csc-ai-objectives.md) cover all eight
Quarters, their suppliers, customers and Services. CSC values the chain.
Civ compares eligible actions, allocates production and workers, and manages
research, treasury and commitments. The numbered problems below retain the
order of the original decision list. Their identifiers stay fixed as we add
evidence.

## Current milestone and active problem

**Intermediate milestone achieved — one working, retained Bakers Stage 2 chain.**
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

**Active problem for reusable tuning — 13.3, destructive Builder work.**
The CE score-stage policy now reads live CSC material rules and protects
critical supplier sites in the matched Boston replay. With the same district
policy in both arms, the control lost its Cattle. The treatment kept its
working Pasture and reached Storekeeper at turns 63 and 66. Verify protection
from already assigned jobs and direct harvests, plus safe alternatives in
ordinary games. For **13.1**, observe how Civ handles the archived natural
damage to Boston's Pasture and Water Mill before adding recovery incentives.
Before a mature-game run, separate native policy limits
from trace retention, preserve per-publication evidence, and index native
lookups by city and district-site pair. Measure the resulting cost in play.
[Current CE startup evidence](../research/mods/csc-ai-xp2-november-hotfix-20261106.md#corrected-shared-ce-loads-and-accepts-district-scores).
[Builder candidate replay](../research/mods/csc-ai-bakers-natural-research-20261106.md#builder-candidate-filtering-before-native-ranking).
[Automatic CE Builder replay](../research/mods/csc-ai-bakers-natural-research-20261106.md#automatic-builder-protection-in-the-matched-ce-replay).

For the reusable Stage 2 goal, preselect these fresh Standard-size, Online
games with normal starts. Run the integrated tuning and record every result.
Use the same starting settings and seeds for the untuned comparison.

| Map | Map seed | Game seed | Configuration |
| --- | ---: | ---: | --- |
| Continents | 17260413 | 27410653 | CSC, matched untuned arm |
| Pangaea | 18431267 | 28681391 | CSC |
| Fractal | 19672039 | 29812257 | CSC with RHAI5 |

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
- **1.5 Tile purchase.** Route an affordable unowned site through native
  planning and treasury checks. Verify the actual purchase.
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
  benefits. Observe the known Mill repair case in ordinary tests. A dedicated
  investigation remains deferred.
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
