# Materials, Builders, preservation and repair

A valid material can be locked, unowned, unsafe, unassigned, reserved for a destructive alternative, pillaged after repair or covered by a district. Builder counts alone cannot distinguish these failures.

Boston's only Cattle survived a matched Campus placement test and became a
working Pasture. A later Farm job for the Feudalism boost removed the Pasture
and harvested the deposit. The same Builder, exact plot and distinct native
operations identify work clearance as the cause. [AI-N087]
[Boston's exchange and Builder-loss evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-ordinary-exchange-worked-then-a-feudalism-boost-consumed-the-base).

The main CSC publisher also preserved that supplier in a matched CE replay.
The AI put Campus on plot 720 and worked the Cattle on plot 796 by turn 37.
This verifies automatic district protection for the fixture. Builder
clearance is a separate decision. [AI-C065]
[Automatic publisher evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#automatic-district-protection-replay).

The follow-up traced two callers of the same improvement site selector.
Boost planning can skip a city whose location result is empty. Ordinary
planning can defer creating an improvement tree. A guarded replay used
both paths to keep Boston's exact Pasture through Storekeeper activation.
[AI-N088] [Native paths and retained replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#guarding-the-boost-decision-before-reservation).

A stock GameCore probe filtered the protected row before native ranking.
The boost route initially deferred Boston's Farm, and later calls retained
eligible same-city alternatives. The supplier survived through Storekeeper.
[AI-N091] [Candidate filtering replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#builder-candidate-filtering-before-native-ranking).

The earlier improvement forecast supplies that ranking cache directly.
CE can scope a score change to one improvement on a protected supplier
site without replacing the selector. An already assigned job can reach
execution without another score calculation. [AI-N092]
[CE score producer and execution limits](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#ce-score-producer-and-execution-limits).

CSC's live supplier scan now feeds that CE capability. In the matched
Boston replay the treatment retained the Cattle Pasture and verified
Storekeeper while the control lost the deposit. [AI-C066]
[Automatic Builder protection evidence](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#automatic-builder-protection-in-the-matched-ce-replay).

After a blizzard, a stock continuation kept the damaged Cattle deposit but
did not rebuild the Pasture or repair the Mill by turn 234. A Wonder claim
on the Cattle plot and a Spaceport in production give two separate recovery
dependencies to trace. [AI-C067]
[Stock recovery baseline](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#natural-recovery-after-the-boston-blizzard).

The main CSC Wonder policy redirected the native claim to another site.
Boston's Cattle remained physically developable, and both links remained
down by turn 222. Selection and execution of a Pasture job remain
separate checks. [AI-C068]
[Matched Wonder protection](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#matched-wonder-protection-changed-the-reservation).

When the Spaceport and Research Lab finished, Boston's eligible Water Mill
repair won the building comparison. The city queued an admitted Theater
Square contract. A later Mill contract lost to Encampment, then executed
after that district completed. The Mill's building yields returned while
the missing Pasture kept Storekeeper inactive.
[AI-C069] [Mill repair choice](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-mill-won-the-building-comparison-and-missed-the-queue).

Removing only the Pasture in the early Boston fixture exposed separate
job and plot gates. The old plot reservation no longer resolved. The
ordinary improvement slot was occupied, then a different job won.
An Irrigation boost made a new claim and its Builder harvested the
Cattle. [AI-N096] [AI-C070]
[Supplier replay](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#isolating-the-missing-pasture).

Both turn-72 CE arms lost the Cattle. The treatment logged the expected
ineligible Farm values, while the same Irrigation job reached execution.
The forecast receipts alone cannot distinguish a fresh selection from
a job carrying a prior location. [AI-C071]
[Matched supplier failure](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#the-turn-72-protection-arms-both-lost-the-cattle).

The turn-69 comparison caught the actual Farm selection before the
Irrigation reservation. The treatment redirected the job and kept the
Cattle through turn 81. Boston's first two open ordinary job slots
went to a Camp elsewhere. A Pasture remained legal and Storekeeper
stayed inactive. [AI-C072]
[Earlier matched protection](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#earlier-protection-redirected-the-boost-and-preserved-the-deposit).

Holding protection constant, a bounded Pasture bid won the next
ordinary job in treatment. The AI assigned a Builder and restored
the original Pasture. Storekeeper and the Mill's supplier output
returned at both subsequent samples. The control kept its Cattle
with the Pasture missing. [AI-C073]
[Matched Pasture recovery](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#a-bounded-pasture-bid-restored-storekeeper-in-the-matched-replay).

A committed Clear Plot job still has to select a worker with charges
before submitting a removal or harvest. That readiness decision is
a separate place to test protection for work that already holds the
plot. Its live failure and retry behavior remain unverified. [AI-N097]
[Clear Plot worker decision](../../../research/mods/csc-ai-bakers-natural-research-20261106.md#clear-plot-validates-its-selected-worker-before-submitting-the-operation).

```mermaid
flowchart TD
 D[Mapped deposit] --> L[Legal unlocked work] --> J[Recommendation and admitted job] --> U[Assigned worker] --> E[Native operation] --> I[Working improvement]
 I --> H[Harvest or replacement]
 I --> P[Pillage] --> R[Repair] --> I
```

## AI-C011 — Broad Builder tuning had mixed confounded outcomes

The historical 90/900 package reached improvement density 7.76/city versus 5.22 at the common 200 checkpoint, but did not finish 250. A later resource-layout variant with the same settings gave 6.70/city at 200. Training, purchases, unit additions and remaining charges measure different things. Later native tracing established that the Units-list Value adds to request priority rather than acting like a percentage; Basic's Builder 50 is not a promise of 50 workers. Required City=-1 removes one city-ID restriction while retaining ordinary eligibility checks; it does not assign a worker or guarantee recruitment.

Scope: One-seed historical Builder/density trials and current-build static Units/request consumer tracing.

Limits: Interrupted runs do not enter completed 250 comparisons. Combined settings and changed worlds do not identify a useful individual coefficient or prove sufficient workers for a particular job.

Sources: [Builder partial result](../../../research/mods/csc-ai-rh-builders-20261017-turn200.md), [interruption](../../../research/mods/csc-ai-rh-builders-20261017.md), [density result](../../../research/mods/csc-ai-density-v4-20261017-turn250.md), [Builder consumers](../../../research/mods/csc-ai-native-builder-consumers-20261028.md), [request priority](../../../research/mods/csc-ai-native-builder-priority-20261028.md).

## AI-C012 — Private yields are not human-economically inert

Zero-turn readbacks showed one worker move to Flax with private+40, changing ordinary worked Production/Culture despite unchanged real plot inputs. The later Plantation extension changed allocations/output without additional material development. Empty icons and UI filters do not prevent this.

Scope: All-owner raw-resource/improvement mechanism arms.

Limits: No direct conversion into money does not imply no economic effect. Older inert-output wording is superseded; all-owner diagnostic packages were not AI-only release candidates.

Sources: [Citizen effects](../../../research/mods/csc-ai-private-resource-citizen-effects-20261024.md), [extended forecast](../../../research/mods/csc-ai-resource-improvement-forecast75-results-20261024.md).

## AI-C013 — Soft care landed without reliable preservation

Material-care v 1 stopped 170; v 2 ended after observer defeat 192 rather than 225. V 2 recorded eleven repair-to-working episodes and thirteen supporting-link losses, including four confirmed native harvests for Farm jobs. A working improvement was sometimes actively removed before harvesting.

Scope: Historical 160/80/20 care and urgency experiments.

Limits: Occupancy alone is not a confirmed harvest. Repairs do not prove incentive causality, and nodeSUCCESS is not operation/completion. Neither endpoint achieved the declared 225 test.

Sources: [v1](../../../research/mods/csc-ai-material-care-v1-20261023.md), [decision paths](../../../research/mods/csc-ai-material-care-decision-paths-20261023.md), [v2 terminal result](../../../research/mods/csc-ai-material-care-v2-terminal192-20261023.md).

## AI-C014 — A harvest ban was an unsuitable preservation control

The no-harvest rule prevented the raw control’s three losses through 75 and yielded six versus five working Base producers. It also removed Quarter options and caused repeated rejected harvest/build routes, some later adapting to Pastures.

Scope: Identical source 16→75 counterfactual pair.

Limits: One world, shared private signals and subsidies; zero working Both producers. A player-wide legality restriction is not targeted care and was not promoted.

Sources: [Native harvest-rule result](../../../research/mods/csc-ai-native-harvest-rule75-20261024.md).

## AI-C015 — Direct Pasture and conditional Farm routes had positive controls

Cattle 2533 changed from a Farm reservation/harvest in the raw control to a Pasture reservation 20, working 21 and retained 75 under direct Pasture 80. The 150 resource-Farm pilot verified seven isolated resource-Farm positives and 81 terrain-only negatives, with logged job/reservation and physical development evidence.

Scope: Separate historical direct and conditional forecasting treatments.

Limits: All-owner scope, whole-bundle/timing differences and divergent spending prevent isolated empire-benefit claims. The Farm poweroff left 45 research rows and other interval observations missing; its dense-observation pass stayed false. Preservation and repeated pillage remained problems.

Sources: [Pasture result](../../../research/mods/csc-ai-pasture-forecast75-results-20261024.md), [Farm150](../../../research/mods/csc-ai-resource-farm150-test-20261024.md).

## AI-C016 — District-free supply is necessary but insufficient

A planner falsely counted Silk retained under a City Center as future Plantation supply. The corrected same-source 75 guard omitted that site: four valid foundations versus five, unchanged seven working Base producers and zero Both producers.

Scope: Exact precommit audit and external planner/commit correction.

Limits: A globally valid improvement mapping plus owned/revealed/district-free resource does not prove current unlock, terrain legality, reachable Builder or eventual work. Fewer false starts is a quality fix, not a causal whole-mod victory.

Sources: [False-Both discovery](../../../research/mods/csc-ai-resource-improvement-forecast75-results-20261024.md), [corrected result](../../../research/mods/csc-ai-material-viability75-results-20261024.md).

## AI-C017 — Recommendations, assignments and getter domains differ

Honey became its city’s highest returned recommendation at 112/113 and stayed unimproved; different Builders received identical city lists. Flax’s absence did not prove illegality or zero hidden value. Separate probes also found existing serialized Farm values and newly assigned Sugar responding differently despite correct loaded definitions.

Scope: Bounded follow-through, recommendation/admission and zero-turn delivery studies.

Limits: No same-path positive control means a getter’s zero is inconclusive. UI, Gameplay, initialization phase and reload cannot be interchanged; recommendation is not admitted work or allocated capacity.

Sources: [Follow-through](../../../research/mods/csc-ai-material-followthrough-20261031.md), [recommendations](../../../research/mods/csc-ai-material-recommendations-20261031.md), [admission](../../../research/mods/csc-ai-work-admission-20261031.md), [delivery](../../../research/mods/csc-ai-acquisition-signal-delivery-20261024.md).

[Complete source map](source-map.md).
