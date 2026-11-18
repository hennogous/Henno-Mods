"""Active Service recipients, shared MCUIS presentation and camera-facing pins."""
from pathlib import Path
import xml.etree.ElementTree as ET


def test_service_markers(runtime, db):
    lua = runtime()
    lua.execute('''
        local s=CSC_QuarterLensSupport
        resetWorld(5,5)
        Locale={Lookup=function(s) return s end}
        for _,p in ipairs(world) do
            p.owner=0
            p.purchaseCity={GetID=function() return p.index+100 end}
        end
        entries={}
        for _,index in ipairs({0,1}) do
            entries[#entries+1]={index=index,quarterKey='BAKERS',category='SALE',
                readyStyle='SALE',outlineStyle='SALE',ready=true,
                color=UI.GetColorValue('COLOR_CSC_LENS_SALE_DISTRICT')}
        end
        effects={}
        GameEffects={
            GetModifiers=function() local ids={} for id in pairs(effects) do ids[#ids+1]=id end return ids end,
            GetModifierDefinition=function(id) return effects[id].definition end,
            GetModifierActive=function(id) return effects[id].active end,
            GetModifierSubjectCount=function(id) return #(effects[id].subjects or {}) end,
            GetModifierSubjects=function(id) return effects[id].subjects end,
            GetObjectType=function(subject) return subject.kind or 'District' end,
            GetObjectString=function(subject) return subject.text end,
        }
        function effect(id,anchor,active,subjects)
            effects[id]={definition={Id=anchor},active=active,subjects=subjects}
        end
        function subject(index,owner,city,kind)
            return {text='District: '..index..', Owner: '..(owner or 0)..', City: '..(city or index+100),kind=kind}
        end
        function check(key,expected)
            local plots=s.GetServicePlots(key,entries)
            assert(#plots==#expected,'Wrong number of functional service icons')
            for i,index in ipairs(expected) do assert(plots[i]==index) end
        end
        -- Readiness, a persistent Service grant or a city art flag alone never
        -- invents a working service. Only active benefit anchors qualify.
        check('BAKERS',{})
        effect(1,'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY',true,{subject(0)})
        check('BAKERS',{})
        effects={}
        effect(1,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(0)})
        check('BAKERS',{0});check('TAILORS',{})
        effects[1].active=false;check('BAKERS',{}) -- Any failed gameplay gate.
        effects[1].active=true;effects[1].subjects={};check('BAKERS',{})
        effects[1].subjects={subject(0,1),subject(0,0,999),subject(0,0,100,'City'),
            {text='Owner: 0, City: 100'},{text='invalid'}}
        check('BAKERS',{})
        effects[1].subjects={subject(0),subject(0),subject(1)}
        effect(2,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',true,{subject(0)})
        check('BAKERS',{0,1}) -- Two producers/duplicates still one icon per plot.
        world[1].owner=1;check('BAKERS',{1});world[1].owner=0
        entries[1].readyStyle=nil;check('BAKERS',{1});entries[1].readyStyle='SALE'
        local filtered={entries[2]};assert(#s.GetServicePlots('BAKERS',filtered)==1)
        entries[1].category='QUARTER';check('BAKERS',{1});entries[1].category='SALE'
        effects[3]={active=true,subjects={subject(0)}} -- Unresolved native definition.
        check('BAKERS',{0,1})

        -- Every actual registered Service, including the three Wonder anchors,
        -- uses the same exact-recipient reader without a copied gate algorithm.
        for row in GameInfo.CSC_AbilityAttachModifiers() do
            if row.AbilityIconTarget and row.AbilityIconTarget:find('_SERVICE',1,true) then
                effects={}
                effect(1,row.ModifierId,true,{subject(0)})
                check(row.NotificationQuarter,{0})
                check(row.NotificationQuarter=='BAKERS' and 'TAILORS' or 'BAKERS',{})
            end
        end
        effects={}
        effect(1,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(0)})
        ExposedMembers={}
        local _,stats=s.DrawOverlay('Lens',entries)
        assert(stats.services==1 and stats.servicesAvailable)
        assert(outlines.CSC_QuarterLens_Services==nil) -- Retired flat sprites.
        assert(ExposedMembers.CSC_QuarterServicePins.Lens.markers[1].icon ==
            'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE')
        local cached=s.PrepareOverlay(entries)
        s.DrawPreparedOverlay('Lens',cached)
        s.DrawOverlay('Lens',{})
        assert(#ExposedMembers.CSC_QuarterServicePins.Lens.markers==0)
        s.DrawPreparedOverlay('Lens',cached)
        assert(#ExposedMembers.CSC_QuarterServicePins.Lens.markers==1)
        s.DrawOverlay('Placement',entries)
        assert(ExposedMembers.CSC_QuarterServicePins.Placement==nil)
        effects[1].active=false;s.DrawOverlay('Lens',entries)
        assert(#ExposedMembers.CSC_QuarterServicePins.Lens.markers==0)
        s.ClearOverlay('Placement');assert(ExposedMembers.CSC_QuarterServicePins.Placement==nil)
        effects[1].active=true;s.DrawOverlay('Lens',entries)
        for _,entry in ipairs(entries) do entry.quarterKey='TAILORS' end
        s.DrawOverlay('Lens',entries)
        assert(#ExposedMembers.CSC_QuarterServicePins.Lens.markers==0)
        s.ClearOverlay('Lens')
        local api=GameEffects;GameEffects=nil;check('BAKERS',{});GameEffects=api
        missingArt=true;s.DrawOverlay('Lens',entries);s.ClearOverlay('Lens');missingArt=false
    ''')
    test_pin_controls(lua)
    test_quarter_tooltip(runtime)
    assert db.execute("SELECT COUNT(*) FROM CSC_AbilityAttachModifiers").fetchone()[0] >= 11
    print('Passed Service pins: active recipients, snapshot restoration, MCUIS tooltip, right-click target, hover glow, grouping, static-only placement, and teardown.')


