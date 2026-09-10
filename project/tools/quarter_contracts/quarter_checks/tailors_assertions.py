"""Executable Tailors phase assertions.

Each phase begins red. Replace its sentinel with contract-derived database,
modifier-graph, replacement, and localization assertions before implementing
that phase. The phase handoff validator cannot pass while the sentinel remains.
"""

from __future__ import annotations

from pathlib import Path
import hashlib
import json
import re
import sqlite3
import xml.etree.ElementTree as ET
from typing import Any


REQUIREMENTS_BY_PHASE = {
    "foundation": {
        "I.IDENTITY_AND_TYPES",
        "I.MATERIAL_CLASSES",
        "I.DISTRICT_DEFINITION",
        "I.DISTRICT_MATERIAL_ADJACENCY",
        "I.DISTRICT_CUSTOMER_ADJACENCIES",
        "I.DISTRICT_RIVER",
    },
    "materials_and_stage2": {
        "I.MATERIAL_IMPROVEMENT_EXCHANGES",
        "I.STAGE2_DEFINITION",
        "I.STAGE2_BASE_INPUT",
        "I.STAGE2_CUSTOMER_AND_LOCAL",
        "I.DOCKMASTER",
    },
    "stage3": {
        "I.STAGE3_DEFINITION_LOCAL_SPECIALISTS",
        "I.STAGE3_POP_CUSTOMERS",
        "I.SACRISTAN",
        "I.STAGE3_TRADE",
    },
    "stage4": {
        "I.STAGE4_DEFINITION_LOCAL_SPECIALISTS",
        "I.STAGE4_SPEC_INPUT",
        "I.STAGE4_POP_CUSTOMERS",
        "I.STAGE_MANAGER",
        "I.STAGE4_TRADE",
    },
    "compatibility": {"I.CITY_LIGHTS", "I.PRESERVED_RESOURCE_MODSUPPORT"},
    "localization_and_integration": {
        "I.LOCALIZATION_COMPLETE",
        "I.MODBUDDY_WIRING",
    },
    "art_integration": {"I.ART_PROPERTY_BRIDGE"},
}


IMPLEMENTED_ASSERTION_PHASES = {"foundation", "materials_and_stage2", "stage3", "art_integration"}


def _runtime_database() -> Path:
    return Path.home() / "AppData/Local/Firaxis Games/Sid Meier's Civilization VI/Cache/DebugGameplay.sqlite"


def _clean_tailors_rows(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = OFF")
    tables = connection.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    ).fetchall()
    for (table,) in tables:
        columns = connection.execute(f'PRAGMA table_info("{table}")').fetchall()
        text_columns = [row[1] for row in columns if str(row[2]).upper() in {"TEXT", ""}]
        if not text_columns:
            continue
        predicate = " OR ".join(f'"{column}" LIKE ?' for column in text_columns)
        try:
            connection.execute(f'DELETE FROM "{table}" WHERE {predicate}', ["%TAILORS%"] * len(text_columns))
        except sqlite3.DatabaseError:
            # Read-only/virtual helper tables are irrelevant to gameplay rows.
            continue


def _load_phase_database(root: Path) -> tuple[sqlite3.Connection | None, list[str]]:
    source = _runtime_database()
    if not source.is_file():
        return None, [f"offline gameplay cache is missing: {source}"]
    source_connection = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True)
    connection = sqlite3.connect(":memory:")
    source_connection.backup(connection)
    source_connection.close()
    connection.create_function(
        "Make_Hash",
        -1,
        lambda *values: int.from_bytes(
            hashlib.sha256("|".join(str(value) for value in values).encode("utf-8")).digest()[:7],
            "big",
        ),
    )
    _clean_tailors_rows(connection)
    scripts = [
        "Civ Supply Chains/Data/CSC_Q_TAILORS.sql",
        "Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql",
        "Civ Supply Chains/Data/CSC_Q_TAILORS_MC_MODE.sql",
        "Civ Supply Chains/Data/CSC_Q_TAILORS_MC_MODE_GOLD.sql",
        "Civ Supply Chains/Lua_UI/Ruivo_Adjacencies/CSC_Ruivo_AdjacencyProcessor.sql",
        "Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/CSC_UI_DB_Dynamic.sql",
    ]
    try:
        for relative in scripts:
            connection.executescript((root / relative).read_text(encoding="utf-8-sig"))
    except (OSError, sqlite3.DatabaseError) as failure:
        connection.close()
        return None, [f"offline database integration failed: {failure}"]
    return connection, []


def _scalar(connection: sqlite3.Connection, sql: str, values: tuple[Any, ...] = ()) -> Any:
    row = connection.execute(sql, values).fetchone()
    return None if row is None else row[0]


def _expect(failures: list[str], actual: Any, expected: Any, label: str) -> None:
    if actual != expected:
        failures.append(f"{label}: expected {expected!r}, found {actual!r}")


def _validate_tailors_icon_bindings(
    root: Path, bindings: tuple[tuple[str, int], ...]
) -> list[str]:
    failures: list[str] = []
    icon_source = (
        root / "Civ Supply Chains/Icons/CSC_TAILORS_ICONS.sql"
    ).read_text(encoding="utf-8")
    for icon, index in bindings:
        exact_row = (
            r"\(\s*" + re.escape(f"'{icon}'")
            + r"\s*,\s*'ICON_ATLAS_CSC_TAILORS'\s*,\s*"
            + str(index)
            + r"\s*\)"
        )
        if not re.search(exact_row, icon_source):
            failures.append(f"Tailors icon binding missing: {icon} index {index}")
    return failures


def _validate_tailors_building_chain(
    root: Path,
    expected_levels: dict[str, str],
    *,
    empty_levels: tuple[str, ...] = (),
) -> list[str]:
    failures: list[str] = []
    artdef_path = root / "Civ Supply Chains/ArtDefs/CSC_Buildings.artdef"
    try:
        document = ET.parse(artdef_path).getroot()
    except ET.ParseError as failure:
        return [f"CSC_Buildings.artdef is not valid XML: {failure}"]

    root_collections = document.findall("./m_RootCollections/Element")
    building_chains = next(
        (
            element
            for element in root_collections
            if element.find("./m_CollectionName") is not None
            and element.find("./m_CollectionName").get("text") == "BuildingChains"
        ),
        None,
    )
    if building_chains is None:
        return ["CSC_Buildings.artdef is missing its BuildingChains collection"]

    chains = [
        element
        for element in building_chains.findall("./Element")
        if element.find("./m_Name") is not None
        and element.find("./m_Name").get("text") == "CSC_TAILORS_BuildingChain"
    ]
    if len(chains) != 1:
        return [
            "CSC_Buildings.artdef must contain exactly one "
            f"CSC_TAILORS_BuildingChain; found {len(chains)}"
        ]

    collections = {
        element.find("./m_CollectionName").get("text"): element
        for element in chains[0].findall("./m_ChildCollections/Element")
        if element.find("./m_CollectionName") is not None
    }
    required_collections = {
        "Districts",
        "Buildings (Level 1)",
        "Buildings (Level 2)",
        "Buildings (Level 3)",
    }
    missing = sorted(required_collections - set(collections))
    if missing:
        failures.append("Tailors BuildingChain missing collections: " + ", ".join(missing))

    expected = {"Districts": "DISTRICT_CSC_TAILORS_QUARTER", **expected_levels}
    for collection_name, expected_type in expected.items():
        collection = collections.get(collection_name)
        if collection is None:
            continue
        references = collection.findall(
            "./Element/m_Fields/m_Values/Element[@class='AssetObjects..ArtDefReferenceValue']"
        )
        actual_types = [
            reference.find("./m_ElementName").get("text")
            for reference in references
            if reference.find("./m_ElementName") is not None
        ]
        if actual_types != [expected_type]:
            failures.append(
                f"Tailors BuildingChain {collection_name}: expected exactly "
                f"{expected_type}, found {actual_types!r}"
            )
            continue
        reference = references[0]
        is_district = collection_name == "Districts"
        expected_fields = {
            "m_RootCollectionName": "District" if is_district else "Building",
            "m_ArtDefPath": "CSC_Districts.artdef" if is_district else "CSC_Buildings.artdef",
            "m_TemplateName": "Districts" if is_district else "Buildings",
            "m_ParamName": "District" if is_district else "Building",
        }
        for field, expected_value in expected_fields.items():
            node = reference.find(f"./{field}")
            actual_value = None if node is None else node.get("text")
            if actual_value != expected_value:
                failures.append(
                    f"Tailors BuildingChain {collection_name} {field}: expected "
                    f"{expected_value}, found {actual_value}"
                )

    for collection_name in empty_levels:
        collection = collections.get(collection_name)
        if collection is not None and collection.findall("./Element"):
            failures.append(
                f"Tailors BuildingChain {collection_name} must remain empty until its stage"
            )
    return failures


