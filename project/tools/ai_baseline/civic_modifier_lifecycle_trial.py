"""C10: native material-loss / Quarter-pillage cycles and target cleanup.

Identical controlled fixture transitions run in both arms, independently of
the incentive flag. The fixture mutator runs before the diagnostic callback's
ordinary readiness query. This is deliberate test instrumentation, never a
proposed production callback. No research, progress or economic yields granted.
"""
from pathlib import Path
import re
import civic_modifier_trial as dormant
import civic_modifier_inert_guard_trial as guard
import civic_modifier_neutral_yield_trial as neutral
import civic_modifier_strategy_yield_trial as strategy
from paired_standard import read, sha
from run import write

VERSION='civic-modifiers-loss-pillage-reacquisition-v1'
TEST='C10-material-lifecycle'
ROUNDS=16

BOOTSTRAP=r"""
local R=CSC_AI_Research;local audit=CSC_RESEARCH_PROBE_NATIVE;
assert(R and audit);
local sites=Game:GetProperty('CSC_C7_MATERIAL_SITES');assert(sites and #sites==5);
local byplayer={};for _,s in ipairs(sites) do byplayer[s.player]=s end;
local base={};for tag in GameInfo.TypeTags() do if tag.Tag=='CLASS_CSC_TAILORS_BASE' then base[tag.Type]=true end end;
local last,removed,pillaged={},{},{};
local function quarters(pid)
 local result={};for _,city in Players[pid]:GetCities():Members() do
  local ds=city:GetDistricts();for i=0,ds:GetNumDistricts()-1 do
   local d=ds:GetDistrictByIndex(i);local def=GameInfo.Districts[d:GetType()];
   if def and def.DistrictType=='DISTRICT_CSC_TAILORS_QUARTER' then result[#result+1]=d end;
  end;
 end;return result;
end;
function CSC_C10_TargetReady(pid,civic)
 local def=GameInfo.Civics[civic];assert(def);
 return R.Evaluate(pid,5) and not Players[pid]:GetCulture():HasCivic(def.Index);
end;
-- Verified City district SetPillaged(bool) API; exercise/read back and restore
-- before autoplay so an unavailable native method fails the setup gate.
local ds=quarters(4);assert(#ds==1);local d=ds[1];assert(not d:IsPillaged());
d:SetPillaged(true);assert(d:IsPillaged());R.Invalidate();assert(not R.Evaluate(4,5));
d:SetPillaged(false);assert(not d:IsPillaged());R.Invalidate();assert(R.Evaluate(4,5));
for pid=1,5 do
 assert(Players[pid]:GetCulture():HasCivic(GameInfo.Civics.CIVIC_CODE_OF_LAWS.Index));
 assert(not CSC_C10_TargetReady(pid,'CIVIC_CODE_OF_LAWS'),'Already-owned civic must suppress guidance');
 assert(CSC_C10_TargetReady(pid,'CIVIC_DIVINE_RIGHT')==(pid>=3));
end;
function CSC_C10_Apply(pid)
 if pid~=3 and pid~=4 then return end;
 local turn=Game.GetCurrentGameTurn();
 local available=turn<73 or (turn>=77 and turn<=80) or turn>=83;
 if last[pid]==available then return end;
 if pid==3 then
  if not available then
   removed={};for index=0,Map.GetPlotCount()-1 do
    local p=Map.GetPlotByIndex(index);local res=GameInfo.Resources[p:GetResourceType()];
    if p:GetOwner()==pid and res and base[res.ResourceType] then
     removed[#removed+1]={plot=index,resource=res.Index,quantity=p:GetResourceCount()};
     ResourceBuilder.SetResourceType(p,-1);assert(p:GetResourceType()==-1);
    end;
   end;
   assert(#removed>0,'Material loss needs actual owned Base');
  elseif last[pid]~=nil then
   for _,s in ipairs(removed) do local p=Map.GetPlotByIndex(s.plot);
    ResourceBuilder.SetResourceType(p,s.resource,s.quantity);assert(p:GetResourceType()==s.resource and p:GetResourceCount()==s.quantity);
   end;
  end;
 else
  local qs=quarters(pid);assert(#qs>0);
  if not available then
   pillaged={};for _,q in ipairs(qs) do
    if not q:IsPillaged() then q:SetPillaged(true);pillaged[#pillaged+1]=Map.GetPlot(q:GetX(),q:GetY()):GetIndex() end;
    assert(q:IsPillaged());
   end;
  elseif last[pid]~=nil then
   for _,q in ipairs(qs) do local index=Map.GetPlot(q:GetX(),q:GetY()):GetIndex();
    for _,old in ipairs(pillaged) do if old==index then q:SetPillaged(false);assert(not q:IsPillaged()) end end;
   end;
  end;
 end;
 last[pid]=available;R.Invalidate();
 local material=R.Evaluate(pid,5);local owned=Players[pid]:GetCulture():HasCivic(GameInfo.Civics.CIVIC_DIVINE_RIGHT.Index);
 if not available then assert(not material,'Loss/pillage failed to withdraw actual readiness') end;
 if available and not owned then assert(material,'Reacquisition failed to restore actual readiness') end;
 audit.lifecycle=audit.lifecycle or {};
 audit.lifecycle[#audit.lifecycle+1]={turn=turn,player=pid,available=available,material_ready=material,target_owned=owned};
end;
print('CSC_C10_FIXTURE_LIFECYCLE_READY');
"""


