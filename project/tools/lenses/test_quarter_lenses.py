"""Exercise Quarter lenses against live SQL declarations and native-style UI mocks.

Requires lupa, as used by the adjacency tests. No game/mod preferences are changed.
"""
import argparse
import json
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "Civ Supply Chains"
LENSES = MOD / "Lua_UI/Lenses"
sys.path.insert(0, str(ROOT / "project/tools/adjacencies"))
from test_parity import lua_value, untype


def sql(path):
    text = path.read_text(encoding="utf-8-sig")
    return re.sub(r"--[^\n]*", "", re.sub(r"/\*.*?\*/", "", text, flags=re.S))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path)
    parser.add_argument("--game", type=Path, help="Also exercise the placement override against the installed native PlotInfo")
    parser.add_argument("--more-lenses", type=Path, help="Also run installed More Lenses layer listeners during placement")
    parser.add_argument("--gameplay-database", type=Path, help="Validate palette SQL against a read-only runtime gameplay Colors schema")
    args = parser.parse_args()
    if args.dependencies:
        sys.path.insert(0, str(args.dependencies))
    from lupa import LuaRuntime

    db = sqlite3.connect(":memory:")
    db.row_factory = sqlite3.Row
    db.executescript("""
        CREATE TABLE TypeTags(Type TEXT, Tag TEXT, PRIMARY KEY(Type,Tag));
        CREATE TABLE Resources(ResourceType TEXT PRIMARY KEY);
        CREATE TABLE DistrictReplaces(CivUniqueDistrictType TEXT, ReplacesDistrictType TEXT);
        CREATE TABLE Colors(Type TEXT PRIMARY KEY, Color TEXT, Red REAL, Green REAL, Blue REAL, Alpha REAL);
        CREATE TABLE LocalizedText(Language TEXT, Tag TEXT PRIMARY KEY, Text TEXT);
    """)
    shared = sql(MOD / "Data/CSC_Q_ALL.sql")
    db.executescript(re.search(r"CREATE TABLE IF NOT EXISTS CSC_QuarterMaterialAdjacencyConfig.*?;", shared, re.S)[0])
    db.executescript(re.search(r"CREATE TABLE IF NOT EXISTS CSC_QuarterWonderSales.*?;", shared, re.S)[0])
    for key in ("BAKERS", "TAILORS"):
        for statement in re.findall(r"INSERT OR IGNORE INTO (?:TypeTags|CSC_QuarterMaterialAdjacencyConfig|CSC_QuarterWonderSales)\b.*?;",
                                    sql(MOD / f"Data/CSC_Q_{key}.sql"), re.S):
            db.executescript(statement)
    db.execute("INSERT INTO Resources SELECT DISTINCT Type FROM TypeTags WHERE Type LIKE 'RESOURCE_%'")
    db.execute("INSERT INTO Resources VALUES ('RESOURCE_GOLD')")
    # Execute real optional resource tagging rather than hard-code the resulting lens set.
    for statement in re.findall(r"INSERT OR IGNORE INTO TypeTags\b.*?;", sql(MOD / "ModSupport/ModSupport_SR.sql"), re.S):
        db.executescript(statement)
    db.executescript("""
        INSERT INTO DistrictReplaces VALUES ('DISTRICT_ROYAL_NAVY_DOCKYARD', 'DISTRICT_HARBOR');
        INSERT INTO DistrictReplaces VALUES ('DISTRICT_SUGUBA', 'DISTRICT_COMMERCIAL_HUB');
    """)
    processor = sql(MOD / "Lua_UI/Adjacencies/CSC_AdjacencyProcessor.sql")
    db.executescript(re.search(r"INSERT OR IGNORE INTO TypeTags\b.*?;", processor, re.S)[0])
    db.executescript((LENSES / "CSC_Lens_Colors.sql").read_text(encoding="utf-8-sig"))
    db.executescript((LENSES / "CSC_Lens_Text.sql").read_text(encoding="utf-8-sig"))
    colors = {row["Type"]: i + 1 for i, row in enumerate(db.execute("SELECT * FROM Colors"))}
    colors["COLOR_MORELENSES_GREY"] = 100
    texts = {row["Tag"] for row in db.execute("SELECT * FROM LocalizedText")}
    resources = [{"ResourceType": row[0], "Index": i} for i, row in enumerate(db.execute("SELECT * FROM Resources ORDER BY ResourceType"))]
    districts = sorted({row[0] for row in db.execute("SELECT Type FROM TypeTags WHERE Type LIKE 'DISTRICT_%'")} |
                       {"DISTRICT_CSC_BAKERS_QUARTER", "DISTRICT_CSC_TAILORS_QUARTER", "DISTRICT_CAMPUS", "DISTRICT_WONDER"})
    district_rows = [{"DistrictType": name, "Index": i} for i, name in enumerate(districts)]
    wonder_rows = [{"BuildingType": row[0], "Index": i, "IsWonder": True, "Name": row[0]}
                   for i, row in enumerate(db.execute("SELECT DISTINCT BuildingType FROM CSC_QuarterWonderSales ORDER BY BuildingType"))]
    wonder_rows.append({"BuildingType": "BUILDING_UNMAPPED_WONDER", "Index": len(wonder_rows), "IsWonder": True})
    service_source = (MOD / "Lua_UI/WonderServices/CSC_WonderServicePlacement.lua").read_text()
    assert {row[0] for row in db.execute("SELECT BuildingType FROM CSC_QuarterWonderSales WHERE QuarterKey='TAILORS'")} == set(re.findall(r'HostType\s*=\s*"([^"]+)"', service_source))
    lens_source = (LENSES / "ModLens_CSC_Quarters.lua").read_text(encoding="utf-8-sig")

    def runtime(lens=True, panel=True):
        lua = LuaRuntime(unpack_returned_tuples=True)
        # Must be inert without More Lenses, even when no UI APIs exist.
        if not lens and not panel:
            lua.execute(lens_source)
            assert lua.globals().CSC_Adjacency is None
            return lua
        lua.execute((ROOT / "project/tests/adjacencies/world.lua").read_text(encoding="utf-8"))
        # Remove permissive missing-table behavior to match native GameInfo.
        lua.execute("setmetatable(GameInfo, nil)")
        lua.execute('''
            local reset=resetWorld
            function resetWorld(w,h)
                reset(w,h)
                for _,p in ipairs(world) do p.wonder=-1; p.complete=false end
            end
        ''')
        for name, rows in (
            ("Resources", resources), ("Districts", district_rows),
            ("Buildings", wonder_rows),
            ("TypeTags", [dict(row) for row in db.execute("SELECT * FROM TypeTags")]),
            ("CSC_QuarterWonderSales", [dict(row) for row in db.execute("SELECT * FROM CSC_QuarterWonderSales")]),
            ("CSC_QuarterMaterialAdjacencyConfig", [dict(row) for row in db.execute("SELECT * FROM CSC_QuarterMaterialAdjacencyConfig")]),
        ):
            lua.execute(f"GameInfo.{name}=info({lua_value(rows)})")
        def include(name):
            directory = LENSES if name == "CSC_QuarterLensSupport" else MOD / "Lua_UI/Adjacencies"
            lua.execute((directory / f"{name}.lua").read_text(encoding="utf-8-sig"))
        lua.globals().include = include
        lua.execute("UI={}; Map.GetGridSize=function() return width,height end; PlayersVisibility={[0]={IsRevealed=function(_,x,y) return not world[y*width+x+1].hidden end}}")
        lua.globals().UI.GetColorValue = lambda key: colors[key]
        lua.execute('''
            outlines={}
            function GetTestOverlay(name)
                if missingArt then return nil end
                if not outlines[name] then outlines[name]={channels={},colors={},visible=false,
                    ClearPlotChannel=function(self) self.channels={} end,
                    SetVisible=function(self,v) self.visible=v end,
                    ShowHighlights=function(self,v) self.highlights=v end,
                    ShowBorders=function(self,v) self.borders=v end,
                    SetBorderColors=function(self,ch,back,front) self.colors[ch]={back,front} end,
                    SetPlotChannel=function(self,plots,ch) self.channels[ch]=plots end} end
                return outlines[name]
            end
            UILens={GetOverlay=GetTestOverlay}
        ''')
        if lens:
            lua.execute("g_ModLenses={}")
        if panel:
            lua.execute("g_ModLensModalPanel={}")
        lua.execute(lens_source)
        for registry in ("g_ModLenses", "g_ModLensModalPanel"):
            table = lua.globals()[registry]
            if table is not None:
                assert set(table.keys()) == {"ML_CSC_SUPPLY_CHAINS"}
        if lens:
            entry = lua.globals().g_ModLenses.ML_CSC_SUPPLY_CHAINS
            assert entry.LensButtonText in texts and entry.LensButtonTooltip in texts
        if panel:
            for key in lua.globals().CSC_QuarterLensSupport.Quarters.keys():
                entry = lua.globals().CSC_QuarterLensSupport.GetLensLegend(key)
                assert entry.LensTextKey in texts
                for legend in entry.Legend.values():
                    assert legend[1] in texts and legend[2] in colors.values()
        return lua

    runtime(False, False)
    runtime(False, True)
    runtime(True, False)
    lua = runtime()
    cases = 0

    def bucket(key, plot):
        table = lua.globals().CSC_QuarterLensSupport.GetColorPlotTable(key)
        matches = [color for color, indexes in table.items() if plot in indexes.values()]
        assert len(matches) <= 1
        return matches[0] if matches else None

    for key in ("BAKERS", "TAILORS"):
        base = {row[0] for row in db.execute("""
            SELECT TT.Type FROM TypeTags TT JOIN CSC_QuarterMaterialAdjacencyConfig C ON TT.Tag=C.SourceTag
            WHERE C.QuarterKey=? AND C.SourceTag LIKE '%_BASE' AND (C.SourceFilter='' OR TT.Type LIKE C.SourceFilter)
        """, (key,))}
        spec = {row[0] for row in db.execute("""
            SELECT TT.Type FROM TypeTags TT JOIN CSC_QuarterMaterialAdjacencyConfig C ON TT.Tag=C.SourceTag
            WHERE C.QuarterKey=? AND C.SourceTag LIKE '%_SPEC' AND (C.SourceFilter='' OR TT.Type LIKE C.SourceFilter)
        """, (key,))}
        sales = {row[0] for row in db.execute("SELECT Type FROM TypeTags WHERE Tag=?", (f"CLASS_CSC_{key}_SALES",))}
        lua.execute("resetWorld(1,1); world[1].district=-1; world[1].resource=-1")
        p = lua.globals().world[1]
        for resource in resources:
            p.resource = resource["Index"]
            for improved, pillaged in ((False, False), (True, False), (True, True)):
                p.improvement = 0 if improved else -1
                p.pillaged = pillaged
                kind = "BASE" if resource["ResourceType"] in base else "SPEC" if resource["ResourceType"] in spec else None
                expected = colors[f"COLOR_CSC_LENS_{kind}_{'IMPROVED' if improved and not pillaged else 'UNIMPROVED'}"] if kind else 100
                assert bucket(key, 0) == expected, (key, resource, improved, pillaged)
                cases += 1
        for district in district_rows:
            p.district = district["Index"]
            p.resource = -1
            suffix = f"{key}_QUARTER" if district["DistrictType"] == f"DISTRICT_CSC_{key}_QUARTER" else "SALE_DISTRICT" if district["DistrictType"] in sales else None
            assert bucket(key, 0) == (colors[f"COLOR_CSC_LENS_{suffix}"] if suffix else 100)
            cases += 1
        p.hidden = True
        assert bucket(key, 0) is None
        p.hidden = False

    # Discovery is queried each time, so revealing a tech updates an existing lens.
    lua.execute("world[1].district=-1; world[1].resource=GameInfo.Resources.RESOURCE_SILVER.Index; world[1].improvement=0; world[1].pillaged=false; GameInfo.Resources.RESOURCE_SILVER.PrereqTech='TECH_REVEAL'")
    assert bucket("TAILORS", 0) == 100
    lua.execute("discoveredTech=true")
    assert bucket("TAILORS", 0) == colors["COLOR_CSC_LENS_SPEC_IMPROVED"]
    lua.execute("Game.GetLocalPlayer=function() return -1 end")
    assert len(lua.globals().CSC_QuarterLensSupport.GetColorPlotTable("TAILORS")) == 0

    # Compare SourceFilter's %, _, case and punctuation handling to SQLite LIKE.
    for pattern in ("resource_c_t%", "RESOURCE_CSC_%", "RESOURCE_%", "RESOURCE_COTTON", "RESOURCE_%.?", "NO_MATCH"):
        db.execute("UPDATE CSC_QuarterMaterialAdjacencyConfig SET SourceFilter=? WHERE QuarterKey='TAILORS' AND SourceTag LIKE '%_BASE'", (pattern,))
        lua = runtime()
        lua.execute("resetWorld(1,1); world[1].district=-1; world[1].improvement=0")
        for resource in resources:
            lua.globals().world[1].resource = resource["Index"]
            match = resource["ResourceType"] in {row[0] for row in db.execute("SELECT Type FROM TypeTags WHERE Tag='CLASS_CSC_TAILORS_BASE' AND Type LIKE ?", (pattern,))}
            assert (bucket("TAILORS", 0) == colors["COLOR_CSC_LENS_BASE_IMPROVED"]) == match
            cases += 1

    source = json.loads((ROOT / "project/modbuddy/CivSupplyChains.actions.json").read_text(encoding="utf-8-sig"))
    criteria = {row["attributes"]["id"]: row for row in source["blocks"]["actionCriteria"]}
    assert criteria["MoreLensesMod"]["children"] == [{"tag": "ModInUse", "text": "35f33319-ad93-4d6b-bf27-406fac382d06"}]
    project = ET.parse(MOD / "Civ Supply Chains.civ6proj")
    contents = {row.attrib["Include"].replace("\\", "/") for row in project.findall(".//{*}Content")}
    # More Lenses consumes RGBA columns from gameplay Colors. UpdateColors targets
    # a different colour-manager schema and silently leaves these rows unavailable.
    types = {"ModLens_CSC_Quarters.lua": "ImportFiles", "CSC_Lens_Colors.sql": "UpdateDatabase", "CSC_Lens_Text.sql": "UpdateText"}
    for file, action_type in types.items():
        path = f"Lua_UI/Lenses/{file}"
        actions = [row for row in source["blocks"]["inGameActions"] if path in row.get("files", [])]
        assert path in contents and len(actions) == 1
        assert actions[0]["type"] == action_type
        assert actions[0].get("criteria", []) == ([] if file == "CSC_Lens_Colors.sql" else ["MoreLensesMod"])
    placement = [row for row in source["blocks"]["inGameActions"] if row["id"] == "CSC_QuarterPlacementOverlay"][0]
    assert not placement.get("criteria")
    assert placement["type"] == "ReplaceUIScript" and placement["properties"]["LuaContext"] == "PlotInfo"
    assert placement["properties"]["LuaReplace"] in contents
    chooser = next(row for row in source["blocks"]["inGameActions"] if row["id"] == "CSC_SupplyChainsLensPanel")
    assert chooser["type"] == "AddUserInterfaces" and chooser["criteria"] == ["MoreLensesMod"]
    assert chooser["properties"]["Context"] == "InGame"
    assert all(file in contents for file in chooser["files"])
    imports = next(row for row in source["blocks"]["inGameActions"] if row["id"] == "CSC_QuarterLenses")
    assert "Lua_UI/Lenses/CSC_SupplyChainsLensPanel.lua" in imports["files"]
    assert imports["criteria"] == ["MoreLensesMod"]
    ET.parse(LENSES / "CSC_SupplyChainsLensPanel.xml")
    print(f"Passed {cases} plot classifications; separate More Lenses panels, discovery, visibility, pillage, unique districts, optional resources, SQL filters and build wiring.")

    db.execute("UPDATE CSC_QuarterMaterialAdjacencyConfig SET SourceFilter='' WHERE QuarterKey='TAILORS'")
    test_wonder_sales(runtime, colors, wonder_rows)
    if args.game:
        test_placement(args.game, runtime, colors, args.more_lenses)
    test_supply_chains_panel(runtime, colors)
    test_improved_borders(runtime, colors)
    if args.gameplay_database:
        runtime_db = sqlite3.connect(args.gameplay_database.resolve().as_uri() + "?mode=ro", uri=True)
        schema = runtime_db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='Colors'").fetchone()[0]
        fixture = sqlite3.connect(":memory:")
        fixture.executescript(schema)
        fixture.executescript((LENSES / "CSC_Lens_Colors.sql").read_text(encoding="utf-8-sig"))
        rows = fixture.execute("SELECT Type, Red, Green, Blue, Alpha FROM Colors WHERE Type LIKE 'COLOR_CSC_LENS_%'").fetchall()
        assert len(rows) == 9
        assert len({row[1:] for row in rows}) == 9
        assert all(all(channel is not None and 0 <= channel <= 1 for channel in row[1:]) and row[4] > 0 for row in rows)
        print("Palette SQL verified on runtime gameplay Colors schema: 9 named RGBA colours: shared materials/sales plus icon-based Quarter colours, all visible.")
        runtime_db.close()


