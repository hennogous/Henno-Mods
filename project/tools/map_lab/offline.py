"""Experimental offline execution of installed resource Lua on exported landscapes.

This is an API emulator, not the Civ VI engine. Outputs retain that distinction.
No game files, Workshop files, native settings, or survey evidence are modified.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import random
import re
import sqlite3
import sys
import time
import zlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE.parent / "map_survey"))
from analyze import analyze_map


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def lua_runtime(dependencies=None, backend='lua51'):
    if dependencies:
        sys.path.insert(0, str(dependencies))
    try:
        from importlib import import_module
        LuaRuntime = import_module('lupa.' + backend).LuaRuntime
    except ImportError:
        raise RuntimeError("Lupa's Lua 5.1 runtime is required. Pass --lua-dependencies pointing to the existing isolated test-deps directory.")
    return LuaRuntime(unpack_returned_tuples=True)


def derive_regions(data):
    """Explicit fallback: connected landmasses, never presented as native continents."""
    plots = data["plots"]
    remaining = {p["index"] for p in plots if not p["water"]}
    region = 0
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        stack = [first]
        while stack:
            index = stack.pop()
            plots[index]["continent"] = region
            neighbours = sorted(set(plots[index]["neighbors"]) & remaining)
            remaining.difference_update(neighbours)
            stack.extend(neighbours)
        region += 1
    remaining = {p["index"] for p in plots if p["water"]}
    while remaining:
        first = min(remaining)
        remaining.remove(first)
        stack, component = [first], []
        while stack:
            index = stack.pop()
            component.append(index)
            neighbours = sorted(set(plots[index]["neighbors"]) & remaining)
            remaining.difference_update(neighbours)
            stack.extend(neighbours)
        lake = len(component) <= 10 and all(plots[i]["terrain"] != "TERRAIN_OCEAN" for i in component)
        for index in component:
            plots[index]["continent"] = -1
            plots[index]["lake"] = lake


class OfflineWorld:
    def __init__(self, native, db_path, game_root, workshop_root, seed, resource_setting, lua_deps=None, approximate=False, lua_backend='lua51'):
        self.data = copy.deepcopy(native)
        self.data.pop("neighbor_normalization", None)
        self.native_data = native
        self.db = sqlite3.connect(":memory:")
        source = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
        source.backup(self.db)
        source.close()
        self.db.row_factory = sqlite3.Row
        # Only needed by Types/Kinds insert triggers; Lua uses local stable indices.
        self.db.create_function("Make_Hash", 1, lambda value: zlib.crc32(value.encode("utf-8")))
        self.game_root, self.workshop_root = game_root, workshop_root
        self.seed, self.resource_setting = seed, resource_setting
        self.rng = random.Random(seed)
        self.lua = lua_runtime(lua_deps, lua_backend)
        self.logs, self.sources, self.properties = [], {}, {}
        self.missing = []
        for field in ("continent", "river", "lake"):
            if any(field not in p for p in self.data["plots"]):
                self.missing.append(field)
        if self.missing and not approximate:
            raise RuntimeError("Native export lacks " + ", ".join(self.missing) + "; use a richer export or explicitly pass --approximate.")
        if "continent" in self.missing:
            derive_regions(self.data)
        for p in self.data["plots"]:
            p.setdefault("river", False)
            p.setdefault("lake", False)
        self.lua.globals().OFFLINE_RANDOM = lambda n, reason="": self.rng.randrange(max(1, int(n)))
        self.lua.globals().OFFLINE_LOG = lambda *args: self.logs.append("\t".join(map(str, args)))
        self.lua.globals().OFFLINE_INCLUDE = self.include
        self.lua.globals().OFFLINE_QUERY = lambda query: self.lua.table_from([self.lua.table_from(dict(r)) for r in self.db.execute(query)])

    def sql(self, path):
        self.sources[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.db.executescript(path.read_text(encoding="utf-8-sig"))

    def rows(self, table):
        return [dict(row) for row in self.db.execute(f'SELECT rowid AS _rowid, * FROM "{table}" ORDER BY rowid')]

    def bootstrap(self, oceans=False):
        if oceans:
            root = self.workshop_root / "2542898147"
            kelp = self.db.execute("SELECT 1 FROM Features WHERE FeatureType='FEATURE_SUK_KELP'").fetchone()
            seals = self.db.execute("SELECT 1 FROM Resources WHERE ResourceType='RESOURCE_SUK_SEALS'").fetchone()
            if bool(kelp) != bool(seals):
                raise RuntimeError("Partial Oceans database profile; capture a complete profile first")
            if not kelp:
                for name in ["Suk_Oceans_Features.sql", "Suk_Oceans_Resources.sql"]:
                    self.sql(root / "Core" / name)
        tables = {}
        for name in ("Resources", "Features", "Terrains", "Maps", "Resource_Distribution", "Resource_SeaLuxuries", "Resource_SeaStrategics", "Resource_ValidTerrains", "Resource_ValidFeatures", "TypeTags", "Feature_ValidTerrains"):
            tables[name] = self.rows(name)
        for name, key in [("Resources", "ResourceType"), ("Features", "FeatureType"), ("Terrains", "TerrainType"), ("Maps", "MapSizeType")]:
            for index, row in enumerate(tables[name]):
                row["Index"] = index
                row["Hash"] = index
                row["Type"] = row[key]
        self.tables = tables
        self.lua.globals().OFFLINE_TABLES = self.lua.table_from(tables, recursive=True)
        self.lua.globals().OFFLINE_DATA = self.lua.table_from(self.data, recursive=True)
        self.lua.globals().OFFLINE_SETTING = self.resource_setting
        self.lua.execute((HERE / "world.lua").read_text(encoding="utf-8"))
        # Verify the coordinate adapter against every exported native neighbour set.
        self.lua.execute("""
        for _,p in ipairs(OFFLINE_DATA.plots)do
          local expected={};for _,i in ipairs(p.neighbors)do expected[i]=true end
          local found=0
          for d=0,5 do local n=Map.GetAdjacentPlot(p.x,p.y,d);if n then assert(expected[n.index],'Coordinate/neighbor mismatch');found=found+1 end end
          assert(found==#p.neighbors,'Coordinate/neighbor count mismatch')
        end
        """)

    def include(self, name):
        if name == 'MapUtilities':
            # Use the installed helper: Civ draws and removes one element at a
            # time, including a final size-one draw. Fisher–Yates changes both
            # the output order and subsequent RNG position.
            path = self.game_root / 'Base/Assets/Maps/Utility/MapUtilities.lua'
            source = path.read_text(encoding='utf-8-sig')
            helper = re.search(r'function GetShuffledCopyOfTable\(incoming_table\).*?^end$', source, re.S | re.M)
            assert helper, 'Installed shuffle helper not found'
            self.sources[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
            self.lua.execute(helper.group(0), name=str(path) + ':GetShuffledCopyOfTable')
            return
        if name == "MapEnums":
            return
        allowed = {p.stem: p for p in (self.workshop_root / "2542898147/Lua").glob("*.lua")}
        if name not in allowed:
            raise RuntimeError(f"Unsupported include: {name}; no silent engine stubs are installed")
        self.execute(allowed[name])

    def execute(self, path):
        self.sources[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        self.lua.execute(path.read_text(encoding="utf-8-sig"), name=str(path))

    def run(self, generator="tar", luxury_types=4, oceans=False, clear=True):
        self.bootstrap(oceans)
        if clear:
            self.lua.execute("for _,p in ipairs(OFFLINE_DATA.plots) do p.resource=nil end")
        if generator != "keep":
            script = (self.workshop_root / "901009089/Utility/ResourceGenerator.lua" if generator == "tar"
                      else self.game_root / "DLC/Expansion2/Maps/Utility/ResourceGenerator.lua")
            self.execute(script)
            self.lua.globals().OFFLINE_LUXURY_TYPES = luxury_types
            self.lua.execute("ResourceGenerator.Create{resources=OFFLINE_SETTING,LuxuriesPerRegion=OFFLINE_LUXURY_TYPES,START_CONFIG=2}")
        if oceans:
            self.execute(self.workshop_root / "2542898147/Lua/Suk_OceansMapGen.lua")
        native = self.lua.globals().OFFLINE_DATA
        for index, plot in enumerate(self.data["plots"], 1):
            row = native.plots[index]
            for field in ["resource", "feature"]:
                if row[field] is None:
                    plot.pop(field, None)
                else:
                    plot[field] = row[field]
            feature = next((r for r in self.tables["Features"] if r["FeatureType"] == plot.get("feature")), None)
            plot["impassable"] = "MOUNTAIN" in plot["terrain"] or bool(feature and feature["Impassable"])
        self.data["resources"] = [{"type": r["ResourceType"], "class": r["ResourceClassType"]} for r in self.tables["Resources"]]
        self.data["features"] = [{"type": r["FeatureType"], "removable": bool(r["Removable"]), "impassable": bool(r["Impassable"]), "natural_wonder": bool(r["NaturalWonder"])} for r in self.tables["Features"]]
        self.data["material_tags"] = [{"type": r["Type"], "tag": r["Tag"]} for r in self.db.execute("SELECT Type,Tag FROM TypeTags WHERE Tag LIKE 'CLASS_CSC_%'")]
        self.data["harvests"] = [{"resource": r["ResourceType"], "tech": r["PrereqTech"]} for r in self.db.execute("SELECT * FROM Resource_Harvests")]
        return self.data


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--map", type=Path, required=True, help="Native map.json landscape")
    p.add_argument("--database", type=Path, required=True, help="Explicit native DebugGameplay.sqlite rule profile")
    p.add_argument("--game-root", type=Path, required=True)
    p.add_argument("--workshop-root", type=Path, required=True)
    p.add_argument("--lua-dependencies", type=Path)
    p.add_argument("--generator", choices=["tar", "stock", "keep"], default="tar")
    p.add_argument("--luxury-types", type=int, choices=range(1, 13), default=4)
    p.add_argument("--resources", type=int, choices=[1, 2, 3, 25, 45], default=3)
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--oceans", action="store_true")
    p.add_argument("--approximate", action="store_true", help="Explicitly allow reconstructed continents, missing rivers and inferred lakes")
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    if args.generator == "stock" and args.resources in (25, 45):
        p.error("Stock does not understand TAR's 25/45 settings")
    started = time.monotonic()
    world = OfflineWorld(read(args.map), args.database, args.game_root, args.workshop_root, args.seed, args.resources, args.lua_dependencies, args.approximate)
    data = world.run(args.generator, args.luxury_types, args.oceans, clear=args.generator != "keep")
    original_settings = read(args.map.parent / "settings.json") if (args.map.parent / "settings.json").exists() else {}
    settings = {"group": f"offline-{args.generator}-lux{args.luxury_types}" + ("-oceans" if args.oceans else ""), "map_number": original_settings.get("map_number", 1), "map_seed": original_settings.get("map_seed"), "resource_seed": args.seed, "speed": "OFFLINE", "resource_setting": args.resources, "csc": True}
    args.output.mkdir(parents=True, exist_ok=True)
    write(args.output / "map.json", data)
    write(args.output / "settings.json", settings)
    rows, sites, summary = analyze_map(args.output, read(HERE.parent / "map_survey/materials.json"))
    warning = "OFFLINE EMULATION · native landscape with emulated script execution. Placement eligibility and RNG are approximations; starting-position adjustment is absent."
    if world.missing:
        warning += " Missing native fields: " + ", ".join(world.missing) + ". Landmasses substitute for continents."
    result = {"id": settings["group"] + "-" + str(args.seed), "group": settings["group"], "groupLabel": f"Offline {args.generator.upper()} · {args.luxury_types} luxuries" + (" + Oceans" if args.oceans else ""), "number": settings["map_number"],
              "data": data, "settings": settings, "definitions": summary["resolved_definitions"], "reference": rows,
              "provenance": {"warning": warning, "native": False, "seed": args.seed, "rng": "Python MT19937, not Civ RNG", "missing_native_fields": world.missing,
                             "database": str(args.database.resolve()), "database_sha256": hashlib.sha256(args.database.read_bytes()).hexdigest(),
                             "source_map_sha256": hashlib.sha256(args.map.read_bytes()).hexdigest(), "lua_runtime": world.lua.eval("_VERSION"),
                             "rule_profile_note": "Uses the supplied database's rules; choosing stock Lua does not undo TAR or other SQL changes in that profile.",
                             "lua_source_sha256": world.sources, "seconds": round(time.monotonic() - started, 3)}}
    write(args.output / "viewer-map.json", result)
    write(args.output / "analysis.json", {"opportunities": rows, "summary": summary})
    (args.output / "lua.log").write_text("\n".join(world.logs) + "\n", encoding="utf-8")
    print(json.dumps({"viewer_import": str(args.output / "viewer-map.json"), "seconds": result["provenance"]["seconds"], "warning": warning}))


if __name__ == "__main__":
    main()
