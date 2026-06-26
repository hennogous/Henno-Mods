--=================================================================================================================
--=================================================================================================================
--	Civ Supply Chains - Customer Population Returns
--=================================================================================================================
--=================================================================================================================
-- This gameplay script handles Bakers returns that depend on another city's
-- current population. SQL cannot ask "how many Citizens are in the adjacent
-- customer city" directly, so Lua scans the map, computes the return amounts,
-- and writes city-center plot properties that SQL requirements can read.
--
-- The SQL side turns those properties into modifiers in CSC_Q_BAKERS.sql.
-- Fractional returns are scaled by AMOUNT_SCALE and decomposed into bit flags
-- because Civ requirements can test exact property matches, but not numeric ranges.

local function CSC_AddDistrictIndex(districtIndexes, districtTypes, districtType)
	if districtType == nil or districtTypes[districtType] then return false; end

	local district = GameInfo.Districts[districtType];
	if district == nil then return false; end

	districtTypes[districtType] = true;
	table.insert(districtIndexes, district.Index);
	return true;
end

local function CSC_AddBuildingIndex(buildingIndexes, buildingTypes, buildingType)
	if buildingType == nil or buildingTypes[buildingType] then return false; end

	local building = GameInfo.Buildings[buildingType];
	if building == nil then return false; end

	buildingTypes[buildingType] = true;
	table.insert(buildingIndexes, building.Index);
	return true;
end

local function CSC_CreateDistrictReplacementFamily(baseDistrictType)
	-- Build the vanilla district plus any unique replacements exposed by loaded mods.
	-- The loop follows replacement chains defensively, so a replacement of a
	-- replacement is still recognized if a compatibility mod introduces one.
	local districtIndexes = {};
	local districtTypes = {};
	CSC_AddDistrictIndex(districtIndexes, districtTypes, baseDistrictType);

	local changed = true;
	while changed do
		changed = false;
		for row in GameInfo.DistrictReplaces() do
			if districtTypes[row.ReplacesDistrictType] then
				changed = CSC_AddDistrictIndex(districtIndexes, districtTypes, row.CivUniqueDistrictType) or changed;
			end
		end
	end

	return districtIndexes;
end

local function CSC_CreateBuildingReplacementFamily(baseBuildingType)
	-- Same pattern as districts: keep gameplay scans in terms of live indices,
	-- while callers can think in terms of base building types like BUILDING_MARKET.
	local buildingIndexes = {};
	local buildingTypes = {};
	CSC_AddBuildingIndex(buildingIndexes, buildingTypes, baseBuildingType);

	local changed = true;
	while changed do
		changed = false;
		for row in GameInfo.BuildingReplaces() do
			if buildingTypes[row.ReplacesBuildingType] then
				changed = CSC_AddBuildingIndex(buildingIndexes, buildingTypes, row.CivUniqueBuildingType) or changed;
			end
		end
	end

	return buildingIndexes;
end

local function CSC_CreateExplicitDistrictFamily(districtTypeList)
	local districtIndexes = {};
	local districtTypes = {};

	for _, districtType in ipairs(districtTypeList) do
		CSC_AddDistrictIndex(districtIndexes, districtTypes, districtType);
	end

	return districtIndexes;
end

local function CSC_CreateExplicitBuildingFamily(buildingTypeList)
	local buildingIndexes = {};
	local buildingTypes = {};

	for _, buildingType in ipairs(buildingTypeList) do
		CSC_AddBuildingIndex(buildingIndexes, buildingTypes, buildingType);
	end

	return buildingIndexes;
end