def _validate_dockmaster_mcuis_signs(source: str) -> list[str]:
    failures: list[str] = []
    dockmaster_state_keys = (
        "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION",
        "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_NEW",
        "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_INCREASED",
        "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_DECREASED",
        "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_REMOVED",
    )
    for key in dockmaster_state_keys:
        match = re.search(rf"## {key}\n(.*?)(?=\n## |\Z)", source, flags=re.DOTALL)
        if match is None:
            failures.append(f"Dockmaster MCUIS localization missing {key}")
        else:
            fragment = match.group(1).strip()
            if re.search(r"(?:[+-]\s*\{1_|\b(?:less|lost|fewer)\s+\{[12]_)", fragment):
                failures.append(
                    f"{key}: MCUIS dynamically signs amounts; do not add a literal sign or directional qualifier"
                )
            if key != "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION" and fragment.endswith(
                (".", "!", "?")
            ):
                failures.append(
                    f"{key}: notification state fragments omit terminal punctuation because the shared summary appends it"
                )
    return failures


def _validate_resource_pedia_contract(root: Path) -> list[str]:
    failures: list[str] = []
    optional_bindings = (
        ("RESOURCE_AOM_HEMP", "CLASS_CSC_TAILORS_BASE", "Hemp", "Base Materials:",
         "Civ Supply Chains/ModSupport/ModSupport_CH.sql",
         "project/localization/ModSupport_CH_TAILORS_TEXT.md",
         "Civ Supply Chains/ModSupport/ModSupport_CH_TAILORS_TEXT.sql",
         "ModSupport_CH_Tailors_Text", ["ModSupport_CH"]),
        ("RESOURCE_LEU_P0K_LLAMAS", "CLASS_CSC_TAILORS_BASE", "Llamas", "Base Materials:",
         "Civ Supply Chains/ModSupport/ModSupport_LAR_A.sql",
         "project/localization/ModSupport_LAR_A_TAILORS_TEXT.md",
         "Civ Supply Chains/ModSupport/ModSupport_LAR_A_TAILORS_TEXT.sql",
         "ModSupport_LAR_A_Tailors_Text", ["CSC_A_RESOURCES", "ModSupport_LAR"]),
        ("RESOURCE_BAMBOO", "CLASS_CSC_TAILORS_BASE", "Bamboo", "Base Materials:",
         "Civ Supply Chains/ModSupport/ModSupport_R2.sql",
         "project/localization/ModSupport_R2_TEXT.md",
         "Civ Supply Chains/ModSupport/ModSupport_R2_TEXT.sql",
         "ModSupport_R2_Text", ["ModSupport_R2"]),
        ("RESOURCE_GOLD2", "CLASS_CSC_TAILORS_SPEC", "Gold", "Specialty Materials:",
         "Civ Supply Chains/ModSupport/ModSupport_R2.sql",
         "project/localization/ModSupport_R2_TEXT.md",
         "Civ Supply Chains/ModSupport/ModSupport_R2_TEXT.sql",
         "ModSupport_R2_Text", ["ModSupport_R2"]),
        ("RESOURCE_CASHMERE", "CLASS_CSC_TAILORS_SPEC", "Cashmere", "Specialty Materials:",
         "Civ Supply Chains/ModSupport/ModSupport_R2_A.sql",
         "project/localization/ModSupport_R2_A_TAILORS_TEXT.md",
         "Civ Supply Chains/ModSupport/ModSupport_R2_A_TAILORS_TEXT.sql",
         "ModSupport_R2_A_Tailors_Text", ["CSC_A_RESOURCES", "ModSupport_R2"]),
        ("RESOURCE_GOLD", "CLASS_CSC_TAILORS_SPEC", "Gold", "Specialty Materials:",
         "Civ Supply Chains/ModSupport/ModSupport_SR.sql",
         "project/localization/ModSupport_SR_TAILORS_TEXT.md",
         "Civ Supply Chains/ModSupport/ModSupport_SR_TAILORS_TEXT.sql",
         "ModSupport_SR_Tailors_Text", ["ModSupport_SR"]),
    )
    manifest_path = root / "project/modbuddy/CivSupplyChains.actions.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actions = {action["id"]: action for action in manifest["blocks"]["inGameActions"]}
    project_text = (root / "Civ Supply Chains/Civ Supply Chains.civ6proj").read_text(encoding="utf-8-sig")

    localization_paths = {
        "project/localization/CSC_BAKERS_TEXT.md",
        "project/localization/CSC_TAILORS_TEXT.md",
        "Civ Supply Chains/Text/CSC_BAKERS_TEXT.sql",
        "Civ Supply Chains/Text/CSC_TAILORS_TEXT.sql",
    }
    localization_paths.update(binding[5] for binding in optional_bindings)
    localization_paths.update(binding[6] for binding in optional_bindings)
    localization_paths.update(
        path.relative_to(root).as_posix()
        for path in (root / "project/localization").glob("*.md")
    )
    localization_paths.update(
        path.relative_to(root).as_posix()
        for folder in (root / "Civ Supply Chains/Text", root / "Civ Supply Chains/ModSupport")
        for path in folder.glob("*.sql")
    )
    for relative in sorted(localization_paths):
        text = (root / relative).read_text(encoding="utf-8-sig")
        if "Base material:" in text or "Specialty material:" in text:
            failures.append(f"{relative}: singular resource-role line would create duplicate pedia lists")
        if re.search(r"(?:Base|Specialty) Materials:\[NEWLINE\]\[ICON_BULLET\]", text):
            failures.append(f"{relative}: resource role label must leave one open line before its first bullet")

    for relative in (
        "project/localization/CSC_BAKERS_TEXT.md",
        "project/localization/CSC_TAILORS_TEXT.md",
    ):
        text = (root / relative).read_text(encoding="utf-8-sig")
        titles = re.findall(
            r"## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_(?:BAKERS|TAILORS)_QUARTER_CHAPTER_(?:CSCBASE|CSCSPEC|CSCGOODS|CSCSALES)_TITLE\n([^\n]+)",
            text,
        )
        if len(titles) != 4 or any("[ICON_" in title for title in titles):
            failures.append(f"{relative}: four Quarter pedia section headers must exist without icons")

    tailors_source = (root / "project/localization/CSC_TAILORS_TEXT.md").read_text(encoding="utf-8-sig")
    sales_prose = (
        "Bales of cloth move naturally through the Harbor",
        "The Commercial Hub brings staple provisions and finished cloth into the same busy exchange",
        "Vestments, hangings and ceremonial cloth",
        "Costumes, drapery and fashionable display",
        "An adjacent Bakers'' Quarter gains +1 [ICON_Gold] Gold",
        "An adjacent Tailors'' Quarter gains +1 [ICON_Gold] Gold",
        "INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)",
        "LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_COMMERCIAL_HUB_CHAPTER_CSCHAIN_PARA_1",
    )
    for exact in sales_prose:
        if exact not in tailors_source:
            failures.append(f"Tailors sales-district pedia prose/composition missing: {exact}")

    for resource, resource_class, display_name, group_label, mapping_file, source_file, generated_file, action_id, criteria in optional_bindings:
        mapping = (root / mapping_file).read_text(encoding="utf-8-sig")
        if resource not in mapping or resource_class not in mapping:
            failures.append(f"{mapping_file}: missing {resource} -> {resource_class} gameplay mapping")
        reverse_tag = f"LOC_PEDIA_RESOURCES_PAGE_{resource}_CHAPTER_CSCQUAR_PARA_1"
        quarter_entry = f"[ICON_{resource}] {display_name}"
        for relative in (source_file, generated_file):
            text = (root / relative).read_text(encoding="utf-8-sig")
            reciprocal_present = (
                f"{group_label}[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors' Quarter" in text
                or f"{group_label}[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter" in text
            )
            if reverse_tag not in text or quarter_entry not in text or not reciprocal_present:
                failures.append(f"{relative}: incomplete Quarter-side/reciprocal pedia pair for {resource}")
        action = actions.get(action_id)
        expected_file = generated_file.removeprefix("Civ Supply Chains/")
        if action is None:
            failures.append(f"action manifest missing {action_id}")
        else:
            if action.get("type") != "UpdateText" or action.get("files") != [expected_file]:
                failures.append(f"{action_id}: must be an UpdateText action for {expected_file}")
            if action.get("criteria", []) != criteria:
                failures.append(f"{action_id}: criteria must exactly match {criteria}")
        gameplay_action_id = Path(mapping_file).stem
        gameplay_action = actions.get(gameplay_action_id)
        expected_gameplay_file = mapping_file.removeprefix("Civ Supply Chains/")
        if gameplay_action is None:
            failures.append(f"action manifest missing {gameplay_action_id}")
        else:
            if (
                gameplay_action.get("type") != "UpdateDatabase"
                or gameplay_action.get("files") != [expected_gameplay_file]
            ):
                failures.append(
                    f"{gameplay_action_id}: must be an UpdateDatabase action for {expected_gameplay_file}"
                )
            if gameplay_action.get("criteria", []) != criteria:
                failures.append(
                    f"{gameplay_action_id}: gameplay criteria must exactly match text criteria {criteria}"
                )
        content_path = expected_file.replace("/", "\\")
        if f'Content Include="{content_path}"' not in project_text:
            failures.append(f".civ6proj Content missing {content_path}")

    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE LocalizedText (Language TEXT, Tag TEXT PRIMARY KEY, Text TEXT)")
        for relative in (
            "Civ Supply Chains/Text/CSC_BAKERS_TEXT.sql",
            "Civ Supply Chains/Text/CSC_TAILORS_TEXT.sql",
            "Civ Supply Chains/ModSupport/ModSupport_CH_TAILORS_TEXT.sql",
            "Civ Supply Chains/ModSupport/ModSupport_LAR_A_TAILORS_TEXT.sql",
            "Civ Supply Chains/ModSupport/ModSupport_R2_TEXT.sql",
            "Civ Supply Chains/ModSupport/ModSupport_R2_A_TAILORS_TEXT.sql",
            "Civ Supply Chains/ModSupport/ModSupport_SR_TAILORS_TEXT.sql",
        ):
            connection.executescript((root / relative).read_text(encoding="utf-8-sig"))
        flax = _scalar(
            connection,
            "SELECT Text FROM LocalizedText WHERE Tag='LOC_PEDIA_RESOURCES_PAGE_RESOURCE_CSC_FLAX_CHAPTER_CSCQUAR_PARA_1'",
        )
        expected_flax = (
            "Base Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_BAKERS] Bakers' Quarter"
            "[NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors' Quarter"
        )
        _expect(failures, flax, expected_flax, "Flax composed Base Materials pedia list")
        base_list = _scalar(
            connection,
            "SELECT Text FROM LocalizedText WHERE Tag='LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_PARA_1'",
        ) or ""
        spec_list = _scalar(
            connection,
            "SELECT Text FROM LocalizedText WHERE Tag='LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1'",
        ) or ""
        for resource, _, display_name, group_label, *_ in optional_bindings:
            material_list = base_list if group_label == "Base Materials:" else spec_list
            entry = f"[ICON_{resource}] {display_name}"
            if material_list.count(entry) != 1:
                failures.append(f"Tailors {group_label[:-1]} list must contain {entry} exactly once")
            reverse = _scalar(
                connection,
                f"SELECT Text FROM LocalizedText WHERE Tag='LOC_PEDIA_RESOURCES_PAGE_{resource}_CHAPTER_CSCQUAR_PARA_1'",
            ) or ""
            if reverse.count(group_label) != 1 or reverse.count("[ICON_TAILORS] Tailors' Quarter") != 1:
                failures.append(f"{resource} reciprocal pedia list is absent, duplicated, or mis-grouped")
            if f"{group_label}[NEWLINE][NEWLINE][ICON_BULLET]" not in reverse:
                failures.append(f"{resource} reciprocal pedia list must leave one open line after {group_label}")
    except (OSError, sqlite3.DatabaseError) as failure:
        failures.append(f"resource pedia localization composition failed: {failure}")
    finally:
        connection.close()
    return failures


