-- Read-only source and endpoint facts for the two declared IZ cities.
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
local w=assert(GameInfo.Buildings.BUILDING_WORKSHOP)
local f=assert(GameInfo.Buildings.BUILDING_FACTORY)
local iz=assert(GameInfo.Districts.DISTRICT_INDUSTRIAL_ZONE)
local out={turn=Game.GetCurrentGameTurn(),targets={},buildingCatalog={},assistance={}}
out.width,out.height=Map.GetGridSize()
local count,maxIndex=0,-1
for row in GameInfo.Buildings()do
 count=count+1;maxIndex=math.max(maxIndex,row.Index)
 out.buildingCatalog[#out.buildingCatalog+1]={index=row.Index,type=row.BuildingType}
end
out.mapping={workshopIndex=w.Index,factoryIndex=f.Index,izIndex=iz.Index,buildingCount=count,buildingIndexLimit=maxIndex+1}
out.player0={human=Players[0]:IsHuman(),alive=Players[0]:IsAlive()}
out.relevantDB={buildings={},prerequisites={},cityEvents={}}
for _,row in ipairs({w,f})do
 out.relevantDB.buildings[#out.relevantDB.buildings+1]={index=row.Index,type=row.BuildingType,cost=row.Cost,tech=row.PrereqTech,district=row.PrereqDistrict,placement=row.RequiresPlacement}
end
for row in GameInfo.BuildingPrereqs()do if row.Building=='BUILDING_FACTORY'or row.Building=='BUILDING_WORKSHOP'then out.relevantDB.prerequisites[#out.relevantDB.prerequisites+1]={building=row.Building,prerequisite=row.PrereqBuilding}end end
local cityLists={}
for row in GameInfo.AiLists()do if row.System=='CityEvents'then cityLists[row.ListType]=true end end
for row in GameInfo.AiFavoredItems()do if cityLists[row.ListType]then out.relevantDB.cityEvents[#out.relevantDB.cityEvents+1]={list=row.ListType,event=row.Item,tree=row.StringVal,favored=row.Favored,value=row.Value}end end
out.assistance.mode='OFF'
if GameInfo.CSC_AI_Profile then for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then out.assistance.mode=row.Mode end end end
for _,k in ipairs({'TOTALS','ERROR_INDEX','PURCHASE_INDEX','FOUNDATION_INDEX','INITIAL_HUMANS','PENDING_2','PENDING_4'})do out.assistance[k]=Game:GetProperty('CSC_AI_ASSISTANCE_V1_'..k)end
out.assistance.turnCycles={};out.assistance.pending={}
for pid=0,61 do
 local cycle=Game:GetProperty('CSC_AI_ASSISTANCE_V1_TURN_'..pid)
 local pending=Game:GetProperty('CSC_AI_ASSISTANCE_V1_PENDING_'..pid)
 if cycle~=nil then out.assistance.turnCycles[tostring(pid)]=cycle end
 if pending~=nil then out.assistance.pending[tostring(pid)]=pending end
end
out.assistance.selectiveConfig=Game:GetProperty('CSC_AI_SELECTIVE_SCREEN_V1')
for _,scope in ipairs({{player=4,city=262147},{player=2,city=589832}})do
 local p=Players[scope.player]
 local row={player=scope.player,city=scope.city,exists=false}
 out.targets[#out.targets+1]=row
 if p then
  row.human=p:IsHuman();row.alive=p:IsAlive();row.major=p:IsMajor();row.gold=p:GetTreasury():GetGoldBalance()
  row.technologies={};for _,name in ipairs({'TECH_APPRENTICESHIP','TECH_INDUSTRIALIZATION','TECH_ELECTRICITY'})do local d=assert(GameInfo.Technologies[name]);row.technologies[name]=p:GetTechs():HasTech(d.Index)end
  local civic=assert(GameInfo.Civics.CIVIC_CLASS_STRUGGLE)
  row.classStruggle={owned=p:GetCulture():HasCivic(civic.Index),boost=call(p:GetCulture(),'HasBoostBeenTriggered',civic.Index),progressing=call(p:GetCulture(),'GetProgressingCivic')}
  for _,c in p:GetCities():Members()do if c:GetID()==scope.city then
   row.exists=true;row.name=c:GetName();row.x=c:GetX();row.y=c:GetY();row.population=c:GetPopulation()
   local b,q=c:GetBuildings(),c:GetBuildQueue()
   row.workshop={present=b:HasBuilding(w.Index),pillaged=b:IsPillaged(w.Index),progress=call(q,'GetBuildingProgress',w.Index)}
   row.factory={present=b:HasBuilding(f.Index),pillaged=b:IsPillaged(f.Index),progress=call(q,'GetBuildingProgress',f.Index)}
   row.queue={production=q:CurrentlyBuilding(),hash=call(q,'GetCurrentProductionTypeHash'),size=call(q,'GetSize'),entries={}}
   if type(row.queue.size)=='number'then for i=0,row.queue.size-1 do local v=call(q,'GetAt',i);local scalar={};if type(v)=='table'then for k,x in pairs(v)do if type(x)=='string'or type(x)=='number'or type(x)=='boolean'then scalar[tostring(k)]=x end end else scalar.value=tostring(v)end;row.queue.entries[#row.queue.entries+1]=scalar end end
   row.districts={}
   -- Gameplay CityDistricts lacks the UI Members iterator. This is the native
   -- index loop also used by CSC_AdjacencyGameplay and the installed AI host.
   local ds=c:GetDistricts()
   assert(type(ds.GetNumDistricts)=='function'and type(ds.GetDistrictByIndex)=='function','Native district index API unavailable')
   for i=0,ds:GetNumDistricts()-1 do
    local d=ds:GetDistrictByIndex(i)
    if d and d:GetType()==iz.Index then row.districts[#row.districts+1]={type=iz.DistrictType,complete=d:IsComplete(),pillaged=d:IsPillaged(),plot=d:GetX()+d:GetY()*out.width}end
   end
  end end
 end
end
print('CSC_IZ_WORLD='..json(out))