local DISTRICT_BAKERS_QUARTER = GameInfo.Districts["DISTRICT_CSC_BAKERS_QUARTER"] ~= nil and GameInfo.Districts["DISTRICT_CSC_BAKERS_QUARTER"].Index or -1;
local DISTRICT_COMMERCIAL_HUB_FAMILY = CSC_CreateDistrictReplacementFamily("DISTRICT_COMMERCIAL_HUB");
local DISTRICT_ENTERTAINMENT_FAMILY = CSC_CreateDistrictReplacementFamily("DISTRICT_ENTERTAINMENT_COMPLEX");
local DISTRICT_WATER_PARK_FAMILY = CSC_CreateDistrictReplacementFamily("DISTRICT_WATER_ENTERTAINMENT_COMPLEX");
local DISTRICT_GARDEN_FAMILY = CSC_CreateExplicitDistrictFamily({ "DISTRICT_LEU_GARDEN" });

local BUILDING_BAKERY = GameInfo.Buildings["BUILDING_CSC_BAKERS_BAKERY"] ~= nil and GameInfo.Buildings["BUILDING_CSC_BAKERS_BAKERY"].Index or -1;
local BUILDING_CAFE = GameInfo.Buildings["BUILDING_CSC_BAKERS_CAFE"] ~= nil and GameInfo.Buildings["BUILDING_CSC_BAKERS_CAFE"].Index or -1;
local BUILDING_MARKET_FAMILY = CSC_CreateBuildingReplacementFamily("BUILDING_MARKET");
local BUILDING_ZOO_FAMILY = CSC_CreateBuildingReplacementFamily("BUILDING_ZOO");
local BUILDING_FERRIS_FAMILY = CSC_CreateBuildingReplacementFamily("BUILDING_FERRIS_WHEEL");
local BUILDING_CONSERVATORY_FAMILY = CSC_CreateExplicitBuildingFamily({ "BUILDING_LEU_CONSERVATORY" });

local PROP_BAKERY_SUPPLIED = "CSC_BAKERS_BAKERY_SUPPLIED";
local PROP_BAKERS_MARKET_CUSTOMER_POP = "CSC_BAKERS_STAGE_3_MARKET_CUSTOMER_POP";
local PROP_BAKERS_MARKET_FOOD_AMOUNT = "CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT";
local PROP_BAKERS_MARKET_RETURN_AMOUNT = "CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT";
local PROP_BAKERS_STAGE_4_CAFE_RETURN = "CSC_BAKERS_STAGE_4_CAFE_RETURN";
local PROP_BAKERS_STAGE_4_ZOO_CULTURE_RETURN = "CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN";
local PROP_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN = "CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN";
local PROP_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN = "CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN";
local AMOUNT_SCALE = 10000;
-- These bits mirror CSC_ScaledAmountBits and CSC_Stage4StackBits in CSC_Q_ALL.sql.
-- For decimal per-population returns, Lua writes scaled integers such as 2500
-- for 0.25; SQL activates the matching bit modifiers and sums their amounts.
local AMOUNT_STACK_BITS = {
	1, 2, 4, 8, 16, 32, 64, 128,
	256, 512, 1024, 2048, 4096, 8192, 16384, 32768,
	65536, 131072, 262144, 524288
};
local NUM_DIRECTIONS = (DirectionTypes ~= nil and DirectionTypes.NUM_DIRECTION_TYPES) or 6;

local function CSC_GetCityStateKey(iPlayerID, iCityID)
	return tostring(iPlayerID) .. ":" .. tostring(iCityID);
end

local function CSC_GetPlotKey(iX, iY)
	return tostring(iX) .. "," .. tostring(iY);
end

local function CSC_GetBitProperty(basePropertyName, bit)
	return basePropertyName .. "_BIT_" .. tostring(bit);
end

local function CSC_GetBitValue(value, bit)
	value = tonumber(value) or 0;
	return math.floor(value / bit) % 2;
end

local function CSC_SetPropertyIfChanged(owner, propertyName, value)
	if owner == nil then return; end

	local currentValue = owner:GetProperty(propertyName) or 0;
	if currentValue ~= value then
		owner:SetProperty(propertyName, value);
	end
end

