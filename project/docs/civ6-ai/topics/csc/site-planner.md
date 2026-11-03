# Explainable Quarter site planning

The fresh planner starts with an offline investment review. Its first Tailors
profile evaluates **44 copied historical cases**, with separate yield, cost,
timing, supply and customer explanations. It imports no retired tuning policy
and sends no native incentive. [AI-C048]

Read the [first review and actual case tables](../../../research/mods/csc-ai-site-evaluator-20261103.md).
Use the [interactive comparison](https://hennogous.github.io/Henno-Mods/ai/static/site-planner-review.html)
to change horizon, yield emphasis and reference construction costs on desktop or phone.
The [roadmap](../../roadmap.md) remains the current development plan; the
[objectives](../../../integrations/csc-ai-objectives.md) govern what counts as success.

## What can be reviewed now

| Comparison | Current treatment |
|---|---|
| Build at a captured new site | Compare valid producer bundles with defer |
| Develop an existing Quarter | Subtract retaining present benefits and sunk construction |
| Working versus unimproved material | Separate district adjacency from actual producer supply |
| Working versus unworked material tile | Supply can work; tile income needs citizen-working evidence |
| Existing customer versus missing building | Separate flat adjacency and building transactions |
| Future customer | A specific captured footprint with priced, timed conditional development |
| Future material improvement | An owned mapped footprint with explicit work cost, timing and conflict assessment |
| Repair or unfinished construction | Require repair/remaining-work inputs; do not make them free |

The model enumerates Workshop, Tailor and Fashion House bundles. Fashion House
requires Workshop, so Workshop+Fashion does not automatically pay for Tailor.
Ordinary sales remain distinct from Service supply gates.

## A concrete sensitivity result

The copied Kerma Quarter has functioning Base and Specialty supply, Workshop
and Tailor, and an adjacent Amphitheater. In the default reference-cost scenario,
Fashion House is ready after six turns. Over the remaining 74 of an 80-turn
horizon, its modeled incremental ledger is:

| Component | Modeled total |
|---|---:|
| Production |+148|
| Gold after additional maintenance |−74|
| Culture |+222|
| New construction |250 Production|

With review weights P1/G0.5/C1 this yields 83 assumed utility. At 40 turns the
model prefers retain; at 80 it favours reviewing Fashion House; at 1.5× unquoted
construction costs it returns to retain. This is a forecast under assumptions,
not an observed AI decision or measured profit.

The six captured new sites are tied on quantified present CSC relationships.
Three are near Dyes belonging to somebody else; no site has owned mapped supply.
One river edge does not meet Tailors' two-edge Production step. Future customer
spaces differ, but potential is not completed customers or immediate permission.

## What the first score does not establish

The score is **partial review utility**, never native Q8. Service values,
specialists, exports, growth/amenities, actual queue delays, alternative land
uses and empire priorities still need fuller valuation. Missing positive and
negative terms prevent treating the score as a bound on economic benefit.

Current and conditional effects remain labelled. The Base-supply planning
ambition is reported independently: positive conditional cashflow does not
qualify a new site without a credible Base path. Every output remains
non-deployable. Ordinary adjacency and costs already overlap native valuation;
feeding the whole review score into the extension would double-count them.

The copied worlds include earlier treatments. Comparisons stay within their
world/player/city identities. The Sydney native bridge result is not turned
into a site-quality case by joining another world's material catalogue.

## Simple full-adjacency policy

Henno separately requested a simpler first native policy: promote Bakers/Tailors
sites with at least +4 combined Production/Gold adjacency. Include every designed
adjacency source, including rivers and the appropriate first Bakers Mill before
it exists. This is a priority rule, not the offline investment utility above.
The [policy implementation and Online100 test](../../../research/mods/csc-ai-adjacency-policy-20261103.md)
record its mechanics, native bridge, interruption/recovery and observed results.
The Online100 game recorded52 native adjustments with no errors. All7 promoted
Bakers sites founded and completed;23 other Quarters founded below4 in their
preceding scans. No Tailors site qualified in this world. The machine interruption
and recovery are retained in the evidence, not treated as uninterrupted parity.
This is placement follow-through, not causal or economic-benefit proof. [AI-C049]
The richer investment evaluator remains available for later refinement.

## Discouraging weak sites

The [soft-penalty extension](../../../research/mods/csc-ai-placement-penalties-20261103.md)
keeps that good-site promotion and subtracts a graded priority from every observed
sub-4 Bakers/Tailors pair:65,536 Q8 per missing point, capped262,144. Multiple
district/tile entries can now share a city. These are experimental priorities,
not calibrated yield prices. Native negative scores can still win, and crossing
zero also removes the later future-building uplift. No unconditional poor-site
ban is added. The fresh Online100 test is in progress; source/host checks alone
do not establish a changed live placement or economic benefit. [AI-C050]

## Next decision

Review the assumptions and case explanations. Extend profiles to Bakers and
later Quarters, and gather only missing facts that could change a choice:
unlocks/costs, worked tiles, future customer permission, Services and competing
opportunities. Then derive the **additional** CSC value the native scorer does
not already represent, and test a genuine site choice through the existing
bridge and shared controller.
