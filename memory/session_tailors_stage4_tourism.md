# Tailors Stage 4 Tourism amendment — 13 October 2026

Henno changed the canonical Tailors design and asked to implement +2 Tourism
instead of +10% Culture for Stage Manager, Ballet Dancer, Musical Actor and
Opera Singer. Implemented with Bakers' destination-district Tourism modifier,
Amount=2, keeping per-seller gates and Great Artist point siblings. Updated
localization Markdown/generated SQL, contracts, assertions and Lua fixtures.
Foundation includes the whole buildings subtree, so its design slice hash also
changed under this authorized amendment. Stage4 is ready_for_review; no runtime
acceptance was recorded. Review: project/docs/quarters/tailors-stage4-review.md.

Windows tests used Python312 with PYTHONPATH pointing to the existing isolated
C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps directory for Lupa.
Quarter and stage4 handoff validators pass with no warnings; full localization
check passes. Rebuild/reload and confirm Tourism at all four service venues.


Follow-up: Henno caught missing Citizen-slot disclosure in Stage Manager's NEW
notification. Added +1 Citizen slot in the Theater Square and the corresponding
REMOVED persistence wording, matching Sacristan. Shared notification pattern
and I.STAGE_MANAGER now require state-specific slot handling. Stage4 assertions
check generated text against actual Buildings.CitizenSlots; five regression
cases caught the old omission and pass after correction. Shared catalog tests,
localization check and Stage4 handoff pass. No gameplay/design change.


Temporary baseline test requested by Henno: CSC_Q_TAILORS.sql now ends with a
labelled DELETE block detaching only the three Wonder Tourism wrappers from
Fashion House. Theater Square Tourism and all Artist points remain active.
Remove that block to restore the intended design. Offline DB smoke checks pass.
This is a temporary test override: normal Stage4 semantic/handoff assertions
expect those attachments and will be red until restored. Text/design are kept
for restoration rather than changed for this baseline test.


Henno requested re-enabling the Wonder Tourism modifiers. Removed the temporary
baseline DELETE block; all three +2 Tourism wrappers are attached again and
verified in the offline database. The baseline override described above is retired.


Live verification after Henno challenged district-instance assumptions:
Tenochtitlan city 65536 had three distinct Wonder district IDs, each on its own
host tile (Bolshoi 262146/672; Broadway 327683/599; Sydney 393220/600).
Loaded BuildingModifiers still omitted all three Wonder Tourism wrappers, so
the running session was the baseline build; re-enabled Tourism is not live
validated. Details in the Stage4 review doc. Resolve debug context IDs with
LSQ rather than assuming state 3. Enumerate player:GetDistricts():Members();
CityDistricts has no Members API in gameplay. Henno authorized closing FireTuner.
