-- Native reads that are only available to the UI context.
-- This context does not set plot properties or mutate any gameplay object.
ExposedMembers.CSC_Adjacency = ExposedMembers.CSC_Adjacency or {};
ExposedMembers.CSC_Adjacency.GetUnitLevel = function(playerID,unitID)
    local player = Players[playerID];
    local unit = player and player:GetUnits():FindID(unitID);
    return unit and unit:GetExperience():GetLevel() or 0;
end;

ExposedMembers.CSC_Adjacency.IsSinglePlayer = function()
    return type(GameConfiguration.IsAnyMultiplayer) == 'function'
        and type(GameConfiguration.IsHotseat) == 'function'
        and GameConfiguration.IsAnyMultiplayer() == false
        and GameConfiguration.IsHotseat() == false;
end;

-- Ask the native queue which building variant this city can start now.
ExposedMembers.CSC_Adjacency.CanProduceBuilding = function(playerID, cityID, buildingHash)
    local city = CityManager.GetCity(playerID, cityID);
    local queue = city and city:GetBuildQueue();
    if not queue then return false; end
    local ok, legal = pcall(queue.CanProduce, queue, buildingHash, false, true);
    return ok and legal == true;
end;

-- The live Gameplay build queue does not implement CanProduce. Query the
-- UI cache here and return only the plot indices, without sending commands.
ExposedMembers.CSC_Adjacency.GetLegalDistrictTargets = function(playerID, cityID, districtHash)
    local city = CityManager.GetCity(playerID, cityID);
    if not city then return {}; end
    local queue = city:GetBuildQueue();
    if queue:HasBeenPlaced(districtHash) or not queue:CanProduce(districtHash, false, true) then
        return {};
    end
    local build = CityOperationTypes.BUILD;
    local params = { [CityOperationTypes.PARAM_DISTRICT_TYPE] = districtHash };
    local result = CityManager.GetOperationTargets(city, build, params);
    local legal = {};
    for _, index in ipairs(result and result[CityOperationResults.PLOTS] or {}) do
        local plot = Map.GetPlotByIndex(index);
        params[CityOperationTypes.PARAM_X], params[CityOperationTypes.PARAM_Y] = plot:GetX(), plot:GetY();
        if CityManager.CanStartOperation(city, build, params, true) then legal[#legal + 1] = index; end
    end
    return legal;
end;
