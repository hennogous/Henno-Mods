#!/usr/bin/env python3
"""Validate CSC Quarter contracts and their locked/preserved inputs."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[3]
SPEC_ROOT = ROOT / "project" / "specs"
STYLE_MODULE_SPEC = importlib.util.spec_from_file_location(
    "csc_validate_sql_style", Path(__file__).with_name("validate_sql_style.py")
)
assert STYLE_MODULE_SPEC and STYLE_MODULE_SPEC.loader
SQL_STYLE = importlib.util.module_from_spec(STYLE_MODULE_SPEC)
STYLE_MODULE_SPEC.loader.exec_module(SQL_STYLE)
LOCALIZATION_MODULE_SPEC = importlib.util.spec_from_file_location(
    "csc_validate_localization_patterns",
    Path(__file__).with_name("validate_localization_patterns.py"),
)
assert LOCALIZATION_MODULE_SPEC and LOCALIZATION_MODULE_SPEC.loader
LOCALIZATION_PATTERNS = importlib.util.module_from_spec(LOCALIZATION_MODULE_SPEC)
LOCALIZATION_MODULE_SPEC.loader.exec_module(LOCALIZATION_PATTERNS)

QUARTER_ICON_ATLAS_LAYOUT = {
    "district_normal": 0,
    "district_fow": 1,
    "stage2_building": 4,
    "stage3_building": 5,
    "stage4_building": 6,
    "stage2_service": 8,
    "stage3_service": 9,
    "stage4_service": 10,
}

QUARTER_ICON_ATLAS_LAYOUT = {
    "district_normal": 0,
    "district_fow": 1,
    "stage2_building": 4,
    "stage3_building": 5,
    "stage4_building": 6,
    "stage2_service": 8,
    "stage3_service": 9,
    "stage4_service": 10,
}


class Validation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_schema(instance: dict[str, Any], schema_name: str, result: Validation) -> None:
    schema_path = SPEC_ROOT / "schema" / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    for failure in sorted(validator.iter_errors(instance), key=lambda error: list(error.path)):
        location = ".".join(str(part) for part in failure.path) or "<root>"
        result.error(f"{schema_name} {location}: {failure.message}")


def validate_icon_atlas_layout(
    gameplay_catalog: dict[str, Any],
    implementation: dict[str, Any],
    result: Validation,
) -> dict[str, int]:
    catalog_layout = gameplay_catalog.get("quarter_icon_atlas_layout")
    if catalog_layout != QUARTER_ICON_ATLAS_LAYOUT:
        result.error(
            "gameplay catalog quarter_icon_atlas_layout must match the shared "
            "CSC district/building/service convention"
        )
        catalog_layout = QUARTER_ICON_ATLAS_LAYOUT

    contract = implementation.get("icon_atlas_layout", {})
    overrides = contract.get("overrides", {})
    if not isinstance(overrides, dict):
        return dict(catalog_layout)
    effective = dict(catalog_layout)
    effective.update(overrides)
    duplicate_indices = sorted(
        index for index in set(effective.values()) if list(effective.values()).count(index) > 1
    )
    if duplicate_indices:
        result.error(
            "icon_atlas_layout assigns multiple semantic roles to index(es): "
            + ", ".join(str(index) for index in duplicate_indices)
        )
    return effective


def validate_icon_atlas_layout(
    gameplay_catalog: dict[str, Any],
    implementation: dict[str, Any],
    result: Validation,
) -> dict[str, int]:
    catalog_layout = gameplay_catalog.get("quarter_icon_atlas_layout")
    if catalog_layout != QUARTER_ICON_ATLAS_LAYOUT:
        result.error(
            "gameplay catalog quarter_icon_atlas_layout must match the shared "
            "CSC district/building/service convention"
        )
        catalog_layout = QUARTER_ICON_ATLAS_LAYOUT

    contract = implementation.get("icon_atlas_layout", {})
    overrides = contract.get("overrides", {})
    if not isinstance(overrides, dict):
        return dict(catalog_layout)
    effective = dict(catalog_layout)
    effective.update(overrides)
    duplicate_indices = sorted(
        index for index in set(effective.values()) if list(effective.values()).count(index) > 1
    )
    if duplicate_indices:
        result.error(
            "icon_atlas_layout assigns multiple semantic roles to index(es): "
            + ", ".join(str(index) for index in duplicate_indices)
        )
    return effective


def resolve_design_ref(document: Any, reference: str) -> tuple[bool, Any]:
    current = document
    tokens = reference.split(".")
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if isinstance(current, dict) and token in current:
            current = current[token]
            index += 1
        elif isinstance(current, list):
            match = None
            consumed = 0
            for end in range(len(tokens), index, -1):
                candidate = ".".join(tokens[index:end])
                match = next(
                    (
                        item
                        for item in current
                        if isinstance(item, dict) and str(item.get("id")) == candidate
                    ),
                    None,
                )
                if match is not None:
                    consumed = end - index
                    break
            if match is None:
                return False, None
            current = match
            index += consumed
        else:
            return False, None
    return True, current


def phase_design_sha256(
    design: dict[str, Any], implementation: dict[str, Any], phase_id: str
) -> str:
    """Hash only the canonical design subtrees consumed by one phase."""
    phase = next(
        (item for item in implementation.get("phases", []) if item.get("id") == phase_id),
        None,
    )
    if phase is None:
        raise ValueError(f"unknown phase {phase_id}")
    references = sorted(
        {
            reference
            for requirement in phase.get("requirements", [])
            for reference in requirement.get("design_refs", [])
        }
    )
    resolved: list[dict[str, Any]] = []
    for reference in references:
        found, value = resolve_design_ref(design, reference)
        if not found:
            raise ValueError(f"{phase_id}: unresolved design reference {reference}")
        resolved.append({"reference": reference, "value": value})
    payload = json.dumps(
        resolved, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def phase_design_sha256(
    design: dict[str, Any], implementation: dict[str, Any], phase_id: str
) -> str:
    """Hash only the canonical design subtrees consumed by one phase."""
    phase = next(
        (item for item in implementation.get("phases", []) if item.get("id") == phase_id),
        None,
    )
    if phase is None:
        raise ValueError(f"unknown phase {phase_id}")
    references = sorted(
        {
            reference
            for requirement in phase.get("requirements", [])
            for reference in requirement.get("design_refs", [])
        }
    )
    resolved: list[dict[str, Any]] = []
    for reference in references:
        found, value = resolve_design_ref(design, reference)
        if not found:
            raise ValueError(f"{phase_id}: unresolved design reference {reference}")
        resolved.append({"reference": reference, "value": value})
    payload = json.dumps(
        resolved, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def collect_design_ids(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        identifier = value.get("id")
        if isinstance(identifier, str) and identifier.startswith("D."):
            found.add(identifier)
        for child in value.values():
            found.update(collect_design_ids(child))
    elif isinstance(value, list):
        for child in value:
            found.update(collect_design_ids(child))
    return found


def mapping_exists(path: Path, resource: str, material_class: str) -> bool:
    sql = path.read_text(encoding="utf-8")
    pattern = re.compile(
        r"SELECT\s+ResourceType\s*,\s*'"
        + re.escape(material_class)
        + r"'[\s\S]*?WHERE\s+ResourceType\s+IN\s*\([\s\S]*?'"
        + re.escape(resource)
        + r"'[\s\S]*?\)\s*;",
        re.IGNORECASE,
    )
    return bool(pattern.search(sql))


def flatten_requirements(implementation: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        requirement
        for phase in implementation.get("phases", [])
        for requirement in phase.get("requirements", [])
    ]


DOMESTIC_TRADE_PATTERN = "GP.TRADE.DOMESTIC_SUPPLY"
TRADE_YIELD_PRESENTATION_PATTERN = "GP.TRADE.CITY_YIELD_PRESENTATION"
WONDER_SERVICE_PATTERN = "GP.SERVICE.WONDER_HOSTED_EXACT_PLACEMENT"


def design_origin_yields(value: Any) -> dict[str, float]:
    """Collect designed origin yields from a referenced trade-design subtree."""
    totals: dict[str, float] = {}
    if isinstance(value, dict):
        origin_yields = value.get("origin_yields")
        if isinstance(origin_yields, dict):
            for yield_type, amount in origin_yields.items():
                if isinstance(yield_type, str) and isinstance(amount, (int, float)):
                    totals[yield_type] = totals.get(yield_type, 0) + float(amount)
        for key, child in value.items():
            if key != "origin_yields":
                for yield_type, amount in design_origin_yields(child).items():
                    totals[yield_type] = totals.get(yield_type, 0) + amount
    elif isinstance(value, list):
        for child in value:
            for yield_type, amount in design_origin_yields(child).items():
                totals[yield_type] = totals.get(yield_type, 0) + amount
    return totals


def validate_trade_route_yield_presentation_requirement(
    requirement: dict[str, Any],
    origin_yields: dict[str, float],
    implementation: dict[str, Any],
    result: Validation,
) -> None:
    """Validate the explicit contract that reclassifies CSC route-yield modifiers."""
    requirement_id = str(requirement.get("id", "<unknown>"))
    patterns = set(requirement.get("gameplay_patterns", []))
    binding = requirement.get("trade_route_yield_presentation")
    is_domestic_trade = DOMESTIC_TRADE_PATTERN in patterns
    has_pattern = TRADE_YIELD_PRESENTATION_PATTERN in patterns

    if is_domestic_trade and origin_yields and not has_pattern:
        result.error(
            f"{requirement_id}: domestic trade origin_yields require "
            f"{TRADE_YIELD_PRESENTATION_PATTERN}"
        )
    if is_domestic_trade and origin_yields and not isinstance(binding, dict):
        result.error(
            f"{requirement_id}: domestic trade origin_yields require "
            "trade_route_yield_presentation"
        )
    if binding is not None and not has_pattern:
        result.error(
            f"{requirement_id}: trade_route_yield_presentation requires "
            f"{TRADE_YIELD_PRESENTATION_PATTERN}"
        )
    if has_pattern and not isinstance(binding, dict):
        result.error(
            f"{requirement_id}: {TRADE_YIELD_PRESENTATION_PATTERN} requires "
            "trade_route_yield_presentation"
        )
    if not has_pattern or not isinstance(binding, dict):
        return

    entries = binding.get("entries", [])
    if not isinstance(entries, list):
        return
    for label, key in (
        ("entry ID", "entry_id"),
        ("modifier ID", "modifier_id"),
        ("property name", "property_name"),
    ):
        values = [entry.get(key) for entry in entries if isinstance(entry, dict)]
        text_values = [value for value in values if isinstance(value, str)]
        if len(text_values) != len(set(text_values)):
            result.error(
                f"{requirement_id}: duplicate {label} in "
                "trade_route_yield_presentation"
            )

    expected_quarter = str(implementation.get("quarter", "")).upper()
    transaction_tiers = {
        tier
        for reference in requirement.get("design_refs", [])
        for marker, tier in (
            (".D.STAGE3.", "CONSUMER"),
            (".D.STAGE4.", "SPECIALTY"),
        )
        if marker in reference
    }
    expected_tier = next(iter(transaction_tiers)) if len(transaction_tiers) == 1 else None
    if entries and expected_tier is None:
        result.error(
            f"{requirement_id}: presentation entries require exactly one Stage 3 "
            "CONSUMER or Stage 4 SPECIALTY design reference"
        )
    actual_yields: dict[str, float] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        if entry.get("quarter_key") != expected_quarter:
            result.error(
                f"{requirement_id}: presentation entry {entry.get('entry_id')} "
                f"must use quarter_key {expected_quarter}"
            )
        yield_type = entry.get("yield_type")
        amount = entry.get("amount")
        if isinstance(yield_type, str) and yield_type.startswith("YIELD_") and expected_tier:
            expected_entry_id = (
                f"CSC_{expected_quarter}_IMPORT_{expected_tier}_"
                f"{yield_type.removeprefix('YIELD_')}"
            )
            if entry.get("entry_id") != expected_entry_id:
                result.error(
                    f"{requirement_id}: presentation entry ID must be "
                    f"{expected_entry_id}, found {entry.get('entry_id')}"
                )
        if isinstance(yield_type, str) and isinstance(amount, (int, float)):
            actual_yields[yield_type] = actual_yields.get(yield_type, 0) + float(amount)
    if actual_yields != origin_yields:
        result.error(
            f"{requirement_id}: presentation yields differ from design origin_yields; "
            f"expected={origin_yields}, actual={actual_yields}"
        )

    registry_output = binding.get("registry_output")
    ui_output = binding.get("ui_output")
    declared_outputs = set(requirement.get("outputs", []))
    known_outputs = set(implementation.get("planned_outputs", {}))
    actions = implementation.get("build_wiring", {}).get("actions", {})
    if registry_output not in known_outputs:
        result.error(
            f"{requirement_id}: presentation references unknown registry output "
            f"{registry_output}"
        )
    if registry_output not in declared_outputs:
        result.error(
            f"{requirement_id}: outputs omit presentation registry output "
            f"{registry_output}"
        )
    if ui_output not in known_outputs:
        result.error(f"{requirement_id}: presentation references unknown output {ui_output}")
    if ui_output not in declared_outputs:
        result.error(f"{requirement_id}: outputs omit presentation output {ui_output}")
    registry_path = str(
        implementation.get("planned_outputs", {}).get(registry_output, "")
    ).replace("\\", "/")
    if not registry_path.startswith("Civ Supply Chains/ModSupport/"):
        result.error(
            f"{requirement_id}: presentation registry output must live in ModSupport"
        )
    registry_action = actions.get(registry_output, {})
    if registry_action.get("type") != "UpdateDatabase":
        result.error(
            f"{requirement_id}: presentation registry output {registry_output} "
            "must use UpdateDatabase"
        )
    if registry_action.get("criteria") != ["SimpleUIAdjustmentsMod"]:
        result.error(
            f"{requirement_id}: presentation registry output {registry_output} "
            "must be gated only by SimpleUIAdjustmentsMod"
        )

    ui_action = actions.get(ui_output, {})
    if ui_action.get("type") != "ReplaceUIScript":
        result.error(
            f"{requirement_id}: presentation output {ui_output} must use ReplaceUIScript"
        )
    if ui_action.get("lua_context") != "Suk_YieldTT":
        result.error(
            f"{requirement_id}: presentation output {ui_output} must replace Suk_YieldTT"
        )
    if ui_action.get("criteria") != ["SimpleUIAdjustmentsMod"]:
        result.error(
            f"{requirement_id}: presentation output {ui_output} must be gated only "
            "by SimpleUIAdjustmentsMod"
        )
    registry_order = registry_action.get("load_order")
    ui_order = ui_action.get("load_order")
    if not isinstance(registry_order, int) or not isinstance(ui_order, int) or registry_order >= ui_order:
        result.error(
            f"{requirement_id}: presentation registry must load before Suk_YieldTT"
        )


def validate_trade_route_yield_presentation_uniqueness(
    requirements: list[dict[str, Any]], result: Validation
) -> None:
    """Reject registry identities reused across separate requirement bindings."""
    seen: dict[str, dict[str, str]] = {
        "entry_id": {},
        "modifier_id": {},
        "property_name": {},
    }
    for requirement in requirements:
        requirement_id = str(requirement.get("id", "<unknown>"))
        binding = requirement.get("trade_route_yield_presentation")
        if not isinstance(binding, dict):
            continue
        for entry in binding.get("entries", []):
            if not isinstance(entry, dict):
                continue
            for key, owners in seen.items():
                value = entry.get(key)
                if not isinstance(value, str):
                    continue
                prior = owners.get(value)
                if prior is not None and prior != requirement_id:
                    result.error(
                        f"{requirement_id}: {key} {value} is already bound by {prior}"
                    )
                owners[value] = requirement_id


def wonder_service_destinations(value: Any) -> list[dict[str, Any]]:
    """Return explicit Wonder-tile destinations from a referenced Service design node."""
    if not isinstance(value, dict) or not value.get("service"):
        return []
    destinations = value.get("destinations", [])
    if not isinstance(destinations, list):
        return []
    return [
        destination
        for destination in destinations
        if isinstance(destination, dict)
        and destination.get("placement") == "wonder_tile"
        and isinstance(destination.get("wonder"), str)
    ]


def validate_wonder_service_requirement(
    requirement: dict[str, Any],
    design_destinations: list[dict[str, Any]],
    implementation: dict[str, Any],
    result: Validation,
) -> None:
    requirement_id = str(requirement.get("id", "<unknown>"))
    patterns = set(requirement.get("gameplay_patterns", []))
    binding = requirement.get("wonder_service_binding")
    has_pattern = WONDER_SERVICE_PATTERN in patterns

    if design_destinations and not has_pattern:
        result.error(
            f"{requirement_id}: Wonder-tile Service design requires {WONDER_SERVICE_PATTERN}"
        )
    if design_destinations and not isinstance(binding, dict):
        result.error(
            f"{requirement_id}: Wonder-tile Service design requires wonder_service_binding"
        )
    if binding is not None and not has_pattern:
        result.error(
            f"{requirement_id}: wonder_service_binding requires {WONDER_SERVICE_PATTERN}"
        )
    if not has_pattern or not isinstance(binding, dict):
        return

    variants = binding.get("wonder_variants", [])
    if not isinstance(variants, list):
        return
    hosts = [variant.get("host_wonder_type") for variant in variants if isinstance(variant, dict)]
    services = [variant.get("service_building_type") for variant in variants if isinstance(variant, dict)]
    properties = [variant.get("activation_property") for variant in variants if isinstance(variant, dict)]
    for label, values in (
        ("host Wonder", hosts),
        ("internal Service building", services),
        ("activation property", properties),
    ):
        text_values = [value for value in values if isinstance(value, str)]
        if len(text_values) != len(set(text_values)):
            result.error(f"{requirement_id}: duplicate {label} in wonder_service_binding")

    expected_hosts = {destination["wonder"] for destination in design_destinations}
    actual_hosts = {host for host in hosts if isinstance(host, str)}
    if expected_hosts != actual_hosts:
        result.error(
            f"{requirement_id}: Wonder host mapping differs from design; "
            f"missing={sorted(expected_hosts - actual_hosts)}, "
            f"extra={sorted(actual_hosts - expected_hosts)}"
        )
    if any(destination.get("citizen_slots") != 0 for destination in design_destinations):
        result.error(
            f"{requirement_id}: every Wonder-tile destination must declare citizen_slots: 0"
        )

    normal = binding.get("normal_destination")
    if isinstance(normal, dict) and normal.get("service_building_type") in services:
        result.error(
            f"{requirement_id}: normal and Wonder destinations must use distinct building types"
        )

    placement = binding.get("placement", {})
    ui = binding.get("ui", {})
    output_roles = {
        "gameplay reconciler": placement.get("output"),
        "City Breakdown UI": ui.get("city_breakdown_output"),
        "base PlotToolTip UI": ui.get("base_plot_tooltip_output"),
        "Sukritact PlotToolTip UI": ui.get("suk_plot_tooltip_output"),
    }
    declared_outputs = set(requirement.get("outputs", []))
    known_outputs = set(implementation.get("planned_outputs", {}))
    actions = implementation.get("build_wiring", {}).get("actions", {})
    expected_action_types = {
        "gameplay reconciler": "AddGameplayScripts",
        "City Breakdown UI": "AddUserInterfaces",
        "base PlotToolTip UI": "ReplaceUIScript",
        "Sukritact PlotToolTip UI": "ReplaceUIScript",
    }
    for role, output_key in output_roles.items():
        if not isinstance(output_key, str):
            continue
        if output_key not in known_outputs:
            result.error(f"{requirement_id}: {role} references unknown output {output_key}")
        if output_key not in declared_outputs:
            result.error(f"{requirement_id}: outputs omit {role} output {output_key}")
        action = actions.get(output_key, {})
        expected_type = expected_action_types[role]
        if action.get("type") != expected_type:
            result.error(
                f"{requirement_id}: {role} output {output_key} must use {expected_type}"
            )
        if expected_type == "ReplaceUIScript" and action.get("lua_context") != "PlotToolTip":
            result.error(
                f"{requirement_id}: {role} output {output_key} must replace PlotToolTip"
            )

    base_output = output_roles.get("base PlotToolTip UI")
    suk_output = output_roles.get("Sukritact PlotToolTip UI")
    if isinstance(base_output, str):
        if "NoSimpleUIAdjustmentsMod" not in actions.get(base_output, {}).get("criteria", []):
            result.error(
                f"{requirement_id}: base PlotToolTip replacement requires NoSimpleUIAdjustmentsMod"
            )
        inverse_contract = (
            implementation.get("build_wiring", {})
            .get("criteria_contracts", {})
            .get("NoSimpleUIAdjustmentsMod", {})
        )
        if inverse_contract != {
            "kind": "ModInUse",
            "value": "805cc499-c534-4e0a-bdce-32fb3c53ba38",
            "inverse": True,
        }:
            result.error(
                f"{requirement_id}: NoSimpleUIAdjustmentsMod must be the inverse "
                "ModInUse criterion for Simple UI Adjustments"
            )
    if isinstance(suk_output, str):
        if "SimpleUIAdjustmentsMod" not in actions.get(suk_output, {}).get("criteria", []):
            result.error(
                f"{requirement_id}: Sukritact PlotToolTip replacement requires SimpleUIAdjustmentsMod"
            )

    required_refreshes = {
        "INITIALIZE",
        "Events.LoadScreenClose",
        "Events.WonderCompleted",
        "Events.PlayerTurnActivated",
    }
    actual_refreshes = set(placement.get("refresh_events", []))
    if not required_refreshes.issubset(actual_refreshes):
        result.error(
            f"{requirement_id}: exact-plot reconciler omits refresh events "
            + ", ".join(sorted(required_refreshes - actual_refreshes))
        )


ACTIVE_PHASE_STATUSES = {"approved", "implementing", "ready_for_review", "accepted"}


def validate_quarter(quarter: str, check_clean_start: bool) -> Validation:
    result = Validation()
    quarter_dir = SPEC_ROOT / quarter
    design_path = quarter_dir / "design.yaml"
    implementation_path = quarter_dir / "implementation.yaml"
    control_path = quarter_dir / "control.yaml"

    try:
        design = load_yaml(design_path)
        implementation = load_yaml(implementation_path)
        control = load_yaml(control_path)
        gameplay_catalog = load_yaml(ROOT / implementation["gameplay_catalog"])
        localization_catalog = load_yaml(ROOT / implementation["localization_catalog"])
        load_yaml(ROOT / implementation["sql_style_catalog"])
    except (OSError, KeyError, ValueError, yaml.YAMLError) as failure:
        result.error(str(failure))
        return result

    validate_schema(design, "quarter-design.schema.json", result)
    validate_schema(implementation, "quarter-implementation.schema.json", result)
    validate_schema(control, "quarter-control.schema.json", result)
    localization_catalog_path = ROOT / implementation["localization_catalog"]
    for failure in LOCALIZATION_PATTERNS.validate_catalog(
        localization_catalog, localization_catalog_path
    ):
        result.error(f"localization catalog: {failure}")
    validate_icon_atlas_layout(gameplay_catalog, implementation, result)
    validate_icon_atlas_layout(gameplay_catalog, implementation, result)

    for name, document in (
        ("design", design),
        ("implementation", implementation),
        ("control", control),
    ):
        if document.get("quarter") != quarter:
            result.error(f"{name}.quarter is {document.get('quarter')!r}, expected {quarter!r}")

    canonical_path = ROOT / str(design.get("canonical_source", ""))
    if canonical_path.is_file():
        actual = sha256(canonical_path)
        if actual != design.get("canonical_source_sha256"):
            result.error("design canonical source hash is stale")
    else:
        result.error(f"missing canonical design source: {canonical_path}")

    for locked in control.get("locked_sources", []):
        source_path = ROOT / str(locked.get("path", ""))
        if not source_path.is_file():
            result.error(f"missing locked source: {locked.get('path')}")
            continue
        actual = sha256(source_path)
        if actual != locked.get("sha256"):
            result.error(f"locked source changed: {locked.get('path')}")

    gameplay_patterns = {
        pattern["id"]: pattern for pattern in gameplay_catalog.get("patterns", [])
    }
    localization_patterns = {
        pattern["id"]: pattern for pattern in localization_catalog.get("patterns", [])
    }
    if len(gameplay_patterns) != len(gameplay_catalog.get("patterns", [])):
        result.error("gameplay catalog contains duplicate pattern IDs")
    if len(localization_patterns) != len(localization_catalog.get("patterns", [])):
        result.error("localization catalog contains duplicate pattern IDs")
    valid_classifications = {
        "reusable_invariant",
        "reusable_parameterized",
        "specialized_optional",
        "bakers_only",
    }
    for pattern_id, pattern in gameplay_patterns.items():
        if pattern.get("classification") not in valid_classifications:
            result.error(f"{pattern_id}: invalid gameplay classification")
        if not pattern.get("source_anchor"):
            result.error(f"{pattern_id}: missing Bakers source anchor")

    requirements = flatten_requirements(implementation)
    requirement_ids = {requirement.get("id") for requirement in requirements}
    if len(requirement_ids) != len(requirements):
        result.error("implementation contains duplicate requirement IDs")
    output_keys = set(implementation.get("planned_outputs", {}))
    style_profiles = implementation.get("sql_style_profiles", {})
    unknown_style_outputs = set(style_profiles) - output_keys
    if unknown_style_outputs:
        result.error(
            "SQL style profiles reference unknown outputs: "
            + ", ".join(sorted(unknown_style_outputs))
        )
    used_design_ids: set[str] = set()

    for rule in implementation.get("implementation_rules", []):
        if isinstance(rule, str) and rule.startswith("GP."):
            pattern = gameplay_patterns.get(rule)
            if pattern is None:
                result.error(f"unknown global gameplay pattern {rule}")
            elif pattern.get("classification") == "bakers_only":
                result.error(f"global rules illegally use Bakers-only pattern {rule}")

    for requirement in requirements:
        requirement_id = requirement.get("id", "<unknown>")
        referenced_wonder_destinations: list[dict[str, Any]] = []
        referenced_origin_yields: dict[str, float] = {}
        for reference in requirement.get("design_refs", []):
            resolved, design_value = resolve_design_ref(design, reference)
            if not resolved:
                result.error(f"{requirement_id}: unresolved design ref {reference}")
            else:
                used_design_ids.update(collect_design_ids(design_value))
                referenced_wonder_destinations.extend(
                    wonder_service_destinations(design_value)
                )
                for yield_type, amount in design_origin_yields(design_value).items():
                    referenced_origin_yields[yield_type] = (
                        referenced_origin_yields.get(yield_type, 0) + amount
                    )
        for pattern_id in requirement.get("gameplay_patterns", []):
            pattern = gameplay_patterns.get(pattern_id)
            if pattern is None:
                result.error(f"{requirement_id}: unknown gameplay pattern {pattern_id}")
            elif pattern.get("classification") == "bakers_only":
                result.error(f"{requirement_id}: illegally uses Bakers-only pattern {pattern_id}")
        if "GP.BUILDING.CUSTOMER_TRANSACTION" in requirement.get("gameplay_patterns", []):
            binding = requirement.get("implementation_binding") or {}
            if not binding.get("stacking_unit"):
                result.error(
                    f"{requirement_id}: customer transaction must declare implementation_binding.stacking_unit"
                )
            if str(requirement_id).startswith("I.STAGE3_"):
                if binding.get("transaction_registry") != "CSC_Stage3CustomerTransactions":
                    result.error(
                        f"{requirement_id}: Stage 3 customer transaction must use CSC_Stage3CustomerTransactions"
                    )
                if not binding.get("transaction_ids"):
                    result.error(
                        f"{requirement_id}: Stage 3 customer transaction must list its registry transaction IDs"
                    )
        for pattern_id in requirement.get("localization_patterns", []):
            if pattern_id not in localization_patterns:
                result.error(f"{requirement_id}: unknown localization pattern {pattern_id}")
        for output in requirement.get("outputs", []):
            if output not in output_keys:
                result.error(f"{requirement_id}: unknown planned output key {output}")
        validate_wonder_service_requirement(
            requirement,
            referenced_wonder_destinations,
            implementation,
            result,
        )
        validate_trade_route_yield_presentation_requirement(
            requirement,
            referenced_origin_yields,
            implementation,
            result,
        )

    validate_trade_route_yield_presentation_uniqueness(requirements, result)

    all_design_ids = collect_design_ids(design)
    uncovered = sorted(all_design_ids - used_design_ids)
    if uncovered:
        result.error("design IDs lack implementation coverage: " + ", ".join(uncovered))

    phase_ids = {phase.get("id") for phase in implementation.get("phases", [])}
    gate_ids = set(control.get("phase_gates", {}))
    if phase_ids != gate_ids:
        result.error(
            "phase gates do not match implementation phases; "
            f"missing={sorted(phase_ids - gate_ids)}, extra={sorted(gate_ids - phase_ids)}"
        )

    phase_validation = implementation.get("phase_validation", {})
    validation_phase_ids = set(phase_validation)
    if phase_ids != validation_phase_ids:
        result.error(
            "phase validation entries do not match implementation phases; "
            f"missing={sorted(phase_ids - validation_phase_ids)}, "
            f"extra={sorted(validation_phase_ids - phase_ids)}"
        )
    for phase in implementation.get("phases", []):
        phase_id = phase.get("id")
        validation_contract = phase_validation.get(phase_id, {})
        required_outputs = set(validation_contract.get("required_outputs", []))
        required_suites = set(validation_contract.get("required_suites", []))
        unknown_outputs = required_outputs - output_keys
        if unknown_outputs:
            result.error(
                f"{phase_id}: phase validation references unknown outputs "
                + ", ".join(sorted(unknown_outputs))
            )
        declared_outputs = {
            output
            for requirement in phase.get("requirements", [])
            for output in requirement.get("outputs", [])
        }
        missing_outputs = declared_outputs - required_outputs
        if missing_outputs:
            result.error(
                f"{phase_id}: phase validation omits requirement outputs "
                + ", ".join(sorted(missing_outputs))
            )
        minimum_suites = {"contract", "output_completeness", "semantic_rows"}
        if required_outputs & set(style_profiles):
            minimum_suites.update({"sql_style", "sql_statement_boundaries"})
        if "localization_generated" in required_outputs:
            minimum_suites.update(
                {"localization_generation", "localization_patterns"}
            )
        if required_outputs & set(implementation.get("build_wiring", {}).get("actions", {})):
            minimum_suites.add("modbuddy_wiring")
        if any(
            requirement.get("replacement_binding")
            for requirement in phase.get("requirements", [])
        ):
            minimum_suites.add("replacement_coverage")
        if any(
            any(pattern.startswith("GP.SERVICE.") for pattern in requirement.get("gameplay_patterns", []))
            for requirement in phase.get("requirements", [])
        ):
            minimum_suites.add("modifier_graph")
        if any(
            requirement.get("wonder_service_binding")
            for requirement in phase.get("requirements", [])
        ):
            minimum_suites.add("lua_contract")
        if any(
            requirement.get("trade_route_yield_presentation")
            for requirement in phase.get("requirements", [])
        ):
            minimum_suites.update({"lua_contract", "modifier_graph"})
        missing_suites = minimum_suites - required_suites
        if missing_suites:
            result.error(
                f"{phase_id}: phase validation omits required suites "
                + ", ".join(sorted(missing_suites))
            )
        assertion_module = ROOT / str(validation_contract.get("assertion_module", ""))
        if not assertion_module.is_file():
            result.error(f"{phase_id}: missing assertion module {assertion_module}")

    build_wiring = implementation.get("build_wiring", {})
    action_manifest = ROOT / str(build_wiring.get("action_manifest", ""))
    source_project = ROOT / str(build_wiring.get("source_project", ""))
    if not action_manifest.is_file():
        result.error(f"missing ModBuddy action manifest: {action_manifest}")
    if not source_project.is_file():
        result.error(f"missing ModBuddy source project: {source_project}")
    for output_key, action in build_wiring.get("actions", {}).items():
        if output_key not in output_keys:
            result.error(f"build wiring references unknown output {output_key}")
            continue
        planned = Path(str(implementation["planned_outputs"][output_key])).as_posix()
        expected_file = str(action.get("file", ""))
        project_prefix = "Civ Supply Chains/"
        planned_project_path = (
            planned[len(project_prefix):]
            if planned.startswith(project_prefix)
            else planned
        )
        if expected_file != planned_project_path:
            result.error(
                f"{output_key}: build-wiring file {expected_file!r} does not match "
                f"planned output {planned!r}"
            )

    open_decisions = implementation.get("open_engine_decisions", [])
    resolved_decisions = implementation.get("resolved_engine_decisions", [])
    open_decision_ids = [decision.get("id") for decision in open_decisions]
    resolved_decision_ids = [decision.get("id") for decision in resolved_decisions]
    all_decision_ids = open_decision_ids + resolved_decision_ids
    if len(all_decision_ids) != len(set(all_decision_ids)):
        result.error("engine decisions contain duplicate IDs across open/resolved lists")

    for decision in open_decisions + resolved_decisions:
        affected = decision.get("affects", [])
        if isinstance(affected, str):
            affected = [affected]
        for requirement_id in affected:
            if requirement_id not in requirement_ids:
                result.error(
                    f"{decision.get('id')}: unknown affected requirement {requirement_id}"
                )

    for decision in open_decisions:
        if decision.get("resolution_required_before_phase") not in phase_ids:
            result.error(f"{decision.get('id')}: unknown resolution phase")

    for decision in resolved_decisions:
        for evidence in decision.get("evidence", []):
            if not (ROOT / evidence).is_file():
                result.error(f"{decision.get('id')}: missing resolution evidence {evidence}")

    for preserved in implementation.get("preserved_inputs", []):
        pattern_id = preserved.get("pattern")
        if pattern_id not in gameplay_patterns:
            result.error(f"{preserved.get('id')}: unknown preserved-input pattern {pattern_id}")
        path = ROOT / str(preserved.get("file", ""))
        if not path.is_file():
            result.error(f"{preserved.get('id')}: missing preserved input file")
        elif not mapping_exists(path, preserved["resource"], preserved["class"]):
            result.error(
                f"{preserved.get('id')}: mapping {preserved['resource']} -> "
                f"{preserved['class']} not found in {preserved['file']}"
            )

    for output_key, profile in style_profiles.items():
        output_path = ROOT / implementation["planned_outputs"][output_key]
        if not output_path.exists():
            continue
        for failure in SQL_STYLE.validate_sql_style(
            output_path, profile, quarter, strict_whitespace=True
        ):
            result.error(f"{output_key} SQL style: {failure}")

    if check_clean_start:
        active_phases = {
            phase_id
            for phase_id, gate in control.get("phase_gates", {}).items()
            if gate.get("status") in ACTIVE_PHASE_STATUSES
        }
        if not active_phases:
            for key, relative_path in implementation.get("planned_outputs", {}).items():
                if (ROOT / relative_path).exists():
                    result.error(
                        f"clean-start violation: unapproved output {key} exists at {relative_path}"
                    )

    approvals = control.get("contract_approvals", {})
    for approval_id, approval in approvals.items():
        approval_path = ROOT / str(approval.get("path", ""))
        if not approval_path.is_file():
            result.error(f"{approval_id}: missing approval source {approval_path}")
            continue
        if approval.get("status") == "approved":
            if approval.get("sha256") != sha256(approval_path):
                result.error(f"{approval_id}: approved contract hash is stale")
    approved_exception_ids = {
        exception.get("id")
        for exception in control.get("exceptions", [])
        if exception.get("status") == "approved"
    }
    for phase_id, gate in control.get("phase_gates", {}).items():
        gate_status = gate.get("status")
        if gate_status not in ACTIVE_PHASE_STATUSES:
            continue
        if not gate.get("approved_by") or not gate.get("approved_at"):
            result.error(f"{phase_id}: active phase lacks explicit approval metadata")
        try:
            expected_design_hash = phase_design_sha256(design, implementation, phase_id)
        except ValueError as failure:
            result.error(str(failure))
        else:
            if gate.get("design_sha256") != expected_design_hash:
                result.error(f"{phase_id}: approved design-slice hash is stale")
        if gate_status in {"ready_for_review", "accepted"} and not gate.get("ready_at"):
            result.error(f"{phase_id}: {gate_status} phase lacks ready_at")
        if gate_status == "accepted" and (
            not gate.get("accepted_by") or not gate.get("accepted_at")
        ):
            result.error(f"{phase_id}: accepted phase lacks acceptance metadata")
        unresolved = [
            decision.get("id")
            for decision in open_decisions
            if decision.get("resolution_required_before_phase") == phase_id
            and decision.get("id") not in approved_exception_ids
        ]
        if unresolved:
            result.error(
                f"{phase_id}: phase approved with unresolved decisions {', '.join(unresolved)}"
            )

    if control.get("exceptions"):
        result.warn(f"{len(control['exceptions'])} approved/proposed exception(s) recorded")
    if open_decisions:
        result.warn(
            f"{len(open_decisions)} engine decision(s) remain open"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("quarter", nargs="?", default="tailors")
    parser.add_argument(
        "--no-clean-start-check",
        action="store_true",
        help="Do not require planned outputs to be absent before phase approval.",
    )
    args = parser.parse_args()

    result = validate_quarter(args.quarter, not args.no_clean_start_check)
    for warning in result.warnings:
        print(f"WARN: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.errors:
        print(f"FAIL: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        return 1
    print(f"PASS: {args.quarter} contracts ({len(result.warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
