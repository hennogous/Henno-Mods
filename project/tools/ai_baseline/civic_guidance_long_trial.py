"""User-authorized natural Medieval71 ->250 matched CSC guidance comparison.

Six independent Service channels combine the C8/C9 valuation substrate with
C12's explicit Forbidden exit. Restart after a stopped strategy remains a
KNOWN limitation. No disposable opportunity or material fixture is injected.
Existing accepted placement/Builder/improvement tuning and old lists stay fixed.
"""
import collections
import hashlib
import json
import re
import shutil
import sqlite3
import time
import zlib
import sys
from pathlib import Path

import civic_modifier_trial as harness
import civic_modifier_custom_yield_trial as pristine
import civic_modifier_forbidden_trial as precedent
from fixed_research_trial import inventory
from paired_standard import HERE,read,sha
from run import ROOT,LOGS,SAVES,write

VERSION='natural-six-service-civic-guidance200-forbidden-v1'
TEST='CSC-natural-six-service-long-comparison'
TARGET=250
PLANS=[(1,'BAKERS',2,'CIVIC_FEUDALISM'),(2,'BAKERS',3,'CIVIC_MEDIEVAL_FAIRES'),
       (3,'BAKERS',4,'CIVIC_URBANIZATION'),(4,'TAILORS',2,'CIVIC_NAVAL_TRADITION'),
       (5,'TAILORS',3,'CIVIC_DIVINE_RIGHT'),(6,'TAILORS',4,'CIVIC_OPERA_BALLET')]
PREFIX='CSC_TEST_LONG_'
BASE_ARCHIVE_VERSION=harness.ModifierRunner.archive_version
CONTROLLER_REVISION='long-pair-v2-scoped-errors-frozen-source'
FROZEN_BASELINE=None


def baseline_path(rel):
    if FROZEN_BASELINE and (FROZEN_BASELINE/rel).exists():return FROZEN_BASELINE/rel
    return ROOT/'Civ Supply Chains'/rel


def classify_native_logs(folder):
    fatal=[];localization=[]
    for name in ('Lua.log','Database.log'):
        p=folder/name
        if not p.exists():continue
        for line in p.read_text(errors='replace').splitlines():
            if 'Runtime Error:' not in line and 'Gameplay ERROR' not in line and 'ERROR:' not in line:continue
            if name=='Database.log' and '[Localization] ERROR: UNIQUE constraint failed: LocalizedText.Language, LocalizedText.Tag' in line:
                localization.append(line[:500])
            else:fatal.append(line[:500])
    return {'passed':not fatal,'errors':fatal[:12],
            'retained_localization_duplicates':localization,'localization_duplicate_count':len(localization),
            'scope':'Only exact LocalizedText duplicate entries are nonfatal to gameplay; all other native errors remain fatal.'}


def yield_type(i):return 'YIELD_'+PREFIX+str(i)
def modifier(i,j):return PREFIX+f'CIVIC_{i}_{j}'
def strategy(i):return 'STRATEGY_'+PREFIX+str(i)
def list_type(i):return PREFIX+'YIELDS_'+str(i)
def additions():return {(civic,modifier(i,j)) for i,_,_,civic in PLANS for j in (1,2)}


