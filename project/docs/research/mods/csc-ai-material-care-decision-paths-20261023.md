# Material-care decision paths: stopped170 and native checks

Henno stopped the material-care pilot on 23 October to investigate its decision
paths. It ended at native170, **partial, not the declared225 endpoint**. No tuning
coefficients were changed during the run. The same170 save was subsequently
loaded separately for isolated decision-path, lower-pressure calibration and native-guard diagnostics, with zero AI turns advanced in each. Each output branch journals its single load. No units,
improvements, resources, production, ownership or treasury were changed by those
diagnostics. Only private preservation properties were temporarily disabled and
restored, separately journaled from the accepted game.

## Preserved partial result

- Eight assisted foundations present; seven complete at170.
- Thirteen paid assisted tile assignments:685 Gold,297 from AI treasuries and388
  shortfall donations. This remains quoted Gameplay assignment, not proof of a
  native AI PURCHASE command.
- 845 unique research records, all five AI players on turns1..169, no gaps.
- All91 executed source pins unchanged at the stop; no native fault reported.
- Care scanner valid only from25. The final deep care checkpoint is150; do not
  fabricate per-tile work transitions for151..169 from the terminal census.
- Worker/supervisor exited0 after the human stop. The supervisor's generic
  `attention` classification does not turn this requested stop into a failure.

The partial audit is `run-01/resume-025-district-iterator-v2/independent-human-stop170-audit.json`
under `Desktop/Codex/csc-material-care-v1-20261023`.

## Verified: preservation reaches native plot yields

The diagnostic required exact170 world parity before probing and used fresh
captures for final world/treasury parity. Original observer `snapshot(170)` is
frozen; it must not be mistaken for a new post-probe readback. The final receipt
explicitly uses `CSCBASE.capture()` via the maintained chain collector.

Across31 marked plots, disabling the three private properties removed exactly
the authored160/80/20 preservation amount. Restoring them restored each original
native yield. For example, a last-Base unimproved Wheat went200→40→200 and an
improved last-Base material280→120→280. Ordinary yields and all five AI treasuries
were unchanged. The indexed `GameInfo.Yields['YIELD_CSC_AI_PLACEMENT']` lookup is
necessary in UI: CSC intentionally filters that row from UI enumeration.

This proves native application, not that a district/harvest planner prices the
loss of this yield or of downstream supply. The existing marginal improvement80
was not independently switched off in this experiment.

## Exposed recommendation comparison: no observed score response

Native CityAI exposes `GetBuildRecommendations`,
`GetImprovementRecommendations`, and `GetImprovementRecommendationsForBuilder`.
The last method takes the Builder component ID, as shipped UI code does. Its
returned records include `ImprovementLocation`, `ImprovementHash`, and
`ImprovementScore`. Build recommendations expose item hashes and scores.

At170 the private-signal on/off/restored comparison covered37 AI cities and52
Builder recommendation records from cities with nearby sampled Builders. Two
recommendations were on marked material plots: Wheat1473/Farm score5879 and
Honey2565/Camp score2864. No exposed production or Builder recommendation
selection/score changed when the preservation properties were disabled.

**Limit:** no supported recommendation cache invalidator or district-site/harvest
score interface was identified in the inspected CityAI interface, API corpus or
shipped debug panel. A zero-turn cached recommendation can stay unchanged even
if a later planner evaluation would respond. Constant preservation value is also
different from an improvement's marginal gain. Therefore this is *no demonstrated
decision response*, not proof that the AI ignores all CSC private yields. The
native production log does explicitly enumerate the private yield channel.

## What native logs add

The accepted log stream was archived before the diagnostic reload. Byte-offset
segments remain authoritative; repeated behavior-tree evaluations are not
independent jobs, and many improvement tasks have no CSC connection.

- **Commitment timing:** El Kurru's Campus contract2046 was submitted134 with
  value1392, placed145, and completed151. Placement removed Wheat2389, repaired
  at111 and pillaged again133. This separates proposing a district, committing
  its production, placing it, and completing it. Contract value is not an exposed
  per-site lost-material penalty.
- **Builder availability:** Build City Improvement repeatedly records failed
  `Find Available Unit`, `Move Unit`, `Protect Unit`, `Reserve Plot`, and
  `Build Improvement` nodes. These distinguish production capacity from available
  workers, path/safety and task execution. They do not by themselves identify a
  specific CSC task or prove the reason every delayed tile was ignored.
- **Repair execution:** seven care repair→working transitions through150 match
  exact-player/turn/coordinate native REPAIR operations. Wheat2389 waited from
  repair state58 to repair111; its later replacement demonstrates that repair
  and long-term preservation are separate decisions.
