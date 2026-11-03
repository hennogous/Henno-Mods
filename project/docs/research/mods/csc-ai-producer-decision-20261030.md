# Actual producer valuation and choice — 30 October 2026

## Result

One actual AI interval110→111 exposed the target building's fresh native
valuation, private-yield read, best-building preference and eventual queue entry.
AI3 Kobdo/city458758 selected Textile Workshop147 at native110 through Default
Specialization. Its logged value4102.2 is corroborated by the first queue item
at inactive111. This is actual production selection, not physical completion.

The planned enabled/disabled comparison did **not** complete. A diagnostic refresh
journal reached its256-record cap after the interval and its guard stopped the
driver; no off arm ran. We therefore establish the observed consumer and choice
path, not the marginal score/choice effect of the private+80 or empire benefit.
No new tuning coefficients or live planner policy were shipped.

## Observed chain, with identities and units

Target: player3, Kobdo458758, Tailors plot2781 at43,37, Workshop native147,
private yield7. Initial Workshop is unbuilt and legal, cost40; material facts
Base1/Spec0/configured-AI-role1. Source assistance history is preserved and new
assisted actions are suspended in the common study setup.

| Native observation | Actual evidence |
|---|---|
| Input delivery at inactive110 | Supported Base1→0→1 control; bound state Met/NotMet/Met and native stored adjustment80→absent→80; UI potential stays cached80. |
| Fresh building valuation | NetValue call73, entrysequence145, caller RVA3e3ee2; nested getter74 sequences146–147 returns private80; NetValue leave148 returns480453 signedQ8 =1876.76953125. |
| Best-building decision | Queue99 contains Best100 at sequences198–199. Native effective preference+1; cached525085Q8 becomes1050170Q8 exactly2×, or4102.2265625. |
| Actual selection | AI_CityBuild native110 selects the Textile Workshop, source Default Specialization, Value4102.2. |
| Physical corroboration | Inactive111 independently has Workshop147 first in the same city's queue. This is not evidence that construction finished. |

The fresh NetValue480453 and later cache525085 are separate observations. Their
transition was not captured; do not equate them or assign the difference to the
private yield. Other building NetValues were observed but legality, discount
scalar and complete choice context are not exposed, so they are not a complete
alternative ranking. Inherited Workshop contract2304 had previously been offered
with the forecast enabled; retained maximum contract values remain a general
counterfactual caveat, not a proved explanation for this default-specialization
selection.

The actual caller3e3ee2 also explains an earlier instrumentation blind spot:
the older probe admitted only return3e419f. Both call sites exist in the same
exported city evaluation routine. Existing assembly at3e3edd calls52a050 and,
after3e3ee2, stores its returned value into the building-indexed array at+28.
This establishes a valid observed route; it does not reconstruct the later
cache transition or all score components. The static export is
`csc-native-ai-analysis-20261028/evaluation-exports/CityEvaluationJob_Execute_FirstCallee_3e2aa0.txt`.

## Experimental limits and preparation history

All attempts use the same source110 bytes, SHA256
`62e623f381ffd8e8ece219b6a87c575dbfebaea34ef6fd4c8dcb6c7ef7c0e52c`,
current604-file package and XP2 DLL
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
No new world or forced production/order/research/building/improvement/unit grant.
RH files remain read-only. The sole temporary installed delta is a target-only
diagnostic branch controlling the existing Base fact, restored after Civ exits.

- Run01: Desktop-path load ACK without Gameplay readiness. No census, hook,
  treatment or AI turn. A similar known path failure had already been documented;
  using it as the load target was avoidable setup work, not AI research.
- Run02: byte-identical native-save-directory input loads110. Strict comparison
  with the archived boundary stops on exactly one observer0 Builder3342344 at53,40:
  remaining movement2 versus archived3. All other Core, full UI and economic
  fields match. Maximum movement and the cause of the difference are unobserved.
- Run03: the entire actual post-load Run02 state is explicitly declared as the
  reference, without field masking or forced movement restoration. Initial and
  final known state match; paused live delivery works. Python then assumes the
  pre-AI CityBuild CSV exists and fails before an AI turn. This is a driver bug.