def test_quarter_tooltip(runtime):
    lua = runtime()
    lua.execute('''
        include=function() end
        local function rows(list,key)
            local result={}
            for _,row in ipairs(list) do
                if key then result[row[key]]=row end
                if row.Index then result[row.Index]=row end
            end
            return setmetatable(result,{__call=function()
                local i=0
                return function() i=i+1;return list[i] end
            end})
        end
        local quarterType='DISTRICT_CSC_BAKERS_QUARTER'
        local bakery='BUILDING_CSC_BAKERS_BAKERY'
        local service='BUILDING_CSC_BAKERS_STAGE_3_SERVICE'
        local wrongStage='BUILDING_CSC_BAKERS_STAGE_2_SERVICE'
        local market='BUILDING_MARKET'
        local food,prod,gold='YIELD_FOOD','YIELD_PRODUCTION','YIELD_GOLD'
        local yields=rows({
            {Index=0,YieldType=food,IconString='[ICON_Food]',Name='Food'},
            {Index=1,YieldType=prod,IconString='[ICON_Production]',Name='Production'},
            {Index=2,YieldType=gold,IconString='[ICON_Gold]',Name='Gold'},
        },'YieldType')
        local prefix='MOD_CSC_BAKERS_'
        local source=prefix..'SALE'
        local marketRate=prefix..'BUYER_RATE'
        local sellerRate=prefix..'SELLER_RATE'
        local cityWide=prefix..'UNRELATED'
        local feed=prefix..'FEED'
        local inactive=prefix..'INACTIVE'
        local route=prefix..'EXPORT_BAKERY_GOLD'
        local routeImport=prefix..'IMPORT_CONSUMER_FOOD'
        local stage4=prefix..'STAGE_4_ZOO_CULTURE_RETURN_BIT_2'
        local payProd,payGold,payCustomer,payIndustry=prefix..'PAY_PROD',prefix..'PAY_GOLD',prefix..'PAY_CUSTOMER',prefix..'PAY_INDUSTRY'
        local materialWrapper,customerWrapper='MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER','MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER'
        local plotYield,buildingYield='MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS','MODIFIER_BUILDING_YIELD_CHANGE'
        local function argument(id,name,value)
            return {ModifierId=id,Name=name,Value=value}
        end
        GameInfo={
            Yields=yields,
            Districts=rows({
                {Index=1,DistrictType=quarterType,Name="Bakers' Quarter",Maintenance=1},
                {Index=2,DistrictType='DISTRICT_COMMERCIAL_HUB',Name='Commercial Hub'},
            },'DistrictType'),
            District_Adjacencies=rows({{DistrictType=quarterType,YieldChangeId='NATIVE_FOOD'}}),
            Adjacency_YieldChanges={NATIVE_FOOD={YieldType=food}},
            Buildings=rows({
                {Index=11,BuildingType=bakery,PrereqDistrict=quarterType,Maintenance=2,Entertainment=1},
                {Index=12,BuildingType=market},
                {Index=13,BuildingType=service,Name='Innkeeper'},
                {Index=14,BuildingType=wrongStage,Name='Storekeeper'},
                {Index=15,BuildingType='TEST_WONDER_SERVICE',Name='Stage Manager'},
            },'BuildingType'),
            BuildingModifiers=rows({{BuildingType=bakery,ModifierId=source},
                {BuildingType=bakery,ModifierId=payProd..'_ATTACH'},{BuildingType=bakery,ModifierId=payGold..'_ATTACH'},
                {BuildingType=bakery,ModifierId=payCustomer..'_ATTACH'},{BuildingType=bakery,ModifierId=payIndustry..'_ATTACH'}}),
            DynamicModifiers={
                ATTACH={EffectType='EFFECT_ATTACH_MODIFIER'},
                POP={EffectType='EFFECT_ADJUST_CITY_YIELD_PER_POPULATION'},
                BUILDING={EffectType='EFFECT_ADJUST_BUILDING_YIELD_CHANGE'},
                CITY={EffectType='EFFECT_ADJUST_CITY_YIELD_CHANGE'},
                [materialWrapper]={EffectType='EFFECT_ATTACH_MODIFIER'},
                [plotYield]={EffectType='EFFECT_ADJUST_PLOT_YIELD'},
            },
            Modifiers={
                [source]={ModifierType='ATTACH'},
                [marketRate]={ModifierType='POP',SubjectRequirementSetId='BUYER'},
                [sellerRate]={ModifierType='POP',SubjectRequirementSetId='SELLER'},
                [feed]={ModifierType='BUILDING'},[inactive]={ModifierType='BUILDING'},
                [cityWide]={ModifierType='CITY'},[route]={ModifierType='BUILDING'},
                [routeImport]={ModifierType='CITY'},
                [stage4]={ModifierType='BUILDING'},
                [payProd..'_ATTACH']={ModifierType=materialWrapper,SubjectRequirementSetId='MATERIAL'},
                [payGold..'_ATTACH']={ModifierType=materialWrapper,SubjectRequirementSetId='MATERIAL'},
                [payCustomer..'_ATTACH']={ModifierType=customerWrapper,SubjectRequirementSetId='CUSTOMER'},
                [payIndustry..'_ATTACH']={ModifierType=materialWrapper,SubjectRequirementSetId='INDUSTRY'},
                [payProd]={ModifierType=plotYield},[payGold]={ModifierType=plotYield},
                [payCustomer]={ModifierType=buildingYield},[payIndustry]={ModifierType=plotYield},
            },
            ModifierArguments=rows({
                argument(payProd..'_ATTACH','ModifierId',payProd),argument(payGold..'_ATTACH','ModifierId',payGold),
                argument(payCustomer..'_ATTACH','ModifierId',payCustomer),argument(payIndustry..'_ATTACH','ModifierId',payIndustry),
                argument(payProd,'YieldType',prod),argument(payProd,'Amount','1'),
                argument(payGold,'YieldType',gold),argument(payGold,'Amount','1'),
                argument(payCustomer,'BuildingType',market),argument(payCustomer,'YieldType',food),argument(payCustomer,'Amount','1'),
                argument(payIndustry,'YieldType',prod),argument(payIndustry,'Amount','1'),
            }),
            Requirements={
                ADJ={RequirementType='REQUIREMENT_PLOT_ADJACENT_TO_OWNER'},
                BASE={RequirementType='REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES'},
                SHOP={RequirementType='REQUIREMENT_CITY_HAS_BUILDING'},
                DISTRICT={RequirementType='REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES'},
                INDUSTRY={RequirementType='REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES'},
            },
            RequirementSets={
                MATERIAL={RequirementSetType='REQUIREMENTSET_TEST_ALL'},
                CUSTOMER={RequirementSetType='REQUIREMENTSET_TEST_ALL'},
                INDUSTRY={RequirementSetType='REQUIREMENTSET_TEST_ALL'},
            },
            Resources={[5]={Index=5,ResourceType='RESOURCE_WHEAT'}},
            Improvements={IMPROVEMENT_INDUSTRY={Index=11}},
            CSC_Stage3CustomerTransactions=rows({
                {SellerBuildingType=bakery,CustomerBuildingType=market,
                    SellerReturnAmountProperty='SELLER_PROP',CustomerYieldAmountProperty='BUYER_PROP'}
            }),
            RequirementArguments=rows({
                {Name='PropertyName',Value='BUYER_PROP_BIT_1',RequirementId='REQ_BUYER'},
                {Name='PropertyName',Value='SELLER_PROP_BIT_1',RequirementId='REQ_SELLER'},
                {Name='Tag',Value='CLASS_CSC_BAKERS_BASE',RequirementId='BASE'},
                {Name='BuildingType',Value=market,RequirementId='SHOP'},
                {Name='DistrictType',Value='DISTRICT_COMMERCIAL_HUB',RequirementId='DISTRICT'},
                {Name='ImprovementType',Value='IMPROVEMENT_INDUSTRY',RequirementId='INDUSTRY'},
            }),
            RequirementSetRequirements=rows({
                {RequirementId='REQ_BUYER',RequirementSetId='BUYER'},
                {RequirementId='REQ_SELLER',RequirementSetId='SELLER'},
                {RequirementId='ADJ',RequirementSetId='MATERIAL'},{RequirementId='BASE',RequirementSetId='MATERIAL'},
                {RequirementId='ADJ',RequirementSetId='CUSTOMER'},{RequirementId='SHOP',RequirementSetId='CUSTOMER'},
                {RequirementId='DISTRICT',RequirementSetId='CUSTOMER'},
                {RequirementId='ADJ',RequirementSetId='INDUSTRY'},{RequirementId='BASE',RequirementSetId='INDUSTRY'},
                {RequirementId='INDUSTRY',RequirementSetId='INDUSTRY'},
            }),
        }
        CSC_Adjacency={ByDistrict={
            [quarterType]={{ID='IN',ProvideType='SelfBonus',YieldType=prod},
                {ID='SALES',ProvideType='SelfBonus',YieldType=gold}},
            DISTRICT_COMMERCIAL_HUB={{ID='OUT',ProvideType='SelfBonus',YieldType=food,
                CustomAdjacentObject=quarterType,AdjacencyType='FROM_RINGS_CAO_DISTRICT'}},
        }}
        CSC_Adjacency.ResourceVisible=function() return true end
        CSC_Adjacency.HasTag=function(tag,resource) return tag=='CLASS_CSC_BAKERS_BASE' and resource=='RESOURCE_WHEAT' end
        local function city(id,pop,building,index)
            return {
                GetID=function() return id end,GetOwner=function() return 0 end,
                GetPopulation=function() return pop end,
                GetProperty=function(_,key)
                    if key=='CSC_BAKERS_BAKERY_SUPPLIED' then return 1 end
                    if id==1 and key=='CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE' then return 1 end
                    if id==1 and (key=='CSC_BAKERS_STAGE_3_EFFECT_HOUSING_ART' or key=='CSC_BAKERS_STAGE_2_EFFECT_GROWTH') then
                        return 1
                    end
                end,
                GetDistricts=function() return {
                    IsComplete=function() return true end,IsPillaged=function() return false end,
                    Members=function()
                        return ipairs({{GetX=function() return index end,GetY=function() return 0 end}})
                    end,
                } end,
                GetBuildings=function() return {
                    HasBuilding=function(_,b) return b==building end,
                    IsPillaged=function() return false end,
                    GetBuildingsAtLocation=function(_,p) return p==index and {building} or {} end,
                } end,
                GetTrade=function() return {GetOutgoingRoutes=function()
                    return id==3 and {{DestinationCityPlayer=0,DestinationCityID=1}} or {}
                end} end,
            }
        end
        local cities={city(1,4,11,0),city(2,10,12,1),city(3,3,11,2)}
        CityManager={GetCity=function(owner,id) return owner==0 and cities[id] end}
        local function plot(index,kind,props)
            return {
                GetIndex=function() return index end,GetX=function() return index end,GetY=function() return 0 end,
                GetDistrictType=function() return kind end,GetDistrictID=function() return 50+index end,
                GetOwner=function() return props.owner or 0 end,GetProperty=function(_,key) return props[key] end,
                GetImprovementType=function() return props.improvement or -1 end,
                GetResourceType=function() return props.resource or -1 end,
                IsImprovementPillaged=function() return props.pillaged==true end,
                GetWorkerCount=function() return 2 end,GetYield=function(_,i) return i==0 and 2 or 0 end,
                GetAdjacencyYield=function(_,owner,cityID,district,yield)
                    assert(owner==0 and district==1 and yield==0)
                    return index==0 and 1 or 0
                end,
            }
        end
        local plots={[0]=plot(0,1,{CSC_ADJ_IN_ENCODED_AMOUNT=2,CSC_ADJ_SALES_ENCODED_AMOUNT=4}),
            [1]=plot(1,2,{CSC_ADJ_OUT_TOTAL=2,CSC_ADJ_OUT_ENCODED_AMOUNT=2}),[2]=plot(2,1,{})}
        local farm=plot(3,-1,{improvement=10,resource=5})
        local industry=plot(4,-1,{improvement=11,resource=5})
        local pillaged=plot(5,-1,{improvement=10,resource=5,pillaged=true})
        local foreign=plot(6,-1,{improvement=10,resource=5,owner=1})
        local unimproved=plot(7,-1,{resource=5})
        Map={GetPlotByIndex=function(i) return plots[i] end,GetPlot=function(x,y) return plots[x] end,
            GetAdjacentPlots=function(x)
                if x==0 then return {plots[1],farm,industry,pillaged,foreign,unimproved} end
                return {plots[1]}
            end}
        Cities={GetPlotPurchaseCity=function(p) return cities[p:GetIndex()+1] end}
        -- The built-district read already includes the two CSC incoming yields.
        Players={[0]={GetDistricts=function()
            return {FindID=function() return {GetAdjacencyYield=function(_,i) return ({[0]=1,2,4})[i] end} end}
        end}}
        Game={GetLocalPlayer=function() return 0 end}
        Locale={Lookup=function(key,amount) return amount and key..' '..amount or key end}
        local effects={
            -- The lens resolved the active customer marker, but the tooltip's
            -- modifier scan cannot resolve the source as a Building object.
            {source,103,{102},{ModifierId='IGNORED_LEAF'}},
            {marketRate,102,{102},{Amount='0.105',YieldType=food}},
            -- The 10-pop customer creates 1.05 production. The 4-pop seller
            -- stores that as a .2625 native rate, not .105.
            {sellerRate,103,{103},{Amount='0.2625',YieldType=prod}},
            {feed,102,{103},{Amount='2',YieldType=food,BuildingType=bakery}},
            {inactive,102,{103},{Amount='8',YieldType=food,BuildingType=bakery}},
            {cityWide,103,{103},{Amount='99',YieldType=food}},
            {route,103,{103},{Amount='1',YieldType=gold,BuildingType=bakery}},
            {routeImport,104,{104},{Amount='1',YieldType=food}},
            {stage4,102,{102},{Amount='2',YieldType=gold,BuildingType=market}},
            -- Live leaf and wrapper join successfully. The map-based payment
            -- must still count this payment only once.
            {payProd..'_ATTACH',101,{103},{ModifierId=payProd}},
            {payProd,103,{103},{Amount='1',YieldType=prod}},
        }
        GameEffects={
            GetModifiers=function() return {1,2,3,4,5,6,7,8,9,10,11} end,
            GetModifierDefinition=function(i) return {Id=effects[i][1],Arguments=effects[i][4]} end,
            GetModifierOwner=function(i) return effects[i][2] end,
            GetModifierSubjects=function(i) return effects[i][3] end,
            GetModifierActive=function(i) return i~=5 end,
            GetObjectType=function(id) return id==101 and 'LOC_MODIFIER_OBJECT_BUILDING' or 'LOC_MODIFIER_OBJECT_DISTRICT' end,
            GetObjectString=function(id)
                local ids={[101]=1,[102]=2,[103]=1,[104]=3}
                return ('Owner: 0, City: %d, District: %d'):format(ids[id],49+ids[id])
            end,
        }
        tooltipSnapshot={links={
            {kind='SALE',source=0,target=1,stages={[3]=true,[4]=true}},
            {kind='SALE',source=2,target=1,stages={[3]=true}},
        },markers={
            {index=1,target=service,stage=3,icon='ICON_INNKEEPER'},
            {index=1,target=service,stage=3,icon='ICON_INNKEEPER'},
            {index=1,target=wrongStage,stage=2,icon='ICON_STOREKEEPER'},
        }}
        amenityFixture={cities=cities,effects=effects,plots=plots,bakery=bakery,routeImport=routeImport}
    ''')
    root = Path(__file__).resolve().parents[3]
    lua.execute((root / 'Civ Supply Chains/Lua_UI/Lenses/CSC_QuarterTooltip.lua').read_text())
    lua.execute('''
        local text=CSC_QuarterTooltip.Format(tooltipSnapshot,'BAKERS',0)
        assert(text:find("Bakers' Quarter",1,true),text)
        assert(text:find("2 [ICON_Food] Food[NEWLINE]2 [ICON_Production] Production[NEWLINE]4 [ICON_Gold] Gold",1,true),text)
        assert(text:find("4.5 [ICON_Food] Food[NEWLINE]4 [ICON_Production] Production[NEWLINE]5 [ICON_Gold] Gold",1,true),text)
        local _, serviceCount=text:gsub("%[ICON_Bullet%] Innkeeper","")
        assert(serviceCount==1 and not text:find("Storekeeper",1,true),text)
        assert(text:find("4 [ICON_Food] Food",1,true) and text:find("-3 [ICON_Gold] Gold",1,true),text)
        local other=CSC_QuarterTooltip.Format(tooltipSnapshot,'BAKERS',2)
        assert(not other:find("Innkeeper",1,true) and not other:find("1 [ICON_Production]",1,true),other)
        assert(other:find("1.5 [ICON_Food] Food",1,true) and not other:find("4 [ICON_Production]",1,true),other)
        tooltipSnapshot.markers={}
        local withoutService=CSC_QuarterTooltip.Format(tooltipSnapshot,'BAKERS',0)
        assert(not withoutService:find("Innkeeper",1,true),withoutService)
        local wonder={links=tooltipSnapshot.links,markers={
            {index=1,target='TEST_WONDER_SERVICE',stage=4,icon='ICON_STAGE_MANAGER',isWonder=true},
        }}
        local wonderText=CSC_QuarterTooltip.Format(wonder,'TAILORS',0)
        assert(wonderText:find("[ICON_Bullet] Stage Manager",1,true),wonderText)
        wonder.markers[1].isWonder=false
        local ordinaryText=CSC_QuarterTooltip.Format(wonder,'TAILORS',0)
        assert(not ordinaryText:find("Stage Manager",1,true),ordinaryText)

        local f=amenityFixture
        local function amenityCount(snapshot,index,expected)
            local result=CSC_QuarterTooltip.Format(snapshot,'BAKERS',index)
            assert(result:find('LOC_CSC_LENS_QUARTER_AMENITIES '..expected..'[NEWLINE]',1,true),result)
        end
        local function fresh() return {links=tooltipSnapshot.links,markers={}} end
        local amenity='MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY'
        local amenityBit=amenity..'_BIT_2'
        GameInfo.DynamicModifiers.AMENITY={EffectType='EFFECT_ADJUST_DISTRICT_EXTRA_ENTERTAINMENT'}
        GameInfo.Modifiers[amenity]={ModifierType='AMENITY'}
        GameInfo.Modifiers[amenityBit]={ModifierType='AMENITY'}
        f.effects[#f.effects+1]={amenity,104,{104},{Amount='1'}}
        f.effects[#f.effects+1]={amenityBit,104,{104},{Amount='2'}}
        GameEffects.GetModifiers=function()
            local ids={}; for i=1,#f.effects do ids[#ids+1]=i end; return ids
        end
        -- Base leaf plus bit 2 represents three routes, all supplied by plot 0.
        amenityCount(fresh(),0,'4')
        amenityCount(fresh(),2,'1')
        -- Two routes to one supplier and one to another must attribute 2:1,
        -- including the food leaves that use the same importer accounting.
        f.cities[3].GetTrade=function() return {GetOutgoingRoutes=function() return {
            {DestinationCityPlayer=0,DestinationCityID=1},
            {DestinationCityPlayer=0,DestinationCityID=1},
            {DestinationCityPlayer=0,DestinationCityID=3},
        } end} end
        amenityCount(fresh(),0,'3')
        amenityCount(fresh(),2,'2')
        GameEffects.GetModifierActive=function(i) return i~=5 and i~=#f.effects end
        local inactiveBits=fresh()
        amenityCount(inactiveBits,0,'1.6')
        amenityCount(inactiveBits,2,'1.3')

        -- Regional benefits are received once per building type and city.
        -- Sources equidistant from three recipients share three amenities.
        GameEffects=nil
        GameInfo.Buildings[f.bakery].RegionalRange=6
        for i,candidate in ipairs(f.cities) do
            candidate.regionalRange=0; candidate.regionalEntertainment=0
            candidate.GetX=function() return i-1 end
            candidate.GetY=function() return 0 end
            local buildings=candidate:GetBuildings()
            buildings.IsPillaged=function() return candidate.pillaged==true end
            candidate.GetBuildings=function() return buildings end
        end
        Players[0].GetDistricts=function() return {FindID=function(_,id)
            local candidate=f.cities[id-49]
            return {
                GetExtraRegionalRange=function() return candidate.regionalRange end,
                GetExtraRegionalEntertainment=function() return candidate.regionalEntertainment end,
            }
        end} end
        Players[0].GetCities=function() return {Members=function() return ipairs(f.cities) end} end
        Map.GetPlotDistance=function(x,y,u,v) return math.abs(x-u) end
        local regional=fresh()
        amenityCount(regional,0,'1.5')
        amenityCount(regional,2,'1.5')
        -- The regional scan is shared by Quarters in this lens snapshot.
        Players[0].GetCities=function() error('Regional recipients were rescanned') end
        amenityCount(regional,0,'1.5')
        Players[0].GetCities=function() return {Members=function() return ipairs(f.cities) end} end
        f.cities[2].GetX=function() return 10 end
        regional=fresh()
        amenityCount(regional,0,'1')
        amenityCount(regional,2,'1')
        -- Extra range reaches the city exactly eight tiles from supplier 2.
        f.cities[3].regionalRange=2
        regional=fresh()
        amenityCount(regional,0,'1')
        amenityCount(regional,2,'2')
        -- The strongest source wins. Pillaged sources supply no regional benefit.
        f.cities[3].regionalEntertainment=1
        regional=fresh()
        amenityCount(regional,0,'0')
        amenityCount(regional,2,'6')
        f.cities[3].pillaged=true
        regional=fresh()
        amenityCount(regional,0,'2')
        amenityCount(regional,2,'0')
        GameInfo.Buildings_XP2={[f.bakery]={EntertainmentBonusWithPower=2}}
        local fullyPowered=false
        f.cities[1].GetPower=function() return {
            IsFullyPowered=function() return fullyPowered end,
        } end
        amenityCount(fresh(),0,'2')
        fullyPowered=true
        amenityCount(fresh(),0,'6')
    ''')


