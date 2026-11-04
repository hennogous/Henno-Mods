"""Actual Lua5.1 tests for Core-owned autoplay control across UI lag."""
from pathlib import Path
import unittest

from lupa.lua51 import LuaRuntime

HERE = Path(__file__).resolve().parent
TEMPLATES = ('session_dismissal.lua', 'war_session_dismissal.lua',
             'first_meet_session_dismissal.lua')


class SessionAuthorityTests(unittest.TestCase):
    def execute(self, name, setup='', **overrides):
        lua = LuaRuntime()
        lua.execute("""
calls=0;human=false;localplayer=-1;turn=80;open=true;peer=5;recipient=0
war=true;key='CHOICE_EXIT';definition=true;statement='FIRST_MEET_NEAR_RECIPIENT'
markers={};print=function(...)markers[#markers+1]=table.concat({...},' ')end
Game={GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return localplayer end}
Players={[0]={IsHuman=function()return human end,GetDiplomacy=function()return {
 IsAtWarWith=function(self,from)assert(from==5);return war end}end}}
GameInfo={DiplomacySelections=function()local used=false;return function()
 if definition and not used then used=true;return {
 Type=guard_name=='war_session_dismissal.lua' and 'DECLARE_WAR_FROM_AI' or statement,Key=key}end end end}
DiplomacyManager={FindOpenSessionID=function()return 17 end,
 IsSessionIDOpen=function(id)assert(id==17);return open end,
 GetSessionInfo=function()return{FromPlayer=peer,ToPlayer=recipient}end,
 CloseSession=function(id)assert(id==17);calls=calls+1 end,
 AddResponse=function()error('forbidden response')end,
 AddStatement=function()error('forbidden statement')end}
ContextPtr={IsHidden=function()return true end};Close=function()error('hidden view close')end
AutoplayManager={SetActive=function()error('forbidden activation')end,
 SetTurns=function()error('forbidden budget change')end}
""")
        lua.globals().guard_name = name
        lua.execute(setup)
        values = dict(FROM=5, CORE_TURN=80, TARGET_TURN=85,
                      CORE_ACTIVE=True, CORE_LOCAL=-1, CORE_HUMAN=False,
                      STATEMENT='FIRST_MEET_NEAR_RECIPIENT')
        values.update(overrides)
        code = (HERE/name).read_text(encoding='utf-8')
        for key, value in values.items():
            code = code.replace('__'+key+'__',
                                str(value).lower() if isinstance(value, bool) else str(value))
        self.assertNotIn('__', code)
        lua.execute(code)
        return lua.globals().calls, list(lua.globals().markers.values())

    def test_stale_ui_human_uses_fresh_core_authority_and_records_discrepancy(self):
        for name in TEMPLATES:
            for clock in (80, 79):
                with self.subTest(template=name, ui_turn=clock):
                    calls, markers = self.execute(name, f'human=true;turn={clock}')
                    self.assertEqual(calls, 1)
                    self.assertTrue(any('CSC_OBSERVER_WARNING_STALE_UI_HUMAN' in s for s in markers))
                    self.assertTrue(any('DISMISS_REQUESTED' in s for s in markers))

    def test_current_ui_and_core_control_remain_accepted(self):
        for name in TEMPLATES:
            with self.subTest(template=name):
                calls, markers = self.execute(name)
                self.assertEqual(calls, 1)
                self.assertFalse(any('STALE_UI' in s for s in markers))

    def test_actual_core_human_or_other_core_phase_cannot_close(self):
        for name in TEMPLATES:
            for change in ({'CORE_HUMAN': True}, {'CORE_ACTIVE': False},
                           {'CORE_LOCAL': 0}, {'TARGET_TURN': 80}, {'TARGET_TURN': 86}):
                with self.subTest(template=name, change=change):
                    calls, markers = self.execute(name, 'human=true', **change)
                    self.assertEqual(calls, 0)
                    self.assertTrue(any('SKIPPED core_phase' in s for s in markers))

    def test_ui_clock_local_session_and_participant_guards_remain(self):
        for name in TEMPLATES:
            for setup in ('human=true;turn=78', 'human=true;turn=81',
                          'human=true;localplayer=0', 'human=true;open=false',
                          'human=true;peer=3', 'human=true;recipient=2'):
                with self.subTest(template=name, setup=setup):
                    calls, markers = self.execute(name, setup)
                    self.assertEqual(calls, 0)
                    self.assertTrue(any('DISMISS_SKIPPED' in s for s in markers))

    def test_war_and_first_meet_choice_protections_remain_with_stale_ui(self):
        for name in ('war_session_dismissal.lua', 'first_meet_session_dismissal.lua'):
            for setup in ("human=true;key='CHOICE_POSITIVE'", 'human=true;definition=false'):
                with self.subTest(template=name, setup=setup):
                    self.assertEqual(self.execute(name, setup)[0], 0)
        self.assertEqual(self.execute('war_session_dismissal.lua', 'human=true;war=false')[0], 0)
        self.assertEqual(self.execute('first_meet_session_dismissal.lua', 'human=true',
                                      STATEMENT='UNREVIEWED_STATEMENT')[0], 0)


if __name__ == '__main__':
    unittest.main()
