"""Opportunity denominators require positive sets and an unambiguous clock."""
import unittest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from customer_opportunity_results import candidate_state,classify,analyse


class CustomerOpportunities(unittest.TestCase):
    def test_captured_physical_site_counts_once_with_original_choice(self):
        with TemporaryDirectory(dir=Path(__file__).parent)as temporary:
            root=Path(temporary)
            data={'session-closed.json':dict(verified=True,native_exit_code=0),
                  'loaded-native-customer-database.json':dict(links=[dict(DistrictType='DISTRICT_COMMERCIAL_HUB')]),
                  'planning-results.json':dict(constructions=[dict(player=1,city=7,district=6,
                    districtType='DISTRICT_COMMERCIAL_HUB',plot=20,turn=17,
                    nativeChoice=dict(player=1,city=7,district=6,plot=20,turn=16)),
                    dict(player=2,city=7,district=6,districtType='DISTRICT_COMMERCIAL_HUB',plot=20,turn=40)])}
            for name,value in data.items():(root/name).write_text(json.dumps(value))
            (root/'Lua.log').write_text('''CSC_CUSTOMER_WATCH_GROUP turn=16 player=1 city=7 district=6 reference=10 linked=20:2:1 ordinary=10:3:0
CSC_CUSTOMER_WATCH_CLOCK turn=16 player=1 groups=1
CSC_PLANNING_RELATION\tplayer=1\tneighbourPlot=20\tneighbourDistrict=6\tneighbourFoundationTurn=17\tfoundationOrder=quarterFirst\tquarter=BAKERS
CSC_CUSTOMER_WATCH_FINISH records=4 faults=0 dropped=0
''')
            result=analyse(root)['by_type']['DISTRICT_COMMERCIAL_HUB']
            self.assertEqual(result['physical_customer_sites'],1)
            self.assertEqual(result['founded_with_observed_competing_sites'],1)
            self.assertEqual(result['selected_linked_when_comparable'],1)
            self.assertEqual(result['physically_connected_when_comparable'],1)

    def test_changed_sets_persist_and_missing_clocks_remain_unknown(self):
        log='''CSC_CUSTOMER_WATCH_GROUP turn=150 player=5 city=7 district=6 reference=10 linked=20:2.000000:1 ordinary=10:3.000000:0
CSC_CUSTOMER_WATCH_CLOCK turn=150 player=5 groups=1
CSC_CUSTOMER_WATCH_CLOCK turn=151 player=5 groups=1
'''
        history,clocks=candidate_state(log)
        choice=dict(player=5,city=7,district=6,plot=20,turn=151)
        result=classify(choice,history,clocks)
        self.assertEqual(result['status'],'comparable');self.assertTrue(result['selected_linked'])
        self.assertEqual(result['best_ordinary_adjacency'],3)
        choice['turn']=152
        self.assertEqual(classify(choice,history,clocks)['status'],'publication_clock_unknown_or_ambiguous')

    def test_disappearance_and_singleton_do_not_inflate_comparable_count(self):
        log='''CSC_CUSTOMER_WATCH_GROUP turn=10 player=1 city=7 district=4 reference=30 linked=30:2.000000:1 ordinary=
CSC_CUSTOMER_WATCH_CLOCK turn=10 player=1 groups=1
CSC_CUSTOMER_WATCH_REMOVED turn=11 scope=1:7:4
CSC_CUSTOMER_WATCH_CLOCK turn=11 player=1 groups=0
'''
        history,clocks=candidate_state(log)
        choice=dict(player=1,city=7,district=4,plot=30,turn=10)
        self.assertEqual(classify(choice,history,clocks)['status'],'linked_only')
        choice['turn']=11
        self.assertEqual(classify(choice,history,clocks)['status'],'no_positive_group_observation')
        self.assertEqual(classify(None,history,clocks)['status'],'native_choice_unobserved')


if __name__=='__main__':unittest.main()
