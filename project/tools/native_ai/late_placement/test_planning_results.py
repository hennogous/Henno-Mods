"""Evidence joins must not count offers/captures as constructed districts."""
import json
from pathlib import Path
import tempfile
import unittest
from planning_results import analyse,parse


class PlanningResults(unittest.TestCase):
    def test_choices_yields_and_unbuilt_opportunities_remain_distinct(self):
        with tempfile.TemporaryDirectory()as directory:
            root=Path(directory)
            (root/'source.json').write_text(json.dumps(dict(original_ai=[1])),encoding='utf-8')
            (root/'loaded-district-catalogue.txt').write_text('CSC_DISTRICT_CATALOGUE\t36\tDISTRICT_CSC_BAKERS_QUARTER\n',encoding='utf-8')
            (root/'resource-stack-preflight.json').write_text(json.dumps(dict(groups={
                'CLASS_CSC_BAKERS_BASE':['RESOURCE_WHEAT'],'CLASS_CSC_BAKERS_SPEC':['RESOURCE_HONEY']})),encoding='utf-8')
            (root/'Lua.log').write_text('''CSC_PLANNING_FOUNDATION\tplayer=1\tcity=2\tdistrict=36\tdistrictType=DISTRICT_CSC_BAKERS_QUARTER\tdistrictID=4\tplot=3\tturn=20\tcomplete=false
CSC_PLANNING_FOUNDATION\tplayer=0\tcity=2\tdistrict=36\tdistrictType=DISTRICT_CSC_BAKERS_QUARTER\tdistrictID=4\tplot=3\tturn=20\tcomplete=false
CSC_PLANNING_OWNERSHIP\tplayer=1\tcity=2\tdistrict=36\tplot=9\tturn=30
CSC_PLANNING_OPPORTUNITY\tplayer=1\tcity=2\tdistrict=36\tplot=8\tqualified=true\toffered=true
CSC_PLANNING_OPPORTUNITY\tplayer=1\tcity=2\tdistrict=36\tplot=8\tqualified=true\toffered=true
CSC_QUARTER_WATCH_SITE\tevent=foundation\tplayer=1\tcity=2\tdistrict=36\tplot=3\tbase=1\tspec=1\tmillForecastTotal=4
CSC_DISTRICT_UI_ADJACENCY\tplayer=1\tcity=2\tdistrict=36\tdistrictID=4\tplot=3\tturn=19\tsource=added\tfootprintMatches=true\tYIELD_PRODUCTION=2\tYIELD_CSC_AI_PLACEMENT=1
CSC_PLANNING_MATERIAL_TOTAL\tplayer=1\tquarterPlot=3\tturn=20\tsource=poll\tbase=1\tspec=1\tbaseWorking=1\tspecWorking=0
CSC_PLANNING_MATERIAL_TOTAL\tplayer=1\tquarterPlot=3\tturn=21\tsource=poll\tbase=1\tspec=0\tbaseWorking=1\tspecWorking=0
CSC_PLANNING_MATERIAL_STATE\tplayer=1\tquarter=BAKERS\tquarterPlot=3\tmaterialPlot=5\tpreviousResource=RESOURCE_POTATO\tbase=false\tspec=false\tlostWorking=true\tlostBase=false\tlostSpec=false
CSC_PLANNING_MATERIAL_STATE\tplayer=1\tquarter=BAKERS\tquarterPlot=3\tmaterialPlot=6\tpreviousResource=RESOURCE_WHEAT\tbase=true\tspec=false\tlostWorking=true\tlostBase=false\tlostSpec=false
CSC_AI_QUARTER_COVERAGE turn=20 version=19 player=1 district=36 result={"staged":1,"masked":12}
CSC_AI_QUARTER_COVERAGE turn=20 version=19 player=1 district=36 result={"staged":1,"masked":12}
''',encoding='utf-8')
            choice=dict(kind='district-selection',player=1,city=2,district=36,plot=3,turn=19,
                        sequence=1,totalQ8=96000,scoreStatus='read')
            (root/'economy-savings.ndjson').write_text(json.dumps(choice)+'\n',encoding='utf-8')
            summary=analyse(root)
            quarter=summary['quarter_quality_at_foundation']['BAKERS']
            self.assertEqual(quarter['foundations'],1)
            self.assertEqual(quarter['distinct_positive_offers'],1)
            self.assertEqual(quarter['both'],1)
            district=summary['district_construction']['DISTRICT_CSC_BAKERS_QUARTER']
            self.assertEqual(district['native_choice_total_Q8']['median'],96000)
            self.assertEqual(district['native_choice_age_turns']['median'],1)
            self.assertEqual(district['matched_prior_native_Q8']['n'],0)
            self.assertEqual(district['UI_event_adjacency_joined'],1)
            self.assertEqual(summary['usable_material_exhaustions_by_role'],dict(spec=1))
            self.assertEqual(summary['native_managed_cell_masks'],12)
            self.assertEqual(summary['native_managed_mask_turns'],1)
            self.assertEqual(summary['actual_native_declines'],0)
            self.assertEqual(summary['material_loss_events'],1)
            self.assertEqual(summary['working_supplier_loss_events'],1)
            self.assertEqual(summary['unrelated_compatible_improvement_loss_events'],1)
            rows=json.loads((root/'planning-results.json').read_text(encoding='utf-8'))['constructions']
            self.assertEqual(rows[0]['uiClockDelta'],-1)
            self.assertFalse(rows[0]['sameTurnNativeOrderKnown'])

    def test_parser_keeps_booleans_and_negative_scores(self):
        row=parse('context: CSC_PLANNING_NATIVE_DECLINE\tresult=-262145\tincomplete=false','CSC_PLANNING_')[0]
        self.assertEqual(row['result'],-262145)
        self.assertIs(row['incomplete'],False)


if __name__=='__main__':unittest.main()
