--=================================================================================================================
--=================================================================================================================
--	Civ Supply Chains - Art Properties
--=================================================================================================================
--=================================================================================================================
print("Henno's CSC Art Properties - Gameplay Script loaded!");

local m_CityArtProperties:table = {
	{
		Source = "CSC_BAKERS_STAGE_2_EFFECT_GROWTH",
		Art = "CSC_BAKERS_STAGE_2_EFFECT_GROWTH_ART",
	},
	{
		Source = "CSC_BAKERS_STAGE_3_EFFECT_HOUSING",
		Art = "CSC_BAKERS_STAGE_3_EFFECT_HOUSING_ART",
	},
	{
		Source = "CSC_BAKERS_STAGE_4_EFFECT_TOURISM",
		Art = "CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ART",
	},
};

-- Mirror modifier-adjusted gameplay properties into direct city properties for GamePropertyRanges/CITYPROP.
function CSC_RefreshCityArtProperties(pCity)
	if pCity == nil then return; end

	for _, property in ipairs(m_CityArtProperties) do
		local sourceValue = pCity:GetProperty(property.Source) or 0;
		local artValue = 0;
		if sourceValue > 0 then
			artValue = 1;
		end

		if (pCity:GetProperty(property.Art) or 0) ~= artValue then
			pCity:SetProperty(property.Art, artValue);
		end
	end
end

function CSC_RefreshPlayerArtProperties(iPlayerID:number)
	if iPlayerID == nil or iPlayerID < 0 then return; end

	local pPlayer = Players[iPlayerID];
	if pPlayer == nil then return; end

	local pCities = pPlayer:GetCities();
	if pCities == nil then return; end

	for _, pCity in pCities:Members() do
		CSC_RefreshCityArtProperties(pCity);
	end
end

function CSC_RefreshCityArtPropertiesByID(iPlayerID:number, iCityID:number)
	if iPlayerID == nil or iPlayerID < 0 then return; end

	local pPlayer = Players[iPlayerID];
	if pPlayer == nil then return; end

	local pCities = pPlayer:GetCities();
	if pCities == nil then return; end

	local pCity = pCities:FindID(iCityID);
	CSC_RefreshCityArtProperties(pCity);
end

function CSC_RefreshAllArtProperties()
	for iPlayerID = 0, PlayerManager.GetWasEverAliveCount() - 1 do
		CSC_RefreshPlayerArtProperties(iPlayerID);
	end
end

function CSC_OnPlayerTurnActivated(iPlayerID, bIsFirstTimeThisTurn)
	CSC_RefreshPlayerArtProperties(iPlayerID);
end

function CSC_OnCityRefreshEvent(iPlayerID, iCityID)
	if iPlayerID == nil then return; end

	if iCityID ~= nil then
		CSC_RefreshCityArtPropertiesByID(iPlayerID, iCityID);
	else
		CSC_RefreshPlayerArtProperties(iPlayerID);
	end
end

function CSC_OnPlayerRefreshEvent(iPlayerID)
	if iPlayerID == nil then return; end

	CSC_RefreshPlayerArtProperties(iPlayerID);
end

function CSC_OnPlotOwnerRefreshEvent(iX, iY, iFallbackPlayerID)
	if iX ~= nil and iY ~= nil then
		local pPlot = Map.GetPlot(iX, iY);
		if pPlot ~= nil then
			local iOwner = pPlot:GetOwner();
			if iOwner ~= nil and iOwner >= 0 then
				CSC_OnPlayerRefreshEvent(iOwner);
				return;
			end
		end
	end

	CSC_OnPlayerRefreshEvent(iFallbackPlayerID);
end

function CSC_OnBuildingAddedToMap(iX, iY, iBuildingIndex, iPlayerID, iCityID)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnBuildingChanged(iX, iY, iBuildingIndex, iPlayerID, iCityID)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnBuildingRemovedFromMap(iX, iY)
	CSC_OnPlotOwnerRefreshEvent(iX, iY, nil);
end

function CSC_OnBuildingConstructed(iPlayerID, iCityID, iBuildingID, iPlotID, bOriginalConstruction)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnCityProductionEvent(iPlayerID, iCityID)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnDistrictEvent(iPlayerID, iDistrictID, iCityID, iX, iY)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnDistrictPillaged(iPlayerID, iDistrictID, iCityID, iX, iY)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnImprovementAddedToMap(iX, iY, iImprovementIndex, iPlayerID)
	CSC_OnPlotOwnerRefreshEvent(iX, iY, iPlayerID);
end

function CSC_OnImprovementChanged(iX, iY, iImprovementIndex, iPlayerID, iResourceIndex, bIsPillaged, bIsWorked)
	CSC_OnPlotOwnerRefreshEvent(iX, iY, iPlayerID);
end

function CSC_OnImprovementRemovedFromMap(iX, iY, iPlayerID)
	CSC_OnPlotOwnerRefreshEvent(iX, iY, iPlayerID);
end

