# Fresh start for CSC AI tuning

3 November 2026. Henno authorized a new native placement-choice experiment and
asked to archive earlier tuning so its assumptions would not become defaults.

The old runtime tuning is retired. Seventeen SQL/Lua/UI/localization files were
moved into `project/archive/ai-tuning-20261103/retired/`, after verified current-byte
backups. The archive also snapshots the historical research tools. Their reports
remain evidence; their weights, private signals, subsidies and scripted placement
policies are not inputs to the new experiment.

The active ModBuddy action source and generated project remove15 AI actions and
three criteria. The assistance/subsidy options and labels are removed. A shared
UI yield-filter import remains solely to satisfy existing lens/tooltip includes;
it creates no yield and makes no AI decisions. Quarter gameplay, compatibility,
adjacencies, resource-map preparation and art are preserved.

The installed package was reset independently by transforming only its modinfo
and two Settings XML files. Backups and the complete before/after manifests prove
that every other installed byte was preserved. This is the requested new baseline,
not a temporary test treatment that will reinstall old tuning on cleanup.

The new implementation is `project/tools/native_ai/quarter_placement_trial/`.
Session launch, content selection, restoration and provenance helpers were
promoted into `full_game_controller/environment.py`; these contain no placement
heuristic. The experiment uses the maintained shared controller.

Its first policy is deliberately a mechanism test: capture fresh eligible native
scores and choose a distinct, clear, owned, revealed, unreserved alternative.
Add the measured score gap plus one utility unit, then observe native choice,
request and construction. It does not yet define good supply-chain placement.
The source world is an existing save rebased onto the clean rules; historical
map development is retained, not erased or called a fresh-world comparison.

Source archive application and restoration passed an isolated filesystem test.
Installed two-/three-file reset and restore, owner refusal and preservation of
later edits passed isolated package tests. Actual runtime absence of old inputs
is a separate source gate before the native experiment.

Evidence: `Desktop/Codex/csc-native-placement-choice-20261103/` (staged under the
current chat's visualization directory). The source archive manifest is versioned
with the repository; large game/save/art artifacts are not copied into it.
