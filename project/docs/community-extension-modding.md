# Community Extension API Reference

The [CivilizationVI_CommunityExtension](https://github.com/Wild-W/CivilizationVI_CommunityExtension) is a DLL proxy/script extender by WildW that patches GameCore at runtime. It injects new Lua globals and object methods into the HavokScript environment, exposing capabilities the base game doesn't provide.

**Status:** Beta. AGPL 3.0 (viral — derivatives must be open source).

**How it works:** The mod ships a replacement DLL that the game loads instead of `GameCore_XP2_FinalRelease.dll`. It loads the real GameCore, hooks into the Lua state registration, and injects new globals (`Mem`, `ObjMem`, `RegisterCallEvent`, `RegisterProcessor`) plus new methods on existing game objects.

**Dependency:** Declare it in `.modinfo` as a mod dependency. Users must have the Community Extension installed (Steam Workshop or GitHub release).

**Wiki:** https://github.com/Wild-W/CivilizationVI_CommunityExtension/wiki

---

## Memory Manipulation

Direct read/write access to game memory. Powerful but fragile — offsets are tied to specific game versions.

### Mem(address, fieldType [, newValue])

Read/write global GameCore memory by offset address.

```lua
-- Read a global value
local value = Mem(0xSOME_OFFSET, FIELD_INT)
-- Write a global value
Mem(0xSOME_OFFSET, FIELD_INT, 42)
```

### ObjMem(object, address, fieldType [, newValue])

Read/write instanced memory on any game object that has an `__instance` field (plots, units, players, cities, etc.).

```lua
-- Get plot appeal (offset 0x4a)
local appeal = ObjMem(pPlot, 0x4a, FIELD_SHORT)

-- Set plot appeal
ObjMem(pPlot, 0x4a, FIELD_SHORT, 900)
```

### Field Types

| Constant | C Type | Size |
|---|---|---|
| `FIELD_BYTE` | unsigned char | 1 |
| `FIELD_SHORT` | short | 2 |
| `FIELD_UNSIGNED_SHORT` | unsigned short | 2 |
| `FIELD_INT` | int | 4 |
| `FIELD_UNSIGNED_INT` | unsigned int | 4 |
| `FIELD_LONG_LONG` | long long | 8 |
| `FIELD_UNSIGNED_LONG_LONG` | unsigned long long | 8 |
| `FIELD_CHAR` | char | 1 |
| `FIELD_FLOAT` | float | 4 |
| `FIELD_DOUBLE` | double | 8 |
| `FIELD_C_STRING` | char* | 8 |
| `FIELD_BOOL` | bool | 1 |
| `FIELD_POINTER` | unsigned long long | 8 |

### Known Instance Offsets

**Plot:**
| Offset | Type | Description |
|---|---|---|
| 0x4a | FIELD_SHORT | Plot appeal |

**PlayerInfluence:**
| Offset | Type | Description |
|---|---|---|
| 0xb8 | FIELD_UNSIGNED_INT | Total influence points × 256 |

**Player:**
| Offset | Type | Description |
|---|---|---|
| 0xd8 | FIELD_INT | Unknown (used internally for player ID in AI code) |

**Unit:**
| Offset | Type | Description |
|---|---|---|
| 0xc | FIELD_INT | Experience |
| 0x10 | FIELD_INT | Level |
| 0x128 | FIELD_INT | Owner player ID (setting alone doesn't gift the unit) |

> ⚠️ These offsets are version-specific. If Firaxis patches GameCore, they may shift. The Community Extension is maintained against the current GS build.

---

## Event Systems

### RegisterProcessor(name, processor)

Intercept and override internal game logic. The processor receives a table of parameters (some immutable, some mutable). Return `true` to stop the original function, `false` to pass through.

```lua
-- Override AI district choice in congress
RegisterProcessor("DistrictTargetChooser", function(info)
    -- info.PlayerId (read-only)
    -- info.OutcomeType (read-only) — OutcomeTypes.A or OutcomeTypes.B
    -- info.DistrictIndex (read-write) — set this to override
    
    info.DistrictIndex = GameInfo.Districts.DISTRICT_CITY_CENTER.Index
    return true  -- Stop original function
end)
```

**Available Processors:**

| Name | Immutable | Mutable | Description |
|---|---|---|---|
| `DistrictTargetChooser` | PlayerId, OutcomeType | DistrictIndex | AI chooses district for congress resolution |
| `UnitPromotionClassTargetChooser` | PlayerId, OutcomeType | UnitPromotionClassIndex | AI chooses unit promotion class |
| `UnitBuildYieldTargetChooser` | PlayerId, OutcomeType | YieldIndex | AI chooses yield type |
| `TradingPartnersTargetChooser` | PlayerId, OutcomeType | TargetPlayerId | AI chooses trading partner |
| `PlayerOrDiploLeaderTargetChooser` | PlayerId, OutcomeType | TargetPlayerId | AI chooses player target |
| `GreatPersonClassTargetChooser` | PlayerId, OutcomeType | GreatPersonClassIndex | AI chooses great person class |
| `GreatPersonPatronageTargetChooser` | PlayerId, OutcomeType | GreatPersonClassIndex | AI chooses great person patronage |
| `SpyOperationTargetChooser` | PlayerId, OutcomeType | UnitOperationIndex | AI chooses spy operation |
| `MostCommonLuxuryTargetChooser` | PlayerId, OutcomeType | ResourceIndex | AI chooses luxury resource |
| `MinorCivBonusTargetChooser` | PlayerId, OutcomeType | MinorCivBonusIndex | AI chooses city-state bonus |
| `GrievancesTypeTargetChooser` | PlayerId, OutcomeType | TargetPlayerId | AI chooses grievance target |

> ⚠️ `RegisterProcessor` has potential race conditions — can occasionally crash the game.

### RegisterCallEvent(callback, address, parameters)

Hook into any GameCore function by address. Captures up to 4 arguments.

```lua
-- Detect when units are destroyed
function OnPlayerUnitsDestroy(playerUnitsAddress, unitInstanceAddress)
    local unit = UnitManager.GetInstance(unitInstanceAddress)
    print("Unit destroyed at: x=" .. unit:GetX() .. ", y=" .. unit:GetY())
end

RegisterCallEvent(OnPlayerUnitsDestroy, 0x34d4e0, { FIELD_POINTER, FIELD_POINTER })
```

> ⚠️ Finding the right function addresses requires Ghidra + debug symbols (see Contributor's Guide below).

---

## Extended Object Methods

These methods are added to existing game objects. Use `:` for instanced, `.` for static.

### Plot

```lua
pPlot:SetAppeal(15)      -- Set appeal (overwritten by game unless locked)
pPlot:LockAppeal(true)   -- Prevent game from recalculating appeal
pPlot:LockAppeal(false)  -- Unlock
```

### PlayerCities

```lua
local playerCities = Players[playerId]:GetCities()
playerCities:AddGreatWork(greatWorkListIndex)  -- Move great work to a city
```

### PlayerInfluence

```lua
local influence = Players[playerId]:GetInfluence()
influence:SetTokensToGive(5)   -- Set free envoys
influence:SetPoints(100)       -- Set influence points (clamped ≥ 0)
influence:AdjustPoints(-50)    -- Adjust relative
```

### GameDiplomacy

```lua
local diplomacy = Game.GetGameDiplomacy()
diplomacy:ChangeGrievanceScore(player1Id, player2Id, -100)  -- Reduce grievances
```

### PlayerGovernors

```lua
local governors = Players[playerId]:GetGovernors()
governors:PromoteGovernor(governorIndex, promotionIndex)  -- Spend title + promote
governors:NeutralizeGovernor(governorIndex, 5)             -- Neutralize for 5 turns
governors:ChangeNeutralizedTurns(governorIndex, -2)        -- Shorten neutralization
governors:UnassignGovernor(governorIndex, false, true)     -- Unassign from city
```

### GovernorManager (static)

```lua
GovernorManager.GetTurnsToEstablishDelay(playerId, governorHash, true)  -- UI delay
GovernorManager.SetTurnsToEstablishDelay(playerId, governorHash, 3, true)
GovernorManager.ChangeTurnsToEstablishDelay(playerId, governorHash, -1, true)
```

### CityTradeManager (static)

```lua
CityTradeManager.SetHasConstructedTradingPost(city, playerId)  -- Requires integer playerId
-- Note: confirmed via live FireTuner probe — the function signature requires exactly 2 args.
-- Boolean third arg is NOT supported (throws "integer expected").
```

### CultureManager (static)

```lua
-- Create a great work and assign it to a player
local gwIndex = CultureManager.FindOrAddGreatWork(GameInfo.GreatWorks.GREATWORK_MICHELANGELO_1.Index)
CultureManager.SetGreatWorkPlayer(gwIndex, playerId)
Players[playerId]:GetCities():AddGreatWork(gwIndex)
```

### EconomicManager (static)

```lua
-- Global monopoly tourism multiplier
EconomicManager.SetMonopolyTourismMultiplier(2.0)    -- Double it
EconomicManager.ChangeMonopolyTourismMultiplier(0.5)  -- Add 0.5
local mult = EconomicManager.GetMonopolyTourismMultiplier()

-- Per-player
EconomicManager.SetMonopolyTourismMultiplier(playerId, 0)  -- Remove bonus
local tourism = EconomicManager.GetTourismFromMonopolies(playerId)
```

### EmergencyManager (static)

```lua
-- Adjust COMPETITION emergency score
EmergencyManager.ChangePlayerScore(playerId, emergencyHash, 10)

-- Adjust AID_REQUEST / HOSTILE_EMERGENCY score
EmergencyManager.ChangePlayerScore(playerId, otherPlayerId, emergencyHash, -5)
```

### UnitManager (static)

```lua
-- Get unit from memory address (used with RegisterCallEvent)
local unit = UnitManager.GetInstance(unitAddress)

-- Transfer unit ownership
local newUnit = UnitManager.ChangeOwner(unit, newPlayerId, false, false)
```

### NationalParks (static)

```lua
NationalParks.DesignatePark(playerId, plotX, plotY)  -- Create 4-plot park
local parkData = NationalParks.FindPark(plotX, plotY)
NationalParks.RestoreVisualState(parkData)
```

### AIEspionageManager (static)

```lua
local missionIndex = AIEspionageManager.GetMostUsedSpyMission(player)
```

### OutcomeTypes (enum)

```lua
OutcomeTypes.A  -- First congress outcome
OutcomeTypes.B  -- Second congress outcome
```

---

## Configuration

Create `CommunityExtension.ini` at `Base/Binaries/Win64Steam/` in your Civ VI install:

```ini
[Settings]
EnableConsole=1
```

Enables a debug console window — useful for seeing processor calls and error messages.

---

## Reverse Engineering Guide (Summary)

The Contributor's Guide documents how to analyze GameCore using Ghidra with leaked debug symbols:

1. **Get Ghidra** from NSA's GitHub releases
2. **Download debug symbols** via Steam console: `download_depot 289070 947510 2550987199793754278` (requires GS ownership)
3. **Import** `GameCore_XP2_FinalRelease.dll` into Ghidra, run analyzer
4. **Add** the `.map` file (Microsoft Mapfile format) to map all symbols
5. **Run** the `DemangleAll` script in Script Manager

This gives you a fully labelled disassembly of GameCore — every function, every class, every global. This is how WildW discovers the memory offsets and function addresses for hooks.

**Combined with FireTuner** (TCP protocol to inject Lua at runtime), this creates a complete reverse engineering toolkit: Ghidra for static analysis, FireTuner for dynamic testing.

---

## Declaring the Dependency

In your `.modinfo`:

```xml
<Dependencies>
    <Mod id="COMMUNITY_EXTENSION_MOD_ID" title="Community Extension" />
</Dependencies>
```

For soft dependency (features activate only if CE is present):

```lua
-- Check if Community Extension is loaded
if Mem ~= nil then
    -- CE features available
    pPlot:SetAppeal(15)
else
    -- Fallback to standard modding
end
```

---

## Live FireTuner API Verification (2026-04-01)

Findings from live GameCore state 3 probing via FireTuner TCP. These correct/extend the docs above.

### CE Global Types (confirmed in-game)

| Global | Type | Notes |
|--------|------|-------|
| `Mem` | function | Works |
| `ObjMem` | function | Works — `ObjMem(plot, 0x4a, FIELD_SHORT)` returns plot appeal |
| `UnitManager` | table | Static methods — call as `UnitManager.Kill(unit, true)` |
| `CityTradeManager` | table | Only one method: `SetHasConstructedTradingPost(city, playerID)` |
| `CultureManager` | table | `FindOrAddGreatWork`, `SetGreatWorkPlayer` |
| `EconomicManager` | table | Monopoly tourism only: `Get/Set/Change/GetTourism` |
| `RegisterProcessor` | function | Works but floods output — use sparingly |
| `GovernorManager` | table | Not separately tested |
| `NationalParks` | table | Not separately tested |

### UnitManager.Kill() — confirmed working

```lua
-- Kill a unit in GameCore state 3 via FireTuner
UnitManager.Kill(unit, true)  -- true = remove from map immediately

-- Unit goes to (-9999, -9999) after kill — still briefly in unit list
-- but GetX()/GetY() return -9999. Treated as dead for all gameplay purposes.
-- Garbage-collected from the list on the next turn boundary.
```

Verified: killed a live barb unit mid-game, unit count dropped from 35 → 34 on-map.

### GameInfo iteration for districts

```lua
-- HasDistrict() requires integer Index, NOT the string type
-- Wrong:  cd:HasDistrict("DISTRICT_CAMPUS")   -- returns true for everything
-- Right:
for row in GameInfo.Districts() do
    if cd:HasDistrict(row.Index) then
        -- district present
    end
end
```

### State 3 API limitations

These are **not available** in GameCore state 3 (throw "Not Implemented"):
- `BuildQueue:GetTurnsLeft()` — UI-only
- `BuildQueue:GetPercentComplete()` — nil in state 3
- `city:GetGrowth():GetFoodSurplus()` — throws in state 3

`BuildQueue:CurrentlyBuilding()` **returns a string** (e.g. `"UNIT_SETTLER"`), not an integer type ID.

### District popularity at turn 149 (6 civs, 25 cities)

Observed district build order by frequency — useful for AI priority modelling:

| District | Count | % of cities |
|----------|-------|-------------|
| Campus | 15 | 60% |
| Theater Square | 10 | 40% |
| Holy Site | 7 | 28% |
| Encampment | 4 | 16% |
| Government Plaza | 3 | 12% |
| Industrial Zone | 2 | 8% |
| Dam | 2 | 8% |
| Harbor | 2 | 8% |
| Aqueduct | 2 | 8% |
| Entertainment Complex | 1 | 4% |

**Implication for CSC:** Custom quarters compete for the same district slot budget as Campus and Theater. Players will feel this trade-off most against science/culture. A quarter placed instead of a Campus is a meaningful sacrifice — lean into that in design.

## Gotchas

- **RegisterProcessor race conditions** — can crash the game occasionally. Use sparingly in production.
- **Memory offsets are version-specific** — if Firaxis patches GameCore (rare at this point), offsets shift.
- **RegisterCallEvent captures max 4 arguments** — functions with more parameters need creative workarounds.
- **Setting memory values may not update UI** — e.g., `ChangeGrievanceScore` doesn't immediately refresh the diplomacy screen.
- **Database extensions planned but not yet supported** — can't add new tables or columns through CE yet.
- **DLL must be in `Win64Steam` (or `Win64EOS`)** — placement matters.
- **No macOS/Linux support** — this is Windows-only (DLL injection).
