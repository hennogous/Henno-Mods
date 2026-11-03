# Shared native test sessions for full games and probes

User-confirmed direction,30 October2026: use and harden shared control machinery
for full games and short native probes where practical. The purpose is reliable
actual-AI evidence, not an independent infrastructure project or a reason to
replace observation with offline speculation.

## Current implementation boundary

The maintained finite core in `project/tools/ai_baseline/full_game_controller/`
retains one-send play, transport/journaling, bounded read-only retries, separated
handoff samples, known presentation guards and checkpoint support. Its API and
implementation were not changed by this consolidation.

Implemented30October: `session.py` now wraps the core with held ownership,
exclusive intent records before load/host/Menu/exit, source hash/native-directory
checks, readiness plus an explicit caller source gate, ordered preference/exit/
observer/package callbacks and fresh owner absence. `windows_process.py` provides
held creation/executable identity and Civ/Tuner/research-worker inventory, with
exact exemptions for a declared supervisor. Launch strategy remains a callback.
`log_capture.py` retains the shared log-generation boundary.

`ai_tuning/native_profile_test.worker` uses the common lifecycle for its fresh
full-game path (including observer-loss cleanup); its special historical live125
branch stays separate. `probe.py` supplies a minimal adapter, and maintained
`ai_tuning/native_session_probe.py` exercises it without dated executor imports.
The full-game capture/base adapter chain has not all been consolidated.

[Native integration result](../research/mods/csc-shared-native-session-20261030.md):
exact declared110 census twice, zero AI turns,291 pins/604 installed files equal,
exact145-ID/148-entry preferences and AutoStartfalse, native/worker exit0 and
fresh owner absence. No hook, treatment or full-game validation is claimed.

## Common session responsibilities

Preserve `make_controller`, `ready`, `play`, transport and checkpoint interfaces.
Factor small lifecycle operations around them rather than rewriting the core:

1. Exact owner inventory and held process identity. Refuse a foreign Civ/Tuner or
   research owner; do not kill or claim it. Preserve the original process handle,
   creation time and command identity through exit.
2. Launch and one-shot load, with verified input bytes and supported native save
   location. ACK is not load success. Prove contexts, actual clock and control
   state before a caller-supplied source-eligibility gate. Never replay ambiguous
   load or mutation requests.
3. Original per-installation preferences, AutoStart and package manifest, with
   explicit temporary deltas and unrelated-work preservation.
4. Shared log generation boundaries and evidence metadata. Missing pre-AI logs
   may be normal; missing post-observation evidence is not empty successful work.
5. Normal Menu, exact preferences, one supported exit, held exits and fresh owner
   absence; restore installation deltas only after native absence and expected
   bytes. Preserve partial evidence and error classes on every failure.

Existing preference/package functions should be extracted/reused where their
preconditions apply. Do not make a new runner import six dated Desktop executors.

## What stays specific

| Full-game policy | Probe adapter |
|---|---|
| World setup/seeds, periodic captures, checkpoints, continuation and endpoint | Existing-save/source contract, target readers, observer/health, treatment/restoration, exposure and early-stop criteria |
| Light ordinary telemetry and installed CSC host as sole gameplay mutator | Explicit bounded instrumentation; no forced gameplay to manufacture exposure |

Source parity is a caller's scientific contract, not hidden normalization in the
session layer. Declare rebases before intervention, retain the full discrepancy,
and match complete accepted references across arms. Do not force gameplay values
to look like a historical snapshot. A queue request, fresh value, selection,
completion and net chain benefit remain different evidence levels.

Observers are optional attachments, not mandatory controller dependencies. Their
specific ABI/binary validation belongs in the adapter. Freeze/capture the observer
before diagnostic restoration; retain it safely until native exit according to
its protocol. The common cleanup coordinates these hooks but knows no hardcoded
Quarter, yield, city or Frida address. Do not edit loaded/pinned code while live.

## Practical performance and failure requirements

The [producer observation](../research/mods/csc-ai-producer-decision-20261030.md)
captured a real choice, but also2.5million general-getter hook entries for37
accepted getter records. Full games should stay light; probes should target the
relevant call site/consumer and disclose overhead. Retained-event bounds alone
do not bound interception cost. Avoid deep per-turn capture by default.

Separate diagnostic-detail capacity from signal invalidity. A journal cap is
not a changed owner, material fact or ABI failure. A future bounded summary can
retain aggregate validation plus a limited detailed history; that policy remains
to be implemented and tested. Do not silently drop data or claim unmeasured
counterfactual effects to make a run pass.

First consolidation acceptance is complete for source migration, focused failure
checks and a bounded native zero-turn boundary exercise. A new complete game and
an instrumented finite probe through these adapters remain unvalidated. Use the
same maintained lifecycle for the next authorized experiment; do not revive old
arms simply to test infrastructure. No campaign, world, deployment or extension
is authorized by this document. The original extraction map remains historical
at H/shared-session-integration-map-20261030.md/json.


## Apparent Menu hang can be a native crash dialog — 31 October 2026

