# Native material-marker experiment — rejected

17 October 2026. The user asked to try native adjacency instead of the earlier conditional material modifiers, then stopped the direction because of its accumulating tradeoffs. The experiment is removed from active CSC source and the installed test build. Sales adjacency and the general improvement preference remain. The old material modifiers remain removed.

## What worked

A separate hidden feature type for each mapped Bakers/Tailors resource fed native `AdjacentFeature` rules with the private placement yield: +12 per Base neighbour and +4 per Specialty neighbour. Twenty feature types produced 21 material edges. Resources with reveal prerequisites and deposits already carrying real features were excluded. No real feature was replaced; 1,156 real features were preserved in the smoke fixture.

Paired native prospective `Plot:GetAdjacencyYield` values:

| Fixture | Markers off | Markers on | Difference |
|---|---:|---:|---:|
| Bakers Base | 10 | 22 | 12 |
| Bakers Specialty | 10 | 18 | 8 (two deposits) |
| Tailors Base | 0 | 12 | 12 |
| Tailors Specialty | 0 | 4 | 4 |

The removable-feature candidate preserved tested district and improvement legality, six real tile yields, appeal and resource quantity. Normal native Builder requests successfully built a Farm, Plantation and Mine with one charge consumed each. Resource-removal events cleaned up the marker. Save/reload worked. UI enumeration filtering and a UnitPanel patch hid markers and their clear action in the tested API contexts. Pixel-level visual verification was unavailable.

## Why it was rejected

A Civ feature is a gameplay object. Making the marker removable exposed a zero-yield clear-feature operation to the native AI. Making it non-removable suppressed clearing but blocked district construction on tested bonus-resource tiles. Hiding the human button did not change AI planning.

In the controlled 20-turn run, markers repeatedly disappeared from still-present, unimproved resource plots and were reinstated by the refresh script. Plot 1717 (Maize) lost its marker at turns 9, 10 and 18; plot 1617 (Cattle) at turns 10 and 17. These deposits still had no improvement or district at turn 20. This clearing/replacement loop is the decisive failure. Separate removals due to settlement or district construction were expected and are distinguishable in the event log.

Other limitations were already present: the single feature slot excluded Woods/Rainforest/etc., shared markers rewarded foreign/unowned deposits, and per-deposit counting differed from the earlier owned, once-per-class condition. Hiding art cannot remove those mechanical effects.

Revision 3 attempted to withhold markers near Builders. It was hot-loaded after turn 20 but received no further AI turns before rejection. It is an unvalidated workaround, not a solution.

## Trial scope and provenance

This was a deliberately modified disposable seed-1 fixture with prearranged cities, research grants and a legal added Silver deposit. It is **not** a natural baseline or a valid treatment comparison. The 20-turn observer retained 12 Quarter placements including city states, nine for major players, with zero observer errors. Those placements do not establish efficacy.

Evidence root: `C:/Users/Shadow/Desktop/Codex/csc-ai-markers-v2-20261017/`.

- `deploy-final/deployment.json` pins the tested revision-2 files. `native/marker-summary.json` records those hashes and paired smoke results.
- `native/controlled-ai/` retains turn-1/20 snapshots, commands and `marker-events.json`.
- `native/final-*.json` retains paired API, Builder, UnitPanel and resource-removal results.
- `rejected-source/` preserves the final attempted source, including the untested revision-3 guard. The unregistered module also lives at `project/tools/ai_baseline/experiments/rejected_CSC_AI_MaterialMarkers.lua`.
- `rollback/` retains focused installed backups, generated SDK manifest, deployment and SQL-validation results.

## Cleanup

The live disabled-module refresh removed all 66 remaining markers before returning to the menu. Original mod preferences (141 unique IDs) and auto-start=false were restored and verified, then Civ exited. Source and installed marker actions/file registrations were removed; the installed gameplay module was deleted after backup. Marker-specific feature UI filtering and UnitPanel changes were removed. No new game was launched after rollback.

Current SQL validates 33 sales edges, no material adjacency or conditional material modifiers, repeat-application equality and global improvement default 3.0. UI facade and shipped ReportScreen worked-tile checks pass. Other installed action trees were preserved by the focused deployer. This experiment established preview recognition, not a safe material-guidance implementation.
