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
        assert(not outlines.CSC_QuarterLens_Services.visible) -- Retired flat sprites.
        assert(ExposedMembers.CSC_QuarterServicePins.Lens.markers[1].icon ==
            'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE')
        s.DrawOverlay('Placement',entries)
        assert(#ExposedMembers.CSC_QuarterServicePins.Placement.markers==1)
        effects[1].active=false;s.DrawOverlay('Lens',entries)
        assert(#ExposedMembers.CSC_QuarterServicePins.Lens.markers==0)
        s.ClearOverlay('Placement');assert(ExposedMembers.CSC_QuarterServicePins.Placement.key==nil)
        effects[1].active=true;s.DrawOverlay('Lens',entries)
        for _,entry in ipairs(entries) do entry.quarterKey='TAILORS' end
        s.DrawOverlay('Lens',entries)
        assert(#ExposedMembers.CSC_QuarterServicePins.Lens.markers==0)
        s.ClearOverlay('Lens')
        local api=GameEffects;GameEffects=nil;check('BAKERS',{});GameEffects=api
        missingArt=true;s.DrawOverlay('Lens',entries);s.ClearOverlay('Lens');missingArt=false
    ''')
    test_pin_controls(lua)
    root = Path(__file__).resolve().parents[3]
    mod = root / 'Civ Supply Chains'
    art = ET.parse(mod / 'ArtDefs/CSC_QuarterResourceBorders.artdef')
    for key, index in [('BAKERS', 0), ('TAILORS', 8)]:
        from PIL import Image
        atlas = Image.open(mod / 'Textures/CSC_Effect_Notifications_100.dds').convert('RGBA')
        original = atlas.crop((index % 8 * 100, index // 8 * 100, index % 8 * 100 + 100, index // 8 * 100 + 100))
        overlay = Image.open(mod / f'Textures/CSC_Lens_Service_{key}.dds').convert('RGBA')
        foreground = overlay.crop((14,14,114,114))
        shadow_pixels = 0
        for source, result in zip(original.getdata(), foreground.getdata()):
            if source[3] == 255:
                assert result == source # Opaque original artwork is untouched.
            assert result[3] >= source[3]
            # A black shadow behind a translucent edge preserves the source's
            # premultiplied colour, within 8-bit compositing rounding.
            for channel in range(3):
                assert abs(result[channel]*result[3]/255-source[channel]*source[3]/255)<=1.5
            if source[3] == 0 and result[3] > 0:
                assert result[:3] == (0,0,0) and result[3] <= 72
                shadow_pixels += 1
        assert shadow_pixels > 50
        assert overlay.getpixel((0,0))[3] == 0
        style = next(r for r in art.findall('.//m_ChildCollections/Element/Element')
                     if r.find('m_Name').get('text') == 'CSC_Lens_Service_'+key)
        values = {r.find('m_ParamName').get('text'): r for r in style.findall('m_Fields/m_Values/Element')}
        assert values['GeomType'].find('m_Value').get('text') == 'RECT_GEO'
        assert values['RotateToAlign'].find('m_bValue').text == 'false'
        assert values['RectDims'].find('m_x').text == '48'
        assert values['RectDims'].find('m_y').text == '48'
    for owner in ('Lens','Placement'):
        layer = next(r for r in art.findall('m_RootCollections/Element/Element')
                     if r.find('m_Name').get('text') == 'CSC_Quarter'+owner+'_Services')
        values = {r.find('m_ParamName').get('text'): r for r in layer.findall('m_Fields/m_Values/Element')}
        assert values['Pass'].find('m_nValue').text == '2'
        assert float(values['Priority'].find('m_fValue').text) > 20
    assert db.execute("SELECT COUNT(*) FROM CSC_AbilityAttachModifiers").fetchone()[0] >= 11
    print('Passed Service pins: actual service icons, exact active recipients, shared MCUIS cumulative tooltip, right-click target, pooled cleanup, grouping, both owners and teardown. Legacy sprite art remains a valid unused asset.')


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
        Events=events();LuaEvents=events();Mouse={eRClick=2}
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
                SetIcon=function(self,icon,size) self.icon=icon;self.size=size;pinCalls=pinCalls+1 end,
                SetToolTipString=function(self,text) self.tooltip=text;pinCalls=pinCalls+1 end,
                RegisterCallback=function(self,button,fn) assert(button==Mouse.eRClick);self.click=fn;pinCalls=pinCalls+1 end,
                ClearCallback=function(self) self.click=nil;pinCalls=pinCalls+1 end,
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
                        pin={Anchor=control(),PinRoot=control(),ServiceIcon=control(),ServiceButton=control()}
                        pinCreates=pinCreates+1;pins[#pins+1]=pin
                    end
                    pin.active=true;return pin
                end,
                ReleaseInstance=function(_,pin) pin.active=false;pinReleases=pinReleases+1;pool[#pool+1]=pin end,
            }
        end}
        UI.GridToWorld=function(index) return index*10,index*20 end
        Locale.Lookup=function(key,...)
            local values={key};for _,value in ipairs({...}) do values[#values+1]=tostring(value) end
            return table.concat(values,'|')
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
        assert(pin.ServiceIcon.size==38 and pin.ServiceButton.tooltip==icon.tooltip)
        assert(icon.tooltip==row.AbilityDesc..'|+30|+3|3',icon.tooltip)
        local opened
        LuaEvents.OpenCivilopedia.Add(function(target) opened=target end)
        pin.ServiceButton.click();assert(opened==row.AbilityIconTarget)
        CSC_QuarterLensSupport.DrawOverlay('Lens',entries)
        assert(pinCreates==2 and pinReleases==0) -- Stable instances.
        -- Current effect updates without recreating the pin or reopening lens.
        effects[2].active=false;Events.GameCoreEventPublishComplete()
        assert(pinAt(0)==pin and pin.ServiceButton.tooltip==row.AbilityDesc..'|+20|+2|2')
        -- Exact district subject loss removes the pin, even though another
        -- district in that same city still has a current active Service.
        effects[1].active=false;Events.GameCoreEventPublishComplete()
        assert(pinAt(0)==nil and pinAt(1) and pin.ServiceButton.click==nil)
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
            positions[p.PinRoot.offset[1]..':'..p.PinRoot.offset[2]]=true
            assert(p.ServiceIcon.icon:find('ICON_BUILDING_CSC_BAKERS_',1,true)==1)
        end
        assert(positions['-44:-44.0'] or positions['-44:-44'])
        assert(positions['44:44.0'] or positions['44:44'])
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
            if p.PinRoot.offset[2]==-44 then top=top+1 else assert(p.PinRoot.offset[2]==44);bottom=bottom+1 end
        end
        assert(top==1 and bottom==2)
        LuaEvents.CSC_QuarterServicePins_Update('Lens','BAKERS',{markers[1],markers[2]})
        assert(#activePins()==2)
        for _,p in ipairs(activePins()) do assert(p.PinRoot.offset[2]==0) end
        Events.GameCoreEventPublishComplete();assert(#activePins()==4)
        -- Placement owns the markers briefly; clearing it restores manual lens.
        LuaEvents.CSC_QuarterServicePins_Update('Placement','TAILORS',{})
        assert(#activePins()==0)
        LuaEvents.CSC_QuarterServicePins_Update('Placement',nil,{})
        assert(#activePins()==4)
        Events.LocalPlayerChanged();assert(#activePins()==0)
        local calls=pinCalls;shutdown();assert(pinCalls==calls)
        assert(Events.GameCoreEventPublishComplete.Count()==0)
        assert(Events.LoadScreenClose.Count()==0)
        assert(LuaEvents.CSC_QuarterServicePins_Update.Count()==0)
        LuaEvents.CSC_QuarterServicePins_Update('Lens','BAKERS',{});assert(pinCalls==calls)
    ''')
    xml = ET.parse(root / 'Civ Supply Chains/Lua_UI/Lenses/CSC_QuarterServicePins.xml')
    assert xml.getroot().get('Layer') == 'WorldAnchor'
    assert xml.find('.//Image[@Texture="CityBannerProdCircle"]').get('Size') == '60,60'
    assert xml.find('.//Button[@ID="ServiceButton"]').get('Size') == '60,60'
    assert xml.find('.//Container[@ID="PinRoot"]').get('Size') == '80,80'
    assert xml.find('.//Image[@ID="ServiceIcon"]').get('Offset') == '-2,0'
    assert xml.find('.//Image[@ID="ServiceIcon"]').get('Size') == '38,38'