def test_wonder_sales(runtime, colors, wonder_rows):
    """Named, completed, revealed customer Wonders share both views' yellow fill."""
    lua = runtime()
    lua.execute("resetWorld(1,1); world[1].district=GameInfo.Districts.DISTRICT_WONDER.Index; world[1].resource=-1")
    plot = lua.globals().world[1]
    support = lua.globals().CSC_QuarterLensSupport
    for wonder in wonder_rows:
        plot.wonder = wonder["Index"]
        mapped = wonder["BuildingType"] != "BUILDING_UNMAPPED_WONDER"
        for key in ("TAILORS", "BAKERS"):
            for complete in (True, False):
                plot.complete = complete
                for ignored in (True, False):
                    entries = support.GetPlotEntries(key, ignored)
                    expected = mapped and key == "TAILORS" and complete
                    if expected:
                        assert len(entries) == 1 and entries[1].category == "SALE"
                        assert entries[1].color == colors["COLOR_CSC_LENS_SALE_DISTRICT"]
                        assert entries[1].icon == "ICON_" + wonder["BuildingType"]
                    elif ignored:
                        assert len(entries) == 1 and entries[1].category == "IGNORE"
                    else:
                        assert len(entries) == 0
        plot.hidden = True
        assert len(support.GetPlotEntries("TAILORS", True)) == 0
        plot.hidden = False
    plot.wonder = -1
    assert len(support.GetPlotEntries("TAILORS", False)) == 0
    print("Passed Wonder sales: all three declared Tailors customers, both palettes/views, completion, visibility, unmapped Wonders and Quarter scope.")