def _validate_city_lights_contract(
    root: Path, gameplay_connection: sqlite3.Connection | None = None
) -> list[str]:
    failures: list[str] = []
    rural = (
        "DISTRICT_RURALCOMMUNITYA",
        "DISTRICT_COREX_FRONTIER_TOWN",
        "DISTRICT_RURALCOMMUNITYB",
        "DISTRICT_COREX_TROYU",
        "DISTRICT_COREX_TSIKHE",
        "DISTRICT_RURALCOMMUNITYC",
        "DISTRICT_COREX_GYOSON",
    )
    urban = (
        "DISTRICT_COREEXPANSIONA",
        "DISTRICT_COREX_XIAN",
        "DISTRICT_COREX_UPAPITHA",
        "DISTRICT_COREX_VENICE_01",
        "DISTRICT_COREEXPANSIONB",
        "DISTRICT_COREX_VENICE_02",
        "DISTRICT_COREX_FUERTE",
        "DISTRICT_COREEXPANSIONC",
        "DISTRICT_COREX_ELYSEE",
    )
    gameplay_path = root / "Civ Supply Chains/ModSupport/ModSupport_CL.sql"
    source_path = root / "project/localization/ModSupport_CL_TEXT.md"
    generated_path = root / "Civ Supply Chains/ModSupport/ModSupport_CL_TEXT.sql"
    gameplay = gameplay_path.read_text(encoding="utf-8-sig")
    source = source_path.read_text(encoding="utf-8-sig")
    generated = generated_path.read_text(encoding="utf-8-sig")

    for district in rural:
        for tag in ("CLASS_CSC_TAILORS_GOODS_PROVIDER", "CLASS_CSC_TAILORS_SALES_CULTURE"):
            if not re.search(rf"'{district}'\s*,\s*'{tag}'", gameplay):
                failures.append(f"City Lights gameplay missing {district} -> {tag}")
    for district in urban:
        for tag in ("CLASS_CSC_TAILORS_SALES", "CLASS_CSC_TAILORS_SALES_CULTURE"):
            if not re.search(rf"'{district}'\s*,\s*'{tag}'", gameplay):
                failures.append(f"City Lights gameplay missing {district} -> {tag}")

    processor = (
        root / "Civ Supply Chains/Lua_UI/Ruivo_Adjacencies/CSC_Ruivo_AdjacencyProcessor.sql"
    ).read_text(encoding="utf-8-sig")
    if not re.search(
        r"'CLASS_CSC_TAILORS_GOODS_PROVIDER'\s*,\s*'LOC_CLASS_CSC_GOODS_PROVIDER_NAME'\s*,\s*'CSC_Goods_Provider'",
        processor,
    ):
        failures.append(
            "Tailors goods-provider MAB class lacks the Bakers-pattern readable Ruivo_CAO tooltip registration"
        )

    reciprocal_description_lines = (
        "[NEWLINE][NEWLINE]Yield bonus from Quarters, and+1 [ICON_Production] Production in return.",
        "[NEWLINE][NEWLINE]Yield bonus from Quarters, and+1 [ICON_Gold] Gold in return.",
    )
    tailors_quarter_lines = (
        "+1 [ICON_Production] Production from each adjacent [ICON_CSC_GOODS] Rural Community, and +1 [ICON_Culture] Culture in return.",
        "+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] Commercial Hub, Holy Site, Theater Square and Urban Borough, and +1 [ICON_Culture] Culture in return.",
    )
    bakers_quarter_lines = (
        "+1 [ICON_Production] Production from each adjacent [ICON_CSC_GOODS] Rural Community, and +1 [ICON_Food] Food in return.",
        "+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.",
    )
    invalid_city_lights_description_keys = (
        "LOC_DISTRICT_COREEXPANSIONA_VENICE_DESCRIPTION",
        "LOC_DISTRICT_COREX_VENICE_02_DESCRIPTION",
    )
    for relative, text in ((source_path, source), (generated_path, generated)):
        for exact in reciprocal_description_lines + tailors_quarter_lines + bakers_quarter_lines:
            if exact not in text:
                failures.append(f"{relative}: missing exact City Lights reciprocal text {exact}")
        for exact in (
            "Rural Communities supply nearby Quarters with raw goods and a dependable workforce",
            "Urban Boroughs gather households, shops and passing customers into dense markets",
            "LOC_PEDIA_DISTRICTS_PAGE_' || DistrictType || '_CHAPTER_CSCHAIN_TITLE",
            "LOC_PEDIA_DISTRICTS_PAGE_' || DistrictType || '_CHAPTER_CSCHAIN_PARA_1",
        ):
            if exact not in text:
                failures.append(f"{relative}: incomplete integrated City Lights pedia content: {exact}")
        for invalid_key in invalid_city_lights_description_keys:
            if invalid_key in text:
                failures.append(f"{relative}: targets nonexistent City Lights description key {invalid_key}")

    manifest = json.loads(
        (root / "project/modbuddy/CivSupplyChains.actions.json").read_text(encoding="utf-8")
    )
    actions = {action["id"]: action for action in manifest["blocks"]["inGameActions"]}
    expected_actions = {
        "ModSupport_CL": ("UpdateDatabase", ["ModSupport/ModSupport_CL.sql"], ["ModSupport_CL"]),
        "ModSupport_CL_TEXT": ("UpdateText", ["ModSupport/ModSupport_CL_TEXT.sql"], ["ModSupport_CL"]),
    }
    for action_id, (action_type, files, criteria) in expected_actions.items():
        action = actions.get(action_id, {})
        if (
            action.get("type") != action_type
            or action.get("files") != files
            or action.get("criteria", []) != criteria
        ):
            failures.append(f"{action_id}: City Lights action type, file, or criteria drift")

    if gameplay_connection is not None:
        try:
            gameplay_connection.execute(
                "DELETE FROM ImprovementModifiers WHERE ImprovementType='IMP_CL_TRADING_POST' AND ModifierId='MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'"
            )
            gameplay_connection.executescript(gameplay)
            expected_tag_counts = {
                "CLASS_CSC_TAILORS_GOODS_PROVIDER": len(rural),
                "CLASS_CSC_TAILORS_SALES_CULTURE": len(rural) + len(urban),
                "CLASS_CSC_TAILORS_SALES": len(urban),
            }
            scoped_types = rural + urban
            placeholders = ",".join("?" for _ in scoped_types)
            for tag, expected_count in expected_tag_counts.items():
                actual_count = _scalar(
                    gameplay_connection,
                    f"SELECT COUNT(*) FROM TypeTags WHERE Tag=? AND Type IN ({placeholders})",
                    (tag, *scoped_types),
                )
                _expect(failures, actual_count, expected_count, f"City Lights {tag} mappings")
            _expect(
                failures,
                gameplay_connection.execute(
                    "SELECT Name, ArtdefOverlayEntry FROM Ruivo_CAO WHERE CustomAdjacentObject='CLASS_CSC_TAILORS_GOODS_PROVIDER'"
                ).fetchone(),
                ("LOC_CLASS_CSC_GOODS_PROVIDER_NAME", "CSC_Goods_Provider"),
                "Tailors Rural Community adjacency tooltip presentation",
            )
        except sqlite3.DatabaseError as failure:
            failures.append(f"City Lights gameplay integration failed: {failure}")

    connection = sqlite3.connect(":memory:")
    try:
        connection.execute("CREATE TABLE LocalizedText (Language TEXT, Tag TEXT PRIMARY KEY, Text TEXT)")
        for description_tag in (
            "LOC_DISTRICT_RURALCOMMUNITYA_DESCRIPTION",
            "LOC_DISTRICT_COREX_FRONTIER_TOWN_DESCRIPTION",
            "LOC_DISTRICT_RURALCOMMUNITYB_DESCRIPTION",
            "LOC_DISTRICT_COREX_TROYU_DESCRIPTION",
            "LOC_DISTRICT_COREX_TSIKHE_DESCRIPTION",
            "LOC_DISTRICT_RURALCOMMUNITYC_DESCRIPTION",
            "LOC_DISTRICT_COREX_GYOSON_DESCRIPTION",
            "LOC_DISTRICT_COREEXPANSIONA_DESCRIPTION",
            "LOC_DISTRICT_COREX_XIAN_DESCRIPTION",
            "LOC_DISTRICT_COREX_UPAPITHA_DESCRIPTION",
            "LOC_DISTRICT_COREEXPANSIONB_DESCRIPTION",
            "LOC_DISTRICT_COREX_FUERTE_DESCRIPTION",
            "LOC_DISTRICT_COREEXPANSIONC_DESCRIPTION",
            "LOC_DISTRICT_COREX_ELYSEE_DESCRIPTION",
        ):
            connection.execute(
                "INSERT INTO LocalizedText VALUES ('en_US', ?, 'City Lights base description.')",
                (description_tag,),
            )
        for core_text in (
            root / "Civ Supply Chains/Text/CSC_BAKERS_TEXT.sql",
            root / "Civ Supply Chains/Text/CSC_TAILORS_TEXT.sql",
        ):
            connection.executescript(core_text.read_text(encoding="utf-8-sig"))
        connection.executescript(generated)

        tailors_description = _scalar(
            connection,
            "SELECT Text FROM LocalizedText WHERE Tag='LOC_DISTRICT_CSC_TAILORS_QUARTER_DESCRIPTION'",
        ) or ""
        for exact in tailors_quarter_lines:
            _expect(
                failures,
                tailors_description.count(exact),
                1,
                f"Tailors City Lights district-description line {exact}",
            )
        ordered_tailors_bonuses = (
            "Production from every 2 adjacent river segments.",
            "Base or [ICON_CSC_SPEC] Specialty Materials resource from this supply chain.",
            "[ICON_CSC_GOODS] Rural Community, and +1 [ICON_Culture] Culture in return.",
            "[ICON_CSC_SALES] Harbor, and +1 [ICON_Production] Production in return.",
            "[ICON_CSC_SALES] Commercial Hub, Holy Site, Theater Square and Urban Borough, and +1 [ICON_Culture] Culture in return.",
        )
        ordered_positions = [tailors_description.find(text) for text in ordered_tailors_bonuses]
        if any(position < 0 for position in ordered_positions) or ordered_positions != sorted(ordered_positions):
            failures.append(
                "Tailors City Lights district description must follow canonical UI order: river, materials, Rural Community, Stage 2 sales, combined Stage 3/4/Urban sales"
            )

        bakers_description = _scalar(
            connection,
            "SELECT Text FROM LocalizedText WHERE Tag='LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION'",
        ) or ""
        for exact in bakers_quarter_lines:
            _expect(
                failures,
                bakers_description.count(exact),
                1,
                f"Bakers City Lights district-description line {exact}",
            )
        ordered_bakers_bonuses = (
            "Production from every 2 adjacent river segments once the Water Mill is built",
            "Base or [ICON_CSC_SPEC] Specialty Materials resource from this supply chain.",
            "[ICON_CSC_GOODS] Rural Community, and +1 [ICON_Food] Food in return.",
            "[ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.",
            "[ICON_CSC_SALES] Entertainment Complex and Water Park, and +1 [ICON_Culture] Culture in return.",
        )
        ordered_positions = [bakers_description.find(text) for text in ordered_bakers_bonuses]
        if any(position < 0 for position in ordered_positions) or ordered_positions != sorted(ordered_positions):
            failures.append(
                "Bakers City Lights district description must follow canonical UI order: terrain/river, materials, Rural Community, combined Stage 2/Urban sales, Stage 3/4 sales"
            )

        quarter_pedia_tags = (
            "LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER",
            "LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER",
        )
        for quarter_tag in quarter_pedia_tags:
            goods = _scalar(
                connection,
                "SELECT Text FROM LocalizedText WHERE Tag=?",
                (f"{quarter_tag}_CHAPTER_CSCGOODS_PARA_1",),
            ) or ""
            sales = _scalar(
                connection,
                "SELECT Text FROM LocalizedText WHERE Tag=?",
                (f"{quarter_tag}_CHAPTER_CSCSALES_PARA_1",),
            ) or ""
            for district in rural:
                _expect(
                    failures,
                    goods.count(f"[ICON_{district}]"),
                    1,
                    f"{quarter_tag} Goods Providers entry for {district}",
                )
            for district in urban:
                _expect(
                    failures,
                    sales.count(f"[ICON_{district}]"),
                    1,
                    f"{quarter_tag} Sales Districts entry for {district}",
                )

        for district in rural + urban:
            title = _scalar(
                connection,
                "SELECT Text FROM LocalizedText WHERE Tag=?",
                (f"LOC_PEDIA_DISTRICTS_PAGE_{district}_CHAPTER_CSCHAIN_TITLE",),
            )
            overview = _scalar(
                connection,
                "SELECT Text FROM LocalizedText WHERE Tag=?",
                (f"LOC_PEDIA_DISTRICTS_PAGE_{district}_CHAPTER_CSCHAIN_PARA_1",),
            ) or ""
            _expect(failures, title, "Supply Chains", f"{district} City Lights pedia title")
            if overview.count("[NEWLINE][NEWLINE]") != 1:
                failures.append(f"{district}: City Lights pedia must contain one flavour/mechanics paragraph break")
            if "Bakers' Quarter" in overview or "Tailors' Quarter" in overview:
                failures.append(f"{district}: integrated City Lights pedia must not hard-code the current Quarter roster")
            if district in rural:
                if "goods and a dependable workforce" not in overview or "+1 [ICON_Production] Production" not in overview:
                    failures.append(f"{district}: Rural Community pedia must explain goods/workforce provision and its Production exchange")
            elif "urban" not in overview.lower() or "+1 [ICON_Gold] Gold" not in overview:
                failures.append(f"{district}: Urban Borough pedia must explain its urban sales role and Gold exchange")
    except sqlite3.DatabaseError as failure:
        failures.append(f"City Lights localization composition failed: {failure}")
    finally:
        connection.close()
    return failures


