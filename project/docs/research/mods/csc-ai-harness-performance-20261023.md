# Faster CSC test harness and delta evaluation — 23 October 2026

The donated-Both diagnostic was paused by its human at native turn 88. The
replacement continues the same live DX12 process and world. It does not reload
a save, recreate a foundation, grant additional assistance, or host a new game.
The earlier suggestion to finish and launch a fresh game was superseded.

## Why the old run was slow

Ordinary recent rounds took about 58 seconds. Native autoplay plus detecting its
return took about 18 seconds; separated return checks about 10 seconds; evaluator,
metrics, duplicate exports and next-operation checks about 28 seconds. Individual
commands repeatedly waited through a fixed discovery receive window. The
opportunity evaluator itself was only part of the overhead.

## Maintained improvements

`full_game_controller.discovery` freshly resolves the current native context
list for every command, returning when its complete framed response arrives.
It handles numeric native lists and prefixed lists, fragmented frames and console
noise. It does not cache context IDs, alter transport, weaken the three separated
handoff samples, or change the finite autoplay operation. Bounded discovery
retries remain read-only and occur before any Lua command transmission.

`service_planner.boundary_bundle` combines native Quarter locations, current
chain metrics, current primary capture, research and Builder observer prefixes
into one Gameplay command. Full current primary and chain metrics share a capture.
Formal first-activation primary checkpoints remain separate and unchanged. A
second bundle after an actual acquisition/foundation captures its resulting state.
Per-turn research, Builder/event prefixes, materials and chain records remain;
the redundant standalone research export is removed.

The opt-in native delta reader caches each city's fixed ring-four geography
(Quarter sources still limited to ring three). A cheap per-turn signature checks
revealed ownership, resources, improvements/pillage, districts/features/terrain,
native prices, research unlocks, population, production and same-Quarter state.
Changed/new/captured scopes refresh native placement projections and candidate
routes immediately; unchanged scopes reuse them. A 25-turn reconciliation catches
uncovered engine eligibility changes. We still inspect native facts over the fixed
footprint; this is not an assumption that all relevant events are available.

Every purchase and placement still obtains its existing immediate native quote,
ownership, legality, production, treasury and queue proofs. A cached opportunity
never authorizes a mutation by itself. Diagnostic donations and staged assignments
retain their native persistent tokens and one-send transport.

Raw delta references, full-observation ages and expanded compatible native-service
files are retained. New per-turn performance records distinguish play/confirmation,
collection, policy and other capture time. Cached scope does not mean a missing
material observation: the separate current chain census is still taken every turn.

## Same-world handoff evidence

The old worker 4400 and supervisor 23452 exited cleanly at inactive native 88
before evaluating that round. All 78 old executed pins matched before edits.
The new reader matched the complete exported world, both assisted sites and UI
production, 435 research rows and the two closed acquisition ledgers. Existing
outcomes were inherited once: two foundations, four acquired tiles and 165 gold
donated/charged. Installed 510-file runtime and resource pass remain unchanged.

The first optimized cycle 88 took 3.78 seconds for collection/evaluation/capture
excluding autoplay. Its one 88→89 operation completed, but the first optimized
discovery callback had bypassed an existing busy-game retry and stopped on a
read-only discovery failure. Cleanup independently proved actual inactive 89.
Version 7 restores that bounded pre-transmission retry and continues the
previously unevaluated 89 cycle, with no replay, reload or reconstruction.

Version 7 reached inactive 90, then stopped in the first city's policy lookup:
delta refresh had invalidated its scan timestamp without removing cached marks.
No acquisition or placement action was reached. Version 8 invalidates these two
parts of the cache together; the regression covers the adapter→Planner path.
It continues the intact 90 world after full parity/445 research rows, with no
replay, reload or reconstruction. All failed branch evidence is retained.

Old output branches, source versions, failed commands and receipts are preserved.
The new active pointer is in the donated diagnostic's `active-run.json`.

## Validation limits

The staged full suite passed 237 Python checks and 35 actual Lua 5.1 guards;
64 targeted controller/performance checks passed after the busy-discovery fix.
Another 66 targeted cache/material/transaction checks passed after the cache fix.
The delta Lua fixture verifies unchanged-scope projection avoidance and immediate
invalidation for ownership/resource/improvement/pillage/district/feature/reveal,
population and tech/civic changes. Read-only native bundle validation matched
the paused world and all 435 research rows without advancing its clock.

The speedup must be measured from subsequent ordinary accepted rounds, keeping
presentation delays and scheduled full checkpoints separate. Neither these tests
nor partial progress establish full-game reliability or a causal AI improvement.
All current executed source pins stay frozen while the worker runs. No recurring
automation was created; previously deleted monitors remain deleted.

## Accepted version9 and measured result

Version8 completed cycle90 with no actions, then the renderer reporter required
a missing run-start file. This was repaired offline from the original supervisor
timestamp; renderer logs were reviewed without any native rerun. Version9 now
initializes reporter/watchdog identity metadata before native work, and the shared
validator rejects missing files at startup. The accepted continuation skips the
already-completed90 cycle and begins with the single90→91 operation.

The installed full suite passes240 checks and35 actualLua51 guards. Exact90
world/two physical+UI production/445research/closedacquisition ledger parity
passed. Current worker10476/supervisor2036 owns the SAME DX12Civ4476.

Ordinary accepted sample turns [91, 92, 93] averaged
32.0seconds per round, compared with about58.6
seconds in the earlier ordinary sample. Collection and policy averaged
3.6seconds, excluding native play and
handoff confirmation. This is a small descriptive timing sample. All95
current executedpins matched at review. No reload, reconstruction or AIturn replay
occurred. Full250 and final audit remain pending.
