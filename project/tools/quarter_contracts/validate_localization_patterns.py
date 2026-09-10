#!/usr/bin/env python3
"""Validate and deterministically render CSC localization pattern catalogs."""

from __future__ import annotations

import argparse
import json
import re
import string
import sys
from pathlib import Path
from typing import Any, Mapping

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[3]
SPEC_ROOT = ROOT / "project" / "specs"
DEFAULT_CATALOG = SPEC_ROOT / "reference" / "bakers-localization-patterns.yaml"
SCHEMA_PATH = SPEC_ROOT / "schema" / "localization-pattern-catalog.schema.json"


class PatternError(ValueError):
    """Raised when a pattern cannot be rendered deterministically."""


ENGINE_RENDERED_STATS_OMISSION_PATTERN = (
    "LP.BUILDING.ENGINE_RENDERED_STATS_OMITTED"
)
DEPRECATED_ENGINE_RENDERED_STAT_PATTERNS = {
    "LP.CITIZEN.BULLET",
    "LP.REGIONAL.BULLET",
}


def load_catalog(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle)
    if not isinstance(value, dict):
        raise PatternError(f"{path} must contain a YAML mapping")
    return value


def pattern_map(catalog: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(pattern.get("id")): pattern
        for pattern in catalog.get("patterns", [])
        if isinstance(pattern, dict)
    }


def template_slots(template: str) -> list[str]:
    slots: list[str] = []
    try:
        parsed = string.Formatter().parse(template)
        for _, field_name, format_spec, conversion in parsed:
            if field_name is None:
                continue
            if not field_name or "." in field_name or "[" in field_name:
                raise PatternError(f"unsupported template slot {field_name!r}")
            if format_spec or conversion:
                raise PatternError(
                    f"template slot {field_name!r} may not use conversion or formatting"
                )
            slots.append(field_name)
    except ValueError as failure:
        raise PatternError(f"invalid template: {failure}") from failure
    return slots


def validate_catalog(catalog: dict[str, Any], path: Path = DEFAULT_CATALOG) -> list[str]:
    failures: list[str] = []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(catalog), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.path) or "<root>"
        failures.append(f"{path.name} {location}: {error.message}")

    patterns = [item for item in catalog.get("patterns", []) if isinstance(item, dict)]
    identifiers = [str(pattern.get("id")) for pattern in patterns]
    if len(identifiers) != len(set(identifiers)):
        failures.append("localization catalog contains duplicate pattern IDs")
    if ENGINE_RENDERED_STATS_OMISSION_PATTERN not in identifiers:
        failures.append(
            "localization catalog must declare the structural engine-rendered "
            "building-stat omission pattern"
        )
    for deprecated in sorted(DEPRECATED_ENGINE_RENDERED_STAT_PATTERNS):
        if deprecated in identifiers:
            failures.append(
                f"{deprecated}: authored building descriptions must not template "
                "engine-rendered building stats"
            )

    order = catalog.get("building_description_order", [])
    for pattern in patterns:
        pattern_id = str(pattern.get("id", "<unknown>"))
        template = pattern.get("template")
        if isinstance(template, str):
            try:
                actual_slots = list(dict.fromkeys(template_slots(template)))
            except PatternError as failure:
                failures.append(f"{pattern_id}: {failure}")
                continue
            required_slots = pattern.get("required_slots", [])
            if actual_slots != required_slots:
                failures.append(
                    f"{pattern_id}: template slots {actual_slots!r} do not exactly match "
                    f"required_slots {required_slots!r}"
                )
        order_group = pattern.get("order_group")
        if order_group is not None and order_group not in order:
            failures.append(
                f"{pattern_id}: unknown building description order group {order_group}"
            )

    reference = ROOT / str(catalog.get("reference_file", ""))
    reference_text = ""
    if not reference.is_file():
        failures.append(f"missing localization reference file: {reference}")
    else:
        reference_text = reference.read_text(encoding="utf-8")
    if reference_text:
        for pattern in patterns:
            anchor = pattern.get("source_anchor")
            if anchor and f"## {anchor}" not in reference_text:
                failures.append(
                    f"{pattern.get('id', '<unknown>')}: source anchor {anchor} "
                    f"does not exist in {catalog.get('reference_file')}"
                )
    return failures


