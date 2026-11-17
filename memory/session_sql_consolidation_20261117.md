# SQL consolidation and action organization — 17 November 2026

User authorized source cleanup, comments/docs and offline regression checks.
No test games. The old AI goal was cleared; do not restart campaigns from it.

Current layout: `project/docs/integrations/csc-shared-sql.md`. Shared economic
DDL is in Schema, helper seeds in Common; Quarter/Gold declarations are back
inside their owning files. One transaction processor runs material/fixed/
population sections; material hosts and the route read model keep their late
load phases. Removed redundant generated rows and two dead Bakery roots.

All actions have explicit LoadOrder. Ordering is numeric LoadOrder, alphabetical
action type, alphabetical action ID. Compatible declarative actions combined;
runtime contexts retain identities. JSON is source, project CDATA regenerated.
Worktree actions109→90; committed base105→87. Existing art/lens/Pedia/localization
work and Tailors PLUNDER_GOLD edit are preserved separately from this commit.

Before/after SQL compared25 native/economic tables across16 option combinations;
only dead roots/three arguments differ. Checked-in regression hashes preserve
that reference.83 transaction,123 economy,175 selected Quarter,9 manifest,
2 package tests pass; lens suite passes. Full Quarter sweep still has stale
Fashion population/trade fixtures (8 methods) and design/localization locks.
Fashion test/runtime/fixture files are unchanged; do not report the full suite
as green or refresh unrelated public-design locks to conceal these results.

Native replay/package helper paths follow the new files. No CE/native binary
or AI policy change was needed. No game/controller/FireTuner launch occurred.
