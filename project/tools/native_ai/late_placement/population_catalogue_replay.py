"""Zero-turn, shared-controller gameplay migration qualification.

Install an isolated copy of the qualified saved-world package, append production
population catalogue SQL, and replace only the population gameplay script. Run
the pre-migration QAed refresh in lexical isolation, then the shipping refresh.
Compare every registered city/center property and bit, preserving native rules,
ordinary policy and the original save. No orders or turns are issued.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from planning_continue import prepare, enable, parse_census, compare_structure
from driver import (NativeSession,HeldProcess,make_probe_controller,native_inventory,
    launch,configure,flags,manifest,read,lua,sha,write_json,restore_preferences,require)
from ce_replay import DLL,HOTFIX_SHA,verify_modules
from ce_bakers_fresh import LOGS

HERE=Path(__file__).resolve().parent
MOD=HERE.parents[3]/'Civ Supply Chains'
GAMEPLAY='Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua'
SQL_PATH='Data/CSC_DIAG_POPULATION_CATALOGUE.sql'


def survey(reference):
    # Shadow every global export before compiling the reference; do not replace
    # registered gameplay callbacks or depend on setfenv/_G absent in Havok.
    body=reference.split('if GameEvents and GameEvents.PlayerTurnStarted then',1)[0]
    names=re.findall(r'^function (CSC_\w+)\(',body,re.M)
    require(names and len(names)==len(set(names)),'Reference export shape differs')
    encoder=read(HERE/'economy_component_probe.lua').split('for _,target in ipairs(CSC_COMPONENT_TARGETS)do',1)[0]
    encoder=encoder[encoder.index('local function encode'):]
    return encoder+'\nlocal legacyRefresh=(function()\nlocal '+','.join(names)+'\n'+body+'''
return CSC_RefreshCustomerPopulationReturns end)()
local properties={}
for row in GameInfo.CSC_BuildingTransactionYields()do if row.AmountProperty then properties[row.AmountProperty]=true end end
for row in GameInfo.CSC_Stage3CustomerTransactions()do properties[row.SellerPopulationProperty]=true end
local function capture()
 local result={};local players=PlayerManager.GetAlive()
 table.sort(players,function(a,b)return a:GetID()<b:GetID()end)
 for _,player in ipairs(players)do
  local cities={};for _,city in player:GetCities():Members()do cities[#cities+1]=city end
  table.sort(cities,function(a,b)return a:GetID()<b:GetID()end)
  for _,city in ipairs(cities)do
   local plot=Map.GetPlot(city:GetX(),city:GetY());local values={}
   for property in pairs(properties)do
    values[property]={city:GetProperty(property)or 0,plot:GetProperty(property)or 0}
    for i=0,19 do local bit=property..'_BIT_'..tostring(2^i)
     values[bit]={city:GetProperty(bit)or 0,plot:GetProperty(bit)or 0}
    end
   end
   result[#result+1]={player=player:GetID(),city=city:GetID(),properties=values}
  end
 end
 return result
end
legacyRefresh()
local expected=capture()
CSC_RefreshCustomerPopulationReturns()
local actual=capture()
local same=encode(expected)==encode(actual)
print('CSC_POPULATION_EXPECTED='..encode(expected))
print('CSC_POPULATION_ACTUAL='..encode(actual))
print('CSC_POPULATION_RESULT='..encode({verified=same,turn=Game.GetCurrentGameTurn(),cities=#actual}))
assert(same,'Population migration changes gameplay properties')
'''


def run(args):
    plan=prepare(args.source,args.output,args.at,args.at,args.dependencies,read_only=True)
    require(not native_inventory(),'Preserve foreign Civ/Tuner session')
    out=plan.output;out.mkdir(parents=True)
    paths=[MOD/'Data/CSC_BuildingTransactionSchema.sql']
    for q in('BAKERS','TAILORS'):
        paths.extend([MOD/f'Data/CSC_Q_{q}_TRANSACTIONS.sql',MOD/f'Data/CSC_Q_{q}_TRANSACTIONS_GOLD.sql'])
    paths.append(MOD/'Data/CSC_BuildingTransactionProcessor.sql')
    sql='\n'.join(read(p)for p in paths)
    reference=read(args.reference/GAMEPLAY)
    pins={str(p.resolve()):sha(p)for p in [*paths,MOD/GAMEPLAY,args.reference/GAMEPLAY,Path(__file__)]}
    code=survey(reference)
    (out/'diagnostic.sql').write_text(sql,encoding='utf-8')
    (out/'diagnostic.lua').write_text(code,encoding='utf-8')
    write_json(out/'protocol.json',dict(diagnostic=True,zero_turn=True,at=args.at,production_population_sql=True,
        legacy_refresh_isolated=True,no_orders=True,source_pins=pins,lgd=False))
    c=make_probe_controller(out,user_root=plan.user_root)
    s=NativeSession(out,c,inventory=native_inventory,hold=HeldProcess,write=write_json)
    copied=[]
    def verify():
        for i in copied:require(manifest(i['install'])==i['staged'],'Staged package changed')
        for i in plan.packages:require(manifest(i['source'])==i['files'],'Source package changed')
        for i in plan.extras.values():require(manifest(Path(i['path']))==i['files'],'Optional package changed')
        require(all(sha(Path(p))==h for p,h in pins.items()),'Qualification source changed')
    def gate():
        raw=c.cmd('CSC_ENDPOINT_PLAYERS='+lua(plan.identity['original_ai'])+'\nCSC_ENDPOINT_EXPECTED_TURN='+str(args.at)+'\n'+read(HERE/'full_game_census.lua'),'CSC_AI_BakersGameplay','population-source-census')
        (out/'source-census.txt').write_text(raw,encoding='utf-8')
        proof=compare_structure(plan.expected_census,parse_census(raw,args.at))
        write_json(out/'source-structure-comparison.json',proof)
        require(proof['verified'],'Saved structure differs')
        return True
    try:
        for item in plan.packages:
            shutil.copytree(item['source'],item['install']);copied.append(item)
            if item['role']=='csc':
                metadata,=item['install'].glob('*.modinfo');root=ET.fromstring(metadata.read_bytes())
                actions=root.find('InGameActions');files=root.find('Files')
                highest=max(int(p.text)for action in actions for p in action.findall('Properties/LoadOrder'))
                a=ET.SubElement(actions,'UpdateDatabase',id='CSC_DIAG_POPULATION_CATALOGUE')
                ET.SubElement(ET.SubElement(a,'Properties'),'LoadOrder').text=str(highest+1)
                ET.SubElement(a,'File').text=SQL_PATH;ET.SubElement(files,'File').text=SQL_PATH
                metadata.write_bytes(ET.tostring(root,encoding='utf-8',xml_declaration=True))
                (item['install']/SQL_PATH).write_text(sql,encoding='utf-8')
                shutil.copyfile(MOD/GAMEPLAY,item['install']/GAMEPLAY)
            item['staged']=manifest(item['install'])
        write_json(out/'staged-manifests.json',{i['role']:i['staged']for i in copied})
        s.start(lambda:launch(SimpleNamespace(binary=plan.binary),out));s.wait_context('MainMenu')
        configure(c,out,csc_id=plan.protocol['ce']);enable(s,plan.protocol['csc'])
        for identity in plan.extras:enable(s,identity)
        require({k for k,v in flags(c,'population-mods')['mods'].items()if v}=={plan.protocol['ce'],plan.protocol['csc'],*plan.extras},'Unexpected packages')
        s.load_once(plan.checkpoint['native_save'],sha256=plan.checkpoint['sha256'],native_directory=plan.saves,
            turn=args.at,contexts=('GameCore_Tuner','PlotInfo','CSC_AI_BakersGameplay','CSC_CustomerPopulationReturns'),eligibility=gate)
        ce=next(i for i in copied if i['role']=='ce')
        verify_modules(s,ce['install']/'Binaries/Win64'/DLL,out,HOTFIX_SHA)
        result=c.cmd(code,'CSC_CustomerPopulationReturns','population-gameplay-equivalence')
        (out/'gameplay-equivalence.txt').write_text(result,encoding='utf-8')
        match=re.search(r'CSC_POPULATION_RESULT=([^\r\n]+)',result);require(match,'Missing gameplay result')
        proof=json.loads(match[1]);require(proof['verified']and proof['turn']==args.at,'Gameplay equivalence failed')
        write_json(out/'complete.json',proof)
    finally:
        if s.owner is not None and s.owner.poll()is None:
            s.close(restore_preferences=lambda:restore_preferences(c,out),restore_package=verify)
        if s.closed:
            for i in copied:i['install'].rename(out/i['install'].name)
            for name in LOGS:
                p=plan.user_root/'Logs'/name
                if p.is_file():shutil.copyfile(p,out/name)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for k in('source','output','dependencies','reference'):p.add_argument('--'+k,type=Path,required=True)
    p.add_argument('--at',type=int,default=250)
    run(p.parse_args())
