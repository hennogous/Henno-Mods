# CSC AI handoff — 20 November 2026

Regular CSC policy enables sole-supplier repair finishing on CE builds that
expose `CE_AIMaterialWorkerFinishOffer` and report finishing-only support.
Matched controls explicitly disable it. The matched Kish replay restored the
Flax on 166, while the scheduler-off arm stayed pillaged at 170. Olympia's
Farm took one extra turn. Both tuned Continents variants repaired Barley on
119 and had the same supplier, Storekeeper, and economic outcomes.
[Replay and delivery details](../research/mods/csc-ai-material-development-matched-20261118.md#finishing-only-replay-from-the-same-kish-assignment).

The active qualification starts when the improvement is legal. Use the
[numbered Problem 3 campaign](roadmap.md#problem-3-qualification-campaign)
for the current thresholds and preselected map seeds. The reference Kish
replay is `kish150-worker-pools`. Its Water Mill operated and the only
Bakers Base Farm stayed pillaged through 175. Eleven searches found no stock
Builder and another twelve found only processed Builders. Four older
Builder contracts for this repair had separate eight-turn waits. The
matched treatment `kish150-early-recruitment` advanced the reserved job at
the same priority, and a third tree still took the Builder first. See
`kish150-first-recruitment` for the completed start-of-priority replay.
It recruited Builder 4390912 on 172, delaying Isin's Ziggurat, and lost it
to Nippur's Power Station on 173. The completed
`kish150-finish-recruitment` probe gave the assigned Builder one finishing
opportunity on the Farm on 173. The Farm worked at 175 and Isin recruited
the Builder two turns later than in the passive control. The integrated
policy reproduced the handoff in `kish150-packaged-worker-r1`.
Both arms use identical CSC Lua, with only the CE DLL changed. In treatment,
Builder 4390912 reached the Farm on 165 and repaired it on 166. The
matched control still had pillaged Flax at 175. Umma's next two Farm jobs
each finished two turns later. Preserve the matched packages for fresh seeds.

The first qualification arm is `qualification-fractal-28111119-control`
under `csc-ai-problem3-20261118`. It passed normal-start package and map
checks and began the supplier census on turn 1. The turn-200 manual save
was acknowledged and produced no file. That session closed cleanly.
`qualification-fractal-28111119-control-resume150` loaded the earlier
verified manual save and matched all 162 structural rows. The original
`verified-prefix150` ends at the matching SaveComplete record. The
resumed control saved at 200 and stopped after a display failure, with a
verified inactive boundary at 240. The treatment used the same frozen CSC
Lua and the packaged dispatch CE from the Kish pair. It reached 250 and
closed cleanly. Use `comparison-fractal-28111119-verified-snapshots.json`
for the common turn-200 and turn-240 comparisons.
[Fractal results](../research/mods/csc-ai-material-development-matched-20261118.md#fractal-dispatch-comparison-at-verified-snapshots).

Optional mid-run saves can now be recorded as unavailable after a confirmed
file timeout and verified unchanged native phase. Keep an ambiguous save
strict and issue no retry. At a verified endpoint, retain the same
session's autosave if the manual checkpoint is unavailable.
The fresh-game observer now records legal supplier readiness, recovery and
exact buyer construction separately for the two material classes.
[Current evidence](../research/mods/csc-ai-material-development-matched-20261118.md#kish-completed-the-repair-before-the-next-reassignment).

The Quebec pair `quebec150-cafe-specialty-ui-r2` closed at 166 with matching
source, damage on 159 and Café opening on 163. Treatment published three
construction-period Berries offers. Both arms reserved the repair on 164
and sent a Builder on 165. Both still had pillaged Berries at 166. Look
for a Specialty case where the improvement job competes successfully while
its buyer is still under construction.
[Quebec details](../research/mods/csc-ai-material-development-matched-20261118.md#quebecs-specialty-bid-before-the-cafe-opened).

## Earlier investigations

Henno's latest priority is **Problem 3, material work and Builder capacity**.
Current campaign artifacts are in `Desktop/Codex/csc-ai-problem3-20261118`.
The matched Fractal pair verified the same opening and closed at Online turn
250. Distinct worked plots were 16 in the control and 15 in treatment. New
improvements were 15 and 14. Repair events were 3 and 5 across 3 and 2
distinct plots. The working endpoint was 18/24 and 12/20. Treatment CE
`24d17754` had all three optional consumers ready. It published 133 Builder
offers and received zero matching native Builder initializer receipts.
Kish never reserved Flax 2112 as an ordinary city job during treatment.
The closed turn-100 Flax replays compared 64- and 128-unit improvement
ceilings. Both repaired Bakers Flax on 128. The higher ceiling raised its
earlier Builder contract from 154 to 166 utility and moved the first
Tailors job from 133 to 129. The Tailors plot stayed bare through 135.
After finding a Builder on 131, the earlier job failed at Protect Unit
on 132. Inspect worker ownership and native availability across that
handoff before increasing capacity pressure.

The revised production policy credits carried-through job value and can
quote one nearby unstaffed job to value another charge. The frozen package
`treatment-build06/frozen` uses CE `ca09d797` and passed 164 economy,
20 front-end, and 262 native checks. The isolated Irrigation pair is
`research-06`. Both arms added the same fixture city because the
checkpoint player has one city with an existing incomplete Bakers Quarter.
The treatment's +5,994 Q8 reaches the actual research comparison. Both
arms pick Irrigation on 104 and acquire it on 105.

The revised normal-start Online250 game was running in `treatment06-250`
with the verified original Fractal setup. The latest controller owns
worker 20940 and native PID 21196, with campaign shell session 87468.
At verified turn 120 all three runs had seven new improvements, one
repair, and 11/23 eligible plots working. By turn 190 all three had
14 distinct worked plots. Control had two repair events and 18/24
working. Both treatments had five repair events and 16/23 working.
The revised run had four verified native Builder submissions by 190
for two Babylonian repairs. Neither job had worked by that boundary.
The current session stopped at 242 with verification through 240.
All three arms had worked 15 distinct plots through 240. Control had
14 new improvements, three repair events and 17/25 working. Both
treatments had 14 new improvements, five repair events and 14/21 working.
The preserved logs and autosaves are in `stalled-242-evidence`.
After the verified ten-minute timeout, the owned game was stopped and
its preferences and packages restored via a verified menu-only session.
`treatment06-recovery200` matched all 219 retained source rows and
reached verified turn 250 with normal closure. The manual save gate
declined before a request. The original autosave and recorded census
were preserved and validated offline. The combined comparison used the
original through 200 and the resumed branch through 250. Keep the
earlier T240 observation separate.

The combined treatment counts are 15 distinct worked versus control's
16, new 14 versus 15, repairs six versus three across three distinct
plots in both. Both end with 18 working suppliers, from 22 and 24
eligible plots. Publishing averages 1.208 versus 1.321 seconds and
peaks 3.617 versus 2.837, across 250 measured turns. Kish recruits a new
worker for a fresh 188-utility job and repairs Bakers Flax on 248.
Earlier sponsored requests only submitted. Evidence is
`comparison-06-recovered.json`.

The first worker replay was handed off at 108 after repeated presentation
delays. The narrowed `kish-worker-05-late` replay closed normally at 135.
Four recruitment, eight Protect Unit and 106 release checks were
recorded with no callback faults. At 129–130 all four existing Babylonian
Builders had processed their turns. Kish lost its new worker the next
day when Umma's 581-utility Mine outbid its 210-utility Farm at native
priority 2. The same charged unit changed controller, and the Mine
completed at 134. See AI-N158 and the dated matched report.

The next main-CSC candidate credits each imminent compatible queue for
one nearby job and allows one charge-free repair for an existing
worker. Research for a working buyer can value an independent locked
supplier alongside an immediately viable improvement. The 166 economy
and 20 front-end checks pass. Candidate 08 also leaves a conditional
residual-only production quote for an apparently staffed job. It can
land only when the exact native Build Unit fallback runs after actual
worker selection. Shadow records the contingency flag for diagnostics.

Fresh Online250 `treatment08-250` used the same Fractal seeds,
original roster, optional mods and XP2/CE builds. Its package differs
from candidate 06 in two main-CSC Lua files. Shadow's outage stopped
the game after verified turn 185. The turn-188 autosave and interrupted
logs were archived under `treatment08-outage188`. The last checkpoint
with a verified manual save and structural census was turn 150.
The original test preferences and packages were restored through
a verified menu session. Shell 34788 reopened that exact checkpoint
in `treatment08-recovery150`. The source gate matched all 176 retained
rows. The game reached 250, archived its native autosave when the
manual save was unavailable, and closed with preferences restored.
`comparison-08-recovered.json` verifies 23 distinct worked plots
versus control's 16. New improvements were 20 versus 15 and repairs
were six across four plots versus three across three. Working supply
was 19/27 versus 18/24. Publisher mean/peak was 1.242/2.559 seconds
versus 1.321/2.837. Seven extra plots were worked only in the recovered
arm. The control's entire worked set is present in that arm. The
trajectories diverged after the reload.

At the verified T160 boundary the control had worked 13 distinct
plots, and candidates 06 and 08 had both worked 14. Working supply
was 17/24 in control and 17/23 in both treatments. Candidate 08
had 92 material Builder offers, 38 flagged as contingency, and four
native receipts. The two new contingency receipts reached the
Kish Flax repair on turns 123 (218 → 221, contract 2249) and 133
(219 → 223, contract 2478). Both reached production submission.
The earlier contract cancelled and neither had actual Flax work at 160.

The working tree includes the next material-value change. An exact
job gains the value of a Service it can restore by itself when the
producer, customer and unlock already operate. A separate ordinary
subtotal prevents duplicating one Service in the multi-job capacity quote.
The 169 economy and 20 front-end checks pass. Version 09 was frozen
with five changed main-CSC Lua files and unchanged CE. At Henno's
approval on the morning of 19 November, the same-seed fresh Online250
run in shell 92947 started after verified version-08 closure. The
folder is `treatment09-250`, native PID is 5612 and controller worker
is 4204. Turn-1 setup verified. Both arms had nine distinct worked
plots through candidate 09's verified turn 125. Seven positive
Service quotes were published. The first was 6,250 Q8 at Kish's
Tailors Flax 2112 on 107, above 17,954 Q8 of ordinary utility.
Through verified turn 205, candidate 09 had worked 16 distinct plots
versus 14 in control, with 17/23 versus 19/25 suppliers working.
It published 31 positive Service quotes across three plots. Aztec
Builder contract 4061 for plot 925 rose from 219 to 282 utility on
195. The native game recorded its gold purchase and contract
completion on 203. Tenochtitlan found a Builder on 207, hit a
Protect Unit failure on 208, then reopened the job and repaired the
Farm on 209. A single physical repair restored the last working
Base supplier for two Quarters. Their Storekeeper growth modifiers worked
again on 210. The game recorded a second purchase for this job (contract
4369 at 257 utility) on 207. The native unit log identifies the repairer
as 12189724. Both purchase rows omit unit IDs.

The fresh game reached verified turn 250, saved normally and closed with
preferences and packages restored. `comparison-09.json` shows 17 versus
16 distinct worked plots, 16 versus 15 new plots, and 4 repairs on one
plot versus 3 repairs on three plots. Both had 18 working at 250, from
23 and 24 eligible respectively. Candidate publisher time was 1.162 s
mean and 2.605 s peak versus 1.321 s and 2.837 s. Kish's Textile Workshop
completed on 103 and the legal Flax work offered by 107 remained undone.
The fresh run gives a smaller gain than candidate 08's resumed game.

Henno wants supplier work to start when a producer commits to construction.
The main mod now reads the current production hash and ETA once per city
and publication. The exact Stage 2/4 commitment enables Base/Specialty
jobs while the building is still underway. The quote prices actual material
transactions after the later of the supplier job and building completion.
Service restoration credit still requires its live prerequisites. This is
candidate 10, frozen with four changed CSC Lua files and the same CE
binary. Henno requested the same Fractal through turn 250 and a breakdown
of successful and unsuccessful Builder bids. The shared controller started
`treatment10-250` from the normal same-seed setup. Turn-1 source and both
native module identities verified. It ran without a reload to turn 250,
closed and restored settings and packages. The manual save gate declined
before a save request. The archived native turn-250 autosave and all ten
censuses verify. `comparison-10.json` records 21 distinct worked plots
versus 17 in 09 and 16 in control. The endpoint was 15/22 working versus
18/23 and 18/24. Both Umma Farms disappeared on 236 and stayed bare.
Kish's first active-buyer Farm bid on 61 added 15,364 Q8, while the
ordinary job retained its Ziggurat site. It completed the Farm on 75,
the same turn in all three arms. The 19 early quotes covered eight exact
Base jobs and seven eventually saw work. Of 205 Builder offers for nine
jobs, seven received exact native initialization. Two were cancelled and
five had submissions only. None acquired a new Builder. Two offered plots
saw later work in a fresh job. No game remains. The tracker carries the
earlier usage-limit status.
[Campaign details](../research/mods/csc-ai-material-development-matched-20261118.md).

The matched dispatch study is closed. `dispatch-kish150-corrected` reused
the passive Kish control, verified the same source and found the Flax
repair already selected at both useful vacancies. Both arms made 20 failed
Builder searches and left the Farm pillaged at 175. Both test-only native
prototypes remained idle in that window. The preserved Umma T241 autosave
retained AI ownership of the observer seat. The shared controller safely
closed it and used `dispatch-umma200` with identical one-time damage from
the verified manual checkpoint. The changed CSC rule admits repair offers
with legally recoverable Base supply and an existing on-site producer.
It produced one exact Umma offer from 201. CE admitted zero and counted
the ordinary 214 repair as a duplicate. Both arms had no working supply
at 215 and closed with settings and packages restored. See the checkpoint
results in the dated report. Game and CE build hashes were unchanged.

Main CSC now prices exact legal material jobs from the transaction definitions.
The Fractal candidate reserves Mycenae's Pasture two turns earlier and the
saved game verifies working supply on 183. Both arms finish work on 169.
Tenochtitlan's Wheat repair reaches a completed Builder request and still
needs a worker. The active capacity question is how to get a real assignment
for a valuable admitted job.
[Implementation and evidence](../research/mods/csc-ai-material-job-followthrough-20261118.md).

The first slice of **14.3 prospective Service value in Quarter bids** is
implemented and qualified for native prices and calculated bids
in unchanged saved100/250 worlds. [Implementation, costs and remaining work](../research/mods/csc-ai-service-valuation-implementation-20261118.md).
Use matching CE development build00edf646; source and frozen03 are recorded there.
Native source branch is `codex/native-quarter-valuation`; no upstream PR.
Housing and the linked-Wonder branches are now covered in the standard
Bakers/Tailors catalogue, with the Horticulturist in the optional Leugi branch.
Next validate these additions live, then check changed choices, foundations and
whole-guidance timing.
[Catalogue/evidence](../research/mods/csc-ai-bakers-tailors-service-catalogue-20261118.md).

**Problem2.1 is closed.** All six preselected fresh Online250 comparisons qualify,
restore and pass fresh v3 accounting. Links75→86; customer-after-Quarter45→56
(Bakers35→42, Tailors10→14); customer-first30 unchanged. Mean/max guidance
2.321/7.044→2.451/5.882s. All69 guided foundations have Base; Fractal has the
first campaign Dockmaster. Short changed-choice/foundation, stronger-site and
invalidation checks plus two mature same-state timing checks complete the audit.
Astra recommends closure; no more policy changes/games are needed for2.1.
[Final results and limits](../research/mods/csc-ai-customer-scheduling-20261117.md).

The initial Problem 3 census found seven endpoint cases with operating
producers and no working Base supplier. The customer-placement goal is complete.
Parent5067 and saved-world timing sessions are closed. Main F/M/E policy text
matches the qualified candidate; the model-reuse prototype stays unintegrated.
Keep unrelated art/UI work intact and review any CE PR with Henno first.

## Earlier handoff checkpoints (historical)

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
