-- Stock/CQUI Gathering Storm PlotToolTip wrapper for the Wonder-hosted Services. Prefer CQUI when present, using the same fallback chain as Sukritact's
-- Simple UI Adjustments.
include('CSC_AI_UIFilter');
local BASE_FILES:table = {
    'plottooltip_CQUI_expansion2.lua',
    'PlotTooltip_Expansion2.lua',
};

local SERVICE_TYPES :table = {
    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',
    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',
    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',
};

for _, filename in ipairs(BASE_FILES) do
    include(filename);
    if Initialize ~= nil then
        print('CSC Wonder Services: PlotToolTip base=' .. filename);
        break;
    end
end

local BASE_CSC_WONDER_SERVICES_GetDetails = GetDetails;

function GetDetails(data:table)
    local details:table = BASE_CSC_WONDER_SERVICES_GetDetails(data);
    local foundService:boolean = false;

    if data.WonderType ~= nil and data.BuildingTypes ~= nil then
        for _, serviceType in ipairs(SERVICE_TYPES) do
            local service:table = GameInfo.Buildings[serviceType];
            if service ~= nil then
                for _, buildingIndex in ipairs(data.BuildingTypes) do
                    if buildingIndex == service.Index then
                        if not foundService then
                            table.insert(details, Locale.Lookup('LOC_CSC_WONDER_SERVICES_PLOT_TOOLTIP_HEADER'));
                            foundService = true;
                        end
                        table.insert(details, '- ' .. Locale.Lookup(service.Name));
                        break;
                    end
                end
            end
        end
    end

    return details;
end
