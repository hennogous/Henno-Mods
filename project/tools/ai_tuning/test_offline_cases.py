"""Focused integrity checks for archived customer-option comparisons."""
import unittest
from offline_cases import customer_comparisons

def option(player,city,plot,adjacent,gold=None):
    yields={'YIELD_CSC_AI_PLACEMENT':10 if adjacent else 0}
    if gold is not None: yields['YIELD_GOLD']=gold
    return dict(player=player,city=city,district='DISTRICT_HARBOR',plot=plot,
                adjacent_quarters=[99] if adjacent else [],sole_base=False,adjacency=yields)

class ComparisonIntegrity(unittest.TestCase):
    def test_city_ids_are_player_local(self):
        rows=[option(1,7,10,True,0),option(2,7,11,False,4)]
        self.assertEqual(customer_comparisons(rows),[])
    def test_district_types_must_match(self):
        rows=[option(1,7,10,True,0),option(1,7,11,False,4)]
        rows[1]['district']='DISTRICT_COMMERCIAL_HUB'
        self.assertEqual(customer_comparisons(rows),[])
    def test_missing_is_not_zero(self):
        result=customer_comparisons([option(1,7,10,True),option(1,7,11,False,4)])[0]
        self.assertEqual(result['gold_comparison'],'unobserved')
        self.assertIn('YIELD_GOLD',result['unobserved_yields'])
        self.assertIsNone(result['chosen_option'])
    def test_real_and_private_not_added(self):
        result=customer_comparisons([option(1,7,10,True,0),option(1,7,11,False,3)])[0]
        self.assertEqual(result['alternative_minus_adjacent_real_yields'],{'YIELD_GOLD':3})
        self.assertEqual(result['private_values'],{'adjacent':10,'alternative':0})
    def test_duplicate_option_is_error(self):
        row=option(1,7,10,True,0)
        with self.assertRaises(ValueError): customer_comparisons([row,row])
if __name__=='__main__': unittest.main()
