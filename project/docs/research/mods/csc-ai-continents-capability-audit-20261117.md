# Continents: Problems 1 and 2 capability audit

17 November 2026. Read-only review of the completed integrated Continents250
run and current main-mod code, with an independent Astra code/results review.
No game was launched. The suggested repeat run is not yet started.

## What is active

| Roadmap | Evidence from this run | Remaining question |
| --- | --- | --- |
| 1.1–1.4, 1.8 | 22 foundations, all Base-adjacent;20 at+3+,7 at+4+,5 with both materials.82/82 observed native Quarter BEST values match published bids.53,073 managed-cell masks recorded | Why strong geometry sometimes fails to become an economical positive offer |
| 1.5–1.6 | Tailors1123: selected22, paid30Gold23, founded33, completed35. Ownership-completion API acknowledges in3 observed windows | Frequency across different opportunities; natural supplier-land acquisition |
| 1.7 | Managed negative defaults cover unoffered Quarter cells;97 reconsideration transitions | Trace a natural weak-city defer/change/reconsider/build sequence |
| 2.1 | 4,834 economic proposals;1,587 native writes and19 observed site-win windows. Existing-Quarter customer scoring is implemented | Customer spatial/investment coordination, especially Tailors/Harbor |
| 2.2 | Native exclusions mask candidates, Wonder and Builder protection alter evaluations. No recorded voluntary district destroys the last owned material class | Harvest route and broader loss/recovery opportunities |

The 22 founded sites all tie best geometry among the planner's positive
city/type offers. Geometry-qualified identities are374 Bakers/215 Tailors;
positive-offer identities78/60. This makes the rejection funnel worth auditing
before increasing bids. It does not establish that every rejected site deserved
construction. [Full result, definitions and provenance](csc-ai-ordinary-economy-continents-20261117.md).

## Additional native receipt audit

Read all250 `previous=` status windows in the frozen run's Lua.log. These are
windows containing nonzero counters, not counts of distinct decisions:

- Supplier exclusions: nonzero masked counter in230 windows.
- Wonder protection: nonzero changed counter in233 windows.
- Builder protection: nonzero changed counter in217 windows; bid counter
  nonzero in154. This is useful adjacent evidence for material preservation and
  later Problem3, not a new placement-only mechanism.
- Ownership completion: considered in41 windows, acknowledged in3.
- Harvest protection: ready in250 windows, rejected counter zero throughout.
- Typed decline: no considered/masked rows. Current managed complete-valuation
  mode supplies negative defaults instead; zero use of this older optional
  route does not establish failed poor-site suppression.
- Building nominations changed values in60 windows. Repair admission was zero
  in four considered windows; that later-stage execution dependency belongs to
  Problem13, outside the current placement scope.

All250 windows of the capability statuses exposing a faults field report zero.
Exclusion status has no faults field; do not infer one. Customer receipt readback
errors are zero. The common scoring/transport path is not silently inert.

## Concrete code boundaries

**Customer land and eligibility.** `EconomyFacts.CustomerCandidateSets` builds
economic alternatives around existing Quarters from currently owned,
resource-free footprints, unlocked district types and current native legal
targets. There is no equivalent customer-site purchase/preparation path for a
good adjacent tile outside those conditions. This can omit a viable long-term
layout even though Quarter-footprint acquisition works.

**Customer continuity.** `PlanContinuity` tracks native-confirmed Quarter
choices and releases their plan at foundation. Customer layouts are recomputed
from current facts without a persistent commitment to a particular joint
footprint. The Quarter can therefore finish while its intended customer tile,
slot or investment priority goes elsewhere.

**Distinct customer paths.** Post-foundation customer scoring is already in
`EconomyFacts.CustomerCandidateSets` and `EconomyAdapters.CustomerEconomicOffers`.
Do not repeat the obsolete diagnosis that built Quarters get only native SQL.
The separate customer-first geometric preference serves empty future Quarter
footprints and strictly preserves best ordinary adjacency. Built Quarters get
SQL adjacency and ordinary transaction residuals, without that same preparation
preference. Prospective Service value remains deliberately excluded.

**Bounded shortlist.** Customer economics prices at most16 worlds/player,
reference plus up to3 alternatives/group. Group rotation does not guarantee
that every alternative plot is eventually priced. This is a coverage question
to observe before widening the work budget.

**Building execution.** The economic scheduler forecasts later producer/customer
investments; it does not nominate all those buildings for construction. Retained
execution assistance is Stage2. The Temple-connected Tailors lacking its Tailor
building is therefore a later building-guidance dependency. It should not be
misdiagnosed as failure to deliver a district-site bid.

**Diagnostics.** The153 customer skips combine reference/candidate quote failures
and missing/nonpositive raw native values;13 residuals clamp. Split the causes.
Zero harvest rejections needs an actual eligible harvest opportunity before
assessing that intervention's effectiveness.

**Performance.** Late-game publication averages2.98s/turn across five AI players,
for two Quarter families. Profile repeated world/pricing work before expanding
scope; retain the current value bands during this audit.

## Recommended next run

Astra and the primary reviewer recommend one fresh same-seed Continents250
regression run before changing policy: same stock AI, Online speed, leaders,
map/game seeds, optional-mod stack and qualified CE binary. Build current CSC
through its normal packaging. This tests the new SQL/actions from fresh startup;
a loaded-save replay alone misses that bootstrap path. Complete the pending
Government-screen check with EPC enabled.

Add bounded passive opportunity/reason counters, preserving tuning values:

1. For disconnected Tailors, track adjacent Harbor geometry, ownership/unlock,
   native legality/capacity, ordinary adjacency, shortlist inclusion, offer,
   native comparison and later footprint occupation.
2. For good Quarter sites, trace geometry→supply→economics→publication→selection→
   admission→foundation, including rejection reasons and winning competitors.
3. Split customer skip causes and retain timing/receipt coverage. Aggregate or
   sample diagnostics rather than logging a full repeated search on every turn.

Compare definitions, health, bids/receipts, the placement/chain trajectory,
material losses and average/max processing time, as well as the endpoint.
Keep the existing run as the reference. The shared controller and15-minute
check-ins remain required. Do not restart all remaining campaign games as a
side effect of authorizing a single regression run.
