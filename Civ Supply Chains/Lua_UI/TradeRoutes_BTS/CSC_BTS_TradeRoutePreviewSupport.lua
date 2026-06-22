--=================================================================================================================
--  Civ Supply Chains - Better Trade Screen Preview Support
--=================================================================================================================
--  This file is intentionally small and rule-focused. Better Trade Screen already knows how to render
--  normal trade-route yields; CSC only needs to tell it which extra route effects our supply-chain
--  system would create for the currently previewed origin/destination city pair.
--
--  The live gameplay effects are still driven by CSC_TradeRouteInteractions.lua and SQL plot/city
--  properties. This helper is only for UI preview: it computes the same hypothetical route state before
--  the route exists, because active-route city properties cannot include a not-yet-created route.
--=================================================================================================================

print("Henno's CSC BTS trade-route preview support loaded!");

local DISTRICT_BAKERS_QUARTER = -1;
if GameInfo.Districts["DISTRICT_CSC_BAKERS_QUARTER"] ~= nil then
	DISTRICT_BAKERS_QUARTER = GameInfo.Districts["DISTRICT_CSC_BAKERS_QUARTER"].Index;
end

local PROP_BAKERY_SUPPLIED = "CSC_BAKERS_BAKERY_SUPPLIED";
local PROP_CAFE_SUPPLIED = "CSC_BAKERS_CAFE_SUPPLIED";

local function CSC_BTS_IsPositiveProperty(owner, propertyName)
	if owner == nil then return false; end

	local value = owner:GetProperty(propertyName);
	if value == nil then return false; end

	return tonumber(value) ~= nil and tonumber(value) > 0;
end

local function CSC_BTS_CityHasFunctioningBakersQuarter(pCity)
	if pCity == nil or DISTRICT_BAKERS_QUARTER < 0 then return false; end

	local pDistricts = pCity:GetDistricts();
	if pDistricts == nil then return false; end
	if not pDistricts:HasDistrict(DISTRICT_BAKERS_QUARTER) then return false; end

	if pDistricts.IsPillaged ~= nil then
		return not pDistricts:IsPillaged(DISTRICT_BAKERS_QUARTER);
	end

	return true;
end

local function CSC_BTS_GetCity(iPlayerID, iCityID)
	if iPlayerID == nil or iCityID == nil or iPlayerID < 0 then return nil; end

	local pPlayer = Players[iPlayerID];
	if pPlayer == nil then return nil; end

	local pCities = pPlayer:GetCities();
	if pCities == nil then return nil; end

	return pCities:FindID(iCityID);
end

-- Returns the two Bakers export channels for a hypothetical route:
--   bakeryRoute: supplied Bakery in the destination city exports consumer goods.
--   cafeRoute: supplied Cafe in the destination city exports specialty goods.
--
-- This mirrors CSC_GetBakersTradeRouteState in the route-state UI script, but stays available to BTS even
-- when that separate UI context has not loaded yet.
function CSC_BTS_GetBakersTradeRouteState(routeInfo)
	if routeInfo == nil then
		return false, false;
	end

	local pOriginCity = CSC_BTS_GetCity(routeInfo.OriginCityPlayer, routeInfo.OriginCityID);
	local pDestinationCity = CSC_BTS_GetCity(routeInfo.DestinationCityPlayer, routeInfo.DestinationCityID);
	if pOriginCity == nil or pDestinationCity == nil then
		return false, false;
	end

	-- First implementation is domestic-only. The gameplay scanner uses the same gate, so BTS should not
	-- preview benefits for routes the modifier system will never apply.
	if pOriginCity:GetOwner() ~= pDestinationCity:GetOwner() then
		return false, false;
	end

	-- Origin cities with their own functioning Bakers' Quarter do not import Bakers goods by trade route.
	if CSC_BTS_CityHasFunctioningBakersQuarter(pOriginCity) then
		return false, false;
	end

	return CSC_BTS_IsPositiveProperty(pDestinationCity, PROP_BAKERY_SUPPLIED),
		CSC_BTS_IsPositiveProperty(pDestinationCity, PROP_CAFE_SUPPLIED);
end

local function CSC_BTS_AppendTooltip(existingTooltip, newLine)
	if newLine == nil or newLine == "" then
		return existingTooltip or "";
	end

	if existingTooltip ~= nil and existingTooltip ~= "" then
		return existingTooltip .. "[NEWLINE]" .. newLine;
	end

	return newLine;
