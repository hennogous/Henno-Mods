"""Independent completed C11/C12 evidence audit. No native game connection."""
from pathlib import Path
import argparse
import json
import sqlite3
import time
from civic_modifier_material_audit import read,digest,rows,scores


def audit(root,current=False):
    assert read(root/'job-status.json')['status']=='complete'
    inv={};summary={}
    for arm in ('off','on'):
        p=root/arm;v=read(p/'source-version/version.json');counts={}
        for k,folder in (('source_files','repository'),('installed_files','installed'),
                         ('workshop_files','workshop-real-strategy'),('rh_example_hashes','rh-readonly-examples')):
            for rel,h in v[k].items():assert digest(p/'source-version'/folder/rel)==h,(arm,k,rel)
            counts[k]=len(v[k])
        if current:
            for name in ('tuning-source-hashes','controller-source-hashes'):
                for rel,h in read(p/(name+'.json')).items():assert digest(Path(rel))==h,rel
        for name in ('complete','observation-validation','native-database-validation','native-script-validation',
                     'material-case-validation','lifecycle-setup-validation','strategy-activation-validation',
                     'disqualifier-validation','guard-before','guard-after','paired-preflight'):
            assert read(p/(name+'.json'))['passed'],(arm,name)
        ov=read(p/'observation-validation.json');assert ov['observations']==80 and ov['analyzed_turns']==[71,86] and ov['actual_endpoint']==88
        pref=read(p/'preferences-restored.json');assert pref['verified'] and pref['auto_start'] is False
        db=sqlite3.connect(p/'native-gameplay.sqlite');inv[arm]=rows(db)
        gate=db.execute("SELECT a.Value,q.Inverse FROM RequirementSetRequirements s JOIN Requirements q ON q.RequirementId=s.RequirementId JOIN RequirementArguments a ON a.RequirementId=q.RequirementId WHERE s.RequirementSetId='CSC_TEST_CIVIC_MODIFIER_DORMANT' AND a.Name='CivicType' ORDER BY q.Inverse").fetchall()
        assert gate==[('CIVIC_FUTURE_CIVIC',0),('CIVIC_FUTURE_CIVIC',1)]
        assert db.execute("SELECT RequirementSetType FROM RequirementSets WHERE RequirementSetId='CSC_TEST_CIVIC_MODIFIER_DORMANT'").fetchone()==('REQUIREMENTSET_TEST_ALL',)
        conditions=db.execute("SELECT ThresholdValue,Forbidden,Disqualifier,Exclusive FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_TEST_CIVIC_YIELD' ORDER BY Exclusive").fetchall()
        assert conditions in ([(1,0,0,0),(2,0,1,1)],[(1,0,0,0),(2,1,0,1)])
        obs=read(p/'observations.json');n=obs['native'];assert not n['errors']
        assert len(obs['history'])==80
        states=n['turn_readiness'];assert {(x['turn'],x['player']) for x in states}=={(t,pid) for t in range(71,88) for pid in range(1,6)}
        assert len(states)==85
        for pid in (3,4):
            changes=[(x['turn'],x['available']) for x in n['lifecycle'] if x['player']==pid]
            assert changes==[(71,True),(73,False),(77,True),(81,False),(83,True)]
            assert all(not x['material_ready'] for x in states if x['player']==pid and x['turn'] in (74,75,76,82))
            assert all(x['material_ready'] for x in states if x['player']==pid and x['turn'] in (78,79,84))
        assert all(x['active']==(arm=='on' and x['eligible']) for x in n['readiness_history'])
        assert all(not x['active'] for x in n['readiness_history'] if x['target_owned'])
        assert read(p/'material-case-validation.json')['cases'][2]['improvement']=='NONE'
        summary[arm]={'archive_counts':counts,'observations':80,'native_turn_states':85,'preferences':pref,
             'strategy_conditions':conditions,'native_sha256':digest(p/'native-gameplay.sqlite'),
             'callback_calls':{str(pid):{str(k):n['calls'].get(str(pid)+':'+str(k),0) for k in (1,2)} for pid in range(1,6)}}
    assert [t for t in inv['off'] if inv['off'][t]!=inv['on'][t]]==['CivicModifiers']
    assert not(inv['off']['CivicModifiers']-inv['on']['CivicModifiers'])
    assert sum((inv['on']['CivicModifiers']-inv['off']['CivicModifiers']).values())==2
    for rel in ('game-01/initial-map.json','game-01/turn-071.json','original-preferences.json','material-case-validation.json'):
        assert read(root/'off'/rel)==read(root/'on'/rel),rel
    fixtures=[read(root/a/'fixture-census.json') for a in ('off','on')]
    for f in fixtures:f['options'].sort(key=lambda x:(x['player'],x['city'],x['quarter']))
    assert fixtures[0]==fixtures[1]
    cb=[(root/a/'source-version/applied-callback.lua').read_bytes() for a in ('off','on')]
    assert cb[0].replace(b'local CSC_C6_ENABLED=false',b'local CSC_C6_ENABLED=true')==cb[1]
    s={a:scores(root/a/'native-logs/AI_GovtPolicies.csv') for a in ('off','on')}
    initial={k:v for k,v in s['off'].items() if k[0]==71};assert len(initial)==55 and all(s['on'].get(k)==v for k,v in initial.items())
    delta={t:{pid:round(s['on'][(t,pid,'CIVIC_DIVINE_RIGHT')]-s['off'][(t,pid,'CIVIC_DIVINE_RIGHT')],4) for pid in range(1,6) if all((t,pid,'CIVIC_DIVINE_RIGHT') in s[a] for a in ('off','on'))} for t in range(71,87)}
    first_zero={pid:next((t for t in range(74,77) if abs(delta[t].get(pid,99999))<.05),None) for pid in (3,4)}
    assert read(root/'installed-restored.json')=={'verified':True,'source_unchanged':True}
    summary.update(passed=True,audited_unix=time.time(),current_pins_checked=current,
                   initial_identical_records=55,phase_score_samples={t:delta[t] for t in (72,74,75,76,78,82,84,86)},
                   first_clean_zero_after_loss=first_zero,
                   reactivated_at78=all(delta[78].get(pid,0)>.05 for pid in (3,4)),
                   reactivated_at84=all(delta[84].get(pid,0)>100 for pid in (3,4)),
                   natural_DivineRight_completions={a:len([x for x in read(root/a/'observations.json')['completions'] if x['civic']=='CIVIC_DIVINE_RIGHT']) for a in ('off','on')},
                   limits='Later world/research divergence affects paired scores; phase/readiness and score response are independent evidence. No natural performance claim.')
    (root/'post-run-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--current-pins',action='store_true');a=p.parse_args()
    r=audit(a.root,a.current_pins)
    print(json.dumps({k:r[k] for k in ('passed','first_clean_zero_after_loss','reactivated_at78','reactivated_at84','natural_DivineRight_completions')}))
