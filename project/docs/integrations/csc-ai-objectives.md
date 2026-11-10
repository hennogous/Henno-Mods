# CSC AI objectives

Agreed direction, 6 November 2026. The AI should build and sustain worthwhile
supply chains across all eight Quarters and their associated base-game and
optional-mod elements. The current Bakers Stage 2 milestone qualifies CSC
with stock Civ VI AI. After that milestone, assess the worker and other AI
support RHAI5 provides before deciding what to adapt. Activate family-specific
decisions as their gameplay becomes available.

CSC owns the value of its supply-chain relationships. Civ continues to choose
among eligible actions, apply its strategic priorities and manage commitments
and budgets. Success means functioning chains and realised empire benefit
after costs, including displaced alternatives. Adjacency, construction and
Service activations are useful intermediate measures.

## Decisions to support

| Decision | CSC contribution |
| --- | --- |
| Quarter siting and land | Prefer a viable adjacent Base source and ideally both Base and Specialty. Value the Quarter's actual river effects and customer or City Lights goods-provider links. Count future neighbors only where a specific legal footprint exists. Prefer combined adjacency around +4 and above, discourage individual sites with missing or destroyed supply-chain links, and support a worthwhile affordable tile purchase through native planning. |
| Other districts | Value adjacency to existing or credible future provider Quarters. Prefer safe sites over mapped Base or Specialty deposits, improved or unimproved. Protect the last viable deposit of either class per Quarter, with particular urgency when the last working supplier sustains a Service. Price the opportunity cost of shifting an otherwise good native district. |
| Material work and Builder supply | Prioritize Base improvement once its Stage 2 buyer is working, and Specialty once its Stage 4 buyer is working. Prepare necessary technologies in time. Give the actual job to a reachable Builder with charges, including from another city. Value another Builder when useful jobs exceed available capacity. |
| Stage 2 producer | Value its technology or civic and construction when two or more viable Base materials are adjacent. One viable Base can still support a worthwhile producer. |
| Stage 2 customer | Value the mapped building in an adjacent customer district. Respect applicable unique replacements. |
| Stage 3 producer | Favor the unlock from population 7 and construction from population 10, subject to the investment's expected return. |
| Stage 3 customer | Value the mapped building in an adjacent customer district. |
| Stage 4 producer | Favor the unlock from population 7 and construction from population 10 when a viable Base and Specialty deposit are both adjacent. |
| Stage 4 customer | Value the mapped building in an adjacent customer district. For a Wonder, value a legal adjacent footprint beside a Quarter with the required materials. |
| Stage 2, 3 and 4 Services | Favor research or civics when the applicable material, working producer and customer requirements are ready. Combine contributions from distinct chains. Eventually weigh Service outcomes by empire needs and victory direction. |
| Quarter investment and trade | Compare weak local Quarters with the same-family import benefits they could displace. Value trade routes to supplied Quarter destinations when the origin qualifies and can use the benefits. |

The adjacency, material-count and population thresholds are starting
preferences. Eligibility follows the actual game rules. Distinguish mapped
deposits, viable supply, working improvements and material-dependent effects.
Ordinary building exchanges and sales can have different gates from Services.
Use enabled game data, including compatible resources, unique replacements
and optional City Lights providers, rather than generic resource categories.

## Care and trade-offs

- Restore pillaged material improvements, Quarters and customer assets when
  restoring the chain is worthwhile. Replan after capture or lost supply.
- Protect critical deposits from harvest and other destructive work as well as
  district placement. Track viable and working supply separately. A single
  footprint can affect multiple Quarters, and two plans can compete for one
  customer tile.
- Compare finishing or repairing a chain, opening a new one and deferring.
  Account for land purchase, construction, upkeep, unlock time, Builder travel
  and charges, and other uses of scarce production and treasury.
- Preserve the standalone merits of shared base-game assets. Add a bounded CSC
  relationship benefit or cost. For CSC's own Quarters and producers, compare
  coarse adjustments with complete custom valuations as the decision is
  qualified. Validate the native consumer, eligibility, timing and scale.
- Treat last-material protection as a distinct policy from normal adjacency
  scoring. A finite bid penalty can discourage an otherwise legal placement.
  Guaranteed protection requires a separately qualified eligibility rule.

## Evidence of progress

Verify candidate delivery, actual choice, execution, retained supply and
economic benefit separately. Compare site quality, time to first operation,
working supply and Service turns, costs and displaced opportunities against
matched untuned CSC. For later RHAI5 work, use a reference with the same RHAI5
configuration. Track performance per turn as well as choice and outcome.
A first useful improvement can ship with coarse bid bands and limited family
coverage, provided its decision path and scope are verified.

See the [implementation roadmap](../civ6-ai/roadmap.md) and the
[baseline and evaluation handbook](../civ6-ai/topics/csc/objectives-and-baselines.md).