def overlay(arm):
    # Preserve ALL pre-existing native preferences identically, including
    # ordinary leader favorites and accepted CSC support-research lists.
    sql="""
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType,Inverse) VALUES
 ('CSC_TEST_LONG_HAS_FUTURE','REQUIREMENT_PLAYER_HAS_CIVIC',0),
 ('CSC_TEST_LONG_NOT_FUTURE','REQUIREMENT_PLAYER_HAS_CIVIC',1);
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value) VALUES
 ('CSC_TEST_LONG_HAS_FUTURE','CivicType','CIVIC_FUTURE_CIVIC'),
 ('CSC_TEST_LONG_NOT_FUTURE','CivicType','CIVIC_FUTURE_CIVIC');
INSERT OR IGNORE INTO RequirementSets (RequirementSetId,RequirementSetType) VALUES
 ('CSC_TEST_LONG_NEVER','REQUIREMENTSET_TEST_ALL');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId) VALUES
 ('CSC_TEST_LONG_NEVER','CSC_TEST_LONG_HAS_FUTURE'),
 ('CSC_TEST_LONG_NEVER','CSC_TEST_LONG_NOT_FUTURE');
"""
    for i,q,stage,civic in PLANS:
        y,s,l=yield_type(i),strategy(i),list_type(i)
        sql+=f"""
INSERT OR IGNORE INTO Types (Type,Kind) VALUES ('{y}','KIND_YIELD'),('{s}','KIND_VICTORY_STRATEGY');
INSERT OR IGNORE INTO Yields (YieldType,Name,IconString,OccupiedCityChange,DefaultValue)
 VALUES ('{y}','LOC_{y}','',0,1);
INSERT OR IGNORE INTO Strategies (StrategyType,VictoryType,NumConditionsNeeded) VALUES ('{s}',NULL,1);
INSERT OR IGNORE INTO StrategyConditions (StrategyType,ConditionFunction,StringValue,ThresholdValue,Forbidden,Disqualifier,Exclusive) VALUES
 ('{s}','Call Lua Function','CSC_TestLongServiceReady',{i},0,0,0),
 ('{s}','Call Lua Function','CSC_TestLongServiceReady',{100+i},1,0,1);
INSERT OR IGNORE INTO AiListTypes (ListType) VALUES ('{l}');
INSERT INTO AiLists (ListType,System) SELECT '{l}','Yields' WHERE NOT EXISTS(SELECT 1 FROM AiLists WHERE ListType='{l}');
INSERT OR IGNORE INTO Strategy_Priorities (StrategyType,ListType) VALUES ('{s}','{l}');
DELETE FROM AiFavoredItems WHERE Item='{y}';
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES ('DefaultYieldBias','{y}',0,-100),('{l}','{y}',0,100);
"""
        for j in (1,2):
            m=modifier(i,j)
            sql+=f"""
INSERT OR IGNORE INTO Modifiers (ModifierId,ModifierType,SubjectRequirementSetId)
 VALUES ('{m}','MODIFIER_PLAYER_CAPITAL_CITY_ADJUST_CITY_YIELD_CHANGE','CSC_TEST_LONG_NEVER');
INSERT OR IGNORE INTO ModifierArguments (ModifierId,Name,Value) VALUES ('{m}','YieldType','{y}'),('{m}','Amount',100);
DELETE FROM CivicModifiers WHERE ModifierId='{m}';
"""
            if arm=='on':sql+=f"INSERT INTO CivicModifiers (CivicType,ModifierId) VALUES ('{civic}','{m}');\n"
    return sql


def callback_bytes(arm):
    text="""
CSC_RESEARCH_PROBE_NATIVE={version='rst-original-list-v1',calls={},first_true={},errors={},states={},transitions={}};
local G=CSC_RESEARCH_PROBE_NATIVE;
local enabled=__ENABLED__;
G.code_version='natural-six-service-civic-guidance200-forbidden-v1';G.enabled=enabled;
local targets={[1]='CIVIC_FEUDALISM',[2]='CIVIC_MEDIEVAL_FAIRES',[3]='CIVIC_URBANIZATION',[4]='CIVIC_NAVAL_TRADITION',[5]='CIVIC_DIVINE_RIGHT',[6]='CIVIC_OPERA_BALLET'};
GameEvents.CSC_TestLongServiceReady.Add(function(pid,which)
 local inverse=which>100;local plan=inverse and which-100 or which;
 local eligible,owned=false,false;
 local player=Players[pid];
 if player and player:IsAlive() and player:IsMajor() and not player:IsHuman() and targets[plan] then
  local ok,value=pcall(function()
   owned=player:GetCulture():HasCivic(GameInfo.Civics[targets[plan]].Index);
   return not owned and CSC_AI_Research.Evaluate(pid,plan)==true;
  end);
  if ok then eligible=value else if #G.errors<30 then G.errors[#G.errors+1]={turn=Game.GetCurrentGameTurn(),player=pid,plan=plan,error=tostring(value)} end end;
 end;
 local active=enabled and eligible;
 if pid>=1 and pid<=5 and targets[plan] then
  local key=tostring(pid)..':'..tostring(plan);local call=key..(inverse and ':inverse' or ':primary');
  G.calls[call]=(G.calls[call] or 0)+1;
  if not inverse then
   if active and not G.first_true[key] then G.first_true[key]=Game.GetCurrentGameTurn() end;
   local old=G.states[key];
   if not old or old.eligible~=eligible or old.active~=active or old.owned~=owned then
    local row={turn=Game.GetCurrentGameTurn(),player=pid,plan=plan,civic=targets[plan],eligible=eligible,active=active,owned=owned};
    G.transitions[#G.transitions+1]=row;G.states[key]=row;
   end;
  end;
 end;
 return inverse and not active or (not inverse and active);
end);
print('CSC_LONG_GUIDANCE_READY',tostring(enabled));
""".replace('__ENABLED__','true' if arm=='on' else 'false')
    return text.encode()


