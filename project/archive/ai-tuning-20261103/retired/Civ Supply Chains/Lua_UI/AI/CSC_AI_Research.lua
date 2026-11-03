-- Independent CSC implementation of native "Call Lua Function" AI strategies.
-- RH's micro-strategies demonstrate the callback/strategy-list mechanism.
-- No research selection, progress, resource, improvement or real yield is granted.
include('CSC_AdjacencyCore');
local A = CSC_Adjacency;
CSC_AI_Research = {version=1, cache={}, calls={}, errors={}, checkpoints={}};
local R = CSC_AI_Research;
local plans, materials = {}, {};
for p in GameInfo.CSC_AI_ServiceResearch() do plans[p.Id]=p; end
for p in GameInfo.CSC_QuarterMaterialAdjacencyConfig() do
    local key=p.QuarterKey;
    materials[key]=materials[key] or {base={},spec={}};
    local target=p.SourceTag:match('_BASE$') and materials[key].base or materials[key].spec;
    for tag in GameInfo.TypeTags() do
        if tag.Tag==p.SourceTag and GameInfo.Resources[tag.Type] then target[tag.Type]=true; end
    end
end
local function missing(player, plan)
    for row in GameInfo.CSC_AI_ResearchItems() do
        if row.PlanId==plan then
            if row.System=='Civics' then
                local def=GameInfo.Civics[row.Item];
                if def and not player:GetCulture():HasCivic(def.Index) then return true; end
            else
                local def=GameInfo.Technologies[row.Item];
                if def and not player:GetTechs():HasTech(def.Index) then return true; end
            end
        end
    end
    return false;
end
function R.Invalidate() R.cache={}; end
function R.Scan(pid)
    -- This is a demand signal for native AI callbacks, not a choice of research.
    -- Evaluate each completed, functioning Quarter against its own visible owned
    -- materials; unrelated cities cannot pool Base and Specialty into one site.
    local player=Players[pid];
    local out={turn=Game.GetCurrentGameTurn(),player=pid,active={},sites={}};
    if not player or not player:IsAlive() or not player:IsMajor() or player:IsHuman() then return out; end
    for _,city in player:GetCities():Members() do
        local districts=city:GetDistricts();
        for i=0,districts:GetNumDistricts()-1 do
            local district=districts:GetDistrictByIndex(i);
            local def=GameInfo.Districts[district:GetType()];
            local key=def and def.DistrictType:match('^DISTRICT_CSC_(.-)_QUARTER$');
            local map=key and materials[key];
            if map and district:IsComplete() and not district:IsPillaged() then
                local base,spec=false,false;
                for _,p in ipairs(Map.GetAdjacentPlots(district:GetX(),district:GetY())) do
                    local res=GameInfo.Resources[p:GetResourceType()];
                    if p:GetOwner()==pid and res and A.ResourceVisible(pid,res.Index) then
                        base=base or map.base[res.ResourceType] or false;
                        spec=spec or map.spec[res.ResourceType] or false;
                    end
                end
                out.sites[#out.sites+1]={quarter=key,plot=Map.GetPlot(district:GetX(),district:GetY()):GetIndex(),base=base,spec=spec};
                for id,plan in pairs(plans) do
                    -- Unimproved owned materials count as potential supplies.
                    -- Stage4 requires BOTH classes at the SAME Quarter.
                    if plan.QuarterKey==key and base and (plan.Stage<4 or spec) and missing(player,id) then out.active[id]=true; end
                end
            end
        end
    end
    return out;
end
function R.Evaluate(pid, plan)
    -- Native strategies can ask repeatedly within a turn. Share the scan per
    -- player until an eligibility event invalidates it or the game turn changes.
    local cached=R.cache[pid];
    if not cached or cached.turn~=Game.GetCurrentGameTurn() then cached=R.Scan(pid);R.cache[pid]=cached; end
    return cached.active[plan or 0]==true;
end
local function strategy(pid, plan)
    -- A failed diagnostic callback must return an inactive signal to the native
    -- strategy caller; bound error capture so repeated calls cannot grow it forever.
    local key=tostring(pid)..':'..tostring(plan);
    R.calls[key]=(R.calls[key] or 0)+1;
    local ok,result=pcall(R.Evaluate,pid,plan);
    if not ok then
        if #R.errors<20 then R.errors[#R.errors+1]={turn=Game.GetCurrentGameTurn(),player=pid,plan=plan,error=tostring(result)};print('CSC_AI_RESEARCH_ERROR',result); end
        return false;
    end
    return result;
end
GameEvents.CSC_AI_ServiceResearchReady.Add(strategy);
local function json(v)
    local t=type(v);
    if t=='nil' then return 'null'; end
    if t=='number' or t=='boolean' then return tostring(v); end
    if t=='string' then return string.format('%q',v); end
    local parts,array,n={},true,0;
    for k in pairs(v) do n=n+1;if type(k)~='number' then array=false;end;end
    if n~=#v then array=false;end
    if array then for _,x in ipairs(v) do parts[#parts+1]=json(x);end;return '['..table.concat(parts,',')..']';end
    for k,x in pairs(v) do parts[#parts+1]=json(tostring(k))..':'..json(x);end
    return '{'..table.concat(parts,',')..'}';
end
function R.Capture()
    local out={turn=Game.GetCurrentGameTurn(),players={},calls=R.calls,errors=R.errors};
    for _,p in ipairs(PlayerManager.GetAliveMajors()) do
        local row=R.Scan(p:GetID());row.completed={};row.active_plans={};
        for id,plan in pairs(plans) do
            row.active_plans[tostring(id)]=row.active[id]==true;
            row.completed[plan.CivicType]=p:GetCulture():HasCivic(GameInfo.Civics[plan.CivicType].Index);
        end
        row.active=nil;out.players[#out.players+1]=row;
    end
    -- Counters/errors are still shared tables here. The checkpoint/export caller
    -- serializes this result immediately to freeze it while callbacks keep running.
    return out;
end
function R.Export(target)
    local text=R.checkpoints[target];
    if not text then assert(target==Game.GetCurrentGameTurn(),'Missing research checkpoint');text=json(R.Capture());end
    print('CSC_AI_RESEARCH_AUDIT='..text);
end
Events.PlayerTurnActivated.Add(function()
    local t=Game.GetCurrentGameTurn();
    if t%25==0 and not R.checkpoints[t] then R.checkpoints[t]=json(R.Capture());end
end);
-- Recompute once per player turn, and invalidate on within-turn map/research changes.
for _,name in ipairs({'PlayerTurnActivated','DistrictAddedToMap','DistrictRemovedFromMap','DistrictBuildProgressChanged','DistrictPillaged','CityOccupationChanged','CityRemovedFromMap','ResourceAddedToMap','ResourceRemovedFromMap','TechCompleted','CivicCompleted','ImprovementAddedToMap','ImprovementRemovedFromMap','PlotOwnershipChanged'}) do
    if Events[name] then Events[name].Add(R.Invalidate); end
end
print('CSC_AI_RESEARCH_READY',R.version);
