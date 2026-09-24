from __future__ import annotations

import sqlite3
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


ROOT = Path(__file__).resolve().parent
MODINFO = ROOT / "WonderServiceHostingSpike.modinfo"
SERVICE_HOSTS = {
    "BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE": "BUILDING_ORACLE",
    "BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI": "BUILDING_BOLSHOI_THEATRE",
    "BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY": "BUILDING_BROADWAY",
    "BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY": "BUILDING_SYDNEY_OPERA_HOUSE",
}


def fail(message: str) -> None:
    raise AssertionError(message)


def validate_manifest() -> None:
    tree = ET.parse(MODINFO)
    root = tree.getroot()

    if root.tag != "Mod":
        fail("Manifest root must be <Mod>.")
    if root.attrib.get("version") != "3":
        fail("Exact-placement spike manifest version must be 3.")

    criteria_ids = {
        node.attrib["id"] for node in root.findall("./ActionCriteria/Criteria")
    }
    action_ids: list[str] = []

    for action in root.findall("./InGameActions/*"):
        action_id = action.attrib.get("id")
        if not action_id:
            fail(f"{action.tag} is missing an id.")
        action_ids.append(action_id)

        for criterion in action.findall("Criteria"):
            if criterion.text not in criteria_ids:
                fail(f"{action_id} references unknown criterion {criterion.text!r}.")

        for file_node in action.findall("File"):
            path = ROOT / (file_node.text or "")
            if not path.is_file():
                fail(f"{action_id} references missing file {file_node.text!r}.")

        lua_replace = action.find("./Properties/LuaReplace")
        if lua_replace is not None:
            path = ROOT / (lua_replace.text or "")
            if not path.is_file():
                fail(f"{action_id} references missing LuaReplace {lua_replace.text!r}.")

    if len(action_ids) != len(set(action_ids)):
        fail("InGame action ids must be unique.")

    declared_files = {
        node.text for node in root.findall("./Files/File") if node.text
    }
    for relative in declared_files:
        if not (ROOT / relative).is_file():
            fail(f"<Files> references missing file {relative!r}.")

    for action in root.findall("./InGameActions/*"):
        paths = [node.text for node in action.findall("File") if node.text]
        lua_replace = action.find("./Properties/LuaReplace")
        if lua_replace is not None and lua_replace.text:
            paths.append(lua_replace.text)
        for relative in paths:
            if relative not in declared_files:
                fail(f"Action file {relative!r} is absent from <Files>.")

    for xml_path in ROOT.glob("UI/*.xml"):
        ET.parse(xml_path)
        if not xml_path.with_suffix(".lua").is_file():
            fail(f"AddUserInterfaces XML has no matching Lua: {xml_path.name}")

    city_breakdown = (ROOT / "UI/CSC_WonderServiceCityBreakdown.lua").read_text(
        encoding="utf-8"
    )
    if ":GetBuildingLocation(" in city_breakdown:
        fail("City Breakdown must not call gameplay-only GetBuildingLocation.")

    suk_tooltip = (ROOT / "UI/CSC_WonderServicePlotTooltip_Suk.lua").read_text(
        encoding="utf-8"
    )
    if "include('Suk_PlotTooltips')" in suk_tooltip:
        fail("Suk tooltip wrapper must not include another mod's LuaReplace source.")
    if "'PlotTooltip_Expansion2.lua'" not in suk_tooltip:
        fail("Suk tooltip wrapper must include a known working base tooltip.")

    gameplay_lua = (ROOT / "Scripts/CSC_WonderServiceHostingSpike.lua").read_text(
        encoding="utf-8"
    )
    if ":CreateBuilding(service.Index, hostPlot)" not in gameplay_lua:
        fail("Gameplay reconciler must create each Service on the explicit host plot.")
    if ":RemoveBuilding(service.Index)" not in gameplay_lua:
        fail("Gameplay reconciler must remove misplaced saved-game instances.")

    for service_type, host_type in SERVICE_HOSTS.items():
        for path, text in (
            ("diagnostics", gameplay_lua),
            ("City Breakdown", city_breakdown),
            ("Suk tooltip", suk_tooltip),
        ):
            if service_type not in text:
                fail(f"{path} is missing Service variant {service_type}.")
        if host_type not in gameplay_lua or host_type not in city_breakdown:
            fail(f"Runtime mappings are missing host {host_type}.")


