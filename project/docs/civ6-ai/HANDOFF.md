# CSC AI handoff — 18 November 2026

**Current work: the customer-placement goal is active.** Start with
[the goal, gates and preselected maps](customer-placement-goal.md) and
[current status](STATUS.md). Main CSC's pair-first customer scheduler7ea8820a
reaches all164 observed city/type windows in the150–160 comparison, versus123,
at the same474 forecasts. Buffalo's fresh62.414utility residual reaches its
actual native comparison; the stronger alternative still wins and is founded.
No coefficients or Services changed. Current-stack Magdeburg combined-edge0/1
changes unlinked2377 to linked2227 and each is founded151. Zero also removes
the Lua routing edge, so this qualifies combined guidance. The first fresh
Online250 pair is complete: non-City-Center links20→34, comparable connected
foundations8/16→17/20. Bakers links11→20, Tailors9→14. Pangaea control completes
250 with32 links and10/14 comparable connected foundations; its treatment also
qualifies250:28 links,13/24 comparable,18vs16 Quarter-first links. Tailors has
threevs six foundations and sixvs12 links. Guidance3.028→2.638s average.
Across two maps links52→62, average2.502→2.500s. Audit the mixed outcome and
native misses before closing2.1. After a pre-Lua discovery gap, controllerc7bf6b2b preserves the finite
operation on that failure. Parent exec5067 owns the six-game campaign. Keep its
frozen policy unchanged; Fractal control qualifies250(23 links,16 Base-adjacent
Quarters,10/20 comparable). Its treatment is running, the last of six games.
The runner uses immutable
manifests, initial parity, closed-child recovery and duplicate retirement.
Use the shared controller, fifteen-minute checks and bounded passive diagnostics.
[Native evidence, timing and storage retirement](../research/mods/csc-ai-customer-scheduling-20261117.md).
Continue Problem3 research only after2.1 succeeds if usage remains. No upstream PR.

**Latest Perth follow-up:** recorded native comparisons answer the delivery
question:20/20 positive target writes equal published values and lose to higher
district bids; zero Tailors winner/request. Perth was+2 through203, then+3;
first positive+3 offer214 loses to Campus. Removing only the quality cap would
not reverse any matched numeric comparison. Next1.4: audit ordinary economic
income/cost and staffed-footprint pricing against competing investments, before
changing values. No replay/game/tuning/native change was needed.
[Perth report and comparison records](../research/mods/csc-ai-perth-followthrough-20261117.md).

**Later continuation completed:** post-restructure Continents250 closes/restores
normally:23 foundations,21 at+3+,eight Storekeepers/three Innkeepers, guidance
1.97s average/3.86s maximum. Government/Policies UI passes at25.20 physical
non-City-Center links include12 Quarter-first/eight customer-first, after capture
deduplication; earlier24 counted owner-scoped records. See
[completed regression](../research/mods/csc-ai-restructure-regression-20261117.md).
[Per-type placement and count correction](../research/mods/csc-ai-customer-placement-breakdown-20261117.md).
Read-only current50/250 and earlier Fractal250 surveys also close/restore.
[Dockmaster survey](../research/mods/csc-dockmaster-opportunity-survey-20261117.md)
finds two good owned Fractal layouts and a current Perth follow-through case:
improved Base+Harbor/Lighthouse,+3 unbuilt Quarter,42 acknowledged native writes.
Those surveys and the earlier stopped campaign are closed. The newer authorised
customer-placement goal above governs current tests; do not resume older campaigns.

This is the starting point for continuing the research in a new chat. Read this
page, [STATUS](STATUS.md), the opening of the [roadmap](roadmap.md), and the
installed `civ6-ai` skill. Earlier dated checkpoints remain evidence; their
superseded next-step lists are not instructions to restart that work.

Follow-up: Henno chose to continue in this chat and requested Astra's review.
[Problems1/2 capability audit](../research/mods/csc-ai-continents-capability-audit-20261117.md)
records additional native receipt counts, customer code boundaries and the
recommended post-restructure regression, now completed as summarized above.

## Scope and architecture

The current AI scope is **Problems 1.1–1.8 and 2.1–2.2**: worthwhile Quarter
sites, acquisition/follow-through, poor-site suppression, customer/provider
placement and material protection. Bakers and Tailors share mechanisms intended
to extend to all eight Quarters. Stock game AI is the focus; RHAI5 is deferred.

Gameplay definitions own materials, partners, amounts and gates. One central
economic model builds before/after worlds; decision adapters deliver their value
through CE/native decisions and SQL private-yield adjacency. Preserve ordinary
district competition. Prospective Service valuation remains deferred; existing
Stage 2 assistance remains. Reasonable economic estimates and useful outcomes
are the target, with bounded processing time.

- [Architecture and diagram](architecture.md)
- [Economic contract](../integrations/csc-economic-contract.md)
- [Implementation goal and G1–G7 dependencies](ordinary-economy-goal.md)
- [Joint customer-world/native pricing evidence](../research/mods/csc-customer-world-pricing-20261117.md)

Main code is in `Civ Supply Chains/Lua_UI/AI/`: `CSC_AI_EconomyFacts.lua`,
`CSC_AI_EconomyModel.lua`, `CSC_AI_EconomyAdapters.lua`,
`CSC_AI_QuarterPlacement.lua`, `CSC_AI_AdjacencyScan.lua`,
`CSC_AI_PlanContinuity.lua` and `CSC_AI_DistrictBridge.lua`. Native customer SQL
signals are in `Data/CSC_Q_ALL_AI_Connectors.sql`.

