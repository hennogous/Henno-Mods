# Joint customer worlds and corrected interval pricing

Roadmap: **1.4 / 2.1 / 2.2**. Updated 17 November 2026.

The current model can now price an owned customer footprint against the existing
Quarter economy using actual gameplay definitions. In a mature saved world,
eight of eight sampled native-admitted footprints produce real native prices.
The first attempt priced zero of eight; the blocker was the CE timing wrapper.

## What the customer evaluation includes

Facts builds a common before/after world for the player's existing Bakers and
Tailors. The after world adds the proposed customer and its defined building
venues, changes actual Quarter/customer adjacency, and removes suppliers on the
footprint. The model shares city construction queues, prerequisites, investments,
upkeep and rounded population targets. Observed routes and actual specialist
assignments use the same baseline in both worlds. Prospective Services remain
deferred.

Adjacency reads the bundled gameplay matcher, including City Lights tags.
An unfinished district can already be an adjacency source, while a receiving
district must finish before receiving its own bonus. Construction/repair work
for a Quarter and a new customer in the same city uses one queue. These facts
prevent both premature income and duplicate construction opportunities.

Twelve tests exercise actual transaction SQL, adjacency Core, Facts and Model:
shared Markets, Bakers/Tailors pooling, unique buildings, provider foundations,
supplier removal, route thresholds, unfinished/damaged hosts and common-world
identity. The complete transaction suite passes76 checks; the economy suite
passes114 after the pricing adapter change.

## Why the first native quotes failed

The native cumulative-income helper returns its input at time zero. Its timed
helper subtracts the start quote from the end quote. A short `0..1` recurring
income can consequently return a negative raw difference. The existing CE yield
wrapper rejects the unexpected sign. Mature-world routes already eligible to
finish produced precisely these one-turn windows, blocking otherwise valid
joint customer quotes.

CE now offers two explicit APIs, `CE_AIYieldIntervalValue` and
`CE_AIAmenityIntervalValue`. They keep the native economic weights and discount
curve, and use a zero cumulative origin for recurring intervals. For a zero-start
yield they add the normalized amount before range/sign validation. For amenities
they add the native current quote for the same city and combined count; happiness
thresholds make a multiple of a one-amenity quote inappropriate. Arithmetic uses
a wide intermediate. Existing Stream and fixed-amount APIs retain their behavior.
CSC requires the new interval bindings rather than dropping short contributions.

The supported VS2022 Release build passes.249 native checks, four Runtime hook
failure/cleanup cases and instruction-call restoration pass. Astra reviewed the
implemented native and Lua changes without a material finding. No upstream PR.

## Live evidence

`customer-world250-02`, shared controller, original turn250 world, no orders or
turns advanced:

- Fifteen real pricing cases pass across five AI players: signed one-turn
  Production, interval subdivision, preserved positive-start/fixed quotes and
  pooled two-amenity quotes.
- Eight of eight customer footprints price successfully. Marginal values range
  from14,449 to65,322 Q8, approximately56–255 utility.
- Quotes across players with Quarters use85–136 cached native prices and96–160
  joint evaluations per before/after pair. The two-target per-player command
  takes3.7–5.4 seconds including facts, definitions and console transport. This
  is diagnostic cost, not an approved recurring full-map scanning budget.
- All10,954 native gameplay effect rows match the reference. Population refresh
  and the22-chain reader smoke pass. Process exits0; ownership, preferences and
  package restoration verify.

Native build SHA256:
`3cdaf7a190f7b190cbc37059c7bd5981ac92b0a13364b8fcc62b91eaf6712b23`.
Source binary XP2 SHA092abfbb; Ghidra reference SHA324c51e9 has identical relevant
instructions. Private evidence root:
`Desktop/Codex/csc-ai-ordinary-economy-20261116`.

## Native delivery qualification and gameplay QA

The narrow observer now records native GetBestDistrict's actual comparison at
RVA3e4b2c: ECX is the candidate score, EDI its reservation threshold, EBX the
best score so far, RSI the plot-analysis row and R14 the district type. It also
records raw activation and post-aggregation values. All hooks are observational
and avoid CE's patched function entries and the guarded aggregation CALL.

The one-turn baseline qualifies two real player5/city65536 Hub footprints:

| Plot | Native pre-aggregation Q8 | Native aggregate/compared Q8 | Joint marginal Q8 |
| --- | --- | --- | --- |
|1082|605,685|730,973|59,110|
|1083|575,787|701,075|29,871|

Both guarded-late attempts skip the write because the legacy API requires an
actual reservation ID of−1. Plot1082 has an active claim;1083 retains ID3538948
while its effective comparison threshold is the ordinary−2,559,744 sentinel.
That threshold does not establish an empty reservation slot. Both attempts exit0
and restore normally; no correction
was consumed in those arms.

Astra recommends testing the existing early Entry hook before adding another
native API. The off-turn evaluator writes fresh NetValue output and then applies
the stock district preference; aggregation adds the common building subtotal.
An early site differential can follow this established path without cumulative
reader writes. The two-turn early probe now passes. For plot1082, the actual
fresh native result605,685 becomes664,795 after the59,110 adjustment. The native
building aggregation still adds125,288, producing790,083. GetBestDistrict's
comparison reads exactly790,083, against the control730,973. The stronger
1,019,221 candidate remains ahead. This is real reception with ordinary
competition preserved. The observed preference factor is1 in this case; the
evaluator's1.5 branch remains part of native policy when applicable.

