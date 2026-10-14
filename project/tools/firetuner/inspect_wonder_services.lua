-- Read-only diagnosis; run in the GameCore_Tuner context with an affected save.
local hosts={
    {"BUILDING_BOLSHOI_THEATRE","BOLSHOI"},
    {"BUILDING_BROADWAY","BROADWAY"},
    {"BUILDING_SYDNEY_OPERA_HOUSE","SYDNEY"},
};
local function property(owner,key)
    if owner==nil then return "nil";end;
    local value=owner:GetProperty(key);return tostring(value);
end;
local function location(buildings,row)
    if row==nil or not buildings:HasBuilding(row.Index)then return -1;end;
    return buildings:GetBuildingLocation(row.Index);
end;
local fashion=GameInfo.Buildings.BUILDING_CSC_TAILORS_FASHION_HOUSE;
local quarter=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER;
local civic=GameInfo.Civics.CIVIC_OPERA_BALLET;
print("[CSC_WONDER_INSPECT] playerCount="..tostring(PlayerManager.GetWasEverAliveCount()));
for _,player in ipairs(PlayerManager.GetAlive())do
    local cities=player:GetCities();
    print("[CSC_WONDER_INSPECT] player="..player:GetID().." cities="..tostring(cities));
    if cities~=nil then
        for _,city in cities:Members()do
            local buildings=city:GetBuildings();
            if fashion~=nil and buildings:HasBuilding(fashion.Index)then
                local districts=city:GetDistricts();
                local x,y=districts:GetDistrictLocation(quarter.Index);
                print("[CSC_WONDER_INSPECT] seller="..city:GetOwner()..":"..city:GetID()
                    .." name="..city:GetName().." quarter="..tostring(x)..","..tostring(y)
                    .." suppliedCity="..property(city,"CSC_TAILORS_FASHION_HOUSE_SUPPLIED")
                    .." suppliedCenter="..property(Map.GetPlot(city:GetX(),city:GetY()),"CSC_TAILORS_FASHION_HOUSE_SUPPLIED")
                    .." housePillaged="..tostring(buildings:IsPillaged(fashion.Index))
                    .." quarterPillaged="..tostring(districts:GetDistrict(quarter.Index):IsPillaged())
                    .." civic="..tostring(player:GetCulture():HasCivic(civic.Index)));
                for direction=0,5 do
                    local plot=Map.GetAdjacentPlot(x,y,direction);
                    if plot~=nil then
                        print("[CSC_WONDER_INSPECT] sellerAdjacent="..plot:GetIndex());
                    end;
                end;
            end;
            for _,pair in ipairs(hosts)do
                local host=GameInfo.Buildings[pair[1]];
                local service=GameInfo.Buildings["BUILDING_CSC_TAILORS_STAGE_4_SERVICE_"..pair[2]];
                local hostPlot=location(buildings,host);
                if hostPlot~=nil and hostPlot>=0 then
                    local ready="CSC_TAILORS_STAGE_4_SERVICE_"..pair[2].."_READY";
                    print("[CSC_WONDER_INSPECT] customer="..city:GetOwner()..":"..city:GetID()
                        .." name="..city:GetName().." host="..pair[1].." plot="..hostPlot
                        .." servicePlot="..tostring(location(buildings,service))
                        .." hostPillaged="..tostring(buildings:IsPillaged(host.Index))
                        .." readyCity="..property(city,ready)
                        .." readyPlot="..property(Map.GetPlotByIndex(hostPlot),ready)
                        .." established="..property(city,ready.."_ESTABLISHED")
                        .." lastPlot="..property(city,ready.."_PLOT"));
                end;
            end;
        end;
    end;
end;
