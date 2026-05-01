# Civ 6 Autonomous Game Launch — Research Notes
*2026-04-01, Bill (Opus session, updated 11:30) — CE crash investigation added 2026-04-02*

## What Works ✓

### Launching a new game via FireTuner
From the main menu (full menu, NOT the "Play Now" splash):
```lua
-- Clear PlayNowSave (empty string = new game with defaults)
Options.SetAppOption("Debug", "PlayNowSave", "")
-- Fire the state transition
LuaEvents.Raise_State_Transition("MainMenu")
```
This triggers the full game load sequence: JoiningRoom → mod loading → map generation → in-game.

### Mods load automatically
CE and all other enabled mods load based on the `Mods.sqlite` database in:
`C:\Users\Shadow\AppData\Local\Firaxis Games\Sid Meier's Civilization VI\Mods.sqlite`

Key tables:
- `ModGroups` — named groups (Default, "Auto: Last Used Mods")
- `ModGroupItems` — (GroupId, ModRowId, Disabled) — `Disabled=0` means enabled
- The `Selected=1` group in `ModGroups` is used for new games
- CE is ModRowId=1431 (ModId: `3351473b-0746-417a-a618-2b66a04d8f3d`)

### CE fully functional in-game
All CE globals available via FireTuner state 3 (GameCore):
- `Mem` / `ObjMem` — memory read/write
- `RegisterProcessor` — AI decision interception
- `CityTradeManager`, `CultureManager`, `UnitManager`, `GovernorManager`, `NationalParks`, `EconomicManager`
- `FIELD_SHORT`, `FIELD_INT`, etc. field type constants

### AutoplayManager
Available in state 3 (GameCore context only, NOT state 0):
- `SetActive(bool)` / `IsActive()` — start/stop autoplay
- `SetTurns(n)` / `GetTurns()` — set turn count
- `SetObserveAsPlayer(id)` / `GetObserveAsPlayer()`
- `SetReturnAsPlayer(id)` / `GetReturnAsPlayer()`

### Automation API
Available in state 3:
- `SetActive(bool)` / `IsActive()` / `IsPaused()` / `Pause()`
- `GenerateSaveName()` / `GetLastGeneratedSaveName()`
- `SendTestComplete()` — signals test harness
- `Log()`, `LogDateAndTime()`, `LogDivider()`
- `SetInputHandler()` / `RemoveInputHandler()` — input interception

## Blockers / Issues

### 1. "Begin Game" leader intro screen
After `Raise_State_Transition("MainMenu")`, the game loads to the leader intro screen with a "Begin Game" button. FireTuner port drops during this transition and only comes back after the button is clicked. **Requires human click** currently.

**Possible fixes to investigate:**
- AppOptions setting to skip the intro screen
- `SuppressInfoPopups 1` in AppOptions (currently 0)
- Adding `PlayIntroVideo 0` style setting for leader screen
- Pre-game Lua hook that auto-dismisses the screen

### 2. Input injection doesn't work on Shadow
The Shadow cloud PC renders through a streaming protocol. All standard Windows input injection methods fail:
- `pyautogui` (SendInput) — ignored
- `ctypes.windll.user32.mouse_event` — ignored
- `PostMessage`/`SendMessage` WM_LBUTTONDOWN — ignored
- `keybd_event` with hardware scan codes — ignored
- All return success (1) but game doesn't process them

The game only receives input from Shadow's virtual input device.

### 3. EnableMod API doesn't persist
`Modding.EnableMod(handle)` returns nil and `IsModEnabled` stays false. The mod enable state is cached at game startup from Mods.sqlite. To change enabled mods, must edit the database and restart the game.

### 4. RegisterProcessor floods output
The DistrictTargetChooser processor fires for ALL players on EVERY turn during autoplay, creating massive output. This can overwhelm the FireTuner TCP connection and cause disconnection. Use sparingly or only register temporarily.

### 5. Eureka/notification popups block autoplay
UI popup notifications (Eureka, natural wonder discovery, etc.) pause autoplay and require clicking "Continue". Since we can't inject mouse clicks, these block autonomous play.

**Fix**: Set `SuppressInfoPopups 1` in AppOptions before launching.

### 6. Save game API
`Network.SaveGame()` is not available in GameCore (state 3). Need to use UI context (state 0) or find the right API. The `Automation.GenerateSaveName()` exists but the actual save call needs investigation.

## Architecture

