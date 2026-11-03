# Offline Quarter evidence evaluator — first bounded version

`site_evaluator.py` is a pure Python fact evaluator for Basic and RH opportunities.
It performs no file reads/writes, native calls, game imports, purchases or tuning.
The caller supplies explicit snapshot facts. `evaluate_site(site, mapping)` returns
review evidence, never permission to place or spend. `current_dominance(a, b)` is
conservative local Pareto evidence; `archive_coverage(casepack)` adapts the closed
28 October casepack without inventing Quarter sites.

## Evidence contract

An observed field uses `{ "value": ..., "source": "file SHA / JSON pointer" }`.
Missing value or source is unknown. Numeric booleans/nonfinite values are invalid.
Use the synthetic test constructors for a compact complete schema example; their
identifiers, zero costs and measured yields are fixtures, not game observations.
Identity includes player, city, turn, plot and source. The input is retained in
the result alongside mapping provenance so every reason can be traced.

Mappings must be an explicitly validated, enabled snapshot: `validated` evidence,
`snapshot` identity, `quarter_classes[quarter]` with Base/Specialty tag names,
`TypeTags` rows (`Type`, `Tag`, `source`) and `Improvement_ValidResources` rows
(`ResourceType`, `ImprovementType`, `source`). The evaluator validates this
envelope, not the database extraction. Do not set validated=true on guessed
relations. Optional resources work through rows rather than resource-name rules.
Current mapped supply needs adjacent, working, valid improvement evidence, explicit supply_eligible native-bound evidence, and supply_context evidence matching player/city/quarter. This eligibility must cover ownership, pillage, and the actual native city supply gates; adjacency alone is insufficient.
Footprint materials are listed as lost and never counted as retained supply.

Current real candidate adjacency is explicit `YIELD_PRODUCTION` and `YIELD_GOLD`
evidence. These are real post-placement components; callers must not insert
private placement units, native scores or material/Service potential as yields.
River and existing customer facts remain visible separately; no hidden conversion
from flags to economic yields occurs. Missing P/G stays unknown, never zero.
Built stages and customer buildings remain separate from supply and Service
activation. Both supply is option potential; active Service is unassessed.

Every site and future plan requires legal, unlocked, accessible,
capacity_supported and affordable evidence. Site false gates are infeasible;
unknown gates require more evidence. Future false/unknown gates withhold that
proposal rather than reject an otherwise currently legal site. Each future plan
has a specific plot, positive estimated delay, source, kind (`material` or
`customer`), and nonnegative marginal real P/G increments. Material proposals
also need resource/improvement mapping, adjacency, and a unique sourced matching resource on that plot in the observed material inventory; customer proposals need
mapped-customer evidence from a validated customer/replacement mapping plus explicit adjacency. This
first module takes that mapping fact as input; it does not extract database rows.
Every duplicate future plot and footprint conflict is withheld symmetrically.

Costs require evidenced acquisition Gold, own Gold, subsidy Gold, production,
Builder charges, travel turns, maintenance, lost tile value and district capacity
used, for both the foundation and each future step. These fields retain distinct
units; lost_tile_value is a caller's explicit comparable opportunity measure,
not an inferred Gold price. A known zero needs provenance. No ROI is computed.
The caller must document estimate/fresh-price status and units in sources.

## Recommendation semantics and limits

Review categories distinguish infeasible, insufficient evidence, tradeoff,
marginal and promising opportunities. Descriptive combined +3/+4/+5 bands retain
P/G components; they are not approved purchase thresholds. Both-or-combined
potential can trigger promising review only after full evidence coverage. Future
credit is explicitly delayed/conditional and reported separately; no invented
numeric discount is calibrated here. `credible_future_increment` is only the
known subset; `future_total_increment` is null when any proposal is withheld.
The projected band describes this subset, never the unknown total or an active
chain. Arbitrary future increments are not independently verified by this module.

Existing unfinished chains, build commitment, footprint loss and valued customer
alternatives force explicit comparison. The evaluator preserves their evidence
and defers tradeoffs instead of choosing an arbitrary utility coefficient. It
does not yet compare start versus finish/repair returns, enforce an empire budget,
coordinate separate sites, model shared customers, predict native behavior or
authorize backend integration. Supply absence in an incomplete inventory cannot
establish no opportunity. It does not recommend a quota or district spam.

