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
