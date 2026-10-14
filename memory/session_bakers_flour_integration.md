# Bakers flour integration — 7 October 2026

Completed the Windows integration of `Working Files/3D Art/Props/Bakers/Bakers_Flour_FINAL` after merging expanded art into main CSC.

- Henno explicitly requested retaining the original runtime names: `CSC_BAKERS_Flour`, `CSC_BAKERS_Flour_Closed`, `CSC_BAKERS_Flour_Open`. The package's `CSC_ALL_Flour_*` identities map to those names; no temporary entries remain in the active project.
- Retired original AST/FGX/GEO files are in `C:\Users\Shadow\Desktop\Archive\CSC Bakers Flour - retired 2026-10-07`. Recovery/staging/build evidence is in `C:\Users\Shadow\Desktop\Codex\bakers-flour-integration-20261007`.
- Uses existing `CSC_ALL_Props_01` and authoritative Shared 01 r021. Package texture maps match Current; no new material/texture IDs. Source handoff files unchanged.
- All 156 placements across 23 assets migrated, including normal/expanded buildings. Preserved position/orientation/bone/parent/state behavior. Pile geometry has baked 0.2 scale: attachment 0.2 → 1.0, 0.15 → 0.75. Sack scales unchanged.
- Old/new FGX readback: pile 138 → 66 vertices; closed sack 304 → 140; open sack 248 → 122. Unique total 690 → 328; weighted authored placements 42,986 → 19,980 (23,006 saved). These are alternative asset definitions, not one simultaneous scene; no FPS measurement.
- Standard ModBuddy Windows/Mac cooks passed. Asset Editor cache still lists old material dependencies; reopen/refresh before visual review. Cache not manually patched. Asset Editor appearance and in-game review pending.
- Verified build installed into the game Mods folder; 449 staged files matched the build output. Previous installation retained under the task evidence directory.

Durable report: [Bakers flour integration](../project/docs/art/bakers-flour-integration.md).
