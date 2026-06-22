#!/usr/bin/env python3
"""Export, validate, and patch ModBuddy action CDATA blocks.

ModBuddy stores ActionCriteriaData, FrontEndActionData, and InGameActionData as
minified XML inside CDATA. This tool lets CSC keep a readable JSON mirror and
regenerate those CDATA blocks instead of editing them by hand.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


BLOCKS = {
    "actionCriteria": {
        "property": "ActionCriteriaData",
        "root": "ActionCriteria",
    },
    "frontEndActions": {
        "property": "FrontEndActionData",
        "root": "FrontEndActions",
    },
    "inGameActions": {
        "property": "InGameActionData",
        "root": "InGameActions",
    },
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_project_path() -> Path:
    return project_root() / "Civ Supply Chains" / "Civ Supply Chains.civ6proj"


def default_json_path() -> Path:
    return project_root() / "project" / "modbuddy" / "CivSupplyChains.actions.json"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


def block_pattern(property_name: str) -> re.Pattern[str]:
    return re.compile(
        rf"(<{property_name}>\s*<!\[CDATA\[)(.*?)(\]\]>\s*</{property_name}>)",
        re.DOTALL,
    )


def extract_block(project_text: str, property_name: str) -> str:
    match = block_pattern(property_name).search(project_text)
    if not match:
        raise ValueError(f"Could not find {property_name} CDATA block")
    return match.group(2)


def replace_block(project_text: str, property_name: str, xml_text: str) -> str:
    pattern = block_pattern(property_name)
    if not pattern.search(project_text):
        raise ValueError(f"Could not find {property_name} CDATA block")
    return pattern.sub(lambda m: f"{m.group(1)}{xml_text}{m.group(3)}", project_text, count=1)


def parse_xml_fragment(xml_text: str, expected_root: str) -> ET.Element:
    root = ET.fromstring(xml_text)
    if root.tag != expected_root:
        raise ValueError(f"Expected <{expected_root}>, found <{root.tag}>")
    return root


def node_to_json(node: ET.Element) -> dict[str, Any]:
    result: dict[str, Any] = {"tag": node.tag}
    if node.attrib:
        result["attributes"] = dict(node.attrib)
    text = (node.text or "").strip()
    if text:
        result["text"] = text
    children = [node_to_json(child) for child in list(node)]
    if children:
        result["children"] = children
    return result


def json_to_node(data: dict[str, Any]) -> ET.Element:
    node = ET.Element(data["tag"], {str(k): str(v) for k, v in data.get("attributes", {}).items()})
    if "text" in data:
        node.text = str(data["text"])
    for child in data.get("children", []):
        node.append(json_to_node(child))
    return node


def properties_to_json(node: ET.Element) -> dict[str, str]:
    props: dict[str, str] = {}
    for child in list(node):
        props[child.tag] = (child.text or "")
    return props


def properties_to_node(properties: dict[str, Any]) -> ET.Element:
    node = ET.Element("Properties")
    for name, value in properties.items():
        child = ET.SubElement(node, name)
        child.text = str(value)
    return node


def action_to_json(node: ET.Element) -> dict[str, Any]:
    action: dict[str, Any] = {"type": node.tag}
    if "id" in node.attrib:
        action["id"] = node.attrib["id"]
    extra_attributes = {k: v for k, v in node.attrib.items() if k != "id"}
    if extra_attributes:
        action["attributes"] = extra_attributes

    criteria: list[str] = []
    files: list[Any] = []
    excludes: list[Any] = []
    extras: list[dict[str, Any]] = []

    for child in list(node):
        if child.tag == "Properties":
            action["properties"] = properties_to_json(child)
        elif child.tag == "Criteria":
            criteria.append((child.text or ""))
        elif child.tag == "File":
            file_text = child.text or ""
            files.append({"path": file_text, "attributes": dict(child.attrib)} if child.attrib else file_text)
        elif child.tag == "Exclude":
            excludes.append(dict(child.attrib))
        else:
            extras.append(node_to_json(child))

    if criteria:
        action["criteria"] = criteria
    if files:
        action["files"] = files
    if excludes:
        action["excludes"] = excludes
    if extras:
        action["extraChildren"] = extras
    return action


def action_from_json(action: dict[str, Any]) -> ET.Element:
    attributes = dict(action.get("attributes", {}))
    if "id" in action:
        attributes = {"id": str(action["id"]), **{str(k): str(v) for k, v in attributes.items()}}
    node = ET.Element(action["type"], attributes)

    if "properties" in action:
        node.append(properties_to_node(action["properties"]))
    for criterion in action.get("criteria", []):
        child = ET.SubElement(node, "Criteria")
        child.text = str(criterion)
    for file_entry in action.get("files", []):
        if isinstance(file_entry, str):
            child = ET.SubElement(node, "File")
            child.text = file_entry
        else:
            child = ET.SubElement(node, "File", {str(k): str(v) for k, v in file_entry.get("attributes", {}).items()})
            child.text = str(file_entry["path"])
    for exclude in action.get("excludes", []):
        ET.SubElement(node, "Exclude", {str(k): str(v) for k, v in exclude.items()})
    for child in action.get("extraChildren", []):
        node.append(json_to_node(child))
    return node


def criteria_to_json(root: ET.Element) -> list[dict[str, Any]]:
    return [node_to_json(child) for child in list(root)]


def criteria_from_json(items: list[dict[str, Any]]) -> ET.Element:
    root = ET.Element("ActionCriteria")
    for item in items:
        root.append(json_to_node(item))
    return root


def actions_to_json(root: ET.Element) -> list[dict[str, Any]]:
    return [action_to_json(child) for child in list(root)]


def actions_from_json(root_name: str, actions: list[dict[str, Any]]) -> ET.Element:
    root = ET.Element(root_name)
    for action in actions:
        root.append(action_from_json(action))
    return root


def xml_to_string(root: ET.Element) -> str:
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def export_json(project_path: Path) -> dict[str, Any]:
    project_text = read_text(project_path)
    try:
        source_project = project_path.resolve().relative_to(project_root()).as_posix()
    except ValueError:
        source_project = str(project_path)
    data: dict[str, Any] = {
        "schemaVersion": 1,
        "sourceProject": source_project,
        "blocks": {},
    }
    blocks = data["blocks"]
    for key, meta in BLOCKS.items():
        xml_text = extract_block(project_text, meta["property"])
        root = parse_xml_fragment(xml_text, meta["root"])
        if key == "actionCriteria":
            blocks[key] = criteria_to_json(root)
        else:
            blocks[key] = actions_to_json(root)
    return data


def xml_blocks_from_json(data: dict[str, Any]) -> dict[str, str]:
    blocks = data.get("blocks")
    if not isinstance(blocks, dict):
        raise ValueError("JSON must contain a 'blocks' object")

    rendered: dict[str, str] = {}
    for key, meta in BLOCKS.items():
        if key not in blocks:
            raise ValueError(f"JSON is missing blocks.{key}")
        if key == "actionCriteria":
            root = criteria_from_json(blocks[key])
        else:
            root = actions_from_json(meta["root"], blocks[key])
        rendered[key] = xml_to_string(root)
    return rendered


def patch_project_text(project_text: str, data: dict[str, Any]) -> str:
    patched = project_text
    for key, xml_text in xml_blocks_from_json(data).items():
        patched = replace_block(patched, BLOCKS[key]["property"], xml_text)
    return patched


def canonical_data(data: dict[str, Any]) -> dict[str, Any]:
    clone = copy.deepcopy(data)
    clone.pop("sourceProject", None)
    return clone


def validate(project_path: Path, json_path: Path) -> None:
    data = json.loads(read_text(json_path))
    patched_text = patch_project_text(read_text(project_path), data)

    temp_path = project_path.with_suffix(project_path.suffix + ".tmp-check")
    try:
        write_text(temp_path, patched_text)
        patched_data = canonical_data(export_json(temp_path))
    finally:
        if temp_path.exists():
            temp_path.unlink()

    json_data = canonical_data(data)
    json_data.setdefault("schemaVersion", 1)
    if patched_data != json_data:
        raise ValueError("JSON did not round-trip through generated CDATA")


def patch(project_path: Path, json_path: Path) -> bool:
    data = json.loads(read_text(json_path))
    original = read_text(project_path)
    patched = patch_project_text(original, data)
    if original == patched:
        return False
    write_text(project_path, patched)
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=("export", "check", "patch"),
        help="export JSON, verify JSON matches the project, or patch the project from JSON",
    )
    parser.add_argument("--project", type=Path, default=default_project_path(), help="Path to the .civ6proj file")
    parser.add_argument("--json", type=Path, default=default_json_path(), help="Path to the action JSON file")
    args = parser.parse_args(argv)

    try:
        if args.command == "export":
            data = export_json(args.project)
            args.json.parent.mkdir(parents=True, exist_ok=True)
            write_text(args.json, json.dumps(data, indent=2) + "\n")
            print(f"Exported {args.json}")
        elif args.command == "check":
            validate(args.project, args.json)
            print("JSON can regenerate ModBuddy action CDATA blocks")
        elif args.command == "patch":
            changed = patch(args.project, args.json)
            print("Patched project CDATA blocks" if changed else "Project already matches JSON")
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