def test_improved_borders(runtime, colors):
    """Check manual-only edges and sampler removal."""
    lua = runtime()
    g = lua.globals()
    lua.execute('''
        resetWorld(7,1)
        for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
        world[1].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[1].improvement=0
        world[2].resource=GameInfo.Resources.RESOURCE_DYES.Index; world[2].improvement=0
        world[3].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[3].improvement=-1
        world[4].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[4].improvement=0; world[4].pillaged=true
        world[5].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[5].improvement=0; world[5].hidden=true
        world[6].district=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index
        world[7].district=GameInfo.Districts.DISTRICT_HARBOR.Index
        CSC_QuarterLensSupport.DrawImprovedBorders('Lens','TAILORS')
        local border=outlines.CSC_QuarterLens_Improved
        assert(border.visible and border.borders and not border.highlights)
        assert(table.count(border.channels)==2 and border.channels[1][1]==0 and border.channels[2][1]==1)
        assert(border.colors[1][1]==UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'))
        assert(border.colors[1][2]==UI.GetColorValue('COLOR_CSC_LENS_BASE_OUTLINE'))
        assert(border.colors[2][2]==UI.GetColorValue('COLOR_CSC_LENS_SPEC_OUTLINE'))
        CSC_QuarterLensSupport.DrawImprovedBorders('Placement','TAILORS')
        CSC_QuarterLensSupport.ClearImprovedBorders('Placement')
        assert(border.visible and outlines.CSC_QuarterPlacement_Improved==nil)
        world[1].pillaged=true
        CSC_QuarterLensSupport.DrawImprovedBorders('Lens','TAILORS')
        assert(table.count(border.channels)==1 and border.channels[1][1]==1)
        world[2].improvement=-1
        CSC_QuarterLensSupport.DrawImprovedBorders('Lens','TAILORS')
        assert(not border.visible and table.count(border.channels)==0)
        missingArt=true
        CSC_QuarterLensSupport.DrawImprovedBorders('Lens','TAILORS')
        CSC_QuarterLensSupport.ClearImprovedBorders('Lens')
    ''')
    assert len(g.CSC_QuarterLensSupport.GetLensLegend("TAILORS").Legend) == 4
    source = json.loads((ROOT / "project/modbuddy/CivSupplyChains.actions.json").read_text())
    assert not any("Prototype" in row["id"] for row in source["blocks"]["inGameActions"])
    project = ET.parse(MOD / "Civ Supply Chains.civ6proj")
    assert not any("QuarterPlacementPrototype" in row.get("Include", "") for row in project.findall(".//{*}Content"))
    art = ET.parse(MOD / "ArtDefs/CSC_QuarterResourceBorders.artdef")
    names = {row.get("text") for row in art.findall(".//m_Name")}
    assert names == {"CSC_QuarterLens_Improved"}
    placement = (LENSES / "PlotInfo_CSC_QuarterPlacement.lua").read_text()
    assert "ImprovedBorders" not in placement
    assert all(row.get("text") == "BorderOverlay" for row in art.findall('.//m_Value') if row.get("text") != "MapSearchBorder")
    print("Passed improved resource borders: manual lens only, fill-only placement, individual edges, shared hues, pillage/unimproved/discovery filtering, missing art, four-row legend and sampler removal.")


