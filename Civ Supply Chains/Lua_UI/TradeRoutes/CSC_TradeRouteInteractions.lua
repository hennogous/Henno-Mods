--=================================================================================================================
--=================================================================================================================
--	Civ Supply Chains - Trade Route Interactions
--=================================================================================================================
--=================================================================================================================
-- This file runs in the UI context. That matters because the UI context can inspect
-- trade route objects, but it should not directly mutate gameplay state. When this
-- script decides a city needs new route flags, it asks the gameplay script to write
-- those flags through PlayerOperations.EXECUTE_SCRIPT.

local DISTRICT_BAKERS_QUARTER = -1;
if GameInfo.Districts["DISTRICT_CSC_BAKERS_QUARTER"] ~= nil then
	DISTRICT_BAKERS_QUARTER = GameInfo.Districts["DISTRICT_CSC_BAKERS_QUARTER"].Index;
end

-- Property vocabulary shared with SQL and the gameplay script.
-- CSC_HAS_BAKERS_QUARTER is a city-center plot property used as a general city flag.
-- The *_ROUTE properties are also city-center plot properties. SQL requirements read
-- them from the City Center modifiers and apply the actual yields/amenities.
local PROP_HAS_BAKERS_QUARTER			= "CSC_HAS_BAKERS_QUARTER";

-- These two are city properties set by SQL modifiers on the Bakery/Cafe buildings.
-- They mirror the existing stage 3/4 supply gates, so trade exports use the same
-- "supplied building" logic as the local city effects.
local PROP_BAKERY_SUPPLIED				= "CSC_BAKERS_BAKERY_SUPPLIED";
local PROP_CAFE_SUPPLIED					= "CSC_BAKERS_CAFE_SUPPLIED";

local PROP_IMPORT_CONSUMER_ROUTE			= "CSC_BAKERS_IMPORT_CONSUMER_ROUTE";
local PROP_IMPORT_SPECIALTY_ROUTE		= "CSC_BAKERS_IMPORT_SPECIALTY_ROUTE";
local PROP_EXPORT_BAKERY_ROUTE			= "CSC_BAKERS_EXPORT_BAKERY_ROUTE";
local PROP_EXPORT_CAFE_ROUTE				= "CSC_BAKERS_EXPORT_CAFE_ROUTE";
local ROUTE_STACK_BITS					= { 1, 2, 4, 8, 16 };
local BUILDING_BAKERY = GameInfo.Buildings["BUILDING_CSC_BAKERS_BAKERY"] ~= nil and GameInfo.Buildings["BUILDING_CSC_BAKERS_BAKERY"].Index or -1;
local BUILDING_CAFE = GameInfo.Buildings["BUILDING_CSC_BAKERS_CAFE"] ~= nil and GameInfo.Buildings["BUILDING_CSC_BAKERS_CAFE"].Index or -1;
local CIVIC_MEDIEVAL_FAIRES = GameInfo.Civics["CIVIC_MEDIEVAL_FAIRES"] ~= nil and GameInfo.Civics["CIVIC_MEDIEVAL_FAIRES"].Index or -1;
local CIVIC_URBANIZATION = GameInfo.Civics["CIVIC_URBANIZATION"] ~= nil and GameInfo.Civics["CIVIC_URBANIZATION"].Index or -1;

-- Civ properties are loose values: nil, numbers, sometimes strings depending on source.
-- Normalize them through one helper so the route logic only cares about "truthy and > 0".
local function CSC_IsPositiveProperty(owner, propertyName)
	if owner == nil then return false; end

	local value = owner:GetProperty(propertyName);
	if value == nil then return false; end

	return tonumber(value) ~= nil and tonumber(value) > 0;
end

local function CSC_CityHasBuilding(pCity, iBuilding)
	if pCity == nil or iBuilding == nil or iBuilding < 0 then return false; end

	local pBuildings = pCity:GetBuildings();
	if pBuildings == nil then return false; end
	if not pBuildings:HasBuilding(iBuilding) then return false; end

	if pBuildings.IsPillaged ~= nil then
		return not pBuildings:IsPillaged(iBuilding);
	end

	return true;
