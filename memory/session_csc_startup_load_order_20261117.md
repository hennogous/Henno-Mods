# CSC startup failure after action consolidation — 17 November 2026

Database.log reported no such table: CSC_PopulationLevels, followed by two
CSC_TradeReadChecks failures and a missing Tailors Stage 3 bit-1 modifier.
Modding.log at 3923235.803–3923235.813 showed Common loading before Schema
inside CSC_Q_ALL, despite Schema appearing first in the generated manifest XML.
Previously populated cache fixtures and XML-sequence checks missed the bootstrap
dependency introduced by the action merge.

Fix: CSC_Q_ALL now contains only Schema at LoadOrder 94. The separate
CSC_Q_ALL_Common action runs at 95. Other phases and all gameplay SQL remain
unchanged. JSON is authoritative; project CDATA was regenerated. Architecture
contracts, tests and documentation now follow this separation. The loading
validator models file Priority/default filename order and rejects equal-order
dependencies across separate actions.

Fresh in-memory tests reproduce the old missing-table failure and verify helper
creation/seeding through the current phases without any pre-existing CSC state.
Full Quarter suite: 205 tests; transaction suite: 83; ModBuddy suite: 11, passed.
The action round-trip check also passed. No game or FireTuner session was touched.
Henno must rebuild CSC in ModBuddy to deploy the corrected manifest and retry.

Keep unrelated art, lenses, Pedia, localization and Tailors PLUNDER_GOLD changes
out of this commit. Clean HEAD-based project/JSON staging variants carry only
the phase split while preserving the current working files.

## Follow-up: rebuilt game loads successfully; policy UI errors

Henno requested a read-only log review after further in-game issues. Current
Modding.log confirms Schema then Common in separate actions at 3923837.030 and
3923837.044; all shared transaction passes loaded. Database.log reports Gameplay
Passed Validation at 3923838.338. No gameplay SQL errors or CSC Lua exceptions.

Lua.log contains three identical exceptions in Extended Policy Cards, Workshop
2266952591, GovernmentScreen.lua:1493. EnsureRowContentsFit accesses
inst.Content:SetOffsetX during OnRowAnimCallback; the expected card instance or
Content control is missing. CSC does not replace GovernmentScreen. The installed
mod identifies itself as Extended Policy Cards by Aristos; Better Report Screen,
its documented dependency, is active. Cause of the missing UI instance remains
unconfirmed; disabling EPC on a subsequent launch is the direct isolation test.
Repeated LOC_CLICKOUT_26_CAROUSEL_TOOLTIP duplicates come from Firaxis
CurrentClickouts XML, separately from gameplay validation. No files or game state
were changed during this log inspection.

## Correction: CSC participates in EPC's rendering path

Henno pointed out the EPC adapter and clarified that the Government screen no
longer opens, beginning after the latest restructuring. The initial attribution
to EPC alone was premature. The working CSC_PolicyCardEstimates ReplaceUIScript
replaced BRS's RMA context, tried to include its original paired (not imported)
Lua, and silently returned if initialization was absent. Modding.log confirms
that replacement action ran, not that the original API was restored. The saved
pre-restructure working JSON has the same EPC action, so the precise trigger
has not been reproduced; don't claim the action changed in consolidation.

Reworked the adapter into a separate BRS-gated paired XML/Lua context. Original
BRS initializes normally, then CSC decorates its exposed table. A one-time load
event handles late publication; unavailable APIs leave BRS untouched. A small
policy-only fold uses public decoder results for affected cards; other objects
pass through. Optional forecast errors fall back/log once and cannot abort card
creation. No Workshop source or active game was modified.

80 numerical fixtures and separate-context lifecycle tests pass, including
immediate/late/absent APIs, table identity, no duplicate installation, original
refresh preservation and fault recovery. The installed EPC card renderer also
passes with mock controls for both normal and injected-failure paths. See the
new project/docs/integrations/csc-policy-card-estimates.md. Rebuild/reload and
Government-screen review are still needed in Henno's session.
