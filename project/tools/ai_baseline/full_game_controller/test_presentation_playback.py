"""Offline regression for default presentation recovery; never connects to Civ."""
import copy
import json
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

from . import controller as shared
from . import natural_wonder_guard as natural
from . import project_built_guard as project
from .presentation_playback import install


PROOF = dict(turn=253, remaining=1, active=True, local_player=-1,
             player0_human=False, player0_alive=True)


class Diagnostics:
    def __init__(self):
        self.records = {}

    def write(self, path, value):
        self.records[str(path)] = copy.deepcopy(value)


class Base:
    def __init__(self, output):
        self.seq = 0
        self.state = {'NaturalWonderPopup': 1, 'ProjectBuiltPopup': 2}
        self.required_state = []


class PresentationPlaybackTests(unittest.TestCase):
    def setUp(self):
        self.output = Path.cwd() / ('presentation-no-io-' + uuid.uuid4().hex)
        self.events = []
        self.diagnostics = Diagnostics()
        self.proof = copy.deepcopy(PROOF)
        self.responses = {}

    def make(self):
        events = self.events

        def original(instance, target):
            events.append(('original', target))
            return 'existing-result'

        cls = shared.make_controller(Base, diagnostics=self.diagnostics,
                                     boundary_decision=lambda *args: ('wait', 0),
                                     tuner_port=0)
        out = self.output
        with patch.object(shared.FullGameController, 'release_disaster', original):
            instance = cls(out)
        self.assertEqual(events, [])
        self.assertEqual(self.diagnostics.records, {})
        self.assertFalse(out.exists(), 'constructor/install must perform no game or output I/O')
        self.assertTrue(hasattr(instance, '_natural_wonder_guard'))
        self.assertTrue(hasattr(instance, '_project_built_guard'))

        def state_read(label):
            events.append(('core', label))
            return copy.deepcopy(self.proof)

        def states():
            events.append(('states',))
            return instance.state

        def cmd(code, context, label, wait):
            events.append(('cmd', context))
            prefix = 'NATURAL_WONDER' if context == 'NaturalWonderPopup' else 'PROJECT_BUILT'
            state = (instance._natural_wonder_guard if context == 'NaturalWonderPopup'
                     else instance._project_built_guard)
            self.assertIn(254, state['blocked_targets'])
            self.assertTrue(any(r['phase'] == 'intent-reserved' and r['context'] == context
                                for r in self.diagnostics.records.values()))
            response = self.responses.get(context, 'success')
            if isinstance(response, BaseException):
                raise response
            requested = response == 'success'
            value = dict(coreTurn=253, target=254, requested=requested,
                         reason='shipped_cosmetic_close' if requested else response,
                         hidden=False, path_hidden=False, path_visible=True,
                         popup_stack_before=[dict(id=context, priority=1000, flags=0)],
                         popup_stack_target_verified=True,
                         popup_stack_target_highest_priority=True)
            return ('CSC_' + prefix + '_BEFORE={}\nCSC_' + prefix + '_GUARD='
                    + json.dumps(value)
                    + ('\nCSC_' + prefix + '_RELEASE_REQUESTED' if requested else ''))

        instance.state_read, instance.states, instance.cmd = state_read, states, cmd
        return instance

    def test_actual_default_constructor_composes_original_then_both_once(self):
        instance = self.make()
        self.assertEqual(instance.release_disaster(254), 'existing-result')
        self.assertEqual([e for e in self.events if e[0] in ('original', 'cmd')],
                         [('original', 254), ('cmd', 'NaturalWonderPopup'),
                          ('cmd', 'ProjectBuiltPopup')])
        self.assertEqual(sum(e[0] == 'core' for e in self.events), 2)
        self.assertEqual(len(self.diagnostics.records), 2)

    def test_install_is_idempotent(self):
        instance = self.make()
        wrapper = instance.release_disaster
        install(instance)
        natural.install(instance)
        project.install(instance)
        self.assertIs(instance.release_disaster, wrapper)
        self.assertEqual(self.events, [])

    def test_fresh_core_rejections_send_no_ui_command(self):
        instance = self.make()
        for change in ({'player0_human': True}, {'active': False},
                       {'player0_alive': False}, {'local_player': 0},
                       {'remaining': 0}, {'remaining': 6}, {'turn': 252}):
            with self.subTest(change=change):
                self.events.clear()
                self.proof = dict(PROOF, **change)
                self.assertEqual(instance.release_disaster(254), 'existing-result')
                self.assertFalse(any(e[0] == 'cmd' for e in self.events))
                self.assertEqual(sum(e[0] == 'original' for e in self.events), 1)

    def test_confirmed_noop_can_be_rechecked(self):
        instance = self.make()
        self.responses = {'NaturalWonderPopup': 'hidden',
                          'ProjectBuiltPopup': 'popup_stack_unverified'}
        for _ in range(2):
            instance.release_disaster(254)
        self.assertEqual(sum(e[0] == 'cmd' for e in self.events), 4)
        for state in (instance._natural_wonder_guard, instance._project_built_guard):
            self.assertFalse(state['blocked_targets'])
            self.assertFalse(state['acknowledgements'])

    def test_ambiguous_project_ack_blocks_replay(self):
        instance = self.make()
        instance.state = {'ProjectBuiltPopup': 2}
        self.responses['ProjectBuiltPopup'] = TimeoutError('reply missing after Close')
        with self.assertRaises(TimeoutError):
            instance.release_disaster(254)
        instance.release_disaster(254)
        self.assertEqual(sum(e == ('cmd', 'ProjectBuiltPopup') for e in self.events), 1)
        self.assertIn(254, instance._project_built_guard['blocked_targets'])
        self.assertEqual(next(iter(self.diagnostics.records.values()))['phase'],
                         'ambiguous-or-failed')

    def test_each_guard_has_eight_ack_interval_cap(self):
        instance = self.make()
        for _ in range(10):
            instance.release_disaster(254)
        for context in ('NaturalWonderPopup', 'ProjectBuiltPopup'):
            self.assertEqual(sum(e == ('cmd', context) for e in self.events), 8)
        self.assertEqual(instance._project_built_guard['acknowledgements'][254], 8)
        self.assertEqual(instance._natural_wonder_guard['acknowledgements'][254], 8)

    def test_missing_popup_context_sends_no_command(self):
        instance = self.make()
        instance.state = {}
        instance.release_disaster(254)
        self.assertFalse(any(e[0] == 'cmd' for e in self.events))


