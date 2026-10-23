# Native validation limit —23 October observer defeat

The own-first pilot ended partial232 because return player0 was dead. All studied
AIs survived, but native One More Turn was disabled and GetWinningTeam returned
nil. The guarded handler correctly did not call the disabled callback. The shipped
Autoplay panel only lists living return players. A full250 run under this observer
setup remains unvalidated; do not treat this as a completed controller pass or
automatically take over a studied AI to work around it. The run was independently
audited and normally closed with preferences/current510 verified. Final outcome
report is documented in the project own-first research note.

# Opt-in fixed-endpoint continuation —23 October

The new fresh run02 can use `allow_one_more_turn=True` and `study_endpoint=250`.
If a finite operation ends short, the controller checks the shipped EndGameMenu
One More Turn button, actual native winner, current clock/control and exact
positive remaining budget. It calls shipped OnBack once, then reuses only that
remaining budget if still inactive. It never adds SetTurns or resends an ambiguous
action. The feature is off by default. Hidden/disabled UI, defeat without a winner
and wrong phases do nothing; they require preservation and investigation.
264 installed checks+35Lua guards pass, including guard and duplicate fixtures.
Native continuation proof is pending an actual eligible end-game event.

Fresh current game uses own-first shortfall funding, delta capture, unchanged510
and resource pass. Full status/ownership/pins are in the run02 monitor-context.
Earlier dated statuses below retain their original executed-version meaning.

Current performancev9 has accepted native progress beyond90 in the same world.
Installed240offlinechecks+35Lua guardsPASS; small ordinary-round timing sample
is roughly32seconds versus prior58.6seconds. Detailed evidence/limits and corrected
integration issues are in the performance research doc. Full250 remains pending.
All executed sources are frozen while the current worker runs.

# Opt-in faster diagnostic reads and delta evaluation —23 October

Fresh framed discovery is in `full_game_controller.discovery`; pass
`state_discovery=discover_contexts` to the factory. Context IDs are resolved anew
for every command. Busy simulation retains bounded pre-transmission read-only
discovery retries. Command transport and separated handoff samples are unchanged.

`service_planner.boundary_bundle` preserves current chain/full-primary and
research/Builder prefixes in one read-only transaction. `native_delta.lua` plus
`NativeAdapter.delta_mode=True` caches fixed city scopes and candidate routes,
compares native fingerprints each turn and refreshes changed/new/captured scopes;
reconcile unchanged scopes every25turns. Install the delta helper before enabling
the reader. Pass a bundle's Quarter facts to `collect(...,quarters=...)` and its
chain value to `record_chain_metrics(...,value=...)`; recapture after mutations.
Full current data and scheduled first-activation checkpoints remain distinct.
Native precommit/economic receipts are never replaced by cached opportunities.

Read `project/docs/research/mods/csc-ai-harness-performance-20261023.md` for
coverage, provenance, tests, two corrected integration failures and native limits.
Current donated test continues the same process; do not edit any pinned sources
while its worker is alive. Earlier status entries below are historical snapshots.

# Reusable CSC full-game controller

Maintained code: `project/tools/ai_baseline/full_game_controller/`.
Use this shared core for new CSC automated full-game drivers instead of copying
the controller from a dated experiment or chat output. The closed three-world
foundation study used it from game 2 onward; current material pilots also import
this package. Experiment seeds, package changes,
foundation placement, observers and acceptance conditions stay in their driver.

The next-version offline placement policy is maintained separately in
`../foundation_planner.lua`, with `../test_foundation_planner.py` covering its
same-type exclusion and Base-before-total ranking. It is not installed gameplay
and existing study drivers retain their archived planner until explicitly
rebound for a future authorized run. See
`project/docs/research/mods/csc-ai-service-aware-foundation-planning-20261022.md`
for Service-based planning, material retention and acquisition proposals.

## What it provides

