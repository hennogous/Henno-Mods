#!/usr/bin/env python3
"""Bakers-derived visual and architectural style checks for Quarter SQL."""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path

import yaml


LAYOUT_SPEC = importlib.util.spec_from_file_location(
    "csc_format_sql_layout", Path(__file__).with_name("format_sql_layout.py")
)
assert LAYOUT_SPEC and LAYOUT_SPEC.loader
SQL_LAYOUT = importlib.util.module_from_spec(LAYOUT_SPEC)
LAYOUT_SPEC.loader.exec_module(SQL_LAYOUT)


ROOT = Path(__file__).resolve().parents[3]
POLICY_PATH = ROOT / "project/specs/reference/bakers-sql-style.yaml"
MAJOR_RULE = re.compile(r"^--={80,}--$")
SUBSECTION_RULE = re.compile(r"^-{80,}$")
MAJOR_HEADING = re.compile(r"^/\*\t(.+?) \*/$")
SUBSECTION_HEADING = re.compile(r"^--\t([^-].*?)$")
TOP_LEVEL_KEYWORD = re.compile(
    r"^(INSERT|VALUES|SELECT|UPDATE|DELETE|CREATE|DROP|WITH|UNION)\b"
)
INDENTED_KEYWORD = re.compile(
    r"^[ \t]+(INSERT|VALUES|SELECT|UPDATE|DELETE|CREATE|DROP|WITH|UNION)\b"
)


def load_policy() -> dict:
    return yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))


def ordered_subset(required: list[str], actual: list[str]) -> list[str]:
    """Return required values missing from actual in the required order."""
    cursor = 0
    missing: list[str] = []
    for value in required:
        try:
            cursor = actual.index(value, cursor) + 1
        except ValueError:
            missing.append(value)
    return missing


def validate_sql_style(
    path: Path,
    profile: str,
    quarter: str,
    *,
    strict_whitespace: bool = True,
) -> list[str]:
    policy = load_policy()
    raw = path.read_text(encoding="utf-8-sig")
    lines = raw.splitlines()
    errors: list[str] = []
    quarter_upper = quarter.upper()

    if (
        not lines
        or (
            not lines[0].startswith(f"-- CSC_Q_{quarter_upper}")
            and strict_whitespace
        )
    ):
        errors.append("line 1 must identify CSC_Q_<QUARTER>")
    if not any(line == "-- Author: Henno" for line in lines[:6]):
        errors.append("header must contain '-- Author: Henno'")
    if strict_whitespace:
        for number, line in enumerate(lines, 1):
            if line != line.rstrip():
                errors.append(f"line {number}: trailing whitespace")
        formatted = SQL_LAYOUT.format_sql_layout_text(raw)
        if formatted != raw:
            original_lines = raw.splitlines()
            formatted_lines = formatted.splitlines()
            mismatch = next(
                (
                    number
                    for number, (original, expected) in enumerate(
                        zip(original_lines, formatted_lines), 1
                    )
                    if original != expected
                ),
                min(len(original_lines), len(formatted_lines)) + 1,
            )
            errors.append(
                f"line {mismatch}: Bakers-derived row alignment differs; "
                "run format_sql_layout.py"
            )
    for number, line in enumerate(lines, 1):
        if INDENTED_KEYWORD.match(line):
            errors.append(f"line {number}: top-level SQL keyword is indented")

    major_sections: list[str] = []
    subsections: list[str] = []
    for index, line in enumerate(lines):
        major = MAJOR_HEADING.match(line)
        if major:
            major_sections.append(major.group(1))
            previous = lines[index - 1] if index > 0 else ""
            following = lines[index + 1] if index + 1 < len(lines) else ""
            if (
                index == 0
                or index + 1 >= len(lines)
                or not (MAJOR_RULE.match(previous) or SUBSECTION_RULE.match(previous))
                or previous != following
            ):
                errors.append(
                    f"line {index + 1}: major heading must have matching equals delimiters"
                )
        subsection = SUBSECTION_HEADING.match(line)
        if subsection:
            title = subsection.group(1).rstrip()
            previous = lines[index - 1] if index > 0 else ""
            following = lines[index + 1] if index + 1 < len(lines) else ""
            # Effect comments and group labels also begin with a tab. Only a
            # line actually sandwiched by delimiters is a named subsection.
            if (
                not re.search(r"-{10,}$", title)
                and SUBSECTION_RULE.match(previous)
                and previous == following
            ):
                subsections.append(title)

    if profile == "core":
        required_sections = [
            value.replace("{QUARTER}", quarter_upper)
            for value in policy["core_required_sections"]
        ]
        missing = ordered_subset(required_sections, major_sections)
        if missing:
            errors.append(
                "missing or out-of-order major sections: " + ", ".join(missing)
            )
        for subsection in policy["core_required_subsections"]:
            if subsection not in subsections:
                errors.append(f"missing required subsection: {subsection}")
        for table, first_column in (
            ("Districts", "DistrictType"),
            ("Buildings", "BuildingType"),
        ):
            table_insert = re.search(
                rf"INSERT(?: OR IGNORE)? INTO {table}\b", raw, re.IGNORECASE
            )
            value_comment = re.search(
                rf"/\*\s*{first_column},?\s*\*/", raw, re.IGNORECASE
            )
            if table_insert and not value_comment:
                errors.append(
                    f"{table} rows must use per-value /* {first_column}, */ comments"
                )
        if quarter_upper != "BAKERS" and "CSC_BAKERS" in raw:
            errors.append("foreign Bakers identifier found in Quarter SQL")

    if profile in {"gold", "monopolies_gold"}:
        non_gold_yields = sorted(
            set(re.findall(r"'(YIELD_(?!GOLD\b)[A-Z_]+)'", raw))
        )
        if non_gold_yields:
            errors.append(
                "Gold companion contains non-Gold YieldType literals: "
                + ", ".join(non_gold_yields)
            )
    if profile == "monopolies":
        if re.search(r"'YIELD_GOLD'", raw):
            errors.append("non-Gold M&C companion contains YIELD_GOLD")

    for table in policy["shared_definitions_forbidden_in_quarter"]:
        if re.search(
            rf"CREATE\s+(?:TEMP(?:ORARY)?\s+)?TABLE(?:\s+IF\s+NOT\s+EXISTS)?\s+{re.escape(table)}\b",
            raw,
            re.IGNORECASE,
        ):
            errors.append(f"shared CSC_Q_ALL table redefined: {table}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("path", type=Path)
    parser.add_argument(
        "--profile",
        required=True,
        choices=["core", "gold", "monopolies", "monopolies_gold"],
    )
    parser.add_argument("--quarter", required=True)
    parser.add_argument(
        "--reference-compatible",
        action="store_true",
        help="Allow legacy reference whitespace while checking its structural style.",
    )
    args = parser.parse_args()
    path = args.path if args.path.is_absolute() else ROOT / args.path
    failures = validate_sql_style(
        path,
        args.profile,
        args.quarter,
        strict_whitespace=not args.reference_compatible,
    )
    for failure in failures:
        print(f"ERROR: {path}: {failure}")
    if failures:
        print(f"FAIL: {len(failures)} SQL style violation(s)")
        return 1
    print(f"PASS: {path} ({args.profile} style)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