## Latest completed game and interpretation

The integrated Online Continents game completed turn 250. Pangaea was stopped
at Henno's request after its last verified turn-75 boundary; Fractal never
started. There is **no active goal** in the goal tool and no agent-owned game.
Do not resume the old campaign without a new instruction.

The completed game had:

- 22 foundations: 17 Bakers, 5 Tailors; all Base-adjacent, 5 with both materials.
- 20 rated +3 or better, 7 at +4 or better. All 22 tied the best geometry among
  their positive city/type offers. Future customers were excluded from ratings.
- 82/82 observed native Quarter BEST results matched the published bid.
- At 250: 8 Storekeepers, 2 Innkeepers, no Dockmasters or Sacristans; 1,101
  independently observed Storekeeper chain-turns over the run.
- Customer writes reach native decisions, but Tailors' customer coordination is
  weak: no adjacent Harbor; producer and Temple investments fail to coincide.
- Guidance averages 2.03 seconds per turn across five AI players, max 4.61;
  the last 50 turns average 2.98. Repeated pricing needs further profiling.

[Full analysis, baseline comparison and provenance](../research/mods/csc-ai-ordinary-economy-continents-20261117.md)
includes placement/building/material counts, economic totals, losses, native
receipts, clocks and the distinction between offers and actual follow-through.
The report identifies frozen AI revision `1d7ecc0f`, CE source `39c5ebf` and
the tested DLL hash. Preserve its baseline/provenance when comparing later code.

## Implemented versus next work

The major ordinary economic channels are integrated: fixed/local exchanges,
directional material flows, population scaling, shared producer/customer
investments and queues, observed staffing/routes and pooled amenity effects.
Native interval pricing and representative customer correction transport are
qualified; the completed run adds actual reception/outcome and timing evidence.
Do not restart these migrations because an older paragraph calls them open.

The clearest AI next steps, when Henno resumes tuning, are:

1. Problem 2.1: coherent customer planning after a Quarter exists, especially
   Tailors/Harbor and producer/customer investment coordination.
2. Problems 1.1–1.6: audit profitable strong sites that were never offered or
   followed through on; continue Base/Spec opportunity and acquisition awareness.
3. G5: profile and reduce repeated economic pricing while retaining useful bids.
4. Further full-game qualification only when authorized. Pangaea/Fractal remain
   incomplete; don't claim the three-game campaign finished.

The [manual gameplay QA checklist](../research/mods/csc-economic-integration-manual-qa-20261117.md)
is still for Henno. No upstream CE PR is authorized; review contributions with
him first. The development CE build supplies APIs not assumed in upstream CE.

## Source cleanup and latest UI follow-up

After the game analysis, work moved to source organization and offline checks,
with no new test games. [Shared SQL structure](../integrations/csc-shared-sql.md)
documents the consolidated schemas/processors and seven-section Quarter format.
Action order is LoadOrder, action type, action ID; JSON generates project CDATA.

Two regressions were fixed: duplicate Schema Content broke ModBuddy copying
(`97de8a86`); merging Schema/Common exposed native file ordering and broke fresh
startup (`4a92db48`). Schema now loads at 94 and Common at 95. The user's rebuilt
game confirms correct ordering and passed gameplay database validation.

Henno then reported that the Government screen no longer opens, only after the
latest restructuring. Initial blame on EPC alone was premature: CSC's adapter
participates in its rendering path. The adapter now preserves BRS initialization
and attaches from its own context through the public API (`ad774e85`). Offline
checks pass, including EPC's renderer with stand-in controls and failure recovery.
**Rebuild/reload and native Government-screen review are still pending.** Keep
EPC enabled for that check; the exact restructuring trigger is not reproduced.
[UI integration, evidence and delivery details](../integrations/csc-policy-card-estimates.md).

Latest maintenance checks: 205 Quarter tests, 83 transaction tests, 11 ModBuddy
tests and 80 policy-estimate fixtures, plus lifecycle/renderer checks. There were
no new AI policy or CE binary changes during the cleanup/UI repair.

## Operating rules and knowledge locations

- Do not close/restart the user's Civ/FireTuner session or connect a competing
  controller. No desktop automation on Shadow. Use the shared controller for
  authorized live tests, with 15-minute check-ins and reconstructable logs.
- Test main-mod tuning alone; no diagnostic policy, grants or forced execution
  in efficacy games. Diagnostic fixtures remain separate and labelled.
- Keep baseline/current relevant evidence; don't accumulate every obsolete dump.
- The checkout contains unrelated art, lens, Pedia, localization and Tailors
  PLUNDER_GOLD work. Preserve it; use scoped staging, not a blanket reset/commit.
- CSC policy/results live in repo Markdown. Reusable engine knowledge lives in
  the separate installed `civ6-ai` skill: focused engine references and AI-N
  finding register (through AI-N142 for the latest pricing/transport work).
- AI handbook Quartz publishing is retired. Markdown commits/pushes suffice;
  the separate public player site continues.

This handoff consolidates the current state, not every raw transcript. Dated
reports and the [finding register](findings.md) retain detailed evidence and
corrections. [Maintenance](maintenance.md) describes how to extend them.
