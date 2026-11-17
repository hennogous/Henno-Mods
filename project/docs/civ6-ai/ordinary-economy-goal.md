# Ordinary-economy implementation goal

**Continuation status, 17 November:** no active goal; further games stopped at
Henno's request. One integrated Continents 250 game and its analysis are complete.
Pangaea stopped at verified 75; Fractal unstarted. Read the [handoff](HANDOFF.md)
before treating the implementation sequence below as new work.

Updated 17 November 2026. The numbered roadmap remains the spine: Problems
1.1–1.8 (worthwhile Quarter placement and follow-through) and 2.1–2.2 (related
district placement and material protection). Support Bakers and Tailors through
shared mechanisms that can extend to future Quarters.

The goal is a reasonable reflection of the major gameplay-defined economic
channels. Reuse completed migrations and working guidance. Read materials,
partners, buildings, amounts and eligibility from gameplay definitions; named
tuning weights and documented forecast assumptions remain appropriate. Adapt
gameplay only where a demonstrated bug or missing shared contract requires it.
Exact vanilla component parity and exhaustive edge-case qualification are not
completion requirements.

Represent adjacency, material exchanges, producer/customer transactions,
population scaling and relevant observed trade/staffing. Prospective Service
valuation remains deferred. Keep ordinary district value and native competition,
and avoid materially duplicated income or inflated bids.

Next sequence: fix short-interval pricing; demonstrate one representative
customer-site evaluation consumed by a native comparison; integrate remaining
major placement/protection channels; then run three fresh stock-AI Online games
through turn250 using only main-mod tuning and the shared controller, with
15-minute checks. Report placements, materials, customers, buildings, Services,
baseline comparisons and practical overhead. Finish with exact gameplay changes
and a focused manual QA checklist for Henno. Subsequent Problems3–6 research is
outside this goal. Consult Astra at meaningful checkpoints and maintain comments,
roadmap, reusable engine findings and scoped commits/pushes.

Performance is a release requirement. The next and subsequent full games must
report average/max guidance processing time per turn across all AI players,
per-player breakdowns and slowest turns, with explicit clock coverage.
See [measurement scope and bounded work](performance.md).

The G labels below track implementation dependencies within Problems1 and2;
they do not replace or expand the numbered roadmap.

| Requirement | Completion evidence | Current state |
| --- | --- | --- |
| G1 Fixed external/local exchanges | Gameplay-owned headers/legs and native gate templates; UI/AI readers; baseline graph parity, replacements/alternatives/amount tests | Verified: corrected replay matches all10,954 native rows,137 fixed rows and67-city population refresh; closed/restored |
| G2 Directional materials | Data-owned inputs/returns, registered hosts, Base/Spec, M&C2/3 totals, ownership/worked/pillage behavior, protection consumes actual legs | Verified: Gold/M&C graph parity, end-to-end protection/owner tests,30 live lifecycle observations and final current-reader22-chain smoke pass; native10,954-row graph unchanged |
| G3 Joint customer economy | A coherent shared model covers affected suppliers, adjacency/provider changes, shared queues/rounding and observed routes/staffing | Implemented and exercised in completed Continents 250. 22 Base-adjacent foundations; strong Bakers outcomes, Tailors customer/investment coordination remains the clearest gap. Prior mature-world, graph and interval-quote checks remain valid |
| G4 Native residual | Representative overlap check avoids substantial duplication; correction retains ordinary district value and is consumed by a native comparison | Representative matched transport qualified. Completed game records customer writes/native comparisons and82/82 exact Quarter BEST receipts; continue outcome/calibration audits without reopening transport as unimplemented |
| G5 Bounded work | Definition caches, targeted updates and measured mature-empire overhead | Bounded searches/caches implemented. Complete250-turn clock coverage: average2.03s/max4.61s across five AIs, last50 average2.98s. Repeated economic pricing still needs profiling |
| G6 Review and handoff | Astra review, maintained findings/roadmap/skill, scoped pushes, exact gameplay change list and manual QA cases | Ongoing |
| G7 Three250-turn efficacy games | After G1–G6, run integrated-only stock AI games on Online speed through shared controller;15-minute checks; regular placement, chain, Service and economy comparisons | Incomplete and stopped by Henno: Continents250 analysed, Pangaea interrupted at75, Fractal unstarted. Do not resume without instruction |

## Fixed slice

Nine concrete relationships: alternative Water/Wind Mills to Granary/Bakery/Café,
and Workshop to Lighthouse/Tailor/Fashion House. Preserve native ownership per
leg, functioning-customer checks on outward wrappers, narrower reverse wrappers,
city scope for local yields, and one selected Mill. Recipient building and enabling
investment are separate model metadata. Shared leaf identities reject conflicting
terms. The material migration now checks the shared Café Food leaf against both
catalogues; conflicting amounts or recipients fail generation.

The first native qualification caught a generator defect: REPLACE of shared
Requirements/RequirementSets cascaded deletion into native dependents. The source
now uses stable INSERT/UPDATE and creates gates before dependent modifiers.
New enforced-FK tests preserve unrelated Service siblings and shared memberships.
The replacement check now compares every CSC native effect row against a fresh
original-package baseline, rather than just fixed aliases. Failed attempt closes
and restores normally; no turns or saved-world changes are retained.

## Material slice

Do not collapse native input hosts and output eligibility into a symmetric rule.
The audited input root is registered on improvement types and gated by material
tag plus adjacent owned Quarter. Ordinary return wrappers target tagged player
improvements without an explicit valid-resource-pair requirement. M&C inputs are
full2/3; returns are ordinary1 plus increments1/2. Preserve existing late ordinary
host reconciliation after CL/R2 definitions. Observe native pillage lifecycle
separately from explicit SQL gates, and record which city actually works a plot.

## Native/customer slice

17 November route slice: native SQL projection/shared kernel now drives the
scanner/previews. The67-city zero-turn replay matches packets and all10,954
native rows;43 route operation start times qualify. Route events, aggregate
amenity counterfactual pricing and live affected-world integration remain G3
work; no customer residual is enabled by this slice.
[Evidence and exact preview changes](../research/mods/csc-observed-routes-20261117.md).

The engine adds a shared city/type building subtotal to positive customer-site
cells. Preserve that ordinary valuation and identify existing CSC contributions
before adding a site-dependent residual. Keep native SQL placement preference1
fixed during calibration. Do not sum independent Quarter projections when they
share a customer, prerequisites, queues or a rounded payout property.

Relevant artifacts live under
`C:/Users/Shadow/Desktop/Codex/csc-ai-ordinary-economy-20261116`.
The prior QA baseline is60b51107; the qualified population migration isdbcc0864.
[Economic contract](../integrations/csc-economic-contract.md).