### FireTuner States
| State | Context | Available APIs |
|-------|---------|---------------|
| 0 | UI/Frontend | LuaEvents, Network, Options, Modding |
| 3 | GameCore | Game, Players, Map, AutoplayManager, Automation, CE (Mem/ObjMem) |
| 4 | WorldInput | (not tested) |
| 5 | StrategicView | (not tested) |

### Game Launch Sequence
1. Start Civ 6 via `Start-Process "steam://rungameid/289070"`
2. Wait for FireTuner port 4318 to open
3. Verify full main menu (not "Play Now" splash) — `Network.IsInSession()` should be false
4. Clear PlayNowSave and fire state transition
5. Wait ~15-20s for game to load (mods, map gen)
6. **BLOCKER**: Human clicks "Begin Game"
7. FireTuner reconnects, game is live on turn 1
8. Use AutoplayManager in state 3 for autonomous turns

### "Play Now" splash vs full menu
- **home-screen-1** (Play Now splash): minimal UI, clicking Play Now loops back. This is what Sonnet left the game on.
- **home-screen-2** (full menu): all buttons visible. This is what a fresh game launch shows.
- If the game is on the splash, `HostGame(-1)` briefly enters JoiningRoom but falls back. The splash state is a dead end for automation.

## Files Created
- `check_modding_api.py` — explore Modding API from main menu
- `explore_ui_manager.py` — LuaEvents discovery (found the transition events)
- `try_play_now.py` — **THE LAUNCHER** (Options + Raise_State_Transition)
- `check_mods_db.py` / `check_mods_db2.py` — Mods.sqlite inspection
- `autoplay_and_explore.py` — autoplay + CE exploration
- `check_live_game.py` — game state + CE + AutoplayManager probe
- `take_screenshot.py` — PIL-based compressed screenshot utility

## Key Discoveries (afternoon session)

### Autoplay.ltp panel revealed SetDisableAssertsForAutoplay
`AutoplayManager.SetDisableAssertsForAutoplay(true)` — CRITICAL for stable autoplay.
Without this, asserts fire during autoplay and crash the game (~turn 15-20).

### ToolTipLoader_MAB.lua is the real TCP flood source
Ruivo's Modular Adjacency Bonus tooltip loader (`ToolTipLoader_MAB.lua:12`) throws a runtime error
on EVERY FRAME via `OnDirtyCheck`. This is not CE's fault — it's a broken workshop mod.
This error floods the FireTuner TCP connection, making recv loops hang indefinitely.
**Fix: filter `Runtime Error`, `stack traceback`, `ToolTipLoader` in recv.**

### FireTuner is single-client
Only one TCP connection at a time. If FireTuner2 GUI is running, our script can't connect.
Kill `FireTuner2` before launching. After ungraceful disconnect, the game may not reopen
the listener until restart.

### LoadScreen.lua auto-click timing
`if (true) then OnActivateButtonClicked()` — fires immediately, causes `Failed to load GameCore DLL`
because CE DLL isn't fully initialized yet. Need a ~10s delay using `ContextPtr:SetUpdate()` timer.
Timer patch syntax: one-liner `local g_autoTimer = 0; ContextPtr:SetUpdate(function(fDelta)...end)`

### Save game API (from Automation_DailySmokeTest.lua)
```lua
local sg = {}
sg.Name = "MySave"
sg.Location = SaveLocations.LOCAL_STORAGE
sg.Type = SaveTypes.SINGLE_PLAYER
sg.IsAutosave = false; sg.IsQuicksave = false
Network.SaveGame(sg)  -- state 0 (UI context)
```
Save is async — wait for `Events.SaveComplete` callback.

### Exit game
`UI.ExitGame()` works from state 0. `Events.UserConfirmedClose()` is nil.

### AppOptions changes made
- `SuppressInfoPopups 1` (prevents Eureka/tech popups blocking autoplay)
- `EnableAsserts 0` (belt-and-suspenders with SetDisableAssertsForAutoplay)

## Status: Working but needs polish
- Launch → menu → transition → game load: **SOLID**
- Begin Game auto-click: **Works with 10s delay timer, but DLL error with instant click**
- Autoplay 20 turns with CE: **WORKS** (multiple confirmed runs to turn 21)
- Reconnect after autoplay: **Works but ft_cmd recv hangs on MAB error flood**
- Save: **API identified, tested partially**
- Exit: **`UI.ExitGame()` works**

## Next Steps
1. Clean up LoadScreen.lua patch (proper timer implementation)
2. Fix recv to hard-cap at 3s regardless of incoming data
3. Full end-to-end test with save + exit
4. Consider disabling ToolTipLoader_MAB workshop mod for clean autoplay
5. Package as reusable tool