local function CSC_IsPositiveProperty(owner, propertyName)
	if owner == nil then return false; end

	local value = owner:GetProperty(propertyName);
	if value == nil then return false; end

	return tonumber(value) ~= nil and tonumber(value) > 0;
end

local function CSC_CityHasFunctioningBuilding(pCity, iBuilding)
	if pCity == nil or iBuilding == nil or iBuilding < 0 then return false; end

	local pBuildings = pCity:GetBuildings();
	if pBuildings == nil or not pBuildings:HasBuilding(iBuilding) then return false; end

	if pBuildings.IsPillaged ~= nil then
		return not pBuildings:IsPillaged(iBuilding);
	end

	return true;
end

local function CSC_CityHasFunctioningDistrict(pCity, iDistrict)
	if pCity == nil or iDistrict == nil or iDistrict < 0 then return false; end

	local pDistricts = pCity:GetDistricts();
	if pDistricts == nil or not pDistricts:HasDistrict(iDistrict) then return false; end

	if pDistricts.IsPillaged ~= nil then
		return not pDistricts:IsPillaged(iDistrict);
	end

	return true;
end

local function CSC_CityHasAnyFunctioningBuilding(pCity, buildingIndexes)
	for _, iBuilding in ipairs(buildingIndexes) do
		if CSC_CityHasFunctioningBuilding(pCity, iBuilding) then
			return true;
		end
	end

	return false;
end

local function CSC_CityHasMarket(pCity)
	return CSC_CityHasAnyFunctioningBuilding(pCity, BUILDING_MARKET_FAMILY);
end

local function CSC_CityHasBakerySeller(pCity)
	return CSC_CityHasFunctioningBuilding(pCity, BUILDING_BAKERY)
		and CSC_CityHasFunctioningDistrict(pCity, DISTRICT_BAKERS_QUARTER)
		and CSC_IsPositiveProperty(pCity, PROP_BAKERY_SUPPLIED);
end

local function CSC_CityHasCafeSeller(pCity)
	return CSC_CityHasFunctioningBuilding(pCity, BUILDING_CAFE)
		and CSC_CityHasFunctioningDistrict(pCity, DISTRICT_BAKERS_QUARTER);
end

local function CSC_GetCityDistrictPlot(pCity, iDistrict)
	if pCity == nil or iDistrict == nil or iDistrict < 0 then return nil; end

	local pDistricts = pCity:GetDistricts();
	if pDistricts == nil or not pDistricts:HasDistrict(iDistrict) then return nil; end

	local iX, iY = pDistricts:GetDistrictLocation(iDistrict);
	if iX == nil or iY == nil or iX < 0 or iY < 0 then return nil; end

	return Map.GetPlot(iX, iY);
end

local function CSC_GetCityAnyDistrictPlot(pCity, districtIndexes)
	for _, iDistrict in ipairs(districtIndexes) do
		local pDistrictPlot = CSC_GetCityDistrictPlot(pCity, iDistrict);
		if pDistrictPlot ~= nil then
			return pDistrictPlot;
		end
	end

	return nil;
end

local function CSC_AddStage4CustomerCity(stage4CustomerCitiesByPlotKey, pCity, districtIndexes, branch)
	local pDistrictPlot = CSC_GetCityAnyDistrictPlot(pCity, districtIndexes);
	if pDistrictPlot == nil then return; end

	stage4CustomerCitiesByPlotKey[CSC_GetPlotKey(pDistrictPlot:GetX(), pDistrictPlot:GetY())] = {
		City = pCity,
		Branch = branch,
	};
end

