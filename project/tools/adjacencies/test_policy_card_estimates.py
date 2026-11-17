"""Execute the CSC adapter with installed RMA aggregation/formatting in Lua 5.1.
No game, Workshop file or runtime database is modified.
"""
import argparse
import json
import sys
from pathlib import Path
from test_policy_returns import database
from test_parity import CODE, TESTS, lua_value, untype


def check_context_lifecycle(LuaRuntime):
    """Run the actual adapter in its own globals, with BRS owned elsewhere.

    The previous fixture preloaded RMA helpers into CSC's globals. That cannot
    catch replacing BRS's only initialization script and then failing to include
    it. Here CSC has only the public API; original functions must survive even
    when BRS publishes late or never publishes the optional API.
    """
    source = untype((CODE/'CSC_PolicyCardEstimates.lua').read_text(encoding='utf-8-sig'))
    for ready, publish_later in ((True,False),(False,True),(False,False)):
        lua = LuaRuntime(unpack_returned_tuples=True)
        lua.execute('''
            callbacks={}; messages={};
            YieldTypes={FOOD=0,PRODUCTION=1,GOLD=2,SCIENCE=3,CULTURE=4,FAITH=5};
            ExposedMembers={RMA={}};
            GameInfo={PolicyModifiers=function() return function() return nil end end};
            Events={LoadGameViewStateDone={Add=function(fn) table.insert(callbacks,fn) end}};
            originalDecode=function() return 'original decode' end;
            originalCalculate=function(...) return 'original estimate',7,'original tooltip',false end;
            originalFormatter=function() return '' end;
            originalRefresh=function() return 'original refresh' end;
            function publish()
                ExposedMembers.RMA.DecodeModifier=originalDecode;
                ExposedMembers.RMA.CalculateModifierEffect=originalCalculate;
                ExposedMembers.RMA.YieldTableGetInfo=originalFormatter;
                ExposedMembers.RMA.RefreshBaseData=originalRefresh;
            end
            originalTable=ExposedMembers.RMA;
            adapter=setmetatable({}, {__index=_G});
            adapter.print=function(message) table.insert(messages,message) end;
            adapter.include=function(name)
                assert(name ~= 'RealModifierAnalysis', 'must preserve original BRS context');
                if name=='CSC_AdjacencyCore' then
                    adapter.CSC_Adjacency={Initialize=function() end,Rules={},Bits={}};
                else assert(name=='Civ6Common') end
            end;
            function loadAdapter(source)
                local chunk=assert(loadstring(source)); setfenv(chunk,adapter); chunk();
            end
        ''')
        if ready:
            lua.globals().publish()
        lua.globals().loadAdapter(source)
        if not ready:
            lua.execute('assert(ExposedMembers.RMA.CalculateModifierEffect==nil)')
        if publish_later:
            lua.globals().publish()
        lua.execute('for _,callback in ipairs(callbacks) do callback() end')
        if ready or publish_later:
            lua.execute('''
                assert(ExposedMembers.RMA==originalTable);
                assert(ExposedMembers.RMA.RefreshBaseData==originalRefresh);
                assert(DecodeModifier==nil and CalculateModifierEffect==nil,
                    'CSC wrote functions into original/global context');
                local fn=ExposedMembers.RMA.CalculateModifierEffect;
                assert(fn~=originalCalculate);
                local text,impact,tooltip,unknown=fn('Unrelated','TEST',0);
                assert(text=='original estimate' and impact==7 and tooltip=='original tooltip' and unknown==false);
                for _,callback in ipairs(callbacks) do callback() end;
                assert(fn==ExposedMembers.RMA.CalculateModifierEffect);
            ''')
        else:
            lua.execute('assert(ExposedMembers.RMA==originalTable and next(originalTable)==nil)')

    # Check delivery too: the same-basename XML must load CSC's paired script;
    # no action may displace the original RealModifierAnalysis context.
    root = CODE.parents[2]
    actions = json.loads((root/'project/modbuddy/CivSupplyChains.actions.json').read_text())['blocks']['inGameActions']
    action = next(row for row in actions if row['id']=='CSC_PolicyCardEstimates')
    assert action['type']=='AddUserInterfaces'
    assert action['files']==['Lua_UI/Adjacencies/CSC_PolicyCardEstimates.xml']
    assert action['criteria']==['BetterReportScreenMod']
    assert not any(row.get('properties',{}).get('LuaContext')=='RealModifierAnalysis' for row in actions)


