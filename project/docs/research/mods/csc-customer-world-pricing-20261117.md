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

## Next dependency and gameplay QA

The next diagnostic records the ordinary pre-aggregation score and the exact
candidate value read inside native GetBestDistrict, then tests one guarded late
adjustment in a matched replay. Shipping customer residuals and their recurring
budget remain implementation work. These sampled quotes have not yet been
published as routine policy.

This slice changes AI facts/pricing only. It changes no gameplay payout, building
availability, transaction rate or material gate. Earlier definition migrations
and preview corrections retain their separate gameplay QA lists. The final goal
handoff will consolidate those lists for Henno.
