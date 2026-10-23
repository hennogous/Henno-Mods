"""Stage or install a Base 03-only split-donkey experiment, preserving crane/cargo data."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time

from lxml import etree as E
from storage_pivot_trial import parse, txt, parameter, save, POINTS, MODELS, BINDINGS

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT/"Civ Supply Chains"
CHILD = "CSC_TRIAL_Delivery_Donkey"
PARENT = "CSC_TRIAL_BAKERS_Delivery_Split"
BASE = "CSC_BAKERS_Classical_Base_03"
ORIGINAL = "CSC_BAKERS_Storage_Delivery"


def stage(out):
    checks = json.loads((out/"split-check.json").read_text())
    assert max(checks["source_errors"].values()) < .002
    assert max(checks["native_errors"].values()) < .4
    before = out/"before"
    before.mkdir(exist_ok=True)
    for rel in (f"Assets/{BASE}.ast", f"Assets/{ORIGINAL}.ast",
                "Geometries/CSC_ALL_Delivery_Pivot.fgx", "Animations/CSC_ALL_Delivery_Pivot.fgx"):
        target = before/rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            assert target.read_bytes() == (MOD/rel).read_bytes(), f"Baseline changed: {rel}"
        else:
            shutil.copy2(MOD/rel, target)
    original = parse(MOD/f"Assets/{ORIGINAL}.ast")
    parent = copy.deepcopy(original)
    parent.find("m_Name").set("text", PARENT)
    parent.find("m_BehaviorData/m_dsgName").set("text", "Standard_LandmarkNoRandomOffset")
    original_model = original.find(MODELS)[0]
    hidden = 0
    for state in parent.find(MODELS)[0].find("m_GroupStates"):
        if "Donkey" in txt(state, "m_MeshName"):
            for e in state.findall("m_Values/m_Values/Element"):
                if txt(e, "m_ParamName") == "Visible":
                    e.find("m_bValue").text = "false"
                    hidden += 1
    assert hidden == 5, hidden
    cargo = parent.find(POINTS)[0]
    point = copy.deepcopy(cargo)
    point.find("m_Name").set("text", "Donkey_TerrainTrial")
    point.find("m_BoneName").set("text", "DonkeyPath")
    parameter(point, "Asset").find("m_EntryName").set("text", CHILD)
    parameter(point, "RandomizeAnims").find("m_bValue").text = "false"
    parameter(point, "TerrainFollowMode").find("m_Value").set("text", "Pivot Height")
    for field in ("m_position", "m_orientation"):
        for axis in "xyz":
            point.find(field+"/"+axis).text = "0.000000"
    point.find("m_scale").text = "1.000000"
    parent.find(POINTS).append(point)
    assert E.tostring(cargo) == E.tostring(original.find(POINTS)[0])
    assert E.tostring(parent.find(BINDINGS)) == E.tostring(original.find(BINDINGS))
    save(parent, out/f"staged/Assets/{PARENT}.ast")
    # Child uses the original donkey material/state definitions and no cargo.
    child = copy.deepcopy(original)
    child.find("m_Name").set("text", CHILD)
    child.find("m_BehaviorData/m_dsgName").set("text", "Standard_LandmarkNoRandomOffset")
    child.find(POINTS).clear()
    for binding in child.findall(".//m_AnimationName"):
        binding.set("text", CHILD)
    model = child.find(MODELS)[0]
    descriptor = parse(out/f"staged/Geometries/{CHILD}.geo")
    model.find("m_Name").set("text", txt(descriptor, "m_ModelName"))
    model.find("m_GeoName").set("text", CHILD)
    geo_mesh = descriptor.find("m_Meshes/Element")
    assert len(descriptor.find("m_Meshes")) == 1
    states = model.find("m_GroupStates")
    for state in list(states):
        if "Donkey" not in txt(state, "m_MeshName"):
            states.remove(state)
        else:
            state.find("m_MeshName").set("text", txt(geo_mesh, "m_Name"))
            state.find("m_GroupName").set("text", txt(geo_mesh.find("m_Groups/Element"), "m_Name"))
    assert len(states) == 5
    save(child, out/f"staged/Assets/{CHILD}.ast")
    base = parse(MOD/f"Assets/{BASE}.ast")
    matches = [p for p in base.find(POINTS) if parameter(p, "Asset").find("m_EntryName").get("text") == ORIGINAL]
    assert len(matches) == 1
    parameter(matches[0], "Asset").find("m_EntryName").set("text", PARENT)
    parameter(matches[0], "RandomizeAnims").find("m_bValue").text = "false"
    save(base, out/f"staged/Assets/{BASE}.ast")
    report = dict(parent=PARENT, child=CHILD, base=BASE, cargo_attachment_unchanged=True,
                  parent_animation_binding_unchanged=True, hidden_parent_donkey_states=hidden,
                  child_states=len(states), phase_randomization=False,
                  original_binary_hashes={rel:hashlib.sha256((before/rel).read_bytes()).hexdigest()
                    for rel in ("Geometries/CSC_ALL_Delivery_Pivot.fgx", "Animations/CSC_ALL_Delivery_Pivot.fgx")})
    (out/"assembly-check.json").write_text(json.dumps(report, indent=2))
    print("STAGED", json.dumps(report))


def install(out):
    stage_root = out/"staged"
    payload = [p for p in stage_root.rglob("*") if p.suffix in (".ast", ".fgx", ".geo", ".anm")]
    assert json.loads((out/"assembly-check.json").read_text())["cargo_attachment_unchanged"]
    for p in payload:
        target = MOD/p.relative_to(stage_root)
        if target.exists():
            backup = out/"before"/p.relative_to(stage_root)
            assert (backup.exists() and target.read_bytes() == backup.read_bytes()) or target.read_bytes() == p.read_bytes(), target
    # Prepare packaging and dependency registration before changing live files.
    xlp = MOD/"XLPs/CSC_Tilebases.xlp"
    xlp_raw = xlp.read_bytes()
    entries = []
    for name in (CHILD, PARENT):
        if f'text="{name}"'.encode() not in xlp_raw:
            entries.append(f'\t\t<Element>\r\n\t\t\t<m_EntryID text="{name}"/>\r\n'
                           f'\t\t\t<m_ObjectName text="{name}"/>\r\n\t\t</Element>\r\n')
    xlp_new, count = re.subn(rb"(?m)^[ \t]*</m_Entries>", "".join(entries).encode()+b"\t</m_Entries>", xlp_raw)
    assert count == 1
    project = MOD/"Civ Supply Chains.civ6proj"
    project_raw = project.read_bytes()
    entries = []
    for p in payload:
        rel = str(p.relative_to(stage_root)).replace("/", "\\")
        if f'Include="{rel}"'.encode() not in project_raw:
            entries.append(f'    <Content Include="{rel}">\r\n      <SubType>Content</SubType>\r\n    </Content>\r\n')
    project_new = project_raw.replace(b"  <Import Project=", ("  <ItemGroup>\r\n"+"".join(entries)+"  </ItemGroup>\r\n").encode()+b"  <Import Project=", 1) if entries else project_raw
    cache_path = Path(os.environ["APPDATA"])/"AssetCloud/mod-Civ Supply Chains-asset-deps.json"
    cache_raw = cache_path.read_bytes()
    cache = json.loads(cache_raw.decode("utf-8-sig"))
    index = {(Path(e["Filename"]).suffix.lower(), Path(e["Filename"]).stem.casefold()):
             e["Filename"].replace("\\", "/") for e in cache["Files"]}
    for p in MOD.rglob("*"):
        if p.is_file():
            index[(p.suffix.lower(), p.stem.casefold())] = p.relative_to(ROOT).as_posix()
    for p in payload:
        index[(p.suffix, p.stem.casefold())] = "Civ Supply Chains/"+p.relative_to(stage_root).as_posix()
    pantry = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry")
    for p in (pantry/"DSGs").glob("*.dsg"):
        index.setdefault((".dsg", p.stem.casefold()), "Civ6/pantry/DSGs/"+p.name)
    records = {e["Filename"].replace("\\", "/"): e for e in cache["Files"]}
    dependencies = {}
    for p in payload:
        if p.suffix == ".fgx":
            continue
        root = parse(p)
        key = "Civ Supply Chains/"+p.relative_to(stage_root).as_posix()
        refs = {str(Path(key).parent/e.get("text")).replace("\\", "/")
                for e in root.findall(".//m_DataFiles/Element/m_RelativePath")}
        for tag, ext in (("m_GeoName", ".geo"), ("m_AnimationName", ".anm"),
                         ("m_EntryName", ".ast"), ("m_dsgName", ".dsg")):
            for e in root.findall(".//"+tag):
                if e.get("text"):
                    refs.add(index[(ext, e.get("text").replace("\\", "/").split("/")[-1].casefold())])
        for e in root.findall(".//Element"):
            obj, kind = e.find("m_ObjectName"), e.find("m_eObjectType")
            if obj is not None and kind is not None and obj.get("text"):
                ext = {"MATERIAL":".mtl", "TEXTURE":".tex", "GEOMETRY":".geo"}.get(kind.text)
                if ext:
                    refs.add(index[(ext, obj.get("text").replace("\\", "/").split("/")[-1].casefold())])
        record = dict(Filename=key, Timestamp=int(time.time()*10000000)+116444736000000000,
                      Status=0, Type=2, EntityType={".ast":0, ".geo":2, ".anm":4}[p.suffix],
                      EntityClass=txt(root, "m_ClassName"), Filesize=p.stat().st_size,
                      Tags=[e.get("text") for e in root.findall("m_Tags/Element")], Stats={})
        if key in records:
            records[key].update(record)
        else:
            cache["Files"].append(record)
        cache["Dependencies"][key] = dependencies[key] = sorted(refs)
    for data in (xlp_new, project_new):
        E.fromstring(data)
    backup = out/("install-backup-"+time.strftime("%H%M%S"))
    backup.mkdir()
    def publish(path, data):
        if path.exists():
            rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path("AssetCloud")/path.name
            saved = backup/rel
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    assert cache_path.read_bytes() == cache_raw and xlp.read_bytes() == xlp_raw and project.read_bytes() == project_raw
    for p in payload:
        publish(MOD/p.relative_to(stage_root), p.read_bytes())
    publish(xlp, xlp_new)
    publish(project, project_new)
    cache["Timestamp"] = int(time.time()*10000000)+116444736000000000
    publish(cache_path, json.dumps(cache, separators=(",", ":")).encode())
    for rel in ("Geometries/CSC_ALL_Delivery_Pivot.fgx", "Animations/CSC_ALL_Delivery_Pivot.fgx", f"Assets/{ORIGINAL}.ast"):
        assert (MOD/rel).read_bytes() == (out/"before"/rel).read_bytes(), rel
    (out/"install-report.json").write_text(json.dumps(dict(backup=str(backup), dependencies=dependencies,
        files=[p.relative_to(stage_root).as_posix() for p in payload], original_delivery_unchanged=True), indent=2))
    print("INSTALLED", len(payload), "files; original crane/cargo and delivery asset unchanged")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("stage", "install"))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    {"stage":stage, "install":install}[args.phase](args.output)