- **Disaster context:** RandomEvents records a severity2 Capelinhos eruption125
  at55,19. Banana1462 at56,19 simultaneously loses its resource, gains volcanic
  soil and has a pillaged Plantation. This strongly supports eruption damage;
  the summary event is not an individual damaged-plot list.

Through150, five resource losses are directly associated with surviving district
replacement: Maize→Tailors, two Cattle→Commercial Hubs, Rice→Dam, Wheat→Campus.
Three other resource removals remain unresolved: a transient raw district13 at
removal is not sufficient to infer a completed Wonder or Builder harvest.

## Builder demand gate and next investigation

The material-shortage callback was evaluated751 times through150 with zero
errors. Shortage was false for all five studied AIs at every saved checkpoint.
There is no continuous activation counter, so transient activation cannot be
ruled out. The gate compares missing improvements to **all** Builder charges,
or checks for repairs with **no** Builder. It does not measure busy/reserved,
nearby, reachable, or safe-to-use Builders. Failure nodes in the native job tree
make that distinction practically relevant.

Do not raise plot numbers and call the decision path fixed. Next work should
separately establish fresh district-site/harvest opportunity-cost response,
marginal improvement/repair forecasting, and local available-job capacity. Any
stronger placement reservation or Builder dispatcher is a new implementation,
not something validated by this pilot. No new game was started. The revised source candidate below was built after the original native process and its owners had exited; original executed sources remain archived.

## Restoration and evidence

Supported MainMenu/ExitOK completed and all Civilization processes were absent
before restoration. The parent pretest510 manifest matches every installed file.
Only modinfo and the two candidate care files differed; the candidate versions
are archived. Original144 preferences/autostartfalse verified. Art source fixes,
other runtime files and unrelated work were preserved.

Evidence under study `decision-path-verification/`:
`decision-path-findings.json`, `detail-{baseline,off,restored}.json`,
`fresh-final-parity.json`, `final-restoration.json`, and original command/reply
journals. The first JSON depth guard omitted nested recommendation fields; its
raw outputs remain preserved and the separately completed detailed probe fixes
that diagnostic limitation. Original run outcomes were never replayed.

## Full accepted-log synthesis

`project/tools/ai_baseline/log_intelligence.py` reconstructs byte-offset gzip
segments, checks conflicting overlaps/gaps, rejoins split CSV lines and restricts
analysis to parent1..24 plus child25..169. The inspected streams had no byte gaps
or conflicting segments. Empty/unparsed logs are coverage limitations, not proof
that their events did not occur. `AI_Planning` enumerates unit plot plans;
research/policy logs enumerate candidate scores, so those rows must not be counted
as adopted choices or policies. The native research observer remains authoritative
for actual choices/completions. No log examined supplies a monetary Service ledger.

| Contract cohort | Unique contracts | Selected | Completed | Offered in multiple cities |
|---|---:|---:|---:|---:|
| Builder | 266 | 209 | 116 | 227 |
| CSC buildings | 99 | 55 | 42 | 0 |
| Districts | 237 | 173 | 133 | 4 |

Observed median submission-to-selection delays were1,2 and3 turns respectively.
These are censored cohorts, not completion rates for equally aged opportunities.
A cancellation in one city can coexist with completion elsewhere. Native observer
records separately show127 Builder training completions and18 Builder purchases;
contract totals are not a substitute for unit event counts. The repeated native
improvement tree contains777 Find Available Unit failures,146 Move Unit failures,
402 Protect Unit failures,8 Reserve Plot failures and25 Build Improvement failures.
These are evaluation records, not unique jobs, and include non-CSC work.

This supports changing the kind of pressure, rather than simply producing more
Builders. AI+'s any-city production contract change is already effective:227
Builder contracts were offered across cities. Reapplying it would not fix local
worker availability, safety, pathing or reservation. Real Strategy's separation
of production capacity from work demand is consequently more relevant now.

The99 CSC building contracts include19 Bakery,8 Cafe,15 Water Mill,20 Wind Mill,
5 Fashion House,14 Tailor and18 Textile Workshop contracts. Completed contracts
were7,2,4,10,3,4 and12 respectively. Some completions can later be lost/captured;
they are not current owned-building counts. At150 the native outcome census had
36 producer buildings but only13 with improved owned Base material and4 with both
improved materials. Eleven of the13 functioning producers had an eligible sales
district link. Seven recipient Service-property instances were observed, which
remain distinct from customer building requirements and unobserved payments.
The upstream material bottleneck is more pressing than blanket downstream demand.

