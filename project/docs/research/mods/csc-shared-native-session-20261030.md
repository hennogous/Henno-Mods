# Shared native session consolidation — 30 October 2026

The maintained finite-play core remains unchanged. New maintained modules wrap
it with session ownership and lifecycle handling:

- `full_game_controller/session.py`: held owner, one-shot intent records,
  supported-save hash gate, context/clock readiness plus caller eligibility,
  ordered Menu/preferences/exit/owner-absence/package callbacks.
- `full_game_controller/windows_process.py`: read-only Civ/Tuner/research-worker
  inventory and held creation/executable identity. Declared supervisor exemptions
  use exact identities. Launch strategy stays adapter-owned.
- `full_game_controller/probe.py`: minimal controller/diagnostics adapter without
  dated Desktop executor imports or mandatory DLL instrumentation.
- `ai_tuning/native_session_probe.py`: maintained zero-turn source-load/census/
  close exercise, with strict caller-provided complete reference and runtime/
  source pins. It never requests autoplay or creates a world.

`native_profile_test.worker` now uses this session for fresh launch/attachment,
load/host intent reservation, readiness after its existing source/database
checks, successful cleanup and observer-elimination cleanup. Full-game seeds,
installed assistance ownership, periodic outcomes, continuation and endpoint
rules remain in that driver. The historical special live125 recovery branch
remains separate; old archives and executors are unchanged.

Scientific source eligibility remains explicit and adapter-owned. The shared
layer does not mask fields, repair historical movement discrepancies, rebase a
source, choose treatment, attach observers or restart an ambiguous operation.
Load acknowledgement is not readiness. Preference and package callbacks must
verify their complete promised postconditions; callbacks are not inferred proof.

Observers, when used, freeze/capture and restore treatment before Menu, remain
retained safely until native exit, and confirm their own exit before package
restoration. An unconfirmed observer or restoration stops cleanup without a
false success. A diagnostic journal cap is not automatically an invalid input;
redesign of that producer-specific journal remains future work.

Validation separates lifecycle from AI research: offline failure fixtures cover
foreign owners, PID reuse, ambiguous load/exit, missing contexts, source mismatch,
observer failure, preference failure, surviving native, foreign successors and
changed packages. The native integration exercise has no hooks, no AI turns and
no gameplay coefficients changed. It cannot prove AI improvement, DLL neutrality,
full-game reliability or producer-forecast marginal efficacy.

Full games should remain light. Future decision probes should use targeted
consumer/call-site observation and bound interception volume; a retained-record
cap alone does not control hot-hook overhead.

## Accepted evidence and limitations

Native record: `Desktop/Codex/csc-shared-session-20261030/run-01`.
One preserved native-path source110 load, SHA256
`62e623f381ffd8e8ece219b6a87c575dbfebaea34ef6fd4c8dcb6c7ef7c0e52c`.
The entire exported Core census equals the previously declared R2 post-load
reference and remains equal in a second read. This uses that explicitly rebased
reference, not a claim of parity to the older historical movement value.

Twenty journaled native commands include exactly one load, Menu and ExitOK;
no autoplay, HostGame, observer attachment or treatment. Native11276 (creation
FILETIME134378235955962379) exited0; worker16812 returned0. Fresh independent
CIM check found neither exact worker nor any Civ/FireTuner process. All291 pins
and604 installed hash/size entries remained unchanged. Final raw preferences
equal the original145 mod IDs/148 subscription entries, AutoStartfalse.
Independent Sol review checked these raw artifacts, complete reference equality,
command sources and current files rather than relying on the result summary.

Offline checks:24 new session/probe failure checks;54 existing core and6
checkpoint checks (84 together);6 shared-log checks;53 profile/observer checks
reported OK with6 native-database cases explicitly skipped. No synthetic result
is counted as native AI behavior.

This first integration used direct DX11 startup, no Steam successor handoff and
no instrumentation. The newly migrated full-game worker was reviewed and its
existing regressions passed; a new end-to-end full game was not run. The legacy
live125 branch and full-game capture/base adapter chain were not rewritten.
The standalone probe no longer depends on that dated import chain. Its inherited
finite-play methods were not exercised by this zero-turn check. Future native
decision probes still need their own source, observation and exposure contract.
No old counterfactual, campaign, automation or goal was resumed.
