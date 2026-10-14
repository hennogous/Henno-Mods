-- One optional More Lenses parent; its options panel selects the Quarter.
if g_ModLenses == nil and g_ModLensModalPanel == nil then return end
include("CSC_QuarterLensSupport")
local S = CSC_QuarterLensSupport
local quarters = {}
for _, quarter in pairs(S.Quarters) do table.insert(quarters, quarter) end
table.sort(quarters, function(a, b) return a.id < b.id end)

local parent = "ML_CSC_SUPPLY_CHAINS"

if #quarters == 0 then return end
if g_ModLenses ~= nil then
    g_ModLenses[parent] = {
        LensButtonText = "LOC_HUD_CSC_SUPPLY_CHAINS_LENS",
        LensButtonTooltip = "LOC_HUD_CSC_SUPPLY_CHAINS_LENS_TOOLTIP",
        SortOrder = 100,
        OnToggle = function() LuaEvents.CSC_SupplyChainsLens_OpenPanel() end,
        NonStandardFunction = function() LuaEvents.CSC_SupplyChainsLens_Refresh() end,
    }
end
if g_ModLensModalPanel ~= nil then
    g_ModLensModalPanel[parent] = S.GetLensLegend(quarters[1].id)
end