def _foundation_assertions(root: Path, connection: sqlite3.Connection) -> list[str]:
    failures: list[str] = _validate_resource_pedia_contract(root)
    failures.extend(_validate_city_lights_contract(root, connection))
    expected_types = {
        "DISTRICT_CSC_TAILORS_QUARTER",
        "BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP",
        "BUILDING_CSC_TAILORS_TAILOR",
        "BUILDING_CSC_TAILORS_FASHION_HOUSE",
        "BUILDING_CSC_TAILORS_STAGE_2_SERVICE",
        "BUILDING_CSC_TAILORS_STAGE_3_SERVICE",
        "BUILDING_CSC_TAILORS_STAGE_4_SERVICE",
    }
    actual_types = {
        row[0]
        for row in connection.execute(
            "SELECT Type FROM Types WHERE Type LIKE 'DISTRICT_CSC_TAILORS_%' OR Type LIKE 'BUILDING_CSC_TAILORS_%'"
        )
    }
    _expect(failures, actual_types, expected_types, "Tailors object Types")
    _expect(
        failures,
        connection.execute(
            "SELECT ResourceType, Tag FROM (SELECT Type AS ResourceType, Tag FROM TypeTags) WHERE Tag IN ('CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC') ORDER BY ResourceType"
        ).fetchall(),
        [
            ("RESOURCE_COTTON", "CLASS_CSC_TAILORS_BASE"),
            ("RESOURCE_CSC_FLAX", "CLASS_CSC_TAILORS_BASE"),
            ("RESOURCE_DYES", "CLASS_CSC_TAILORS_SPEC"),
            ("RESOURCE_SHEEP", "CLASS_CSC_TAILORS_BASE"),
            ("RESOURCE_SILK", "CLASS_CSC_TAILORS_SPEC"),
            ("RESOURCE_SILVER", "CLASS_CSC_TAILORS_SPEC"),
        ],
        "core material mappings",
    )
    district = connection.execute(
        "SELECT PrereqCivic, Cost, Maintenance FROM Districts WHERE DistrictType='DISTRICT_CSC_TAILORS_QUARTER'"
    ).fetchone()
    _expect(failures, district, ("CIVIC_CRAFTSMANSHIP", 60, 1), "district definition")
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM CSC_QuarterMaterialAdjacencyConfig WHERE QuarterKey='TAILORS' AND YieldType='YIELD_PRODUCTION' AND YieldChange=1"),
        2,
        "material adjacency configuration",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM Ruivo_New_Adjacency WHERE DistrictType='DISTRICT_CSC_TAILORS_QUARTER' AND ID='CSC_CITY_ALL_SALES_GOLD_TO_TAILORS' AND YieldType='YIELD_GOLD' AND YieldChange=1"),
        1,
        "Quarter customer Gold adjacency",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM Ruivo_New_Adjacency WHERE ID='CSC_TAILORS_PRODUCTION_FROM_RIVER_EDGES' AND YieldChange=0.5 AND AdjacencyType='FROM_RIVER_CROSSING'"),
        1,
        "river-edge adjacency",
    )
    source = (root / "project/localization/CSC_TAILORS_TEXT.md").read_text(encoding="utf-8")
    for exact in (
        "A district in your city specializing in tailoring.",
        "+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] Harbor, and +1 [ICON_Production] Production in return.",
        "+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] Commercial Hub, Holy Site and Theater Square, and +1 [ICON_Culture] Culture in return.",
        "Fibres processed in a workshop become tailored consumer goods, then fashion and performance goods sold into the institutions where a city presents itself to its people and the wider world.",
    ):
        if exact not in source:
            failures.append(f"foundation localization missing exact pattern: {exact}")
    history_match = re.search(
        r"## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_HISTORY_PARA_1\n(.*?)(?=\n## LOC_PEDIA_BUILDINGS_PAGE_|\Z)",
        source,
        flags=re.DOTALL,
    )
    if history_match is None:
        failures.append("Tailors Quarter Historical Context is missing")
    elif re.search(r"\barc\b", history_match.group(1), flags=re.IGNORECASE):
        failures.append("Tailors Quarter Historical Context must imply its progression without calling it an arc")
    return failures


