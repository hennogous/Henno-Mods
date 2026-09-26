"""Promote reviewed Pantry plants to the CSC Blender prop library.

Python: this.py prepare|install
Blender: --python this.py -- build|verify-live
The review selection is numbered 01-50; 14, 20 and 45 were rejected by Henno.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
REVIEW = Path("C:/Users/Shadow/.codex/visualizations/2026/09/25/01a0d6f1-68f7-7631-ad15-3495800970cb/pantry-plants")
SOURCE = REVIEW / "work/CSC_Prop_Library"
STAGE = REVIEW / "approved-library-intake"
LIVE = Path("C:/Users/Shadow/Desktop/Working Files/3D Art/Props/CSC_Prop_Library")
SDK = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
TOOLS = ROOT / "project/tools/blender"
REJECTED_NUMBERS = {14, 20, 45}
MODE = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else sys.argv[1]


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def nested_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from nested_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from nested_strings(item)


def txt(element, path):
    node = element.find(path)
    return node.get("text", node.text or "") if node is not None else ""


def state_behaviour(row):
    result = {}
    for state in ("Construction", "Pillaged"):
        bindings = []
        for model in row["models"]:
            for group in ET.fromstring(model["xml"]).findall("m_GroupStates/Element"):
                if txt(group, "m_StateName") != state:
                    continue
                values = {txt(value, "m_ParamName"): txt(value, "m_ObjectName") or txt(value, "m_bValue")
                          for value in group.findall("m_Values/m_Values/Element")}
                bindings.append(dict(geometry=model["geometry"], mesh=txt(group, "m_MeshName"),
                                     group=txt(group, "m_GroupName"), values=values))
        visible = [binding for binding in bindings if binding["values"].get("Visible") == "true"]
        materials = sorted({binding["values"].get("Material", "") for binding in visible} - {""})
        note = (f"{len(visible)} explicitly visible / {len(bindings)} group bindings; materials: "
                + (", ".join(materials) or "none explicitly visible") + ".") if bindings else "No explicit group-state bindings."
        result[state] = dict(note=note, bindings=bindings,
                             verification="Source AST metadata only; not tested in Asset Editor or game.")
    return result


def native_bindings(ids):
    bindings = {asset_id.lower(): [] for asset_id in ids}
    seen = set()
    for manifest in ("civ6", "expansion1", "expansion2"):
        for entry in read(SDK / (manifest + "-asset-deps.json"))["Files"]:
            path = SDK / entry["Filename"]
            if path.suffix.lower() != ".xlp" or str(path).lower() in seen or not path.is_file():
                continue
            seen.add(str(path).lower())
            try:
                root = ET.parse(path).getroot()
            except ET.ParseError:
                continue
            for element in root.findall("m_Entries/Element"):
                asset_id = txt(element, "m_ObjectName")
                if asset_id.lower() in bindings:
                    bindings[asset_id.lower()].append(dict(xlp=str(path.relative_to(SDK)),
                        entry_id=txt(element, "m_EntryID"), asset_class=txt(root, "m_ClassName"),
                        package=txt(root, "m_PackageName")))
    return bindings


if MODE == "prepare":
    index = read(REVIEW / "candidate-index.json")
    approved = {row["asset_id"]: row for row in index["candidates"] if row["number"] not in REJECTED_NUMBERS}
    rejected = {row["asset_id"] for row in index["candidates"] if row["number"] in REJECTED_NUMBERS}
    assert len(index["candidates"]) == 50 and len(approved) == 47 and len(rejected) == 3
    assert rejected == {"Shrub_Round_Sm_Flowered_Color", "IMP_QuarryREDO_GrassTuft_C", "Tree_StumpA"}
    data = read(REVIEW / "candidate-catalogue.json")
    data["assets"] = [row for row in data["assets"] if row["asset_id"] in approved]
    assert len(data["assets"]) == 47
    bindings = native_bindings(approved)
    for row in data["assets"]:
        review = approved[row["asset_id"]]
        row["category"] = review["category"]
        row["state_behavior"] = state_behaviour(row)
        row["native_bindings"] = bindings[row["asset_id"].lower()]
        row["intake_note"] = "Approved from plant contact sheet; entries 14, 20 and 45 excluded."
        row["dimension_units"] = "Source geometry units; identical Blender units; visible " + row["preview_state"] + "-state asset-local bounds"
        row["pivot"] = [0, 0, 0]
    material_ids = {material for row in data["assets"] for material in row["material_ids"]}
    data["materials"] = {key: value for key, value in data["materials"].items() if key in material_ids}
    STAGE.mkdir(exist_ok=False)
    paths = {value for value in nested_strings(data) if value.startswith(("sources/", "textures/")) and (SOURCE / value).is_file()}
    for row in data["assets"]:
        for texture_id, dds in row["textures"].items():
            for path in (Path(dds).with_suffix(".png"), Path("sources/textures") / (texture_id + ".tex")):
                if (SOURCE / path).is_file():
                    paths.add(path.as_posix())
    for relative in paths:
        target = STAGE / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(SOURCE / relative, target)
    write(STAGE / "catalogue.json", data)
    write(REVIEW / "plant-intake-selection.json", dict(approved=sorted(approved), rejected=sorted(rejected),
                                                    unpreviewed=sorted(row["asset_id"] for row in index["unpreviewed"])))
    print("STAGED", len(data["assets"]), "plants,", len(paths), "source dependencies", flush=True)

elif MODE == "build":
    import bpy
    sys.argv = ["plant-intake", "--", str(STAGE)]
    source = TOOLS / "build_prop_library_blends.py"
    code = source.read_text(encoding="utf-8").split("for row in data['assets']:")[0]
    code = code.replace("s['state']=='Worked'", "s['state']==row.get('preview_state','Worked')")
    code = code.replace("obj['default_state']='Worked'", "obj['default_state']=row.get('preview_state','Worked')")
    namespace = {"__file__": str(source), "__name__": "plant_intake_builder"}
    exec(compile(code, str(source), "exec"), namespace)
    base_material = namespace["material"]

    def material(name, row):
        result = base_material(name, row)
        nodes, links = result.node_tree.nodes, result.node_tree.links
        for channel in ("AO", "Gloss", "Metalness", "Opacity"):
            texture = nodes.get(channel)
            if not texture:
                continue
            outgoing = list(texture.outputs["Color"].links)
            if not outgoing:
                continue
            separate = nodes.new("ShaderNodeSeparateColor")
            separate.mode = "RGB"
            links.new(texture.outputs["Color"], separate.inputs["Color"])
            for link in outgoing:
                destination = link.to_socket
                links.remove(link)
                links.new(separate.outputs["Red"], destination)
        if result.get("source_shader") == "DecalMaterial" and nodes.get("BaseColor"):
            links.new(nodes["BaseColor"].outputs["Alpha"], nodes["Principled BSDF"].inputs["Alpha"])
        return result

    namespace["material"] = material
    for row in namespace["data"]["assets"]:
        namespace["build"](row)
        row["material_conversion_notes"] = ["Original source texture bindings retained. Blender scalar maps use red and decals use source alpha; native Firaxis effects remain metadata."] + row["issues"]
        row["source_model_transforms"] = {model["geometry"]: read(STAGE / model["extracted"])["models"] for model in row["models"]}
    write(STAGE / "catalogue.json", namespace["data"])
    exec(compile((TOOLS / "verify_prop_library.py").read_text(encoding="utf-8"), str(TOOLS / "verify_prop_library.py"), "exec"), {"__name__": "plant_intake_verify"})

elif MODE == "install":
    data = read(STAGE / "catalogue.json")
    live = read(LIVE / "catalogue.json")
    assert len(data["assets"]) == 47 and all(row["verification"]["status"] == "passed" for row in data["assets"])
    approved = set(read(REVIEW / "plant-intake-selection.json")["approved"])
    assert {row["asset_id"] for row in data["assets"]} == approved
    assert not approved & {row["asset_id"] for row in live["assets"]}, "Asset ID collision with existing library"
    collisions = []
    for path in STAGE.rglob("*"):
        if not path.is_file() or path.name in {"catalogue.json", "verification.json"}:
            continue
        target = LIVE / path.relative_to(STAGE)
        if target.exists() and digest(path) != digest(target):
            collisions.append(str(target))
    for key, value in data["materials"].items():
        if key in live["materials"] and live["materials"][key] != value:
            collisions.append("material " + key)
    assert not collisions, collisions
    backup = STAGE / "pre-intake-live-metadata"
    backup.mkdir(exist_ok=False)
    for name in ("catalogue.json", "verification.json", "README.md", "STATE_BEHAVIOR.md"):
        if (LIVE / name).is_file():
            shutil.copy2(LIVE / name, backup / name)
    old_blends = {path.name: digest(path) for path in LIVE.glob("*.blend")}
    old_count = len(live["assets"])
    for path in STAGE.rglob("*"):
        if not path.is_file() or path.name in {"catalogue.json", "verification.json"} or backup in path.parents:
            continue
        target = LIVE / path.relative_to(STAGE)
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(path, target)
    live["assets"].extend(data["assets"])
    live["materials"].update(data["materials"])
    write(LIVE / "catalogue.json", live)
    existing_verification = read(backup / "verification.json") if (backup / "verification.json").is_file() else []
    write(LIVE / "verification.json", existing_verification + read(STAGE / "verification.json"))
    with (LIVE / "STATE_BEHAVIOR.md").open("a", encoding="utf-8") as file:
        file.write("\n## Pantry plant intake — 25 September 2026\n\nSource AST metadata only; native runtime states remain untested.\n\n| Asset | Construction | Pillaged |\n|---|---|---|\n")
        for row in data["assets"]:
            file.write("| " + row["asset_id"] + " | " + row["state_behavior"]["Construction"]["note"] + " | " + row["state_behavior"]["Pillaged"]["note"] + " |\n")
    with (LIVE / "README.md").open("a", encoding="utf-8") as file:
        file.write("\n## Pantry plant intake — 25 September 2026\n\nAdded 47 approved native vegetation assets from the plant contact sheets. Review entries 14, 20 and 45 were excluded; ten extraction failures remain outside the library. Source IDs, geometry, UVs, normals, transforms, state components and texture bindings were retained. Blender shader nodes interpret scalar maps and decal alpha for review. No custom CSC asset registrations were added; native runtime placement remains to be checked in context.\n")
    assert all(digest(LIVE / name) == sha for name, sha in old_blends.items())
    report = dict(added=sorted(approved), rejected=read(REVIEW / "plant-intake-selection.json")["rejected"],
                  existing_blends_preserved=len(old_blends), previous_catalogue_entries=old_count,
                  catalogue_entries=len(live["assets"]), blend_files=len(list(LIVE.glob("*.blend"))))
    write(REVIEW / "plant-intake-install-report.json", report)
    print("INSTALLED", len(approved), "plants; preserved", len(old_blends), "existing blends", flush=True)

elif MODE == "verify-live":
    approved = set(read(REVIEW / "plant-intake-selection.json")["approved"])
    source = (TOOLS / "verify_prop_library.py").read_text(encoding="utf-8")
    source = source.replace("data=json.loads((LIB/'catalogue.json').read_text())",
                            "data=json.loads((LIB/'catalogue.json').read_text()); data['assets']=[r for r in data['assets'] if r['asset_id'] in " + repr(approved) + "]")
    source = source.replace("(LIB/'verification.json').write_text(json.dumps(reports,indent=2))",
                            "(pathlib.Path(" + repr(str(REVIEW)) + ")/'plant-intake-live-verification.json').write_text(json.dumps(reports,indent=2))")
    source = source.replace("(LIB/'catalogue.json').write_text(json.dumps(data,indent=2))", "")
    sys.argv = ["plant-live-verify", "--", str(LIVE)]
    exec(compile(source, str(TOOLS / "verify_prop_library.py"), "exec"), {"__name__": "plant_live_verify"})

else:
    raise ValueError(MODE)
