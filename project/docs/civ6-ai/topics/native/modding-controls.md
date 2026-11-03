# Modding controls and the boundary of arbitrary incentives

Choose the native consumer before choosing a number. SQL and Lua offer useful controls, but each has particular units, scope and timing. A private property named “desirability” does not create a score reader.

## Established forms

| Control | Useful scope | Main limit |
|---|---|---|
| Real yields, costs, housing, maintenance and building unlocks | Economic value | Changes gameplay as well as AI. |
| Native district adjacency rows | Differentiate district sites and types | Uses predefined spatial predicates. |
| Registered custom yield in adjacency | Author a purpose-specific weighted channel | Is not automatically AI-only or economically inert. |
| Districts favored preference | Type-wide admission/multiplier | Sign-based in the inspected path. |
| Yields / PseudoYields lists | Benefit-category importance | Different consumers and units; a name alone creates no consumer. |
| Boolean Lua strategy condition | Broad state-dependent motive | Does not return a numeric candidate-plot score. |
| Explicit orders/planner | Direct chosen action | A different control mechanism from native scoring. |

Native Adjacency_YieldChanges has integer YieldChange, TilesRequired and specific district/improvement/terrain/feature/river/resource/wonder predicates, Self and research gates. AdjacentResource is Boolean; AdjacentResourceClass accepts one native class string. There is no standard ResourceType or arbitrary TypeTag-set column. Multiple rules can be attached, but arbitrary AND/OR or multi-ring formulas must not be assumed. [AI-N033]

The [district incentive report](../../../research/mods/civ6-district-choice-placement-and-incentives-20261103.md) ties these controls to current schema and scoring. [District choice](district-choice.md) explains why alternative-land deductions and later processing prevent treating a cue as an equal final-score increment.

Time preference is also consumed: AI_DISCOUNT_RATE has a shipped default 2.0, is adjusted for game speed, and feeds fixed-amount/income-stream helpers. The exact piecewise arithmetic should be traced rather than replaced with an assumed exponential formula. This is an engine control, not a calibrated CSC recommendation. [AI-N050] See the [native production analysis](../../../research/mods/csc-ai-native-production-analysis-20261028.md).

## Lua can gate a preference

The shipped strategy pattern accepts a player-level Boolean from a Lua condition. Such a condition can calculate an accessible-state opportunity and switch linked preferences. Its transmitted result is not “+137 for this district at this plot.” A broad type preference can affect several cities and sites. [AI-N034]

A positive ordinary numerical Lua callback for every district/city/plot candidate was not established in the inspected schema, primary examples and bounded API catalog. This is a bounded interface finding, not engine-wide impossibility.

## Private does not mean inert

A hidden yield without Gold/Production conversion can still affect automatic citizen allocation. The October 24 source-load comparison observed a worker moving onto private-yield Flax and a corresponding real city-output change. That diagnostic is not a universal formula for every custom yield, but it rejects automatic human-inert/AI-only assumptions. [AI-N035]

The older “inert virtual human output” description is **superseded**. [AI-N047] Keep actual gameplay effects, presentation hiding and AI normalization separate. See the [citizen-effect evidence](../../../research/mods/csc-ai-private-resource-citizen-effects-20261024.md).

## A fully custom per-site formula needs a bridge

A native extension could in principle introduce F(player,city,district,plot,state) at a verified value/cache boundary. Selection, cached present value and downstream request valuation need a coherent contract; request priority and extra present value are separate fields. Merely replacing a reported winner can leave downstream values inconsistent. No such score extension was implemented or validated in the district study. [AI-N036]

The subsequent [extension feasibility investigation](native-placement-extension.md)
identifies a concrete pre-cache candidate boundary and additional consumers.
It also finds zero early-outs, serialized scores and retained request values that
an implementation must handle. A fixed single-entry native prototype now passes
isolated Win64 checks and a matched one-save trial: one+256 Q8 input reached
cache/winner/present value and increased the new request's logged value by1.
The same candidate already won the baseline. Arbitrary-policy authoring and
release integration remain open. [AI-N061] [AI-N062]

A separate integration problem is submitting a planner-selected economic job. Native build/repair consumers exist, but the inspected operation/tree routes did not establish a general typed player/city/plot/improvement payload writer. Target/rally coordinates and externally reported callbacks are insufficient proof of that bridge. [AI-N037] See the [material-job feasibility assessment](../../../research/mods/csc-ai-native-material-job-feasibility-20261030.md).

## Historical research goals: responsive does not mean release-ready

The October 20 artificial construction-prerequisite experiment demonstrated native civic research requests, changed scores and some changed natural research. It did not connect ordinary CSC Service modifier requirements to safe goal creation/withdrawal. Later gate tests left ownership and reliable cancellation unresolved. [AI-N038]

The behavior-tree GameEvents result channel (targetInfo.Extra) in that research is distinct from the player-level Boolean strategy condition above. Empty callback context tables must not be given an invented player identity. The [civic findings](../../../research/mods/csc-native-civic-goals-findings-20261020.md) and [community-route review](../../../research/mods/csc-ai-community-native-job-routes-20261030.md) preserve the exact local/external evidence boundaries.
