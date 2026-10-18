-- Read-only reference capture for the offline API emulator. No extra RNG draws.
local CSCcal = nil;
local function CSCcalFlushSort()
    if not CSCcal or not CSCcal.pending then return end;
    local pending=CSCcal.pending;CSCcal.pending=nil;local after={};
    for _,row in ipairs(pending.rows) do after[#after+1]=row.MapIndex end;
    CSCcal.sortCalls=CSCcal.sortCalls+1;
    CSCcal.sorts[#CSCcal.sorts+1]=CSCcal.sortCalls..'|'..pending.before..'|'..table.concat(after,',');
end
local function CSCcalEmit(kind, rows)
    local payload=table.concat(rows,';')..';';local part=1;
    for offset=1,#payload,1700 do print('CSC_CAL_DATA',kind,part,payload:sub(offset,offset+1699));part=part+1 end
end
local function CSCcalSnapshot(kind)
    local rows={};local w,h=Map.GetGridSize();
    for i=0,w*h-1 do
        local p=Map.GetPlotByIndex(i);local t=GameInfo.Terrains[p:GetTerrainType()];local f=GameInfo.Features[p:GetFeatureType()];local r=GameInfo.Resources[p:GetResourceType()];
        rows[#rows+1]=table.concat({i,t and t.TerrainType or '',f and f.FeatureType or '',r and r.ResourceType or '',p:GetContinentType(),p:IsRiver() and 1 or 0,p:IsLake() and 1 or 0},'|');
    end
    CSCcalEmit(kind,rows);
end
function CSCcalBegin()
    print('CSC_CAL_BEGIN',MapConfiguration.GetValue('RANDOM_SEED'),MapConfiguration.GetValue('CSC_LUXURY_TYPES'),_VERSION);
    CSCcalSnapshot('pre');
    local ids=Map.GetContinentsInUse();CSCcalEmit('continents',{table.concat(ids,'|')});
    for _,id in ipairs(ids) do CSCcalEmit('plots_'..id,{table.concat(Map.GetContinentPlots(id),'|')}) end
    CSCcal={random=TerrainBuilder.GetRandomNumber,canHave=ResourceBuilder.CanHaveResource,setResource=ResourceBuilder.SetResourceType,adjacent=ResourceBuilder.GetAdjacentResourceCount,draws={},eligibility={},seen={},placements={},adjacency={},adjSeen={},sorts={},sortCalls=0,scoreFunctions={}};
    TerrainBuilder.GetRandomNumber=function(n,reason)
        local value=CSCcal.random(n,reason);CSCcal.draws[#CSCcal.draws+1]=table.concat({n,value,tostring(reason)},'|');return value;
    end
    ResourceBuilder.CanHaveResource=function(p,r)
        local value=CSCcal.canHave(p,r);local resource=GameInfo.Resources[r];
        if p and resource then
            local key=table.concat({r,p:GetTerrainType(),p:GetFeatureType(),p:IsRiver() and 1 or 0,p:IsLake() and 1 or 0,p:GetResourceType()},'|');
            if not CSCcal.seen[key] then
                CSCcal.seen[key]=true;local existing=GameInfo.Resources[p:GetResourceType()];
                CSCcal.eligibility[#CSCcal.eligibility+1]=table.concat({p:GetIndex(),resource.ResourceType,value and 1 or 0,existing and existing.ResourceType or ''},'|');
            end
        end
        return value;
    end
    ResourceBuilder.SetResourceType=function(p,r,count)
        CSCcalFlushSort();
        local result;if count==nil then result=CSCcal.setResource(p,r) else result=CSCcal.setResource(p,r,count) end;local resource=GameInfo.Resources[r];
        CSCcal.placements[#CSCcal.placements+1]=table.concat({p:GetIndex(),resource and resource.ResourceType or 'NONE',count or -1,#CSCcal.draws},'|');return result;
    end
    ResourceBuilder.GetAdjacentResourceCount=function(p)
        local n=CSCcal.adjacent(p);local key=p:GetIndex()..'|'..#CSCcal.placements;
        if not CSCcal.adjSeen[key] then CSCcal.adjSeen[key]=true;CSCcal.adjacency[#CSCcal.adjacency+1]=table.concat({p:GetIndex(),n,#CSCcal.placements},'|') end;
        return n;
    end
    -- Civ's standard table library is read-only. Observe these Lua-owned arrays
    -- before scoring returns and at the next placement; never replace table.sort.
    local scoreArrays={__ScoreLuxuryPlots='aaPossibleLuxLocs',__ScoreStrategicPlots='aaPossibleStratLocs',__ScorePlots='aaPossibleLocs',__ScoreWaterPlots='aaPossibleWaterLocs'};
    for name,arrayName in pairs(scoreArrays) do
        local original=ResourceGenerator[name];local collection=arrayName;CSCcal.scoreFunctions[name]=original;
        ResourceGenerator[name]=function(self,index,continent)
            CSCcalFlushSort();local result=original(self,index,continent);local rows=self[collection][index];
            if rows and #rows>0 then local before={};for _,row in ipairs(rows) do before[#before+1]=row.MapIndex..':'..row.Score end;CSCcal.pending={rows=rows,before=table.concat(before,',')} end;
            return result;
        end;
    end
end
function CSCcalResourcesEnd()
    CSCcalFlushSort();
    TerrainBuilder.GetRandomNumber=CSCcal.random;
    ResourceBuilder.CanHaveResource=CSCcal.canHave;
    ResourceBuilder.SetResourceType=CSCcal.setResource;
    ResourceBuilder.GetAdjacentResourceCount=CSCcal.adjacent;
    for name,original in pairs(CSCcal.scoreFunctions) do ResourceGenerator[name]=original end;
    CSCcalEmit('rng',CSCcal.draws);CSCcalEmit('eligibility',CSCcal.eligibility);CSCcalEmit('placements',CSCcal.placements);CSCcalEmit('adjacency',CSCcal.adjacency);CSCcalEmit('sorts',CSCcal.sorts);CSCcal=nil;
    CSCcalSnapshot('resources');
    print('CSC_CAL_RESOURCES_END');
end
function CSCcalEnd()
    CSCcalSnapshot('starts');print('CSC_CAL_END');
end
