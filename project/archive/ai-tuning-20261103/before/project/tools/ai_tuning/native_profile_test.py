"""Bounded observation-only test of installed CSC/RH assistance.

The shared maintained controller owns finite autoplay/transport/playback guards.
This driver only configures a world, installs read-only observers, exports saved
receipts and outcomes, and restores the exact pre-test preferences/package.
"""
import argparse,hashlib,importlib.util,json,os,re,shutil,sqlite3,subprocess,sys,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];AI=ROOT/'project/tools/ai_baseline'
CSC='c5e66bd1-d804-443b-ac3d-1917a20dba3c';RH='2501be3e-9780-4e9f-9506-4ff71cf076cb'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.tmp');tmp.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8');tmp.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(root):return {str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size}for p in root.rglob('*')if p.is_file()}
def adapter(path):
 sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location('profile_controller_adapter',path);c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c);return c
def parse(raw,marker):return json.loads(re.findall(re.escape(marker)+r'=([^\r\n]+)',raw)[-1])

# Read only: no planner invocation or native economic commands. Saved receipts
# remain authoritative if the UI is behind; a pending transaction is not retried.
RECEIPTS=r'''
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 if t~='table'then return 'null'end
 local out,n,array={},0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(out,',')..'}'
end
local prefix='CSC_AI_ASSISTANCE_V1_'
local function get(k,default)local v=Game:GetProperty(prefix..k);if v==nil then return default end;return v end
local out={turn=Game.GetCurrentGameTurn(),totals=get('TOTALS',{tiles=0,cost=0,own=0,subsidy=0,foundations=0}),receipts={},foundations={},pending={},errors={},players={}}
for _,token in ipairs(get('RECEIPT_INDEX',{}))do out.receipts[#out.receipts+1]=get('RECEIPT_'..token)end
for _,key in ipairs(get('FOUNDATION_INDEX',{}))do out.foundations[#out.foundations+1]={key=key,value=get('FOUNDATION_'..key)}end
for _,p in ipairs(PlayerManager.GetAliveMajors())do local id=p:GetID()
 local pending=get('PENDING_'..id);if pending then out.pending[tostring(id)]=pending end
 local error=get('ERROR_'..id);if error then out.errors[#out.errors+1]={player=id,value=error}end
 out.players[#out.players+1]={player=id,gold=p:GetTreasury():GetGoldBalance(),last_cycle=get('TURN_'..id),eligible_UI=ExposedMembers.CSC_AI_AssistanceUI.IsAIPlayer(id)}
end
local roles=ExposedMembers.CSC_RH_CustomerRoles
if roles and roles.foundation_priority then out.foundation_priority=roles.foundation_priority end
print('CSC_PROFILE_RECEIPTS='..json(out))
'''

def flags(r,label):
 raw=r.cmd("local a={};for _,m in ipairs(Modding.GetInstalledMods())do if m.Source=='Mod'and not m.Official then a[m.Id]=a[m.Id]or m.Enabled;print('CSC_PROFILE_ENTRY',m.Id,tostring(m.SubscriptionId or ''),tostring(m.SourceFileName or ''),tostring(m.Enabled))end end;local entries={};for k,v in pairs(a)do entries[#entries+1]='\"'..k..'\":'..tostring(v)end;print('CSC_PROFILE_PREFS={'..table.concat(entries,',')..'}');print('CSC_PROFILE_AUTO',Automation.IsAutoStartEnabled());",'MainMenu',label)
 rows=[dict(id=i,subscription=sub,file=file,enabled=enabled=='true')for i,sub,file,enabled in re.findall(r'CSC_PROFILE_ENTRY\s+([^\s]+)\t([^\t\r\n]*)\t([^\t\r\n]*)\t(true|false)',raw)]
 return dict(mods=parse(raw,'CSC_PROFILE_PREFS'),auto_start=re.search(r'CSC_PROFILE_AUTO\s+(true|false)',raw)[1]=='true',entries=sorted(rows,key=lambda v:(v['id'],v['subscription'],v['file'])))

def restore_preferences(r,out):
 original=read(out/'original-preferences.json')
 entries=','.join('['+json.dumps(v['id']+'|'+v['subscription']+'|'+v['file'])+']='+str(v['enabled']).lower()for v in original['entries'])
 code='local wanted={'+entries+"};local function key(m)return m.Id..'|'..tostring(m.SubscriptionId or '')..'|'..tostring(m.SourceFileName or '')end;local disable={};for _,m in ipairs(Modding.GetInstalledMods())do if wanted[key(m)]==false and m.Enabled then disable[#disable+1]=m.Handle end end;if #disable>0 then Modding.DisableMod(disable)end;for _,m in ipairs(Modding.GetInstalledMods())do if wanted[key(m)]==true and not m.Enabled then Modding.EnableMod(m.Handle,true)end end;Automation.SetAutoStartEnabled("+str(original['auto_start']).lower()+');'
 r.cmd(code,'MainMenu','restore-exact-subscription-preferences');r.wait('MainMenu',90)
 actual=flags(r,'verify-exact-subscription-preferences');assert actual==original
 write(out/'preferences-restored.json',dict(verified=True,mods=len(actual['mods']),installed_entries=len(actual['entries']),auto_start=actual['auto_start']))

