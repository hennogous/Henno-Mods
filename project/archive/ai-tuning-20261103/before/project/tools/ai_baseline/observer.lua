-- Read-only CSC autoplay instrumentation. No gameplay properties or yields written.
CSCBASE = {events={},errors={},candidates={},customer_candidates={},turns={},version=1};
local B=CSCBASE;
local function json(v)
    local k=type(v);
    if k=='nil' then return 'null' end
    if k=='boolean' or k=='number' then return tostring(v) end
    if k=='string' then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t'):gsub('%z','')..'"' end
    if k~='table' then return 'null' end
    local parts={}; local n=0; local array=true;
    for key in pairs(v) do n=n+1; if type(key)~='number' then array=false end end
    if n~=#v then array=false end
    if array then for _,x in ipairs(v) do parts[#parts+1]=json(x) end; return '['..table.concat(parts,',')..']' end
    for key,x in pairs(v) do parts[#parts+1]=json(tostring(key))..':'..json(x) end
    return '{'..table.concat(parts,',')..'}';
end
local function kind(tab,index,field) local r=GameInfo[tab][index]; return r and r[field] or nil end
local function protect(name,fn)
    return function(...) local ok,err=pcall(fn,...); if not ok then B.errors[#B.errors+1]={turn=Game.GetCurrentGameTurn(),name=name,error=tostring(err)} end end;
end
B.quarters={};
for r in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local q=B.quarters[r.QuarterKey] or {key=r.QuarterKey,district='DISTRICT_CSC_'..r.QuarterKey..'_QUARTER',base={},spec={},sales={}};
    B.quarters[r.QuarterKey]=q;
    local target=r.SourceTag:match('_BASE$') and q.base or q.spec;
    for t in GameInfo.TypeTags() do if t.Tag==r.SourceTag and GameInfo.Resources[t.Type] then target[t.Type]=true end end;
end
for key,q in pairs(B.quarters) do for t in GameInfo.TypeTags() do if t.Tag=='CLASS_CSC_'..key..'_SALES' then q.sales[t.Type]=true end end end
function B.site(plot,pid,q)
    local v={plot=plot:GetIndex(),base=0,spec=0,base_any=0,spec_any=0,base_improved=0,spec_improved=0,sales=0,quarters=0,sales_plots={},materials={},river=plot:IsRiver(),hills=plot:IsHills()};
    for _,p in ipairs(Map.GetAdjacentPlots(plot:GetX(),plot:GetY())) do
        local res=kind('Resources',p:GetResourceType(),'ResourceType');
        local visible=res and CSC_Adjacency.ResourceVisible(pid,p:GetResourceType());
        local cat=visible and (q.base[res] and 'base' or q.spec[res] and 'spec');
        if cat then
            v[cat..'_any']=v[cat..'_any']+1;
            if p:GetOwner()==pid then v[cat]=v[cat]+1; if p:GetImprovementType()~=-1 and not p:IsImprovementPillaged() then v[cat..'_improved']=v[cat..'_improved']+1 end end
            v.materials[#v.materials+1]={plot=p:GetIndex(),resource=res,category=cat,owner=p:GetOwner(),improvement=kind('Improvements',p:GetImprovementType(),'ImprovementType'),pillaged=p:IsImprovementPillaged()};
        end
        local dt=kind('Districts',p:GetDistrictType(),'DistrictType');
        if dt==q.district and p:GetOwner()==pid then v.quarters=v.quarters+1 end
        if dt and q.sales[dt] and p:GetOwner()==pid then v.sales=v.sales+1;v.sales_plots[#v.sales_plots+1]=p:GetIndex() end
    end
    return v;
end
function B.options(city,q,districtType)
    local pid=city:GetOwner(); local result={};
    local plots=CSC_Adjacency.PlotsInBand(Map.GetPlot(city:GetX(),city:GetY()),0,3);
    for _,p in ipairs(plots) do
        if p:GetOwner()==pid and p:GetDistrictType()==-1 then
            local pc=Cities.GetPlotPurchaseCity(p);
            if pc and pc:GetID()==city:GetID() and pc:GetOwner()==pid then
                local ok,allowed=pcall(function() return p:CanHaveDistrict(GameInfo.Districts[districtType or q.district].Index,pid,city:GetID()) end);
                if ok and allowed then result[#result+1]=B.site(p,pid,q) end
            end
        end
    end
    return result;
end
local function citykey(pid,cid,q) return pid..':'..cid..':'..q end
local function scanPlayer(pid)
    local p=Players[pid]; if not p or not p:IsMajor() then return end
    B.turns[tostring(pid)]=Game.GetCurrentGameTurn();
    local existing={};
    for _,city in p:GetCities():Members() do
        local ds=city:GetDistricts();for i=0,ds:GetNumDistricts()-1 do existing[kind('Districts',ds:GetDistrictByIndex(i):GetType(),'DistrictType')]=true end
    end
    for _,c in p:GetCities():Members() do
        for key,q in pairs(B.quarters) do
            if not c:GetDistricts():HasDistrict(GameInfo.Districts[q.district].Index) then
                B.candidates[citykey(pid,c:GetID(),key)]={turn=Game.GetCurrentGameTurn(),sites=B.options(c,q)};
            end
            if existing[q.district] then
                for dt in pairs(q.sales) do
                    if dt~='DISTRICT_CITY_CENTER' and not c:GetDistricts():HasDistrict(GameInfo.Districts[dt].Index) then
                        B.customer_candidates[citykey(pid,c:GetID(),key)..':'..dt]={turn=Game.GetCurrentGameTurn(),sites=B.options(c,q,dt)};
                    end
                end
            end
        end
    end
end
Events.PlayerTurnActivated.Add(protect('candidate scan',scanPlayer));
Events.DistrictAddedToMap.Add(protect('district placed',function(pid,did,cid,x,y,di)
    local dt=kind('Districts',di,'DistrictType');local p=Map.GetPlot(x,y);
    local e={event='district',turn=Game.GetCurrentGameTurn(),player=pid,city=cid,district=dt,plot=p:GetIndex(),x=x,y=y,quarter_sites={},customer_candidates={}};
    for key,q in pairs(B.quarters) do
        if dt==q.district then e.quarter=key;e.site=B.site(p,pid,q);e.previous_candidates=B.candidates[citykey(pid,cid,key)] end
        if q.sales[dt] then
            local neighbors={};for _,a in ipairs(Map.GetAdjacentPlots(x,y)) do if kind('Districts',a:GetDistrictType(),'DistrictType')==q.district and a:GetOwner()==pid then neighbors[#neighbors+1]=a:GetIndex() end end
            e.quarter_sites[key]=neighbors;
            e.customer_candidates[key]=B.customer_candidates[citykey(pid,cid,key)..':'..dt];
        end
    end
    B.events[#B.events+1]=e;
end));
Events.ImprovementAddedToMap.Add(protect('improvement added',function(x,y,ii,pid)
    local p=Map.GetPlot(x,y);B.events[#B.events+1]={event='improvement',turn=Game.GetCurrentGameTurn(),plot=p:GetIndex(),owner=p:GetOwner(),resource=kind('Resources',p:GetResourceType(),'ResourceType'),improvement=kind('Improvements',p:GetImprovementType(),'ImprovementType')};
end));
function B.snapshot()
    local s={version=B.version,turn=Game.GetCurrentGameTurn(),events=B.events,errors=B.errors,quarters=B.quarters,players={},cities={},plots={},options={}};
    for _,p in ipairs(PlayerManager.GetAliveMajors()) do
        local id=p:GetID();local pc=PlayerConfigurations[id];local pr={id=id,human=p:IsHuman(),civ=kind('Civilizations',pc:GetCivilizationTypeID(),'CivilizationType'),leader=kind('Leaders',pc:GetLeaderTypeID(),'LeaderType'),techs={},civics={}};
        for t in GameInfo.Technologies() do if p:GetTechs():HasTech(t.Index) then pr.techs[#pr.techs+1]=t.TechnologyType end end
        for t in GameInfo.Civics() do if p:GetCulture():HasCivic(t.Index) then pr.civics[#pr.civics+1]=t.CivicType end end
        s.players[#s.players+1]=pr;
        for _,c in p:GetCities():Members() do
            local cr={player=id,id=c:GetID(),name=c:GetName(),x=c:GetX(),y=c:GetY(),population=c:GetPopulation(),districts={},buildings={},properties={},yields={}};
            for b in GameInfo.Buildings() do if c:GetBuildings():HasBuilding(b.Index) then cr.buildings[#cr.buildings+1]={type=b.BuildingType,plot=c:GetBuildings():GetBuildingLocation(b.Index),pillaged=c:GetBuildings():IsPillaged(b.Index)} end end
            for _,key in ipairs({'CSC_BAKERS_STAGE_2_EFFECT_GROWTH','CSC_BAKERS_STAGE_3_EFFECT_HOUSING','CSC_BAKERS_STAGE_4_EFFECT_TOURISM','CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION','CSC_TAILORS_STAGE_3_EFFECT_FAITH','CSC_TAILORS_STAGE_4_EFFECT_TOURISM'}) do cr.properties[key]=c:GetProperty(key) or 0 end
            for y in GameInfo.Yields() do if y.YieldType:match('^YIELD_') then local ok,v=pcall(function() return c:GetYield(y.Index) end);if ok then cr.yields[y.YieldType]=v end end end
            local ds=c:GetDistricts();for i=0,ds:GetNumDistricts()-1 do
                local d=ds:GetDistrictByIndex(i);local dt=kind('Districts',d:GetType(),'DistrictType');local plot=Map.GetPlot(d:GetX(),d:GetY());
                local dr={type=dt,plot=plot:GetIndex(),x=d:GetX(),y=d:GetY(),complete=d:IsComplete(),pillaged=d:IsPillaged(),yields={}};
                for y in GameInfo.Yields() do local ok,v=pcall(function() return d:GetYield(y.Index) end);if ok then dr.yields[y.YieldType]=v end end
                for key,q in pairs(B.quarters) do if dt==q.district then dr.quarter=key;dr.site=B.site(plot,id,q) end end
                cr.districts[#cr.districts+1]=dr;
            end
            for key,q in pairs(B.quarters) do if not ds:HasDistrict(GameInfo.Districts[q.district].Index) then s.options[#s.options+1]={player=id,city=c:GetID(),quarter=key,sites=B.options(c,q)} end end
            s.cities[#s.cities+1]=cr;
        end
    end
    local w,h=Map.GetGridSize();s.width=w;s.height=h;
    for index=0,w*h-1 do local p=Map.GetPlotByIndex(index);
        if p:GetOwner()>=0 or p:GetResourceType()>=0 or p:GetDistrictType()>=0 then
            s.plots[#s.plots+1]={index=index,x=p:GetX(),y=p:GetY(),owner=p:GetOwner(),resource=kind('Resources',p:GetResourceType(),'ResourceType'),improvement=kind('Improvements',p:GetImprovementType(),'ImprovementType'),pillaged=p:IsImprovementPillaged(),terrain=kind('Terrains',p:GetTerrainType(),'TerrainType'),feature=kind('Features',p:GetFeatureType(),'FeatureType'),district=kind('Districts',p:GetDistrictType(),'DistrictType'),yields={p:GetYield(0),p:GetYield(1),p:GetYield(2),p:GetYield(3),p:GetYield(4),p:GetYield(5)}};
        end
    end
    print('CSCBASE_SNAPSHOT='..json(s));
end
for _,p in ipairs(PlayerManager.GetAliveMajors()) do protect('initial candidates',scanPlayer)(p:GetID()) end
print('CSCBASE_OBSERVER_READY');
