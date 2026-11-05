"""Actual Lua5.1 read-only collector fixtures; optional full rules transport check."""
import argparse
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = (HERE / "world.lua").read_text(encoding="utf-8")
DATABASE = None
spec = importlib.util.spec_from_file_location("adjacency_test_helpers", ROOT / "project/tools/adjacencies/test_parity.py")
helpers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(helpers)


def decode_chunks(lines):
    """Strict fixture decoder mirrors the controller transport contract."""
    marker = "CSC_MILL_BUILDING_WORLD_CHUNK="
    frames = [json.loads(line[len(marker):]) for line in lines if line.startswith(marker)]
    if not frames:
        raise ValueError("Missing world frames")
    first = frames[0]
    if (first["schema"] != 1 or first["encoding"] != "hex"
            or not 0 < first["bytes"] < 1024 * 1024
            or first["parts"] != (first["bytes"] + 511) // 512
            or len(frames) != first["parts"]):
        raise ValueError("Invalid frame metadata")
    chunks = []
    for part, frame in enumerate(frames, 1):
        if frame["part"] != part or any(frame[key] != first[key]
                for key in ("schema", "parts", "bytes", "sum32", "encoding")):
            raise ValueError("Out-of-order or inconsistent frame")
        chunk = bytes.fromhex(frame["data"])
        expected = min(512, first["bytes"] - (part - 1) * 512)
        if len(chunk) != expected or len(frame["data"]) != expected * 2:
            raise ValueError("Invalid chunk length")
        chunks.append(chunk)
    raw = b"".join(chunks)
    if len(raw) != first["bytes"] or sum(raw) % 2**32 != first["sum32"]:
        raise ValueError("World checksum mismatch")
    return raw.decode("utf-8")

SETUP = r'''
CAPTURED={};READS=0;WRITES=0
print=function(s)CAPTURED[#CAPTURED+1]=s end
Map.GetGridSize=function()return width,height end
local family=GameInfo.Buildings
function makeCity(owner,id,x,y,candidate)
 local city={owner=owner,id=id,x=x,y=y,candidate=candidate,quarter=false,built={}}
 function city:GetOwner()return self.owner end
 function city:GetID()return self.id end
 function city:GetName()return 'Fixture '..self.id end
 function city:GetX()return self.x end
 function city:GetY()return self.y end
 function city:GetPopulation()return 15 end
 function city:GetProperty(key)READS=READS+1;if key=='CSC_HAS_BAKERS_QUARTER'then return 0 end end
 function city:SetProperty()WRITES=WRITES+1;error('Forbidden property write')end
 function city:GetBuildings()return {
  HasBuilding=function(_,index)return self.built[index]==true end,
  IsPillaged=function()return false end,
  GetBuildingLocation=function(_,index)if self.built[index]then return Map.GetPlot(self.x,self.y):GetIndex()end;return -1 end}end
 function city:GetBuildQueue()return {
  CurrentlyBuilding=function()return 'UNIT_WARRIOR'end,GetCurrentProductionTypeHash=function()return 17 end,
  GetSize=function()return 1 end,GetBuildingProgress=function()return 0 end,
  CreateBuilding=function()WRITES=WRITES+1;error('Forbidden grant')end}end
 function city:GetGrowth()return {GetAmenities=function()return 2 end,GetAmenitiesNeeded=function()return 7 end,
  GetHousing=function()return 15 end,GetFoodSurplus=function()return 3 end,GetHappiness=function()return -1 end}end
 function city:GetYield(index)return index+2 end
 function city:GetDistricts()
  local function district(index,x,y)return {GetType=function()return index end,GetX=function()return x end,
   GetY=function()return y end,IsComplete=function()return true end,IsPillaged=function()return false end}end
  return {GetNumDistricts=function()return self.quarter and 2 or 1 end,
   GetDistrictByIndex=function(_,i)if i==0 then return district(0,self.x,self.y)
    elseif i==1 and self.quarter then local p=Map.GetPlotByIndex(self.candidate);return district(1,p:GetX(),p:GetY())end end}
 end
 return city
end
local function player(pid,city)
 return {IsHuman=function()return pid==0 end,IsAlive=function()return true end,IsMajor=function()return true end,
  GetCities=function()return {Members=function()local done=false;return function()if not done then done=true;return 1,city end end end}end,
  GetTechs=function()return {HasTech=function()return true end}end,
  GetCulture=function()return {HasCivic=function()return true end}end,
  GetTreasury=function()return {GetGoldBalance=function()return 100 end}end}
end
local positions=FIXTURE_POSITIONS or {{1,1,2,1},{5,5,4,5}}
city1=makeCity(1,11,positions[1][1],positions[1][2],positions[1][3]+positions[1][4]*width)
city2=makeCity(2,22,positions[2][1],positions[2][2],positions[2][3]+positions[2][4]*width)
Players={[0]={IsHuman=function()return true end},[1]=player(1,city1),[2]=player(2,city2)}
PlayersVisibility={[1]={IsRevealed=function()return true end},[2]={IsRevealed=function()return true end}}
for _,city in ipairs({city1,city2})do
 local center=Map.GetPlot(city.x,city.y);center.owner=city.owner;center.district=0
 local candidate=Map.GetPlotByIndex(city.candidate);candidate.owner=city.owner;candidate.district=-1
end
for _,p in ipairs(world)do
 p.IsRiver=function(self)return self.riverCount>0 end
 p.CanHaveDistrict=function()return true end
 p.GetProperty=function(self,key)READS=READS+1;return self.properties[key]end
 p.SetProperty=function()WRITES=WRITES+1;error('Forbidden plot property write')end
end
Game={GetCurrentGameTurn=function()return 17 end}
CSC_MILL_STUDY_CONFIG={targets={{player=1,city=11,plot=city1.candidate},{player=2,city=22,plot=city2.candidate}}}
'''


