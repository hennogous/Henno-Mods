-- Shared exact-plot placement for persistent Wonder-hosted Services.
-- SQL grants select the first Wonder district; CreateBuilding's explicit plot
-- argument is required when a city contains several eligible Wonders.
local SERVICE_HOSTS = {
	{ HostType = "BUILDING_BOLSHOI_THEATRE", ServiceType = "BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI", ActivationProperty = "CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_READY" },
	{ HostType = "BUILDING_BROADWAY", ServiceType = "BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY", ActivationProperty = "CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_READY" },
	{ HostType = "BUILDING_SYDNEY_OPERA_HOUSE", ServiceType = "BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY", ActivationProperty = "CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_READY" },
};
local m_IsReconciling = false;
local m_HostPlots = {};
local m_CurrentHostPlots = {};
local FASHION_HOUSE = GameInfo.Buildings["BUILDING_CSC_TAILORS_FASHION_HOUSE"];
local TAILORS_QUARTER = GameInfo.Districts["DISTRICT_CSC_TAILORS_QUARTER"];
-- SQL owns unlock and material rules through the shared producer requirement set.
local SOURCE_ELIGIBILITY_PROPERTY = "CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE";
local NUM_DIRECTIONS = (DirectionTypes and DirectionTypes.NUM_DIRECTION_TYPES) or 6;

local function PropertyNumber(owner, name)
	if owner == nil then return nil; end
	-- Native GetProperty may return zero values for an unset key. Capture it
	-- first so tonumber always receives one argument, including an explicit nil.
	local value = owner:GetProperty(name);
	return tonumber(value);
end

local function SetProperty(owner, name, value)
	if owner ~= nil and (PropertyNumber(owner, name) or 0) ~= value then
		owner:SetProperty(name, value);
	end
end

local function Location(buildings, index)
	if buildings:HasBuilding(index) then return buildings:GetBuildingLocation(index); end
	return -1;
end

local function HasFunctioningQuarter(districts)
	if not districts:HasDistrict(TAILORS_QUARTER.Index) then return false; end
	-- CityDistricts.IsPillaged is a UI API. Gameplay exposes the instance query.
	local district = districts:GetDistrict(TAILORS_QUARTER.Index);
	return district ~= nil and not district:IsPillaged();
end

local function IsEligible(city, hostPlot, hostIndex)
	if FASHION_HOUSE == nil or TAILORS_QUARTER == nil then return false; end
	local player = Players[city:GetOwner()];
	if player == nil then return false; end
	if city:GetBuildings():IsPillaged(hostIndex) then return false; end
	local plot = Map.GetPlotByIndex(hostPlot);
	if plot == nil then return false; end
	for _, seller in player:GetCities():Members() do
		local buildings = seller:GetBuildings();
		local districts = seller:GetDistricts();
		if buildings:HasBuilding(FASHION_HOUSE.Index) and not buildings:IsPillaged(FASHION_HOUSE.Index)
			and HasFunctioningQuarter(districts)
			and (PropertyNumber(seller, SOURCE_ELIGIBILITY_PROPERTY) or 0) > 0 then
			local x, y = districts:GetDistrictLocation(TAILORS_QUARTER.Index);
			for direction = 0, NUM_DIRECTIONS - 1 do
				local adjacent = Map.GetAdjacentPlot(x, y, direction);
				if adjacent ~= nil and adjacent:GetIndex() == hostPlot then return true; end
			end
		end
	end
	return false;
end

