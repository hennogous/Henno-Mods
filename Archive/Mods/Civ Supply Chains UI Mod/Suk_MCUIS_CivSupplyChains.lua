--==========================================================================================================================
--<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
--==========================================================================================================================
-- Suk_MCUIS_CivSupplyChains UI Script
--==========================================================================================================================
print('Suk_MCUIS_CivSupplyChains UI Script Loaded!!!')

--==========================================================================================================================
-- CONSTANTS
--==========================================================================================================================
-- we faster processing, we cache all data in Henno_ValidCityModifiers in m_ValidCityModifiers to access them faster in this script
local m_ValidCityModifiers = {};
for row in GameInfo.Henno_ValidCityModifiers() do
	m_ValidCityModifiers[row.ModifierId] = {};
	m_ValidCityModifiers[row.ModifierId].AttachModifier = row.AttachedModifierId;
	m_ValidCityModifiers[row.ModifierId].ArgumentAmount = row.ArgumentAmount;
	m_ValidCityModifiers[row.ModifierId].Desc = row.ModifierDesc;
	m_ValidCityModifiers[row.ModifierId].Icon = row.ModifierIcon;
	m_ValidCityModifiers[row.ModifierId].IconTarget = row.ModifierIconTarget;
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
	else
		m_CityAttachedModifiers[v.AttachModifier].Desc = v.Desc
	end
	
	m_CityAttachedModifiers[v.AttachModifier].Icon = v.Icon
	m_CityAttachedModifiers[v.AttachModifier].IconTarget = v.IconTarget
end

--==========================================================================================================================
-- REGISTRATION
--==========================================================================================================================
-- Suk_MCUIS_RequestRegistration
-- This is run once when the script it loaded
-- Simply register the names you want with RegisterUnitIcon or RegisterCityIcon
--
-- If an MCUIS is civ specific for instance, you may not want to register the icon
-- if the local player leads a different civilization
--=================================================================================================================
function OnSuk_MCUIS_RequestRegistration(pRegistration)
	-- we want to create/preserve a City Icon for each AttachModifier in m_CityAttachedModifiers
	for sModifier,v in pairs(m_CityAttachedModifiers) do
		local sIconName = 'Henno_Civ_Supply_Chains_ActiveModifiers_'..sModifier
		pRegistration:RegisterCityIcon(sIconName)
	end
end
LuaEvents.Suk_MCUIS_RequestRegistration.Add(OnSuk_MCUIS_RequestRegistration)

