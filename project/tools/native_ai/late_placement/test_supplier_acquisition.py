"""Exercise the live supplier policy's ownership, readiness and retirement gates.

The existing fixture deliberately gives player 3 team 9. Native traces establish
buying and assignment; these Lua tests establish bounded proposal behavior only.
"""
import importlib.util
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime

ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('supplier_fixture',
    ROOT/'project/tools/ai_workshop_bridge/ce_frontend/test_bakers_gameplay.py')
fixture=importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)


def runtime():
    vm=LuaRuntime();vm.execute(fixture.FIXTURE)
    vm.execute((ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_QuarterPlacement.lua').read_text(encoding='utf-8'))
    vm.execute('''
pasture.GetOwner=function()return -1 end
improvement=-1
chain={ready=true,supply={base={}},plot=Map.GetPlot(),city=city,
 profile=CSC_AI_QuarterPlacement.StageTwoProfiles()[1]}
-- Unowned prospective feasibility must be left to native row admission.
ImprovementBuilder.CanHaveImprovement=function()error('Ownership-sensitive Lua query used for future land')end
quote=40
ui={GetPlotPurchaseQuote=function(p,c,i)assert(p==3 and c==42 and i==101);return quote end}
function offers(limit)
 return CSC_AI_QuarterPlacement.SupplierAcquisitionOffers(Players[3],{chain},ui,limit or 14336)
end
''')
    return vm


class SupplierAcquisition(unittest.TestCase):
    def test_live_identity_modest_band_and_retirement_after_ownership(self):
        vm=runtime();vm.execute('''
local rows=offers();assert(#rows==1)
local r=rows[1]
assert(r.player==3 and r.city==42 and r.plot==101 and r.quarter==100)
assert(r.deltaQ8==26*256 and #r.improvements==2 and r.purchaseGold==40)
assert(offers(256)[1].deltaQ8==256)
pasture.GetOwner=function()return 3 end
assert(#offers()==0)
''')

    def test_unknown_quote_foreign_hidden_or_already_viable_supply_is_neutral(self):
        vm=runtime();vm.execute('''
quote=nil;assert(#offers()==0)
quote=-1;assert(#offers()==0)
quote=40;ui.GetPlotPurchaseQuote=function()error('Unavailable context')end;assert(#offers()==0)
ui.GetPlotPurchaseQuote=function()return 40 end
pasture.GetOwner=function()return 7 end;assert(#offers()==0)
pasture.GetOwner=function()return -1 end
PlayersVisibility[3].IsRevealed=function()return false end;assert(#offers()==0)
PlayersVisibility[3].IsRevealed=function()return true end
chain.supply.base={{working=false,ready=false}};assert(#offers()==0)
chain.supply.base={};chain.ready=false;assert(#offers()==0)
chain.ready=true;assert(#offers(0)==0)
''')

    def test_unlock_gate_and_shared_chain_deduplication(self):
        vm=runtime();vm.execute('''
GameInfo.Improvements[5].PrereqTech='TECH_FIXTURE'
GameInfo.Improvements[6].PrereqTech='TECH_FIXTURE'
GameInfo.Technologies={TECH_FIXTURE={Index=12}}
Players[3].GetTechs=function()return {HasTech=function()return false end}end
assert(#offers()==0)
Players[3].GetTechs=function()return {HasTech=function()return true end}end
local r=CSC_AI_QuarterPlacement.SupplierAcquisitionOffers(Players[3],{chain,chain},ui,14336)
assert(#r==1 and r[1].deltaQ8==6656)
''')

    def test_quote_then_plot_tie_break_does_not_depend_on_neighbor_order(self):
        vm=runtime();vm.execute('''
local other=setmetatable({GetIndex=function()return 102 end},{__index=pasture})
Map.GetAdjacentPlots=function()return {other,pasture}end
ui.GetPlotPurchaseQuote=function(p,c,index)return index==102 and 30 or 40 end
assert(offers()[1].plot==102)
ui.GetPlotPurchaseQuote=function()return 40 end
assert(offers()[1].plot==101)
''')


if __name__=='__main__':unittest.main()
