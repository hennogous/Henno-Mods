# What we’re investigating

## Three ordinary games with integrated CSC tuning

Across three Online-speed games through turn 200, 13 Bakers chains operated
for 546 confirmed chain-turns. One chain passed 100 active turns. Two chains
resumed after interruptions in ordinary play. Tailors finished 47 Quarters,
but only six had a working Base supplier at the endpoint and none registered
Stage 2 Service. The shared model is running for both Quarters. The Tailors
results show where to look next for the missing links.
[Game results and measurement details](../topics/csc/site-planner.md#three-normal-start-games-through-turn-200).

Repeating the same starts with CSC tuning off yielded two Bakers chains
and 94 confirmed Service turns. V2 had almost the same number of Bakers
Quarters and substantially more with working Base supply and a working
customer. Neither arm had an active Tailors Stage 2 Service at turn 200.
The v2 empires had higher Gold reserves overall but lower combined
Production, net Gold income, population and Food surplus at that boundary.
[Matched comparison and turn-200 census](../../research/mods/csc-ai-integrated-stage-two-20261108.md#matched-baseline-with-csc-tuning-disabled).

The next Fractal repeat used shared Stage 2 guidance for both industries
and deductions for weak Quarter sites. It finished seven fewer Bakers
Quarters and delivered 69 more confirmed Storekeeper chain-turns. Tailors
finished four fewer Quarters and still had no active Stage 2 Service.
[Shared policy and matched Fractal result](../../research/mods/csc-ai-shared-stage-two-fractal-20261108.md).

## Milestone reached — Boston's working Bakers chain

Boston completed Bakers on our chosen site after one turn-22 score change.
The game began with Craftsmanship locked and Boston's player researched it
normally. The control founded Bakers on a different tile. The chosen Quarter
had its Base deposit and an adjacent City Center at completion. A second
matched test lowered the Campus score on the only Base tile. Boston placed
Campus elsewhere and built a Pasture, Granary and Water Mill through its
ordinary plans. We then protected the Pasture from two independent Farm
decisions, one for the Feudalism boost and one from ordinary city planning.
Boston researched Feudalism and had a working Storekeeper at turns 63 and 66.
The Granary produced 2 Food against its base of 1, and the Water Mill produced
1 Production and 1 Gold at both observations. The controller saved the
complete chain on turn 66.
[Construction, supplier protection and actual yields](../../research/mods/csc-ai-bakers-natural-research-20261106.md).

The same chain also passed a 152-turn durability test, from turn 90 to 242.
It kept its original Cattle Pasture, Water Mill and Granary, with Storekeeper
active and the building yields still present. An earlier continuation ended
the streak after 141 turns when the Pasture failed during a nearby blizzard.
The later run followed a different weather sequence.
[152-turn audit and the earlier break](../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-same-chain-passed-152-turns-in-a-separate-continuation).

## Intermediate milestone — repeat the Bakers Stage 2 chain from normal starts

The sequence is a completed Quarter with viable Base supply and an adjacent
Granary host (**1**), a working Mill and Granary (**4, 5**), a working Base
improvement and sufficient Builder capacity (**3**), then a functioning
exchange with its supplier retained (**2.2**). Feudalism and Storekeeper
extend the test to a working Service (**6.1**). Existing unlocks and buildings
can satisfy dependencies. Tailors comes next through the same model.

The live Boston replay establishes this sequence for one Bakers chain. The
normal-start placement policy currently works on owned Quarter sites.
Acquiring a Quarter footprint and acquiring an adjacent resource are
separate decisions. For Bakers Stage 2, the Quarter can already be on
city land while the material that makes the site viable is beyond it.
[Land acquisition](../topics/native/district-choice.md#buying-a-future-site).

The first turn-100 development game finished four AI Bakers
Quarters. None had an active Storekeeper. Alexandria Troas had
the buildings and unlocks, but the Cattle tile was still unimproved
after the game applied the Pasture preference. The replay showed
the city chose a different Pasture when it had room for a new job.
A small extra bid redirected the job and the city assigned a
Builder. Keeping the bid active through reassignment led the AI to
finish the Bakers Pasture and activate Storekeeper. In the matched
control it built the other Pasture. The integrated publisher
reproduced the result on the same save and then in a normal-start
game. The fresh game had six confirmed Storekeeper turns in
Alexandria and none elsewhere. Melbourne still needed only a
Wind Mill. A test bid made it offer the Mill instead of an
Amphitheater. When production opened, the AI refreshed the offer
and built the Mill at its own valuation. Storekeeper operated
for six measured turns. The main CSC policy and CE review build
then reproduced the nomination, construction and a measured
Storekeeper turn from the same save. The next checks are how
this bid behaves in other cities and how to value a Granary.
Ancyra could build one, but Castle won the building nominations
and a Cuirassier took the open production slot. Trebizond
already has a Mill, so a Granary there would begin the exchange
even while its Wheat still needs a Farm. A matched nomination
test produced a valid Granary offer, and Trebizond bought it with
Gold. Before later Mill damage, the Granary gained one Food and
the Mill gained one Production and one Gold. The Granary's native
forecast returned zero for its exchange roots. The initial
reusable bid credits the Food using the native income timing.
The clean replay confirmed that the bid reached the comparison
and Library still won. Native samples for Production and Gold
then raised the initial exchange preference to 52 points.

In the next ordinary start, Melbourne submitted a Wind Mill offer
and used its production for other commitments. It bought the Mill
on turn 113, and Storekeeper operated for 132 turns by the endpoint.
Aigai still lacked a Pasture at 150 despite the supplier bid
reaching its scorer. The same setup took a different course in a
second game, where the city at that site built the Pasture on 118.
Trace the job decision and Builder assignment before adjusting the
bid. The follow-up found that Alexandria's Pasture won all
three open comparisons before it was built. The city still had
to wait for a Builder. Six other sites
had both types of neighbor and multiple unfinished links. They
also need a way to value the first investment in the chain.
Heidelberg assembled several such links and activated Storekeeper
on turn 178. That was too late to reach 100 active turns by the
end of the run. Its Builder repaired the Maize Farm during a
short lapse, and the native effect returned. Launceston bought
its Granary after receiving the exchange bid and became the
third chain on 189. Four chains operated over the run, and only
Melbourne had 100 active turns. Heidelberg later lost its only Maize
to a Dam despite the district-score deduction. This leaves a separate
supplier-protection problem.
[Ordinary-start evidence](../../research/mods/csc-ai-bakers-natural-research-20261106.md#melbourne-bought-its-mill-in-the-ordinary-start-development-run).

For earlier investment, Melbourne's turn-105 replay shows that an
existing Granary already gives the proposed Wind Mill credit for
Production and Gold. Even pricing the missing exchange and an
immediately working Storekeeper leaves Castle ahead in this replay.
Melbourne reserved the Rice Farm. Its request for another Builder
lost nine comparisons across six cities. In the closest comparison,
Adelaide took a higher-valued request for a Builder on a different
job. The nearby Builder repaired Sydney's Farm, then built an Outback
Station for Canberra. Melbourne found no eligible worker on ten checks.
The next development run looks for earlier investments with credible
payoffs and a save before a district can cover a working supplier.
[Opening forecast and Builder evidence](../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-first-rice-recruitment-found-the-nearby-builder-already-busy).

The turn-200 repeat observed four active chains. Ancyra still needed
both buildings on 190. Alexandria's Service stopped after 69 turns
when its Quarter and Mill were damaged, with its Pasture and Granary
still present. The saved game also has Charleston's working Maize chain
beside a completed Dam. The live survey confirmed the Farm and Dam
share a floodplain. Charleston had no legal new Dam site, so the next
supplier-protection comparison needs a different city or an earlier save.
[Turn-200 development evidence](../../research/mods/csc-ai-bakers-natural-research-20261106.md#a-normal-start-repeat-reached-four-chains-by-turn-200).

In Alexandria's repair replay, the Water Mill scored well and failed
the building requirements while its Quarter was pillaged. The Quarter
repair was legal. It scored below Aerodrome in the only two open
district comparisons. The same plan then occupied all 15 checks in
the continuation. The Quarter and Mill were still damaged at turn
229. The reservation saved on the Quarter's tile did not block it
on turn 201. A separate repair tree submitted a request alongside
Aerodrome. The corrected replay used the Quarter's ordinary value
and kept the Aerodrome request. Alexandria repaired the Quarter after
finishing Broadcast Center. The later Aerodrome request also advanced.
The restored Quarter made its Water Mill eligible. The AI completed
the Mill repair on 220, and Storekeeper resumed on 221. The packaged
CE and CSC versions reproduced both repairs and the resumed Service.
The pending Quarter repair also survived a save and reload. The AI
used the original request, and CE suppressed a duplicate. In the matched
run with the same CE binary and repair nominations disabled, both the
Quarter and its Mill were still pillaged at turn 214.
[Repair evidence](../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-quarter-can-gate-its-own-mills-repair).

Ancyra already had a working Rice Farm but needed both the Wind Mill
and Granary. Both buildings were legal and lost their comparisons
to Walls. The Wind Mill came closer. In both replays the AI also
spent Production on Line Infantry. The normal-start development
repeat saw no immediately viable Mill exchange before Feudalism in
its early snapshots. It reproduced four working chains and only
Melbourne reached 100 active turns. Heidelberg again lost its only
Maize to a Dam. The read-only replay found a legal alternative with
the same flood coverage. The Maize site still scored higher.
Excluding the Maize tile in one matched comparison let the AI
choose Harbor elsewhere. It started the Harbor and kept the Farm
and Storekeeper. Next, verify that the protection holds after
production and make it reusable.
[Ancyra replay](../../research/mods/csc-ai-bakers-natural-research-20261106.md#ancyras-early-wind-mill-lost-to-walls).
[Normal-start repeat](../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-integrated-repair-build-repeated-the-ordinary-development-outcome).
[Heidelberg site comparison](../../research/mods/csc-ai-bakers-natural-research-20261106.md#heidelberg-had-a-legal-dam-alternative-with-the-same-flood-coverage).

Charleston activated a third Storekeeper chain after a Maize
Farm appeared. That chain has two measured Service turns so far.
[Turn-100 census](../../research/mods/csc-ai-bakers-natural-research-20261106.md#normal-start-follow-through-to-turn-100).

The offline planner separately covers actual gameplay definitions and a copied
Tailors case. In matched replays the main CSC policy redirected Campus off
the Cattle, then separately kept a destructive Farm out of the Builder
rankings. The latter replay kept Boston's Pasture working through
Storekeeper. In a later stock replay, Boston rebuilt neither the Pasture
nor the damaged Mill by turn 234. The matched CE policy diverted a new
Wonder reservation away from the Cattle in a separate replay. That replay
also ended with both links down. A later stock continuation found that the
damaged Mill won its building comparison while Boston queued a Theater
Square contract. Boston later submitted a Mill repair contract. The city
accepted it and refreshed its value, then executed a higher-valued
Encampment contract. The Mill repair ran after Encampment and restored its
building yields. In a separate test with only the Mill pillaged, the AI
repaired it and restored Storekeeper with its original Pasture. The late
Boston chain still needs that Pasture rebuilt before Storekeeper can return.
A matched replay screened unavailable projects before ranking and
Boston chose a valid Terrestrial Laser. A repair bid needs to earn its
place against that kind of executable investment. A separate Mill-only
replay left the supplier and customer working. Boston finished a Theater
Square, then repaired the Mill and restored Storekeeper. Check for
recurrent delays in ordinary games before tuning this choice.
In the controlled Pasture-loss replay, an Irrigation boost harvested the
Cattle before Boston could rebuild. The matched replay also lost the
deposit after CE suppressed the Farm forecast. The earlier replay will
trace which location selector the boost uses and what it reads.
[Stage 2 replay](../topics/csc/site-planner.md#stage-2-decision-replay) ·
[Qualification roadmap](../roadmap.md#current-milestone-and-active-problem).
[Recovery evidence](../../research/mods/csc-ai-bakers-natural-research-20261106.md#natural-recovery-after-the-boston-blizzard).
[Matched Wonder test](../../research/mods/csc-ai-bakers-natural-research-20261106.md#matched-wonder-protection-changed-the-reservation).
[Mill repair choice](../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-mill-won-the-building-comparison-and-missed-the-queue).
[Pasture decision and harvest](../../research/mods/csc-ai-bakers-natural-research-20261106.md#isolating-the-missing-pasture).

## Tools for this milestone

The shared controller and guarded stock score hook support matched live tests.
On the patched DX11 executable, the corrected CE profile loads the save
that previously crashed and carries both score writes. The same CE review
line now carries the automatic district and Builder supplier policies.
Dev-CE 0.8.1 is an optional research tool for a specific
extra Lua getter or debugging need. Packaged CE delivery is a separate
qualification on the patched Windows host.
[Dev-CE release](https://github.com/cru121/civ6-dev-ce/releases/tag/v0.8.1-experimental) ·
[CE hotfix notes](../../research/mods/csc-ai-xp2-november-hotfix-20261106.md).

For each problem, we trace the decision in the game files and native code
with REA and Ghidra, then use a focused runtime trace to check what the AI
actually does. The handbook records the mechanism and the limits of the
evidence. [Research workflow](../roadmap.md#reverse-engineering-each-decision).

The [numbered roadmap](../roadmap.md#numbered-problems-to-solve) tracks the
decisions and the [current problem](../roadmap.md#current-milestone-and-active-problem).
