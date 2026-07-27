#!/usr/bin/env python3
"""Validate CSC Quarter authority, applicability, traceability, and source gates."""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - exercised by installation errors
    yaml = None


CLASSIFICATIONS = {
    "invariant",
    "parameterized",
    "conditional",
    "quarter_specific",
    "shared",
    "not_applicable",
    "superseded",
}
TRACE_STATUSES = {"mapped", "implemented", "runtime_pending", "tested", "conflict"}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: int = 0

    def check(self, condition: bool, message: str) -> bool:
        self.checks += 1
        if not condition:
            self.errors.append(message)
        return condition

    def warn(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.warnings.append(message)


def read_json(path: Path, report: Report) -> dict[str, Any]:
    if not report.check(path.is_file(), f"Missing JSON contract: {path.as_posix()}"):
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.errors.append(f"Cannot parse {path.as_posix()}: {exc}")
        return {}


def read_yaml(path: Path, report: Report) -> dict[str, Any]:
    if yaml is None:
        report.errors.append("PyYAML is required: py -3 -m pip install PyYAML")
        return {}
    if not report.check(path.is_file(), f"Missing YAML contract: {path.as_posix()}"):
        return {}
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("top level must be a mapping")
        return value
    except (OSError, ValueError, yaml.YAMLError) as exc:
        report.errors.append(f"Cannot parse {path.as_posix()}: {exc}")
        return {}


def repo_path(root: Path, value: str) -> Path:
    return root / Path(value)


def posix(value: str | Path) -> str:
    return str(value).replace("\\", "/")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_dot_path(document: Any, dotted: str) -> tuple[bool, Any]:
    current = document
    for segment in dotted.split("."):
        if isinstance(current, dict) and segment in current:
            current = current[segment]
        elif isinstance(current, list) and segment.isdigit():
            index = int(segment)
            if index >= len(current):
                return False, None
            current = current[index]
        else:
            return False, None
    return True, current


def markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## ") and not line.startswith("### "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def matches_any(path: str, patterns: list[str]) -> bool:
    normalized = posix(path)
    return any(fnmatch.fnmatchcase(normalized, posix(pattern)) for pattern in patterns)


def validate_output_scope(
    output_path: str,
    phase: dict[str, Any],
    report: Report,
    requirement_id: str,
) -> None:
    allowed = list(phase.get("allowed_files", [])) + list(phase.get("allowed_with_art_phase", []))
    forbidden = list(phase.get("forbidden_files", []))
    report.check(
        matches_any(output_path, allowed),
        f"{requirement_id}: output is outside phase allowlist: {output_path}",
    )
    report.check(
        not matches_any(output_path, forbidden),
        f"{requirement_id}: output matches phase denylist: {output_path}",
    )


def validate_source_assertions(
    root: Path,
    requirement: dict[str, Any],
    report: Report,
) -> None:
    requirement_id = requirement.get("id", "<missing-id>")
    for output in requirement.get("outputs", []):
        path_value = output.get("path", "")
        path = repo_path(root, path_value)
        if not report.check(path.is_file(), f"{requirement_id}: missing output: {path_value}"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for literal in output.get("contains", []):
            report.check(
                literal in text,
                f"{requirement_id}: {path_value} does not contain {literal!r}",
            )
        for literal in output.get("not_contains", []):
            report.check(
                literal not in text,
                f"{requirement_id}: {path_value} unexpectedly contains {literal!r}",
            )

    for assertion in requirement.get("localization", []):
        path_value = assertion.get("path", "")
        path = repo_path(root, path_value)
        if not report.check(path.is_file(), f"{requirement_id}: missing localization source: {path_value}"):
            continue
        sections = markdown_sections(path.read_text(encoding="utf-8", errors="replace"))
        key = assertion.get("key", "")
        if not report.check(key in sections, f"{requirement_id}: missing localization key {key}"):
            continue
        body = sections[key]
        for literal in assertion.get("contains", []):
            report.check(
                literal in body,
                f"{requirement_id}: {key} does not contain {literal!r}",
            )
        cursor = -1
        for literal in assertion.get("ordered_contains", []):
            location = body.find(literal, cursor + 1)
            report.check(
                location >= 0,
                f"{requirement_id}: {key} is missing ordered fragment {literal!r}",
            )
            if location >= 0:
                report.check(
                    location > cursor,
                    f"{requirement_id}: {key} has fragment out of order: {literal!r}",
                )
                cursor = location


def run_generated_checks(root: Path, report: Report) -> None:
    commands = [
        [sys.executable, "project/tools/localization/loc_md_to_sql.py", "--check"],
        [sys.executable, "project/tools/modbuddy/civ6proj_actions.py", "check"],
    ]
    for command in commands:
        completed = subprocess.run(
            command,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        report.check(
            completed.returncode == 0,
            f"Generated-file check failed ({' '.join(command[1:])}):\n{completed.stdout.strip()}",
        )


def validate(  # noqa: PLR0915 - one orchestrator keeps error reporting coherent
    root: Path,
    quarter_slug: str,
    phase_name: str | None,
    ready: bool,
    generated: bool,
) -> Report:
    report = Report()
    spec_dir = root / "project" / "specs" / quarter_slug
    control_path = spec_dir / f"{quarter_slug}-implementation-control.json"
    control = read_json(control_path, report)
    if not control:
        return report
    report.check(
        control.get("schema") == "csc-quarter-implementation-control",
        "Unexpected implementation-control schema",
    )
    report.check(control.get("schema_version") == 1, "Unsupported implementation-control schema version")
    report.check(control.get("review_status") in {"draft", "approved", "superseded"}, "Invalid review_status")
    report.check(
        control.get("conflict_policy") == "stop_and_request_henno_decision",
        "Conflict policy must stop and request Henno's decision",
    )

    authority = control.get("authority", {})
    required_authority = {
        "design_doc",
        "design_spec",
        "gameplay_contract",
        "art_contract",
        "localization_source",
        "localization_patterns",
        "applicability_manifest",
        "traceability_manifest",
    }
    for key in sorted(required_authority):
        value = authority.get(key)
        report.check(isinstance(value, str) and bool(value), f"Control authority is missing {key}")
        if isinstance(value, str) and value:
            report.check(repo_path(root, value).is_file(), f"Authority path does not exist: {value}")

    design = read_yaml(repo_path(root, authority.get("design_spec", "")), report)
    gameplay = read_yaml(repo_path(root, authority.get("gameplay_contract", "")), report)
    art = read_yaml(repo_path(root, authority.get("art_contract", "")), report)
    applicability = read_json(repo_path(root, authority.get("applicability_manifest", "")), report)
    traceability = read_json(repo_path(root, authority.get("traceability_manifest", "")), report)
    loc_patterns = read_json(repo_path(root, authority.get("localization_patterns", "")), report)

    quarter_key = control.get("quarter_key")
    report.check(quarter_key == quarter_slug.upper(), "Control quarter_key does not match directory slug")
    identities = {
        "design": design.get("metadata", {}).get("quarter_key"),
        "gameplay": gameplay.get("metadata", {}).get("quarter_key"),
        "art": art.get("metadata", {}).get("quarter_key"),
        "applicability": applicability.get("quarter_key"),
        "traceability": traceability.get("quarter_key"),
    }
    for label, value in identities.items():
        report.check(value == quarter_key, f"{label} quarter identity {value!r} does not match {quarter_key!r}")

    expected_design_path = authority.get("design_spec")
    report.check(
        gameplay.get("design_spec") == expected_design_path,
        "Gameplay design_spec does not match the control authority path",
    )
    report.check(
        art.get("design_spec") == expected_design_path,
        "Art design_spec does not match the control authority path",
    )
    report.check(
        design.get("metadata", {}).get("design_doc") == authority.get("design_doc"),
        "Design metadata.design_doc does not match the control authority path",
    )

    lock_files: dict[str, dict[str, Any]] = {}
    for item in control.get("reference_lock", {}).get("files", []):
        path_value = item.get("path", "")
        report.check(path_value not in lock_files, f"Duplicate reference lock path: {path_value}")
        lock_files[path_value] = item
        path = repo_path(root, path_value)
        if report.check(path.is_file(), f"Pinned reference does not exist: {path_value}"):
            report.check(
                sha256(path) == item.get("sha256"),
                f"Pinned reference drifted: {path_value}",
            )
    report.check(bool(lock_files), "Reference lock contains no files")
    pinned_commit = control.get("reference_lock", {}).get("commit", "")
    commit_check = subprocess.run(
        ["git", "cat-file", "-e", f"{pinned_commit}^{{commit}}"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    report.check(bool(pinned_commit) and commit_check.returncode == 0, "Pinned reference commit is not available in Git")
    for source_reference in gameplay.get("metadata", {}).get("source_reference_sql", []):
        report.check(
            source_reference in lock_files,
            f"Gameplay source reference is not pinned: {source_reference}",
        )

    applicability_ids: set[str] = set()
    for entry in applicability.get("entries", []):
        entry_id = entry.get("id", "")
        report.check(bool(entry_id), "Applicability entry has no id")
        report.check(entry_id not in applicability_ids, f"Duplicate applicability id: {entry_id}")
        applicability_ids.add(entry_id)
        classification = entry.get("classification")
        report.check(
            classification in CLASSIFICATIONS,
            f"{entry_id}: invalid classification {classification!r}",
        )
        source_file = entry.get("source_file", "")
        report.check(
            source_file in lock_files,
            f"{entry_id}: source file is not in the pinned reference lock: {source_file}",
        )
        source_path = repo_path(root, source_file)
        if source_path.is_file():
            source_text = source_path.read_text(encoding="utf-8", errors="replace")
            anchor = entry.get("source_anchor", "")
            report.check(bool(anchor) and anchor in source_text, f"{entry_id}: missing source anchor {anchor!r}")
        report.check(bool(entry.get("rationale")), f"{entry_id}: missing rationale")

    reference_source = loc_patterns.get("reference_source", "")
    report.check(reference_source in lock_files, "Localization reference is not pinned")
    reference_sections: dict[str, str] = {}
    reference_path = repo_path(root, reference_source)
    if reference_path.is_file():
        reference_sections = markdown_sections(reference_path.read_text(encoding="utf-8", errors="replace"))
    loc_pattern_ids: set[str] = set()
    for pattern in loc_patterns.get("patterns", []):
        pattern_id = pattern.get("id", "")
        report.check(bool(pattern_id) and pattern_id not in loc_pattern_ids, f"Duplicate/empty localization pattern id: {pattern_id}")
        loc_pattern_ids.add(pattern_id)
        reference_key = pattern.get("reference_key", "")
        report.check(reference_key in reference_sections, f"{pattern_id}: missing Bakers LOC key {reference_key}")
        literal = pattern.get("required_literal")
        if literal and reference_key in reference_sections:
            report.check(literal in reference_sections[reference_key], f"{pattern_id}: required literal absent from Bakers reference")

    phase_contracts = gameplay.get("phase_contracts", {})
    selected_phase_name = phase_name or traceability.get("phase")
    selected_phase = phase_contracts.get(selected_phase_name, {})
    report.check(bool(selected_phase), f"Gameplay contract has no phase {selected_phase_name!r}")
    report.check(
        traceability.get("phase") in phase_contracts,
        f"Traceability phase {traceability.get('phase')!r} is absent from gameplay contract",
    )
    report.check(
        applicability.get("phase") == traceability.get("phase"),
        "Applicability and traceability phases do not match",
    )
    if selected_phase:
        overlap = set(selected_phase.get("allowed_files", [])) & set(selected_phase.get("forbidden_files", []))
        report.check(not overlap, f"Phase has exact allow/deny overlap: {sorted(overlap)}")

    trace_ids: set[str] = set()
    for requirement in traceability.get("requirements", []):
        requirement_id = requirement.get("id", "")
        report.check(bool(requirement_id), "Traceability row has no id")
        report.check(requirement_id not in trace_ids, f"Duplicate traceability id: {requirement_id}")
        trace_ids.add(requirement_id)
        report.check(
            requirement.get("status") in TRACE_STATUSES,
            f"{requirement_id}: invalid status {requirement.get('status')!r}",
        )
        for design_ref in requirement.get("design_refs", []):
            resolved, _ = resolve_dot_path(design, design_ref)
            report.check(resolved, f"{requirement_id}: unresolved design path {design_ref}")
        report.check(bool(requirement.get("design_refs")), f"{requirement_id}: no design references")
        for pattern_id in requirement.get("bakers_patterns", []):
            report.check(pattern_id in applicability_ids, f"{requirement_id}: unknown Bakers pattern {pattern_id}")
        report.check(bool(requirement.get("bakers_patterns")), f"{requirement_id}: no Bakers patterns")
        outputs = requirement.get("outputs", [])
        report.check(bool(outputs), f"{requirement_id}: no declared outputs")
        phase_for_row = phase_contracts.get(traceability.get("phase"), {})
        for output in outputs:
            validate_output_scope(output.get("path", ""), phase_for_row, report, requirement_id)
        report.check(bool(requirement.get("static_checks")), f"{requirement_id}: no static checks")
        report.check(bool(requirement.get("runtime_checks")), f"{requirement_id}: no runtime checks")
        if phase_name and traceability.get("phase") == phase_name:
            validate_source_assertions(root, requirement, report)

    if ready:
        report.check(control.get("review_status") == "approved", "Readiness blocked: review_status is not approved")
        report.check(control.get("implementation_ready") is True, "Readiness blocked: implementation_ready is not true")
        approval = control.get("approval", {})
        report.check(bool(approval.get("approved_by")), "Readiness blocked: approved_by is empty")
        report.check(bool(approval.get("approved_at")), "Readiness blocked: approved_at is empty")
        report.check(not control.get("open_conflicts"), "Readiness blocked: open conflicts exist")
        for requirement in traceability.get("requirements", []):
            report.check(
                requirement.get("status") != "conflict",
                f"Readiness blocked: {requirement.get('id')} is in conflict",
            )
    else:
        report.warn(
            control.get("review_status") == "approved" and control.get("implementation_ready") is True,
            "Quarter contracts are valid but remain a draft; --ready will fail until Henno approves them.",
        )

    if generated:
        run_generated_checks(root, report)
    return report


def find_repo_root(start: Path) -> Path:
    current = start.resolve()
    for candidate in (current, *current.parents):
        if (candidate / "project" / "specs").is_dir() and (candidate / ".git").exists():
            return candidate
    raise SystemExit("Could not locate the CSC repository root")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("quarter", help="Quarter directory slug, for example: tailors")
    parser.add_argument("--phase", help="Run declared source assertions for this phase")
    parser.add_argument("--ready", action="store_true", help="Enforce human approval/readiness gates")
    parser.add_argument("--generated", action="store_true", help="Run localization and ModBuddy generated-file checks")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable results")
    args = parser.parse_args()

    root = find_repo_root(Path.cwd())
    report = validate(root, args.quarter.lower(), args.phase, args.ready, args.generated)
    payload = {
        "quarter": args.quarter.lower(),
        "checks": report.checks,
        "errors": report.errors,
        "warnings": report.warnings,
        "ok": not report.errors,
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Quarter contract validation: {payload['quarter']}")
        print(f"Checks: {report.checks}  Errors: {len(report.errors)}  Warnings: {len(report.warnings)}")
        for warning in report.warnings:
            print(f"WARNING: {warning}")
        for error in report.errors:
            print(f"ERROR: {error}")
        print("PASS" if payload["ok"] else "FAIL")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