def fixture(extra="", full_database=False, with_core=False, large_world=False):
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((ROOT / "project/tests/adjacencies/world.lua").read_text(encoding="utf-8"))
    ledger = json.loads((HERE / "ledger/contributions.json").read_text(encoding="utf-8"))
    buildings = []
    for index, item in enumerate(ledger["building_definitions"]):
        row = {key: value for key, value in item.items() if not isinstance(value, (list, dict))}
        row["Index"] = index
        buildings.append(row)
    buildings.append({"Index": len(buildings), "BuildingType": "BUILDING_GRANARY", "PrereqDistrict": "DISTRICT_CITY_CENTER"})
    lua.execute("GameInfo.Buildings=info(" + helpers.lua_value(buildings) + ")")
    lua.execute("GameInfo.Districts=info({{Index=0,DistrictType='DISTRICT_CITY_CENTER'},"
        "{Index=1,DistrictType='DISTRICT_CSC_BAKERS_QUARTER',OnePerCity=1},"
        "{Index=2,DistrictType='DISTRICT_CSC_TAILORS_QUARTER',OnePerCity=1}})")
    lua.execute("GameInfo.CSC_AdjacencyRules=info({});GameInfo.CSC_AdjacencyUnitSteps=info({})")
    if full_database:
        if DATABASE is None:
            raise unittest.SkipTest("Full rules budget needs --database")
        with sqlite3.connect(DATABASE.resolve().as_uri() + "?mode=ro", uri=True) as db:
            db.row_factory = sqlite3.Row
            for table in ("Buildings", "Districts", "Yields", "BuildingPrereqs", "MutuallyExclusiveBuildings",
                "Building_CitizenYieldChanges", "Building_YieldChanges", "BuildingModifiers", "DistrictModifiers",
                "Modifiers", "ModifierArguments", "DynamicModifiers", "CSC_AdjacencyRules", "CSC_AdjacencyUnitSteps",
                "CSC_AdjacencySources", "CSC_AdjacencyProviders", "CSC_AdjacencyObjects", "TypeTags", "Tags",
                "Resources", "Technologies", "Civics"):
                rows = [dict(r) for r in db.execute(f"SELECT * FROM {table}")]
                if table in ("Buildings", "Districts", "Yields", "Resources", "Technologies", "Civics"):
                    # Fixture-only indices; native mapping is never inferred from SQLite.
                    for index, row in enumerate(rows):
                        row["Index"] = index
                lua.execute(f"GameInfo.{table}=info(" + helpers.lua_value(rows) + ")")
    if large_world:
        lua.execute("resetWorld(20,10,false);FIXTURE_POSITIONS={{4,4,5,4},{14,4,13,4}}")
        lua.execute("DB.MakeHash=function(s)local h=0;for i=1,#s do h=(h*31+s:byte(i))%4294967296 end;return h end")
    lua.execute(SETUP)
    if with_core:
        lua.execute((ROOT / "Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua").read_text(encoding="utf-8-sig"))
    if extra:
        lua.execute(extra)
    lua.execute(SOURCE)
    lines = list(lua.globals().CAPTURED.values())
    raw = decode_chunks(lines)
    return lua, json.loads(raw), raw, lines