end

local function CSC_PlayerHasCivic(iPlayerID, iCivic)
	if iPlayerID == nil or iPlayerID < 0 or iCivic == nil or iCivic < 0 then return false; end

	local pPlayer = Players[iPlayerID];
	if pPlayer == nil then return false; end

	local pCulture = pPlayer:GetCulture();
	if pCulture == nil then return false; end

	return pCulture:HasCivic(iCivic);
end

-- A city with a built but pillaged Bakers' Quarter should not block imports.
-- The design phrase is "functioning Bakers' Quarter", so we check both existence
-- and pillage state when the API exposes that information.
local function CSC_CityHasFunctioningBakersQuarter(pCity)
	if pCity == nil or DISTRICT_BAKERS_QUARTER < 0 then return false; end

	local pDistricts = pCity:GetDistricts();
	if pDistricts == nil then return false; end
	if not pDistricts:HasDistrict(DISTRICT_BAKERS_QUARTER) then return false; end

	if pDistricts.IsPillaged ~= nil then
		return not pDistricts:IsPillaged(DISTRICT_BAKERS_QUARTER);
	end

	return true;
end

-- Central rule function for the Bakers route interaction.
-- Return values are:
--   1. Bakery route active: origin imports consumer goods; destination exports Bakery goods.
--   2. Cafe route active: origin imports specialty goods; destination exports Cafe goods.
--
-- Keeping this rule isolated is deliberate. If we later build a trade-route preview
-- override, that UI can call the same function instead of duplicating the design logic.
function CSC_GetBakersTradeRouteState(pOriginCity, pDestinationCity)
	if pOriginCity == nil or pDestinationCity == nil then
		return false, false;
	end

	-- First implementation follows Leugi's domestic-route pattern. If we later want
	-- international imports, this is the narrow point where that rule changes.
	if pOriginCity:GetOwner() ~= pDestinationCity:GetOwner() then
		return false, false;
	end

	if CSC_CityHasFunctioningBakersQuarter(pOriginCity) then
		return false, false;
	end

	local bBakerySupplied = CSC_IsPositiveProperty(pDestinationCity, PROP_BAKERY_SUPPLIED);
	local bCafeSupplied = CSC_IsPositiveProperty(pDestinationCity, PROP_CAFE_SUPPLIED);

	return bBakerySupplied, bCafeSupplied;
end

local function CSC_GetCityStateKey(iPlayerID, iCityID)
	return tostring(iPlayerID) .. ":" .. tostring(iCityID);
end

local function CSC_GetRouteBitProperty(basePropertyName, bit)
	return basePropertyName .. "_BIT_" .. tostring(bit);
end

local function CSC_GetRouteBitValue(routeCount, bit)
	routeCount = tonumber(routeCount) or 0;
	return math.floor(routeCount / bit) % 2;
end

-- Local working state for one city during a refresh pass.
-- Everything starts at 0, then active routes turn specific flags on. At the end of
-- the pass, the state is sent to the gameplay context and written to the city-center plot.
local function CSC_CreateBakersCityState(pCity)
	return {
		PlayerID = pCity:GetOwner(),
		CityID = pCity:GetID(),
		X = pCity:GetX(),
		Y = pCity:GetY(),
		HasBakersQuarter = CSC_CityHasFunctioningBakersQuarter(pCity) and 1 or 0,
		ImportConsumerRoute = 0,
		ImportSpecialtyRoute = 0,
		ExportBakeryRoute = 0,
		ExportCafeRoute = 0,
		ExportBakeryRouteBits = {},
		ExportCafeRouteBits = {},
	};
end