- One transmission per command. A single socket receives delayed and fragmented
  replies for a bounded window (at least 15 seconds), retaining partial frames.
  Missing acknowledgment is ambiguous; it never resends a control or mutation.
  Refused or timed-out connection setup can retry at most three times within
  that window, before a socket is obtained or any command is sent. A send failure
  never reconnects. The supplied port may be a callable, resolved after native
  context discovery so the selected context and transport use the same port.
- A classified, bounded retry for its own read-only state query. Native Lua
  failures preserve the reply and fail immediately.
- Three separated native handoff samples and one finite autoplay activation per
  interval. The current contract is at most five turns, with a ten-minute progress
  stall limit and a thirty-minute interval limit.
- Independent handling of the known observer playback contexts. A visible
  `NaturalDisasterPopup` uses shipped `OnLocalPlayerTurnEnd()`. A visible
  `DiplomacyActionView` uses shipped cosmetic `Close()` only, after fresh Core
  observer/active/budget proof. A visible `WonderBuiltPopup` uses its shipped
  cosmetic `Close()` to restore the lens and release the presentation lock.
  It never calls diplomatic `OnClose()`, `AddResponse()` or
  `CloseSession()`. Hidden, human-control, wrong-phase and wrong-budget cases do
  nothing. Each actual request and raw Core/UI phase is archived.
- Command journaling before transmission, saved native replies, and independent
  best-effort research/primary/Builder exports before a driver's Menu cleanup.
  The optional active-command status index retries Windows sharing locks five
  times. A persistent lock is journaled without stopping a valid native command;
  the fsynced journal and unique command/reply files remain authoritative. No
  native command is repeated to repair metadata publication.

It does not launch Civ, host a world, select seeds, install files, place districts,
restart games, choose diplomatic responses or supply a crash watchdog. Those
remain explicit responsibilities of the authorized experiment driver.

## Integration

Add `project/tools/ai_baseline` to the driver's import path and compose with its
validated native interfaces:

```python
from full_game_controller import make_controller

Runner = make_controller(
    ExistingNativeInterfaces,
    diagnostics=diagnostics,
    boundary_decision=boundary_decision,
    tuner_port=4318,
    prepare_output=bind_existing_output_roots,
)
runner = Runner(output_directory)
runner.play(next_target)
```

The base interface supplies `__init__(output)`, `states()`, `state` (context name
to native ID), `seq`, `required_state`, and the experiment's config/capture/scan/
Menu/restore methods. Diagnostics supplies `write`, `sha`, `journal` (fsync), and
`checkpoint`. The boundary function returns `("wait"|"done", inactive_count)` and
rejects overrun or a persistent inactive state below target. `prepare_output` is
optional and binds any legacy output globals before base initialization.

`play(target)` starts from `last_interval_turn` (initially 1). A checkpoint-load
driver must prove its actual source clock, physical/production parity, native DB
and package identity before setting a different starting turn. Do not use this
factory as permission to replay or load an unverified state. If native hosting
returns unconfirmed, verify its native postcondition; do not resend it.

Archive and pin every package `.py` and `.lua`, the driver, observers, planner and
installed package before starting. One worker exclusively owns FireTuner. Freeze
all imported sources while it runs, including shared files used by later games.
Preserve actual clocks and evidence on failure. A process watchdog belongs in the
driver: require exact-PID exit or exception evidence; a reporter title or live
dump without an exception stream is insufficient to claim a native crash.

## Verification and current limits

Run without Civ or a tuner connection, from the repository root:

```powershell
python -B -m project.tools.ai_baseline.full_game_controller.test_offline --scratch '<Codex outputs>' --lua51-path '<existing Lua51 dependencies>' --output '<Codex outputs>/controller-offline.json'
```

Alternatively run `python -B -m full_game_controller.test_offline` with
`project/tools/ai_baseline` as the working directory. The Python tests use fake
sockets and simulated phases. `--lua51-path` uses an existing `lupa.lua51`; it
does not install packages. Without that runtime, Lua coverage is `UNOBSERVED`.