function CSC_OnImprovementPillaged(iPlotIndex, iImprovementIndex)
	if iPlotIndex == nil then return; end

	local pPlot = Map.GetPlotByIndex(iPlotIndex);
	if pPlot == nil then return; end

	CSC_OnPlayerRefreshEvent(pPlot:GetOwner());
end

function CSC_OnResourceMapEvent(iX, iY, iResourceIndex)
	CSC_OnPlotOwnerRefreshEvent(iX, iY, nil);
end

function CSC_OnCityTileOwnershipChanged(iPlayerID, iCityID, iX, iY)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnCityTransfered(iNewOwnerID, iCityID, iOldOwnerID)
	CSC_OnPlayerRefreshEvent(iNewOwnerID);
	CSC_OnPlayerRefreshEvent(iOldOwnerID);
end

function CSC_OnCityAddedToMap(iPlayerID, iCityID, iX, iY)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnCityRemovedFromMap(iPlayerID, iCityID)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnCivicCompleted(iPlayerID, iCivicIndex, bCancelled)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

function CSC_OnUnitOperationEvent(iPlayerID, iUnitID)
	CSC_OnPlayerRefreshEvent(iPlayerID);
end

Events.PlayerTurnActivated.Add(CSC_OnPlayerTurnActivated);
if Events.BuildingAddedToMap ~= nil then
	Events.BuildingAddedToMap.Add(CSC_OnBuildingAddedToMap);
end
if Events.BuildingChanged ~= nil then
	Events.BuildingChanged.Add(CSC_OnBuildingChanged);
end
if Events.BuildingRemovedFromMap ~= nil then
	Events.BuildingRemovedFromMap.Add(CSC_OnBuildingRemovedFromMap);
end
if Events.CityProductionCompleted ~= nil then
	Events.CityProductionCompleted.Add(CSC_OnCityProductionEvent);
end
if Events.CityProductionUpdated ~= nil then
	Events.CityProductionUpdated.Add(CSC_OnCityProductionEvent);
end
if Events.DistrictAddedToMap ~= nil then
	Events.DistrictAddedToMap.Add(CSC_OnDistrictEvent);
end
if Events.DistrictRemovedFromMap ~= nil then
	Events.DistrictRemovedFromMap.Add(CSC_OnDistrictEvent);
end
if Events.DistrictPillaged ~= nil then
	Events.DistrictPillaged.Add(CSC_OnDistrictPillaged);
end
if Events.ImprovementAddedToMap ~= nil then
	Events.ImprovementAddedToMap.Add(CSC_OnImprovementAddedToMap);
end
if Events.ImprovementChanged ~= nil then
	Events.ImprovementChanged.Add(CSC_OnImprovementChanged);
end
if Events.ImprovementRemovedFromMap ~= nil then
	Events.ImprovementRemovedFromMap.Add(CSC_OnImprovementRemovedFromMap);
end
if Events.ResourceAddedToMap ~= nil then
	Events.ResourceAddedToMap.Add(CSC_OnResourceMapEvent);
end
if Events.ResourceChanged ~= nil then
	Events.ResourceChanged.Add(CSC_OnResourceMapEvent);
end
if Events.ResourceRemovedFromMap ~= nil then
	Events.ResourceRemovedFromMap.Add(CSC_OnResourceMapEvent);
end
if Events.CityTileOwnershipChanged ~= nil then
	Events.CityTileOwnershipChanged.Add(CSC_OnCityTileOwnershipChanged);
end
if Events.CityTransfered ~= nil then
	Events.CityTransfered.Add(CSC_OnCityTransfered);
end
if Events.CityAddedToMap ~= nil then
	Events.CityAddedToMap.Add(CSC_OnCityAddedToMap);
end
if Events.CityRemovedFromMap ~= nil then
	Events.CityRemovedFromMap.Add(CSC_OnCityRemovedFromMap);
end
if Events.CivicCompleted ~= nil then
	Events.CivicCompleted.Add(CSC_OnCivicCompleted);
end
if Events.UnitOperationSegmentComplete ~= nil then
	Events.UnitOperationSegmentComplete.Add(CSC_OnUnitOperationEvent);
end
if Events.UnitOperationDeactivated ~= nil then
	Events.UnitOperationDeactivated.Add(CSC_OnUnitOperationEvent);
end
if Events.UnitOperationsCleared ~= nil then
	Events.UnitOperationsCleared.Add(CSC_OnUnitOperationEvent);
end
if GameEvents ~= nil and GameEvents.BuildingConstructed ~= nil then
	GameEvents.BuildingConstructed.Add(CSC_OnBuildingConstructed);
end
if GameEvents ~= nil and GameEvents.OnImprovementPillaged ~= nil then
	GameEvents.OnImprovementPillaged.Add(CSC_OnImprovementPillaged);
end
if Events.LoadGameViewStateDone ~= nil then
	Events.LoadGameViewStateDone.Add(CSC_RefreshAllArtProperties);
end
CSC_RefreshAllArtProperties();

--=================================================================================================================
--=================================================================================================================