def _stage2_assertions(root: Path, connection: sqlite3.Connection) -> list[str]:
    failures: list[str] = []
    building = connection.execute(
        "SELECT PrereqTech, Cost, Maintenance, PrereqDistrict FROM Buildings WHERE BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'"
    ).fetchone()
    _expect(failures, building, ("TECH_CONSTRUCTION", 80, 2, "DISTRICT_CSC_TAILORS_QUARTER"), "Textile Workshop definition")
    service = connection.execute(
        "SELECT Cost, MustPurchase, CitizenSlots, PrereqDistrict FROM Buildings WHERE BuildingType='BUILDING_CSC_TAILORS_STAGE_2_SERVICE'"
    ).fetchone()
    _expect(failures, service, (0, 1, 1, "DISTRICT_HARBOR"), "Dockmaster hidden building")
    _expect(
        failures,
        _scalar(connection, "SELECT Pillage FROM Buildings_XP2 WHERE BuildingType='BUILDING_CSC_TAILORS_STAGE_2_SERVICE'"),
        0,
        "Dockmaster pillage flag",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_%' AND ModifierType='MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION'"),
        12,
        "Dockmaster mechanical modifier family",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM BuildingModifiers WHERE BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP' AND ModifierId LIKE 'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_%'"),
        12,
        "Dockmaster attach family",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(DISTINCT OwnerRequirementSetId || '|' || SubjectRequirementSetId) FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_%'"),
        1,
        "Dockmaster gate equivalence",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM CSC_AbilityAttachModifiers WHERE ModifierId LIKE 'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_%'"),
        1,
        "Dockmaster MCUIS anchor",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT AbilityEffectModifierId, AbilityArgumentAmount, AbilityDesc, AbilityNewDesc, AbilityIncreasedDesc, AbilityDecreasedDesc, AbilityRemovedDesc FROM CSC_AbilityAttachModifiers WHERE ModifierId='MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_ANCIENT_NAVAL_MELEE'"
        ).fetchone(),
        (
            "MOD_CSC_TAILORS_DOCKMASTER_EFFECT_ANCIENT_NAVAL_MELEE",
            20,
            "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION",
            "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_NEW",
            "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_INCREASED",
            "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_DECREASED",
            "LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_REMOVED",
        ),
        "Dockmaster resolved MCUIS row",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM ModifierStrings WHERE ModifierId LIKE 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_%'"),
        1,
        "Dockmaster aggregate preview string",
    )
    for modifier, amount in (
        ("MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP", "1"),
        ("MOD_CSC_TAILORS_PROD_TO_ADJ_BASE", "1"),
        ("MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE", "1"),
        ("MOD_CSC_TAILORS_BASE_INDUSTRY_CULTURE_TO_WORKSHOP", "2"),
        ("MOD_CSC_TAILORS_BASE_CORPORATION_CULTURE_TO_WORKSHOP", "3"),
        ("MOD_CSC_TAILORS_PROD_TO_ADJ_IND", "2"),
        ("MOD_CSC_TAILORS_PROD_TO_ADJ_CORP", "3"),
        ("MOD_CSC_TAILORS_GOLD_TO_ADJ_IND", "2"),
        ("MOD_CSC_TAILORS_GOLD_TO_ADJ_CORP", "3"),
    ):
        _expect(
            failures,
            str(_scalar(connection, "SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name='Amount'", (modifier,))),
            amount,
            f"{modifier} amount",
        )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM BuildingModifiers BM JOIN BuildingReplaces BR ON BR.CivUniqueBuildingType=BM.BuildingType WHERE BR.ReplacesBuildingType='BUILDING_LIGHTHOUSE' AND BM.ModifierId IN ('MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD','MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD')"),
        2 * _scalar(connection, "SELECT COUNT(*) FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_LIGHTHOUSE'"),
        "direct Lighthouse replacement BuildingModifiers",
    )
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM Buildings WHERE BuildingType='BUILDING_CSC_TAILORS_FASHION_HOUSE'"),
        0,
        "unapproved Stage 4 building rows",
    )
    source = (root / "project/localization/CSC_TAILORS_TEXT.md").read_text(encoding="utf-8")
    monopolies_source = (root / "project/localization/CSC_TAILORS_MC_MODE_TEXT.md").read_text(encoding="utf-8")
    for exact in (
        "+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_BASE] Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.",
        "At Naval Tradition, a supplied Textile Workshop establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME} in an adjacent Harbor with a Lighthouse.",
        "+1 [ICON_Production] Production and +1 [ICON_Gold] Gold from each adjacent Lighthouse, and +1 [ICON_Production] Production in return.",
        "+20% [ICON_Production] Production toward Renaissance Era or earlier naval units and +1 [ICON_GreatAdmiral] Great Admiral point from each adjacent supplied Textile Workshop.",
        "The established service and its [ICON_Citizen] Citizen slot remain",
        "## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_TITLE\nSupply Chains",
        "## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_HISTORY_TITLE\nHistorical Context",
        "The Textile Workshop draws on improved Tailors' [ICON_CSC_BASE] Base Materials nearby, turns their fibres into cloth and sail canvas, and sends that steady flow to the adjacent Lighthouse.",
        "This gives a Citizen the opportunity to take up employment as a Dockmaster in the Harbor, coordinating crews, stores and waterfront traffic so the city can fit out early naval vessels more efficiently and cultivate experienced Great Admirals.",
        "Dockmasters allocated berths, coordinated loading crews, supervised stores and repairs, and kept vessels moving through limited waterfront space.",
    ):
        if exact not in source:
            failures.append(f"Stage 2 localization missing exact pattern: {exact}")
    dockmaster_tags = re.findall(
        r"^## (LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_[A-Z0-9_]+)$",
        source,
        flags=re.MULTILINE,
    )
    _expect(
        failures,
        dockmaster_tags,
        [
            "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_TITLE",
            "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_PARA_1",
            "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_HISTORY_TITLE",
            "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_HISTORY_PARA_1",
        ],
        "Dockmaster Civilopedia chapter scope and order",
    )
    dockmaster_supply_match = re.search(
        r"## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_PARA_1\n(.*?)(?=\n## |\Z)",
        source,
        flags=re.DOTALL,
    )
    if dockmaster_supply_match is None or dockmaster_supply_match.group(1).count("\n\n") != 1:
        failures.append("Dockmaster Supply Chains pedia must have exactly one upstream-to-employment paragraph break")
    forbidden = ("Industry", "Corporation")
    description_match = re.search(
        r"## LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_DESCRIPTION\n(.*?)(?=\n## |\Z)",
        source,
        flags=re.DOTALL,
    )
    if description_match is None:
        failures.append("Textile Workshop description is missing")
    else:
        description = description_match.group(1)
        if any(term in description for term in forbidden):
            failures.append("Textile Workshop M&C wording must not appear in always-loaded Tailors text")
        base_position = description.find("Base Materials improvement")
        lighthouse_position = description.find("from each adjacent Lighthouse")
        local_position = description.find("from the local Tailor and Fashion House")
        if min(base_position, lighthouse_position, local_position) < 0 or not (
            base_position < lighthouse_position < local_position
        ):
            failures.append(
                "Textile Workshop description must order Base input, Lighthouse end customer, then downstream local Tailor/Fashion House"
            )
    if not all(term in monopolies_source for term in forbidden):
        failures.append("Monopolies-gated Textile Workshop text must contain Industry and Corporation wording")
    if "Production to the Lighthouse city" in source:
        failures.append("Stage 2 customer text must not use a redundant Lighthouse-city suffix")
    civic_match = re.search(
        r"## LOC_CSC_TAILORS_STAGE_2_CIVIC\n(.*?)(?=\n## |\Z)",
        source,
        flags=re.DOTALL,
    )
    if civic_match is None or "text-prefix:" in civic_match.group(1):
        failures.append("Naval Tradition has no base description, so its Tailors append must have no text-prefix")
    civic_append_match = re.search(
        r"## LOC_CSC_TAILORS_STAGE_2_CIVIC_APPEND\n(.*?)(?=\n## |\Z)",
        source,
        flags=re.DOTALL,
    )
    if civic_append_match is None or "text-prefix: [NEWLINE][NEWLINE]" not in civic_append_match.group(1):
        failures.append("non-empty Civic descriptions must select a two-newline-prefixed Tailors append key")
    core_source = (root / "Civ Supply Chains/Data/CSC_Q_TAILORS.sql").read_text(encoding="utf-8-sig")
    for exact in (
        "WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_2_CIVIC'",
        "ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_2_CIVIC_APPEND}'",
    ):
        if exact not in core_source:
            failures.append(f"Naval Tradition conditional description composition missing: {exact}")
    failures.extend(_validate_dockmaster_mcuis_signs(source))
    notification_text_source = (
        root / "project/localization/CSC_UI_Text.md"
    ).read_text(encoding="utf-8-sig")
    if "closing the local {2_Ability}. " not in notification_text_source:
        failures.append(
            "shared removed-service notification summary must own the single terminal period after {2_Ability}"
        )
    notification_panel = (
        root / "Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/NotificationPanel_CSC_UI.lua"
    ).read_text(encoding="utf-8")
    for notification in ("NEW", "INCREASED", "DECREASED", "REMOVED"):
        if f'NOTIFICATION_CSC_TAILORS_EFFECT_{notification}' not in notification_panel:
            failures.append(f"Tailors notification handler missing {notification}")
    for relative in (
        "Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/CSC_UI_Notifications_Icons.sql",
        "Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS/CSC_UI_Notifications_Icons_XP1.sql",
    ):
        icon_source = (root / relative).read_text(encoding="utf-8")
        for notification in ("NEW", "INCREASED", "DECREASED", "REMOVED"):
            if f"ICON_NOTIFICATION_CSC_TAILORS_EFFECT_{notification}" not in icon_source:
                failures.append(f"{relative}: Tailors notification icon missing {notification}")
    failures.extend(
        _validate_tailors_icon_bindings(
            root,
            (
                ("ICON_DISTRICT_CSC_TAILORS_QUARTER", 0),
                ("ICON_DISTRICT_CSC_TAILORS_QUARTER_FOW", 1),
                ("ICON_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP", 4),
                ("ICON_BUILDING_CSC_TAILORS_STAGE_2_SERVICE", 8),
            ),
        )
    )
    failures.extend(
        _validate_tailors_building_chain(
            root,
            {"Buildings (Level 1)": "BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP"},
        )
    )
    return failures


