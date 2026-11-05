"""Pin a read-only rules snapshot and the current CSC contribution questions.

This inventories source/rules, not city state or native forecast execution.
Output paths are explicit; the cache, game, policy and installed mods are untouched.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parents[5]
MOD = ROOT / "Civ Supply Chains"
HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def actions(value):
    if isinstance(value, dict):
        if "type" in value and "files" in value:
            yield value
        for item in value.values():
            yield from actions(item)
    elif isinstance(value, list):
        for item in value:
            yield from actions(item)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    db = sqlite3.connect(args.database.resolve().as_uri() + "?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    rows = lambda sql, values=(): [dict(row) for row in db.execute(sql, values)]
    buildings = rows("SELECT BuildingType,PrereqDistrict,PrereqTech,PrereqCivic,Cost,Maintenance,Entertainment,RegionalRange,CitizenSlots,MustPurchase FROM Buildings WHERE BuildingType LIKE 'BUILDING_CSC_%' ORDER BY BuildingType")
    assert len(buildings) == 19, "Study family changed: review the source before repinning"
    family = {row["BuildingType"] for row in buildings}
    ordinary = {row["BuildingType"] for row in buildings if not row["MustPurchase"]}
    assert len(ordinary) == 7
    definitions = {row["ModifierId"]: row for row in rows("SELECT * FROM Modifiers")}
    dynamic = {row["ModifierType"]: row for row in rows("SELECT * FROM DynamicModifiers")}
    arguments = defaultdict(list)
    for row in rows("SELECT * FROM ModifierArguments ORDER BY ModifierId,Name"):
        arguments[row["ModifierId"]].append(row)
    root_tables = {}
    for table, column in (("BuildingModifiers", "BuildingType"), ("DistrictModifiers", "DistrictType"), ("ImprovementModifiers", "ImprovementType")):
        roots = rows(f"SELECT {column},ModifierId AS ModifierId FROM {table} ORDER BY {column},ModifierId")
        root_tables[table] = [row for row in roots if row.get(column) in family
            or re.search(r"CSC_(BAKERS|TAILORS)", row["ModifierId"])]
    all_roots = [dict(row, table=table) for table, items in root_tables.items() for row in items]
    closure = {}

    def visit(modifier):
        if modifier in closure:
            return
        assert modifier in definitions, f"Missing attached modifier {modifier}"
        row = definitions[modifier]
        kind = dynamic.get(row["ModifierType"])
        assert kind, f"Missing dynamic modifier {row['ModifierType']}"
        closure[modifier] = {**row, "CollectionType": kind["CollectionType"],
            "EffectType": kind["EffectType"], "arguments": arguments[modifier]}
        for argument in arguments[modifier]:
            if argument["Name"] == "ModifierId":
                visit(argument["Value"])

    for row in all_roots:
        visit(row["ModifierId"])
    requirement_sets = set()
    for node in closure.values():
        requirement_sets.update(filter(None, (node["OwnerRequirementSetId"], node["SubjectRequirementSetId"])))
    members = rows("SELECT * FROM RequirementSetRequirements ORDER BY RequirementSetId,RequirementId")
    reqargs = rows("SELECT * FROM RequirementArguments ORDER BY RequirementId,Name")
    requirement_ids = set()
    changed = True
    while changed:
        before = (len(requirement_sets), len(requirement_ids))
        requirement_ids.update(row["RequirementId"] for row in members if row["RequirementSetId"] in requirement_sets)
        requirement_sets.update(row["Value"] for row in reqargs if row["RequirementId"] in requirement_ids and row["Name"] == "RequirementSetId")
        changed = before != (len(requirement_sets), len(requirement_ids))
    specialties = rows("SELECT * FROM Building_CitizenYieldChanges WHERE BuildingType LIKE 'BUILDING_CSC_%' ORDER BY BuildingType,YieldType")
    flat = rows("SELECT * FROM Building_YieldChanges WHERE BuildingType LIKE 'BUILDING_CSC_%' ORDER BY BuildingType,YieldType")
    assert not flat, "Direct flat-yield baseline changed"
    active_bm = root_tables["BuildingModifiers"]
    for building in buildings:
        building["role"] = "ordinary_producer" if building["BuildingType"] in ordinary else "internal_grant_or_flag"
        building["active_building_roots"] = sorted(row["ModifierId"] for row in active_bm if row["BuildingType"] == building["BuildingType"])
        building["specialist_yields"] = [row for row in specialties if row["BuildingType"] == building["BuildingType"]]
        building["direct_flat_yields"] = []
    manifest = json.loads((ROOT / "project/modbuddy/CivSupplyChains.actions.json").read_text(encoding="utf-8-sig"))
    relevant_actions = [row for row in actions(manifest) if row["id"].startswith("CSC_Q_") or row["id"].startswith("ModSupport_LGD")]
    profiles = {row["id"]: row["type"] for row in relevant_actions}
    assert profiles["CSC_Q_BAKERS"] == profiles["CSC_Q_TAILORS"] == "UpdateDatabase"
    for name in ("APOTHECARIES", "STONEMASONS", "CARPENTERS", "BLACKSMITHS", "GOLDSMITHS", "BREWERS"):
        assert profiles["CSC_Q_" + name] == "DoNothing"

    groups = []

    def add(identifier, priority, tables, pattern, benefit, gates, question, sources, channel="candidate_building_modifier", status="source_established; native_contribution_unmeasured_in_this_study"):
        matched = [row for row in all_roots if row["table"] in tables and re.search(pattern, row["ModifierId"])]
        groups.append({"id": identifier, "priority": priority, "root_tables": tables,
            "root_selector": pattern, "matched_root_count": len(matched),
            "root_ids": sorted({row["ModifierId"] for row in matched}),
            "source_buildings": sorted({row["BuildingType"] for row in matched if row["table"] == "BuildingModifiers"}),
            "real_benefit": benefit, "real_gates": gates, "forecast_question": question,
            "channel": channel, "status": status, "source_refs": sources})
        if len(groups[-1]["root_ids"]) > 24:
            complete = groups[-1].pop("root_ids")
            groups[-1]["root_ids_preview"] = complete[:6] + complete[-2:]
            groups[-1]["root_ids_complete_count"] = len(complete)
            groups[-1]["complete_root_ids_location"] = "raw evidence roots, filtered by root_tables/root_selector"

    B = ["BuildingModifiers"]
    D = ["DistrictModifiers"]
    I = ["ImprovementModifiers"]
    both = B + I
    add("mill_local_steps", 0, B, r"^ATTACH_MOD_CSC_ADJ_CSC_BAKERS_(WIND|WATER)_MILL_.*_STEP_[123]$",
        "Wind: +1 Quarter Production on its hills plot; Water: floor(river edges/2), maximum3. Four active +1 children total.",
        ["Corresponding functioning Mill in this city's exact completed/unpillaged Bakers Quarter", "CITY_DISTRICTS parent; property flags only on the Quarter", "Wind and Water mutually exclusive; Wind also legal on river sites"],
        "Do new unit children stay bounded/local through native scoring, preserve genuine geometry, and clear old saved bits? Smaller capacity alone does not restore skipped hypothetical gates.",
        ["Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyProcessor.sql", "Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyModifiers.sql", "Civ Supply Chains/Lua_UI/Adjacencies/CSC_AdjacencyCore.lua"])
    assert groups[-1]["matched_root_count"] == 4
    add("bakers_material_food_input", 2, I, r"MOD_CSC_BAKERS_(BASE|SPEC)_IMPROVEMENT_ATTACH_QUARTER",
        "+1 Mill Food per improved Base; +1 Cafe Food per improved Specialty. Inputs are attached by actual improvements.",
        ["Same-owner adjacent appropriate material tag and actual improvement", "Actual receiving building must operate to realize the yield"],
        "Separate live per-building GetYieldChange from candidate roots. Does an absent producer receive an existing delivered adjustment? Do not assume future unimproved supply is simulated.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql"], "live_building_yield_input")
    add("bakers_material_reciprocity", 2, B, r"MOD_CSC_BAKERS_(FLOUR_MILL|CAFE)_ATTACH_ADJ_IMP_(BASE|SPEC)(_PROD)?$",
        "+1 Production/+1 Gold to adjacent improved Base from Mill, or Specialty from Cafe.",
        ["Real producer and owned adjacent improved matching material"],
        "PLAYER_IMPROVEMENTS is absent in the inspected native forecast registry; identify omitted real benefit rather than rewarding a fictitious fully developed chain.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql", "Civ Supply Chains/Data/CSC_Q_BAKERS_GOLD.sql"])
    add("bakers_granary_exchange", 1, B, r"MOD_CSC_BAKERS_(FLOUR_MILL_ATTACH_CITY_CENTER|GRANARY_ATTACH_BAKERS_(WATER|WIND)(_PROD)?)$",
        "+1 Food to an adjacent Granary; reciprocal +1 Production/+1 Gold to the relevant Mill.",
        ["Same-owner adjacent actual Granary; its SQL leaf explicitly MustBeFunctioning=1", "No Service civic or improved-material requirement for ordinary exchange"],
        "Measure parent/child sums with actual recipient context. Native ordinary HasBuilding is actual-state; adjacency approximation is not proof of precise distance.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql", "Civ Supply Chains/Data/CSC_Q_BAKERS_GOLD.sql"])
    add("bakers_local_building_exchange", 1, B, r"MOD_CSC_BAKERS_(PROD_TO_(WATER|WIND)_MILL|GOLD_TO_(WATER|WIND)_MILL|FLOUR_MILL_FOOD_TO_BAKERY|FOOD_TO_CAFE)$",
        "Each Bakery/Cafe gives local Mill +1Production/+1Gold; Mill gives each +1Food.",
        ["Actual local buildings; exactly one Mill variant can exist", "Independent of material/customer/Service gates"],
        "Can hypothetical Bakery/Cafe credit both mutually exclusive Mill recipients, including the native absent-recipient0.5 approximation? Keep incoming Food getter separate from outgoing candidate roots.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql", "Civ Supply Chains/Data/CSC_Q_BAKERS_GOLD.sql"])
    add("bakers_stage2_service", 1, B, r"MOD_CSC_BAKERS_STAGE_2_(EFFECT_ATTACH_CITY_(WATER|WIND)|SERVICE_ATTACH_CITY|GPP_ATTACH_CITY)$",
        "At adjacent Granary: +10%growth, Storekeeper grant, +1GreatEngineer point. Storekeeper definition has no intrinsic slot/yields.",
        ["Feudalism", "Improved Base adjacent to producer", "Adjacent qualifying Granary", "Complete owner gate on source; recipient filter on subject"],
        "Which growth/grant/GPP contributions survive hypothetical admission when source owner gates are omitted? Count actual matching recipients and preserved conditions.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql"])
    add("bakers_stage3_service", 1, B, r"MOD_CSC_BAKERS_STAGE_3_(SERVICE|EFFECT|GPP)_ATTACH_COMHUB$",
        "Innkeeper hidden slot, +2Housing and +1GreatMerchant point at adjacent Market city.",
        ["Medieval Faires", "Improved Base", "Adjacent Market presence; SQL HasBuilding does not explicitly set MustBeFunctioning here"],
        "Distinguish source-gated housing/GPP from hidden grant value and intrinsic slot; determine omissions rather than inferring all service benefits from the grant alone.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql"])
    add("bakers_stage4_service", 1, B, r"MOD_CSC_BAKERS_STAGE_4_(EFFECT|SERVICE|GPP)_ATTACH_(ENTERTAINMENT|WATER_PARK|ENTER|WATER)$",
        "Groundskeeper/RideTechnician hidden slot; +2Tourism and +1GreatEngineer point at qualified Zoo/Ferris customer.",
        ["Urbanization", "Improved Base AND Specialty", "Adjacent Zoo/Ferris customer; SQL leaves lack explicit MustBeFunctioning argument"],
        "Measure Tourism/GPP/grant separately; do property/nested/owner gates disappear? These gates do not condition the Cafe's ordinary amenity or sales.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql"])
    add("bakers_market_population_sale", 1, D, r"MOD_CSC_BAKERS_(MARKET_RETURN_(PROD|GOLD)_AMOUNT_BIT_|MARKET_FOOD_AMOUNT_BIT_)",
        "0.105Food per actual customer citizen to Market city; 0.105Production+0.105Gold per customer citizen to seller city. Lua sums sellers/customers and pays each city once.",
        ["Actual functioning Bakery and Quarter", "Same-owner adjacent functioning Market building", "Customer population, including cross-city sales", "No material or Service civic requirement"],
        "CityCenter property consumers are not Bakery-owned roots. Observe delivered getter/channel explicitly; absence from candidate vector is not universal AI blindness or proof of future Lua simulation.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql", "Civ Supply Chains/Data/CSC_Q_BAKERS_GOLD.sql", "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua"], "citycenter_population_property_consumer")
    add("bakers_cafe_population_sale", 2, D, r"MOD_CSC_BAKERS_STAGE_4_(CAFE_RETURN_(PRODUCTION|GOLD)|.*_CULTURE_RETURN_).*_BIT_",
        "Per qualified customer city/site: floor(itsPopulation/5) stacks; Culture to Zoo/Ferris/optionalConservatory, Production+Gold to Cafe.",
        ["Actual functioning Cafe and Quarter", "Same-owner adjacent functioning customer building", "Floor each customer's population before summing", "No Urbanization/material gate for this ordinary sale"],
        "Read current bit states and per-building adjustments. Do not aggregate all populations before floor or treat citycenter bits as candidate Cafe roots.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql", "Civ Supply Chains/Data/CSC_Q_BAKERS_GOLD.sql", "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua"], "citycenter_stack_property_consumer")
    add("river_flags_and_prerequisites", 1, D, r"^MOD_CSC_BAKERS_(RIVER_ACCESS|NO_RIVER_ACCESS)_FLAG$",
        "Zero-cost internal flags mark Quarter river access. Water requires RiverAccess and excludes NoRiverAccess/Wind; Wind excludes Water. Neither flag is a productive investment.",
        ["Actual Quarter river state", "Flags are MustPurchase internal grants", "Bakery/Cafe need either Mill, not each other"],
        "Record hidden direct exclusion, exact first-prerequisite pointer/order, research readiness and mutual canonicalization. SQL iteration order alone does not prove the native depth path.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql"], "district_grant_and_native_prerequisite_structure")
    add("tailors_material_inputs", 2, I, r"MOD_CSC_TAILORS_(BASE|SPEC)_IMPROVEMENT_ATTACH_QUARTER$",
        "+1Culture to Workshop per improved Base; +1Culture to FashionHouse per improved Specialty.",
        ["Owned adjacent improved matching material", "Actual receiving producer for realized yield"],
        "Does the live per-building getter carry existing inputs to an unbuilt candidate? Distinguish that from discovering or developing future resources.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql"], "live_building_yield_input")
    add("tailors_material_reciprocity", 2, B, r"MOD_CSC_TAILORS_(WORKSHOP_ATTACH_ADJ_IMP_BASE|FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC)_(PROD|GOLD)$",
        "+1Production+1Gold to improved Base from Workshop or Specialty from FashionHouse.",
        ["Actual producer and owned adjacent matching improved material"],
        "Confirm the expected unsupported PLAYER_IMPROVEMENTS traversal omission in this city's native root vector; preserve real economic value separately.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql"])
    add("tailors_local_exchange", 1, B, r"MOD_CSC_TAILORS_(WORKSHOP_CULTURE_TO_(TAILOR|FASHION_HOUSE)|(TAILOR|FASHION_HOUSE)_(PROD|GOLD)_TO_WORKSHOP)$",
        "Workshop gives Tailor/FashionHouse+1Culture; each returns Workshop+1Production/+1Gold.",
        ["Actual local buildings", "FashionHouse requires Workshop, not Tailor", "No material/customer/Service requirement for ordinary local exchange"],
        "Compare outgoing candidate-root value and incoming live getter; avoid counting the same exchange twice when prerequisite value propagates.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql"])
    add("tailors_lighthouse_exchange", 2, B, r"MOD_CSC_TAILORS_(WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE|LIGHTHOUSE_ATTACH_QUARTER_(PROD|GOLD))$",
        "Workshop gives adjacent Lighthouse+1Production; Lighthouse gives Workshop+1Production/+1Gold.",
        ["Same-owner adjacent functioning Lighthouse; explicit MustBeFunctioning=1", "No NavalTradition or material requirement for ordinary exchange"],
        "Measure actual-state customer gate, adjacency approximation and absent-recipient behavior separately from Dockmaster service.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql"])
    add("tailors_stage2_service", 2, B, r"MOD_CSC_TAILORS_(STAGE_2_SERVICE_ATTACH_HARBOR|DOCKMASTER_GPP_ATTACH_HARBOR|STAGE_2_DOCKMASTER_ATTACH_)",
        "Dockmaster slot, +1GreatAdmiral point and +20%Production toward Ancient–Renaissance naval melee/ranged/raider units. Twelve explicit era×promotion-class production children.",
        ["NavalTradition", "Improved Base", "Adjacent functioning Lighthouse", "Era/promotion-class matrix applies to eligible units, not all production"],
        "Does native evaluation value all12 mutually filtered unit-production branches indiscriminately? Capture per-root accepted requirements and totals without assuming independent +240%actual benefit.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql"])
    add("tailors_stage3_service", 2, B, r"MOD_CSC_TAILORS_(STAGE_3_SERVICE_ATTACH_HOLY_SITE|SACRISTAN_(FAITH|GPP)_ATTACH_HOLY_SITE)$",
        "Sacristan slot, +10%Faith and +1GreatProphet point in adjacent Temple city.",
        ["DivineRight", "Improved Base", "Adjacent functioning Temple; explicit MustBeFunctioning=1"],
        "Which conditional Faith/GPP/grant values are admitted before civic/material readiness, and which require actual customers?",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql"])
    add("tailors_stage4_service", 2, B, r"MOD_CSC_TAILORS_(STAGE_4_SERVICE_ATTACH_THEATER|STAGE_MANAGER_(TOURISM|GPP)_ATTACH_)",
        "At Theater/Amphitheater or each named Wonder: +2Tourism,+1GreatArtist point per eligible adjacent FashionHouse. Theater StageManager adds a slot; Wonder services do not.",
        ["OperaAndBallet", "Improved Base AND Specialty", "Qualified adjacent same-owner customer", "Actual Wonder host readiness/establishment handled by synchronized Lua; exact plot matters"],
        "Can native approximation admit multiple Wonder/property-gated branches without actual qualified venues? Separate service marker grants from conditional Tourism/GPP.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Lua_UI/WonderServices/CSC_WonderServicePlacement.lua"])
    add("tailors_stage3_population_sale", 2, D, r"MOD_CSC_TAILORS_(CUSTOMER_RETURN_(PROD|GOLD)_AMOUNT_BIT_|(MARKET|TEMPLE)_CUSTOMER_CULTURE_BIT_)",
        "0.105Culture per actual Market/Temple customer citizen to its city; matching Production+Gold to Tailor city, accumulated across customer sites.",
        ["Actual functioning Tailor and Quarter", "Same-owner adjacent functioning Market or Temple", "No material/DivineRight gate for ordinary sales"],
        "Native roots vs live citycenter property consumers: does the new candidate receive a justified prospective contribution, no contribution, or an improperly ungated amount?",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql", "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua"], "citycenter_population_property_consumer")
    add("tailors_stage4_population_sale", 2, D, r"MOD_CSC_TAILORS_STAGE_4_.*RETURN_.*BIT_",
        "Each actual Amphitheater/Bolshoi/Broadway/Sydney site contributes floor(itsCityPopulation/5): Culture to that venue, Production+Gold to FashionHouse.",
        ["Functioning FashionHouse and Quarter", "Same-owner adjacent actual functioning venue", "Theater customer requires functioning district; Wonder uses exact building plot", "Floor per customer before sum; no material/Service-civic gate"],
        "Measure live named-building adjustment and current bits without inventing future venue construction or confusing neighboring Wonders in one city.",
        ["Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Data/CSC_Q_TAILORS_GOLD.sql", "Civ Supply Chains/Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua"], "citycenter_stack_property_consumer")
    add("trade_route_transactions", 3, D, r"MOD_CSC_(BAKERS|TAILORS)_(IMPORT_|EXPORT_)",
        "Each enabled import channel gives origin+1Food(Bakers)or+1Culture(Tailors),plus+1Amenity; qualifying destination producer receives+1Production/+1Gold per export route.",
        ["Real active route (domestic/international same fixed CSC payout)", "Origin lacks functioning same-industry Quarter", "Destination producer supplied property; Tailors also explicitly checks producer building", "Ordinary imports Boolean per channel; export counts encoded with1/2/4/8/16 bits", "No automatic international native-yield multiplier on fixed CSC modifiers"],
        "Route-state UI/gameplay bridge does not run hypothetical future routes. Separate citycenter consumers, actual supplied properties and current per-building returns from candidate-owned forecast roots.",
        ["Civ Supply Chains/Lua_UI/TradeRoutes/CSC_TradeRouteInteractions.lua", "Civ Supply Chains/Lua_UI/TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua", "Civ Supply Chains/Lua_UI/TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua"], "citycenter_route_property_consumer")
    add("non_yield_properties", 2, B, r"MOD_CSC_(BAKERS_(EXPORT_(BAKERY|CAFE)_SUPPLIED_PROP|STAGE_[234]_PROP.*)|TAILORS_((TAILOR|FASHION_HOUSE)_(SUPPLIED|SERVICE_ELIGIBLE)_PROPERTY|STAGE_[234]_ART_PROPERTY))$",
        "State for export supply, Service eligibility and expanded art. Property amount1 is a flag, not1economic yield.",
        ["Complete source owner gates from corresponding Service/supply contract", "Properties consumed by actual art/trade/Wonder scripts"],
        "Does native interpreter assign nonzero economic value to property flags or confuse side effects with yields? Expected real benefit lives in downstream consumers, not property numeric magnitude.",
        ["Civ Supply Chains/Data/CSC_Q_BAKERS.sql", "Civ Supply Chains/Data/CSC_Q_TAILORS.sql", "Civ Supply Chains/Lua_UI/ArtProperties/CSC_ArtProperties.lua"], "state_property")

    common = [
        {"id": "intrinsic_amenities", "priority": 1, "buildings": sorted(row["BuildingType"] for row in buildings if row["Entertainment"]),
         "real_benefit": "Bakery/Tailor1localAmenity; Cafe/FashionHouse1Amenity RegionalRange6. Independent of material/customer Service gates.",
         "forecast_question": "Preserve legitimate amenity value. Record recipient cities, need/marginal overlap, readiness/horizon and actual site context; city/type aggregation alone does not establish site-aware regional pricing."},
        {"id": "specialist_slots", "priority": 2, "buildings": sorted({row["BuildingType"] for row in specialties}),
         "real_benefit": "Assigned specialist yields only: Bakery2Food; Cafe1Food1Culture; Tailor2Culture1Gold; FashionHouse1Culture2Gold; Bakers Stage4services2Culture2Gold. Other hidden service slots have no own declared Building_CitizenYieldChanges rows.",
         "forecast_question": "Do not report slots or per-citizen specialist yields as passive flat building income. Account for staffing and displaced citizen opportunities."},
        {"id": "hidden_grants", "priority": 1, "buildings": sorted(family - ordinary),
         "real_benefit": "Twelve MustPurchase internal buildings:2riverflags+10Service markers. Zero cost/maintenance; not ordinary production options. Slots live on certain markers while active effects are producer-owned roots.",
         "forecast_question": "Observe rather than force their admission. Distinguish direct candidate exclusion, nested grant valuation, prerequisite-depth artifacts and persistent markers after eligibility changes."},
        {"id": "native_prerequisites_and_units", "priority": 1, "buildings": sorted(ordinary),
         "real_benefit": "Seven ordinary producers; actual base Production costs, maintenance and unlocks are inputs, not native utility prices. No direct flat Building_YieldChanges across the19definitions.",
         "forecast_question": "Record exact first-prerequisite vector/readiness and building entry/return values. Preserve genuine costs/delays; do not add the entire offline economic ledger to an already overlapping native score."},
    ]

    source_paths = sorted({MOD / row["files"][0] for row in relevant_actions if row.get("files")}
        | {MOD / "Data/CSC_Q_ALL.sql", ROOT / "project/modbuddy/CivSupplyChains.actions.json"}
        | {MOD / f"Lua_UI/Adjacencies/CSC_Adjacency{name}{extension}" for name, extension in (("Schema", ".sql"), ("Processor", ".sql"), ("Modifiers", ".sql"), ("Core", ".lua"))}
        | {MOD / rel for rel in ("Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua", "Lua_UI/TradeRoutes/CSC_TradeRouteInteractions.lua", "Lua_UI/TradeRoutes/CSC_TradeRouteInteractions_Gameplay.lua", "Lua_UI/TradeRoutes/CSC_BTS_TradeRoutePreviewSupport.lua", "Lua_UI/WonderServices/CSC_WonderServicePlacement.lua", "Lua_UI/ArtProperties/CSC_ArtProperties.lua")}
        | set((ROOT / "docs/content/quarters").glob("*.md")))
    pins = [{"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256_exact_bytes": digest(path)} for path in source_paths if path.is_file()]
    raw = {"schema": 1, "date": "2026-11-05", "scope": "Source/rules only; no native calls or world state",
        "database_path": str(args.database.resolve()), "database_sha256": digest(args.database),
        "buildings": buildings, "roots": root_tables, "modifier_closure": closure,
        "requirement_sets": [row for row in rows("SELECT * FROM RequirementSets ORDER BY RequirementSetId") if row["RequirementSetId"] in requirement_sets],
        "requirement_members": [row for row in members if row["RequirementSetId"] in requirement_sets],
        "requirements": [row for row in rows("SELECT * FROM Requirements ORDER BY RequirementId") if row["RequirementId"] in requirement_ids],
        "requirement_arguments": [row for row in reqargs if row["RequirementId"] in requirement_ids],
        "building_prerequisites": rows("SELECT * FROM BuildingPrereqs WHERE Building LIKE 'BUILDING_CSC_%' ORDER BY Building,PrereqBuilding"),
        "mutual_exclusions": rows("SELECT * FROM MutuallyExclusiveBuildings WHERE Building LIKE 'BUILDING_CSC_%' ORDER BY Building,MutuallyExclusiveBuilding"),
        "flat_yields": flat, "specialist_yields": specialties,
        "population_transactions": rows("SELECT * FROM CSC_Stage3CustomerTransactions ORDER BY TransactionId"),
        "yield_default_values": rows("SELECT YieldType,DefaultValue FROM Yields ORDER BY YieldType"),
        "local_mill_steps": rows("SELECT * FROM CSC_AdjacencyUnitSteps ORDER BY ID"),
        "action_profiles": relevant_actions, "source_pins": pins}
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    raw_path = args.artifact_dir / "rules-and-roots.json"
    raw_path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    concise = {"schema": 1, "date": "2026-11-05", "scope": "Current source truth and questions, not measured native contributions",
        "studied_profile": "Core Bakers/Tailors plus Gold companions, local Mill unit steps; conditional variants listed separately",
        "summary": {"loaded_buildings": len(buildings), "ordinary_producers": len(ordinary), "internal_grants_flags": len(family - ordinary),
            "active_building_root_counts": dict(sorted(Counter(row["BuildingType"] for row in active_bm if row["BuildingType"] in family).items())),
            "flat_yield_rows": len(flat), "contribution_groups": len(groups), "root_closure_nodes": len(closure)},
        "probe_family": sorted(family), "building_definitions": buildings, "contribution_groups": groups, "common_components": common,
        "optional_profiles": [
            {"name": "Monopolies_Mode", "loaded_in_snapshot": any("INDUSTRY" in row["ModifierId"] for row in all_roots),
             "semantics": "Bakers/Tailors Industry/Corporation inputs total2/3; producer-to-improvement files add marginal1/2 to core1. Keep core/companion Gold separate; no Product commissioning in CSC.",
             "source_files": [f"Civ Supply Chains/Data/CSC_Q_{quarter}_MC_MODE{gold}.sql" for quarter in ("BAKERS", "TAILORS") for gold in ("", "_GOLD")]},
            {"name": "ModSupport_LGD", "loaded_in_snapshot": "BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN" in family,
             "additional_building": "BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN",
             "semantics": "Horticulturist: zero-cost MustPurchase hidden slot at Garden/Conservatory;2Culture2Gold specialist yields; Urbanization+Base+Specialty+qualifiedcustomer gates2Tourism/+1GreatArtistpoint; Cafe/Conservatory sales use same per-customer stacks.",
             "source_files": ["Civ Supply Chains/ModSupport/ModSupport_LGD.sql", "Civ Supply Chains/ModSupport/ModSupport_LGD_GOLD.sql"]}],
        "inactive_quarters": [{"quarter": name, "action": profiles["CSC_Q_" + name],
            "note": "Source scaffold only; not loaded. Carpenters contains a parked Joinery definition, not an implemented chain." if name == "CARPENTERS" else "Source scaffold only; not loaded."}
            for name in ("APOTHECARIES", "STONEMASONS", "CARPENTERS", "BLACKSMITHS", "GOLDSMITHS", "BREWERS")],
        "known_design_source_distinctions": [
            "Public Stage3 descriptions use0.1 per citizen; current transaction registry uses0.105. This inventory records the actual engine amount; no design correction was made.",
            "Wind Mill is legal on river sites; Water additionally requires RiverAccess. Both are mutually exclusive. Do not label Wind as strictly no-river.",
            "Cafe/FashionHouse do not require Bakery/Tailor; each requires the common upstream Mill/Workshop.",
            "Customer population, not seller population, determines the current Lua sale target; floor each Stage4customer before summing.",
            "Flags/properties and hidden service markers are not independent yield streams or automatically normal build candidates.",
            "Source-sized yield DefaultValue is only one native conversion input; no universal yield-to-Q8 exchange rate is asserted."],
        "raw_evidence": {"path": str(raw_path), "sha256": digest(raw_path), "database_sha256": digest(args.database)},
        "source_pins": pins,
        "validation": {"all_attached_modifier_references_resolved": True, "all_dynamic_types_resolved": True,
            "local_mill_active_children": 4, "ordinary7_internal12": True, "game_started": False,
            "native_observation": False, "tuning_changed": False}}
    output = HERE / "contributions.json"
    output.write_text(json.dumps(concise, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "ledger": str(output), "sha256": digest(output),
        "bytes": output.stat().st_size, "raw": str(raw_path), "raw_sha256": digest(raw_path),
        "raw_bytes": raw_path.stat().st_size, "summary": concise["summary"]}))


if __name__ == "__main__":
    main()
