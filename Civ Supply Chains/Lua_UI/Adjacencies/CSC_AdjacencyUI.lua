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

-- Use the same plot predicate as the native Wonder forecast. It checks the
-- loaded terrain and required adjacent district in this city. The separate
-- native forecast still decides which technology, construction and race
-- windows to consider. This read does not select or reserve a Wonder.
ExposedMembers.CSC_Adjacency.CanPlaceWonder = function(playerID, cityID, buildingIndex, plotIndex)
    local plot = Map.GetPlotByIndex(plotIndex);
    if plot and type(plot.CanHaveWonder) == 'function' then
        local ok, legal = pcall(plot.CanHaveWonder, plot, buildingIndex, playerID, cityID);
        if ok and type(legal) == 'boolean' then return legal; end;
    end;
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

-- Economic valuation needs this city's actual invoice even when another city
-- has an equal/cheaper one. The exclusive-buyer helper above remains the
-- conservative admission screen for the older positive purchase offer. Price
-- is not payment, affordability, legality or an ownership-completion receipt.
ExposedMembers.CSC_Adjacency.GetRawPlotPurchaseQuote = function(playerID, cityID, plotIndex)
    local city = CityManager.GetCity(playerID, cityID);
    local gold = city and city:GetGold();
    if not gold or type(gold.GetPlotPurchaseCost) ~= 'function' then return nil; end
    local ok, value = pcall(gold.GetPlotPurchaseCost, gold, plotIndex);
    if ok and (type(value) == 'number' or type(value) == 'integer') and value > 0 then return value; end
end;

-- These wrappers are UI-only native reads, not production instructions. Some
-- Gameplay objects omit the cost/yield methods despite sharing their names
-- with UI objects. Return numbers only; never pass UI-owned objects to Gameplay.
-- EconomyFacts memoizes each player/city/item within one publication.
local function economyNumber(object, method, ...)
    if not object or type(object[method]) ~= 'function' then return nil; end
    local ok, value = pcall(object[method], object, ...);
    if ok and (type(value) == 'number' or type(value) == 'integer') and value == value then return value; end
end

ExposedMembers.CSC_Adjacency.GetEconomyCityNumber = function(playerID, cityID, kind, index)
    local city = CityManager.GetCity(playerID, cityID);
    if not city then return nil; end
    if kind == 'yield' then return economyNumber(city, 'GetYield', index); end
    if kind == 'housing' then return economyNumber(city:GetGrowth(), 'GetHousing'); end
    local queue = city:GetBuildQueue();
    if kind == 'building' then return economyNumber(queue, 'GetBuildingCost', index); end
    if kind == 'district' then return economyNumber(queue, 'GetDistrictCost', index); end
    if kind == 'unit' then return economyNumber(queue, 'GetUnitCost', index); end

    -- Queue demand belongs in this numeric reader, not district-target lookup.
    -- Return definition IDs/turns only; Gameplay never borrows a UI unit/queue.
    if kind == 'currentUnit' or kind == 'unitTurns' then
        local hash=economyNumber(queue,'GetCurrentProductionTypeHash');
        local unit=hash and GameInfo.Units[hash];
        if not unit then return nil; end;
        if kind == 'currentUnit' then return unit.Index; end;
        if unit.Index~=index then return nil; end; -- queue changed since snapshot
        return economyNumber(queue,'GetTurnsLeft',unit.UnitType);
    end;
    if kind == 'currentBuilding' or kind == 'currentBuildingTurns' then
        local hash=economyNumber(queue,'GetCurrentProductionTypeHash');
        local building=hash and GameInfo.Buildings[hash];
        if not building then return nil; end;
        if kind == 'currentBuilding' then return building.Index; end;
        if building.Index~=index then return nil; end; -- the city switched production
        return economyNumber(queue,'GetTurnsLeft',building.BuildingType);
    end;
    if kind == 'navalProduction' then
        -- Value Dockmaster's Production only against observed eligible naval
        -- work, not as a permanent bonus to all of this city's production.
        local hash=economyNumber(queue,'GetCurrentProductionTypeHash');
        local unit=hash and GameInfo.Units[hash];
        local classes={PROMOTION_CLASS_NAVAL_MELEE=true,PROMOTION_CLASS_NAVAL_RANGED=true,PROMOTION_CLASS_NAVAL_RAIDER=true};
        local last=GameInfo.Eras.ERA_RENAISSANCE;
        if not unit or unit.Domain~='DOMAIN_SEA'or not classes[unit.PromotionClass]or not last then return 0; end;
        for _,pair in ipairs({{'PrereqTech','Technologies'},{'PrereqCivic','Civics'}})do
            local name=unit[pair[1]];
            local unlock=name and GameInfo[pair[2]][name];
            local era=unlock and GameInfo.Eras[unlock.EraType];
            if name and(not era or era.Index>last.Index)then return 0; end;
        end;
        return economyNumber(city,'GetYield',GameInfo.Yields.YIELD_PRODUCTION.Index);
    end;

