# Joint customer economy: shared ledger foundation

16 November2026. Ordinary-economy goal G3; roadmap1.4/2.1/2.2.
The pure joint evaluator is implemented and regression checked. Live customer
facts, route/staffing integration and the native residual remain open.

## What this changes

`CSC_AI_EconomyModel.JointForecast` evaluates an explicit affected world rather
than adding independent Quarter quotes. Each investment and city queue uses
`owner:city:building`; each population accumulator includes owner, recipient city,
yield and native property. Two Quarters can fund one Market and prerequisite.
Its completion enables every eligible relationship automatically.

The before-world is the existing economy. Only the after-world reserves the new
district's queue time and changes footprints/venues. Both worlds are passed as
plain facts to `JointCustomerForecast`; the evaluator issues no game operation.

```mermaid
flowchart LR
    Facts[Complete affected-world facts] --> Before[Existing economy]
    Facts --> After[Candidate economy]
    Before --> Shared[Shared investment and city queue scheduler]
    After --> Shared
    Shared --> Edges[All eligible automatic exchange legs]
    Edges --> Pools[Pool population targets before Q8 rounding]
    Pools --> Price[Native price adapter]
    Price --> Delta[Joint marginal ordinary value]
    Delta -. remaining G4 .-> Residual[Subtract native CSC overlap and deliver residual]
```

Population flows retain their investment contributors. A pooled stream does not
inherit the last contributor's building type/depth premium. Allocation of that
premium remains part of native attribution/calibration; raw shared income is
already computed. Single-Quarter consumers keep their previous stream identities
and pricing behavior.

## Planning and failure behavior

The search tries minimal and all-enabled seeds, then at most two deterministic
coordinate sweeps per seed. The second seed admits shared-cost opportunities
where neither producer alone can cover a customer building's upkeep. Optional
customer choices disable a unique physical investment globally; relationship
edges are immutable. Mill alternatives and Stage3/4 subsets retain physical
existing owners. Identical stage alternatives are deduplicated.

The default limits are64 affected chains and512 complete evaluations. Exceeding
a limit returns unavailable, including after a promising partial search; no
truncated quote is published. Missing owners/cities, conflicting copies of a
shared investment and inconsistent population contracts also return unavailable.
The caller must supply the complete affected closure and observed facts; the
evaluator cannot establish coverage from a partial list by itself.

## Regression evidence

Production Lua tests cover:

- One shared Market/prerequisite, one upkeep charge, one city queue.
- Shared payout rounding once, including differing completion times.
- Input-order stability and owner/city-specific depth attribution.
- The candidate's queue delay only in the after-world; Services excluded.
- Two individually losing producers funding a profitable shared Market.
- All automatic links retained after the shared customer is chosen.
- Owner/city collisions, contradictory facts and explicit work-budget failures.

Astra found the shared-investment and deleted-edge cases during review; both
are retained as regression tests. Tests live in
`project/tools/ai_economy/test_joint_customer_economy.py`.

## Remaining integration

Build `CustomerWorld` from the actual candidate and the full connected closure
of Quarter/customer queues and population recipients. Include footprint material
loss and direct/provider adjacency changes. Snapshot actual routes once,
including foreign origins; value only this player's receipts and preserve import
loss when its own Quarter becomes functioning. Share a small gameplay-owned
channel evaluator with the route scanner, preserving five-bit count wrapping
and the existing Bakers/Tailors source-gate difference. Read ordinary specialist
amounts from citizen-yield definitions and credit only observed workers.

Then measure existing native CSC forecast components, apply only the residual at
the qualified boundary, and measure mature-empire overhead. No new live customer
residual is enabled by this foundation; native SQL placement preference stays1.
