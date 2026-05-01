--==========================================================================================================================
-- Suk_MCUIS_CityPanelFix
-- Fixes MCUIS city panel positioning when WoodBacking doesn't exist (Civ 6 UI update broke the path)
-- This runs after MCUIS initialization and re-parents the panel to the correct element.
--==========================================================================================================================
print('[MCUIS_FIX] CityPanel fix script loaded')

function OnMCUISFix_LoadScreenClose()
	local m_CityPanelBackingPath = "/InGame/CityPanel/MainPanel"
	local pParent_City = ContextPtr:LookUpControl(m_CityPanelBackingPath)
	
	if not pParent_City then
		print('[MCUIS_FIX] MainPanel not found, trying WoodBacking...')
		m_CityPanelBackingPath = "/InGame/CityPanel/WoodBacking"
		pParent_City = ContextPtr:LookUpControl(m_CityPanelBackingPath)
	end
	
	if not pParent_City then
		print('[MCUIS_FIX] FAILED: Neither MainPanel nor WoodBacking found')
		return
	end
	
	local pChild_City = Controls.MCUIS_CityPanel and Controls.MCUIS_CityPanel.Root
	if not pChild_City then
		print('[MCUIS_FIX] FAILED: MCUIS_CityPanel.Root not found')
		return
	end
	
	-- Check if already parented correctly
	local currentParent = pChild_City:GetParent()
	if currentParent == pParent_City then
		print('[MCUIS_FIX] Already correctly parented')
		return
	end
	
	-- Re-parent to the correct element
	pChild_City:ChangeParent(pParent_City)
	print('[MCUIS_FIX] Successfully re-parented MCUIS CityPanel to ' .. m_CityPanelBackingPath)
end

-- Register to fire after LoadScreenClose (MCUIS's retry also fires here)
Events.LoadScreenClose.Add(OnMCUISFix_LoadScreenClose)
print('[MCUIS_FIX] LoadScreenClose handler registered')
