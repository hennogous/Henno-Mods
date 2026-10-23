-- Material care v2. Writes private valuation properties only; never moves units,
-- repairs improvements, changes resources, spends Gold or changes production.
-- Independent implementation of live demand, inspired by the reviewed AI mods.
include('CSC_AdjacencyCore');
CSC_AI_MaterialCare={version=3,players={},errors={},events={},calls=0,dirty={},
    strategy={active_calls=0,inactive_calls=0,transitions={}},
    policy={critical_repair_wait=1,repair_wait=2,critical_develop_wait=3,
        develop_wait=5,redundant_wait=8,nearby_radius=6}};
local M=CSC_AI_MaterialCare;
local generation=0;
local keys={'LAST_BASE','LAST_SPEC','REDUNDANT'};
local classes={};
for _,key in ipairs({'BAKERS','TAILORS'}) do
    local def=GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER'];
    if def then
        local row={base={},spec={}};classes[def.Index]=row;
        for tag in GameInfo.TypeTags() do
            local resource=GameInfo.Resources[tag.Type];
            if resource then
                if tag.Tag=='CLASS_CSC_'..key..'_BASE' then row.base[resource.Index]=true;end;
                if tag.Tag=='CLASS_CSC_'..key..'_SPEC' then row.spec[resource.Index]=true;end;
            end;
        end;
    end;
end;
local function eligible(pid)
    local p=Players[pid];return p and p:IsAlive() and p:IsMajor() and not p:IsHuman();
end;
local function visible(pid,plot)
    return PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY()) and
        CSC_Adjacency.ResourceVisible(pid,plot:GetResourceType());
end;
local function set(plot,key,value)
    local name='CSC_AI_CARE_'..key;
    if (plot:GetProperty(name) or 0)~=value then plot:SetProperty(name,value);end;
end;
local function unlocked(player,improvement)
    local tech=improvement.PrereqTech and GameInfo.Technologies[improvement.PrereqTech];
    local civic=improvement.PrereqCivic and GameInfo.Civics[improvement.PrereqCivic];
    return (not tech or player:GetTechs():HasTech(tech.Index)) and
        (not civic or player:GetCulture():HasCivic(civic.Index));
end;
local function workState(pid,plot)
    local ii=plot:GetImprovementType();
    -- Do not create extra demand for a tile currently occupied by a visible
    -- enemy. Reachability/path reservations remain the native job planner's job.
    if Units and Units.GetUnitsInPlot then
        for _,unit in ipairs(Units.GetUnitsInPlot(plot) or {}) do
            if unit:GetOwner()~=pid and Players[pid]:GetDiplomacy():IsAtWarWith(unit:GetOwner()) then return 'unsafe';end;
        end;
    end;
    -- An actual pillaged improvement is repair work, never "already improved".
    if ii>=0 then return plot:IsImprovementPillaged() and 'repair' or 'working';end;
    if plot:IsWater() or plot:IsImpassable() then return 'inaccessible';end;
    local resource=GameInfo.Resources[plot:GetResourceType()];
    for valid in GameInfo.Improvement_ValidResources() do
        if resource and valid.ResourceType==resource.ResourceType then
            local improvement=GameInfo.Improvements[valid.ImprovementType];
            if improvement and unlocked(Players[pid],improvement) then
                if ImprovementBuilder and ImprovementBuilder.CanHaveImprovement then
                    if ImprovementBuilder.CanHaveImprovement(plot,improvement.Index,pid) then return 'develop';end;
                else return 'legality_unknown';end;
            end;
        end;
    end;
    return 'locked_or_illegal';
end;
local function workDelay(mark)
    if mark.state=='repair' then
        return mark.rank==3 and M.policy.critical_repair_wait or M.policy.repair_wait;
    end;
    if mark.rank==3 then return M.policy.critical_develop_wait;end;
    return mark.rank==2 and M.policy.develop_wait or M.policy.redundant_wait;
end;
local function area(plot)
    -- Area is only a diagnostic proximity screen, not a native path proof.
    if plot and type(plot.GetAreaID)=='function' then return plot:GetAreaID();end;
    return nil;