22 October 2026: 24 Python fixtures and 26 actual Lua51 guard fixtures pass,
including wonder phase/visibility/budget guards and actual command/snapshot
output filenames. The earlier packaged version completed audited game 2 at250
on DX11. Game 3 stopped at20 with an unhandled wonder presentation lock; the
wonder handler was added after its controller exited and evidence was archived.
The first human-authorized same-save recovery passed source20 parity and restored
both sites, then a refused TCP connection interrupted observer setup before any
turn advancement or wonder-handler request. This led to the bounded pre-send
connection handling above. Native wonder release→progress was then
confirmed in the next same-save continuation: shipped wonder Close/Unlock and
UI hiding were followed by the same finite operation reaching25, then50. At50
a Windows lock on the status index stopped that earlier writer; the optional
metadata publisher above now handles that separately. The disaster release has
native release→progress
evidence; diplomacy Close ran in game 1 without establishing subsequent full
turn progress. Passing offline checks does not establish full-game reliability.

The same update corrects malformed command and snapshot filename literals from
the original packaging step. Outputs now use `active-command.json` (matching
the watchdog) and `turn-025.json`, etc. Earlier run archives and executed pins
remain unchanged; their snapshots must be indexed by their recorded native turn.
Do not rerun native simulation to repair a filename or reporter assumption.
See `project/docs/research/mods/csc-ai-dynamic-foundations-three-games-20261021.md`
for current run results, same-world continuation provenance and telemetry gaps.
Neither a controller change nor a successful game proves a foundation gameplay
benefit. Keep placement/AI changes and measured outcomes separate in reports.


## Optional next-version Service planner

`../service_planner/` provides a separate policy, normalized observation builder
and coordinator for Service-aligned plans and native gold-spending requests.
Use this shared controller as its runner; do not copy its transport. Spending
is opt-in and requires fresh native facts and Core safe-boundary proof.59offline
checks pass; live AI purchase authority/collector integration remain unverified.
The previous three-world study is closed and is not resumed by this package.

Recovery policy22Oct: recovery is allowed by default unless Henno explicitly prohibits it. Preserve exact-save provenance and observer prefixes, validate native world/production/package/database state, and avoid ambiguous mutation replay. Diagnostic native sessions/context state are now captured before cosmetic teardown. continuation.py restores only whitelisted observer records; it does not load saves or alter gameplay. Finite play command unchanged.

Observer warning recovery: explicitly enabled drivers may dismiss a native-log-verified WARNING_TOO_MANY_TROOPS_NEAR_ME conversation addressed to AI-controlled observer player0, after fresh exact phase/participant/session checks. This uses shipped CloseSession semantics and is recorded as an intervention; it does not choose AddResponse/AddStatement or treaty options. resume_active continues the existing exact finite budget without a second activation. Exit-only DIPLOMATIC_KUDO, DIPLOMATIC_WARNING, DIPLOMATIC_HIDDEN_AGENDA_KUDO and DIPLOMATIC_HIDDEN_AGENDA_WARNING are also supported: the shipped KudosAndWarnings XML defines only CHOICE_EXIT for their KUDO_EXIT/WARNING_EXIT selections. Deals/demands/promises and unreviewed statements remain excluded; the latest message per participant wins. Same-process native validation at turn91 closed the hidden agenda-warning session and reached92 using the existing one-turn budget, with no second activation or replay. Human control/wrong phases do nothing.


### Confirmed skips versus attempted conversation dismissal

The optional warning guard reports an explicit pre-action skip reason. Only an
acknowledged skip without BEGIN/REQUESTED permits a later fresh check, bounded
to four at the normal stall cadence. A send/ACK ambiguity or any actual dismissal
reserves the warning identity and cannot replay. Native92->93 confirmation in
the material pilot followed one dismissal while attaching to the original active
operation, with full physical/UI/database/package parity and no new activation.

When attaching a new source owner, archive inherited log bytes separately and
start current observation offsets at the reviewed boundary. Retain and review
earlier failed diagnostic ACKs; a prior read-only probe traceback must not be
relabeled as a fresh native gameplay error in a later owner. Positive new Lua
errors and native faults remain blocking evidence.


## Connector routing / passive-message handling —version9

