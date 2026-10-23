# Material preservation and repair: CSC, Real Strategy, AI+ and RH

Read-only review on 23 October 2026. The current donated-Both game and its pinned
sources/settings remain unchanged. This is a proposed next experiment, not an
implemented maintenance controller or a claim that native AI forecasting works.

## Concrete failure in the running diagnostic

The turn-110 current census shows assisted Tailors plot657 still owned by its
original player and complete. Its original material plot731 now contains a
Commercial Hub, with no remaining resource. Its Specialty Silver plot583 is
still owned but its Mine is pillaged. These are distinct problems: permanent
loss of supply to construction versus potentially repairable loss of function.
The Quarter now has sales adjacency but zero Base supply. Initial successful
acquisition, improvement and Quarter completion did not ensure preservation.

Evidence: donated diagnostic run01/resume-090-performance-v9, chain-metrics/
turn-110.json and current primary preservation export. All three assisted
Quarters were complete; two retained both improved material categories.

## Existing CSC mechanisms

`Civ Supply Chains/Data/CSC_AI.sql` currently provides:

- General improvement pseudo-yield90 and separate Builder unit preference50.
- Quarter-owned, exact-material presence value40 on owned visible supplies at
  distance1, independent of whether the material is improved.
- Matching improvement-owned extra80, gated to an AI owner, exact visible
  resource and adjacent same-owner matching Quarter. One marginal contribution
  per industry/resource, rather than per adjacent same-industry Quarter.
- Reciprocal native sales adjacency10, plus broad bonus-resource12 and river4
  guidance for Quarter placement.

The 40 and80 are private AI-planning yield amounts, not real Gold, and cannot
be compared directly to Builder/PseudoYield weights. Modifier application alone
does not prove that district replacement or repair planners consume that value.
The unfinished-Quarter and pillage cases must be checked on the actual current
mechanism before strengthening it. Earlier native fixture contracts explicitly
required40/120/pillaged40, but historical contracts are not substitutes for
current decision-level evidence.

## Rechecked earlier AI mods

| Mod | Actual mechanism in inspected source | What it does not establish |
|---|---|---|
| Real Strategy2.3.1, Workshop1617282434 | Improvement base4; peace/defense/war biases change demand. Author distinguishes improvement contracts from production speed of contracted Builders. | No targeted CSC resource-preservation or pillaged-material repair dispatcher found. Raising Builder unit preference alone does not identify jobs. |
| AI+v13, Workshop878717347 | Improvement base5 and situational biases. Build City Improvement nodes13/23 set Required City=-1, allowing Builder production contracts in any city. | That parameter changes production location, not repair priority or assignments of idle Builders to CSC materials. |
| RH5.097, Workshop3792072489 | Improvement base30, resource-sensitive city Builder-need scoring and scripted Builder acquisition; private values for raw luxury/strategic resources. | Its need scorer counts any existing improvement as improved, including pillaged ones. No general Builder build/repair operation dispatcher or preservation guarantee was found in this review and the earlier package-wide review. |

Useful lessons are state-sensitive demand, production-contract flexibility and
resource-work diagnostics. None of these source patterns is proof of a complete
material-maintenance solution. In particular, an offensive pillage operation or
PROJECT_REPAIR_OUTER_DEFENSES is not a resource-improvement repair mechanism.

### Source anchors

- CSC_AI.sql lines17–38,151–158,214–231,238–305.
- RealStrategy_Main.sql105,927,973 and following war/peace rows;
  RealStrategy_Poland.sql43–53 documents improvement-tree distinctions.
- AI+ behaviortrees.xml732–733; core.xml664–669,908–915.
- RH_AutoPurchase.lua1473–1560: `iImprov >= 0` increments improvedOwned before
  resource work is considered; this branch does not test pillaged state.
- Previous detailed reviews: csc-rh-v5097-ai-review-20261018.md,
  csc-real-strategy-research-review-20261020.md,
  csc-aiplus-research-review-20261020.md.
- Author notes, re-fetched23October:
  https://github.com/Infixo/Civ6-Real-Strategy/wiki/PseudoYields
  https://github.com/Infixo/Civ6-Real-Strategy/wiki/Systems

The current read-only native database contains UNITOPERATION_REPAIR and
UNITOPERATION_HARVEST_RESOURCE. This establishes operation definitions, not a
working Lua dispatch context, job reservation mechanism or AI-priority hook.
Build City Improvement has native Find Available Unit/Build Improvement nodes;
no independently exposed repair-specific preference was identified in the
queried favored items, parameters and node definitions.

## Recommended design and test order

1. **Keep resource preservation separate from working-improvement value.** A
   material remains important while unimproved or pillaged. Give the last Base
   of an established/planned Quarter highest preservation urgency; unique
   Specialty high urgency; redundant supplies lower urgency. Start protecting
   the intended chain at foundation placement, rather than waiting for every
   downstream building. Prefer alternative empty adjacent sales sites.

2. **Expose the marginal benefit of development and repair.** A separate signal
   should appear only for a matching functioning, unpillaged improvement. Repair
   should restore this signal. Verify that native action valuation actually
   anticipates that difference; do not increase40/80 blindly. Losing a working
   Base that supports current stage2/3 production is more urgent than a distant
   optional Specialty upgrade. Unworked tiles can still be CSC supplies, so
   citizen assignment alone must not define the backlog.

3. **Maintain an actionable, plot-specific backlog.** Separate safe reachable
   repairs, missing valid improvements, locked prerequisites, hostile/unsafe
   access and permanently lost resources. Compare available eligible Builders
   and existing jobs, avoiding duplicate reservations. Temporary demand should
   reflect this backlog, not indiscriminately favor Farms/Mines or produce
   additional Builders when existing ones could do the work.

4. **First prove the native incentive response in focused cases.** Measure
   replacement candidate scores/actual placement; improvement and repair choices;
   signal before pillage/after pillage/after repair; adjacent unfinished versus
   complete Quarters; last supply versus redundant supply. If the native
   replacement evaluator ignores lost supply value, larger plot numbers are not
   an adequate demonstrated fix. A location veto or reservation would need a
   separately verified engine mechanism and is stronger than a soft preference.

5. **Use a stronger job helper only if necessary.** Independently author a
   limited existing-Builder helper only after proving legal native movement and
   REPAIR/build requests in the correct context. Respect normal movement,
   charges/costs, safety, existing assignments and one-shot mutation receipts.
   No free repair, teleportation or automatic resource restoration. RH provides
   useful need-scoring ideas, not proof of this operation backend.

Evaluate material loss per observed supply-turn, last-Base losses, repair delays
after safe accessibility, demand versus available Builders, and chain downtime.
Separate disappearance under districts, harvest, pillage and ownership loss.
Do not count a repair blocked by enemies as simple preference failure.