def _compact(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_match_text(text: str) -> str:
    normalized = text.replace("[NEWLINE]", "\n")
    normalized = re.sub(r"(?m)^\s*[-*]\s+", "* ", normalized)
    return _compact(normalized)


def render_pattern(
    catalog: Mapping[str, Any],
    pattern_id: str,
    slots: Mapping[str, Any],
    *,
    bullet_marker: str = "*",
) -> str:
    patterns = pattern_map(catalog)
    pattern = patterns.get(pattern_id)
    if pattern is None:
        raise PatternError(f"unknown localization pattern {pattern_id}")
    template = pattern.get("template")
    if not isinstance(template, str):
        raise PatternError(f"{pattern_id} is structural and cannot be rendered")

    required = list(pattern.get("required_slots", []))
    supplied = set(slots)
    missing = [slot for slot in required if slot not in supplied]
    extra = sorted(supplied - set(required))
    if missing:
        raise PatternError(f"{pattern_id} missing slots: {', '.join(missing)}")
    if extra:
        raise PatternError(f"{pattern_id} extra slots: {', '.join(extra)}")
    if any(slots[slot] is None for slot in required):
        empty = [slot for slot in required if slots[slot] is None]
        raise PatternError(f"{pattern_id} null slots: {', '.join(empty)}")
    if bullet_marker not in {"*", "-"}:
        raise PatternError("bullet marker must be '*' or '-'")

    rendered = _compact(template).format(**{key: str(value) for key, value in slots.items()})
    if rendered.startswith("* "):
        rendered = bullet_marker + rendered[1:]
    return rendered


def pattern_matches(
    catalog: Mapping[str, Any],
    pattern_id: str,
    slots: Mapping[str, Any],
    actual: str,
) -> bool:
    expected = render_pattern(catalog, pattern_id, slots)
    return normalize_match_text(expected) == normalize_match_text(actual)


def source_contains_exact_text(source: str, rendered: str) -> bool:
    return normalize_match_text(rendered) in normalize_match_text(source)


def validate_engine_rendered_building_stats_omitted(description: str) -> list[str]:
    """Reject owning-building stats that Civ VI adds below authored descriptions."""
    failures: list[str] = []
    lines = description.replace("[NEWLINE]", "\n").splitlines()
    for line in lines:
        if re.search(r"\[ICON_Citizen\]\s+Citizen slots?", line, re.IGNORECASE):
            failures.append("authored description repeats an engine-rendered Citizen slot")
        if re.search(
            r"\[ICON_Citizen\]\s+Citizens?\s+in\s+(?:the\s+)?(?:Quarter|district)",
            line,
            re.IGNORECASE,
        ):
            failures.append(
                "authored description repeats engine-rendered specialist yields"
            )
        if re.search(
            r"^\s*[-*]\s*\+\d+(?:\.\d+)?\s+\[ICON_Amenities\]\s+Amenit(?:y|ies)\b",
            line,
            re.IGNORECASE,
        ):
            failures.append(
                "authored description repeats an engine-rendered intrinsic Amenity"
            )
    return failures


def validate_description_order(
    catalog: Mapping[str, Any], pattern_ids: list[str]
) -> list[str]:
    failures: list[str] = []
    patterns = pattern_map(catalog)
    order = list(catalog.get("building_description_order", []))
    positions = {group: index for index, group in enumerate(order)}
    previous_position = -1
    previous_group: str | None = None
    for pattern_id in pattern_ids:
        pattern = patterns.get(pattern_id)
        if pattern is None:
            failures.append(f"unknown localization pattern {pattern_id}")
            continue
        group = pattern.get("order_group")
        if group is None:
            continue
        position = positions.get(group)
        if position is None:
            failures.append(f"{pattern_id}: unknown order group {group}")
            continue
        if position < previous_position:
            failures.append(
                f"{pattern_id}: {group} appears after {previous_group}; expected order is "
                + " -> ".join(order)
            )
        else:
            previous_position = position
            previous_group = str(group)
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("catalog", nargs="?", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--render", metavar="PATTERN_ID")
    parser.add_argument(
        "--slots-json",
        default="{}",
        help="JSON object containing exact values for every required template slot",
    )
    parser.add_argument(
        "--slot",
        action="append",
        default=[],
        metavar="NAME=VALUE",
        help="supply one template slot; may be repeated and overrides --slots-json",
    )
    parser.add_argument("--bullet-marker", choices=["*", "-"], default="*")
    args = parser.parse_args(argv)

    try:
        catalog = load_catalog(args.catalog.resolve())
        failures = validate_catalog(catalog, args.catalog)
        if failures:
            for failure in failures:
                print(f"ERROR: {failure}")
            print(f"FAIL: {len(failures)} localization pattern error(s)")
            return 1
        if args.render:
            slots = json.loads(args.slots_json)
            if not isinstance(slots, dict):
                raise PatternError("--slots-json must contain a JSON object")
            for assignment in args.slot:
                if "=" not in assignment:
                    raise PatternError("--slot values must use NAME=VALUE")
                name, value = assignment.split("=", 1)
                if not name:
                    raise PatternError("--slot names may not be empty")
                slots[name] = value
            print(
                render_pattern(
                    catalog,
                    args.render,
                    slots,
                    bullet_marker=args.bullet_marker,
                )
            )
        else:
            print(f"PASS: localization pattern catalog ({len(catalog['patterns'])} patterns)")
        return 0
    except (OSError, PatternError, json.JSONDecodeError, yaml.YAMLError) as failure:
        print(f"ERROR: {failure}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