def native_check(db,arm,patch,source,with_rst=False):
    assert not with_rst
    expected=sorted(additions()) if arm=='on' else []
    assert db.execute("SELECT CivicType,ModifierId FROM CivicModifiers WHERE ModifierId LIKE 'CSC_TEST_LONG_%' ORDER BY CivicType,ModifierId").fetchall()==expected
    assert db.execute("SELECT RequirementType,Inverse FROM Requirements WHERE RequirementId IN ('CSC_TEST_LONG_HAS_FUTURE','CSC_TEST_LONG_NOT_FUTURE') ORDER BY Inverse").fetchall()==[('REQUIREMENT_PLAYER_HAS_CIVIC',0),('REQUIREMENT_PLAYER_HAS_CIVIC',1)]
    assert db.execute("SELECT Value FROM RequirementArguments WHERE RequirementId LIKE 'CSC_TEST_LONG_%' AND Name='CivicType'").fetchall()==[('CIVIC_FUTURE_CIVIC',),('CIVIC_FUTURE_CIVIC',)]
    assert db.execute("SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId='CSC_TEST_LONG_NEVER'").fetchall()==[('REQUIREMENTSET_TEST_ALL',)]
    assert db.execute("SELECT COUNT(*) FROM RequirementSetRequirements WHERE RequirementSetId='CSC_TEST_LONG_NEVER'").fetchone()[0]==2
    for i,q,stage,civic in PLANS:
        assert db.execute('SELECT QuarterKey,Stage,CivicType FROM CSC_AI_ServiceResearch WHERE Id=?',(i,)).fetchall()==[(q,stage,civic)]
        assert db.execute('SELECT DefaultValue FROM Yields WHERE YieldType=?',(yield_type(i),)).fetchall()==[(1,)]
        assert db.execute('SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?',(list_type(i),)).fetchall()==[(None,None,'Yields')]
        assert db.execute('SELECT ThresholdValue,Forbidden,Disqualifier,Exclusive FROM StrategyConditions WHERE StrategyType=? ORDER BY Exclusive',(strategy(i),)).fetchall()==[(i,0,0,0),(100+i,1,0,1)]
        assert sorted(db.execute('SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item=?',(yield_type(i),)).fetchall())==sorted([('DefaultYieldBias',0,-100),(list_type(i),0,100)])
        for j in (1,2):
            assert db.execute('SELECT ModifierType,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(modifier(i,j),)).fetchall()==[('MODIFIER_PLAYER_CAPITAL_CITY_ADJUST_CITY_YIELD_CHANGE','CSC_TEST_LONG_NEVER')]
            assert db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=? ORDER BY Name',(modifier(i,j),)).fetchall()==[('Amount','100'),('YieldType',yield_type(i))]
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()[0]==90
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall()==[(50,)]
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_AI_PLACEMENT'").fetchall()==[(25,)]
    before=inventory(db);db.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
    db.executescript(source+'\n'+patch);assert inventory(db)==before
    return {'passed':True,'arm':arm,'attachments':expected,'inventory':before,'replay_identical':True,
            'six_independent_channels':True,'baseline_old_research_preferences_preserved':True,'economic_guard_contradictory':True,
            'known_limitation':'A strategy stopped after temporary loss has not been shown to restart.'}


def preflight(path):
    # Historical schema reference deliberately removed the old CSC lists. This
    # study preserves them: reconstruct accepted source BEFORE taking the
    # offline comparison inventory, exactly as a fresh native load does.
    ref=sqlite3.connect(harness.REFERENCE.as_uri()+'?mode=ro',uri=True)
    source=baseline_path(harness.base.prior.SQL).read_text(encoding='utf-8')
    result={}
    for arm in ('off','on'):
        db=sqlite3.connect(':memory:');ref.backup(db)
        db.create_function('Make_Hash',1,lambda s:zlib.crc32(s.encode()))
        patch=overlay(arm);db.executescript(source+'\n'+patch)
        result[arm]=native_check(db,arm,patch,source)
    changed={k for k in result['off']['inventory'] if result['off']['inventory'][k]!=result['on']['inventory'][k]}
    assert changed=={'CivicModifiers'},changed
    write(path,{'passed':True,'old_source_lists_reconstructed_before_probe':True,
        'only_native_table_difference':'CivicModifiers','expected_added_attachments':12,
        'cases':{a:{k:v for k,v in d.items() if k!='inventory'} for a,d in result.items()}})


class LongRunner(pristine.CustomYieldRunner):
    def pin_sources(self):
        super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
        for f in (Path(__file__),HERE/'civic_guidance_long_job.py',ROOT/'project/tools/ai_baseline/analyze.py'):
            pins[str(f)]=sha(f)
        write(p,pins)

    def archive_version(self):
        # Skip custom single-channel archive metadata; retain actual complete
        # repository/installed/RH reference snapshots of the proven harness.
        BASE_ARCHIVE_VERSION(self)
        p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,arm=self.arm,plans=PLANS,start_era='ERA_MEDIEVAL',
          target_turn=TARGET,natural_play=True,fixtures=False,simulation_rounds=179,
          all_baseline_preferences_preserved=True,research={'channel_amount':200,'static_bias':-100,'active_bias':100},
          known_restart_limitation=True,experimental_weights_not_release_balance=True,
          common_overlay='Preserve accepted CSC research lists and vanilla favorites; register six neutral private channels and Forbidden strategies in both arms.',
          controller_revision=CONTROLLER_REVISION,
          frozen_baseline_reference=str(FROZEN_BASELINE) if FROZEN_BASELINE else None,
          worktree_source_is_not_installed_baseline_on_continuation=bool(FROZEN_BASELINE))
        write(p,v);(p.parent/'applied-callback.lua').write_bytes(callback_bytes(self.arm))

    def finish_preflight(self,i):
        self.reset_logs=set()
        for name,old in self.offsets.items():
            p=LOGS/name
            if p.exists():
                b=p.read_bytes()
                if len(b)<old['bytes'] or hashlib.sha256(b[:old['bytes']]).hexdigest()!=old['hash']:self.reset_logs.add(name)
        write(self.out/'native-log-offsets.json',{'before_host':self.offsets,'reset_detected_during_load':sorted(self.reset_logs)})
        self.cmd("assert(CSC_RESEARCH_PROBE_NATIVE.code_version=='"+VERSION+"');assert(CSC_AI_Research.version==1);assert(not Game:GetProperty('CSC_RESEARCH_CHOICE_FIXTURE'));assert(not Game:GetProperty('CSC_C7_MATERIAL_SITES'));",'CSC_AI_Research','probe-loaded')
        cache=Path.home()/"AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"
        src=sqlite3.connect(cache.as_uri()+'?mode=ro',uri=True);db=sqlite3.connect(':memory:');src.backup(db);src.close()
        dst=sqlite3.connect(self.out/'native-gameplay.sqlite');db.backup(dst);dst.close()
        result=native_check(db,self.arm,self.overlay,baseline_path(harness.base.prior.SQL).read_text(encoding='utf-8'))
        write(self.out/'native-database-validation.json',result)
        self.cmd((HERE/'builder_export.lua').read_text(encoding='utf-8'),'CSC_AdjacencyGameplay','builder-unit-export',wait=2)
        self.builder_snapshot(1)
        p=self.out/'game-01/settings.json';settings=read(p)
        settings.update(code_version=VERSION,arm=self.arm,target_turn=250,analyzed_turns=[71,249],
             observed_rounds=179,natural_start=True,opportunity_fixture=False,
             guidance='Six Service civic channels200, static-100, ready+100, Forbidden exit; known restart gap',
             ai='Accepted Quarter40/improvement80; improvement90/Builder50/native12/4/10; old lists unchanged')
        write(p,settings)

    def observe(self):
        self.cmd((HERE/'strategy_research_observer.lua').read_text(encoding='utf-8'),'CSC_AI_Research','probe-observer-install',wait=4)
        self.observer_active=True;self.export_probe()
        self.cmd("Events.PlayerTurnActivated.Add(function() if Game.GetCurrentGameTurn()>=250 and AutoplayManager.IsActive() then AutoplayManager.SetActive(false) end end);",'GameCore_Tuner','target250-hook')
        self.cmd("Automation.SetActive(false);AutoplayManager.SetDisableAssertsForAutoplay(true);AutoplayManager.SetTurns(250-Game.GetCurrentGameTurn());AutoplayManager.SetReturnAsPlayer(PlayerManager.GetAliveMajors()[1]:GetID());AutoplayManager.SetObserveAsPlayer(-1);AutoplayManager.SetActive(true);",'GameCore_Tuner','long-autoplay-start',wait=3)
        self.say(f'{TEST}/{self.arm}: NATURAL autoplay started, Medieval71 to250; no fixtures.')
        archived={71};builders={71};deadline=time.monotonic()+14400;last=71;changed=time.monotonic();failures=0
        checkpoints=[75,*range(100,251,25)]
        while time.monotonic()<deadline:
            time.sleep(25)
            try:
                text=self.cmd("print('CSC_LONG_PROGRESS',Game.GetCurrentGameTurn(),AutoplayManager.IsActive());",'GameCore_Tuner','research-probe-poll-long',wait=2)
                found=re.findall(r'CSC_LONG_PROGRESS\s+(\d+)\s+(true|false)',text);assert found
                current=int(found[-1][0]);active=found[-1][1]=='true';failures=0
            except (RuntimeError,OSError,KeyError,AssertionError):
                failures+=1
                if failures>=3:raise RuntimeError('Three failed native read polls; preserve partial game, no restart')
                continue
            if current!=last:last=current;changed=time.monotonic()
            write(self.out/'live-status.json',{'status':'running','arm':self.arm,'turn':current,'target':250,'updated_unix':time.time()})
            for t in checkpoints:
                if t<=min(current,250) and t not in archived:
                    self.snapshot(1,t);data=read(self.out/f'game-01/turn-{t:03d}.json')
                    for city in data['cities']:
                        for i,_,_,_ in PLANS:
                            value=city['yields'].get(yield_type(i));assert value is not None,'Missing private-yield readback'
                            assert abs(value)<1e-6,'Inert private guidance unexpectedly granted a yield'
                    self.export_probe();archived.add(t)
                    self.say(f'{self.arm}: checkpoint{t} and research history archived.')
                    if t%50==0 and t not in builders:self.builder_snapshot(t);builders.add(t)
            if current>=250:
                if active:self.cmd('AutoplayManager.SetActive(false);','GameCore_Tuner','long-autoplay-stop')
                assert current==250,'Native endpoint overshoot; retain frozen250 and actual endpoint evidence'
                break
            if not active:raise RuntimeError('Native autoplay stopped before250 at'+str(current))
            if time.monotonic()-changed>600:raise RuntimeError('Native autoplay stalled ten minutes at'+str(current))
        else:raise RuntimeError('Natural arm exceeded four-hour bound')
        data=self.export_probe();assert not data['errors'] and not data['native']['errors']
        selected=[x for x in data['history'] if 71<=x['turn']<250]
        pairs={(x['turn'],x['player']) for x in selected};assert len(pairs)==len(selected)
        defeated={x['player']:x['turn'] for x in data['defeats']}
        missing={(t,p) for t in range(71,250) for p in range(1,6)}-pairs
        assert all(p in defeated and t>=defeated[p] for t,p in missing),sorted(missing)[:8]
        write(self.out/'observations.json',{**data,'history':selected})
        write(self.out/'observation-validation.json',{'passed':True,'analyzed_turns':[71,249],
               'observations':len(selected),'expected_uncensored':895,'censored_pairs':sorted(missing),
               'actual_endpoint':current,'no_research_setters':True,'no_opportunity_fixtures':True})
        self.save_checkpoint(1,250);self.archive_native_logs()
        log_validation=classify_native_logs(self.out/'native-logs')
        write(self.out/'native-script-validation.json',log_validation)
        assert log_validation['passed'],log_validation['errors'][:3]
        autos=self.out/'endpoint-autosaves';autos.mkdir(exist_ok=True)
        for f in sorted((SAVES/'auto').glob('*.Civ6Save'),key=lambda p:p.stat().st_mtime,reverse=True)[:3]:shutil.copy2(f,autos/f.name)
        self.check_installed()
        source_changes=[]
        for name in ('tuning-source-hashes','controller-source-hashes'):
            for rel,h in read(self.out/(name+'.json')).items():
                f=Path(rel)
                if sha(f)!=h:
                    # Uninstalled project edits cannot alter the frozen native
                    # game. Preserve them and record divergence; executable
                    # controller/observer changes still invalidate the trial.
                    assert f.is_relative_to(ROOT/'Civ Supply Chains') or f.is_relative_to(ROOT/'project/modbuddy'),rel
                    source_changes.append({'path':rel,'archived':h,'current':sha(f)})
        self.actual_endpoint=current
        write(self.out/'validation.json',{'passed':True,'frozen_endpoint':250,'actual_endpoint':current,
               'primary_checkpoints':sorted(archived),'builder_checkpoints':sorted(builders),
               'private_yield_readback_all_zero':True,'executed_tool_pins_unchanged':True,
               'uninstalled_worktree_source_changes':source_changes})
        return data


