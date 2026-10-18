-- Independent oracle: Tailors gains +1 Production per adjacent owned Base or
-- Specialty resource. No CSC count function or encoded amount supplies expectations.
-- Only fixture creation mutates a turn-1 game; recheck merely reads saved state.
local KEY='CSC_QA_MATERIAL_FIXTURE';
local function districtAt(city,x,y)
    local districts=city:GetDistricts();
    for i=0,districts:GetNumDistricts()-1 do
        local district=districts:GetDistrictByIndex(i);
        if district:GetX()==x and district:GetY()==y then return district; end
    end
end
local function fixture()
    local f=Game:GetProperty(KEY); assert(f and f.PlacementVersion==QAPlacement.Version,'QA_PLACEMENT_BLOCKED: missing or unaudited fixture');
    local city=Players[f.PlayerID]:GetCities():FindID(f.CityID);
    assert(city,'QA city missing');
    local district=districtAt(city,f.X,f.Y);
    assert(district and district:GetType()==GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index,'QA district missing');
    return f,city,district;
end
function CSC_QA_CreateMaterials()
    assert(Game.GetCurrentGameTurn()==1,'Use a fresh disposable turn-1 game');
    assert(not Game:GetProperty(KEY),'Fixture already exists; use recheck instead');
    local player=Players[0];local city=nil;
    assert(player:GetCities():GetCount()==1,'normally founded capital required');
    for _,c in player:GetCities():Members() do city=c;break;end;
    player:GetCulture():SetCivic(GameInfo.Civics.CIVIC_CRAFTSMANSHIP.Index,true);
    local base={Tag='CLASS_CSC_TAILORS_BASE',Improvements={'IMPROVEMENT_FARM','IMPROVEMENT_PLANTATION','IMPROVEMENT_PASTURE'}};
    local request={Player=0,District='DISTRICT_CSC_TAILORS_QUARTER',Slots={base,base,
        {Tag='CLASS_CSC_TAILORS_SPEC',Improvements={'IMPROVEMENT_PLANTATION','IMPROVEMENT_MINE'}}}};
    local plan=QAPlacement.Find(request);
    assert(#plan.Candidates>0,'QA_PLACEMENT_BLOCKED: no viable two-Base/one-Specialty layout');
    local chosen=plan.Candidates[1];assert(QAPlacement.Recheck(request,chosen));
    local quarter=Map.GetPlotByIndex(chosen.Quarter.Plot);
    local slots={};local resources={};
    for i,material in ipairs(chosen.Materials) do
        local p=Map.GetPlotByIndex(material.Plot);
        assert(p:GetImprovementType()==-1,'QA_PLACEMENT_BLOCKED: adjacency lifecycle needs unimproved resources');
        slots[i]=material.Plot;resources[i]=material.Resource;
    end;
    city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index,quarter:GetIndex(),100);
    -- Valid resource removal supplies the zero baseline; terrain/features stay intact.
    for _,index in ipairs(slots) do ResourceBuilder.SetResourceType(Map.GetPlotByIndex(index),-1);end;
    CSC_RefreshAdjacencies(); -- setup only; subsequent mutations rely on real events.
    local district=districtAt(city,quarter:GetX(),quarter:GetY());
    assert(district and district:IsComplete(),'Quarter creation incomplete');
    local f={PlacementVersion=QAPlacement.Version,PlacementPlan=chosen,PlayerID=0,CityID=city:GetID(),X=quarter:GetX(),Y=quarter:GetY(),
             Slots={slots[1],slots[2],slots[3]},Resources=resources,
             Baseline=district:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index)};
    Game:SetProperty(KEY,f);
    print('CSC_QA_FIXTURE',f.CityID,quarter:GetIndex(),f.Baseline);
end
function CSC_QA_Resource(slot,present)
    local f=fixture(); local p=Map.GetPlotByIndex(f.Slots[slot]);
    if present then assert(ResourceBuilder.CanHaveResource(p,GameInfo.Resources[f.Resources[slot]].Index),'QA_PLACEMENT_BLOCKED: resource terrain check failed');end;
    ResourceBuilder.SetResourceType(p,present and GameInfo.Resources[f.Resources[slot]].Index or -1,1);
    assert(p:GetResourceType()==(present and GameInfo.Resources[f.Resources[slot]].Index or -1),'Resource mutation failed');
end
function CSC_QA_Owner(owned)
    local f,city=fixture(); local p=Map.GetPlotByIndex(f.Slots[1]);
    if owned then WorldBuilder.CityManager():SetPlotOwner(p:GetX(),p:GetY(),f.PlayerID,city:GetID());
    else WorldBuilder.CityManager():SetPlotOwner(p:GetX(),p:GetY(),false); end
    assert(p:GetOwner()==(owned and f.PlayerID or -1),'Ownership mutation failed');
end
function CSC_QA_AssertMaterials(expected)
    local f,city,district=fixture();
    local actual=district:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index)-f.Baseline;
    print('CSC_QA_NATIVE_PRODUCTION',expected,actual,'turn',Game.GetCurrentGameTurn());
    assert(math.abs(actual-expected)<0.001,'Native Production: expected '..expected..', actual '..actual);
end
