-- ============================================================================
-- Exact-plot reconciler for the isolated Wonder-hosted Service spike.
-- Search Lua.log for: [CSC WSHS]
--
-- SQL grant modifiers cannot distinguish multiple DISTRICT_WONDER instances:
-- they place every compatible building in the city's first Wonder district.
-- This spike instead calls BuildQueue:CreateBuilding(buildingIndex, plotIndex)
-- with the corresponding Wonder's stored plot. Existing misplaced instances
-- from spike v2 are removed and recreated at the explicit target.
-- ============================================================================

local SERVICE_HOSTS :table = {
    {
        ServiceType = 'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE',
        HostType = 'BUILDING_ORACLE', -- laboratory trigger only
    },
    {
        ServiceType = 'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI',
        HostType = 'BUILDING_BOLSHOI_THEATRE',
    },
    {
        ServiceType = 'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY',
        HostType = 'BUILDING_BROADWAY',
    },
    {
        ServiceType = 'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY',
        HostType = 'BUILDING_SYDNEY_OPERA_HOUSE',
    },
};

local m_LastSignatures :table = {};
local m_IsReconciling :boolean = false;

local function GetBuildingLocation(pBuildings:table, buildingType:string)
    local row:table = GameInfo.Buildings[buildingType];
    if row == nil or not pBuildings:HasBuilding(row.Index) then
        return -1;
    end
    return pBuildings:GetBuildingLocation(row.Index);
end

local function ReportPair(pCity:table, pair:table, reason:string, action:string)
    local pBuildings:table = pCity:GetBuildings();
    local hostPlot:number = GetBuildingLocation(pBuildings, pair.HostType);
    local servicePlot:number = GetBuildingLocation(pBuildings, pair.ServiceType);
    local status:string = 'NO_SERVICE';

    if servicePlot ~= -1 and hostPlot == -1 then
        status = 'ORPHAN_SERVICE';
    elseif servicePlot ~= -1 and servicePlot == hostPlot then
        status = 'COLOCATED';
    elseif servicePlot ~= -1 then
        status = 'MISMATCH';
    end

    local cityKey:string = tostring(pCity:GetOwner()) .. ':' .. tostring(pCity:GetID());
    local signatureKey:string = cityKey .. ':' .. pair.ServiceType;
    local signature:string = tostring(hostPlot)
        .. '|service@' .. tostring(servicePlot)
        .. '|status=' .. status
        .. '|action=' .. action;

    if m_LastSignatures[signatureKey] ~= signature then
        m_LastSignatures[signatureKey] = signature;
        print('[CSC WSHS] reason=' .. reason
            .. ' action=' .. action
            .. ' player=' .. tostring(pCity:GetOwner())
            .. ' city=' .. tostring(pCity:GetID())
            .. ' name=' .. tostring(pCity:GetName())
            .. ' host=' .. pair.HostType .. '@' .. tostring(hostPlot)
            .. ' service=' .. pair.ServiceType .. '@' .. tostring(servicePlot)
            .. ' result=' .. status);
    end
end

local function ReconcilePair(pCity:table, pair:table, reason:string)
    local pBuildings:table = pCity:GetBuildings();
    local host:table = GameInfo.Buildings[pair.HostType];
    local service:table = GameInfo.Buildings[pair.ServiceType];

    if host == nil or service == nil then
        print('[CSC WSHS] reason=' .. reason
            .. ' action=CONFIG_ERROR'
            .. ' host=' .. pair.HostType
            .. ' service=' .. pair.ServiceType);
        return;
    end

    local hostPlot:number = GetBuildingLocation(pBuildings, pair.HostType);
    local servicePlot:number = GetBuildingLocation(pBuildings, pair.ServiceType);

    if hostPlot == -1 then
        if servicePlot ~= -1 then
            pBuildings:RemoveBuilding(service.Index);
            ReportPair(pCity, pair, reason, 'REMOVE_ORPHAN');
        end
        return;
    end

    if servicePlot == hostPlot then
        ReportPair(pCity, pair, reason, 'KEEP');
        return;
    end

    local action:string = 'CREATE_EXPLICIT';
    if servicePlot ~= -1 then
        action = 'RELOCATE_EXPLICIT';
        pBuildings:RemoveBuilding(service.Index);
    end

    -- The second argument is the exact plot index. Unlike a grant modifier,
    -- this does not ask the engine to choose among DISTRICT_WONDER instances.
    pCity:GetBuildQueue():CreateBuilding(service.Index, hostPlot);
    ReportPair(pCity, pair, reason, action);
end

local function ReconcileCityUnchecked(pCity:table, reason:string)
    for _, pair in ipairs(SERVICE_HOSTS) do
        ReconcilePair(pCity, pair, reason);
    end
end

local function ReconcileCity(pCity:table, reason:string)
    if pCity == nil or m_IsReconciling then
        return;
    end

    m_IsReconciling = true;
    local success:boolean, errorMessage = pcall(ReconcileCityUnchecked, pCity, reason);
    m_IsReconciling = false;

    if not success then
        print('[CSC WSHS] reason=' .. reason
            .. ' action=RECONCILE_ERROR'
            .. ' player=' .. tostring(pCity:GetOwner())
            .. ' city=' .. tostring(pCity:GetID())
            .. ' error=' .. tostring(errorMessage));
    end
end

local function ReconcilePlayer(playerID:number, reason:string)
    local pPlayer:table = Players[playerID];
    if pPlayer == nil or not pPlayer:IsAlive() or not pPlayer:IsMajor() then
        return;
    end

    for _, pCity in pPlayer:GetCities():Members() do
        ReconcileCity(pCity, reason);
    end
end

local function ReconcileAll(reason:string)
    for _, pPlayer in ipairs(PlayerManager.GetAliveMajors()) do
        for _, pCity in pPlayer:GetCities():Members() do
            ReconcileCity(pCity, reason);
        end
    end
end

local function OnPlayerTurnActivated(playerID:number)
    ReconcilePlayer(playerID, 'PLAYER_TURN_ACTIVATED');
end

local function OnBuildingAddedToMap()
    ReconcileAll('BUILDING_ADDED');
end

local function OnWonderCompleted(_plotX:number, _plotY:number, _buildingIndex:number, playerID:number, cityID:number)
    ReconcileCity(CityManager.GetCity(playerID, cityID), 'WONDER_COMPLETED');
end

local function OnLoadScreenClose()
    ReconcileAll('LOAD_SCREEN_CLOSE');
end

print('[CSC WSHS] exact-plot reconciler loaded');

Events.PlayerTurnActivated.Add(OnPlayerTurnActivated);
if Events.BuildingAddedToMap ~= nil then
    Events.BuildingAddedToMap.Add(OnBuildingAddedToMap);
end
if Events.WonderCompleted ~= nil then
    Events.WonderCompleted.Add(OnWonderCompleted);
end
if Events.LoadScreenClose ~= nil then
    Events.LoadScreenClose.Add(OnLoadScreenClose);
end

ReconcileAll('INITIALIZE');
