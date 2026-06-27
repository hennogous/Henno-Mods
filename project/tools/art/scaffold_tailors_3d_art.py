#!/usr/bin/env python3
"""Scaffold Tailors' Quarter 3D artdef entries from Bakers' direct children.

This intentionally edits artdef XML as text so Asset Editor formatting remains
stable. It only clones direct children of known collections; nested references
with repeated names are not treated as clone sources.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class Block:
    start: int
    end: int
    parent: int | None
    name: str | None
    collection: str | None


STRUCT_OPEN = re.compile(r"^\s*<Element(?:\s|>)")
STRUCT_CLOSE = re.compile(r"^\s*</Element>\s*$")
NAME_RE = re.compile(r'<m_Name text="([^"]*)"')
COLLECTION_RE = re.compile(r'<m_CollectionName text="([^"]*)"')


def read_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8-sig").splitlines(keepends=True)


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("".join(lines), encoding="utf-8", newline="")


def discover_blocks(lines: list[str]) -> dict[int, Block]:
    stack: list[int] = []
    raw: dict[int, dict[str, object]] = {}
    blocks: dict[int, Block] = {}

    for idx, line in enumerate(lines):
        if STRUCT_OPEN.match(line):
            parent = stack[-1] if stack else None
            raw[idx] = {"parent": parent, "name": None, "collection": None}
            stack.append(idx)
            continue

        if stack:
            if match := NAME_RE.search(line):
                raw[stack[-1]]["name"] = match.group(1)
            if match := COLLECTION_RE.search(line):
                raw[stack[-1]]["collection"] = match.group(1)

        if STRUCT_CLOSE.match(line):
            if not stack:
                raise ValueError(f"Unmatched </Element> at line {idx + 1}")
            start = stack.pop()
            data = raw[start]
            blocks[start] = Block(
                start=start,
                end=idx,
                parent=data["parent"],  # type: ignore[arg-type]
                name=data["name"],  # type: ignore[arg-type]
                collection=data["collection"],  # type: ignore[arg-type]
            )

    if stack:
        raise ValueError("Unclosed <Element> block(s)")
    return blocks


def root_collection(blocks: dict[int, Block], name: str) -> Block:
    matches = [b for b in blocks.values() if b.parent is None and b.collection == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one root collection {name!r}, found {len(matches)}")
    return matches[0]


def direct_children(blocks: dict[int, Block], parent: Block) -> list[Block]:
    return sorted((b for b in blocks.values() if b.parent == parent.start), key=lambda b: b.start)


def direct_child_by_name(blocks: dict[int, Block], parent: Block, name: str) -> Block:
    matches = [b for b in direct_children(blocks, parent) if b.name == name]
    if len(matches) != 1:
        raise ValueError(f"Expected one direct child {name!r} under {parent.collection or parent.name}, found {len(matches)}")
    return matches[0]


def insert_before_collection_close(lines: list[str], collection: Block, text: str) -> list[str]:
    insert_at = collection.end
    return lines[:insert_at] + text.splitlines(keepends=True) + lines[insert_at:]


def replace_many(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    text = text.replace("CSC_TAILORS_SV_Fashion House", "CSC_TAILORS_SV_Fashion_House")
    return text


TAILORS_REPLACEMENTS = [
    ("CSC_TAILORS_SV_Fashion House", "CSC_TAILORS_SV_Fashion_House"),
    ("CSC_BAKERS_SV_Cafe", "CSC_TAILORS_SV_Fashion_House"),
    ("DISTRICT_CSC_BAKERS_QUARTER", "DISTRICT_CSC_TAILORS_QUARTER"),
    ("BUILDING_CSC_BAKERS_WIND_MILL", "BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP"),
    ("BUILDING_CSC_BAKERS_BAKERY", "BUILDING_CSC_TAILORS_TAILOR"),
    ("BUILDING_CSC_BAKERS_CAFE", "BUILDING_CSC_TAILORS_FASHION_HOUSE"),
    ("CSC_BAKERS_WIND_MILL", "CSC_TAILORS_TEXTILE_WORKSHOP"),
    ("CSC_BAKERS_BAKERY", "CSC_TAILORS_TAILOR"),
    ("CSC_BAKERS_CAFE", "CSC_TAILORS_FASHION_HOUSE"),
    ("CSC_BAKERS_Wind_Mill", "CSC_TAILORS_Textile_Workshop"),
    ("CSC_BAKERS_Bakery", "CSC_TAILORS_Tailor"),
    ("CSC_BAKERS_Cafe", "CSC_TAILORS_Fashion_House"),
    ("WIND MILL, BAKERY, CAFE", "TEXTILE WORKSHOP, TAILOR, FASHION HOUSE"),
    ("WIND MILL, BAKERY", "TEXTILE WORKSHOP, TAILOR"),
    ("WIND MILL, CAFE", "TEXTILE WORKSHOP, FASHION HOUSE"),
    ("WIND MILL", "TEXTILE WORKSHOP"),
    ("BAKERY", "TAILOR"),
    ("CAFE", "FASHION HOUSE"),
    ("Wind Mill", "Textile Workshop"),
    ("Bakery", "Tailor"),
    ("Cafe", "Fashion House"),
    ("Wind_Mill", "Textile_Workshop"),
    ("Bakery", "Tailor"),
    ("Cafe", "Fashion_House"),
    ("BAKERS", "TAILORS"),
    ("Bakers", "Tailors"),
    ("CSC_BAKERS", "CSC_TAILORS"),
]


def normalize_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8-sig")
    normalized = replace_many(text, TAILORS_REPLACEMENTS)
    if normalized == text:
        return False
    path.write_text(normalized, encoding="utf-8", newline="")
    return True


def clone_direct_entries(path: Path, collection_name: str, mapping: dict[str, str]) -> bool:
    lines = read_lines(path)
    blocks = discover_blocks(lines)
    collection = root_collection(blocks, collection_name)
    changed = False

    existing = {b.name for b in direct_children(blocks, collection)}
    additions: list[str] = []
    for source, target in mapping.items():
        if target in existing:
            continue
        source_block = direct_child_by_name(blocks, collection, source)
        text = "".join(lines[source_block.start : source_block.end + 1])
        additions.append(replace_many(text, TAILORS_REPLACEMENTS))
        changed = True

    if changed:
        write_lines(path, insert_before_collection_close(lines, collection, "".join(additions)))
    return changed


def set_direct_child_name(block_text: str, old: str, new: str) -> str:
    return block_text.replace(f'<m_Name text="{old}"', f'<m_Name text="{new}"')


def keep_subcollection_children(block_text: str, collection_name: str, keep_names: list[str], rename: dict[str, str] | None = None) -> str:
    lines = block_text.splitlines(keepends=True)
    blocks = discover_blocks(lines)
    collection = next((b for b in blocks.values() if b.collection == collection_name), None)
    if collection is None:
        raise ValueError(f"Missing subcollection {collection_name}")

    rename = rename or {}
    children = {child.name: child for child in direct_children(blocks, collection)}
    missing = [name for name in keep_names if name not in children]
    if missing:
        raise ValueError(f"Missing expected {collection_name} child/children: {', '.join(missing)}")

    ordered_blocks: list[str] = []
    for name in keep_names:
        child = children[name]
        child_text = "".join(lines[child.start : child.end + 1])
        if name in rename:
            child_text = set_direct_child_name(child_text, name, rename[name])
        ordered_blocks.append(child_text)

    direct = direct_children(blocks, collection)
    if not direct:
        return "".join(lines)
    first = min(child.start for child in direct)
    last = max(child.end for child in direct)
    return "".join(lines[:first] + "".join(ordered_blocks).splitlines(keepends=True) + lines[last + 1 :])


def reorder_subcollection_children(block_text: str, collection_name: str, ordered_names: list[str]) -> str:
    return keep_subcollection_children(block_text, collection_name, ordered_names)


def scaffold_landmarks() -> bool:
    path = ROOT / "Civ Supply Chains" / "ArtDefs" / "CSC_Landmarks.artdef"
    lines = read_lines(path)
    blocks = discover_blocks(lines)
    collection = root_collection(blocks, "Districts")
    tailors = next((b for b in direct_children(blocks, collection) if b.name == "DISTRICT_CSC_TAILORS_QUARTER"), None)
    if tailors is not None:
        text = "".join(lines[tailors.start : tailors.end + 1])
        normalized = reorder_subcollection_children(
            text,
            "BaseVariants",
            [
                "01 Ancient: Empty",
                "02 Classical: Empty",
                "03 Classical: Textile Workshop",
                "04 Classical: Textile Workshop, Tailor",
                "05 Classical: Textile Workshop, Fashion House",
                "06 Classical: Textile Workshop, Tailor, Fashion House",
            ],
        )
        if normalized == text:
            return False
        write_lines(path, lines[: tailors.start] + normalized.splitlines(keepends=True) + lines[tailors.end + 1 :])
        return True

    source = direct_child_by_name(blocks, collection, "DISTRICT_CSC_BAKERS_QUARTER")
    text = "".join(lines[source.start : source.end + 1])

    text = keep_subcollection_children(
        text,
        "BaseVariants",
        [
            "01 Ancient: Empty",
            "03 Classical: Empty",
            "04_1 Classical: B1_1",
            "05_1 Classical: B1_1, B2",
            "06_1 Classical: B1_1, B3",
            "07_1 Classical: B1_1, B2, B3",
        ],
        {
            "03 Classical: Empty": "02 Classical: Empty",
            "04_1 Classical: B1_1": "03 Classical: Textile Workshop",
            "05_1 Classical: B1_1, B2": "04 Classical: Textile Workshop, Tailor",
            "06_1 Classical: B1_1, B3": "05 Classical: Textile Workshop, Fashion House",
            "07_1 Classical: B1_1, B2, B3": "06 Classical: Textile Workshop, Tailor, Fashion House",
        },
    )
    text = keep_subcollection_children(
        text,
        "BuildingVariants",
        ["01 Ancient: Wind Mill", "02 Medieval: Bakery", "03 Renaissance: Cafe"],
        {
            "01 Ancient: Wind Mill": "01 Classical: Textile Workshop",
            "02 Medieval: Bakery": "02 Medieval: Tailor",
            "03 Renaissance: Cafe": "03 Renaissance: Fashion House",
        },
    )
    text = keep_subcollection_children(
        text,
        "BuildingSets",
        ["EMPTY", "WIND MILL", "WIND MILL, BAKERY", "WIND MILL, CAFE", "WIND MILL, BAKERY, CAFE"],
    )
    text = replace_many(text, TAILORS_REPLACEMENTS)

    write_lines(path, insert_before_collection_close(lines, collection, text))
    return True


def validate_xml(paths: list[Path]) -> None:
    for path in paths:
        ET.parse(path)


def main() -> int:
    paths = {
        "districts": ROOT / "Civ Supply Chains" / "ArtDefs" / "CSC_Districts.artdef",
        "strategic": ROOT / "Civ Supply Chains" / "ArtDefs" / "CSC_StrategicView.artdef",
        "buildings": ROOT / "Civ Supply Chains" / "ArtDefs" / "CSC_Buildings.artdef",
        "landmarks": ROOT / "Civ Supply Chains" / "ArtDefs" / "CSC_Landmarks.artdef",
    }

    changed = []
    if clone_direct_entries(paths["districts"], "District", {"DISTRICT_CSC_BAKERS_QUARTER": "DISTRICT_CSC_TAILORS_QUARTER"}):
        changed.append(paths["districts"])

    if clone_direct_entries(
        paths["strategic"],
        "DistrictEntries",
        {
            "CSC_BAKERS": "CSC_TAILORS",
            "CSC_BAKERS_Pillaged": "CSC_TAILORS_Pillaged",
            "CSC_BAKERS_UnderConstruction": "CSC_TAILORS_UnderConstruction",
        },
    ):
        changed.append(paths["strategic"])

    if clone_direct_entries(
        paths["strategic"],
        "Districts",
        {
            "CSC_BAKERS": "CSC_TAILORS",
            "CSC_BAKERS_Pillaged": "CSC_TAILORS_Pillaged",
            "CSC_BAKERS_UnderConstruction": "CSC_TAILORS_UnderConstruction",
        },
    ):
        changed.append(paths["strategic"])

    strategic_buildings = {
        "CSC_BAKERS_Wind_Mill": "CSC_TAILORS_Textile_Workshop",
        "CSC_BAKERS_Wind_Mill_Pillaged": "CSC_TAILORS_Textile_Workshop_Pillaged",
        "CSC_BAKERS_Wind_Mill_UnderConstruction": "CSC_TAILORS_Textile_Workshop_UnderConstruction",
        "CSC_BAKERS_Bakery": "CSC_TAILORS_Tailor",
        "CSC_BAKERS_Bakery_Pillaged": "CSC_TAILORS_Tailor_Pillaged",
        "CSC_BAKERS_Bakery_UnderConstruction": "CSC_TAILORS_Tailor_UnderConstruction",
        "CSC_BAKERS_Cafe": "CSC_TAILORS_Fashion_House",
        "CSC_BAKERS_Cafe_Pillaged": "CSC_TAILORS_Fashion_House_Pillaged",
        "CSC_BAKERS_Cafe_UnderConstruction": "CSC_TAILORS_Fashion_House_UnderConstruction",
    }

    if clone_direct_entries(paths["strategic"], "BuildingEntries", strategic_buildings):
        changed.append(paths["strategic"])

    if clone_direct_entries(paths["strategic"], "Buildings", strategic_buildings):
        changed.append(paths["strategic"])

    if normalize_file(paths["strategic"]):
        changed.append(paths["strategic"])

    if clone_direct_entries(
        paths["buildings"],
        "Building",
        {
            "BUILDING_CSC_BAKERS_WIND_MILL": "BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP",
            "BUILDING_CSC_BAKERS_BAKERY": "BUILDING_CSC_TAILORS_TAILOR",
            "BUILDING_CSC_BAKERS_CAFE": "BUILDING_CSC_TAILORS_FASHION_HOUSE",
        },
    ):
        changed.append(paths["buildings"])

    if scaffold_landmarks():
        changed.append(paths["landmarks"])

    validate_xml(list(paths.values()))
    if changed:
        print("Updated:")
        for path in sorted(set(changed)):
            print(f"  {path.relative_to(ROOT)}")
    else:
        print("Tailors 3D artdef scaffold already present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
