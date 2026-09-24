-- ============================================================================
-- Additive City Breakdown proof for multiple Wonder-hosted Services.
--
-- The base CitySupport code discards DISTRICT_WONDER after extracting Wonders,
-- so ordinary co-located buildings are otherwise invisible in this panel. This
-- context reads every Service's actual stored plot and nests it beneath the
-- Wonder on that plot. A wrong-host result is labelled rather than disguised.
-- ============================================================================

include('InstanceManager');
include('ToolTipHelper');

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

local PILLAGED_ICON :string = '[ICON_Pillaged]';

local m_WondersStack:table = nil;
local m_ServiceIM:table = InstanceManager:new('CSC_WonderServiceInstance', 'Top');
local m_PendingCity:table = nil;
local m_WaitingForLoad:boolean = false;

-- CityBuildings:GetBuildingLocation is exposed to gameplay scripts but not to
-- this UI context. Resolve the stored location the same way CitySupport does:
-- inspect every city-district plot's building list.
local function FindBuildingPlot(pCity:table, buildingIndex:number)
    local pBuildings:table = pCity:GetBuildings();

    for _, pDistrict in pCity:GetDistricts():Members() do
        local pPlot:table = Map.GetPlot(pDistrict:GetX(), pDistrict:GetY());
        if pPlot ~= nil then
            local plotIndex:number = pPlot:GetIndex();
            for _, candidateIndex in ipairs(pBuildings:GetBuildingsAtLocation(plotIndex)) do
                if candidateIndex == buildingIndex then
                    return plotIndex;
                end
            end
        end
    end

    return -1;
end

local function CollectCompletedWonders(pCity:table)
    local wonders:table = {};
    local pBuildings:table = pCity:GetBuildings();

    for _, pDistrict in pCity:GetDistricts():Members() do
        local pPlot:table = Map.GetPlot(pDistrict:GetX(), pDistrict:GetY());
        if pPlot ~= nil then
            local plotIndex:number = pPlot:GetIndex();
            for _, buildingIndex in ipairs(pBuildings:GetBuildingsAtLocation(plotIndex)) do
                local building:table = GameInfo.Buildings[buildingIndex];
                if building ~= nil and building.IsWonder and pBuildings:HasBuilding(building.Index) then
                    table.insert(wonders, {
                        Type = building.BuildingType,
                        Name = Locale.Lookup(building.Name),
                        PlotIndex = plotIndex,
                    });
                end
            end
        end
    end

    return wonders;
end

local function FindWonderByType(wonders:table, buildingType:string)
    for index, wonder in ipairs(wonders) do
        if wonder.Type == buildingType then
            return wonder, index;
        end
    end
    return nil, -1;
end

local function FindWonderByPlot(wonders:table, plotIndex:number)
    for index, wonder in ipairs(wonders) do
        if wonder.PlotIndex == plotIndex then
            return wonder, index;
        end
    end
    return nil, -1;
end

local function ConfigureServiceRow(instance:table, pCity:table, service:table, displayName:string, tooltip:string, sortKey:number)
    local pBuildings:table = pCity:GetBuildings();
    local name:string = displayName;

    if pBuildings:IsPillaged(service.BuildingType) then
        name = name .. PILLAGED_ICON;
    end

    instance.Top:SetVoid1(sortKey);
    instance.BuildingName:SetText(name);
    instance.Icon:SetIcon('ICON_' .. service.BuildingType);
    instance.Top:SetToolTipString(tooltip);
    instance.Top:RegisterCallback(Mouse.eRClick, function()
        LuaEvents.OpenCivilopedia(service.BuildingType);
    end);
end

