# Tailor material-site density preview — 17 October 2026

Henno requested a temporary increase while Bakers and Tailors are the only implemented Quarters: **2× Base-only sites and4× both-material sites**. Version4 adds a deterministic density stage after the unchanged continental repair. Targets are relative to each actual post-v3 map, so opportunities still differ between maps and continents.

## Paired Standard maps

| Map | Base-only before → after | Both before → after | Extra copies beyond v3 | Total CSC copies |
|---|---:|---:|---:|---:|
| 1 | 71 → 142 | 2 → 8 | 16 | 17 |
| 2 | 75 → 150 | 6 → 24 | 21 | 22 |
| 3 | 140 → 281 | 5 → 21 | 35 | 38 |
| 4 | 82 → 164 | 4 → 16 | 19 | 20 |
| 5 | 94 → 189 | 0 → 5 | 18 | 18 |

Map1 is the world used for the matched AI trials. Its16 extra copies are6Sheep,5Flax,2Cotton and one eachDyes/Silk/Silver. Together with the original v3Dyes addition, total CSC assistance is17 individual resource copies on17 tiles. Base-supported sites total150 (142Base-only +8both), up from73.

## All captured resource levels

| Level | Base-only before → after, five maps | Both before → after | Density copies | Total CSC copies |
|---|---:|---:|---:|---:|
| Sparse | 464 → 931 | 11 → 49 | 98 | 103 |
| Standard | 462 → 926 | 17 → 74 | 109 | 115 |
| Abundant | 480 → 964 | 20 → 85 | 118 | 124 |

All15 captured native landscapes reach both targets in the offline replay. Density additions range15–41 copies per map. Whole-site gains can overshoot by a few because a deposit may support several centers. These counts are tile opportunities, not independent city/industry locations; clusters and exact proposed deposits remain in the output.

## Policy and verification

The minimum both-class target is abundance-scaled from4 at Abundant:3Sparse,4Standard/Abundant, higher with the richest TAR presets. This explicitly handles zero reference sites. There are no equal continent quotas. Targets are feasible aims under native eligibility and safety ceilings; failed targets are visible in the audit. Density ceilings are5% of passable land times abundance scale globally and8% per continent, separate from the original repair limits.

Only empty native-eligible plots receive one copy each. Existing resources, feature/terrain and quantities are retained. The density stage excludes exact starts, reserves intended Quarter centers, preserves Baker Base/both site counts per continent and retains the last existing material coverage. Shared Flax can incidentally help Bakers. No design-only Quarter drives placement. Continental soft palettes and actual loaded material classes include optional mapped modded resources.

The original v3 repair additions reproduce exactly on all15 maps. Independent continent censuses match the new audit, all15 targets pass, and a repeated Standard1 plan is identical. Actual entry-point tests pass on five native eligibility fixtures: re-entry/save/disabled/late/unknown-setting guards, complete rollback after a forced write failure, two-resource repair, optional class resolution and all ten vanilla/TAR profile combinations. Shared engine RNG draws remain zero. The tests use the archived full-expansion gameplay DB; main-menu cleanup had reset the live cache to base-game content.

Evidence: `Desktop/Codex/csc-tailor-density-20261017/candidate-02/` contains plans, proposed worlds, CSV/JSON summaries, entry-point validation and the preserved installed v3 core. The earlier exploratory run in the parent folder had restrictive caps and no zero-site floor; candidate02 is the reviewed source.

**Status: implemented, deployed and validated on [six fresh native maps](csc-tailor-density-native-20261017.md), three Standard and three Abundant.** Historical v3 map/AI evidence and the pre-v4 installed backup remain unchanged. Existing native study and matched-AI scripts assume v3 and must be adapted for a new v4 baseline; they cannot regenerate the previous starting resource maps after updating the installed pass.

Tuning lives in `C.SiteMultipliers` and `C.SiteMinimums` in CSC_MaterialMapCore.lua. Revisit the temporary Tailor emphasis as more Quarters become playable.
