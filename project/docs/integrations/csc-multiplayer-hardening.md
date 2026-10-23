# CSC multiplayer runtime hardening

20 October 2026. Implemented in source and tested offline. No games were launched,
no installed mod was updated, and no multiplayer acceptance is implied.

## Deterministic mutation order

| Subsystem | Order |
|---|---|
| Adjacency | Collect native district instances, sort by plot index, then write each district's already sorted rule list. Clear stale plots by sorted index. |
| Customer population returns | Sort actual alive players and each player's city instances; sort registry transactions and direct replacement families. Process city-state keys, property names and Fashion House return branches in sorted order. Bit arrays and six-direction traversal remain fixed. |
| Art-property mirror | Sort actual alive players and their cities; retain the fixed source/art property mapping. |
| Wonder Services | Keep existing numeric player/city ordering and fixed host list; also sort remembered marker keys before stale-marker cleanup. |
| Trade routes | Sort actual alive players/cities for scanning and numeric owner/city IDs for submissions. The gameplay receiver uses a fixed field/bit schema. |

`pairs()` remains appropriate for gathering keys/records before sorting, and for
read-only membership/count operations. It no longer directly determines property
write order in these paths. Native collection iteration is not assumed stable.
Player counts are not used as player-ID ranges: actual alive entries include
sparse IDs and exclude unavailable city collections.

## Trade-route submission authority

`CSC_TradeRouteInteractions.lua` stays in UI because active route lists are a UI
API. During network multiplayer, only the client whose `Game.GetLocalPlayer()`
equals `Network.GetGameHostPlayerID()` submits updates. That host scans all cities,
including AI cities. Single-player/hotseat use the current local player on the
single UI instance. A negative/unavailable local player submits nothing.

Every request uses the **local sender ID**, rather than impersonating the target
city's owner. Target owner, city ID and coordinates are separate payload fields.
The host is checked afresh on each pass, and `MultiplayerHostMigrated` requests a
new scan. There is no persistent host lock to strand after migration.

UI events coalesce into one scan on the next `ContextPtr:SetUpdate` callback.
`CityPropertyChanged` catches changes to SQL supply properties; route, city,
building, research and load events also schedule refreshes. Outstanding requests
cause a fresh scan once per UI second until the properties agree. There is no
continuous full scan once state agrees.

All mutations still travel through `UI.RequestPlayerOperation` with
`PlayerOperations.EXECUTE_SCRIPT`. No UI callback directly calls a gameplay writer.

### Snapshot validation and acknowledgement

The version-2 payload contains the game turn, city owner/ID/coordinates, nine
raw route fields and the city's saved `CSC_TRADE_ROUTE_REVISION`.

The gameplay receiver, `CSC_SetBakersTradeRouteProperties`, checks the entire
payload before the first write:

- The operation sender exists, the version matches and the turn is current.
- Identity/coordinate/revision values are bounded nonnegative integers.
- The city still exists at that coordinate with the same owner and city ID.
- The saved revision matches the request's expected revision.
- Every route count is a bounded nonnegative integer; the Quarter flag is 0/1.

It then mirrors fields to plot/city in fixed order, derives the existing export
bits from raw counts, and increments the city revision **last**. Supplied bit
fields are ignored. Duplicate and superseded requests cannot reapply old state.
An in-flight change that was not yet represented in the accepted snapshot is
corrected by the host's fresh retry, rather than replaying a cached payload.
The existing 1/2/4/8/16 encoding and gameplay amounts are preserved.

Host election is a **UI submission** decision. The synchronized receiver does not
consult local Network/UI state, which could differ while clients load/migrate.

## Loading and reconciliation

Adjacency, population-return, art-property and Wonder-Service gameplay scripts no
longer mutate state merely because the script loads, `LoadGameViewStateDone`
fires, or a client closes its loading screen. Adjacency initialization only builds
read-only rule caches. Existing saved properties/buildings remain intact.

These reconcilers use `GameEvents.PlayerTurnStarted` and
`GameEvents.OnGameTurnStarted`, plus their existing relevant gameplay mutation
events. The gameplay writers no longer use `Events.PlayerTurnActivated` as their
turn hook. A repair/migration required by an old save waits for the next shared
gameplay event/turn rather than running independently during each client's load.

The trade-route **UI** may schedule a scan on loading, but only the authority
sends network operations. Presentation-only loading hooks elsewhere remain.
The one-time material-placement adapter is also unchanged: it intentionally runs
before in-game UI, uses a dedicated map-seeded stream and has saved once-only
guards. Its multiplayer execution still needs native validation.

The dormant adjacency unit-level capability retains its UI read bridge. Current
Quarter rules do not use it; activating a rule that depends on this bridge needs
separate multiplayer validation. This work does not certify dormant sources.

## Offline evidence

`project/tools/quarter_contracts/tests/test_multiplayer_hardening.py` executes the
production Lua in isolated Lua runtimes and forces different hash/native collection
orders. Its 12 tests cover:

- Identical population/art/Wonder/adjacency mutation traces, including cleanup.
- No gameplay writes/grants during script creation or local loading events.
- Shared turn reconciliation and idempotent repeat refreshes.
- Host/nonhost submission, local sender versus AI/foreign target, host migration
  and single-process hotseat routing.
- Queued duplicates, stale revisions/turns/city identities and malformed fields.
- In-flight route changes, event coalescing, sparse player IDs and derived bits.
- Identical route-operation write traces across two separate simulated peers.

Validation on 20 October:

- **50 tests passed** across the new suite, Fashion House gameplay, Cafe population
  contract and Stage 3 registry suites.
- **14 existing QA regressions passed** against the frozen read-only gameplay DB.
  The default current-cache invocation failed during fixture setup because it
  replayed existing M&C `ImprovementModifiers` rows. No live database was changed.
- Policy returns: **220 gameplay/UI cases**, 9 mappings, 20 rules, 200 modifiers.
- Historical adjacency parity: **1,465 comparisons**, 61 rules, 610 bit modifiers,
  55 registered sources. Report: `Desktop/Codex/csc-multiplayer-hardening-20261020/parity/`.
- ModBuddy action JSON check passed; no manifest changes/new runtime files needed.

The existing isolated `lupa` dependency is at
`C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps` on Shadow. Add it to
`PYTHONPATH` when running the unittest files. Set `CSC_GAMEPLAY_DATABASE` to
`C:/Users/Shadow/Desktop/Codex/csc-adjacencies/mab-DebugGameplay.sqlite` for the
QA regression fixture, so its M&C setup starts from the expected baseline.

Native multiplayer remains pending: fresh game, simultaneous turns, save/reload,
late join/reconnect, host migration, capture/pillage and route creation/termination
while supply changes. Check AI and other-human target updates through a host's
operation sender, and verify the empty UI context's deferred refresh/retry callbacks.
The user explicitly deferred all game launches for this task.
