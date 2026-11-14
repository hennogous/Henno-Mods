"""Passive resource preflight: loaded DB gates, provenance and census integrity."""
from contextlib import closing
import hashlib
import importlib.util
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from lupa.lua51 import LuaRuntime

SOURCE = Path(__file__).with_name('resource_stack_preflight.py')
spec = importlib.util.spec_from_file_location('resource_preflight', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Controller:
    def __init__(self, raw=None):
        self.calls = []
        self.raw = raw or ('CSC_RESOURCE_STACK_BEGIN\t1\n'
                           'CSC_RESOURCE_STACK_ROW\tRESOURCE_WHEAT\t8\t2\n'
                           'CSC_RESOURCE_STACK_ROW\tRESOURCE_MODDED_BASE\t3\t1\n'
                           'CSC_RESOURCE_STACK_END\t2\n')

    def cmd(self, *args):
        self.calls.append(args)
        return self.raw


def fixture(folder):
    root = Path(folder)
    (root / 'Cache').mkdir()
    vanilla = root / 'Resources.xml'
    vanilla.write_text('<GameInfo><Resources><Row ResourceType="RESOURCE_WHEAT"/>'
                       '<Row ResourceType="RESOURCE_CSC_VANILLA_NAME"/></Resources></GameInfo>')
    mod = root / 'resource-pack'
    mod.mkdir()
    (mod / 'Resources.sql').write_text("""
INSERT INTO Resources(ResourceType,ResourceClassType) VALUES
 ('RESOURCE_MODDED_BASE','RESOURCECLASS_BONUS'),
 ('RESOURCE_MODDED_SPEC','RESOURCECLASS_LUXURY');
INSERT INTO Resources(ResourceType) SELECT 'RESOURCE_GOLD' FROM Resource_YieldChanges;
""")
    csc = root / 'csc'
    csc.mkdir()
    (csc / 'Resources.xml').write_text('<GameInfo><Resources><Row>'
        '<ResourceType>RESOURCE_HANDMADE</ResourceType></Row></Resources></GameInfo>')
    mods = {m.SR_ID: dict(path=str(mod), files={'Resources.sql': 'unusedhash'}),
            m.CL_ID: dict(path=str(mod), files=[])}
    dbpath = root / 'Cache/DebugGameplay.sqlite'
    with closing(sqlite3.connect(dbpath)) as db:
        db.executescript('''
CREATE TABLE Resources(ResourceType);
CREATE TABLE TypeTags(Type,Tag);
CREATE TABLE Improvements(ImprovementType);
CREATE TABLE Improvement_ValidResources(ResourceType,ImprovementType);
CREATE TABLE Districts(DistrictType);
CREATE TABLE DistrictReplaces(CivUniqueDistrictType,ReplacesDistrictType);
INSERT INTO Resources VALUES('RESOURCE_WHEAT'),('RESOURCE_MODDED_BASE'),
 ('RESOURCE_MODDED_SPEC'),('RESOURCE_GOLD'),('RESOURCE_HANDMADE'),
 ('RESOURCE_UNKNOWN'),('RESOURCE_CSC_VANILLA_NAME');
INSERT INTO Improvements VALUES('IMPROVEMENT_MINE');
INSERT INTO Improvement_ValidResources SELECT ResourceType,'IMPROVEMENT_MINE' FROM Resources;
INSERT INTO TypeTags VALUES
 ('RESOURCE_WHEAT','CLASS_CSC_BAKERS_BASE'),
 ('RESOURCE_MODDED_SPEC','CLASS_CSC_BAKERS_SPEC'),
 ('RESOURCE_MODDED_BASE','CLASS_CSC_TAILORS_BASE'),
 ('RESOURCE_GOLD','CLASS_CSC_TAILORS_SPEC');
INSERT INTO Districts VALUES('DISTRICT_RURALCOMMUNITYA'),('DISTRICT_MODDED_RURAL_REPLACEMENT');
INSERT INTO DistrictReplaces VALUES('DISTRICT_MODDED_RURAL_REPLACEMENT','DISTRICT_RURALCOMMUNITYA');
INSERT INTO TypeTags SELECT DistrictType,'CLASS_CSC_BAKERS_GOODS_PROVIDER' FROM Districts;
INSERT INTO TypeTags SELECT DistrictType,'CLASS_CSC_TAILORS_GOODS_PROVIDER' FROM Districts;
''')
        db.commit()
    return root, vanilla, csc, mods


class ResourceStackPreflight(unittest.TestCase):
    def test_sources_are_actual_producers_not_mentions_or_identifier_prefixes(self):
        with tempfile.TemporaryDirectory(dir=SOURCE.parent) as folder:
            p = Path(folder) / 'producer.sql'
            p.write_text("""
-- INSERT INTO Resources(ResourceType) VALUES('RESOURCE_COMMENT');
INSERT INTO TypeTags(Type,Tag) VALUES('RESOURCE_REFERENCE','CLASS_OTHER');
UPDATE Resources SET ResourceType='RESOURCE_UPDATE' WHERE ResourceType='RESOURCE_OLD';
INSERT OR IGNORE INTO Resources(Name,ResourceType) VALUES
 ('Text with ; separator','RESOURCE_LITERAL'),('Other','RESOURCE_SECOND');
INSERT INTO Resources(ResourceType) SELECT 'RESOURCE_SELECTED' FROM OtherTable;
INSERT INTO Resources(ResourceType) SELECT ResourceType FROM OtherTable;
""")
            names, uncertain = m.declared_resources(p)
            self.assertEqual(names, {'RESOURCE_LITERAL', 'RESOURCE_SECOND', 'RESOURCE_SELECTED'})
            self.assertEqual(len(uncertain), 1)

    def test_scenario_only_gold_is_not_a_vanilla_normal_game_producer(self):
        with tempfile.TemporaryDirectory(dir=SOURCE.parent) as folder:
            root = Path(folder)
            normal = root / 'Base/Assets/Gameplay/Data/Resources.xml'
            scenario = root / 'DLC/AustraliaScenario/Data/Resources.xml'
            normal.parent.mkdir(parents=True); scenario.parent.mkdir(parents=True)
            normal.write_text('<GameInfo><Resources><Row ResourceType="RESOURCE_WHEAT"/></Resources></GameInfo>')
            scenario.write_text('<GameInfo><Resources><Row ResourceType="RESOURCE_GOLD"/></Resources></GameInfo>')
            with patch.object(m, 'GAME_ROOT', root):
                self.assertEqual(m._vanilla_sources(), [normal])

    def test_loaded_rules_origin_coverage_and_absent_seed_materials(self):
        with tempfile.TemporaryDirectory(dir=SOURCE.parent) as folder:
            root, vanilla, csc, mods = fixture(folder)
            original = hashlib.sha256((root / 'Cache/DebugGameplay.sqlite').read_bytes()).hexdigest()
            controller = Controller()
            with patch.object(m, '_vanilla_sources', return_value=[vanilla]):
                result = m.inspect_resource_stack(controller, root / 'out', root, mods, csc_path=csc)
            self.assertTrue(result['verified'])
            self.assertEqual(result['origins']['RESOURCE_CSC_VANILLA_NAME'], 'vanilla')
            self.assertEqual(result['origins']['RESOURCE_HANDMADE'], 'modded')
            self.assertEqual(result['origins']['RESOURCE_MODDED_SPEC'], 'modded')
            self.assertEqual(result['origins']['RESOURCE_UNKNOWN'], 'unknown')
            self.assertEqual(result['counts']['RESOURCE_MODDED_BASE'], dict(map=3, ai_owned=1))
            self.assertEqual(result['counts']['RESOURCE_GOLD'], dict(map=0, ai_owned=0))
            self.assertIn('No map instances for CLASS_CSC_TAILORS_SPEC', result['limits'])
            self.assertIn('DISTRICT_MODDED_RURAL_REPLACEMENT', result['city_lights_providers'])
            self.assertEqual(len(controller.calls), 1)
            self.assertEqual(original, result['database_sha256'])
            self.assertEqual(original, hashlib.sha256((root / 'Cache/DebugGameplay.sqlite').read_bytes()).hexdigest())
            vm = LuaRuntime()
            origins = vm.execute('return ' + (root / 'out/resource-origins.lua').read_text())
            self.assertEqual(origins['RESOURCE_HANDMADE'], 'modded')
            self.assertTrue(json.loads((root / 'out/resource-stack-preflight.json').read_text())['verified'])

    def test_removed_resourceful_gold_alias_is_unused_not_a_broken_supplier(self):
        with tempfile.TemporaryDirectory(dir=SOURCE.parent) as folder:
            root, vanilla, csc, mods = fixture(folder)
            with closing(sqlite3.connect(root / 'Cache/DebugGameplay.sqlite')) as db:
                # R2 compatibility can retain this declaration after Suk has
                # removed GOLD2. The actual GOLD tag and Mine mapping remain.
                db.execute("INSERT INTO TypeTags VALUES('RESOURCE_GOLD2','CLASS_CSC_TAILORS_SPEC')")
                db.commit()
            with patch.object(m, '_vanilla_sources', return_value=[vanilla]):
                result = m.inspect_resource_stack(Controller(), root / 'out', root, mods, csc_path=csc)
            self.assertTrue(result['verified'])
            self.assertEqual(result['errors'], [])
            self.assertEqual(result['groups']['CLASS_CSC_TAILORS_SPEC'], ['RESOURCE_GOLD'])
            self.assertEqual(result['unused_material_tags']['CLASS_CSC_TAILORS_SPEC'], ['RESOURCE_GOLD2'])
            self.assertTrue(result['warnings'])
            self.assertNotIn('RESOURCE_GOLD2', result['origins'])

    def test_missing_loaded_mapping_or_provider_fails_before_live_census(self):
        for sql, expected in (
            ("DELETE FROM Improvement_ValidResources WHERE ResourceType='RESOURCE_MODDED_SPEC'", 'No valid loaded improvement'),
            ("DELETE FROM TypeTags WHERE Type='RESOURCE_GOLD'", 'Suk Gold replacement'),
            ("DELETE FROM TypeTags WHERE Type='DISTRICT_MODDED_RURAL_REPLACEMENT'", 'Missing BAKERS goods-provider'),
        ):
            with self.subTest(expected=expected), tempfile.TemporaryDirectory(dir=SOURCE.parent) as folder:
                root, vanilla, csc, mods = fixture(folder)
                with closing(sqlite3.connect(root / 'Cache/DebugGameplay.sqlite')) as db:
                    db.execute(sql); db.commit()
                controller = Controller()
                with patch.object(m, '_vanilla_sources', return_value=[vanilla]):
                    with self.assertRaisesRegex(AssertionError, expected):
                        m.inspect_resource_stack(controller, root / 'out', root, mods, csc_path=csc)
                self.assertEqual(controller.calls, [])
                self.assertTrue(json.loads((root / 'out/resource-stack-preflight.json').read_text())['errors'])

    def test_census_is_passive_and_separates_ai_major_ownership(self):
        vm = LuaRuntime()
        lines = []
        vm.globals().print = lines.append
        vm.execute('''
Game={GetCurrentGameTurn=function()return 2 end}
GameInfo={Resources={[0]={ResourceType='RESOURCE_ONE'},[1]={ResourceType='RESOURCE_TWO'}}}
Players={
 [1]={IsMajor=function()return true end,IsHuman=function()return false end},
 [2]={IsMajor=function()return true end,IsHuman=function()return true end},
 [3]={IsMajor=function()return false end,IsHuman=function()return false end}}
local owners={1,2,3,-1};local resources={0,0,1,1}
Map={GetPlotCount=function()return 4 end,GetPlotByIndex=function(i)return{
 GetOwner=function()return owners[i+1]end,GetResourceType=function()return resources[i+1]end}end}
''')
        vm.execute(m._census_code())
        turn, counts = m._parse_census('\n'.join(lines))
        self.assertEqual(turn, 2)
        self.assertEqual(counts['RESOURCE_ONE'], dict(map=2, ai_owned=1))
        self.assertEqual(counts['RESOURCE_TWO'], dict(map=2, ai_owned=0))
        with self.assertRaises(AssertionError):
            m._parse_census('\n'.join(lines[:-1]))


if __name__ == '__main__':
    unittest.main()

