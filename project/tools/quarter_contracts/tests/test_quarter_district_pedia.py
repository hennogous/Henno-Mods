import unittest
from pathlib import Path

try:
    from lupa.lua51 import LuaRuntime
except ImportError:
    LuaRuntime = None


ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "Civ Supply Chains/Lua_UI/Pedia/CivilopediaPage_CSC_QuarterDistricts.lua"
BAKERS = "DISTRICT_CSC_BAKERS_QUARTER"
TAILORS = "DISTRICT_CSC_TAILORS_QUARTER"


@unittest.skipIf(LuaRuntime is None, "requires the isolated Lua 5.1 test dependency")
class QuarterDistrictPediaTests(unittest.TestCase):
    def setUp(self):
        self.lua = LuaRuntime()
        self.lua.execute("""
            local function rows(items)
                return function()
                    local i = 0
                    return function() i = i + 1; return items[i] end
                end
            end
            local districts = {}
            GameInfo = {
                Districts = setmetatable({}, { __call = rows(districts) }),
                Leaders = { WILFRID = { InheritFrom = 'LEADER_DEFAULT' } },
                CivilizationTraits = rows({ { CivilizationType = 'CANADA', TraitType = 'CANADIAN' } }),
                LeaderTraits = rows({ { LeaderType = 'WILFRID', TraitType = 'WILFRID_TRAIT' } }),
                ExcludedDistricts = rows({ { DistrictType = 'DISTRICT_EXTRA', TraitType = 'WILFRID_TRAIT' } }),
            }
            local tags, replacements = {}, {}
            GameInfo.TypeTags = rows(tags)
            GameInfo.DistrictReplaces = rows(replacements)
            function AddDistrict(kind, name, trait, internal)
                local row = { DistrictType = kind, Name = name, TraitType = trait, InternalOnly = internal }
                districts[#districts + 1] = row
                GameInfo.Districts[kind] = row
            end
            function AddTag(kind, tag)
                tags[#tags + 1] = { Type = kind, Tag = 'CLASS_CSC_' .. tag }
            end
            function AddReplacement(base, unique)
                replacements[#replacements + 1] = { ReplacesDistrictType = base, CivUniqueDistrictType = unique }
            end
            function SetPlayer(civilization, leader)
                playerId = civilization and 0 or -1
                PlayerConfigurations[0] = {
                    GetCivilizationTypeName = function() return civilization end,
                    GetLeaderTypeName = function() return leader end,
                }
            end
            PlayerConfigurations = {}
            Game = { GetLocalPlayer = function() return playerId end }
            Locale = {
                Lookup = function(name) return name end,
                Compare = function(a, b) if a == b then return 0 elseif a < b then return -1 else return 1 end end,
            }
            function GetChapterBody() return { 'Stock chapter' } end
            SetPlayer('ROME', 'TRAJAN')
        """)
        self.lua.execute(SCRIPT.read_text(encoding="utf-8"))

    def chapter(self, page, chapter):
        result = self.lua.globals().GetChapterBody("DISTRICTS", page, chapter)
        return result[1] if result else None

    def test_base_lists_use_tags_and_leave_other_chapters_to_stock_renderer(self):
        self.lua.execute("""
            AddDistrict('DISTRICT_CITY_CENTER', 'City Center')
            AddDistrict('DISTRICT_INTERNAL', 'Internal district', nil, true)
            AddTag('DISTRICT_CITY_CENTER', 'BAKERS_SALES')
            AddTag('DISTRICT_INTERNAL', 'BAKERS_SALES')
            AddTag('MISSING_DISTRICT', 'BAKERS_SALES')
        """)
        self.assertEqual(self.chapter(BAKERS, "CSCSALES"), "[ICON_BULLET][ICON_DISTRICT_CITY_CENTER] City Center")
        self.assertIsNone(self.chapter(BAKERS, "CSCGOODS"))
        self.assertEqual(self.chapter(BAKERS, "CSCBASE"), "Stock chapter")
        self.assertEqual(self.chapter("DISTRICT_HARBOR", "CSCSALES"), "Stock chapter")

    def test_city_lights_replacements_follow_the_active_player(self):
        self.lua.execute("""
            AddDistrict('DISTRICT_RURALCOMMUNITYA', 'Farming Town')
            AddDistrict('DISTRICT_COREX_FRONTIER_TOWN', 'Frontier Town', 'CANADIAN')
            AddDistrict('DISTRICT_EXTRA', 'Extra Town')
            AddDistrict('DISTRICT_COREX_VENICE_01', 'Venetian Borough', 'MINOR_CIV_ANTIOCH_TRAIT')
            AddReplacement('DISTRICT_RURALCOMMUNITYA', 'DISTRICT_COREX_FRONTIER_TOWN')
            for _, quarter in ipairs({ 'BAKERS', 'TAILORS' }) do
                AddTag('DISTRICT_RURALCOMMUNITYA', quarter .. '_GOODS_PROVIDER')
                AddTag('DISTRICT_COREX_FRONTIER_TOWN', quarter .. '_GOODS_PROVIDER')
                AddTag('DISTRICT_COREX_FRONTIER_TOWN', quarter .. '_SALES_FOOD')
                AddTag('DISTRICT_EXTRA', quarter .. '_GOODS_PROVIDER')
                AddTag('DISTRICT_COREX_VENICE_01', quarter .. '_SALES')
            end
        """)
        for page in (BAKERS, TAILORS):
            with self.subTest(page=page):
                self.lua.globals().SetPlayer("ROME", "TRAJAN")
                goods = self.chapter(page, "CSCGOODS")
                self.assertIn("Farming Town", goods)
                self.assertNotIn("Frontier Town", goods)
                self.lua.globals().SetPlayer("CANADA", "WILFRID")
                self.assertEqual(self.chapter(page, "CSCGOODS"), "[ICON_BULLET][ICON_DISTRICT_COREX_FRONTIER_TOWN] Frontier Town")
                self.assertIsNone(self.chapter(page, "CSCSALES"))
                self.lua.globals().SetPlayer(None, None)
                goods = self.chapter(page, "CSCGOODS")
                self.assertIn("Farming Town", goods)
                self.assertIn("Frontier Town", goods)
