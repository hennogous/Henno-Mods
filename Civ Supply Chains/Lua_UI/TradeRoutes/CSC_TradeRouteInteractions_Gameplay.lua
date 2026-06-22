--=================================================================================================================
--=================================================================================================================
--	Civ Supply Chains - Trade Route Interactions
--=================================================================================================================
--=================================================================================================================
-- This file runs as a gameplay script. It does not discover routes itself; the UI
-- script does that, then calls this script through PlayerOperations.EXECUTE_SCRIPT.
--
-- The gameplay side has the authority to mutate persistent state. Here that means
-- writing city-center plot properties, which SQL can read with REQUIREMENT_PLOT_PROPERTY_MATCHES.

local PROP_HAS_BAKERS_QUARTER			= "CSC_HAS_BAKERS_QUARTER";
local PROP_IMPORT_CONSUMER_ROUTE			= "CSC_BAKERS_IMPORT_CONSUMER_ROUTE";
local PROP_IMPORT_SPECIALTY_ROUTE		= "CSC_BAKERS_IMPORT_SPECIALTY_ROUTE";
local PROP_EXPORT_BAKERY_ROUTE			= "CSC_BAKERS_EXPORT_BAKERY_ROUTE";
local PROP_EXPORT_CAFE_ROUTE				= "CSC_BAKERS_EXPORT_CAFE_ROUTE";

local function CSC_GetRouteBitProperty(basePropertyName, bit)
	return basePropertyName .. "_BIT_" .. tostring(bit);
end

-- Properties are only written when they actually change. That avoids extra modifier
-- churn and makes repeated refresh events harmless.
local function CSC_SetPropertyIfChanged(owner, propertyName, value)
	if owner == nil then return; end

	local currentValue = owner:GetProperty(propertyName) or 0;
	if currentValue ~= value then
		owner:SetProperty(propertyName, value);
	end
end

-- Entry point called from the UI script.
-- The incoming parameters describe one city's complete route state for this refresh.
-- We write every flag, including 0 values, so stale route bonuses are removed when
-- a trade route ends or a city gains a functioning Bakers' Quarter.
function CSC_SetBakersTradeRouteProperties(iPlayerID, parameters)
	if parameters == nil then return; end

	local iX = parameters.CityX;
	local iY = parameters.CityY;
	if iX == nil or iY == nil then return; end

	local pPlot = Map.GetPlot(iX, iY);
	if pPlot == nil then return; end

	local pCity = CityManager.GetCityAt(iX, iY);

	CSC_SetPropertyIfChanged(pPlot, PROP_HAS_BAKERS_QUARTER, parameters.HasBakersQuarter or 0);
	CSC_SetPropertyIfChanged(pPlot, PROP_IMPORT_CONSUMER_ROUTE, parameters.ImportConsumerRoute or 0);
	CSC_SetPropertyIfChanged(pPlot, PROP_IMPORT_SPECIALTY_ROUTE, parameters.ImportSpecialtyRoute or 0);
	CSC_SetPropertyIfChanged(pPlot, PROP_EXPORT_BAKERY_ROUTE, parameters.ExportBakeryRoute or 0);
	CSC_SetPropertyIfChanged(pPlot, PROP_EXPORT_CAFE_ROUTE, parameters.ExportCafeRoute or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 1), parameters.ExportBakeryRouteBit1 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 2), parameters.ExportBakeryRouteBit2 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 4), parameters.ExportBakeryRouteBit4 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 8), parameters.ExportBakeryRouteBit8 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 16), parameters.ExportBakeryRouteBit16 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 1), parameters.ExportCafeRouteBit1 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 2), parameters.ExportCafeRouteBit2 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 4), parameters.ExportCafeRouteBit4 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 8), parameters.ExportCafeRouteBit8 or 0);
	CSC_SetPropertyIfChanged(pPlot, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 16), parameters.ExportCafeRouteBit16 or 0);

	-- Mirror the same values onto the city object for FireTuner/debug inspection.
	-- SQL still consumes the plot properties above.
	CSC_SetPropertyIfChanged(pCity, PROP_HAS_BAKERS_QUARTER, parameters.HasBakersQuarter or 0);
	CSC_SetPropertyIfChanged(pCity, PROP_IMPORT_CONSUMER_ROUTE, parameters.ImportConsumerRoute or 0);
	CSC_SetPropertyIfChanged(pCity, PROP_IMPORT_SPECIALTY_ROUTE, parameters.ImportSpecialtyRoute or 0);
	CSC_SetPropertyIfChanged(pCity, PROP_EXPORT_BAKERY_ROUTE, parameters.ExportBakeryRoute or 0);
	CSC_SetPropertyIfChanged(pCity, PROP_EXPORT_CAFE_ROUTE, parameters.ExportCafeRoute or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 1), parameters.ExportBakeryRouteBit1 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 2), parameters.ExportBakeryRouteBit2 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 4), parameters.ExportBakeryRouteBit4 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 8), parameters.ExportBakeryRouteBit8 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 16), parameters.ExportBakeryRouteBit16 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 1), parameters.ExportCafeRouteBit1 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 2), parameters.ExportCafeRouteBit2 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 4), parameters.ExportCafeRouteBit4 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 8), parameters.ExportCafeRouteBit8 or 0);
	CSC_SetPropertyIfChanged(pCity, CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 16), parameters.ExportCafeRouteBit16 or 0);
end

-- Register the function name used by parameters.OnStart in the UI script.
GameEvents.CSC_SetBakersTradeRouteProperties.Add(CSC_SetBakersTradeRouteProperties);

--=================================================================================================================
--=================================================================================================================
