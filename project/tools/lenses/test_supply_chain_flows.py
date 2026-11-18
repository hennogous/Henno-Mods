"""Connection semantics and native pressure-arrow lifecycle; no rendered-shader claims."""
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def test_supply_chain_flows(runtime, game=None):
    lua = runtime()
    lua.execute('''
        local s=CSC_QuarterLensSupport
        local function index(name) return GameInfo.Buildings[name].Index end
        function flowWorld(key)
            resetWorld(7,7)
            for _,p in ipairs(world) do
                p.resource=-1; p.district=-1; p.owner=0; p.complete=true
                p.built={}; p.buildingPillaged={}; p.districtPillaged=false
                p.purchaseCity={
                    GetOwner=function() return p.owner end, GetID=function() return p.index end,
                    GetDistricts=function() return {
                        IsComplete=function(_,_,plot) return plot==p.index and p.complete end,
                        IsPillaged=function() return p.districtPillaged end,
                    } end,
                    GetBuildings=function() return {
                        HasBuilding=function(_,i) return p.built[i]==true end,
                        IsPillaged=function(_,i) return p.buildingPillaged[i]==true end,
                        GetBuildingsAtLocation=function(_,plot)
                            local result={}
                            if plot==p.index and not p.wrongBuildingLocation then
                                for i in pairs(p.built) do result[#result+1]=i end
                            end
                            return result
                        end,
                    } end,
                }
            end
            currentKey=key; q=world[25]; base=world[32]; spec=world[26]; customer=world[19]
            q.district=GameInfo.Districts[s.Quarters[key].districtType].Index
        end
        function stage(n)
            -- Bakers' two mill variants are alternatives, not an AND gate.
            q.built={[assert(next(s.Quarters[currentKey].flowStages[n]))]=true}
        end
        function material(p,kind)
            local quarter=s.Quarters[currentKey]
            p.resource=GameInfo.Resources[next(kind=='BASE' and quarter.baseSet or quarter.specSet)].Index
            p.improvement=0; p.pillaged=false
        end
        function venue(p,district,building)
            p.district=GameInfo.Districts[district].Index
            p.built={[index(building)]=true}
        end
        function links() return s.GetFlowLinks(currentKey) end
        local function only(source,target,kind,yieldType)
            local result=links()
            assert(#result==1, 'Expected exactly one active connection; got '..#result)
            assert(result[1].source==source and result[1].target==target and result[1].kind==kind)
            if yieldType then assert(result[1].yieldType==yieldType) end
        end

        -- Identity-coloured Quarters follow the lens's 20%/60% readiness split. Hidden
        -- automatically granted flags/Services must not upgrade an empty tile.
        for _,key in ipairs({'BAKERS','TAILORS'}) do
            flowWorld(key)
            local function quarterEntry()
                for _,entry in ipairs(s.GetPlotEntries(key,false)) do
                    if entry.index==q.index then return entry end
                end
                error('Missing Quarter entry')
            end
            assert(not quarterEntry().ready and quarterEntry().color==UI.GetColorValue(s.Quarters[key].quarterEmptyColor))
            q.built={[index('BUILDING_CSC_BAKERS_RIVER_ACCESS')]=true,[index('BUILDING_CSC_BAKERS_STAGE_2_SERVICE')]=true}
            assert(not quarterEntry().ready)
            stage(2)
            assert(quarterEntry().ready and quarterEntry().color==UI.GetColorValue(s.Quarters[key].quarterColor))
            for i in pairs(q.built) do q.buildingPillaged[i]=true end
            assert(not quarterEntry().ready)
            q.buildingPillaged={}
            for _,owner in ipairs({'Lens','Placement'}) do
                s.DrawOverlay(owner,s.GetPlotEntries(key,false))
                assert(OutlineContains(owner,q.index))
                local edge=owner=='Lens' and 'CSC_Lens_Ready_' or 'CSC_Lens_Dim_'
                assert(outlines['CSC_Quarter'..owner..'_Ready'].styles[3]==edge..s.Quarters[key].quarterStyle)
                s.ClearOverlay(owner)
            end
        end

        for _,key in ipairs({'BAKERS','TAILORS'}) do
            flowWorld(key); material(base,'BASE'); material(spec,'SPEC')
            assert(#links()==0) -- Improved resources alone do not have a buyer.
            stage(3); assert(#links()==0) -- Stage 3 is neither material buyer.
            local materialYield=key=='BAKERS' and 'YIELD_FOOD' or 'YIELD_CULTURE'
            stage(2); only(base.index,q.index,'BASE',materialYield)
            stage(4); only(spec.index,q.index,'SPEC',materialYield)
            q.complete=false; assert(#links()==0); q.complete=true
            q.districtPillaged=true; assert(#links()==0); q.districtPillaged=false
            for i in pairs(q.built) do q.buildingPillaged[i]=true end
            assert(#links()==0); q.buildingPillaged={}
            q.wrongBuildingLocation=true; assert(#links()==0); q.wrongBuildingLocation=false
            spec.pillaged=true; assert(#links()==0); spec.pillaged=false
            spec.improvement=-1; assert(#links()==0); spec.improvement=0
            spec.owner=1; assert(#links()==0); spec.owner=0
            spec.hidden=true; assert(#links()==0); spec.hidden=false
            q.owner=1; assert(#links()==0); q.owner=0
            q.hidden=true; assert(#links()==0); q.hidden=false

            flowWorld(key)
            local district=key=='BAKERS' and 'DISTRICT_CITY_CENTER' or 'DISTRICT_HARBOR'
            local building=key=='BAKERS' and 'BUILDING_GRANARY' or 'BUILDING_LIGHTHOUSE'
            venue(customer,district,building)
            assert(#links()==0) -- A ready customer alone is insufficient.
            stage(4); assert(#links()==0) -- Wrong producer stage.
            stage(2); only(q.index,customer.index,'SALE',key=='BAKERS' and 'YIELD_FOOD' or 'YIELD_PRODUCTION')
            customer.complete=false; assert(#links()==0); customer.complete=true
            customer.districtPillaged=true; assert(#links()==0); customer.districtPillaged=false
            customer.buildingPillaged[index(building)]=true; assert(#links()==0); customer.buildingPillaged={}
            customer.wrongBuildingLocation=true; assert(#links()==0); customer.wrongBuildingLocation=false
            customer.owner=1; assert(#links()==0); customer.owner=0
            customer.hidden=true; assert(#links()==0); customer.hidden=false
            local remote=world[21] -- Same row, two tiles beyond the adjacent customer.
            venue(remote,district,building); customer.district=-1; assert(#links()==0)

            flowWorld(key); venue(customer,'DISTRICT_COMMERCIAL_HUB','BUILDING_MARKET')
            stage(2); assert(#links()==0)
            stage(3); only(q.index,customer.index,'SALE',key=='BAKERS' and 'YIELD_FOOD' or 'YIELD_CULTURE') -- Exact gameplay producer.
            customer.built={}; assert(#links()==0)
        end

        flowWorld('TAILORS'); stage(2)
        venue(customer,'DISTRICT_ROYAL_NAVY_DOCKYARD','BUILDING_TEST_LIGHTHOUSE')
        only(q.index,customer.index,'SALE','YIELD_PRODUCTION') -- Direct uniques inherit actual adjacency yield tags.
        flowWorld('TAILORS'); stage(4)
        venue(customer,'DISTRICT_THEATER','BUILDING_AMPHITHEATER')
        only(q.index,customer.index,'SALE','YIELD_CULTURE')
        flowWorld('BAKERS'); stage(4)
        venue(customer,'DISTRICT_LEU_GARDEN','BUILDING_LEU_CONSERVATORY')
        only(q.index,customer.index,'SALE','YIELD_CULTURE') -- Optional mapping remains additive SQL.

        flowWorld('TAILORS')
        venue(customer,'DISTRICT_WONDER','BUILDING_BROADWAY')
        customer.wonder=index('BUILDING_BROADWAY')
        stage(3); assert(#links()==0)
        stage(4); only(q.index,customer.index,'SALE','YIELD_CULTURE')
        -- A completed Wonder in the city's exact plot list remains a
        -- customer when the plot's separate completion flag is false.
        customer.complete=false
        only(q.index,customer.index,'SALE','YIELD_CULTURE')
        local host=index('BUILDING_BROADWAY')
        customer.built[host]=nil; assert(#links()==0)
        customer.built[host]=true
        customer.wrongBuildingLocation=true
        only(q.index,customer.index,'SALE','YIELD_CULTURE')
        customer.wonder=-1
        assert(#links()==0)
        customer.wrongBuildingLocation=false
        only(q.index,customer.index,'SALE','YIELD_CULTURE')
        customer.buildingPillaged[index('BUILDING_BROADWAY')]=true; assert(#links()==0)

        -- Colours follow the receiving site's actual adjacency yield, not
        -- the Quarter's gold return, customer category, or producer stage.
        for _,case in ipairs({
            {'BAKERS',4,'DISTRICT_ENTERTAINMENT_COMPLEX','BUILDING_ZOO','YIELD_CULTURE'},
            {'BAKERS',4,'DISTRICT_WATER_ENTERTAINMENT_COMPLEX','BUILDING_FERRIS_WHEEL','YIELD_CULTURE'},
            {'TAILORS',3,'DISTRICT_HOLY_SITE','BUILDING_TEMPLE','YIELD_CULTURE'},
            {'BAKERS',3,'DISTRICT_SUGUBA','BUILDING_SUKIENNICE','YIELD_FOOD'},
        }) do
            flowWorld(case[1]); stage(case[2]); venue(customer,case[3],case[4])
            only(q.index,customer.index,'SALE',case[5])
            s.DrawOverlay('Lens',s.GetPlotEntries(currentKey,false))
            local wave=outlines.CSC_QuarterLens_Flow.waves[1]
            assert(wave.color==UI.GetColorValue(s.FlowYieldColors[case[5]]))
            s.ClearOverlay('Lens')
        end
        for _,name in ipairs({'BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE'}) do
            -- Native Wonder tiles need not return a normal district or the
            -- Wonder building in an ordinary district's at-location list.
            flowWorld('TAILORS'); stage(4)
            customer.wonder=index(name)
            only(q.index,customer.index,'SALE','YIELD_CULTURE')
            s.DrawOverlay('Lens',s.GetPlotEntries(currentKey,false))
            assert(outlines.CSC_QuarterLens_Flow.waves[1].color==UI.GetColorValue('COLOR_CSC_LENS_FLOW_CULTURE'))
            s.ClearOverlay('Lens')
        end

        for _,key in ipairs({'BAKERS','TAILORS'}) do
            flowWorld(key)
            for _,kind in ipairs({'DISTRICT_RURALCOMMUNITYA','DISTRICT_COREX_FRONTIER_TOWN'}) do
                customer.district=GameInfo.Districts[kind].Index
                local function goodsEntry()
                    for _,entry in ipairs(s.GetPlotEntries(key,false)) do
                        if entry.index==customer.index then return entry end
                    end
                end
                assert(goodsEntry().category=='GOODS' and goodsEntry().readyStyle=='GOODS')
                assert(goodsEntry().color==UI.GetColorValue('COLOR_CSC_LENS_GOODS'))
                assert(#links()==0)
                customer.districtPillaged=true
                assert(goodsEntry().readyStyle==nil and #links()==0)
                customer.districtPillaged=false
                customer.owner=1; assert(#links()==0); customer.owner=0
            end
            local tag='CLASS_CSC_'..key..'_GOODS_PROVIDER'
            local icon
            for row in GameInfo.CSC_AdjacencyObjects() do
                if row.CustomAdjacentObject==tag then icon=row.ArtdefOverlayEntry end
            end
            assert(icon=='CSC_Goods')
        end

        flowWorld('BAKERS'); stage(2); material(base,'BASE')
        s.DrawOverlay('Lens',s.GetPlotEntries(currentKey,false))
        local effect=outlines.CSC_QuarterLens_Flow
        local creates=effect.creates
        s.FlowYieldColors.YIELD_FOOD='COLOR_CSC_LENS_FLOW_CULTURE'
        s.DrawOverlay('Lens',s.GetPlotEntries(currentKey,false))
        assert(effect.creates==creates+1 and effect.waves[1].color==UI.GetColorValue('COLOR_CSC_LENS_FLOW_CULTURE'))
        s.FlowYieldColors.YIELD_FOOD='COLOR_CSC_LENS_FLOW_FOOD'
        s.ClearOverlay('Lens')
        -- Missing/unknown mapping leaves static sites alone, and makes no
        -- wrong-colour outgoing arrow. No generic yellow fallback.
        flowWorld('BAKERS'); stage(2); venue(customer,'DISTRICT_CITY_CENTER','BUILDING_GRANARY')
        local saved=s.Quarters.BAKERS.customerYields.DISTRICT_CITY_CENTER
        s.Quarters.BAKERS.customerYields.DISTRICT_CITY_CENTER={YIELD_UNKNOWN=true}
        assert(#links()==0)
        s.Quarters.BAKERS.customerYields.DISTRICT_CITY_CENTER=saved

        -- The manual effect stays cached. Placement is purely static.
        flowWorld('TAILORS'); stage(2); material(base,'BASE')
        venue(customer,'DISTRICT_HARBOR','BUILDING_LIGHTHOUSE')
        local entries=s.GetPlotEntries('TAILORS',false)
        for _,owner in ipairs({'Lens'}) do
            assert(s.DrawOverlay(owner,entries))
            local flow=outlines['CSC_Quarter'..owner..'_Flow']
            assert(flow.visible and #flow.waves==2)
            local gotInput,gotOutput=false,false
            for _,wave in ipairs(flow.waves) do
                assert(wave.speed==2 and wave.type=='CIVILIZATION_UNKNOWN')
                if wave.pos1==base.index and wave.pos2==q.index then
                    gotInput=true; assert(wave.color==UI.GetColorValue('COLOR_CSC_LENS_FLOW_CULTURE'))
                elseif wave.pos1==q.index and wave.pos2==customer.index then
                    gotOutput=true; assert(wave.color==UI.GetColorValue('COLOR_CSC_LENS_FLOW_PRODUCTION'))
                end
            end
            assert(gotInput and gotOutput)
            local resets,creates=flow.resets,flow.creates
            s.DrawOverlay(owner,entries)
            assert(flow.resets==resets and flow.creates==creates)
        end
        local readLinks, readMarkers=s.GetFlowLinks,s.GetServiceMarkers
        s.GetFlowLinks=function() error('Placement read animation data') end
        s.GetServiceMarkers=function() error('Placement read Service data') end
        assert(s.DrawOverlay('Placement',entries))
        s.GetFlowLinks,s.GetServiceMarkers=readLinks,readMarkers
        s.ClearOverlay('Placement')
        assert(outlines.CSC_QuarterPlacement_Flow==nil and outlines.CSC_QuarterLens_Flow.visible)
        base.pillaged=true; q.built={}
        s.DrawOverlay('Lens',s.GetPlotEntries('TAILORS',false))
        assert(not outlines.CSC_QuarterLens_Flow.visible and #outlines.CSC_QuarterLens_Flow.waves==0)
        stage(2); base.pillaged=false
        s.DrawOverlay('Lens',s.GetPlotEntries('TAILORS',false))
        assert(outlines.CSC_QuarterLens_Flow.visible)
        s.ClearOverlay('Lens'); assert(not outlines.CSC_QuarterLens_Flow.visible)
        assert(s.FlowSignatures.Lens==nil and s.FlowSignatures.Placement==nil)
        -- Placement filters and missing art cannot invent a ghost Quarter.
        assert(#s.GetFlowLinks('TAILORS',{entries[1]})==0)
        missingArt=true; assert(s.DrawOverlay('Lens',entries)); s.ClearOverlay('Lens')
    ''')
    lua.execute('''
        local s=CSC_QuarterLensSupport
        missingArt=false; missingTint=false
        Locale={Lookup=function(value) return value end}
        local cases={
            {'BAKERS',2,'DISTRICT_CITY_CENTER','BUILDING_GRANARY','MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER'},
            {'BAKERS',3,'DISTRICT_COMMERCIAL_HUB','BUILDING_MARKET','MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB'},
            {'BAKERS',4,'DISTRICT_ENTERTAINMENT_COMPLEX','BUILDING_ZOO','MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT'},
            {'TAILORS',4,'DISTRICT_WONDER','BUILDING_BROADWAY','MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY'},
        }
        for _,case in ipairs(cases) do
            local key,n,district,building,anchor=table.unpack(case)
            flowWorld(key); stage(n)
            if district=='DISTRICT_WONDER' then
                customer.wonder=GameInfo.Buildings[building].Index
                local service=GameInfo.Buildings.BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY.Index
                customer.built[service]=true
                local otherWonder=world[17]
                otherWonder.wonder=GameInfo.Buildings.BUILDING_BOLSHOI_THEATRE.Index
                otherWonder.purchaseCity=customer.purchaseCity
            else
                venue(customer,district,building)
            end
            material(base,'BASE'); material(spec,'SPEC')
            local unimproved,pillaged=world[31],world[27]
            material(unimproved,'BASE'); unimproved.improvement=-1
            material(pillaged,'SPEC'); pillaged.pillaged=true
            local unreadyCustomer=world[18]
            local unreadyDistrict=key=='BAKERS' and 'DISTRICT_CITY_CENTER' or 'DISTRICT_HARBOR'
            unreadyCustomer.district=GameInfo.Districts[unreadyDistrict].Index
            local remoteQuarter,remoteBase=world[1],world[2]
            remoteQuarter.district=q.district
            remoteQuarter.built={[assert(next(s.Quarters[key].flowStages[2]))]=true}
            material(remoteBase,'BASE')
            local otherCustomer
            if n==2 then
                otherCustomer=world[24]
                venue(otherCustomer,district,building)
            end
            local active=true
            GameEffects={
                GetModifiers=function() return {1} end,
                GetModifierDefinition=function() return {Id=anchor} end,
                GetModifierActive=function() return active end,
                GetModifierSubjectCount=function() return 1 end,
                GetModifierSubjects=function() return {1} end,
                GetObjectType=function() return 'District' end,
                GetObjectString=function()
                    local subjectID=district=='DISTRICT_WONDER' and 999 or customer.index
                    return 'District: '..subjectID..', Owner: 0, City: '..customer.index
                end,
            }
            local entries=s.GetPlotEntries(key,false)
            local markers=s.GetServiceMarkers(key,entries)
            assert(#markers==1 and markers[1].index==customer.index and markers[1].stage==n,anchor)
            if district=='DISTRICT_WONDER' then
                local host=GameInfo.Buildings[building].Index
                customer.district=GameInfo.Districts.DISTRICT_WONDER.Index
                customer.built[host]=true
                customer.complete=false
                customer.wonder=-1
                local fallback=s.PrepareOverlay(s.GetPlotEntries(key,false))
                local sale
                for _,entry in ipairs(fallback.entries) do
                    if entry.index==customer.index then sale=entry end
                end
                assert(sale and sale.wonder.Index==host and sale.category=='SALE' and sale.ready)
                assert(#fallback.markers==1 and fallback.markers[1].index==customer.index
                    and fallback.markers[1].target==markers[1].target)
                customer.wrongBuildingLocation=true
                local missing=s.PrepareOverlay(s.GetPlotEntries(key,false))
                assert(#missing.markers==0)
                for _,entry in ipairs(missing.entries) do assert(entry.index~=customer.index) end
                customer.wrongBuildingLocation=false
                active=false
                assert(#s.GetServiceMarkers(key,fallback.entries)==0)
                active=true
            end
            for _,owner in ipairs({'Lens'}) do
                local prefix='CSC_Quarter'..owner
                local function alphas()
                    local result={}
                    for rgba,plots in pairs(outlines[prefix..'_Tint'].tints) do
                        for _,index in ipairs(plots) do result[index]=math.floor((rgba%0x100000000)/0x1000000) end
                    end
                    return result
                end
                active=true
                s.DrawOverlay(owner,entries,false,markers[1])
                local alpha=alphas()
                assert(alpha[q.index]==153 and alpha[customer.index]==153 and alpha[base.index]==153,anchor)
                assert(alpha[spec.index]==(n==4 and 153 or 77),anchor)
                assert(alpha[remoteQuarter.index]==77 and alpha[remoteBase.index]==77)
                assert(alpha[unimproved.index]==26 and alpha[pillaged.index]==26)
                local outline=outlines[prefix..'_Ready']
                for channel,plots in pairs(outline.channels) do
                    for _,index in ipairs(plots) do
                        local expectedStyle=alpha[index]==153 and '^CSC_Lens_Ready_' or '^CSC_Lens_Faint_'
                        assert(outline.styles[channel]:match(expectedStyle))
                    end
                end
                local expected={
                    [base.index..':'..q.index]=204,
                    [q.index..':'..customer.index]=204,
                    [remoteBase.index..':'..remoteQuarter.index]=26,
                }
                if n==4 then expected[spec.index..':'..q.index]=204 end
                if otherCustomer then expected[q.index..':'..otherCustomer.index]=26 end
                local materialColor=UI.GetColorValue(key=='BAKERS' and 'COLOR_CSC_LENS_FLOW_FOOD' or 'COLOR_CSC_LENS_FLOW_CULTURE')
                for _,wave in ipairs(outlines[prefix..'_Flow'].waves) do
                    local edge=wave.pos1..':'..wave.pos2
                    assert(wave.peakAlpha==expected[edge],anchor..' '..edge)
                    if wave.pos2==q.index or wave.pos2==remoteQuarter.index then
                        assert(wave.color%0x1000000==materialColor%0x1000000,anchor..' '..edge)
                    end
                    expected[edge]=nil
                end
                assert(next(expected)==nil,anchor)
                local snapshot=s.PrepareOverlay(entries)
                assert(snapshot.quarterPins[q.index].icon=='ICON_DISTRICT_CSC_'..key..'_QUARTER')
                assert(snapshot.quarterPins[remoteQuarter.index] and not snapshot.quarterPins[customer.index])
                s.DrawPreparedOverlay(owner,snapshot,false,{index=q.index,isQuarter=true})
                local quarterAlpha=alphas()
                assert(quarterAlpha[q.index]==153 and quarterAlpha[customer.index]==153)
                assert(quarterAlpha[remoteQuarter.index]==77 and quarterAlpha[remoteBase.index]==77)
                assert(quarterAlpha[unimproved.index]==76 and quarterAlpha[unreadyCustomer.index]==51)
                assert(quarterAlpha[pillaged.index]==26)
                local outputs=0
                for _,wave in ipairs(outlines[prefix..'_Flow'].waves) do
                    assert(wave.pos1~=unimproved.index and wave.pos2~=unreadyCustomer.index)
                    local touchesQuarter=wave.pos1==q.index or wave.pos2==q.index
                    assert(wave.peakAlpha==(touchesQuarter and 204 or 26),anchor)
                    if wave.pos1==q.index then outputs=outputs+1 end
                end
                assert(outputs>=(otherCustomer and 2 or 1),anchor)
                s.DrawPreparedOverlay(owner,snapshot,false,markers[1])
                local readAdjacent=Map.GetAdjacentPlots
                Map.GetAdjacentPlots=function() error('Returning to a focused Service rescanned its feeder tiles') end
                s.DrawPreparedOverlay(owner,snapshot)
                s.DrawPreparedOverlay(owner,snapshot,false,markers[1])
                Map.GetAdjacentPlots=readAdjacent
                s.DrawOverlay(owner,entries)
                alpha=alphas()
                assert(alpha[base.index]==153 and alpha[unimproved.index] and alpha[pillaged.index])
                for _,wave in ipairs(outlines[prefix..'_Flow'].waves) do assert(wave.peakAlpha==nil) end
                active=false
                s.DrawOverlay(owner,entries,false,markers[1])
                assert(alphas()[base.index]==153) -- Stale Service no longer owns focus.
                s.ClearOverlay(owner)
            end
        end
        GameEffects=nil; missingTint=true
    ''')
    mod = Path(__file__).resolve().parents[3] / 'Civ Supply Chains'
    art = ET.parse(mod/'ArtDefs/CSC_QuarterResourceBorders.artdef')
    edge_art = ET.parse(mod/'ArtDefs/CSC_Overlay.artdef')
    assert any(row.get('text') == 'CSC_Goods' for row in edge_art.findall('.//m_Name'))
    layers = next(row for row in art.findall('m_RootCollections/Element') if row.find('m_CollectionName').get('text') == 'Layers')
    for owner in ('Lens',):
        layer = next(row for row in layers.findall('Element') if row.find('m_Name').get('text') == 'CSC_Quarter'+owner+'_Flow')
        params = {row.find('m_ParamName').get('text'): row for row in layer.findall('m_Fields/m_Values/Element')}
        assert params['Type'].find('m_Value').get('text') == 'PressureOverlay'
        assert params['Material'].find('m_Value').get('text') == 'CSC_Lens_FlowArrow'
        assert params['Pass'].find('m_nValue').text == '1'
        assert float(params['Priority'].find('m_fValue').text) == 20
        tint = next(row for row in layers.findall('Element') if row.find('m_Name').get('text') == 'CSC_Quarter'+owner+'_Tint')
        tint_priority = next(row.find('m_fValue').text for row in tint.findall('m_Fields/m_Values/Element') if row.find('m_ParamName').get('text') == 'Priority')
        assert float(params['Priority'].find('m_fValue').text) > float(tint_priority)
    if game:
        # Verify the current game, not the older SDK's missing texture entry.
        # Caller variable names alone did not prove playback direction; the
        # pos1=source adapter above follows the user's actual native review.
        native = ET.parse(game/'Base/ArtDefs/Overlay.artdef')
        assert any(row.get('text') == 'FormCorpsArrow' for row in native.findall('.//m_Name'))
        pointer = (game/'DLC/PiratesScenario/UI/Replacements/MinimapPanel_PiratesScenario.lua').read_text(encoding='utf-8-sig')
        assert re.search(r'pos1\s*=\s*targetPlotIndex', pointer)
        assert re.search(r'pos2\s*=\s*unitPlotIndex', pointer)
    print('Passed directional supply chains: Stage 2/4 buyers, matching Stage 2/3/4 producers/customers, uniques/Garden/Wonders, owner/range/completion/pillage/visibility/location gates, native arrow API/layer contract, cached refresh and owner cleanup.')
    # The private material changes width only; its recovered native artwork
    # retains every original RGBA mip. Do not accept the SDK's error texture.
    style = next(row for row in art.findall('m_RootCollections/Element/Element')
                 if row.find('m_Name').get('text') == 'CSC_Lens_FlowArrow')
    params = {row.find('m_ParamName').get('text'):row for row in
              style.findall('m_ChildCollections/Element/Element/m_Fields/m_Values/Element')}
    assert float(params['SplineWidth'].find('m_fValue').text) == 20*.7
    assert float(params['SplineSegmentLength'].find('m_fValue').text) == 15
    assert params['SplineTexture'].find('m_EntryName').get('text') == 'CSC_Lens_FlowArrow'
    import hashlib
    texture = (mod/'Textures/CSC_Lens_FlowArrow.dds').read_bytes()
    assert hashlib.sha256(texture[128:128+128*64*4]).hexdigest() == '88d68d9eeb71829da550ed1f66ba2f8da49bd99500022735f3ce0fbcbd6cbe5c'
    if game:
        from extract_native_flow_texture import extract
        assert extract(game/'Base/Platforms/Windows/BLPs/Overlay.blp') == texture

    # Exercise the default conveyor and retained native-art comparison together.
    # Rendering remains native; these assertions validate ownership/data/API use.
    lua.execute('''
        local function events()
            return setmetatable({}, {__index=function(self,key)
                local listeners={}
                local event={Add=function(f) listeners[f]=true end,Remove=function(f) listeners[f]=nil end}
                setmetatable(event,{__call=function(_,...) for f in pairs(listeners) do f(...) end end})
                rawset(self,key,event);return event
            end})
        end
        LuaEvents=events();Events=events();ExposedMembers={}
        ContextPtr={SetShutdown=function(_,f) shutdown=f end,
            SetUpdate=function(_,f) flowUpdate=f end,ClearUpdate=function() flowUpdate=nil end}
        local get=UILens.GetOverlay
        pathOverlays={}
        UILens.GetOverlay=function(name)
            assert(name~='TradeRoutes','Must not borrow the native trade-route layer')
            local isWave=name:match('_FlowConveyor%a+$')
            if name:match('_FlowChevrons$') or name:match('_FlowTrade$') or isWave then
                if missingPaths then return nil end
                if not pathOverlays[name] then
                    pathOverlays[name]={paths={},waves={},clears=0,creates=0,
                        SetVisible=function(self,b) self.visible=b end,
                        ClearAllPaths=function(self) self.paths={};self.clears=self.clears+1 end,
                        ResetAllWaves=function(self)
                            assert(isWave)
                            self.waves={};self.clears=self.clears+1
                        end,
                        CreateLinearWaves=function(self,waves)
                            assert(isWave)
                            self.waves=waves;self.creates=self.creates+1
                        end,
                        CreatePathAlongSpline=function(self,plots,color)
                            assert(#plots==2 and type(plots[1])=='number' and type(color)=='number')
                            self.creates=self.creates+1
                            table.insert(self.paths,{plots=plots,color=color})
                        end}
                end
                return pathOverlays[name]
            end
            return get(name)
        end
    ''')
    lua.execute((mod/'Lua_UI/Lenses/CSC_QuarterFlowTrial.lua').read_text(encoding='utf-8'))
    lua.execute('''
        local s=CSC_QuarterLensSupport
        missingArt=false;s.ClearOverlay('Lens');s.ClearOverlay('Placement')
        flowWorld('BAKERS');stage(2);material(base,'BASE')
        venue(customer,'DISTRICT_CITY_CENTER','BUILDING_GRANARY')
        local entries=s.GetPlotEntries('BAKERS',false)
        s.DrawOverlay('Lens',entries)
        local native=outlines.CSC_QuarterLens_Flow
        local nativeCreates=native.creates
        local conveyor=pathOverlays.CSC_QuarterLens_FlowConveyorWaves
        assert(ExposedMembers.CSC_QuarterFlowTrial.Enabled and ExposedMembers.CSC_QuarterFlowTrial.Style=='conveyor')
        assert(conveyor.visible and #conveyor.waves==2 and not native.visible)
        for i,wave in ipairs(conveyor.waves) do
            assert(wave.pos1==native.waves[i].pos1 and wave.pos2==native.waves[i].pos2)
            assert(wave.color % 0x1000000 == 0xffffff)
            assert(math.floor(wave.color / 0x1000000)==128 and wave.speed==3)
        end
        local conveyorCreates,conveyorClears=conveyor.creates,conveyor.clears
        s.DrawOverlay('Lens',entries)
        assert(conveyor.creates==conveyorCreates and conveyor.clears==conveyorClears)
        s.DrawOverlay('Placement',entries)
        local placedConveyor=pathOverlays.CSC_QuarterPlacement_FlowConveyorWaves
        assert(placedConveyor==nil and conveyor.visible)
        s.ClearOverlay('Placement');assert(conveyor.visible)
        LuaEvents.CSC_QuarterFlowTrial_Enable(false)
        assert(native.visible and not conveyor.visible and #conveyor.waves==0)
        LuaEvents.CSC_QuarterFlowTrial_SetStyle('chevrons')
        local chevrons=pathOverlays.CSC_QuarterLens_FlowChevrons
        assert(ExposedMembers.CSC_QuarterFlowTrial.Ready and not native.visible)
        assert(chevrons.visible and #chevrons.paths==2)
        for i,path in ipairs(chevrons.paths) do
            local wave=native.waves[i]
            assert(path.plots[1]==wave.pos1 and path.plots[2]==wave.pos2 and path.color==wave.color)
        end
        local creates,clears=chevrons.creates,chevrons.clears
        s.DrawOverlay('Lens',entries);LuaEvents.CSC_QuarterFlowTrial_Enable(true)
        assert(chevrons.creates==creates and chevrons.clears==clears)
        LuaEvents.CSC_QuarterFlowTrial_SetStyle('trade')
        local trade=pathOverlays.CSC_QuarterLens_FlowTrade
        assert(trade.visible and #trade.paths==2 and not chevrons.visible and #chevrons.paths==0)
        assert(ExposedMembers.CSC_QuarterFlowTrial.Style=='trade' and not native.visible)
        s.DrawOverlay('Placement',entries)
        assert(pathOverlays.CSC_QuarterPlacement_FlowTrade==nil and trade.visible)
        s.ClearOverlay('Placement')
        assert(trade.visible)
        LuaEvents.CSC_QuarterFlowTrial_SetStyle('invalid')
        assert(ExposedMembers.CSC_QuarterFlowTrial.Style=='trade' and trade.visible)
        LuaEvents.CSC_QuarterFlowTrial_Enable(false)
        assert(native.visible and not trade.visible and native.creates==nativeCreates)
        LuaEvents.CSC_QuarterFlowTrial_SetStyle('chevrons')
        assert(chevrons.visible and not native.visible)
        missingPaths=true;LuaEvents.CSC_QuarterFlowTrial_Enable(true)
        assert(not ExposedMembers.CSC_QuarterFlowTrial.Ready and native.visible)
        s.DrawOverlay('Lens',entries);assert(native.visible)
        missingPaths=false;LuaEvents.CSC_QuarterFlowTrial_Enable(true)
        assert(ExposedMembers.CSC_QuarterFlowTrial.Ready and not native.visible)
        s.ClearOverlay('Lens');assert(not chevrons.visible and #chevrons.paths==0)
        -- Native PathOverlay owns shortest-path wrapping, rather than drawing
        -- a long zero-height UI line across the map seam.
        LuaEvents.CSC_QuarterFlowTrial_Update('Lens',{{pos1=0,pos2=6,color=1}})
        assert(chevrons.paths[1].plots[1]==0 and chevrons.paths[1].plots[2]==6)
        LuaEvents.CSC_QuarterFlowTrial_SetStyle('conveyor')
        LuaEvents.CSC_QuarterFlowTrial_Update('Lens',{{pos1=0,pos2=6,color=-1,type='CIVILIZATION_UNKNOWN'}})
        assert(conveyor.waves[1].color==0x80ffffff)
        assert(conveyor.waves[1].pos1==0 and conveyor.waves[1].pos2==6)
        LuaEvents.CSC_QuarterFlowTrial_Update('Lens',{{pos1=0,pos2=6,color=-1,peakAlpha=204}})
        assert(conveyor.waves[1].color==0xccffffff)
        LuaEvents.CSC_QuarterFlowTrial_Update('Lens',{{pos1=0,pos2=6,color=-1,peakAlpha=26}})
        assert(conveyor.waves[1].color==0x1affffff)
        -- Religion workaround removed: no timer/context callback can gate
        -- rendering in a logic-only context, including repeated activations.
        assert(flowUpdate==nil and conveyor.visible)
        Events.LocalPlayerChanged();assert(not chevrons.visible and #chevrons.paths==0)
        assert(flowUpdate==nil)
        assert(not conveyor.visible and #conveyor.waves==0)
        shutdown();assert(ExposedMembers.CSC_QuarterFlowTrial==nil and flowUpdate==nil)
        LuaEvents.CSC_QuarterFlowTrial_SetStyle('trade')
        assert(ExposedMembers.CSC_QuarterFlowTrial==nil)
    ''')
    trial_xml=ET.parse(mod/'Lua_UI/Lenses/CSC_QuarterFlowTrial.xml').getroot()
    assert not trial_xml.findall('.//Line') and trial_xml.get('ConsumeMouse') == '0'
    for kind in ('Chevrons','Trade','Conveyor'):
        wave = kind.startswith('Conveyor')
        layer = 'ConveyorWaves' if kind=='Conveyor' else kind
        material='CSC_Lens_'+layer if wave else 'CSC_Lens_Path'+kind
        for owner in ('Lens',):
            row=next(r for r in layers.findall('Element') if r.find('m_Name').get('text')=='CSC_Quarter'+owner+'_Flow'+layer)
            params={r.find('m_ParamName').get('text'):r for r in row.findall('m_Fields/m_Values/Element')}
            assert params['Type'].find('m_Value').get('text')==('PressureOverlay' if wave else 'PathOverlay')
            assert params['Pass'].find('m_nValue').text=='1'
            assert float(params['Priority'].find('m_fValue').text)==20
            assert params['Material'].find('m_Value').get('text')==material
            assert params['ShowOnMap'].find('m_bValue').text=='false'
        row=next(r for r in art.findall('m_RootCollections/Element/Element') if r.find('m_Name').get('text')==material)
        params={r.find('m_ParamName').get('text'):r for r in row.findall('m_ChildCollections/Element/Element/m_Fields/m_Values/Element')}
        assert float(params['SplineWidth'].find('m_fValue').text)==18
        assert float(params['SplineScrollSpeed'].find('m_fValue').text)==(.11 if wave else .13)
        assert float(params['SplineSegmentLength'].find('m_fValue').text)==(48 if wave else 32)
        assert int(params['Color_Alpha'].find('m_nValue').text)==(255 if wave else 224)
        texture=params['SplineTexture'].find('m_EntryName').get('text')
        assert texture==('CSC_Lens_'+kind+'Wave' if wave else
                         {'Trade':'TradeRoutePrimary','Chevrons':'CSC_Lens_FlowArrow'}[kind])
    from PIL import Image
    wave_texture=Image.open(mod/'Textures/CSC_Lens_ConveyorWave.dds').convert('RGBA')
    assert wave_texture.size==(128,256)
    # Shadow adds alpha but no white light. Premultiplied red recovers the
    # original white stroke coverage, independently of its dark drop shadow.
    def foreground(x, y):
        red, _, _, alpha = wave_texture.getpixel((x,y))
        return red * alpha / (255 * 255)
    alpha=[foreground(64,y) for y in range(256)]
    slat_length=sum(alpha)/256*48
    # Direction and complete-shape placement matter for a chevron: its tip is
    # ahead of the arms, while its whole-area centroid stays over the border.
    row_alpha=[sum(foreground(x,y) for x in range(128)) for y in range(256)]
    glyph_v=sum((y+.5)*a for y,a in enumerate(row_alpha))/sum(row_alpha)/256
    side_alpha=[foreground(32,y) for y in range(256)]
    tip_v=sum((y+.5)*a for y,a in enumerate(alpha))/sum(alpha)/256
    side_v=sum((y+.5)*a for y,a in enumerate(side_alpha))/sum(side_alpha)/256
    assert abs(slat_length/8-.67)<.004
    assert abs((.5-glyph_v)*48-16)<.03
    assert 1.65<(side_v-tip_v)*48<1.8 # Shallow point; V=0 faces source -> target.
    shadows=[pixel for pixel in wave_texture.getdata() if pixel[0]==0 and 0<pixel[3]]
    assert len(shadows)>100 and max(pixel[3] for pixel in shadows)<=72
    print('Passed native fading conveyor and path comparisons: wave backend, shadowed white chevrons/50% peak, correct texture travel axis/67:33 stroke gaps, preserved endpoints/comparison yield RGB, caches, owner isolation, missing-art fallback and shutdown.')
