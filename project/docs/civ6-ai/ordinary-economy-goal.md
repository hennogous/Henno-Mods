# Ordinary-economy implementation goal

Active16 November2026. Scope: Bakers/Tailors, roadmap1.4/2.1/2.2. Services stay
deferred. Human in-game QA and the later long-game evaluation follow this goal;
agent implementation, regression, native reception and performance checks precede
handoff. Keep the full scope below until every item is verified.

| Requirement | Completion evidence | Current state |
| --- | --- | --- |
| G1 Fixed external/local exchanges | Gameplay-owned headers/legs and native gate templates; UI/AI readers; baseline graph parity, replacements/alternatives/amount tests | Verified: corrected replay matches all10,954 native rows,137 fixed rows and67-city population refresh; closed/restored |
| G2 Directional materials | Data-owned inputs/returns, registered hosts, Base/Spec, M&C2/3 totals, ownership/worked/pillage behavior, protection consumes actual legs | Audited; implementation and native lifecycle probes open |
| G3 Joint customer economy | All adjacent suppliers evaluated together; adjacency/provider changes, shared queues/rounding; observed routes/staffing; no duplicate costs | Open |
| G4 Native residual | Component attribution measures CSC overlap; late delta retains native ordinary district value; received/compared in bounded matched replay | Open |
| G5 Bounded work | Definition caches, targeted updates and measured mature-empire overhead | Fixed argument cache restricted; full measurement open |
| G6 Review and handoff | Astra review, maintained findings/roadmap/skill, scoped pushes, exact gameplay change list and manual QA cases | Ongoing |

## Fixed slice

Nine concrete relationships: alternative Water/Wind Mills to Granary/Bakery/Café,
and Workshop to Lighthouse/Tailor/Fashion House. Preserve native ownership per
leg, functioning-customer checks on outward wrappers, narrower reverse wrappers,
city scope for local yields, and one selected Mill. Recipient building and enabling
investment are separate model metadata. Shared leaf identities reject conflicting
terms. The material-unit guard on the shared Café Food leaf remains until G2.

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

The engine adds a shared city/type building subtotal to positive customer-site
cells. Preserve that ordinary valuation and identify existing CSC contributions
before adding a site-dependent residual. Keep native SQL placement preference1
fixed during calibration. Do not sum independent Quarter projections when they
share a customer, prerequisites, queues or a rounded payout property.

Relevant artifacts live under
`C:/Users/Shadow/Desktop/Codex/csc-ai-ordinary-economy-20261116`.
The prior QA baseline is60b51107; the qualified population migration isdbcc0864.
[Economic contract](../integrations/csc-economic-contract.md).
