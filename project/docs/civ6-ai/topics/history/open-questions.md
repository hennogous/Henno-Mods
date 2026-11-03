# Questions that remain open

We now know enough to ask narrower questions. The priorities below are a research backlog, not an instruction to resume the paused optimisation campaign. Each question distinguishes the mechanism already established from the decision or benefit still needing evidence. **[AI-H004]**

## 1. Can we supply an arbitrary, local district incentive coherently?

**Known:** ordinary district scoring consumes native adjacency and dynamic custom yields. Lua can evaluate arbitrary accessible state to return a Boolean strategy condition. No ordinary numerical per-candidate Lua callback was established in the inspected interfaces.

**Open:** whether a native extension could add a function of player, city, district, plot and current state at the right score/cache boundary, while keeping downstream present value and request priority consistent. This is a design possibility, not an implemented or tested feature. **[AI-H012]**

**Useful next evidence:** map the relevant cache writes and downstream readers offline; specify the intended score units, available context, lifetime and invalidation behaviour. A first prototype would need a zero-change control and a bounded nonzero input demonstrating consistent candidate, winner and request values. Altering only the final winner would not establish a coherent valuation mechanism.

Source: [custom-incentive boundary](../../../research/mods/civ6-district-choice-placement-and-incentives-20261103.md#fully-arbitrary-per-site-incentives-remain-a-separate-integration-problem).

## 2. What exact material/customer forecast should an incentive represent?

**Known:** the native AI can propagate explicit building-prerequisite value. An existing Quarter can also supply an explicit per-building forecast before its producer exists. The hypothetical modifier interpreter does not faithfully simulate every gameplay gate or the entire jointly missing supply network.

**Open:** the contract for credible future development: which materials, improvements, unlocks, customer spaces, buildings, costs and timings should count, and how strongly? A signal for potential must remain distinguishable from working supply and realised returns.

**Useful next evidence:** evaluate captured cases offline with explicit assumptions and alternatives. Include Base-only high-value sites, Both sites without customers, existing customers missing one building, shared customers, legal but distant resources, blocked future footprints and good native district alternatives. Preserve unknown travel and opportunity costs instead of silently treating them as zero.

Sources: [forecast channels](../../../research/mods/csc-future-economy-forecast-20261103.md), [objective and planning distinctions](../../../integrations/csc-ai-objectives.md), [customer-aware implementation](../../../research/mods/csc-ai-customer-aware-planner-v2-20261101.md).

## 3. Can we observe a complete natural district decision at reasonable cost?

**Known:** the static route and weight units are established. The two early-turn observers captured too many unrelated evaluations and no useful target decision. There was no changed-weight experiment.

**Open:** an affordable capture linking fresh candidate components, final cached values, natural winning type/site, reservation and production request. Partial visibility must not be presented as an exhaustive ranking.

**Useful next evidence:** demonstrate filtering before expensive JavaScript callbacks, using offline accepted/rejected scope and budget checks. The closed runs do not justify another address-only retry or a larger cap. An eventual bounded existing-save observation should target the remaining decision question rather than re-prove already established arithmetic. **[AI-H008]**

Source: [observer closure and measurement limit](../../../research/mods/csc-native-quarter-placement-control-evidence-20261101.md).

## 4. How do useful material recommendations become admitted, assigned jobs?

**Known:** the city can admit Farm and Mine jobs; recommendation and admitted values can differ. Honey became a top exposed recommendation but never appeared in the captured payloads. Charged nearby Builders did other work. Native improvement/repair consumers exist, but a safe arbitrary planner-to-economic-job submission route was not established.

**Open:** which earlier admission conditions, opportunity comparisons or reservations excluded the target work; which worker and travel constraints matter after admission. We do not yet have evidence that assignment was the failure in the Honey case.

**Useful next evidence:** reuse the captured recommendation, admission and commitment records to define a specific missing transition. Only then instrument that transition. A higher blanket Builder bias or a forced improvement order would answer a different question.

Sources: [recommendations](../../../research/mods/csc-ai-material-recommendations-20261031.md), [work admission](../../../research/mods/csc-ai-work-admission-20261031.md), [native job feasibility](../../../research/mods/csc-ai-native-material-job-feasibility-20261030.md).

## 5. What makes a valued producer or customer win actual production?

**Known:** a direct Granary trait preference reached the native consumer; fresh producer valuation consumed a private forecast; IZ prerequisite value propagated backwards. Actual production still competed with units, districts and other buildings. Some best-building returns belonged to threat review rather than the ordinary new-request path.

**Open:** the marginal choice effect of a narrowly changed forecast at a fresh ordinary decision, including its request value and queue competition. A persistent whole-chain plan has not been established by the IZ observation.

**Useful next evidence:** an existing eligible city with the relevant decision boundary exposed; compare the changed input, recalculated value, ordinary request and actual queue, preserving competing choices. The prior producer off arm did not run, and the short IZ window did not observe a new ordinary Workshop request, so neither supplies that missing causal contrast.

Sources: [producer decision](../../../research/mods/csc-ai-producer-decision-20261030.md), [direct Granary](../../../research/mods/csc-ai-granary-direct-priority-20261101.md), [IZ decision boundary](../../../research/mods/civ6-industrial-zone-decision-boundary-20261101.md).

## 6. How should a supply chain survive competing land uses and damage?

**Known:** some native repair follow-through occurs. Soft care incentives have not prevented every harvest, district replacement or pillage loss. In one v2 case an identified Builder harvested the selected unimproved Cattle for a Farm plan. A promised future Holy Site was used by a Theater Square.

**Open:** when preserving or restoring a chain is worth more than an alternative use, and how that value can reach the actual destructive or repair decision. An absolute no-harvest rule is not the objective.

**Useful next evidence:** classify existing losses by confirmed cause and value already at risk. Distinguish material removal from district footprint coverage, building repair from Builder improvement repair, and a speculative future customer from an actual native reservation. Track legitimate replacement paths: the one successful assisted v2 chain used a different valid Mill from the planned one.

Sources: [progress and loss review](../../../integrations/csc-ai-progress-and-learnings-20261101.md), [material preservation review](../../../research/mods/csc-ai-material-preservation-and-repair-review-20261023.md), [selective outcome](../../../research/mods/csc-ai-paired-selective-chain-screen-results-20261101.md).

## 7. Which current CSC effects appear in which native forecast?

**Known:** today's population returns use actual-state Lua/property calculations and City Center consumers. Ordinary sales, material-enabled Services and explicit private forecasts have different requirements. Historical building-owned definitions do not automatically describe currently attached roots. The inspected candidate path does not invoke CSC's Lua matcher on a hypothetical chain.

**Open:** the precise live score contribution of current Stage 4/export named-building adjustments and property-based consumers in a specific city and profile. Unsupported property requirements can be omitted by the AI approximation, so a positive hypothetical value need not represent faithful economic foresight.

**Useful next evidence:** pin today's active attachments and choose one effect/channel for a controlled consumer contrast. Keep a live building getter, hypothetical modifier evaluation and total score separate. Do not extrapolate one empty-context result to universal AI blindness.

Source: [current source and interpreter study](../../../research/mods/csc-future-economy-forecast-20261103.md).

## 8. Does a coherent package improve total empire benefit under Basic and RH?

**Known:** some selected interventions work mechanically; several individual chains developed. The selective and customer-aware screens did not establish improved combined chain outcomes. Working producers and materials may provide partial benefits before a full-supply milestone.

**Open:** sustained, worthwhile, balanced performance over meaningful horizons and multiple maps under both profiles. No single same-map joint-package comparison establishes general capability or isolates each input. **[AI-H002]**

**Useful next evidence:** after a justified mechanism change, compare total and opportunity-adjusted outcomes, completion delays, repair/retention, actual returns, acquisition/subsidy costs and displaced military/economic development. Keep late investments right-censored and report missing observation intervals. Service-to-strategy matching belongs after the basic chain capabilities are dependable, though native strategy/need sensitivity already exists.

Sources: [objective](../../../integrations/csc-ai-objectives.md), [selective screen](../../../research/mods/csc-ai-paired-selective-chain-screen-results-20261101.md), [v2 outcome](../../../research/mods/csc-ai-customer-aware-planner-v2-native-20261101.md), [district empire-need inputs](../../../research/mods/civ6-district-choice-placement-and-incentives-20261103.md).

## Questions that should not be reopened from stale status

The UI helper cold-start question is closed at the capability level by the two later diagnostic startups; the v2 report's earlier “pending” wording is historical. The root cause of the reproducible lens-panel exit failure was investigated and corrected, with dedicated exit checks; callback fan-out in the later placement observers was a different issue. The old arbitrary native economic-job route remains unestablished rather than a ready execution interface. **[AI-H010] [AI-H011]**

Sources: [later cold-start evidence](../../../research/mods/csc-native-quarter-placement-weights-20261101.md#native-baseline-initial1-gate), [UI exit investigation](../../../research/mods/csc-ui-exit-crash-20261031.md), [job feasibility boundary](../../../research/mods/csc-ai-native-material-job-feasibility-20261030.md).