def test_pin_controls(lua):
    root = Path(__file__).resolve().parents[3]
    lua.execute('''
        local function event()
            local callbacks={}
            return setmetatable({
                Add=function(fn) callbacks[#callbacks+1]=fn end,
                Remove=function(fn) for i=#callbacks,1,-1 do if callbacks[i]==fn then table.remove(callbacks,i) end end end,
                Count=function() return #callbacks end,
            }, {__call=function(_,...) for _,fn in ipairs({table.unpack(callbacks)}) do fn(...) end end})
        end
        local function events() return setmetatable({}, {__index=function(t,k) local e=event();rawset(t,k,e);return e end}) end
        Events=events();LuaEvents=events();Mouse={eLClick=1,eRClick=2,eMouseEnter=3}
        local realInclude=include
        include=function(name) if name~='InstanceManager' then realInclude(name) end end
        Controls={ServicePins={}}
        -- Native InGame.LoadNewContext passes isHidden=true for every added UI.
        -- Visible child instances cannot override their hidden context ancestor.
        contextHidden=true;contextParent=nil;nativeWorldView=nil
        ContextPtr={
            SetShutdown=function(_,fn) shutdown=fn end,
            SetInitHandler=function(_,fn) initializePins=fn end,
            LookUpControl=function(_,path) assert(path=='/InGame/WorldViewControls');return nativeWorldView end,
            ChangeParent=function(_,parent) contextParent=parent end,
            SetHide=function(_,hidden) contextHidden=hidden end,
        }
        pinCreates=0;pinReleases=0;pinCalls=0;pins={};pool={}
        local function control()
            return {
                SetWorldPositionVal=function(self,x,y,z) self.world={x,y,z};pinCalls=pinCalls+1 end,
                SetOffsetVal=function(self,x,y) self.offset={x,y};pinCalls=pinCalls+1 end,
                SetSizeVal=function(self,w,h) self.size={w,h};pinCalls=pinCalls+1 end,
                SetIcon=function(self,icon,size) self.icon=icon;self.size=size;pinCalls=pinCalls+1 end,
                SetTexture=function(self,x,y,texture)
                    self.texture=texture or x
                    self.textureOffset=texture and {x,y}
                    pinCalls=pinCalls+1
                end,
                SetAlpha=function(self,alpha) self.alpha=alpha;pinCalls=pinCalls+1 end,
                SetHide=function(self,hidden) self.hidden=hidden;pinCalls=pinCalls+1 end,
                SetToolTipString=function(self,text) self.tooltip=text;pinCalls=pinCalls+1 end,
                RegisterCallback=function(self,button,fn)
                    local field=({[Mouse.eLClick]='select',[Mouse.eRClick]='click',[Mouse.eMouseEnter]='hover'})[button]
                    self[assert(field)]=fn;pinCalls=pinCalls+1
                end,
                ClearCallback=function(self,button)
                    local field=({[Mouse.eLClick]='select',[Mouse.eRClick]='click',[Mouse.eMouseEnter]='hover'})[button]
                    self[assert(field)]=nil;pinCalls=pinCalls+1
                end,
            }
        end
        InstanceManager={new=function(_,name,anchor,parent)
            assert(name=='QuarterServicePin' and anchor=='Anchor' and parent==Controls.ServicePins)
            return {
                GetInstance=function()
                    assert(not contextHidden and contextParent==nativeWorldView,
                        'Pin instances cannot render under a hidden/unattached context')
                    local pin=table.remove(pool)
                    if not pin then
                        pin={Anchor=control(),PinRoot=control(),Backing=control(),
                            ServiceIcon=control(),ServiceButton=control(),QuarterIcon=control()}
                        pinCreates=pinCreates+1;pins[#pins+1]=pin
                    end
                    pin.active=true;return pin
                end,
                ReleaseInstance=function(_,pin) pin.active=false;pinReleases=pinReleases+1;pool[#pool+1]=pin end,
            }
        end}
        UI.GridToWorld=function(index,y)
            if y then return index*10,y*20 end
            return index*10,index*20
        end
        Locale.Lookup=function(key,...)
            local values={key};for _,value in ipairs({...}) do values[#values+1]=tostring(value) end
            local text=table.concat(values,'|')
            if key=='LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER' then
                text='Miller: '..text..'[NEWLINE]Supply Chain: Water Mill [ICON_ARROW] Granary.'
            end
            return text
        end
        local s=CSC_QuarterLensSupport
        s.GetPlotEntries=function() return entries end
        for _,entry in ipairs(entries) do entry.quarterKey='BAKERS' end
        effects={}
        -- Three producers of the same Service in city100, including a second
        -- exact recipient. City totals must match MCUIS even on just one pin.
        effect(1,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(0)})
        effect(2,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(0)})
        effect(3,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(9,0,100)})
        effect(4,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(1)})
        effect(5,'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',true,{subject(0,1,100)})
        s.DrawOverlay('Lens',entries)
        -- The owning view publishes after GameCore updates. The marker UI
        -- consumes that snapshot without a second game-data scan.
        function refreshOwner() s.DrawOverlay('Lens',entries) end
        Events.GameCoreEventPublishComplete.Add(refreshOwner)
    ''')
    lua.execute((root / 'Civ Supply Chains/Lua_UI/Lenses/CSC_QuarterServicePins.lua').read_text())
    lua.execute('''
        assert(contextHidden and pinCreates==0)
        initializePins(false) -- Early init: native parent is not available yet.
        assert(contextHidden and pinCreates==0 and Events.LoadScreenClose.Count()==1)
        nativeWorldView={}
        Events.LoadScreenClose()
        assert(not contextHidden and contextParent==nativeWorldView)
        assert(Events.LoadScreenClose.Count()==0)
        initializePins(true) -- Reload initialization is safe and preserves pins.
        assert(pinCreates==2 and pinReleases==0)
    ''')
    lua.execute((root / 'Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/Suk_MCUIS_CSC.lua').read_text())
    lua.execute('''
        function activePins() local result={} for _,pin in ipairs(pins) do if pin.active then result[#result+1]=pin end end return result end
        function pinAt(index) for _,pin in ipairs(activePins()) do if pin.Anchor.world[1]==index*10 then return pin end end end
        assert(#activePins()==2 and pinCreates==2) -- Cold-start snapshot restored.
        UI.GetHeadSelectedCity=function() return {GetID=function() return 100 end,GetOwner=function() return 0 end} end
        local row=CSC_ServicePresentation.Anchors.MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER
        local icon={SetIconData=function(self,make,request,tooltip,art) self.make=make;self.tooltip=tooltip;self.art=art end}
        OnSuk_MCUIS_QueryIcon('City','CSC_ActiveModifiers_'..row.AbilityEffectModifierId,icon)
        local pin=pinAt(0)
        assert(icon.make and pin.ServiceIcon.icon==icon.art)
        assert(not pin.ServiceIcon.hidden and pin.ServiceIcon.size==256 and pin.ServiceButton.tooltip==icon.tooltip)
        local benefit='Miller: '..row.AbilityDesc..'|+30|+3|3'
        local secondBenefit='Miller: '..row.AbilityDesc..'|+10|+1|1'
        local details='Supply Chain: Water Mill [ICON_ARROW] Granary.'
        assert(icon.tooltip==benefit..'[NEWLINE]'..details,icon.tooltip)
        local focus={}
        LuaEvents.CSC_QuarterServiceFocus.Add(function(owner,key,index,target,isQuarter)
            assert(owner=='Lens' and key=='BAKERS')
            focus[#focus+1]={index=index,target=target,isQuarter=isQuarter}
        end)
        pin.ServiceButton.select()
        assert(#focus==1 and focus[1].index==0 and focus[1].target==row.AbilityIconTarget)
        local second=pinAt(1)
        assert(pin.ServiceButton.tooltip==icon.tooltip and second.ServiceButton.tooltip==secondBenefit..'[NEWLINE]'..details)
        assert(pin.Backing.texture=='CSC_ServiceMedallion.dds' and pin.ServiceIcon.alpha==1)
        assert(second.Backing.texture=='CSC_ServiceMedallionGray.dds' and second.ServiceIcon.alpha==.5)
        second.ServiceButton.select()
        assert(#focus==2 and focus[2].index==1)
        assert(second.Backing.texture=='CSC_ServiceMedallion.dds' and second.ServiceIcon.alpha==1)
        second.ServiceButton.select()
        assert(#focus==3 and focus[3].index==nil)
        assert(pin.ServiceIcon.alpha==1 and second.ServiceIcon.alpha==1)
        assert(pin.ServiceButton.tooltip==icon.tooltip)
        assert(second.ServiceButton.tooltip==secondBenefit..'[NEWLINE]'..details)
        local opened
        LuaEvents.OpenCivilopedia.Add(function(target) opened=target end)
        pin.ServiceButton.click();assert(opened==row.AbilityIconTarget)
        CSC_QuarterLensSupport.DrawOverlay('Lens',entries)
        assert(pinCreates==2 and pinReleases==0) -- Stable instances.
        -- Current effect updates without recreating the pin or reopening lens.
        effects[2].active=false;Events.GameCoreEventPublishComplete()
        assert(pinAt(0)==pin and pin.ServiceButton.tooltip=='Miller: '..row.AbilityDesc..'|+20|+2|2[NEWLINE]'..details)
        -- Exact district subject loss removes the pin, even though another
        -- district in that same city still has a current active Service.
        pin.ServiceButton.select()
        effects[1].active=false;Events.GameCoreEventPublishComplete()
        assert(#focus==5 and focus[4].index==0 and focus[5].index==nil)
        assert(pinAt(0)==nil and pinAt(1) and pin.ServiceButton.click==nil
            and pin.ServiceButton.select==nil)
        effects[4].active=false;Events.GameCoreEventPublishComplete();assert(#activePins()==0)
        -- Four distinct selected-Quarter Services at the same tile form a square.
        effects={}
        local i=0
        for anchor,r in pairs(CSC_ServicePresentation.Anchors) do
            if r.NotificationQuarter=='BAKERS' then i=i+1;effect(i,anchor,true,{subject(0)}) end
        end
        Events.GameCoreEventPublishComplete();assert(#activePins()==4)
        local positions={}
        for _,p in ipairs(activePins()) do
            local x, y = table.unpack(p.PinRoot.offset)
            positions[x] = positions[x] or {}
            positions[x][y] = true
            assert(not p.ServiceIcon.hidden and p.ServiceIcon.icon:find('ICON_BUILDING_CSC_BAKERS_',1,true)==1)
        end
        assert(positions[-281][-281] and positions[281][281])
        local markers=CSC_QuarterLensSupport.GetServiceMarkers('BAKERS',entries)
        local expected={}
        for _,record in ipairs(markers) do expected[record.icon]=record.target end
        for _,p in ipairs(activePins()) do
            p.ServiceButton.click();assert(opened==expected[p.ServiceIcon.icon])
        end
        LuaEvents.CSC_QuarterServicePins_Update('Lens','BAKERS',{markers[1],markers[2],markers[3]})
        assert(#activePins()==3)
        local top,bottom=0,0
        for _,p in ipairs(activePins()) do
            if p.PinRoot.offset[2]==-281 then top=top+1 else assert(p.PinRoot.offset[2]==281);bottom=bottom+1 end
        end
        assert(top==1 and bottom==2)
        LuaEvents.CSC_QuarterServicePins_Update('Lens','BAKERS',{markers[1],markers[2]})
        assert(#activePins()==2)
        for _,p in ipairs(activePins()) do assert(p.PinRoot.offset[2]==0) end
        Events.GameCoreEventPublishComplete();assert(#activePins()==4)
        -- Placement never takes ownership or shows Service pins.
        LuaEvents.CSC_QuarterServicePins_Update('Placement','TAILORS',{})
        assert(#activePins()==4)
        LuaEvents.CSC_QuarterServicePins_Update('Placement',nil,{})
        assert(#activePins()==4)
        local quarterIcon='ICON_DISTRICT_CSC_BAKERS_QUARTER'
        LuaEvents.CSC_QuarterServicePins_Update('Lens','BAKERS',{
            markers[1], {index=2,icon=quarterIcon,isQuarter=true}, {index=3,icon=quarterIcon,isQuarter=true}})
        local service,quarter,other=pinAt(0),pinAt(2),pinAt(3)
        assert(service.Anchor.world[2]==-16 and service.Anchor.world[3]==0)
        assert(quarter.Anchor.world[2]==24 and quarter.Anchor.world[3]==0)
        assert(other.Anchor.world[2]==44 and other.Anchor.world[3]==0)
        assert(quarter.QuarterIcon.icon=='ICON_DISTRICT_CSC_BAKERS_QUARTER')
        assert(not quarter.Backing.hidden and quarter.Backing.texture=='CSC_QuarterLensBacking.dds')
        assert(quarter.ServiceIcon.hidden and not quarter.QuarterIcon.hidden)
        assert(quarter.ServiceButton.click==nil)
        CSC_QuarterTooltip={Format=function(snapshot,key,index)
            assert(snapshot.key==key and #snapshot.markers==3 and index==2)
            return "Quarter report"
        end}
        quarter.ServiceButton.hover()
        assert(quarter.ServiceButton.tooltip=="Quarter report")
        quarter.ServiceButton.select()
        assert(focus[#focus].index==2 and focus[#focus].isQuarter)
        assert(quarter.QuarterIcon.icon=='ICON_DISTRICT_CSC_BAKERS_QUARTER')
        assert(other.QuarterIcon.icon=='ICON_DISTRICT_CSC_BAKERS_QUARTER_GRAY')
        assert(quarter.Backing.texture=='CSC_QuarterLensBacking.dds')
        assert(other.Backing.texture=='CSC_QuarterLensBackingGray.dds')
        assert(service.Backing.texture=='CSC_ServiceMedallionGray.dds' and service.ServiceIcon.alpha==.5)
        service.ServiceButton.select()
        assert(focus[#focus].index==0 and not focus[#focus].isQuarter)
        assert(quarter.QuarterIcon.icon=='ICON_DISTRICT_CSC_BAKERS_QUARTER_GRAY')
        other.ServiceButton.select()
        assert(focus[#focus].index==3 and focus[#focus].isQuarter)
        other.ServiceButton.select()
        assert(focus[#focus].index==nil)
        assert(service.ServiceIcon.alpha==1)
        assert(quarter.QuarterIcon.icon=='ICON_DISTRICT_CSC_BAKERS_QUARTER')
        assert(other.QuarterIcon.icon=='ICON_DISTRICT_CSC_BAKERS_QUARTER')
        LuaEvents.CSC_QuarterServicePins_Update('Lens','TAILORS',{
            {index=2,icon='ICON_DISTRICT_CSC_TAILORS_QUARTER',isQuarter=true}})
        assert(pinAt(2)==quarter and quarter.QuarterIcon.icon=='ICON_DISTRICT_CSC_TAILORS_QUARTER')
        Events.LocalPlayerChanged();assert(#activePins()==0)
        Events.GameCoreEventPublishComplete.Remove(refreshOwner)
        local calls=pinCalls;shutdown();assert(pinCalls==calls)
        assert(Events.GameCoreEventPublishComplete.Count()==0)
        assert(Events.LoadScreenClose.Count()==0)
        assert(LuaEvents.CSC_QuarterServicePins_Update.Count()==0)
        LuaEvents.CSC_QuarterServicePins_Update('Lens','BAKERS',{});assert(pinCalls==calls)
    ''')
    xml = ET.parse(root / 'Civ Supply Chains/Lua_UI/Lenses/CSC_QuarterServicePins.xml')
    assert xml.getroot().get('Layer') == 'WorldAnchor'
    anchor = xml.find('.//WorldAnchor[@ID="Anchor"]')
    assert anchor.get('Scaling') == '1' and anchor.get('Billboard') == '1'
    assert anchor.get('UnitsPerPixel') == '0.037'
    backing = xml.find('.//Image[@ID="Backing"]')
    assert backing.get('Texture') == 'CSC_ServiceMedallion.dds'
    assert backing.get('Size') == '383,383' and backing.get('StretchMode') == 'Fill'
    quarter_icon = xml.find('.//Image[@ID="QuarterIcon"]')
    assert quarter_icon.get('Size') == '256,256'
    assert quarter_icon.get('Offset') is None
    assert xml.find('.//Button[@ID="ServiceButton"]').get('Size') == '383,383'
    assert xml.find('.//Container[@ID="PinRoot"]').get('Size') == '510,510'
    assert xml.find('.//Image[@ID="ServiceIcon"]').get('Offset') == '0,-6'
    assert xml.find('.//Image[@ID="ServiceIcon"]').get('Size') == '256,256'
    pin = xml.find('.//Container[@ID="PinRoot"]')
    assert pin.get('Anchor') == 'C,C'
    assert [control.get('ID') for control in pin] == ['Backing', 'ServiceButton']
