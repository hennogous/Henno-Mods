-- Read-only inspection of a recorded world; no property, score or queue writes.
-- Use the loaded CSC evaluator and compare its active rule amounts with the
-- saved property encoding. Mill geometry is a hypothetical completed/repaired
-- local Mill, not a construction order or a prediction of future customers.
local scope=__SCOPE__
assert(Game.GetCurrentGameTurn()==scope.turn and not AutoplayManager.IsActive())
local A=assert(CSC_Adjacency);A.Initialize()
local P=assert(CSC_AI_QuarterPlacement)
local wind='BUILDING_CSC_BAKERS_WIND_MILL'
local water='BUILDING_CSC_BAKERS_WATER_MILL'
local function json(v)
 if v==nil then return 'null'end
 if type(v)=='number'or type(v)=='boolean'then return tostring(v)end
 if type(v)=='string'then
  return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'
 end
 assert(type(v)=='table');local keys,values={},{}
 for key in pairs(v)do keys[#keys+1]=key end;table.sort(keys)
 for _,key in ipairs(keys)do values[#values+1]=json(key)..':'..json(v[key])end
 return '{'..table.concat(values,',')..'}'
end
local emitted,sites=0,0
local function emit(row)print('CSC_QUARTER_ADJ_ROW\t'..json(row));emitted=emitted+1 end
local function zero()return {production=0,gold=0}end
local function yieldKey(kind)
 if kind=='YIELD_PRODUCTION'then return 'production'end
 if kind=='YIELD_GOLD'then return 'gold'end
end
local function apply(values,percent)
 local result=zero()
 for key,value in pairs(values)do result[key]=value*(1+percent[key]/100)end
 result.total=result.production+result.gold;return result
end
for _,quarterKey in ipairs(scope.quarters)do
local definition=assert(GameInfo.Districts['DISTRICT_CSC_'..quarterKey..'_QUARTER'])
local profile
for _,p in ipairs(P.StageTwoProfiles())do if p.key==quarterKey then profile=p end end
assert(profile)
for _,pid in ipairs(scope.players)do
 local player=assert(Players[pid]);assert(player:IsAlive()and not player:IsHuman())
 for _,city in player:GetCities():Members()do
  local districts=city:GetDistricts()
  for di=0,districts:GetNumDistricts()-1 do
   local district=districts:GetDistrictByIndex(di)
   if district and district:GetType()==definition.Index then
    local plot=assert(Map.GetPlot(district:GetX(),district:GetY()))
    local index=plot:GetIndex();sites=sites+1
    local current,base,millWind,millWater,percent=zero(),zero(),zero(),zero(),zero()
    local activePercent=zero();local propertyMismatches=0
    for _,rule in ipairs(A.ByDistrict[definition.DistrictType]or{})do
     local key=yieldKey(rule.YieldType)
     if key and(rule.ProvideType=='SelfBonus'or rule.ProvideType=='SelfMultiplier')then
      local eligible=A.Eligible(rule,city,pid)
      local active=district:IsComplete()and eligible
      local count=A.Count(rule,plot,city,pid)
      local amount=A.Amount(rule,count)
      local expected=active and amount or 0
      local stored=plot:GetProperty('CSC_ADJ_'..rule.ID..'_ENCODED_AMOUNT')
      local agrees=stored==expected or stored==nil and expected==0
      if not agrees then propertyMismatches=propertyMismatches+1 end
      local mill=quarterKey=='BAKERS'and rule.ModifierOwner=='BuildingModifiers'
       and(rule.WhoIsTheOwner==wind or rule.WhoIsTheOwner==water)
      if rule.ProvideType=='SelfBonus'then
       current[key]=current[key]+expected
       if mill then
        local values=rule.WhoIsTheOwner==wind and millWind or millWater
        values[key]=values[key]+amount
       elseif eligible then base[key]=base[key]+amount end
      elseif eligible then
       percent[key]=percent[key]+amount
       if active then activePercent[key]=activePercent[key]+amount end
      end
      emit{kind='rule',plot=index,id=rule.ID,yield=key,provider=rule.ProvideType,
       source=rule.AdjacencyType,object=rule.CustomAdjacentObject,owner=rule.ModifierOwner,
       ownerType=rule.WhoIsTheOwner,count=count,amount=amount,eligible=eligible,
       active=active,expected=expected,stored=stored,propertyAgrees=agrees,mill=mill==true}
     end
    end
    local function millState(kind)
     local b=assert(GameInfo.Buildings[kind]);local buildings=city:GetBuildings()
     local exists=buildings:HasBuilding(b.Index)and buildings:GetBuildingLocation(b.Index)==index
     return exists and(buildings:IsPillaged(b.Index)and'pillaged'or'working')or'absent'
    end
    local function withMill(add)
     local value=zero();for key,n in pairs(base)do value[key]=n+add[key]end
     return apply(value,percent)
    end
    local supplies=P.ReadSuppliers(player,plot,profile)
    local baseWorking,specWorking=0,0
    for _,m in ipairs(supplies.base)do if m.working then baseWorking=baseWorking+1 end end
    for _,m in ipairs(supplies.specialty)do if m.working then specWorking=specWorking+1 end end
    local cfg=PlayerConfigurations[pid]
    local planned=CSC_AI_QuarterAdjacencyValue(definition.DistrictType,plot,city,pid,true)
    emit{kind='site',quarter=quarterKey,player=pid,city=city:GetID(),name=city:GetName(),civilization=cfg:GetCivilizationTypeName(),
     plot=index,x=plot:GetX(),y=plot:GetY(),complete=district:IsComplete(),pillaged=district:IsPillaged(),
     hills=plot:IsHills(),river=plot:IsRiver(),riverEdges=plot:GetRiverCrossingCount(),
     wind=quarterKey=='BAKERS'and millState(wind)or nil,water=quarterKey=='BAKERS'and millState(water)or nil,current=apply(current,activePercent),
     withoutMill=apply(base,percent),withWind=quarterKey=='BAKERS'and withMill(millWind)or nil,
     withWater=quarterKey=='BAKERS'and plot:IsRiver()and withMill(millWater)or nil,
     planner={production=planned.production,gold=planned.gold,total=planned.total},
     base=#supplies.base,spec=#supplies.specialty,baseWorking=baseWorking,specWorking=specWorking,
     propertyMismatches=propertyMismatches}
    for _,near in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY()))do
     local r=GameInfo.Resources[near:GetResourceType()]
     local d=GameInfo.Districts[near:GetDistrictType()]
     local imp=GameInfo.Improvements[near:GetImprovementType()]
     emit{kind='neighbor',plot=index,neighbor=near:GetIndex(),owner=near:GetOwner(),
      terrain=GameInfo.Terrains[near:GetTerrainType()].TerrainType,hills=near:IsHills(),
      resource=r and r.ResourceType or '-',district=d and d.DistrictType or '-',
      improvement=imp and imp.ImprovementType or '-',improvementPillaged=near:IsImprovementPillaged()}
    end
   end
  end
 end
end
end
print('CSC_QUARTER_ADJ_END',Game.GetCurrentGameTurn(),sites,emitted)
