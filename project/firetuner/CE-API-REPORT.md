# Community Extension API Report
*2026-04-01 — Bill, from wiki docs + live testing via FireTuner*

## Overview

The Community Extension (CE) by Wild-W is a DLL mod that hooks into Civ 6's GameCore, exposing functionality that's normally inaccessible from Lua. It provides:

1. **Direct memory read/write** on game objects
2. **New singleton managers** for trade, culture, economy, governors, etc.
3. **Processor hooks** to intercept and modify AI decisions
4. **Event callbacks** on native C++ functions

All CE APIs are available from **GameCore context (FireTuner state 3)** only.

---

## 1. Memory Manipulation

### `Mem(address, fieldType [, newValue])` — Global Memory
Reads/writes global GameCore memory. Rarely useful directly.

### `ObjMem(object, offset, fieldType [, newValue])` — Instance Memory
Reads/writes memory on any game object with an `__instance` field (plots, units, players, cities, etc.).

**Confirmed working:**
```lua
-- Read plot appeal
local appeal = ObjMem(plot, 0x4a, FIELD_SHORT)  -- returns integer

-- Write plot appeal
ObjMem(plot, 0x4a, FIELD_SHORT, 900)
```

### Field Types
| Constant | C Type | Size |
|---|---|---|
| `FIELD_BYTE` (0) | unsigned char | 1 |
| `FIELD_SHORT` (1) | short | 2 |
| `FIELD_UNSIGNED_SHORT` (2) | unsigned short | 2 |
| `FIELD_INT` (3) | int | 4 |
| `FIELD_UNSIGNED_INT` (4) | unsigned int | 4 |
| `FIELD_LONG_LONG` (5) | long long | 8 |
| `FIELD_UNSIGNED_LONG_LONG` (6) | unsigned long long | 8 |
| `FIELD_CHAR` (7) | char | 1 |
| `FIELD_FLOAT` (8) | float | 4 |
| `FIELD_DOUBLE` (9) | double | 8 |
| `FIELD_C_STRING` (10) | char* | 8 |
| `FIELD_BOOL` (11) | bool | 1 |
| `FIELD_POINTER` (12) | unsigned long long | 8 |

### Known Offsets

| Object | Offset | Type | Description |
|---|---|---|---|
| Plot | 0x4a | FIELD_SHORT | Appeal |
| PlayerInfluence | 0xb8 | FIELD_UNSIGNED_INT | Influence points × 256 |
| Player | 0xd8 | FIELD_INT | Unknown |
| UnitExperience | 0xc | FIELD_INT | XP amount |
| UnitExperience | 0x10 | FIELD_INT | Level |
| Unit | 0x128 | FIELD_INT | Owner player ID (read-only — use UnitManager.ChangeOwner to transfer) |

**CSC relevance:** ObjMem lets us read/write ANY game value if we know the offset. This means we can implement custom mechanics (e.g., supply chain bonuses) by modifying yields, appeal, or any other property at the memory level. Finding new offsets requires IDA/Ghidra analysis of the GameCore DLL.

---

## 2. Singleton Managers

### CityTradeManager
```lua
CityTradeManager.SetHasConstructedTradingPost(city, playerId, toConstruct)
```
Creates or destroys a trading post in a city for a specific player. Useful for CSC supply chain connections.

### CultureManager
```lua
local gwIndex = CultureManager.FindOrAddGreatWork(GameInfo.GreatWorks.GREATWORK_MICHELANGELO_1.Index)
CultureManager.SetGreatWorkPlayer(gwIndex, playerId)
Players[playerId]:GetCities():AddGreatWork(gwIndex)
```
Create great works programmatically and assign them to players/cities.

### EconomicManager
```lua
EconomicManager.SetMonopolyTourismMultiplier(amount)         -- global
EconomicManager.SetMonopolyTourismMultiplier(playerId, amount) -- per-player
EconomicManager.GetTourismFromMonopolies(playerId)            -- returns int
```
Control monopoly tourism multipliers. Could be used for CSC trade bonuses.

### EmergencyManager
```lua
EmergencyManager.ChangePlayerScore(playerId, emergencyHash, amount)
```
Modify emergency/competition scores.

### GovernorManager
```lua
GovernorManager.GetTurnsToEstablishDelay(playerId, governorHash, ui)
GovernorManager.SetTurnsToEstablishDelay(playerId, governorHash, amount, updateUi)
GovernorManager.ChangeTurnsToEstablishDelay(playerId, governorHash, amount, updateUi)
```
Modify governor establishment time. The `ui` parameter controls whether the displayed value or the actual value is affected.

### UnitManager
```lua
local unit = UnitManager.GetInstance(address)  -- from memory address
local newUnit = UnitManager.ChangeOwner(unit, newPlayerId, false, false)
```
Get unit instances from memory addresses, transfer unit ownership between players.

