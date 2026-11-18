# Prospective Service pricing: native mechanisms and CSC forecasting

18 November2026. Roadmap14.3, applying initially to Quarter investment1.4.
Source/maintained-native-evidence audit; no game, gameplay change or new hook.

**Use CSC to forecast a Service's recipients, activity and timing; use native
pricing wherever the engine has a suitable consumer.** Existing CE yield and
amenity quotes already give native Q8 utility. We need a small set of additional
effect quotes and bounded proxies, rather than one arbitrary bonus per Service.

## Available and missing pieces

| Effect | Practical pricing route | Current evidence/status |
|---|---|---|
|Ordinary additional Food/Production/Gold/Faith/Culture/Science|Existing `CE_AIYieldIntervalValue` with recipient, amount and start/end|Integrated and qualified, using native weights and timing|
|Amenities|Existing `CE_AIAmenityIntervalValue` with pooled city changes|Integrated; nonlinear thresholds require a joint before/after quote|
|Growth percentage|Expose the native city-growth child, compare with the existing Food-surplus proxy|AI-N105 establishes native Food-surplus input and timed valuation; no dedicated current adapter call|
|Great Person points|Expose a type-specific native GPP quote|AI-N105 establishes player pseudo-yield weights and timing; not yet a Service placement input|
|Housing|Trace the existing housing valuation path with recipient context, then expose if usable|Native district/building scoring includes housing; the Service root's zero result did not identify a useful child quote|
|Naval production percentage|Forecast eligible ship work, price the marginal saving/production through native Production pricing; inspect direct unit-production valuation if useful|Current narrow Stage2 proxy uses observed eligible ship production; prospective demand is still needed|
|Tourism|Investigate another native valuation route/weight; otherwise use a calibrated proxy|Measured modifier traversal lacks the Tourism effect analyzer; generic yield pricing is not automatically Tourism pricing|

These quotes do not require applying an effect or granting a hidden building.
Quoting a whole native future-building total would combine unrelated benefits
and unreliable gate interpretation. Prefer the individual effect consumers.
All new CE wrappers require current-binary verification, bounded arguments and
the existing CE API conventions; no upstream PR is authorized.

## Current implementation boundary

`CSC_AI_EconomyAdapters.lua:rawPrice` already prices `GROWTH` as positive current
Food surplus times the percentage, converted to a Food stream. It prices
`NAVAL_PRODUCTION_PERCENT` against observed eligible ship work, with a short
window. These are explicit proxies passed through native yield pricing.

The single-chain model has gated Stage2 Service streams, but the placement
adapter clears `transactionSite.service`; joint planning also clears
`site.service`. Customer worlds deliberately exclude Services too. Adding a
price helper alone will therefore have no effect on current spatial bids.
Service streams must become part of the common joint-world comparison.

Native modifier forecasting cannot supply the whole CSC chain forecast. It has
known collection/requirement omissions; some Service roots returned zero before
reaching their child. AI-N105 separately establishes usable growth and GPP child
arithmetic, byte-matched for reference324c51e9 and current092abfbb. Reuse that
arithmetic without inheriting incorrect chain eligibility.

## Recommended implementation sequence

1. Inventory actual Service effects and gates from gameplay registrations,
   modifiers and arguments. Reuse amounts there. Add explicit metadata only
   where recipient/effect relationships cannot be recovered reliably; avoid a
   second list of amounts, customers or material classes.
2. Add Service records to the common world ledger: actual beneficiary, supplier
   and buyer prerequisites, unlock/readiness, amount, demand and useful lifetime.
   Evaluate **with candidate minus without candidate**, including shared links,
   existing active benefits, disabled effects and actual stacking rules.
3. Start with readily priced effects: Faith/yield percentages and GPP, plus
   growth. Verify native growth/GPP quotes and compare against a small selection
   of ordinary native investments. Housing and Tourism need their own consumers
   or calibrated proxies. Dockmaster needs credible eligible naval use.
4. Feed the marginal Service utility into the existing complete Quarter bid.
   Keep economic value separate from investment weighting. Do not automatically
   apply the ordinary future-building depth multiplier to every Service.
   Preserve material guards and ordinary district/production competition.
5. Validate recipient/gate/stacking cases and zero demand, then short matched
   bids around close and strongly superior ordinary alternatives. Full games
   should compare forecast Service opportunities with actual activation and use.

Future customer footprints can support an explicitly scheduled prospective
Service; mere free space is not a guaranteed customer/building. Missing links
need credible costs and delays. The previous campaign's seven producer/supplier
gaps make this timing material to investment quality.

Bound recurring work: cache the static Service catalogue, reuse existing world
plans, group identical recipient/effect/time quotes per publication, and omit
out-of-horizon/zero-demand effects before native calls. Retain the existing
bounded candidate search. Measure added time on mature saves before full runs.

Sources: [roadmap14.3](../../civ6-ai/roadmap.md),
[native pricing implementation/evidence](csc-ai-native-valuation-20261115.md),
[corrected interval quotes](csc-customer-world-pricing-20261117.md),
[forecast coverage](../../civ6-ai/topics/csc/forecast-coverage.md), current
`CSC_AI_EconomyFacts.lua`, `CSC_AI_EconomyModel.lua`,
`CSC_AI_EconomyAdapters.lua` and the installed civ6-ai engine findingAI-N105.
