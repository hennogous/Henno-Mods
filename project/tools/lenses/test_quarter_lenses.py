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
from test_standalone_panel import test_supply_chains_panel
from test_supply_chain_flows import test_supply_chain_flows
from test_service_markers import test_service_markers


def sql(path):
    text = path.read_text(encoding="utf-8-sig")
    return re.sub(r"--[^\n]*", "", re.sub(r"/\*.*?\*/", "", text, flags=re.S))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dependencies", type=Path)
    parser.add_argument("--game", type=Path, help="Also exercise the placement override against the installed native PlotInfo")
    parser.add_argument("--more-lenses", type=Path, help="Also run installed More Lenses layer listeners during placement")
    parser.add_argument("--gameplay-database", type=Path, help="Validate palette SQL against a read-only runtime gameplay Colors schema")
    parser.add_argument("--panel-source", type=Path, help="Use an isolated panel source for lifecycle regression")
    parser.add_argument("--lifecycle-scenario", choices=("unopened_close", "unopened_shutdown", "active_shutdown", "normal_toggle"),
                        help="Run one standalone lifecycle scenario against --panel-source")
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
        CREATE TABLE BuildingReplaces(CivUniqueBuildingType TEXT, ReplacesBuildingType TEXT);
        CREATE TABLE Colors(Type TEXT PRIMARY KEY, Color TEXT, Red REAL, Green REAL, Blue REAL, Alpha REAL);
        CREATE TABLE LocalizedText(Language TEXT, Tag TEXT PRIMARY KEY, Text TEXT);
    """)
    shared = sql(MOD / "Data/CSC_Q_ALL.sql")
    db.executescript(re.search(r"CREATE TABLE IF NOT EXISTS CSC_QuarterMaterialAdjacencyConfig.*?;", shared, re.S)[0])
    db.executescript(re.search(r"CREATE TABLE IF NOT EXISTS CSC_QuarterWonderSales.*?;", shared, re.S)[0])
    for name in ("CSC_Stage3CustomerTransactions", "CSC_QuarterCustomerBuildings", "CSC_QuarterFlowBuildings", "CSC_AbilityAttachModifiers"):
        db.executescript(re.search(r"CREATE TABLE IF NOT EXISTS " + name + r".*?;", shared, re.S)[0])
    for key in ("BAKERS", "TAILORS"):
        for statement in re.findall(r"INSERT (?:OR IGNORE )?INTO (?:TypeTags|CSC_QuarterMaterialAdjacencyConfig|CSC_QuarterWonderSales|CSC_Stage3CustomerTransactions|CSC_QuarterCustomerBuildings|CSC_QuarterFlowBuildings|CSC_AbilityAttachModifiers)\b.*?;",
                                    sql(MOD / f"Data/CSC_Q_{key}.sql"), re.S):
            db.executescript(statement)
    # Resolve the real notification registry exactly as its late SQL pass does.
    db.executescript("CREATE TABLE ModifierArguments(ModifierId TEXT,Name TEXT,Value TEXT); CREATE TABLE ModifierStrings(ModifierId TEXT,Context TEXT,Text TEXT);")
    for key in ("BAKERS", "TAILORS"):
        for statement in re.findall(r"INSERT (?:OR (?:IGNORE|REPLACE) )?INTO (?:ModifierArguments|ModifierStrings)\b.*?;", sql(MOD / f"Data/CSC_Q_{key}.sql"), re.S):
            if "VALUES" in statement and "SELECT" not in statement:
                db.executescript(statement)
    db.executescript(sql(MOD / "Lua_UI/Notifications_Suk_MCUIS/CSC_UI_DB_Dynamic.sql"))
    # Dockmaster's era/unit branch is generated from Units, outside this map
    # fixture. The remaining real district/Wonder service metadata is resolved.
    assert [row[0] for row in db.execute("SELECT ModifierId FROM CSC_AbilityAttachModifiers WHERE AbilityEffectModifierId IS NULL OR AbilityDesc IS NULL")] == ["MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_ANCIENT_NAVAL_MELEE"]
    db.execute("INSERT INTO Resources SELECT DISTINCT Type FROM TypeTags WHERE Type LIKE 'RESOURCE_%'")
    db.execute("INSERT INTO Resources VALUES ('RESOURCE_GOLD')")
    # Execute real optional resource tagging rather than hard-code the resulting lens set.
    for statement in re.findall(r"INSERT OR IGNORE INTO TypeTags\b.*?;", sql(MOD / "ModSupport/ModSupport_SR.sql"), re.S):
        db.executescript(statement)
    db.executescript("""
        INSERT INTO DistrictReplaces VALUES ('DISTRICT_ROYAL_NAVY_DOCKYARD', 'DISTRICT_HARBOR');
        INSERT INTO DistrictReplaces VALUES ('DISTRICT_SUGUBA', 'DISTRICT_COMMERCIAL_HUB');
        INSERT INTO BuildingReplaces VALUES ('BUILDING_SUKIENNICE', 'BUILDING_MARKET');
        INSERT INTO BuildingReplaces VALUES ('BUILDING_TEST_LIGHTHOUSE', 'BUILDING_LIGHTHOUSE');
        INSERT INTO BuildingReplaces VALUES ('BUILDING_TEST_SECOND_LEVEL', 'BUILDING_TEST_LIGHTHOUSE');
    """)
    for statement in re.findall(r"INSERT OR IGNORE INTO (?:TypeTags|CSC_QuarterCustomerBuildings)\b.*?;", sql(MOD / "ModSupport/ModSupport_LGD.sql"), re.S):
        db.executescript(statement)
    processor = sql(MOD / "Lua_UI/Adjacencies/CSC_AdjacencyProcessor.sql")
    db.executescript(re.search(r"INSERT OR IGNORE INTO TypeTags\b.*?;", processor, re.S)[0])
    db.executescript((LENSES / "CSC_Lens_Colors.sql").read_text(encoding="utf-8-sig"))
    db.executescript((LENSES / "CSC_Lens_Text.sql").read_text(encoding="utf-8-sig"))
    # Native colour buckets use packed RGBA, so equal colours across readiness
    # states must merge. Unique fake IDs would hide duplicate-colour bugs.
    colors = {row["Type"]: sum(round(row[channel] * 255) << (8 * i)
              for i, channel in enumerate(('Red','Green','Blue','Alpha')))
              for row in db.execute("SELECT * FROM Colors")}
    texts = {row["Tag"] for row in db.execute("SELECT * FROM LocalizedText")}
    for row in db.execute("SELECT Text FROM LocalizedText WHERE Tag LIKE 'LOC_TOOLTIP_CSC_LENS_%'"):
        assert '[ICON_' not in row[0]
    resources = [{"ResourceType": row[0], "Index": i} for i, row in enumerate(db.execute("SELECT * FROM Resources ORDER BY ResourceType"))]
    districts = sorted({row[0] for row in db.execute("SELECT Type FROM TypeTags WHERE Type LIKE 'DISTRICT_%'")} |
                       {"DISTRICT_CSC_BAKERS_QUARTER", "DISTRICT_CSC_TAILORS_QUARTER", "DISTRICT_CAMPUS", "DISTRICT_WONDER"})
    district_rows = [{"DistrictType": name, "Index": i} for i, name in enumerate(districts)]
    wonder_rows = [{"BuildingType": row[0], "Index": i, "IsWonder": True, "Name": row[0]}
                   for i, row in enumerate(db.execute("SELECT DISTINCT BuildingType FROM CSC_QuarterWonderSales ORDER BY BuildingType"))]
    wonder_rows.append({"BuildingType": "BUILDING_UNMAPPED_WONDER", "Index": len(wonder_rows), "IsWonder": True})
    customer_types = {row[0] for row in db.execute("SELECT BuildingType FROM CSC_QuarterCustomerBuildings UNION SELECT CustomerBuildingType FROM CSC_Stage3CustomerTransactions UNION SELECT SellerBuildingType FROM CSC_Stage3CustomerTransactions UNION SELECT BuildingType FROM CSC_QuarterFlowBuildings UNION SELECT CivUniqueBuildingType FROM BuildingReplaces")}
    customer_types.update({'BUILDING_CSC_BAKERS_RIVER_ACCESS', 'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'})
    buildings = wonder_rows + [{"BuildingType": name, "Index": i + len(wonder_rows), "IsWonder": False} for i, name in enumerate(sorted(customer_types))]
    service_source = (MOD / "Lua_UI/WonderServices/CSC_WonderServicePlacement.lua").read_text()
    assert {row[0] for row in db.execute("SELECT BuildingType FROM CSC_QuarterWonderSales WHERE QuarterKey='TAILORS'")} == set(re.findall(r'HostType\s*=\s*"([^"]+)"', service_source))

    def runtime():
        lua = LuaRuntime(unpack_returned_tuples=True)
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
            ("Buildings", buildings),
            ("DistrictReplaces", [dict(row) for row in db.execute("SELECT * FROM DistrictReplaces")]),
            ("BuildingReplaces", [dict(row) for row in db.execute("SELECT * FROM BuildingReplaces")]),
            ("CSC_QuarterCustomerBuildings", [dict(row) for row in db.execute("SELECT * FROM CSC_QuarterCustomerBuildings")]),
            ("CSC_QuarterFlowBuildings", [dict(row) for row in db.execute("SELECT * FROM CSC_QuarterFlowBuildings")]),
            ("CSC_AbilityAttachModifiers", [dict(row) for row in db.execute("SELECT * FROM CSC_AbilityAttachModifiers")]),
            ("CSC_LensFlowYieldColors", [dict(row) for row in db.execute("SELECT * FROM CSC_LensFlowYieldColors")]),
            ("CSC_LensQuarterColors", [dict(row) for row in db.execute("SELECT * FROM CSC_LensQuarterColors")]),
            ("CSC_Stage3CustomerTransactions", [dict(row) for row in db.execute("SELECT * FROM CSC_Stage3CustomerTransactions")]),
            ("TypeTags", [dict(row) for row in db.execute("SELECT * FROM TypeTags")]),
            ("CSC_QuarterWonderSales", [dict(row) for row in db.execute("SELECT * FROM CSC_QuarterWonderSales")]),
            ("CSC_QuarterMaterialAdjacencyConfig", [dict(row) for row in db.execute("SELECT * FROM CSC_QuarterMaterialAdjacencyConfig")]),
        ):
            lua.execute(f"GameInfo.{name}=info({lua_value(rows)})")
        def include(name):
            directory = (MOD / "Lua_UI/Notifications_Suk_MCUIS" if name == "CSC_ServicePresentation"
                         else LENSES if name == "CSC_QuarterLensSupport" else MOD / "Lua_UI/Adjacencies")
            lua.execute((directory / f"{name}.lua").read_text(encoding="utf-8-sig"))
        lua.globals().include = include
        lua.execute("UI={}; Map.GetGridSize=function() return width,height end; PlayersVisibility={[0]={IsRevealed=function(_,x,y) return not world[y*width+x+1].hidden end}}")
        lua.execute("Cities={GetPlotPurchaseCity=function(plot) return plot.purchaseCity end}")
        lua.globals().UI.GetColorValue = lambda key: colors[key]
        lua.execute('''
            outlines={}; missingTint=true -- Existing suites also cover older cooked-art fallback.
            function GetTestOverlay(name)
                if missingArt then return nil end
                if missingTint and name:match('_Tint$') then return nil end
                if missingFill and name:match('_Fill$') then return nil end
                if missingLegacy and name=='CSC_QuarterPlacement' then return nil end
                if not outlines[name] then outlines[name]={channels={},colors={},styles={},visible=false,
                    ClearPlotChannel=function(self) assert(not name:match('_Ready$')); self.channels={} end,
                    ClearAll=function(self) assert(name:match('_Ready$') or name:match('_Fill$') or name:match('_Tint$') or name:match('_Services$')); self.channels={}; self.styles={}; self.tints={}; self.clears=(self.clears or 0)+1 end,
                    CreateSprites=function(self,plots,style,channel) assert(name:match('_Ready$') or name:match('_Fill$') or name:match('_Services$')); self.channels[channel]=plots; self.styles[channel]=style; self.creates=(self.creates or 0)+1 end,
                    HighlightColoredHexes=function(self,plots,color,channel) assert(name:match('_Tint$') and channel==0); self.tints[color]=plots; self.creates=(self.creates or 0)+1 end,
                    SetChannelOn=function(self,ch) assert(name:match('_Tint$') and ch==0); self.enabledChannel=ch end,
                    ResetAllWaves=function(self) assert(name:match('_Flow$')); self.waves={}; self.resets=(self.resets or 0)+1 end,
                    CreateLinearWaves=function(self,waves) assert(name:match('_Flow$')); self.waves=waves; self.creates=(self.creates or 0)+1 end,
                    SetVisible=function(self,v) self.visible=v; self.visibilityCalls=(self.visibilityCalls or 0)+1 end,
                    ShowHighlights=function(self,v) self.highlights=v end,
                    ShowBorders=function(self,v) self.borders=v end,
                    InitializeStyles=function(self,count,material)
                        assert(count>0 and material=='MapSearchBorder')
                        self.styleCount=count; self.material=material; self.colors={}
                    end,
                    SetBorderColors=function(self,ch,back,front) assert(self.styleCount and ch>=0 and ch<self.styleCount); self.borderColors=self.borderColors or {}; self.borderColors[ch]={back,front} end,
                    SetHighlightColor=function(self,ch,color)
                        assert(self.styleCount and ch>0 and ch<self.styleCount, 'Unallocated fill style')
                        self.colors[ch]=color
                    end,
                    SetPlotChannel=function(self,plots,ch) self.channels[ch]=plots end} end
                return outlines[name]
            end
            nativeHexes={}
            function OutlineContains(owner,index)
                local overlay=outlines['CSC_Quarter'..owner..'_Ready']
                if overlay then for _,plots in pairs(overlay.channels) do
                    for _,plot in ipairs(plots) do if plot==index then return true end end
                end end
                return false
            end
            UILens={GetOverlay=GetTestOverlay,CreateLensLayerHash=function(name) return name end,
                ClearLayerHexes=function(layer) nativeHexes[layer]={}; nativeClears=(nativeClears or 0)+1 end,
                SetLayerHexesColoredArea=function(layer,player,plots,color)
                    -- Actual native Appeal dispatch masks off caller alpha,
                    -- then sets the high byte to 0x80. Model that limitation.
                    color=color % 0x1000000 + 0x80000000
                    nativeHexes[layer]=nativeHexes[layer] or {}; nativeHexes[layer][color]=plots
                end}
        ''')
        include("CSC_QuarterLensSupport")
        for key in lua.globals().CSC_QuarterLensSupport.Quarters.keys():
            entry = lua.globals().CSC_QuarterLensSupport.GetLensLegend(key)
            assert entry.LensTextKey in texts
            for legend in entry.Legend.values():
                assert legend[1] in texts and legend[2] in colors.values()
        return lua

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
                expected = colors[f"COLOR_CSC_LENS_{kind}_{'IMPROVED' if improved and not pillaged else 'UNIMPROVED'}"] if kind else colors["COLOR_CSC_LENS_IGNORE"]
                assert bucket(key, 0) == expected, (key, resource, improved, pillaged)
                cases += 1
        for district in district_rows:
            p.district = district["Index"]
            p.resource = -1
            suffix = key + "_QUARTER_EMPTY" if district["DistrictType"] == f"DISTRICT_CSC_{key}_QUARTER" else "SALE_UNREADY" if district["DistrictType"] in sales else None
            assert bucket(key, 0) == (colors[f"COLOR_CSC_LENS_{suffix}"] if suffix else colors["COLOR_CSC_LENS_IGNORE"])
            cases += 1
        p.hidden = True
        assert bucket(key, 0) is None
        p.hidden = False

    # Discovery is queried each time, so revealing a tech updates an existing lens.
    lua.execute("world[1].district=-1; world[1].resource=GameInfo.Resources.RESOURCE_SILVER.Index; world[1].improvement=0; world[1].pillaged=false; GameInfo.Resources.RESOURCE_SILVER.PrereqTech='TECH_REVEAL'")
    assert bucket("TAILORS", 0) == colors["COLOR_CSC_LENS_IGNORE"]
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
    assert "MoreLensesMod" not in criteria
    project = ET.parse(MOD / "Civ Supply Chains.civ6proj")
    contents = {row.attrib["Include"].replace("\\", "/") for row in project.findall(".//{*}Content")}
    # More Lenses consumes RGBA columns from gameplay Colors. UpdateColors targets
    # a different colour-manager schema and silently leaves these rows unavailable.
    types = {"CSC_SupplyChainsLensPanel.lua": "ImportFiles", "CSC_Lens_Colors.sql": "UpdateDatabase", "CSC_Lens_Text.sql": "UpdateText",
             "CSC_QuarterFlowTrial.lua": "ImportFiles", "CSC_QuarterFlowTrial.xml": "AddUserInterfaces"}
    for file, action_type in types.items():
        path = f"Lua_UI/Lenses/{file}"
        actions = [row for row in source["blocks"]["inGameActions"] if path in row.get("files", [])]
        assert path in contents and len(actions) == 1
        assert actions[0]["type"] == action_type
        assert not actions[0].get("criteria")
    placement = [row for row in source["blocks"]["inGameActions"] if row["id"] == "CSC_QuarterPlacementOverlay"][0]
    assert not placement.get("criteria")
    assert placement["type"] == "ReplaceUIScript" and placement["properties"]["LuaContext"] == "PlotInfo"
    assert placement["properties"]["LuaReplace"] in contents
    chooser = next(row for row in source["blocks"]["inGameActions"] if row["id"] == "CSC_SupplyChainsLensPanel")
    assert chooser["type"] == "AddUserInterfaces" and not chooser.get("criteria")
    assert chooser["properties"]["Context"] == "InGame"
    assert all(file in contents for file in chooser["files"])
    imports = next(row for row in source["blocks"]["inGameActions"] if row["id"] == "CSC_QuarterLenses")
    assert "Lua_UI/Lenses/CSC_SupplyChainsLensPanel.lua" in imports["files"]
    assert not imports.get("criteria")
    assert not any("ModLens_CSC_Quarters.lua" in path for path in contents)
    assert not any(row.get("properties",{}).get("LuaContext") in ("MinimapPanel", "ModalLensPanel") for row in source["blocks"]["inGameActions"])
    ET.parse(LENSES / "CSC_SupplyChainsLensPanel.xml")
    print(f"Passed {cases} plot classifications; standalone CSC registration, discovery, visibility, pillage, unique districts, optional resources, SQL filters and build wiring.")

    scenarios = (args.lifecycle_scenario,) if args.lifecycle_scenario else (
        "unopened_close", "unopened_shutdown", "active_shutdown", "normal_toggle")
    for scenario in scenarios:
        test_supply_chains_panel(runtime, colors, lifecycle_scenario=scenario, panel_source=args.panel_source)
    if args.lifecycle_scenario:
        return
    db.execute("UPDATE CSC_QuarterMaterialAdjacencyConfig SET SourceFilter='' WHERE QuarterKey='TAILORS'")
    test_wonder_sales(runtime, colors, wonder_rows)
    if args.game:
        test_placement(args.game, runtime, colors)
        if args.more_lenses:
            for deferred in (False, True):
                test_placement(args.game, runtime, colors, args.more_lenses, deferred)
    test_supply_chains_panel(runtime, colors, args.more_lenses, install_more_lenses_listeners, panel_source=args.panel_source)
    test_customer_readiness(runtime, db)
    test_service_markers(runtime, db)
    test_ready_styling(runtime, colors)
    test_static_sprite_lifecycle(runtime)
    test_direct_rgba(runtime, colors)
    def tint_runtime():
        lua = runtime()
        lua.globals().missingTint = False
        return lua
    test_supply_chains_panel(tint_runtime, colors, args.more_lenses, install_more_lenses_listeners, panel_source=args.panel_source)
    if args.game:
        test_placement(args.game, tint_runtime, colors)
        if args.more_lenses:
            test_placement(args.game, tint_runtime, colors, args.more_lenses, True)
    test_supply_chain_flows(runtime, args.game)
    if args.gameplay_database:
        runtime_db = sqlite3.connect(args.gameplay_database.resolve().as_uri() + "?mode=ro", uri=True)
        schema = runtime_db.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='Colors'").fetchone()[0]
        fixture = sqlite3.connect(":memory:")
        fixture.executescript(schema)
        fixture.executescript((LENSES / "CSC_Lens_Colors.sql").read_text(encoding="utf-8-sig"))
        rows = fixture.execute("SELECT Type, Red, Green, Blue, Alpha FROM Colors WHERE Type LIKE 'COLOR_CSC_LENS_%'").fetchall()
        assert len(rows) == 48
        assert all(all(channel is not None and 0 <= channel <= 1 for channel in row[1:]) for row in rows)
        palette = {row[0]: row[1:] for row in rows}
        for kind in ('BASE', 'SPEC'):
            faint, ready, edge = (palette[f'COLOR_CSC_LENS_{kind}_{suffix}'] for suffix in ('UNIMPROVED', 'IMPROVED', 'OUTLINE'))
            assert faint[:3] == ready[:3] and faint[3] == (0.30 if kind=='BASE' else 0.20) and ready[3] == 0.60
            assert edge[3] == 1 and edge[:3] == ready[:3]
        assert palette['COLOR_CSC_LENS_SALE_UNREADY'][3] == 0.20
        assert palette['COLOR_CSC_LENS_SALE_DISTRICT'][3] == 0.60
        for kind in ('QUARTER','BASE','SPEC','SALE'):
            assert palette[f'COLOR_CSC_LENS_LEGEND_{kind}'][3] == 1
        assert palette['COLOR_CSC_LENS_QUARTER'][:3] == (1.0, 1.0, 1.0)
        assert palette['COLOR_CSC_LENS_QUARTER'][3] == 0.60
        assert palette['COLOR_CSC_LENS_QUARTER_EMPTY'][3] == 0.20
        assert palette['COLOR_CSC_LENS_QUARTER_OUTLINE'] == (1,1,1,1)
        def rgb_hex(name):
            return ''.join(f'{round(v*255):02x}' for v in palette[name][:3])
        for kind, value in {'BASE':'7a3700','SPEC':'ea8706','SALE':'b6a835'}.items():
            assert rgb_hex(f'COLOR_CSC_LENS_{kind}_OUTLINE') == value
            assert rgb_hex(f'COLOR_CSC_LENS_LEGEND_{kind}') == value
        quarters = {'BAKERS':'5f821c','TAILORS':'9037aa','APOTHECARIES':'0e54a9',
                    'CARPENTERS':'be6b0a','STONEMASONS':'be6b0a','BLACKSMITHS':'be6b0a',
                    'BREWERS':'c2af38','GOLDSMITHS':'c2af38'}
        assert dict(fixture.execute('SELECT QuarterKey, ColorType FROM CSC_LensQuarterColors')) == {
            key: f'COLOR_CSC_LENS_{key}_QUARTER' for key in quarters}
        for key, value in quarters.items():
            for suffix, alpha in (('',.6),('_EMPTY',.2),('_OUTLINE',1)):
                name=f'COLOR_CSC_LENS_{key}_QUARTER{suffix}'
                assert rgb_hex(name) == value and palette[name][3] == alpha
            art = ET.parse(MOD/'ArtDefs/CSC_QuarterResourceBorders.artdef')
            for style_suffix, color_suffix in ((f'Ready_{key}_QUARTER','_OUTLINE'),
                    (f'Fill_{key}_QUARTER_Unready','_EMPTY'),(f'Fill_{key}_QUARTER_Ready','')):
                style=next(row for row in art.findall('m_RootCollections/Element/Element')
                           if row.find('m_Name').get('text') == 'CSC_Lens_'+style_suffix)
                tint=next(row for row in style.findall('m_ChildCollections/Element/Element/m_Fields/m_Values/Element')
                          if row.find('m_ParamName').get('text') == 'TintColor')
                assert tuple(int(tint.find('m_'+c).text) for c in ('r','g','b')) == tuple(
                    round(v*255) for v in palette[f'COLOR_CSC_LENS_{key}_QUARTER{color_suffix}'][:3])
        for kind,value in {'PRODUCTION':'894000','GOLD':'fdec5d','FOOD':'468419',
                           'CULTURE':'bb44bd','SCIENCE':'0873e1','FAITH':'a7bede'}.items():
            assert rgb_hex(f'COLOR_CSC_LENS_FLOW_{kind}') == value
            assert fixture.execute('SELECT ColorType FROM CSC_LensFlowYieldColors WHERE YieldType=?',
                                   ('YIELD_'+kind,)).fetchone()[0] == 'COLOR_CSC_LENS_FLOW_'+kind
        print("Palette SQL/art verified: exact requested hex colours, eight Quarter palettes, six flow yields, Base unready30%/other unready20%/ready60%, opaque outlines/legend.")
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
                        assert entries[1].readyStyle == "SALE"
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


def test_customer_readiness(runtime, db):
    """Use actual gameplay transaction rows plus supplemental UI mappings."""
    lua = runtime()
    lua.execute("""
        resetWorld(1,1); world[1].resource=-1; world[1].improvement=-1
        present={}; damaged={}; locations={}; districtDamaged=false
        world[1].purchaseCity={
            GetDistricts=function() return {IsPillaged=function() return districtDamaged end} end,
            GetBuildings=function() return {
                HasBuilding=function(_,i) return present[i] or false end,
                IsPillaged=function(_,i) return damaged[i] or false end,
                GetBuildingsAtLocation=function(_,plot) local result={}; for i,location in pairs(locations) do if location==plot then result[#result+1]=i end end; return result end,
                GetBuildingLocation=function() error("Gameplay-only API called by UI") end,
            } end,
        }
        function classify(key) return CSC_QuarterLensSupport.GetPlotEntries(key,false)[1] end
    """)
    g = lua.globals()
    mappings = [tuple(row) for row in db.execute("SELECT QuarterKey,DistrictType,BuildingType FROM CSC_QuarterCustomerBuildings")]
    mappings += [(re.search(r'DISTRICT_CSC_(.*?)_QUARTER', row[0])[1], row[1], row[2]) for row in db.execute("SELECT SellerDistrictType,CustomerDistrictType,CustomerBuildingType FROM CSC_Stage3CustomerTransactions")]
    for key, district, building in mappings:
        district_types = [district] + [row[0] for row in db.execute("SELECT CivUniqueDistrictType FROM DistrictReplaces WHERE ReplacesDistrictType=?", (district,))]
        building_types = [building] + [row[0] for row in db.execute("SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType=?", (building,))]
        for d in district_types:
            g.world[1].district = g.GameInfo.Districts[d].Index
            for b in building_types:
                index = g.GameInfo.Buildings[b].Index
                lua.execute("present={}; damaged={}; locations={}; districtDamaged=false")
                assert g.classify(key).readyStyle is None
                assert g.classify(key).color == g.UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY')
                g.present[index] = True; g.locations[index] = 0
                assert g.classify(key).readyStyle == "SALE", (key,d,b)
                assert g.classify(key).color == g.UI.GetColorValue('COLOR_CSC_LENS_SALE_DISTRICT')
                g.locations[index] = 1
                assert g.classify(key).readyStyle is None  # Same city, wrong plot.
                g.locations[index] = 0; g.damaged[index] = True
                assert g.classify(key).readyStyle is None
                g.damaged[index] = False; g.districtDamaged = True
                assert g.classify(key).readyStyle is None
                g.districtDamaged = False; g.world[1].hidden = True
                assert g.classify(key) is None
                g.world[1].hidden = False
    lua.execute("""
        present={}; damaged={}; locations={}; districtDamaged=false
        world[1].district=GameInfo.Districts.DISTRICT_HARBOR.Index
        local i=GameInfo.Buildings.BUILDING_TEST_SECOND_LEVEL.Index
        present[i]=true; locations[i]=0
        assert(classify('TAILORS').readyStyle==nil) -- No recursive unique expansion.
    """)
    print("Passed customer readiness: gameplay Stage 3 + UI Stage 2/4 + Garden; direct unique districts/buildings, exact plots, empty/missing/pillaged/hidden venues and no recursive replacements.")


def test_ready_styling(runtime, colors):
    lua = runtime()
    lua.execute("""
        resetWorld(5,1)
        for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
        world[1].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[1].improvement=0
        world[2].resource=GameInfo.Resources.RESOURCE_DYES.Index; world[2].improvement=0
        world[3].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[3].pillaged=true
        world[4].district=GameInfo.Districts.DISTRICT_HARBOR.Index
        world[5].district=GameInfo.Districts.DISTRICT_WONDER.Index
        world[5].wonder=GameInfo.Buildings.BUILDING_BROADWAY.Index; world[5].complete=true
        local s=CSC_QuarterLensSupport
        local entries=s.GetPlotEntries('TAILORS',false)
        for _,owner in ipairs({'Lens','Placement'}) do
            assert(s.DrawOverlay(owner,entries))
            local fill=outlines['CSC_Quarter'..owner]
            local pattern=outlines['CSC_Quarter'..owner..'_Ready']
            if owner=='Lens' then
                assert(not fill.visible and next(nativeHexes.Hex_Coloring_Appeal_Level)==nil)
            else assert(not fill.visible and next(fill.channels)==nil) end
            do
                local textured=outlines['CSC_Quarter'..owner..'_Fill']
                assert(textured.visible and table.count(textured.channels)==5)
                assert(textured.styles[0]=='CSC_Lens_Fill_BASE_Unready' and textured.channels[0][1]==2)
                assert(textured.styles[1]=='CSC_Lens_Fill_BASE_Ready' and textured.channels[1][1]==0)
                assert(textured.styles[2]=='CSC_Lens_Fill_SPEC_Ready' and textured.channels[2][1]==1)
                assert(textured.styles[3]=='CSC_Lens_Fill_SALE_Unready' and textured.channels[3][1]==3)
                assert(textured.styles[4]=='CSC_Lens_Fill_SALE_Ready' and textured.channels[4][1]==4)
            end
            assert(pattern.visible and table.count(pattern.channels)==3)
            assert(pattern.styleCount==nil and pattern.borderColors==nil)
            assert(pattern.channels[0][1]==0 and pattern.styles[0]=='CSC_Lens_Ready_BASE')
            assert(pattern.channels[0][2]==2) -- Pillaged resource keeps its edge.
            assert(pattern.channels[1][1]==1 and pattern.styles[1]=='CSC_Lens_Ready_SPEC')
            assert(pattern.channels[2][1]==3 and pattern.channels[2][2]==4 and pattern.styles[2]=='CSC_Lens_Ready_SALE')
            assert(entries[3].ready==false and entries[4].ready==false)
            assert(entries[1].ready and entries[2].ready and entries[5].ready)
            assert(entries[4].color==UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY'))
            assert(entries[5].color==UI.GetColorValue('COLOR_CSC_LENS_SALE_DISTRICT'))
        end
        s.ClearOverlay('Placement')
        assert(not outlines.CSC_QuarterPlacement_Ready.visible and outlines.CSC_QuarterLens_Ready.visible)
        world[1].pillaged=true; world[2].improvement=-1; world[5].complete=false
        s.DrawOverlay('Lens',s.GetPlotEntries('TAILORS',false))
        assert(outlines.CSC_QuarterLens_Ready.visible)
        assert(nativeHexes.Hex_Coloring_Appeal_Level[UI.GetColorValue('COLOR_CSC_LENS_IGNORE')]==nil)
        assert(next(nativeHexes.Hex_Coloring_Appeal_Level)==nil)
        assert(outlines.CSC_QuarterLens_Fill.styles[0]=='CSC_Lens_Fill_BASE_Unready')
        assert(#outlines.CSC_QuarterLens_Fill.channels[0]==2)
        assert(s.DrawOverlay('Placement',s.GetPlotEntries('TAILORS',false)))
        assert(outlines.CSC_QuarterPlacement_Fill.visible and outlines.CSC_QuarterPlacement_Ready.visible)
        s.ClearOverlay('Placement'); assert(not outlines.CSC_QuarterPlacement_Ready.visible)
        s.ClearOverlay('Lens')
        assert(not outlines.CSC_QuarterLens.visible)
        assert(not outlines.CSC_QuarterLens_Fill.visible)
        missingArt=true; assert(s.DrawOverlay('Lens',entries)); s.ClearOverlay('Lens')
        assert(next(nativeHexes.Hex_Coloring_Appeal_Level)==nil)
    """)
    art = ET.parse(MOD / "ArtDefs/CSC_QuarterResourceBorders.artdef")
    layers = next(row for row in art.findall('m_RootCollections/Element') if row.find('m_CollectionName').get('text')=='Layers')
    assert {row.find('m_Name').get('text') for row in layers.findall('Element')} == {
        'CSC_Quarter'+owner+suffix for owner in ('Lens','Placement')
        for suffix in ('','_Ready','_Flow','_Fill','_Tint','_Services','_FlowChevrons','_FlowTrade','_FlowConveyorWaves')}
    for row in layers.findall('Element'):
        if row.find('m_Name').get('text').endswith(('_Ready','_Fill')):
            params = {x.find('m_ParamName').get('text'):x for x in row.findall('m_Fields/m_Values/Element')}
            assert params['Type'].find('m_Value').get('text') == 'SpriteOverlay'
            assert params['Material'].find('m_Value').get('text') == ''
            assert params['Priority'].find('m_fValue').text == '0'
    for kind in ('BASE','SPEC','SALE','QUARTER'):
        sprite = next(row for row in art.findall('.//m_ChildCollections/Element/Element')
                      if row.find('m_Name').get('text') == 'CSC_Lens_Ready_' + kind)
        fields = {row.find('m_ParamName').get('text'):row for row in sprite.findall('m_Fields/m_Values/Element')}
        assert fields['StaticTexture'].find('m_EntryName').get('text') == 'CSC_Lens_HexOutline'
        assert fields['GeomType'].find('m_Value').get('text') == 'HEX_GEO'
        palette = re.search(r"'COLOR_CSC_LENS_" + kind + r"_OUTLINE'\s*,\s*([.\d]+),\s*([.\d]+),\s*([.\d]+)", (LENSES/'CSC_Lens_Colors.sql').read_text()).groups()
        assert tuple(int(fields['TintColor'].find('m_'+c).text) for c in ('r','g','b')) == tuple(round(float(v)*255) for v in palette)
    from PIL import Image
    mask = Image.open(MOD/'Textures/CSC_Lens_HexOutline.dds').getchannel('A')
    assert mask.size == (512,512) and mask.getpixel((256,256)) == 0
    assert mask.getpixel((40,256)) == 255 and mask.getpixel((10,256)) == 0
    assert 0.05 < sum(v*count for v,count in enumerate(mask.histogram()))/(255*512*512) < 0.15
    # Opacity is part of the DDS, independent of Appeal's forced alpha. Both
    # readiness masks use the same geometry and stay clear of the bright edge.
    for state, alpha in (('Unready',51),('Ready',153),('BaseUnready',round(.30*255))):
        fill = Image.open(MOD/f'Textures/CSC_Lens_HexFill_{state}.dds')
        assert fill.getpixel((256,256)) == (255,255,255,alpha)
        assert fill.getpixel((40,256))[3] == 0 and fill.getpixel((10,256))[3] == 0
        if state == 'BaseUnready': continue
        for kind, suffix in {'BASE':'BASE_IMPROVED','SPEC':'SPEC_IMPROVED','SALE':'SALE_DISTRICT','QUARTER':'QUARTER'}.items():
            style = next(row for row in art.findall('.//m_ChildCollections/Element/Element')
                         if row.find('m_Name').get('text') == f'CSC_Lens_Fill_{kind}_{state}')
            fields = {row.find('m_ParamName').get('text'):row for row in style.findall('m_Fields/m_Values/Element')}
            mask = 'BaseUnready' if kind=='BASE' and state=='Unready' else state
            assert fields['StaticTexture'].find('m_EntryName').get('text') == f'CSC_Lens_HexFill_{mask}'
            assert fields['GeomType'].find('m_Value').get('text') == 'HEX_GEO'
            expected = colors['COLOR_CSC_LENS_'+suffix]
            assert tuple(int(fields['TintColor'].find('m_'+c).text) for c in ('r','g','b')) == tuple((expected>>s)&255 for s in (0,8,16))
    panel = ET.parse(LENSES/'CSC_SupplyChainsLensPanel.xml')
    assert not panel.findall(".//*[@ID='LegendTint']")
    lua.execute("""
        missingArt=false
        resetWorld(2,1)
        for _,p in ipairs(world) do p.resource=GameInfo.Resources.RESOURCE_COTTON.Index; p.improvement=0; p.district=-1 end
        CSC_QuarterLensSupport.DrawOverlay('Lens',CSC_QuarterLensSupport.GetPlotEntries('TAILORS',false))
        local pattern=outlines.CSC_QuarterLens_Ready
        assert(#pattern.channels[0]==2 and pattern.styles[0]=='CSC_Lens_Ready_BASE')
        assert(pattern.channels[0][1]~=pattern.channels[0][2]) -- One edge sprite per adjacent hex.
    """)
    assert not (LENSES / 'ModLens_CSC_Quarters.lua').exists()
    print("Passed shared ready styling: soft fills, per-plot hex-edge sprites in both owners, native hollow legend swatches, alpha-mask geometry, pillage/Wonder filtering and independent cleanup.")


def test_static_sprite_lifecycle(runtime):
    """Stable native sprites survive repeated refreshes; actual state changes repaint."""
    lua = runtime()
    lua.execute("""
        resetWorld(2,1)
        for _,p in ipairs(world) do
            p.resource=GameInfo.Resources.RESOURCE_COTTON.Index
            p.district=-1; p.improvement=-1
        end
        world[1].improvement=0
        local s=CSC_QuarterLensSupport
        local function draw(owner,key)
            local entries=s.GetPlotEntries(key or 'TAILORS',false)
            return s.DrawOverlay(owner or 'Lens',entries)
        end
        local _,stats=draw()
        assert(stats.fillRebuilt and stats.outlinesRebuilt)
        local fill=outlines.CSC_QuarterLens_Fill
        local edge=outlines.CSC_QuarterLens_Ready
        local fc,ec,fv,ev=fill.creates,edge.creates,fill.visibilityCalls,edge.visibilityCalls
        local nc=nativeClears
        for i=1,20 do
            local _,same=draw()
            assert(not same.fillRebuilt and not same.outlinesRebuilt and not same.backgroundRepainted)
        end
        assert(fill.creates==fc and edge.creates==ec)
        assert(fill.visibilityCalls==fv and edge.visibilityCalls==ev)
        assert(fill.clears==1 and edge.clears==1 and fill.visible and edge.visible)
        assert(nativeClears==nc)
        -- Reordering equal input must not recreate native instances either.
        local entries=s.GetPlotEntries('TAILORS',false)
        local _,same=s.DrawOverlay('Lens',{entries[2],entries[1]})
        assert(not same.fillRebuilt and not same.outlinesRebuilt)
        local _,settled=s.DrawOverlay('Lens',entries,true)
        assert(settled.backgroundRepainted and not settled.fillRebuilt and not settled.outlinesRebuilt)
        assert(nativeClears==nc+1)
        -- Equal category counts, different plots: replace fills, retain edges.
        world[1].pillaged=true; world[2].improvement=0
        local _,changed=draw()
        assert(changed.fillRebuilt and not changed.outlinesRebuilt)
        assert(fill.clears==2 and edge.clears==1)
        assert(fill.styles[0]=='CSC_Lens_Fill_BASE_Unready' and fill.channels[0][1]==0)
        assert(fill.styles[1]=='CSC_Lens_Fill_BASE_Ready' and fill.channels[1][1]==1)
        draw('Placement')
        local placementFill=outlines.CSC_QuarterPlacement_Fill
        local placementEdge=outlines.CSC_QuarterPlacement_Ready
        local pc,pe,pv=placementFill.clears,placementEdge.clears,placementFill.visibilityCalls
        for i=1,20 do draw('Placement') end
        assert(placementFill.clears==pc and placementEdge.clears==pe and placementFill.visibilityCalls==pv)
        s.ClearOverlay('Placement')
        assert(not placementFill.visible and not placementEdge.visible and fill.visible)
        local _,independent=draw()
        assert(not independent.fillRebuilt and not independent.outlinesRebuilt)
        -- Removing/changing the selected Quarter clears old sprites once.
        draw('Lens','BAKERS'); assert(not fill.visible and not edge.visible)
        local clears=fill.clears
        draw('Lens','BAKERS'); assert(fill.clears==clears)
        draw(); assert(fill.visible and edge.visible)
        s.ClearOverlay('Lens',true)
        assert(not fill.visible and not edge.visible)
        local _,reopened=draw()
        assert(reopened.fillRebuilt and reopened.outlinesRebuilt)
        -- Art temporarily absent invalidates cache, so its return rebuilds.
        missingArt=true; draw(); missingArt=false
        local _,restored=draw()
        assert(restored.fillRebuilt and restored.outlinesRebuilt)
        -- New placement art works independently of its legacy BorderOverlay.
        missingLegacy=true
        local painted,textured=draw('Placement')
        assert(painted and textured.textureFillAvailable and placementFill.visible)
        missingLegacy=false; missingFill=true
        local fallback,legacy=draw('Placement')
        assert(fallback and not legacy.textureFillAvailable and legacy.backend=='BorderOverlay (fallback)')
        assert(outlines.CSC_QuarterPlacement.visible)
        missingFill=false
        draw('Placement')
        assert(placementFill.visible and not outlines.CSC_QuarterPlacement.visible)
    """)
    print('Passed static sprite lifecycle: no clear/create/hide on unchanged refreshes, exact-plot readiness swaps, Quarter switches, independent owners, close/reopen and art restoration.')


def test_direct_rgba(runtime, colors):
    lua = runtime()
    lua.execute("""
        -- Strong alpha sets the sign bit. Preserve packed RGBA when a native
        -- colour is exposed as a signed 32-bit value rather than a positive ID.
        local originalColor=UI.GetColorValue
        UI.GetColorValue=function(key)
            local color=originalColor(key)
            return color>=0x80000000 and color-0x100000000 or color
        end
        missingTint=false; resetWorld(4,1)
        for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
        world[1].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[1].improvement=0
        world[2].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[2].improvement=-1
        world[3].resource=GameInfo.Resources.RESOURCE_DYES.Index; world[3].improvement=0
        world[4].district=GameInfo.Districts.DISTRICT_HARBOR.Index
        local s=CSC_QuarterLensSupport
        for _,owner in ipairs({'Lens','Placement'}) do
            local entries=s.GetPlotEntries('TAILORS',false)
            local ok,stats=s.DrawOverlay(owner,entries)
            assert(ok and stats.tintAvailable and stats.tintPlots==4 and stats.tintRebuilt)
            local tint=outlines['CSC_Quarter'..owner..'_Tint']
            assert(tint.visible and tint.enabledChannel==0)
            assert(tint.tints[UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED')][1]==0)
            assert(tint.tints[UI.GetColorValue('COLOR_CSC_LENS_BASE_UNIMPROVED')][1]==1)
            assert(tint.tints[UI.GetColorValue('COLOR_CSC_LENS_SPEC_IMPROVED')][1]==2)
            assert(tint.tints[UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY')][1]==3)
            assert(not outlines['CSC_Quarter'..owner..'_Fill'].visible)
            assert(outlines['CSC_Quarter'..owner..'_Ready'].visible)
            local clears,creates,visible=tint.clears,tint.creates,tint.visibilityCalls
            for i=1,20 do
                local _,same=s.DrawOverlay(owner,entries)
                assert(not same.tintRebuilt)
            end
            assert(tint.clears==clears and tint.creates==creates and tint.visibilityCalls==visible)
        end
        world[1].pillaged=true
        local _,changed=s.DrawOverlay('Lens',s.GetPlotEntries('TAILORS',false))
        assert(changed.tintRebuilt)
        local tint=outlines.CSC_QuarterLens_Tint
        assert(tint.tints[UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED')]==nil)
        assert(#tint.tints[UI.GetColorValue('COLOR_CSC_LENS_BASE_UNIMPROVED')]==2)
        s.ClearOverlay('Placement')
        assert(not outlines.CSC_QuarterPlacement_Tint.visible and tint.visible)
        s.ClearOverlay('Lens',true)
        assert(not tint.visible and next(tint.tints)==nil)
        s.DrawOverlay('Lens',s.GetPlotEntries('TAILORS',false))
        assert(tint.visible)
        missingTint=true
        local _,fallback=s.DrawOverlay('Placement',s.GetPlotEntries('TAILORS',false))
        assert(not fallback.tintAvailable and outlines.CSC_QuarterPlacement_Fill.visible)
    """)
    art=ET.parse(MOD/'ArtDefs/CSC_QuarterResourceBorders.artdef')
    for owner in ('Lens','Placement'):
        layer=next(e for e in art.findall('m_RootCollections/Element/Element') if e.find('m_Name').get('text')==f'CSC_Quarter{owner}_Tint')
        params={e.find('m_ParamName').get('text'):e for e in layer.findall('m_Fields/m_Values/Element')}
        assert params['Type'].find('m_Value').get('text')=='HexHighlightOverlay'
        assert params['Material'].find('m_Value').get('text')==''
        assert params['Pass'].find('m_nValue').text=='0'
    print('Passed direct RGBA fills: both native owners, separate 20/60 alpha buckets, channel 0 enabled, unchanged assignment cache, pillage, independent exits and old-art sprite fallback.')


def install_more_lenses_listeners(lua, root, deferred=False):
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
            g_ModLenses={ML_BUILDER={NonStandardFunction=function() morePaints=morePaints+1 end}},
            SetAppealHexes=function()
                morePaints=morePaints+1
                UILens.SetLayerHexesColoredArea('Hex_Coloring_Appeal_Level',0,{0},999)
            end,
            print=function(message) moreDiagnostics[#moreDiagnostics+1]=message end}, {__index=_G})
        moreModal=setmetatable({m_HexColoringAppeal='Hex_Coloring_Appeal_Level',g_ModLensModalPanel={},
            unpack=table.unpack,
            Controls={LensText=nativeTitle or control,KeyPanel=nativeKeyPanel or control,KeyScrollPanel=control},
            ResetKeyStackIM=function() end,AddKeyEntry=function() end,
            ShowAppealLensKey=function() end,
            print=function(message) error('More Lenses diagnostic: '..message) end}, {__index=_G})
        morePaints=0; moreDiagnostics={}
        UI.GetHeadSelectedUnit=function() return nil end
        UI.PlaySound=function() end
        Locale={Lookup=function(s) return s end,ToUpper=function(s) return s end}
    ''')
    for context, source in sources.items():
        lua.globals().native_listener_source = source
        lua.execute(f"assert(load(native_listener_source, 'More Lenses {context}', 't', more{context.title()}))()")
    lua.globals().deferMoreCallbacks = deferred
    lua.execute('''
        delayedMore={}
        function FlushMoreCallbacks()
            local pending=delayedMore; delayedMore={}
            for _,callback in ipairs(pending) do callback() end
        end
        local function listen(callback)
            Events.LensLayerOn.Add(function(layer)
                if deferMoreCallbacks then
                    delayedMore[#delayedMore+1]=function() callback(layer) end
                else callback(layer) end
            end)
        end
        LuaEvents.MinimapPanel_GetActiveModLens.Add(moreMini.GetActiveModdedLens)
        LuaEvents.MinimapPanel_SetActiveModLens.Add(moreMini.SetActiveModdedLens)
        LuaEvents.ModalLensPanel_AddLensEntry.Add(moreModal.AddLensEntry)
        listen(moreMini.OnLensLayerOn)
        listen(moreModal.OnLensLayerOn)
    ''')


def test_placement(game, runtime, colors, more_lenses=None, deferred=False):
    """Exercise native PlotInfo; placement must never touch lens/framework state."""
    art = ET.parse(MOD / "ArtDefs/CSC_QuarterResourceBorders.artdef")
    entry = next(row for row in art.findall("m_RootCollections/Element/Element")
                 if row.find("m_Name").get("text") == "CSC_QuarterPlacement")
    fields = {row.find("m_ParamName").get("text"): row for row in entry.findall("m_Fields/m_Values/Element")}
    assert fields["Type"].find("m_Value").get("text") == "BorderOverlay"
    assert fields["Material"].find("m_Value").get("text") == "MapSearchBorder"
    assert fields["Visible"].find("m_bValue").text == "false"
    assert all(row.text == "false" for row in art.findall(".//m_ReplaceMergedCollectionElements"))
    project = ET.parse(MOD / "Civ Supply Chains.civ6proj")
    assert any(row.get("Include") == "ArtDefs\\CSC_QuarterResourceBorders.artdef" for row in project.findall(".//{*}Content"))
    assert not any("CSC_Lenses.artdef" in row.get("Include", "") for row in project.findall(".//{*}Content"))
    spec = ET.fromstring((MOD / "Civ Supply Chains.Art.xml").read_text(encoding="utf-8-sig").replace("AssetObjects::", "AssetObjects.."))
    consumer = next(row for row in spec.findall("artConsumers/Element") if row.find("consumerName").get("text") == "Overlay")
    assert any(row.get("text") == "CSC_QuarterResourceBorders.artdef" for row in consumer.findall("relativeArtDefPaths/Element"))
    assert not any(row.get("text") == "CSC_Lenses.artdef" for row in spec.findall(".//relativeArtDefPaths/Element"))
    assert not (MOD / "ArtDefs/CSC_Lenses.artdef").exists()
    native = (game / "Base/Assets/UI/WorldView/PlotInfo.lua").read_text(encoding="utf-8-sig")
    wrapper = (LENSES / "PlotInfo_CSC_QuarterPlacement.lua").read_text(encoding="utf-8-sig")
    lua = runtime()
    g = lua.globals()
    lua.execute("g_ModLenses=nil; g_ModLensModalPanel=nil")
    g.UI.GetColorValue = lambda key: colors[key]
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
        -- Any attempt to borrow More Lenses state fails even when it is absent.
        for _,name in ipairs({'MinimapPanel_GetActiveModLens','MinimapPanel_SetActiveModLens','ModalLensPanel_AddLensEntry'}) do
            LuaEvents[name].Add(function() error('Placement called More Lenses: '..name) end)
        end
        UILens={GetOverlay=GetTestOverlay,
            CreateLensLayerHash=function(name) return name end,
            ClearLayerHexes=function(layer) log[#log+1]='clear:'..layer; areas[layer]={} end,
            ToggleLayerOn=function(layer)
                log[#log+1]='on:'..layer
                if not layers[layer] then layers[layer]=true; Events.LensLayerOn(layer) end
            end,
            ToggleLayerOff=function(layer)
                log[#log+1]='off:'..layer
                if layers[layer] then layers[layer]=false; Events.LensLayerOff(layer) end
            end,
            IsLayerOn=function(layer) return layers[layer] or false end,
            IsLensActive=function(name) return activeLens==name end,
            SetLayerHexesArea=function(layer,player,plots) areas[layer]=plots end,
            SetLayerHexesColoredArea=function() error('Placement painted a shared lens layer') end,
        }
        ContextPtr={SetInitHandler=function() end, SetShutdown=function(_,fn) shutdown=fn end}
        InstanceManager={new=function() return {DestroyInstances=function() end} end}
        Controls={PlotInfoContainer={}}
        UserConfiguration={ShowMapYield=function() return false end}
        GameInfo.GameCapabilities={CAPABILITY_DISPLAY_PLOT_YIELDS={}}
        InterfaceModeTypes={DISTRICT_PLACEMENT=7,BUILDING_PLACEMENT=8,SELECTION=0,VIEW_MODAL_LENS=9}
        CityOperationTypes={PARAM_DISTRICT_TYPE='district'}
        UI.GetInterfaceMode=function() return mode end
        UI.GetInterfaceModeParameter=function() return chosen end
        focusedCity=city
        UI.GetHeadSelectedCity=function() return citySelected and focusedCity or nil end
        Cities={GetPlotPurchaseCity=function(plot) return plot.purchaseCity end}
        resetWorld(4,1)
        for _,p in ipairs(world) do p.resource=-1; p.district=-1 end
    ''')
    original_include = g.include

    def include(name):
        if name == "PlotInfo":
            lua.execute(re.sub(r"\s*:\s*object\b", "", untype(native)))
        elif name in ("CSC_QuarterLensSupport", "CSC_AdjacencyCore"):
            original_include(name)
    g.include = include
    lua.execute(wrapper)
    if more_lenses:
        install_more_lenses_listeners(lua, more_lenses, deferred)
    lua.execute('''
        function CheckPlacementIsolation()
            if FlushMoreCallbacks then FlushMoreCallbacks() end
            assert(not layers.Hex_Coloring_Appeal_Level)
            assert(activeLens=='DistrictPlacement')
            if moreMini then assert(moreMini.m_CurrentModdedLensOn==nil and morePaints==0 and #moreDiagnostics==0) end
            for _,call in ipairs(log) do assert(call=='clear:Map_Hex_Mask',call) end
        end
        function PlacementPlots(color)
            local result={}
            local tint=outlines.CSC_QuarterPlacement_Tint
            if tint and tint.visible then return tint.tints[color] or result end
            local overlay=outlines.CSC_QuarterPlacement_Fill
            local colors={BASE={'BASE_UNIMPROVED','BASE_IMPROVED'},SPEC={'SPEC_UNIMPROVED','SPEC_IMPROVED'},SALE={'SALE_UNREADY','SALE_DISTRICT'},QUARTER={'QUARTER_EMPTY','QUARTER'}}
            for channel,plots in pairs(overlay.channels) do
                local kind,state=overlay.styles[channel]:match('CSC_Lens_Fill_([%u_]+)_(%a+)$')
                local suffix=colors[kind] and colors[kind][state=='Ready' and 2 or 1] or kind..(state=='Ready' and '' or '_EMPTY')
                if UI.GetColorValue('COLOR_CSC_LENS_'..suffix)==color then
                    for _,index in ipairs(plots) do result[#result+1]=index end
                end
            end
            return result
        end
        assert(LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Count()==1)
        assert(LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Count()==1)
        chosen=GameInfo.Districts.DISTRICT_CAMPUS.Index
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(#log==0 and outlines.CSC_QuarterPlacement==nil)
        RealizeShadowMask(); assert(areas.Map_Hex_Mask[1]==0 and #areas.Map_Hex_Mask==1)
        chosen=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index
        world[2].resource=GameInfo.Resources.RESOURCE_COTTON.Index; world[2].improvement=0
        world[3].district=GameInfo.Districts.DISTRICT_ROYAL_NAVY_DOCKYARD.Index
        world[4].resource=GameInfo.Resources.RESOURCE_DYES.Index; world[4].hidden=true
        original={0}; LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes(original)
        assert(#original==1 and original[1]==0)
        assert(#areas.Map_Hex_Mask==3) -- Include the Harbor's 20% yellow fill.
        fill=outlines.CSC_QuarterPlacement_Tint or outlines.CSC_QuarterPlacement_Fill
        assert(fill.visible and fill.highlights==nil and fill.borders==nil)
        assert(OutlineContains('Placement',1))
        assert(OutlineContains('Placement',2)) -- Harbor uses the faint fill without a customer building.
        assert(outlines.CSC_QuarterPlacement_Improved==nil)
        assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'))[1]==1)
        assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY'))[1]==2)
        CheckPlacementIsolation()
        -- Relevant sites remain visible in the selected city and all other
        -- territories, across every category and after city/tile ownership swaps.
        local function ownerCity(owner,id)
            return {GetOwner=function() return owner end,GetID=function() return id end,GetDistricts=function() return {IsPillaged=function() return false end} end,GetBuildings=function() return {HasBuilding=function() return false end,GetBuildingsAtLocation=function() return {} end} end}
        end
        local firstCity=ownerCity(0,101)
        local secondCity=ownerCity(0,102)
        local foreignCity=ownerCity(1,101) -- Same ID as firstCity, different player.
        for _,key in ipairs({'BAKERS','TAILORS'}) do
            local quarter=CSC_QuarterLensSupport.Quarters[key]
            chosen=GameInfo.Districts[quarter.districtType].Index
            world[1].district=chosen; world[1].purchaseCity=firstCity
            world[2].resource=GameInfo.Resources[next(quarter.baseSet)].Index; world[2].purchaseCity=firstCity
            world[3].district=GameInfo.Districts[next(quarter.saleSet)].Index; world[3].purchaseCity=secondCity
            world[4].hidden=false; world[4].resource=GameInfo.Resources[next(quarter.specSet)].Index
            world[4].purchaseCity=foreignCity
            focusedCity=firstCity
            LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
            assert(#PlacementPlots(UI.GetColorValue(quarter.quarterColor))==0)
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'))[1]==1)
            assert(PlacementPlots(UI.GetColorValue(quarter.quarterEmptyColor))[1]==0)
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY'))[1]==2 and OutlineContains('Placement',2))
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SPEC_IMPROVED'))[1]==3)
            assert(#areas.Map_Hex_Mask==4)
            assert(areas.Map_Hex_Mask[1]==0)
            local manualCount=0
            for _,plots in pairs(CSC_QuarterLensSupport.GetColorPlotTable(key,false)) do manualCount=manualCount+#plots end
            assert(manualCount==4) -- Manual lens still includes this city's materials/districts.
            world[4].purchaseCity=nil -- Unclaimed material remains highlighted.
            LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SPEC_IMPROVED'))[1]==3)
            focusedCity=secondCity -- Changing focus must not hide that city's customers.
            LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY'))[1]==2)
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'))[1]==1)
            assert(PlacementPlots(UI.GetColorValue(quarter.quarterEmptyColor))[1]==0)
            assert(#areas.Map_Hex_Mask==4)
            world[2].purchaseCity=secondCity -- A tile swap must not hide its materials.
            LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
            assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_BASE_IMPROVED'))[1]==1)
            focusedCity=firstCity
            for _,plot in ipairs(world) do plot.purchaseCity=firstCity end
            LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
            assert(fill.visible and #areas.Map_Hex_Mask==4)
            assert(OutlineContains('Placement',0) and OutlineContains('Placement',1))
            assert(OutlineContains('Placement',2) and OutlineContains('Placement',3))
        end
        focusedCity=city; chosen=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index
        for _,plot in ipairs(world) do plot.purchaseCity=nil end
        world[1].district=-1
        world[2].resource=GameInfo.Resources.RESOURCE_COTTON.Index
        world[3].district=GameInfo.Districts.DISTRICT_ROYAL_NAVY_DOCKYARD.Index
        world[4].resource=GameInfo.Resources.RESOURCE_DYES.Index; world[4].hidden=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        CheckPlacementIsolation()
        world[4].hidden=false; world[4].resource=-1
        world[4].district=GameInfo.Districts.DISTRICT_WONDER.Index
        world[4].wonder=GameInfo.Buildings.BUILDING_BROADWAY.Index; world[4].complete=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(#areas.Map_Hex_Mask==4)
        assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SALE_UNREADY'))[1]==2)
        assert(#PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_SALE_DISTRICT'))==1) -- Only the Wonder has a fill.
        assert(OutlineContains('Placement',2) and OutlineContains('Placement',3))
        local lighthouse=GameInfo.Buildings.BUILDING_LIGHTHOUSE.Index
        world[3].purchaseCity={
            GetOwner=function() return 0 end,GetID=function() return 999 end,
            GetDistricts=function() return {IsPillaged=function() return false end} end,
            GetBuildings=function() return {
                HasBuilding=function(_,i) return i==lighthouse end,
                IsPillaged=function() return false end,
                GetBuildingsAtLocation=function(_,plot) return plot==2 and {lighthouse} or {} end,
            } end,
        }
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(OutlineContains('Placement',2) and OutlineContains('Placement',3))
        world[3].purchaseCity=nil
        world[4].complete=false; world[2].pillaged=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(#areas.Map_Hex_Mask==3)
        assert(PlacementPlots(UI.GetColorValue('COLOR_CSC_LENS_BASE_UNIMPROVED'))[1]==1)
        assert(OutlineContains('Placement',1))
        assert(fill.visible and outlines.CSC_QuarterPlacement_Ready.visible)
        chosen=GameInfo.Districts.DISTRICT_CAMPUS.Index
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(not fill.visible and table.count(fill.channels)==0 and #areas.Map_Hex_Mask==1)
        -- Cancellation, confirmation, Wonder placement and direct modal takeover.
        chosen=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index
        world[2].resource=GameInfo.Resources.RESOURCE_WHEAT.Index; world[2].pillaged=false
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(fill.visible)
        LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes()
        assert(not fill.visible and #areas.Map_Hex_Mask==0)
        for _,nextMode in ipairs({InterfaceModeTypes.SELECTION,InterfaceModeTypes.BUILDING_PLACEMENT,InterfaceModeTypes.VIEW_MODAL_LENS}) do
            mode=InterfaceModeTypes.DISTRICT_PLACEMENT
            LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
            assert(fill.visible)
            -- Another overlay may already be painted before the mode event.
            areas.Hex_Coloring_Appeal_Level={[999]={3}}
            areas.Empire_Details={2}; areas.Yield_Icons={1}
            mode=nextMode; Events.InterfaceModeChanged(InterfaceModeTypes.DISTRICT_PLACEMENT,mode)
            assert(not fill.visible and table.count(fill.channels)==0 and #areas.Map_Hex_Mask==0)
            assert(areas.Hex_Coloring_Appeal_Level[999][1]==3 and areas.Empire_Details[1]==2 and areas.Yield_Icons[1]==1)
        end
        mode=InterfaceModeTypes.DISTRICT_PLACEMENT
        citySelected=false; LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0}); assert(not fill.visible)
        citySelected=true; chosen=-1
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0}); assert(not fill.visible)
        chosen=GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER.Index
        missingArt=true
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        RealizeShadowMask(); assert(#areas.Map_Hex_Mask==1 and not fill.visible)
        missingArt=false
        CheckPlacementIsolation()
        -- Actual native yield handlers still toggle their own layer afterward.
        LuaEvents.PlotInfo_ShowYieldIcons(); assert(layers.Yield_Icons)
        LuaEvents.PlotInfo_HideYieldIcons(); assert(not layers.Yield_Icons)
        if FlushMoreCallbacks then FlushMoreCallbacks() end
        -- Exercise native Empire dispatch, replacing only city-control rendering.
        empireShows=0; empireHides=0
        ShowEmpireDetails=function() empireShows=empireShows+1 end
        HideEmpireDetails=function() empireHides=empireHides+1 end
        UILens.ToggleLayerOn('Empire_Details'); UILens.ToggleLayerOff('Empire_Details')
        assert(empireShows==1 and empireHides==1)
        if FlushMoreCallbacks then FlushMoreCallbacks() end
        if moreMini then assert(moreMini.m_CurrentModdedLensOn==nil and morePaints==0 and #moreDiagnostics==0) end
        -- Existing manual selection and its independent resource edges survive.
        if moreMini then moreMini.m_CurrentModdedLensOn='ML_BUILDER' end
        local placementPaint=UILens.SetLayerHexesColoredArea
        UILens.SetLayerHexesColoredArea=function(layer,player,plots,color) areas[layer]=areas[layer] or {}; areas[layer][color]=plots end
        CSC_QuarterLensSupport.DrawOverlay('Lens',CSC_QuarterLensSupport.GetPlotEntries('BAKERS',false))
        UILens.SetLayerHexesColoredArea=placementPaint
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        assert(fill.visible and outlines.CSC_QuarterLens_Ready.visible)
        LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes()
        assert(not fill.visible and outlines.CSC_QuarterLens_Ready.visible)
        if moreMini then assert(moreMini.m_CurrentModdedLensOn=='ML_BUILDER') end
        -- Shutdown clears only the placement overlay and unregisters its hooks.
        LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes({0})
        shutdown()
        assert(not fill.visible and table.count(fill.channels)==0)
        assert(LuaEvents.StrategicView_MapPlacement_AddDistrictPlacementShadowHexes.Count()==0)
        assert(LuaEvents.StrategicView_MapPlacement_ClearDistrictPlacementShadowHexes.Count()==0)
        assert(Events.InterfaceModeChanged.Count()==0)
        assert(Events.LensLayerOff.Count()==1) -- Only native PlotInfo; CSC adds none.
    ''')
    framework = ("with deferred" if deferred else "with immediate") + " More Lenses callbacks" if more_lenses else "without More Lenses"
    print(f"Passed independent native placement {framework}: both Quarters, palette/masks, redraw, exits, missing art, yield/Empire handlers, manual overlay preservation and shutdown.")


if __name__ == "__main__":
    main()