def test_supply_chains_panel(runtime, colors):
    """Exercise the actual chooser through More Lenses' public event hooks."""
    lua = runtime()
    g = lua.globals()
    lua.execute('''
        parentEntry=g_ModLenses.ML_CSC_SUPPLY_CHAINS
        g_ModLenses=nil; g_ModLensModalPanel=nil -- Panel has its own context.
        local function event()
            local callbacks={}
            return setmetatable({
                Add=function(fn) callbacks[#callbacks+1]=fn end,
                Remove=function(fn) for i=#callbacks,1,-1 do if callbacks[i]==fn then table.remove(callbacks,i) end end end,
                Count=function() return #callbacks end,
            }, {__call=function(_,...) for _,fn in ipairs(callbacks) do fn(...) end end})
        end
        local function events() return setmetatable({}, {__index=function(t,k) local e=event(); rawset(t,k,e); return e end}) end
        Events=events(); LuaEvents=events()
        local function control()
            return {
                GetTextButton=function(self) return self end,
                LocalizeAndSetText=function(self,text) self.text=text end,
                SetToolTipString=function(self,text) self.tooltip=text end,
                SetCheck=function(self,checked) self.checked=checked end,
                RegisterCallback=function(self,_,fn) self.click=fn end,
                SetHide=function(self,hidden) self.hidden=hidden end,
                SetSizeY=function(self,height) self.height=height end,
                SetOffsetX=function(self,x) self.x=x end,
                SetOffsetY=function(self,y) self.y=y end,
                CalculateSize=function() end, ReprocessAnchoring=function() end,
                ChangeParent=function(self,owner) self.owner=owner end,
            }
        end
        choices={}; InstanceManager={new=function() return {
            GetInstance=function() local button=control(); choices[#choices+1]=button; return {QuarterButton=button} end,
            ResetInstances=function() choices={} end,
        } end}
        Controls={SupplyChainsLensPanel=control(),QuarterChoices=control(),QuarterScroll=control()}
        hud={DestroyChild=function(_,child) child.destroyed=true end}
        ContextPtr={SetInitHandler=function(_,fn) init=fn end,SetShutdown=function(_,fn) shutdown=fn end,
                    LookUpControl=function() return hud end}
        Locale={Lookup=function(text) return text end}; Mouse={eLClick=1}
        mode=0; layerOn=false; active='NONE'; painted={}; paintCount=0
        InterfaceModeTypes={SELECTION=0,VIEW_MODAL_LENS=9,DISTRICT_PLACEMENT=7}
        UI.GetInterfaceMode=function() return mode end
        UILens={GetOverlay=GetTestOverlay,CreateLensLayerHash=function(name) return name end,
                IsLayerOn=function() return layerOn end,
                ClearLayerHexes=function() painted={} end,
                SetLayerHexesColoredArea=function(_,player,plots,color) painted[color]=plots; paintCount=paintCount+1 end}
        LuaEvents.MinimapPanel_GetActiveModLens.Add(function(result) result[1]=active end)
        LuaEvents.MinimapPanel_GetLensPanelOffsets.Add(function(result) result.X=200; result.Y=180 end)
        LuaEvents.ModalLensPanel_AddLensEntry.Add(function(name,entry,refresh)
            assert(name=='ML_CSC_SUPPLY_CHAINS' and refresh); legend=entry
        end)
        resetWorld(3,1)
        for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
        world[1].resource=GameInfo.Resources.RESOURCE_WHEAT.Index; world[1].improvement=0
        world[2].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[2].improvement=0
        world[3].district=GameInfo.Districts.DISTRICT_WONDER.Index
        world[3].wonder=GameInfo.Buildings.BUILDING_BOLSHOI_THEATRE.Index; world[3].complete=true
    ''')
    original_include = g.include
    g.include = lambda name: original_include(name) if name != "InstanceManager" else None
    lua.execute((LENSES / "CSC_SupplyChainsLensPanel.lua").read_text(encoding="utf-8-sig"))
    lua.execute('''
        assert(#choices==2 and choices[1].text=='LOC_HUD_CSC_BAKERS_LENS' and choices[2].text=='LOC_HUD_CSC_TAILORS_LENS')
        assert(Controls.SupplyChainsLensPanel.hidden and choices[1].checked)
        Events.LoadScreenClose()
        assert(Controls.SupplyChainsLensPanel.owner==hud and Controls.SupplyChainsLensPanel.x==195)
        -- More Lenses opens the panel and layer before entering modal mode.
        active='ML_CSC_SUPPLY_CHAINS'; parentEntry.OnToggle(); layerOn=true
        parentEntry.NonStandardFunction(); assert(paintCount==0)
        assert(not Controls.SupplyChainsLensPanel.hidden)
        mode=9; Events.InterfaceModeChanged(0,9)
        assert(legend.LensTextKey=='LOC_HUD_CSC_BAKERS_LENS')
    ''')
    assert list(g.painted[colors["COLOR_CSC_LENS_BASE_IMPROVED"]].values()) == [0]
    lua.execute("assert(outlines.CSC_QuarterLens_Improved.visible and outlines.CSC_QuarterLens_Improved.channels[1][1]==0)")
    lua.execute("choices[2].click(); assert(choices[2].checked and not choices[1].checked); assert(legend.LensTextKey=='LOC_HUD_CSC_TAILORS_LENS')")
    assert list(g.painted[colors["COLOR_CSC_LENS_BASE_IMPROVED"]].values()) == [1]
    assert list(g.painted[colors["COLOR_CSC_LENS_SALE_DISTRICT"]].values()) == [2]
    lua.execute('''
        assert(outlines.CSC_QuarterLens_Improved.channels[1][1]==1)
        world[2].pillaged=true; parentEntry.NonStandardFunction()
        assert(not outlines.CSC_QuarterLens_Improved.visible)
        assert(painted[UI.GetColorValue('COLOR_CSC_LENS_BASE_UNIMPROVED')][1]==1)
        world[2].pillaged=false; parentEntry.NonStandardFunction()
        Events.LensLayerOff('Hex_Coloring_Appeal_Level')
        assert(not outlines.CSC_QuarterLens_Improved.visible)
        Events.LensLayerOn('Hex_Coloring_Appeal_Level')
        assert(outlines.CSC_QuarterLens_Improved.visible)
        LuaEvents.ML_CloseLensPanels(); assert(Controls.SupplyChainsLensPanel.hidden)
        assert(outlines.CSC_QuarterLens_Improved.visible) -- Options panel can close without turning its lens off.
        parentEntry.OnToggle(); assert(choices[2].checked and not Controls.SupplyChainsLensPanel.hidden)
        local before=paintCount
        active='ML_BUILDER'; LuaEvents.MinimapPanel_ModdedLensOn(active)
        assert(Controls.SupplyChainsLensPanel.hidden)
        assert(not outlines.CSC_QuarterLens_Improved.visible)
        parentEntry.NonStandardFunction(); assert(paintCount==before) -- Preserve another lens.
        active='ML_CSC_SUPPLY_CHAINS'; mode=7; Events.InterfaceModeChanged(9,7)
        CSC_QuarterLensSupport.DrawImprovedBorders('Placement','TAILORS')
        parentEntry.NonStandardFunction(); assert(paintCount==before) -- Preserve placement's colours.
        assert(outlines.CSC_QuarterPlacement_Improved==nil and not outlines.CSC_QuarterLens_Improved.visible)
        shutdown(); assert(Controls.SupplyChainsLensPanel.destroyed)
        assert(outlines.CSC_QuarterPlacement_Improved==nil)
        assert(LuaEvents.CSC_SupplyChainsLens_OpenPanel.Count()==0)
        assert(LuaEvents.CSC_SupplyChainsLens_Refresh.Count()==0)
        assert(Events.InterfaceModeChanged.Count()==0 and Events.LensLayerOn.Count()==0 and Events.LensLayerOff.Count()==0)
    ''')
    print("Passed Supply Chains chooser: single parent, data-driven Quarter choices, initial activation, palette/legend switching, selection retention, dismissal and placement isolation.")