Material-first v2 can opt into at most two connector tiles with
`max_connectors=2` and adapter `connector_limit=2`. Required source/Base/Spec
remain at most three, hence five total native buys. Routes stay in revealed
city purchase radius3, avoid foreign/unsafe tiles, and start from actual native
purchase reach. Future adjacency is projected, not command permission. Every
step re-reads native reach/price/ownership/treasury; missing quotes remain unknown
and cannot fund speculative connector purchases. A currently unreachable good
site remains a watch mark for natural growth. Rolling/lifetime caps and durable
one-shot receipts remain unchanged.118 planner/collector/native-Lua fixtures pass.

The collector now records terrain/water/impassability plus native CanProduce
rejection details. Broad scans cache fixed ring-four geometry, and focused
checks iterate only watched sources/materials/connectors; current ownership and
reveal still refresh. Exact current Quarter sites use a district-only native
read instead of a second full-world census. Tests prove focused and cached broad
checks do not iterate the full map again. Metrics label functioning fields as
structural proxies until exact resource-improvement/customer requirements are
independently checked; raw identities remain available.

Shared controller additionally handles the actually observed passive
`DIPLOMATIC_KUDO` session, using the same fresh observer/budget/session guards.
It does not fall back to an earlier warning behind a newer deal/demand statement.
Unknown or choice-bearing messages remain diagnostic, with no response selected.
An explicit active-operation source handoff can archive the live budget and exit
without stopping, reloading or issuing another activation.41 Python+35 actual
Lua5.1 shared-controller fixtures pass. Native101 kudos release remains pending
until guarded request plus observed102 progression. No actual purchase claim.

## Exact checkpoints, export receipts and unavailable purchase paths — version12

`checkpoint.save_inactive_boundary` uses one supported `Network.SaveGame` request
at a verified inactive boundary. Require a unique name, native `SaveComplete`, a
stable CIV6 file and equal archive hash, and unchanged native phase. Missing ACK
never sends another save. File handles close promptly; the temporary callback is
removed. The material pilot saves after25-turn planner cycles, including their
placements. This API saves state only; it introduces no automatic load/restart.

`continuation.read_research_export(root, turn=...)` accepts the maintained
supplemental or preservation filename only with matching actual clock/schema;
conflicting current exports and duplicate player-turn observations fail. Avoid
assuming `preserve_telemetry` creates `research-latest.json`.

The actual exact124 checkpoint and full restoration are locally validated with
17 physical/production targets, unchanged gold and615 research rows. A separate
frozen45 one-shot AI tile request remained unconfirmed and is excluded from main
outcomes. That diagnostic does not establish native purchase authority.179
installed tests plus35 Lua guard fixtures pass; these counts are not a full-game
or general native API guarantee. See the material-first research doc for current
branch status, evidence and limitations. The former three-world study is closed.

## Rejected command-actor route — native evidence

`command_actor.probe_command_actor` is disabled by default. It temporarily
transfers human control, not just the camera. The across-frame query at131 proved
UI synchronization, but restoring actor0 advanced the native clock to132 without
an autoplay request. It is rejected for production purchasing. A caller must
explicitly opt into an unsafe diagnostic; ordinary controllers never call it.
The clock guard caught the side effect, original roles were restored, and exact131
world/gold/19physical+UI/650research prefixes were independently restored from the
pre-test manual save. Preserve the discarded/replayed diagnostic interval; never
label it zero raw AI replay. A simulated guard test does not establish native role
switching safety. Recovery remains autonomous; this guard is not an approval rule.

Checkpoint/performance hardening (23 October): exact-save names include a stable hash of the resolved archive path; existing namespaced native files or archives still block before any SaveGame command. This preserves other runs and makes ambiguous same-boundary saves one-shot. Inactive handoff confirmation still needs three separate replies, now separated by 0.15s idle spacing; progress polling starts at 0.5s, then1s. The finite play command is unchanged. Same-world native100 checkpoint/SaveComplete/hash and subsequent101+ advancement verified. Initial local normal-turn timings: 26.1s before, 19.9s after; small sample, not player-install latency.
