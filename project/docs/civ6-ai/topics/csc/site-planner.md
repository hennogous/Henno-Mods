# Explainable Quarter site planning

## In-mod Stage 2 integration trial

CSC now builds a turn-local view of the loaded Bakers and Tailors
Quarter sites and their working suppliers. The model takes producer
and customer types from the Stage 2 gameplay registry, expands
building and district replacements, and keeps the two Service
unlock and property rules explicit. The publication starts once per
turn for original AI majors in single-player. It refreshes live
facts and caches the static relationships. The existing Bakers
calibrations remain scoped to Bakers. Tailors use smaller initial
nomination bands while their own calibration is pending.

The CE adapters publish the selected legal owned Quarter sites,
supplier deductions and work, building preferences and supported
repair requests. A modest missing-supplier bid can also compete
while a pillaged Bakers Mill awaits native repair. A separate CE
capability temporarily hides a protected owned plot during the
ordinary joint district selector. The original selector runs once.
The hook restores the original row eligibility before the native
winner goes into preparation. It leaves district scores, stored
reservations and later queue arbitration to the game. Alternate
placement consumers and requests already under preparation still
require their own protection checks. This capability is a local
CE build under review.

With the corresponding CE package present, CSC also loads one
private adjacency step from a mapped Quarter to a Stage 2 customer
district. It includes Harbor replacements and leaves City Centers
to settlement. No private yield is added to material plots. The
archived cross-city Builder request is restored with a 10-point
Builder preference where another mod has supplied none. These are
native database inputs, with no movement or gameplay yield bonus.
Private customer adjacency still needs separate human allocation
qualification.

The initial trial runs three ordinary Online-speed games to turn
200 with CSC and the corresponding CE package. The shared controller
records ordinary Lua publication, census and actual Storekeeper
effects. The trial uses no Frida, external policy or AI test action.
The Tailors Service property is reported separately from the native
Storekeeper effect audit.

## Earlier offline placement model

The fresh planner starts with an offline investment review. Its first Tailors
profile evaluates **44 copied historical cases**, with separate yield, cost,
timing, supply and customer explanations. It imports no retired tuning policy
and sends no native incentive. [AI-C048]

