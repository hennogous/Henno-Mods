--==========================================================================================================================
--<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
--==========================================================================================================================
-- Civ Supply Chains Notifications UI Script
-- By Zegangani
--==========================================================================================================================
print('CivSupplyChains_Notifications_UI script loaded!!!')

include("Civ6Common"); --  we include this so we can use the ReadCustomData() and WriteCustomData() functions

function PrintTable(t, indent)
	indent = indent or 0
	local prefix = string.rep("  ", indent)
	for k, v in pairs(t) do
		if type(v) == "table" then
			print(prefix .. tostring(k) .. " = {")
			PrintTable(v, indent + 1)
			print(prefix .. "}")
		else
			print(prefix .. tostring(k) .. " = " .. tostring(v))
		end
	end
end

function tableLength(t)
    local count = 0
    for _ in pairs(t) do
        count = count + 1
    end
    return count
end

--===========================================================================================
-- CONSTANTS
--===========================================================================================
-- we faster processing, we cache all data in CSC_AbilityAttachModifiers in mCSC_AbilityAttachModifiers to access them faster in this script
local mCSC_AbilityAttachModifiers = {};
for row in GameInfo.CSC_AbilityAttachModifiers() do
	mCSC_AbilityAttachModifiers[row.ModifierId] = {};
	mCSC_AbilityAttachModifiers[row.ModifierId].AbilityEffectModifierId = row.AbilityEffectModifierId;
	mCSC_AbilityAttachModifiers[row.ModifierId].ArgumentAmount = row.AbilityArgumentAmount;
	mCSC_AbilityAttachModifiers[row.ModifierId].Desc = row.AbilityDesc;
	mCSC_AbilityAttachModifiers[row.ModifierId].NewDesc = row.AbilityNewDesc;
	mCSC_AbilityAttachModifiers[row.ModifierId].IncreasedDesc = row.AbilityIncreasedDesc;
	mCSC_AbilityAttachModifiers[row.ModifierId].DecreasedDesc = row.AbilityDecreasedDesc;
	mCSC_AbilityAttachModifiers[row.ModifierId].RemovedDesc = row.AbilityRemovedDesc;
end

-- we also add each individual AbilityEffectModifierId found in mCSC_AbilityAttachModifiers to mCSC_AbilityEffectModifiers, for easy fetching later in the script
local mCSC_AbilityEffectModifiers = {}
for i,v in pairs(mCSC_AbilityAttachModifiers) do
	mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId] = {};

	if v.ArgumentAmount == nil then
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].Amount = 0
	else
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].Amount = v.ArgumentAmount
	end
	
	if v.Desc == nil then
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].Desc = ''
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].NewDesc = ''
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].IncreasedDesc = ''
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].DecreasedDesc = ''
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].RemovedDesc = ''
	else
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].Desc = v.Desc
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].NewDesc = v.NewDesc
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].IncreasedDesc = v.IncreasedDesc
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].DecreasedDesc = v.DecreasedDesc
		mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].RemovedDesc = v.RemovedDesc
	end
	
    mCSC_AbilityEffectModifiers[v.AbilityEffectModifierId].Quarter = string.match(i, "MOD_CSC_([A-Z_]+)_STAGE_%d+")

end

--[[
----------
-- Specialist-slot grant notifications are currently folded into the main
-- Quarter effect notification text instead.
local mCSC_SpecialistAttachModifiers = {};
for row in GameInfo.CSC_SpecialistAttachModifiers() do
	mCSC_SpecialistAttachModifiers[row.ModifierId] = {};
	mCSC_SpecialistAttachModifiers[row.ModifierId].SpecialistGrantModifierId = row.SpecialistGrantModifierId;
	mCSC_SpecialistAttachModifiers[row.ModifierId].GrantDesc = row.SpecialistGrantDesc;
end

local mCSC_SpecialistGrantModifiers = {}
for i,v in pairs(mCSC_SpecialistAttachModifiers) do
	mCSC_SpecialistGrantModifiers[v.SpecialistGrantModifierId] = {};
	
	if v.GrantDesc == nil then
		mCSC_SpecialistGrantModifiers[v.SpecialistGrantModifierId].GrantDesc = ''
	else
		mCSC_SpecialistGrantModifiers[v.SpecialistGrantModifierId].GrantDesc = v.GrantDesc
	end
	
end
]]