---

## Session 2 Learnings — 2026-04-01 (evening)

### FireTuner is single-client, confirmed again
If FireTuner2 GUI is open, our script gets the port. FireTuner2 must be fully closed before
connecting. Even brief competing connections kill the listener.

### Graceful disconnect fix
Root cause of listener death: `socket.shutdown(SHUT_RDWR)` sends RST. Game's listener doesn't
recover from RST. Fix: `socket.shutdown(SHUT_WR)` only (FIN), then 500ms wait, then close.
Updated in `firetuner_client.py`. See `FIRETUNER-PROTOCOL.md` for full protocol RE details.

### Protocol fully reverse-engineered
ILSpy decompile of FireTuner2.exe via dnfile + manual IL disassembly. Key findings:
- `DefaultRequestHandler` dispatches: `"L"` = load lua states, `"O"` = console output, `"Closing"` = game-initiated disconnect → client calls `SocketConnection.CloseConnection()`
- `btnForceDisconnect_Click` = 2 IL instructions: `GetInstance()` + `CloseConnection()`. No packet sent.
- Game is the TCP *server*. It sends `"Closing"` to tell FireTuner2 to disconnect gracefully.
- Full command set documented in `FIRETUNER-PROTOCOL.md`

### state 3 print() is the only reliable output mechanism
`return` in state 3 (GameCore) is silently dropped — response arrives empty.
Must use `print()` for all output. Output arrives on sender_id `0xFFFFFFFF`.
`return` works in state 0 (UI context) for some globals.

### SetTurns() is RELATIVE — confirmed 2026-04-01
`AutoplayManager.SetTurns(N)` runs exactly N turns from the current turn, then stops.
`SetTurns(10)` at turn 1 → stops at turn 11. `SetTurns(20)` at turn 11 → stops at turn 31.
Both confirmed exact and `stopped_cleanly=True` in overnight test.

### Correct autoplay sequence (confirmed working)
```python
# 1. Fire as fire-and-forget (listener drops, that's fine)
fire_nowait(
    "Automation.SetActive(false); "          # Clear IsActive() guard
    "LuaEvents.AutoPlayEnd.RemoveAll(); "    # Clean up any old handlers  
    "LuaEvents.AutoPlayEnd.Add(function() print('AUTOPLAY_END:t='..Game.GetCurrentGameTurn()) end); "
    "AutoplayManager.SetDisableAssertsForAutoplay(true); "
    "AutoplayManager.SetTurns(N); "          # Relative: runs N turns from now
    "AutoplayManager.SetReturnAsPlayer(0); " # Return control to player 0
    "AutoplayManager.SetObserveAsPlayer(-1); "
    "AutoplayManager.SetActive(true)"
)
# 2. Wait 8s for listener to recover
# 3. Poll with fresh connections, check IsActive() == false or AUTOPLAY_END event
```

### Automation.IsActive() guard blocks SetTurns/SetActive
From Autoplay.ltp panel source: both `AutoplayManager.SetTurns()` and `AutoplayManager.SetActive()`
are wrapped in `if (not Automation.IsActive())`. If the game was launched via our LoadScreen.lua
auto-start patch, `Automation.IsActive()` may return true — silently blocking both calls.
Result: turns=10 gets ignored, SetActive is a no-op, autoplay runs forever.
**Fix:** call `Automation.SetActive(false)` BEFORE setting turns and starting autoplay.

