import json,unittest
from pathlib import Path
try:
 from lupa.lua51 import LuaRuntime
except ImportError:
 LuaRuntime=None
from native_harvest_rule import verify_live

@unittest.skipIf(LuaRuntime is None,'Actual Lua5.1 runtime required')
class Rule(unittest.TestCase):
 def setUp(self):
  self.lua=LuaRuntime(unpack_returned_tuples=True);self.output=[];self.lua.globals().print=lambda x:self.output.append(str(x))
  self.lua.execute('''
  Game={turn=16,props={},trace={}};function Game.GetCurrentGameTurn()return Game.turn end
  function Game:GetProperty(k)return self.props[k]end
  function Game:SetProperty(k,v)self.props[k]=v;self.trace[#self.trace+1]='save:'..v.status end
  AutoplayManager={active=false};function AutoplayManager.IsActive()return AutoplayManager.active end
  GameEffects={rows={},calls=0,drop=false,fail=-1,inactive=false};local effects=GameEffects
  function GameEffects.GetModifiers()local out={};for id in ipairs(effects.rows)do out[#out+1]=id end;return out end
  function GameEffects.GetModifierDefinition(id)return {Id='TRAIT_MAORI_PREVENT_HARVEST'}end
  function GameEffects.GetModifierOwner(id)return effects.rows[id].pid end
  function GameEffects.GetObjectsPlayerId(owner)return owner end
  function GameEffects.GetModifierActive(id)return not effects.inactive end
  Players={}
  for pid=0,5 do
   local owner=pid;Players[owner]={pid=owner,human=owner==0};local actor=Players[owner]
   function actor:IsAlive()return true end
   function actor:IsMajor()return true end
   function actor:IsHuman()return self.human end
   function actor:AttachModifierByID(def)
    assert(def=='TRAIT_MAORI_PREVENT_HARVEST');local ledger=Game:GetProperty('CSC_NATIVE_RULE_test')
    assert(ledger.status=='attach_requested'and ledger.attempted[#ledger.attempted]==self.pid)
    assert(Game.trace[#Game.trace]=='save:attach_requested');Game.trace[#Game.trace+1]='attach:'..self.pid
    effects.calls=effects.calls+1
    if self.pid==effects.fail then error('simulated attachment error')end
    if not effects.drop then effects.rows[#effects.rows+1]={pid=self.pid}end
   end
  end
  ''')
  self.lua.execute(Path(__file__).with_name('native_harvest_rule_ui.lua').read_text())
  self.lua.execute(Path(__file__).with_name('native_harvest_rule.lua').read_text())
 def call(self,name):
  self.lua.execute('CSC_NATIVE_HARVEST_RULE.'+name+'({enabled=true,token="test",turn=16});')
  return json.loads(self.output[-1].split('=',1)[1])
 def test_five_exact_active_owners_and_closed_ledger(self):
  self.assertEqual(self.call('Read')['instances'],[]);returned=self.call('Begin');self.assertTrue(verify_live(returned));closed=self.call('Confirm');self.assertTrue(verify_live(closed,confirmed=True));self.assertEqual(self.lua.globals().GameEffects.calls,5)
 def test_repeated_begin_never_reattaches(self):
  self.call('Begin');self.call('Confirm')
  with self.assertRaises(Exception):self.call('Begin')
  self.assertEqual(self.lua.globals().GameEffects.calls,5)
 def test_active_autoplay_or_wrong_clock_does_nothing(self):
  for code in('AutoplayManager.active=true','Game.turn=17'):
   self.setUp();self.lua.execute(code)
   with self.subTest(code=code),self.assertRaises(Exception):self.call('Begin')
   self.assertEqual(self.lua.globals().GameEffects.calls,0)
 def test_human_target_rejected_before_attachment(self):
  self.lua.execute('Players[2].human=true')
  with self.assertRaises(Exception):self.call('Begin')
  self.assertEqual(self.lua.globals().GameEffects.calls,0)
 def test_preexisting_instance_for_observer_or_ai_requires_reconciliation(self):
  for owner in(0,2):
   self.setUp();self.lua.execute('GameEffects.rows={{pid='+str(owner)+'}}')
   with self.subTest(owner=owner),self.assertRaises(Exception):self.call('Begin')
   self.assertEqual(self.lua.globals().GameEffects.calls,0)
 def test_partial_failure_keeps_attempt_and_never_repeats(self):
  self.lua.execute('GameEffects.fail=3')
  with self.assertRaises(Exception):self.call('Begin')
  value=self.call('Read');self.assertEqual(value['ledger']['attempted'],[1,2,3]);self.assertEqual(value['ledger']['returned'],[1,2])
  with self.assertRaises(Exception):self.call('Begin')
  self.assertEqual(self.lua.globals().GameEffects.calls,3)
 def test_silent_attach_failure_is_not_native_proof(self):
  self.lua.execute('GameEffects.drop=true');value=self.call('Begin')
  with self.assertRaises(AssertionError):verify_live(value)
  with self.assertRaises(Exception):self.call('Confirm')
  self.assertEqual(self.lua.globals().GameEffects.calls,5)
 def test_inactive_native_instance_not_accepted(self):
  self.lua.execute('GameEffects.inactive=true');value=self.call('Begin')
  with self.assertRaises(AssertionError):verify_live(value)
  with self.assertRaises(Exception):self.call('Confirm')
 def test_duplicate_owner_or_observer_extra_is_not_accepted(self):
  self.call('Begin');self.lua.execute('GameEffects.rows[5].pid=1')
  with self.assertRaises(AssertionError):verify_live(self.call('Read'))
  with self.assertRaises(Exception):self.call('Confirm')
 def test_gameplay_does_not_require_UI_only_GameEffects_global(self):
  self.lua.execute('NativeEffectReader=GameEffects;GameEffects=nil')
  # The native fake attachment closure needs its own runtime backing store, as
  # separate UI/gameplay VMs do; preserve it while hiding the gameplay global.
  self.lua.execute('GameEffects=NativeEffectReader')
  self.call('Begin');self.lua.execute('GameEffects=nil');closed=self.call('Confirm');self.assertTrue(verify_live(closed,confirmed=True))
 def test_missing_bridge_rejected_before_effect(self):
  self.lua.execute('ExposedMembers.CSC_NATIVE_HARVEST_RULE_UI=nil')
  with self.assertRaises(Exception):self.call('Begin')
  self.assertEqual(self.lua.globals().GameEffects.calls,0)
 def test_confirm_without_attempt_rejected(self):
  with self.assertRaises(Exception):self.call('Confirm')
  self.assertEqual(self.lua.globals().GameEffects.calls,0)

if __name__=='__main__':unittest.main()
