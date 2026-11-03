import copy,unittest
import observer_host as ob
from test_placement_observer_host import CONFIG as BASE, snapshot as empty
CONFIG=dict(BASE,profile=ob.PLACEMENT_POST_PROFILE,privateYieldDefaultValue=1,
            yieldDefinitions={str(BASE['privateYieldIndex']):dict(type='YIELD_CSC_AI_PLACEMENT',DefaultValue=1)})
SPEC=dict(path='C:/game/GameCore_XP2_FinalRelease.dll',
    sha256='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c',
    timestamp=1719431003,image_size=12976128,
    functions=[dict(name=n,rva=v[0],bytes=v[1])for n,v in ob.PLACEMENT_POST_FUNCTIONS.items()])
def snapshot():return dict(empty(),profile=ob.PLACEMENT_POST_PROFILE)
def status():return dict(installed=True,hooks=10,enabled=False,module_path=SPEC['path'],module_size=SPEC['image_size'],loaded_timestamp=SPEC['timestamp'],validated_entry_fingerprints=copy.deepcopy(SPEC['functions']),config=copy.deepcopy(CONFIG),read_only=True)
class PostHostTests(unittest.TestCase):
    def test_exact_ten_only_named_post_profile(self):
        ob.validate_contract(SPEC,CONFIG,10);self.assertEqual(ob.expected_hook_count(CONFIG),10)
        for cfg,count in [(CONFIG,9),(dict(CONFIG,profile=ob.PLACEMENT_PROFILE),10),
                          (dict(CONFIG,profile='generic-ten'),10),(BASE,10)]:
            with self.assertRaises(ValueError):ob.validate_contract(SPEC,cfg,count)
    def test_no_global_normalize_boundary_or_changed_fingerprint(self):
        self.assertNotIn('normalize',ob.PLACEMENT_POST_FUNCTIONS)
        self.assertNotIn('normalize_bonus',ob.PLACEMENT_POST_FUNCTIONS)
        value=copy.deepcopy(SPEC);value['functions'][0]['bytes']='00'*32
        with self.assertRaises(ValueError):ob.validate_contract(value,CONFIG,10)
    def test_actual_native_default1_mapping_is_mandatory(self):
        for cfg in [dict(CONFIG,privateYieldDefaultValue=2),dict(CONFIG,yieldDefinitions={}),
                    dict(CONFIG,yieldDefinitions={'6':dict(type='YIELD_CSC_AI_PLACEMENT',DefaultValue=2)}),
                    dict(CONFIG,yieldDefinitions={'6':dict(type='OTHER',DefaultValue=1)})]:
            with self.assertRaises(ValueError):ob.validate_contract(SPEC,cfg,10)
    def test_exact_install_status_and_profile_mismatch_fail(self):
        ob.validate_status(status(),SPEC,enabled=False,config=CONFIG)
        with self.assertRaises(ValueError):ob.validate_status(status(),SPEC,enabled=False,config=BASE)
        with self.assertRaises(ValueError):ob.validate_status(dict(status(),hooks=9),SPEC,enabled=False,config=CONFIG)
        with self.assertRaises(ValueError):ob.validate_status(status(),SPEC,enabled=False)
    def test_partial_raw_is_accepted_without_inventing_bonus(self):
        value=snapshot();value['stats']['completedPairs']=1
        value['candidates']=[dict(kind='net_value',districtIndex=BASE['districtIndex'],districtValues=[dict(normalizations=[dict(group='wrapper',rawInteger=4,rawInputQ8=None,effectiveBonusQ8=None),dict(group='own_static',rawInteger=None,rawInputQ8=None,effectiveBonusQ8=None)])])]
        self.assertFalse(ob.validate_snapshot(value,config=CONFIG))
        for field in ['rawInteger','rawInputQ8','effectiveBonusQ8']:
            bad=copy.deepcopy(value);bad['candidates'][0]['districtValues'][0]['normalizations'][1][field]=1024
            with self.assertRaises(ValueError):ob.validate_snapshot(bad,config=CONFIG)
    def test_v1_payload_is_never_mislabeled_post(self):
        with self.assertRaises(ValueError):ob.validate_snapshot(empty(),config=CONFIG)
        with self.assertRaises(ValueError):ob.validate_snapshot(snapshot(),config=BASE)
    def test_retained_freeze_once_same_lifecycle(self):
        obj=object.__new__(ob.NativeObserver);obj.spec=SPEC;obj.config=CONFIG;obj.frozen=False;calls=[]
        obj._intent=lambda *a:calls.append(a);obj._wait=lambda *a,**k:dict(status=status(),snapshot=snapshot())
        obj.before_menu();obj.before_menu();self.assertTrue(obj.frozen);self.assertEqual(len(calls),1)
if __name__=='__main__':unittest.main()
