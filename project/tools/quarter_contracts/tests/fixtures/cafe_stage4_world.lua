-- Minimal game API fixture; the tests execute CSC's unchanged gameplay script.
local function info(rows)
    local object = {};
    for _, row in ipairs(rows) do
        if row.Index ~= nil then object[row.Index] = row; end
        for key, value in pairs(row) do
            if key:match('Type$') then object[value] = row; end
        end
    end
    return setmetatable(object, {__call=function()
        local i=0;
        return function() i=i+1; return rows[i]; end;
    end});
end
GameInfo = {
    Districts=info({
        {Index=0, DistrictType='DISTRICT_CSC_BAKERS_QUARTER'},
        {Index=1, DistrictType='DISTRICT_ENTERTAINMENT_COMPLEX'},
        {Index=2, DistrictType='DISTRICT_WATER_ENTERTAINMENT_COMPLEX'},
        {Index=3, DistrictType='DISTRICT_LEU_GARDEN'},
        {Index=4, DistrictType='DISTRICT_STREET_CARNIVAL'},
    }),
    Buildings=info({
        {Index=0, BuildingType='BUILDING_CSC_BAKERS_CAFE'},
        {Index=1, BuildingType='BUILDING_ZOO'},
        {Index=2, BuildingType='BUILDING_FERRIS_WHEEL'},
        {Index=3, BuildingType='BUILDING_LEU_CONSERVATORY'},
        {Index=4, BuildingType='BUILDING_THERMAL_BATH'},
    }),
    DistrictReplaces=info({{ReplacesDistrictType='DISTRICT_ENTERTAINMENT_COMPLEX', CivUniqueDistrictType='DISTRICT_STREET_CARNIVAL'}}),
    BuildingReplaces=info({{ReplacesBuildingType='BUILDING_ZOO', CivUniqueBuildingType='BUILDING_THERMAL_BATH'}}),
    CSC_Stage3CustomerTransactions=info({}),
};
local plots = {};
local function plot(x,y)
    local key=tostring(x)..','..tostring(y);
    if not plots[key] then
        plots[key]={x=x,y=y,properties={},
            GetX=function(self) return self.x; end,
            GetY=function(self) return self.y; end,
            GetProperty=function(self,k) return self.properties[k]; end,
            SetProperty=function(self,k,v) self.properties[k]=v; end,
        };
    end
    return plots[key];
end
local offsets={{1,0},{0,1},{-1,1},{-1,0},{0,-1},{1,-1}};
NUM_DIRECTIONS=6;
Map={GetPlot=plot, GetAdjacentPlot=function(x,y,d)
    local offset=offsets[d+1]; return plots[tostring(x+offset[1])..','..tostring(y+offset[2])];
end};
local cities={};
Players={[0]={GetCities=function()
    return {Members=function()
        local i=0; return function() i=i+1; if cities[i] then return i,cities[i]; end; end;
    end};
end}};
PlayerManager={GetWasEverAliveCount=function() return 1; end};
Players[0].GetID=function()return 0;end;
PlayerManager.GetAlive=function()return {Players[0]};end;
Events={PlayerTurnActivated={Add=function() end}};

function addCity(id,population)
    local city={id=id,owner=0,population=population,properties={},buildings={},districts={},pillagedBuildings={},pillagedDistricts={}};
    city.center=plot(20+id,20);
    function city:GetOwner() return self.owner; end
    function city:GetID() return self.id; end
    function city:GetPopulation() return self.population; end
    function city:GetX() return self.center.x; end
    function city:GetY() return self.center.y; end
    function city:GetProperty(k) return self.properties[k]; end
    function city:SetProperty(k,v) self.properties[k]=v; end
    function city:GetBuildings()
        return {HasBuilding=function(_,i) return self.buildings[i] or false; end,
            IsPillaged=function(_,i) return self.pillagedBuildings[i] or false; end};
    end
    function city:GetDistricts()
        return {HasDistrict=function(_,i) return self.districts[i]~=nil; end,
            IsPillaged=function(_,i) return self.pillagedDistricts[i] or false; end,
            GetDistrictLocation=function(_,i) local p=self.districts[i]; return p.x,p.y; end};
    end
    table.insert(cities,city);
    return city;
end
function addDistrict(city,type,x,y) city.districts[GameInfo.Districts[type].Index]=plot(x,y); end
function addBuilding(city,type) city.buildings[GameInfo.Buildings[type].Index]=true; end