def comparison(root):
    from analyze import analyze
    result={'code_version':VERSION,'test':TEST,'matched_world':True,'arms':{},'target_score_response':False,
            'limits':['One matched seed, six combined channels; not six independent treatments.',
                      'Natural Medieval71 start to250,179rounds; player0 autoplay is a separate observer participant.',
                      'Forbidden exit may fail to restart after temporary loss; transitions/native strategy events retained.',
                      'Amount200 is a provisional test weight; UI/release integration not validated.']}
    for arm in ('off','on'):
        p=root/arm;obs=read(p/'observations.json');end=read(p/'game-01/turn-250.json')
        summaries={str(t):analyze(p/'game-01',t) for t in (200,250)}
        builders=read(p/'builders-250.json');research={}
        for pid in range(1,6):
            hist=[x for x in obs['history'] if x['player']==pid];targets={}
            for i,q,stage,civic in PLANS:
                selected=[x['turn'] for x in hist if x['civic']==civic]
                completed=[x['turn'] for x in obs['completions'] if x['player']==pid and x['civic']==civic]
                eligible=[x['turn'] for x in obs['native'].get('transitions',[]) if x['player']==pid and x['plan']==i and x['eligible']]
                targets[civic]={'first_eligible':min(eligible) if eligible else None,'first_selected':min(selected) if selected else None,
                                'completed':min(completed) if completed else None}
            cities=[c for c in end['cities'] if c['player']==pid];pr=next((x for x in end['players'] if x['id']==pid),None)
            b=next((x for x in builders['players'] if x['player']==pid),{})
            research[str(pid)]={'targets':targets,'cities':len(cities),'population':sum(c['population'] for c in cities),
                'techs':len(pr['techs']) if pr else None,'civics':len(pr['civics']) if pr else None,
                'builders':b.get('count'),'builder_charges':b.get('charges'),
                'builders_per_city':b.get('count',0)/len(cities) if cities else None}
        result['arms'][arm]={'research_per_player':research,'summaries':summaries}
    score={a:harness.base.score_rows(root/a/'native-logs/AI_GovtPolicies.csv',71,249) for a in ('off','on')}
    civics={x[3] for x in PLANS};common=score['off'].keys()&score['on'].keys()
    result['target_score_response']=any(score['off'][k]!=score['on'][k] for k in common if k[2] in civics)
    result['score_difference_is_descriptive_after_world_divergence']=True
    write(root/'comparison.json',result)
    return result


if __name__=='__main__':
    # The saved actual baseline is authoritative for a continued matched study.
    # Never overwrite concurrent source edits to force equality with old bytes.
    if '--continue-study' in sys.argv:
        FROZEN_BASELINE=Path(sys.argv[sys.argv.index('--output')+1])/'original-installed'
        assert FROZEN_BASELINE.is_dir()
        harness.baseline_source_path=baseline_path
    harness.VERSION=VERSION;harness.TEST=TEST;harness.ROUNDS=179
    harness.MODS=tuple(modifier(i,j) for i,_,_,_ in PLANS for j in (1,2))
    harness.PAIR_TABLE='CivicModifiers';harness.PAIR_COLUMNS='CivicType,ModifierId';harness.pair_additions=additions
    harness.overlay=overlay;harness.callback_bytes=callback_bytes;harness.native_check=native_check
    harness.preflight=preflight
    harness.ModifierRunner=LongRunner;harness.comparison=comparison
    harness.main()
