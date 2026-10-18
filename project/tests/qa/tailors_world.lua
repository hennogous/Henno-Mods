-- Disposable native-game fixture. Expected values are supplied by the Python
-- design matrix, never computed from CSC modifiers or encoded properties.
TQA=TQA or {};
local Q='DISTRICT_CSC_TAILORS_QUARTER';
function TQA.P(x,y) local p=Map.GetPlot(x,y); assert(p,'plot outside map'); return p; end
function TQA.C(name) local f=Game:GetProperty('CSC_TAILORS_QA'); assert(f and f.PlacementVersion==QAPlacement.Version,'QA_PLACEMENT_BLOCKED: unaudited historic fixture');assert(f.Cities[name],name); return Players[0]:GetCities():FindID(f.Cities[name]); end
function TQA.Site(name) local f=Game:GetProperty('CSC_TAILORS_QA'); assert(f and f.PlacementVersion==QAPlacement.Version,'QA_PLACEMENT_BLOCKED: unaudited historic fixture');assert(f.Sites[name],name); return Map.GetPlotByIndex(f.Sites[name]); end
function TQA.Clean(p)
    QAPlacement.AssertLand(p);
    assert(p:GetDistrictType()==-1 and p:GetResourceType()==-1 and p:GetImprovementType()==-1 and p:GetFeatureType()==-1,
        'QA_PLACEMENT_BLOCKED: preserve existing map content; select another site');
end
function TQA.Store(f) Game:SetProperty('CSC_TAILORS_QA',f); end
function TQA.City()
    error('QA_PLACEMENT_BLOCKED: fixed-coordinate debug cities retired; found cities through native settlement');
end
function TQA.District(site,cityName,kind,x,y)
    local f=Game:GetProperty('CSC_TAILORS_QA');local city=TQA.C(cityName);local p=TQA.P(x,y);
    local legal,reason=QAPlacement.DistrictAllowed(p,city,kind,3);
    assert(legal,'QA_PLACEMENT_BLOCKED: '..tostring(reason));
    city:GetBuildQueue():CreateIncompleteDistrict(GameInfo.Districts[kind].Index,p:GetIndex(),100);
    assert(p:GetDistrictType()==GameInfo.Districts[kind].Index,'district not created '..site);
    f.Sites[site]=p:GetIndex();f.SiteCities[site]=cityName;TQA.Store(f);return p;
end
function TQA.Add(site,kind)
    local f=Game:GetProperty('CSC_TAILORS_QA');local city=TQA.C(f.SiteCities[site]);local p=TQA.Site(site);
    local b=GameInfo.Buildings[kind];assert(b,'missing '..kind);
    city:GetBuildQueue():CreateBuilding(b.Index,p:GetIndex());
    assert(city:GetBuildings():HasBuilding(b.Index),'building not created '..kind);
end
function TQA.Remove(city,kind) TQA.C(city):GetBuildings():RemoveBuilding(GameInfo.Buildings[kind].Index); end
function TQA.Pop(city,n) local c=TQA.C(city);c:ChangePopulation(n-c:GetPopulation());assert(c:GetPopulation()==n);end
function TQA.Civic(kind,yes) Players[0]:GetCulture():SetCivic(GameInfo.Civics[kind].Index,yes);end
function TQA.Tech(kind,yes) Players[0]:GetTechs():SetTech(GameInfo.Technologies[kind].Index,yes);end
function TQA.Resource(site,kind,improvement)
    local p=TQA.Site(site);QAPlacement.AssertLand(p);
    assert(p:GetOwner()==0 and p:GetDistrictType()==-1,'QA_PLACEMENT_BLOCKED: owned, vacant material plot required');
    local oldResource=p:GetResourceType();local oldImprovement=p:GetImprovementType();
    if not kind then
        if oldImprovement>=0 then ImprovementBuilder.SetImprovementType(p,-1,0);end;
        ResourceBuilder.SetResourceType(p,-1);return;
    end;
    local resource=assert(GameInfo.Resources[kind],'unknown resource');
    assert(oldResource==-1 or oldResource==resource.Index,'QA_PLACEMENT_BLOCKED: choose a new candidate for a different resource');
    local added=false;
    if oldResource==-1 then
        assert(type(ResourceBuilder.CanHaveResource)=='function','QA_PLACEMENT_BLOCKED: resource feasibility API unavailable');
        assert(ResourceBuilder.CanHaveResource(p,resource.Index),'QA_PLACEMENT_BLOCKED: resource does not fit native terrain/features');
        ResourceBuilder.SetResourceType(p,resource.Index,1);added=true;
    end;
    local target=improvement and assert(GameInfo.Improvements[improvement],'unknown improvement').Index or -1;
    if target>=0 and target~=oldImprovement then
        local ok,legal=pcall(function()
            assert(type(ImprovementBuilder.CanHaveImprovement)=='function','native improvement feasibility API unavailable');
            return ImprovementBuilder.CanHaveImprovement(p,target,Players[0]:GetTeam());
        end);
        if not ok or not legal then
            if added then ResourceBuilder.SetResourceType(p,-1);end;
            error('QA_PLACEMENT_BLOCKED: native improvement rejected: '..tostring(legal));
        end;
    end;
    if target~=oldImprovement then
        if oldImprovement>=0 then ImprovementBuilder.SetImprovementType(p,-1,0);end;
        if target>=0 then ImprovementBuilder.SetImprovementType(p,target,0);end;
    end;
    print('QA_MATERIAL_PLACEMENT',p:GetIndex(),p:GetTerrainType(),p:GetFeatureType(),kind,improvement);
