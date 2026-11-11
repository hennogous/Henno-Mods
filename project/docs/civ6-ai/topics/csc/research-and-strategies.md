# Research guidance and strategy lifecycle

For the wider valuation context, see [empire needs](https://github.com/hennogous/civ6-ai/blob/main/references/engine/empire-needs.md)
and [modding controls](https://github.com/hennogous/civ6-ai/blob/main/references/engine/modding-controls.md). A research-specific
working consumer and a district preference can have different units and limits.

Research work moved from named favorites to candidate-score controls, construction goals and dormant-effect forecasts. Locate the working consumer and natural decision boundary before increasing a number.

```mermaid
flowchart LR
 C[Readiness callback] --> S[Strategy Following] --> V[Value consumed] --> N[Next civic selected] --> F[Civic completed] --> E[Eligible chain operates]
```

## AI-C018 — Following did not establish dynamic civic consumption

Clean sham/stock-Naval/custom-CSC arms had 400 identical civic-history rows each through 150 and 59 natural completion boundaries per arm. Retrospective analysis matched 5002 candidate keys per arm, including 327 Naval keys. No logged target-score or choice response was observed.

Scope: One synthetic Medieval-start fixture with five AI players; earlier 180/120 and fixed/extreme controls provide supporting history.

Limits: The planned Culture-weight positive sample was unavailable, not a measured zero. These are bounded route nulls without a working positive control, not proof that all civic preferences fail. Failed research-clearing assumptions and residual lists remain documented.

Sources: [Clean comparison](../../../research/mods/csc-ai-clean-strategies-20261020.md), [candidate-score audit](../../../research/mods/csc-real-strategy-research-review-20261020.md), [earlier priorities/audit](../../../research/mods/csc-ai-research-priorities-20261019.md).

## AI-C019 — Trait preferences and construction goals worked separately

Trait-owned favoring raised a target civic score about 50% in the tested context. A temporary construction prerequisite delivered PresentValue-sized research boosts: four of five selected and three completed Divine Right versus zero in the disconnected arm.

Scope: Disposable matched Medieval mechanism controls, not ordinary CSC Service dependencies.

Limits: The typed target came from an artificial prerequisite. Safe material-aware goal ownership, submission and complete withdrawal were not established. Callback tables lacked a player ID in the captured generic Lua-condition calls.

Sources: [Native civic-goal findings](../../../research/mods/csc-native-civic-goals-findings-20261020.md), [experiment ledger](../../../research/mods/csc-civic-unlock-experiments-20261020.md).

## AI-C020 — Dormant forecasts delivered selective research value

A contradictory economically inactive CivicModifiers benefit plus private Yield strategy produced boosts for material-ready Tailors and zero for no-Quarter/no-Base controls. Exit variants withdrew value, but finite C 11/C 12 probes did not regain the treatment after supply recovery.

Scope: Controlled civic-modifier diagnostics; actual Service effects were unchanged.

Limits: Diagnostic magnitudes are not recommended weights. UI/human effects, complete lifecycle and natural-game benefit were not release-qualified; repeated arbitrary flag or weight changes were stopped.

Sources: [Influence findings](../../../research/mods/csc-research-influence-findings-20261021.md), [full modifier ledger](../../../research/mods/csc-civic-modifier-tests-20261020.md).

## AI-C021 — Permanent restart failure was an overgeneralization

Later natural guidance showed Germany’s Feudalism/Faires and Greece’s Urbanization re-adopted 20 turns after stopping. This supersedes a blanket irreversible-strategy interpretation while preserving the earlier finite no-restart observations.

Scope: Two qualifying Game 1 return episodes; Games 2/3 lacked equivalent recovery opportunities.

Limits: Twenty turns is an observed delay, not a universal cooldown or a complete lifecycle fix. Continued callbacks, adoption, preference application and score consumption remain distinct.

Sources: [Three-game results](../../../research/mods/csc-ancient-guidance-three-games-results-20261021.md), [earlier finite lifecycle findings](../../../research/mods/csc-research-influence-findings-20261021.md).

## AI-C022 — Research adoption did not establish chain improvement

Three Ancient candidates completed 3735 observations; all 15 AI completed five lower Service civics and six completed Opera. Nine Naval completions lacked direct Naval eligibility. Separately, the long paired test ended with 12 Service flags versus 18 OFF.

Scope: Three natural candidates and a separate Medieval 250 pair.

Limits: Candidate/historical comparisons changed source and resource versions; the long pair’s OFF retained legacy guidance. Research gates often stopped being the endpoint bottleneck because materials, producers and venues did not align.

Sources: [Ancient results](../../../research/mods/csc-ancient-guidance-three-games-results-20261021.md), [long paired comparison](../../../research/mods/csc-long-guidance-comparison-20261021.md), [fixed viewing extension](../../../research/mods/csc-ai-fixed-research-20261019-comparison.md).

## AI-C023 — Boolean strategies are not per-plot score callbacks

Call Lua Function can compute a complex accessible-state condition and switch linked player-level preferences. It does not itself transmit a candidate city/plot or continuous numeric desirability. Source registration and Following do not prove consumption by every downstream subsystem.

Scope: Shipped API pattern, current CSC strategy use and traced consumer distinctions.

Limits: An arbitrary numerical placement formula needs a separately proved consumer. UI previews and plot-property writers alone do not establish native hypothetical evaluation.

Sources: [Current future-economy study](../../../research/mods/csc-future-economy-forecast-20261103.md), [profile source audit](../../../research/mods/csc-ai-profile-source-audit-20261028.md).

[Complete source map](source-map.md).