end;
function M.Refresh(pid)
    -- A reload must not preserve priorities whose old Lua owner table vanished.
    if not M.initialized then
        for index=0,Map.GetPlotCount()-1 do
            local plot=Map.GetPlotByIndex(index);
            for _,key in ipairs(keys) do set(plot,key,0);end;
        end;
        M.initialized=true;
    end;
    local old=M.players[pid];local row={player=pid,turn=Game.GetCurrentGameTurn(),plots={},jobs={},
        missing=0,repairs=0,working=0,builders=0,charges=0,lost={},shortage=false,
        work_urgent=false,urgent_jobs=0,local_uncovered_jobs=0,generation=generation};
    local marks,builderUnits={},{};
    if eligible(pid) then
        for _,city in Players[pid]:GetCities():Members() do
            local districts=city:GetDistricts();
            for i=0,districts:GetNumDistricts()-1 do
                local district=districts:GetDistrictByIndex(i);
                local cls=classes[district:GetType()];
                if cls then
                    local neighbors={base={},spec={}};
                    for direction=0,5 do
                        local p=Map.GetAdjacentPlot(district:GetX(),district:GetY(),direction);
                        if p and p:GetOwner()==pid and p:GetDistrictType()<0 and visible(pid,p) then
                            local res=p:GetResourceType();
                            if cls.base[res] then neighbors.base[#neighbors.base+1]=p;end;
                            if cls.spec[res] then neighbors.spec[#neighbors.spec+1]=p;end;
                        end;
                    end;
                    -- Unfinished/pillaged Quarters still reserve future supply.
                    -- One strongest signal per physical tile avoids stacking when
                    -- several Quarters share the same material deposit.
                    for _,kind in ipairs({'base','spec'}) do
                        for _,p in ipairs(neighbors[kind]) do
                            local index=p:GetIndex();local rank=#neighbors[kind]==1 and (kind=='base' and 3 or 2) or 1;
                            local current=marks[index];
                            if not current then current={plot=index,rank=rank,resource=p:GetResourceType(),links={}};marks[index]=current;end;
                            current.rank=math.max(current.rank,rank);
                            current.links[#current.links+1]={quarter=district:GetType(),city=city:GetID(),source=Map.GetPlot(district:GetX(),district:GetY()):GetIndex(),category=kind};
                        end;
                    end;
                end;
            end;
        end;
        for _,unit in Players[pid]:GetUnits():Members() do
            if unit:GetType()==GameInfo.Units.UNIT_BUILDER.Index then
                row.builders=row.builders+1;row.charges=row.charges+unit:GetBuildCharges();
                local plot=Map.GetPlot(unit:GetX(),unit:GetY());
                builderUnits[#builderUnits+1]={x=unit:GetX(),y=unit:GetY(),charges=unit:GetBuildCharges(),area=area(plot)};
            end;
        end;
    end;
    -- Clear stale priorities on lost/replaced/unlinked materials, including the
    -- old owner's property when ownership changes. New owner eligibility is
    -- also checked independently by the native modifier's owner requirements.
    if old then for _,prior in ipairs(old.plots) do
        if not marks[prior.plot] then
            local plot=Map.GetPlotByIndex(prior.plot);
            if plot:GetProperty('CSC_AI_CARE_OWNER')==pid then
                for _,key in ipairs(keys) do set(plot,key,0);end;
            end;
            row.lost[#row.lost+1]={plot=prior.plot,resource=plot:GetResourceType(),owner=plot:GetOwner(),district=plot:GetDistrictType(),previous_resource=prior.resource};
            M.events[#M.events+1]={turn=row.turn,player=pid,plot=prior.plot,event='supply_lost',previous_resource=prior.resource,resource=plot:GetResourceType(),owner=plot:GetOwner(),district=plot:GetDistrictType()};
        end;
    end;end;
    local indices={};for index in pairs(marks) do indices[#indices+1]=index;end;table.sort(indices);
    for _,index in ipairs(indices) do
        local mark=marks[index];local plot=Map.GetPlotByIndex(index);
        local active=mark.rank==3 and 'LAST_BASE' or mark.rank==2 and 'LAST_SPEC' or 'REDUNDANT';
        if plot:GetProperty('CSC_AI_CARE_OWNER')~=pid then plot:SetProperty('CSC_AI_CARE_OWNER',pid);end;
        for _,key in ipairs(keys) do set(plot,key,key==active and 1 or 0);end;
        mark.state=workState(pid,plot);row.plots[#row.plots+1]=mark;
        local prior=nil;if old then for _,p in ipairs(old.plots) do if p.plot==index then prior=p;break;end;end;end;
        -- Waiting ages use game turns, not callback counts. Unsafe/locked/worked
        -- transitions reset the ready interval. A reload starts a new, explicitly
        -- observed interval rather than inventing earlier waiting time.
        local actionable=mark.state=='develop' or mark.state=='repair';
        if actionable then
            mark.ready_since=prior and prior.state==mark.state and prior.resource==mark.resource and prior.ready_since or row.turn;
            mark.ready_age=math.max(0,row.turn-mark.ready_since);
            mark.urgent=mark.ready_age>=workDelay(mark);
            mark.nearby_builders=0;mark.nearby_charges=0;
            local plotArea=area(plot);
            for _,unit in ipairs(builderUnits) do
                local sameArea=plotArea==nil or unit.area==nil or plotArea==unit.area;
                local distance=Map.GetPlotDistance(unit.x,unit.y,plot:GetX(),plot:GetY());
                if sameArea and distance<=M.policy.nearby_radius then
                    mark.nearby_builders=mark.nearby_builders+1;
                    mark.nearby_charges=mark.nearby_charges+unit.charges;
                end;
            end;
            -- These counts may include busy/reserved units and share Builders
            -- across jobs. They are NOT an available-worker or path guarantee,
            -- and never request production, purchases or unit assignments.
            if mark.nearby_builders==0 then row.local_uncovered_jobs=row.local_uncovered_jobs+1;end;
            if mark.urgent then row.urgent_jobs=row.urgent_jobs+1;row.work_urgent=true;end;
        end;
        if not prior or prior.state~=mark.state or prior.resource~=mark.resource then
            M.events[#M.events+1]={turn=row.turn,player=pid,plot=index,event='work_state',previous=prior and prior.state or 'new',state=mark.state,resource=mark.resource,rank=mark.rank};
        end;
        if mark.state=='develop' then row.missing=row.missing+1;
        elseif mark.state=='repair' then row.repairs=row.repairs+1;
        elseif mark.state=='working' then row.working=row.working+1;end;
        if mark.state~='working' then row.jobs[#row.jobs+1]=mark;end;
    end;
    -- Retain the old capacity flag for comparison only. V2's native strategy
    -- consumes work_urgent, independently of the empire-wide Builder count.
    -- Repairs need a Builder but consume no charge.
    row.shortage=eligible(pid) and (row.missing>row.charges or (row.repairs>0 and row.builders==0));
    M.players[pid]=row;M.dirty[pid]=false;return row;
end;
function M.RefreshAll()
    for _,player in ipairs(PlayerManager.GetAliveMajors()) do M.Refresh(player:GetID());end;
end;
local function refresh(pid)
    local ok,result=pcall(M.Refresh,pid);
    if not ok then
        if #M.errors<20 then M.errors[#M.errors+1]={turn=Game.GetCurrentGameTurn(),player=pid,error=tostring(result)};end;
        print('CSC_AI_MATERIAL_CARE_ERROR',tostring(result));return nil;
    end;
    return result;
end;
GameEvents.CSC_AI_MaterialCareShortage.Add(function(pid)
    if not eligible(pid) then return false;end;
    local row=M.players[pid];
    if not row or row.turn~=Game.GetCurrentGameTurn() or row.generation~=generation then row=refresh(pid);end;
    return row and row.shortage or false;
end);
GameEvents.CSC_AI_MaterialWorkReady.Add(function(pid)
    M.calls=M.calls+1;
    local row=M.players[pid];
    if eligible(pid) and (not row or row.turn~=Game.GetCurrentGameTurn() or row.generation~=generation) then row=refresh(pid);end;
    local active=eligible(pid) and row and row.work_urgent or false;
    local key=active and 'active_calls' or 'inactive_calls';M.strategy[key]=M.strategy[key]+1;
    local previous=M.strategy[pid];
    if previous~=active then
        M.strategy.transitions[#M.strategy.transitions+1]={turn=Game.GetCurrentGameTurn(),player=pid,active=active,urgent_jobs=row and row.urgent_jobs or 0};
        M.strategy[pid]=active;
    end;
    return active;
end);
Events.PlayerTurnActivated.Add(function(pid) if Players[pid] then refresh(pid);end;end);
-- Multiple within-turn changes only invalidate. A native strategy callback or
-- the next activation refreshes once; there is no repeated whole-map scan.
for _,name in ipairs({'DistrictAddedToMap','DistrictRemovedFromMap','DistrictBuildProgressChanged',
    'ImprovementAddedToMap','ImprovementRemovedFromMap','ImprovementPillaged','ResourceAddedToMap',
    'ResourceRemovedFromMap','PlotOwnershipChanged','UnitAddedToMap','UnitRemovedFromMap','TechCompleted','CivicCompleted'}) do
    if Events[name] then Events[name].Add(function() generation=generation+1;end);end;
end;
function M.Capture() return {version=M.version,turn=Game.GetCurrentGameTurn(),players=M.players,events=M.events,errors=M.errors,calls=M.calls,strategy=M.strategy,policy=M.policy};end;
local function json(v)
    local t=type(v);if t=='nil' then return 'null';end;
    if t=='number' or t=='boolean' then return tostring(v);end;
    if t=='string' then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"';end;
    local parts,array,count={},true,0;
    for key in pairs(v) do count=count+1;if type(key)~='number' then array=false;end;end;
    if count~=#v then array=false;end;
    if array then for _,value in ipairs(v) do parts[#parts+1]=json(value);end;return '['..table.concat(parts,',')..']';end;
    for key,value in pairs(v) do parts[#parts+1]=json(tostring(key))..':'..json(value);end;
    return '{'..table.concat(parts,',')..'}';
end;
function M.Export() print('CSC_MATERIAL_CARE='..json(M.Capture()));end;
print('CSC_AI_MATERIAL_CARE_READY',M.version);
