--==========================================================================================================================
--<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
--==========================================================================================================================
-- Civ Supply Chains Notifications UI Script
-- By Zegangani
--==========================================================================================================================
print('CivSupplyChains_Notifications_UI script loaded!!!')

include("Civ6Common"); --  we include this so we can use the ReadCustomData() and WriteCustomData() functions

--===========================================================================================
-- CONSTANTS
--===========================================================================================
-- we faster processing, we cache all data in Henno_ValidCityModifiers in m_ValidCityModifiers to access them faster in this script
local m_ValidCityModifiers = {};
for row in GameInfo.Henno_ValidCityModifiers() do
	m_ValidCityModifiers[row.ModifierId] = {};
	m_ValidCityModifiers[row.ModifierId].AttachModifier = row.AttachedModifierId;
	m_ValidCityModifiers[row.ModifierId].ArgumentAmount = row.ArgumentAmount;
	m_ValidCityModifiers[row.ModifierId].Desc = row.ModifierDesc;
	m_ValidCityModifiers[row.ModifierId].NewDesc = row.ModifierNewDesc;
	m_ValidCityModifiers[row.ModifierId].IncreasedDesc = row.ModifierIncreasedDesc;
	m_ValidCityModifiers[row.ModifierId].DecreasedDesc = row.ModifierDecreasedDesc;
	m_ValidCityModifiers[row.ModifierId].RemovedDesc = row.ModifierRemovedDesc;
--	m_ValidCityModifiers[row.ModifierId].Icon = row.ModifierIcon;
end

-- we also add each individual AttachedModifierId found in m_ValidCityModifiers to m_CityAttachedModifiers, for easy fetching later in the script
local m_CityAttachedModifiers = {}
for i,v in pairs(m_ValidCityModifiers) do
	m_CityAttachedModifiers[v.AttachModifier] = {};
	if v.ArgumentAmount == nil then
		m_CityAttachedModifiers[v.AttachModifier].Amount = 0
	else
		m_CityAttachedModifiers[v.AttachModifier].Amount = v.ArgumentAmount
	end
	
	if v.Desc == nil then
		m_CityAttachedModifiers[v.AttachModifier].Desc = ''
		m_CityAttachedModifiers[v.AttachModifier].NewDesc = ''
		m_CityAttachedModifiers[v.AttachModifier].IncreasedDesc = ''
		m_CityAttachedModifiers[v.AttachModifier].DecreasedDesc = ''
		m_CityAttachedModifiers[v.AttachModifier].RemovedDesc = ''
	else
		m_CityAttachedModifiers[v.AttachModifier].Desc = v.Desc
		m_CityAttachedModifiers[v.AttachModifier].NewDesc = v.NewDesc
		m_CityAttachedModifiers[v.AttachModifier].IncreasedDesc = v.IncreasedDesc
		m_CityAttachedModifiers[v.AttachModifier].DecreasedDesc = v.DecreasedDesc
		m_CityAttachedModifiers[v.AttachModifier].RemovedDesc = v.RemovedDesc
	end
	
--	m_CityAttachedModifiers[v.AttachModifier].Icon = v.Icon
    m_CityAttachedModifiers[v.AttachModifier].Quarter = string.match(i, "MOD_CSC_([A-Z_]+)_STAGE_%d+")

end

----------
local m_SpecialistModifiers = {};
for row in GameInfo.CSC_SpecialistModifiers() do
	m_SpecialistModifiers[row.ModifierId] = {};
	m_SpecialistModifiers[row.ModifierId].AttachModifier = row.AttachedModifierId;
	m_SpecialistModifiers[row.ModifierId].NewDesc = row.ModifierNewDesc;
end

local m_SpecialistAttachedModifiers = {}
for i,v in pairs(m_SpecialistModifiers) do
	m_SpecialistAttachedModifiers[v.AttachModifier] = {};
	
	if v.NewDesc == nil then
		m_SpecialistAttachedModifiers[v.AttachModifier].NewDesc = ''
	else
		m_SpecialistAttachedModifiers[v.AttachModifier].NewDesc = v.NewDesc
	end
	
end

