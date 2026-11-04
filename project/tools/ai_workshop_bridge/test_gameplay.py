"""Run the actual Workshop gameplay script against a small Lua 5.1 game fixture.

Supply --dependencies (or CSC_LUA51_DEPENDENCIES) for an existing Lupa install.
The fixture records native publication calls; it does not emulate native scores.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "gameplay.lua"
FIXTURE = r"""
Delta=256; Turn=1; Log={}; Calls={}; Enabled=true; Props={}
FailBegin=false; FailEntry=false
function print(...)
    local parts={};for n=1,select('#',...) do parts[n]=tostring(select(n,...)) end
    Log[#Log+1]=table.concat(parts,'\t')
end
local function call(name,...)
    local row={name};for n=1,select('#',...) do row[#row+1]=select(n,...) end
    Calls[#Calls+1]=row
end
function CSCBridgeBegin(v,w,h,d)
    call('begin',v,w,h,d);Enabled=false;return FailBegin and 0 or 1
end
function CSCBridgeAllow(pid)call('allow',pid);return 1 end
function CSCBridgeEntry(pid,cid,d,p,delta)
    call('entry',pid,cid,d,p,delta);return FailEntry and 0 or 1
end
function CSCBridgeCommit()call('commit');Enabled=true;return 1 end
function CSCBridgeDisable()call('disable');Enabled=false;return 1 end
function CSCBridgeStatus()return '{"fixture":true}' end
local function event()
    local listeners={}
    return {Add=function(fn)listeners[#listeners+1]=fn end,
            Fire=function(...)for _,fn in ipairs(listeners)do fn(...)end end}
end
GameEvents={OnGameTurnStarted=event()}
Events={PlayerTurnActivated=event()}
Game={GetProperty=function(_,key)return Props[key]end,
      SetProperty=function(_,key,value)Props[key]=value end,
      GetCurrentGameTurn=function()return Turn end}
GameConfiguration={GetValue=function(key)
    assert(key=='CSC_BRIDGE_SMOKE_DELTA');return Delta
end}
local districts={{Index=0,DistrictType='DISTRICT_CITY_CENTER'},
                 {Index=3,DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},
                 {Index=7,DistrictType='DISTRICT_TEST_OTHER'}}
local info={}
for _,row in ipairs(districts)do info[row.DistrictType]=row end
GameInfo={Districts=setmetatable(info,{__call=function()
    local n=0;return function()n=n+1;return districts[n]end
end})}
local function city(id,x,y,has)
    return {GetID=function()return id end,GetX=function()return x end,
        GetY=function()return y end,GetDistricts=function()
            return {HasDistrict=function(_,index)assert(index==3);return has end}
        end}
end
CityA=city(65536,5,5,false)
CityB=city(131072,20,5,true)
HumanCity=city(0,40,5,false)
local function player(human,alive,major,cities)
    return {human=human,IsHuman=function(self)return self.human end,
        IsAlive=function()return alive end,IsMajor=function()return major end,
        GetCities=function()return {Members=function()
            local n=0;return function()n=n+1;if cities[n]then return n,cities[n]end end
        end}end}
end
Players={[0]=player(true,true,true,{HumanCity}),
         [1]=player(false,true,true,{CityA}),
         [2]=player(false,true,true,{CityB}),
         [3]=player(false,true,false,{}),
         [4]=player(false,false,true,{})}
local plots={}
local function plot(x,y,index,owner,purchaseCity)
    plots[x..':'..y]={purchaseCity=purchaseCity,
        GetOwner=function()return owner end,GetIndex=function()return index end}
end
plot(5,5,101,1,CityA)       -- The sole admissible pair.
plot(6,5,102,1,CityB)       -- Owned by player1 but belongs to another city.
plot(5,6,103,-1,nil)        -- Unowned land is outside this shipping smoke scope.
plot(4,5,104,0,HumanCity)   -- Foreign ownership.
plot(5,4,105,1,nil)         -- Owned with no city assignment.
plot(20,5,201,2,CityB)      -- This city already has the Quarter.
plot(40,5,301,0,HumanCity)  -- Original human must never enter the policy.
Map={GetGridSize=function()return 64,40 end,
     GetPlotXYWithRangeCheck=function(x,y,dx,dy,r)
        if math.max(math.abs(dx),math.abs(dy),math.abs(dx+dy))>r then return nil end
        return plots[(x+dx)..':'..(y+dy)]
     end}
Cities={GetPlotPurchaseCity=function(p)return p.purchaseCity end}
"""


class GameplayTest(unittest.TestCase):
    def fixture(self, before: str = ""):
        from lupa.lua51 import LuaRuntime

        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute(FIXTURE)
        if before:
            lua.execute(before)
        lua.execute(SOURCE.read_text(encoding="utf-8-sig"))
        return lua

    @staticmethod
    def calls(lua):
        rows = lua.globals().Calls
        return [[row[n] for n in range(1, len(row) + 1)]
                for row in (rows[i] for i in range(1, len(rows) + 1))]

    @staticmethod
    def logs(lua):
        rows = lua.globals().Log
        return [rows[n] for n in range(1, len(rows) + 1)]

    def test_publication_order_and_only_owned_assigned_unbuilt_city(self):
        lua = self.fixture()
        self.assertEqual(self.calls(lua), [
            ["begin", 1, 64, 40, 8], ["allow", 1],
            ["entry", 1, 65536, 3, 101, 256], ["allow", 2], ["commit"],
        ])
        self.assertTrue(lua.globals().Enabled)
        self.assertIn("CSC_WORKSHOP_PUBLICATION 1 1 1", self.logs(lua))

    def test_default_observation_disables_existing_native_policy(self):
        lua = self.fixture("Delta=nil")
        self.assertFalse(lua.globals().Enabled)
        self.assertEqual(self.calls(lua), [["disable"]])
        self.assertTrue(any("observe" in line for line in self.logs(lua)))

    def test_switch_to_observation_disables_previously_published_policy(self):
        lua = self.fixture()
        lua.execute("Delta=0;GameEvents.OnGameTurnStarted.Fire()")
        self.assertFalse(lua.globals().Enabled)
        self.assertEqual(self.calls(lua)[-1], ["disable"])
        self.assertEqual(sum(row[0] == "commit" for row in self.calls(lua)), 1)

    def test_original_human_excluded_after_runtime_autoplay_role_changes(self):
        lua = self.fixture()
        lua.execute("Players[0].human=false;Players[1].human=true;Turn=2;GameEvents.OnGameTurnStarted.Fire()")
        entries = [row for row in self.calls(lua) if row[0] == "entry"]
        self.assertEqual(entries, [["entry", 1, 65536, 3, 101, 256]] * 2)
        self.assertEqual(lua.globals().Props["CSC_BRIDGE_ORIGINAL_HUMAN_0"], 1)
        self.assertEqual(lua.globals().Props["CSC_BRIDGE_ORIGINAL_HUMAN_1"], 0)

    def test_saved_original_human_identity_overrides_current_runtime_role(self):
        lua = self.fixture("Players[0].human=false;Props.CSC_BRIDGE_ORIGINAL_HUMAN_0=1")
        allowed = [row[1] for row in self.calls(lua) if row[0] == "allow"]
        self.assertEqual(allowed, [1, 2])

    def test_real_event_handler_refreshes_with_monotonic_versions(self):
        lua = self.fixture()
        lua.execute("Turn=2;GameEvents.OnGameTurnStarted.Fire();Turn=3;GameEvents.OnGameTurnStarted.Fire()")
        begins = [row for row in self.calls(lua) if row[0] == "begin"]
        self.assertEqual([row[1] for row in begins], [1, 2, 3])
        self.assertEqual(sum(row[0] == "commit" for row in self.calls(lua)), 3)
        self.assertIn("CSC_WORKSHOP_PUBLICATION 3 3 1", self.logs(lua))

    def test_absent_native_api_fails_closed_and_logs(self):
        lua = self.fixture("CSCBridgeBegin=nil")
        self.assertFalse(lua.globals().Enabled)
        self.assertEqual(self.calls(lua), [["disable"]])
        self.assertTrue(any("FAILURE" in line and "Native Workshop bridge was not loaded" in line
                            for line in self.logs(lua)))

    def test_entire_native_api_absent_logs_without_publication(self):
        lua = self.fixture("CSCBridgeBegin=nil;CSCBridgeDisable=nil;CSCBridgeStatus=nil")
        self.assertEqual(self.calls(lua), [])
        self.assertTrue(any("FAILURE" in line for line in self.logs(lua)))

    def test_invalid_delta_disables_and_never_publishes(self):
        for delta in (-256, 1, 1048576):
            with self.subTest(delta=delta):
                lua = self.fixture(f"Delta={delta}")
                self.assertEqual(self.calls(lua), [["disable"]])
                self.assertFalse(lua.globals().Enabled)
                self.assertTrue(any("FAILURE" in line for line in self.logs(lua)))

    def test_native_begin_rejection_stops_before_allow_or_commit(self):
        lua = self.fixture("FailBegin=true")
        self.assertEqual(self.calls(lua), [["begin", 1, 64, 40, 8], ["disable"]])
        self.assertFalse(lua.globals().Enabled)

    def test_partial_entry_failure_disables_without_commit(self):
        lua = self.fixture("FailEntry=true")
        self.assertEqual([row[0] for row in self.calls(lua)], ["begin", "allow", "entry", "disable"])
        self.assertFalse(lua.globals().Enabled)

    def test_missing_quarter_disables_existing_policy(self):
        lua = self.fixture("GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER=nil")
        self.assertEqual(self.calls(lua), [["disable"]])
        self.assertFalse(lua.globals().Enabled)
        self.assertTrue(any("no-CSC" in line for line in self.logs(lua)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path,
                        default=os.environ.get("CSC_LUA51_DEPENDENCIES"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.dependencies:
        sys.path.insert(0, str(args.dependencies.resolve()))
    try:
        from lupa.lua51 import LuaRuntime
    except ImportError as error:
        parser.error(f"An existing Lupa Lua5.1 install is required: {error}")
    runtime = LuaRuntime()
    version = runtime.eval("_VERSION")
    if version != "Lua 5.1":
        parser.error(f"Expected Lua 5.1, received {version!r}")
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(GameplayTest)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_bytes((json.dumps({
            "ok": result.wasSuccessful(), "tests": result.testsRun,
            "failures": len(result.failures), "errors": len(result.errors),
            "lua": version, "source": str(SOURCE),
            "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "scope": "Actual gameplay.lua; synthetic game/native-publication fixture; no native execution",
        }, indent=2) + "\n").encode("utf-8"))
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