def configure(r,out,profile="RH"):
 assert profile in ("RH","BASIC")
 allowed=(CSC,RH)if profile=="RH"else(CSC,)
 original=flags(r,'save-menu-before-configuration')
 if(out/'original-preferences.json').exists():
  wanted=read(out/'original-preferences.json')
  if 'entries'not in wanted:
   wanted['entries']=[dict(v,enabled=wanted['mods'][v['id']])for v in original['entries']]
   write(out/'original-preferences.json',wanted)
 else:write(out/'original-preferences.json',original)
 # Enabling content may rebuild the frontend before its ACK. Never resend a
 # mutation after ambiguity; verify flags through the newly discovered context.
 def once(code,label):
  try:r.cmd(code,'MainMenu',label)
  except RuntimeError as e:write(out/(label+'-ack-warning.json'),dict(error=str(e),no_resend=True))
  r.wait('MainMenu',90)
 allowed_lua="m.Id=='"+CSC+"'"+("or(m.Id=='"+RH+"'and tostring(m.SubscriptionId)=='3792072489')"if profile=="RH"else"")
 once("local a={};for _,m in ipairs(Modding.GetInstalledMods())do if m.Source=='Mod'and not m.Official and m.Enabled and not("+allowed_lua+")then a[#a+1]=m.Handle end end;if #a>0 then Modding.DisableMod(a)end;",'disable-unrelated-mods-once')
 for identifier in allowed:
  wanted=flags(r,'check-mod-before-enable-'+identifier)['mods']
  if not wanted.get(identifier):once("local best=nil;for _,m in ipairs(Modding.GetInstalledMods())do if m.Id=='"+identifier+"'and(m.Id~='"+RH+"'or tostring(m.SubscriptionId)=='3792072489')then assert(not best,'Ambiguous required mod entry');best=m end end;assert(best,'Required mod missing');print('CSC_PROFILE_ENABLE',best.Id,best.Name,best.SubscriptionId);Modding.EnableMod(best.Handle,true);",'enable-required-mod-once-'+identifier)
 selected=flags(r,'verify-CSC-and-RH-only');assert all(selected['mods'].get(k)for k in allowed)and not any(v for k,v in selected['mods'].items()if k not in allowed)
 raw=r.cmd("for _,m in ipairs(Modding.GetInstalledMods())do if m.Enabled then print('CSC_PROFILE_SELECTED',m.Id,m.SubscriptionId,m.Name,m.Source,m.Official)end end;",'MainMenu','selected-content-and-expansions')
 assert profile!='RH'or 'v5.097' in raw,'Require the reviewed RH5 beta, not a same-ID older Workshop copy'
 write(out/'native-menu-configuration.json',dict(verified=True,enabled_mod_ids=[k for k,v in selected['mods'].items()if v],profile=profile,RH_version_name_verified='v5.097'if profile=='RH'else None,expansion_ruleset='RULESET_EXPANSION_2',subsidies=True,assistance=True))

def restore_package(c,out):
 assert not[p for p in c.d.processes()if p['name'].startswith('CivilizationVI')]
 deploy=out/'deployment';before=read(deploy/'original-installed-manifest.json');expected=read(deploy/'expected-installed-manifest.json');actual=manifest(c.d.INSTALLED)
 assert actual==expected,'Installed files changed while running; preserve and reconcile instead of overwrite'
 for relative in read(deploy/'deployment.json')['changed']:
  p=c.d.INSTALLED/relative;p.resolve().relative_to(c.d.INSTALLED.resolve())
  if relative in before:shutil.copy2(deploy/'backup'/relative,p)
  else:assert sha(p)==expected[relative]['sha256'];p.unlink()
 assert manifest(c.d.INSTALLED)==before
 write(out/'package-restored.json',dict(verified=True,pretest_package_equal=True,files=len(before),all_Civ_absent=True))

