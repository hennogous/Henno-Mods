-- Read-only facts for one declared, existing-save Avignon fixture.
local function json(v)
 local t=type(v)
 if t=='nil'then return 'null'end
 if t=='boolean'or t=='number'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local n,array=0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end;local a={}
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end
 return '{'..table.concat(a,',')..'}'
end
local function call(o,k,...)
 if not o or type(o[k])~='function'then return {unavailable=k}end
 local ok,v=pcall(o[k],o,...);if ok then return v end
 return {error=tostring(v)}
end
local d=assert(GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER)
local out={turn=Game.GetCurrentGameTurn(),districtCatalog={},mapping={},assistance={},target={player=4,city=655369,exists=false}}
out.width,out.height=Map.GetGridSize()
local count,maxIndex=0,-1
for row in GameInfo.Districts()do
 count=count+1;maxIndex=math.max(maxIndex,row.Index)
 out.districtCatalog[#out.districtCatalog+1]={index=row.Index,type=row.DistrictType}
end
out.mapping={districtIndex=d.Index,districtType=d.DistrictType,districtCount=count,districtIndexLimit=maxIndex+1}
out.definition={type=d.DistrictType,requiresPlacement=d.RequiresPlacement,internalOnly=d.InternalOnly,onePerCity=d.OnePerCity,prereqTech=d.PrereqTech,prereqCivic=d.PrereqCivic}
out.player0={human=Players[0]:IsHuman(),alive=Players[0]:IsAlive()}
out.assistance.mode='OFF'
if GameInfo.CSC_AI_Profile then for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then out.assistance.mode=row.Mode end end end
for _,k in ipairs({'TOTALS','ERROR_INDEX','PURCHASE_INDEX','FOUNDATION_INDEX','INITIAL_HUMANS'})do out.assistance[k]=Game:GetProperty('CSC_AI_ASSISTANCE_V1_'..k)end
out.assistance.turnCycles={};out.assistance.pending={}
for pid=0,61 do
 local cycle=Game:GetProperty('CSC_AI_ASSISTANCE_V1_TURN_'..pid)
 local pending=Game:GetProperty('CSC_AI_ASSISTANCE_V1_PENDING_'..pid)
 if cycle~=nil then out.assistance.turnCycles[tostring(pid)]=cycle end
 if pending~=nil then out.assistance.pending[tostring(pid)]=pending end
end
local p=assert(Players[4]);local target=out.target
target.human=p:IsHuman();target.alive=p:IsAlive();target.major=p:IsMajor()
for _,c in p:GetCities():Members()do if c:GetID()==655369 then
 target.exists=true;target.name=c:GetName();target.x=c:GetX();target.y=c:GetY();target.population=c:GetPopulation()
 target.districts={};local ds=c:GetDistricts()
 assert(type(ds.GetNumDistricts)=='function'and type(ds.GetDistrictByIndex)=='function','Native district index API unavailable')
 for i=0,ds:GetNumDistricts()-1 do
  local district=ds:GetDistrictByIndex(i)
  if district then target.districts[#target.districts+1]={index=district:GetType(),type=GameInfo.Districts[district:GetType()].DistrictType,x=district:GetX(),y=district:GetY(),complete=district:IsComplete(),pillaged=district:IsPillaged()}end
 end
 local q=c:GetBuildQueue();target.queue={production=q:CurrentlyBuilding(),hash=call(q,'GetCurrentProductionTypeHash'),size=call(q,'GetSize')}
 target.research={technology=call(p:GetTechs(),'GetResearchingTech'),civic=call(p:GetCulture(),'GetProgressingCivic')}
 local plot=assert(Map.GetPlotByIndex(3076))
 out.plot={index=plot:GetIndex(),x=plot:GetX(),y=plot:GetY(),owner=plot:GetOwner(),district=plot:GetDistrictType(),feature=plot:GetFeatureType(),resource=plot:GetResourceType(),improvement=plot:GetImprovementType(),pillaged=plot:IsImprovementPillaged(),water=plot:IsWater(),impassable=plot:IsImpassable(),revealed=PlayersVisibility[4]:IsRevealed(plot:GetX(),plot:GetY()),legal=call(plot,'CanHaveDistrict',d.Index,4,655369)}
 if Cities and type(Cities.GetPlotPurchaseCity)=='function'then
  local ok,ownerCity=pcall(Cities.GetPlotPurchaseCity,plot)
  if ok and ownerCity then out.plot.purchaseCity={player=ownerCity:GetOwner(),city=ownerCity:GetID()}end
 end
end end
print('CSC_DISTRICT_EXTENSION_WORLD='..json(out))
