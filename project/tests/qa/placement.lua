-- Read-only native-map planner. This is QA tooling, not shipped gameplay code.
QAPlacement = {};
QAPlacement.Version = 1;

local function requireAPI(value, name)
    assert(type(value)=='function','QA_PLACEMENT_BLOCKED: native API unavailable: '..name);
end

function QAPlacement.Facts(p)
    return {Plot=p:GetIndex(), X=p:GetX(), Y=p:GetY(),
        Terrain=p:GetTerrainType(), Feature=p:GetFeatureType(),
        Water=p:IsWater(), Mountain=p:IsMountain(), Impassable=p:IsImpassable(),
        NaturalWonder=p:IsNaturalWonder(), River=p:IsRiver(),
        Owner=p:GetOwner(), District=p:GetDistrictType(),
        Resource=p:GetResourceType(), Improvement=p:GetImprovementType()};
end

function QAPlacement.IsLand(p)
    return p and not p:IsWater() and not p:IsMountain()
        and not p:IsImpassable() and not p:IsNaturalWonder();
end

function QAPlacement.AssertLand(p)
    assert(QAPlacement.IsLand(p),'QA_PLACEMENT_BLOCKED: passable natural land required');
end

local function belongsTo(p, city, radius)
    if p:GetOwner()~=city:GetOwner() then return false,'ownership'; end
    if Map.GetPlotDistance(city:GetX(),city:GetY(),p:GetX(),p:GetY())>radius then
        return false,'working_radius';
    end
    requireAPI(Cities.GetPlotPurchaseCity,'Cities.GetPlotPurchaseCity');
    local ownerCity=Cities.GetPlotPurchaseCity(p);
    if not ownerCity or ownerCity:GetID()~=city:GetID()
        or ownerCity:GetOwner()~=city:GetOwner() then return false,'owning_city'; end
    return true;
end

function QAPlacement.DistrictAllowed(p, city, districtType, radius)
    local kind=assert(GameInfo.Districts[districtType],'Unknown district '..districtType);
    if districtType=='DISTRICT_WONDER' then return false,'wonder_needs_building_specific_check'; end
    if kind.Coast==true or kind.Coast==1 then
        if not p:IsWater() or p:IsImpassable() or p:IsNaturalWonder() then return false,'water_district_terrain'; end
    elseif not QAPlacement.IsLand(p) then return false,'land_district_terrain'; end
    if p:GetDistrictType()~=-1 or p:GetImprovementType()~=-1 or p:GetResourceType()~=-1 then
        return false,'occupied_district_site';
    end
    -- Do not silently clear woods, floodplains or other features for a fixture.
    if p:GetFeatureType()~=-1 then return false,'feature_preservation'; end
    local owned,reason=belongsTo(p,city,radius or 3);
    if not owned then return false,reason; end
    requireAPI(p.CanHaveDistrict,'Plot.CanHaveDistrict');
    if not p:CanHaveDistrict(kind.Index,city:GetOwner(),city:GetID()) then return false,'native_district_rejected'; end
    return true;
end

local function resourceMatches(resourceType, slot)
    if slot.Resource then return resourceType==slot.Resource; end
    assert(slot.Tag,'Material slot needs Resource or Tag');
    for row in GameInfo.TypeTags() do
        if row.Type==resourceType and row.Tag==slot.Tag then return true; end
    end
    return false;
end

function QAPlacement.MaterialAllowed(p, city, slot, radius)
    if not QAPlacement.IsLand(p) then return nil,'material_terrain'; end
    if p:GetDistrictType()~=-1 then return nil,'occupied_material_site'; end
    local owned,reason=belongsTo(p,city,radius or 3);
    if not owned then return nil,reason; end
    local resource=GameInfo.Resources[p:GetResourceType()];
    if not resource or not resourceMatches(resource.ResourceType,slot) then return nil,'material_class'; end
    -- Existing resources preserve native terrain/feature combinations. Do not
    -- invent resources to make a requested constellation fit this map.
    local current=p:GetImprovementType();
    for _,name in ipairs(slot.Improvements) do
        local improvement=GameInfo.Improvements[name];
        if improvement then
            if current==improvement.Index then
                if not p:IsImprovementPillaged() then
                    return {Resource=resource.ResourceType, Improvement=name, State='existing'};
                end
            elseif current==-1 then
                requireAPI(ImprovementBuilder.CanHaveImprovement,'ImprovementBuilder.CanHaveImprovement');
                if ImprovementBuilder.CanHaveImprovement(p,improvement.Index,Players[city:GetOwner()]:GetTeam()) then
                    return {Resource=resource.ResourceType, Improvement=name, State='native_feasible'};
                end
            end
        end
    end
    return nil,'native_improvement_rejected';
