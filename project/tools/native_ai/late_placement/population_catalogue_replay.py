"""Shared-controller gameplay migration and bounded native reception qualification.

Install an isolated copy of the qualified saved-world package, append production
population catalogue SQL, and replace only the population gameplay script. Run
the pre-migration QAed refresh in lexical isolation, then the shipping refresh.
Compare every registered city/center property and bit, preserving native rules,
ordinary policy and the original save. The default advances no turns; explicit
native-customer arms hold score publication and advance one ordinary turn.
"""
import argparse
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import time
from types import SimpleNamespace
import xml.etree.ElementTree as ET

from planning_continue import prepare, enable, parse_census, compare_structure
from driver import (NativeSession,HeldProcess,make_probe_controller,native_inventory,
    launch,configure,flags,manifest,read,lua,sha,write_json,restore_preferences,require)
from ce_replay import DLL,HOTFIX_SHA,verify_modules
from ce_bakers_fresh import LOGS

HERE=Path(__file__).resolve().parent
MOD=HERE.parents[3]/'Civ Supply Chains'
sys.path.insert(0,str(HERE.parents[3]/'project/tools/transactions'))
from population_catalogue_fixture import graph as transaction_graph, fixed_aliases
GAMEPLAY='Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua'
ECONOMY_UI='Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'
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
-- Compare EVERY property/bit in memory, but do not flood the console with two
-- mostly-zero multi-megabyte arrays. That can exhaust transport's ACK window
-- after a successful comparison. Keep useful nonzero base amounts and emit
-- full affected-city differences only when the exact comparison fails.
local readings=0
for i,record in ipairs(actual)do
 local amounts={}
 for property,pair in pairs(record.properties)do
  readings=readings+2
  if not property:find('_BIT_',1,true)and(pair[1]~=0 or pair[2]~=0)then amounts[property]=pair end
 end
 print('CSC_POPULATION_CITY='..encode({player=record.player,city=record.city,amounts=amounts}))
 if not same and encode(record)~=encode(expected[i])then
  print('CSC_POPULATION_DIFFERENCE='..encode({expected=expected[i],actual=record}))
 end