local function CSC_CreateReturnStates()
	-- First pass: cache every city and build lookup tables by district plot.
	-- Later scans only walk the six plots around each Bakers' Quarter and use
	-- these maps to find eligible customer cities quickly.
	local cityStates = {};
	local commercialHubCitiesByPlotKey = {};
	local stage4CustomerCitiesByPlotKey = {};

	for iPlayerID = 0, PlayerManager.GetWasEverAliveCount() - 1 do
		local pPlayer = Players[iPlayerID];
		if pPlayer ~= nil then
			local pCities = pPlayer:GetCities();
			if pCities ~= nil then
				for _, pCity in pCities:Members() do
					local cityState = {
						City = pCity,
						BakersQuarterPlot = CSC_GetCityDistrictPlot(pCity, DISTRICT_BAKERS_QUARTER),
						CommercialHubPlot = CSC_GetCityAnyDistrictPlot(pCity, DISTRICT_COMMERCIAL_HUB_FAMILY),
						CustomerPopulation = 0,
						FoodPopulation = 0,
						Stage4CafeReturn = 0,
						Stage4ZooCultureReturn = 0,
						Stage4FerrisCultureReturn = 0,
						Stage4ConservatoryCultureReturn = 0,
						CustomersSeen = {},
						Stage4CustomersSeen = {},
					};

					cityStates[CSC_GetCityStateKey(iPlayerID, pCity:GetID())] = cityState;

					if cityState.CommercialHubPlot ~= nil then
						commercialHubCitiesByPlotKey[CSC_GetPlotKey(cityState.CommercialHubPlot:GetX(), cityState.CommercialHubPlot:GetY())] = pCity;
					end

					if CSC_CityHasAnyFunctioningBuilding(pCity, BUILDING_ZOO_FAMILY) then
						CSC_AddStage4CustomerCity(stage4CustomerCitiesByPlotKey, pCity, DISTRICT_ENTERTAINMENT_FAMILY, "ZOO");
					end
					if CSC_CityHasAnyFunctioningBuilding(pCity, BUILDING_FERRIS_FAMILY) then
						CSC_AddStage4CustomerCity(stage4CustomerCitiesByPlotKey, pCity, DISTRICT_WATER_PARK_FAMILY, "FERRIS");
					end
					if CSC_CityHasAnyFunctioningBuilding(pCity, BUILDING_CONSERVATORY_FAMILY) then
						CSC_AddStage4CustomerCity(stage4CustomerCitiesByPlotKey, pCity, DISTRICT_GARDEN_FAMILY, "CONSERVATORY");
					end
				end
			end
		end
	end

	return cityStates, commercialHubCitiesByPlotKey, stage4CustomerCitiesByPlotKey;
end

local function CSC_MarkBakeryMarketTransaction(cityStates, pSellerCity, pCustomerCity)
	-- Stage 3 Bakery -> Market relationship:
	--   * the Bakery city receives per-population Production/Gold returns
	--   * the Market city receives per-population Food
	-- The Gold side lives in CSC_Q_BAKERS_GOLD.sql; this script only computes
	-- shared population totals and writes neutral property names.
	if pSellerCity == nil or pCustomerCity == nil then return; end
	if pSellerCity:GetOwner() ~= pCustomerCity:GetOwner() then return; end
	if not CSC_CityHasBakerySeller(pSellerCity) then return; end
	if not CSC_CityHasMarket(pCustomerCity) then return; end

	local sellerKey = CSC_GetCityStateKey(pSellerCity:GetOwner(), pSellerCity:GetID());
	local sellerState = cityStates[sellerKey];
	if sellerState == nil then return; end

	local customerKey = CSC_GetCityStateKey(pCustomerCity:GetOwner(), pCustomerCity:GetID());
	if sellerState.CustomersSeen[customerKey] then return; end

	sellerState.CustomersSeen[customerKey] = true;
	sellerState.CustomerPopulation = sellerState.CustomerPopulation + (pCustomerCity:GetPopulation() or 0);

	local customerState = cityStates[customerKey];
	if customerState ~= nil then
		customerState.FoodPopulation = customerState.FoodPopulation + (pCustomerCity:GetPopulation() or 0);
	end
end

