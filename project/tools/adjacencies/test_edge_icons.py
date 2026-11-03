"""Offline placement-edge regression against the MAB fork and native collector.

Loads the real CSC wrapper/Firaxis support in isolated Lua. No game connection,
installed-package edits or settings changes. Reference source is read-only.
"""
import argparse
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

from test_parity import CODE, ROOT, TESTS, lua_value, untype


def run(args, wrapper_source=None):
    sys.path.insert(0, str(args.dependencies))
    from lupa import LuaRuntime

    db = sqlite3.connect(':memory:')
    db.row_factory = sqlite3.Row
    for name in ('Schema', 'Sources'):
        db.executescript((CODE / f'CSC_Adjacency{name}.sql').read_text(encoding='utf-8-sig'))
    processor = (CODE / 'CSC_AdjacencyProcessor.sql').read_text(encoding='utf-8-sig')
    for statement in re.findall(r'INSERT OR IGNORE INTO CSC_AdjacencyObjects\b.*?;', processor, re.S):
        db.executescript(statement)

    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute((TESTS / 'world.lua').read_text(encoding='utf-8-sig'))
    g = lua.globals()
    for table in ('Sources', 'Providers', 'Objects'):
        rows = [dict(row) for row in db.execute('SELECT * FROM CSC_Adjacency' + table)]
        lua.execute('GameInfo.CSC_Adjacency' + table + '=info(' + lua_value(rows) + ')')

    def include(name):
        if name not in ('Civ6Common', 'MapEnums'):
            source = wrapper_source if name == 'AdjacencyBonusSupport' and wrapper_source else (CODE / f'{name}.lua').read_text(encoding='utf-8-sig')
            lua.execute(untype(source))

    g.include = include
    lua.execute('''
        GameInfo.Yields=info({{Index=0,YieldType='YIELD_FOOD'}, {Index=5,YieldType='YIELD_FAITH'}});
        GameInfo.Districts=info({{Index=0,DistrictType='DISTRICT_TEST'},
            {Index=1,DistrictType='DISTRICT_WONDER'}, {Index=2,DistrictType='DISTRICT_CSC_TAILORS_QUARTER'}});
        AdjacencyBonusTypes={NO_ADJACENCY=0,ADJACENCY_DISTRICT=1,ADJACENCY_RESOURCE=2,
            ADJACENCY_RESOURCE_CLASS=3,ADJACENCY_RIVER=4};
        GameInfo.Tags=info({{Tag='CLASS_CSC_TAILORS_BASE',Vocabulary='RESOURCE_CLASS'},
            {Tag='CLASS_CSC_TAILORS_SPEC',Vocabulary='RESOURCE_CLASS'},
            {Tag='CLASS_CSC_TAILORS_SALES',Vocabulary='DISTRICT_CLASS'}});
        GameInfo.TypeTags=info({{Tag='CLASS_CSC_TAILORS_BASE',Type='RESOURCE_VISIBLE'},
            {Tag='CLASS_CSC_TAILORS_BASE',Type='RESOURCE_CIVIC'},
            {Tag='CLASS_CSC_TAILORS_SPEC',Type='RESOURCE_HIDDEN'},
            {Tag='CLASS_CSC_TAILORS_SALES',Type='DISTRICT_TEST'}});
        function prepareEdges(w,h,wrap)
            resetWorld(w,h,wrap);
            for _,p in ipairs(world) do
                p.owner=0; p.resource=-1; p.district=-1; p.riverE=false; p.riverSE=false; p.riverSW=false;
                p.GetAdjacencyBonusType=function(self) return self.nativeType or 0,-1 end;
            end
        end
        function edgeRule(source,object)
            return {ID='EDGE',DistrictType='DISTRICT_TEST',ProvideType='SelfBonus',YieldType='YIELD_FOOD',
                YieldChange=1,AdjacencyType=source,CustomAdjacentObject=object or 'NONE',
                MinRings=1,MaxRings=1,MustOwn=1,ModifierOwner='DistrictModifiers'};
        end
        opposite={[0]=3,[1]=4,[2]=5,[3]=0,[4]=1,[5]=2};
        function face(bonuses,p,direction)
            local view=bonuses[p:GetIndex()]; local found=nil;
            for _,edge in ipairs(view and view.adjacent or {}) do
                if edge.direction==opposite[direction] then
                    assert(not found,'Duplicate face'); found=edge;
                end
            end
            return found;
        end
        function collectEdge(direction)
            local p=Map.GetAdjacentPlot(center.x,center.y,direction);
            local edge=face(AddAdjacentPlotBonuses(center,'DISTRICT_TEST',city,{}),p,direction);
            return edge and edge.iconArtdef or '';
        end
    ''')
    include('AdjacencyBonusSupport')
    reference = (args.reference / 'UI/Common/AdjacencyBonusSupport.lua').read_text(encoding='utf-8-sig')
    matcher = re.search(r'^function PlotMatchesRuivoCAO\(.*?^end', reference, re.S | re.M)
    assert matcher, 'Reference matcher missing'
    # The reference matcher closes over a visibility helper. Recreate its native
    # prerequisites without delegating the expected result to CSC's evaluator.
    lua.execute('''
        ResourceTypeMap={[0]='RESOURCE_VISIBLE',[1]='RESOURCE_HIDDEN',[2]='RESOURCE_CIVIC'};
        DistrictTypeMap={[0]='DISTRICT_TEST',[1]='DISTRICT_WONDER',[2]='DISTRICT_CSC_TAILORS_QUARTER'};
        TypeTagsMap={CLASS_CSC_TAILORS_BASE={RESOURCE_VISIBLE=true,RESOURCE_CIVIC=true},
            CLASS_CSC_TAILORS_SPEC={RESOURCE_HIDDEN=true},CLASS_CSC_TAILORS_SALES={DISTRICT_TEST=true}};
        function IsResourceVisibleToLocalPlayer(index)
            if index==1 then return discoveredTech; end
            if index==2 then return discoveredCivic; end
            return index==0;
        end
    ''')
    lua.execute(untype(matcher.group()))
    lua.execute('''
        function matchesFork(rule,p,direction)
            return PlotMatchesRuivoCAO(p,rule.AdjacencyType,rule.CustomAdjacentObject,direction,center);
        end
        -- Every face, with and without native generic icons. A stock resource-
        -- class face must not mask Base, nor a stock district face mask Sales.
        roleCases=0;
        for direction=0,5 do
            for _,case in ipairs({
                {'FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_TAILORS_BASE',0,-1,'CSC_Base_Materials',3},
                {'FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_TAILORS_SPEC',1,-1,'CSC_Spec_Materials',2},
                {'FROM_RINGS_TYPETAG_DISTRICT','CLASS_CSC_TAILORS_SALES',-1,0,'CSC_Sales',1},
                {'FROM_RINGS_CAO_DISTRICT','DISTRICT_CSC_TAILORS_QUARTER',-1,2,'CSC_Goods',1}
            }) do
                for _,nativeType in ipairs({0,case[6]}) do
                    prepareEdges(); discoveredTech=true;
                    local p=Map.GetAdjacentPlot(center.x,center.y,direction);
                    p.resource=case[3]; p.district=case[4]; p.nativeType=nativeType;
                    local rule=edgeRule(case[1],case[2]); CSC_Adjacency.ByDistrict.DISTRICT_TEST={rule};
                    assert(matchesFork(rule,p,direction),'Fork must recognize the authored role');
                    assert(collectEdge(direction)==case[5],case[5]..' masked on face '..direction);
                    assert(GetAdjacentIconArtdefName('DISTRICT_TEST',p,city,direction,center)==case[5]);
                    roleCases=roleCases+1;
                end
            end
        end
        -- Ring zero, broad rings, ownership, hidden resources and negative yields.
        filterCases=0;
        for _,bounds in ipairs({{0,0,false},{0,1,true},{1,1,true},{1,3,true},{2,3,false},{1,0,false}}) do
            for _,owner in ipairs({0,1}) do
                for _,mustOwn in ipairs({0,1}) do
                    for _,visible in ipairs({false,true}) do
                        prepareEdges(); discoveredTech=visible;
                        local p=Map.GetAdjacentPlot(center.x,center.y,1); p.resource=1; p.owner=owner;
                        local rule=edgeRule('FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_TAILORS_SPEC');
                        rule.MinRings=bounds[1]; rule.MaxRings=bounds[2]; rule.MustOwn=mustOwn; rule.YieldChange=-1;
                        CSC_Adjacency.ByDistrict.DISTRICT_TEST={rule};
                        local expected=bounds[3] and (mustOwn==0 or owner==0) and matchesFork(rule,p,1);
                        assert((collectEdge(1)~='')==expected,'Ring/ownership/visibility mismatch');
                        filterCases=filterCases+1;
                    end
                end
            end
        end
        prepareEdges(); local civicPlot=Map.GetAdjacentPlot(center.x,center.y,1); civicPlot.resource=2;
        CSC_Adjacency.ByDistrict.DISTRICT_TEST={edgeRule('FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_TAILORS_BASE')};
        assert(collectEdge(1)==''); discoveredCivic=true; assert(collectEdge(1)=='CSC_Base_Materials');
        -- Update cached faces instead of treating them as permanently occupied.
        local current={[civicPlot:GetIndex()]={adjacent={
            {direction=4,iconArtdef='Districts_Generic_District',inBonus=true},
            {direction=4,iconArtdef='',inBonus=false},
            {direction=5,iconArtdef='Other placement',inBonus=true}}}};
        local updated=AddAdjacentPlotBonuses(center,'DISTRICT_TEST',city,current);
        local edge=face(updated,civicPlot,1);
        assert(edge.iconArtdef=='CSC_Base_Materials' and edge.inBonus and edge.outBonus);
        assert(#updated[civicPlot:GetIndex()].adjacent==2);
        local again=AddAdjacentPlotBonuses(center,'DISTRICT_TEST',city,updated);
        assert(#again[civicPlot:GetIndex()].adjacent==2,'Repeated call duplicated face');
        -- A source fallback before an explicit object must not steal its icon.
        local river=edgeRule('FROM_RIVER_CROSSING'); river.MustOwn=0; center.riverE=true;
        table.insert(CSC_Adjacency.ByDistrict.DISTRICT_TEST,1,river);
        assert(collectEdge(1)=='CSC_Base_Materials');
        -- When no object matches, native behavior remains available.
        civicPlot.resource=-1; center.riverE=false; civicPlot.nativeType=1;
        assert(collectEdge(1)=='Districts_Generic_District');
        CSC_Adjacency.ByDistrict.DISTRICT_TEST=nil;
        assert(collectEdge(1)=='Districts_Generic_District');
        -- The six physical flags are independent. Compare all 64 river layouts
        -- to the fork, with the native aggregate count for yield calculation.
        riverCases=0;
        for mask=0,63 do
            prepareEdges(); local river=edgeRule('FROM_RIVER_CROSSING'); river.MustOwn=0;
            CSC_Adjacency.ByDistrict.DISTRICT_TEST={river}; local expectedCount=0;
            for direction=0,5 do
                local present=math.floor(mask/2^direction)%2==1;
                local p=Map.GetAdjacentPlot(center.x,center.y,direction);
                if direction==0 then p.riverSW=present;
                elseif direction==1 then center.riverE=present;
                elseif direction==2 then center.riverSE=present;
                elseif direction==3 then center.riverSW=present;
                elseif direction==4 then p.riverE=present;
                else p.riverSE=present; end
                if present then expectedCount=expectedCount+1; end
            end
            center.riverCount=expectedCount;
            local bonuses=AddAdjacentPlotBonuses(center,'DISTRICT_TEST',city,{});
            for direction=0,5 do
                local p=Map.GetAdjacentPlot(center.x,center.y,direction);
                local edge=face(bonuses,p,direction);
                local expected=matchesFork(river,p,direction);
                assert((edge~=nil)==expected,'Directional river parity');
                if edge then assert(edge.iconArtdef=='Terrain_River'); end
                riverCases=riverCases+1;
            end
            assert(CSC_Adjacency.Count(river,center,city,0)==expectedCount);
            for _,change in ipairs({0.5,-0.5}) do
                river.YieldChange=change;
                assert(CSC_Adjacency.Amount(river,expectedCount)==(change>0 and math.floor(expectedCount/2) or -math.floor(expectedCount/2)));
            end
        end
        -- Building gates, including a mill in another city, remain effective.
        local river=CSC_Adjacency.ByDistrict.DISTRICT_TEST[1];
        river.ModifierOwner='BuildingModifiers'; river.WhoIsTheOwner='BUILDING_MILL';
        river.CollectionType='COLLECTION_PLAYER_DISTRICTS';
        assert(collectEdge(1)==''); otherCity.mill=true; assert(collectEdge(1)=='Terrain_River');
        -- Wrapped neighbors can repeat, but their different faces must survive.
        prepareEdges(2,2,true); CSC_Adjacency.ByDistrict.DISTRICT_TEST={edgeRule('FROM_RINGS_TYPETAG_RESOURCE','CLASS_CSC_TAILORS_BASE')};
        for _,p in ipairs(world) do p.resource=0; end
        local wrapped=AddAdjacentPlotBonuses(center,'DISTRICT_TEST',city,{});
        for direction=0,5 do
            local p=Map.GetAdjacentPlot(center.x,center.y,direction);
            assert(face(wrapped,p,direction).iconArtdef=='CSC_Base_Materials');
        end
    ''')

    # Check the selected names through Overlay -> XLP -> AST -> material -> TEX.
    overlay = ET.parse(ROOT / 'Civ Supply Chains/ArtDefs/CSC_Overlay.artdef')
    entries = {e.find('m_Name').get('text'): e for e in overlay.findall('m_RootCollections/Element/Element')}
    xlp = ET.parse(ROOT / 'Civ Supply Chains/XLPs/CSC_UILensAssets.xlp')
    xlp_names = {e.get('text') for e in xlp.findall('.//m_EntryID')}
    for role in ('Base_Materials', 'Spec_Materials', 'Sales', 'Goods'):
        name = 'CSC_' + role
        assert name in entries
        assert name + '_Box' in xlp_names
        assert entries[name].find('.//m_EntryName[@text="' + name + '_Box"]') is not None
        asset = ET.parse(ROOT / f'Civ Supply Chains/Assets/{name}_Box.ast')
        assert asset.find('.//m_ObjectName[@text="' + name + '_Icon"]') is not None
        material = ET.parse(ROOT / f'Civ Supply Chains/Materials/{name}_Icon.mtl')
        assert material.find('.//m_ObjectName[@text="' + name + '"]') is not None
        assert (ROOT / f'Civ Supply Chains/Textures/{name}.tex').is_file()
        assert (ROOT / f'Civ Supply Chains/Textures/{name}.dds').is_file()
    for quarter in ('BAKERS', 'TAILORS'):
        for role, art in (('BASE', 'Base_Materials'), ('SPEC', 'Spec_Materials'), ('SALES', 'Sales')):
            row = db.execute('SELECT ArtdefOverlayEntry FROM CSC_AdjacencyObjects WHERE CustomAdjacentObject=?',
                             (f'CLASS_CSC_{quarter}_{role}',)).fetchone()
            assert row and row[0] == 'CSC_' + art
    print(f'PASS: {g.roleCases} role/native-conflict cases; {g.filterCases} ring/ownership/visibility cases; '
          f'{g.riverCases} fork river-edge comparisons; signed river totals; cache deduplication; wrapped faces; art links')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, required=True)
    parser.add_argument('--dependencies', type=Path, required=True)
    run(parser.parse_args())


if __name__ == '__main__':
    main()