def install_more_lenses_listeners(lua, root):
    """Execute actual Workshop callbacks in isolated contexts; files stay read-only."""
    def function(path, name):
        source = path.read_text(encoding="utf-8-sig")
        start = source.index(f"function {name}(")
        end = re.search(r"\n(?:function |-- ?={5,})", source[start:])
        assert end, name
        return untype(source[start:start + end.start()])

    mini = root / "Base/Assets/UI/minimappanel.lua"
    modal = root / "Base/Assets/UI/Panels/modallenspanel.lua"
    sources = {
        "mini": "\n".join(function(mini, name) for name in
                           ("SetModLens", "SetActiveModdedLens", "GetActiveModdedLens", "OnLensLayerOn")),
        "modal": "\n".join(function(modal, name) for name in
                            ("ShowModLensKey", "OnLensLayerOn", "AddLensEntry")),
    }
    lua.execute('''
        local control={SetText=function() end,SetHide=function() end,CalculateSize=function() end}
        moreMini=setmetatable({m_HexColoringAppeal='Hex_Coloring_Appeal_Level',
            m_AttackRange='Attack_Range',m_HexColoringGreatPeople='Great_People',m_MovementZoneOfControl='Zone_Control',
            g_ModLenses={ML_CSC_SUPPLY_CHAINS={NonStandardFunction=function() morePaints=morePaints+1 end}},
            print=function(message) moreDiagnostics[#moreDiagnostics+1]=message end}, {__index=_G})
        moreModal=setmetatable({m_HexColoringAppeal='Hex_Coloring_Appeal_Level',g_ModLensModalPanel={},
            unpack=table.unpack,
            Controls={LensText=control,KeyPanel=control,KeyScrollPanel=control},
            ResetKeyStackIM=function() end,AddKeyEntry=function() end,
            print=function(message) error('More Lenses diagnostic: '..message) end}, {__index=_G})
        morePaints=0; moreDiagnostics={}
        UI.GetHeadSelectedUnit=function() return nil end
        UI.PlaySound=function() end
        Locale={Lookup=function(s) return s end,ToUpper=function(s) return s end}
    ''')
    for context, source in sources.items():
        lua.globals().native_listener_source = source
        lua.execute(f"assert(load(native_listener_source, 'More Lenses {context}', 't', more{context.title()}))()")
    lua.execute('''
        LuaEvents.MinimapPanel_GetActiveModLens.Add(moreMini.GetActiveModdedLens)
        LuaEvents.MinimapPanel_SetActiveModLens.Add(moreMini.SetActiveModdedLens)
        LuaEvents.ModalLensPanel_AddLensEntry.Add(moreModal.AddLensEntry)
        Events.LensLayerOn.Add(moreMini.OnLensLayerOn)
        Events.LensLayerOn.Add(moreModal.OnLensLayerOn)
    ''')