-- Build a complete city table first, rather than updating cities while scanning.
-- This lets one route mark both its origin and destination in the same refresh pass.
local function CSC_CollectBakersCityStates()
	local cityStates = {};
	local iCitiesSeen = 0;
	local iCitiesWithBakersQuarter = 0;

	for iPlayerID = 0, PlayerManager.GetWasEverAliveCount() - 1 do
		local pPlayer = Players[iPlayerID];
		if pPlayer ~= nil then
			local pCities = pPlayer:GetCities();
			if pCities ~= nil then
				for _, pCity in pCities:Members() do
					local cityState = CSC_CreateBakersCityState(pCity);
					iCitiesSeen = iCitiesSeen + 1;
					if cityState.HasBakersQuarter > 0 then
						iCitiesWithBakersQuarter = iCitiesWithBakersQuarter + 1;
					end

					cityStates[CSC_GetCityStateKey(iPlayerID, pCity:GetID())] = cityState;
				end
			end
		end
	end

	return cityStates, iCitiesSeen, iCitiesWithBakersQuarter;
end

local function CSC_GetCityFromRoute(iPlayerID, iCityID)
	if iPlayerID == nil or iCityID == nil or iPlayerID < 0 then return nil; end

	local pPlayer = Players[iPlayerID];
	if pPlayer == nil then return nil; end

	local pCities = pPlayer:GetCities();
	if pCities == nil then return nil; end

	return pCities:FindID(iCityID);
end

-- Convert one eligible active trade route into city counters.
-- Origin flags drive import Food/Amenity effects. Destination flags drive export
-- Production/Gold returns. Destination counters are important because multiple
-- origins can feed the same supplied Bakery/Cafe and each route should add a return.
local function CSC_MarkBakersTradeRoute(cityStates, pOriginCity, pDestinationCity)
	local bBakeryRoute, bCafeRoute = CSC_GetBakersTradeRouteState(pOriginCity, pDestinationCity);
	if not bBakeryRoute and not bCafeRoute then return; end

	local originState = cityStates[CSC_GetCityStateKey(pOriginCity:GetOwner(), pOriginCity:GetID())];
	local destinationState = cityStates[CSC_GetCityStateKey(pDestinationCity:GetOwner(), pDestinationCity:GetID())];
	if originState == nil or destinationState == nil then return; end

	if bBakeryRoute then
		originState.ImportConsumerRoute = originState.ImportConsumerRoute + 1;
		destinationState.ExportBakeryRoute = destinationState.ExportBakeryRoute + 1;
	end

	if bCafeRoute then
		originState.ImportSpecialtyRoute = originState.ImportSpecialtyRoute + 1;
		destinationState.ExportCafeRoute = destinationState.ExportCafeRoute + 1;
	end
end

local function CSC_ApplyBakersRouteBitState(cityState)
	for _, bit in ipairs(ROUTE_STACK_BITS) do
		cityState.ExportBakeryRouteBits[bit] = CSC_GetRouteBitValue(cityState.ExportBakeryRoute, bit);
		cityState.ExportCafeRouteBits[bit] = CSC_GetRouteBitValue(cityState.ExportCafeRoute, bit);
	end
end

