# CSC research influence: working valuation, unresolved restart

The experiments demonstrate a native path from actual Quarter materials to
selective civic research value. They do **not** yet establish a production-ready,
reversible AI treatment. The accepted CSC tuning was preserved and restored;
no candidate was deployed and no ungated natural-game comparison was started.

## What works

A dormant benefit attached through `CivicModifiers` can be forecast even when
its economic requirements are false. A dedicated internal yield isolates this
value from the six ordinary economic yields. A native `Yields` preference can
adjust that forecast, including when an RH-style Lua strategy activates it.
This consumer works where strategy-linked `Civics` favorites did not.

With `DefaultValue=1`, static preference `-100` and ready-only strategy `+100`,
the controlled candidate had the same 55 initial civic scores as a matched
no-attachment reference. On the next turn, Divine Right gained:

| Player setup | Added target score |
|---|---:|
| No Tailors' Quarter | 0 |
| Quarter, no mapped Base | 0 |
| Quarter, unimproved Flax | 656 |
| Quarter, farmed Flax | 1,076 |
| Quarter, farmed Flax | 168 |

The different magnitudes reflect each player's native valuation, not different
configured weights. These are diagnostic values, **not recommended release
weights**. The contrast combines attachment and callback enablement; it does
not isolate every component of the candidate.

The same selectivity survives a structurally contradictory economic guard:
the native ALL requirement set contains Has Future Civic **and** its inverse.
The guidance definitions therefore cannot satisfy their economic gate. Actual
Service modifiers were left untouched. UI omission and full gameplay invariance
remain release gates; these trials did not validate a complete player-facing
integration.

The ordinary CSC scan supplies real readiness: an owned, visible, mapped
resource adjacent to a completed, unpillaged Quarter. Unimproved Base supply
counts. A single-target predicate additionally checks that the target civic is
not already owned; the existing multi-item research plan alone can remain true
when producer-support research is still missing.

## Lifecycle results

All three lifecycle treatments used the same controlled phase schedule. Player3
lost owned Tailor Base resources and player4 had its Quarter pillaged at73;
both recovered77, lost access again81 and recovered83. A ready player5 was a
control. In the final two treatments, native player-turn events drove these
fixture changes independently of whether the engine queried the strategy.

| Treatment | Initial activation | Value withdrawn after loss | Return after recovery |
|---|---|---|---|
| C10: positive readiness callback | Yes | Not demonstrated | Persistent value made this inconclusive |
| C11v2: inverse `Disqualifier=1` | Yes | Exact reference scores at75–78 | No, through86; callbacks stopped after74 |
| C12: inverse `Forbidden=1` | Yes | Exact reference scores at75–79 | No, through86, despite continued callbacks |

For C12, each primary and inverse callback was evaluated 17 times per player.
The inverse condition correctly switched back to false at78 and84 after
readiness returned. Native logs record `Stopped` at74 for players3–4, but no
subsequent `Following` adoption for those players. Scores stayed at the
reference at79 instead of regaining the prior large increment. Later small
residuals coincide with ordinary world/research divergence and are not evidence
of a restored guidance bonus. The continuously ready control kept its signal.

This is a finite diagnostic result, not proof that all engine strategy paths
are permanently irreversible. In particular, the two Lua conditions use the
native `Exclusive` key to coexist. Rechecking callbacks, adopting a strategy,
applying a preference and consuming it in a civic score are distinct layers.
The unresolved layer is restarting the treatment after it has stopped.

Native timing also matters: initial activation71 affects scores72. With the
independent phase fixture, loss73 was seen by the inverse callback74 and the
score reached the reference75. Requiring withdrawal74 or restoration78 would
have been premature. No natural Divine Right completion occurred in these
short probes; an already-owned Code of Laws control tested the cleanup
predicate without granting or resetting research.

## Evidence and limits

Each valid lifecycle pair contains 80 observed player-turns per arm, turns71–86,
with native endpoint88. C11v2 and C12 additionally archive 85 independent turn
readiness records per arm. Native database row-multiset audits confirm only the
two intended CivicModifiers attachments differ between each pair; callback
bytes differ only by the enabled literal. The conditions, fixtures, code,
settings and actual installed gameplay files were archived before native play.

Independent audits verified the exact initial map, census, preferences and
fixture, including genuinely unimproved Flax; clean native scripts; restoration
of all 144 original mod preferences and disabled auto-start; and restored source
and installed AI SQL/Lua hashes. The controller has exited. Civ remains open.

These are save-derived, artificial Medieval-start mechanism tests, not evidence
of improved natural play. ON loads the exact unplayed OFF world because a
same-seed fresh regeneration once changed resources and start positions for an
unknown reason. No map normalization was performed. Target prerequisite
propagation to Reformed Church is recorded separately from unrelated effects.

Harness failures are retained explicitly: C2A never produced an ON contrast;
C10's completed data was recovered offline after a mistaken per-turn log
assertion; C11v1's OFF fixture stopped advancing when callbacks stopped. C11's
single instrumentation repair produced the valid independent-event v2 pair.
No native turns were replayed to recover C10. No crashes were demonstrated.

Detailed version history: [experiment ledger](csc-civic-modifier-tests-20261020.md).
Evidence root: `C:/Users/Shadow/Desktop/Codex/csc-ai-civic-modifiers-20261020`.
Final audits: `c11-disqualifier-v2/post-run-audit.json`,
`c12-forbidden-v1/post-run-audit.json`, and
`terminal-baseline-verification.json`. Audit tooling lives in
`project/tools/ai_baseline/civic_modifier_lifecycle_audit.py`.

## Decision

Selective material-aware civic valuation and an explicit exit are demonstrated.
Repeated off/on guidance is not. A bounded read-only search of RH Lua and shipped
Base UI code found no supported strategy restart/reset API; this does not prove
none exists. Further arbitrary weight or condition-flag variations would not
resolve that uncertainty responsibly.

The automatic series ends at this mechanism boundary. Restart behavior, target
completion, reload, ownership/visibility changes, duplicate Quarters, stage4
same-Quarter supply, UI omission and actual Service/natural-play validation
remain unvalidated. The evidence supports designing the next focused experiment;
it does not justify silently shipping the diagnostic treatment.