end
print('CSC_POPULATION_RESULT='..encode({verified=same,turn=Game.GetCurrentGameTurn(),cities=#actual,readings=readings}))
assert(same,'Population migration changes gameplay properties')
'''


def run(args):
    plan=prepare(args.source,args.output,args.at,args.at,args.dependencies,read_only=True)
    require(not native_inventory(),'Preserve foreign Civ/Tuner session')
    ce_dll=getattr(args,'ce_dll',None);ce_sha=getattr(args,'ce_sha',None)
    require(bool(ce_dll)==bool(ce_sha),'CE diagnostic overlay requires both DLL and expected SHA')
    if ce_dll:require(sha(ce_dll)==ce_sha,'CE diagnostic overlay identity differs')
    out=plan.output;out.mkdir(parents=True)
    paths=[MOD/'Data/CSC_BuildingTransactionSchema.sql',MOD/'Data/CSC_TradeRouteSchema.sql']
    for q in('BAKERS','TAILORS'):
        paths.extend([MOD/f'Data/CSC_Q_{q}_TRANSACTIONS.sql',MOD/f'Data/CSC_Q_{q}_TRANSACTIONS_GOLD.sql'])
    paths.extend([MOD/'Data/CSC_MaterialTransactionProcessor.sql',MOD/'Data/CSC_FixedBuildingTransactionProcessor.sql',
                  MOD/'Data/CSC_BuildingTransactionProcessor.sql',MOD/'Data/CSC_MaterialTransactions.sql',
                  MOD/'Data/CSC_TradeRouteProcessor.sql'])
    # Compare the complete loaded native rows for fixed aliases, including all
    # actual engine columns/defaults, rather than only the fixture's schema.
    # The source cache is read-only and was produced by the already qualified
    # original mod stack; the structural save gate separately checks the world.
    database=plan.user_root/'Cache/DebugGameplay.sqlite'
    if args.reference_graph:
        path=args.reference_graph.resolve(strict=True)
        previous=json.loads((path.parent/'protocol.json').read_text())
        closed=json.loads((path.parent/'session-closed.json').read_text())
        require(closed['verified']and previous['source']==str(plan.source)
            and previous['start']==args.at==previous['through']
            and previous['gameplay_edits']is False and previous['main_lua_policy_unchanged']is True,
            'Require closed, unchanged-policy same-world native reference')
        original_all=json.loads(path.read_text())
        aliases=fixed_aliases()
        original_fixed={name:[r for r in rows if r[1 if name in('BuildingModifiers','DistrictModifiers')else 0]in aliases]
            for name,rows in original_all.items()}
    else:
        with sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)as db:
            require(not db.execute("SELECT 1 FROM sqlite_master WHERE name='CSC_BuildingTransactions'").fetchone(),
                'Use an explicit original-package reference after a candidate cache')
            original_fixed=transaction_graph(db,'fixed');original_all=transaction_graph(db,'all_csc')
    require(sum(map(len,original_fixed.values()))>0,'Missing fixed native reference')
    write_json(out/'reference-fixed-native-graph.json',original_fixed)
    write_json(out/'reference-all-csc-native-graph.json',original_all)
    sql='\n'.join(read(p)for p in paths)
    reference=read(args.reference/GAMEPLAY)
    inputs=[*paths,MOD/GAMEPLAY,args.reference/GAMEPLAY,Path(__file__),Path(transaction_graph.__code__.co_filename)]
    route_legacy=None
    if getattr(args,'route_smoke',False):
        require(not getattr(args,'joint_route_smoke',False)or args.model_smoke,'Joint route smoke requires --model-smoke UI overlay')
        from route_catalogue_probe import inputs as route_inputs
        package=next(i for i in plan.packages if i['role']=='csc')
        route_legacy=package['source']/'Lua_UI/TradeRoutes/CSC_TradeRouteInteractions.lua'
        inputs.extend(route_inputs(route_legacy))
    if getattr(args,'customer_world_smoke',False):
        require(args.route_smoke and args.model_smoke and args.joint_route_smoke,'Customer world requires route/model/joint smoke flags')
        from customer_world_probe import inputs as customer_inputs
        inputs.extend(customer_inputs())
    native_baseline=getattr(args,'customer_native_baseline',False)
    native_treatment=getattr(args,'customer_native_treatment',None)
    native_mode=getattr(args,'customer_native_mode','late')
    require(not(native_baseline and native_treatment),'Choose one native customer diagnostic arm')
    if native_baseline or native_treatment:
        require(args.customer_world_smoke and ce_dll,'Customer native probe requires corrected CE and customer-world quotes')
        inputs.extend([HERE/'customer_native_probe.py',HERE/'customer_native_watch.js'])
        if native_treatment:inputs.append(native_treatment)
    if args.reference_graph:inputs.append(args.reference_graph)
    pins={str(p.resolve()):sha(p)for p in inputs}
    if ce_dll:
        pins[str(ce_dll.resolve())]=ce_sha
        pins[str((HERE/'interval_pricing_probe.py').resolve())]=sha(HERE/'interval_pricing_probe.py')
    code=survey(reference)
    smoke=None
    if args.model_smoke:
        pins[str((MOD/ECONOMY_UI).resolve())]=sha(MOD/ECONOMY_UI)
        encoder=read(HERE/'economy_component_probe.lua').split('for _,target in ipairs(CSC_COMPONENT_TARGETS)do',1)[0]
        smoke=encoder[encoder.index('local function encode'):]
        smoke+='\nlocal activeFacts,activeModel=CSC_AI_EconomyFacts,CSC_AI_EconomyModel\nlocal CSC_AI_EconomyFacts,CSC_AI_EconomyModel\n'
        for name in('CSC_AI_EconomyFacts.lua','CSC_AI_EconomyModel.lua'):
            path=MOD/'Lua_UI/AI'/name;pins[str(path.resolve())]=sha(path)
            smoke+='\ndo\n'+read(path)+'\nend\n'
        smoke+='''
local rows={};local placement=assert(CSC_AI_QuarterPlacement)
for _,pid in ipairs('''+lua(plan.identity['original_ai'])+''')do
 local snapshot=CSC_AI_EconomyFacts.New(assert(Players[pid]),placement,assert(ExposedMembers.CSC_Adjacency),{horizon=50})
 for _,chain in ipairs(snapshot.chains)do
  local site=assert(chain.economy,'Existing chain economy unavailable')
  assert(site.service==nil,'Services entered ordinary placement smoke')
  local result=CSC_AI_EconomyModel.Forecast(site,function()return 0 end)
  local suppliers,legs,worked,workingCities,inputStreams,returnStreams,specialistStreams=0,0,0,0,0,0,0
  for _,s in ipairs(site.suppliers)do
   assert(s.transactions,'Missing canonical material map');suppliers=suppliers+1
   if s.worked then worked=worked+1 end
   if s.city then workingCities=workingCities+1 end
   for _,tx in pairs(s.transactions)do legs=legs+#tx.legs end
  end
  for _,stream in ipairs(result.streams)do
   if stream.id:find('material:',1,true)==1 then
    if stream.recipientBuilding then inputStreams=inputStreams+1 else returnStreams=returnStreams+1 end
   elseif stream.id:find('specialist-',1,true)==1 then specialistStreams=specialistStreams+1 end
  end
  rows[#rows+1]={player=pid,city=chain.city:GetID(),quarter=chain.profile.key,
   suppliers=suppliers,eligibleLegs=legs,workedSuppliers=worked,knownWorkingCities=workingCities,
   inputStreams=inputStreams,returnStreams=returnStreams,streams=#result.streams,omissions=#result.omissions,
   specialistWorkers=site.specialists and site.specialists.workers or 0,
   specialistCity=site.specialists and site.specialists.city,specialistStreams=specialistStreams}
 end
end
assert(#rows>0,'No actual chain sites sampled')
print('CSC_MATERIAL_MODEL_SMOKE='..encode({verified=true,turn=Game.GetCurrentGameTurn(),chains=rows}))
'''
        (out/'model-smoke.lua').write_text(smoke,encoding='utf-8')
    (out/'diagnostic.sql').write_text(sql,encoding='utf-8')
    (out/'diagnostic.lua').write_text(code,encoding='utf-8')
    write_json(out/'protocol.json',dict(diagnostic=True,zero_turn=not(native_baseline or native_treatment),at=args.at,production_population_sql=True,
        production_fixed_sql=True,native_graph_scope='all_csc',reference_graph=str(args.reference_graph),
        legacy_refresh_isolated=True,no_orders=True,source_pins=pins,lgd=False,
        model_smoke_isolated=bool(smoke),ui_economy_facts_overlay=bool(smoke),model_smoke_price='zero diagnostic; no bids',
        ce_overlay_sha256=ce_sha,customer_native_baseline=native_baseline,
        customer_native_treatment=str(native_treatment)if native_treatment else None,
        diagnostic_ordinary_turns_advanced=(2 if native_mode=='early'and native_treatment else 1)if native_baseline or native_treatment else 0))
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
            # Local, explicitly pinned native API candidate. The qualified source
            # package is immutable; cleanup removes this diagnostic copy only.
            if item['role']=='ce'and ce_dll:
                shutil.copyfile(ce_dll,item['install']/'Binaries/Win64'/DLL)
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
                if smoke:shutil.copyfile(MOD/ECONOMY_UI,item['install']/ECONOMY_UI)
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
        if ce_dll:
            require(sha(ce['install']/'Binaries/Win64'/DLL)==ce_sha,'Loaded CE overlay changed')
            from interval_pricing_probe import run as interval_probe
            interval_probe(c,out,plan.identity['original_ai'])
        with sqlite3.connect(database.resolve().as_uri()+'?mode=ro',uri=True)as db:
            loaded_fixed=transaction_graph(db,'fixed')
            loaded_all=transaction_graph(db,'all_csc')
        write_json(out/'loaded-all-csc-native-graph.json',loaded_all)
        all_effects=dict(verified=original_all==loaded_all,rows=sum(map(len,loaded_all.values())))
        write_json(out/'all-csc-native-equivalence.json',all_effects)
        require(all_effects['verified'],'Native CSC graph changes outside the declared migration')
        write_json(out/'loaded-fixed-native-graph.json',loaded_fixed)
        fixed=dict(verified=original_fixed==loaded_fixed,rows=sum(map(len,loaded_fixed.values())))
        write_json(out/'fixed-native-equivalence.json',fixed)
        require(fixed['verified'],'Fixed native graph changes the QAed loaded rules')
        result=c.cmd(code,'CSC_CustomerPopulationReturns','population-gameplay-equivalence')
        (out/'gameplay-equivalence.txt').write_text(result,encoding='utf-8')
        match=re.search(r'CSC_POPULATION_RESULT=([^\r\n]+)',result);require(match,'Missing gameplay result')
        proof=json.loads(match[1]);require(proof['verified']and proof['turn']==args.at,'Gameplay equivalence failed')
        if route_legacy:
            from route_catalogue_probe import run as route_probe
            route_result=route_probe(c,out/'routes',route_legacy,plan.identity['original_ai']if args.joint_route_smoke else None,
                                     args.customer_world_smoke)
        if smoke:
            started=time.perf_counter()
            raw=c.cmd(smoke,'CSC_AI_BakersGameplay','material-model-smoke')
            elapsed=time.perf_counter()-started
            (out/'model-smoke.txt').write_text(raw,encoding='utf-8')
            match=re.search(r'CSC_MATERIAL_MODEL_SMOKE=([^\r\n]+)',raw);require(match,'Missing material model smoke result')
            result=json.loads(match[1]);require(result['verified']and result['turn']==args.at,'Model smoke failed')
            write_json(out/'model-smoke.json',result)
            write_json(out/'model-smoke-runtime.json',dict(wall_seconds=elapsed,
                scope='Five-player mature-world Facts plus isolated zero-price Model, including console transport',
                pricing='Zero diagnostic, no native pricing or bids',chains=len(result['chains'])))
        if native_baseline or native_treatment:
            from customer_native_probe import run as native_probe
            native_probe(s,c,out/'customer-native',args.dependencies,route_result['customer_world'],native_treatment,native_mode)
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
    p.add_argument('--reference-graph',type=Path)
    p.add_argument('--ce-dll',type=Path,help='Explicit read-only pricing API candidate, installed only in the isolated replay copy')
    p.add_argument('--ce-sha',help='Required SHA-256 for --ce-dll')
    p.add_argument('--customer-native-baseline',action='store_true',help='One ordinary turn with passive customer comparison receipts; holds normal CE publication')
    p.add_argument('--customer-native-treatment',type=Path,help='Matched baseline result for one guarded diagnostic customer adjustment and one ordinary turn')
    p.add_argument('--customer-native-mode',choices=('late','early'),default='late',help='Diagnostic transport; early arm advances two turns to include fresh evaluation')
    p.add_argument('--model-smoke',action='store_true',help='Isolated current Facts/Model pass over actual saved-world chains; no bids')
    p.add_argument('--joint-route-smoke',action='store_true',help='With --route-smoke --model-smoke, qualify current joint route ledger using zero diagnostic prices')
    p.add_argument('--customer-world-smoke',action='store_true',help='Also quote admitted customer footprints with the real CE pricing API; no published bids')
    p.add_argument('--route-smoke',action='store_true',help='Compare isolated original/current UI packets and read native trader operation clocks; no submitted operations')
    run(p.parse_args())
