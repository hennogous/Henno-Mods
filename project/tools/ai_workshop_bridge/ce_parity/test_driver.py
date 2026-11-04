"""Offline guards for the live harness; imports never launch Civ."""
import copy
import unittest

from driver import audit_plan, parse, setup
from policy import shortlist


def state():
    snapshot = dict(turn=6, originalAI=[1, 2], currentHumans=[0], candidates=[
        dict(player=1, city=7, district=8, plot=30, quarter='BAKERS',
             production=2, gold=2, total=4, materialOnSite=False, legal=True),
        dict(player=1, city=7, district=9, plot=31, quarter='TAILORS',
             production=1, gold=1, total=2, materialOnSite=False, legal=True)])
    return dict(originalAI=[1, 2], snapshot=snapshot, plan=shortlist(snapshot))


class Guards(unittest.TestCase):
    def test_actual_policy_audit_accepts_both_signs(self):
        value = audit_plan(state())
        self.assertTrue(value['verified'])
        self.assertEqual(value['entries'], 2)

    def test_policy_audit_rejects_silent_parameter_change(self):
        value = state()
        value['plan']['entries'][1]['delta'] *= 2
        with self.assertRaisesRegex(RuntimeError, 'entries'):
            audit_plan(value)

    def test_policy_audit_rejects_human_identity_change(self):
        value = state()
        value['originalAI'] = [0, 1, 2]
        with self.assertRaisesRegex(RuntimeError, 'human'):
            audit_plan(value)

    def test_policy_audit_rejects_candidate_omission(self):
        value = state()
        value['plan']['penalized'] = []
        with self.assertRaisesRegex(RuntimeError, 'penalized'):
            audit_plan(value)

    def test_receipt_requires_unambiguous_marker(self):
        self.assertEqual(parse('noise\nX={"ok":1}\n', 'X'), dict(ok=1))
        for text in ('', 'X={}\nX={}\n'):
            with self.assertRaises(RuntimeError):
                parse(text, 'X')

    def test_modes_and_speed_are_explicit(self):
        self.assertIn("'GAMESPEED_ONLINE'", setup())
        self.assertIn("'CSC_CE_POLICY_MODE','off'", setup('off'))
        with self.assertRaises(ValueError):
            setup('other')


if __name__ == '__main__':
    unittest.main()
