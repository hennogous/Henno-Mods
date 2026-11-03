"""C7: real Quarter/material readiness gates the proven strategy Yields signal.

Same SQL and controlled material fixture in both arms. OFF callback disabled;
ON callback uses existing CSC_AI_Research.Evaluate(player,5). Extra score
incentive should activate only for players3-5; player3 Flax is unimproved.
The default dedicated benefit is still present for everyone: this establishes
selective additional influence, not idle neutralization or lifecycle yet.
"""
from pathlib import Path
import re

import civic_modifier_trial as dormant
import civic_modifier_strategy_yield_trial as strategy
from paired_standard import HERE, read, sha
from run import write

VERSION = 'civic-modifiers-material-yield-gate-v1'
TEST = 'C7-quarter-material-selective-yield'
FIXTURE = HERE / 'civic_modifier_ready_fixture.lua'
YIELD = strategy.YIELD


def overlay(arm):
    return strategy.overlay(arm)


def callback_bytes(arm):
    text = strategy.callback_bytes(arm).decode()
    old = 'local active=CSC_C6_ENABLED and pid>=1 and pid<=5 and PlayerManager.IsAlive(pid) and not Players[pid]:IsHuman();'
    new = """local eligible=false;
 if pid>=1 and pid<=5 and PlayerManager.IsAlive(pid) and not Players[pid]:IsHuman() then
  local ok,result=pcall(CSC_AI_Research.Evaluate,pid,5);
  if ok then eligible=result==true else r.errors[#r.errors+1]={player=pid,error=tostring(result)} end;
 end;
 r.last_eligible=r.last_eligible or {};r.last_eligible[key]=eligible;
 local active=CSC_C6_ENABLED and eligible;
 if pid>=1 and pid<=5 then
  r.readiness_history=r.readiness_history or {};
  r.readiness_history[#r.readiness_history+1]={turn=Game.GetCurrentGameTurn(),player=pid,eligible=eligible,active=active};
 end;"""
    assert text.count(old) == 1
    return text.replace(old, new).replace("experiment_version='strategy-yield-gate-v1'", "experiment_version='material-yield-gate-v1'").encode()


def native_check(db, arm, patch, source, with_rst=False):
    result = strategy.native_check(db, arm, patch, source, with_rst)
    result.update(test=TEST, expected_callback_players=[3,4,5] if arm == 'on' else [],
                  plan_id=5, source='Existing CSC_AI_Research.Evaluate; no readiness override')
    result.pop('expected_callback_active', None)
    return result