Pareto comparison is deliberately narrower than net chain benefit: same player,
city, turn, Quarter, mappings, supply, future plans and chain context, no unknowns
or rejections, no worse current P/G or evidenced costs and at least one strict
improvement. It returns undetermined when relevant context differs. Equal Gold
does not establish equal sites; Production and all cost dimensions still matter.

## Archived coverage and validation

The real `csc-native-ai-analysis-20261028/offline-chain-cases.json` casepack has
Coimbra Harbor alternatives, Rice1087 repair need and the Maize1863 commitment
case. It lacks a validated enabled mapping snapshot, complete current Quarter P/G,
future feasibility/capacity/delay and whole-chain costs. The adapter therefore
evaluates **zero complete Quarter sites** while preserving actual cases and source
hashes as coverage evidence. No claim of archived +4 validation or native policy
improvement is supported. A complete archived capture is still needed before
connecting to the guarded backend.

Validation: 21 synthetic scenario/integrity tests exercise strong/marginal/illegal,
private-versus-real/missing yields, current versus future, unavailable capacity,
unknown access/costs, conflicting future plots, lost Base footprint, unrelated
mod resources, validated mapping gates, Both option versus Service, valued
customer/existing-chain alternatives, conservative dominance and input purity.
Run with `python -B -X utf8 -m unittest -v test_site_evaluator test_offline_cases`
from this folder. Synthetic success establishes implementation behavior only.




## Additional real archived cases (29 October)

`archived_site_cases.py` evaluates three explicitly partial records from Basic A
turn 100 against that archive's database mappings. See its adjacent tests and
`Desktop/Codex/csc-ai-next-step-20261029/archive-review/archived-site-cases.json`.
Two are actual-AI existing chains; one original-human candidate is retained only
as an excluded negative control. All three are insufficient for a new-placement
recommendation, with zero complete or ranked sites. This is deliberate evidence
coverage, not evidence that those sites are bad.

The negative control's unimproved Flax is occupied by a City Center, so its future
Farm is rejected. Meroe's Tailors has owned, unpillaged mapped material improvements;
Lisbon's Bakers has pillaged material improvements. Existing district GetYield
totals are retained separately and never used as new-site adjacency forecasts.

Run all three suites with `python -B -X utf8 -m unittest -v test_site_evaluator
test_offline_cases test_archived_site_cases`; 29 checks pass in the reviewed
version. The first policy remains an offline reviewer. Geometry quality and
execution readiness should remain distinct as capture coverage improves; an
unknown whole-chain cost must not be presented as zero or as proof of a bad site.


## Cross-site coordination — 30 October 2026

The first [offline chain coordinator](COORDINATOR.md) now wraps this evaluator
with existing-chain/request facts and explicit plot/dependency relationships.
It preserves unknown capacity and sharing, defers inconsistent duplicate starts,
and never authorizes or ranks actions. It is a reusable review layer, not a live
placement policy or evidence of native AI improvement. Production calibration
and complete candidate captures remain prerequisites for backend integration.

## Selective starts and attachment projection — 31 October 2026

`selective_planner.shortlist(sites, mapping)` is the first explicit offline trial
policy over this evaluator: stable sourced `configured_ai=true`, credible Base,
then Both potential or real combined P+G >=4 (configurable3/4/5). Unknown costs or
future feasibility defer; recorded commitments, footprint loss and valued customer
alternatives require comparison. Only conservative same-context dominated sites
are removed. The output is an unallocated investment shortlist, never an action.

`shadow_projection.py` reconstructs captured SelfBonus contributions per active
source building, preserving the SQL collection and source pillage state. The
closed source110 capture now matches11/11 existing controls. The shared preview's
boolean empire building presence missed stacking/pillage; the game source remains
unchanged. The failed native Plot preview is not promoted to success. Twelve real
captured alternatives lack adjacent Base; their investment facts remain partial.
See the [result and commands](../../docs/research/mods/csc-ai-selective-planner-20261031.md).

Run `test_shadow_projection` and `test_selective_planner` alongside the existing
evaluator/coordinator/reader suites. The new modules perform no native calls and
are not integrated into the live host. Credible future material improvement may
enable supply without adding resource adjacency again: avoid double counting.
