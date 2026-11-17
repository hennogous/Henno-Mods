# Localization/design reference locks refreshed — 17 November 2026

Henno authorized the remaining reference-lock fixes. Restored the truncated
Tailors Harbor sentence and reviewed its River capitalization/trade-route
wording changes as presentation-only. Updated canonical_source_sha256 in the
design transcription and its matching control.yaml source lock.

Bakers descriptions use ICON_Amenities and identify returns to the Bakery/Cafe.
Regenerated SQL and refreshed the localization reference lock after checks.
All 201 Quarter tests, localization generator/pattern checks and the focused SQL
architecture check pass. The public player-site build also passes.

Separate Civilopedia district-list/UI work remains in progress. Publish only
the reviewed two description changes in Bakers source/generated SQL; keep the
existing published district-list generation intact. The staged control checksum
matches that source variant. Local source/SQL/control retain the full Pedia work
and matching local checksum, so their remaining diffs are intentional. Do not
overwrite this work or treat it as another unexplained stale-lock failure.

No gameplay rules, acceptance statuses or phase approvals changed. No game,
FireTuner or controller session was started.
