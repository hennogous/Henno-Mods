"""Offline retained-observer lifecycle contract checks; no native/frida import."""
import copy
import unittest
import json
import hashlib
import tempfile
from unittest.mock import patch
from pathlib import Path
from observer_host import NativeObserver,validate_contract,validate_status,validate_snapshot,prove_loaded_module

SPEC={'path':'C:/game/GameCore_XP2_FinalRelease.dll','sha256':'a'*64,'image_size':12976128,'timestamp':1719431003,'functions':[{'name':'CheckForImprovement','rva':0x3e1150,'bytes':'11'*32},{'name':'DecodeTrigger','rva':0x55a680,'bytes':'22'*32}]}
CONFIG={'player':3,'city':655369,'maxPairs':64}
def status(enabled=False):return{'installed':True,'hooks':2,'enabled':enabled,'module_path':SPEC['path'],'module_size':SPEC['image_size'],'loaded_timestamp':SPEC['timestamp'],'validated_entry_fingerprints':SPEC['functions']}
def snapshot(pairs=0,pending=0):return{'read_only':True,'paired':True,'stats':{'completedPairs':pairs},'frozenPendingPairs':pending,'records':[]}


class ObserverHostTests(unittest.TestCase):
    def test_scope_two_entries_and_exact_fingerprints(self):
        validate_contract(SPEC,CONFIG,2)
        for spec,cfg,hooks in [(dict(SPEC,functions=SPEC['functions'][:1]),CONFIG,2),(SPEC,dict(CONFIG,city=1),2),(SPEC,dict(CONFIG,maxPairs=65),2),(SPEC,CONFIG,3)]:
            with self.assertRaises(ValueError):validate_contract(spec,cfg,hooks)

    def test_status_checks_module_fingerprints_and_enable_phase(self):
        validate_status(status(),SPEC,enabled=False)
        for key,value in [('hooks',5),('module_size',1),('loaded_timestamp',0),('enabled',True),('validated_entry_fingerprints',[])]:
            bad=status();bad[key]=value
            with self.assertRaises(ValueError):validate_status(bad,SPEC,enabled=False)

    def test_pair_budget_saturation_is_not_input_failure(self):
        self.assertFalse(validate_snapshot(snapshot(63)))
        self.assertTrue(validate_snapshot(snapshot(64)))
        with self.assertRaises(ValueError):validate_snapshot(snapshot(65))

    def test_before_menu_freezes_once_without_detach_or_native_control(self):
        ob=object.__new__(NativeObserver);ob.frozen=False;ob.spec=SPEC;calls=[]
        ob._intent=lambda *a:calls.append(a)
        ob._wait=lambda *a,**k:{'status':status(False),'snapshot':snapshot()}
        ob.before_menu();ob.before_menu();self.assertTrue(ob.frozen);self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][0],'trace-freeze.request')

    def test_pending_pair_or_missing_freeze_ack_does_not_claim_frozen(self):
        for reply in ({'status':status(False),'snapshot':snapshot(pending=1)},None):
            ob=object.__new__(NativeObserver);ob.frozen=False;ob.spec=SPEC;ob._intent=lambda *a:None
            def wait(*args,**kwargs):
                if reply is None:raise TimeoutError('unconfirmed')
                return reply
            ob._wait=wait
            with self.assertRaises((RuntimeError,TimeoutError)):ob.before_menu()
            self.assertFalse(ob.frozen)

    def test_external_module_proof_joins_held_identity_path_size_and_file_hash(self):
        class Owner:
            identity={'pid':73,'executable_path':'C:/game/CivilizationVI.exe','creation_filetime':123}
            def poll(self):return None
        with tempfile.TemporaryDirectory()as temp:
            folder=Path(temp);dll=folder/'GameCore_XP2_FinalRelease.dll';dll.write_bytes(b'fixture native bytes')
            spec=dict(SPEC,path=str(dll),sha256=hashlib.sha256(dll.read_bytes()).hexdigest())
            row={'ModuleName':dll.name,'FileName':str(dll),'size':spec['image_size'],'base':0x180000000}
            with patch('observer_host.subprocess.check_output',return_value=json.dumps(row)):
                proof=prove_loaded_module(Owner(),spec,folder/'proof.json')
            self.assertEqual(proof['identity'],Owner.identity);self.assertTrue(proof['verified'])
            with patch('observer_host.subprocess.check_output',return_value=json.dumps(dict(row,size=1))):
                with self.assertRaises(RuntimeError):prove_loaded_module(Owner(),spec,folder/'bad-proof.json')

    def test_daemon_contains_no_explicit_live_unload_or_detach(self):
        for name in ('observer_host.py','observer_daemon.py'):
            text=Path(__file__).with_name(name).read_text(encoding='utf-8-sig')
            self.assertNotIn('.detach(',text);self.assertNotIn('.unload(',text)


if __name__=='__main__':unittest.main()