def live_worker(a):
 c=adapter(a.controller_adapter);d=c.d;out=a.output.resolve();parent=Path(a.live_parent);d.ROOT=out
 from full_game_controller.discovery import discover_contexts
 from full_game_controller.checkpoint import save_inactive_boundary
 from full_game_controller.continuation import world_signature
 from service_planner.boundary_bundle import capture
 assert read(parent/'supervisor.json')['exit_code']==1 and not(out/'worker-started.json').exists()
 identity=read(parent/'game-process.json');live=[p for p in d.processes()if p['pid']==identity['pid']and p['created']==identity['created']and p['name']==identity['name']]
 assert len(live)==1,'Exact original native process required'
 expected=read(out/'deployment/expected-installed-manifest.json');assert manifest(d.INSTALLED)==expected
 Controller=c.maintained.make_controller(c.full.Fresh,diagnostics=d,boundary_decision=c.b.boundary_decision,tuner_port=lambda:c.b.tuner.PORT,prepare_output=c.prepare_output,state_discovery=discover_contexts)
 r=Controller(out);r.seq=20000000;r.game_pid=identity['pid'];r.study_endpoint=150;r.allow_observer_warning_dismissal=True;r.allow_one_more_turn=True;r.allow_observer_congress_review=True
 write(out/'game-process.json',identity);write(out/'worker-started.json',dict(pid=os.getpid(),time=time.time(),live_existing_process=True,no_load=True,no_host=True))
 write(out/'job-status.json',dict(status='reconciling-live125',worker_pid=os.getpid(),native_pid=r.game_pid,endpoint=150))
 try:
  r.ready(125,'live125-reconciliation')
  value=parse(r.cmd(RECEIPTS,'CSC_AdjacencyGameplay','live125-exact-receipts'),'CSC_PROFILE_RECEIPTS');assert value==read(parent/'receipts/turn-125.json'),'Economic records changed; reconcile before continuing'
  assert not value['errors']and not value['pending']
  bundle=capture(r,out,write,125);assert world_signature(bundle['primary'])==world_signature(read(parent/'game-01/turn-125.json'))
  assert len(bundle['research']['history'])==620 and not bundle['research']['errors']
  oldpins=read(parent/'executed-source-pins.json');changes=[name for name,digest in oldpins.items()if sha(Path(name))!=digest]
  assert {Path(n).name for n in changes}<= {'checkpoint.py','native_profile_test.py'},changes
  pins={name:sha(Path(name))for name in oldpins}
  for i,name in enumerate(pins):dest=out/'source-version'/f'{i:04d}-{Path(name).name}';dest.parent.mkdir(exist_ok=True);shutil.copy2(name,dest)
  write(out/'executed-source-pins.json',pins);write(out/'initialization.json',dict(read(parent/'initialization.json'),live_resume_turn=125,original_initialization=str(parent/'initialization.json')))
  if(parent/'checkpoint125-save-gap.json').exists():
   saved=read(parent/'checkpoint125-save-gap.json');write(out/'checkpoint125-save-gap.json',saved)
   d.checkpoint('live125-continued-with-explicit-save-gap')
  else:
   saved=save_inactive_boundary(r,turn=125,name='CSC_RH5_T125',native_directory=d.SAVES,archive=out/'exact-checkpoints/turn-125.Civ6Save');write(out/'exact-checkpoints/turn-125.json',saved)
   d.checkpoint('live125-first-successful-save')
  write(out/'live-resume-validation.json',dict(verified=True,turn=125,native_pid=r.game_pid,same_process=True,loads=0,new_worlds=0,AI_replay=0,economic_records_equal=True,world_equal=True,research_rows=620,observers_reset=False,old_failed_assert_before_save=True,controller_only_changed=changes,save=saved))
  write(out/'job-status.json',dict(status='running',worker_pid=os.getpid(),native_pid=r.game_pid,endpoint=150))
  r.last_interval_turn=125
  for turn in(130,135,140,145,150):
   r.play(turn);value=parse(r.cmd(RECEIPTS,'CSC_AdjacencyGameplay','read-installed-receipts-'+str(turn)),'CSC_PROFILE_RECEIPTS');assert value['turn']==turn
   write(out/'receipts'/f'turn-{turn:03d}.json',value)
   assert not value['errors']and not value['pending']
   assert next(v for v in value['players']if v['player']==0)['last_cycle']==24
   if turn==150:
    bundle=capture(r,out,write,turn)
    for key,folder in(('primary','game-01'),('chain','chain-metrics'),('research','research'),('builders','builders'),('quarters','quarter-sites')):write(out/folder/f'turn-{turn:03d}.json',bundle[key])
    d.checkpoint('outcome-'+str(turn))
    saved=save_inactive_boundary(r,turn=turn,name='CSC_RH5_T'+str(turn),native_directory=d.SAVES,archive=out/'exact-checkpoints'/f'turn-{turn:03d}.Civ6Save');write(out/'exact-checkpoints'/f'turn-{turn:03d}.json',saved)
    assert manifest(d.INSTALLED)==expected and all(sha(Path(n))==v for n,v in pins.items())
    write(out/'candidate-runtime-verification.json',dict(verified=True,pins_unchanged=len(pins),files=len(expected),native_endpoint=150))
   write(out/'live-status.json',dict(turn=turn,endpoint=150,worker_pid=os.getpid(),native_pid=r.game_pid,status='running',totals=value['totals'],pending=value['pending'],errors=value['errors'],time=time.time()))
  r.cmd('Events.ExitToMainMenu();','PlotInfo','normal-return-menu-after150',check=False);r.wait('MainMenu',120);restore_preferences(r,out)
  write(out/'exit-issued.json',dict(once=True,pid=r.game_pid,time=time.time()))
  try:r.cmd('assert(type(ExitOK)=="function");ExitOK();','FrontEndPopup','normal-exit-after150',check=False)
  except Exception as e:write(out/'exit-ack-warning.json',dict(error=str(e),no_resend=True))
  for _ in range(45):
   if not[p for p in d.processes()if p['name'].startswith('CivilizationVI')]:break
   time.sleep(1)
  else:raise RuntimeError('Native still alive; no runtime restoration')
  restore_package(c,out);write(out/'job-status.json',dict(status='complete',native_endpoint=150,exit_code=0,time=time.time()))
 except BaseException as e:
  write(out/'failure.json',dict(error=str(e),traceback=traceback.format_exc(),no_mutations_resent=True))
  try:r.preserve_telemetry();d.checkpoint('failure-preserved')
  except Exception as x:write(out/'preservation-warning.json',dict(error=str(x)))
  write(out/'job-status.json',dict(status='attention',worker_pid=os.getpid(),native_pid=r.game_pid,error=str(e),endpoint=150,game_left_for_reconciliation=True));raise

def capture_customer_forecast(r,out,turn):
 """Scheduled read-only UI controls, after an exact checkpoint is preserved."""
 code=Path(__file__).with_name('profile_customer_forecast.lua').read_text(encoding='utf-8').replace('__TARGET_TURN__',str(turn))
 value=parse(r.cmd(code,'PlotInfo','customer-forecast-controls-'+str(turn)),'CSC_PROFILE_CUSTOMER_FORECAST')
 assert value['requested_core_turn']==turn and value['ui_turn']in(turn,turn-1)
 write(out/'customer-forecast-controls'/f'turn-{turn:03d}.json',value)
 assert not value['errors']and value['controls']['failed']==0,('Native customer forecast value mismatch; exact checkpoint already preserved',value['controls'])
 return value