-- Civ exposes active route lists from the origin city's trade object. We scan all
-- players/cities to keep the cache correct for AI, hotseat, and non-local turn events.
local function CSC_ScanBakersTradeRoutes(cityStates)
	local iRoutesSeen = 0;
	local iEligibleBakeryRoutes = 0;
	local iEligibleCafeRoutes = 0;
	local routeDebugLines = {};

	for iPlayerID = 0, PlayerManager.GetWasEverAliveCount() - 1 do
		local pPlayer = Players[iPlayerID];
		if pPlayer ~= nil then
			local pCities = pPlayer:GetCities();
			if pCities ~= nil then
				for _, pOriginCity in pCities:Members() do
					local pTrade = pOriginCity:GetTrade();
					if pTrade ~= nil then
						local outgoingRoutes = pTrade:GetOutgoingRoutes();
						if outgoingRoutes ~= nil then
							for _, route in ipairs(outgoingRoutes) do
								local pDestinationCity = CSC_GetCityFromRoute(route.DestinationCityPlayer, route.DestinationCityID);
								iRoutesSeen = iRoutesSeen + 1;

								local bBakeryRoute, bCafeRoute = CSC_GetBakersTradeRouteState(pOriginCity, pDestinationCity);
								if bBakeryRoute then iEligibleBakeryRoutes = iEligibleBakeryRoutes + 1; end
								if bCafeRoute then iEligibleCafeRoutes = iEligibleCafeRoutes + 1; end

								if pDestinationCity ~= nil then
									table.insert(routeDebugLines, pOriginCity:GetName() .. " -> " .. pDestinationCity:GetName()
										.. " | OriginHasBQ=" .. tostring(CSC_CityHasFunctioningBakersQuarter(pOriginCity))
										.. ", DestBakery=" .. tostring(CSC_CityHasBuilding(pDestinationCity, BUILDING_BAKERY))
										.. ", DestBakerySuppliedProp=" .. tostring(CSC_IsPositiveProperty(pDestinationCity, PROP_BAKERY_SUPPLIED))
										.. ", OwnerHasMedievalFaires=" .. tostring(CSC_PlayerHasCivic(pDestinationCity:GetOwner(), CIVIC_MEDIEVAL_FAIRES))
										.. ", DestCafe=" .. tostring(CSC_CityHasBuilding(pDestinationCity, BUILDING_CAFE))
										.. ", DestCafeSuppliedProp=" .. tostring(CSC_IsPositiveProperty(pDestinationCity, PROP_CAFE_SUPPLIED))
										.. ", OwnerHasUrbanization=" .. tostring(CSC_PlayerHasCivic(pDestinationCity:GetOwner(), CIVIC_URBANIZATION)));
								end

								CSC_MarkBakersTradeRoute(cityStates, pOriginCity, pDestinationCity);
							end
						end
					end
				end
			end
		end
	end

	return iRoutesSeen, iEligibleBakeryRoutes, iEligibleCafeRoutes, table.concat(routeDebugLines, " || ");
end

-- Avoid sending an EXECUTE_SCRIPT operation when the plot already has the right values.
-- This keeps refresh events cheap and reduces unnecessary gameplay operations.
local function CSC_CityStateMatchesPlotProperties(cityState)
	local pPlot = Map.GetPlot(cityState.X, cityState.Y);
	if pPlot == nil then return false; end

	return (pPlot:GetProperty(PROP_HAS_BAKERS_QUARTER) or 0) == cityState.HasBakersQuarter
		and (pPlot:GetProperty(PROP_IMPORT_CONSUMER_ROUTE) or 0) == cityState.ImportConsumerRoute
		and (pPlot:GetProperty(PROP_IMPORT_SPECIALTY_ROUTE) or 0) == cityState.ImportSpecialtyRoute
		and (pPlot:GetProperty(PROP_EXPORT_BAKERY_ROUTE) or 0) == cityState.ExportBakeryRoute
		and (pPlot:GetProperty(PROP_EXPORT_CAFE_ROUTE) or 0) == cityState.ExportCafeRoute
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 1)) or 0) == (cityState.ExportBakeryRouteBits[1] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 2)) or 0) == (cityState.ExportBakeryRouteBits[2] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 4)) or 0) == (cityState.ExportBakeryRouteBits[4] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 8)) or 0) == (cityState.ExportBakeryRouteBits[8] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_BAKERY_ROUTE, 16)) or 0) == (cityState.ExportBakeryRouteBits[16] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 1)) or 0) == (cityState.ExportCafeRouteBits[1] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 2)) or 0) == (cityState.ExportCafeRouteBits[2] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 4)) or 0) == (cityState.ExportCafeRouteBits[4] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 8)) or 0) == (cityState.ExportCafeRouteBits[8] or 0)
		and (pPlot:GetProperty(CSC_GetRouteBitProperty(PROP_EXPORT_CAFE_ROUTE, 16)) or 0) == (cityState.ExportCafeRouteBits[16] or 0);
end