local function CSC_MarkCafeStage4Transaction(cityStates, pSellerCity, customerRecord, customerPlotKey)
	-- Stage 4 Cafe -> customer capstone relationship. Each eligible customer
	-- city contributes floor(population / 5) stacks to both sides of the exchange.
	local pCustomerCity = customerRecord ~= nil and customerRecord.City or nil;
	if pSellerCity == nil or pCustomerCity == nil then return; end
	if pSellerCity:GetOwner() ~= pCustomerCity:GetOwner() then return; end
	if not CSC_CityHasCafeSeller(pSellerCity) then return; end

	local customerPopulation = pCustomerCity:GetPopulation() or 0;
	local stackAmount = math.floor(customerPopulation / 5);
	if stackAmount <= 0 then return; end

	local sellerKey = CSC_GetCityStateKey(pSellerCity:GetOwner(), pSellerCity:GetID());
	local sellerState = cityStates[sellerKey];
	if sellerState == nil then return; end

	local customerKey = CSC_GetCityStateKey(pCustomerCity:GetOwner(), pCustomerCity:GetID());
	local transactionKey = customerKey .. ":" .. tostring(customerPlotKey) .. ":" .. tostring(customerRecord.Branch);
	if sellerState.Stage4CustomersSeen[transactionKey] then return; end

	sellerState.Stage4CustomersSeen[transactionKey] = true;
	sellerState.Stage4CafeReturn = sellerState.Stage4CafeReturn + stackAmount;

	local customerState = cityStates[customerKey];
	if customerState ~= nil then
		if customerRecord.Branch == "ZOO" then
			customerState.Stage4ZooCultureReturn = customerState.Stage4ZooCultureReturn + stackAmount;
		elseif customerRecord.Branch == "FERRIS" then
			customerState.Stage4FerrisCultureReturn = customerState.Stage4FerrisCultureReturn + stackAmount;
		elseif customerRecord.Branch == "CONSERVATORY" then
			customerState.Stage4ConservatoryCultureReturn = customerState.Stage4ConservatoryCultureReturn + stackAmount;
		end
	end
end

local function CSC_ScanBakeryMarketTransactions(cityStates, commercialHubCitiesByPlotKey)
	if DISTRICT_BAKERS_QUARTER < 0 or #DISTRICT_COMMERCIAL_HUB_FAMILY == 0 then return; end

	for _, sellerState in pairs(cityStates) do
		local pSellerPlot = sellerState.BakersQuarterPlot;
		if pSellerPlot ~= nil then
			for direction = 0, NUM_DIRECTIONS - 1 do
				local pCustomerPlot = Map.GetAdjacentPlot(pSellerPlot:GetX(), pSellerPlot:GetY(), direction);
				if pCustomerPlot ~= nil then
					local pCustomerCity = commercialHubCitiesByPlotKey[CSC_GetPlotKey(pCustomerPlot:GetX(), pCustomerPlot:GetY())];
					CSC_MarkBakeryMarketTransaction(cityStates, sellerState.City, pCustomerCity);
				end
			end
		end
	end
end

local function CSC_ScanCafeStage4Transactions(cityStates, stage4CustomerCitiesByPlotKey)
	if DISTRICT_BAKERS_QUARTER < 0 then return; end

	for _, sellerState in pairs(cityStates) do
		local pSellerPlot = sellerState.BakersQuarterPlot;
		if pSellerPlot ~= nil then
			for direction = 0, NUM_DIRECTIONS - 1 do
				local pCustomerPlot = Map.GetAdjacentPlot(pSellerPlot:GetX(), pSellerPlot:GetY(), direction);
				if pCustomerPlot ~= nil then
					local customerPlotKey = CSC_GetPlotKey(pCustomerPlot:GetX(), pCustomerPlot:GetY());
					local customerRecord = stage4CustomerCitiesByPlotKey[customerPlotKey];
					CSC_MarkCafeStage4Transaction(cityStates, sellerState.City, customerRecord, customerPlotKey);
				end
			end
		end
	end
