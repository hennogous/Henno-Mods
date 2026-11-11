-- Diagnostic read-only reconciliation before a proposed river fixture. Count
-- every source plot through the LOADED adjacency handler, then contrast the
-- actual supplier reader's stricter viability rules. No resource, ownership,
-- technology, score, queue or autoplay mutation occurs in this inspection.
local A,P=assert(CSC_Adjacency),assert(CSC_AI_QuarterPlacement)
A.Initialize()
local player=assert(Players[4]);local city=assert(CityManager.GetCity(4,131073))
assert(city:GetName()=='LOC_CITY_NAME_LIVERPOOL')
local site=assert(Map.GetPlotByIndex(2497))
local profile
for _,p in ipairs(P.StageTwoProfiles())do if p.key=='BAKERS'then profile=p end end
assert(profile)
local rule
for _,r in ipairs(A.ByDistrict[profile.district.DistrictType])do
 if r.ID=='CSC_BAKERS_PRODUCTION_FROM_BASE'then rule=r end
end
assert(rule and rule.AdjacencyType=='FROM_RINGS_TYPETAG_RESOURCE')
local first,last=A.Bounds(rule)
assert(first>=0 and last<=3)
local handler=assert(A.Sources[rule.AdjacencyType])
local suppliers=P.ReadSuppliers(player,site,profile)
local viable={}
for _,s in ipairs(suppliers.base)do viable[s.plot]=true end
local function definition(tableName,index,field)
 local row=GameInfo[tableName][index];return row and row[field] or '-'
end
local function inspect(plot)
 local resource=definition('Resources',plot:GetResourceType(),'ResourceType')
 local owner=Cities.GetPlotPurchaseCity(plot)
 local own=rule.MustOwn==1 or rule.MustOwn==true or rule.MustOwn=='1'
 local count=0
 if not handler.Ownership or not own or plot:GetOwner()==4 then
  count=handler.Quantity(plot,rule.CustomAdjacentObject,{PlayerID=4,City=city})or 0
 end
 local row={plot=plot:GetIndex(),owner=plot:GetOwner(),ownerCity=owner and owner:GetID() or -1,
  resource=resource,resourceQuantity=type(plot.GetResourceCount)=='function' and plot:GetResourceCount() or -1,
  district=plot:GetDistrictType(),
  improvement=definition('Improvements',plot:GetImprovementType(),'ImprovementType'),
  pillaged=plot:IsImprovementPillaged(),terrain=definition('Terrains',plot:GetTerrainType(),'TerrainType'),
  feature=definition('Features',plot:GetFeatureType(),'FeatureType'),
  revealed=PlayersVisibility[4]:IsRevealed(plot:GetX(),plot:GetY()),
  baseContribution=count,viableSupplier=viable[plot:GetIndex()]==true,improvements={}}
 for option in GameInfo.Improvement_ValidResources()do
  if option.ResourceType==resource then
   local improvement=assert(GameInfo.Improvements[option.ImprovementType])
   local ok,allowed=pcall(ImprovementBuilder.CanHaveImprovement,plot,improvement.Index,player:GetTeam())
   local tech=improvement.PrereqTech and GameInfo.Technologies[improvement.PrereqTech]
   local civic=improvement.PrereqCivic and GameInfo.Civics[improvement.PrereqCivic]
   row.improvements[#row.improvements+1]={type=option.ImprovementType,queryOK=ok,allowed=ok and allowed==true,
    tech=improvement.PrereqTech or '-',techKnown=not tech or player:GetTechs():HasTech(tech.Index),
    civic=improvement.PrereqCivic or '-',civicKnown=not civic or player:GetCulture():HasCivic(civic.Index)}
  end
 end
 return row
end
local result={turn=Game.GetCurrentGameTurn(),city=city:GetName(),player=4,cityID=city:GetID(),
 currentProduction=city:GetBuildQueue():CurrentlyBuilding(),hasQuarter=city:GetDistricts():HasDistrict(profile.district.Index),
 site=inspect(site),riverEdges=site:GetRiverCrossingCount(),baseRule={id=rule.ID,first=first,last=last,
  mustOwn=rule.MustOwn,count=A.Count(rule,site,city,4)},supply=suppliers,plots={},mutationCommands=0,
 forecast=CSC_AI_QuarterAdjacencyValue(profile.district.DistrictType,site,city,4,false,'DISTRICT_COMMERCIAL_HUB'),
 originalRoles={}}
local summed=0
for _,plot in ipairs(A.PlotsInBand(site,first,last))do
 local row=inspect(plot);result.plots[#result.plots+1]=row;summed=summed+row.baseContribution
end
result.baseRule.summedContributions=summed
assert(summed==result.baseRule.count,'Adjacency source reconciliation differs')
local host=assert(Map.GetPlotByIndex(2571));local buyer=Cities.GetPlotPurchaseCity(host)
local commercial=assert(GameInfo.Districts.DISTRICT_COMMERCIAL_HUB)
local permitted=buyer and CSC_AI_FutureDistrictTypes(4,buyer)
result.futureHost=inspect(host)
result.futureHost.permitted=permitted and permitted[commercial.Index]==true or false
result.futureHost.geometry=buyer and host:CanHaveDistrict(commercial.Index,4,buyer:GetID()) or false
for pid=0,5 do
 local original=Game:GetProperty('CSC_AI_OriginalHuman_'..pid)
 result.originalRoles[#result.originalRoles+1]={player=pid,originalHuman=original,
  human=Players[pid]:IsHuman(),leader=PlayerConfigurations[pid]:GetLeaderTypeName()}
end
local function json(v)
 local kind=type(v)
 if kind=='nil'then return 'null'end
 if kind=='boolean'or kind=='number'then return tostring(v)end
 if kind=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r')..'"'end
 local array,fields=true,{}
 for k in pairs(v)do if type(k)~='number'then array=false end end
 if array then for _,item in ipairs(v)do fields[#fields+1]=json(item)end;return '['..table.concat(fields,',')..']'end
 local keys={};for k in pairs(v)do keys[#keys+1]=k end;table.sort(keys)
 for _,k in ipairs(keys)do fields[#fields+1]=json(k)..':'..json(v[k])end
 return '{'..table.concat(fields,',')..'}'
end
print('CSC_LIVERPOOL_INSPECTION='..json(result))
