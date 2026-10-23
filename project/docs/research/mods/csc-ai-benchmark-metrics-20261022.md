# CSC AI tuning benchmark and metrics

22 October2026. Human accepted the metrics/paired-benchmark proposal with this
overriding baseline definition: “the baseline should be without any AI
intervention at all. the only intervention shared by both should be our resource
pass where we set up some more good quarter placements.”

## Baseline and treatment

**Baseline = ordinary native AI playing CSC, with the shared resource pass.**
CSC's actual gameplay stays enabled: Quarters, building chains, material rules,
real adjacency/yield effects, Services, sales and normal costs/requirements.
The baseline has no deliberate CSC AI assistance. Exclude the external
foundation planner and land purchasing, AI-only placement/private-yield signals,
material-preservation/improvement biases, altered Builder priorities and
improvement pseudo-yields, custom research preferences/goals/strategy callbacks,
and other tuned AI weights or scripted decision overrides. Third-party AI
overhauls are disabled. Normal AI decisions reacting to real CSC gameplay
effects remain part of native play.

The resource-generation pass is the only shared experimental intervention.
Both arms get the same pass version/settings, seeds/rosters/map options and
verified identical initial physical/resource maps. It must only affect the
agreed world-generation setup, with no ongoing grants, district foundations or
AI-control actions hidden inside it. Identical read-only observers may run in
both arms; they must not write economic/gameplay state, priorities or choices.

**Tuned = the same gameplay/resource setup plus explicitly enumerated AI aids.**
Record every treatment component and its parameters/source hashes. It can
include the Service-aware planner and purchases or the AI guidance being tested.
AI-only legacy helpers are treatment components, never quietly shared with the
baseline. The main two-arm comparison estimates the whole declared package.
Separate component effects would require an explicitly planned additional arm.

### Baseline construction and verification

Audit source actions, SQL and Lua across all loaded components, not only the
new planner toggle. Current `Data/CSC_AI.sql` contains existing interventions:
improvement pseudo-yield90, Builder priority50, private placement/sales/bonus/
river signals, exact-material/improvement modifiers and research strategy/list
declarations. Research callback loading must also be considered. This list is
evidence for an exclusion audit, not a claim it is exhaustive.

Disabling the external planner alone does not produce the agreed baseline.
Exclude AI-tuning actions before a fresh game's databases/state are created;
do not attempt a live rollback of an already tuned game. Obtain stock values
from the same game/DLC configuration and verify relevant runtime tables against
that reference. Include an explicit allowlist of treatment-only DB/actions/Lua
differences, and prove normal CSC gameplay tables/effects are otherwise equal.
Preserve installed/build manifests and exact executed inputs for each arm.

Same seeds alone are insufficient when builds or resource passes changed.
Verify the generated initial world, starts and resource plots. Historical games
remain descriptive references unless their settings/data meet this contract.

## Headline scorecard

| Metric | Standard measurement |
|---|---|
| Service delivery | Active recipient-Service instances per100AIcities and cumulative recipient-Service-turns per100AIcity-turns, per Service. Record exact source/recipient identities and avoid duplicate equivalent grants. |
| Functioning sales coverage | Functioning producers with at least one eligible functioning customer / all functioning producers; distinct eligible producer-customer links per100cities. Structural eligibility is not a logged payment. |
| Effective material supply | Developed stage2+Quarters with owned, improved, unpillaged Base / developed Quarters. Report stage4Both separately and zero/one/multiple Base neighbors. |
| Opportunity conversion | Distinct qualifying city-Quarter-Service opportunities becoming functioning chains within25/50turns; conversion delay. Separate ready, one-purchase and future development/research opportunities. |
| Supply durability | Supported developed-Quarter-turns / observed developed-Quarter-turns, plus25/50turn supply-retention cohorts and loss of last required Base. |
| Strategic usefulness | Relevant city/demand-turns covered by the appropriate active Service, and observed benefit use, with directly observed needs separated from inferred priorities. |

The evaluator must be common across arms and independently checked against
canonical gameplay/native requirements. Avoid letting a treatment's own changing
ranking define the denominator used to judge it. Count city-Quarter-Service
opportunities, not all candidate tiles; record conflicts between opportunities
that compete for the same land, budget, district capacity or production.
Stage2/3Base-only routes can succeed; Both is chiefly a stage4 opportunity.

## Diagnostics and guardrails

- Development: foundation→Quarter→producer→Service timings, completion25/50turn
  cohorts, unused/unfinished district-slot commitments, and time blocked by
  buildings, improvement, customer, civic, ownership or native legality.
- Materials/Builders: time to improve useful Base/Spec, eligible supporting plots
  improved, repairs, last-Base losses and redundancy. Deduplicate physical plots;
  also record how many Quarter chains each plot supports. Confirmed harvesting,
  pillage, ownership loss and unexplained disappearance are separate causes.
  Builder counts/charges are capacity/context, not proof of productive use.
