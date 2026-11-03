# Astra review: native economic goals and CSC sequencing — 30 October 2026

> Historical review: the roadmap discussed here was removed on 3 November 2026. The [fresh roadmap](../../civ6-ai/roadmap.md) governs current planning.


Henno requested a review of the two new resources and an actual roadmap update.
The [roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md) now has one governing sequence,
explicit gates and historical records rather than several competing “current”
instructions. This was an offline documentation review. No native session,
source AI change, installed change, automation, goal or commit was made.

## What changes the decision

The new evidence is not merely that the engine contains useful node names.
The author reports a mod-defined tree reaching a Lua condition, and an authored
operation reaching native recruitment, contracts and some movement. That makes
a normal data/Lua route from a CSC-selected goal to native execution plausible
enough to assess early. It could address “the planner knows what should happen,
but generic AI preferences never turn it into work.”

The qualification is substantial. The condition's result channel is Extra;
the target processor's demonstrated output is PlotX/PlotY. Neither establishes
that arbitrary city, improvement or building identifiers can be written into
the tree's working data. Both callbacks reportedly received empty tables. A
global goal shared by every AI demonstrated activation, not correct per-player
economic execution. The test tree also displaced ordinary tech upgrades, and
the operation continued to fail most movement attempts. These remain the
author's reports, not independently replicated CSC results. Sources:
[behavior trees](https://cru121.github.io/civ6-gamecore-reference/ai-behavior-trees.html)
and [contracts and operations](https://cru121.github.io/civ6-gamecore-reference/ai-contracts-and-operations.html).

Consequently the recommendation is an early **feasibility gate**, not commitment
to a new executor. Inspect only additive tree activation and an explicitly
player-owned scripted-operation route. Establish owner, payload, consumer and
release. If both fail that gate, record the missing interface and keep improving
the planner through the known backend/incentives. CE/runtime hooks must not
silently become a shipping dependency to rescue an attractive vocabulary.

## Why the candidate capture still comes first natively

The latest producer observation already shows fresh private80 consumption,
positive preference's2× multiplier and an actual Workshop choice. Its marginal
forecast effect and benefit remain unanswered, but another producer arm is less
urgent than obtaining the first trustworthy set of native site alternatives.
The failed shadow capture returned none. Its Members repair and11 offline
checks are useful preparation, not a successful result.

Finish exact-context preflight using the binding data already on disk, then one
zero-turn capture in the already declared city. That provides geometry evidence
for a meaningful opportunity without mixing reader validation and treatment.
The native-goal feasibility review can proceed offline independently; a failed
candidate binding should not trigger another architecture rewrite or a search
across more saves until something produces a positive output.

The first economic-job prototype should preferably develop one mapped material
for an existing chain with an available Builder. This isolates a major missing
capability and avoids combining recruitment, purchases and a new foundation.
If only a city-bound producer request has defensible bindings, use that smaller
proven interface and leave material execution open. The choice follows evidence
about data flow, not which node label sounds closest to the desired task.

## RH and acceptance

Read-only local RH5.097 source already supplies a relevant precedent:
`core/Strategies/Advanced_Thinking/Features/SettlerSnipe/RH_SettlerSnipe_Operation.sql`
registers TARGET_SCRIPT_SUPPLIED and RH_SettlerSnipe_FindTarget; the matching Lua
callback uses a global latest-target record or scans AI players. It does not
read the requesting player from its callback table. This does not prove a bug,
nor solve our ownership requirement. A negative control involving another AI
with a distinct opportunity is necessary before trusting a CSC provider.

Do not replace base/RH event slots, disable upgrades, duplicate global Builder
policy, or assume operation completion releases every request/reservation.
Prove identity before side effects, one job's physical completion and release,
then cancellation/expiry and duplicate suppression before integration. Reuse
the existing NativeSession and locally traced contract paths. Full-game adapter
validation belongs to the first bounded relevant game, not a new framework.

Success means a useful chain action with attributable investment and reliable
ownership/lifecycle. It first earns a small adapter. Basic/RH comparisons must
then establish sustained chain benefit and acceptable trade-offs before broad
deployment. Strategy-aware Services remain a later capability.

## Reviewed evidence

- [CSC objective](../../integrations/csc-ai-objectives.md) and prior roadmap.
- [Local community route review](csc-ai-community-native-job-routes-20261030.md),
  both full supplied page snapshots and their 30 October receipt.
- [Tooling/context cross-check](csc-native-tooling-community-crosscheck-20261030.md)
  and [failed shadow capture with offline repair](csc-ai-native-shadow-sites-20261030.md).
- Current memory's closed producer, foundation and shared-session results;
  read-only RH operation/target callback source.

External pages combine static reconstruction, inferred semantics and reported
live observations. Older Windows RVAs and Linux-derived layouts still require
current-build validation for any runtime work. No new engine mapping or native
availability was verified during this consultation.
