import copy,unittest
from material_worker_allocation_audit import allocation_difference,channels_correspond,allocations_stable
class Allocation(unittest.TestCase):
 def data(self):return dict(cities=[dict(player=0,city=1,population=1,plots=[dict(plot=10,owner=0,resource=None,workers=1,private=0,economic={'food':2,'production':1,'culture':0}),dict(plot=11,owner=0,resource='FLAX',workers=0,private=0,economic={'food':2,'production':0,'culture':1})])])
 def test_swap_changes_outputs_without_changing_plot_yields(self):
  b=self.data();a=copy.deepcopy(b);a['cities'][0]['plots'][0]['workers']=0;a['cities'][0]['plots'][1].update(workers=1,private=40)
  d=allocation_difference(b,a)[0];self.assertEqual(d['worked_plot_economic_delta'],dict(food=0,production=-1,culture=1));self.assertTrue(channels_correspond(d['worked_plot_economic_delta'],dict(food=0,production=-.8984375,culture=.90234375)))
 def test_real_input_changes_are_rejected(self):
  b=self.data();a=copy.deepcopy(b);a['cities'][0]['plots'][0]['economic']['food']=3
  with self.assertRaises(AssertionError):allocation_difference(b,a)
 def test_population_and_citizen_creation_are_rejected(self):
  b=self.data();a=copy.deepcopy(b);a['cities'][0]['population']=2
  with self.assertRaises(AssertionError):allocation_difference(b,a)
  a=copy.deepcopy(b);a['cities'][0]['plots'][1]['workers']=1
  with self.assertRaises(AssertionError):allocation_difference(b,a)
 def test_unexplained_city_channel_or_opposite_direction_not_explained(self):
  self.assertFalse(channels_correspond(dict(production=-1),dict(production=.9)))
  self.assertFalse(channels_correspond(dict(production=-1),dict(production=-.9,culture=1)))
  self.assertFalse(channels_correspond(dict(production=-1),dict(production=0)))
 def test_private_refresh_does_not_mean_citizens_moved(self):
  b=self.data();a=copy.deepcopy(b);a['cities'][0]['plots'][1]['private']=160;self.assertTrue(allocations_stable(b,a))
  a['cities'][0]['plots'][0]['workers']=0;a['cities'][0]['plots'][1]['workers']=1;self.assertFalse(allocations_stable(b,a))
if __name__=='__main__':unittest.main()