A live PID and an acknowledged Menu event did not mean the game was merely slow:
exact-owner diagnostic window metadata found Civ's access-violation dialog.
One small external stack/module dump plus recovered context and Windows unwind
identified RadioButtonControl:SetCheck(false); a narrow lens lifecycle fix then
passed three zero-AI exits. No DLL hook or forced kill was needed. Preserve the
original runtime exception separately from any earlier Lua reporter failure.
The controller timeout was a symptom; its finite-play/transport behavior was not
changed for this fix. See the [native evidence](../research/mods/csc-ui-exit-crash-20261031.md).
Before calling a future timeout a deadlock or crash, inspect the exact owned
process/dialog/exception evidence. A raw stack scan is not a backtrace. Only
acknowledge a native crash dialog after its exact identity and normal handler
semantics are verified; an arbitrary popup is not permission to click through.


## Retained observer adapter — 31 October 2026

`project/tools/native_ai/observer_host.py` and `observer_daemon.py` compose the
existing NativeSession `before_menu`/`after_native_exit` callbacks. The current
bounded adapter accepts exactly two reviewed work-admission boundaries, explicit
module/spec/config/dependency inputs and a held owner. It attaches disabled,
verifies full source/scoped facts, enables once, snapshots at inactive boundaries,
freezes before Menu and retains the Frida session until exact native exit. It
does not unload/detach while the game lives or offer native job submission.

The source110→113 admission probe natively exercised this lifecycle: five complete
pairs, no errors, frozen with zero pending, native+daemon exit0 and exact settings/
package/source restoration. This validates that bounded adapter, not every future
hook or full-game instrumentation. Keep ABI preflight, raw statuses and actual
target coverage separate from lifecycle success. Old behavior-log SUCCESS can
describe retained node state without a fresh entrypoint invocation.


## Explicit native user root for probe diagnostics

`make_probe_controller(output, user_root=...)` supplies the real native user
directory to Diagnostics.USER. Observer diplomacy guards consume its Logs
directory. A probe that never enters those guards can appear healthy while
omitting this adapter contract. The source110→121 investment observation exposed
the defect when an actual hidden-agenda warning first exercised it.

Prefer an explicit absolute existing native user_root. Default resolution accepts
only an absolute LOCALAPPDATA with an existing derived CivVI/Logs directory;
agent process environments can redirect LOCALAPPDATA. The maintained session CLI
accepts --user-root. Factory-path tests cover positive dismissal and fail-closed
unknown/newer-deal/wrong-turn/missing-log cases. This supplies missing diagnostic
context; it does not relax dismissal, transport or finite-play guards.

Recovery comparators must separate persistent world/economic state from process
diagnostics and measurement precision. UI district progress is integer-valued in
the inspected current build; a decimal AI CSV is a different representation.
Keep raw observations and coverage resets, require the relevant persisted facts,
and qualify continuity instead of fabricating fractional or whole-world parity.


## Classified pre-transmission discovery retry

The partial131 investment observation exposed a missing adapter-layer retry:
discovery exhausted three attempts before sending a read, then its generic
RuntimeError bypassed state_read's bounded retry. The game later answered Menu
and exited normally. No crash or ambiguous repeated control was established.

StateDiscoveryUnavailable now identifies only that exact pre-transmission case.
state_read can use its existing maximum three read attempts, each retaining the
existing bounded discovery attempts. Persistent absence still fails; unknown
RuntimeError and NativeLuaFailure do not enter this branch. Direct mutation
commands gain no outer retry, and missing mutation acknowledgments still never
resend. Six new real probe/factory tests cover transient recovery, persistent
maximum9 discovery checks/0Lua sends, unknown/native errors and both mutation
pre-discovery and ambiguous-send behavior.91 Python+35 Lua guards passed.

The prior skipped UI-human warning check later succeeded under the unchanged
guard and released the exact session to inactive122. Preserve that distinction:
transient UI disagreement is not grounds to weaken role guards. Source versions
are frozen during ownership and changed only after exact exit/restoration audit.


## Core control phase and UI observation time

The existing `checkpoint.validate_ui_save_phase` contract permits an inactive Core boundaryT with UI clockT orT-1 when both contexts return to local0/human control and the UI confirms the observer alive. Core owns the finite-play budget and save boundary. A future or older UI clock, active/mismatched control state or missing observer remains invalid. This is a control-phase rule, not permission to label stale UI measurements as current.

The1November reference exposed this distinction at145: Core, economic receipts and physical facts reported145 while PlotInfo still reported144 after a fresh read. Capture adapters must retain the actual UI timestamp, keep lagged data outside ordinary coherent compact snapshots, and report corresponding measurements unavailable atT. They must not advance extra turns, replay AI or reload only to satisfy an observer clock. Apply equivalent observation rules across comparison arms.

A retained-world handoff can use existing `NativeSession.start(attach_pid=...)` after explicit transfer of sole console ownership. An old worker may remain in a proven OS-only passive hold, but its close-control path must remain unused; its teardown may only write its own diagnostic artifacts after native exit. The new owner must adopt original preferences and package-restoration responsibility, preserve old source bytes, verify exact native creation identity and continue only the old remaining budget. Record this as continuous native-world execution across a controller handoff, not uninterrupted controller execution.

A second145 fault exposed a narrower metadata gap: active-command index publication already retries sharing locks, but `_await_target` wrote `live-status.json` directly. A Windows reader can briefly deny atomic replacement. Optional status publication must not abort an already-issued finite operation. Retry filesystem publication only, preserve raw command/journal evidence, and never issue another native activation because a status index failed. Required scientific files must still fail explicitly if they cannot be persisted. The shared writer/monitor hardening is required after the current pinned owners have exited; a same-world recovery adapter can wrap diagnostics without modifying their frozen inputs.
