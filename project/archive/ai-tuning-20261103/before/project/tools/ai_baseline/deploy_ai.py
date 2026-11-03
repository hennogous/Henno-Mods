"""Deploy only CSC_AI.sql and its SDK-generated manifest action.

Reuse the existing focused delta deployer. It backs up the manifest, preserves
unrelated installed files/actions and records the before/after file inventory.
Run with Civ closed, and provide explicit --installed and --output paths.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'map_lab'))
import deploy_material_map

if __name__ == '__main__':
    deploy_material_map.FILES = [
        'Data/CSC_AI.sql', 'Text/CSC_AI_TEXT.sql',
        'Lua_UI/AI/CSC_AI_UIFilter.lua', 'Lua_UI/AI/ToolTipLoader_CSC_AI.lua',
        'Lua_UI/AI/CivilopediaPage_CSC_AI.lua', 'Lua_UI/AI/CSC_AI_ReportScreen.lua',
        'Lua_UI/TradeRoutes/UnitPanel.lua',
        'Lua_UI/Lenses/PlotInfo_CSC_QuarterPlacement.lua',
        'Lua_UI/WonderServices/CSC_WonderServicePlotTooltip_Base.lua',
        'Lua_UI/WonderServices/CSC_WonderServicePlotTooltip_Suk.lua',
    ]
    deploy_material_map.ACTION_IDS = {'CSC_AI', 'CSC_AI_UI', 'CSC_AI_ReportScreen', 'CSC_AI_Text', 'CSC_UnitPanelTradeRouteSupport'}
    deploy_material_map.REMOVE_ACTION_IDS = {'CSC_AI_MaterialMarkers'}
    deploy_material_map.REMOVE_FILES = {'Lua_UI/AI/CSC_AI_MaterialMarkers.lua'}
    deploy_material_map.main()
