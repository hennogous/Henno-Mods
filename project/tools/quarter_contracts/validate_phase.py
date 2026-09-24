#!/usr/bin/env python3
"""Validate an approved CSC Quarter implementation phase before handoff."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
SPEC_ROOT = ROOT / "project" / "specs"
ACTIVE_PHASE_STATUSES = {"approved", "implementing", "ready_for_review", "accepted"}
HANDOFF_PHASE_STATUSES = {"ready_for_review", "accepted"}

CONTRACT_SPEC = importlib.util.spec_from_file_location(
    "csc_validate_quarter", Path(__file__).with_name("validate_quarter.py")
)
assert CONTRACT_SPEC and CONTRACT_SPEC.loader
CONTRACTS = importlib.util.module_from_spec(CONTRACT_SPEC)
CONTRACT_SPEC.loader.exec_module(CONTRACTS)


class PhaseValidation:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def phase_by_id(implementation: dict[str, Any], phase_id: str) -> dict[str, Any] | None:
    return next(
        (phase for phase in implementation.get("phases", []) if phase.get("id") == phase_id),
        None,
    )


def phase_required_outputs(
    implementation: dict[str, Any], phase_id: str
) -> set[str]:
    validation = implementation.get("phase_validation", {}).get(phase_id, {})
    return set(validation.get("required_outputs", []))


def validate_statement_boundaries(path: Path) -> list[str]:
    sql = path.read_text(encoding="utf-8-sig")
    failures: list[str] = []
    if not sql.strip():
        return ["file is empty"]
    if not sqlite3.complete_statement(sql):
        failures.append("SQL does not end on a complete SQLite statement boundary")
    return failures


def action_file_paths(action: dict[str, Any]) -> list[str]:
    if action.get("type") == "ReplaceUIScript":
        replacement = action.get("properties", {}).get("LuaReplace")
        return [str(replacement)] if replacement else []
    paths: list[str] = []
    for entry in action.get("files", []):
        paths.append(entry if isinstance(entry, str) else str(entry.get("path", "")))
    return paths


def validate_action_wiring(
    actions_document: dict[str, Any],
    wiring: dict[str, Any],
    required_outputs: set[str],
) -> list[str]:
    failures: list[str] = []
    actions = actions_document.get("blocks", {}).get("inGameActions", [])
    for output_key, expected in wiring.get("actions", {}).items():
        if output_key not in required_outputs:
            continue
        matches = [action for action in actions if action.get("id") == expected.get("id")]
        if len(matches) != 1:
            failures.append(
                f"{output_key}: expected exactly one action {expected.get('id')}, found {len(matches)}"
            )
            continue
        actual = matches[0]
        if actual.get("type") != expected.get("type"):
            failures.append(
                f"{output_key}: action type is {actual.get('type')}, expected {expected.get('type')}"
            )
        if action_file_paths(actual) != [expected.get("file")]:
            failures.append(
                f"{output_key}: action files are {action_file_paths(actual)}, expected {[expected.get('file')]}"
            )
        if expected.get("type") == "ReplaceUIScript":
            actual_context = actual.get("properties", {}).get("LuaContext")
            if actual_context != expected.get("lua_context"):
                failures.append(
                    f"{output_key}: LuaContext is {actual_context!r}, "
                    f"expected {expected.get('lua_context')!r}"
                )
        actual_load_order = str(actual.get("properties", {}).get("LoadOrder", ""))
        if actual_load_order != str(expected.get("load_order")):
            failures.append(
                f"{output_key}: LoadOrder is {actual_load_order!r}, expected {expected.get('load_order')!r}"
            )
        if actual.get("criteria", []) != expected.get("criteria", []):
            failures.append(
                f"{output_key}: criteria are {actual.get('criteria', [])}, expected {expected.get('criteria', [])}"
            )
    return failures


def validate_action_criteria_wiring(
    actions_document: dict[str, Any],
    wiring: dict[str, Any],
    required_outputs: set[str],
) -> list[str]:
    failures: list[str] = []
    required_criteria = {
        criterion
        for output_key, action in wiring.get("actions", {}).items()
        if output_key in required_outputs
        for criterion in action.get("criteria", [])
    }
    contracts = wiring.get("criteria_contracts", {})
    criteria_nodes = actions_document.get("blocks", {}).get("actionCriteria", [])
    for criterion_id in sorted(required_criteria & set(contracts)):
        expected = contracts[criterion_id]
        matches = [
            node
            for node in criteria_nodes
            if node.get("tag") == "Criteria"
            and node.get("attributes", {}).get("id") == criterion_id
        ]
        if len(matches) != 1:
            failures.append(
                f"{criterion_id}: expected exactly one ActionCriteria definition, found {len(matches)}"
            )
            continue
        children = matches[0].get("children", [])
        kind_matches = [child for child in children if child.get("tag") == expected.get("kind")]
        if len(kind_matches) != 1:
            failures.append(
                f"{criterion_id}: expected exactly one {expected.get('kind')} condition"
            )
            continue
        condition = kind_matches[0]
        if condition.get("text") != expected.get("value"):
            failures.append(
                f"{criterion_id}: condition value is {condition.get('text')!r}, "
                f"expected {expected.get('value')!r}"
            )
        actual_inverse = condition.get("attributes", {}).get("inverse") == "1"
        if actual_inverse != expected.get("inverse"):
            failures.append(
                f"{criterion_id}: inverse is {actual_inverse}, expected {expected.get('inverse')}"
            )
    return failures


def content_includes(project_path: Path) -> set[str]:
    text = project_path.read_text(encoding="utf-8-sig")
    return {
        match.replace("\\", "/")
        for match in re.findall(r'<Content\s+Include="([^"]+)"', text)
    }


def validate_content_wiring(
    project_path: Path,
    wiring: dict[str, Any],
    required_outputs: set[str],
) -> list[str]:
    included = content_includes(project_path)
    failures: list[str] = []
    for output_key, expected in wiring.get("actions", {}).items():
        if output_key not in required_outputs:
            continue
        expected_file = str(expected.get("file", ""))
        if expected_file not in included:
            failures.append(
                f"{output_key}: {expected_file} is not registered as Content in {project_path}"
            )
    return failures


def run_checked_command(command: list[str], label: str, result: PhaseValidation) -> None:
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode:
        detail = (completed.stdout + completed.stderr).strip()
        result.error(f"{label} failed" + (f": {detail}" if detail else ""))


def run_assertion_module(
    module_path: Path,
    quarter: str,
    phase_id: str,
    implementation: dict[str, Any],
    result: PhaseValidation,
) -> None:
    if not module_path.is_file():
        result.error(f"missing phase assertion module: {module_path}")
        return
    spec = importlib.util.spec_from_file_location(
        f"csc_{quarter}_phase_assertions", module_path
    )
    if spec is None or spec.loader is None:
        result.error(f"cannot load phase assertion module: {module_path}")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    validator = getattr(module, "validate_phase_assertions", None)
    if not callable(validator):
        result.error(
            f"{module_path}: expected callable validate_phase_assertions"
        )
        return
    failures = validator(ROOT, phase_id, implementation)
    if not isinstance(failures, list) or not all(
        isinstance(failure, str) for failure in failures
    ):
        result.error(f"{module_path}: assertion validator must return list[str]")
        return
    for failure in failures:
        result.error(f"phase assertion: {failure}")


def validate_phase(
    quarter: str,
    phase_id: str,
    *,
    handoff: bool = False,
    run_commands: bool = True,
) -> PhaseValidation:
    result = PhaseValidation()
    contract_result = CONTRACTS.validate_quarter(quarter, check_clean_start=False)
    result.errors.extend(f"contract: {error}" for error in contract_result.errors)
    result.warnings.extend(f"contract: {warning}" for warning in contract_result.warnings)

    quarter_dir = SPEC_ROOT / quarter
    try:
        implementation = CONTRACTS.load_yaml(quarter_dir / "implementation.yaml")
        control = CONTRACTS.load_yaml(quarter_dir / "control.yaml")
    except (OSError, ValueError, yaml.YAMLError) as failure:
        result.error(str(failure))
        return result

    phase = phase_by_id(implementation, phase_id)
    if phase is None:
        result.error(f"unknown phase {phase_id}")
        return result
    gate = control.get("phase_gates", {}).get(phase_id, {})
    gate_status = gate.get("status")
    allowed = HANDOFF_PHASE_STATUSES if handoff else ACTIVE_PHASE_STATUSES
    if gate_status not in allowed:
        result.error(
            f"{phase_id}: gate status {gate_status!r} is not valid for "
            + ("handoff" if handoff else "implementation validation")
        )

    phase_validation = implementation.get("phase_validation", {}).get(phase_id)
    if not isinstance(phase_validation, dict):
        result.error(f"{phase_id}: missing phase_validation contract")
        return result
    required_outputs = phase_required_outputs(implementation, phase_id)
    known_outputs = implementation.get("planned_outputs", {})
    for output_key in sorted(required_outputs):
        relative_path = known_outputs.get(output_key)
        if relative_path is None:
            result.error(f"{phase_id}: unknown required output {output_key}")
            continue
        path = ROOT / relative_path
        if not path.is_file():
            result.error(f"{phase_id}: missing required output {output_key}: {relative_path}")
            continue
        if output_key in implementation.get("sql_style_profiles", {}):
            profile = implementation["sql_style_profiles"][output_key]
            for failure in CONTRACTS.SQL_STYLE.validate_sql_style(
                path, profile, quarter, strict_whitespace=True
            ):
                result.error(f"{output_key} SQL style: {failure}")
            for failure in validate_statement_boundaries(path):
                result.error(f"{output_key} SQL syntax: {failure}")

    assertion_module = ROOT / str(phase_validation.get("assertion_module", ""))
    run_assertion_module(
        assertion_module, quarter, phase_id, implementation, result
    )

    wiring = implementation.get("build_wiring", {})
    try:
        action_manifest = ROOT / wiring["action_manifest"]
        project_path = ROOT / wiring["source_project"]
        actions_document = load_json(action_manifest)
        for failure in validate_action_wiring(actions_document, wiring, required_outputs):
            result.error(f"ModBuddy action: {failure}")
        for failure in validate_action_criteria_wiring(
            actions_document, wiring, required_outputs
        ):
            result.error(f"ModBuddy criterion: {failure}")
        for failure in validate_content_wiring(project_path, wiring, required_outputs):
            result.error(f"ModBuddy Content: {failure}")
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as failure:
        result.error(f"ModBuddy wiring: {failure}")

    if run_commands and required_outputs:
        if "localization_generated" in required_outputs:
            run_checked_command(
                [
                    sys.executable,
                    str(ROOT / "project/tools/localization/loc_md_to_sql.py"),
                    "--check",
                ],
                "localization generation check",
                result,
            )
        if wiring:
            run_checked_command(
                [
                    sys.executable,
                    str(ROOT / "project/tools/modbuddy/civ6proj_actions.py"),
                    "check",
                    "--project",
                    str(ROOT / wiring["source_project"]),
                    "--json",
                    str(ROOT / wiring["action_manifest"]),
                ],
                "ModBuddy action round-trip check",
                result,
            )

    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quarter")
    parser.add_argument("phase")
    parser.add_argument(
        "--handoff",
        action="store_true",
        help="Require the phase gate to be ready_for_review or accepted.",
    )
    parser.add_argument(
        "--no-command-checks",
        action="store_true",
        help="Skip localization-generator and ModBuddy round-trip subprocess checks.",
    )
    args = parser.parse_args(argv)
    result = validate_phase(
        args.quarter,
        args.phase,
        handoff=args.handoff,
        run_commands=not args.no_command_checks,
    )
    for warning in result.warnings:
        print(f"WARN: {warning}")
    for error in result.errors:
        print(f"ERROR: {error}")
    if result.errors:
        print(f"FAIL: {len(result.errors)} error(s), {len(result.warnings)} warning(s)")
        return 1
    print(f"PASS: {args.quarter}/{args.phase} ({len(result.warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
