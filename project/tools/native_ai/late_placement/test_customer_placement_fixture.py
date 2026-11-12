"""Reject geometry-only, protected and capacity-starved2.1 fixture leads."""
from copy import deepcopy
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from customer_placement_fixture import qualify_hamburg,native_signal_active


def fixture():
    return dict(turn=202,mutationCommands=0,
        city=dict(player=3,id=393221,name='LOC_CITY_NAME_HAMBURG',hasQuarter=False,hasHarbor=False),
        quarter=dict(type='DISTRICT_CSC_TAILORS_QUARTER',requiresPopulation=True),
        harbor=dict(type='DISTRICT_HARBOR',requiresPopulation=True),
        site=dict(plot=1083,owner=3,city=393221,district=-1,resource=-1,improvement=-1,protected=False,quarterTarget=True),
        suppliers=[dict(plot=1084,owner=3,resourceType='RESOURCE_SHEEP',ready=True)],
        candidates=[dict(plot=1082,owner=3,city=393221,district=-1,resource=-1,
            protected=False,quarterDistance=1,harborTarget=True)])


class CustomerPlacementFixture(unittest.TestCase):
    def test_native_definition_gate_does_not_treat_absent_link_as_active(self):
        signal=dict(nativeSignal=dict(yieldDefinition=dict(type='YIELD_CSC_AI_PLACEMENT',defaultValue=1),
            bias=[dict(item='YIELD_CSC_AI_PLACEMENT',value=25)],
            adjacencies=[{'customer':'DISTRICT_HARBOR','quarter':'DISTRICT_CSC_TAILORS_QUARTER',
                'yield':'YIELD_CSC_AI_PLACEMENT','amount':1,'tilesRequired':1}]))
        self.assertTrue(native_signal_active(signal))
        signal['nativeSignal']['adjacencies']=[]
        self.assertFalse(native_signal_active(signal))

    def test_native_targets_and_loaded_required_slots_are_required(self):
        facts=fixture();city=dict(player=3,city=393221,ui=dict(allowedDistricts=4,zonedDistricts=2))
        result=qualify_hamburg(facts,city)
        self.assertTrue(result['eligible']);self.assertEqual(result['legal_customer_candidates'],[1082])
        for ui in ({},dict(allowedDistricts=4,zonedDistricts=3),dict(allowedDistricts=None,zonedDistricts=2)):
            changed=deepcopy(city);changed['ui']=ui
            self.assertFalse(qualify_hamburg(facts,changed)['eligible'])
        facts['candidates'][0]['harborTarget']=False
        self.assertFalse(qualify_hamburg(facts,city)['eligible']) # Potential geometry alone is insufficient.

    def test_population_free_quarter_does_not_require_a_spurious_second_slot(self):
        facts=fixture();facts['quarter']['requiresPopulation']=False
        city=dict(player=3,city=393221,ui=dict(allowedDistricts=4,zonedDistricts=3))
        result=qualify_hamburg(facts,city)
        self.assertTrue(result['eligible']);self.assertEqual(result['required_slots'],1)

    def test_empty_alternative_precedes_declared_lumber_mill_fallback(self):
        facts=fixture();city=dict(player=3,city=393221,ui=dict(allowedDistricts=4,zonedDistricts=2))
        mill=facts['site'];mill.update(improvement=8,improvementType='IMPROVEMENT_LUMBER_MILL')
        empty=deepcopy(mill);empty.update(plot=1157,improvement=-1,customerPlots=[1082])
        facts['quarterAlternatives']=[mill,empty]
        self.assertEqual(qualify_hamburg(facts,city,allow_lumber_mill=True)['quarter_plot'],1157)
        facts['quarterAlternatives']=[mill]
        self.assertFalse(qualify_hamburg(facts,city)['eligible'])
        self.assertTrue(qualify_hamburg(facts,city,allow_lumber_mill=True)['eligible'])

    def test_protected_or_resource_customer_and_wrong_supplier_are_refused(self):
        city=dict(player=3,city=393221,ui=dict(allowedDistricts=4,zonedDistricts=2))
        for key,value in(('protected',True),('resource',1),('city',123),('quarterDistance',2)):
            facts=fixture();facts['candidates'][0][key]=value
            self.assertFalse(qualify_hamburg(facts,city)['eligible'])
        facts=fixture();facts['suppliers'][0]['resourceType']='RESOURCE_IRON'
        self.assertFalse(qualify_hamburg(facts,city)['eligible'])

    def test_quarter_must_be_empty_unprotected_and_native_legal(self):
        city=dict(player=3,city=393221,ui=dict(allowedDistricts=4,zonedDistricts=2))
        for key,value in(('protected',True),('quarterTarget',False),('district',36),('resource',1),('improvement',0)):
            facts=fixture();facts['site'][key]=value
            self.assertFalse(qualify_hamburg(facts,city)['eligible'])
        facts=fixture();facts['quarter']['requiresPopulation']=None
        with self.assertRaises(AssertionError):qualify_hamburg(facts,city)

    def test_read_only_inspector_compiles(self):
        code=Path(__file__).with_name('hamburg_customer_inspect.lua').read_text()
        LuaRuntime().eval('function(s)assert(loadstring(s))end')(code)


if __name__=='__main__':unittest.main()
