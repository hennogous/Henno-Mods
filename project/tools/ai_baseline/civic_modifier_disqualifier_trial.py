"""C11: explicit inverse Lua disqualifier for the material strategy.

Grounding: RH_Religious_Commemoration.sql registers a second Call Lua Function
condition with Disqualifier=1, Exclusive=1. We use that native wiring with our
own inverse material/target predicate. No RH Lua or gameplay tuning is copied.
Identical C10 loss/pillage fixture and settings; fresh matched pair.
"""
from pathlib import Path
import shutil
import civic_modifier_trial as dormant
import civic_modifier_neutral_yield_trial as neutral
import civic_modifier_strategy_yield_trial as strategy
import civic_modifier_inert_guard_trial as guard
import civic_modifier_lifecycle_trial as life
from paired_standard import read,sha
from run import write

VERSION='civic-modifiers-explicit-lua-disqualifier-v2-independent-fixture'
TEST='C11-inverse-readiness-disqualifier'
REFERENCE=dormant.RH_CIVICS.parents[1]/'Advanced_Thinking/experimental/RH_Religious_Commemoration.sql'


def overlay(arm):
    return guard.overlay(arm)+"""
INSERT OR IGNORE INTO StrategyConditions
 (StrategyType,ConditionFunction,StringValue,ThresholdValue,Disqualifier,Exclusive) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_YIELD','Call Lua Function','CSC_TestCivicYieldStrategy',2,1,1);
"""


def callback_bytes(arm):
    text=life.callback_bytes(arm).decode()
    # Fixture transitions must not depend on whether an inactive/disqualified
    # strategy gets evaluated. Native turn events drive them in this version.
    text=text.replace('if CSC_C10_Apply then CSC_C10_Apply(pid) end;', '')
    old='if active and not r.first_true[key] then'
    assert text.count(old)==1
    text=text.replace(old,"""if which==2 then
 if pid>=1 and pid<=5 then
  r.disqualifier_history=r.disqualifier_history or {};
  r.disqualifier_history[#r.disqualifier_history+1]={turn=Game.GetCurrentGameTurn(),player=pid,disqualify=not active};
 end;
 return not active;
end;
"""+old)
    return text.encode()


def native_check(db,arm,patch,source,with_rst=False):
    result=guard.native_check(db,arm,patch,source,with_rst)
    assert db.execute('SELECT ThresholdValue,Disqualifier,Exclusive FROM StrategyConditions WHERE StrategyType=? ORDER BY Exclusive',(strategy.STRATEGY,)).fetchall()==[(1,0,0),(2,1,1)]
    result.update(test=TEST,explicit_inverse_readiness_disqualifier=True,reference='RH_Religious_Commemoration.sql second exclusive Call Lua Function')
    return result


class DisqualifierRunner(life.LifecycleRunner):
    def pin_sources(self):
        super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
        for f in (Path(__file__),REFERENCE):pins[str(f)]=sha(f)
        write(p,pins)

    def archive_version(self):
        super().archive_version();p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,explicit_inverse_readiness_disqualifier=True,
                 counterpart='Condition primaryThreshold1 active, exclusiveThreshold2 returns inverse')
        dest=p.parent/'rh-readonly-examples'/REFERENCE.name;shutil.copy2(REFERENCE,dest)
        v['rh_example_hashes'][REFERENCE.name]=sha(dest);write(p,v)
        (p.parent/'applied-callback.lua').write_bytes(callback_bytes(self.arm))

    def after_fixture(self):
        super().after_fixture()
        code="""
local r=CSC_RESEARCH_PROBE_NATIVE;
Events.PlayerTurnActivated.Add(function(pid)
 if pid<1 or pid>5 then return end;
 local ok,err=pcall(function()
  CSC_C10_Apply(pid);CSC_AI_Research.Invalidate();
  local material=CSC_AI_Research.Evaluate(pid,5);
  local owned=Players[pid]:GetCulture():HasCivic(GameInfo.Civics.CIVIC_DIVINE_RIGHT.Index);
  r.turn_readiness=r.turn_readiness or {};
  r.turn_readiness[#r.turn_readiness+1]={turn=Game.GetCurrentGameTurn(),player=pid,material_ready=material,target_owned=owned,eligible=material and not owned};
 end);
 if not ok then r.errors[#r.errors+1]={turn=Game.GetCurrentGameTurn(),player=pid,error=tostring(err)} end;
end);
CSC_C10_Apply(3);CSC_C10_Apply(4);
print('CSC_C11_INDEPENDENT_FIXTURE_READY');
"""
        text=self.cmd(code,'CSC_AI_Research','independent-phase-fixture',wait=4)
        assert 'CSC_C11_INDEPENDENT_FIXTURE_READY' in text
        (self.out/'source-version/independent-phase-fixture.lua').write_text(code,encoding='utf-8')

    def observe(self):
        data=super().observe()
        history=data['native'].get('disqualifier_history') or []
        assert history,'Native inverse disqualifier callback never invoked'
        assert {x['player'] for x in history}==set(range(1,6))
        write(self.out/'disqualifier-validation.json',{'passed':True,'callbacks':len(history),
             'players':sorted({x['player'] for x in history}),
             'runtime_score_withdrawal_separate':True})
        return data


def comparison(root):
    result=life.comparison(root);result.update(code_version=VERSION,test=TEST,
           explicit_inverse_disqualifier=True,
           disqualifier_callbacks={a:read(root/a/'disqualifier-validation.json')['callbacks'] for a in ('off','on')})
    return result


if __name__=='__main__':
    dormant.VERSION=VERSION;dormant.TEST=TEST;dormant.ROUNDS=life.ROUNDS
    dormant.MODIFIER_YIELDS=(neutral.YIELD,neutral.YIELD);dormant.GUARD_REQUIREMENT_COUNT=5
    neutral.STRATEGY_CONDITION_ROWS=[('Call Lua Function',strategy.CALLBACK,1),('Call Lua Function',strategy.CALLBACK,2)]
    dormant.PAIR_TABLE='CivicModifiers';dormant.PAIR_COLUMNS='CivicType,ModifierId'
    dormant.pair_additions=lambda:{(dormant.base.TARGET,m) for m in dormant.MODS}
    dormant.overlay=overlay;dormant.callback_bytes=callback_bytes;dormant.native_check=native_check
    dormant.ModifierRunner=DisqualifierRunner;dormant.comparison=comparison
    dormant.main()
