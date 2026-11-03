"""Explicit Granary profile validation; no native query, Frida or subprocess."""
import copy
import unittest

from observer_host import GRANARY_FUNCTIONS, GRANARY_PROFILE, NativeObserver
from observer_host import validate_contract, validate_status, validate_snapshot

SPEC={'path':'C:/game/GameCore_XP2_FinalRelease.dll',
      'sha256':'324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c',
      'image_size':12976128,'timestamp':1719431003,
      'functions':[dict(name=name,rva=rva,bytes=raw)for name,(rva,raw)in GRANARY_FUNCTIONS.items()]}
CONFIG=dict(profile=GRANARY_PROFILE,player=3,city=196610,buildingIndex=3,
            buildingType='BUILDING_GRANARY',buildingIndexLimit=512,mappingVerified=True,maxPairs=64)

def status(enabled=False):
    return dict(installed=True,hooks=2,enabled=enabled,module_path=SPEC['path'],
                module_size=SPEC['image_size'],loaded_timestamp=SPEC['timestamp'],
                validated_entry_fingerprints=copy.deepcopy(SPEC['functions']),config=copy.deepcopy(CONFIG),read_only=True)

def snapshot(pairs=0,pending=0):
    return dict(profile=GRANARY_PROFILE,read_only=True,paired=True,
                stats=dict(completedPairs=pairs,errors=0,identityChanges=0),
                records=[dict(kind='GetBestBuilding')for _ in range(pairs)],
                pendingPairs=pending,frozenPendingPairs=0)


class BuildingObserverHostTests(unittest.TestCase):
    def test_exact_reviewed_two_hook_profile(self):
        validate_contract(SPEC,CONFIG,2)
        for change in (dict(profile='unknown'),dict(city=655369),dict(buildingIndex=4),
                       dict(buildingType='BUILDING_MONUMENT'),dict(maxPairs=65),
                       dict(mappingVerified=False),dict(buildingIndexLimit=3),
                       dict(buildingIndexLimit=4097),dict(buildingIndexLimit=True)):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):validate_contract(SPEC,dict(CONFIG,**change),2)

    def test_hook_name_rva_fingerprint_and_native_build_are_exact(self):
        mutations=(lambda s:s['functions'][0].update(name='OtherHook'),
                   lambda s:s['functions'][0].update(rva=0x3e4711),
                   lambda s:s['functions'][0].update(bytes='11'*32),
                   lambda s:s.update(sha256='b'*64),lambda s:s.update(timestamp=1),
                   lambda s:s.update(image_size=1))
        for mutate in mutations:
            spec=copy.deepcopy(SPEC);mutate(spec)
            with self.assertRaises(ValueError):validate_contract(spec,CONFIG,2)

    def test_granary_spec_cannot_use_legacy_scope_or_status_without_config(self):
        with self.assertRaises(ValueError):validate_contract(SPEC,dict(CONFIG,profile=None),2)
        with self.assertRaises(ValueError):validate_status(status(),SPEC,enabled=False)

    def test_status_requires_exact_config_and_read_only(self):
        validate_status(status(),SPEC,enabled=False,config=CONFIG)
        for mutation in ('config','read_only','enabled','validated_entry_fingerprints'):
            value=status()
            if mutation=='config':value['config']['city']=196611
            elif mutation=='read_only':value[mutation]=False
            elif mutation=='enabled':value[mutation]=True
            else:value[mutation]=[]
            with self.subTest(field=mutation):
                with self.assertRaises(ValueError):validate_status(value,SPEC,enabled=False,config=CONFIG)

    def test_snapshot_profile_counts_pending_budget_and_boundaries(self):
        self.assertFalse(validate_snapshot(snapshot(63,1),config=CONFIG))
        self.assertTrue(validate_snapshot(snapshot(64),config=CONFIG))
        bad=[dict(snapshot(),profile='unknown'),dict(snapshot(),profile=None),
             dict(snapshot(1),records=[]),snapshot(64,1),dict(snapshot(),pendingPairs=-1),
             dict(snapshot(1),records=[dict(kind='UnknownHook')])]
        for value in bad:
            with self.assertRaises(ValueError):validate_snapshot(value,config=CONFIG)
        with self.assertRaises(ValueError):validate_snapshot(snapshot())

    def test_legacy_default_scope_stays_accepted_and_unknown_profile_rejected(self):
        legacy_spec=dict(SPEC,functions=[dict(name='CheckForImprovement',rva=0x3e1150,bytes='11'*32),
                                        dict(name='DecodeTrigger',rva=0x55a680,bytes='22'*32)])
        legacy=dict(player=3,city=655369,maxPairs=64)
        validate_contract(legacy_spec,legacy,2)
        with self.assertRaises(ValueError):validate_contract(legacy_spec,dict(legacy,profile='unknown'),2)
        with self.assertRaises(ValueError):validate_contract(legacy_spec,CONFIG,2)

    def test_new_profile_freeze_still_requires_zero_pending_and_no_detach(self):
        observer=object.__new__(NativeObserver)
        observer.frozen=False;observer.spec=SPEC;observer.config=CONFIG;calls=[]
        observer._intent=lambda *args:calls.append(args)
        observer._wait=lambda *args,**kwargs:dict(status=status(),snapshot=snapshot())
        observer.before_menu();observer.before_menu()
        self.assertTrue(observer.frozen);self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][0],'trace-freeze.request')


if __name__=='__main__':unittest.main()
