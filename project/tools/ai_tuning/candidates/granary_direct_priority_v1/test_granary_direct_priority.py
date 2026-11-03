"""Immutable native SQLite deltas and actual Lua51 read-only roster preflight."""
import collections
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import unittest
from lupa.lua51 import LuaRuntime

HERE=Path(__file__).resolve().parent
SQL=(HERE/'granary_direct_priority.sql').read_text(encoding='utf-8')
READER=(HERE/'granary_direct_preflight.lua').read_text(encoding='utf-8')
DATABASE=Path(os.environ.get('CSC_TEST_GRANARY_DIRECT_DATABASE',r'C:\Users\Shadow\Desktop\Codex\csc-native-producer-decision-20261030\run-04\on\runtime-gameplay.sqlite'))
EXPECTED_DB='e7267fd206e7c4ea3553c9ad06973de9ea811a6467a27e2391bdc1914d5de2c8'
TRAIT='TRAIT_LEADER_GENGHIS_KHAN_ABILITY';LIST='CSC_AI_GranaryDirectPriority_V1'

def database():
 if hashlib.sha256(DATABASE.read_bytes()).hexdigest()!=EXPECTED_DB:raise AssertionError('Immutable reference database hash changed')
 result=sqlite3.connect(':memory:')
 with sqlite3.connect(DATABASE.resolve().as_uri()+'?mode=ro',uri=True)as source:source.backup(result)
 return result

class NativeSQL(unittest.TestCase):
 def setUp(self):self.db=database()
 def tearDown(self):self.db.close()
 def test_exact_trait_is_real_unique_and_not_a_raw_leader(self):
  self.assertEqual(list(self.db.execute('SELECT TraitType FROM Traits WHERE TraitType=?',(TRAIT,))),[(TRAIT,)])
  self.assertEqual(list(self.db.execute('SELECT LeaderType,TraitType FROM LeaderTraits WHERE TraitType=?',(TRAIT,))),[('LEADER_GENGHIS_KHAN',TRAIT)])
  self.assertEqual(list(self.db.execute('SELECT * FROM CivilizationTraits WHERE TraitType=?',(TRAIT,))),[])
  leaders=dict(self.db.execute('SELECT LeaderType,InheritFrom FROM Leaders'))
  matching=[]
  for original in leaders:
   node=original;seen=set()
   while node:
    self.assertNotIn(node,seen);seen.add(node)
    if node=='LEADER_GENGHIS_KHAN':matching.append(original);break
    node=leaders.get(node)
  self.assertEqual(matching,['LEADER_GENGHIS_KHAN'])
 def test_exactly_three_additive_rows_preserve_RH_and_private40(self):
  tables=('AiListTypes','AiLists','AiFavoredItems','Types','Strategies','StrategyConditions','Strategy_Priorities','Modifiers','ModifierArguments','TreeData')
  before={t:collections.Counter(self.db.execute('SELECT * FROM '+t))for t in tables}
  self.db.executescript(SQL);after={t:collections.Counter(self.db.execute('SELECT * FROM '+t))for t in tables}
  for table in tables:
   self.assertFalse(before[table]-after[table])
   self.assertEqual(sum((after[table]-before[table]).values()),1 if table in tables[:3]else 0)
  self.assertEqual(list(self.db.execute('SELECT LeaderType,System,AgendaType FROM AiLists WHERE ListType=?',(LIST,))),[(TRAIT,'Buildings',None)])
  self.assertEqual(list(self.db.execute('SELECT Item,Favored,Value FROM AiFavoredItems WHERE ListType=?',(LIST,))),[('BUILDING_GRANARY',1,0)])
  self.assertEqual(list(self.db.execute("SELECT Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_BUILDING_GRANARY' AND Name='Amount'")),[('40',)])
 def test_repeat_is_idempotent(self):
  self.db.executescript(SQL);tables=('AiListTypes','AiLists','AiFavoredItems')
  before={t:list(self.db.execute('SELECT * FROM '+t))for t in tables}
  self.db.executescript(SQL);self.assertEqual(before,{t:list(self.db.execute('SELECT * FROM '+t))for t in tables})
 def test_non_RH_profile_adds_nothing(self):
  self.db.execute("UPDATE CSC_AI_Profile SET Mode='BASIC' WHERE Id='ACTIVE'");self.db.executescript(SQL)
  self.assertEqual(list(self.db.execute('SELECT * FROM AiListTypes WHERE ListType=?',(LIST,))),[])
 def test_missing_exact_leader_trait_binding_adds_nothing(self):
  self.db.execute('DELETE FROM LeaderTraits WHERE LeaderType=? AND TraitType=?',('LEADER_GENGHIS_KHAN',TRAIT));self.db.executescript(SQL)
  for table in ('AiListTypes','AiLists','AiFavoredItems'):
   self.assertEqual(list(self.db.execute('SELECT * FROM '+table+' WHERE ListType=?',(LIST,))),[])