def validate_workshop_database(db):
 """Verify the active source-property path before AI, without a plot counter."""
 assert db.execute("SELECT COUNT(*) FROM DistrictModifiers WHERE DistrictType='DISTRICT_CSC_TAILORS_QUARTER'AND ModifierId LIKE 'MOD_CSC_RH_WORKSHOP_FORECAST_%'").fetchone()[0]==2
 assert dict(db.execute("SELECT ModifierId,Value FROM ModifierArguments WHERE Name='Amount'AND ModifierId LIKE 'MOD_CSC_RH_WORKSHOP_FORECAST_%'"))=={'MOD_CSC_RH_WORKSHOP_FORECAST_BASE':'80','MOD_CSC_RH_WORKSHOP_FORECAST_BOTH_EXTRA':'40'}
 for key in('BASE','BOTH_EXTRA'):
  required={'REQ_CSC_AI_SUPPLY_AI','REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI','REQ_CSC_RH_WORKSHOP_FACT_BASE'}
  if key=='BOTH_EXTRA':required.add('REQ_CSC_RH_WORKSHOP_FACT_SPEC')
  actual={r[0]for r in db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?',('REQSET_CSC_RH_WORKSHOP_OWNER_'+key,))}
  assert actual==required,('Wrong native Workshop source-fact gates',key,actual)
 for key in('BASE','SPEC'):
  rid='REQ_CSC_RH_WORKSHOP_FACT_'+key
  assert db.execute('SELECT RequirementType FROM Requirements WHERE RequirementId=?',(rid,)).fetchone()==('REQUIREMENT_PLOT_PROPERTY_MATCHES',)
  assert dict(db.execute('SELECT Name,Value FROM RequirementArguments WHERE RequirementId=?',(rid,)))=={'PropertyName':'CSC_RH_WORKSHOP_'+key+'_PRESENT','PropertyMinimum':'1'},('Wrong Workshop fact property',key)
 assert db.execute("SELECT COUNT(*) FROM Requirements WHERE RequirementId LIKE 'REQ_CSC_RH_WORKSHOP_%'AND RequirementType='REQUIREMENT_COLLECTION_COUNT_ATLEAST'").fetchone()[0]==0


def capture_workshop_forecast(r,out,turn):
 """Read-only UI scope/value/legality controls after the boundary export/save."""
 code=Path(__file__).with_name('profile_workshop_forecast.lua').read_text(encoding='utf-8').replace('__TARGET_TURN__',str(turn))
 value=parse(r.cmd(code,'PlotInfo','workshop-forecast-controls-'+str(turn)),'CSC_PROFILE_WORKSHOP_FORECAST')
 assert value['requested_core_turn']==turn and value['ui_turn']in(turn,turn-1)
 write(out/'workshop-forecast-controls'/f'turn-{turn:03d}.json',value)
 assert not value['errors']and value['controls']['failed']==0,('Native Workshop forecast mismatch; boundary preserved first',value['controls'])
 return value

def worker(a):
 assert not a.workshop_forecast_controls or(a.profile=='RH'and a.customer_forecast_controls and not a.live_parent),'Workshop controls require the fresh RH role-gated candidate'
 assert not a.customer_forecast_controls or(a.profile=='RH'and not a.live_parent),'Customer controls belong only to fresh RH candidate arms'
 assert not getattr(a,'strategy_building_controls',False)or(a.profile=='RH'and a.workshop_forecast_controls and not a.live_parent),'Strategy controls require fresh RH Workshop candidate'
 if a.live_parent:
  assert a.profile=='RH','The legacy live125 recovery belongs only to the original RH pilot'
  return live_worker(a)
 c=adapter(a.controller_adapter);d=c.d;out=a.output.resolve();d.ROOT=out
 assert not(out/'worker-started.json').exists()
 running=[p for p in d.processes()if p['name'].startswith('CivilizationVI')]
 assert (len(running)==1 and running[0]['pid']==a.attach_menu)if a.attach_menu else not running
 expected=read(out/'deployment/expected-installed-manifest.json');assert manifest(d.INSTALLED)==expected
 from full_game_controller.discovery import discover_contexts
 from full_game_controller.checkpoint import save_inactive_boundary
 from service_planner.boundary_bundle import capture
 Controller=c.maintained.make_controller(c.full.Fresh,diagnostics=d,boundary_decision=c.b.boundary_decision,tuner_port=lambda:c.b.tuner.PORT,prepare_output=c.prepare_output,state_discovery=discover_contexts)
 r=Controller(out);r.seq=10000000;r.study_endpoint=a.endpoint;r.allow_observer_warning_dismissal=True;r.allow_one_more_turn=True;r.allow_observer_congress_review=True
 from full_game_controller.session import NativeSession
 from full_game_controller.windows_process import HeldProcess,native_inventory
 parent=HeldProcess(os.getppid());allowed_owner=parent.identity;parent.close()
 session=NativeSession(out,r,inventory=lambda:native_inventory(allowed=(allowed_owner,)),hold=HeldProcess,write=write)
 write(out/'worker-started.json',dict(pid=os.getpid(),time=time.time(),endpoint=a.endpoint,mutation_owner='installed CSC_AI_Assistance only'))
 hint=out/'sdk-working/steam_appid.txt';hint.parent.mkdir();hint.write_text('289070\n',encoding='ascii')
 native=None;loaded=False;complete=False
 try:
  if a.attach_menu:session.start(attach_pid=a.attach_menu)
  else:
   def launch():
    process=subprocess.Popen([str(d.BINARY/'CivilizationVI_DX12.exe')],cwd=hint.parent,creationflags=subprocess.CREATE_NO_WINDOW)
    return HeldProcess.from_popen(process)
   native=session.start(launch)
  identity=next(p for p in d.processes()if p['pid']==r.game_pid);write(out/'game-process.json',identity)
  write(out/'job-status.json',dict(status='starting',worker_pid=os.getpid(),native_pid=r.game_pid,endpoint=a.endpoint))
  r.wait('MainMenu',240);hint.unlink();configure(r,out,a.profile)
  leaders=['LEADER_TOMYRIS','LEADER_AMANITORE','LEADER_TAMAR','LEADER_GENGHIS_KHAN','LEADER_JOAO_III','LEADER_HOJO']
  if a.resume_checkpoint:
   meta=read(Path(a.resume_checkpoint));source=Path(meta['native_save'])
   assert meta['verified']and meta['turn']in(1,25)and sha(source)==meta['sha256']
   write(out/'load-issued.json',dict(once=True,source=str(source),source_sha256=meta['sha256'],source_turn=meta['turn'],new_worlds=0,AI_replay=0))
   session.issue_load_once(source,sha256=meta['sha256'],native_directory=d.SAVES,turn=meta['turn'])
  else:
   code="GameConfiguration.SetToDefaults();GameConfiguration.SetRuleSet('RULESET_EXPANSION_2');BuildHeadlessGameSetup();RebuildPlayerParameters(true);GameSetup_RefreshParameters();MapConfiguration.SetScript('Continents.lua');MapConfiguration.SetMapSize('MAPSIZE_SMALL');GameConfiguration.SetParticipatingPlayerCount(6);GameConfiguration.SetValue('CITY_STATE_COUNT',9);GameConfiguration.SetGameSpeedType('GAMESPEED_ONLINE');GameConfiguration.SetHandicapType('DIFFICULTY_PRINCE');GameConfiguration.SetValue('GAME_SYNC_RANDOM_SEED',GAME_SEED_PLACEHOLDER);MapConfiguration.SetValue('RANDOM_SEED',MAP_SEED_PLACEHOLDER);MapConfiguration.SetValue('resources',2);GameConfiguration.SetValue('CSC_INCLUDE_ANIMAL_RESOURCES',1);GameConfiguration.SetValue('CSC_REMOVE_UNUSED_MODDED_RESOURCES',1);GameConfiguration.SetValue('CSC_AI_ASSISTANCE',1);GameConfiguration.SetValue('CSC_AI_SUBSIDIES',1);GameConfiguration.SetValue('CSC_RESOURCE_MAP_ASSISTANCE',1);GameConfiguration.SetValue('CSC_MATERIAL_MAP_DIAGNOSTICS',false);GameConfiguration.SetValue('GAMEMODE_MONOPOLIES',false);GameConfiguration.SetStartEra(DB.MakeHash('ERA_ANCIENT'));"
   code=code.replace('GAME_SEED_PLACEHOLDER',str(a.game_seed)).replace('MAP_SEED_PLACEHOLDER',str(a.map_seed))
   code+=''.join('PlayerConfigurations['+str(i)+']:SetLeaderTypeName('+json.dumps(leader)+');'for i,leader in enumerate(leaders))
   code+="assert(GameConfiguration.GetRuleSet()=='RULESET_EXPANSION_2');assert(GameConfiguration.GetGameSpeedType()==DB.MakeHash('GAMESPEED_ONLINE'),'Online speed mismatch');ReleasePlayerParameters();HideGameSetup();Automation.SetAutoStartEnabled(true);Network.HostGame(ServerType.SERVER_TYPE_NONE);"
   write(out/'host-issued.json',dict(once=True,worlds=1,map_seed=a.map_seed,game_seed=a.game_seed,endpoint=a.endpoint,expansions=['Rise and Fall','Gathering Storm'],time=time.time()))
   session.issue_once('host',code,'MainMenu',label='host-one-RH5-CSC-world')
  r.wait('CSC_AdjacencyGameplay',300);r.wait('CSC_AI_Assistance',120);r.wait('PlotInfo',120);loaded=True
  start=meta['turn']if a.resume_checkpoint else 1
  r.ready(start,'source-before-observers')
  preflight="local mode=nil;for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then mode=row.Mode end end;assert(mode=='PROFILE_PLACEHOLDER');assert(ExposedMembers.CSC_AI_Assistance and ExposedMembers.CSC_AI_AssistanceUI and type(ExposedMembers.CSC_AI_AssistanceUI.Read)=='function','Installed host/UI bridge missing');assert(GameInfo.Governors and GameInfo.Districts.DISTRICT_DAM and GameInfo.Units.UNIT_ROCK_BAND,'R&F / GS content missing');PROFILE_MOVEMENT_PLACEHOLDER;assert(WorldBuilder and type(WorldBuilder.CityManager)=='function','Paid assignment unavailable');assert(type(WorldBuilder.CityManager().SetPlotOwner)=='function');local function enabled(v)return v==1 or v==true or v=='1'end;assert(enabled(GameConfiguration.GetValue('CSC_AI_ASSISTANCE'))and enabled(GameConfiguration.GetValue('CSC_AI_SUBSIDIES')),'Assistance/subsidy settings missing');assert(ExposedMembers.CSC_AI_AssistanceUI.SupportsEconomics(),'Single-player economic UI guard failed');print('CSC_PROFILE_NATIVE_PREFLIGHT',mode);"
  preflight=preflight.replace('PROFILE_PLACEHOLDER',a.profile).replace('PROFILE_MOVEMENT_PLACEHOLDER',"assert(GameInfo.Modifiers.MOD_CSC_AI_BASIC_BUILDER_MOVEMENT~=nil,'Basic movement missing')"if a.profile=='BASIC'else"assert(GameInfo.Modifiers.MOD_CSC_AI_BASIC_BUILDER_MOVEMENT==nil,'Basic movement leaked into RH')")
  raw=r.cmd(preflight,'CSC_AdjacencyGameplay','native-profile-and-expansion-host-gates')
  assert 'CSC_PROFILE_NATIVE_PREFLIGHT' in raw
  if start==1:
   assert not(out/'initial-census.json').exists()
   raw=r.cmd(RECEIPTS+'\n'+Path(__file__).with_name('profile_initial_census.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','initial-full-map-and-setup-units')
   initial=parse(raw,'CSC_PROFILE_INITIAL');initial_receipts=parse(raw,'CSC_PROFILE_RECEIPTS')
   assert initial['turn']==1 and len(initial['plots'])==initial['width']*initial['height']
   assert not initial_receipts['receipts']and not initial_receipts['foundations']and not initial_receipts['pending']and not initial_receipts['errors']
   write(out/'initial-census.json',initial);write(out/'initial-receipts.json',initial_receipts)
  for path,label in((AI/'paired_observer.lua','primary'),(Path(__file__).with_name('profile_completion_observer.lua'),'quarter-completion'),(AI/'builder_observer.lua','builders'),(AI/'builder_export.lua','builder-export'),(Path(__file__).with_name('profile_research_observer.lua'),'research')):r.cmd(path.read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','install-readonly-'+label)
  src=sqlite3.connect((d.USER/'Cache/DebugGameplay.sqlite').as_uri()+'?mode=ro',uri=True);dst=sqlite3.connect(out/'native-gameplay.sqlite');src.backup(dst);src.close();dst.close()
  db=sqlite3.connect(out/'native-gameplay.sqlite');assert db.execute("SELECT Mode FROM CSC_AI_Profile WHERE Id='ACTIVE'").fetchone()==(a.profile,);
  if a.profile=='RH':assert db.execute("SELECT COUNT(*) FROM RHAITags WHERE YieldName='LOC_CSC_AI_PLACEMENT_NAME'").fetchone()[0]==1
  else:
   assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()==(30.0,)
   assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts'AND Item='UNIT_BUILDER'").fetchone()==(50,)
  if a.customer_forecast_controls:
   targets=1+db.execute("SELECT COUNT(DISTINCT CivUniqueBuildingType) FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_GRANARY'").fetchone()[0]
   assert db.execute("SELECT COUNT(*) FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_%'").fetchone()[0]==targets
   assert db.execute("SELECT COUNT(*) FROM BuildingModifiers WHERE ModifierId LIKE 'MOD_CSC_RH_CUSTOMER_FORECAST_ATTACH_%'").fetchone()[0]==2*targets

  if a.workshop_forecast_controls:validate_workshop_database(db)
  if getattr(a,'strategy_building_controls',False):
   from profile_strategy_coverage import validate_database
   write(out/'strategy-building-controls.json',validate_database(db))
  if getattr(a,'foundation_priority_controls',False):
   from profile_foundation_priority import validate_database
   write(out/'foundation-priority-controls.json',validate_database(db))
   probe=parse(r.cmd("local f=assert(ExposedMembers.CSC_RH_CustomerRoles).foundation_priority;assert(f and f.version==1 and f.registered==2 and #f.errors==0);print('CSC_FOUNDATION_READY={\"registered\":'..f.registered..'}');",'CSC_AdjacencyGameplay','foundation-registration-preflight'),'CSC_FOUNDATION_READY')
   write(out/'foundation-registration-controls.json',probe)
  db.close()
  if a.resume_checkpoint:
   from full_game_controller.continuation import world_signature
   source_root=Path(a.resume_checkpoint).parent.parent
   current=r.snapshot(1,start);reference=read(source_root/'game-01'/f'turn-{start:03d}.json')
   assert world_signature(current)==world_signature(reference),'Initial world changed'
   raw=r.cmd(RECEIPTS+"\nlocal rows={};for _,p in ipairs(PlayerManager.GetAliveMajors())do for _,u in p:GetUnits():Members()do rows[#rows+1]={player=p:GetID(),id=u:GetID(),type=u:GetType(),x=u:GetX(),y=u:GetY(),damage=u:GetDamage()}end end;print('CSC_PROFILE_UNITS='..json(rows));",'CSC_AdjacencyGameplay','verify-source1-world-Gold-units')
   receipts=parse(raw,'CSC_PROFILE_RECEIPTS');units=parse(raw,'CSC_PROFILE_UNITS')
   unit_reference=read(source_root/('initial1-units.json'if start==1 else 'resume-source-units.json'))
   assert sorted(units,key=lambda u:(u['player'],u['id']))==sorted(unit_reference,key=lambda u:(u['player'],u['id']))
   before=read(source_root/('initial1-receipts.json'if start==1 else 'resume-source-receipts.json'));assert {v['player']:v['gold']for v in receipts['players']}=={v['player']:v['gold']for v in before['players']}
   assert not receipts['receipts']and not receipts['foundations']and not receipts['pending']and not receipts['errors']
   write(out/'resume-validation.json',dict(verified=True,source_turn=start,source_sha256=meta['sha256'],world_equal=True,units_equal=True,Gold_equal=True,economic_actions_repeated=0,AI_turns_replayed=0,new_worlds=0))
  if a.resume_checkpoint and start>1:
   from full_game_controller.continuation import restore_observer
   research=read(source_root/'research'/f'turn-{start:03d}.json');builders=read(source_root/'builders'/f'turn-{start:03d}.json');primary=read(source_root/'game-01'/f'turn-{start:03d}.json')
   for field in('history','completions','defeats','errors','duplicate_callbacks'):
    restore_observer(r,'CSC_AdjacencyGameplay','CSC_SERIES_RESEARCH',field,research[field],c.b.old.v3.lua)
   restore_observer(r,'CSC_AdjacencyGameplay','CSC_SERIES_RESEARCH','seen',{str(v['turn'])+':'+str(v['player']):True for v in research['history']},c.b.old.v3.lua)
   restore_observer(r,'CSC_AdjacencyGameplay','CSC_BUILDERS','events',builders['events'],c.b.old.v3.lua)
   restore_observer(r,'CSC_AdjacencyGameplay','CSCBASE','events',primary['events'],c.b.old.v3.lua)
   # Copy immutable earlier observations; current start is a disclosed reload census.
   for folder in('game-01','chain-metrics','research','builders','quarter-sites','exact-checkpoints','receipts'):
    for path in(source_root/folder).glob('*'):
     match=re.search(r'turn-(\d+)',path.name)
     if path.is_file()and match and int(match[1])<start:
      target=out/folder/path.name;target.parent.mkdir(exist_ok=True);shutil.copy2(path,target)
   write(out/'inherited-observers.json',dict(verified=True,source=str(source_root),research_rows=len(research['history']),events_inherited_once=True,source_census='reload readback',discarded_native_intervals=[]))
  pins={}
  if a.customer_forecast_controls:
   extra=Path(__file__).with_name('profile_customer_forecast.lua');pins[str(extra.resolve())]=sha(extra)
  if a.workshop_forecast_controls:
   extra=Path(__file__).with_name('profile_workshop_forecast.lua');pins[str(extra.resolve())]=sha(extra)
  for module in list(sys.modules.values()):
   path=getattr(module,'__file__',None)
   if path:
    p=Path(path).resolve()
    if p.is_file()and p.suffix=='.py'and(str(p).startswith(str(ROOT))or str(p).startswith(str(a.controller_adapter.parent))):pins[str(p)]=sha(p)
  for p in list((AI/'full_game_controller').glob('*.lua'))+[AI/'paired_observer.lua',AI/'builder_observer.lua',AI/'builder_export.lua',Path(__file__).with_name('profile_research_observer.lua'),Path(__file__).with_name('profile_initial_census.lua'),Path(__file__).with_name('profile_completion_observer.lua')]+list((AI/'service_planner').glob('native_*metrics.lua'))+[AI/'service_planner/native_quarter_sites.lua',Path(__file__).resolve()]:pins[str(p.resolve())]=sha(p)
  for relative in expected:
   p=d.INSTALLED/relative
   if p.suffix.lower()in('.sql','.lua','.xml','.modinfo'):pins[str(p.resolve())]=sha(p)
  rh=Path(a.rh_package)
  for p in rh.rglob('*'):
   if p.is_file():pins[str(p.resolve())]=sha(p)
  for i,path in enumerate(pins):p=Path(path);archive=out/'source-version'/f'{i:04d}-{p.name}';archive.parent.mkdir(exist_ok=True);shutil.copy2(p,archive)
  # All adapter-owned native DB/source/observer gates above have passed.
  # Session records readiness only now; an ACK or context alone is insufficient.
  session.ready_after_issue(start,('GameCore_Tuner','PlotInfo','CSC_AdjacencyGameplay','CSC_AI_Assistance'),eligibility=lambda:True)
  write(out/'executed-source-pins.json',pins);write(out/'initialization.json',dict(verified=True,turn=start,RH_mode=a.profile=='RH',profile=a.profile,map_seed=a.map_seed,game_seed=a.game_seed,expansions=['Rise and Fall','Gathering Storm'],pins=len(pins),economic_backend='assisted quoted assignment',observer_only_external_driver=True,endpoint=a.endpoint,customer_forecast_controls=a.customer_forecast_controls,workshop_forecast_controls=a.workshop_forecast_controls,strategy_building_controls=getattr(a,'strategy_building_controls',False),foundation_priority_controls=getattr(a,'foundation_priority_controls',False)))
  write(out/'job-status.json',dict(status='running',worker_pid=os.getpid(),native_pid=r.game_pid,endpoint=a.endpoint))
  r.last_interval_turn=start
  turns=([1,5]+list(range(10,a.endpoint+1,5)))if start==1 else[start]+list(range(start+5,a.endpoint+1,5))
  for turn in turns:
   if turn>start:r.play(turn)
   value=parse(r.cmd(RECEIPTS,'CSC_AdjacencyGameplay','read-installed-receipts-'+str(turn)),'CSC_PROFILE_RECEIPTS');assert value['turn']==turn
   write(out/'receipts'/f'turn-{turn:03d}.json',value)
   if turn==start or turn%25==0 or turn==a.endpoint:
    bundle=capture(r,out,write,turn)
    for key,folder in(('primary','game-01'),('chain','chain-metrics'),('research','research'),('builders','builders'),('quarters','quarter-sites')):write(out/folder/f'turn-{turn:03d}.json',bundle[key])
    d.checkpoint('outcome-'+str(turn))
    saved=save_inactive_boundary(r,turn=turn,name='CSC_RH5_T'+str(turn),native_directory=d.SAVES,archive=out/'exact-checkpoints'/f'turn-{turn:03d}.Civ6Save');write(out/'exact-checkpoints'/f'turn-{turn:03d}.json',saved)
    if a.customer_forecast_controls:capture_customer_forecast(r,out,turn)
    if a.workshop_forecast_controls:capture_workshop_forecast(r,out,turn)
    assert manifest(d.INSTALLED)==expected and all(sha(Path(p))==v for p,v in pins.items()),'Frozen source/runtime changed'
   if turn==5:
    raw=r.cmd('CSC_BUILDERS.Export(5);','CSC_AdjacencyGameplay','read-Builder5');write(out/'builders/turn-005.json',parse(raw,'CSC_BUILDERS_SNAPSHOT'))
   write(out/'live-status.json',dict(turn=turn,endpoint=a.endpoint,worker_pid=os.getpid(),native_pid=r.game_pid,status='running',totals=value['totals'],pending=value['pending'],errors=value['errors'],time=time.time()))
   if turn>start:
    assert all(v.get('last_cycle')!=turn-1 for v in value['players']if v['player']==0),'Observer received a new intervention cycle'
   if getattr(a,'foundation_priority_controls',False):
    f=value.get('foundation_priority',{});assert f.get('registered')==2 and not f.get('errors'),('Foundation strategy diagnostics',f)
   assert not value['errors'],('Installed assistance errors',value['errors'])
   assert not value['pending'],('Unresolved economic transaction; preserve without resending',value['pending'])
   if(out/'stop-request.json').exists():raise RuntimeError('Human stop requested at safe boundary')
  complete=True
  session.close(restore_preferences=lambda:restore_preferences(r,out),restore_package=lambda:restore_package(c,out))
  write(out/'job-status.json',dict(status='complete',native_endpoint=a.endpoint,exit_code=0,time=time.time()))
 except BaseException as e:
  write(out/'failure.json',dict(error=str(e),traceback=traceback.format_exc(),no_ambiguous_mutation_repeated=True,time=time.time()))
  try:r.preserve_telemetry();d.checkpoint('failure-preserved')
  except BaseException as x:write(out/'preservation-warning.json',dict(error=str(x)))
  if isinstance(e,c.core.ObserverEliminated):
   try:close_eliminated_observer(c,r,out,session=session)
   except BaseException as cleanup_error:write(out/'observer-cleanup-warning.json',dict(error=str(cleanup_error),original_error=str(e)))
  write(out/'job-status.json',dict(status='attention',worker_pid=os.getpid(),native_pid=r.game_pid,error=str(e),endpoint=a.endpoint,game_left_for_reconciliation=True));raise
 finally:
  if hint.exists():hint.unlink()


def close_eliminated_observer(c,r,out,session=None):
 """Failure-only cleanup; never revive/switch roles or start more autoplay.

 An eliminated return player can leave the engine advancing with counter zero.
 Preserve the current journal (including any extra effects), then use the same
 supported menu/exit/restoration path. The failed job remains partial/exit1.
 """
 d=c.d;identity=read(out/'game-process.json')
 assert any(v['pid']==identity['pid']and v['created']==identity['created']for v in d.processes())
 phase=r.state_read('observer-elimination-before-exit');assert phase.get('player0_alive')is False
 write(out/'observer-elimination.json',dict(phase=phase,partial=True,no_role_switch=True,no_new_activation=True))
 try:
  receipt=parse(r.cmd(RECEIPTS,'CSC_AdjacencyGameplay','observer-terminal-economic-journal'),'CSC_PROFILE_RECEIPTS')
  write(out/'observer-terminal-receipts.json',receipt)
 except Exception as error:write(out/'observer-terminal-receipt-warning.json',dict(error=str(error),effects_unobserved=True))
 if session is not None:
  session.close(restore_preferences=lambda:restore_preferences(r,out),restore_package=lambda:restore_package(c,out))
  write(out/'observer-elimination-cleanup.json',dict(verified=True,partial_NOT_complete=True,all_Civ_absent=True,preferences_and_package_restored=True,shared_session=True))
  return
 r.cmd('Events.ExitToMainMenu();','PlotInfo','observer-eliminated-supported-menu',check=False);r.wait('MainMenu',120)
 restore_preferences(r,out)
 write(out/'exit-issued.json',dict(once=True,pid=r.game_pid,time=time.time(),reason='observer eliminated'))
 try:r.cmd('assert(type(ExitOK)=="function");ExitOK();','FrontEndPopup','observer-eliminated-supported-exit',check=False)
 except Exception as error:write(out/'exit-ack-warning.json',dict(error=str(error),no_resend=True))
 for _ in range(45):
  if not[v for v in d.processes()if v['name'].startswith('CivilizationVI')]:break
  time.sleep(1)
 else:raise RuntimeError('Native did not exit after observer loss; preserve runtime')
 restore_package(c,out)
 write(out/'observer-elimination-cleanup.json',dict(verified=True,partial_NOT_complete=True,all_Civ_absent=True,preferences_and_package_restored=True))

def supervise(a):
 out=a.output;assert not(out/'supervisor.json').exists()
 with(out/'worker.stdout.log').open('w',encoding='utf-8')as stdout,(out/'worker.stderr.log').open('w',encoding='utf-8')as stderr:
  workerp=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'worker','--output',str(out),'--controller-adapter',str(a.controller_adapter),'--rh-package',str(a.rh_package),'--endpoint',str(a.endpoint),'--attach-menu',str(a.attach_menu),'--resume-checkpoint',a.resume_checkpoint,'--live-parent',a.live_parent,'--profile',a.profile,'--map-seed',str(a.map_seed),'--game-seed',str(a.game_seed)]+(['--customer-forecast-controls']if a.customer_forecast_controls else[])+(['--workshop-forecast-controls']if a.workshop_forecast_controls else[])+(['--strategy-building-controls']if a.strategy_building_controls else[])+(['--foundation-priority-controls']if a.foundation_priority_controls else[]),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  base=dict(supervisor_pid=os.getpid(),worker_pid=workerp.pid,started_unix=time.time(),endpoint=a.endpoint,native_client_owner='worker only',automatic_restarts=0)
  while workerp.poll()is None:
   write(out/'supervisor.json',dict(base,status='running',updated_unix=time.time()));time.sleep(10)
  code=workerp.wait();status=read(out/'job-status.json')if(out/'job-status.json').exists()else{}
  write(out/'supervisor.json',dict(base,status='complete'if code==0 and status.get('status')=='complete'else'attention',exit_code=code,finished_unix=time.time()))

def main():
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['launch','supervise','worker']);p.add_argument('--output',type=Path,required=True);p.add_argument('--controller-adapter',type=Path,required=True);p.add_argument('--rh-package',type=Path,required=True);p.add_argument('--endpoint',type=int,default=150);p.add_argument('--attach-menu',type=int,default=0);p.add_argument('--resume-checkpoint',default='');p.add_argument('--study-root',type=Path);p.add_argument('--live-parent',default='');p.add_argument('--profile',choices=['BASIC','RH'],default='RH');p.add_argument('--map-seed',type=int,default=830405);p.add_argument('--game-seed',type=int,default=940411);p.add_argument('--customer-forecast-controls',action='store_true');p.add_argument('--workshop-forecast-controls',action='store_true');p.add_argument('--strategy-building-controls',action='store_true');p.add_argument('--foundation-priority-controls',action='store_true');a=p.parse_args()
 assert a.endpoint in(150,200),'Supported bounded profile endpoints are 150 and 200'
 assert not a.foundation_priority_controls or(a.profile=='RH'and a.customer_forecast_controls and not a.resume_checkpoint and not a.live_parent),'Foundation controls require a fresh RH arm'
 if a.mode=='worker':worker(a)
 elif a.mode=='supervise':supervise(a)
 else:
  assert a.output.is_dir()and(a.output/'deployment/deployment.json').exists();assert not(a.output/'supervisor.json').exists()
  with(a.output/'job.stdout.log').open('w')as stdout,(a.output/'job.stderr.log').open('w')as stderr:
   proc=subprocess.Popen([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'supervise','--output',str(a.output),'--controller-adapter',str(a.controller_adapter),'--rh-package',str(a.rh_package),'--endpoint',str(a.endpoint),'--attach-menu',str(a.attach_menu),'--resume-checkpoint',a.resume_checkpoint,'--live-parent',a.live_parent,'--profile',a.profile,'--map-seed',str(a.map_seed),'--game-seed',str(a.game_seed)]+(['--customer-forecast-controls']if a.customer_forecast_controls else[])+(['--workshop-forecast-controls']if a.workshop_forecast_controls else[])+(['--strategy-building-controls']if a.strategy_building_controls else[])+(['--foundation-priority-controls']if a.foundation_priority_controls else[]),stdout=stdout,stderr=stderr,creationflags=subprocess.CREATE_NO_WINDOW)
  write((a.study_root or a.output.parent)/'active-run.json',dict(root=str(a.output),status='starting',supervisor_pid=proc.pid,endpoint=a.endpoint,automation_id='PENDING',time=time.time()))
  print(json.dumps(dict(supervisor_pid=proc.pid,root=str(a.output),native_progress='PENDING')))
if __name__=='__main__':main()


