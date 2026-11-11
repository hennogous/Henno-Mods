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

-- Ask the native queue which building or unit this city can start now.
-- The gameplay publisher uses this for building bids and for whether a
-- Dockmaster customer can use its ship-production bonus. This read sends
-- no order, and CE still checks eligibility at the native comparison.
ExposedMembers.CSC_Adjacency.CanProduceItem = function(playerID, cityID, itemHash, isUnit)
    local city = CityManager.GetCity(playerID, cityID);
    local queue = city and city:GetBuildQueue();
    if not queue then return false; end
    local item = itemHash;
    if isUnit then
        -- Match the stock Production Panel's single-unit query and visibility
        -- check so hidden or superseded ships cannot justify a bid.
        item = {UnitType=itemHash, MilitaryFormationType=MilitaryFormationTypes.STANDARD_MILITARY_FORMATION};
        local ok, visible = pcall(queue.CanProduce, queue, item, true);
        if not ok or visible ~= true then return false; end
    end
    local ok, legal = pcall(queue.CanProduce, queue, item, false, true);
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

-- A placed but unfinished or pillaged host still has the right geometry.
-- A functioning district breaks ties between sites with equal potential.
ExposedMembers.CSC_Adjacency.HasWorkingDistrictAt = function(x, y)
    local district = CityManager.GetDistrictAt(x, y);
    return district and district:IsComplete() and not district:IsPillaged();
end;

-- Gameplay lacks this city Gold method. A price alone is insufficient:
-- Economic can buy for a different city, while district reservation requires
-- the original city's ownership (AI-N115). Only quote an unambiguous intended
-- buyer here; tied/cheaper other buyers leave the positive offer neutral.
-- This is a current quote screen, not a lifetime ownership guarantee or proof
-- of command legality, funds, payment or construction. The native contract
-- still buys normally. Cross-city purchase/transfer support remains open.
-- This first implementation scans own cities per promising target. It can be
-- quadratic across overlapping city candidates. Measure before broadening it;
-- any later memoization must last one publication, not survive changed quotes.
ExposedMembers.CSC_Adjacency.GetPlotPurchaseQuote = function(playerID, cityID, plotIndex)
    local city = CityManager.GetCity(playerID, cityID);
    if not city or type(city.GetGold) ~= 'function' then return nil; end
    local gold = city:GetGold();
    if not gold or type(gold.GetPlotPurchaseCost) ~= 'function' then return nil; end
    local ok, value = pcall(gold.GetPlotPurchaseCost, gold, plotIndex);
    if not ok or type(value) ~= 'number' or value <= 0 then return nil; end
    local player = Players[playerID];
    if not player then return nil; end
    for _, other in player:GetCities():Members() do
        if other:GetID() ~= cityID then
            local otherGold = other:GetGold();
            if not otherGold or type(otherGold.GetPlotPurchaseCost) ~= 'function' then return nil; end
            local quoted, cost = pcall(otherGold.GetPlotPurchaseCost, otherGold, plotIndex);
            -- Incomplete buyer information cannot prove that this city wins.
            if not quoted or type(cost) ~= 'number' then return nil; end
            if cost > 0 and cost <= value then return nil; end
        end
    end
    return value;
end;