FIXTURE=r'''
function rows(values,key)
 local result={};for _,v in ipairs(values)do if key and v[key]then result[v[key]]=v end end
 return setmetatable(result,{__call=function()local i=0;return function()i=i+1;return values[i]end end})
end
Game={GetCurrentGameTurn=function()return 110 end}
GameInfo={};GameInfo.CSC_AI_Profile=rows({{Id='ACTIVE',Mode='RH'}})
GameInfo.AiListTypes=rows({{ListType='CSC_AI_GranaryDirectPriority_V1'}})
GameInfo.AiLists=rows({{ListType='CSC_AI_GranaryDirectPriority_V1',LeaderType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY',System='Buildings'}})
GameInfo.AiFavoredItems=rows({{ListType='CSC_AI_GranaryDirectPriority_V1',Item='BUILDING_GRANARY',Favored=true,Value=0}})
GameInfo.LeaderTraits=rows({{LeaderType='LEADER_GENGHIS_KHAN',TraitType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY'}})
GameInfo.CivilizationTraits=rows({})
local leaders={};for i=0,5 do leaders[#leaders+1]={LeaderType=i==3 and'LEADER_GENGHIS_KHAN'or'LEADER_FIXTURE_'..i,InheritFrom='LEADER_DEFAULT'}end
leaders[#leaders+1]={LeaderType='LEADER_DEFAULT'};GameInfo.Leaders=rows(leaders,'LeaderType')
Players={};PlayerConfigurations={}
for i=0,5 do local pid=i
 Players[pid]={IsAlive=function()return true end,IsMajor=function()return true end,IsHuman=function()error('current human flag forbidden')end}
 PlayerConfigurations[pid]={GetLeaderTypeName=function()return pid==3 and'LEADER_GENGHIS_KHAN'or'LEADER_FIXTURE_'..pid end,
 GetCivilizationTypeName=function()return pid==3 and'CIVILIZATION_MONGOLIA'or'CIVILIZATION_FIXTURE_'..pid end}
end
'''

class ReadonlyPreflight(unittest.TestCase):
 def read(self,setup='',roles="{['0']=true}"):
  lua=LuaRuntime();texts=[];lua.globals().print=texts.append;lua.execute(FIXTURE);lua.execute(setup)
  lua.execute(READER.replace('__ORIGINAL_HUMANS__',roles))
  self.assertEqual(len(texts),1);self.assertTrue(texts[0].startswith('CSC_GRANARY_DIRECT_PREFLIGHT='))
  return json.loads(texts[0].split('=',1)[1])
 def test_valid_roster_and_exact_rows_do_not_claim_native_preference(self):
  value=self.read();self.assertTrue(value['scope_verified']);self.assertEqual(value['turn'],110)
  self.assertEqual(value['eligible_player_ids'],[3]);self.assertEqual([r['player']for r in value['roster']],list(range(6)))
  self.assertTrue(value['roster'][0]['original_human']);self.assertFalse(value['roster'][3]['original_human'])
  self.assertEqual(value['native_preference'],'UNOBSERVED_BY_THIS_READER')
 def test_unknown_or_wrong_original_roles_fail_closed(self):
  for roles in ('nil','{}',"{['0']=true,['3']=true}"):
   self.assertFalse(self.read(roles=roles)['scope_verified'])
 def test_shared_actual_roster_leader_is_exposed_and_rejected(self):
  value=self.read("PlayerConfigurations[1].GetLeaderTypeName=function()return 'LEADER_GENGHIS_KHAN'end")
  self.assertEqual(value['eligible_player_ids'],[1,3]);self.assertFalse(value['scope_verified'])
 def test_inherited_shared_trait_and_civilization_membership_rejected(self):
  for setup in ("GameInfo.Leaders.LEADER_FIXTURE_2.InheritFrom='LEADER_GENGHIS_KHAN'",
                "GameInfo.CivilizationTraits=rows({{CivilizationType='CIVILIZATION_FIXTURE_2',TraitType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY'}})"):
   value=self.read(setup);self.assertIn(2,value['eligible_player_ids']);self.assertFalse(value['scope_verified'])
 def test_raw_leader_wrong_rows_or_missing_Getter_rejected(self):
  for setup in ("GameInfo.AiLists[1]=nil;GameInfo.AiLists=rows({{ListType='CSC_AI_GranaryDirectPriority_V1',LeaderType='LEADER_GENGHIS_KHAN',System='Buildings'}})",
                'PlayerConfigurations[3].GetLeaderTypeName=nil',
                "GameInfo.AiFavoredItems=rows({{ListType='CSC_AI_GranaryDirectPriority_V1',Item='BUILDING_GRANARY',Favored=true,Value=1}})"):
   self.assertFalse(self.read(setup)['scope_verified'])
 def test_no_runtime_mutation_flag_callback_or_property_getter(self):
  for token in ('SetProperty(', 'GameEvents', 'GetProperty(', 'RequestOperation(', 'SetHuman(', 'CreateBuilding('):
   self.assertNotIn(token,READER)

if __name__=='__main__':unittest.main()
