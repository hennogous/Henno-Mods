"""Evidence joins keep physical links, prior plans and SQL readings separate."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from customer_coordination_results import analyse, physical_summary, district_breakdown


class CoordinationResults(unittest.TestCase):
    def test_capture_does_not_create_another_placement_and_shared_customer_counts_once(self):
        row=dict(player=1,quarter='BAKERS',quarterPlot=10,customerPlot=20,
            customerDistrict='DISTRICT_COMMERCIAL_HUB',cityCenter=False,order='quarter_first',
            exactPriorCustomerFirstLink=False,latestQuarterLayoutMatches=False,
            priorCustomerEconomicOffer=True,privateYieldAtCustomerFoundation=1,
            ownedBaseAtCustomerPlacement=1,roles=['customer','sales'])
        rows=[row,dict(row,player=2),dict(row,quarterPlot=11,order='customer_first')]
        summary=physical_summary(rows)
        self.assertEqual(summary['physical_links'],2)
        self.assertEqual(summary['owner_scoped_links'],3)
        self.assertEqual(summary['order'],dict(quarter_first=1,customer_first=1))
        self.assertEqual(summary['customer_foundations_with_private_yield'],1)
        bytype=district_breakdown(rows,[dict(district=6),dict(district=4)],
            {6:'DISTRICT_COMMERCIAL_HUB',4:'DISTRICT_HARBOR'}, {'DISTRICT_HARBOR'})
        self.assertEqual(bytype['DISTRICT_COMMERCIAL_HUB']['adjacent_district_sites'],1)
        self.assertEqual(bytype['DISTRICT_COMMERCIAL_HUB']['quarter_district_pairs'],2)
        self.assertEqual(bytype['DISTRICT_HARBOR']['adjacent_district_sites'],0)

    def test_both_directions_deduplicate_roles_and_keep_base_and_sql_evidence(self):
        with TemporaryDirectory()as temporary:
            root=Path(temporary)
            edge=dict(player=1,quarter='TAILORS',quarterPlot=10,quarterFoundationTurn=5,
                      neighbourPlot=20,neighbourDistrict=4,neighbourFoundationTurn=12,present=True,role='customer')
            reverse=dict(edge,quarterPlot=11,quarterFoundationTurn=20,neighbourPlot=21,neighbourFoundationTurn=8)
            center=dict(edge,neighbourPlot=1,neighbourDistrict=0,neighbourFoundationTurn=1)
            constructions=[dict(player=1,district=4,plot=20,uiAdjacency={'YIELD_CSC_AI_PLACEMENT':1}),
                           dict(player=1,district=4,plot=21,uiAdjacency={'YIELD_CSC_AI_PLACEMENT':0})]
            (root/'planning-results.json').write_text(json.dumps(dict(constructions=constructions,
                relationship_pairs=[edge,dict(edge,role='sales'),reverse,center])))
            (root/'loaded-district-catalogue.txt').write_text(
                'CSC_DISTRICT_CATALOGUE\t0\tDISTRICT_CITY_CENTER\tfalse\n'
                'CSC_DISTRICT_CATALOGUE\t4\tDISTRICT_HARBOR\ttrue\n'
                'CSC_DISTRICT_CATALOGUE\t43\tDISTRICT_CSC_TAILORS_QUARTER\ttrue\n')
            (root/'Lua.log').write_text(
                'CSC_AI_SPATIAL_BID turn=4 player=1 district=43 plot=10 customerPlot1=20 customerType1=4\n'
                'CSC_AI_CUSTOMER_ECONOMIC_BID turn=11 player=1 district=4 plot=20 deltaQ8=100\n'
                'CSC_AI_CUSTOMER_FUTURE_LINK turn=7 player=1 district=4 plot=21 quarterPlot=11 quarterDistrict=43\n'
                'CSC_PLANNING_MATERIAL_STATE\tplayer=1\tquarterPlot=10\tmaterialPlot=30\tturn=5\tbase=true\towner=1\tdistrict=-1\tworking=true\tcompatible=true\n')
            report=analyse(root);summary=report['summary']
            self.assertEqual(summary['physical_links'],3)
            self.assertEqual(summary['planned_district_links'],2)
            self.assertEqual(summary['order'],{'quarter_first':1,'customer_first':1})
            self.assertEqual(summary['exact_prior_customer_first_links'],1)
            self.assertEqual(summary['latest_quarter_layout_matches'],1)
            self.assertEqual(summary['links_with_prior_economic_offer'],1)
            self.assertEqual(summary['customer_foundations_with_private_yield'],1)
            first=next(r for r in report['links']if r['customerPlot']==20)
            self.assertEqual(first['ownedBaseAtCustomerPlacement'],1)
            self.assertEqual(first['workingBaseAtCustomerPlacement'],1)
            second=next(r for r in report['links']if r['customerPlot']==21)
            self.assertIsNone(second['ownedBaseAtCustomerPlacement'])


if __name__=='__main__':unittest.main()
