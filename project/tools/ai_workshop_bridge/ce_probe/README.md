# CE-dependent memory capability probe

This is a Lua-only diagnostic package depending on the existing Community
Extension Workshop mod. It contains no native binary, registers no native hook,
and never writes memory. It is separate from the independent native carrier.

Build with Python and explicit `--gamecore` and `--output` paths. The builder
qualifies the pristine XP2 SHA and creates `package/` plus a source/hash manifest.
It does not deploy, publish, attach to or launch Civ. Run native checks only
through the maintained shared controller and archive Lua.log.

The script fingerprints mapped PE headers and three function prefixes, then
uses normal gameplay event callbacks to inspect bounded cache snapshots. The
entire-file hash is verified at build time and must also be independently
verified for the actual loaded DLL by the controller. Header/prefix matching is
not a replacement for that identity proof.

Current-build pointer path (all offsets hexadecimal):

1. Global Game instance pointer at `b8aa68`.
2. Game `+240` points to player manager; manager `+20` to player pointer array.
3. Array `+8*playerID` points to Player::Instance; player `+650` to CityManager.
4. CityManager `+98` points to a null-terminated linked list. Each node `+0`
   points to CityBuild; node `+10` points to the next node.
5. CityBuild `+90` points to the city. Owner `+d8`, ID `+a8`, XY `+c0/+c4`
   are checked against normal Lua city getters before reading cache data.
6. CityBuild `+4c8` points to `+78`-stride plot rows; row count is `+4d8`.
   Row `+20` points to signed Q8 district scores; coordinates are `+8/+c`.

These are Win64 offsets for the pinned DLL, not the Linux reference-layout
offsets. In particular, the latter's Player city-manager `+658` is incorrect
for this binary. `Players[id].__instance` is a Lua reference wrapper and is
deliberately not dereferenced as Player::Instance.

Primary static anchors: GetPlayer `63d080`, InitializeAiSystems `2f9350`,
CityManager DoTurnActivate `3d9130`, CityBuild Initialize `3e64e0`, plot
initialization `3e7030`, and GetBestDistrict `3e4a50`.

The CE API does not expose safe pointer-span validation. Numeric null/alignment
checks, list/array bounds, exact version guards and identity matching reduce
uncertainty but cannot make a bad native pointer safe. Lua `pcall` handles Lua
errors, not access violations. The probe disables after its first Lua error.

Observations cover available module-load, game-turn-start, player-turn-start
and player-activation callbacks. Job-done `4c0` and offturn-done `1b0` flags
gate score reads, but these are observations rather than locks. A successful
read would establish cache access only. It would not prove a synchronized
write window, that edits survive refresh/aggregation, a replacement hook,
save/load safety, selection effects or a shipping AI policy.

Native result: CE-only Online1–3 read55city and174score observations, with no
memory writes or diagnostic disable. The selected local CE1.3 DLL was byte-identical
to Workshop3277976174. The new CE score API was absent. Earlier menu-only attempts
exposed duplicate-GUID dependency resolution; failed read-probe branches exposed
missing `_G` and numeric-string FIELD_* constants. Use tonumber for capability
validation. These details are preserved in the dated delivery report.
