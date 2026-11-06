# Civ VI November hotfix and the CSC AI hooks

The Windows Steam install is on build `26407122` following Firaxis's 5 November
security hotfix. This report compares its exact Gathering Storm GameCore with
the DLL used in the previous CSC placement tests.
[Firaxis announcement](https://store.steampowered.com/oldnews/?appids=289070&feed=steam_community_announcements&l=hungarian)

| Windows XP2 build | GameCore SHA-256 | PE timestamp | Image size |
| --- | --- | ---: | ---: |
| Earlier qualified reference | `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c` | 1719431003 | 12,976,128 |
| November hotfix | `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f` | 1793649108 | 12,976,128 |

## GameCore code and layout

The two GameCore images have the same section layout and identical `.text`,
including all 10,180,608 raw section bytes. `.data`, unwind entries, relocations,
resources, TLS and control-flow guard sections also match. The `.rdata` comparison
reconciles after accounting for 533 build-path tokens, export and debug timestamps,
and the CodeView PDB GUID. The PE certificate table changed. All 157 export
names, ordinals and targets match. This compares XP2 files and gives no diagnosis
of the security issue addressed by the patch.

| Contract | RVA on both images |
| --- | --- |
| `RegisterScriptData` prefix guard | `0x5bdac0` |
| District `NetValue` | `0x52a440` |
| Plot analysis call and return | `0x3e30b9` → `0x3e30be` |
| `CalculateDistrictValues` | `0x3dfee0` |
| `DoTurnActivate` aggregation call and return | `0x3e293c` → `0x3e2941` |
| `GetBestDistrict` | `0x3e4a50` |
| District `PresentValueOf` | `0x3e7f40` |

REA and Ghidra decompiled the four hooks and their enclosing decision paths
on the hotfix hash. `DoTurnActivate` still calls aggregation before district
selection. The aggregation writes via the editable district matrix, while the
selector and the plot present-value path read the row's score pointer at
`+0x20`. The same machine code supports carrying over the reviewed ABI and
layout assumptions for these functions. All entry prefixes and both direct
call displacements were checked independently against the PE bytes.
[Previous runtime and ABI qualification](csc-ce-late-score-api-20261105.md)

The main DX11 `CivilizationVI.exe` hash changed from `e7450823…` to `d1a0cfd4…`.
CE's shared Runtime also resolves functions in that executable, including the
Lua critical-section entry points. The GameCore comparison leaves those
executable contracts outside its scope. Public CE `develop` still pointed to
`2986a74` when checked. The executable and shared-hook qualification belong
with the CE compatibility work.

## Porting scope

The CE hotfix candidate keeps the reviewed hooks, addresses, ABI, layout and
prefix checks. It changes the exact accepted GameCore SHA and PE timestamp in
the named target profile. The prior tested branch remains the reference for
the earlier binary. The candidate is intended to be applied on top of a
compatible CE `develop` base and qualified there before native CE use.

The candidate builds with CE's existing MSVC Release x64 project. The build
reports 144 warnings and zero errors, matching the earlier supported build's
warning count. The 50 isolated score checks and four hook-group checks pass.
The built DLL SHA-256 is
`c39a24fd5d1af7e191edeefec10b1d5f8e2280a17c173bc5d944ec313f93118d`.
[CE hotfix candidate `e67b4a2`](https://github.com/hennogous/CivilizationVI_CommunityExtension/commit/e67b4a2805615495ed1469b4fdb4488d5f8c21d3)

The stock research observer accepts the two exact verified identities. The
explicit `--hotfix-baseline` replay selects the patched build and starts a new
control. Historical pulse and correction receipts remain associated with their
original build. The replay uses the shared controller, the exact earlier
Online turn-1 checkpoint and its isolated CSC package, with CE disabled and
the score writer set to zero.

## Patched stock replay

The controller loaded the exact patched XP2 DLL without a CE proxy and
advanced the saved world to turn 2. The captured starting world, complete
calibration record, district calculation, winner, present-value records and
Delhi requests match the earlier stock control. In particular:

| Observation | Earlier and patched stock result |
| --- | ---: |
| Delhi Bakers, plot 1210, aggregation entry | 77,534 Q8 |
| Delhi Bakers, plot 1210, aggregation return | 104,621 Q8 |
| Winning Neighborhood, plot 1358 | 248,223 Q8 |
| Reconstructed deduction for the same Mill forecast errors | 4,398 Q8 |

The deduction was reconstructed from the observed forecasts. The observer
recorded 361 complete pairs, zero faults and zero score writes. The shared
controller verified native exit code 0, preference restoration and retirement
of the isolated package. This is a one-turn stock result. The new CE candidate
still needs a replay of actual writes on a compatible CE base.

Evidence is under `Desktop/Codex/csc-gamecore-hotfix-20261106`, including
`pe-audit.json`, `rea-xp2-hotfix-evidence.json` and `stock-baseline/`. The frozen
stock trace SHA-256 is `c14daad7de831a85d55e297d54f3df6bf13df889aad0626d5cd4ab5edfcf6652`.
The reproducible PE audit
reads the two hash-pinned DLLs and verifies the mapped section differences,
entry prefixes and call displacements without loading either DLL.
[PE audit script](https://github.com/hennogous/Henno-Mods/blob/main/project/tools/native_ai/late_placement/audit_xp2_hotfix.py)