--===========================================================================================
-- UTILITY FUNCTIONS
--===========================================================================================
function IsLocalPlayer(iPlayerID)
	local iLocalPlayerID = Game.GetLocalPlayer();
	if iPlayerID == iLocalPlayerID then
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

function tableLength(t)
    local count = 0
    for _ in pairs(t) do
        count = count + 1
    end
    return count
end

local function GetSignedAmountText(iAmount)
	if iAmount > 0 then
		return '+' .. tostring(iAmount)
	end
	return tostring(iAmount)
end

--==========================================================================================================================
-- OnRefreshCityQuarters
--==========================================================================================================================
function OnRefreshCityQuarters()
	
	local iPlayerID = Game.GetLocalPlayer();
	if (iPlayerID and iPlayerID >= 0) then		-- Check to see if there is any local player
		
		-- Each Player has his own cached table for City Modifiers. We use it to get access to data from player's last turn (or cache update) to compare them with current turn. 
		-- mostly useful for triggering notifications for things happened during other players' turn, but also very improtant for game save/load compatibility.
		local sCSC_CitiesAbilitiesStringKey = 'CSC_AbilitiesCaching_Player'..tostring(iPlayerID);
		local tCSC_CitiesAbilitiesCache = ReadCustomData(sCSC_CitiesAbilitiesStringKey); -- this function reads specific cached data (if it exists) using its relevant specific string key.
																   		 				 -- we add ID of the Player at the end of the string so we only read/load this player's cached data		
		local tCSC_CitiesAbilitiesCurrent = {} -- holds data for all Cities of the Player. Later cached in sCSC_CitiesAbilitiesStringKey custom data.
		local bCSC_AbilitiesHaveChanged = false -- if we notice any changes compared to last cached state then we cache the new changes.
	
--[[		local sCSC_CitiesSpecialistsStringKey = 'CSC_SpecialistsCaching_Player'..tostring(iPlayerID);
		local tCSC_CitiesSpecialistsCache = ReadCustomData(sCSC_CitiesSpecialistsStringKey);
		local tCSC_CitiesSpecialistsCurrent = {}
		local bCSC_SpecialistsHaveChanged = false ]]

		-- we iterate through each City of the Player to check for their individual City Modifiers
		local playerCities = Players[iPlayerID]:GetCities();
		for i, pCity in playerCities:Members() do
			if pCity then
				local iCityID		:number = pCity:GetID();
				local iCityX		:number = pCity:GetX();
				local iCityY		:number = pCity:GetY();
				local sCityName		:string = Locale.Lookup(pCity:GetName());
				local tCityCurrentAbilityModifiers = {}; -- holds all current Ability modifiers in this city
--				local tCityCurrentSpecialistModifiers = {}; -- holds all current Specialist modifiers in this city
				
				-- we iterate through all modifiers in the Game, and collect all 'active and henno-valid' ones in the city
				local tModifiers = GameEffects.GetModifiers()
				for _, iModifier in pairs(tModifiers) do
					local sModifier = GameEffects.GetModifierDefinition(iModifier).Id
					-- Now we check if the ModifierId is also listed as a City Modifier in 'mCSC_AbilityAttachModifiers' or 'mCSC_SpecialistAttachModifiers'
					if mCSC_AbilityAttachModifiers[sModifier] then
						
						-- Is this Modifer Active and has Subjects?
						if (GameEffects.GetModifierActive(iModifier)) and (GameEffects.GetModifierSubjectCount(iModifier) > 0) then
							
							-- now we iterate through the subjects of this modifier, bc they are the ones that hold the effect / grant modifier
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
									
									-- Since the attached modifers we're looking for are applied to Districts, we only check for those
									-- And we also check if this Subject's CityID and OwnerID are the same as the current City's
									if sObjectTypeName == 'District' and info.City == iCityID and info.Owner == iPlayerID  then
										-- now we get the AttachedModifier and double check if it's in tCityCurrentAbilityModifiers
										if mCSC_AbilityAttachModifiers[sModifier] then
											local sAbilityEffectModifierId = mCSC_AbilityAttachModifiers[sModifier].AbilityEffectModifierId
											if mCSC_AbilityEffectModifiers[sAbilityEffectModifierId] then
												-- if this City doesn't already have this modifier, then add it as a new table in tCityCurrentAbilityModifiers with StackAmount 1
												-- else just add +1 to StackAmount of same table												
												if not tCityCurrentAbilityModifiers[sAbilityEffectModifierId] then
													tCityCurrentAbilityModifiers[sAbilityEffectModifierId] = {}
													tCityCurrentAbilityModifiers[sAbilityEffectModifierId].StackAmount = 1;
												else
													tCityCurrentAbilityModifiers[sAbilityEffectModifierId].StackAmount = tCityCurrentAbilityModifiers[sAbilityEffectModifierId].StackAmount + 1
												end
											end
