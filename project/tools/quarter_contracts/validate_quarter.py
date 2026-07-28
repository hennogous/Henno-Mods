#!/usr/bin/env python3
"""Validate CSC Quarter contracts and their locked/preserved inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema
import yaml


ROOT = Path(__file__).resolve().parents[3]
SPEC_ROOT = ROOT / "project" / "specs"


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
    validator = jsonschema.Draft202012Validator(schema)
    for failure in sorted(validator.iter_errors(instance), key=lambda error: list(error.path)):
        location = ".".join(str(part) for part in failure.path) or "<root>"
        result.error(f"{schema_name} {location}: {failure.message}")


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
    except (OSError, KeyError, ValueError, yaml.YAMLError) as failure:
        result.error(str(failure))
        return result

    validate_schema(design, "quarter-design.schema.json", result)
    validate_schema(implementation, "quarter-implementation.schema.json", result)
    validate_schema(control, "quarter-control.schema.json", result)

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
        for reference in requirement.get("design_refs", []):
            resolved, design_value = resolve_design_ref(design, reference)
            if not resolved:
                result.error(f"{requirement_id}: unresolved design ref {reference}")
            else:
                used_design_ids.update(collect_design_ids(design_value))
        for pattern_id in requirement.get("gameplay_patterns", []):
            pattern = gameplay_patterns.get(pattern_id)
            if pattern is None:
                result.error(f"{requirement_id}: unknown gameplay pattern {pattern_id}")
            elif pattern.get("classification") == "bakers_only":
                result.error(f"{requirement_id}: illegally uses Bakers-only pattern {pattern_id}")
        for pattern_id in requirement.get("localization_patterns", []):
            if pattern_id not in localization_patterns:
                result.error(f"{requirement_id}: unknown localization pattern {pattern_id}")
        for output in requirement.get("outputs", []):
            if output not in output_keys:
                result.error(f"{requirement_id}: unknown planned output key {output}")

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

    for decision in implementation.get("open_engine_decisions", []):
        affected = decision.get("affects", [])
        if isinstance(affected, str):
            affected = [affected]
        for requirement_id in affected:
            if requirement_id not in requirement_ids:
                result.error(
                    f"{decision.get('id')}: unknown affected requirement {requirement_id}"
                )
        if decision.get("resolution_required_before_phase") not in phase_ids:
            result.error(f"{decision.get('id')}: unknown resolution phase")

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

    if check_clean_start:
        approved_phases = {
            phase_id
            for phase_id, gate in control.get("phase_gates", {}).items()
            if gate.get("status") == "approved"
        }
        if not approved_phases:
            for key, relative_path in implementation.get("planned_outputs", {}).items():
                if (ROOT / relative_path).exists():
                    result.error(
                        f"clean-start violation: unapproved output {key} exists at {relative_path}"
                    )

    approvals = control.get("contract_approvals", {})
    all_contracts_approved = bool(approvals) and all(
        approval.get("status") == "approved" for approval in approvals.values()
    )
    approved_exception_ids = {
        exception.get("id")
        for exception in control.get("exceptions", [])
        if exception.get("status") == "approved"
    }
    for phase_id, gate in control.get("phase_gates", {}).items():
        if gate.get("status") != "approved":
            continue
        if not all_contracts_approved:
            result.error(f"{phase_id}: phase approved before all contracts")
        unresolved = [
            decision.get("id")
            for decision in implementation.get("open_engine_decisions", [])
            if decision.get("resolution_required_before_phase") == phase_id
            and decision.get("id") not in approved_exception_ids
        ]
        if unresolved:
            result.error(
                f"{phase_id}: phase approved with unresolved decisions {', '.join(unresolved)}"
            )

    if control.get("exceptions"):
        result.warn(f"{len(control['exceptions'])} approved/proposed exception(s) recorded")
    if implementation.get("open_engine_decisions"):
        result.warn(
            f"{len(implementation['open_engine_decisions'])} engine decision(s) remain open"
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