end;

-- Population-limited district admission is exposed only by the UI cache.
-- Return plain facts, not UI objects or a production order. These are the stock
-- CitySupport counters: zoned includes unfinished foundations, and allowed
-- includes the city's extra allowance (rather than assuming population / 3).
-- Gameplay cross-checks population and its live district inventory before
-- labelling current admission readiness. Missing/lagging data is unknown; it
-- does not erase a future planning bid or alter foundations/repairs. Population
-- can grow after publication but before the player's native district choice.
ExposedMembers.CSC_Adjacency.GetDistrictCapacity = function(playerID, cityID)
    local city = CityManager.GetCity(playerID, cityID);
    if not city then return nil; end
    local districts = city:GetDistricts();
    local growth = city.GetGrowth and city:GetGrowth();
    return {
        population = economyNumber(city, 'GetPopulation'),
        -- The next citizen's ETA is the only growth date used by the planner.
        -- Native zoning continues to use the current allowed and used counts.
        turnsToGrowth = economyNumber(growth, 'GetTurnsUntilGrowth'),
        used = economyNumber(districts, 'GetNumZonedDistrictsRequiringPopulation'),
        allowed = economyNumber(districts, 'GetNumAllowedDistrictsRequiringPopulation')
    };
end;

ExposedMembers.CSC_Adjacency.GetEconomyResearchNumbers = function(playerID, kind, index)
    local player = Players[playerID];
    if not player then return nil; end
    local object = kind == 'tech' and player:GetTechs() or player:GetCulture();
    return {
        cost = economyNumber(object, kind == 'tech' and 'GetResearchCost' or 'GetCultureCost', index),
        progress = economyNumber(object, kind == 'tech' and 'GetResearchProgress' or 'GetCulturalProgress', index),
        rate = economyNumber(object, kind == 'tech' and 'GetScienceYield' or 'GetCultureYield')
    };
end;

ExposedMembers.CSC_Adjacency.GetEconomyPlotFacts = function(index)
    local plot = Map.GetPlotByIndex(index);
    if not plot then return nil; end
    local facts = {workers=economyNumber(plot, 'GetWorkerCount'), yields={}};
    -- A tile's receiving city can differ from its purchase city after citizen
    -- reassignment. Supply returns belong to the observed working city. Include
    -- the UI clock so Gameplay can reject a stale assignment independently of
    -- its own plot/worker facts; never infer future staffing from ownership.
    facts.turn = Game.GetCurrentGameTurn();
    facts.plotOwner = plot:GetOwner();
    local working = Cities.GetPlotWorkingCity(index);
    if working then facts.workingCity = working:GetID(); facts.workingPlayer = working:GetOwner(); end
    for yield in GameInfo.Yields() do facts.yields[yield.YieldType] = economyNumber(plot, 'GetYield', yield.Index); end
    return facts;
end;

-- Placement diagnostics and the central AI spatial planner use this stock UI
-- adjacency read for an explicit AI owner, city and district. It writes no
-- bids or yields; the planner separately converts ordinary yields to a bounded
-- terrain preference for concrete future customer footprints. The UI
-- may trail Core at a foundation event, so return its clock and footprint for
-- the observer to qualify rather than silently calling this an exact-time read.
-- Keep private AI yields separate from ordinary yields in downstream reports.
ExposedMembers.CSC_Adjacency.GetDistrictAdjacency = function(playerID, cityID, plotIndex, districtIndex)
    local plot = Map.GetPlotByIndex(plotIndex);
    local city = CityManager.GetCity(playerID, cityID);
    if not plot or not city then return {available=false}; end
    local result = {available=true, turn=Game.GetCurrentGameTurn(),
        plotDistrict=plot:GetDistrictType(), yields={}};
    for yield in GameInfo.Yields() do
        local ok, value = pcall(function()
            return plot:GetAdjacencyYield(playerID, cityID, districtIndex, yield.Index);
        end);
        if ok and (type(value) == 'number' or type(value) == 'integer') then result.yields[yield.YieldType] = value;
        else result.available=false; end
    end
    return result;
end;