- Research: unlock dates, opportunity→required-civic delay and opportunity-turns
  blocked solely by research. Never infer an observed active native strategy
  merely from leader identity or our own recommendation logic.
- Acquisition: actual native gold spent and ownership receipts, cost per useful
  functioning acquired chain, intended outcome within25/50turns, stranded buys,
  cooldown/reserve compliance; strong Service and general purchases separately.
- Wider empire: totals and city/pop-normalized science/culture/production,
  population/expansion, military readiness, maintenance and treasury trajectory.
  Savings alone can indicate underinvestment; judge trade-offs alongside CSC.
- Reliability/evidence: completed games, controller failures, genuine native
  crashes, recoveries, interventions and missing observations. A valid partial
  run is disclosed separately and never relabeled a250completion.

Do not add incomparable yield types into a universal profit score without an
explicit valuation model. Exact native contribution measurements, if added,
must remain distinct from structural relationship counts and counterfactual
claims about benefits attributable to tuning.

## Sampling and comparison

Use common beginning-of-turn checkpoints1,25,50,...250 plus event/turn records
for transitions, choices, losses and Service activation. Report endpoint values
and cumulative curves. Native phase differences must remain explicit.

Every rate includes numerator/denominator, Quarter/Service/stage breakdown and
per-game variation. Zero available opportunities means not applicable, not a
zero-success judgment. Late cohorts that have not had25/50turns are censored.
Separate naturally chosen, foundation-assisted and purchased sites, then show
the combined empire result. Ownership changes and defeated/nonmajor owners
must not silently turn observed completion into noncompletion or missing data.

Five matched world pairs are a reasonable starting benchmark design. Games are
the main independent samples; fiveAIplayers from one map are not five
independent worlds. Instrumentation/metric definitions and gameplay/resource
pass are frozen before official benchmark arms. Small historical samples and
changing builds do not establish statistical or causal superiority.

## Execution status

The running Service-aware run02 is a tuned development pilot on the current
build. Keep its sources/runtime frozen and let it proceed under its existing
authorization. This agreement does not convert it into a baseline, retrofit all
proposed telemetry or launch additional benchmark games now. Some historical
metrics can be reconstructed; additional instrumentation needs verification
before the formal paired comparison. Benchmark execution is a separate next
step after the pilot/instrumentation review.

## Pilot evidence coverage at exact124 — 23 October

The current material-first development pilot has615 unique AI player-turn research
rows through123 and17 assisted foundation targets at124. This is a continuation
checkpoint, not a completed benchmark. Fine-grained chain/treasury/retention
collection begins67; historical missing coverage and the explicit76 planner gap
remain disclosed. Native stage/venue links and producer metrics are structural
proxies; they do not establish every Service requirement or actual transactions.

Separate four acquisition states: discovered Both plan; funded/reachable decision;
one request dispatched; actual same-turn native ownership+exact gold receipt.
The frozen45 diagnostic reached the third state only. Its real outcome was
unconfirmed, with no changed world/gold and no AI turn advance. Exclude its scene,
requests and any potential effects from the accepted current124→250 performance
cohort. Preserve the diagnostic as capability evidence. Main `purchase_unavailable`
counts measure a command-path limitation separately from planning/affordability
rejections and successful owned-land establishment. An unavailable path must not
silently count as no opportunity or as money spent.

Exact supported manual checkpoints after planner cycles preserve assisted sites
and simplify clean recovery. Retain native timestamp/phase/SaveComplete/hash and
cycle-executed metadata alongside observer coverage so recovery and repeated
readbacks never inflate placement/completion or research denominators.

## Reusable offline pilot evaluator — version14

`service_planner.benchmark_report` reads accepted-root metric points and journal,
checks actual-turn uniqueness and reports missing/left-censored coverage. Physical
plot+Quarter identity keeps captured assisted sites in the assisted cohort. A site
missing from the major-AI census is unknown/outside that census, not automatically
destroyed. Zero denominators produce null ratios. PrivateYIELD_CSC_AI_* are
reported separately and excluded from economic output comparisons.

Report owned/improved/unpillaged material links at endpoints separately from
availability at every observed boundary; neither claims unobserved within-turn
continuity. A shared material tile may supply multiple physical Quarters and
therefore count per link. Raw turn96..130 pilot data has9 baseline links retained
at130,8 observed throughout all35 checkpoints. This is a small censored cohort,
not a claim that every placed Quarter kept its Base or that all materials survived.

Through130 physical cohort counts:19 assisted Quarters(12complete,9producerbuilt,
15with ownedBase,0Both),25 other native Quarters(24complete,16producerbuilt,
5ownedBase,0Both). ImprovedBase producer proxy4/9 vs3/16 is descriptive with
different placement ages, not a causal comparison. Native Service fulfillment,
exact improvement requirements and monetary transactions remain unverified.
Primary1/25/50/75/100/125 and Builders1/5/50/100 scheduled snapshots are present.
Rejected role diagnostic131→132 must be excluded and the discarded/replayed raw
interval disclosed; the accepted trajectory is restored from exact131 checkpoint.