end

local function CSC_GetScaledPerPopulationAmount(targetYield, population)
	-- Convert a city-total target into the per-population amount expected by
	-- MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION.
	targetYield = tonumber(targetYield) or 0;
	population = tonumber(population) or 0;

	if targetYield <= 0 or population <= 0 then
		return 0;
	end

	return math.floor(((targetYield * AMOUNT_SCALE) / population) + 0.5);
end

local function CSC_WriteAmountBits(pCity, pCityCenterPlot, propertyName, scaledAmount)
	-- Write both the raw scaled amount for debugging and the decomposed bit
	-- properties consumed by SQL requirement sets.
	local plotCurrentValue = pCityCenterPlot ~= nil and (pCityCenterPlot:GetProperty(propertyName) or 0) or 0;
	local cityCurrentValue = pCity ~= nil and (pCity:GetProperty(propertyName) or 0) or 0;
	if plotCurrentValue == scaledAmount and cityCurrentValue == scaledAmount then
		return;
	end

	CSC_SetPropertyIfChanged(pCityCenterPlot, propertyName, scaledAmount);
	CSC_SetPropertyIfChanged(pCity, propertyName, scaledAmount);

	for _, bit in ipairs(AMOUNT_STACK_BITS) do
		local bitValue = CSC_GetBitValue(scaledAmount, bit);
		local bitPropertyName = CSC_GetBitProperty(propertyName, bit);
		CSC_SetPropertyIfChanged(pCityCenterPlot, bitPropertyName, bitValue);
		CSC_SetPropertyIfChanged(pCity, bitPropertyName, bitValue);
	end
end

local function CSC_WriteReturnState(pCity, customerPopulation, foodPopulation, stage4CafeReturn, stage4ZooCultureReturn, stage4FerrisCultureReturn, stage4ConservatoryCultureReturn)
	if pCity == nil then return; end

	local pCityCenterPlot = Map.GetPlot(pCity:GetX(), pCity:GetY());
	local sellerPopulation = pCity:GetPopulation() or 0;
	local returnTargetYield = (tonumber(customerPopulation) or 0) * 0.105;
	local foodTargetYield = (tonumber(foodPopulation) or 0) * 0.105;
	local returnScaledAmount = CSC_GetScaledPerPopulationAmount(returnTargetYield, sellerPopulation);
	local foodScaledAmount = CSC_GetScaledPerPopulationAmount(foodTargetYield, sellerPopulation);

	CSC_SetPropertyIfChanged(pCityCenterPlot, PROP_BAKERS_MARKET_CUSTOMER_POP, customerPopulation);
	CSC_SetPropertyIfChanged(pCity, PROP_BAKERS_MARKET_CUSTOMER_POP, customerPopulation);

	CSC_WriteAmountBits(pCity, pCityCenterPlot, PROP_BAKERS_MARKET_RETURN_AMOUNT, returnScaledAmount);
	CSC_WriteAmountBits(pCity, pCityCenterPlot, PROP_BAKERS_MARKET_FOOD_AMOUNT, foodScaledAmount);
	CSC_WriteAmountBits(pCity, pCityCenterPlot, PROP_BAKERS_STAGE_4_CAFE_RETURN, stage4CafeReturn);
	CSC_WriteAmountBits(pCity, pCityCenterPlot, PROP_BAKERS_STAGE_4_ZOO_CULTURE_RETURN, stage4ZooCultureReturn);
	CSC_WriteAmountBits(pCity, pCityCenterPlot, PROP_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN, stage4FerrisCultureReturn);
	CSC_WriteAmountBits(pCity, pCityCenterPlot, PROP_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN, stage4ConservatoryCultureReturn);
end

