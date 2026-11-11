"""Stage the known Boston material-policy comparison, never a native score pulse.

Both arms run the main CSC publisher. Fixture-only saved-seat metadata and
read-only receipts are identical; control removes one positive entry after
capacity truncation. It changes no other policy array or native score directly.
"""
from pathlib import Path
import hashlib
import json

SOURCE_PIN='22e69e2e5841b2aa02c4023bcdaed77ca5c8b3ed39f4776271f21694ef53424e'
SCOUT_PIN='4993fb5c8f660cafa3420621f2ae1fcd73962d582d9f6fcfe67ba4347f24aca7'


def provenance(worlds):
    root=Path(worlds)/'matched-02'
    source=root/'discovery/search-result.json'
    scout=root/'source-version/008-scout.lua'
    assert hashlib.sha256(source.read_bytes()).hexdigest()==SOURCE_PIN
    assert hashlib.sha256(scout.read_bytes()).hexdigest()==SCOUT_PIN
    data=json.loads(source.read_text(encoding='utf-8'))
    # The pinned scout emits civic rows only for alive, non-human majors.
    # The exact inactive checkpoint separately records human seat0. This is
    # source provenance, not a deduction from a later autoplay IsHuman value.
    assert data['world']['turn']==22 and any(r['player']==3 for r in data['world']['civics'])
    assert data['checkpoint']['UI_phase']==dict(turn=22,active=False,local_player=0,
        player0_human=True,player0_alive=True)
    return dict(source_sha256=SOURCE_PIN,scout_sha256=SCOUT_PIN,original_ai_player=3)


PREFIX="""-- Diagnostic saved-fixture metadata/receipts only; not shipping CSC policy.
local p=assert(Players[3])
local c=assert(CityManager.GetCity(3,131073))
assert(Game.GetCurrentGameTurn()==22 and Players[0]:IsHuman())
assert(not p:IsHuman() and PlayerConfigurations[3]:GetLeaderTypeName()=='LEADER_T_ROOSEVELT')
assert(c:GetName()=='LOC_CITY_NAME_BOSTON')
local previous=Game:GetProperty('CSC_AI_OriginalHuman_3')
assert(previous==nil or previous==0,'Conflicting saved player role')
print('CSC_MATERIAL_ROLE',tostring(previous),0)
if previous==nil then Game:SetProperty('CSC_AI_OriginalHuman_3',0)end
CSC_MATERIAL_DIAG_CONTROL=__CONTROL__
function CSC_MATERIAL_DIAG_Snapshot(strict)
 local turn=Game.GetCurrentGameTurn()
 if turn<22 or turn>__THROUGH__ then return end
 local status=CE_AIDistrictScoresStatus()
 local version=assert(tonumber(status:match('"version":(%d+)')))
 -- Keep complete status even when native samples exceed one log line.
 for first=1,#status,1000 do print('CSC_MATERIAL_STATUS_CHUNK',turn,first,status:sub(first,first+999))end
 if strict then
  assert(status:match('"ready":1') and status:match('"enabled":1')
   and status:match('"faults":0'),'Material policy is not healthy/enabled')
  if turn==22 then
   local initial=assert(CSC_MATERIAL_DIAG_INITIAL,'Initial publication was not observed')
   assert(initial.matches==1 and initial.delta==6144,'Expected ordinary Boston offer changed')
   assert(initial.removed==(CSC_MATERIAL_DIAG_CONTROL and 1 or 0),'Initial ablation missing')
  end
 end
 print('CSC_MATERIAL_RECEIPT',turn,version,CE_AIDistrictScoresReceipt(version,3,131073,36,721))
 local q=Map.GetPlotByIndex(721);local b=Map.GetPlotByIndex(796)
 local city=assert(CityManager.GetCity(3,131073))
 local district
 if q:GetDistrictType()==36 then district=Players[3]:GetDistricts():FindID(q:GetDistrictID())end
 local resource=GameInfo.Resources[b:GetResourceType()]
 print('CSC_MATERIAL_STATE',turn,q:GetOwner(),q:GetDistrictType(),
  district and district:IsComplete() or false,city:GetBuildQueue():CurrentlyBuilding(),
  b:GetOwner(),resource and resource.ResourceType or '-',b:GetDistrictType(),
  b:GetImprovementType(),b:IsImprovementPillaged())
end
-- Registered before the publisher: retain the preceding packet's counters
-- before Commit resets them. Initial and endpoint snapshots are also explicit.
GameEvents.OnGameTurnStarted.Add(function()
 local ok,error=pcall(CSC_MATERIAL_DIAG_Snapshot)
 if not ok then print('CSC_MATERIAL_DIAG_FAILED',tostring(error))end
end)
"""

FILTER="""    -- Diagnostic ablation after all capacity trimming. Removing the
    -- retained target cannot admit another omitted entry. Other arrays stay intact.
    local removed,matches,targetDelta=0,0,nil
    for i=#entries,1,-1 do
        local entry=entries[i]
        if entry.player==3 and entry.city==131073 and entry.district==36
            and entry.plot==721 and entry.delta>0 then
            matches=matches+1;targetDelta=entry.delta
            print('CSC_MATERIAL_OFFER',turn,version+1,entry.delta,CSC_MATERIAL_DIAG_CONTROL)
            if CSC_MATERIAL_DIAG_CONTROL then table.remove(entries,i);removed=removed+1 end
        end
    end
    assert(matches<=1 and removed<=1,'Duplicate material-policy target')
    print('CSC_MATERIAL_ABLATION',turn,removed)
    if turn==22 then
        CSC_MATERIAL_DIAG_INITIAL={matches=matches,removed=removed,delta=targetDelta}
        for _,entry in ipairs(entries)do
            print('CSC_MATERIAL_INITIAL_ENTRY',entry.player,entry.city,entry.district,entry.plot,entry.delta)
        end
        print('CSC_MATERIAL_INITIAL_ARRAYS',#builderSites,#nominations,#repairs,#exclusions)
    end
"""


def stage(source,arm,through):
    assert arm in ('control','treatment') and 23<=through<=40
    needle=b'    local accepted, message = bridge.Publish('
    assert source.count(needle)==1
    assert source.index(b'for i = #entries, capacity + 1, -1')<source.index(needle)
    prefix=PREFIX.replace('__CONTROL__','true' if arm=='control' else 'false').replace('__THROUGH__',str(through))
    return prefix.encode()+source.replace(needle,FILTER.encode()+needle)
