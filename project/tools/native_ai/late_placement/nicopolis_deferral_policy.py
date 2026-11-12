"""Declared knowledge fixture for the remaining1.7 deferral comparison.

Diagnostic only: reveal radius4 around pinned Nicopolis before the first main
publication, so radius3 frontier sites cannot escape deductions merely because
an adjacent tile is unexplored. This changes AI knowledge, never map contents,
ownership, Treasury, score bands or native decisions. The ordinary main CSC
model then decides whether those sites really are weak; this fixture promises
no particular winner. Native matrices are read by the existing selector probe.
"""

REVEAL="""-- Diagnostic common knowledge fixture, not shipping CSC policy.
do
 assert(Game.GetCurrentGameTurn()==200,'Nicopolis knowledge fixture requires200')
 local city=assert(CityManager.GetCity(1,524295))
 assert(city:GetName()=='LOC_CITY_NAME_NICOPOLIS')
 local player=assert(Players[1]);assert(player:IsAlive() and not player:IsHuman())
 local visibility=assert(PlayersVisibility[1]);local changed={}
 for index=0,Map.GetPlotCount()-1 do
  local plot=assert(Map.GetPlotByIndex(index))
  if Map.GetPlotDistance(city:GetX(),city:GetY(),plot:GetX(),plot:GetY())<=4
   and not visibility:IsRevealed(index) then
   -- Balanced visibility counts leave explored knowledge without granting
   -- ongoing sight of foreign units. Verify both contracts immediately.
   local visibleBefore=visibility:IsVisible(index)
   visibility:ChangeVisibilityCount(index,1)
   visibility:ChangeVisibilityCount(index,-1);changed[#changed+1]=index
   assert(visibility:IsRevealed(index),'Declared knowledge edit did not land')
   assert(visibility:IsVisible(index)==visibleBefore,'Knowledge fixture changed live sight')
  end
 end
 print('CSC_DEFERRAL_COMMON_REVEAL',Game.GetCurrentGameTurn(),#changed,table.concat(changed,','))
end
"""

RECEIPT="""-- Diagnostic packet metadata, not a native acceptance receipt.
do
 local placement=assert(CSC_AI_QuarterPlacement)
 local profile
 for _,p in ipairs(placement.StageTwoProfiles())do if p.key=='BAKERS' then profile=p end end
 assert(profile)
 print('CSC_DEFERRAL_DISTRICT_TYPES',turn,GameInfo.Districts[31].DistrictType,
  GameInfo.Districts[36].DistrictType,GameInfo.Districts[37].DistrictType)
 local allVisible=true
 for definition in GameInfo.Resources() do
  if CSC_Adjacency.HasTag(profile.base,definition.ResourceType)
   and not CSC_Adjacency.ResourceVisible(1,definition.Index)then allVisible=false end
 end
 print('CSC_DEFERRAL_BASE_VISIBILITY',turn,nextVersion,tostring(allVisible))
 local city=assert(CityManager.GetCity(1,524295))
 local center=assert(Map.GetPlot(city:GetX(),city:GetY()))
 local visibility=assert(PlayersVisibility[1])
 for _,plot in ipairs(CSC_Adjacency.PlotsInBand(center,1,3))do
  local uncertain,possibleBase=false,false
  for _,neighbor in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
   if not visibility:IsRevealed(neighbor:GetIndex())then uncertain=true
   elseif neighbor:GetOwner()==1 or neighbor:GetOwner()==-1 then
    local resource=GameInfo.Resources[neighbor:GetResourceType()]
    if resource and CSC_Adjacency.ResourceVisible(1,resource.Index)
     and CSC_Adjacency.HasTag(profile.base,resource.ResourceType)then possibleBase=true end
   end
  end
  local buyer=Cities.GetPlotPurchaseCity(plot)
  print('CSC_DEFERRAL_SITE_FACTS',turn,nextVersion,plot:GetIndex(),plot:GetOwner(),
   buyer and buyer:GetID() or -1,plot:GetDistrictType(),
   tostring(plot:CanHaveDistrict(profile.district.Index,1,524295)),
   tostring(visibility:IsRevealed(plot:GetIndex())),tostring(uncertain),tostring(possibleBase))
 end
 for _,entry in ipairs(entries)do
  if entry.player==1 and entry.city==524295 and entry.district==profile.district.Index then
   local plot=assert(Map.GetPlotByIndex(entry.plot))
   local supply=placement.ReadSuppliers(Players[1],plot,profile)
   print('CSC_DEFERRAL_RETAINED',turn,nextVersion,entry.plot,entry.delta,
    tostring(entry.weak),#supply.base,#supply.specialty,tostring(entry.declineNoBase))
  end
 end
 for _,scope in ipairs(declines or {})do
  if scope.player==1 and scope.city==524295 and scope.district==profile.district.Index then
   print('CSC_DEFERRAL_DECLINE_RETAINED',turn,nextVersion,scope.plot)
  end
 end
end
"""


OPPORTUNITY_RECEIPT=b'''-- Diagnostic lineage for the changed supplier only.
do
 local profile
 for _,p in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do if p.key=='BAKERS'then profile=p end end
 assert(profile)
 local supplier=assert(Map.GetPlotByIndex(471));local owner=Cities.GetPlotPurchaseCity(supplier)
 print('CSC_DEFERRAL_TRACKED_SUPPLIER',turn,version+1,supplier:GetOwner(),owner and owner:GetID()or -1,
  supplier:GetResourceType(),supplier:GetImprovementType(),tostring(supplier:IsImprovementPillaged()))
 for _,index in ipairs({397,398,472})do
  local plot=assert(Map.GetPlotByIndex(index))
  local supply=CSC_AI_QuarterPlacement.ReadSuppliers(Players[1],plot,profile)
  for _,base in ipairs(supply.base)do
   print('CSC_DEFERRAL_TRACKED_BASE',turn,version+1,index,base.plot,tostring(base.ready),tostring(base.working))
  end
  -- Read the still-active PREVIOUS publication before the ordinary commit.
  -- A missing new proposal alone is not proof that an old decline retired.
  print('CSC_DEFERRAL_DECLINE_PREVIOUS',turn,version,index,
   CE_AIDistrictDeclineReceipt(version,1,524295,36,index))
 end
end
'''


def stage(publisher,*,arm=None,opportunity=False):
    """Observe retained main packets; do not change their contents or lifetime."""
    needle=b'    local accepted, message = bridge.Publish('
    assert publisher.count(needle)==1
    assert arm in (None,'full','control')
    # The production locals are `turn`, `version` and `entries`. Keep the
    # diagnostic's version equal to the exact next committed main packet.
    receipt=RECEIPT.replace('nextVersion','(version+1)').encode('utf-8')
    if opportunity:receipt+=OPPORTUNITY_RECEIPT
    if arm=='control':
        # Only the target city's Bakers admission scopes are removed. Numeric
        # deductions and every other player/city/district intervention remain.
        # Filter before both actual publication and committed-scope logging.
        receipt=b'''-- Diagnostic matched control; no shipping policy toggle.
do
 local removed=0
 for i=#declines,1,-1 do
  local scope=declines[i]
  if scope.player==1 and scope.city==524295 and scope.district==36 then
   table.remove(declines,i);removed=removed+1
  end
 end
 print('CSC_DEFERRAL_DECLINES_WITHHELD',turn,version+1,removed)
end
'''+receipt
    return REVEAL.encode('utf-8')+publisher.replace(needle,receipt+needle)