class WorldTests(unittest.TestCase):
    def test_scope_mapping_and_no_gameplay_mutation(self):
        lua, out, _, lines = fixture()
        self.assertGreater(len(lines), 1)
        self.assertTrue(all(len(line.encode("utf-8")) < 2047 for line in lines))
        self.assertTrue(out["sourceValidation"]["valid"])
        self.assertEqual(len(out["observerConfig"]["buildings"]), 19)
        self.assertEqual(out["observerConfig"]["targets"], [{"player": 1, "city": 11}, {"player": 2, "city": 22}])
        self.assertEqual(out["observerConfig"]["maxPairs"], 16384)
        self.assertEqual(out["observerConfig"]["maxModifierName"], 256)
        self.assertEqual(out["targets"][0]["population"], 15)
        self.assertEqual(out["targets"][0]["growth"]["GetAmenitiesNeeded"], 7)
        self.assertEqual(lua.globals().WRITES, 0)
        self.assertGreater(lua.globals().READS, 0)

    def test_built_endpoint_is_captured_without_rejecting_receipt(self):
        _, out, _, _ = fixture("city1.quarter=true;Map.GetPlotByIndex(9).district=1")
        self.assertTrue(out["mappingVerified"])
        self.assertFalse(out["sourceValidation"]["valid"])
        self.assertFalse(out["sourceValidation"]["noQuarterAtSource"])
        self.assertTrue(out["targets"][0]["hasQuarters"]["DISTRICT_CSC_BAKERS_QUARTER"])
        self.assertEqual(len(out["targets"][0]["districts"]), 2)

    def test_missing_scope_and_foreign_candidate_are_explicit(self):
        _, out, _, _ = fixture("CSC_MILL_STUDY_CONFIG.targets[2].city=999;Map.GetPlotByIndex(9).owner=2")
        self.assertFalse(out["sourceValidation"]["targetsExist"])
        self.assertFalse(out["sourceValidation"]["ownedEmptyCandidates"])
        self.assertFalse(out["targets"][1]["exists"])

    def test_absent_and_zero_properties_are_distinct(self):
        _, out, _, _ = fixture()
        index = out["propertyNames"].index("CSC_HAS_BAKERS_QUARTER")
        self.assertEqual(out["targets"][0]["cityProperties"][index], 0)
        self.assertIn("ABSENT", out["targets"][0]["cityProperties"])

    def test_native_integer_tag_receipts_and_input_rejects_strings(self):
        extra = """
local realType=type
type=function(v)if realType(v)=='number'and v==math.floor(v)then return 'integer'end;return realType(v)end
"""
        _, out, _, _ = fixture(extra)
        self.assertTrue(out["mappingVerified"])
        with self.assertRaises(Exception):
            fixture("CSC_MILL_STUDY_CONFIG.targets[1].plot='9'")

    def test_full_rules_metadata_and_transport_budget(self):
        lua, out, raw, lines = fixture(full_database=True,with_core=True,large_world=True)
        self.assertEqual(len(out["mapping"]["family"]), 19)
        self.assertEqual(len(out["metadata"]["unitSteps"]["rows"]), 2)
        self.assertGreater(len(out["metadata"]["modifiers"]["rows"]), 88)
        self.assertTrue(out["sharedAdjacencyAvailable"])
        self.assertEqual(out["targets"][0]["cityTilesRadius"],3)
        self.assertEqual(len(out["targets"][0]["cityTiles"]),37)
        self.assertLess(len(raw.encode("utf-8")), 1024*1024)
        self.assertTrue(all(len(line.encode("utf-8")) < 2047 for line in lines))
        self.assertEqual(lua.globals().WRITES,0)
        self.assertIn("outside candidate building root coverage", out["coverage"]["citycenterBitDefinitions"])

    def test_chunk_integrity_and_utf8_reconstruction(self):
        _, out, raw, lines = fixture("function city1:GetName()return 'Fixture café' end")
        self.assertEqual(out["targets"][0]["name"], "Fixture café")
        self.assertEqual(decode_chunks(lines), raw)
        with self.assertRaises(ValueError):
            decode_chunks(lines[:-1])
        with self.assertRaises(ValueError):
            decode_chunks([lines[1], lines[0], *lines[2:]])
        frame = json.loads(lines[0].split("=", 1)[1])
        frame["data"] = ("00" if frame["data"][:2] != "00" else "01") + frame["data"][2:]
        with self.assertRaises(ValueError):
            decode_chunks(["CSC_MILL_BUILDING_WORLD_CHUNK=" + json.dumps(frame), *lines[1:]])


def main():
    global DATABASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path, required=True)
    parser.add_argument("--database", type=Path)
    args, remaining = parser.parse_known_args()
    sys.path.insert(0, str(args.dependencies))
    DATABASE = args.database
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == "__main__":
    main()
