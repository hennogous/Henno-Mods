"""Closed-log verdicts and executed UI readbacks; no native connection."""
import json
import unittest
from lupa.lua51 import LuaRuntime
from native_ui_exit_probe import review_exit_log,ui_readback


def log(scenario='unopened'):
    phases=['initial-unopened','final-unopened']if scenario=='unopened'else['initial-unopened','opened-BAKERS','switched-TAILORS','closed-selection','reopened-BAKERS','final-active']
    lines=['CSC Lenses: choice init begin quarter=BAKERS','CSC Lenses: choice init end quarter=BAKERS',
           'CSC Lenses: choice init begin quarter=TAILORS','CSC Lenses: choice init end quarter=TAILORS',
           'CSC Lenses: loaded; quarters=2; global shortcut observer installed; Q+1=BAKERS Q+2=TAILORS']
    for phase in phases:
        lines.append('CSC_UI_EXIT_PHASE='+json.dumps({'phase':phase,'turn':110}))
    if scenario=='active-lens':lines+=['CSC Lenses: entry check begin value=true reason=open','CSC Lenses: entry check end value=true','CSC Lenses: choice check begin quarter=BAKERS value=true','CSC Lenses: choice check end quarter=BAKERS']
    lines+=['CSC Lenses: shutdown begin active=false entry=false','CSC Lenses: entry check skipped during shutdown desired=false reason=shutdown','CSC Lenses: shutdown complete']
    return '\n'.join(lines)


class ExitEvidenceTests(unittest.TestCase):
    def test_unopened_and_active_completed_generation(self):
        for scenario in ('unopened','active-lens'):
            value=review_exit_log(log(scenario),scenario)
            self.assertTrue(value['shutdown_complete'])
            self.assertEqual(value['radio_calls_after_shutdown'],0)
            self.assertFalse(value['renderer_visual_validation'])

    def test_shutdown_started_without_completion_is_failure(self):
        with self.assertRaisesRegex(ValueError,'Shutdown'):
            review_exit_log(log().replace('CSC Lenses: shutdown complete',''),'unopened')

    def test_shutdown_radio_call_rejected_even_with_later_completion(self):
        with self.assertRaisesRegex(ValueError,'during/after shutdown'):
            review_exit_log(log().replace('CSC Lenses: entry check skipped','CSC Lenses: entry check begin value=false\nCSC Lenses: entry check skipped'),'unopened')

    def test_uncompleted_callback_or_lua_error_rejected(self):
        for text in (log().replace('CSC Lenses: choice init end quarter=TAILORS',''),log()+'\nRuntime Error: bad context'):
            with self.assertRaises(ValueError):review_exit_log(text,'unopened')

    def test_generation_scope_clock_and_phase_order_rejected(self):
        for text in (log()+log(),log().replace('110','111'),log().replace('final-unopened','initial-unopened')):
            with self.assertRaises(ValueError):review_exit_log(text,'unopened')

    def test_actual_lua_ui_readback_guard(self):
        for active in (False,True):
            lua=LuaRuntime();captured=[];lua.globals().print=captured.append
            lua.execute('local active='+str(active).lower()+''';
Controls={SupplyChainsLensEntry={IsChecked=function()return active end},SupplyChainsLensPanel={IsVisible=function()return active end}}
UI={GetInterfaceMode=function()return active and 2 or 1 end};InterfaceModeTypes={VIEW_MODAL_LENS=2};Game={GetCurrentGameTurn=function()return 110 end}
''')
            lua.execute(ui_readback('fixture',active))
            value=json.loads(captured[0].split('=',1)[1]);self.assertEqual(value['checked'],active)
            with self.assertRaises(Exception):lua.execute(ui_readback('wrong',not active))


if __name__=='__main__':unittest.main()
