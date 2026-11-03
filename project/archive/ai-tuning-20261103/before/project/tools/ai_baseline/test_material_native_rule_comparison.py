import copy,unittest
import material_native_rule_comparison as m
class ReportTests(unittest.TestCase):
 def fixture(self):
  scope=[dict(plot=1648,quarter='BAKERS',category='base',material_plot=1573)]
  material=dict(plot=1573,resource='RESOURCE_CATTLE',category='base',owner=2,improvement=None,pillaged=False)
  site=dict(plot=1648,quarter='BAKERS',player=2,complete=True,pillaged=False,producer_built=True,materials=[material])
  return scope,site
 def test_harms_in_both_arms_and_missing_resource_identity_remain_visible(self):
  a=dict(loss_attribution=dict(cases=[dict(plot=1,prior_resource='RESOURCE_CATTLE')]))
  b=dict(loss_attribution=dict(cases=[dict(plot=2,prior_resource='RESOURCE_SHEEP'),dict(plot=3)]))
  out=m.loss_union([a,b]);self.assertEqual([x['plot']for x in out],[1,2,3]);self.assertIsNone(out[-1]['resource']);self.assertEqual(set(out[1]['losses']),{'native_rule'})
 def test_native_spec_vocabulary_has_a_real_working_specialty_link(self):
  scope,site=self.fixture();scope[0]['category']='spec';site['materials'][0]['category']='spec';site['materials'][0]['improvement']='IMPROVEMENT_PLANTATION';tile=dict(index=1573,resource=1,neighbors=[1648],base_for=[],spec_for=['BAKERS']);source=dict(production=dict(cities=[dict(tiles=[tile])]))
  resolved=m.reference_scope(1573,'RESOURCE_CATTLE',[dict(sites=[site])],source);self.assertEqual(resolved[0]['category'],'spec');v=m.endpoint_state(dict(resource='RESOURCE_CATTLE'),'RESOURCE_CATTLE',[site],resolved);self.assertEqual(v['working_links'],1);self.assertEqual(v['functioning_links'],1)
 def test_missing_plot_is_unknown_not_a_false_resource_loss(self):
  scope,site=self.fixture();v=m.endpoint_state(None,'RESOURCE_CATTLE',[site],scope);self.assertIsNone(v['resource_present']);self.assertFalse(v['endpoint_plot_observed'])
 def test_retained_owned_but_unimproved_is_not_working_supply(self):
  scope,site=self.fixture();v=m.endpoint_state(dict(resource='RESOURCE_CATTLE',owner=2),'RESOURCE_CATTLE',[site],scope);self.assertTrue(v['resource_present']);self.assertTrue(v['links'][0]['owned_material']);self.assertEqual((v['working_links'],v['functioning_links']),(0,0))
 def test_improved_foreign_or_pillaged_or_unbuilt_producer_gates(self):
  scope,site=self.fixture();site['materials'][0]['improvement']='IMPROVEMENT_PASTURE'
  self.assertEqual(m.endpoint_state(dict(resource='RESOURCE_CATTLE'),'RESOURCE_CATTLE',[site],scope)['functioning_links'],1)
  for location,field,value in(('material','owner',3),('material','pillaged',True),('site','producer_built',False),('site','pillaged',True),('site','complete',False)):
   changed=copy.deepcopy(site);(changed['materials'][0]if location=='material'else changed)[field]=value
   with self.subTest(field=field):self.assertEqual(m.endpoint_state(dict(resource='RESOURCE_CATTLE'),'RESOURCE_CATTLE',[changed],scope)['functioning_links'],0)
 def test_source_disagreement_rejected(self):
  tile=dict(index=1573,resource=1,neighbors=[1648],base_for=['BAKERS'],spec_for=[]);other=copy.deepcopy(tile);other['resource']=2
  with self.assertRaises(AssertionError):m.reference_scope(1573,'RESOURCE_CATTLE',[],dict(production=dict(cities=[dict(tiles=[tile]),dict(tiles=[other])])))


if __name__=='__main__':unittest.main()
