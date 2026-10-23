# Native AI completion of fixed-site Quarter foundations

**Result: all four placed foundations were selected and completed by native AI, without additional completion incentives or scripted production orders.**

This is a successful mechanism demonstration with a later native crash. It is not a completed 75-round stability validation.

| AI | Plot | Placement | First observed queue at chosen site | Completed | Elapsed | Initial production / cost |
|---|---:|---:|---:|---:|---:|---|
| Germany (Ludwig) | 1195 | 73 | 75 | 76 | 3 | 0 / 17 |
| Phoenicia (Dido) | 1619 | 73 | 75 | 75 | 2 | 0 / 17 |
| Vietnam (Lady Trieu) | 2020 | 73 | 75 | 77 | 4 | 0 / 17 |
| Greece (Pericles) | 784 | 73 | 75 | 76 | 3 | 0 / 17 |

## What was demonstrated

The test uses normal Gathering Storm/Continents rules, Medieval start71, Online/Prince/Small/Standard resources, seeds830102/940104, and CSC with its accepted AI baseline unchanged. Black Death scenario scripts/rules are not used. Its code was only the research lead; foundation creation uses the native base-game BuildQueue API also called by Firaxis TunerCityPanel.

At73 the script chose at most one native-legal owned empty feature-free site per AI player, requiring owned visible mapped Base materials nearby. Germany/Phoenicia/Vietnam/Greece qualified; Nubia had no qualifying site and was skipped. All chosen foundations happened to be Bakers. The script called CreateIncompleteDistrict(Index,plot,0), but did not add a BUILD order, grant production or research, create cities, alter population/materials or install any gameplay overlay.

Independent UI readbacks immediately before/after placement report progress 0, cost 17 unchanged, and production queue size 0. Placement therefore created an incomplete district, not an immediate queue order. Later UI queues explicitly contain DistrictType 36 and the exact chosen x/y site for each AI. Native construction events and district IsComplete readbacks corroborate completion. Native events appear twice in some cases; the audit deduplicates by player/city/type/turn and counts four physical districts, not event rows.

Vietnam supplies a direct intermediate production sample:14/17 at 76, then complete 77. Other sampled cases can finish within one production cycle, so no positive intermediate progress was observed for them; that missing sample is not treated as zero production spent. Their normal queue and completion events still corroborate native construction.

All four remained complete at the same plot and owner through the exported native turn 140. Native player-turn coverage 73–140 is complete for all four targets, plus their four immediate placement readbacks:276 rows. UI exports contain296 samples through141, including duplicate periodic readbacks; this is not 296 independent player turns.

## Crash and restoration

The final successful native progress poll was 147; target 148 was not verified. The process window explicitly reported an EXCEPTION_ACCESS_VIOLATION in CivilizationVI_DX12.exe. Logs, available dump files and autosaves through filename 147 are archived. Crash cause is unknown: do not conclude that DX12 alone caused it or that the foundation/observer code was unrelated. The crash occurred long after the completion evidence was exported.

A menu-only cleanup relaunch is separate from a test replay. No test game was loaded or restarted for cleanup. Current restoration metadata: {"verified": true, "unique_mods": 144, "auto_start": false, "installed_files_unchanged": 122, "no_test_game_restarted": true, "cleanup_only_main_menu_relaunch": true, "native_readback": "cleanup-menu-resume/commands"}. All 122 installed gameplay files independently match the original archived hashes.

## Interpretation and next boundary

The core handoff works in these four cases. A temporary Districts favored strategy is not required to explain these completions and was not tested. It remains a contingency for other cases that genuinely stall. This evidence does not validate an automatic city/site/district planner, opportunity costs of reserving a plot/slot, every district type, Tailors foundations, Ancient-start balance, load/duplicate lifecycle or long-run stability. No candidate was deployed.

The original v1/v2 instrument failures and their terminal audit are retained as historical evidence. Renewed explicit user authorization allowed the corrected UI-context v3 test. Full machine-readable audit: continuation-v3/completion-audit.json; source snapshots and native/UI observations are alongside it.