def test_placement(game, runtime, colors, more_lenses=None):
    """Load the complete native panel so event rebinding/masking use Firaxis code."""
    # The native placement lens permits only fixed-colour hex layers by default.
    # Check our additive permission patch and its project/consumer registrations.
    native_art = ET.parse(game / "Base/ArtDefs/Lenses.artdef").getroot()
    patch_art = ET.parse(MOD / "ArtDefs/CSC_Lenses.artdef").getroot()
    def permission(root):
        return next(row for row in root.findall("m_RootCollections/Element/Element")
                    if row.find("m_Name").get("text") == "DistrictPlacement_PermissionMask")
    base_permission, patch_permission = permission(native_art), permission(patch_art)
    allowed = {row.get("text") for row in base_permission.findall(".//m_ElementName")}
    additions = {row.get("text") for row in patch_permission.findall(".//m_ElementName")}
    assert "Hex_Coloring_Appeal_Level" not in allowed
    assert additions == {"Hex_Coloring_Appeal_Level"}
    assert all(row.text == "false" for row in patch_art.findall(".//m_ReplaceMergedCollectionElements"))
    base_names = {row.get("text") for row in base_permission.findall("m_ChildCollections/Element/Element/m_Name")}
    patch_names = {row.get("text") for row in patch_permission.findall("m_ChildCollections/Element/Element/m_Name")}
    assert not base_names & patch_names  # Append a unique child, preserve native permissions.
    project = ET.parse(MOD / "Civ Supply Chains.civ6proj")
    assert any(row.get("Include") == "ArtDefs\\CSC_Lenses.artdef" for row in project.findall(".//{*}Content"))
    spec = ET.fromstring((MOD / "Civ Supply Chains.Art.xml").read_text(encoding="utf-8-sig").replace("AssetObjects::", "AssetObjects.."))
    consumer = next(row for row in spec.findall("artConsumers/Element") if row.find("consumerName").get("text") == "Lenses")
    assert any(row.get("text") == "CSC_Lenses.artdef" for row in consumer.findall("relativeArtDefPaths/Element"))
    native = (game / "Base/Assets/UI/WorldView/PlotInfo.lua").read_text(encoding="utf-8-sig")
    wrapper = (LENSES / "PlotInfo_CSC_QuarterPlacement.lua").read_text(encoding="utf-8-sig")
    lua = runtime()
    g = lua.globals()
    # No framework registries or grey colour are available to the placement UI.
    lua.execute("g_ModLenses=nil; g_ModLensModalPanel=nil")
    placement_colors = {key: value for key, value in colors.items() if key != "COLOR_MORELENSES_GREY"}
    g.UI.GetColorValue = lambda key: placement_colors[key]
    g.permitted = lua.table_from({name: True for name in allowed | additions})
    lua.execute('''
        log={}; areas={}; layers={}; mode=7; chosen=nil; citySelected=true; activeLens='DistrictPlacement'
        local function event()
            local callbacks={}
            return setmetatable({
                Add=function(fn) callbacks[#callbacks+1]=fn end,
                Remove=function(fn) for i=#callbacks,1,-1 do if callbacks[i]==fn then table.remove(callbacks,i) end end end,
                Count=function() return #callbacks end,
            }, {__call=function(_,...) for _,fn in ipairs(callbacks) do fn(...) end end})
        end
        local function events() return setmetatable({}, {__index=function(t,k) local e=event(); rawset(t,k,e); return e end}) end
        Events=events(); LuaEvents=events()
        UILens={GetOverlay=GetTestOverlay,
            CreateLensLayerHash=function(name) return name end,
            ClearLayerHexes=function(layer) log[#log+1]='clear:'..layer; areas[layer]={} end,
            ToggleLayerOn=function(layer)
                assert(permitted[layer]); log[#log+1]='on:'..layer
                if not layers[layer] then layers[layer]=true; Events.LensLayerOn(layer) end
            end,
            ToggleLayerOff=function(layer)
                log[#log+1]='off:'..layer
                if layers[layer] then layers[layer]=false; Events.LensLayerOff(layer) end
            end,
            IsLensActive=function(name) return activeLens==name end,
            SetLayerHexesArea=function(layer,player,plots) areas[layer]=plots end,
            SetLayerHexesColoredArea=function(layer,player,plots,color)
                assert(layer=='Hex_Coloring_Appeal_Level', 'Quarter colours require the same layer as More Lenses')
                log[#log+1]='paint:'..layer; areas[layer]=areas[layer] or {}; areas[layer][color]=plots
            end,
        }
        ContextPtr={SetInitHandler=function() end, SetShutdown=function(_,fn) shutdown=fn end}
        InstanceManager={new=function() return {DestroyInstances=function() end} end}
        Controls={PlotInfoContainer={}}
        UserConfiguration={ShowMapYield=function() return false end}
        InterfaceModeTypes={DISTRICT_PLACEMENT=7,BUILDING_PLACEMENT=8,SELECTION=0,VIEW_MODAL_LENS=9}
        CityOperationTypes={PARAM_DISTRICT_TYPE='district'}
        UI.GetInterfaceMode=function() return mode end
        UI.GetInterfaceModeParameter=function() return chosen end
        UI.GetHeadSelectedCity=function() return citySelected and city or nil end
        resetWorld(4,1)
        for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
    ''')
    original_include = g.include

    def include(name):
        if name == "PlotInfo":
            lua.execute(re.sub(r"\s*:\s*object\b", "", untype(native)))
        elif name in ("CSC_QuarterLensSupport", "CSC_AdjacencyCore"):
            original_include(name)
        # Native panel includes: initialization uses only the provided UI mocks.
    g.include = include
    lua.execute(wrapper)
    if more_lenses:
        install_more_lenses_listeners(lua, more_lenses)
    lua.execute('''
        -- Model native/More Lenses listeners: turning Appeal on paints its own
        -- contents; turning it off clears the map mask. CSC must repaint after.
        Events.LensLayerOn.Add(function(layer)
            if layer=='Hex_Coloring_Appeal_Level' then areas[layer]={[999]={3}} end
        end)
        Events.LensLayerOff.Add(function(layer)
            if layer=='Hex_Coloring_Appeal_Level' then areas.Map_Hex_Mask={} end
        end)
    ''')
    lua.execute('''
        assert(LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Count()==1)
        assert(LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Count()==1)
        chosen=GameInfo.Districts.DISTRICT_CAMPUS.Index
        original={0}; LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes(original)
        assert(#log==0) -- A standard district causes no extra lens calls.
        RealizeShadowMask(); assert(areas.Map_Hex_Mask[1]==0 and #areas.Map_Hex_Mask==1)
        chosen=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index
        world[2].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[2].improvement=0
        world[3].district=GameInfo.Districts.DISTRICT_ROYAL_NAVY_DOCKYARD.Index
        world[4].resource=GameInfo.Resources.RESOURCE_DYES.Index; world[4].hidden=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes(original)
        assert(layers.Hex_Coloring_Appeal_Level)
        assert(#original==1 and original[1]==0) -- Never mutate the caller's native list.
        assert(#areas.Map_Hex_Mask==3) -- Valid plot plus material and unique customer.
        assert(outlines.CSC_QuarterPlacement_Improved==nil)
    ''')
    plots = g.areas.Hex_Coloring_Appeal_Level
    assert list(plots[colors["COLOR_CSC_LENS_BASE_IMPROVED"]].values()) == [1]
    assert list(plots[colors["COLOR_CSC_LENS_SALE_DISTRICT"]].values()) == [2]
    assert 100 not in plots.keys()
    assert 999 not in plots.keys()
    if more_lenses:
        lua.execute("assert(moreMini.m_CurrentModdedLensOn=='NONE' and #moreDiagnostics==0)")
    lua.execute('''
        world[4].hidden=false; world[4].resource=-1
        world[4].district=GameInfo.Districts.DISTRICT_WONDER.Index
        world[4].wonder=GameInfo.Buildings.BUILDING_BROADWAY.Index; world[4].complete=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(#areas.Map_Hex_Mask==4)
    ''')
    assert list(g.areas.Hex_Coloring_Appeal_Level[colors["COLOR_CSC_LENS_SALE_DISTRICT"]].values()) == [2, 3]
    lua.execute('''
        world[4].complete=false
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(#areas.Map_Hex_Mask==3)
    ''')
    lua.execute('''
        -- Native plot-purchase redraw is the same event; pillage is read afresh.
        world[2].pillaged=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
    ''')
    assert list(g.areas.Hex_Coloring_Appeal_Level[colors["COLOR_CSC_LENS_BASE_UNIMPROVED"]].values()) == [1]
    lua.execute("assert(outlines.CSC_QuarterPlacement_Improved==nil)")
    lua.execute('''
        -- Switching directly to a standard district clears only CSC's layer.
        chosen=GameInfo.Districts.DISTRICT_CAMPUS.Index
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(not layers.Hex_Coloring_Appeal_Level and #areas.Hex_Coloring_Appeal_Level==0)
        assert(#areas.Map_Hex_Mask==1) -- Mask restoration is immediate on a direct switch.
        local before=#log
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(#log==before)
        -- Re-enter Bakers, then clear/cancel placement via the native event.
        chosen=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index
        world[2].resource=GameInfo.Resources.RESOURCE_WHEAT.Index
        world[2].pillaged=false
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(layers.Hex_Coloring_Appeal_Level)
        LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes()
        assert(not layers.Hex_Coloring_Appeal_Level and #areas.Map_Hex_Mask==0)
        -- Confirm production without any native clear event.
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        mode=InterfaceModeTypes.SELECTION
        Events.InterfaceModeChanged(InterfaceModeTypes.DISTRICT_PLACEMENT, mode)
        assert(not layers.Hex_Coloring_Appeal_Level and #areas.Hex_Coloring_Appeal_Level==0)
        assert(#areas.Map_Hex_Mask==0)
        assert(outlines.CSC_QuarterPlacement_Improved==nil)
        -- A new manual lens can take the layer before the mode event arrives.
        mode=InterfaceModeTypes.DISTRICT_PLACEMENT; activeLens='DistrictPlacement'
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        activeLens='Appeal'; areas.Hex_Coloring_Appeal_Level={[999]={3}}
        if moreMini then moreMini.SetActiveModdedLens('ML_CSC_SUPPLY_CHAINS') end
        CSC_QuarterLensSupport.DrawImprovedBorders('Lens','BAKERS')
        mode=InterfaceModeTypes.VIEW_MODAL_LENS
        Events.InterfaceModeChanged(InterfaceModeTypes.DISTRICT_PLACEMENT, mode)
        assert(layers.Hex_Coloring_Appeal_Level and areas.Hex_Coloring_Appeal_Level[999][1]==3)
        assert(outlines.CSC_QuarterLens_Improved.visible and outlines.CSC_QuarterPlacement_Improved==nil)
        -- Native SetActive can first turn off the layer, then reuse it. Cleanup
        -- must release ownership at that first off event and preserve new art.
        mode=InterfaceModeTypes.DISTRICT_PLACEMENT; activeLens='DistrictPlacement'
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        UILens.ToggleLayerOff('Hex_Coloring_Appeal_Level')
        activeLens='Appeal'; UILens.ToggleLayerOn('Hex_Coloring_Appeal_Level')
        mode=InterfaceModeTypes.VIEW_MODAL_LENS
        Events.InterfaceModeChanged(InterfaceModeTypes.DISTRICT_PLACEMENT, mode)
        assert(layers.Hex_Coloring_Appeal_Level and areas.Hex_Coloring_Appeal_Level[999][1]==3)
        UILens.ToggleLayerOff('Hex_Coloring_Appeal_Level')
        -- Leaving for Wonder placement also clears Quarter highlights.
        mode=InterfaceModeTypes.DISTRICT_PLACEMENT; activeLens='DistrictPlacement'
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        mode=InterfaceModeTypes.BUILDING_PLACEMENT
        Events.InterfaceModeChanged(InterfaceModeTypes.DISTRICT_PLACEMENT, mode)
        assert(not layers.Hex_Coloring_Appeal_Level and #areas.Map_Hex_Mask==0)
        -- Wonders and a missing selected city never receive Quarter highlights.
        mode=InterfaceModeTypes.BUILDING_PLACEMENT
        before=#log; LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0}); assert(#log==before)
        mode=InterfaceModeTypes.DISTRICT_PLACEMENT; citySelected=false
        before=#log; LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0}); assert(#log==before)
        citySelected=true; chosen=-1
        before=#log; LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0}); assert(#log==before)
        -- Shutdown releases the layer and all CSC event bindings.
        chosen=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        shutdown()
        assert(not layers.Hex_Coloring_Appeal_Level)
        assert(LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Count()==0)
        assert(LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Count()==0)
        assert(Events.InterfaceModeChanged.Count()==0)
        assert(Events.LensLayerOff.Count()==2) -- Native panel plus fixture; CSC removed.
    ''')
    if more_lenses:
        lua.execute('''
            assert(morePaints>0 and #moreDiagnostics==0)
            assert(moreMini.m_CurrentModdedLensOn=='ML_CSC_SUPPLY_CHAINS')
        ''')
        print("Passed installed More Lenses callbacks: initial nil lens, repeated placement from NONE, valid legend and no warnings/errors.")
    print("Passed native PlotInfo placement: colour layer/permissions, both Quarters, normal districts/wonders, masks, redraw/pillage, confirmation/cancellation, manual lens takeover and shutdown.")


if __name__ == "__main__":
    main()