--[[										elseif mCSC_SpecialistAttachModifiers[sModifier] then
											local sSpecialistGrantModifierId = mCSC_SpecialistAttachModifiers[sModifier].SpecialistGrantModifierId
											if mCSC_SpecialistGrantModifiers[sSpecialistGrantModifierId] then
												tCityCurrentSpecialistModifiers[sSpecialistGrantModifierId] = true										
											end ]]
										end
									end
								end
							end							
						end
					end
				end
				
				-- Add a new Table to tCSC_CitiesAbilitiesCurrent with same key as this City's ID and assign tCityCurrentAbilityModifiers as its value
				tCSC_CitiesAbilitiesCurrent[iCityID] = tCityCurrentAbilityModifiers
--				tCSC_CitiesSpecialistsCurrent[iCityID] = tCityCurrentSpecialistModifiers
				
				-- If we have cached data for this Player's Cities, we iterate over them
				-- For each cached City's modifier, we check if it's still active in the City
				-- if not, we trigger a notification for the Player that Modifier X has been removed from City Y.
				if tCSC_CitiesAbilitiesCache and tCSC_CitiesAbilitiesCache[iCityID] then
					for sAbilityEffectModifierId,v in pairs(tCSC_CitiesAbilitiesCache[iCityID]) do
						local tCurrentModifier = tCSC_CitiesAbilitiesCurrent[iCityID][sAbilityEffectModifierId]
						
						-- if tCurrentModifier is nil then it means it's no longer active in this city (iCityID)
						if tCurrentModifier == nil then
							local iAmount = mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].Amount * -v.StackAmount; -- we multiply this modifier's DB yield value by the -1*StackAmount in this city to get the exact yield loss
							local sMainString = Locale.Lookup(mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].RemovedDesc, GetSignedAmountText(iAmount), v.StackAmount); -- string for this modifier's Ability
							
							bCSC_AbilitiesHaveChanged = true
							
							-- notification data - is unique to each Notification type
							local notificationData = {}
							notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_MESSAGE");
							notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_REMOVED_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
							notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
							notificationData.AlwaysUnique = true;
							--notificationData.AutoActivate = true;
							
							sNotificationType = "NOTIFICATION_CSC_" .. mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].Quarter .. "_EFFECT_REMOVED"

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
				for sAbilityEffectModifierId,v in pairs(tCityCurrentAbilityModifiers) do
					local bIsNewModifier = false
					local bIsStackAmountIncreased = false
					local bIsStackAmountDecreased = false
					local iStackAmountChange = v.StackAmount
					local iCachedStackAmount = nil
					if tCSC_CitiesAbilitiesCache and tCSC_CitiesAbilitiesCache[iCityID] then
						local tCachedModifier = tCSC_CitiesAbilitiesCache[iCityID][sAbilityEffectModifierId]
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
					
					local iAmount = mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].Amount * iStackAmountChange;
					local sAmountText = GetSignedAmountText(iAmount)
					
					if bIsNewModifier == true then
						--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_DESC', iStackAmountChange);
						--sMainString = sMainString..sStackString

						local sMainString = Locale.Lookup(mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].NewDesc, sAmountText, iStackAmountChange);
						
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_NEW_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						--notificationData.AutoActivate = true;
						
						sNotificationType = "NOTIFICATION_CSC_" .. mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].Quarter .. "_EFFECT_NEW"
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bCSC_AbilitiesHaveChanged = true
						
					elseif bIsStackAmountIncreased == true then
						--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_CHANGE_DESC', iStackAmountChange, 'LOC_HENNO_CITY_ABILITY_SOURCE_INCREASE');
						--sMainString = sMainString..sStackString

						local sMainString = Locale.Lookup(mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].IncreasedDesc, sAmountText, iStackAmountChange);
						
						--local sIncreaseString = Locale.Lookup("LOC_HENNO_CITY_ABILITY_CHANGE_INCREASE")
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_INCREASED_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						--notificationData.AutoActivate = true;
						
						sNotificationType = "NOTIFICATION_CSC_" .. mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].Quarter .. "_EFFECT_INCREASED"
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bCSC_AbilitiesHaveChanged = true
						
					elseif bIsStackAmountDecreased == true then
						local iStackAmountChange = math.abs(iStackAmountChange)
						--local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_CHANGE_DESC', iStackAmountChange, 'LOC_HENNO_CITY_ABILITY_SOURCE_DECREASE');
						--sMainString = sMainString..sStackString

						local sMainString = Locale.Lookup(mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].DecreasedDesc, sAmountText, iStackAmountChange);
						
						--local sDecreaseString = Locale.Lookup("LOC_HENNO_CITY_ABILITY_CHANGE_DECREASE")
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_DECREASED_CITY_QUARTER_ABILITY_SUMMARY", sCityName, sMainString);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						--notificationData.AutoActivate = true;
					
						sNotificationType = "NOTIFICATION_CSC_" .. mCSC_AbilityEffectModifiers[sAbilityEffectModifierId].Quarter .. "_EFFECT_DECREASED"
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bCSC_AbilitiesHaveChanged = true
						
					end
				end

