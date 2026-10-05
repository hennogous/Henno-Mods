-- Deterministic small hex worlds for behavioral comparisons, not game content.
function table.count(items) local n=0; for _ in pairs(items or {}) do n=n+1; end; return n; end
function info(rows)
    local object={};
    for _,r in ipairs(rows) do
        if r.Index then object[r.Index]=r; end
        for key,value in pairs(r) do if key:find('Type$') or key=='Tag' then object[value]=r; end end
    end
    return setmetatable(object,{__call=function() local i=0; return function() i=i+1; return rows[i]; end; end});
end
GameInfo=setmetatable({}, {__index=function(self,key) local value=info({}); rawset(self,key,value); return value; end});
GameInfo.Resources=info({
    {Index=0,ResourceType='RESOURCE_VISIBLE',ResourceClassType='RESOURCECLASS_BONUS'},
    {Index=1,ResourceType='RESOURCE_HIDDEN',ResourceClassType='RESOURCECLASS_STRATEGIC',PrereqTech='TECH_REVEAL'},
    {Index=2,ResourceType='RESOURCE_CIVIC',ResourceClassType='RESOURCECLASS_LUXURY',PrereqCivic='CIVIC_REVEAL'}
});
GameInfo.Technologies=info({{Index=0,TechnologyType='TECH_REVEAL'}});
GameInfo.Civics=info({{Index=0,CivicType='CIVIC_REVEAL'}});
GameInfo.Tags=info({{Tag='CLASS_TEST',Vocabulary='RESOURCE_CLASS'},{Tag='CLASS_DISTRICT_TEST',Vocabulary='DISTRICT_CLASS'}});
GameInfo.Districts=info({{Index=0,DistrictType='DISTRICT_TEST'},{Index=1,DistrictType='DISTRICT_WONDER'}});
GameInfo.Buildings=info({{Index=0,BuildingType='BUILDING_WONDER_TEST',Name='Test Wonder'},
    {Index=1,BuildingType='BUILDING_WRONG_WONDER',Name='Wrong Wonder'},{Index=2,BuildingType='BUILDING_MILL',Name='Mill'}});
GameInfo.Routes=info({{Index=0,RouteType='ROUTE_TEST'}});
GameInfo.Units=info({{Index=0,UnitType='UNIT_TEST'}});
GameInfo.Improvements=info({{Index=0,ImprovementType='IMPROVEMENT_TEST',AirSlots=2}});
GameInfo.Features=info({{Index=0,FeatureType='FEATURE_TEST'}});
GameInfo.Terrains=info({{Index=0,TerrainType='TERRAIN_TEST'}});
GameInfo.Yields=info({{Index=0,YieldType='YIELD_PRODUCTION',Name='LOC_YIELD_PRODUCTION',IconString='[ICON_Production]'}});
GameInfo.TypeTags=info({{Type='RESOURCE_VISIBLE',Tag='CLASS_TEST'},{Type='RESOURCE_HIDDEN',Tag='CLASS_TEST'},
    {Type='DISTRICT_TEST',Tag='CLASS_DISTRICT_TEST'}});
DefenseTypes={DISTRICT_GARRISON=0,DISTRICT_OUTER=1};
DirectionTypes={DIRECTION_NORTHEAST=0,DIRECTION_EAST=1,DIRECTION_SOUTHEAST=2,
    DIRECTION_SOUTHWEST=3,DIRECTION_WEST=4,DIRECTION_NORTHWEST=5,NO_DIRECTION=-1,NUM_DIRECTION_TYPES=6};
DB={MakeHash=function(s) return 'HASH_'..tostring(s); end};
local offsets={{0,1},{1,0},{1,-1},{0,-1},{-1,0},{-1,1}};
local plotMethods={};
function plotMethods:GetX() return self.x; end
function plotMethods:GetY() return self.y; end
function plotMethods:GetIndex() return self.index; end
function plotMethods:GetOwner() return self.owner; end
function plotMethods:GetResourceType() return self.resource; end
function plotMethods:GetDistrictType() return self.district; end
function plotMethods:GetDistrictID() return self.index; end
function plotMethods:GetWonderType() return self.wonder; end
function plotMethods:IsWonderComplete() return self.complete; end
function plotMethods:GetRouteType() return self.route; end
function plotMethods:GetWorkerCount() return self.workers; end
function plotMethods:GetUnitCount() return #self.units; end
function plotMethods:GetImprovementType() return self.improvement; end
function plotMethods:IsImprovementPillaged() return self.pillaged or false; end
function plotMethods:GetFeatureType() return self.feature; end
function plotMethods:GetTerrainType() return self.terrain; end
function plotMethods:GetYield(_) return self.yield; end
function plotMethods:GetAppeal() return self.appeal; end
function plotMethods:GetAirUnits() return self.airunits; end
function plotMethods:GetRiverCrossingCount() return self.riverCount; end
function plotMethods:GetProperty(key) return self.properties[key]; end
function plotMethods:SetProperty(key,value) self.properties[key]=value; end
function plotMethods:IsWOfRiver() return self.riverE; end
function plotMethods:IsNWOfRiver() return self.riverSE; end
function plotMethods:IsNEOfRiver() return self.riverSW; end
for _,method in ipairs({'IsMountain','IsHills','IsFlatlands','IsWater','IsShallowWater','IsLake','IsCanyon',
    'IsCoastalLand','IsRiverCrossing','IsOpenGround','IsRoughGround','IsFreshWater','IsNationalPark'}) do
    plotMethods[method]=function(self) return self.flags[method]==true; end