class MaterialYieldRunner(strategy.StrategyYieldRunner):
    def pin_sources(self):
        super().pin_sources()
        p = self.out / 'tuning-source-hashes.json'
        pins = read(p)
        for f in (Path(__file__), FIXTURE):
            pins[str(f)] = sha(f)
        write(p, pins)

    def archive_version(self):
        super().archive_version()
        p = self.out / 'source-version/version.json'
        v = read(p)
        v.update(code_version=VERSION, test=TEST, no_material_condition=False,
                 readiness='Existing Evaluate(pid,5), owned visible potential Base, including unimproved',
                 expected_ready_players=[3,4,5], fixture=str(FIXTURE),
                 fixture_cases={1:'NoQuarter/Flax',2:'Quarter/noBase',
                                3:'Quarter/unimprovedFlax',4:'Quarter/FarmedFlax',5:'Quarter/FarmedFlax'},
                 does_not_establish_idle_neutralization_or_lifecycle=True)
        write(p, v)
        (p.parent / 'applied-callback.lua').write_bytes(callback_bytes(self.arm))

    def after_fixture(self):
        text = self.cmd("""
local sites=Game:GetProperty('CSC_C7_MATERIAL_SITES');assert(sites and #sites==5);
CSC_AI_Research.Invalidate();
for _,fixture in ipairs(sites) do
 local pid=fixture.player;local row=CSC_AI_Research.Scan(pid);local q=0;
 for _,site in ipairs(row.sites) do if site.quarter=='TAILORS' then q=q+1 end end;
 local ready=row.active[5]==true;local mp=Map.GetPlotByIndex(fixture.material);
 local resource=GameInfo.Resources[mp:GetResourceType()];local improvement=GameInfo.Improvements[mp:GetImprovementType()];
 assert((q>0)==(pid~=1),'Quarter fixture mismatch '..pid);
 assert(ready==(pid>=3),'Potential Base readiness mismatch '..pid);
 assert((resource~=nil and resource.ResourceType=='RESOURCE_CSC_FLAX')==(pid~=2),'Material fixture mismatch '..pid);
 if pid==3 then assert(mp:GetImprovementType()==-1,'Player3 must be genuinely unimproved') end;
 if pid==1 or pid>=4 then assert(improvement and improvement.ImprovementType=='IMPROVEMENT_FARM' and not mp:IsImprovementPillaged(),'Farm fixture mismatch '..pid) end;
 print('CSC_C7_CASE',pid,q,tostring(ready),fixture.material,resource and resource.ResourceType or 'NONE',improvement and improvement.ImprovementType or 'NONE');
end;
""", 'CSC_AI_Research', 'material-case-validation', wait=4)
        cases = [{'player':int(p),'quarters':int(q),'ready':ready=='true','material_plot':int(plot),
                  'resource':res,'improvement':imp}
                 for p,q,ready,plot,res,imp in re.findall(r'CSC_C7_CASE\s+(\d+)\s+(\d+)\s+(true|false)\s+(\d+)\s+(\S+)\s+(\S+)', text)]
        assert len(cases) == 5
        if self.arm == 'on':
            assert cases == read(self.out.parent / 'off/material-case-validation.json')['cases']
        write(self.out / 'material-case-validation.json', {'passed':True,'cases':cases})

    def observe(self):
        self.fixture_path = FIXTURE
        self.guard_check('guard-before')
        data = dormant.base.RSTRunner.observe(self)
        self.guard_check('guard-after')
        log = (self.out / 'native-logs/AI_Victories.csv').read_text(errors='replace')
        first, calls = data['native']['first_true'] or {}, data['native']['calls'] or {}
        history = data['native'].get('readiness_history') or []
        assert history
        assert all(x['active'] == (self.arm == 'on' and x['eligible']) for x in history)
        per_player = {}
        for pid in range(1,6):
            active = self.arm == 'on' and pid>=3
            key = str(pid)+':1'
            assert calls.get(key,0)>0, 'Material callback never reached '+key
            if active:
                assert first.get(key) == 71, 'Initially ready player did not activate at71 '+key
            elif self.arm == 'off':
                assert key not in first
            else:
                assert first.get(key, 72) > 71
            turns = [int(t) for t in re.findall(r'^\s*(\d+),\s*'+str(pid)+r',\s*'+strategy.STRATEGY+r',\s*Following\s*$',log,re.M)]
            assert (71 in turns) is active, 'Initial material Following mismatch '+key
            per_player[pid] = {'expected_active':active,'callback_calls':calls[key],
                               'first_true':first.get(key),'following_turns':turns,
                               'readiness_samples':[x for x in history if x['player']==pid]}
        write(self.out / 'strategy-activation-validation.json', {
            'passed':True,'per_player':per_player,'condition':'Real Quarter/material readiness, not constant-true',
            'natural_later_readiness_changes_allowed_and_recorded':True,
            'does_not_establish_score_selectivity_by_itself':True})
        return data


def comparison(root):
    result = strategy.comparison(root)
    scores = {a:dormant.base.score_rows(root/a/'native-logs/AI_GovtPolicies.csv',71,78) for a in ('off','on')}
    deltas = {}
    for t in range(71,79):
        deltas[t] = {}
        for p in range(1,6):
            k = (t,p,dormant.base.TARGET)
            if all(k in scores[a] for a in ('off','on')):
                deltas[t][p] = float(scores['on'][k][0])-float(scores['off'][k][0])
    initial_only = result['target_score_response']
    result.update(code_version=VERSION,test=TEST,
                  initial_target_score_response=initial_only,
                  target_score_response=result['any_target_strategy_response'],
                  target_deltas_by_turn=deltas,
                  expected_ready_players=[3,4,5],
                  material_selective_at_first_expected_response72=(len(deltas[72])==5 and all((abs(deltas[72][p])>0.05)==(p>=3) for p in range(1,6))),
                  material_cases=read(root/'on/material-case-validation.json')['cases'],
                  limits=['Shared controlled material fixture; no natural performance claim.',
                          'Default dormant benefit still present for all; selective additional influence only.',
                          'First expected strategy response is72 after activation71; later worlds may diverge.'])
    return result


if __name__ == '__main__':
    dormant.VERSION = VERSION
    dormant.TEST = TEST
    dormant.ROUNDS = 8
    dormant.MODIFIER_YIELDS = (YIELD,YIELD)
    dormant.PAIR_TABLE = None
    dormant.pair_additions = lambda:set()
    dormant.overlay = overlay
    dormant.callback_bytes = callback_bytes
    dormant.native_check = native_check
    dormant.ModifierRunner = MaterialYieldRunner
    dormant.comparison = comparison
    dormant.main()
