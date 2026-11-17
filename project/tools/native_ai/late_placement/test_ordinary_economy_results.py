"""Economic-component receipt joins must preserve packet identity and counters."""
import unittest
from ordinary_economy_results import customer_delivery


class EconomicDelivery(unittest.TestCase):
    def test_signed_component_joins_correct_version_and_repeated_counter_is_not_added(self):
        result=customer_delivery('''
CSC_AI_CUSTOMER_ECONOMIC_BID turn=8 player=2 city=3 district=6 plot=9 deltaQ8=-256
CSC_AI_BAKERS_DISTRICTS turn=8 version=10 players=5
CSC_AI_CUSTOMER_RECEIPT turn=9 version=9 player=2 city=3 district=6 plot=9 result={"staged":1,"writes":99}
CSC_AI_CUSTOMER_RECEIPT turn=9 version=10 player=2 city=3 district=6 plot=9 result={"staged":1,"scoreAttempts":2,"writes":1,"siteWins":0}
CSC_AI_CUSTOMER_RECEIPT turn=10 version=10 player=2 city=3 district=6 plot=9 result={"staged":1,"scoreAttempts":3,"writes":2,"siteWins":1}
''',[dict(turn=7,player=2,city=3,district=6,plot=9),
     dict(turn=12,player=2,city=3,district=6,plot=9)])
        self.assertEqual(result['negative'],1)
        self.assertEqual(result['receipt_windows'],1)
        self.assertEqual(result['score_writes'],2)
        self.assertEqual(result['score_attempts'],3)
        self.assertEqual(result['site_win_windows'],1)
        self.assertEqual(len(result['foundations_on_previously_proposed_targets']),1)
        self.assertEqual(result['component_utility']['mean'],-1)

    def test_unpublished_proposal_and_failed_readback_do_not_become_accepted(self):
        result=customer_delivery('''
CSC_AI_CUSTOMER_ECONOMIC_BID turn=7 player=2 city=3 district=6 plot=8 deltaQ8=512
CSC_AI_CUSTOMER_ECONOMIC_BID turn=8 player=2 city=3 district=6 plot=9 deltaQ8=256
CSC_AI_BAKERS_DISTRICTS turn=8 version=10 players=5
CSC_AI_CUSTOMER_RECEIPT turn=9 version=10 player=2 city=3 district=6 plot=9 result={"readbackError":true}
''',[])
        self.assertEqual(result['proposals'],2)
        self.assertEqual(result['readback_errors'],1)
        self.assertEqual(result['receipt_windows'],0)
        self.assertEqual(result['staged_windows'],0)


if __name__=='__main__':unittest.main()