local function Render()
    local pCity:table = m_PendingCity or UI.GetHeadSelectedCity();
    m_PendingCity = nil;

    if pCity == nil or m_WondersStack == nil then
        return;
    end

    m_ServiceIM:ResetInstances();

    local children:table = m_WondersStack:GetChildren();
    for index, child in ipairs(children) do
        child:SetVoid1(100000 + index);
    end

    local visibleChildren:table = {};
    for _, child in ipairs(children) do
        if not child:IsHidden() then
            table.insert(visibleChildren, child);
        end
    end

    local wonders:table = CollectCompletedWonders(pCity);
    for index = 1, math.min(#wonders, #visibleChildren) do
        visibleChildren[index]:SetVoid1(index * 100);
    end

    local pBuildings:table = pCity:GetBuildings();
    for pairIndex, pair in ipairs(SERVICE_HOSTS) do
        local service:table = GameInfo.Buildings[pair.ServiceType];
        if service ~= nil and pBuildings:HasBuilding(service.Index) then
            local servicePlot:number = FindBuildingPlot(pCity, service.Index);
            local expectedWonder:table = FindWonderByType(wonders, pair.HostType);
            local actualWonder:table, actualIndex:number = FindWonderByPlot(wonders, servicePlot);
            local baseTooltip:string = ToolTipHelper.GetBuildingToolTip(service.Hash, pCity:GetOwner(), pCity);

            if expectedWonder ~= nil and servicePlot == expectedWonder.PlotIndex then
                ConfigureServiceRow(
                    m_ServiceIM:GetInstance(),
                    pCity,
                    service,
                    Locale.Lookup(service.Name),
                    baseTooltip .. '[NEWLINE][NEWLINE]'
                        .. Locale.Lookup('LOC_CSC_WSHS_UI_COHOSTED_TOOLTIP', expectedWonder.Name),
                    actualIndex * 100 + pairIndex
                );
            else
                local expectedRow:table = GameInfo.Buildings[pair.HostType];
                local expectedName:string = expectedRow ~= nil and Locale.Lookup(expectedRow.Name) or pair.HostType;
                local actualName:string = Locale.Lookup('LOC_CSC_WSHS_UI_NO_WONDER');
                local sortKey:number = (#wonders + 1) * 100 + pairIndex;

                if actualWonder ~= nil then
                    actualName = actualWonder.Name;
                    sortKey = actualIndex * 100 + pairIndex;
                elseif servicePlot ~= -1 then
                    actualName = actualName .. ' (' .. tostring(servicePlot) .. ')';
                end

                ConfigureServiceRow(
                    m_ServiceIM:GetInstance(),
                    pCity,
                    service,
                    Locale.Lookup('LOC_CSC_WSHS_UI_MISMATCH_NAME'),
                    baseTooltip .. '[NEWLINE][NEWLINE]'
                        .. Locale.Lookup('LOC_CSC_WSHS_UI_MISMATCH_TOOLTIP', expectedName, actualName),
                    sortKey
                );
            end
        end
    end

    m_WondersStack:SortChildren(function(a, b) return a:GetVoid1() < b:GetVoid1(); end);
    m_WondersStack:CalculateSize();
    m_WondersStack:ReprocessAnchoring();
end

local function QueueRender(pCity:table)
    m_PendingCity = pCity or UI.GetHeadSelectedCity();
    ContextPtr:RequestRefresh();
end

local function OnSukWonders(_, data:table)
    QueueRender(data ~= nil and data.City or nil);
end

local function OnCityPanelOverviewOpened()
    QueueRender(UI.GetHeadSelectedCity());
end

local function OnCitySelectionChanged()
    QueueRender(UI.GetHeadSelectedCity());
end

local function OnInit()
    m_WondersStack = ContextPtr:LookUpControl('/InGame/CityPanelOverview/WondersStack');
    if m_WondersStack == nil then
        Events.LoadScreenClose.Add(OnInit);
        m_WaitingForLoad = true;
        return;
    end

    m_ServiceIM.m_ParentControl = m_WondersStack;
    ContextPtr:SetRefreshHandler(Render);
    LuaEvents.Suk_CityPanelOverview_Wonders.Add(OnSukWonders);
    LuaEvents.CityPanelOverview_Opened.Add(OnCityPanelOverviewOpened);
    Events.CitySelectionChanged.Add(OnCitySelectionChanged);
    print('[CSC WSHS] additive multi-Wonder City Breakdown UI loaded');
end

local function OnShutdown()
    if m_WaitingForLoad then
        Events.LoadScreenClose.Remove(OnInit);
    end
    LuaEvents.Suk_CityPanelOverview_Wonders.Remove(OnSukWonders);
    LuaEvents.CityPanelOverview_Opened.Remove(OnCityPanelOverviewOpened);
    Events.CitySelectionChanged.Remove(OnCitySelectionChanged);
    m_ServiceIM:DestroyInstances();
end

function Initialize()
    ContextPtr:SetInitHandler(OnInit);
    ContextPtr:SetShutdown(OnShutdown);
    ContextPtr:SetHide(false);
end

Initialize();