Read the [first review and actual case tables](../../../research/mods/csc-ai-site-evaluator-20261103.md).
Use the [interactive comparison](https://hennogous.github.io/Henno-Mods/ai/static/site-planner-review.html)
to change horizon, yield emphasis and reference construction costs on desktop or phone.
The [roadmap](../../roadmap.md) remains the current development plan; the
[objectives](../../../integrations/csc-ai-objectives.md) govern what counts as success.

## Stage 2 decision replay

The first Stage 2 replay reads the active material, producer and customer
registries from a copied gameplay database. The Bakers sequence covers site
preference, the eligible Mill, an adjacent Granary, exact Base improvement or
repair work, and the Feudalism goal when the remaining Storekeeper gates are
ready. The output distinguishes the last viable deposit from the last working
supplier and flags distinct jobs with known unmet Builder capacity. It includes
Specialty deposits in the protection ledger.

Synthetic state transitions exercise the sequence. The local gameplay database
verifies both Bakers and Tailors definitions, including Lighthouse and Naval
Tradition. Replaying the copied Kerma Tailors observation identifies its last
Flax and Silk suppliers and keeps its Amphitheater outside the Stage 2 customer
set. Proposal bands and protection flags are diagnostic outputs. A native
adapter still needs live facts, scale calibration and proof of the resulting
choice, assignment and completion. [Replay input and test commands](../../../../tools/ai_site_planner/README.md#stage-2-decision-replay).

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

The scanner now lives in the main CSC `Lua_UI/AI` folder with the late
correction library. It reads current material deposits and customer districts,
Tailors river-edge bonuses, and the prospective Water or Wind Mill for Bakers.
The experimental CE package can still copy this scanner for historical CSC
builds. The scanner measures adjacency for eligible owned plots. The +4 rule
turns that measure into an experimental priority.

## Customer geography and readiness

For effects that require adjacency, first establish that the customer's
district occupies a neighboring tile or has a specific legal neighboring
site. Then value the relationship according to its actual state.

| Customer state | Forecast treatment |
| --- | --- |
| Functioning building in an adjacent qualifying district | Use the actual recipient and population. The stream starts when both sides can operate. |
| Adjacent qualifying district with a missing, unfinished or pillaged building | Treat the benefit as conditional on the building's unlock, remaining cost and delay. |
| Specific legal neighboring site for a future customer district | Price the district and then its building. Compare competing uses of the footprint and avoid counting several alternatives on the same tile. |
| No qualifying adjacent district or credible legal site | Adjacency-dependent customer value is zero for that branch. |

The offline Tailors planner has conditional branches for captured future
customer footprints. The live adjacency scanner uses current districts. The
first late correction concerns internal Bakers Mill eligibility and local
building returns. Future customer additions need their own native calibration.
[Late placement and calibration](../../../research/mods/csc-ai-late-placement-20261105.md)

Keep an effect ledger across both stages. The early +4 experiment already uses
the prospective Bakers Mill to decide which site to promote. Its priority does
not give us the Mill's separate Q8 price. A calibrated policy needs to account
for that overlap before combining site guidance with a late adjustment.

## Discouraging weak sites

The [soft-penalty extension](../../../research/mods/csc-ai-placement-penalties-20261103.md)
keeps that good-site promotion and subtracts a graded priority from every observed
sub-4 Bakers/Tailors pair:65,536 Q8 per missing point, capped262,144. Multiple
district/tile entries can now share a city. These are experimental priorities,
not calibrated yield prices. Native negative scores can still win, and crossing
zero also removes the later future-building uplift. No unconditional poor-site
ban is added. The recovered Online100 game founded ten promoted Quarters and
four below-4 Quarters (12 total completions), with13,881 deductions,75 additions
and zero native errors in completed windows. The positive-only pilot had23
below-4 foundations; this is descriptive, not a matched causal comparison. [AI-C050]

The exceptions identify two different gaps. The Hague and Pokrovka entered native
requests before their sites first appeared in the scanner; later negative values
did not retract the retained requests. Delhi and Majapahit remained positive
after deduction and won with much larger final cached values after downstream
native valuation. The next placement refinement should cover candidates before
request admission and use a [native-versus-CSC component ledger](../native/district-score-anatomy.md)
before deciding on final-aggregate changes. Simply raising a late subtraction
would not solve both problems. The report preserves
the controller interruption, exact scanner-fact recovery comparison and all four
case traces. No empire-benefit or release-readiness claim follows from this test.

## Next decision

**Bakers component result:** a scoped read-only archived80→81 observation now
attributes the dominant weak-site uplift to generated Mill adjacency encoding
bits. The Wind Mill contributes over99.8% of each admitted building sum; the
native interpreter credits all ten magnitudes without their gameplay owner
property gates. The remaining building benefits are much smaller and are not
all individually attributed. [AI-C053] See the
[component report](../../../research/mods/csc-ai-bakers-forecast-components-20261104.md).
The immediate model task is a targeted forecast correction, not a stronger
blanket site penalty. No correction or new policy was installed by that study.

The [range/simplification follow-up](../../../research/mods/csc-ai-adjacency-simplification-20261104.md)
initially recommended a small Mill-specific source representation: one
Wind +1 switch and three Water unit steps.317 actual shared-Lua count cases
preserve current numerical payouts; no replacement was installed at that stage. Smaller bounds
contain phantom magnitude but do not restore omitted gates. Both Mills share
the leak; forecast readiness and native mutual canonicalization explain their
different reported values and admission. [AI-C054] [AI-C055]

**Later4 November implementation:** the recommended one/three unit steps are
now in source, with explicit CITY scope and functioning local-Mill eligibility.
The old player-wide behavior came from CSC omitting MAB's scope override. The
focused actual SQL/Lua checks cover the new graph and scanner; generic rules and
the v2 policy weights are unchanged. At that stage no installation or native game
check was performed, per Henno's offline-only choice. The earlier317-case study remains
historical proposal evidence. [Implementation](../../../research/mods/csc-ai-local-mill-unit-steps-20261104.md). [AI-C056]

**4 November carrier checkpoint:** The
[CE fork parity port](../../../research/mods/csc-ce-policy-parity-20261104.md)
completed Online100 with the same v2 policy and full native diagnostics.
CSC Lua/SQL now has a qualified development path through a CE dependency;
stock CE still lacks the API and upstream release remains separate. [AI-C052]
This clears the development-carrier prerequisite for later model work; it does
not establish the economic quality of the current rule or authorize another game.

**5 November supported-build checkpoint:** the API-only develop port passes
MSVC Release/x64 and a separate Online100/context/save/reload regression, with
101 matching plans, both adjustment signs and all four diagnostic families.
The isolated CSC copy includes the reviewed local-Mill unit steps. That is
carrier qualification, not an isolated native Mill yield/forecast comparison or
evidence of better economic outcomes. All preferences and earlier development
packages were restored; human CSC/stock CE remained unchanged.
[Qualification](../../../research/mods/csc-ce-develop-port-20261105.md). [AI-C052] [AI-C056]

**5 November isolated Mill/building checkpoint:**20 native payout/locality cases
pass, while direct Quarter repair retains a failed native Production assertion
through another turn and exact reload. The smaller roots execute without the
retired weighted roots, but candidate geometry is still absent from the building
forecast. The complete19-building ledger identifies amenities, double-counted
alternative Mill recipients, absent-Wonder GPP and missing material/Service/tourism
channels. Raw district sums and propagated construction vectors reconcile
separately. No policy weights or CE API changed. Normal queued repair later
fails to recover the affected checkpoint at turn4; this is not yet a pristine
ordinary-pillage reproduction. Activation/invalidation and one measured forecast
correction remain separate questions.
[Combined results](../../../research/mods/csc-ai-mill-building-study-20261105.md).
[AI-C058] [AI-C059] [AI-N074]

Review the assumptions and case explanations. Extend profiles to Bakers and
later Quarters, and gather only missing facts that could change a choice:
unlocks/costs, worked tiles, future customer permission, Services and competing
opportunities. Then derive the **additional** CSC value the native scorer does
not already represent, and test a genuine site choice through the existing
bridge and shared controller.