### CE crash on this machine (unresolved)
CE crashes both DX11 and DX12 (`0xc0000005 ACCESS_VIOLATION`) after AppOptions changes.
Possibly related to `EnableAsserts 0` or LoadScreen.lua patch residue.
Decision: decouple automation from CE. Automation should work without CE enabled.
CE crash should be reported to Wild-W with dump files in `Base\Binaries\Win64Steam\`.

### build queue query bug
`BuildQueue:CurrentlyBuilding()` returns an integer type ID, not a string.
Concatenating it directly into a print() call crashes silently (no output).
Fix: look up in `GameInfo.Units`, `GameInfo.Buildings`, `GameInfo.Districts` tables.
Fixed in `check_cities.py` but not yet merged back into `game_state.py`.

### City count visibility issue
`game_state.py` city loop silently fails when the build queue Lua crashes mid-loop.
Result: city count appears as 0 when there are actually multiple cities.
Fix: wrap each city's build queue lookup in pcall, or fix the type ID lookup.

### PlayerConfigurations API
`PlayerConfigurations[playerID]:GetCivilizationTypeID()` → look up in `GameInfo.Civilizations`
`PlayerConfigurations[playerID]:GetLeaderTypeID()` → look up in `GameInfo.Leaders`
Confirmed working in state 3.

---

## CE Crash Investigation — 2026-04-02

### CE Architecture
CE works by **replacing the GameCore DLL entirely** via Config.sql:
```sql
UPDATE GameCores SET PackageId='...', DllPrefix='GameCore_XP2_CE'
WHERE GameCore='Expansion2';
```
DLL lives at: `steamapps/workshop/content/289070/3277976174/Binaries/Win64/GameCore_XP2_CE_FinalRelease.dll`
This is a heavier load than normal mods — it swaps the entire game core DLL.

CE is currently **disabled** in Mods.sqlite (Disabled=1 in all groups). ModRowId=1431.

### Crash Dump Analysis
Two dumps in `Base\Binaries\Win64Steam\`:
- `CivilizationVI_DX12.exe.dmp` — 2026-04-01 22:25 (615KB)
- `CivilizationVI.exe.dmp` — 2026-04-01 16:00 (52KB)

Exception code in DX12 dump: `0x0000000a` (EXCEPTION_IN_PAGE_ERROR, not 0xc0000005 as noted earlier).
Module names corrupted in dump (minimal dump format, limited data). CE DLL name not visible.

### Hypothesis: `EnableAsserts 0` is killing CE
The crash appeared after `EnableAsserts 0` was added to AppOptions. CE's replacement DLL likely has
assert-guarded code paths that prevent null pointer dereferences during load. With asserts disabled,
those guard rails vanish → ACCESS_VIOLATION / in-page error.

`EnableAsserts 0` was added as belt-and-suspenders for autoplay stability, but the actual fix for
asserts during autoplay is `AutoplayManager.SetDisableAssertsForAutoplay(true)` called in Lua.
The AppOptions flag may be redundant and harmful.

### Fix Options (ordered by effort)
1. **Remove `EnableAsserts 0`** from AppOptions.txt — restore to `EnableAsserts 1` (default).
   Cost: one line change. If CE loads, problem solved. Autoplay remains stable via SetDisableAssertsForAutoplay.
2. **Bump LoadScreen.lua timer to 20-22s** — CE loads a whole replacement DLL, needs more headroom.
   OnLoadGameViewStateDone fires when UI is ready, but DLL may need extra time to hook in.
3. **Adaptive timer based on CE state** — detect CE enabled in Mods.sqlite before launch,
   patch LoadScreen.lua with 20s timer; use 15s when CE is off. Cleanest long-term.

### Next step
Try option 1 first: restore `EnableAsserts 1`, launch with CE enabled, observe.

---

## run_csc_demo.py — Full End-to-End Script (2026-04-02)

### What it does
Single script: kill → Steam launch → new game → 50-turn autoplay → snapshot.
Location: `csc/firetuner/run_csc_demo.py`
Output tee'd to `csc/firetuner/demo_run.log` (shared-read safe while running).

### Confirmed working
- CSC + 50 turns + full snapshot in one run (~90s total)
- Philadelphia building `DISTRICT_CSC_BAKERS_QUARTER` at turn 51 — CSC alive ✓
- No CE, no LoadScreen.lua issues, no crashes

### Key fixes vs earlier scripts

**1. Reuse connection across FE check + transition (don't reconnect)**
FE check and `Raise_State_Transition` must use the SAME `FTSession` instance.
Closing the FE connection and immediately opening a new one for the transition
causes `ConnectionResetError [WinError 10054]` — the listener isn't ready for
a new client that fast. Reuse the live session instead.

**2. Poll for turn >= 1 before firing autoplay**
Port comes back during the load screen (before the 15s `BeginGame` timer fires).
`ft.turn()` returns -1 in this window. Polling with 1.5s sleep until `t >= 1`
waits for the actual game start. Use up to 40 retries (~60s headroom).

**3. Tee stdout to log file**
Background `exec` sessions swallow stdout if the encoding doesn't match PowerShell's
codepage (cp1252). Fix: open a UTF-8 log file and tee all prints there.
Then tail the log with `[System.IO.File]::Open(... FileShare.ReadWrite)` while running.

**4. Skip `→` arrow in print statements**
`→` (U+2192) is cp1252-unencodable and crashes on PowerShell stdout even with a tee.
Use ASCII `->` in f-strings.