def validate_sql() -> None:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE Types (
            Type TEXT PRIMARY KEY,
            Kind TEXT NOT NULL
        );
        CREATE TABLE Buildings (
            BuildingType TEXT PRIMARY KEY,
            Name TEXT,
            Description TEXT,
            Cost INTEGER,
            PrereqDistrict TEXT,
            PurchaseYield TEXT,
            Maintenance INTEGER,
            CitizenSlots INTEGER,
            AdvisorType TEXT,
            MustPurchase INTEGER DEFAULT 0
        );
        CREATE TABLE Buildings_XP2 (
            BuildingType TEXT PRIMARY KEY,
            Pillage INTEGER
        );
        CREATE TABLE Building_CitizenYieldChanges (
            BuildingType TEXT,
            YieldType TEXT,
            YieldChange INTEGER,
            PRIMARY KEY (BuildingType, YieldType)
        );
        CREATE TABLE Modifiers (
            ModifierId TEXT PRIMARY KEY,
            ModifierType TEXT
        );
        CREATE TABLE ModifierArguments (
            ModifierId TEXT,
            Name TEXT,
            Value TEXT,
            PRIMARY KEY (ModifierId, Name)
        );
        CREATE TABLE BuildingModifiers (
            BuildingType TEXT,
            ModifierId TEXT,
            PRIMARY KEY (BuildingType, ModifierId)
        );
        CREATE TABLE LocalizedText (
            Tag TEXT,
            Language TEXT,
            Text TEXT,
            PRIMARY KEY (Tag, Language)
        );
        CREATE TABLE IconDefinitions (
            Name TEXT PRIMARY KEY,
            Atlas TEXT,
            'Index' INTEGER
        );

        INSERT INTO Buildings (BuildingType) VALUES
            ('BUILDING_BOLSHOI_THEATRE'),
            ('BUILDING_BROADWAY'),
            ('BUILDING_SYDNEY_OPERA_HOUSE'),
            ('BUILDING_ORACLE');
        INSERT INTO IconDefinitions (Name, Atlas, 'Index')
        VALUES ('ICON_BUILDING_AMPHITHEATER', 'ICON_ATLAS_BUILDINGS', 7);
        """
    )

    connection.executescript(
        (ROOT / "Data/CSC_WonderServiceHostingSpike.sql").read_text(encoding="utf-8")
    )
    connection.executescript(
        (ROOT / "Text/CSC_WonderServiceHostingSpike_Text.sql").read_text(
            encoding="utf-8"
        )
    )
    connection.executescript(
        (ROOT / "Icons/CSC_WonderServiceHostingSpike_Icons.sql").read_text(
            encoding="utf-8"
        )
    )

    for service_type in SERVICE_HOSTS:
        building = connection.execute(
            "SELECT PrereqDistrict, CitizenSlots, MustPurchase FROM Buildings "
            "WHERE BuildingType = ?",
            (service_type,),
        ).fetchone()
        if building != ("DISTRICT_WONDER", 0, 1):
            fail(f"Unexpected service building row for {service_type}: {building!r}")

        specialist_yields = connection.execute(
            "SELECT YieldType, YieldChange FROM Building_CitizenYieldChanges "
            "WHERE BuildingType = ?",
            (service_type,),
        ).fetchall()
        if specialist_yields:
            fail(f"Wonder-hosted Service must have no specialist yields: {service_type}")

        icon = connection.execute(
            'SELECT Atlas, "Index" FROM IconDefinitions WHERE Name = ?',
            (f"ICON_{service_type}",),
        ).fetchone()
        if icon != ("ICON_ATLAS_BUILDINGS", 7):
            fail(f"Unexpected icon alias for {service_type}: {icon!r}")

    for table in ("Modifiers", "ModifierArguments", "BuildingModifiers"):
        count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if count != 0:
            fail(f"Exact-placement spike must not contain SQL grants in {table}.")


def main() -> int:
    validate_manifest()
    validate_sql()
    print("PASS: Wonder-hosted Service spike manifest, XML, paths, and SQL")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, ET.ParseError, sqlite3.Error) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
