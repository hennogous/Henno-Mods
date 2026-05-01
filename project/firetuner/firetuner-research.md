# FireTuner Research

## Overview
FireTuner2 is Firaxis's runtime debug console for Civ 6. It connects to a running game instance over TCP and can execute Lua commands, inspect game state, place buildings/districts, grant techs, manipulate cities, etc.

## Architecture

### Connection
- **Protocol:** TCP socket (Firaxis "Nexus" protocol)
- **Default endpoint:** `127.0.0.1:4318`
- **Buffer size:** 2MB (2,097,152 bytes)
- **Implementation:** `Firaxis.Net.SocketConnection` (base) → `FireTuner2.Connection` (app-level)

### Enabling
- `AppOptions.txt` → `[Debug]` section → `EnableTuner 1` (already enabled on Shadow)
- Location: `%LOCALAPPDATA%\Firaxis Games\Sid Meier's Civilization VI\AppOptions.txt`
- Game must be running for FireTuner to connect

### Lua States
The game exposes multiple Lua contexts (states):
- `GameCore_Tuner` — main gameplay context (modifiers, cities, players, units)
- `TunerCityPanel` — city-specific operations (place buildings/districts)
- `TunerMapPanel` — map operations
- `TunerUnitPanel` — unit operations
- Other panel-specific states

FireTuner can switch between states to execute Lua in different contexts.

### Message Protocol (from IL analysis)
- Messages appear to use a **length-prefixed binary framing**
- Request format: `[4-byte length prefix][sender ID (int32)][UTF-8 string payload]`
- Response: parsed into `RequestResponse` objects, routed to listeners by sender ID
- The `OnReceivedData` method reads a 4-byte length (`ReadUInt32`), then reads that many chars
- Multiple messages can arrive in a single TCP receive

### Panel Files (.ltp)
- XML format defining UI panels with embedded Lua code
- Located in `<game>\Debug\*.ltp`
- `DefaultPanels.xml` lists which panels load by default
- Each panel has:
  - `CompatibleStates` — which Lua states it works with
  - `LoadStates` — which Lua states to load when panel is active
  - `Actions` — buttons that execute Lua snippets
  - `StringControls` — text fields with Lua get/set functions
  - `ValueControls`, `BooleanControls`, `TableViews`, etc.

### Tuner Lua Scripts
- Located in `<game>\Base\Assets\UI\Tuner\*.lua`
- Loaded into the game when FireTuner connects
- Provide helper functions for panels (e.g., `GetSelectedCity()`, `GetSelectedPlayer()`)
- Can call any gameplay API: `Players[]`, `Cities`, `Map`, `GameInfo`, `GameEffects`, etc.

## Key Gameplay APIs Available via FireTuner

### City operations
- `pCity:ChangePopulation(n)` — add/remove population
- `pBuildQueue:CreateIncompleteDistrict(type, plotIndex, percentComplete)` — place district
- `pBuildQueue:CreateIncompleteBuilding(type, plotIndex, percentComplete)` — place building
- `CityManager.DestroyDistrict(district)` — remove district

### Player operations
- `playerTechs:SetResearchProgress(techIndex, cost)` — grant tech
- `playerTechs:SetTech(id, bool)` — set tech status
- All tech/civic granting

### Game state inspection
- `GameEffects.GetModifierDefinition(modifierId)` — inspect modifier
- `GameEffects.GetModifierOwner(modifierId)` — get modifier owner
- `GameEffects.GetObjectString(object)` — get string representation
- Full `GameInfo.*` table access
- All requirement/modifier chain inspection

### Map operations
- `Map.GetPlot(x, y)` — get plot
- Plot property get/set
- Feature/resource/improvement manipulation

## Automation Ambition

### Phase 1: TCP Client
Write a Python/Node client that speaks the Nexus protocol:
1. Connect to `127.0.0.1:4318`
2. Send Lua commands as framed messages
3. Parse responses
4. Need to reverse-engineer exact framing from packet capture or deeper IL analysis

### Phase 2: Test Harness
Wrap the client as a CLI tool:
- `firetuner exec "Lua code"` — execute and return result
- `firetuner place-district DISTRICT_CSC_BAKERS 0 10 10` — place CSC district
- `firetuner inspect-modifier MOD_CSC_BAKERS_ADJACENCY` — check modifier state

### Phase 3: MCP Server (stretch)
Expose the client as an MCP tool so Bill can interact with a running game directly.

## Protocol (Confirmed via ILSpy token resolution)

### Request Wire Format
```
[uint32 LE] content_length    // bytes after header = utf8_len(lua_code) + 1
[uint32 LE] sender_id         // listener index for routing responses
[utf-8]     lua_code           // BinaryWriter.Write(Char) per char → UTF-8 encoded
[0x00]      null_terminator    // BinaryWriter.Write(Char) with value 0
```

### Response Wire Format (OnReceivedData framing)
```
[uint32 LE] message_length    // BitConverter.ToUInt32 — byte count of body
[body]:
  [uint32 LE] sender_id      // BinaryReader.ReadUInt32
  [chars]     response        // BinaryReader.ReadChars(remaining) — null-separated
```

### Resolved Tokens
- 0x0A00022A = BinaryWriter.Write(UInt32) — header fields
- 0x0A00022B = BinaryWriter.Write(Char) — string chars + null term
- 0x0A00022C = MemoryStream.GetBuffer()
- 0x0A00022D = Stream.get_Position
- 0x0A00022E = Stream.set_Position (for length correction)
- 0x0A000212 = BitConverter.ToUInt32 (receive framing)
- 0x0A000215 = BinaryReader.ReadUInt32 (sender_id in response)
- 0x0A000216 = BinaryReader.ReadChars (response content)

## Tools Built
- `firetuner_client.py` — Python TCP client speaking the protocol, with REPL mode
- `firetuner_csc_test.py` — Example CSC mod test harness

## Next Steps
1. **Test with live game** — connect client, verify protocol works
2. **Adjust for any quirks** — BinaryWriter.Write(Char) may have edge cases with UTF-8 length prefix bytes
3. **Expand test harness** — add placement tests, adjacency verification, modifier chain inspection

## Files on Shadow
- FireTuner2.exe: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\FireTuner\FireTuner2.exe`
- Tuner panels: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\Debug\*.ltp`
- Tuner Lua: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\Base\Assets\UI\Tuner\*.lua`
- Plugin DLL: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\Debug\Civ6TunerPlugin.dll`
- AppOptions: `C:\Users\Shadow\AppData\Local\Firaxis Games\Sid Meier's Civilization VI\AppOptions.txt`