### NationalParks
```lua
NationalParks.DesignatePark(playerId, plotX, plotY)
local parkData = NationalParks.FindPark(plotX, plotY)
NationalParks.RestoreVisualState(parkData)
```
Create national parks programmatically and query existing ones.

---

## 3. Extended Object Methods

### Plot
```lua
plot:SetAppeal(value)   -- will be overwritten by game unless locked
plot:LockAppeal(true)   -- prevents game from recalculating appeal
```

### PlayerCities
```lua
cities:AddGreatWork(greatWorkListIndex)  -- find a city to add the great work to
```

### PlayerInfluence
```lua
influence:SetTokensToGive(amount)  -- set free envoys
influence:SetPoints(amount)        -- set influence points (overflow carries over)
influence:AdjustPoints(amount)     -- adjust influence points
```

### GameDiplomacy
```lua
diplomacy:ChangeGrievanceScore(player1Id, player2Id)  -- does NOT update UI immediately
```

---

## 4. Processors — AI Decision Interception

### RegisterProcessor(name, callback)
Hooks into AI decision-making functions. The callback receives an info table with immutable and mutable parameters. Return `true` to stop execution (override), `false` to pass through.

**Available Processors:**

| Name | Immutable | Mutable | Description |
|---|---|---|---|
| `DistrictTargetChooser` | `PlayerId`, `OutcomeType` | `DistrictIndex` | AI district scoring for World Congress votes. Original algorithm scores by building count. |

**Confirmed working (with caveats):**
```lua
RegisterProcessor("DistrictTargetChooser", function(info)
    print("Player=" .. info.PlayerId .. " District=" .. info.DistrictIndex)
    info.DistrictIndex = GameInfo.Districts.DISTRICT_CITY_CENTER.Index
    return true  -- override
end)
```

**WARNING:** The CE wiki explicitly warns: *"RegisterProcessor suffers from potential race conditions. Every so often it could crash the game!"* In our testing, it fired for ALL players on EVERY turn during autoplay, generating massive output. Use sparingly.

### RegisterCallEvent(callback, address, paramTypes) — EXPERIMENTAL
Registers a callback at a specific C++ function address. Captures up to 4 arguments.

```lua
RegisterCallEvent(OnPlayerUnitsDestroy, 0x34d4e0, { FIELD_POINTER, FIELD_POINTER })
```

**Status: "Under construction"** per wiki. Avoid in production.

---

## 5. Confirmed Working in Live Game (2026-04-01)

All confirmed from FireTuner state 3 in a live game:

| API | Status |
|---|---|
| `Mem` | ✓ Available |
| `ObjMem` | ✓ Tested — read plot appeal |
| `RegisterProcessor` | ✓ Tested — DistrictTargetChooser fires |
| `CityTradeManager` | ✓ Available (not exercised) |
| `CultureManager` | ✓ Available (not exercised) |
| `UnitManager` | ✓ Available (not exercised) |
| `GovernorManager` | ✓ Available (not exercised) |
| `NationalParks` | ✓ Available (not exercised) |
| `EconomicManager` | ✓ Available (not exercised) |
| `FIELD_SHORT` etc. | ✓ Constants available |
| `OutcomeTypes` | ✓ Available |

---

## 6. CSC Relevance

### What CE enables for CSC:
- **Custom yield bonuses** via ObjMem (write to city/plot yield offsets)
- **Trading post manipulation** via CityTradeManager (supply chain connections)
- **AI decision interception** via RegisterProcessor (AI Quarter placement preferences)
- **Governor timing** via GovernorManager (could tie to supply chain bonuses)
- **Memory inspection** for debugging (read any game state without API)

### What CE doesn't provide (that CSC would need):
- No way to add new resource types at runtime
- No way to modify the database at runtime (SQL changes are pre-game only)
- No custom UI rendering (CE is GameCore only, not UI)
- RegisterProcessor only has one hook point (DistrictTargetChooser) — no hooks for city production, unit building, etc.
- RegisterCallEvent is experimental and unstable

### Key limitation for autonomous operation:
CE's DLL (`CivilizationVI_CommunityExtension.dll`) must be loaded at game start. It hooks into GameCore DLL loading, which makes it sensitive to load order and timing. The crash we're seeing (`Failed to load GameCore DLL` / access violation at 0x159a4fcb5) is likely a CE initialization issue triggered by non-standard game start sequences. This should be reported to Wild-W.

---

## 7. Source & References

- Wiki: `csc/community-extension-wiki/` (cloned from GitHub)
- Source: `csc/community-extension/` (C++ DLL source)
- CE mod ID in Mods.sqlite: `ModRowId=1431`, GUID `3351473b-0746-417a-a618-2b66a04d8f3d`
- Mod folder: `Documents\My Games\Sid Meier's Civilization VI\Mods\CivilizationVI_CommunityExtension\`
