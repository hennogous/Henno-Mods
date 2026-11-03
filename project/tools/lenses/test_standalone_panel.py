"""Standalone Supply Chains menu tests; UI calls are mocked, shaders are not rendered."""
from pathlib import Path

LENSES = Path(__file__).resolve().parents[3] / 'Civ Supply Chains/Lua_UI/Lenses'


def test_supply_chains_panel(runtime, colors, more_lenses=None, install_more=None,
                             lifecycle_scenario=None, panel_source=None):
    for with_more in ([False, True] if more_lenses and not lifecycle_scenario else [False]):
        lua = runtime()
        lua.execute('''
            local function event()
                local callbacks={}
                return setmetatable({
                    Add=function(fn) callbacks[#callbacks+1]=fn end,
                    Remove=function(fn) for i=#callbacks,1,-1 do if callbacks[i]==fn then table.remove(callbacks,i) end end end,
                    Count=function() return #callbacks end,
                }, {__call=function(_,...) local pending={table.unpack(callbacks)}; for _,fn in ipairs(pending) do fn(...) end end})
            end
            local function events() return setmetatable({}, {__index=function(t,k) local e=event(); rawset(t,k,e); return e end}) end
            Events=events(); LuaEvents=events()
            debugLines={}; print=function(message) debugLines[#debugLines+1]=message end
            function control()
                return {hidden=false,height=300,width=190,children={},
                    GetTextButton=function(self) return self end,
                    RegisterCheckHandler=function(self,fn) self.checkHandler=fn end,
                    LocalizeAndSetText=function(self,text) self.text=text end,
                    SetText=function(self,text) self.text=text end,
                    SetColor=function(self,color) self.color=color end,
                    SetTexture=function(self,texture) self.texture=texture end,
                    SetToolTipString=function(self,text) self.tooltip=text end,
                    SetCheck=function(self,checked) self.checked=checked; if self.checkHandler then self.checkHandler(checked) end end,
                    IsChecked=function(self) return self.checked end,
                    SetSelected=function(self,v) self.selected=v end,
                    RegisterCallback=function(self,_,fn) self.click=fn end,
                    SetHide=function(self,hidden) self.hidden=hidden end,
                    IsVisible=function(self) return not self.hidden end,
                    HasFocus=function(self) return self.focused==true end,
                    GetChildren=function(self) return self.children end,
                    SetSizeY=function(self,height) self.height=height end,
                    GetSizeY=function(self) return self.height end,
                    GetSizeX=function(self) return self.width end,
                    SetOffsetX=function(self,x) self.x=x end,
                    SetOffsetY=function(self,y) self.y=y end,
                    CalculateSize=function() end,ReprocessAnchoring=function() end,
                    ChangeParent=function(self,owner)
                        self.owner=owner; owner.children[#owner.children+1]=self
                        if owner==menuStack then owner.height=owner.height+35 end
                    end,
                    DestroyChild=function(self,child) child.destroyed=true end,
                }
            end
            choices={}; legends={}
            InstanceManager={new=function(_,name) return {
                GetInstance=function()
                    if name=='QuarterChoiceInstance' then
                        local button=control(); choices[#choices+1]=button; return {QuarterButton=button}
                    end
                    local row={LegendColor=control(),LegendLabel=control()}; legends[#legends+1]=row; return row
                end,
                ResetInstances=function() if name=='QuarterChoiceInstance' then choices={} else legends={} end end,
            } end}
            Controls={}
            for _,name in ipairs({'SupplyChainsLensEntry','SupplyChainsLensPanel','SupplyChainsLensDisplay',
                'LensHeader','QuarterChoices','QuarterScroll','LegendStack','LegendScroll','LensTitle','CloseButton'}) do Controls[name]=control() end
            -- Instrument the single native radio binding implicated in teardown;
            -- other controls retain the existing ordinary fixture behavior.
            entrySetCheckCalls=0; entryIsCheckedCalls=0; teardownBegun=false
            local entry=Controls.SupplyChainsLensEntry
            local realSetCheck, realIsChecked=entry.SetCheck, entry.IsChecked
            entry.SetCheck=function(self,checked)
                entrySetCheckCalls=entrySetCheckCalls+1
                assert(not teardownBegun, 'entry SetCheck invoked after teardown begins')
                return realSetCheck(self,checked)
            end
            entry.IsChecked=function(self)
                entryIsCheckedCalls=entryIsCheckedCalls+1
                assert(not teardownBegun, 'entry IsChecked invoked after teardown begins')
                return realIsChecked(self)
            end
            Controls.SupplyChainsLensPanel.hidden=true; Controls.SupplyChainsLensDisplay.hidden=true
            menuStack=control(); menuPanel=control(); menuChooser=control(); hud=control(); nativeModal=control(); nativeButton=control(); nativeTitle=control(); nativeKeyPanel=control()
            root=control(); editContainer=control(); edit=control(); root.children={editContainer}; editContainer.children={edit}
            menuReady=false
            ContextPtr={SetInitHandler=function(_,fn) init=fn end,SetShutdown=function(_,fn) shutdown=fn end,
                SetInputHandler=function(_,fn) input=fn end,
                SetRefreshHandler=function(_,fn) inputRefresh=fn end,
                SetUpdate=function(_,fn) frameUpdate=fn end, ClearUpdate=function() frameUpdate=nil end,
                RequestRefresh=function() refreshPending=true end,
                ClearRequestRefresh=function() refreshPending=false end,
                SetAppLostFocusHandler=function(_,fn) lostFocus=fn end,
                SetAppRegainedFocusHandler=function(_,fn) regainedFocus=fn end,
                LookUpControl=function(_,path)
                    if not menuReady then return nil end
                    return ({['/InGame']=root,['/InGame/MinimapPanel/LensToggleStack']=menuStack,
                        ['/InGame/MinimapPanel/LensPanel']=menuPanel,['/InGame/HUD']=hud,
                        ['/InGame/MinimapPanel/LensChooserList']=menuChooser,
                        ['/InGame/ModalLensPanel']=nativeModal,['/InGame/ModalLensPanel/LensText']=nativeTitle,['/InGame/ModalLensPanel/KeyPanel']=nativeKeyPanel,['/InGame/MinimapPanel/LensButton']=nativeButton})[path]
                end}
            function lookup(text)
                return ({LOC_OPTIONS_KEY_Q='Q',LOC_HUD_CSC_BAKERS_LENS="Bakers' Quarter",LOC_HUD_CSC_TAILORS_LENS="Tailors' Quarter",LOC_HUD_APPEAL_LENS='Appeal'})[text] or text
            end
            Locale={Lookup=lookup,ToUpper=string.upper}
            Mouse={eLClick=1}; Keys={VK_ESCAPE=27,Q=81,['1']=49,['2']=50}; KeyEvents={KeyDown=1,KeyUp=2}
            InputContext={World=16}; activeContext=16; recording=false; editor=false; actionEnabled=true
            contextStack={}; maskPushes=0; maskPops=0; nativeDigits=0; nativeResources=0
            globalInstalls=0
            UIManager={SetGlobalInputHandler=function(_,fn) globalInstalls=globalInstalls+1; globalInput=fn end,
                ClearGlobalInputHandler=function() globalInput=nil end}
            resourceBinding='Q'; resourceIcons=true; resourceChanges=0
            Input={GetActiveContext=function() return activeContext end,
                PushActiveContext=function(value)
                    contextStack[#contextStack+1]=activeContext; activeContext=value; maskPushes=maskPushes+1
                end,
                PopContext=function()
                    assert(#contextStack>0); activeContext=table.remove(contextStack); maskPops=maskPops+1
                end,
                IsRecordingGestures=function() return recording end,
                GetActionId=function(name) return name=='ToggleResources' and 77 or name end,
                GetActionEnabled=function(id) assert(id==77); return actionEnabled end,
                GetGestureDisplayString=function(id,index) assert(id==77); return index==0 and resourceBinding or nil end}
            GameConfiguration={IsWorldBuilderEditor=function() return editor end}
            GameCapabilities={HasCapability=function(name) assert(name=='CAPABILITY_DISPLAY_MINIMAP_RESOURCES'); return true end}
            UserConfiguration={ShowMapResources=function(value)
                if value~=nil then resourceIcons=value; resourceChanges=resourceChanges+1 end
                return resourceIcons
            end}
            UI.PlaySound=function() end
            function key(message,code,modifier)
                local event={GetKey=function() return code end, GetMessageType=function() return message end,
                    IsControlDown=function() return modifier=='Control' end,
                    IsAltDown=function() return modifier=='Alt' end,
                    IsShiftDown=function() return modifier=='Shift' end}
                -- The native global observer's return is discarded. Deliberately
                -- dispatch the action matcher before the ordinary context handler
                -- so a local return true cannot hide a leaked vanilla action.
                local consumed=false
                -- The live log delivers a physical edge more than once through
                -- the global observer, with a restored World context in between.
                for pass=1,(inputDispatchPasses or 1) do
                    if globalInput then globalInput(event) end
                    local masked=activeContext==0x20000000
                    if activeContext==16 and modifier==nil and not recording and not editor
                        and Game.GetLocalPlayer()~=-1 and not (edit.focused and not editContainer.hidden) then
                        if code==81 and actionEnabled and resourceBinding=='Q' then
                            nativeResources=nativeResources+1
                            resourceIcons=not resourceIcons
                        elseif (code==49 or code==50) and (mode==0 or mode==9 or extraMapModes[mode]) then
                            nativeDigits=nativeDigits+1
                            engineLens=code==49 and 'Religion' or 'Continent'
                            UI.SetInterfaceMode(9); Events.LensLayerOn('Native_'..engineLens)
                        end
                    end
                    local handled=input(event)
                    if refreshPending and not deferRefresh then inputRefresh() end
                    if not deferRefresh then Events.SystemUpdateUI(); if FlushMoreCallbacks then FlushMoreCallbacks() end; if frameUpdate then frameUpdate() end end
                    consumed=consumed or masked or handled
                end
                return consumed
            end
            mode=0; engineLens='Default'; setActiveCalls={}; nativeAreas={}; layers={}
            InterfaceModeTypes={SELECTION=0,VIEW_MODAL_LENS=9,DISTRICT_PLACEMENT=7,
                BUILDING_PLACEMENT=8,CINEMATIC=10,FULLSCREEN_MAP=11,DEBUG=12,
                CITY_MANAGEMENT=13,CITY_SELECTION=14,MOVE_TO=15}
            -- Include the actual rejected mode value, without assuming which
            -- named enum it represents in the native build.
            extraMapModes={[12]=true,[13]=true,[14]=true,[15]=true,[372882022]=true}
            UI.GetInterfaceMode=function() return mode end
            modeNotifications={}
            function deliverMode(old,new)
                -- Native minimap hides its chooser on the modal exit, even
                -- when this queued event is older than the actual current mode.
                if old==9 and new~=9 then menuPanel.hidden=true end
                if new==0 and UILens then nativeReset=true; UILens.SetActive('Default'); nativeReset=false end
                Events.InterfaceModeChanged(old,new)
            end
            UI.SetInterfaceMode=function(new)
                local old=mode; mode=new
                if deferModeNotifications then modeNotifications[#modeNotifications+1]={old,new}
                else deliverMode(old,new) end
                if new==9 and modeCleanup then Events.LensLayerOn('Hex_Coloring_Appeal_Level') end
            end
            function flushModeNotifications()
                local pending=modeNotifications; modeNotifications={}
                for _,change in ipairs(pending) do deliverMode(change[1],change[2]) end
            end
            UILens={GetOverlay=GetTestOverlay,CreateLensLayerHash=function(name) return name end,
                IsLensActive=function(name) return engineLens==name end,
                IsLayerOn=function(layer) return layers[layer] or false end,
                SetActive=function(name)
                    engineLens=name; if not nativeReset then setActiveCalls[#setActiveCalls+1]=name end
                    local carrier='Hex_Coloring_Appeal_Level'
                    if name=='Appeal' and not layers[carrier] then layers[carrier]=true; Events.LensLayerOn(carrier)
                    elseif name~='Appeal' and layers[carrier] then layers[carrier]=false; Events.LensLayerOff(carrier) end
                end,
                ClearLayerHexes=function(layer) nativeAreas[layer]={} end,
                SetLayerHexesColoredArea=function(layer,player,plots,color)
                    color=color % 0x1000000 + 0x80000000 -- Native fixed-alpha Appeal path.
                    nativeAreas[layer]=nativeAreas[layer] or {}
                    local assigned={}; for _,plot in ipairs(plots) do assigned[plot]=true end
                    for oldColor,oldPlots in pairs(nativeAreas[layer]) do
                        local retained={}; for _,plot in ipairs(oldPlots) do if not assigned[plot] then retained[#retained+1]=plot end end
                        nativeAreas[layer][oldColor]=retained
                    end
                    nativeAreas[layer][color]=plots
                end}
            resetWorld(3,1)
            for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
            world[1].resource=GameInfo.Resources.RESOURCE_WHEAT.Index; world[1].improvement=0
            world[2].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[2].improvement=0
            world[3].district=GameInfo.Districts.DISTRICT_WONDER.Index
            world[3].wonder=GameInfo.Buildings.BUILDING_BOLSHOI_THEATRE.Index; world[3].complete=true
            function manualVisible()
                local fill=outlines.CSC_QuarterLens_Fill
                local tint=outlines.CSC_QuarterLens_Tint
                return CSC_QuarterLensSupport.NativeLensFillOwned and layers.Hex_Coloring_Appeal_Level
                    and ((tint and tint.visible) or (fill and fill.visible) or next(nativeAreas.Hex_Coloring_Appeal_Level or {})~=nil)
            end
            function fillContains(color,index)
                for _,p in ipairs((nativeAreas.Hex_Coloring_Appeal_Level or {})[color] or {}) do if p==index then return true end end
                local tint=outlines.CSC_QuarterLens_Tint
                if tint and tint.visible then
                    for _,p in ipairs(tint.tints[color] or {}) do if p==index then return true end end
                end
                local fill=outlines.CSC_QuarterLens_Fill
                if fill and fill.visible then
                    local suffixes={BASE={'BASE_UNIMPROVED','BASE_IMPROVED'},SPEC={'SPEC_UNIMPROVED','SPEC_IMPROVED'},SALE={'SALE_UNREADY','SALE_DISTRICT'},QUARTER={'QUARTER_EMPTY','QUARTER'}}
                    for channel,style in pairs(fill.styles) do
                        local kind,state=style:match('CSC_Lens_Fill_([%u_]+)_(%a+)$')
                        local suffix=suffixes[kind] and suffixes[kind][state=='Ready' and 2 or 1] or kind..(state=='Ready' and '' or '_EMPTY')
                        if UI.GetColorValue('COLOR_CSC_LENS_'..suffix)==color then
                            for _,plot in ipairs(fill.channels[channel]) do if plot==index then return true end end
                        end
                    end
                end
                return false
            end
        ''')
        if with_more:
            install_more(lua, more_lenses)
            lua.execute('''
                moreModal.g_ModLensModalPanel.ML_BUILDER=CSC_QuarterLensSupport.GetLensLegend('BAKERS')
                -- The shared More callback fixture resets Locale; keep this
                -- test's real localized key display value for native bindings.
                Locale.Lookup=lookup; Locale.ToUpper=string.upper
            ''')
        original_include = lua.globals().include
        lua.globals().include = lambda name: original_include(name) if name not in ('InstanceManager', 'InputSupport') else None
        lua.execute((Path(panel_source) if panel_source else LENSES / 'CSC_SupplyChainsLensPanel.lua').read_text(encoding='utf-8-sig'))
        if lifecycle_scenario:
            cases = {
                'unopened_close': '''
                    menuReady=true; Events.LoadScreenClose()
                    Events.LocalPlayerChanged(); Events.LocalPlayerChanged()
                    Events.InterfaceModeChanged(0,0)
                    assert(entrySetCheckCalls==0, 'unopened close called entry SetCheck')
                ''',
                'unopened_shutdown': '''
                    menuReady=true; Events.LoadScreenClose()
                    local checks, queries=entrySetCheckCalls, entryIsCheckedCalls
                    teardownBegun=true; shutdown()
                    assert(entrySetCheckCalls==checks and entryIsCheckedCalls==queries,
                        'unopened shutdown touched entry radio binding')
                ''',
                'active_shutdown': '''
                    menuReady=true; Events.LoadScreenClose()
                    LuaEvents.CSC_SupplyChainsLens_OpenPanel('BAKERS')
                    assert(mode==9 and Controls.SupplyChainsLensEntry.checked)
                    local checks, queries=entrySetCheckCalls, entryIsCheckedCalls
                    teardownBegun=true; shutdown()
                    assert(entrySetCheckCalls==checks and entryIsCheckedCalls==queries,
                        'active shutdown touched entry radio binding')
                ''',
                'normal_toggle': '''
                    menuReady=true; Events.LoadScreenClose()
                    Controls.SupplyChainsLensEntry:SetCheck(true)
                    Controls.SupplyChainsLensEntry.click()
                    assert(mode==9 and Controls.SupplyChainsLensEntry.checked)
                    Controls.CloseButton.click()
                    assert(mode==0 and not Controls.SupplyChainsLensEntry.checked)
                    Controls.SupplyChainsLensEntry:SetCheck(true)
                    Controls.SupplyChainsLensEntry.click()
                    assert(mode==9 and Controls.SupplyChainsLensEntry.checked)
                    Controls.SupplyChainsLensEntry:SetCheck(false)
                    Controls.SupplyChainsLensEntry.click()
                    assert(mode==0 and not Controls.SupplyChainsLensEntry.checked)
                ''',
            }
            lua.execute(cases[lifecycle_scenario])
            print(f'Passed standalone panel lifecycle: {lifecycle_scenario}')
            continue
        lua.execute('''
            assert(#choices==2 and choices[1].text=='LOC_HUD_CSC_BAKERS_LENS' and choices[2].text=='LOC_HUD_CSC_TAILORS_LENS')
            Events.LoadScreenClose(); assert(Controls.SupplyChainsLensEntry.owner==nil)
            LuaEvents.CSC_SupplyChainsLens_OpenPanel(); assert(mode==0) -- Missing UI is harmless.
            menuReady=true; Events.LoadScreenClose(); Events.LoadScreenClose()
            assert(#menuStack.children==1 and Controls.SupplyChainsLensEntry.owner==menuStack)
            -- Native radios live in a different UI context: reparenting CSC's
            -- row alone cannot uncheck Empire (or optional modded choices).
            empireRadio=control(); empireRadio.checked=true
            optionalContainer=control(); optionalRadio=control(); optionalRadio.checked=true
            optionalContainer.children={optionalRadio}
            empireRadio.click=function() error('Must not click the previous lens to uncheck it') end
            menuStack.children[#menuStack.children+1]=empireRadio
            menuStack.children[#menuStack.children+1]=optionalContainer
            assert(Controls.SupplyChainsLensPanel.owner==menuPanel and Controls.SupplyChainsLensPanel.x==195)
            assert(Controls.SupplyChainsLensDisplay.owner==nativeModal and menuPanel.height==335)
            Controls.SupplyChainsLensEntry.checked=true; Controls.SupplyChainsLensEntry.click()
            assert(mode==9 and engineLens=='Appeal' and not Controls.SupplyChainsLensDisplay.hidden)
            assert(not Controls.SupplyChainsLensPanel.hidden and not nativeModal.hidden and Controls.LensHeader.hidden and nativeKeyPanel.hidden)
            assert(Controls.LensTitle.text=="BAKERS' QUARTER" and #legends==8)
            assert(nativeTitle.text=="BAKERS' QUARTER")
            assert(legends[1].LegendColor.color==UI.GetColorValue('COLOR_CSC_LENS_BAKERS_QUARTER_OUTLINE'))
            assert(legends[1].LegendColor.texture=='Controls_KeySwatchHexEmpty')
            assert(legends[2].LegendColor.texture=='Controls_KeySwatchHex')
            assert(legends[3].LegendColor.texture=='Controls_KeySwatchHexEmpty')
            assert(legends[4].LegendColor.texture=='Controls_KeySwatchHex')
            assert(legends[3].LegendColor.color==UI.GetColorValue('COLOR_CSC_LENS_BASE_OUTLINE'))
            assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'),0))
            assert(layers.Hex_Coloring_Appeal_Level and not outlines.CSC_QuarterLens.visible)
            assert(OutlineContains('Lens',0))
            assert(not empireRadio.checked and not optionalRadio.checked and Controls.SupplyChainsLensEntry.checked)
            choices[2].click()
            assert(Controls.LensTitle.text=="TAILORS' QUARTER")
            assert(legends[1].LegendColor.color==UI.GetColorValue('COLOR_CSC_LENS_TAILORS_QUARTER_OUTLINE'))
            -- Match More Lenses: no Selection round trip while changing a
            -- modal lens, including takeover from another native lens. Native
            -- WorldInput resets the active lens to Default on Selection.
            deferModeNotifications=true
            choices[1].click()
            assert(mode==9 and #modeNotifications==0 and not menuPanel.hidden)
            assert(not Controls.SupplyChainsLensPanel.hidden)
            -- Take over another native lens directly, retaining the chooser.
            engineLens='Religion'; choices[1].click()
            assert(mode==9 and #modeNotifications==0)
            flushModeNotifications()
            assert(manualVisible() and not Controls.SupplyChainsLensDisplay.hidden)
            assert(Controls.LensTitle.text=="BAKERS' QUARTER")
            assert(not menuPanel.hidden); if frameUpdate then frameUpdate() end
            assert(not menuPanel.hidden and not Controls.SupplyChainsLensPanel.hidden)
            engineLens='Religion'
            empireRadio.checked=true
            assert(key(1,81) and key(1,50))
            assert(not empireRadio.checked and Controls.SupplyChainsLensEntry.checked)
            assert(#modeNotifications==0); flushModeNotifications()
            assert(manualVisible() and not Controls.SupplyChainsLensDisplay.hidden)
            assert(Controls.LensTitle.text=="TAILORS' QUARTER")
            assert(key(2,50) and key(2,81))
            -- Conversely, the newest real exit closes, and an older modal event
            -- delivered after that exit cannot repaint or reopen the overlay.
            choices[1].click(); UI.SetInterfaceMode(0); flushModeNotifications()
            assert(not manualVisible() and Controls.SupplyChainsLensDisplay.hidden)
            assert(mode==0)
            deferModeNotifications=false; choices[2].click()
            assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'),1))
            assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_SALE_DISTRICT'),2))
            assert(OutlineContains('Lens',1))
            Events.LensLayerOn('MapLabels_Deserts')
            assert(manualVisible()) -- Labels are not a lens switch.
            world[2].pillaged=true; Events.GameCoreEventPublishComplete()
            assert(OutlineContains('Lens',1))
            assert(not fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'),1))
            assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_UNIMPROVED'),1))
            assert(not fillContains(UI.GetColorValue('COLOR_CSC_LENS_IGNORE'),1))
            world[2].pillaged=false; Events.GameCoreEventPublishComplete()
            -- Closing the main menu hides its child chooser, without clearing the map.
            menuPanel:SetHide(true); assert(manualVisible())
            -- A vanilla lens takes ownership, including a switch directly to Appeal.
            nativeAreas.Hex_Coloring_Appeal_Level={[999]={2}}
            Controls.SupplyChainsLensEntry:SetCheck(false)
            local previousMorePaints=morePaints
            if moreMini then moreMini.SetActiveModdedLens('ML_BUILDER') end
            engineLens='Appeal'; Events.LensLayerOn('Hex_Coloring_Appeal_Level')
            assert(not manualVisible() and not outlines.CSC_QuarterLens_Ready.visible)
            assert(nativeAreas.Hex_Coloring_Appeal_Level[999][1]==2)
            assert(not nativeModal.hidden and Controls.SupplyChainsLensDisplay.hidden)
            if moreMini then assert(morePaints==previousMorePaints+1 and #moreDiagnostics==0) end
            Events.GameCoreEventPublishComplete(); assert(not manualVisible())
            -- A submenu choice must activate even after native takeover closed
            -- the controller; merely selecting/repainting an inactive lens fails.
            modeCleanup=true; choices[2].click(); modeCleanup=false
            assert(mode==9 and manualVisible())
            assert(choices[2].checked and not choices[1].checked)
            assert(input({GetKey=function() return 27 end,GetMessageType=function() return 1 end}))
            assert(input({GetKey=function() return 27 end,GetMessageType=function() return 2 end}))
            assert(mode==0 and not manualVisible() and Controls.SupplyChainsLensDisplay.hidden)
            LuaEvents.CSC_SupplyChainsLens_OpenPanel('BAKERS')
            UI.SetInterfaceMode(7)
            assert(not manualVisible() and not Controls.SupplyChainsLensEntry.checked)
            LuaEvents.CSC_SupplyChainsLens_OpenPanel('TAILORS'); Events.LocalPlayerChanged()
            assert(mode==0 and not manualVisible())
            local before=#setActiveCalls
            LuaEvents.CSC_SupplyChainsLens_OpenPanel('INVALID'); assert(#setActiveCalls==before)
            -- Native single-key lens bindings stay unconsumed without Q.
            assert(not key(1,49) and not key(2,49) and not key(1,50) and not key(2,50))
            assert(#setActiveCalls==before)
            -- A plain Q tap keeps the default resource toggle; repeat cannot
            -- toggle repeatedly. Respect removed/disabled resource bindings.
            inputDispatchPasses=2
            assert(key(1,81) and key(1,81) and key(2,81))
            assert(resourceChanges==1 and not resourceIcons)
            inputDispatchPasses=nil
            resourceBinding='R'; assert(key(1,81) and key(2,81)); assert(resourceChanges==1)
            resourceBinding='Q'; actionEnabled=false
            assert(key(1,81) and key(2,81)); assert(resourceChanges==1); actionEnabled=true
            -- Open directly while closed, without invoking either native digit
            -- lens or the resource toggle. Repeat opens only once.
            assert(key(1,81) and key(1,49))
            assert(mode==9 and Controls.LensTitle.text=="BAKERS' QUARTER")
            before=#setActiveCalls
            assert(key(1,49) and #setActiveCalls==before)
            assert(key(2,81) and key(2,49)) -- Q released first still captures digit up.
            assert(resourceChanges==1)
            assert(key(1,81) and key(1,50) and key(2,50))
            assert(Controls.LensTitle.text=="TAILORS' QUARTER")
            assert(key(1,49) and key(2,49)) -- Switch again while still holding Q.
            assert(Controls.LensTitle.text=="BAKERS' QUARTER")
            assert(key(2,81) and resourceChanges==1)
            assert(nativeResources==0) -- Plain Q/chords never leak native resource actions.
            -- Regression from the human log: a second copy of number-up used
            -- to lose capture and launch Religion after Bakers had opened.
            for _,passes in ipairs({2,3}) do
                inputDispatchPasses=passes
                local digitsBefore=nativeDigits
                local resourcesBefore=resourceChanges
                assert(key(1,81) and key(1,49))
                assert(key(2,81) and key(2,49)) -- Q up first.
                assert(engineLens=='Appeal' and Controls.LensTitle.text=="BAKERS' QUARTER")
                assert(nativeDigits==digitsBefore and resourceChanges==resourcesBefore)
                assert(key(1,81) and key(1,50))
                assert(key(2,50) and key(2,81)) -- Number up first.
                assert(engineLens=='Appeal' and Controls.LensTitle.text=="TAILORS' QUARTER")
                assert(nativeDigits==digitsBefore and resourceChanges==resourcesBefore)
                -- The release latch must not capture a fresh standalone press.
                assert(not key(1,49) and not key(2,49))
                assert(engineLens=='Religion' and nativeDigits>digitsBefore)
                Controls.CloseButton.click()
            end
            inputDispatchPasses=nil
            Controls.CloseButton.click(); before=#setActiveCalls
            -- Native TunerUtilities can replace UIManager's single global slot
            -- after addon init. Recover before a chord in default map view.
            local digitsBefore=nativeDigits
            local resourcesBefore=nativeResources
            globalInput=function() end
            Events.LoadScreenClose()
            globalInput=function() end -- A later callback in the same handoff.
            Events.SystemUpdateUI()
            assert(key(1,81),'Lost Q observer after game-load handoff')
            assert(key(1,49) and key(2,49) and key(2,81))
            assert(Controls.LensTitle.text=="BAKERS' QUARTER" and engineLens=='Appeal')
            assert(nativeDigits==digitsBefore and nativeResources==resourcesBefore)
            local installsAfterHandoff=globalInstalls
            Events.SystemUpdateUI();Events.SystemUpdateUI()
            assert(globalInstalls==installsAfterHandoff,'Observer reinstalled on ordinary UI ticks')
            Controls.CloseButton.click()
            lostFocus();globalInput=function() end
            regainedFocus()
            globalInput=function() end
            Events.SystemUpdateUI()
            assert(key(1,81) and key(1,50) and key(2,50) and key(2,81))
            assert(Controls.LensTitle.text=="TAILORS' QUARTER" and engineLens=='Appeal')
            assert(nativeDigits==digitsBefore and nativeResources==resourcesBefore)
            Controls.CloseButton.click()
            -- An immediate press on regaining focus works before its UI tick;
            -- the settled registration must preserve the held Q state.
            globalInput=function() end;regainedFocus()
            assert(key(1,81) and key(1,49) and key(2,49) and key(2,81))
            assert(nativeDigits==digitsBefore and nativeResources==resourcesBefore)
            Controls.CloseButton.click();before=#setActiveCalls
            -- Previously rejected map modes must capture the Q prefix before
            -- vanilla 1/2 sees a bare lens action. Match the live failed mode too.
            for _,startMode in ipairs({12,13,14,15,372882022}) do
                local digitsBefore=nativeDigits
                for _,digit in ipairs({49,50}) do
                    UI.SetInterfaceMode(startMode)
                    assert(key(1,81) and key(1,digit) and key(2,digit) and key(2,81))
                    assert(nativeDigits==digitsBefore and engineLens=='Appeal')
                    assert(Controls.LensTitle.text==(digit==49 and "BAKERS' QUARTER" or "TAILORS' QUARTER"))
                    Controls.CloseButton.click()
                end
                -- Bare digit retains vanilla behaviour in that same map mode.
                UI.SetInterfaceMode(startMode)
                assert(not key(1,49) and not key(2,49))
                assert(nativeDigits>digitsBefore and engineLens=='Religion')
                Controls.CloseButton.click()
            end
            -- A map-mode transition between Q-down and digit-down must keep
            -- the prefix, rather than cancelling it before 1 arrives.
            UI.SetInterfaceMode(0)
            local digitsBefore=nativeDigits
            assert(key(1,81)); UI.SetInterfaceMode(372882022)
            assert(key(1,49) and key(2,81) and key(2,49))
            assert(engineLens=='Appeal' and nativeDigits==digitsBefore)
            Controls.CloseButton.click();before=#setActiveCalls
            -- Number already held before Q does not become a shortcut by repeat.
            assert(not key(1,49)); assert(key(1,81)); assert(not key(1,49))
            assert(not key(2,49)); assert(key(2,81))
            assert(#setActiveCalls==before and resourceChanges==1)
            -- Do not steal combinations involving real modifiers or unknown digits.
            for _,modifier in ipairs({'Control','Alt','Shift'}) do
                assert(not key(1,81,modifier) and not key(1,49,modifier))
                assert(not key(2,49,modifier) and not key(2,81,modifier))
            end
            assert(key(1,81)); assert(not key(1,51) and not key(2,51)); assert(key(2,81))
            assert(#setActiveCalls==before and resourceChanges==1)
            -- Text focus is found recursively, including unnamed/reparented
            -- controls. A hidden branch must not disable world shortcuts.
            edit.focused=true
            assert(not key(1,81) and not key(1,49) and not key(2,49) and not key(2,81))
            editContainer.hidden=true
            assert(key(1,81) and key(1,50) and key(2,50) and key(2,81))
            assert(Controls.LensTitle.text=="TAILORS' QUARTER")
            editContainer.hidden=false; edit.focused=false; Controls.CloseButton.click()
            before=#setActiveCalls
            for _,blocked in ipairs({'popup','recording','editor','placement','building','cinematic','fullscreen','observer'}) do
                local oldPlayer=Game.GetLocalPlayer
                if blocked=='popup' then activeContext=256
                elseif blocked=='recording' then recording=true
                elseif blocked=='editor' then editor=true
                elseif blocked=='placement' then UI.SetInterfaceMode(7)
                elseif blocked=='building' then UI.SetInterfaceMode(8)
                elseif blocked=='cinematic' then UI.SetInterfaceMode(10)
                elseif blocked=='fullscreen' then UI.SetInterfaceMode(11)
                elseif blocked=='observer' then Game.GetLocalPlayer=function() return -1 end end
                assert(not key(1,81) and not key(1,50) and not key(2,50) and not key(2,81))
                activeContext=16; recording=false; editor=false; Game.GetLocalPlayer=oldPlayer; UI.SetInterfaceMode(0)
            end
            assert(#setActiveCalls==before and resourceChanges==1)
            -- Interrupted prefixes never leak to the next number or become Q taps.
            assert(key(1,81)); lostFocus(); assert(key(2,81))
            assert(not key(1,49) and not key(2,49))
            assert(key(1,81)); UI.SetInterfaceMode(7); assert(key(2,81)); UI.SetInterfaceMode(0)
            assert(not key(1,50) and not key(2,50))
            assert(key(1,81)); Events.LocalPlayerChanged(); assert(key(2,81))
            assert(not key(1,49) and not key(2,49))
            assert(key(1,81)); edit.focused=true; assert(not key(1,49) and not key(2,49))
            edit.focused=false; assert(key(2,81))
            assert(#setActiveCalls==before and resourceChanges==1)
            -- Interrupted captured digit up stays swallowed; if the OS never
            -- sends it, the next fresh standalone digit is not stuck captured.
            assert(key(1,81) and key(1,49)); lostFocus()
            assert(key(2,49) and key(2,81)); Controls.CloseButton.click()
            assert(key(1,81) and key(1,50)); lostFocus(); assert(key(2,81)); Controls.CloseButton.click()
            assert(not key(1,50) and not key(2,50))
            assert(resourceChanges==1)
            -- Model several key events before the deferred refresh. The mask
            -- stays one level deep and is restored after the last dispatch.
            local vanillaBefore=nativeDigits
            deferRefresh=true
            assert(key(1,81)); assert(activeContext==0x20000000 and #contextStack==1)
            assert(key(1,49) and key(2,81) and key(2,49))
            assert(activeContext==0x20000000 and #contextStack==1 and nativeDigits==vanillaBefore)
            inputRefresh(); deferRefresh=false
            assert(activeContext==16 and #contextStack==0)
            Events.SystemUpdateUI() -- Finish the pending activation before the next case.
            -- A context with all visual controls reparented might not refresh;
            -- the native UI tick is an independent bounded restoration path.
            deferRefresh=true; assert(key(1,81)); assert(Events.SystemUpdateUI.Count()==1)
            Events.SystemUpdateUI(); assert(activeContext==16 and Events.SystemUpdateUI.Count()==0)
            assert(key(2,81)); Events.SystemUpdateUI(); deferRefresh=false
            -- A popup can push above our pending mask. Do not pop that popup;
            -- drain only our own mask once it becomes the top context again.
            deferRefresh=true; assert(key(1,81)); Input.PushActiveContext(256)
            lostFocus(); inputRefresh(); assert(activeContext==256 and #contextStack==2)
            assert(not key(2,81)); assert(activeContext==256)
            Input.PopContext(); assert(activeContext==0x20000000)
            Events.SystemUpdateUI()
            inputRefresh(); deferRefresh=false
            assert(activeContext==16 and #contextStack==0 and maskPushes==maskPops)
            -- Native SetActive on the existing Appeal carrier is a no-op.
            -- Force a genuine native layer-on paint when handing it back.
            local appealPaints=0
            Events.LensLayerOn.Add(function(layer)
                if layer=='Hex_Coloring_Appeal_Level' then
                    appealPaints=appealPaints+1
                    nativeAreas[layer]={[777]={1}}
                end
            end)
            for _,quarter in ipairs({'BAKERS','TAILORS'}) do
                LuaEvents.CSC_SupplyChainsLens_OpenPanel(quarter)
                local paintsBefore=appealPaints
                UILens.SetActive('Appeal') -- Native callback before ours.
                assert(appealPaints==paintsBefore,'Same native lens should not repaint')
                Events.InputActionTriggered(Input.GetActionId('LensAppeal'))
                UILens.SetActive('Appeal') -- Native callback after ours is also harmless.
                assert(appealPaints==paintsBefore+1 and engineLens=='Appeal')
                assert(not CSC_QuarterLensSupport.NativeLensFillOwned and nativeAreas.Hex_Coloring_Appeal_Level[777][1]==1)
            end
            assert(frameUpdate==nil)
            -- Clicking our already-checked parent off must close, even though
            -- its check handler runs before its click handler.
            LuaEvents.CSC_SupplyChainsLens_OpenPanel('BAKERS')
            Controls.SupplyChainsLensEntry:SetCheck(false); Controls.SupplyChainsLensEntry.click()
            assert(mode==0 and not manualVisible())
            if moreMini then
                -- Exercise delayed actual More Lenses callbacks: its vanilla
                -- Appeal painter runs after our initial draw; the queued native
                -- context update must then restore the grey background. Private
                -- texture fills survive this shared native-layer repaint.
                deferMoreCallbacks=true
                LuaEvents.CSC_SupplyChainsLens_OpenPanel('BAKERS')
                assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'),0))
                FlushMoreCallbacks()
                empireRadio.checked=true -- A deferred native repaint can reassert its old radio.
                assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'),0))
                assert(nativeAreas.Hex_Coloring_Appeal_Level[0x800003e7]~=nil)
                assert(frameUpdate~=nil); frameUpdate()
                assert(not empireRadio.checked and Controls.SupplyChainsLensEntry.checked)
                assert(fillContains(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'),0))
                assert(nativeAreas.Hex_Coloring_Appeal_Level[0x800003e7]==nil)
                assert(nativeTitle.text=="BAKERS' QUARTER" and nativeKeyPanel.hidden and not nativeModal.hidden)
                assert(#moreDiagnostics==0)
                deferMoreCallbacks=false
            end
            missingArt=true; LuaEvents.CSC_SupplyChainsLens_OpenPanel(); Controls.CloseButton.click(); missingArt=false
            LuaEvents.CSC_SupplyChainsLens_OpenPanel()
            assert(outlines.CSC_QuarterPlacement==nil) -- Manual view never touches placement.
            -- A queued lifecycle repair must not resurrect an unloaded context.
            regainedFocus()
            shutdown()
            local installsAtShutdown=globalInstalls
            Events.SystemUpdateUI()
            assert(globalInstalls==installsAtShutdown)
            assert(globalInput==nil and activeContext==16 and #contextStack==0)
            assert(Events.SystemUpdateUI.Count()==0)
            local sawChoice,sawShortcut,sawMask=false,false,false
            for _,line in ipairs(debugLines) do
                if line:find('Quarter choice clicked=TAILORS',1,true) then sawChoice=true end
                if line:find('shortcut Q+1 -> BAKERS',1,true) then sawShortcut=true end
                if line:find('masked World actions',1,true) then sawMask=true end
            end
            assert(sawChoice and sawShortcut and sawMask)
            assert(not manualVisible() and not outlines.CSC_QuarterLens_Ready.visible)
            assert(Controls.SupplyChainsLensEntry.destroyed and Controls.SupplyChainsLensPanel.destroyed and Controls.SupplyChainsLensDisplay.destroyed)
            assert(menuPanel.height==300)
            assert(Events.InterfaceModeChanged.Count()==0 and Events.LocalPlayerChanged.Count()==0)
            assert(Events.LoadScreenClose.Count()==0 and Events.GameCoreEventPublishComplete.Count()==0)
            assert(LuaEvents.CSC_SupplyChainsLens_OpenPanel.Count()==0 and LuaEvents.CSC_SupplyChainsLens_Refresh.Count()==0)
            for _,name in ipairs(setActiveCalls) do assert(name=='Default' or name=='Appeal') end
        ''')
        print('Passed standalone lens panel ' + ('with actual More Lenses callbacks' if with_more else 'without More Lenses') + ': texture-alpha fills despite native alpha clamp, direct modal switching, deferred carrier repaint, takeover preserves new colours, Q+1/Q+2, uppercase/submenu, debug logs and cleanup.')