class ProjectBuiltLuaTests(unittest.TestCase):
    """Run actual shipped-guard Lua when optional local Lua51 test dependency exists."""
    def test_strict_stack_priority_and_visibility(self):
        try:
            from lupa.lua51 import LuaRuntime
        except ImportError:
            self.skipTest('optional lupa.lua51 is not installed')
        template = project.RESOURCE.read_text(encoding='utf-8')
        for key, value in dict(CORE_TURN=253, TARGET_TURN=254, CORE_ACTIVE=True,
                               REMAINING=1, CORE_LOCAL=-1, CORE_HUMAN=False).items():
            template = template.replace('__' + key + '__', str(value).lower())
        for other, hidden, expected in ((None, False, 1), (500, False, 1),
                                         (1000, False, 0), (2000, False, 0),
                                         (None, True, 0)):
            with self.subTest(other_priority=other, hidden=hidden):
                lua = LuaRuntime()
                lua.execute('''calls=0;hidden=false;other=nil
                    print=function(...)end
                    Game={GetCurrentGameTurn=function()return 253 end,GetLocalPlayer=function()return 0 end}
                    source={IsHidden=function()return hidden end,IsVisible=function()return not hidden end}
                    ContextPtr={IsHidden=function()return hidden end,LookUpControl=function(_,path)
                        assert(path=='/InGame/WorldPopups/ProjectBuiltPopup');return source end}
                    UIManager={GetPopupStack=function()
                        local rows={{ID='ProjectBuiltPopup',Priority=1000,Flags=0}}
                        if other then rows[2]={ID='OtherPopup',Priority=other,Flags=0}end
                        return rows end}
                    Close=function()calls=calls+1;hidden=true end''')
                lua.globals().other, lua.globals().hidden = other, hidden
                lua.execute(template)
                self.assertEqual(lua.globals().calls, expected)


if __name__ == '__main__':
    unittest.main()
