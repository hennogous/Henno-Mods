#!/usr/bin/env python3
"""Format CSC Quarter SQL row blocks using the Bakers-derived visual layout."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


HEADER_ROW = re.compile(r"^(?P<indent>\s*)\(\s*(?P<body>[^()]*)\s*\)\s*$")
VALUE_ROW = re.compile(r"^(?P<prefix>VALUES\s+|\s*)\(\s*(?P<body>.*)\s*\)(?P<ending>\s*[,;])\s*$")
COMMENT_VALUE = re.compile(r"^(?P<indent>\s*)/\*\s*(?P<label>[^*]+?)\s*\*/\s*(?P<value>.+)$")


def split_fields(body: str) -> list[str] | None:
    fields: list[str] = []
    current: list[str] = []
    quote: str | None = None
    depth = 0
    index = 0
    while index < len(body):
        character = body[index]
        if quote:
            current.append(character)
            if character == quote:
                if index + 1 < len(body) and body[index + 1] == quote:
                    current.append(body[index + 1])
                    index += 1
                else:
                    quote = None
        elif character in {"'", '"'}:
            quote = character
            current.append(character)
        elif character == "(":
            depth += 1
            current.append(character)
        elif character == ")":
            depth -= 1
            if depth < 0:
                return None
            current.append(character)
        elif character == "," and depth == 0:
            fields.append("".join(current).strip())
            current = []
        else:
            current.append(character)
        index += 1
    if quote or depth != 0:
        return None
    fields.append("".join(current).strip())
    return fields


def render_row(fields: list[str], widths: list[int], prefix: str, ending: str) -> str:
    parts = [
        field + "," + " " * (widths[index] - len(field) + 3)
        for index, field in enumerate(fields[:-1])
    ]
    parts.append(fields[-1])
    return f"{prefix}(   " + "".join(parts) + f"   ){ending}"


def format_simple_values(lines: list[str]) -> list[str]:
    formatted = list(lines)
    index = 0
    while index < len(formatted):
        header = HEADER_ROW.match(formatted[index])
        if not header:
            index += 1
            continue
        header_fields = split_fields(header.group("body"))
        if not header_fields or len(header_fields) < 2:
            index += 1
            continue
        cursor = index + 1
        while cursor < len(formatted) and not formatted[cursor].strip():
            cursor += 1
        if cursor >= len(formatted) or not formatted[cursor].lstrip().startswith("VALUES"):
            index += 1
            continue

        row_indexes: list[int] = []
        rows: list[list[str]] = []
        scan = cursor
        complete = False
        while scan < len(formatted):
            stripped = formatted[scan].strip()
            if not stripped or stripped.startswith("--"):
                scan += 1
                continue
            match = VALUE_ROW.match(formatted[scan])
            if not match:
                break
            fields = split_fields(match.group("body"))
            if fields is None or len(fields) != len(header_fields):
                break
            row_indexes.append(scan)
            rows.append(fields)
            if match.group("ending").strip() == ";":
                complete = True
                scan += 1
                break
            scan += 1
        if not complete or not rows:
            index += 1
            continue

        widths = [max(len(header_fields[column]), *(len(row[column]) for row in rows)) for column in range(len(header_fields))]
        formatted[index] = render_row(header_fields, widths, "        ", "")
        for row_number, (line_index, fields) in enumerate(zip(row_indexes, rows)):
            ending = ";" if row_number == len(rows) - 1 else ","
            prefix = "VALUES  " if row_number == 0 else "        "
            formatted[line_index] = render_row(fields, widths, prefix, ending)
        index = scan
    return formatted


def format_comment_values(lines: list[str]) -> list[str]:
    formatted = list(lines)
    index = 0
    while index < len(formatted):
        group: list[tuple[int, str, str]] = []
        cursor = index
        while cursor < len(formatted):
            match = COMMENT_VALUE.match(formatted[cursor])
            if not match:
                break
            group.append((cursor, match.group("label").strip(), match.group("value").strip()))
            cursor += 1
        if len(group) >= 4:
            width = max(len(label) for _, label, _ in group)
            for line_index, label, value in group:
                formatted[line_index] = f"        /*  {label.ljust(width)} */  {value}"
            index = cursor
        else:
            index += 1
    return formatted


def format_sql_layout_text(text: str) -> str:
    trailing_newline = text.endswith("\n")
    lines = text.splitlines()
    lines = format_simple_values(lines)
    lines = format_comment_values(lines)
    result = "\n".join(lines)
    return result + ("\n" if trailing_newline else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failures = 0
    for path in args.paths:
        original = path.read_text(encoding="utf-8-sig")
        formatted = format_sql_layout_text(original)
        if original == formatted:
            print(f"PASS: {path}")
            continue
        if args.check:
            print(f"FAIL: {path}: Bakers-derived row alignment differs")
            failures += 1
        else:
            path.write_text(formatted, encoding="utf-8", newline="\n")
            print(f"formatted: {path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
