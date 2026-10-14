-- Extends cafe_stage4_world.lua with real building plots, placement and routes.
local function addInfo(table, index, kind, value)
    local row = { Index=index }; row[kind]=value;
    table[index]=row; table[value]=row;
end
addInfo(GameInfo.Districts,5,'DistrictType','DISTRICT_CSC_TAILORS_QUARTER');
addInfo(GameInfo.Districts,6,'DistrictType','DISTRICT_THEATER');
for index, name in ipairs({
    'BUILDING_CSC_TAILORS_FASHION_HOUSE','BUILDING_AMPHITHEATER',
    'BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE',
    'BUILDING_MARAE','BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',
    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY','BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',
    'BUILDING_CSC_TAILORS_TAILOR',
}) do addInfo(GameInfo.Buildings,index+4,'BuildingType',name); end
GameInfo.Civics={CIVIC_OPERA_BALLET={Index=1}};
local replacementRows={
    {ReplacesBuildingType='BUILDING_ZOO',CivUniqueBuildingType='BUILDING_THERMAL_BATH'},
    {ReplacesBuildingType='BUILDING_AMPHITHEATER',CivUniqueBuildingType='BUILDING_MARAE'},
};
GameInfo.BuildingReplaces=function()
    local i=0;return function() i=i+1;return replacementRows[i];end;
end;

local plotsByIndex={};local nextIndex=0;
local baseGetPlot=Map.GetPlot;
Map.GetPlot=function(x,y)
    local p=baseGetPlot(x,y);
    if not p.index then nextIndex=nextIndex+1;p.index=nextIndex;plotsByIndex[nextIndex]=p;end
    function p:GetIndex() return self.index;end
    return p;
end;
Map.GetPlotByIndex=function(index)return plotsByIndex[index];end;
local baseAddDistrict=addDistrict;
function addDistrict(city,type,x,y) baseAddDistrict(city,type,x,y);Map.GetPlot(x,y);end

fashionCities={};placementCalls={};capturedPrints={};
print=function(message)table.insert(capturedPrints,tostring(message));end;
hasOpera=false;
Players[0].GetID=function()return 0;end;
PlayerManager.GetAlive=function()return {Players[0]};end;
Players[0].GetCulture=function()return {HasCivic=function(_,i)return i==1 and hasOpera;end};end;
Players[0].GetCities=(function(base)
    return function()
        local cities=base();cities.FindID=function(_,id)for _,c in ipairs(fashionCities)do if c.id==id then return c;end;end;end;
        return cities;
    end;
end)(Players[0].GetCities);
local baseAddCity=addCity;
function addCity(id,population)
    local city=baseAddCity(id,population);table.insert(fashionCities,city);
    city.center=Map.GetPlot(city:GetX(),city:GetY());city.locations={};city.routes={};
    function city:GetName()return 'City'..tostring(self.id);end
    local baseGetDistricts=city.GetDistricts;
    function city:GetDistricts()
        local districts=baseGetDistricts(self);
        districts.GetDistrict=function(_,index)
            if self.districts[index]~=nil then
                return {IsPillaged=function()return self.pillagedDistricts[index] or false;end};
            end;
        end;
        return districts;
    end;
    local baseGetBuildings=city.GetBuildings;
    function city:GetBuildings()
        local buildings=baseGetBuildings(self);
        buildings.GetBuildingLocation=function(_,i)return self.locations[i] or -1;end;
        buildings.RemoveBuilding=function(_,i)self.buildings[i]=nil;self.locations[i]=nil;end;
        buildings.GetBuildingsAtLocation=function(_,plot)
            local result={};for i,p in pairs(self.locations)do if p==plot and self.buildings[i]then table.insert(result,i);end;end;return result;
        end;
        return buildings;
    end
    function city:GetBuildQueue()
        return {CreateBuilding=function(_,i,p)
            self.buildings[i]=true;self.locations[i]=p;
            table.insert(placementCalls,{city=self.id,building=i,plot=p});
        end};
    end
    function city:GetTrade()return {GetOutgoingRoutes=function()return self.routes;end};end
    return city;
end
function addWonder(city,type,x,y)
    addBuilding(city,type);city.locations[GameInfo.Buildings[type].Index]=Map.GetPlot(x,y):GetIndex();
end
CityManager={GetCityAt=function(x,y)for _,c in ipairs(fashionCities)do if c:GetX()==x and c:GetY()==y then return c;end;end;end};
PlayerOperations={EXECUTE_SCRIPT=1};
UI={RequestPlayerOperation=function(playerID,operation,parameters)
    CSC_SetBakersTradeRouteProperties(playerID,parameters);
end};
GameEvents={CSC_SetBakersTradeRouteProperties={Add=function()end}};
FOOD_INDEX=0;PRODUCTION_INDEX=1;GOLD_INDEX=2;SCIENCE_INDEX=3;CULTURE_INDEX=4;FAITH_INDEX=5;
Locale={Lookup=function(key)return key;end};
