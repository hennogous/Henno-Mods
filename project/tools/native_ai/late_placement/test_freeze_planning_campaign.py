"""The fresh-game package includes reviewed SQL without importing unrelated WIP."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from freeze_planning_campaign import freeze,register_material_transactions,register_economy_contract


class FreezeCoverage(unittest.TestCase):
    def test_economic_actions_keep_criteria_and_register_shared_schema_and_routes(self):
        specs=json.loads((Path(__file__).resolve().parents[4]/'project/modbuddy/CivSupplyChains.actions.json').read_text(encoding='utf-8'))['blocks']['inGameActions']
        with tempfile.TemporaryDirectory()as directory:
            package=Path(directory)
            (package/'mod.modinfo').write_text('''<Mod id="accepted"><Dependencies><Mod id="CE"/></Dependencies>
<InGameActions><UpdateDatabase id="CSC_Q_BAKERS_GOLD"><Criteria>Gold</Criteria>
<File>old.sql</File></UpdateDatabase></InGameActions><Files/></Mod>''')
            copied=register_economy_contract(package,specs,lambda p:('committed '+p).encode())
            root=ET.parse(package/'mod.modinfo').getroot();actions=root.find('InGameActions')
            gold=next(a for a in actions if a.get('id')=='CSC_Q_BAKERS_GOLD')
            self.assertEqual(gold.findtext('Criteria'),'Gold')
            self.assertEqual(root.find('Dependencies/Mod').get('id'),'CE')
            declared={f.text for f in root.find('Files')}
            self.assertIn('Data/CSC_BuildingTransactionSchema.sql',declared)
            self.assertIn('Data/CSC_TradeRouteSchema.sql',declared)
            self.assertIn('Lua_UI/TradeRoutes/CSC_TradeRouteCore.lua',declared)
            self.assertEqual(next(a for a in actions if a.get('id')=='CSC_BuildingTransactionProcessor').findtext('Properties/LoadOrder'),'2500')
            self.assertEqual(next(a for a in actions if a.get('id')=='CSC_TradeRouteProcessor').findtext('Properties/LoadOrder'),'9999000')
            self.assertEqual(set(copied),declared)
            self.assertTrue(all((package/p).is_file()for p in declared))

    def test_reviewed_runtime_files_and_action_are_deployed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'base';source=root/'source';out=root/'out'
            (base/'CE').mkdir(parents=True);(base/'CSC/Data').mkdir(parents=True)
            (base/'CSC/Data/unrelated.sql').write_text('accepted')
            (base/'CSC/mod.modinfo').write_text('''<Mod id="accepted">
<InGameActions><UpdateDatabase id="CSC_AI_Connectors"><Criteria>CE</Criteria>
<File>Data/CSC_AI_Connectors.sql</File></UpdateDatabase></InGameActions>
<Files><File>Data/CSC_AI_Connectors.sql</File></Files></Mod>''')
            for name in ('Lua_UI/AI/model.lua','Lua_UI/Adjacencies/CSC_AdjacencyUI.lua',
                         'Data/CSC_AI_Connectors.sql','Data/CSC_MaterialTransactions.sql',
                         'Data/unrelated.sql'):
                path=source/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(name)
            freeze(base,source,out)
            self.assertEqual((out/'CSC/Data/unrelated.sql').read_text(),'accepted')
            tree=ET.parse(out/'CSC/mod.modinfo');actions=tree.find('InGameActions')
            action=next(a for a in actions if a.get('id')=='CSC_MaterialTransactions')
            self.assertEqual(action.findtext('Properties/LoadOrder'),'800010')
            self.assertIsNone(action.find('Criteria'))
            self.assertEqual(next(a for a in actions if a.get('id')=='CSC_AI_Connectors').findtext('Criteria'),'CE')
            self.assertIn('Data/CSC_MaterialTransactions.sql',[f.text for f in tree.find('Files')])
            modules=next(a for a in actions if a.get('id')=='CSC_AI_PlacementModules')
            self.assertEqual([f.text for f in modules.findall('File')],['Lua_UI/AI/model.lua'])
            self.assertIn('Lua_UI/AI/model.lua',[f.text for f in tree.find('Files')])
            register_material_transactions(out/'CSC')
            self.assertEqual(len([a for a in ET.parse(out/'CSC/mod.modinfo').find('InGameActions')
                                  if a.get('id')=='CSC_MaterialTransactions']),1)
            record=json.loads((out/'freeze.json').read_text())
            self.assertEqual(len(record['overlays']),4)
            self.assertEqual(len(record['runtime_manifest_sha256']),64)


if __name__=='__main__':unittest.main()
