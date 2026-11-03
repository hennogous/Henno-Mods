"""Profile rejection/lifecycle checks with inert payloads, no native actions."""
import copy
import unittest
import observer_host as ob

CONFIG=dict(profile=ob.PLACEMENT_PROFILE, player=3, city=131073,
    districtType='DISTRICT_CSC_BAKERS_QUARTER', mappingVerified=True,
    districtIndex=11, districtIndexLimit=60, privateYieldIndex=6, yieldIndexLimit=8,
    mapWidth=74,mapHeight=46,maxPairs=64,maxChoices=32,maxRows=64,maxScopeDepth=16,
    maxThreads=8,maxNormalizations=512,maxValuesPerNet=4,maxCallbacks=1000000,maxTrackedMs=300000)
SPEC=dict(path='C:/game/GameCore_XP2_FinalRelease.dll',
    sha256='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c',
    timestamp=1719431003,image_size=12976128,
    functions=[dict(name=n,rva=v[0],bytes=v[1]) for n,v in ob.PLACEMENT_FUNCTIONS.items()])

def status():
    return dict(installed=True,hooks=9,enabled=False,module_path=SPEC['path'],
        module_size=SPEC['image_size'],loaded_timestamp=SPEC['timestamp'],
        validated_entry_fingerprints=copy.deepcopy(SPEC['functions']),
        config=copy.deepcopy(CONFIG),read_only=True)

def snapshot():
    return dict(profile=ob.PLACEMENT_PROFILE,read_only=True,paired=True,saturated=False,
        stats=dict(callbacks=0,completedPairs=0,completedCandidatesTotal=0,errors=0,
                   identityChanges=0,revisionsNotRetained=0,dropped=0,elapsedTrackedMs=0),
        candidates=[],evaluations=[],choices=[],reservations=[],pendingPairs=0,frozenPendingPairs=0)

class PlacementHostTests(unittest.TestCase):
    def test_exact_named_profile_accepts_nine_and_no_generic_nine(self):
        ob.validate_contract(SPEC,CONFIG,9)
        self.assertEqual(ob.expected_hook_count(CONFIG),9)
        self.assertEqual(ob.expected_hook_count({}),2)
        for cfg,hooks in [(CONFIG,2),(dict(CONFIG,profile=None),9),
                          (dict(CONFIG,profile='generic-nine'),9),
                          (dict(player=3,city=655369,maxPairs=64),9)]:
            with self.assertRaises(ValueError):ob.validate_contract(SPEC,cfg,hooks)

    def test_address_bytes_count_build_are_fixed(self):
        changes=[lambda s:s['functions'][0].update(rva=1),
                 lambda s:s['functions'][0].update(bytes='00'*32),
                 lambda s:s['functions'][0].update(bytes=s['functions'][0]['bytes'][:48]),
                 lambda s:s['functions'][0].update(name='unknown'),
                 lambda s:s['functions'].append(copy.deepcopy(s['functions'][0])),
                 lambda s:s['functions'].pop(),
                 lambda s:s.update(sha256='0'*64),lambda s:s.update(timestamp=0),
                 lambda s:s.update(image_size=0)]
        for change in changes:
            value=copy.deepcopy(SPEC);change(value)
            with self.assertRaises(ValueError):ob.validate_contract(value,CONFIG,9)

    def test_mapping_and_bounds_fail_closed(self):
        for key,value in [('player',0),('city',131074),('mappingVerified',1),
                ('districtIndex',True),('districtIndexLimit',0),('districtIndex',60),
                ('privateYieldIndex',8),('yieldIndexLimit',65),('maxPairs',65),
                ('maxNormalizations',513),('maxCallbacks',1000001),('maxThreads',9)]:
            with self.subTest(key=key,value=value):
                with self.assertRaises(ValueError):ob.validate_contract(SPEC,dict(CONFIG,**{key:value}),9)

    def test_install_status_requires_identity_and_explicit_scope(self):
        ob.validate_status(status(),SPEC,enabled=False,config=CONFIG)
        with self.assertRaises(ValueError):ob.validate_status(status(),SPEC,enabled=False)
        for key,value in [('hooks',2),('enabled',True),('read_only',False),('module_path','elsewhere'),
                          ('module_size',1),('loaded_timestamp',1),('config',{}),('validated_entry_fingerprints',[])]:
            with self.assertRaises(ValueError):ob.validate_status(dict(status(),**{key:value}),SPEC,enabled=False,config=CONFIG)

    def test_payload_counts_nesting_and_pending_are_independently_bounded(self):
        self.assertFalse(ob.validate_snapshot(snapshot(),config=CONFIG))
        self.assertTrue(ob.validate_snapshot(dict(snapshot(),saturated=True),config=CONFIG))
        for key,limit in [('candidates',64),('evaluations',64),('choices',32),('reservations',32)]:
            value=snapshot();value[key]=[{}]*(limit+1)
            with self.assertRaises(ValueError):ob.validate_snapshot(value,config=CONFIG)
        value=snapshot();value['stats']['completedPairs']=1
        with self.assertRaises(ValueError):ob.validate_snapshot(value,config=CONFIG)
        for key in ['callbacks','completedPairs','errors']:
            value=snapshot();value['stats'][key]=True
            with self.assertRaises(ValueError):ob.validate_snapshot(value,config=CONFIG)
        for count in [-1,129,True]:
            with self.assertRaises(ValueError):ob.validate_snapshot(dict(snapshot(),pendingPairs=count),config=CONFIG)
        for nested in [[{}]*5,[{'normalizations':[{}]*513}]]:
            value=snapshot();value['stats']['completedPairs']=1
            value['candidates']=[dict(kind='net_value',districtIndex=11,districtValues=nested)]
            with self.assertRaises(ValueError):ob.validate_snapshot(value,config=CONFIG)

    def test_missing_mismatched_profile_or_read_only_fails(self):
        for value,cfg in [(snapshot(),None),(dict(snapshot(),profile=None),CONFIG),
                          (dict(snapshot(),read_only=False),CONFIG),
                          (dict(snapshot(),paired=False),CONFIG)]:
            with self.assertRaises(ValueError):ob.validate_snapshot(value,config=cfg)

    def test_freeze_still_inert_once_pending_fails_without_claim(self):
        for pending in [0,1]:
            obj=object.__new__(ob.NativeObserver);obj.frozen=False;obj.spec=SPEC;obj.config=CONFIG;calls=[]
            obj._intent=lambda *a:calls.append(a)
            obj._wait=lambda *a,**k:dict(status=status(),snapshot=dict(snapshot(),frozenPendingPairs=pending))
            if pending:
                with self.assertRaises(RuntimeError):obj.before_menu()
                self.assertFalse(obj.frozen)
            else:
                obj.before_menu();obj.before_menu();self.assertTrue(obj.frozen);self.assertEqual(len(calls),1)

if __name__=='__main__':unittest.main()