local function ReconcilePair(city, pair)
	local host = GameInfo.Buildings[pair.HostType];
	local service = GameInfo.Buildings[pair.ServiceType];
	if host == nil or service == nil then return; end
	local buildings = city:GetBuildings();
	local hostPlot = Location(buildings, host.Index);
	local servicePlot = Location(buildings, service.Index);
	local establishedProperty = pair.ActivationProperty .. "_ESTABLISHED";
	local lastPlotProperty = pair.ActivationProperty .. "_PLOT";
	local oldPlot = PropertyNumber(city, lastPlotProperty);
	if oldPlot ~= nil and oldPlot >= 0 and oldPlot ~= hostPlot then
		SetProperty(Map.GetPlotByIndex(oldPlot), pair.ActivationProperty, 0);
	end
	SetProperty(city, lastPlotProperty, hostPlot);
	if hostPlot == nil or hostPlot < 0 then
		SetProperty(city, pair.ActivationProperty, 0);
		SetProperty(city, establishedProperty, 0);
		if servicePlot ~= nil and servicePlot >= 0 then buildings:RemoveBuilding(service.Index); end
		return;
	end
	local active = IsEligible(city, hostPlot, host.Index);
	local markerKey = tostring(hostPlot) .. ":" .. pair.ActivationProperty;
	m_CurrentHostPlots[markerKey] = { Plot = hostPlot, Property = pair.ActivationProperty, Owner = city:GetOwner() };
	SetProperty(Map.GetPlotByIndex(hostPlot), pair.ActivationProperty, active and 1 or 0);
	SetProperty(city, pair.ActivationProperty, active and 1 or 0);
	-- Existing variants (including legacy misplaced ones) establish persistence.
	if active or (servicePlot ~= nil and servicePlot >= 0) then SetProperty(city, establishedProperty, 1); end
	if (PropertyNumber(city, establishedProperty) or 0) <= 0 then return; end
	if servicePlot == hostPlot then return; end
	if servicePlot ~= nil and servicePlot >= 0 then buildings:RemoveBuilding(service.Index); end
	city:GetBuildQueue():CreateBuilding(service.Index, hostPlot);
end

local function ReconcileAll()
	if m_IsReconciling then return; end
	-- A player count is not an ID range. Non-city players may also have no city
	-- collection; neither case should prevent grants to another player.
	if PlayerManager == nil or Players == nil then return; end
	local alive = PlayerManager.GetAlive();
	if alive == nil then return; end
	local players = {};
	local unavailable = {};
	for _, player in ipairs(alive) do
		local cities = player:GetCities();
		if cities ~= nil then
			table.insert(players, { Player = player, Cities = cities });
		else
			unavailable[player:GetID()] = true;
		end
	end
	table.sort(players, function(a, b) return a.Player:GetID() < b.Player:GetID(); end);
	m_IsReconciling = true;
	m_CurrentHostPlots = {};
	local success, message = pcall(function()
		-- Numeric player/city order and the fixed host list keep mutations stable.
		for _, entry in ipairs(players) do
			local cities = {};
			for _, city in entry.Cities:Members() do table.insert(cities, city); end
			table.sort(cities, function(a, b) return a:GetID() < b:GetID(); end);
			for _, city in ipairs(cities) do
				for _, pair in ipairs(SERVICE_HOSTS) do ReconcilePair(city, pair); end
			end
		end
		-- A removed city no longer has an object from which to read its last plot.
		-- Clear markers remembered by the preceding pass after processing survivors.
		for key, marker in pairs(m_HostPlots) do
			if m_CurrentHostPlots[key] == nil then
				if unavailable[marker.Owner] then
					m_CurrentHostPlots[key] = marker;
				else
					SetProperty(Map.GetPlotByIndex(marker.Plot), marker.Property, 0);
				end
			end
		end
		m_HostPlots = m_CurrentHostPlots;
	end);
	m_IsReconciling = false;
	if not success then print("CSC Wonder Services: reconciliation failed: " .. tostring(message)); end
end

-- Exposed for focused gameplay tests and diagnostics.
function CSC_RefreshWonderServices() ReconcileAll(); end
for _, name in ipairs({"PlayerTurnActivated", "LoadScreenClose", "WonderCompleted", "BuildingAddedToMap", "BuildingChanged", "BuildingRemovedFromMap", "CityTransfered", "CityRemovedFromMap", "ImprovementAddedToMap", "ImprovementChanged", "ImprovementRemovedFromMap", "ImprovementPillaged", "DistrictAddedToMap", "DistrictChanged", "DistrictRemovedFromMap", "CityTileOwnershipChanged", "CivicCompleted"}) do
	if Events[name] ~= nil then Events[name].Add(ReconcileAll); end
end
ReconcileAll();
