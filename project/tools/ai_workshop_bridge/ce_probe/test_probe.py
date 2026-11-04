"""Lua 5.1 mock checks; they do not validate native pointer lifetime or timing."""

from pathlib import Path
import unittest

try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None


FIXTURE = r"""
logs, memCalls, objCalls, callbacks = {}, 0, 0, {}
FIELD_BYTE=0; FIELD_SHORT=1; FIELD_UNSIGNED_SHORT=2; FIELD_INT=3; FIELD_UNSIGNED_INT=4
FIELD_UNSIGNED_LONG_LONG=6; FIELD_POINTER=12
CSC_CE_PROBE_TARGET={sha256='fixture-only',timestamp=1719431003,image_size=12976128,
 fingerprints={{name='fixture',rva=0x63d080,bytes={1,2,3}}}}
function include(_) end
function print(line) logs[#logs+1]=line end
local globals={ [0]=0x5a4d,[0x3c]=0x80,[0x80]=0x4550,[0x84]=0x8664,
 [0x88]=1719431003,[0x98]=0x20b,[0xd0]=12976128,
 [0x63d080]=1,[0x63d081]=2,[0x63d082]=3,[0xb8aa68]=0x100000 }
fixtureGlobals=globals
local objects={
 [0x100240]=0x200000,[0x200020]=0x300000,[0x300008]=0x400000,
 [0x400650]=0x500000,[0x500000]=0x400000,[0x500098]=0x600000,
 [0x600000]=0x700000,[0x600010]=0,[0x700090]=0x800000,
 [0x8000d8]=1,[0x8000a8]=65536,[0x8000c0]=10,[0x8000c4]=10,
 [0x7004c0]=1,[0x7001b0]=1,[0x7004d8]=1,[0x7004c8]=0x900000,
 [0x900008]=11,[0x90000c]=10,[0x900055]=1,[0x90005a]=1,[0x900057]=0,
 [0x900020]=0xa00000,[0xa00008]=12345,[0xa0000c]=45678 }
fixtureObjects=objects
function Mem(...)
 assert(select('#',...)==2,'memory write attempted')
 local offset,kind=...; memCalls=memCalls+1
 assert(globals[offset]~=nil,'unknown global read '..tostring(offset))
 return globals[offset]
end
function ObjMem(...)
 assert(select('#',...)==3,'object write attempted')
 local object,offset,kind=...; objCalls=objCalls+1
 assert(type(object)=='number','Lua Player wrapper dereferenced')
 assert(objects[object+offset]~=nil,'unknown object read '..tostring(object+offset))
 return objects[object+offset]
end
function RegisterCallEvent(...) error('native callback registration attempted') end
local function event(name)
 local result={}
 result.Add=function(callback) callbacks[name]=callback end
 return result
end
GameEvents={OnGameTurnStarted=event('game'),PlayerTurnStarted=event('started')}
Events={PlayerTurnActivated=event('activated')}
Game={GetCurrentGameTurn=function() return 7 end}
Map={GetGridSize=function() return 80,50 end}
PlayerManager={GetAliveMajorIDs=function() return {1} end}
local city={GetID=function() return 65536 end,GetX=function() return 10 end,
 GetY=function() return 10 end}
local cities={Members=function() return ipairs({city}) end}
Players={[1]={__instance='not_a_Player_Instance',GetCities=function() return cities end}}
GameInfo={Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=2},
 DISTRICT_CSC_TAILORS_QUARTER={Index=3}}}
"""


@unittest.skipIf(LuaRuntime is None, "Requires the Lua 5.1 test dependency")
class ProbeTests(unittest.TestCase):
    def run_probe(self, change=""):
        runtime = LuaRuntime(unpack_returned_tuples=True)
        runtime.execute(FIXTURE)
        if change:
            runtime.execute(change)
        runtime.execute(Path(__file__).with_name("gameplay.lua").read_text(encoding="utf-8"))
        return runtime

    @staticmethod
    def logs(runtime):
        return "\n".join(runtime.globals().logs.values())

    def test_reads_native_chain_and_both_quarter_slots_without_writes(self):
        runtime = self.run_probe()
        log = self.logs(runtime)
        self.assertIn("raw_q8=12345", log)
        self.assertIn("raw_q8=45678", log)
        self.assertNotIn("kind=disabled", log)
        self.assertEqual(len(list(runtime.globals().callbacks.keys())), 3)

    def test_bad_header_disables_before_object_chain(self):
        runtime = self.run_probe("fixtureGlobals[0x88]=0")
        self.assertEqual(runtime.globals().objCalls, 0)
        self.assertIn("timestamp_mismatch", self.logs(runtime))

    def test_null_global_pointer_is_not_followed(self):
        runtime = self.run_probe("fixtureGlobals[0xb8aa68]=0")
        self.assertEqual(runtime.globals().objCalls, 0)
        self.assertIn("reason=game_missing", self.logs(runtime))

    def test_unfinished_job_skips_payload(self):
        runtime = self.run_probe("fixtureObjects[0x7004c0]=0; fixtureObjects[0x7004c8]=nil")
        log = self.logs(runtime)
        self.assertIn("cache_skipped=analysis_not_done", log)
        self.assertNotIn("kind=score", log)
        self.assertNotIn("kind=disabled", log)

    def test_game_turn_argument_is_not_misread_as_player_id(self):
        runtime = self.run_probe()
        runtime.execute("callbacks.game(77)")
        log = self.logs(runtime)
        self.assertIn("event=GameEvents.OnGameTurnStarted", log)
        self.assertNotIn("kind=disabled", log)

    def test_city_identity_mismatch_stops_before_payload(self):
        runtime = self.run_probe("fixtureObjects[0x8000a8]=999; fixtureObjects[0x7004c8]=nil")
        self.assertIn("city_identity_mismatch", self.logs(runtime))
        self.assertNotIn("kind=score", self.logs(runtime))

    def test_unaligned_pointer_is_not_followed(self):
        runtime = self.run_probe("fixtureObjects[0x100240]=0x200001")
        self.assertIn("unaligned_player_manager", self.logs(runtime))
        self.assertEqual(runtime.globals().objCalls, 1)

    def test_gameplay_environment_without_G_alias(self):
        runtime=self.run_probe('_G=nil')
        self.assertNotIn('kind=disabled',self.logs(runtime))
        self.assertIn('kind=score',self.logs(runtime))

    def test_installed_CE_without_unsigned_short_constant(self):
        runtime=self.run_probe('FIELD_UNSIGNED_SHORT=nil')
        self.assertNotIn('kind=disabled',self.logs(runtime))
        self.assertIn('kind=score',self.logs(runtime))

    def test_installed_CE_numeric_string_constants(self):
        runtime=self.run_probe("FIELD_SHORT='1';FIELD_INT='3';FIELD_UNSIGNED_INT='4';FIELD_UNSIGNED_LONG_LONG='6';FIELD_POINTER='12';FIELD_BYTE='0'")
        self.assertNotIn('kind=disabled',self.logs(runtime))
        self.assertIn('kind=score',self.logs(runtime))


if __name__ == "__main__":
    unittest.main()