--===========================================================================================
-- UTILITY FUNCTIONS
--===========================================================================================
function IsLocalPlayer(iPlayerID)
	local iLocalPlayerID = Game.GetLocalPlayer();
	if iPlayerID == iPlayerID then
		return true
	else
		return false
	end
end

function PlotHasInfrastructure(pPlot)
	local eDistrictType :number = pPlot:GetDistrictType();
	local eImprovementType :number = pPlot:GetImprovementType();
	if( eDistrictType ~= -1 ) then
		return true
	elseif( eImprovementType ~= -1 ) then
		return true
	end
		
	return false
end

--==========================================================================================================================
-- OnRefreshCityQuarters
--==========================================================================================================================
function OnRefreshCityQuarters()
	
	local iPlayerID = Game.GetLocalPlayer();
	if (iPlayerID and iPlayerID >= 0) then		-- Check to see if there is any local player
		
		-- Each Player has his own cached table for City Modifiers. We use it to get access to data from player's last turn (or cache update) to compare them with current turn. 
		-- mostly useful for triggering notifications for things happened during other players' turn, but also very improtant for game save/load compatibility.
		local sHQCitiesStringKey = 'HennoQuartersAbilitiesCaching_Player'..tostring(iPlayerID);
		local tHQCitiesCache = ReadCustomData(sHQCitiesStringKey); -- this function reads specific cached data (if it exists) using its relevant specific string key.
																   -- we add ID of the Player at the end of the string so we only read/load this player's cached data
		
		local tHQCitiesCurrent = {} -- holds data for all Cities of the Player. Later cached in sHQCitiesStringKey custom data.
		local bAbilitiesHaveChanged = false -- if we notice any changes compared to last cached state then we cache the new changes.
		
		-- we iterate through each City of the Player to check for their individual City Modifiers
		local playerCities = Players[iPlayerID]:GetCities();
		for i, pCity in playerCities:Members() do
			if pCity then
				local iCityID		:number = pCity:GetID();
				local iCityX		:number = pCity:GetX();
				local iCityY		:number = pCity:GetY();
				local sCityName		:string = Locale.Lookup(pCity:GetName());
				local tCityModifiers = {}; -- holds all current Ability modifiers in this city
				
				-- we iterate through all modifiers in the Game, and collect all 'active and henno-valid' ones in the city
				local tModifiers = GameEffects.GetModifiers()
				for _, iModifier in pairs(tModifiers) do
					local sModifier = GameEffects.GetModifierDefinition(iModifier).Id
					-- Now we check if the ModifierId is also listed as a City Modifier in 'm_ValidCityModifiers'
					if m_ValidCityModifiers[sModifier] then
						
						-- Is this Modifer Active and has Subjects?
						if (GameEffects.GetModifierActive(iModifier)) and (GameEffects.GetModifierSubjectCount(iModifier) > 0) then
							
							-- now we iterate through the subjects of this modifier, bc they are the ones that hold the attached modifier
							local tSubjects = GameEffects.GetModifierSubjects(iModifier) or {}
							for i,v in pairs(tSubjects) do
								local sObjectTypeName = Locale.Lookup(GameEffects.GetObjectType(v) or "");
								local sString = GameEffects.GetObjectString(v)
								
								if sString then
									-- sString holds all neccessary data for this Subject, but we need to organzie it better for easier use
									-- sString may look like this: "District: 262147, Owner: 0, SubType: 1, SubValue: -1237247573, City: 65536"
									-- but we can't directly access a specific tag's info, like City (ID)
									-- this method below dynamically puts every value in a table, inside info, named after the key before it that has ':' at the end, like 65536 inside 'City'
									local info = {}
									for key, value in string.gmatch(sString, "(%w+):%s*(-?%d+)") do
										info[key] = tonumber(value)
									end
									
									-- Since the attached modifers we're looking after are applied to Districts, we only cehck for those
									-- And we also check if this Subject's CityID and OwnerID are the same as the current City's
									if sObjectTypeName == 'District' and info.City == iCityID and info.Owner == iPlayerID  then
										-- now we get the AttachedModifier and double check if it's in tCityModifiers
										local sAttachModifier = m_ValidCityModifiers[sModifier].AttachModifier
										if m_CityAttachedModifiers[sAttachModifier] then
											-- if this City doesn't already have this modifier, then add it as a new table in tCityModifiers with StackAmount 1
											-- else just add +1 to StackAmount of same table
											if not tCityModifiers[sAttachModifier] then
												tCityModifiers[sAttachModifier] = {}
												tCityModifiers[sAttachModifier].StackAmount = 1;
											else
												tCityModifiers[sAttachModifier].StackAmount = tCityModifiers[sAttachModifier].StackAmount + 1
											end
										end
									end
								end
							end							
						end
					end
				end
				
				-- Add a new Table to tHQCitiesCurrent with same key as this City's ID and assign tCityModifiers as its value
				tHQCitiesCurrent[iCityID] = tCityModifiers
				
				-- If we have cached data for this Player's Cities, we iterate over them
				-- For each cached City's modifier, we check if it's still active in the City
				-- if not, we trigger a notification for the Player that Modifier X has been removed from City Y.
				if tHQCitiesCache and tHQCitiesCache[iCityID] then
					for sAttachModifier,v in pairs(tHQCitiesCache[iCityID]) do
						local tCurrentModifier = tHQCitiesCurrent[iCityID][sAttachModifier]
						
						-- if tCurrentModifier is nil then it means it's no longer active in this city (iCityID)
						if tCurrentModifier == nil then
							local iAmount = m_CityAttachedModifiers[sAttachModifier].Amount * -v.StackAmount; -- we multiply this modifier's DB yield value by the -1*StackAmount in this city to get the exact yield loss
							local sString = Locale.Lookup(m_CityAttachedModifiers[sAttachModifier].RemovedDesc, iAmount, v.StackAmount); -- string for this modifier's Ability
							--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_DESC', v.StackAmount); -- string for the Stack Source Amount
							
							local sMainString = ''
							-- If iAmount is positive then we add a '+' sign at start of the string (bc it's not shown automatically), negative values will always have the '-' sign show up. 
							if iAmount > 0 then
								sMainString = '+'..sString
							else
								sMainString = sString
							end
							
							bAbilitiesHaveChanged = true
							
							-- notification data - is unique to each Notification type
							local notificationData = {}
							notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_MESSAGE");
							notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
							notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
							notificationData.AlwaysUnique = true;
							--notificationData.AutoActivate = true;
							
							sNotificationType = "NOTIFICATION_CSC_" .. m_CityAttachedModifiers[sAttachModifier].Quarter .. "_EFFECT_REMOVED"

							-- this triggers the notification for the Player
							NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						end
					end
				end
									
				-- Now we iterate through Current City's Modifiers, and for each check if it already exists in cached data for this city:
				-- 1) if not then we know it's a new applied modifier
				-- 2) if yes, then we compare its current StackAmount with that in the cached data.
				--    - if amount is the same, then we don't have any changes, so we don't need to notify the player
				--    - if current amount is higher then we know we got a new Stack Source and the modifier effect is increased, and notify the player about that
				--    - if current amount is lower then we know we 1 or more Stack Sources have been removed and the modifier effect is decreased, and notify the player about that
				for sAttachModifier,v in pairs(tCityModifiers) do
					local bIsNewModifier = false
					local bIsStackAmountIncreased = false
					local bIsStackAmountDecreased = false
					local iStackAmountChange = v.StackAmount
					local iCachedStackAmount = nil
					if tHQCitiesCache and tHQCitiesCache[iCityID] then
						local tCachedModifier = tHQCitiesCache[iCityID][sAttachModifier]
						if tCachedModifier then
							if tCachedModifier.StackAmount < v.StackAmount then
								-- a modifier stack got added, we can notify player about new stack modifier added
								bIsStackAmountIncreased = true
							elseif tCachedModifier.StackAmount > v.StackAmount then
								-- a modifier stack got reduced, we can notify player about reduced stack modifier
								bIsStackAmountDecreased = true
							end
							iStackAmountChange = v.StackAmount - tCachedModifier.StackAmount
							iCachedStackAmount = tCachedModifier.StackAmount
						else
							bIsNewModifier = true
						end
					else
						bIsNewModifier = true
					end
					
					local iAmount = m_CityAttachedModifiers[sAttachModifier].Amount * iStackAmountChange;
					
					local sMainString = ''
					-- If iAmount is positive then we add a '+' sign at start of the string (bc it's not shown automatically), negative values will always have the '-' sign show up. 
					if iAmount > 0 then
						sMainString = '+'
					end
					
					if bIsNewModifier == true then
						--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_DESC', iStackAmountChange);
						--sMainString = sMainString..sStackString

						local sString = Locale.Lookup(m_CityAttachedModifiers[sAttachModifier].NewDesc, iAmount, iStackAmountChange);
						sMainString = sMainString..sString
						
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						--notificationData.AutoActivate = true;
						
						sNotificationType = "NOTIFICATION_CSC_" .. m_CityAttachedModifiers[sAttachModifier].Quarter .. "_EFFECT_NEW"
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bAbilitiesHaveChanged = true
						
					elseif bIsStackAmountIncreased == true then
						--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_CHANGE_DESC', iStackAmountChange, 'LOC_HENNO_CITY_ABILITY_SOURCE_INCREASE');
						--sMainString = sMainString..sStackString

						local sString = Locale.Lookup(m_CityAttachedModifiers[sAttachModifier].IncreasedDesc, iAmount, iStackAmountChange);
						sMainString = sMainString..sString
						
						--local sIncreaseString = Locale.Lookup("LOC_HENNO_CITY_ABILITY_CHANGE_INCREASE")
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						--notificationData.AutoActivate = true;
						
						sNotificationType = "NOTIFICATION_CSC_" .. m_CityAttachedModifiers[sAttachModifier].Quarter .. "_EFFECT_INCREASED"
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bAbilitiesHaveChanged = true
						
					elseif bIsStackAmountDecreased == true then
						local iStackAmountChange = math.abs(iStackAmountChange)
						--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_CHANGE_DESC', iStackAmountChange, 'LOC_HENNO_CITY_ABILITY_SOURCE_DECREASE');
						--sMainString = sMainString..sStackString

						local sString = Locale.Lookup(m_CityAttachedModifiers[sAttachModifier].DecreasedDesc, iAmount, iStackAmountChange);
						sMainString = sMainString..sString
						
						--local sDecreaseString = Locale.Lookup("LOC_HENNO_CITY_ABILITY_CHANGE_DECREASE")
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						--notificationData.AutoActivate = true;
					
						sNotificationType = "NOTIFICATION_CSC_" .. m_CityAttachedModifiers[sAttachModifier].Quarter .. "_EFFECT_DECREASED"
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bAbilitiesHaveChanged = true
						
					end
				end
			end
		end
		
		-- Last step to do is to cache all Current Player's Cities' data into the game (so it's load/save compatible)
		-- for which we use WriteCustomData() function from Civ6Common.
		-- At the start of this script we used ReadCustomData() to get access to this Player's cached data, if there are any.
		if bAbilitiesHaveChanged == true then
			WriteCustomData(sHQCitiesStringKey, tHQCitiesCurrent);
		end
	end
end


--===========================================================================================
-- Events: listening to Events that should trigger Notifications if available
--
-- Note: we only listen to Actions in the current local Player's Turn. Any Actions that could trigger a Notification, but happened in another Player's turn
-- will be delayed until local Player's Next Turn Start.
--===========================================================================================
function OnLocalPlayerTurnBegin()
	OnRefreshCityQuarters()
end

function OnDistrictRemovedFromMap(iPlayerID, districtID, iCityID, iX, iY, districtType)
	local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
	if bIsLocalPlayer == true then
		OnRefreshCityQuarters()
	end
end

function OnDistrictAddedToMap(iPlayerID, districtID, iCityID, iX, iY, districtType, iPercentage)
	local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
	if bIsLocalPlayer == true then
		OnRefreshCityQuarters()
	end
end

function OnBuildingAddedToMap(iX, iY, iBuildingIndex, iPlayerID, iCityID, iPercentage, bIsPillaged)
	local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
	if bIsLocalPlayer == true and iPercentage >=100 then
		OnRefreshCityQuarters()
	end
end

function OnBuildingChanged(iX, iY, iBuildingIndex, iPlayerID, iCityID, iPercentage)
	local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
	if bIsLocalPlayer == true and (iPercentage >=100 or iPercentage <=0) then
		OnRefreshCityQuarters()
	end
end

function OnBuildingRemovedFromMap(iX, iY)
	local pPlot = Map.GetPlot(iX, iY);
	if pPlot then
		local iOwner = pPlot:GetOwner();
		if iOwner then
			local bIsLocalPlayer = IsLocalPlayer(iOwner)
			if bIsLocalPlayer == true then
				OnRefreshCityQuarters()
			end
		end
	end
end

function OnCityRemovedFromMap(iPlayerID, iCityID)
	local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
	if bIsLocalPlayer == true then
		OnRefreshCityQuarters()
	end
end

function OnCityTransfered(iNewOwnerID, iCityID, iOldOwnerID, eCityTransferType)
	local bIsLocalPlayer = IsLocalPlayer(iNewOwnerID)
	if bIsLocalPlayer == true then
		OnRefreshCityQuarters()
	end
end

function OnImprovementAddedToMap(iX, iY, iImprovementIndex, iPlayerID)
	local pPlot = Map.GetPlot(iX, iY);
	if pPlot then
		local iOwner = pPlot:GetOwner();
		if iOwner and iOwner == iPlayerID then
			local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
			if bIsLocalPlayer == true then
				OnRefreshCityQuarters()
			end
		end
	end
end

function OnImprovementChanged(iX, iY, iImprovementIndex, iPlayerID, iResourceIndex, bIsPillaged, bIsWorked)
	local pPlot = Map.GetPlot(iX, iY);
	if pPlot then
		local iOwner = pPlot:GetOwner();
		if iOwner and iOwner == iPlayerID then
			local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
			if bIsLocalPlayer == true then
				OnRefreshCityQuarters()
			end
		end
	end
end

function OnImprovementRemovedFromMap(iX, iY, iPlayerID)
	local pPlot = Map.GetPlot(iX, iY);
	if pPlot then
		local iOwner = pPlot:GetOwner();
		if iOwner and iOwner == iPlayerID then
			local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
			if bIsLocalPlayer == true then
				OnRefreshCityQuarters()
			end
		end
	end
end

function OnCityTileOwnershipChanged(iPlayerID, iCityID, iX, iY)
	local bIsLocalPlayer = IsLocalPlayer(iPlayerID)
	if bIsLocalPlayer == true then
		local pPlot = Map.GetPlot(iX, iY);
		if pPlot then
			local bPlotHasInfrastructure = PlotHasInfrastructure(pPlot)
			if bPlotHasInfrastructure == true then
				local iPlotCityID = Cities.GetPlotPurchaseCity(pPlot:GetIndex()):GetID();
				local iOwner = pPlot:GetOwner();
				if iOwner and iPlotCityID and (iOwner == iPlayerID) and (iPlotCityID == iCityID) then
					OnRefreshCityQuarters()
				end
			end
		end
	end
end

function Initialize()
	-- Event listeners should only work after the Load Screen is closed, and the Player is in the Game.
	Events.LocalPlayerTurnBegin.Add(OnLocalPlayerTurnBegin);
	Events.DistrictRemovedFromMap.Add(OnDistrictRemovedFromMap)
	Events.DistrictAddedToMap.Add(OnDistrictAddedToMap)
	Events.BuildingAddedToMap.Add(OnBuildingAddedToMap)
	Events.BuildingChanged.Add(OnBuildingChanged)
	Events.BuildingRemovedFromMap.Add(OnBuildingRemovedFromMap)
	Events.CityRemovedFromMap.Add(OnCityRemovedFromMap)
	Events.CityTransfered.Add(OnCityTransfered)
	Events.ImprovementAddedToMap.Add(OnImprovementAddedToMap)
	Events.ImprovementChanged.Add(OnImprovementChanged)
	Events.ImprovementRemovedFromMap.Add(OnImprovementRemovedFromMap)
	Events.CityTileOwnershipChanged.Add(OnCityTileOwnershipChanged)
end
Events.LoadScreenClose.Add(Initialize)
--==========================================================================================================================
--==========================================================================================================================