-- UI-to-gameplay bridge. The gameplay function name goes in OnStart; the remaining
-- parameters are passed through to CSC_SetBakersTradeRouteProperties in the gameplay script.
local function CSC_RequestBakersCityState(cityState)
	if cityState == nil or CSC_CityStateMatchesPlotProperties(cityState) then return; end

	local parameters = {};
	parameters.CityX = cityState.X;
	parameters.CityY = cityState.Y;
	parameters.HasBakersQuarter = cityState.HasBakersQuarter;
	parameters.ImportConsumerRoute = cityState.ImportConsumerRoute;
	parameters.ImportSpecialtyRoute = cityState.ImportSpecialtyRoute;
	parameters.ExportBakeryRoute = cityState.ExportBakeryRoute;
	parameters.ExportCafeRoute = cityState.ExportCafeRoute;
	parameters.ExportBakeryRouteBit1 = cityState.ExportBakeryRouteBits[1] or 0;
	parameters.ExportBakeryRouteBit2 = cityState.ExportBakeryRouteBits[2] or 0;
	parameters.ExportBakeryRouteBit4 = cityState.ExportBakeryRouteBits[4] or 0;
	parameters.ExportBakeryRouteBit8 = cityState.ExportBakeryRouteBits[8] or 0;
	parameters.ExportBakeryRouteBit16 = cityState.ExportBakeryRouteBits[16] or 0;
	parameters.ExportCafeRouteBit1 = cityState.ExportCafeRouteBits[1] or 0;
	parameters.ExportCafeRouteBit2 = cityState.ExportCafeRouteBits[2] or 0;
	parameters.ExportCafeRouteBit4 = cityState.ExportCafeRouteBits[4] or 0;
	parameters.ExportCafeRouteBit8 = cityState.ExportCafeRouteBits[8] or 0;
	parameters.ExportCafeRouteBit16 = cityState.ExportCafeRouteBits[16] or 0;
	parameters.OnStart = "CSC_SetBakersTradeRouteProperties";

	UI.RequestPlayerOperation(cityState.PlayerID, PlayerOperations.EXECUTE_SCRIPT, parameters);
end

-- Full refresh pipeline:
--   1. collect every city and its live Bakers' Quarter status
--   2. scan active outgoing trade routes
--   3. write only changed city-center plot properties
function CSC_RefreshBakersTradeRouteProperties()
	local cityStates = CSC_CollectBakersCityStates();
	CSC_ScanBakersTradeRoutes(cityStates);

	for _, cityState in pairs(cityStates) do
		CSC_ApplyBakersRouteBitState(cityState);
		CSC_RequestBakersCityState(cityState);
	end
end

local function CSC_OnBakersRouteRefreshEvent()
	CSC_RefreshBakersTradeRouteProperties();
end

-- Route changes are the important trigger, but several city/building/district events
-- can change eligibility: a Bakery becomes supplied, a Cafe is built, a Quarter is
-- pillaged, or a city changes owner. These events all use the same full refresh.
Events.PlayerTurnActivated.Add(CSC_OnBakersRouteRefreshEvent);

if Events.TradeRouteActivityChanged ~= nil then
	Events.TradeRouteActivityChanged.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityProductionCompleted ~= nil then
	Events.CityProductionCompleted.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityProductionUpdated ~= nil then
	Events.CityProductionUpdated.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.BuildingAddedToMap ~= nil then
	Events.BuildingAddedToMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.BuildingChanged ~= nil then
	Events.BuildingChanged.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.BuildingRemovedFromMap ~= nil then
	Events.BuildingRemovedFromMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.DistrictAddedToMap ~= nil then
	Events.DistrictAddedToMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.DistrictRemovedFromMap ~= nil then
	Events.DistrictRemovedFromMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.DistrictPillaged ~= nil then
	Events.DistrictPillaged.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityTransfered ~= nil then
	Events.CityTransfered.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityAddedToMap ~= nil then
	Events.CityAddedToMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.CityRemovedFromMap ~= nil then
	Events.CityRemovedFromMap.Add(CSC_OnBakersRouteRefreshEvent);
end
if Events.LoadGameViewStateDone ~= nil then
	Events.LoadGameViewStateDone.Add(CSC_OnBakersRouteRefreshEvent);
end

CSC_RefreshBakersTradeRouteProperties();

--=================================================================================================================
--=================================================================================================================
