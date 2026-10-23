#!/usr/bin/env python3
"""Format CSC SQL: aligned short rows, vertical lists for seven or more columns.

Only whitespace between lexical tokens is edited. Strings, quoted identifiers,
comments, expressions, statement order and delimiters are preserved exactly.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


LEXER = re.compile(
    r"(?P<space>\s+)|(?P<comment>--[^\r\n]*|/\*[\s\S]*?\*/)"
    r"|(?P<quoted>'(?:''|[^'])*'|\"(?:\"\"|[^\"])*\"|`(?:``|[^`])*`|\[[^\]]*\])"
    r"|(?P<number>(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<word>[\w$]+)|(?P<operator>\|\||->>|->|<=|>=|<>|!=|==|<<|>>)"
    r"|(?P<symbol>[^\s])"
)
INDENT = "        "


def sql_tokens(text: str, *, comments: bool = True) -> list[tuple[str, str]]:
    """Return exact lexical tokens, suitable for a formatting regression check."""
    return [
        (match.lastgroup or "", match.group())
        for match in LEXER.finditer(text)
        if match.lastgroup != "space" and (comments or match.lastgroup != "comment")
    ]


def format_sql_layout_text(text: str) -> str:
    tokens = [m for m in LEXER.finditer(text) if m.lastgroup != "space"]
    if not tokens:
        return text
    gaps = [text[:tokens[0].start()]] + [
        text[tokens[i - 1].end():tokens[i].start()] for i in range(1, len(tokens))
    ]
    code = [i for i, token in enumerate(tokens) if token.lastgroup != "comment"]

    def word(position: int) -> str:
        if position >= len(code):
            return ""
        token = tokens[code[position]]
        # Quoted literals/identifiers must never be mistaken for SQL keywords.
        return token.group().upper() if token.lastgroup in {"word", "symbol"} else ""

    def fields(first: int, stop: int) -> list[tuple[int, int]]:
        """Token ranges separated by commas outside nested expressions."""
        result = []
        depth = 0
        start = first
        for i in range(first, stop):
            if tokens[i].lastgroup in {"comment", "quoted"}:
                continue
            value = tokens[i].group()
            if value == "(":
                depth += 1
            elif value == ")":
                depth -= 1
            elif value == "," and depth == 0:
                result.append((start, i))
                start = i + 1
        result.append((start, stop))
        return result

    def matching(position: int) -> int | None:
        depth = 0
        for p in range(position, len(code)):
            if word(p) == "(":
                depth += 1
            elif word(p) == ")":
                depth -= 1
                if depth == 0:
                    return p
        return None

    def compact(first: int, stop: int) -> str:
        return "".join(
            (" " if i > first and gaps[i] else "") + tokens[i].group()
            for i in range(first, stop)
        )

    def row_break(index: int, indent: str) -> str:
        # Blank lines often separate meaningful groups within a VALUES list.
        return "\n" * max(1, gaps[index].count("\n")) + indent

    def layout(group: list[tuple[int, int]], close: int | None,
               vertical: bool, widths: list[int] | None = None) -> None:
        label_width = max(
            (len(tokens[first].group().expandtabs(4)) for first, stop in group
             if first < stop and tokens[first].lastgroup == "comment"
             and tokens[first].group().startswith("/*")
             and "\n" not in tokens[first].group()), default=0
        )
        for column, (first, stop) in enumerate(group):
            if first >= stop:
                return
            prefix = text[text.rfind("\n", 0, tokens[first].start()) + 1:tokens[first].start()]
            shift = len(INDENT) - len(prefix.expandtabs(4)) if not prefix.strip() else 0
            if vertical and shift:
                for i in range(first + 1, stop):
                    if "\n" in gaps[i]:
                        head, tail = gaps[i].rsplit("\n", 1)
                        gaps[i] = head + "\n" + " " * max(0, len(tail.expandtabs(4)) + shift)
            gaps[first] = "\n" + INDENT if vertical else (
                "   " if column == 0 else
                " " * ((widths or [])[column - 1] - len(compact(*group[column - 1])) + 3)
            )
            if not vertical:
                for i in range(first + 1, stop):
                    gaps[i] = " " if gaps[i] else ""
            elif tokens[first].lastgroup == "comment" and label_width:
                # Keep existing /* ColumnName, */ text and align its value.
                if first + 1 < stop and tokens[first + 1].lastgroup != "comment":
                    gaps[first + 1] = " " * (label_width - len(tokens[first].group().expandtabs(4)) + 2)
            if tokens[stop - 1].lastgroup != "comment":
                gaps[stop] = ""
        if close is not None:
            gaps[close] = "\n    " if vertical else "   "

    def layout_selects(source: int, ncolumns: int) -> None:
        cursor = source
        depth = 0
        while cursor < len(code):
            value = word(cursor)
            if value == ";" and depth == 0:
                break
            if value == "SELECT" and depth == 0:
                gaps[code[cursor]] = "\n"
                first = cursor + 1
                if word(first) in {"DISTINCT", "ALL"}:
                    first += 1
                nested = 0
                stop = first
                while stop < len(code):
                    item = word(stop)
                    if nested == 0 and item in {"FROM", "WHERE", "UNION", "EXCEPT", "INTERSECT", "ORDER", "GROUP", "LIMIT", "RETURNING", ";"}:
                        break
                    if item == "(":
                        nested += 1
                    elif item == ")":
                        if nested == 0:
                            break
                        nested -= 1
                    stop += 1
                if stop < len(code) and first < stop:
                    selected = fields(code[first], code[stop])
                    if len(selected) == ncolumns:
                        layout(selected, None, True)
                        if word(stop) != ";":
                            gaps[code[stop]] = "\n"
                cursor = stop
                continue
            if value == "(":
                depth += 1
            elif value == ")":
                if depth == 0:
                    break
                depth -= 1
            cursor += 1

    p = 0
    while p < len(code):
        if word(p) != "INSERT":
            p += 1
            continue
        # INSERT [OR conflict] INTO table [(column, ...)] ...
        into = p + 1
        if word(into) == "OR":
            into += 2
        if word(into) != "INTO" or into + 2 >= len(code):
            p += 1
            continue
        table_end = into + 2
        if word(table_end) == ".":
            table_end += 2
        if word(table_end) != "(":
            p += 1
            continue
        end = matching(table_end)
        if end is None:
            p += 1
            continue
        opening, closing = code[table_end], code[end]
        columns = fields(opening + 1, closing)
        ncolumns = len(columns)
        source = end + 1
        wide = ncolumns >= 7
        if word(source) == "VALUES":
            rows = []
            cursor = source + 1
            while word(cursor) == "(":
                row_end = matching(cursor)
                if row_end is None:
                    break
                rows.append((code[cursor], code[row_end], fields(code[cursor] + 1, code[row_end])))
                cursor = row_end + 1
                if word(cursor) != ",":
                    break
                cursor += 1
            if not rows or any(len(row[2]) != ncolumns for row in rows):
                p = source
                continue
            # Annotated rows and multiline literals retain a vertical layout.
            vertical = wide or any(
                tokens[i].lastgroup == "comment" or "\n" in tokens[i].group()
                for first, last, _ in rows for i in range(first + 1, last)
            )
            groups = [columns] + [row[2] for row in rows]
            widths = [max(len(compact(*group[c])) for group in groups) for c in range(ncolumns)]
            gaps[opening] = "\n    " if vertical else "\n" + INDENT
            layout(columns, closing, vertical, widths)
            gaps[code[source]] = "\n"
            for number, (first, last, group) in enumerate(rows):
                if vertical:
                    gaps[first] = row_break(first, "    ")
                else:
                    gaps[first] = "  " if number == 0 and code[source] == first - 1 else row_break(first, INDENT)
                layout(group, last, vertical, widths)
            p = source
        elif word(source) == "SELECT":
            gaps[opening] = "\n    " if wide else "\n" + INDENT
            widths = [len(compact(*field)) for field in columns]
            layout(columns, closing, wide, widths)
            gaps[code[source]] = "\n"
            if wide:
                layout_selects(source, ncolumns)
            p = source
        else:
            p = source
    # Code following -- must stay on the next line after any layout change.
    for i in range(1, len(tokens)):
        if tokens[i - 1].lastgroup == "comment" and tokens[i - 1].group().startswith("--"):
            if "\n" not in gaps[i]:
                gaps[i] = "\n" + INDENT
    result = "".join(gap + token.group() for gap, token in zip(gaps, tokens))
    result += text[tokens[-1].end():]
    if sql_tokens(result) != sql_tokens(text):
        raise ValueError("Formatting changed SQL tokens or comments")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    failures = 0
    for path in args.paths:
        data = path.read_bytes()
        bom = data.startswith(b"\xef\xbb\xbf")
        original = data.decode("utf-8-sig").replace("\r\n", "\n")
        formatted = format_sql_layout_text(original)
        if original == formatted:
            print(f"PASS: {path}")
        elif args.check:
            print(f"FAIL: {path}: CSC SQL layout differs")
            failures += 1
        else:
            newline = "\r\n" if b"\r\n" in data else "\n"
            payload = formatted.replace("\n", newline).encode("utf-8")
            path.write_bytes((b"\xef\xbb\xbf" if bom else b"") + payload)
            print(f"formatted: {path}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