--[[				local iCityCurrentSpecialistModifiers = tableLength(tCityCurrentSpecialistModifiers)

				for sSpecialistGrantModifierId,v in pairs(tCityCurrentSpecialistModifiers) do
					local bIsNewSpecialistModifier = false

					if tCSC_CitiesSpecialistsCache == nil then
						tCSC_CitiesSpecialistsCache = {}
					end

					if tCSC_CitiesSpecialistsCache[iCityID] == nil then
						tCSC_CitiesSpecialistsCache[iCityID] = {}
					end

					local tCachedSpecialistsModifier = tCSC_CitiesSpecialistsCache[iCityID][sSpecialistGrantModifierId]
					if not tCachedSpecialistsModifier then
						bIsNewSpecialistModifier = true
					end

					if bIsNewSpecialistModifier == true then
						local sSpecialistName = Locale.Lookup(mCSC_SpecialistGrantModifiers[sSpecialistGrantModifierId].GrantDesc);
						
						local notificationData = {}
						notificationData[ParameterTypes.MESSAGE] = Locale.Lookup("LOC_NOTIFICATION_HENNO_NEW_CITY_SPECIALIST_MESSAGE");
						notificationData[ParameterTypes.SUMMARY] = Locale.Lookup("LOC_NOTIFICATION_HENNO_NEW_CITY_SPECIALIST_SUMMARY", sCityName, sSpecialistName, iCityCurrentSpecialistModifiers);
						notificationData[ParameterTypes.LOCATION] = { x = iCityX, y = iCityY };
						notificationData.AlwaysUnique = true;
						
						sNotificationType = string.gsub(sSpecialistGrantModifierId, "^MOD_", "NOTIFICATION_")
						NotificationManager.SendNotification(iPlayerID, DB.MakeHash(sNotificationType), notificationData, iCityX, iCityY)
						bCSC_SpecialistsHaveChanged = true
					end
				end ]]
			end
		end
		
		-- Last step to do is to cache all Current Player's Cities' data into the game (so it's load/save compatible)
		-- for which we use WriteCustomData() function from Civ6Common.
		-- At the start of this script we used ReadCustomData() to get access to this Player's cached data, if there are any.
		if bCSC_AbilitiesHaveChanged == true then
			WriteCustomData(sCSC_CitiesAbilitiesStringKey, tCSC_CitiesAbilitiesCurrent);
		end

--[[		if bCSC_SpecialistsHaveChanged == true then
			WriteCustomData(sCSC_CitiesSpecialistsStringKey, tCSC_CitiesSpecialistsCurrent);
		end ]]
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
