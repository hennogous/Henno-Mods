--==========================================================================================================================
--<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
--==========================================================================================================================
-- Suk_MCUIS_CSC UI Script
--==========================================================================================================================

print('Suk_MCUIS_CSC UI Script loaded!!!')

-- City-panel counterpart to CSC_UI_Notifications.lua: the same SQL registry
-- supplies effect identity, per-stack text and icons. This view displays current
-- active subjects; the notification script separately compares saved counts.

--==========================================================================================================================
-- CONSTANTS
--==========================================================================================================================
include("CSC_ServicePresentation")
local Presentation = CSC_ServicePresentation

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
	local iRegistered = 0
	-- Preserve a City Icon for every resolved effect in the shared SQL registry.
	for sModifier,v in pairs(Presentation.Effects) do
		local sIconName = 'CSC_ActiveModifiers_'..sModifier
		pRegistration:RegisterCityIcon(sIconName)
		iRegistered = iRegistered + 1
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
    if sContext ~= "City" or sName:sub(1, #"CSC_ActiveModifiers_") ~= "CSC_ActiveModifiers_" then return end
    local city = UI.GetHeadSelectedCity()
    if not city then return end
    pIcon:SetIconData(false, false, '', "ICON_BUILDING_MONUMENT", nil, nil, 20)
    local effectID = sName:sub(#"CSC_ActiveModifiers_" + 1)
    local current = Presentation.Collect(city:GetOwner(), city:GetID())[city:GetID()] or {}
    local effect = current[effectID]
    local data = effect and Presentation.Format(effectID, effect.count, city:GetOwner())
    if data then pIcon:SetIconData(true, true, data.tooltip, data.icon, nil, nil, 10) end
end

function OnSuk_MCUIS_RequestedIcon(sContext, sName, tInstance)
    if sContext == "City" and string.find(sName, "CSC_ActiveModifiers_") then
        local sAbilityEffectModifierId = sName:gsub("CSC_ActiveModifiers_", "")
        local row = Presentation.Effects[sAbilityEffectModifierId]
        local sIconTarget = row and row.AbilityIconTarget
        if sIconTarget then
            tInstance.IconFrame:RegisterCallback(Mouse.eRClick, function()
                print("Opening Civilopedia for:", sIconTarget)
                LuaEvents.OpenCivilopedia(sIconTarget)
            end)
        end

        -- MCUIS pools icon instances. Clear this callback before reuse so a later
        -- icon cannot inherit the previous Service's Civilopedia target.
        tInstance.OnResetting = function(tSelf)
            tSelf.IconFrame:ClearCallback(Mouse.eRClick)
            tSelf.OnResetting = nil
        end
    end
end

-- Helper for table counting
function table_count(t)
	local c = 0
	for _ in pairs(t) do c = c + 1 end
	return c
end

LuaEvents.Suk_MCUIS_RequestedIcon.Add(OnSuk_MCUIS_RequestedIcon)
LuaEvents.Suk_MCUIS_QueryIcon.Add(OnSuk_MCUIS_QueryIcon)
--==========================================================================================================================
--==========================================================================================================================