def _stage3_assertions(root: Path, connection: sqlite3.Connection) -> list[str]:
    failures: list[str] = []
    _expect(
        failures,
        connection.execute(
            "SELECT PrereqCivic, Cost, PrereqDistrict, Maintenance, CitizenSlots, Entertainment "
            "FROM Buildings WHERE BuildingType='BUILDING_CSC_TAILORS_TAILOR'"
        ).fetchone(),
        ("CIVIC_GUILDS", 160, "DISTRICT_CSC_TAILORS_QUARTER", 2, 1, 1),
        "Tailor definition",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT PrereqBuilding FROM BuildingPrereqs WHERE Building='BUILDING_CSC_TAILORS_TAILOR'"
        ).fetchall(),
        [("BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP",)],
        "Tailor prerequisite",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT YieldType, YieldChange FROM Building_CitizenYieldChanges "
            "WHERE BuildingType='BUILDING_CSC_TAILORS_TAILOR' ORDER BY YieldType"
        ).fetchall(),
        [("YIELD_CULTURE", 2), ("YIELD_GOLD", 1)],
        "Tailor specialist yields",
    )
    for modifier, expected in (
        ("MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR", ("BUILDING_CSC_TAILORS_TAILOR", "YIELD_CULTURE", "1")),
        ("MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP", ("BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP", "YIELD_PRODUCTION", "1")),
    ):
        row = connection.execute(
            "SELECT MAX(CASE WHEN Name='BuildingType' THEN Value END), "
            "MAX(CASE WHEN Name='YieldType' THEN Value END), MAX(CASE WHEN Name='Amount' THEN Value END) "
            "FROM ModifierArguments WHERE ModifierId=?",
            (modifier,),
        ).fetchone()
        _expect(failures, row, expected, f"{modifier} local exchange")
    _expect(
        failures,
        connection.execute(
            "SELECT ModifierId, ModifierType FROM Modifiers WHERE ModifierId IN "
            "('MOD_CSC_TAILORS_TAILOR_ATTACH_MARKET','MOD_CSC_TAILORS_TAILOR_ATTACH_TEMPLE',"
            "'MOD_CSC_TAILORS_CUSTOMER_CULTURE') ORDER BY ModifierId"
        ).fetchall(),
        [
            ("MOD_CSC_TAILORS_CUSTOMER_CULTURE", "MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION"),
            ("MOD_CSC_TAILORS_TAILOR_ATTACH_MARKET", "MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER"),
            ("MOD_CSC_TAILORS_TAILOR_ATTACH_TEMPLE", "MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER"),
        ],
        "Tailor customer modifier graph",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT Name, Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_TAILORS_CUSTOMER_CULTURE' ORDER BY Name"
        ).fetchall(),
        [("Amount", "0.105"), ("YieldType", "YIELD_CULTURE")],
        "Tailor customer Culture amount",
    )
    for requirement_set, expected_requirements in (
        ("REQSET_CSC_TAILORS_ADJ_MARKET", {"REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER", "REQ_CSC_TAILORS_DISTRICT_IS_COMMERCIAL_HUB", "REQ_CSC_TAILORS_CITY_HAS_MARKET"}),
        ("REQSET_CSC_TAILORS_ADJ_TEMPLE", {"REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER", "REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE", "REQ_CSC_TAILORS_CITY_HAS_TEMPLE"}),
        ("REQSET_CSC_TAILORS_STAGE_3_ART", {"REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER", "REQ_CSC_TAILORS_DISTRICT_IS_QUARTER", "REQ_CSC_TAILORS_CITY_HAS_TAILOR"}),
        ("REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ", {"REQ_CSC_TAILORS_PLAYER_HAS_DIVINE_RIGHT", "REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE"}),
    ):
        actual = {row[0] for row in connection.execute(
            "SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?", (requirement_set,)
        )}
        _expect(failures, actual, expected_requirements, requirement_set)
    _expect(
        failures,
        _scalar(connection, "SELECT COUNT(*) FROM RequirementSetRequirements RSR JOIN Requirements R ON R.RequirementId=RSR.RequirementId WHERE RSR.RequirementSetId='REQSET_CSC_TAILORS_STAGE_3_ART' AND R.RequirementType='REQUIREMENT_PLAYER_HAS_CIVIC'"),
        0,
        "Tailor art civic-gate exclusion",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT PrereqDistrict, Cost, CitizenSlots, MustPurchase FROM Buildings WHERE BuildingType='BUILDING_CSC_TAILORS_STAGE_3_SERVICE'"
        ).fetchone(),
        ("DISTRICT_HOLY_SITE", 0, 1, 1),
        "Sacristan hidden building",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT AbilityEffectModifierId, AbilityArgumentAmount, AbilityDesc, AbilityNewDesc, AbilityIncreasedDesc, AbilityDecreasedDesc, AbilityRemovedDesc "
            "FROM CSC_AbilityAttachModifiers WHERE ModifierId='MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE'"
        ).fetchone(),
        (
            "MOD_CSC_TAILORS_SACRISTAN_FAITH", 10,
            "LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION",
            "LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_NEW",
            "LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_INCREASED",
            "LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_DECREASED",
            "LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_REMOVED",
        ),
        "Sacristan MCUIS presentation anchor",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT Name, Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_TAILORS_SACRISTAN_FAITH' ORDER BY Name"
        ).fetchall(),
        [("Amount", "10"), ("YieldType", "YIELD_FAITH")],
        "Sacristan Faith effect",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT Name, Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_TAILORS_SACRISTAN_GPP' ORDER BY Name"
        ).fetchall(),
        [("Amount", "1"), ("GreatPersonClassType", "GREAT_PERSON_CLASS_PROPHET")],
        "Sacristan Prophet point",
    )
    for modifier, yield_type in (
        ("MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE", "YIELD_CULTURE"),
        ("MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION", "YIELD_PRODUCTION"),
    ):
        if _scalar(connection, "SELECT COUNT(*) FROM Modifiers WHERE ModifierId=?", (modifier,)) != 1:
            failures.append(f"Stage 3 trade modifier missing: {modifier}")
        if yield_type not in {row[0] for row in connection.execute("SELECT Value FROM ModifierArguments WHERE ModifierId=? AND Name='YieldType'", (modifier,))}:
            failures.append(f"Stage 3 trade yield missing: {modifier} -> {yield_type}")
    if _scalar(connection, "SELECT COUNT(*) FROM Modifiers WHERE ModifierId='MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY'") != 1:
        failures.append("Stage 3 trade origin Amenity modifier missing")
    gold_connection = connection
    for token in ("MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_", "MOD_CSC_TAILORS_EXPORT_TAILOR_GOLD"):
        if _scalar(gold_connection, "SELECT COUNT(*) FROM Modifiers WHERE ModifierId LIKE ?", (token + "%",)) < 1:
            failures.append(f"Tailors Gold companion modifier family missing: {token}")
    customer_lua = (root / "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua").read_text(encoding="utf-8")
    for token in ("DISTRICT_TAILORS_QUARTER", "BUILDING_MARKET_FAMILY", "BUILDING_TEMPLE_FAMILY", "PROP_TAILORS_CUSTOMER_RETURN_AMOUNT", "TailorsCustomersSeen"):
        if token not in customer_lua:
            failures.append(f"Tailors customer-population Lua contract missing {token}")
    if "while changed do" in customer_lua:
        failures.append("customer-population Lua must use direct one-level replacement expansion")
    route_ui = (root / "Civ Supply Chains/Lua_UI/TradeRoutes/CSC_TradeRouteInteractions.lua").read_text(encoding="utf-8")
    route_gameplay = (root / "Civ Supply Chains/Lua_UI/TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua").read_text(encoding="utf-8")
    for token in ("CSC_GetTailorsTradeRouteState", "CSC_TAILORS_TAILOR_SUPPLIED", "CSC_TAILORS_IMPORT_TAILOR_ROUTE", "CSC_TAILORS_EXPORT_TAILOR_ROUTE"):
        if token not in route_ui:
            failures.append(f"Tailors route UI bridge missing {token}")
    for token in ("CSC_TAILORS_IMPORT_TAILOR_ROUTE", "CSC_TAILORS_EXPORT_TAILOR_ROUTE", "ExportTailorRouteBit16"):
        if token not in route_gameplay:
            failures.append(f"Tailors route gameplay bridge missing {token}")
    preview_lua = (root / "Civ Supply Chains/Lua_UI/TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua").read_text(encoding="utf-8")
    unit_panel_lua = (root / "Civ Supply Chains/Lua_UI/TradeRoutes/UnitPanel.lua").read_text(encoding="utf-8")
    for token in ("CSC_BTS_GetTailorsTradeRouteState", "PROP_TAILOR_SUPPLIED", "CULTURE_INDEX"):
        if token not in preview_lua:
            failures.append(f"Tailors BTS route preview missing {token}")
    for token in ("CSC_UnitPanel_GetTailorsTradeRouteCount", "CSC_PROP_TAILOR_SUPPLIED", 'GameInfo.Yields["YIELD_CULTURE"]'):
        if token not in unit_panel_lua:
            failures.append(f"Tailors UnitPanel route display missing {token}")
    source = (root / "project/localization/CSC_TAILORS_TEXT.md").read_text(encoding="utf-8")
    description = re.search(r"## LOC_BUILDING_CSC_TAILORS_TAILOR_DESCRIPTION\n(.*?)(?=\n## |\Z)", source, flags=re.DOTALL)
    if description is None:
        failures.append("Tailor description is missing")
    else:
        authored = description.group(1)
        forbidden = (
            "[ICON_Citizen] Citizen slot",
            "[ICON_Citizen] Citizens in the Quarter",
            "[ICON_Amenities] Amenity to the city",
        )
        for token in forbidden:
            if token in authored:
                failures.append(
                    "Tailor description repeats engine-rendered building stats: " + token
                )
        ordered = ("local Textile Workshop", "each adjacent Temple or Market", "trade routes to the city", "At Divine Right")
        positions = [authored.find(token) for token in ordered]
        if any(position < 0 for position in positions) or positions != sorted(positions):
            failures.append("Tailor description does not contain every authored Stage 3 relationship in contract order")
    tailor_tags = re.findall(r"^## (LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_[A-Z0-9_]+)$", source, flags=re.MULTILINE)
    _expect(failures, tailor_tags, [
        "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_CSCHAIN_TITLE",
        "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_CSCHAIN_PARA_1",
        "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_HISTORY_TITLE",
        "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_HISTORY_PARA_1",
        "LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_HISTORY_PARA_2",
    ], "Tailor Civilopedia chapter scope and order")
    failures.extend(
        _validate_tailors_icon_bindings(
            root,
            (
                ("ICON_BUILDING_CSC_TAILORS_TAILOR", 5),
                ("ICON_BUILDING_CSC_TAILORS_STAGE_3_SERVICE", 9),
            ),
        )
    )
    failures.extend(
        _validate_tailors_building_chain(
            root,
            {
                "Buildings (Level 1)": "BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP",
                "Buildings (Level 2)": "BUILDING_CSC_TAILORS_TAILOR",
            },
            empty_levels=("Buildings (Level 3)",),
        )
    )
    art_lua = (root / "Civ Supply Chains/Lua_UI/ArtProperties/CSC_ArtProperties.lua").read_text(encoding="utf-8")
    if 'Source = "CSC_TAILORS_STAGE_3_CUSTOMERS"' not in art_lua or 'Art = "CSC_TAILORS_STAGE_3_CUSTOMERS_ART"' not in art_lua:
        failures.append("Tailor Stage 3 art Lua mirror mapping is missing")
    for relative, tokens in (
        ("Civ Supply Chains/ArtDefs/CSC_Buildings.artdef", ("BUILDING_CSC_TAILORS_TAILOR", "CSC_TAILORS_Tailor")),
        ("Civ Supply Chains/ArtDefs/CSC_Landmarks.artdef", ("CSC_TAILORS_Tailor_2", "[CITYPROP:CSC_TAILORS_STAGE_3_CUSTOMERS_ACTIVE]")),
        ("Civ Supply Chains/ArtDefs/CSC_StrategicView.artdef", ("CSC_TAILORS_Tailor", "CSC_TAILORS_Tailor_Pillaged", "CSC_TAILORS_Tailor_UnderConstruction")),
        ("Civ Supply Chains/ArtDefs/CSC_GamePropertyRanges.artdef", ("CSC_TAILORS_STAGE_3_CUSTOMERS_ART", "CSC_TAILORS_STAGE_3_CUSTOMERS_ACTIVE")),
        ("Civ Supply Chains/XLPs/CSC_Tilebases.xlp", ("CSC_TAILORS_Tailor", "CSC_TAILORS_Tailor_2")),
    ):
        text = (root / relative).read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                failures.append(f"{relative}: Stage 3 art binding missing {token}")
    return failures


