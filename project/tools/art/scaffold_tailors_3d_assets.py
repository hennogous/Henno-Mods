#!/usr/bin/env python3
"""Scaffold Tailors' Quarter 3D assets from the Bakers' Quarter kit.

This script creates the Tailors placeholder AST/material files, prunes the
Bakers-only prop attachment points noted in the Tailors 3D scaffold plan, adds
the new TileBase XLP entries, and mirrors the same additions into AssetCloud's
dependency cache so Asset Editor can browse them.
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "Civ Supply Chains"
ASSETS = MOD / "Assets"
MATERIALS = MOD / "Materials"
XLP = MOD / "XLPs" / "CSC_Tilebases.xlp"
CACHE = Path(os.environ["APPDATA"]) / "AssetCloud" / "mod-Civ Supply Chains-asset-deps.json"
FILETIME_EPOCH_OFFSET = 116_444_736_000_000_000


@dataclass(frozen=True)
class Block:
    start: int
    end: int
    parent: int | None
    name: str | None


STRUCT_OPEN = re.compile(r"^\s*<Element(?:\s|>)")
STRUCT_CLOSE = re.compile(r"^\s*</Element>\s*$")
NAME_RE = re.compile(r'<m_Name text="([^"]*)"')
ENTRY_RE = re.compile(r'<m_EntryID text="([^"]*)"')


BASE_ASSETS = {
    "CSC_BAKERS_Ancient_Base_01": "CSC_TAILORS_Ancient_Base_01",
    "CSC_BAKERS_Classical_Base_01": "CSC_TAILORS_Classical_Base_01",
    "CSC_BAKERS_Classical_Base_02": "CSC_TAILORS_Classical_Base_02",
    "CSC_BAKERS_Classical_Base_03": "CSC_TAILORS_Classical_Base_03",
    "CSC_BAKERS_Classical_Base_04": "CSC_TAILORS_Classical_Base_04",
    "CSC_BAKERS_Classical_Base_05": "CSC_TAILORS_Classical_Base_05",
}

STORAGE_ASSETS = {
    "CSC_BAKERS_Storage_S": "CSC_TAILORS_Storage_S",
    "CSC_BAKERS_Storage_M": "CSC_TAILORS_Storage_M",
    "CSC_BAKERS_Storage_L": "CSC_TAILORS_Storage_L",
}

BUILDING_ASSETS = {
    "CSC_BAKERS_Wind_Mill": "CSC_TAILORS_Textile_Workshop",
    "CSC_BAKERS_Bakery": "CSC_TAILORS_Tailor",
    "CSC_BAKERS_Cafe": "CSC_TAILORS_Fashion_House",
}

WELL_ASSET = {"CSC_BAKERS_Well": "CSC_TAILORS_Well"}

MATERIALS_TO_CLONE = {
    "CSC_BAKERS_E": "CSC_TAILORS_E",
    "CSC_BAKERS_NE": "CSC_TAILORS_NE",
    "CSC_BAKERS_Well": "CSC_TAILORS_Well",
}

STORAGE_KEEP = {
    "CSC_TAILORS_Storage_S": {"newAttachmentPoint_1", "newAttachmentPoint_9", "newAttachmentPoint_10", "newAttachmentPoint_11"},
    "CSC_TAILORS_Storage_M": {"newAttachmentPoint_1", "newAttachmentPoint_2", "newAttachmentPoint_14", "newAttachmentPoint_15"},
    "CSC_TAILORS_Storage_L": {"newAttachmentPoint_1", "newAttachmentPoint_2", "newAttachmentPoint_3", "newAttachmentPoint_42", "newAttachmentPoint_43"},
}

UNWANTED_BASE_REFERENCES = ("CSC_BAKERS_Flour", "IMP_Cree_Mekewap_Mill")

REPLACEMENTS = [
    ("CSC_BAKERS_Wind_Mill", "CSC_TAILORS_Textile_Workshop"),
    ("CSC_BAKERS_Bakery", "CSC_TAILORS_Tailor"),
    ("CSC_BAKERS_Cafe", "CSC_TAILORS_Fashion_House"),
    ("CSC_BAKERS_Well", "CSC_TAILORS_Well"),
    ("CSC_BAKERS_Storage_S", "CSC_TAILORS_Storage_S"),
    ("CSC_BAKERS_Storage_M", "CSC_TAILORS_Storage_M"),
    ("CSC_BAKERS_Storage_L", "CSC_TAILORS_Storage_L"),
    ("CSC_BAKERS_E", "CSC_TAILORS_E"),
    ("CSC_BAKERS_NE", "CSC_TAILORS_NE"),
    ("CSC_Atlas_B_BAKERS", "CSC_Atlas_B_TAILORS"),
    ("CSC_BAKERS", "CSC_TAILORS"),
    ("BAKERS", "TAILORS"),
    ("Bakers", "Tailors"),
    ("Wind_Mill", "Textile_Workshop"),
    ("Wind Mill", "Textile Workshop"),
    ("Bakery", "Tailor"),
    ("Cafe", "Fashion House"),
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> bool:
    old = path.read_text(encoding="utf-8-sig") if path.exists() else None
    if old == text:
        return False
    path.write_text(text, encoding="utf-8", newline="")
    return True


def replace_many(text: str, replacements: list[tuple[str, str]]) -> str:
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def discover_blocks(lines: list[str]) -> dict[int, Block]:
    stack: list[int] = []
    raw: dict[int, dict[str, object]] = {}
    blocks: dict[int, Block] = {}
    for idx, line in enumerate(lines):
        if STRUCT_OPEN.match(line):
            raw[idx] = {"parent": stack[-1] if stack else None, "name": None}
            stack.append(idx)
            continue

        if stack and (match := NAME_RE.search(line)):
            raw[stack[-1]]["name"] = match.group(1)

        if STRUCT_CLOSE.match(line):
            if not stack:
                raise ValueError(f"Unmatched </Element> at line {idx + 1}")
            start = stack.pop()
            blocks[start] = Block(start=start, end=idx, parent=raw[start]["parent"], name=raw[start]["name"])  # type: ignore[arg-type]
    if stack:
        raise ValueError("Unclosed <Element> block(s)")
    return blocks


def remove_line_blocks(text: str, predicate) -> str:
    lines = text.splitlines(keepends=True)
    blocks = discover_blocks(lines)
    remove: set[int] = set()
    for block in blocks.values():
        block_text = "".join(lines[block.start : block.end + 1])
        if predicate(block, block_text):
            remove.update(range(block.start, block.end + 1))
    return "".join(line for idx, line in enumerate(lines) if idx not in remove)


def prune_unwanted_attachment_refs(text: str, needles: tuple[str, ...]) -> str:
    return remove_line_blocks(
        text,
        lambda _block, block_text: '<m_Name text="newAttachmentPoint_' in block_text
        and any(f'<m_EntryName text="{needle}' in block_text for needle in needles),
    )


def prune_storage_attachment_points(text: str, keep: set[str]) -> str:
    return remove_line_blocks(
        text,
        lambda block, block_text: block.name is not None
        and block.name.startswith("newAttachmentPoint_")
        and "<m_BoneName" in block_text
        and block.name not in keep,
    )


def clone_ast(source_name: str, target_name: str, *, prune_base: bool = False, storage_keep: set[str] | None = None) -> tuple[Path, bool]:
    source = ASSETS / f"{source_name}.ast"
    target = ASSETS / f"{target_name}.ast"
    if not source.exists():
        raise FileNotFoundError(source)
    text = read_text(source)
    if prune_base:
        text = prune_unwanted_attachment_refs(text, UNWANTED_BASE_REFERENCES)
    if storage_keep is not None:
        text = prune_storage_attachment_points(text, storage_keep)
        text = prune_unwanted_attachment_refs(text, ("CSC_BAKERS_Flour",))
    text = replace_many(text, REPLACEMENTS)
    return target, write_text(target, text)


def clone_material(source_name: str, target_name: str) -> tuple[Path, bool]:
    source = MATERIALS / f"{source_name}.mtl"
    target = MATERIALS / f"{target_name}.mtl"
    if not source.exists():
        raise FileNotFoundError(source)
    text = read_text(source)
    if source_name in {"CSC_BAKERS_E", "CSC_BAKERS_NE"}:
        text = replace_many(text, REPLACEMENTS)
    else:
        text = text.replace(f'<m_Name text="{source_name}"', f'<m_Name text="{target_name}"')
    return target, write_text(target, text)


def existing_xlp_entries() -> set[str]:
    text = read_text(XLP)
    return set(ENTRY_RE.findall(text))


def update_xlp(names: list[str]) -> bool:
    text = read_text(XLP)
    existing = existing_xlp_entries()
    additions = []
    for name in names:
        if name in existing:
            continue
        additions.append(
            "\t\t<Element>\n"
            f"\t\t\t<m_EntryID text=\"{name}\"/>\n"
            f"\t\t\t<m_ObjectName text=\"{name}\"/>\n"
            "\t\t</Element>\n"
        )
    if not additions:
        return False
    text = text.replace("\t</m_Entries>\n", "".join(additions) + "\t</m_Entries>\n", 1)
    return write_text(XLP, text)


def to_repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def filetime(path: Path) -> int:
    return int(path.stat().st_mtime * 10_000_000) + FILETIME_EPOCH_OFFSET


def clone_dependency_path(path: str) -> str | None:
    if "CSC_BAKERS_Flour" in path or "IMP_Cree_Mekewap_Mill" in path:
        return None
    if path.endswith("CSC_BAKERS_Well.tex"):
        return path
    return replace_many(path, REPLACEMENTS)


def update_asset_cache(created_paths: list[Path]) -> bool:
    if not CACHE.exists():
        return False

    data = json.loads(CACHE.read_text(encoding="utf-8-sig"))
    deps: dict[str, list[str]] = data.setdefault("Dependencies", {})
    files: list[dict[str, object]] = data.setdefault("Files", [])
    file_by_name = {item.get("Filename"): item for item in files}
    changed = False

    source_to_target = {
        **BASE_ASSETS,
        **STORAGE_ASSETS,
        **BUILDING_ASSETS,
        **WELL_ASSET,
        **MATERIALS_TO_CLONE,
    }

    for source_name, target_name in source_to_target.items():
        folder = "Materials" if source_name in MATERIALS_TO_CLONE else "Assets"
        ext = "mtl" if folder == "Materials" else "ast"
        source_key = f"Civ Supply Chains/{folder}/{source_name}.{ext}"
        target_key = f"Civ Supply Chains/{folder}/{target_name}.{ext}"
        source_deps = deps.get(source_key)
        if source_deps is not None:
            target_deps = [new for dep in source_deps if (new := clone_dependency_path(dep)) is not None]
            if deps.get(target_key) != target_deps:
                deps[target_key] = target_deps
                changed = True

        source_file = file_by_name.get(source_key)
        target_path = ROOT / target_key
        if source_file and target_path.exists():
            item = dict(source_file)
            item["Filename"] = target_key
            item["Timestamp"] = filetime(target_path)
            item["Filesize"] = target_path.stat().st_size
            if file_by_name.get(target_key) != item:
                if target_key in file_by_name:
                    file_by_name[target_key].update(item)
                else:
                    files.append(item)
                    file_by_name[target_key] = item
                changed = True

    if changed:
        data["Timestamp"] = int(time.time() * 10_000_000) + FILETIME_EPOCH_OFFSET
        CACHE.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    return changed


def validate_xml(paths: list[Path]) -> None:
    for path in paths:
        ET.parse(path)


def main() -> int:
    changed: list[Path] = []
    generated: list[Path] = []

    for source, target in BASE_ASSETS.items():
        path, did_change = clone_ast(source, target, prune_base=True)
        generated.append(path)
        if did_change:
            changed.append(path)

    for source, target in STORAGE_ASSETS.items():
        path, did_change = clone_ast(source, target, storage_keep=STORAGE_KEEP[target])
        generated.append(path)
        if did_change:
            changed.append(path)

    for source, target in {**BUILDING_ASSETS, **WELL_ASSET}.items():
        path, did_change = clone_ast(source, target)
        generated.append(path)
        if did_change:
            changed.append(path)

    for source, target in MATERIALS_TO_CLONE.items():
        path, did_change = clone_material(source, target)
        generated.append(path)
        if did_change:
            changed.append(path)

    xlp_names = list(BASE_ASSETS.values()) + list(STORAGE_ASSETS.values()) + list(BUILDING_ASSETS.values()) + list(WELL_ASSET.values())
    if update_xlp(xlp_names):
        changed.append(XLP)

    if update_asset_cache(generated):
        changed.append(CACHE)

    validate_xml(generated + [XLP])
    if changed:
        print("Updated:")
        for path in changed:
            label = str(path if path == CACHE else path.relative_to(ROOT))
            print(f"  {label}")
    else:
        print("Tailors 3D assets already scaffolded.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