end
local districtMethods={};
function districtMethods:GetMaxDamage(defense) return defense==0 and 100 or 60; end
function districtMethods:GetDamage(defense) return defense==0 and 20 or 10; end
function districtMethods:GetDefenseStrength() return 30.6; end
function districtMethods:GetYield(_) return 4; end
function districtMethods:GetProperty(key) return self.plot.properties[key]; end
function districtMethods:GetAirSlots() return 3; end
function districtMethods:GetAirUnits() return true,{1}; end
function districtMethods:GetType() return self.plot.district; end
function districtMethods:GetX() return self.plot.x; end
function districtMethods:GetY() return self.plot.y; end
function districtMethods:IsComplete() return self.plot.complete; end
local tech={};
function tech:HasTech(_) return discoveredTech; end
function tech:HasCivic(_) return discoveredCivic; end
local cityMethods={};
function cityMethods:GetOwner() return self.owner; end
function cityMethods:GetID() return self.owner; end
function cityMethods:GetBuildings() return {HasBuilding=function(_,index) return index==2 and self.mill; end}; end
function cityMethods:GetDistricts()
    local districts={};
    for _,plot in ipairs(world) do
        if plot.owner==self.owner and plot.district>=0 then districts[#districts+1]=setmetatable({plot=plot},{__index=districtMethods}); end
    end
    return {GetNumDistricts=function() return #districts; end,
        GetDistrictByIndex=function(_,index) return districts[index+1]; end};
end
city=setmetatable({owner=0,mill=false},{__index=cityMethods});
otherCity=setmetatable({owner=0,mill=false},{__index=cityMethods});
Players={};
for id=0,1 do
    local player={id=id};
    function player:GetID() return self.id; end
    function player:IsHuman() return self.id==0; end
    function player:GetTechs() return tech; end
    function player:GetCulture() return tech; end
    function player:GetCities() return {Members=function() local i=0; return function() i=i+1; if i==1 then return i,city; elseif i==2 then return i,otherCity; end; end; end}; end
    function player:GetDistricts()
        return {FindID=function(_,index)
            local p=world[index+1];
            return p and p.district>=0 and setmetatable({plot=p},{__index=districtMethods});
        end};
    end
    Players[id]=player;
end
PlayerManager={GetAliveMajors=function() return {Players[0]}; end};
Game={GetLocalPlayer=function() return 0; end};
Units={GetUnitsInPlot=function(p) return p.units; end};
local unit={GetType=function() return 0; end,GetExperience=function() return {GetLevel=function() return 2; end}; end,
    GetOwner=function() return 0; end,GetID=function() return 1; end,
    GetAirSlots=function() return 1; end,GetAirUnits=function() return true,{1}; end};
function resetWorld(w,h,wrap)
    width=w or 7; height=h or 7; wrapped=wrap or false;
    discoveredTech=false; discoveredCivic=false; city.mill=false; otherCity.mill=false;
    world={};
    for y=0,height-1 do for x=0,width-1 do
        local n=y*width+x;
        world[n+1]=setmetatable({x=x,y=y,index=n,owner=(n%3==0 and 1 or 0),resource=n%3,
            district=n%2,wonder=n%2,complete=n%4~=0,route=n%2-1,workers=1,units={unit},
            improvement=0,feature=0,terrain=0,yield=3,appeal=2,airunits={1},riverCount=3,
            flags={IsHills=true,IsLake=true,IsFreshWater=true,IsNationalPark=true},
            properties={TEST=5,HASH_TEST=6}},{__index=plotMethods});
    end end
    center=Map.GetPlot(math.floor(width/2),math.floor(height/2)); center.owner=0;
end
Map={};
function Map.GetPlot(x,y)
    if wrapped then x=x%width; y=y%height; end
    if x<0 or x>=width or y<0 or y>=height then return nil; end
    return world[y*width+x+1];
end
function Map.GetPlotByIndex(n) return world[n+1]; end
function Map.GetAdjacentPlot(x,y,d) local delta=offsets[d+1]; return Map.GetPlot(x+delta[1],y+delta[2]); end
function Map.GetAdjacentPlots(x,y)
    local result={}; for d=0,5 do local p=Map.GetAdjacentPlot(x,y,d); if p then result[#result+1]=p; end; end; return result;
end
function Map.GetPlotDistance(x,y,u,v)
    local best=10000;
    local first,last=0,0; if wrapped then first,last=-1,1; end
    for a=first,last do for b=first,last do
        local dx=u+a*width-x; local dy=v+b*height-y;
        best=math.min(best,math.max(math.abs(dx),math.abs(dy),math.abs(dx+dy)));
    end end
    return best;
end
function GetPlayerIDFromPlot(x,y) return Map.GetPlot(x,y):GetOwner(); end
Locale={Lookup=function(key,...) return key..' '..table.concat({...},' '); end};
Events=setmetatable({}, {__index=function(self,key) local e={Add=function(_) end}; rawset(self,key,e); return e; end});
GameEvents=Events;
PlayerConfigurations={};
resetWorld();
