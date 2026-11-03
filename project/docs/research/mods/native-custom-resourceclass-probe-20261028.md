# Native custom resource-class adjacency probe — 28 October 2026

**Result: the custom class works for native adjacency matching and district yield.**

The [multi-value follow-up](native-resourceclass-multivalue-probe-20261028.md)
tested whether one field could encode several memberships: comma variants,
other separators and JSON arrays all matched only as whole literal identifiers.
Changing Wheat's `Resources.ResourceClassType` to a new string and referencing
that string in `Adjacency_YieldChanges.AdjacentResourceClass` produced +10 Food
on a Campus beside Wheat. The simultaneous +10 Faith control from
`RESOURCECLASS_BONUS` matched Rice and excluded the reclassified Wheat.

## Exact setup

- Gathering Storm, DX11, only official content and the standalone probe enabled.
- Probe ID: `a6f8220f-d358-4ca4-b698-84368ee75f10`.
- Wheat reassigned to `RESOURCECLASS_CSC_PROBE_WHEAT`; Rice retained its bonus class.
- Campus adjacency: +10 Food per adjacent custom-class resource; +10 Faith per
  adjacent bonus-class resource; `TilesRequired=1` and `AdjacentResource=0` on both rows.
- No City Center condition. Henno clarified that the target was a Campus beside Wheat.
- No `Tags`, `TypeTags`, resource-class `Types` registration, custom class table,
  scripted adjacency, or yield modifiers. Vanilla has no `ResourceClasses` table
  or `KIND_RESOURCECLASS`; assigning the new string introduces it to this field.
- Fixed Pangaea Duel world, map seed 281029, game seed 281028; fixtures on real
  land. Player 0 city 65536, center 200, Campus 244, Wheat 201, Rice 243.

The operative resource change is:

```sql
UPDATE Resources
SET ResourceClassType = 'RESOURCECLASS_CSC_PROBE_WHEAT'
WHERE ResourceType = 'RESOURCE_WHEAT';
```

## Measurements

| Adjacent resources | Custom-class Food | Bonus-class Faith |
|---|---:|---:|
| None | 0 | 0 |
| Wheat only | 10 | 0 |
| Rice only | 0 | 10 |
| Wheat and Rice | 10 | 10 |
| Both removed | 0 | 0 |

All five phases passed before Campus placement and again with the Campus
complete. Native `Plot:GetAdjacencyYield`, `District:GetAdjacencyYield`, and
`District:GetYield` agreed for the completed district. The verifier also checked
all six neighboring plots and the loaded class/adjacency rows. Ten samples pass.

These are within-turn-1 matching and district-yield observations. No turns were
advanced. The newly created city's `GetYield` totals remained at their cached
baseline during these mutations, including the Faith positive control. Therefore
this probe does **not** establish per-turn city/player economic receipts, other
resource-class consumers, save/reload behavior, AI valuation, or production
suitability. It does refute the claim that the custom class cannot match in a
native district adjacency.

This changes Wheat's one native class; it does not add another simultaneous
membership. Wheat no longer matches `RESOURCECLASS_BONUS` in this test.

## Provenance and recovery

An exploratory draft mistakenly set `AdjacentResource=1` as well as a class.
That flag adds an independent any-resource contribution: Wheat-only yielded
20 Food/10 Faith, Rice-only 10 Food/20 Faith, and both 30/30. That draft is
archived separately and excluded from the clean table above.

The clean test was loaded afresh with both flags zero. A completion assertion
then encountered the gameplay context's missing `Districts:IsComplete` method
after creating the Campus. An independent UI read verified that the Campus was
already complete; the remaining phases continued without recreating it.
The UI context supports that completion query and district `Members`, whereas
the tuner gameplay context exposes indexed district iteration.

Native commands use the maintained `FullGameController`, its one-send transport,
and fresh context discovery under `project/tools/ai_baseline/full_game_controller/`.
Restoration uses `native_profile_test.restore_preferences` with exact installation
identities; same-ID duplicates were independently checked against the pretest DB.
No computer use is permitted on Shadow; use these project tools for native tests.

## Evidence and cleanup

Evidence root: `C:\Users\Shadow\Desktop\Codex\resourceclass-probe-20261028`.

- `custom/package/Probe.sql` and the `.modinfo`: clean standalone mod.
- `custom/native-database.json`, `custom/DebugGameplay.sqlite`: actual loaded rows.
- `custom/results.json`, `custom/verification.json`, `verification.json`: observations and assertions.
- `commands/`, `controller-journal.ndjson`, `custom/logs/`: native commands and logs.
- `exploratory-any-resource-flag/`: excluded first draft and measurements.
- `restoration.json`, `exact-preferences/preferences-restored.json`: independent
  native readback of all 145 mod IDs / 148 installation entries and auto-start false.

The standalone probe remains installed **disabled**. Original mod selections were
restored; existing CSC source and installed package files were not edited. The
assistant-started game was closed through the shipped `FrontEndPopup.ExitOK()`.
