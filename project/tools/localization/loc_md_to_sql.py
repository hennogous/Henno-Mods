#!/usr/bin/env python3
"""Generate Civ VI localization SQL from readable Markdown sources."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[3]


@dataclass
class Entry:
    heading: str
    line: int
    mode: str
    language: str
    tag: str | None
    tags: list[str]
    where: str | None
    text: str
    text_prefix: str = ""
    text_suffix: str = ""


@dataclass
class SourceFile:
    path: Path
    title: str
    output: Path
    language: str
    entries: list[Entry]


class LocError(ValueError):
    pass


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def parse_key_value(line: str) -> tuple[str, str] | None:
    match = re.match(r"^([A-Za-z][A-Za-z0-9_-]*)\s*:\s*(.*)$", line)
    if not match:
        return None
    return match.group(1).lower(), match.group(2).strip()


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def strip_comment(line: str) -> str:
    if line.strip().startswith("<!--") and line.strip().endswith("-->"):
        return ""
    return re.sub(r"\s+<!--.*?-->\s*$", "", line).rstrip()


def remove_comment_blocks(lines: list[str]) -> list[str]:
    kept: list[str] = []
    in_comment = False
    for line in lines:
        stripped = line.strip()
        if in_comment:
            if "-->" in stripped:
                in_comment = False
                remainder = stripped.split("-->", 1)[1].strip()
                if remainder:
                    kept.append(remainder)
            continue
        if stripped.startswith("<!--"):
            if "-->" not in stripped:
                in_comment = True
            continue
        kept.append(line)
    return kept


def markdown_to_civ_text(lines: list[str]) -> str:
    blocks: list[str] = []
    current: list[str] = []
    list_items: list[str] = []

    def flush_paragraph() -> None:
        nonlocal current
        if current:
            blocks.append(" ".join(part.strip() for part in current if part.strip()))
            current = []

    def flush_list() -> None:
        nonlocal list_items
        if list_items:
            blocks.append("[NEWLINE]".join(list_items))
            list_items = []

    for raw in lines:
        line = strip_comment(raw)
        if not line.strip():
            flush_paragraph()
            flush_list()
            continue

        bullet = re.match(r"^\s*[-*]\s+(.*)$", line)
        if bullet:
            flush_paragraph()
            list_items.append(bullet.group(1).strip())
            continue

        if list_items and (raw.startswith("  ") or raw.startswith("\t")):
            list_items[-1] = f"{list_items[-1]} {line.strip()}"
            continue

        flush_list()

        if line.endswith("\\"):
            current.append(line[:-1].rstrip())
            blocks.append(" ".join(part.strip() for part in current if part.strip()))
            current = []
            continue

        current.append(line)

    flush_paragraph()
    flush_list()
    return "[NEWLINE][NEWLINE]".join(blocks)


def parse_source(path: Path) -> SourceFile:
    lines = remove_comment_blocks(path.read_text(encoding="utf-8").splitlines())
    title = path.stem
    output: Path | None = None
    default_language = "en_US"
    entries: list[Entry] = []
    i = 0

    while i < len(lines):
        raw = lines[i]
        line = raw.strip()
        if not line or line.startswith("<!--"):
            i += 1
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            i += 1
            continue
        if line.startswith("### "):
            i += 1
            continue
        if line.startswith("## "):
            heading = line[3:].strip()
            start_line = i + 1
            i += 1
            meta: dict[str, str] = {}

            while i < len(lines):
                if not lines[i].strip():
                    i += 1
                    break
                if lines[i].startswith("#"):
                    break
                kv = parse_key_value(lines[i])
                if not kv:
                    break
                key, value = kv
                meta[key] = value
                i += 1

            body: list[str] = []
            while i < len(lines) and not lines[i].startswith("## "):
                if not lines[i].strip().startswith("<!--") and not lines[i].startswith("### "):
                    body.append(lines[i])
                i += 1

            mode = meta.get("mode", "upsert").lower()
            if mode not in {"upsert", "update", "raw"}:
                raise LocError(f"{rel(path)}:{start_line}: mode must be upsert, update, or raw")

            tag = meta.get("tag") or (heading if heading.startswith("LOC_") else None)
            tags = parse_csv(meta.get("tags", ""))
            if tag and tag not in tags:
                tags.insert(0, tag)
            where = meta.get("where")
            language = meta.get("language", default_language)

            if mode == "upsert" and not tag:
                raise LocError(f"{rel(path)}:{start_line}: upsert entries need a LOC_* heading or tag:")
            if mode == "update" and not tags and not where:
                raise LocError(f"{rel(path)}:{start_line}: update entries need tag:, tags:, or where:")
            if mode == "raw":
                raw_body = "\n".join(body).strip()
                if raw_body.startswith("```"):
                    raw_lines = raw_body.splitlines()
                    if raw_lines and raw_lines[0].startswith("```"):
                        raw_lines = raw_lines[1:]
                    if raw_lines and raw_lines[-1].startswith("```"):
                        raw_lines = raw_lines[:-1]
                    raw_body = "\n".join(raw_lines).strip()
                text = raw_body
            else:
                text = markdown_to_civ_text(body).strip()
                text = meta.get("text-prefix", "") + text + meta.get("text-suffix", "")

            entries.append(
                Entry(
                    heading=heading,
                    line=start_line,
                    mode=mode,
                    language=language,
                    tag=tag,
                    tags=tags,
                    where=where,
                    text=text,
                )
            )
            continue

        kv = parse_key_value(raw)
        if kv:
            key, value = kv
            if key == "output":
                output = (ROOT / value).resolve()
            elif key == "language":
                default_language = value
            i += 1
            continue

        i += 1

    if output is None:
        raise LocError(f"{rel(path)}: missing top-level output: path")
    if not entries:
        raise LocError(f"{rel(path)}: no localization entries found")

    seen: set[tuple[str, str]] = set()
    for entry in entries:
        if entry.mode != "upsert" or not entry.tag:
            continue
        key = (entry.language, entry.tag)
        if key in seen:
            raise LocError(f"{rel(path)}:{entry.line}: duplicate upsert for {entry.language}/{entry.tag}")
        seen.add(key)

    return SourceFile(path=path, title=title, output=output, language=default_language, entries=entries)


def sql_quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def tag_where(tags: list[str], explicit_where: str | None) -> str:
    if explicit_where:
        return explicit_where
    if len(tags) == 1:
        return f"Tag = {sql_quote(tags[0])}"
    return "Tag IN (" + ", ".join(sql_quote(tag) for tag in tags) + ")"


def render_sql(source: SourceFile) -> str:
    out: list[str] = [
        f"-- {source.title}",
        f"-- Generated from {rel(source.path)} by project/tools/localization/loc_md_to_sql.py",
        "-- Edit the Markdown source, then regenerate this file.",
        "--------------------------------------------------------------",
        "",
    ]

    upserts = [entry for entry in source.entries if entry.mode == "upsert"]
    updates = [entry for entry in source.entries if entry.mode == "update"]
    raw_entries = [entry for entry in source.entries if entry.mode == "raw"]

    if upserts:
        out.extend(
            [
                "INSERT OR REPLACE INTO LocalizedText",
                "    (Language, Tag, Text)",
                "VALUES",
            ]
        )
        for index, entry in enumerate(upserts):
            suffix = ";" if index == len(upserts) - 1 else ","
            out.append(
                f"    ({sql_quote(entry.language)}, {sql_quote(entry.tag or '')}, {sql_quote(entry.text)}){suffix}"
            )
        out.append("")

    for entry in updates:
        out.extend(
            [
                "UPDATE LocalizedText",
                f"SET Text = {sql_quote(entry.text)}",
                f"WHERE {tag_where(entry.tags, entry.where)};",
                "",
            ]
        )

    for entry in raw_entries:
        out.extend(
            [
                f"-- {entry.heading}",
                entry.text.rstrip(),
                "",
            ]
        )

    return "\n".join(out).rstrip() + "\n"


def iter_sources(paths: Iterable[Path]) -> list[Path]:
    sources: list[Path] = []
    for path in paths:
        if path.is_dir():
            sources.extend(sorted(item for item in path.rglob("*.md") if item.is_file()))
        elif path.is_file():
            sources.append(path)
        else:
            raise LocError(f"{path}: path does not exist")
    return sources


def write_if_changed(path: Path, content: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else None
    if old == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sources", nargs="*", type=Path, default=[ROOT / "project" / "localization"])
    parser.add_argument("--check", action="store_true", help="fail if generated SQL is not up to date")
    parser.add_argument("--stdout", action="store_true", help="print generated SQL instead of writing files")
    args = parser.parse_args(argv)

    try:
        changed: list[Path] = []
        for source_path in iter_sources(args.sources):
            source = parse_source(source_path.resolve())
            sql = render_sql(source)
            if args.stdout:
                sys.stdout.write(sql)
                continue
            if args.check:
                current = source.output.read_text(encoding="utf-8") if source.output.exists() else None
                if current != sql:
                    changed.append(source.output)
                continue
            if write_if_changed(source.output, sql):
                changed.append(source.output)

        if args.check and changed:
            for path in changed:
                print(f"out of date: {rel(path)}", file=sys.stderr)
            return 1

        if not args.stdout:
            verb = "would update" if args.check else "updated"
            for path in changed:
                print(f"{verb}: {rel(path)}")
            if not changed:
                print("localization SQL is up to date")
        return 0
    except LocError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
