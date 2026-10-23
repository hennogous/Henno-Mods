"""One-time extension of the accepted Storage L ground-pivot/donkey trial.

Stage from a guarded snapshot, verify placement/state preservation, then install.
The original geometry and accepted donkey binaries are deliberately reused.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import time

import numpy as np
from lxml import etree as E
from storage_pivot_trial import (
    ROOT, MOD, POINTS, MODELS, BINDINGS, parse, txt, parameter, save,
    point_matrix, set_point_matrix,
)

ACCEPTED = "CSC_BAKERS_Storage_L"
PARENT = "CSC_TRIAL_BAKERS_Delivery_Split"
CHILD = "CSC_TRIAL_Delivery_Donkey"
RIG = "CSC_ALL_Delivery_Rig"
PIVOT = "CSC_ALL_Delivery_Pivot"
SPLITS = {
    "CSC_BAKERS_Storage_L_2": "CSC_BAKERS_Storage_Delivery_2_Split",
    "CSC_TAILORS_Storage_L": "CSC_TAILORS_Storage_Delivery_Split",
    "CSC_TAILORS_Storage_L_2": "CSC_TAILORS_Storage_Delivery_2_Split",
}


def asset(point):
    try:
        return txt(parameter(point, "Asset"), "m_EntryName")
    except StopIteration:
        return None


def canonical(node):
    return E.tostring(E.fromstring(E.tostring(node), E.XMLParser(remove_blank_text=True)))


def snapshot(out, path):
    dst = out/"before"/path.relative_to(MOD)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        assert dst.read_bytes() == path.read_bytes(), f"Baseline changed: {path}"
    else:
        shutil.copy2(path, dst)


def stage(out, transform):
    assert not (out/"migration.json").exists(), "Use a fresh output folder; do not rebase twice."
    T = np.array(json.loads(transform.read_text())["local_to_district"])
    N = np.linalg.inv(T)
    roots = {}
    for path in (MOD/"Assets").glob("*.ast"):
        root = parse(path)
        if any(txt(m, "m_GeoName") == "CSC_Storage_L" for m in root.find(MODELS)):
            roots[path.stem] = root
            snapshot(out, path)
    assert len(roots) == 6 and ACCEPTED in roots, sorted(roots)
    trial = parse(MOD/f"Assets/{PARENT}.ast")
    donkey = next(p for p in trial.find(POINTS) if asset(p) == CHILD)
    reports = {}
    for name, root in roots.items():
        before = copy.deepcopy(root)
        models = root.find(MODELS)
        rig = next((m for m in models if txt(m, "m_Name") == RIG), None)
        cargo = [p for p in root.find(POINTS) if txt(p, "m_ModelInstanceName") == RIG]
        if name in SPLITS:
            assert rig is not None and len(cargo) == 1
            delivery = copy.deepcopy(root)
            delivery.find("m_Name").set("text", SPLITS[name])
            delivery.find("m_Description").set("text", "Ground-pivot storage delivery with independently terrain-following donkey.")
            delivery.find("m_BehaviorData/m_dsgName").set("text", "Standard_LandmarkNoRandomOffset")
            for m in list(delivery.find(MODELS)):
                if txt(m, "m_Name") != RIG:
                    delivery.find(MODELS).remove(m)
                else:
                    m.find("m_GeoName").set("text", PIVOT)
                    hidden = 0
                    for row in m.find("m_GroupStates"):
                        if "Donkey" in txt(row, "m_MeshName"):
                            for value in row.findall("m_Values/m_Values/Element"):
                                if txt(value, "m_ParamName") == "Visible":
                                    value.find("m_bValue").text = "false"
                                    hidden += 1
                    assert hidden == 5
            for p in list(delivery.find(POINTS)):
                if txt(p, "m_ModelInstanceName") != RIG:
                    delivery.find(POINTS).remove(p)
            assert canonical(delivery.find(POINTS)[0]) == canonical(cargo[0])
            delivery.find(POINTS).append(copy.deepcopy(donkey))
            for b in delivery.find(BINDINGS):
                assert txt(b, "m_AnimationName") == "CSC_ALL_Delivery"
                b.find("m_AnimationName").set("text", PIVOT)
            for sub in ("m_timelineBindings/m_Bindings", "m_timelines/m_Timelines"):
                parent = delivery.find("m_BehaviorData/m_behaviorDataSets/"+sub)
                for e in list(parent):
                    parent.remove(e)
            save(delivery, out/f"staged/Assets/{SPLITS[name]}.ast")
        else:
            assert rig is None
        errors = []
        if name != ACCEPTED:
            if rig is not None:
                models.remove(rig)
            for p in list(root.find(POINTS)):
                if txt(p, "m_ModelInstanceName") == RIG:
                    root.find(POINTS).remove(p)
                else:
                    old = point_matrix(p)
                    set_point_matrix(p, N @ old)
                    errors.append(float(np.max(np.abs(T @ point_matrix(p)-old))))
            for b in list(root.find(BINDINGS)):
                assert txt(b, "m_AnimationName") == "CSC_ALL_Delivery"
                root.find(BINDINGS).remove(b)
            assert max(errors) < 1e-4
            # Static state/material records stay byte-equivalent after XML normalization.
            assert [canonical(m) for m in models] == [
                canonical(m) for m in before.find(MODELS) if txt(m, "m_Name") != RIG]
            save(root, out/f"staged/Assets/{name}.ast")
        reports[name] = dict(transformed_points=len(errors), max_matrix_error=max(errors, default=0),
                             removed_orphan_cargo=len(cargo) if rig is None else 0,
                             delivery=SPLITS.get(name, PARENT if name == ACCEPTED else None))
    placements = []
    for path in sorted((MOD/"Assets").glob("*.ast")):
        root = parse(path)
        points = root.find(POINTS)
        if points is None:
            continue
        targets = [p for p in points if asset(p) in roots]
        if not targets:
            continue
        snapshot(out, path)
        for p in targets:
            name = asset(p)
            old = point_matrix(p)
            accepted = path.stem == "CSC_BAKERS_Classical_Base_03"
            if accepted:
                assert np.max(np.abs(old-T)) < 1e-4
                assert len([q for q in points if asset(q) == PARENT]) == 1
            else:
                set_point_matrix(p, old @ T)
            parameter(p, "TerrainFollowMode").find("m_Value").set("text", "Pivot Height")
            delivery_name = reports[name]["delivery"]
            if delivery_name and not accepted:
                assert not any(asset(q) == delivery_name for q in points)
                sibling = copy.deepcopy(p)
                sibling.find("m_Name").set("text", delivery_name)
                parameter(sibling, "Asset").find("m_EntryName").set("text", delivery_name)
                parameter(sibling, "RandomizeAnims").find("m_bValue").text = "false"
                points.insert(points.index(p)+1, sibling)
            # Compare every static prop in district coordinates against the authored baseline.
            prior = parse(out/f"before/Assets/{name}.ast")
            previous = {txt(q, "m_Name"): q for q in prior.find(POINTS)
                        if txt(q, "m_ModelInstanceName") != RIG}
            errors = []
            for q in roots[name].find(POINTS):
                old_prop = point_matrix(previous[txt(q, "m_Name")])
                # Already centered Bakers L needs its original pre-trial local basis.
                if name == ACCEPTED and not accepted:
                    old_prop = T @ old_prop
                errors.append(float(np.max(np.abs(
                    point_matrix(p) @ point_matrix(q) - old @ old_prop))))
            assert max(errors) < 1e-4, (path, errors)
            placements.append(dict(base=path.stem, storage=name, delivery=delivery_name,
                                   already_migrated=accepted, max_world_matrix_error=max(errors)))
        if path.stem != "CSC_BAKERS_Classical_Base_03":
            save(root, out/"staged/Assets"/path.name)
    assert len(placements) == 12, placements
    assert sum(bool(p["delivery"]) for p in placements) == 8
    # Protect all reused geometry/animation and the accepted trial against incidental edits.
    protected = {}
    for folder in ("Geometries", "Animations"):
        for path in (MOD/folder).glob("*"):
            if path.stem.startswith(("CSC_Storage_L", "CSC_ALL_Delivery", CHILD)):
                protected[path.relative_to(MOD).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    for name in (ACCEPTED, PARENT, CHILD, "CSC_BAKERS_Classical_Base_03"):
        path = MOD/f"Assets/{name}.ast"
        protected[path.relative_to(MOD).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    report = dict(storages=reports, placements=placements, protected_hashes=protected,
                  new_assets=list(SPLITS.values()), transform=T.tolist())
    (out/"migration.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


def install(out):
    report = json.loads((out/"migration.json").read_text())
    assert len(json.loads((out/"state-validation.json").read_text())) == 60
    for state in ("Worked", "Pillaged", "Construction"):
        assert (out/f"review/{state}/storage.png").is_file(), state
    stage_root = out/"staged"
    payload = list(stage_root.glob("Assets/*.ast"))
    assert len(payload) == 19
    for path in payload:
        live = MOD/path.relative_to(stage_root)
        if live.exists():
            assert live.read_bytes() == (out/"before"/path.relative_to(stage_root)).read_bytes(), live
    for rel, digest in report["protected_hashes"].items():
        assert hashlib.sha256((MOD/rel).read_bytes()).hexdigest() == digest, rel
    xlp = MOD/"XLPs/CSC_Tilebases.xlp"
    project = MOD/"Civ Supply Chains.civ6proj"
    cache_path = Path(os.environ["APPDATA"])/"AssetCloud/mod-Civ Supply Chains-asset-deps.json"
    baseline = {p: p.read_bytes() for p in (xlp, project, cache_path)}
    entries = "".join(f'\t\t<Element>\r\n\t\t\t<m_EntryID text="{n}"/>\r\n'
                      f'\t\t\t<m_ObjectName text="{n}"/>\r\n\t\t</Element>\r\n'
                      for n in report["new_assets"] if f'text="{n}"'.encode() not in baseline[xlp])
    xlp_new, count = re.subn(rb"(?m)^[ \t]*</m_Entries>", entries.encode()+b"\t</m_Entries>", baseline[xlp])
    assert count == 1
    entries = "".join(f'    <Content Include="Assets\\{n}.ast">\r\n      <SubType>Content</SubType>\r\n    </Content>\r\n'
                      for n in report["new_assets"] if f'Include="Assets\\{n}.ast"'.encode() not in baseline[project])
    project_new = baseline[project].replace(b"  <Import Project=",
        ("  <ItemGroup>\r\n"+entries+"  </ItemGroup>\r\n").encode()+b"  <Import Project=", 1)
    cache = json.loads(baseline[cache_path].decode("utf-8-sig"))
    index = {(Path(e["Filename"]).suffix.lower(), Path(e["Filename"]).stem.casefold()):
             e["Filename"].replace("\\", "/") for e in cache["Files"]}
    for p in MOD.rglob("*"):
        if p.is_file():
            index[(p.suffix.lower(), p.stem.casefold())] = p.relative_to(ROOT).as_posix()
    for p in payload:
        index[(".ast", p.stem.casefold())] = "Civ Supply Chains/Assets/"+p.name
    pantry = Path(r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry")
    for p in (pantry/"DSGs").glob("*.dsg"):
        index.setdefault((".dsg", p.stem.casefold()), "Civ6/pantry/DSGs/"+p.name)
    records = {e["Filename"].replace("\\", "/"): e for e in cache["Files"]}
    dependencies = {}
    for p in payload:
        root = parse(p)
        key = "Civ Supply Chains/Assets/"+p.name
        refs = set()
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
                      Status=0, Type=2, EntityType=0, EntityClass=txt(root, "m_ClassName"),
                      Filesize=p.stat().st_size,
                      Tags=[e.get("text") for e in root.findall("m_Tags/Element")], Stats={})
        if key in records:
            records[key].update(record)
        else:
            cache["Files"].append(record)
        cache["Dependencies"][key] = dependencies[key] = sorted(refs)
    for data in (xlp_new, project_new):
        E.fromstring(data)
    for p, data in baseline.items():
        assert p.read_bytes() == data
    backup = out/("install-backup-"+time.strftime("%H%M%S"))
    def publish(path, data):
        if path.exists():
            rel = path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path("AssetCloud")/path.name
            dst = backup/rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, dst)
        path.write_bytes(data)
    for p in payload:
        publish(MOD/p.relative_to(stage_root), p.read_bytes())
    publish(xlp, xlp_new)
    publish(project, project_new)
    cache["Timestamp"] = int(time.time()*10000000)+116444736000000000
    publish(cache_path, json.dumps(cache, separators=(",", ":")).encode())
    for rel, digest in report["protected_hashes"].items():
        assert hashlib.sha256((MOD/rel).read_bytes()).hexdigest() == digest, rel
    (out/"install-report.json").write_text(json.dumps(
        dict(files=[p.relative_to(stage_root).as_posix() for p in payload],
             backup=str(backup), dependencies=dependencies), indent=2))
    print("INSTALLED", len(payload), "ASTs; reused binaries and accepted Base 03 unchanged")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("stage", "install"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--transform", type=Path)
    args = p.parse_args()
    if args.phase == "stage":
        stage(args.output, args.transform)
    else:
        install(args.output)
