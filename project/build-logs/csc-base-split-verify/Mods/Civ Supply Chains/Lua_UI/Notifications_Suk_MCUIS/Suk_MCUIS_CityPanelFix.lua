--==========================================================================================================================
-- Suk_MCUIS_CityPanelFix
-- Fixes MCUIS city panel positioning when WoodBacking doesn't exist.
-- If another UI mod provides WoodBacking, preserve Suk's normal behavior.
--==========================================================================================================================
print('[MCUIS_FIX] CityPanel fix script loaded')

local CITY_PANEL_WOOD_BACKING_PATH = "/InGame/CityPanel/WoodBacking"
local CITY_PANEL_MAIN_PANEL_PATH = "/InGame/CityPanel/MainPanel"

local function SortMCUISCityPanel(pParent_City, pChild_City)
	if not pParent_City or not pChild_City or not pParent_City.SortChildren then
		return
	end

	pParent_City:SortChildren(
		function(pA, pB)
			if pA == pChild_City then
				return true
			elseif pB == pChild_City then
				return false
			else
				return false
			end
		end
	)
end

local function OnMCUISFix_LoadScreenClose()
	local pChild_City = Controls.MCUIS_CityPanel and Controls.MCUIS_CityPanel.Root
	if not pChild_City then
		print('[MCUIS_FIX] FAILED: MCUIS_CityPanel.Root not found')
		return
	end

	local pWoodBacking = ContextPtr:LookUpControl(CITY_PANEL_WOOD_BACKING_PATH)
	if pWoodBacking then
		-- Simple UI and similar CityPanel replacements provide the structure Suk expects.
		-- Restore that parent if needed, then otherwise stay out of the way.
		if pChild_City:GetParent() ~= pWoodBacking then
			pChild_City:ChangeParent(pWoodBacking)
			print('[MCUIS_FIX] Restored MCUIS CityPanel to WoodBacking')
		else
			print('[MCUIS_FIX] WoodBacking found; native MCUIS parent is already available')
		end
		SortMCUISCityPanel(pWoodBacking, pChild_City)
		return
	end

	local pParent_City = ContextPtr:LookUpControl(CITY_PANEL_MAIN_PANEL_PATH)
	if not pParent_City then
		print('[MCUIS_FIX] FAILED: Neither WoodBacking nor MainPanel found')
		return
	end

	local currentParent = pChild_City:GetParent()
	if currentParent == pParent_City then
		print('[MCUIS_FIX] MainPanel fallback already parented')
		SortMCUISCityPanel(pParent_City, pChild_City)
		return
	end

	pChild_City:ChangeParent(pParent_City)
	SortMCUISCityPanel(pParent_City, pChild_City)
	print('[MCUIS_FIX] Applied MainPanel fallback for MCUIS CityPanel')
end

-- Register to fire after LoadScreenClose (MCUIS's retry also fires here)
Events.LoadScreenClose.Add(OnMCUISFix_LoadScreenClose)
print('[MCUIS_FIX] LoadScreenClose handler registered')