Seven observed repair episodes completed with native REPAIR operations. Observed
repair-state-to-working delays were2,11,4,7,53,7 and15 turns. The initial11-turn
episode is left-censored; unsafe periods remain included. Wheat2389 was repaired
and later replaced by the Campus: successful repair does not imply preservation.
Nine supporting resources disappeared through150: five confirmed district
replacements, three unresolved removals and one strongly eruption-associated
Banana loss. Do not count improvement loss, resource loss and pillage as the same
outcome or infer that all disappearances were harvests.

## Revised candidate: work demand and native tile validity

Implemented in `CSC_AI.sql`, `CSC_AI_MaterialCare.sql` and
`CSC_AI_MaterialCare.lua` (Lua version3; design revision2):

- Reduce blanket improvement pseudo-yield from90 to30, matching the inspected
  current RH calibration. Keep CSC's existing general Builder preference50.
- Remove the candidate's extra Builder-production100. Activate improvement work
  demand +100% only for a sustained actionable material backlog: base30 becomes60.
  This is a player-wide soft bias, not a guaranteed plot-specific job.
- Escalate last-Base repairs after1 observed safe/actionable turn, other repairs
  after2, last-Base development after3, Specialty development after5 and redundant
  development after8. Repeated callbacks within a turn do not age jobs. Unsafe,
  locked, changed-resource and working transitions reset the observed interval.
  Reloads start censored new intervals; no earlier wait is invented.
- Record nearby same-area Builder counts/charges within6 as diagnostics. Busy or
  reserved units and shared coverage remain possible; proximity is not path or
  available-worker proof. It does not trigger unit purchases or production.
- Record continuous true/false strategy calls and transitions. The old empire-wide
  shortage flag remains diagnostic, rather than being the work activation gate.
- Keep last-Base160/last-Specialty80/redundant20, with no coefficient escalation.
  Add native mapped-resource-present and no-district predicates around the Lua
  mark, so stale properties cannot award preservation value after replacement.

The RH comparison now yields a structural lesson: its direct resource-yield
signal is tied to the resource's lifetime. Our Lua mark alone could outlive that
state between refreshes. Native predicates remove that stale-state problem and
expose tile validity to native evaluation. Whether hypothetical district/harvest
scoring actually prices the loss remains an explicit hypothesis. No protected
plot ban, direct Builder orders, resource restoration, new economic yields or
research forcing was introduced. No RH restricted code was copied.

## Candidate verification and remaining limits

The lower-pressure candidate loaded on the exact170 save with full world and
Gold parity, native default improvement30, the new work callback and zero care
errors. All work strategies were initially inactive because no earlier waiting
age was invented. Its saved-turn build/Builder recommendation records were
identical to the original sample. Even after a cold reload, these may be cached
or serialized; no fresh AI turn or successful behavior change is claimed.

Evidence: `guidance-v2-score-probe/native-calibration-verification.json`,
`recommendation-comparison.json`, and `final-restoration.json`. The additional
native-guard probe is separately journaled under `guidance-v2-native-guard-probe`.
Tests cover actual Lua5.1 callbacks/aging and SQL replay/retirement of the former
capacity callback and extra Builder attachment. No new outcome game has been run.

Next outcome validation should measure actionable-wait distributions, strategy
active time, repair versus resource-replacement outcomes and producer material
fulfillment. District-site opportunity-cost response remains unresolved. A larger
soft number is not an evidence-based substitute for verifying that decision path.

The final native guard check placed temporary private last-Base marks on an owned
empty plot934, district plot1011 and valid material plot1154. Native yield deltas
were0,0 and160 respectively. Restoring the original properties restored all three
yields; fresh world/treasury parity passed and no AI turn advanced. This verifies
actual stale-mark filtering, not a forecast or decision-level preservation effect.
`guidance-v2-native-guard-probe/native-guard-verification.json` is the receipt.

Final validation:25 material-care checks (23 actual Lua5.1,2 SQL migration/replay)
and4 offline log reconstruction/censoring tests pass; `git diff --check` passes.
Both new diagnostic loads were separately bounded to the exact170 save, without
AI-turn replay, reconstructed foundations or economic effects. The second helper
reused its installation-delta variable for yield deltas and failed during file
cleanup after normal native exit. Its raw error is preserved. Independent cleanup
verified all Civilization processes absent, restored only the four known package
deltas and matched every original510 hash. Original144preferences/autostartfalse
were verified. The original stopped game and automation remain closed. This
candidate is source-only; no outcome improvement or deployment is claimed.