def _art_integration_assertions(root: Path, connection: sqlite3.Connection) -> list[str]:
    failures: list[str] = []
    source_property = "CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION"
    art_property = f"{source_property}_ART"
    interval_property = f"{source_property}_ACTIVE"
    naming_match = re.fullmatch(
        r"CSC_TAILORS_STAGE_(?P<stage>[1-4])_EFFECT_(?P<effect>[A-Z0-9_]+)",
        source_property,
    )
    if naming_match is None or naming_match.group("effect") != "PRODUCTION":
        failures.append(
            "Tailors Stage 2 art property must use the reusable "
            "CSC_<QUARTER>_STAGE_<NUMBER>_EFFECT_<EFFECT_CONTENT> naming pattern"
        )
    _expect(
        failures,
        connection.execute(
            "SELECT ModifierType, OwnerRequirementSetId, SubjectRequirementSetId FROM Modifiers WHERE ModifierId='MOD_CSC_TAILORS_STAGE_2_ART_ATTACH_QUARTER'"
        ).fetchone(),
        (
            "MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER",
            None,
            "REQSET_CSC_TAILORS_STAGE_2_ART",
        ),
        "Tailors Stage 2 art receiver modifier",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT ModifierType FROM Modifiers WHERE ModifierId='MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY'"
        ).fetchone(),
        ("MODIFIER_SINGLE_CITY_ADJUST_PROPERTY",),
        "Tailors Stage 2 art source modifier",
    )
    _expect(
        failures,
        connection.execute(
            "SELECT Name, Value FROM ModifierArguments WHERE ModifierId='MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY' ORDER BY Name"
        ).fetchall(),
        [("Amount", "1"), ("Key", source_property)],
        "Tailors Stage 2 art source property arguments",
    )
    _expect(
        failures,
        {
            row[0]
            for row in connection.execute(
                "SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId='REQSET_CSC_TAILORS_STAGE_2_ART'"
            )
        },
        {
            "REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE",
            "REQ_CSC_TAILORS_DISTRICT_IS_QUARTER",
            "REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER",
            "REQ_CSC_TAILORS_CITY_HAS_TEXTILE_WORKSHOP",
        },
        "Tailors Stage 2 art physical-state requirements",
    )
    _expect(
        failures,
        _scalar(
            connection,
            "SELECT COUNT(*) FROM RequirementSetRequirements RSR JOIN Requirements R ON R.RequirementId=RSR.RequirementId WHERE RSR.RequirementSetId='REQSET_CSC_TAILORS_STAGE_2_ART' AND R.RequirementType='REQUIREMENT_PLAYER_HAS_CIVIC'",
        ),
        0,
        "Tailors Stage 2 art civic-gate exclusion",
    )
    _expect(
        failures,
        _scalar(
            connection,
            "SELECT COUNT(*) FROM BuildingModifiers BM JOIN BuildingReplaces BR ON BR.CivUniqueBuildingType=BM.BuildingType WHERE BR.ReplacesBuildingType='BUILDING_LIGHTHOUSE' AND BM.ModifierId='MOD_CSC_TAILORS_STAGE_2_ART_ATTACH_QUARTER'",
        ),
        _scalar(
            connection,
            "SELECT COUNT(*) FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_LIGHTHOUSE'",
        ),
        "Tailors Stage 2 art direct Lighthouse replacement bridge",
    )
    art_lua = (
        root / "Civ Supply Chains/Lua_UI/ArtProperties/CSC_ArtProperties.lua"
    ).read_text(encoding="utf-8")
    if (
        f'Source = "{source_property}"'
        not in art_lua
        or f'Art = "{art_property}"' not in art_lua
    ):
        failures.append("Tailors Stage 2 art Lua mirror mapping is missing")
    property_ranges = (
        root / "Civ Supply Chains/ArtDefs/CSC_GamePropertyRanges.artdef"
    ).read_text(encoding="utf-8")
    if not re.search(
        re.escape(art_property) + r'[\s\S]*?' + re.escape(interval_property),
        property_ranges,
    ):
        failures.append("Tailors Stage 2 GamePropertyRanges art/interval bridge is missing")
    landmarks = (root / "Civ Supply Chains/ArtDefs/CSC_Landmarks.artdef").read_text(
        encoding="utf-8"
    )
    if not re.search(
        r'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP[\s\S]*?'
        r'CSC_TAILORS_Textile_Workshop_2[\s\S]*?'
        + re.escape(f"[CITYPROP:{interval_property}]"),
        landmarks,
    ):
        failures.append("Tailors Stage 2 Textile Workshop alternate landmark is missing")
    tilebase_xlp = (root / "Civ Supply Chains/XLPs/CSC_Tilebases.xlp").read_text(
        encoding="utf-8"
    )
    for asset in (
        "CSC_TAILORS_Textile_Workshop",
        "CSC_TAILORS_Textile_Workshop_2",
    ):
        if asset not in tilebase_xlp:
            failures.append(f"Tailors Stage 2 TileBase asset missing from XLP: {asset}")
    project_source = (root / "Civ Supply Chains/Civ Supply Chains.civ6proj").read_text(
        encoding="utf-8"
    )
    for content in (
        "ArtDefs\\CSC_GamePropertyRanges.artdef",
        "ArtDefs\\CSC_Landmarks.artdef",
        "XLPs\\CSC_Tilebases.xlp",
    ):
        if content not in project_source:
            failures.append(f"Tailors Stage 2 art dependency is not packaged: {content}")
    deferred_properties = {
        "CSC_TAILORS_STAGE_4_CUSTOMERS",
        "CSC_TAILORS_STAGE_4_CUSTOMERS_ART",
    }
    deferred_sql_count = _scalar(
        connection,
        "SELECT COUNT(*) FROM ModifierArguments WHERE Value IN (?, ?)",
        tuple(sorted(deferred_properties)),
    )
    _expect(
        failures,
        deferred_sql_count,
        0,
        "Tailors deferred Stage 4 art properties absent from SQL",
    )
    if any(property_id in art_lua for property_id in deferred_properties):
        failures.append("Tailors deferred Stage 4 art Lua mappings were implemented early")
    return failures


