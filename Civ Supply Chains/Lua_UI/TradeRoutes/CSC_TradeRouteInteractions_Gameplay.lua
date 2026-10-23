-- Network-operation receiver for the host UI's complete per-city route snapshot.
-- Do not consult local UI/Network state here: this callback executes identically
-- on every peer through PlayerOperations.EXECUTE_SCRIPT, including AI targets.
local REVISION = "CSC_TRADE_ROUTE_REVISION";
local BITS = {1, 2, 4, 8, 16};
-- This fixed schema is also the mutation order. Bit flags are derived here rather
-- than trusted as independent UI input. Counts retain the existing 5-bit encoding.
local FIELDS = {
    {"HasBakersQuarter", "CSC_HAS_BAKERS_QUARTER"},
    {"ImportConsumerRoute", "CSC_BAKERS_IMPORT_CONSUMER_ROUTE"},
    {"ImportSpecialtyRoute", "CSC_BAKERS_IMPORT_SPECIALTY_ROUTE"},
    {"ExportBakeryRoute", "CSC_BAKERS_EXPORT_BAKERY_ROUTE", true},
    {"ExportCafeRoute", "CSC_BAKERS_EXPORT_CAFE_ROUTE", true},
    {"ImportTailorRoute", "CSC_TAILORS_IMPORT_TAILOR_ROUTE"},
    {"ImportFashionHouseRoute", "CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE"},
    {"ExportTailorRoute", "CSC_TAILORS_EXPORT_TAILOR_ROUTE", true},
    {"ExportFashionHouseRoute", "CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE", true},
};
local function integer(value)
    return type(value) == "number" and value >= 0 and value <= 2147483647 and value == math.floor(value);
end
local function set(owner, name, value)
    if (owner:GetProperty(name) or 0) ~= value then owner:SetProperty(name, value); end
end

function CSC_SetBakersTradeRouteProperties(senderID, parameters)
    -- Validate the entire snapshot before any property write. Otherwise a bad
    -- later field could leave SQL seeing a mixture of old and new route counts.
    if Players[senderID] == nil or type(parameters) ~= "table" or parameters.Version ~= 2 then return; end
    if parameters.Turn ~= Game.GetCurrentGameTurn() then return; end
    for _, name in ipairs({"CityPlayerID", "CityID", "CityX", "CityY", "Revision"}) do
        if not integer(parameters[name]) then return; end
    end
    local plot = Map.GetPlot(parameters.CityX, parameters.CityY);
    local city = CityManager.GetCityAt(parameters.CityX, parameters.CityY);
    if plot == nil or city == nil or city:GetOwner() ~= parameters.CityPlayerID or city:GetID() ~= parameters.CityID then return; end
    -- A capture/raze/replacement or already accepted newer snapshot invalidates
    -- queued input. Revision is saved with the city, so reloads preserve it.
    if (city:GetProperty(REVISION) or 0) ~= parameters.Revision then return; end
    for _, field in ipairs(FIELDS) do
        local value = parameters[field[1]];
        if not integer(value) or (field[1] == "HasBakersQuarter" and value > 1) then return; end
    end
    for _, field in ipairs(FIELDS) do
        local value, name = parameters[field[1]], field[2];
        set(plot, name, value);
        set(city, name, value);
        if field[3] then
            for _, bit in ipairs(BITS) do
                local flag = math.floor(value / bit) % 2;
                set(plot, name .. "_BIT_" .. bit, flag);
                set(city, name .. "_BIT_" .. bit, flag);
            end
        end
    end
    -- Publish acknowledgement only after all flag writes; duplicates with this
    -- revision become no-ops on every peer, independent of UI event timing.
    set(city, REVISION, parameters.Revision + 1);
end

GameEvents.CSC_SetBakersTradeRouteProperties.Add(CSC_SetBakersTradeRouteProperties);