end
function TQA.ResourceSite(site,city,p)
    QAPlacement.AssertLand(p);
    assert(p:GetDistrictType()==-1 and p:GetOwner()==0,'QA_PLACEMENT_BLOCKED: owned material site required');
    local ownerCity=Cities.GetPlotPurchaseCity(p);
    assert(ownerCity and ownerCity:GetID()==TQA.C(city):GetID(),'QA_PLACEMENT_BLOCKED: wrong owning city');
    local f=Game:GetProperty('CSC_TAILORS_QA');
    f.Sites[site]=p:GetIndex();f.SiteCities[site]=city;TQA.Store(f);
end
function TQA.Setup()
    error('QA_PLACEMENT_BLOCKED: retired fixed-coordinate world; use terrain-aware candidate planning');
end
function TQA.PrintNative(cityName)
    local c=TQA.C(cityName);
    for _,kind in ipairs({'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','BUILDING_CSC_TAILORS_TAILOR','BUILDING_CSC_TAILORS_FASHION_HOUSE','BUILDING_AMPHITHEATER','BUILDING_MARKET','BUILDING_TEMPLE'}) do
        if c:GetBuildings():HasBuilding(GameInfo.Buildings[kind].Index) then
            for _,yield in ipairs({'YIELD_CULTURE','YIELD_PRODUCTION','YIELD_GOLD'}) do
                local ok,value=pcall(function() return c:GetBuildingYield(GameInfo.Buildings[kind].Index,yield);end);
                print('TQA_BUILDING_YIELD',cityName,kind,yield,ok,value);
            end
        end
    end
    for y in GameInfo.Yields() do local ok,value=pcall(function() return c:GetYield(y.Index);end);print('TQA_CITY_YIELD',cityName,y.YieldType,ok,value);end
    local d=c:GetDistricts();for i=0,d:GetNumDistricts()-1 do local v=d:GetDistrictByIndex(i);print('TQA_DISTRICT',cityName,GameInfo.Districts[v:GetType()].DistrictType,v:GetX(),v:GetY(),v:GetYield(GameInfo.Yields.YIELD_PRODUCTION.Index));end
end
function TQA.Equal(label,actual,expected,tolerance)
    print('TQA_ASSERT',label,'actual',actual,'expected',expected);
    assert(type(actual)=='number' and math.abs(actual-expected)<(tolerance or .001),label..': expected '..tostring(expected)..', observed '..tostring(actual));
end
function TQA.BY(city,building,yield) return TQA.C(city):GetBuildingYield(GameInfo.Buildings[building].Index,yield);end
function TQA.PY(site,yield) return TQA.Site(site):GetYield(GameInfo.Yields[yield].Index);end
function TQA.Raw(city,yield)
    local c=TQA.C(city); local modifier=c:GetGrowth():GetHappinessNonFoodYieldModifier();
    local value=c:GetYield(GameInfo.Yields[yield].Index);
    return value/(1+modifier/100);
end
function TQA.Has(city,building) return TQA.C(city):GetBuildings():HasBuilding(GameInfo.Buildings[building].Index);end
function TQA.Pillage(city,building,yes) TQA.C(city):GetBuildings():SetPillaged(GameInfo.Buildings[building].Index,yes);end
function TQA.GPP(kind) return Players[0]:GetGreatPeoplePoints():GetPointsPerTurn(GameInfo.GreatPersonClasses[kind].Index);end
function TQA.Tour(site) return Players[0]:GetCulture():GetTourismAt(TQA.Site(site):GetIndex());end
function TQA.Slots(city,site)
    local params={};params[CityCommandTypes.PARAM_MANAGE_CITIZEN]=true;
    local data=CityManager.GetCommandTargets(TQA.C(city),CityCommandTypes.MANAGE,params);
    assert(data,'No citizen command targets');
    for i,plot in pairs(data[CityCommandResults.PLOTS] or {}) do
        if plot==TQA.Site(site):GetIndex() then return data[CityCommandResults.MAX_CITIZENS][i],data[CityCommandResults.CITIZENS][i];end
    end
    return 0,0;
end
function TQA.Service(city,kind,present)
    local actual=TQA.Has(city,kind);print('TQA_SERVICE',city,kind,actual,present);assert(actual==present,'Service presence '..kind);
end