def callback_bytes(arm):
    text=neutral.callback_bytes(arm).decode()
    old='local ok,result=pcall(CSC_AI_Research.Evaluate,pid,5);'
    new="""local ok,result=pcall(function()
   if CSC_C10_Apply then CSC_C10_Apply(pid) end;
   return CSC_C10_TargetReady and CSC_C10_TargetReady(pid,'CIVIC_DIVINE_RIGHT') or false;
  end);"""
    assert text.count(old)==1
    text=text.replace(old,new)
    text=text.replace('eligible=eligible,active=active};',"eligible=eligible,active=active,target_owned=Players[pid]:GetCulture():HasCivic(GameInfo.Civics.CIVIC_DIVINE_RIGHT.Index),material_ready=CSC_AI_Research.Evaluate(pid,5)};")
    return text.encode()


class LifecycleRunner(guard.InertGuardRunner):
    def pin_sources(self):
        super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
        pins[str(Path(__file__))]=sha(Path(__file__));write(p,pins)

    def archive_version(self):
        super().archive_version();p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,analyzed_rounds=ROUNDS,
                 fixture_mutations='Both arms: player3 owned Base loss/reacquisition; player4 Quarter pillage/repair',
                 phases='available71-72, unavailable73-76, available77-80, unavailable81-82, available83+',
                 explicit_target_completion_cleanup=True,natural_performance=False)
        write(p,v);(p.parent/'applied-callback.lua').write_bytes(callback_bytes(self.arm))
        (p.parent/'lifecycle-fixture.lua').write_text(BOOTSTRAP,encoding='utf-8')

    def after_fixture(self):
        super().after_fixture()
        text=self.cmd(BOOTSTRAP,'CSC_AI_Research','lifecycle-setup',wait=4)
        assert 'CSC_C10_FIXTURE_LIFECYCLE_READY' in text
        write(self.out/'lifecycle-setup-validation.json',{'passed':True,'district_pillage_native_readback':True,
              'already_owned_CodeOfLaws_suppressed':True,'target_initial_readiness_3_4_5':True})

    def observe(self):
        self.fixture_path=neutral.material.FIXTURE
        self.guard_check('guard-before')
        data=dormant.base.RSTRunner.observe(self)
        self.guard_check('guard-after')
        history=data['native'].get('readiness_history') or []
        life=data['native'].get('lifecycle') or []
        assert history and life
        assert all(x['active']==(self.arm=='on' and x['eligible']) for x in history)
        assert all(not x['active'] for x in history if x.get('target_owned'))
        for pid in (3,4):
            changes=[(x['turn'],x['available']) for x in life if x['player']==pid]
            assert changes==[(71,True),(73,False),(77,True),(81,False),(83,True)],changes
        log=(self.out/'native-logs/AI_Victories.csv').read_text(errors='replace')
        per={}
        for pid in range(1,6):
            samples=[x for x in history if x['player']==pid];assert samples
            turns=[int(t) for t in re.findall(r'^\s*(\d+),\s*'+str(pid)+r',\s*'+strategy.STRATEGY+r',\s*Following\s*$',log,re.M)]
            # Following records adoption, not a repeated per-turn status row.
            # Do not interpret missing later entries as strategy withdrawal.
            active_turns={x['turn'] for x in samples if x['active']}
            assert all(t in active_turns for t in turns),(pid,turns)
            if active_turns:
                assert min(active_turns) in turns,(pid,turns,active_turns)
            else:
                assert not turns,(pid,turns)
            per[pid]={'readiness_samples':samples,'following_turns':turns}
        write(self.out/'strategy-activation-validation.json',{'passed':True,'per_player':per,'lifecycle':life,
              'actual_score_withdrawal_requires_comparison':True})
        return data


def comparison(root):
    result=neutral.comparison(root)
    scores={a:dormant.base.score_rows(root/a/'native-logs/AI_GovtPolicies.csv',71,86) for a in ('off','on')}
    deltas={}
    for turn in range(71,87):
        deltas[turn]={}
        for pid in range(1,6):
            key=(turn,pid,dormant.base.TARGET)
            if all(key in scores[a] for a in ('off','on')):
                deltas[turn][pid]=float(scores['on'][key][0])-float(scores['off'][key][0])
    inactive=[74,75,76,82];restored=[78,79,84]
    result.update(code_version=VERSION,test=TEST,target_deltas_by_turn=deltas,
          phase_score_samples={t:deltas[t] for t in (72,74,76,78,80,82,84,86)},
          observed_complete_withdrawal=all(len(deltas[t])==5 and all(abs(deltas[t][p])<.05 for p in (3,4)) for t in inactive),
          observed_reactivation=all(all(deltas[t].get(p,0)>.05 for p in (3,4)) for t in restored),
          lifecycle={a:read(root/a/'strategy-activation-validation.json')['lifecycle'] for a in ('off','on')},
          completion_events={a:read(root/a/'observations.json')['completions'] for a in ('off','on')},
          limits=['Both arms receive same diagnostic map/pillage interventions; not natural performance.',
                  'Later city/research divergence may affect paired scores; callback and Following are separate evidence.',
                  'Already-owned target control tests cleanup predicate; natural DivineRight completion only if observed.',
                  'Reload, ownership loss, visibility, duplicates, UI and release weights remain pending.'])
    return result


if __name__=='__main__':
    dormant.VERSION=VERSION;dormant.TEST=TEST;dormant.ROUNDS=ROUNDS
    dormant.MODIFIER_YIELDS=(neutral.YIELD,neutral.YIELD);dormant.GUARD_REQUIREMENT_COUNT=5
    dormant.PAIR_TABLE='CivicModifiers';dormant.PAIR_COLUMNS='CivicType,ModifierId'
    dormant.pair_additions=lambda:{(dormant.base.TARGET,m) for m in dormant.MODS}
    dormant.overlay=guard.overlay;dormant.callback_bytes=callback_bytes;dormant.native_check=guard.native_check
    dormant.ModifierRunner=LifecycleRunner;dormant.comparison=comparison
    dormant.main()
