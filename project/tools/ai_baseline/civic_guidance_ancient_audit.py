"""Audit one COMPLETED Ancient guidance run, without connecting to Civ.

Other authorized runs may be playing. Do not demand that their live installed
overlay/preferences equal the completed run's restored historical baseline.
"""
import argparse
import csv
import json
import sqlite3
import time
import zlib
from pathlib import Path
from civic_modifier_material_audit import read, digest, rows

TARGETS=['CIVIC_FEUDALISM','CIVIC_MEDIEVAL_FAIRES','CIVIC_URBANIZATION',
         'CIVIC_NAVAL_TRADITION','CIVIC_DIVINE_RIGHT','CIVIC_OPERA_BALLET']


def audit(p):
    assert read(p/'complete.json')['passed']
    v=read(p/'source-version/version.json');counts={}
    for field,folder in [('source_files','repository'),('installed_files','installed'),
                         ('workshop_files','workshop-real-strategy'),('rh_example_hashes','rh-readonly-examples')]:
        for rel,h in v[field].items():assert digest(p/'source-version'/folder/rel)==h,(field,rel)
        counts[field]=len(v[field])
    changed_sources=[]
    for name in ('tuning-source-hashes','controller-source-hashes'):
        for rel,h in read(p/(name+'.json')).items():
            if digest(Path(rel))!=h:
                assert 'Civ Supply Chains' in Path(rel).parts or 'modbuddy' in Path(rel).parts,rel
                changed_sources.append(rel)
    for name in ('validation','native-database-validation','native-script-validation','observation-validation'):
        assert read(p/(name+'.json'))['passed'],name
    pref=read(p/'preferences-restored.json');assert pref['verified'] and pref['auto_start'] is False
    obs=read(p/'observations.json');assert not obs['errors'] and not obs['native']['errors']
    history=obs['history'];pairs={(x['turn'],x['player']) for x in history}
    assert len(pairs)==len(history)
    wanted={(t,pid) for t in range(1,250) for pid in range(1,6)}
    defeat={x['player']:x['turn'] for x in obs['defeats']};missing=wanted-pairs
    assert not pairs-wanted and all(pid in defeat and t>=defeat[pid] for t,pid in missing)
    assert read(p/'observation-validation.json')['actual_endpoint']==250
    initial=read(p/'game-01/turn-001.json');settings=read(p/'game-01/settings.json')
    assert settings['start_era']=='ERA_ANCIENT' and settings['initial_turn']==1
    assert initial['turn']==1 and len(initial['players'])==6 and not initial['cities']
    assert [x['id'] for x in initial['players']]==list(range(6))
    assert [x['leader'] for x in initial['players']]==settings['leaders']
    assert all('CIVIC_NAVAL_TRADITION' not in x['civics'] for x in initial['players'])
    assistance=read(p/'game-01/assistance-audit.json')
    assert assistance['status']=='complete' and assistance['version']==4 and assistance['initialization_turn']==1
    for t in (1,*range(25,251,25)):
        s=read(p/f'game-01/turn-{t:03d}.json');assert s['turn']==t and not s['errors']
        for c in s['cities']:
            for i in range(1,7):assert abs(c['yields'][f'YIELD_CSC_TEST_LONG_{i}'])<1e-6
    for t in (1,50,100,150,200,250):
        b=read(p/f'builders-{t:03d}.json');assert b['turn']==t and not b['errors']
        for row in b['players']:
            assert row['count']==len(row['builders'])
            assert row['charges']==sum(x['charges'] for x in row['builders'])
    assert obs['native']['enabled'] is True
    assert all(x['active']==x['eligible'] for x in obs['native']['transitions'])
    assert all(not x['active'] for x in obs['native']['transitions'] if x['owned'] or x['player']==0)
    for pid in range(1,6):
        for plan in range(1,7):
            assert obs['native']['calls'].get(f'{pid}:{plan}:primary',0)>0
            assert obs['native']['calls'].get(f'{pid}:{plan}:inverse',0)>0
    assert any(x.startswith('0:') for x in obs['native']['calls']), 'No recorded player0 checks'
    adoptions=[];old_adoptions=[]
    for row in csv.reader((p/'native-logs/AI_Victories.csv').read_text().splitlines()):
        row=[x.strip() for x in row]
        if len(row)<4:continue
        if row[2].startswith('STRATEGY_CSC_TEST_LONG_') and row[3]=='Following':
            assert 1<=int(row[1])<=5,row
            adoptions.append(row)
        if row[2].startswith('STRATEGY_CSC_AI_SERVICE_') and row[3]=='Following':old_adoptions.append(row)
    assert not old_adoptions
    callback=(p/'source-version/applied-callback.lua').read_text()
    assert 'if pid>=1 and pid<=5 and player and player:IsAlive()' in callback
    assert 'not owned and CSC_AI_Research.Evaluate(pid,plan)==true' in callback
    native=sqlite3.connect((p/'native-gameplay.sqlite').as_uri()+'?mode=ro',uri=True)
    db=sqlite3.connect(':memory:');native.backup(db);native.close()
    for prefix in ('CSC_AI_SERVICE_%','CSC_AI_FIXED_SERVICE_%'):
        for table in ('AiLists','AiListTypes','AiFavoredItems','Strategy_Priorities'):
            assert db.execute(f'SELECT COUNT(*) FROM {table} WHERE ListType LIKE ?',(prefix,)).fetchone()==(0,)
    for table in ('Strategies','StrategyConditions','Strategy_Priorities'):
        assert db.execute(f"SELECT COUNT(*) FROM {table} WHERE StrategyType LIKE 'STRATEGY_CSC_AI_SERVICE_%' OR StrategyType LIKE 'STRATEGY_CSC_AI_FIXED_SERVICE_%'").fetchone()==(0,)
    assert db.execute('SELECT COUNT(*) FROM CSC_AI_ServiceResearch').fetchone()==(6,)
    attachments=db.execute("SELECT CivicType,ModifierId FROM CivicModifiers WHERE ModifierId LIKE 'CSC_TEST_LONG_%'").fetchall()
    expected={(c,f'CSC_TEST_LONG_CIVIC_{i}_{j}') for i,c in enumerate(TARGETS,1) for j in (1,2)}
    assert len(attachments)==12 and set(attachments)==expected
    assert db.execute("SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId='CSC_TEST_LONG_NEVER'").fetchone()==('REQUIREMENTSET_TEST_ALL',)
    assert db.execute("SELECT a.Value,r.Inverse FROM RequirementSetRequirements s JOIN Requirements r USING(RequirementId) JOIN RequirementArguments a USING(RequirementId) WHERE s.RequirementSetId='CSC_TEST_LONG_NEVER' AND a.Name='CivicType' ORDER BY r.Inverse").fetchall()==[('CIVIC_FUTURE_CIVIC',0),('CIVIC_FUTURE_CIVIC',1)]
    for i in range(1,7):
        assert db.execute('SELECT ThresholdValue,Forbidden,Disqualifier,Exclusive FROM StrategyConditions WHERE StrategyType=? ORDER BY Exclusive',(f'STRATEGY_CSC_TEST_LONG_{i}',)).fetchall()==[(i,0,0,0),(100+i,1,0,1)]
        assert db.execute('SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item=? ORDER BY Value',(f'YIELD_CSC_TEST_LONG_{i}',)).fetchall()==[('DefaultYieldBias',0,-100),(f'CSC_TEST_LONG_YIELDS_{i}',0,100)]
        for j in (1,2):
            assert db.execute('SELECT ModifierType,SubjectRequirementSetId FROM Modifiers WHERE ModifierId=?',(f'CSC_TEST_LONG_CIVIC_{i}_{j}',)).fetchone()==('MODIFIER_PLAYER_CAPITAL_CITY_ADJUST_CITY_YIELD_CHANGE','CSC_TEST_LONG_NEVER')
            assert db.execute('SELECT Name,Value FROM ModifierArguments WHERE ModifierId=? ORDER BY Name',(f'CSC_TEST_LONG_CIVIC_{i}_{j}',)).fetchall()==[('Amount','100'),('YieldType',f'YIELD_CSC_TEST_LONG_{i}')]
    assert db.execute("SELECT DefaultValue FROM PseudoYields WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT'").fetchone()==(90,)
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER'").fetchall()==[(50,)]
    assert db.execute("SELECT YieldChange,AdjacentResourceClass FROM Adjacency_YieldChanges WHERE ID='CSC_AI_BONUS_RESOURCE'").fetchone()==(12,'RESOURCECLASS_BONUS')
    assert db.execute("SELECT YieldChange,AdjacentRiver FROM Adjacency_YieldChanges WHERE ID='CSC_AI_RIVER'").fetchone()==(4,1)
    assert db.execute("SELECT DISTINCT YieldChange FROM Adjacency_YieldChanges WHERE ID LIKE 'CSC_AI_SALES_%'").fetchall()==[(10,)]
    assert db.execute("SELECT DISTINCT Value FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_%_PRESENT' AND Name='Amount'").fetchall()==[('40',)]
    assert db.execute("SELECT DISTINCT Value FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_IMPROVE_%' AND Name='Amount'").fetchall()==[('80',)]
    sql=(p/'source-version/applied-overlay.sql').read_text();original=(p.parent/'original-installed/Data/CSC_AI.sql').read_text()
    before=rows(db);db.create_function('Make_Hash',1,lambda x:zlib.crc32(x.encode()))
    db.executescript(original+'\n'+sql);assert rows(db)==before
    for rel,suffix in [('Data/CSC_AI.sql',b'\n'+sql.encode()),('Lua_UI/AI/CSC_AI_Research.lua',(p/'source-version/applied-callback.lua').read_bytes())]:
        assert (p/'source-version/installed'/rel).read_bytes()==(p.parent/'original-installed'/rel).read_bytes()+suffix
    fatal=[];localization=[]
    for name in ('Database.log','Lua.log'):
        for line in (p/'native-logs'/name).read_text(errors='replace').splitlines():
            if not any(x in line for x in ('ERROR:','Gameplay ERROR','Runtime Error:')):continue
            if name=='Database.log' and '[Localization] ERROR: UNIQUE constraint failed: LocalizedText.Language, LocalizedText.Tag' in line:localization.append(line)
            else:fatal.append(line)
    assert not fatal,fatal[:3]
    saves={}
    for name,t in [('initial-save.json',1),('endpoint-save.json',250)]:
        f=p/'game-01'/name
        if not f.exists():
            assert t==250 and (p/'save-warning-250.json').exists()
            saves[str(t)]={'named_unconfirmed':True};continue
        meta=read(f);assert meta['actual_turn']==t
        archived=p/'game-01'/Path(meta['path']).name;assert digest(archived)==meta['sha256']
        saves[str(t)]=meta
    autos=[{'name':f.name,'filename_turn':int(f.stem.rsplit('_',1)[1]),'sha256':digest(f)} for f in sorted((p/'endpoint-autosaves').glob('*.Civ6Save'))]
    assert autos and autos[-1]['filename_turn']==250
    result={'passed':True,'audited_unix':time.time(),'run':v['run'],'archive_counts':counts,
            'observations':len(history),'defeat_censored_pairs':sorted(missing),
            'endpoint':250,'eleven_primary_six_builder_checkpoints':True,
            'legacy_preference_rows_and_adoptions_absent':True,'player0_rejected_in_callback_and_native_adoption':True,
            'private_yields_zero_all_captured_cities':True,'economic_guard_logically_impossible':True,
            'source_replay_identical':True,'preferences_restored_after_this_run':pref,
            'live_installed_restoration_not_required_while_next_run_active':True,
            'uninstalled_worktree_changes_since_archive':changed_sources,
            'named_saves':saves,'autosaves':autos,'autosave_turn_source':'Filename, not independently reloaded',
            'retained_localization_duplicates':len(localization),
            'native_database_sha256':digest(p/'native-gameplay.sqlite'),
            'callback_sha256':digest(p/'source-version/applied-callback.lua'),
            'overlay_sha256':digest(p/'source-version/applied-overlay.sql')}
    (p/'post-run-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);x=audit(parser.parse_args().run)
    print(json.dumps({k:x[k] for k in ('passed','run','archive_counts','observations','endpoint','player0_rejected_in_callback_and_native_adoption')}))
