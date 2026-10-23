-- One-time late map-generation pass, loaded by AddGameplayScripts after the
-- standard map, starting positions and earlier mod gameplay scripts (Oceans=6).
-- No map-script or ResourceGenerator replacement. No shared engine RNG draws.
include('CSC_MaterialMapCore');
include('CSC_MaterialMapDefinitions');
local C=CSC_MaterialMapCore;
local DONE='CSC_MATERIAL_MAP_ASSISTANCE_DONE';
local AUDIT='CSC_MATERIAL_MAP_ASSISTANCE_AUDIT';
local function flag(value) return value==true or value==1;end

function CSC_InitializeMaterialMap()
    -- This is map initialization, not a recurring gameplay repair. Record skips
    -- as completed too, so loading a save cannot reconsider an earlier decision.
    if Game:GetProperty(DONE) then return;end
    local function skip(reason)
        Game:SetProperty(DONE,true);Game:SetProperty(AUDIT,{version=C.Version,status='skipped',reason=reason});
        print('CSC_MATERIAL_MAP_SKIPPED',reason);
    end
    local configured=GameConfiguration.GetValue('CSC_RESOURCE_MAP_ASSISTANCE');
    if configured~=nil and not flag(configured) then skip('disabled');return;end
    local densityRow=GameInfo.GlobalParameters['CSC_MATERIAL_MAP_STANDARD_DENSITY'];
    local profile=C.ResourceProfile(MapConfiguration.GetValue('resources'),densityRow and tonumber(densityRow.Value) or 30);
    if not profile then skip('unsupported resource setting');return;end
    if GameConfiguration.IsSavedGame and GameConfiguration.IsSavedGame() then skip('existing save');return;end
    if Game.GetCurrentGameTurn()>GameConfiguration.GetStartTurn()+1 then skip('past initialization');return;end
    local mapSeed=MapConfiguration.GetValue('RANDOM_SEED');
    if type(mapSeed)~='number' then skip('no procedural map seed');return;end
    local definitions=CSC_MaterialMapDefinitions.Resolve();
    local data={plots={},resources={},features={}};
    for r in GameInfo.Resources() do data.resources[#data.resources+1]={type=r.ResourceType,class=r.ResourceClassType};end
    for f in GameInfo.Features() do data.features[#data.features+1]={type=f.FeatureType,removable=f.Removable};end
    local mapped,eligible,checks={},{},0;
    for _,q in ipairs(C.Quarters) do for _,kind in ipairs({'base','spec'}) do for _,r in ipairs(definitions[q][kind].resources) do
        local row=GameInfo.Resources[r];if row and row.Frequency>0 then mapped[r]=row.Index;end
    end;end;end
    for r in pairs(mapped) do eligible[r]={};end
    local startingPlots={};
    -- Capture the engine's current map and eligibility before planning. The pure
    -- planner never approximates CanHaveResource or mutates native plot objects.
    for i=0,Map.GetPlotCount()-1 do
        local p=Map.GetPlotByIndex(i);local neighbors={};
        for d=0,5 do local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),d);if n then neighbors[#neighbors+1]=n:GetIndex();end;end
        local r=GameInfo.Resources[p:GetResourceType()];local f=GameInfo.Features[p:GetFeatureType()];local district=GameInfo.Districts[p:GetDistrictType()];
        data.plots[#data.plots+1]={index=i,x=p:GetX(),y=p:GetY(),continent=p:GetContinentType(),neighbors=neighbors,
            terrain=GameInfo.Terrains[p:GetTerrainType()].TerrainType,feature=f and f.FeatureType,resource=r and r.ResourceType,resource_count=p:GetResourceCount(),
            district=district and district.DistrictType,owner=p:GetOwner(),water=p:IsWater(),hills=p:IsHills(),impassable=p:IsImpassable(),river=p:IsRiver(),lake=p:IsLake()};
        if p:IsStartingPlot() then startingPlots[#startingPlots+1]=i;end
        if not p:IsWater() and not p:IsImpassable() and not r and not district and p:GetImprovementType()==-1 then
            for name,index in pairs(mapped) do checks=checks+1;if ResourceBuilder.CanHaveResource(p,index) then eligible[name][i]=true;end;end
        end
    end
    data.starting_plots=startingPlots;
    local plan=C.Plan(data,definitions,eligible,mapSeed,profile);
    plan.status='planned';plan.initialization_turn=Game.GetCurrentGameTurn();plan.eligibility_checks=checks;
    plan.phase='AddGameplayScripts; after native starts; before in-game UI';
    plan.oceans_already_ran=flag(Game:GetProperty('Suk_Oceans_Resources_Spawned'));
    -- Diagnostic capture is enabled only by the test harness. Production saves
    -- retain just the compact audit, never full worlds/eligibility tables.
    if flag(GameConfiguration.GetValue('CSC_MATERIAL_MAP_DIAGNOSTICS')) then
        local lists={};for r,set in pairs(eligible) do local values={};for i in pairs(set) do values[#values+1]=i;end;table.sort(values);lists[r]=values;end
        CSC_MaterialMapDebug={before=data,definitions=definitions,eligible=lists,starting_plots=startingPlots};
    end
    -- Preflight the complete plan, then check each write again. Unexpected
    -- incompatibilities roll back every addition; original deposits are intact.
    Game:SetProperty(DONE,true);
    -- Set the once-only guard before writes can raise events. A failed pass is
    -- rolled back and audited rather than retried against a partly changed map.
    local applied={};
    local ok,message=pcall(function()
        for _,a in ipairs(plan.additions) do local p=Map.GetPlotByIndex(a.plot);assert(p:GetResourceType()==-1 and p:GetImprovementType()==-1 and ResourceBuilder.CanHaveResource(p,mapped[a.resource]),'Material map preflight '..a.resource);end
        for _,a in ipairs(plan.additions) do
            local p=Map.GetPlotByIndex(a.plot);local index=mapped[a.resource];
            assert(ResourceBuilder.CanHaveResource(p,index),'Material map placement changed eligibility');
            applied[#applied+1]=a.plot;ResourceBuilder.SetResourceType(p,index,1);
            assert(p:GetResourceType()==index,'Material map resource readback failed');
            assert(p:GetResourceCount()==a.quantity,'Material map quantity readback failed');
            print('CSC_MATERIAL_MAP_ADDED',a.plot,a.resource,a.quarter,a.continent);
        end
    end);
    if not ok then
        for _,i in ipairs(applied) do ResourceBuilder.SetResourceType(Map.GetPlotByIndex(i),-1);end
        plan.status='failed';plan.error=tostring(message);print('CSC_MATERIAL_MAP_ERROR',tostring(message));
    else plan.status='complete';end
    Game:SetProperty(AUDIT,plan);
    print('CSC_MATERIAL_MAP_RESULT',plan.status,#plan.additions,mapSeed,plan.initialization_turn,checks);
end

CSC_InitializeMaterialMap();