--==========================================================================================================================
-- QUERY ICON
--==========================================================================================================================
-- Suk_MCUIS_QueryIcon
-- This is run whenever the MCUIS panel is refreshed
-- This is where you can set whether an instance should be generated for this icon
-- and basic info, if you're not trying to do anything particularly fancy
-- You can check info from the selected unit or city using UI.GetSelectedUnit() or UI.GetHeadSelectedCity() respectively
-- the data is then showin with pIcon:SetIconData (bMake, bRequest, sDescription, sIcon, iX, iY, iIndex)
----- bMake refers to whether the instance should be generated (false means no icon)
----- bRequest controls whether LuaEvent.Suk_MCUIS_RequestedIcon should be called for advanced control, it is false by default (and unless you need a clickable button it is best left as false)
----- sDescription is jus the tooltip
----- sIcon is just the icon 
----- iX and iY is if you need texture offfset coordinates from the texture file, like if its an atlas and shite, but y'know icons usually already have this by default (so its 0,0)
----- iIndex is the sort order, lower comes first, 20 seems like a good default if its secondary information.
--=================================================================================================================
function OnSuk_MCUIS_QueryIcon(sContext, sName, pIcon)
	
	-- we check if this Icon is one we preserved earlier, by checking if its sName contains 'Henno_Civ_Supply_Chains_ActiveModifiers_'
	local bIconExists = string.find(sName, "Henno_Civ_Supply_Chains_ActiveModifiers_")
	if sContext == "City" and bIconExists then
		
		-- Checking if we actual have a selected City
		pCity = UI.GetHeadSelectedCity()
		if not pCity then return end
		
		-- let's hide this Icon for the moment, and only allow script to show it if we can
		pIcon:SetIconData(false, false, '', "ICON_BUILDING_MONUMENT", nil, nil, 20)
		
		local tCityModifiers = {};
		local iPlayer	= pCity:GetOwner()
		
		-- we iterate through all modifiers in the Game, and collect all 'active and henno-valid' ones in the city
		local tModifiers = GameEffects.GetModifiers()
		for _, iModifier in pairs(tModifiers) do

			-- Now we check if the ModifierId is also listed as a City Modifier in 'm_ValidCityModifiers'
			local sModifier = GameEffects.GetModifierDefinition(iModifier).Id
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
							if sObjectTypeName == 'District' and info.City == pCity:GetID() and info.Owner == iPlayer  then
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
		
		-- Now we iterate through each City-Attached-Modifier in tCityModifiers, and check if the modifier matches this refreshing Icon
		-- If it does, we customzie its ToolTip Text and make its Icon visible
		local sMainString = ''
		local bEmptyString = true;
		for sAttachModifier,v in pairs(tCityModifiers) do
			local sTempIconName = 'Henno_Civ_Supply_Chains_ActiveModifiers_'..sAttachModifier
			if sTempIconName == sName then
				local iAmount = m_CityAttachedModifiers[sAttachModifier].Amount * v.StackAmount; -- we multiply this modifier's DB yield value by the StackAmount in this city to get the exact yield gain
				local sString = Locale.Lookup(m_CityAttachedModifiers[sAttachModifier].Desc, iAmount, v.StackAmount); -- string for this modifier's Ability
				-- local sStackString = Locale.Lookup('LOC_ZEGA_STACK_AMOUNT_DESC', v.StackAmount); -- string for the Stack Source Amount
				local sIcon = m_CityAttachedModifiers[sAttachModifier].Icon -- Icon to use for this modifier
				-- if Icon is nil then we use this Player's Civilization Icon instead, if we can't for some reason then we use the Monument Icon.
				if sIcon == nil then
					local pPlayerConfig = PlayerConfigurations[iPlayer];
					local sCivilizationType = pPlayerConfig:GetCivilizationTypeName();
					if sCivilizationType then
						sIcon = 'ICON_'..sCivilizationType
					else
						sIcon = 'ICON_BUILDING_MONUMENT'
					end
				end
				
				-- this is mostly useful for when we add new lines to the TT, but currently not needed.
				local sNewLine = ''
				if bEmptyString == false then
					sNewLine = '[NEWLINE]'
				end
				bEmptyString = false
				
				-- If iAmount is positive then we add a '+' sign at start of sString (bc it's not shown automatically), negative values will always have the '-' sign show up. 
				if iAmount > 0 then
					sMainString = sMainString..sNewLine..'+'..sString --..sStackString
				else
					sMainString = sMainString..sNewLine..sString --..sStackString
				end

				pIcon:SetIconData(true, true, sMainString, sIcon, nil, nil, 10)

			end
		end
		
	end
end

function OnSuk_MCUIS_RequestedIcon(sContext, sName, tInstance)
    if sContext == "City" and string.find(sName, "Henno_Civ_Supply_Chains_ActiveModifiers_") then
        local sAttachModifier = sName:gsub("Henno_Civ_Supply_Chains_ActiveModifiers_", "")
        local sIconTarget = m_CityAttachedModifiers[sAttachModifier].IconTarget
        if sIconTarget then
            tInstance.IconFrame:RegisterCallback(Mouse.eRClick, function()
                print("Opening Civilopedia for:", sIconTarget)
                LuaEvents.OpenCivilopedia(sIconTarget)
            end)
        end

        tInstance.OnResetting = function(tSelf)
            tSelf.IconFrame:ClearCallback(Mouse.eRClick)
            tSelf.OnResetting = nil
        end
    end
end

LuaEvents.Suk_MCUIS_RequestedIcon.Add(OnSuk_MCUIS_RequestedIcon)
LuaEvents.Suk_MCUIS_QueryIcon.Add(OnSuk_MCUIS_QueryIcon)
--==========================================================================================================================
--==========================================================================================================================