function CSC_RefreshCustomerPopulationReturns()
	-- Full refreshes are intentionally idempotent. Every pass recomputes all
	-- return properties from current game state, so removed buildings, pillage,
	-- population changes, and ownership changes clear stale bonuses naturally.
	local cityStates, commercialHubCitiesByPlotKey, stage4CustomerCitiesByPlotKey = CSC_CreateReturnStates();
	CSC_ScanBakeryMarketTransactions(cityStates, commercialHubCitiesByPlotKey);
	CSC_ScanCafeStage4Transactions(cityStates, stage4CustomerCitiesByPlotKey);

	for _, cityState in pairs(cityStates) do
		CSC_WriteReturnState(cityState.City, cityState.CustomerPopulation, cityState.FoodPopulation, cityState.Stage4CafeReturn, cityState.Stage4ZooCultureReturn, cityState.Stage4FerrisCultureReturn, cityState.Stage4ConservatoryCultureReturn);
	end
end

function CSC_OnCustomerPopulationPlayerRefresh(iPlayerID)
	CSC_RefreshCustomerPopulationReturns();
end

function CSC_OnCustomerPopulationCityRefresh(iPlayerID, iCityID)
	CSC_RefreshCustomerPopulationReturns();
end

function CSC_OnCustomerPopulationPlotRefresh(iX, iY, iFallbackPlayerID)
	CSC_RefreshCustomerPopulationReturns();
end

function CSC_OnCustomerPopulationBuildingEvent(iX, iY, iBuildingIndex, iPlayerID, iCityID)
	CSC_RefreshCustomerPopulationReturns();
end

function CSC_OnCustomerPopulationDistrictEvent(iPlayerID, iDistrictID, iCityID, iX, iY)
	CSC_RefreshCustomerPopulationReturns();
end

Events.PlayerTurnActivated.Add(CSC_OnCustomerPopulationPlayerRefresh);
if Events.BuildingAddedToMap ~= nil then
	Events.BuildingAddedToMap.Add(CSC_OnCustomerPopulationBuildingEvent);
end
if Events.BuildingChanged ~= nil then
	Events.BuildingChanged.Add(CSC_OnCustomerPopulationBuildingEvent);
end
if Events.BuildingRemovedFromMap ~= nil then
	Events.BuildingRemovedFromMap.Add(CSC_OnCustomerPopulationPlotRefresh);
end
if Events.CityPopulationChanged ~= nil then
	Events.CityPopulationChanged.Add(CSC_OnCustomerPopulationCityRefresh);
end
if Events.CityProductionCompleted ~= nil then
	Events.CityProductionCompleted.Add(CSC_OnCustomerPopulationCityRefresh);
end
if Events.DistrictAddedToMap ~= nil then
	Events.DistrictAddedToMap.Add(CSC_OnCustomerPopulationDistrictEvent);
end
if Events.DistrictRemovedFromMap ~= nil then
	Events.DistrictRemovedFromMap.Add(CSC_OnCustomerPopulationDistrictEvent);
end
if Events.DistrictPillaged ~= nil then
	Events.DistrictPillaged.Add(CSC_OnCustomerPopulationDistrictEvent);
end
if Events.CityAddedToMap ~= nil then
	Events.CityAddedToMap.Add(CSC_OnCustomerPopulationCityRefresh);
end
if Events.CityRemovedFromMap ~= nil then
	Events.CityRemovedFromMap.Add(CSC_OnCustomerPopulationCityRefresh);
end
if Events.CityTransfered ~= nil then
	Events.CityTransfered.Add(CSC_OnCustomerPopulationCityRefresh);
end
if Events.LoadGameViewStateDone ~= nil then
	Events.LoadGameViewStateDone.Add(CSC_RefreshCustomerPopulationReturns);
end
if GameEvents ~= nil and GameEvents.BuildingConstructed ~= nil then
	GameEvents.BuildingConstructed.Add(CSC_OnCustomerPopulationCityRefresh);
end

CSC_RefreshCustomerPopulationReturns();

--=================================================================================================================
--=================================================================================================================