end

local function sortedPlots(plots)
    table.sort(plots,function(a,b) return a:GetIndex()<b:GetIndex(); end);
    return plots;
end

-- Solve distinct-plot assignments with backtracking. A greedy selection can use
-- the only plot suitable for a later, more restrictive material slot.
local function assign(slots, choices, index, used, result)
    if index>#slots then return result; end
    for _,candidate in ipairs(choices[index]) do
        if not used[candidate.Plot] then
            used[candidate.Plot]=true; result[index]=candidate;
            if assign(slots,choices,index+1,used,result) then return result; end
            used[candidate.Plot]=nil; result[index]=nil;
        end
    end
    return nil;
end

function QAPlacement.Find(request)
    local radius=request.Radius or 3;
    assert(radius>=1 and radius<=3,'QA planner supports workable radius 1..3');
    assert(#request.Slots>0,'Material requirements are required');
    local out={Version=QAPlacement.Version, Status='blocked', Candidates={}, Rejected={},
        District=request.District, Radius=radius, MapPlotsExamined=0};
    local function reject(reason) out.Rejected[reason]=(out.Rejected[reason] or 0)+1; end
    local cities={};for _,city in Players[request.Player or 0]:GetCities():Members() do cities[#cities+1]=city;end;
    table.sort(cities,function(a,b) return a:GetID()<b:GetID();end);
    if #cities==0 then reject('no_owned_cities');end;
    local width,height=Map.GetGridSize();
    for _,city in ipairs(cities) do
        for plotIndex=0,width*height-1 do
            local q=Map.GetPlotByIndex(plotIndex);out.MapPlotsExamined=out.MapPlotsExamined+1;
            local legal,reason=QAPlacement.DistrictAllowed(q,city,request.District,radius);
            if legal then
                local ring=sortedPlots(Map.GetAdjacentPlots(q:GetX(),q:GetY()));
                local choices={};
                for i,slot in ipairs(request.Slots) do
                    choices[i]={};
                    for _,p in ipairs(ring) do
                        local material,why=QAPlacement.MaterialAllowed(p,city,slot,radius);
                        if material then
                            material.Name=slot.Name;material.Plot=p:GetIndex();material.Facts=QAPlacement.Facts(p);
                            choices[i][#choices[i]+1]=material;
                        else reject(why);end;
                    end
                end
                local selected=assign(request.Slots,choices,1,{},{});
                if selected then
                    out.Candidates[#out.Candidates+1]={City=city:GetID(),Player=city:GetOwner(),
                        Quarter=QAPlacement.Facts(q),Materials=selected};
                else reject('no_distinct_material_layout');end;
            else reject(reason);end;
        end
    end
    if #out.Candidates>0 then out.Status='candidates'; end
    -- All candidates are scanned; output order is stable by city and plot index.
    return out;
end

function QAPlacement.Recheck(request, candidate)
    local city=Players[candidate.Player]:GetCities():FindID(candidate.City);
    if not city then return false,'city_missing';end;
    local q=Map.GetPlotByIndex(candidate.Quarter.Plot);
    local allowed,reason=QAPlacement.DistrictAllowed(q,city,request.District,request.Radius);
    if not allowed then return false,reason;end;
    local used={};
    for i,slot in ipairs(request.Slots) do
        local chosen=candidate.Materials[i];
        if not chosen or used[chosen.Plot] then return false,'invalid_slot_assignment';end;
        used[chosen.Plot]=true;
        local p=Map.GetPlotByIndex(chosen.Plot);
        if Map.GetPlotDistance(q:GetX(),q:GetY(),p:GetX(),p:GetY())~=1 then return false,'material_not_adjacent';end;
        local material,why=QAPlacement.MaterialAllowed(p,city,slot,request.Radius);
        if not material then return false,why;end;
        if material.Resource~=chosen.Resource or material.Improvement~=chosen.Improvement then return false,'material_changed';end;
    end
    return true;
end
