-- Sukritact Simple UI PlotToolTip wrapper for the Wonder-hosted Service spike.
--
-- Do not include Suk_PlotTooltips here: it is registered as another mod's
-- LuaReplace source, not as an includeable support file. Reproduce its small,
-- public wrapper locally so replacing PlotToolTip does not leave the context
-- without the base functions that render every tile tooltip.
local BASE_FILES:table = {
    'plottooltip_CQUI_expansion2.lua',
    'PlotTooltip_Expansion2.lua',
};

local SERVICE_TYPES :table = {
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE',
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI',
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY',
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY',
};

for _, filename in ipairs(BASE_FILES) do
    include(filename);
    if Initialize ~= nil then
        print('[CSC WSHS] Suk PlotToolTip base=' .. filename);
        break;
    end
end

local BASE_CSC_WSHS_FetchData = FetchData;

function FetchData(pPlot:table)
    local data:table = BASE_CSC_WSHS_FetchData(pPlot);
    local rivers:table = RiverManager.GetRiverTypes(pPlot);

    if rivers ~= nil and table.count(rivers) > 0 then
        local floodplainRiver:number = RiverManager.GetRiverForFloodplain(pPlot:GetX(), pPlot:GetY());
        local riverNames:table = {};

        for _, riverType in pairs(rivers) do
            local riverName:string = RiverManager.GetRiverNameByType(riverType);
            if riverName ~= nil and floodplainRiver == riverType then
                riverName = riverName .. '[ICON_You]';
            end
            table.insert(riverNames, riverName);
        end

        data.RiverNames = '[NEWLINE][ICON_Bullet]'
            .. table.concat(riverNames, '[NEWLINE][ICON_Bullet]');
    end

    return data;
end

local BASE_CSC_WSHS_GetDetails = GetDetails;

function GetDetails(data:table)
    local details:table = BASE_CSC_WSHS_GetDetails(data);
    local foundService:boolean = false;

    if data.WonderType ~= nil and data.BuildingTypes ~= nil then
        for _, serviceType in ipairs(SERVICE_TYPES) do
            local service:table = GameInfo.Buildings[serviceType];
            if service ~= nil then
                for _, buildingIndex in ipairs(data.BuildingTypes) do
                    if buildingIndex == service.Index then
                        if not foundService then
                            table.insert(details, Locale.Lookup('LOC_CSC_WSHS_PLOT_TOOLTIP_HEADER'));
                            foundService = true;
                        end
                        table.insert(details, '- ' .. Locale.Lookup('LOC_CSC_WSHS_PLOT_TOOLTIP_LINE'));
                        break;
                    end
                end
            end
        end
    end

    return details;
end
