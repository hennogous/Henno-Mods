-- Stock/CQUI Gathering Storm PlotToolTip wrapper for the Wonder-hosted Service
-- spike. Prefer CQUI when present, using the same fallback chain as Sukritact's
-- Simple UI Adjustments.
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
        print('[CSC WSHS] PlotToolTip base=' .. filename);
        break;
    end
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