def validate_phase_assertions(
    root: Path,
    phase_id: str,
    implementation: dict[str, Any],
) -> list[str]:
    declared = {
        requirement.get("id")
        for phase in implementation.get("phases", [])
        if phase.get("id") == phase_id
        for requirement in phase.get("requirements", [])
    }
    expected = REQUIREMENTS_BY_PHASE.get(phase_id)
    if expected is None:
        return [f"{phase_id}: no Tailors assertion coverage declaration"]
    failures: list[str] = []
    if declared != expected:
        failures.append(
            f"{phase_id}: assertion coverage drift; missing={sorted(declared - expected)}, "
            f"stale={sorted(expected - declared)}"
        )
    if phase_id not in IMPLEMENTED_ASSERTION_PHASES:
        failures.append(
            f"{phase_id}: executable semantic assertions are still red; implement all "
            "database-row, modifier-graph, replacement, and localization checks before handoff"
        )
        return failures
    connection, database_failures = _load_phase_database(root)
    failures.extend(database_failures)
    if connection is None:
        return failures
    try:
        failures.extend(_foundation_assertions(root, connection))
        if phase_id in {"materials_and_stage2", "stage3"}:
            failures.extend(_stage2_assertions(root, connection))
            failures.extend(_art_integration_assertions(root, connection))
        if phase_id == "stage3":
            failures.extend(_stage3_assertions(root, connection))
        if phase_id == "art_integration":
            failures.extend(_art_integration_assertions(root, connection))
    finally:
        connection.close()
    return failures
