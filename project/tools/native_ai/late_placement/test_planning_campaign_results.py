"""Offline financial evidence must distinguish spending, intentions and ordering."""
import unittest
from planning_campaign_results import financial, stock_district


class FinancialTests(unittest.TestCase):
    def test_cl_urban_and_rural_are_not_stock_calibration_districts(self):
        for kind in ('DISTRICT_COREEXPANSIONA','DISTRICT_RURALCOMMUNITYB',
                     'DISTRICT_COREX_GYOSON','DISTRICT_CSC_BAKERS_QUARTER'):
            self.assertFalse(stock_district(kind))
        for kind in ('DISTRICT_HANSA','DISTRICT_ROYAL_NAVY_DOCKYARD','DISTRICT_WONDER'):
            self.assertTrue(stock_district(kind))

    def payment(self):
        return dict(kind='purchase-debit-return',player=2,plot=9,turn=10,
                    measuredDeltaQ8=-6400,deltaMatched=True,
                    ownerAfter=0,ownerMatchesRequest=False)

    def test_same_clock_context_and_invalid_native_owner_are_not_proof(self):
        payment=self.payment()
        context=dict(player=2,plot=9,turn=10,owner=2,base=True,spec=False,quarterPlots=[11])
        result=financial([payment],[context],{42,43})
        self.assertEqual(result['paid'],1)
        self.assertEqual(result['gold'],25)
        self.assertEqual(result['later_owner_confirmed'],0)
        self.assertEqual(result['later_adjacent_material_payments'],0)
        context['turn']=11
        result=financial([payment],[context],{42,43})
        self.assertEqual(result['later_owner_confirmed'],1)
        self.assertEqual(result['later_adjacent_material_payments'],1)
        self.assertEqual(result['quarter_site_payments'],0)

    def test_only_paid_fresh_lineage_counts_as_quarter_purchase(self):
        requested=dict(kind='targeted-request-built',player=2,plot=9,turn=9,
                       lineage=dict(known=True,selection=dict(district=42)))
        self.assertEqual(financial([requested],[],{42})['quarter_site_payments'],0)
        payment=self.payment();payment['lineage']=requested['lineage']
        self.assertEqual(financial([requested,payment],[],{42})['quarter_site_payments'],1)

    def test_reacquisition_does_not_replace_contradictory_first_later_owner(self):
        first=dict(player=2,plot=9,turn=11,owner=3,base=False,spec=False,quarterPlots=[])
        later=dict(first,turn=12,owner=2)
        self.assertEqual(financial([self.payment()],[first,later],{42})['later_owner_confirmed'],0)

    def test_category_funds_are_separate_from_actual_treasury(self):
        check=dict(kind='targeted-savings',passesPlotFund=False,passesCombinedFunds=False,
                   treasuryQ8=25600,gold=25,plotQ8=512,savingWeights=[3,4,1,1])
        result=financial([check],[],{42})
        self.assertEqual(result['category_fail_with_enough_treasury'],1)
        self.assertEqual(result['targeted_pass'],0)
        self.assertEqual(result['max_plot_fund'],2)


if __name__=='__main__':unittest.main()
