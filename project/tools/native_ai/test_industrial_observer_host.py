"""Strict bounded IZ profile and retained lifecycle; no native actions."""
import copy
import unittest

from observer_host import INDUSTRIAL_FUNCTIONS, INDUSTRIAL_PROFILE, NativeObserver
from observer_host import expected_hook_count, validate_contract, validate_status, validate_snapshot

SPEC = dict(path='C:/game/GameCore_XP2_FinalRelease.dll',
            sha256='324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c',
            image_size=12976128, timestamp=1719431003,
            functions=[dict(name=n, rva=r, bytes=b) for n, (r, b) in INDUSTRIAL_FUNCTIONS.items()])
CONFIG = dict(profile=INDUSTRIAL_PROFILE, targets=[dict(player=4, city=262147), dict(player=2, city=589832)],
              workshopIndex=2, factoryIndex=4, buildingIndexLimit=8,
              workshopType='BUILDING_WORKSHOP', factoryType='BUILDING_FACTORY', mappingVerified=True,
              maxPairs=64, maxCallbacks=10000, maxRows=64, maxThreads=8, maxScopeDepth=16)


def status(enabled=False):
    return dict(installed=True, hooks=4, enabled=enabled, module_path=SPEC['path'],
                module_size=SPEC['image_size'], loaded_timestamp=SPEC['timestamp'],
                validated_entry_fingerprints=copy.deepcopy(SPEC['functions']),
                config=copy.deepcopy(CONFIG), read_only=True)


def snapshot(pairs=0, pending=0):
    return dict(profile=INDUSTRIAL_PROFILE, read_only=True, paired=True, enabled=True, saturated=False,
                stats=dict(callbacks=0, completedPairs=pairs, errors=0, identityChanges=0, budgetSuppressed=0),
                records=[dict(kind='GetBestBuilding', entry=dict(identity=dict(owner=4, city=262147))) for _ in range(pairs)],
                pendingPairs=pending, frozenPendingPairs=0)


class IndustrialObserverHostTests(unittest.TestCase):
    def test_named_exact_four_hook_profile(self):
        self.assertEqual(expected_hook_count(CONFIG), 4)
        validate_contract(SPEC, CONFIG, 4)
        single = dict(CONFIG, targets=[CONFIG['targets'][0]])
        validate_contract(SPEC, single, 4)
        for changed in [dict(mappingVerified=False), dict(maxCallbacks=10001), dict(maxPairs=65),
                        dict(buildingIndexLimit=True), dict(factoryIndex=2), dict(factoryIndex=8),
                        dict(workshopType='BUILDING_OTHER'), dict(targets=[]),
                        dict(targets=[dict(player=0, city=1)]), dict(targets=[dict(player=True, city=1)]),
                        dict(targets=[dict(player=1, city=-1)]), dict(targets=[dict(player=1, city=1.5)]),
                        dict(targets=[dict(player=1, city=1)] * 2), dict(targets=[dict(player=p, city=p) for p in [1, 2, 3]])]:
            with self.subTest(changed=changed):
                with self.assertRaises(ValueError):
                    validate_contract(SPEC, dict(CONFIG, **changed), 4)

    def test_build_hookset_and_fingerprints_are_pinned(self):
        for mutate in [lambda s: s['functions'][0].update(rva=1), lambda s: s['functions'][0].update(bytes='00' * 32),
                       lambda s: s['functions'][0].update(name='Other'), lambda s: s.update(sha256='1' * 64),
                       lambda s: s.update(timestamp=1), lambda s: s.update(image_size=1), lambda s: s.update(path='')]:
            value = copy.deepcopy(SPEC)
            mutate(value)
            with self.assertRaises(ValueError):
                validate_contract(value, CONFIG, 4)
        for count in [True, 2, 5]:
            with self.assertRaises(ValueError):
                validate_contract(SPEC, CONFIG, count)

    def test_status_requires_exact_scope_and_explicit_profile(self):
        validate_status(status(), SPEC, enabled=False, config=CONFIG)
        with self.assertRaises(ValueError):
            validate_status(status(), SPEC, enabled=False)
        for key, value in [('hooks', 2), ('enabled', True), ('read_only', False), ('config', {})]:
            result = status()
            result[key] = value
            with self.assertRaises(ValueError):
                validate_status(result, SPEC, enabled=False, config=CONFIG)

    def test_snapshot_type_scope_pair_and_callback_budgets(self):
        self.assertFalse(validate_snapshot(snapshot(63, 1), config=CONFIG))
        self.assertTrue(validate_snapshot(snapshot(64), config=CONFIG))
        second = snapshot(1)
        second['records'][0]['entry']['identity'] = dict(owner=2, city=589832)
        validate_snapshot(second, config=CONFIG)
        wrong = snapshot(1)
        wrong['records'][0]['entry']['identity'] = dict(owner=4, city=589832)
        callback = snapshot()
        callback['stats']['callbacks'] = 10000
        for bad in [wrong, callback, snapshot(64, 1), dict(snapshot(1), records=[]),
                    dict(snapshot(), profile=None), dict(snapshot(), pendingPairs=True)]:
            with self.assertRaises(ValueError):
                validate_snapshot(bad, config=CONFIG)
        callback.update(enabled=False, saturated=True)
        self.assertTrue(validate_snapshot(callback, config=CONFIG))

    def test_freeze_uses_shared_retained_daemon_lifecycle(self):
        observer = object.__new__(NativeObserver)
        observer.frozen = False
        observer.spec, observer.config = SPEC, CONFIG
        calls = []
        observer._intent = lambda *args: calls.append(args)
        observer._wait = lambda *args, **kw: dict(status=status(), snapshot=snapshot())
        observer.before_menu()
        observer.before_menu()
        self.assertTrue(observer.frozen)
        self.assertEqual(calls, [('trace-freeze.request', 'cleanup-once')])


if __name__ == '__main__':
    unittest.main()
