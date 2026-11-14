"""Reject wrong-sized, leaking or incomplete observed native payouts."""
import unittest
from material_coverage_fixture import DELTAS,FIELDS,qualify_rows


class MaterialPayoutObservations(unittest.TestCase):
    def records(self):
        baseline=dict(turn=250,windFood=2,cafeFood=3,workshopCulture=4)
        rows={name:dict(turn=250,**{key:baseline[key]+delta for key,delta in zip(FIELDS,values)})
              for name,values in DELTAS.items()}
        return baseline,rows

    def test_qualifies_only_the_recipient_specific_increment(self):
        baseline,rows=self.records()
        result=qualify_rows(baseline,rows)
        self.assertEqual(result['deltas']['maple'],[0,1,0])
        self.assertFalse(result['ai_outcome'])

    def test_rejects_binary_inflation_and_wrong_recipient_leakage(self):
        for phase,key,extra in [('maple','cafeFood',31),('bamboo','windFood',1),('unmapped','cafeFood',1)]:
            baseline,rows=self.records();rows[phase][key]+=extra
            with self.assertRaises(RuntimeError):qualify_rows(baseline,rows)

    def test_missing_or_different_clock_is_not_a_complete_experiment(self):
        baseline,rows=self.records();del rows['farm']
        with self.assertRaises(RuntimeError):qualify_rows(baseline,rows)
        baseline,rows=self.records();rows['bamboo']['turn']=251
        with self.assertRaises(RuntimeError):qualify_rows(baseline,rows)


if __name__=='__main__':unittest.main()
