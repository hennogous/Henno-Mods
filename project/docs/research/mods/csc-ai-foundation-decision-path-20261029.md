# Unfinished Quarter production decision path — 29 October 2026

## Result and scope

The first decision-tracing roadmap investigation has identified explicit native
support for finishing existing districts. A placed Quarter is eligible for a
different legality path from a new placement, and the forecast accounts for
production already invested. It still needs a competitive candidate/contract
and a queue opportunity. Placing a foundation does not itself establish an AI
construction commitment or move it ahead of the current production item.

This increment combines current-DLL reconstructed code and assembly review with
closed historical evidence. No game was launched, AI turn advanced, gameplay
input changed, native hook installed or RH file edited. These findings do not yet
explain a complete runtime winner with every competing score observed.

DLL SHA256: `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
All addresses below are RVAs for that binary. Historical linker-map names help
navigation; inferred signatures, field names and enum meanings require separate
verification. The raw exports retain assembly beside reconstructed C.

## What happens before a foundation can win

1. **The existing plot can enter the evaluator.** Per-plot evaluation at
   `3e2aa0` distinguishes a district already on the candidate plot from a new
   placement. For the inspected single-instance flag branch, the existing
   district must be on that exact plot. When the plot's district type already
   matches the candidate, the ordinary placement-validator call is skipped.
   Definition flags, negative effective preference, `CanEverZone`, ownership and
   time/score gates still matter. This is admission, not guaranteed selection.
2. **The forecast uses remaining work.** `GetDistrictProductionCost` (`fd470`)
   uses a positive stored cost from the existing district when available.
   `GetTurnsLeft` (`fe610`) supplies accumulated district production plus queue
   carryover to `ComputeTurnsLeft` (`605dd0`). The latter subtracts that amount
   from cost converted to Q8 before dividing by production. Positive production
   with no remaining work returns one turn in this helper, not zero. This path
   therefore does not simply charge the foundation's full cost again.
3. **A district candidate must become an AI request.** `GetBestDistrict`
   (`3e4a50`) scans cached eligible plot/type values. A live plot reservation can
   impose a score threshold; equal district candidate scores can invoke random
   tie-breaking. `CheckForDistrict` (`3e0ee0`) also requires no existing tracked
   district tree and an applicable configured behavior tree before creating a
   request. A foundation visible on the map is not proof this step occurred.
4. **A managed contract must reach an empty-queue selection.** `QueueNextBuild`
   (`3e8190`) returns for a human-controlled owner or occupied queue. In the
   inspected route it considers contracts in raw state 3, validates them,
   invokes Update, and retains the greatest signed score at offset `+158`.
   Equal contract scores keep the earlier candidate here; this differs from
   the district-candidate random tie-break above.
5. **The contract has a conditional advantage over building fallback.** The
   selected contract is compared with the best unit score minus one Q8 unit
   (`0x100`) and best project score, then its Execute is attempted. The best
   building score is compared in the later ordinary fallback, not that final
   contract gate. A valid district contract can therefore reach construction
   without directly defeating the best ordinary building score at that gate.
   Failed admission, validation, competition or execution still prevents it.
6. **Execution checks legality again.** The `CanZone` implementation at `f97b0`
   explicitly calls `IsComplete` for an existing instance. In the relevant
   definition branch, an incomplete district with wildcard coordinates or the
   matching stored zoning plot can succeed before the new-site gates. This is
   a separate legality route; the per-plot evaluator above does not call this
   implementation. Do not conflate the two call chains.

## Continuing and replacing work

The previously traced contract updater (`3fa5e0`) retains the larger of previous
stored score and the current cached present value in its inspected branches.
An already accepted contract can therefore behave differently from a fresh
candidate after an input changes. This is not a lifetime invariant across every
writer or cancellation path.

Normal production selection is not a global re-ranking that replaces the queue
every turn. `UpdateWorkingContract` (`3ea990`) has separate validation-failure,
update-failure and continuing-state branches. Threat-driven interruption is
another route (`3ea150`), not a generic finishing preference. For a useful
intervention, distinguish waiting for an occupied queue from losing an actual
empty-queue competition.

Raw state is read at contract `+b0`; assignments through its wrapper at `+a0`
must not be labelled request-priority changes merely because a generic mapped
helper alias contains `ControlPriority`. Enum labels remain unconfirmed.

## Actual archived case: Nuri Bakers

The preserved V7 source100 contains player1/city524295 Nuri's assisted Bakers
at plot1862, placed at99 and still incomplete at100. Closed logs and original
episode identity establish this sequence:

| Turn | Observation |
|---|---|
| 99 | Assisted Bakers foundation placed. |
| 100 | Tailors construction selected later in the AI interval. |
| 102 | Tailors completes; Ancient Walls selected. |
| 103 | Bakers contract2139 submitted, logged value10206.0. |
| 103–107 | Walls production records accumulate7.5,14.7,21.9,31.5,42.3 against cost40. |
| 107 | Walls completes; Bakers contract2139 selected. |
| 108 | Native IsComplete readback observes Bakers complete. |
| 109 | Construction log records contract COMPLETED. |

The nine-turn placement-to-physical-completion interval divides into eight
turns before selection and one after. Four of those preselection turns are
between the first recorded proposal and selection. This supports queue waiting
as an important diagnosis in this case; it does not establish why all earlier
alternatives won, or imply finishing Bakers earlier would have been preferable
to defensive Walls. Physical completion and the later contract event are kept
separate.

The turn100 save predates the turn100 Tailors selection. Its exact saved current
queue, accumulated Bakers production and runtime type/object indices were not
captured; they remain unknown. Do not assume the source has zero progress or
Tailors already queued. The construction CSV lacks plot/city-ID columns; the
selection join uses the unique player/city-name to city-ID history and original
foundation identity, with later same-owner physical confirmation. A future
current-package replay is not guaranteed to repeat this historical sequence.

Raw lines, source hashes and save metadata are preserved in
`H/foundation-decision-cases-20261029/nuri-case.json`; the source save SHA is
`2982b00a4c4d0c536ac7232e88c2c2b0fc2e56fd2ee7842aa22ad47b2ffb065d`.

## Implications for CSC

- Retain native construction. We have not found evidence that directly placing
  a legal foundation inherently makes it invisible to the AI.
- Measure the delay in stages: placement to candidate/request, request to queue
  selection, selection to physical completion. One placement-to-completion
  number cannot distinguish a planner problem from existing commitments or low
  production.
- A targeted finishing policy should first address a demonstrated missing or
  losing contract. Larger `AiFavoredItems.Value` numbers are not a supported
  remedy in the already-traced boolean Districts preference handler.
- Do not change global task bias, force production orders, or add real yields
  based on this static result. Existing work may be valuable and should not be
  interrupted merely because CSC placed a foundation.
- The engine already considers invested production in this route. Any new CSC
  finishing bonus must add useful chain value, not blindly duplicate a presumed
  missing remaining-cost calculation.

## Next bounded observation

Use a preserved save containing an original-owner incomplete assisted Quarter
and a known competing queue. Capture actual native type indices and complete
target identity before interpreting pointers. Observe the cached target score,
candidate output, contract identity/state/value, queue occupancy, validation and
Execute result, then correlate the actual queue and physical completion. Capture
all relevant competing scores at that decision boundary, or mark the explanation
incomplete. No forced empty queue, order, preference mutation or new world.

Validate Windows argument layouts and pointer bounds before hooks; a mapped name
alone is not a safe observation specification. Use the maintained controller,
one native owner, bounded events/turns, explicit non-exposure and exact package/
preference restoration. A current-package load is a disclosed rebase, not an
assumption that historical selections must repeat. No game is dispatched by this
document.

## Reproduction and review

`A = C:/Users/Shadow/Desktop/Codex/csc-native-ai-analysis-20261028`:

- `foundation-decision-exports/`: CanZone, GetTurnsLeft, CheckForDistrict.
- `foundation-cost-exports/`: GetDistrictProductionCost, ComputeTurnsLeft.
- `evaluation-exports/CityEvaluationJob_Execute_FirstCallee_3e2aa0.txt`.
- `citybuild-exports/`: GetBestDistrict, QueueNextBuild, UpdateWorkingContract,
  DoTurn, DoTurnActivate and existing contract evidence.

Independent review: `H/foundation-decision-review-20261029.md`, where H is this
thread's visualization workspace. The reviewer verified assembly branches and
identified the important separation between evaluator admission and CanZone.
The evaluator's raw instance byte `+3f8` was not independently named in that
review; its exclusion branch must not be treated as a new verified public field
layout. `CanZone` independently calls the named `IsComplete` function.

Related: [roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md),
[earlier production analysis](csc-ai-native-production-analysis-20261028.md),
[symbol resource](csc-ai-gamecore-symbol-resource-20261029.md),
[producer live-effect result](csc-ai-producer-live-effect-20261029.md).


## MCP follow-through: request creation and city acceptance

A second read-only pass used the directly connected GhidraMCP on the same
SHA-pinned DLL. It connects the shipped behavior-tree inputs to the district
initializer, manager submission and receiving city. It adds no runtime exposure
or tuning change.

### Priority, value and city are separate inputs

The shipped Base/Assets/Gameplay/Data/BehaviorTrees.xml defines the normal
**Build City District** node24 using the Build Unit node type. Its bindings are:

| Input | Shipped binding | Meaning established here |
|---|---|---|
| Defn2 | City | Required city decoded from the request. |
| Defn5 | Literal4 | Build Priority. |
| Defn6 | Needed District | Desired district type. |
| Defn7 | Location | Requested coordinates. |
| Defn8 | Present Value | Separate decoded value input. |

Node23's literal15 is the Contract Manager **Turn Limit**, not priority15.
Source lines251–259 define the build-node inputs; lines358–362 define the
manager turn limit; lines1219–1229 bind this district tree. The separate
district-charger branch must not be confused with normal production.

BuildFromCityNode::Execute (55ba40) reads separate priority and value bindings.
Its district route calls Initialize (3f9200), which writes district, coordinates
and required city, converts the supplied integer value to Q8 by shifting left8,
and forwards priority to the base initializer. Unlike the unit overload3f9300,
this district overload does not add the per-unit GrandStrategic preference.
These facts do not establish that changing priority changes a district's final
queue score or that all priority consumers have been reconstructed.

Assembly confirms the Windows entry layout: RCX contract, RDX output handle,
R8D district, R9 coordinate pointer; stack arguments at entry RSP+28/+30/+38/
+40/+48 are player, control owner, priority, value and required city. The
decompiler's one-byte final parameter is misleading: the copy helper at2ca0f0
reads four bytes. This is a static layout finding, not a runtime hook approval.

### Submission becomes a city offer only after validation

Manager::SubmitContract (403c70) places a newly submitted contract in raw state2
and dispatches its acceptance signal. A positive subscriber result changes it
to raw state3. CityBuild::Initialize (3e64e0) registers ReceiveContract (3e9500)
on that exact signal at the player's component+798, signal+270.

ReceiveContract calls the virtual Validate slot+98 against that city. Failure
returns false; success appends the handle to the city's contract vector and
returns true. District Validate (3fa8e0) rejects a mismatching required city
unless the field is-1. Thus this normal district tree supplies a city-specific
request, even though other kinds of contracts can be available to any city.
Acceptance is still separate from the later QueueNextBuild winner and Execute.

The district validation path also has defensive-only, working-contract/current
district, turn-limit and CanZone-result checks. Some result fields remain
unnamed; do not reduce this path to the CanZone return boolean or label those
fields by guesswork. Final BuildDistrict legality remains separate.

### A narrow queue-clearing exception

ReceiveContract contains a queue-clear branch that qualifies the earlier
empty-queue description. Assembly at3e95bd–3e9608 requires BOTH:

- incoming contract score+158 exceeds CityBuild's default-build present value;
- current turn is at most the city's founding turn plus1.

Field names are independently established from constructors: CityBuild3db2f0
names m_defaultBuildPresentValue (raw+3c8); City::Instance127de0 names
m_iTurnCityFounded (raw+14d0); Game::Instance639160 names m_iCurrentTurn
(raw+c0), accessed through951550/b8aa68. These are pointer-sized constructor
indices converted to byte offsets, not names inferred from generic helper aliases.

This is a newly founded-city exception, not a general higher-value-contract
preemption rule for established cities. It does not explain away Nuri's observed
Walls interval and is not a proposed CSC queue-clearing mechanism. Other
interruption routes still require their own conditions.

### What RH changes here

The inspected RH5.097 subscription3792072489 does not directly modify these
district-tree bindings. Its tree edits inspected here concern settlement and
military operations. RH changes upstream district valuation, including
PSEUDOYIELD_DISTRICT DefaultValue18 and a conditional RH_DistrictPush
PseudoYields entry Value150. Those are separate from the build priority4 and
the Districts-system boolean preference handler.

This is a pinned source audit, not a new merged-runtime database observation or
an exhaustive proof against arbitrary dynamic SQL. RH files were read-only.
Exact paths, source lines and hashes are in
H/district-tree-controls-20261029.json and the companion Markdown report.

### Practical consequence and next useful boundary

We can now distinguish a foundation never becoming a request, a request rejected
by its city, a valid offer waiting behind production, and an offer losing the
empty-queue comparison. None is fixed merely by calling every number priority.

The next bounded passive observation should record target admission/request,
ReceiveContract result, raw state/value/priority, queue and founding turn, and
the actual competing unit/project/contract values at selection. Use an existing
original-owner foundation; do not clear the queue or raise a global weight to
manufacture exposure. This is preferable to a broad priority4 change affecting
all districts. Existing same-type district preference and meaningful site/chain
valuation remain possible inputs, but their useful effect requires the measured
decision margin. No finish-first shipping change is justified by this pass.

Raw current-DLL exports: H/foundation-mcp-path-20261029.json and
H/foundation-mcp-game-constructor-20261029.json. These preserve decompilation,
ReceiveContract/district-initializer assembly, and constructor field evidence.


## Subsequent native decision boundary — closed 29 October

The [bounded observation and independent audit](csc-ai-foundation-observation-20261029.md)
now establish exact target request acceptance at103/105 while Builder production
continues, then selection/Execute at109 with an empty queue. Physical completion
is censored at110. The current-package sequence differs from the historical Walls
case; no replication or causal tuning claim follows. The report preserves competing
values, identities, material conflict and full cleanup. The proposed passive
observation above is completed, not an outstanding instruction to replay it.
