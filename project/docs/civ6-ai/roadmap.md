# CSC AI roadmap

The [CSC objectives](../integrations/csc-ai-objectives.md) cover all eight
Quarters, their suppliers, customers and Services. CSC values the chain.
Civ compares eligible actions, allocates production and workers, and manages
research, treasury and commitments. The numbered problems below retain the
order of the original decision list. Their identifiers stay fixed as we add
evidence.

## Current milestone and active problem

**Intermediate milestone — one working, retained Bakers Stage 2 chain.**
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

**Active problem — 1.6, time the first Quarter bid so it reaches foundation.**
The patched stock replay proved score delivery, selection and reservation.
Delhi's prerequisite contract expired before it could submit a Bakers
production order. For the next matched comparison, start with Craftsmanship
locked and let the AI progress through civics naturally. Check from around
turn 5. Use a checkpoint where Code of Laws is complete, Craftsmanship is
still locked but actively progressing, and its estimated completion leaves
room in the observed eight-turn preparation window. Treat the estimate as
an admission check and record the actual unlock separately.

Use that same checkpoint for the unmodified control and the one-bid arm.
Recheck site ownership, siting requirements and city capacity. Record the
current civic and its progress, native winner, prerequisite request, actual
production contract, queue entry, foundation and completion separately.
If the research state never qualifies, record that outcome before choosing
another candidate. A later bid tests timing with native research intact.
[Live bid and preparation expiry](../research/mods/csc-ai-hotfix-live-bid-20261106.md).

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
