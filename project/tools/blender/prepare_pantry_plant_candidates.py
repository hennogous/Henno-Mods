"""Stage a curated vegetation review without changing the live CSC library.

Run with Python: this.py OUTPUT --prepare
The output directory contains review-only source copies and Blender inputs.
"""
import importlib.util
import json
import re
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(sys.argv[1]).resolve()
GROUPS = {
    "Planters and hanging greenery": """IMP_Beach_Resort_PlantA IMP_Beach_Resort_PlantB IMP_Beach_Resort_Plantbox IMP_Beach_Resort_PlantPot Won_Bush_Planter Won_Hagia_Planter DIS_ThermalBath_Planter_A DIS_ThermalBath_Planter_C WON_Orszaghaz_Planter_A WON_Hanging_Planter_Foliage_L""",
    "Shrubs and flowering plants": """Cristo_shrub_a Cristo_shrub_c Shrub_01 Shrub_02 Shrub_Round_Single Shrub_Round_Sm Shrub_Round_Lg Shrub_Long Shrub_Round_Sm_Flowered_Color Shrub_Round_Single_Flowered_White Shrub_Long_Flowered_Color Shrub_semi-circle_C_Flowered_White Tree_Pink_Sm Tree_Trop_A_Flowered_White""",
    "Ground and wetland plants": """IMP_QuarryREDO_GrassTuft_A IMP_QuarryREDO_GrassTuft_C Jungle_Grass_01 Jungle_Grass_03 Jungle_Plant_01 Jungle_Plant_03 PantanalGrassA PantanalPlantA PantanalPlantC TER_River_Grass01 NWON_IkKil_FoliageA NWON_IkKil_VineA""",
    "Crops and productive plants": """RES_Banana_Tree_01 RES_Citrus_Tree01 RES_Cocoa_Tree01 RES_Coffee_01 RES_Cotton_01 RES_Rice_Tuft01 RES_Sugar_Plant01 RES_Tea_01 RES_Tobacco_Plant01 RES_Wheat_Tuft01 RES_Wine_Vine01 RES_Olives_Tree_01""",
    "Trees and palms": """Tree_A_Sm Tree_B_Sm Tree_C_Sm Tree_Trop_A Tree_Decid_01 Tree_Pine_01 Tree_StumpA Jungle_Palm_01 Jungle_PalmA PantanalTreeA PantanalTreeBushA WON_Great_Zimbabwe_Tree""",
}


def txt(element, path):
    node = element.find(path)
    return node.get("text", node.text or "") if node is not None else ""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source = ROOT / "project/tools/blender/export_prop_library.py"
    spec = importlib.util.spec_from_file_location("source_export", source)
    exp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exp)
    exp.STAGE = OUT / "work"
    exp.STAGE.mkdir(exist_ok=True)
    discovery = json.loads((OUT / "discovery.json").read_text())
    byid = {}
    for row in discovery["candidates"]:
        if not row["already_in_library"]:
            byid.setdefault(row["asset_id"], row)
    selected = []
    for category, names in GROUPS.items():
        for asset_id in names.split():
            row = byid[asset_id].copy()
            row["category"] = category
            ast = ET.fromstring(re.sub(r"(<\/?)([\w.]+):+", r"\1\2.", Path(row["source_ast"]).read_text(encoding="utf-8-sig")))
            row["models"] = [dict(geometry=txt(node, "m_GeoName"), instance=txt(node, "m_Name"), xml=ET.tostring(node, encoding="unicode"))
                             for node in ast.findall("m_GeometrySet/m_ModelInstances/Element")]
            visible = {}
            for model in row["models"]:
                for group in ET.fromstring(model["xml"]).findall("m_GroupStates/Element"):
                    if any(txt(value, "m_ParamName") == "Visible" and txt(value, "m_bValue") == "true"
                           for value in group.findall(".//Element")):
                        state = txt(group, "m_StateName")
                        visible[state] = visible.get(state, 0) + 1
            row["preview_state"] = next((state for state in ("Worked", "Unworked", "Construction", "Unbuilt", "Default") if visible.get(state)),
                                         next(iter(visible), "geometry only"))
            row["candidate_note"] = "Native " + row["preview_state"] + " state preview."
            selected.append(row)
    (OUT / "selection.json").write_text(json.dumps(selected, indent=2))
    index = {}
    for path in exp.SDK.rglob("*"):
        if path.suffix.lower() in (".ast", ".geo", ".fgx", ".mtl", ".dds", ".tex"):
            index.setdefault(path.name.lower(), []).append(str(path))
    (exp.STAGE / "file_index.json").write_text(json.dumps(index))
    print("Selected", len(selected), "review-only vegetation candidates", flush=True)
    if "--prepare" not in sys.argv:
        return
    prepared, materials, failed = [], {}, []
    for row in selected:
        (exp.STAGE / "inventory.json").write_text(json.dumps([row]))
        try:
            exp.prepare()
            result = json.loads((exp.STAGE / "CSC_Prop_Library/catalogue.json").read_text())
            prepared.extend(result["assets"])
            materials.update(result["materials"])
        except Exception as exc:
            failed.append(dict(asset_id=row["asset_id"], error=str(exc)))
            print("FAILED", row["asset_id"], str(exc), flush=True)
    (exp.STAGE / "CSC_Prop_Library/catalogue.json").write_text(json.dumps(dict(assets=prepared, materials=materials), indent=2))
    (OUT / "preparation-failures.json").write_text(json.dumps(failed, indent=2))
    print("PREPARED", len(prepared), "FAILED", len(failed), flush=True)


if __name__ == "__main__":
    main()
