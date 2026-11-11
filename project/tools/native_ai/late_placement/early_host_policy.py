"""Qualify the archived early world's seats and observe live host-aware offers.

Diagnostic only. Role migration restores missing metadata from pinned original
setup/scout evidence. Every identity/property is checked before any write; neither
scores nor gameplay facts are changed. Extra staged candidate metadata and logs
connect live supply/host contributions to the ordinary main CSC publication.
"""
import hashlib
import json
from pathlib import Path
from boston_material_policy import provenance

LEADERS=['LEADER_CLEOPATRA','LEADER_GANDHI','LEADER_TOMYRIS',
         'LEADER_T_ROOSEVELT','LEADER_VICTORIA','LEADER_HOJO']
ANCESTRY={
 'scout-03/commands/0007-host-natural-online.lua':'9a4d4b9b4d1d8b99e5479387504c0ec05d8da3818c969256b9d92d7a3e1a452b',
 'scout-03/commands/0007-host-natural-online.txt':'c93ea427a8ecc42c6c31c4b12bf526998bd0714e674c76bb53d1f2fd80635eab',
 'scout-03/scout-result.json':'1b4fb8c9e8bc95bef0ffa1953087b7e185ef6a6b881df54a8e3f093165117e7d',
 'matched-02/discovery/session-load-input.json':'66a5f2eda5bc977cb4f9c8851b57b5396a05171f7b68147143b9dd9f18344f49',
}


def source_provenance(worlds):
    root=Path(worlds);result=provenance(root)
    result.pop('original_ai_player') # The older helper qualified only seat3.
    data=json.loads((root/'matched-02/discovery/search-result.json').read_text(encoding='utf-8'))
    assert sorted(r['player']for r in data['world']['civics'])==[1,2,3,4,5]
    for relative,digest in ANCESTRY.items():
        assert hashlib.sha256((root/relative).read_bytes()).hexdigest()==digest,relative
    setup=(root/'scout-03/commands/0007-host-natural-online.lua').read_text(encoding='utf-8')
    assert all(name in setup for name in LEADERS)
    assert 'CSC_FULL_ACK_9432_7\ttrue' in (root/'scout-03/commands/0007-host-natural-online.txt').read_text(encoding='utf-8')
    ancestor=json.loads((root/'scout-03/scout-result.json').read_text(encoding='utf-8'))['checkpoint']
    loaded=json.loads((root/'matched-02/discovery/session-load-input.json').read_text(encoding='utf-8'))
    assert ancestor['verified'] and ancestor['turn']==loaded['turn']==8
    assert ancestor['sha256']==loaded['sha256']=='95a26a1976400ef0d8232fc3a0d2b857f0cbc277b6e07ff2f66195f7df1310bc'
    return dict(**result,ancestry=ANCESTRY,original_ai_players=[1,2,3,4,5],leaders=LEADERS)


ROLE_PREFIX="""-- Diagnostic original-seat migration for this pinned turn22 world only.
do
 assert(Game.GetCurrentGameTurn()==22)
 local leaders={'LEADER_CLEOPATRA','LEADER_GANDHI','LEADER_TOMYRIS',
  'LEADER_T_ROOSEVELT','LEADER_VICTORIA','LEADER_HOJO'}
 local missing={}
 for pid=0,5 do
  local p=assert(Players[pid]);local config=assert(PlayerConfigurations[pid])
  assert(p:IsAlive() and p:IsMajor() and p:IsHuman()==(pid==0),'Early saved role differs')
  assert(config:GetLeaderTypeName()==leaders[pid+1],'Early leader differs')
  local value=pid==0 and 1 or 0
  local key='CSC_AI_OriginalHuman_'..pid
  local previous=Game:GetProperty(key)
  assert(previous==nil or previous==value,'Conflicting early original role')
  print('CSC_EARLY_ORIGINAL_ROLE',pid,leaders[pid+1],tostring(previous),value)
  if previous==nil then missing[#missing+1]={key=key,value=value}end
 end
 assert(CityManager.GetCity(3,131073):GetName()=='LOC_CITY_NAME_BOSTON')
 -- Do not partially migrate earlier seats when a later seat conflicts.
 for _,r in ipairs(missing)do Game:SetProperty(r.key,r.value)end
 print('CSC_EARLY_ROLES_MIGRATED',#missing)
end
function CSC_EARLY_DIAG_Retained(entries,turn,nextVersion)
 -- This is the retained precommit offer, not a native consumption receipt.
 -- Join its nextVersion to CE's versioned net/cache/winner records afterwards.
 local placement=assert(CSC_AI_QuarterPlacement)
 local profiles={}
 for _,profile in ipairs(placement.StageTwoProfiles())do profiles[profile.district.Index]=profile end
 for _,entry in ipairs(entries)do
  local profile=profiles[entry.district]
  if profile and entry.delta>0 then
   local player=assert(Players[entry.player]);local city=assert(CityManager.GetCity(entry.player,entry.city))
   local plot=assert(Map.GetPlotByIndex(entry.plot))
   local supply=placement.ReadSuppliers(player,plot,profile)
   local forecast=CSC_AI_QuarterAdjacencyValue(profile.district.DistrictType,plot,city,entry.player,false)
   print('CSC_EARLY_RETAINED_OFFER',turn,nextVersion,entry.player,entry.city,entry.district,entry.plot,
    entry.delta,entry.adjacency or '-',forecast.total,#supply.base,#supply.specialty,
    entry.diagnosticFutureDistrict or '-',entry.diagnosticFuturePlot or -1)
   for _,kind in ipairs({'base','specialty'})do
    for _,material in ipairs(supply[kind])do
     print('CSC_EARLY_SUPPLIER',turn,nextVersion,entry.player,entry.city,entry.plot,
      kind,material.plot,material.resource,material.working,material.ready)
    end
   end
   for _,detail in ipairs(forecast.details)do
    print('CSC_EARLY_RULE',turn,nextVersion,entry.player,entry.city,entry.plot,
     detail.rule,detail.count,detail.amount,detail.inPlan)
   end
  end
 end
end
"""


def stage(scanner,publisher):
    # Passive metadata only: retain the exact host already selected by the live
    # model. CE reads only its required numeric entry fields; these extra keys
    # cannot alter its packet or supply/placement policy.
    needle=b'        if ready and futurePlot then candidate.futureHost = legalCustomers[futurePlot] end'
    assert scanner.count(needle)==1
    scanner=scanner.replace(needle,b'        candidate.diagnosticFutureDistrict, candidate.diagnosticFuturePlot = futureDistrict, futurePlot\n'+needle)
    needle=b'    local accepted, message = bridge.Publish('
    assert publisher.count(needle)==1
    assert publisher.index(b'for i = #entries, capacity + 1, -1')<publisher.index(needle)
    publisher=ROLE_PREFIX.encode('utf-8')+publisher.replace(needle,
        b'    CSC_EARLY_DIAG_Retained(entries,turn,version+1)\n'+needle)
    return scanner,publisher


FUTURE_HOST_ABLATION=b"""        -- Diagnostic counterfactual only: withhold one prospective
        -- customer footprint from player3's Bakers model. Existing districts,
        -- real map legality, supply, score bands and CE writes are untouched.
        -- This helper serves multiple sites: audit the WHOLE packet afterwards.
        if pid == 3 and profile.key == 'BAKERS' and index == 869 then return false end
"""


def without_washington_future_host(scanner):
    needle=b'        if potential[index] ~= nil then return potential[index] end'
    assert scanner.count(needle)==1
    # Before the cache: the control must not retain a previous true result.
    return scanner.replace(needle,FUTURE_HOST_ABLATION+needle)
