"""Read-only cache clone + actual Lua 5.1 tests for local, bounded Mill bonuses.

The two Mill rules deliberately supersede their historical empire-wide binary
contract. Generic owners/encodings and the frozen MAB comparison remain distinct.
No game is launched and no cache/installed mod file is modified.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
import sqlite3
import sys
import unittest
import zlib

from test_parity import CODE, ROOT, TESTS, lua_value

WIND = "CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS"
WATER = "CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER"
QUARTER = "DISTRICT_CSC_BAKERS_QUARTER"
BUILDINGS = {WIND: "BUILDING_CSC_BAKERS_WIND_MILL", WATER: "BUILDING_CSC_BAKERS_WATER_MILL"}
DATABASE: Path | None = None


def clone(source: Path) -> sqlite3.Connection:
    db = sqlite3.connect(":memory:")
    with sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True) as original:
        original.backup(db)
    db.row_factory = sqlite3.Row
    db.create_function("Make_Hash", 1, lambda value: zlib.crc32(value.encode()))
    return db


def compile_source(db: sqlite3.Connection) -> None:
    for name in ("Schema", "Sources", "Processor", "Modifiers"):
        db.executescript((CODE / f"CSC_Adjacency{name}.sql").read_text(encoding="utf-8-sig"))


def active_children(db: sqlite3.Connection) -> list[dict]:
    return [dict(row) for row in db.execute("""
        SELECT BM.BuildingType, BM.ModifierId AS Parent, M.ModifierId AS Child,
            M.OwnerRequirementSetId, A.Value AS Amount, T.CollectionType
        FROM BuildingModifiers AS BM
        JOIN ModifierArguments AS Link ON Link.ModifierId = BM.ModifierId AND Link.Name = 'ModifierId'
        JOIN Modifiers AS M ON M.ModifierId = Link.Value
        JOIN Modifiers AS Parent ON Parent.ModifierId = BM.ModifierId
        JOIN DynamicModifiers AS T ON T.ModifierType = Parent.ModifierType
        JOIN ModifierArguments AS A ON A.ModifierId = M.ModifierId AND A.Name = 'Amount'
        WHERE BM.BuildingType IN (?, ?) AND M.ModifierId LIKE 'MOD_CSC_ADJ_%'
        ORDER BY BM.BuildingType, M.ModifierId
    """, tuple(BUILDINGS.values()))]


def legacy_ids() -> tuple[list[str], list[str]]:
    modifiers, requirements = [], []
    for rule in (WIND, WATER):
        for bit in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
            modifiers.extend((f"MOD_CSC_ADJ_{rule}_{bit}", f"ATTACH_MOD_CSC_ADJ_{rule}_{bit}"))
            requirements.append(f"REQ_CSC_ADJ_{rule}_{bit}")
    return modifiers, requirements


def lua_world(db: sqlite3.Connection):
    from lupa.lua51 import LuaRuntime
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((TESTS / "world.lua").read_text(encoding="utf-8"))
    # Isolated native-shaped local cities; the existing broad world supplies
    # geography/plot objects and GameInfo's callable table adapter.
    lua.execute(r'''
GameInfo.Districts=info({{Index=77,DistrictType='DISTRICT_CSC_BAKERS_QUARTER',OnePerCity=1}})
GameInfo.Buildings=info({
 {Index=101,BuildingType='BUILDING_CSC_BAKERS_WIND_MILL',PrereqDistrict='DISTRICT_CSC_BAKERS_QUARTER'},
 {Index=102,BuildingType='BUILDING_CSC_BAKERS_WATER_MILL',PrereqDistrict='DISTRICT_CSC_BAKERS_QUARTER'}})
center.owner=0;center.district=77;center.riverCount=0
center.IsRiver=function(self)return self.riverCount>0 end
otherCenter=Map.GetPlot(5,5);otherCenter.owner=0;otherCenter.district=77
function millCity(plot,id)
 local c={owner=0,id=id,built={},pillaged={},locations={},quarterPillaged=false,ui=false}
 function c:GetOwner()return self.owner end
 function c:GetID()return self.id end
 function c:GetBuildings()
  local b={HasBuilding=function(_,index)return self.built[index]==true end,
   IsPillaged=function(_,index)return self.pillaged[index]==true end}
  if not self.ui then b.GetBuildingLocation=function(_,index)return self.locations[index] or -1 end end
  return b
 end
 function c:GetDistricts()
  if self.ui then return {
   IsPillaged=function(_,index)assert(index==77,'UI district type required');return self.quarterPillaged end,
   IsComplete=function(_,index)assert(index==77,'UI district type required');return self.quarterComplete~=false end}
  end
  if self.managerFallback then return {
   IsPillaged=function(_,index)assert(index==77);return self.quarterPillaged end,
   IsComplete=function(_,index)assert(index==77);return self.quarterComplete~=false end,
   GetDistrictLocation=function(_,index)assert(index==77);return plot.x,plot.y end}
  end
  return {
  GetNumDistricts=function()return 1 end,
  GetDistrictByIndex=function(_,index)if index==0 then return {
   GetType=function()return 77 end,GetX=function()return plot.x end,GetY=function()return plot.y end,
   IsComplete=function()return true end,IsPillaged=function()return self.quarterPillaged end}end end,
  GetDistrictLocation=function(_,index)if index==77 then return plot.x,plot.y end;return -1,-1 end,
  IsPillaged=function()return self.quarterPillaged end}
 end
 return c
end
city=millCity(center,11);otherCity=millCity(otherCenter,22)
local p=Players[0]
function p:GetCities()return {Members=function()local n=0;return function()n=n+1;if n==1 then return n,city elseif n==2 then return n,otherCity end end end}end
''')
    for table in ("CSC_AdjacencySources", "CSC_AdjacencyProviders", "CSC_AdjacencyObjects", "CSC_AdjacencyUnitSteps"):
        rows = [dict(row) for row in db.execute(f"SELECT * FROM {table}")]
        lua.execute(f"GameInfo.{table}=info({lua_value(rows)})")
    rules = [dict(row) for row in db.execute("SELECT * FROM CSC_AdjacencyRules WHERE ID IN (?, ?) ORDER BY ID", (WIND, WATER))]
    lua.execute(f"GameInfo.CSC_AdjacencyRules=info({lua_value(rules)})")
    lua.execute((CODE / "CSC_AdjacencyCore.lua").read_text(encoding="utf-8-sig"))
    lua.globals().CSC_Adjacency.Initialize()
    return lua, {row["ID"]: lua.table_from(row) for row in rules}


class LocalMillSteps(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if DATABASE is None:
            raise RuntimeError("Run test_local_mill_steps.py --database <read-only gameplay.sqlite> --dependencies <lupa directory>")
        cls.base = clone(DATABASE)
        cls.old_violations = set(map(tuple, cls.base.execute("PRAGMA foreign_key_check")))
        cls.old_unrelated = set(map(tuple, cls.base.execute(
            "SELECT * FROM BuildingModifiers WHERE ModifierId NOT LIKE 'ATTACH_MOD_CSC_ADJ_' || ? || '_%' AND ModifierId NOT LIKE 'ATTACH_MOD_CSC_ADJ_' || ? || '_%'",
            (WIND, WATER))))
        compile_source(cls.base)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "base"):
            cls.base.close()

    def db_copy(self):
        db = sqlite3.connect(":memory:")
        self.base.backup(db)
        db.row_factory = sqlite3.Row
        db.create_function("Make_Hash", 1, lambda value: zlib.crc32(value.encode()))
        self.addCleanup(db.close)
        return db

    def test_sql_four_unit_children_and_local_scope(self):
        children = active_children(self.base)
        self.assertEqual(len(children), 4)
        self.assertEqual(sum(row["BuildingType"] == BUILDINGS[WIND] for row in children), 1)
        self.assertEqual(sum(row["BuildingType"] == BUILDINGS[WATER] for row in children), 3)
        for child in children:
            self.assertEqual(child["Amount"], "1")
            self.assertEqual(child["CollectionType"], "COLLECTION_CITY_DISTRICTS")
            self.assertIn("_STEP_", child["Child"])
            args = dict(self.base.execute("SELECT Name,Value FROM RequirementArguments WHERE RequirementId = ?",
                (child["OwnerRequirementSetId"].replace("REQSET_", "REQ_", 1),)))
            self.assertEqual(args["PropertyMinimum"], "1")
            self.assertIn("_STEP_", args["PropertyName"])
        self.assertFalse(set(map(tuple, self.base.execute("PRAGMA foreign_key_check"))) - self.old_violations)
        now = set(map(tuple, self.base.execute(
            "SELECT * FROM BuildingModifiers WHERE ModifierId NOT LIKE 'ATTACH_MOD_CSC_ADJ_' || ? || '_%' AND ModifierId NOT LIKE 'ATTACH_MOD_CSC_ADJ_' || ? || '_%'",
            (WIND, WATER))))
        self.assertEqual(now, self.old_unrelated)

    def test_sql_reprocessing_is_duplicate_safe(self):
        db = self.db_copy()
        before = active_children(db)
        before_counts = {table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in ("Modifiers", "BuildingModifiers", "RequirementArguments")}
        compile_source(db)
        self.assertEqual(active_children(db), before)
        self.assertEqual({table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in before_counts}, before_counts)

    def test_fresh_database_recreates_disconnected_legacy_ids(self):
        db = self.db_copy()
        modifiers, requirements = legacy_ids()
        # Emulate their absence on a fresh game rules DB. This clone is the only
        # object changed; game SQL regenerates definitions without active roots.
        for modifier in modifiers:
            db.execute("DELETE FROM ModifierArguments WHERE ModifierId=?", (modifier,))
            db.execute("DELETE FROM Modifiers WHERE ModifierId=?", (modifier,))
        for requirement in requirements:
            reqset = requirement.replace("REQ_", "REQSET_", 1)
            db.execute("DELETE FROM RequirementSetRequirements WHERE RequirementSetId=?", (reqset,))
            db.execute("DELETE FROM RequirementArguments WHERE RequirementId=?", (requirement,))
            db.execute("DELETE FROM Requirements WHERE RequirementId=?", (requirement,))
            db.execute("DELETE FROM RequirementSets WHERE RequirementSetId=?", (reqset,))
        db.executescript((CODE / "CSC_AdjacencyModifiers.sql").read_text(encoding="utf-8-sig"))
        self.assertEqual(len(active_children(db)), 4)
        for modifier in modifiers:
            self.assertIsNotNone(db.execute("SELECT 1 FROM Modifiers WHERE ModifierId=?", (modifier,)).fetchone())
            self.assertIsNone(db.execute("SELECT 1 FROM BuildingModifiers WHERE ModifierId=?", (modifier,)).fetchone())

    def test_every_legal_amount_and_legacy_property_retirement(self):
        lua, rules = lua_world(self.base)
        core, plot = lua.globals().CSC_Adjacency, lua.globals().center
        for name, counts, maximum in ((WIND, range(2), 1), (WATER, range(7), 3)):
            key = "CSC_ADJ_" + name
            for count in list(counts) + [0]:
                for bit in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
                    plot.properties[f"{key}_{bit}"] = 1
                core.Write(plot, rules[name], count)
                expected = math.floor(count * rules[name].YieldChange)
                self.assertEqual(plot.properties[f"{key}_TOTAL"], count)
                self.assertEqual(plot.properties[f"{key}_ACTUAL_AMOUNT"], expected)
                self.assertEqual(plot.properties[f"{key}_ENCODED_AMOUNT"], expected)
                self.assertEqual(sum(plot.properties[f"{key}_STEP_{step}"] for step in range(1, maximum + 1)), expected)
                self.assertTrue(all(plot.properties[f"{key}_{bit}"] == 0 for bit in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512)))

    def test_only_local_functioning_building_and_matching_quarter(self):
        lua, rules = lua_world(self.base)
        g = lua.globals()
        wind = rules[WIND]
        g.otherCity.built[101] = True
        g.otherCity.locations[101] = g.otherCenter.GetIndex(g.otherCenter)
        self.assertFalse(g.CSC_Adjacency.Eligible(wind, g.city, 0))
        g.city.built[101] = True
        g.city.locations[101] = g.center.GetIndex(g.center)
        self.assertTrue(g.CSC_Adjacency.Eligible(wind, g.city, 0))
        g.city.pillaged[101] = True
        self.assertFalse(g.CSC_Adjacency.Eligible(wind, g.city, 0))
        g.city.pillaged[101] = False
        g.city.quarterPillaged = True
        self.assertFalse(g.CSC_Adjacency.Eligible(wind, g.city, 0))
        g.city.quarterPillaged = False
        g.city.locations[101] = g.otherCenter.GetIndex(g.otherCenter)
        self.assertFalse(g.CSC_Adjacency.Eligible(wind, g.city, 0))
        g.city.locations[101] = g.center.GetIndex(g.center)
        self.assertFalse(g.CSC_Adjacency.Eligible(wind, g.city, 1))
        g.city.ui = True
        self.assertTrue(g.CSC_Adjacency.Eligible(wind, g.city, 0))
        g.city.built[101] = False
        self.assertFalse(g.CSC_Adjacency.Eligible(wind, g.city, 0))

    def test_manager_only_ui_lifecycle_and_hks_integer_tags(self):
        lua, rules = lua_world(self.base)
        g=lua.globals()
        wind=rules[WIND]
        g.city.built[101]=True
        g.city.locations[101]=g.center.GetIndex(g.center)
        g.city.ui=True  # No indexed objects, location getter or building location.
        self.assertTrue(g.CSC_Adjacency.Eligible(wind,g.city,0))
        g.city.quarterPillaged=True
        self.assertFalse(g.CSC_Adjacency.Eligible(wind,g.city,0))
        g.city.quarterPillaged=False
        g.city.quarterComplete=False
        self.assertFalse(g.CSC_Adjacency.Eligible(wind,g.city,0))
        g.city.quarterComplete=True
        self.assertTrue(g.CSC_Adjacency.Eligible(wind,g.city,0))
        # Simulate the native HKS numeric tag using the actual Lua source; this
        # tests the new guards, not an assertion of native in-game execution.
        lua.execute("""