- Run04: same source and complete declared post-load reference; uses the new
  maintained log-boundary helper. Entire initial state matches. The finite core
  reaches inactive111 and the consumer/choice above is captured. The diagnostic
  journal cap then stops the intended pair.

Historical exact full-world parity is false and is not claimed. The actual
reference is pinned Run02 `on/boundary-110.json`, SHA256
`ac24b2ca9f14d2e19809c35040dd2c8be32b591ca71dba485f4ba2bcd559b382`.
Neither the reference amendment nor the first three attempts followed any
observed AI outcome or intervention. They do not provide extra treatment arms.

The256 recorded target refreshes all have natural1/desired1. The diagnostic
marks itself failed and disarms at its cap, but Base1/Spec0/role1 and an empty
bridge-error collection remain observed. Its cap time relative to the native
calls was not recorded. Do not infer a source-fact change from that generic flag,
or claim sustained off-input control across AI play: no off arm ran.

## Controller and instrumentation findings

The maintained finite-play core completed the actual interval. Earlier launch,
parity and missing-log failures were in the driver around that core. All native
processes exited normally; these failures are not evidence of a native crash.
No known popup or open diplomacy session explained the long active interval;
playback ACKs were guard checks, not actual release requests.

Activation to the first inactive111 reply took444.73 seconds; the three separated
handoff samples completed at470.55 seconds. The observer entered GetYieldChange
2,509,007 times, accepting37 and rejecting the rest after hook entry. It retained
122 complete paired records overall with zero errors, drops, identity changes
or pending pairs. Broad hot-function interception is a credible overhead source,
but its contribution was not isolated against an unhooked same-state control.
Normal completion does not establish observer neutrality.

Full games should default to light capture. Short probes should target the
consumer/call site rather than send millions of irrelevant calls through the
observer. Record total intercepted calls as well as retained records. Diagnostic
detail saturation should be distinguished from an actual invalid input; the
current stop guard was safe but prevented the marginal comparison.

## Shared source improvements and next boundary

- `full_game_controller/log_capture.py` now records absent initial AI logs
  explicitly, while requiring actual post-play files and the same byte
  generation. Six meaningful regressions and11 driver-integration checks passed.
  It does not connect to Civ or change finite-play behavior.
- The first offline `ai_tuning/chain_coordinator.py` integrates site evidence,
  existing requests, material dependencies and competing plot claims.35 relevant
  checks passed. It does not rank, spend or alter the live AI host.
- The user confirmed [shared session hardening for full games and probes](../../integrations/csc-native-test-controller.md).
  Common launch/load/ownership/settings/log/cleanup operations need maintained
  composition; full games and probes retain their distinct policies. The shared
  log helper exists; the complete common session layer is not yet implemented.

Retain the producer forecast as a consumer-observed research input; do not call
its current amount calibrated, increase it from this result, or infer that it
caused the Workshop choice. Continue against the supply-chain objective, not a
goal of collecting exhaustive engine internals or maximizing Quarter count.

## Closure and reproducible evidence

Run04 native8572 and observer8188 exited0. Held worker5116/session79238 exited1
from the diagnostic guard after the observed AI interval. Exact145 mod-ID flags,
148 subscription entries and AutoStart=false were restored. All604 original
installed hashes,343 source pins,12 dependencies and input hashes verify, and a
fresh owner inventory is empty. Earlier attempts have their own preserved audits.
No additional native attempt, extension, off arm or automation was started.

At cleanup111, target facts, persisted economics and all city queues match the
first111 capture. Full final UI equality is not claimed: observer0's research UI
changes from technology15/progress71.00390625 to technology−1/no progress field.
The cause is unproved and no research command was issued. This does not alter the
producer queue corroboration, but remains a recorded publication/state caveat.

Study: `Desktop/Codex/csc-native-producer-decision-20261030/run-04`.
Primary indexes: `native-observation-index.json`, `performance-observation.json`,
`operator-summary.json`, `observed-building-net-values.csv` and the raw trace,
CityBuild delta and boundary111 to which they point. Independent closed audit:
H/`producer-decision-run04-audit.json` and `.md`. H is this thread's visualization
workspace. A successful closed audit verifies evidence and restoration, not a
successful completed counterfactual experiment or AI efficacy.