def run(args):
    sys.path.insert(0, str(args.dependencies))
    from lupa.lua51 import LuaRuntime
    check_context_lifecycle(LuaRuntime)
    db, rules = database(args.database)
    source = args.analyser.read_text(encoding='utf-8-sig')
    helpers = 'local YieldTypesMap' + source.split('local YieldTypesMap', 1)[1].split('function GetGameInfoIndex', 1)[0]
    aggregation = 'local TOOLTIP_SEP' + source.split('local TOOLTIP_SEP', 1)[1].split('function RefreshBaseData', 1)[0]
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((TESTS / 'world.lua').read_text())
    g = lua.globals()
    for name in ('Districts', 'Policies', 'TypeTags', 'CSC_AdjacencyRules', 'CSC_AdjacencyProviders', 'CSC_AdjacencySources', 'CSC_AdjacencyObjects', 'PolicyModifiers'):
        rows = [dict(row) for row in db.execute('SELECT * FROM ' + name)]
        for i, row in enumerate(rows): row['Index'] = i
        lua.execute('GameInfo.' + name + '=info(' + lua_value(rows) + ')')
    yields = [{'Index': i, 'YieldType': 'YIELD_' + kind, 'Name': kind, 'IconString': '[' + kind + ']'} for i, kind in enumerate(('FOOD','PRODUCTION','GOLD','SCIENCE','CULTURE','FAITH'))]
    lua.execute('GameInfo.Yields=info(' + lua_value(yields) + ')')
    lua.execute("""
        YieldTypes={FOOD=0,PRODUCTION=1,GOLD=2,SCIENCE=3,CULTURE=4,FAITH=5,TOURISM=6,AMENITY=7,HOUSING=8,LOYALTY=9};
        ExposedMembers={RMA={}};
        installCallbacks={};
        Events={LoadGameViewStateDone={Add=function(fn) table.insert(installCallbacks,fn) end}};
        function GetYieldString(kind, amount) return '['..kind..']+'..string.format('%g',amount) end
        active=false; pillaged=false; vanillaCalls=0;
        Players[0].GetCities=function() return {Members=function() local done=false; return function() if not done then done=true; return 1,city end end end} end;
        local getDistricts=city.GetDistricts;
        city.GetDistricts=function(self)
            local manager=getDistricts(self);
            manager.IsPillaged=function() return pillaged end;
            return manager;
        end;
        city.GetID=function() return 7 end;
        Players[0].GetCulture=function() return {IsPolicyActive=function() return active end} end;
        function DecodeModifier(id, ...)
            vanillaCalls=vanillaCalls+1;
            if attachmentMode and id ~= 'FIXTURE_LEAF' then
                return 'Native root',nil,'FIXTURE_LEAF',false,
                    {SubjectReqSetId='PLAYER_HAS_FIXTURE_INFLUENCE'},
                    emptySubjects and {} or {1},'City';
            end
            local impact=YieldTableNew(); impact.GOLD=4;
            if id=='FIXTURE_LEAF' then impact.GOLD=3; end
            return 'Native detail',impact,nil,false,{SubjectReqSetId=nil}, {}, 'District';
        end
    """)
    lua.execute(untype(helpers + aggregation))
    lua.execute('''
        ExposedMembers.RMA.DecodeModifier=DecodeModifier;
        ExposedMembers.RMA.CalculateModifierEffect=CalculateModifierEffect;
        ExposedMembers.RMA.YieldTableGetInfo=YieldTableGetInfo;
        originalRma=ExposedMembers.RMA;
        originalCalculate=CalculateModifierEffect;
    ''')
    def include(name):
        assert name != 'RealModifierAnalysis', 'BRS paired script must not be included or replaced'
        if name != 'Civ6Common':
            lua.execute(untype((CODE / (name + '.lua')).read_text(encoding='utf-8-sig')))
    g.include = include
    include('CSC_PolicyCardEstimates')
    lua.execute('''
        assert(ExposedMembers.RMA == originalRma);
        assert(ExposedMembers.RMA.CalculateModifierEffect ~= originalCalculate);
        local wrapper=ExposedMembers.RMA.CalculateModifierEffect;
        for _,callback in ipairs(installCallbacks) do callback(); callback(); end
        assert(wrapper == ExposedMembers.RMA.CalculateModifierEffect, 'wrapper stacked on reload event');
    ''')
    cases = 0
    for rule in rules:
        for count in (0, 1, 2, 6):
            lua.execute('resetWorld(); for _,p in ipairs(world) do p.district=-1; p.owner=0 end; pillaged=false; active=false')
            g.center.district = g.GameInfo.Districts[rule['DistrictType']].Index
            g.center.complete = True
            for direction in range(count):
                plot = g.Map.GetAdjacentPlot(g.center.x,g.center.y,direction)
                plot.district = g.GameInfo.Districts[rule['CustomAdjacentObject']].Index
                plot.complete = True
            # Use full RMA policy aggregation. Its vanilla stub remains intact;
            # only the exact compiled CSC attachments are intercepted.
            _, impact, _, unknown = g.ExposedMembers.RMA.CalculateModifierEffect('Policy', rule['WhoIsTheOwner'], 0, None, None)
            kind = rule['YieldType'].removeprefix('YIELD_')
            assert impact[kind] == count, (rule['ID'],count,dict(impact))
            assert impact.GOLD > 0 and not unknown
            g.active = True
            text, slotted, _, _ = g.ExposedMembers.RMA.CalculateModifierEffect('Policy', rule['WhoIsTheOwner'], 0, None, None)
            assert slotted[kind] == count
            if count: assert g.GetYieldString(rule['YieldType'], count) in text, (rule['ID'],text)
            g.pillaged = True
            assert g.CalculateModifierEffect('Policy', rule['WhoIsTheOwner'], 0, None, None)[1][kind] == 0
            g.pillaged = False
            g.center.complete = False
            assert g.CalculateModifierEffect('Policy', rule['WhoIsTheOwner'], 0, None, None)[1][kind] == 0
            g.center.complete = True
            assert g.CalculateModifierEffect('Policy', rule['WhoIsTheOwner'], 0, 999, None)[1][kind] == 0
            # Live ownership changes must invalidate the previous call's amount.
            for direction in range(count): g.Map.GetAdjacentPlot(g.center.x,g.center.y,direction).owner = 1
            assert g.CalculateModifierEffect('Policy', rule['WhoIsTheOwner'], 0, None, None)[1][kind] == 0
            cases += 1
    # Mixed Quarter yields must share the ordinary EPC summary, with Food
    # visible even though this installed RMA formatter skips zero-index yields.
    lua.execute("""
        resetWorld(); for _,p in ipairs(world) do p.district=-1; p.owner=0 end;
        pillaged=false; active=false;
        center.district=GameInfo.Districts.DISTRICT_COMMERCIAL_HUB.Index; center.complete=true;
        Map.GetAdjacentPlot(center.x,center.y,0).district=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index;
        Map.GetAdjacentPlot(center.x,center.y,1).district=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index;
        Map.GetAdjacentPlot(center.x,center.y,2).district=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index;
    """)
    text, impact, tooltip, unknown = g.CalculateModifierEffect('Policy','POLICY_ECONOMIC_UNION',0,None,None)
    assert impact.FOOD == 1 and impact.CULTURE == 2 and impact.GOLD == 8
    assert '[YIELD_FOOD]+1' in text and '[YIELD_CULTURE]+2' in text and '[YIELD_GOLD]+8' in text
    assert not unknown and '[YIELD_FOOD]+1' in tooltip
    # Preserve BRS's one-attachment fold and empty-subject suppression. Both
    # original wrappers and leaves are decoded by BRS, except exact CSC roots.
    lua.execute('attachmentMode=true; emptySubjects=false')
    text, impact, _, _ = g.ExposedMembers.RMA.CalculateModifierEffect('Policy','POLICY_ECONOMIC_UNION',0,None,None)
    assert impact.FOOD==1 and impact.CULTURE==2 and impact.GOLD==6
    lua.execute('emptySubjects=true')
    assert g.ExposedMembers.RMA.CalculateModifierEffect('Policy','POLICY_ECONOMIC_UNION',0,None,None)[1].GOLD==0
    lua.execute('emptySubjects=false')
    filtered = g.ExposedMembers.RMA.CalculateModifierEffect('Policy','POLICY_ECONOMIC_UNION',0,None,'FIXTURE')[1]
    assert filtered.GOLD==6 and filtered.FOOD==0 and filtered.CULTURE==0
    lua.execute('attachmentMode=false')
    # Missing player cannot invent a CSC benefit; unrelated RMA calls still work.
    assert g.CalculateModifierEffect('Policy','POLICY_TOWN_CHARTERS',99,None,None)[1].FOOD == 0
    original = g.vanillaCalls
    assert g.DecodeModifier('UNRELATED',0,None,None,None)[0] == 'Native detail'
    assert g.vanillaCalls == original + 1
    if args.epc:
        # Execute EPC's actual card renderer against the public API. A successful
        # return is required before RealizeActivePoliciesRows records its instance.
        # Controls are stand-ins; this tests the API boundary, not native animation.
        epc = args.epc.read_text(encoding='utf-8-sig')
        renderer = epc[epc.index('function RealizePolicyCard('):epc.index('function RealizeTabs()')]
        lua.execute('''
            local control={};
            function control:GetSizeY() return 100 end;
            setmetatable(control,{__index=function() return function() end end});
            epcCard=setmetatable({},{__index=function() return control end});
            epcEnv=setmetatable({
                RMA=ExposedMembers.RMA,isBRSActive=true,m_debugShowPolicyIDs=false,
                m_kPolicyCatalogData={POLICY_ECONOMIC_UNION={Name='Economic Union',Description='policy description'}},
                GetPolicyBGTexture=function() return 'texture' end
            },{__index=_G});
            function loadRenderer(source)
                local chunk=assert(loadstring(source)); setfenv(chunk,epcEnv); chunk();
            end
        ''')
        g.loadRenderer(untype(renderer))
        g.epcEnv.RealizePolicyCard(g.epcCard,'POLICY_ECONOMIC_UNION')
    # A bad optional forecast must not abort EPC's RealizePolicyCard before it
    # stores the card instance. Clear/retry the fault to prove cache cleanup.
    lua.execute('savedCount=CSC_Adjacency.Count; CSC_Adjacency.Count=function() error("injected site API failure") end')
    result = g.ExposedMembers.RMA.CalculateModifierEffect('Policy','POLICY_ECONOMIC_UNION',0,None,None)
    assert isinstance(result[0], str) and len(result)==4
    if args.epc:
        g.epcEnv.RealizePolicyCard(g.epcCard,'POLICY_ECONOMIC_UNION')
    lua.execute('CSC_Adjacency.Count=savedCount')
    text, impact, _, unknown = g.ExposedMembers.RMA.CalculateModifierEffect('Policy','POLICY_ECONOMIC_UNION',0,None,None)
    assert impact.FOOD==1 and impact.CULTURE==2 and impact.GOLD==8 and not unknown
    print(f'PASS: {cases} RMA policy/unique/count fixtures; separate-context immediate/delayed/missing API, idempotent install, fault recovery, vanilla passthrough and visible summaries')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path, required=True)
    parser.add_argument('--analyser', type=Path, required=True)
    parser.add_argument('--epc', type=Path, help='Installed EPC GovernmentScreen.lua for its actual card renderer')
    run(parser.parse_args())