local originalType=type
type=function(value)
 if originalType(value)=='number' and value==math.floor(value) then return 'integer' end
 return originalType(value)
end
""")
        g.city.ui=False
        self.assertTrue(g.CSC_Adjacency.Eligible(wind,g.city,0))
        g.city.managerFallback=True  # Verified x,y binding plus native integer tags.
        self.assertTrue(g.CSC_Adjacency.Eligible(wind,g.city,0))
        self.assertEqual(g.CSC_Adjacency.Amount(wind,1),(1,1))
        self.assertEqual(g.CSC_Adjacency.Amount(rules[WATER],6),(3,3))
        with self.assertRaises(Exception):
            g.CSC_Adjacency.Amount(wind,"1")

    def test_planned_scanner_and_actual_ui_remain_distinct(self):
        lua, _ = lua_world(self.base)
        g = lua.globals()
        g.include = lambda name: None  # The real shared core is already loaded.
        lua.execute((CODE / "CSC_AdjacencyPresentation.lua").read_text(encoding="utf-8-sig"))
        _, _, totals = g.CSC_Adjacency.Preview(QUARTER, g.center, g.city)
        self.assertIsNone(totals["SelfBonus:YIELD_PRODUCTION"])
        # Execute the scanner's actual score closure, without scanning or writing
        # any world. Planning deliberately includes the first local Mill.
        scanner = (ROOT / "Civ Supply Chains/Lua_UI/AI/CSC_AI_AdjacencyScan.lua").read_text(encoding="utf-8")
        lua.execute(scanner.split("function CSC_AI_AdjacencyScan", 1)[0] + "\nCSC_LocalMillTestScore=score")
        planned = g.CSC_LocalMillTestScore(QUARTER, g.center, g.city, 0)
        self.assertEqual(planned.production, 1)
        self.assertEqual(planned.current.production, 0)
        g.center.riverCount = 6
        planned = g.CSC_LocalMillTestScore(QUARTER, g.center, g.city, 0)
        self.assertEqual(planned.production, 3)
        self.assertEqual(planned.current.production, 0)
        g.city.built[102] = True
        g.city.locations[102] = g.center.GetIndex(g.center)
        planned = g.CSC_LocalMillTestScore(QUARTER, g.center, g.city, 0)
        self.assertEqual(planned.current.production, 3)
        _, _, totals = g.CSC_Adjacency.Preview(QUARTER, g.center, g.city)
        self.assertEqual(totals["SelfBonus:YIELD_PRODUCTION"].Amount, 3)

    def test_invalid_bounds_fail_before_property_publication(self):
        lua, rules = lua_world(self.base)
        g = lua.globals()
        before = dict(g.center.properties.items())
        for name, count in ((WIND, 2), (WATER, 7), (WATER, -1), (WATER, 1.5), (WATER, float("nan"))):
            with self.assertRaises(Exception):
                g.CSC_Adjacency.Write(g.center, rules[name], count)
            self.assertEqual(dict(g.center.properties.items()), before)
        lua.execute(f"GameInfo.CSC_AdjacencyUnitSteps=info({{{{ID='{WIND}',MaxAmount=2}}}})")
        with self.assertRaises(Exception):
            g.CSC_Adjacency.Initialize()
        db = self.db_copy()
        db.execute("UPDATE CSC_AdjacencyUnitSteps SET MaxAmount=2 WHERE ID=?", (WIND,))
        with self.assertRaises(sqlite3.IntegrityError):
            db.executescript((CODE / "CSC_AdjacencyModifiers.sql").read_text(encoding="utf-8-sig"))

    def test_generic_signed_binary_and_owner_contract_unchanged(self):
        lua, _ = lua_world(self.base)
        g = lua.globals()
        generic = lua.table_from({"ID": "GENERIC_NEGATIVE", "YieldChange": -0.5})
        for count in (0, 1, 2, 3, 6, 10000, 0):
            g.CSC_Adjacency.Write(g.center, generic, count)
            raw = math.trunc(-0.5 * count)
            self.assertEqual(g.center.properties["CSC_ADJ_GENERIC_NEGATIVE_ACTUAL_AMOUNT"], raw)
            self.assertEqual(sum(bit * g.center.properties[f"CSC_ADJ_GENERIC_NEGATIVE_{bit}"] for bit in (1,2,4,8,16,32,64,128,256,512)), min(abs(raw), 1023))
        generic = lua.table_from({"ID": "UNRELATED_OWNER", "ModifierOwner": "BuildingModifiers", "WhoIsTheOwner": BUILDINGS[WIND], "CollectionType": "COLLECTION_PLAYER_DISTRICTS"})
        g.otherCity.built[101] = True
        self.assertTrue(g.CSC_Adjacency.Eligible(generic, g.city, 0))


def main():
    global DATABASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--dependencies", type=Path, required=True)
    args, remaining = parser.parse_known_args()
    DATABASE = args.database
    sys.path.insert(0, str(args.dependencies))
    unittest.main(argv=[sys.argv[0], *remaining])


if __name__ == "__main__":
    main()
