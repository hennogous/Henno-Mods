# Community native AI job routes —30October2026

Primary references supplied by Henno:
- https://cru121.github.io/civ6-gamecore-reference/ai-behavior-trees.html
- https://cru121.github.io/civ6-gamecore-reference/ai-contracts-and-operations.html

Current pages were retrieved successfully over HTTPS after the web reader failed.
Snapshots/hashes are in H/community-ai-pages-20261030/receipt.json. These are
external reports, including author-reported live tests, not locally replicated
CSC results. Old RVAs and platform layouts still require current-build checks.
No game, source gameplay change or sample-mod installation accompanied review.

## New practical route

The behavior-tree page reports a mod-authored tree reaching native execution and
calling a Lua GameEvents condition. Its handler sets targetInfo.Extra; a normal
Lua return alone is not the documented result channel. Tree definitions need an
activation route. The author's gain-tech test only ran after removing the base
trigger; the event has a single slot and competing-trigger precedence remains
uncertain. Never transplant that test override: it disables ordinary upgrades.

For CSC, the vocabulary suggests native requests for producer buildings and
material jobs, with availability, recruitment and reservation stages. This is a
research lead, not evidence that custom supply-chain execution or preservation
already works. Reservation lifetime, release and interactions remain unverified.

The operations page reports Lua-supplied target coordinates, recruitment,
production requests and some movement through an authored operation. Default
attack-tree nodes caused immediate completion for scripted targets; changing
the tree enabled recruitment, but frequent movement failures remained unexplained.
Its demonstration recruits combat units toward a shared map-center goal; it is
not a validated Builder/material workflow.

Both reported callbacks received empty context tables. Identifying the evaluating
AI/city and passing a specific economic job are unresolved for our intended use;
do not substitute local observer identity. Lua target activation, a native request,
movement, completed work and beneficial retained supply remain distinct evidence.

## CSC follow-through

Add a separate native-goal/provider route to the roadmap: shadow planner selects
an evidenced economic opportunity; a validated interface could submit it to
native execution. First inspect shipped scenario usage, callback context and
current-build data bindings. An isolated future test should prove correct AI/
city/target identity and one request's lifecycle before any production policy.
Avoid RH trigger collisions, recurring operation spam, forced Lua unit orders
and replacement of unrelated AI behavior. This does not authorize a new test.

Our selected UnitRequest initialization/validation/execution paths already have
deeper local native evidence than the companion page's general lifecycle sketch.
Combine that with these activation findings; do not discard stronger local proof
or assume the whole native job system is newly understood. The repaired one-city
shadow collector remains unvalidated and these resources do not change its result.
