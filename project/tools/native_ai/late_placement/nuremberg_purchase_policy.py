"""Source qualification and common ownership release for the 1.5 purchase test.

Only the explicit preparation mode clears one empty plot in an ephemeral loaded
game. It does not pay for/acquire land, alter treasury or provide shipping policy.
Ordinary main CSC supplies any later frontier bid; native Economic must execute
the actual paid purchase for the test to count.
"""
from pathlib import Path
from driver import load,sha

MAIN_FILES=tuple(Path('Lua_UI/AI')/name for name in ('CSC_AI_AdjacencyScan.lua',
    'CSC_AI_BakersGameplay.lua','CSC_AI_QuarterPlacement.lua','CSC_AI_DistrictBridge.lua'))+(
    Path('Lua_UI/Adjacencies/CSC_AdjacencyUI.lua'),)


def source_checkpoint(folder,home,world_sha,policy_root):
    """Require a normally closed inactive202 source, never a rotating save."""
    assert folder.is_dir(),'A verified paused Nuremberg run directory is required'
    assert load(folder/'complete.json')['verified'] and load(folder/'session-closed.json')['verified']
    origin=load(folder/'owned-comparison-source.json')
    assert origin['verified'] and origin['source_world_sha256']==world_sha
    assert (origin['player'],origin['city'],origin['plot'])==(3,458758,788)
    assert origin['main_policy_sha256']=={str(p):sha(policy_root/p)for p in MAIN_FILES}
    checkpoint=load(folder/'checkpoint.json')
    assert checkpoint['verified'] and checkpoint['turn']==202
    assert checkpoint['save_complete_event'] and checkpoint['native_phase_unchanged']
    for key in ('before','after'):
        phase=checkpoint[key]
        assert phase['turn']==202 and not phase['active'] and phase['local_player']==0 and phase['player0_human']
    native=Path(checkpoint['native_save']).resolve(strict=True)
    assert native.parent==(home/'Saves/Single').resolve()
    assert sha(native)==sha(Path(checkpoint['archive']))==checkpoint['sha256']
    return dict(path=str(native),sha256=checkpoint['sha256'],turn=202)


PREPARE_RELEASE=r'''
assert(Game.GetCurrentGameTurn()==202 and Players[0]:IsHuman() and not AutoplayManager.IsActive())
local player=assert(Players[3]);assert(not player:IsHuman())
local original=Game:GetProperty('CSC_AI_OriginalHuman_3');assert(original==0)
local city=assert(CityManager.GetCity(3,458758));assert(city:GetName()=='LOC_CITY_NAME_NUREMBERG')
local site=assert(Map.GetPlotByIndex(788));local owner=assert(Cities.GetPlotPurchaseCity(site))
assert(site:GetOwner()==3 and owner:GetID()==458758 and site:GetDistrictType()==-1)
print('CSC_NUREMBERG_RELEASE_ELIGIBILITY',788,site:GetResourceType(),site:GetImprovementType(),site:GetTerrainType(),site:GetFeatureType())
assert(site:GetResourceType()==-1 and site:GetImprovementType()==-1)
local center=assert(Map.GetPlot(city:GetX(),city:GetY()));assert(center:GetIndex()==787)
local profile
for _,p in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do if p.key=='BAKERS'then profile=p end end
assert(profile and not city:GetDistricts():HasDistrict(profile.district.Index))
local supplies=CSC_AI_QuarterPlacement.ReadSuppliers(player,site,profile)
assert(#supplies.base==1 and supplies.base[1].plot==861)
local host=assert(Map.GetPlotByIndex(713));local hostCity=assert(Cities.GetPlotPurchaseCity(host))
local commercial=assert(GameInfo.Districts.DISTRICT_COMMERCIAL_HUB)
assert(host:GetOwner()==3 and hostCity:GetID()==458758 and host:GetDistrictType()==-1 and host:GetResourceType()==-1)
assert(CSC_AI_FutureDistrictTypes(3,city)[commercial.Index] and host:CanHaveDistrict(commercial.Index,3,458758))
local before=CSC_AI_QuarterAdjacencyValue(profile.district.DistrictType,site,city,3,false,commercial.DistrictType)
assert(before.total==4)
local terrain,feature,rivers=site:GetTerrainType(),site:GetFeatureType(),site:GetRiverCrossingCount()
local gold=player:GetTreasury():GetGoldBalance()
local manager=WorldBuilder.CityManager();assert(type(manager.SetPlotOwner)=='function')
-- RE: Lua lSetPlotOwner5efe90 retains invalidCityID for a boolean following
-- the plot; manager608b60 / Apply607190 allow clearing an empty district plot.
-- This is a COMMON FIXTURE EDIT, never a native purchase or AI investment.
print('CSC_NUREMBERG_RELEASE_BEFORE',788,site:GetOwner(),owner:GetID(),gold,terrain,feature,rivers)
manager:SetPlotOwner(site:GetX(),site:GetY(),false)
assert(site:GetOwner()==-1 and not Cities.GetPlotPurchaseCity(site),'Plot was not fully released')
assert(site:GetDistrictType()==-1 and site:GetResourceType()==-1 and site:GetImprovementType()==-1)
assert(site:GetTerrainType()==terrain and site:GetFeatureType()==feature and site:GetRiverCrossingCount()==rivers)
assert(player:GetTreasury():GetGoldBalance()==gold,'Fixture edit changed treasury')
local after=CSC_AI_QuarterAdjacencyValue(profile.district.DistrictType,site,city,3,false,commercial.DistrictType)
local retained=CSC_AI_QuarterPlacement.ReadSuppliers(player,site,profile)
assert(after.total==4 and #retained.base==1 and retained.base[1].plot==861)
print('CSC_NUREMBERG_RELEASED',788,-1,gold,after.total)
'''
