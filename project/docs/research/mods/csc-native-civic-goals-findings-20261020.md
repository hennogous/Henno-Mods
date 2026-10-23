# CSC native civic research goals: findings and stopping point

20 October 2026. Authorized investigation using CSC, Real Strategy and AI+ as
source leads. The accepted CSC gameplay baseline remains unchanged. The automatic
series stopped at its conditional-control gate; no natural validation games were
launched and no candidate was deployed.

## Demonstrated mechanisms

| Route | Measured result | Practical limit |
|---|---|---|
| Trait-owned Civics favorite | Approximately 50% target-score increase; one CSC-only pair changed Germany's natural choice to Divine Right | Static preference; Value10000 produced the same scores as Value0 in the historical test |
| Strategy-owned Civics favorite | No score response in clean stock/custom comparisons despite verified callbacks and Following | Source wiring does not establish consumption by the research system |
| List owned by both trait and strategy | Target134.1 with strategy OFF and ON | Trait preference was not gated by the strategy |
| Native construction prerequisite goal | Accepted civic requests, large targeted score changes and changed natural research | Typed target came from a disposable native prerequisite, not a CSC Service requirement |

The native goal pair used fresh matched Medieval/Online/Prince/Small/Continents/
Standard worlds, map830102/game940104, and analyzed rounds71–90. Both arms used a
temporary Bakers/Divine Right prerequisite and identical construction demand.
Only the Build City District/node8 Desired Civics binding differed.

At turn72 only two of55 matched civic-score records changed: Phoenicia
168.4→11098.4 (+10930), Vietnam194.0→11353.0 (+11159). Both increments equal the
native district request's recorded Present Value. Four of five AIs selected
Divine Right and three completed it, versus zero selected/completed with the
binding disconnected. Germany, the preregistered primary player, received a goal
but did not select the civic by90. Other players are secondary evidence on one
artificial matched map, not independent replications.

## Conditional gate and contract lifetime

The shipped LUA Script Condition node can invoke a GameEvents callback. The
official Civ Royale example writes `targetInfo.Extra=1/0` and returns true. That
output shape worked in our diagnostic construction tree.

The first time-phase probe recorded194 callbacks:76 ON successes and118 OFF
failures. Existing requests could remain behind an eight-turn Contract Manager;
the child condition and goal appeared as READY while the manager waited. READY
rows are retained state, not fresh submissions.

One bounded follow-up changed only the manager's Turn Limit8→1 and added callback
argument instrumentation. It recorded213 callbacks:81 ON successes and132 OFF
failures. No fresh Divine Right submission occurred in either OFF phase, even
when checking all behavior trees. Early boosts cleared, but later high target
scores persisted through the second OFF phase. Phoenicia was15944.9 at84 and
Vietnam26410.3, while the condition was false. We could not establish reliable
withdrawal of every incentive or identify all retained contract ownership.

The first12 captured calls supplied an empty result table and no additional
arguments. No player ID was observed. This contradicts relying on the node's
short description as a sufficient per-player callback contract; it does not prove
that every possible way of obtaining player context is unavailable.

Both probes completed80 observations over rounds71–86, endpoint88. Each passed
native/replay/script/fixture checks,53source/122installed/46reference archive
hashes, current pins, and restored144 mod preferences/autostartfalse/installed
SQL and Lua. The baseline mod source was not changed. No Civ crash occurred.

## Remaining gap and why the series stopped

A release implementation still needs to create a typed goal for a particular CSC
Service, associate it with the right player/material opportunity, and withdraw it
without suppressing unrelated native construction goals. Neither the artificial
prerequisite nor a global gate is suitable for release. The gate branch's one
bounded lifetime follow-up was consumed; further ungrounded rewrites were stopped.

Build City Building exposes Needed Civic but its captured Add Goal Tech/node3
Desired Civics tag is empty. Actual Bakery/Tailor prerequisites are Guilds and
Cafe/Fashion House prerequisites Humanism. That offers a separate building-unlock
lead, but it does not expose Naval Tradition/Divine Right Services whose unlocks
are modifier requirements. No supported direct goal creation/cancellation API was
found in the inspected sources and shipped debug panels. This is a scoped finding,
not a claim that the engine cannot support one.

Material lifecycle/reload/duplicate tests, prerequisite-path tests and the six
natural validation games were therefore not run. Static favorites and native
construction research goals are proven separately; a safe material-aware Service
goal implementation remains unproven.

## Evidence and provenance

Study root on Shadow: `Desktop/Codex/csc-civic-unlocks-20261020`.

- `t2-district-goal-v1/post-run-audit.json` and `score-and-unlock-summary.json`.
- `t3-gate-probe-v1/post-run-audit.json`.
- `t3-gate-probe-v2-limit1/post-run-audit.json`.
- Every arm retains actual source/installed files and hashes, native database,
  scoped logs, observations, settings and restoration checks.
- Exact controller versions: `civic-unlock-t2-native-district-civic-goal-v1`,
  `civic-unlock-t3-native-lua-condition-lifetime-v1`,
  `civic-unlock-t3-native-lua-condition-lifetime-v2-limit1`.

See the [experiment ledger](csc-civic-unlock-experiments-20261020.md) and
[preregistered plan](csc-civic-unlock-test-plan-20261020.md) for earlier stages,
controller repairs and preserved historical limitations.