`customer-native-early250-01` advances two ordinary turns, records no observer
faults, exits0 and restores ownership/preferences/packages. The packet contains
one diagnostic model bid; the main publisher is held only in this diagnostic.
Full outcome games will use integrated main-mod guidance alone.

For routine overlap handling, use a signed same-city/type difference against a
stable ordinary-preferred reference footprint. That retains native type-level
value and cancels common terms without an exact native component reconstruction.
Keep custom CSC receiving adjacency unless a specific native overlap is shown.
The full marginal in the transport diagnostic is not the proposed routine bid.
Bound the shortlist and check CE write/trace headroom. The routine implementation and recurring budget are described below.

The early path preserves native invalid sentinels, but permits valid negative
raw scores. A routine negative differential should account for the aggregation
gate at zero: crossing it can remove the common positive building subtotal.
The existing read-only site quote exposes `netQ8`, so this boundary can be
checked without inventing a new native reader API. Cache changes follow native
reevaluation; existing request maxima retain their ordinary lifecycle.

This slice changes AI facts/pricing only. It changes no gameplay payout, building
availability, transaction rate or material gate. Earlier definition migrations
and preview corrections retain their separate gameplay QA lists. The final goal
handoff will consolidate those lists for Henno.


## Routine Problems1/2 integration and performance

The main CSC adapter now computes signed customer-site differences against a
stable ordinary-preferred reference in the same city/district type. It includes
unlinked alternatives, so a useful linked reference can also demote a less useful
site. The adjustment preserves native type-level value and the positive raw-score
gate for ordinary building aggregation. Same-key spatial, protection and economic
entries are merged before publication; the transport remains the qualified early
Entry API. Actual construction remains native competition.

New Quarter candidates now use the same before/after player economy as existing
customer sites. Worlds account for covered suppliers, actual Core adjacency,
customer/provider links, shared physical buildings, queues, population rounding,
observed staffing and the relevant observed route network. Only the proposed
Quarter receives its calibrated missing-building depth premium. Its own stream
list is kept for purchase/displacement diagnostics. Joint-world supplier losses
replace the duplicate economic SupplyValue deduction; the explicit policy floor
against covering a Quarter's own materials remains.

A global search at every candidate was too slow in the mature save. The first
policy-only two-pass check took1.85/21.66/36.69/91.57/48.56 host seconds across
players1–5. These include console/source loading and are not per-turn guidance
measurements. Keeping unaffected discrete investment choices, reconsidering
shared customer investments, and limiting customer worlds to16/player/publication
reduced those values to1.82/6.36/14.91/13.66/15.63. Every candidate still recomputes
queue times, physical building deduplication, pooled amenities and rounding.

The publication now observes only routes touching its own cities, retaining
foreign endpoints and currently ineligible routes that may activate. It shares
at most128 distinct route timelines. Chronological no-op events are normalized
only after validation; restoration, explicit route removal, incoming foreign
routes and32-contributor wrap behavior remain covered. This lowers the third
host two-pass check to1.83/2.60/3.94/3.61/4.21 seconds. Quarter offers stay2/6/1/6
for players2–5 and economic customer offers6/3/5/8. All three replays exit0 and
restore their sessions. The third replay's route cache hit/miss counts are
194/18,462/27,440/30,545/39, with no overflow or unknown/budget failures.

The native clock build is now
`b7194a83569283033a7c9687ae6d92c33cef7b7d04daaf8e115c641077cd7da9`.
It adds only a read-only steady clock to CE;251 native checks and four hook-layer
checks pass. Precise mature-save qualification `integrated-policy250-04` passes: cold/warm
planning totals across five players are3,851.612/3,489.519 milliseconds. These
cover the diagnostic planning calculation; complete publication overhead is
measured in the upcoming full games. The zero-turn replay closes/restores0. Main-mod timing
records include the complete publication, per-player partitions and cumulative
managed native refresh. Full runs automatically write average/max and coverage
to `ai-processing-time.json`; [measurement details](../../civ6-ai/performance.md).
123 economy tests,82 transaction tests and16 timing/controller/packaging tests
pass. Astra approves the bounded route memo and timing approach; the packet-version
attribution guard from that review is included. Three fresh
Online250 outcome games remain the next integration evidence.

These routine changes alter AI calculation and observability only. Gameplay
payouts, transaction eligibility and building availability are unchanged by this
slice. Earlier contract migrations retain their documented manual QA cases.


## Architecture review before outcome analysis

Astra's final read-only review confirms the major ordinary economic channels,
shared definition authority, native competition and bounded work are represented
coherently. There is no ordinary-game blocker requiring interruption of the
pinned campaign. The proposed jointEconomy flag concern was checked against
committed571f381f line580 and retracted: the original site already receives the
returned quote's flag before final placement pricing.

The handoff limits are intentional: customer guidance adjusts siting while native
type-level demand remains; local search freezes distant discrete investment
choices while recalculating their consequences; future staffing, route renewal
and prospective placement Services are not invented. Cached reevaluation and
retained request maxima keep their native lifecycle. Efficacy and complete-run
overhead await the three outcome games.
