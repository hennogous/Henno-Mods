"""List vegetation-related ASTs in the Civ VI base and expansion pantries.

Usage: python discover_pantry_plants.py OUTPUT_JSON
This is discovery only; it does not alter the CSC prop library.
"""
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

SDK = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
LIB = Path("C:/Users/Shadow/Desktop/Working Files/3D Art/Props/CSC_Prop_Library/catalogue.json")
PATTERN = re.compile(
    r"tree|bush|shrub|plant|flower|grass|vine|fern|palm|cactus|crop|reed|ivy|moss|"
    r"sapling|hedge|bramble|bamboo|orchard|garden|foliage|vegetation|leaf|leaves|"
    r"agave|aloe|acacia|baobab|birch|cedar|cypress|elm|eucalyptus|fir(?:_|$)|"
    r"juniper|mangrove|maple|oak|olive|pine|poplar|redwood|spruce|willow|"
    r"wheat|rice|cotton|tobacco|banana|cocoa|coffee|tea(?:_|$)|sugar|maize|corn|"
    r"potato|grape|lotus|lily|tulip|rose|papyrus|date(?:_|$)", re.I)


def txt(element, path):
    node = element.find(path)
    return node.get("text", node.text or "") if node is not None else ""


def main():
    owned = {row["asset_id"].lower() for row in json.loads(LIB.read_text())["assets"]}
    files = {}
    for key, pack in (("civ6", "Base game"), ("expansion1", "Rise and Fall"), ("expansion2", "Gathering Storm")):
        manifest = key + "-asset-deps.json"
        data = json.loads((SDK / manifest).read_text())
        for entry in data["Files"]:
            rel = entry["Filename"]
            if Path(rel).suffix.lower() == ".ast":
                files.setdefault(rel.lower(), (rel, pack, manifest))
    rows, errors = [], []
    for rel, pack, manifest in files.values():
        path = SDK / rel
        if not path.is_file():
            continue
        name = path.stem
        try:
            root = ET.fromstring(re.sub(r"(<\/?)([\w.]+):+", r"\1\2.", path.read_text(encoding="utf-8-sig")))
            geometry = [txt(node, "m_GeoName") for node in root.findall("m_GeometrySet/m_ModelInstances/Element")]
            matched_name = bool(PATTERN.search(name))
            matched_geo = bool(PATTERN.search(" ".join(geometry)))
            if not matched_name and not matched_geo:
                continue
            rows.append(dict(asset_id=name, source_pack=pack, source_ast=str(path),
                             provenance=dict(manifest=manifest, path=rel), asset_class=txt(root, "m_ClassName"),
                             geometry_ids=geometry, matched_name=matched_name,
                             matched_geometry=matched_geo, already_in_library=name.lower() in owned))
        except Exception as exc:
            errors.append(dict(path=rel, error=str(exc)))
    rows.sort(key=lambda r: (r["source_pack"], r["asset_id"].lower()))
    result = dict(package_ast_count=len(files), matched_count=len(rows), errors=errors, candidates=rows)
    Path(sys.argv[1]).write_text(json.dumps(result, indent=2))
    print(f"Scanned {len(files)} ASTs; {len(rows)} name/geometry matches; {len(errors)} parse errors")
    for row in rows:
        print(f"{row['asset_id']} | {row['source_pack']} | {row['asset_class']} | {','.join(row['geometry_ids'])}")


if __name__ == "__main__":
    main()
