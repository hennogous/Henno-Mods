--==========================================================================================================================
--<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
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
	print('Zega OnSuk_MCUIS_RequestRegistration')
	pRegistration:RegisterCityIcon("Henno_City_Quarters_ActiveModifiers")
	--pRegistration:RegisterUnitIcon("Henno_Unit_Quarters_ActiveModifiers")
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
	--print('Zega OnSuk_MCUIS_QueryIcon 000', sContext, sName, pIcon)
	if sContext == "City" and sName == "Henno_City_Quarters_ActiveModifiers" then
		print('Zega OnSuk_MCUIS_QueryIcon 111')
		
		--print("We are trying to show the preserve icon now")
		-- All of this is just specific info getting for this icon
		pObject = UI.GetHeadSelectedCity()
		if not pObject then return end
		--
		
		
		
		
		
		local numBuildings = 5
		
		print('Henno_City_Quarters_ActiveModifiers', pObject, numBuildings)
		pIcon:SetIconData(true, false, "somethingsomething", "ICON_BUILDING_MONUMENT", nil, nil, 10)
		print('Success111!!!!')
		--pIcon:SetIconData(true, false, "This is an Advanced Iconooooooossssss", "ICON_IMPROVEMENT_ROCK_HEWN_CHURCH", nil, nil, 20)
		--print('Success222!!!!')
	end
end

LuaEvents.Suk_MCUIS_QueryIcon.Add(OnSuk_MCUIS_QueryIcon)
--==========================================================================================================================
--==========================================================================================================================