end

local function CSC_BTS_PrependTooltip(existingTooltip, newLine)
	if newLine == nil or newLine == "" then
		return existingTooltip or "";
	end

	if existingTooltip ~= nil and existingTooltip ~= "" then
		return newLine .. "[NEWLINE]" .. existingTooltip;
	end

	return newLine;
end

local function CSC_BTS_FormatSignedAmount(amount)
	if amount == nil then
		return "0";
	end

	if amount > 0 then
		return "+" .. tostring(amount);
	end

	return tostring(amount);
end

local function CSC_BTS_FormatQuarterYieldTooltip(amount, iconString, yieldName, directionName)
	return CSC_BTS_FormatSignedAmount(amount) .. " " .. iconString .. " " .. Locale.Lookup(yieldName)
		.. " from Quarter " .. directionName .. ".";
end

local function CSC_BTS_FormatQuarterAmenityTooltip(amount)
	local amenityText = "Amenity";
	if amount ~= 1 then
		amenityText = "Amenities";
	end

	return CSC_BTS_FormatSignedAmount(amount) .. " [ICON_Amenities] " .. amenityText .. " from Quarter imports.";
end

local function CSC_BTS_GetLastPositiveYieldIndex(yieldValues)
	if yieldValues == nil then return FOOD_INDEX; end

	for yieldIndex = FAITH_INDEX, FOOD_INDEX, -1 do
		if (yieldValues[yieldIndex] or 0) > 0 then
			return yieldIndex;
		end
	end

	return FOOD_INDEX;
end

-- Mutates BTS's normal yield arrays so its existing display, sorting, and overview logic can do the rest.
-- Amenities are not a BTS yield column, so the first implementation adds them to the last positive yield
-- tooltip. That keeps the aggregate tooltip ordered after yields without rewriting BTS' tooltip renderer.
function CSC_BTS_ApplyBakersTradeRoutePreview(routeInfo, yieldValues, yieldTooltips, buildTooltip, target)
	if yieldValues == nil then return; end

	local bBakeryRoute, bCafeRoute = CSC_BTS_GetBakersTradeRouteState(routeInfo);
	local routeCount = 0;
	if bBakeryRoute then routeCount = routeCount + 1; end
	if bCafeRoute then routeCount = routeCount + 1; end
	if routeCount <= 0 then return; end

	if target == "Origin" then
		yieldValues[FOOD_INDEX] = (yieldValues[FOOD_INDEX] or 0) + routeCount;

		if buildTooltip and yieldTooltips ~= nil then
			yieldTooltips[FOOD_INDEX] = CSC_BTS_PrependTooltip(
				yieldTooltips[FOOD_INDEX],
				CSC_BTS_FormatQuarterYieldTooltip(routeCount, "[ICON_Food]", "LOC_YIELD_FOOD_NAME", "imports")
			);

			local amenityTooltipIndex = CSC_BTS_GetLastPositiveYieldIndex(yieldValues);
			yieldTooltips[amenityTooltipIndex] = CSC_BTS_AppendTooltip(
				yieldTooltips[amenityTooltipIndex],
				CSC_BTS_FormatQuarterAmenityTooltip(routeCount)
			);
		end
	elseif target == "Destination" then
		yieldValues[PRODUCTION_INDEX] = (yieldValues[PRODUCTION_INDEX] or 0) + routeCount;
		yieldValues[GOLD_INDEX] = (yieldValues[GOLD_INDEX] or 0) + routeCount;

		if buildTooltip and yieldTooltips ~= nil then
			yieldTooltips[PRODUCTION_INDEX] = CSC_BTS_PrependTooltip(
				yieldTooltips[PRODUCTION_INDEX],
				CSC_BTS_FormatQuarterYieldTooltip(routeCount, "[ICON_Production]", "LOC_YIELD_PRODUCTION_NAME", "exports")
			);
			yieldTooltips[GOLD_INDEX] = CSC_BTS_PrependTooltip(
				yieldTooltips[GOLD_INDEX],
				CSC_BTS_FormatQuarterYieldTooltip(routeCount, "[ICON_Gold]", "LOC_YIELD_GOLD_NAME", "exports")
			);
		end
	end
end

--=================================================================================================================
