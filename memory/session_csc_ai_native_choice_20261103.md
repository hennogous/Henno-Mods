# Fresh CSC AI tuning and native choice test — 3 November 2026

Henno authorized archiving the previous AI tuning and a bounded native Quarter
choice test. The broad older optimization campaign remains paused; this new
mechanism experiment does not authorize reviving its policies.

Retirement is committed/pushed in355c0b5. Current-byte archive:
`project/archive/ai-tuning-20261103/`, including335 historical tooling snapshots
and17 retired runtime/localization files. Fifteen action entries and three
criteria were removed. The installed reset changed only modinfo and two Settings
XML files; all other installed bytes were preserved. Keep the reset as the new
baseline. The remaining UI yield-filter import satisfies existing includes and
creates no AI yield or policy.

Fresh trial infrastructure is committed/pushed in0710579:
`project/tools/native_ai/quarter_placement_trial/`. It imports neutral shared
controller helpers, not old placement, subsidy or scripted-foundation policies.
Native source, ABI and per-load budgets are pinned. No forced build orders,
grants, reservation removal or queue clearing are part of this trial.

Canonical report:
`project/docs/research/mods/civ6-district-placement-choice-20261103.md`.
Evidence package: `Desktop/Codex/csc-native-placement-choice-20261103/`;
working stage in this chat's visualization root under the same basename.

Original save is game04/turn250, SHA256
`ea818368130273e02e70e31449a6f24a54e34486b8bfa402dd34b62255443e48`.
Current gameplay is rebased onto this historical world, not called a fresh world.
Target: original AI P5/Sydney city131073, Tailors district37.

Baseline01 observed scores but no new selector opportunity250→251; Aerodrome
completed. Baseline02 reached a new choice at252: Neighborhood10 at2272
(52,30),585676 Q8. Only2272 was definitely unreserved among the qualified
Tailors candidates; positive other reservation IDs remain unresolved.

Planner revision permits one qualified site for a different-type alternative;
same-type site relocation still needs two. Only offline make_plan/load_baseline
changed in the driver; original baseline source archive and exact hashes prove
the exception. Native C/JS/daemon and original prefix remained unchanged.

Treatment01 added342655 Q8 (gap342399 +256) to fresh Tailors values at2272.
At252 Tailors243277 became585932 in raw output/cache/Best/PV. Winner changed
Neighborhood→Tailors at the SAME tile. Native request6527 was accepted/submitted
with logged value2288.0. This is a caused district-type switch and request;
it is not a caused Quarter site relocation, completed district or benefit.
Turn251 physical/queue/research prefix exactly matched baseline02.

Treatment01 observed no foundation through253, with Bomber in production.
Attempt254 timed out after600 seconds; no successful260 endpoint. Cleanup was
verified normal: exit0, preferences restored, owners absent, frozen inputs and
installed/source hashes unchanged, native daemon faultfalse and frozen mode0.

Retained logs show an unmatched NaturalWonderPopup event lock59896. This is a
strong stall candidate, not demonstrated unguarded causality. A separate opt-in
shared guard calls the shipped popup Close only after fresh finite Core observer
proof, matching UI clock and exact context visibility. It records stack reads,
caps acknowledgements at8 per interval, and blocks replay after ambiguous ACK.
Stack topness/membership is not an admission condition. Lua5.1 tests16 and Python
mocks6 passed. Existing controller.py was not edited for this guard.

Control01 is now running no-score-adjustment250→254 with this presentation guard;
follow-through results are to be reconciled below before final publication.

Publishing preference: commit and push updated findings; skip added website,
link or deployment QA. See `feedback_ai_publishing.md`.
