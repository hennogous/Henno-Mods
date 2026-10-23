"""Read-only native snapshots and assembly migration for the storage pivot trial."""
import argparse
import copy
import hashlib
import json
import math
import os
import re
from pathlib import Path
import shutil
import subprocess
import sys
import time
from lxml import etree as E
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "Civ Supply Chains"
sys.path.insert(0, str(ROOT / "project/tools/blender"))
from render_ae_asset import helper, Resolver, Assembly, prepare_geometry, DEFAULT_SDK
STATIC = ("CSC_Storage_L", "CSC_Storage_L_CON+PIL", "CSC_Storage_L_PIL_Decals")
DELIVERY = "CSC_BAKERS_Storage_Delivery"
DELIVERY_NATIVE = "CSC_ALL_Delivery_Pivot"
POINTS = "m_BehaviorData/m_behaviorDataSets/m_attachmentPoints/m_Points"
MODELS = "m_GeometrySet/m_ModelInstances"
BINDINGS = "m_BehaviorData/m_behaviorDataSets/m_animationBindings/m_Bindings"


def parse(path):
    return E.fromstring(path.read_bytes().replace(b"AssetObjects:", b"AssetObjects.."))


def txt(root, tag):
    return root.find(tag).get("text")


def parameter(root, key):
    return next(e for e in root.findall("m_CookParams/m_Values/Element")
                if txt(e, "m_ParamName") == key)


def save(root, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b'<?xml version="1.0" encoding="UTF-8" ?>\r\n' +
                     E.tostring(root, encoding="utf-8").replace(b"\r\n", b"\n").replace(b"\n", b"\r\n") + b"\r\n")


def point_matrix(p):
    position = np.array([float(p.findtext("m_position/" + a)) for a in "xyz"]) * 10
    x, y, z = [float(p.findtext("m_orientation/" + a)) for a in "xyz"]
    c, s = math.cos(-z), math.sin(-z)
    cx, sx, cy, sy = math.cos(x), math.sin(x), math.cos(y), math.sin(y)
    rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    m = np.eye(4)
    m[:3, :3] = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]) @ ry @ rx * float(p.findtext("m_scale"))
    m[:3, 3] = position
    return m


def set_point_matrix(p, matrix):
    scale = np.linalg.norm(matrix[:3, 0])
    assert np.max(np.abs(matrix[:3, :3].T @ matrix[:3, :3] - np.eye(3)*scale**2)) < 1e-5
    rot = matrix[:3, :3] / scale
    y = math.asin(max(-1., min(1., -rot[2, 0])))
    assert abs(math.cos(y)) > 1e-5, "Gimbal lock requires explicit decomposition"
    x = math.atan2(rot[2, 1], rot[2, 2])
    z = -math.atan2(rot[1, 0], rot[0, 0])
    for a, value in zip("xyz", matrix[:3, 3]/10):
        p.find("m_position/"+a).text = f"{value:.9f}"
    for a, value in zip("xyz", (x, y, z)):
        p.find("m_orientation/"+a).text = f"{value:.9f}"
    p.find("m_scale").text = f"{scale:.9f}"


def snapshot(out):
    backup = out / "before"
    if backup.exists():
        raise RuntimeError("Snapshot already exists; refusing to replace the baseline")
    paths = [
        *[MOD / "Geometries" / (n + ext) for n in (
            "CSC_Storage_L", "CSC_Storage_L_CON+PIL", "CSC_Storage_L_PIL_Decals",
            "CSC_ALL_Delivery", "CSC_ALL_District_Base") for ext in (".geo", ".fgx")],
        MOD / "Animations/CSC_ALL_Delivery.fgx",
        MOD / "Animations/CSC_ALL_Delivery.anm",
        MOD / "Assets/CSC_BAKERS_Storage_L.ast",
        MOD / "Assets/CSC_BAKERS_Classical_Base_03.ast",
        MOD / "XLPs/CSC_Tilebases.xlp",
        MOD / "Civ Supply Chains.civ6proj",
    ]
    for path in paths:
        target = backup / path.relative_to(MOD)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    exe, _ = helper(out / "cache")
    native = out / "native-before"
    native.mkdir()
    for path in paths:
        if path.suffix == ".fgx" and path.parent.name == "Geometries":
            subprocess.run([str(exe), str(exe.parent), str(path), str(native / (path.stem + ".json"))],
                           cwd=exe.parent, check=True, capture_output=True, text=True)
    report = {}
    for path in native.glob("*.json"):
        raw = json.loads(path.read_text())
        report[path.stem] = dict(models=[dict(name=m["name"], placement=m["placement"],
            bones=[b for b in m["bones"] if b["parent"] < 0]) for m in raw["models"]],
            meshes=[dict(name=m["name"], count=len(m["vertices"]),
                bounds=[[min(v["position"][i] for v in m["vertices"]) for i in range(3)],
                        [max(v["position"][i] for v in m["vertices"]) for i in range(3)]])
                    for m in raw["meshes"]])
    (out / "native-summary.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


def assembly(out):
    before, stage = out/"before", out/"staged"
    transform = json.loads((out/"transform.json").read_text())
    T = np.array(transform["local_to_district"])
    N = np.linalg.inv(T)
    storage = parse(before/"Assets/CSC_BAKERS_Storage_L.ast")
    delivery = copy.deepcopy(storage)
    delivery.find("m_Name").set("text", DELIVERY)
    delivery.find("m_Description").set("text", "Storage delivery with the building's ground pivot; separate district attachment.")
    for owner, keep_delivery in ((storage, False), (delivery, True)):
        for model in list(owner.find(MODELS)):
            is_delivery = txt(model, "m_Name") == "CSC_ALL_Delivery_Rig"
            if is_delivery != keep_delivery:
                owner.find(MODELS).remove(model)
            elif is_delivery:
                model.find("m_GeoName").set("text", DELIVERY_NATIVE)
        for point in list(owner.find(POINTS)):
            is_delivery = txt(point, "m_ModelInstanceName") == "CSC_ALL_Delivery_Rig"
            if is_delivery != keep_delivery:
                owner.find(POINTS).remove(point)
            elif not is_delivery:
                set_point_matrix(point, N @ point_matrix(point))
        for binding in list(owner.find(BINDINGS)):
            if keep_delivery:
                binding.find("m_AnimationName").set("text", DELIVERY_NATIVE)
            else:
                owner.find(BINDINGS).remove(binding)
    for tag in ("m_timelineBindings/m_Bindings", "m_timelines/m_Timelines"):
        node = delivery.find("m_BehaviorData/m_behaviorDataSets/"+tag)
        for item in list(node):
            node.remove(item)
    save(storage, stage/"Assets/CSC_BAKERS_Storage_L.ast")
    save(delivery, stage/"Assets"/(DELIVERY+".ast"))

    base = parse(before/"Assets/CSC_BAKERS_Classical_Base_03.ast")
    points = base.find(POINTS)
    targets = [p for p in points if txt(parameter(p, "Asset"), "m_EntryName") == "CSC_BAKERS_Storage_L"]
    assert len(targets) == 1
    storage_point = targets[0]
    old = point_matrix(storage_point)
    set_point_matrix(storage_point, old @ T)
    delivery_point = copy.deepcopy(storage_point)
    delivery_point.find("m_Name").set("text", "CSC_BAKERS_Storage_Delivery")
    parameter(delivery_point, "Asset").find("m_EntryName").set("text", DELIVERY)
    points.insert(points.index(storage_point)+1, delivery_point)
    save(base, stage/"Assets/CSC_BAKERS_Classical_Base_03.ast")
    # Retain the source declaration/format when adding the single new XLP entry.
    xlp = parse(before/"XLPs/CSC_Tilebases.xlp")
    entries = xlp.find("m_Entries")
    assert not any(txt(e, "m_EntryID") == DELIVERY for e in entries)
    entry = copy.deepcopy(entries[-1])
    entry.find("m_EntryID").set("text", DELIVERY)
    entry.find("m_ObjectName").set("text", DELIVERY)
    entries.append(entry)
    save(xlp, stage/"XLPs/CSC_Tilebases.xlp")
    checks = []
    old_storage = parse(before/"Assets/CSC_BAKERS_Storage_L.ast")
    for a, b in zip([p for p in old_storage.find(POINTS) if txt(p, "m_ModelInstanceName") != "CSC_ALL_Delivery_Rig"],
                    storage.find(POINTS)):
        error = float(np.max(np.abs(T @ point_matrix(b) - point_matrix(a))))
        assert error < 1e-4, (txt(a, "m_Name"), error)
        checks.append(dict(name=txt(a, "m_Name"), matrix_error=error))
    assert len(storage.find(MODELS)) == 3 and len(delivery.find(MODELS)) == 1
    assert len(delivery.find(POINTS)) == 1
    (out/"assembly-check.json").write_text(json.dumps(dict(attachment_checks=checks,
        shared_pivot=True, base="CSC_BAKERS_Classical_Base_03", delivery_asset=DELIVERY), indent=2))
    print("ASSEMBLY_STAGED", len(checks), "static points; one moving cargo; shared pivot")


def native_check(out):
    exe, _ = helper(out/"cache")
    after = out/"native-after"
    after.mkdir(exist_ok=True)
    T = np.array(json.loads((out/"transform.json").read_text())["local_to_district"])
    results = {}
    for name in STATIC:
        path = out/"staged/Geometries"/(name+".fgx")
        decoded = after/(name+".json")
        subprocess.run([str(exe), str(exe.parent), str(path), str(decoded)],
                       cwd=exe.parent, capture_output=True, check=True)
        old = json.loads((out/"native-before"/(name+".json")).read_text())
        new = json.loads(decoded.read_text())
        old_meshes = {m["name"]:m for m in old["meshes"]}
        report = {}
        for mesh in new["meshes"]:
            prior = old_meshes.pop(mesh["name"])
            assert len(mesh["vertices"]) == len(prior["vertices"]), mesh["name"]
            assert mesh["triangles"] == prior["triangles"], mesh["name"]
            assert mesh["boneBindings"] == prior["boneBindings"], (mesh["name"], "native bone bindings changed")
            maxpos = maxnorm = maxuv = 0
            for a, b in zip(prior["vertices"], mesh["vertices"]):
                maxpos = max(maxpos, float(np.linalg.norm((T @ [*b["position"], 1])[:3]-a["position"])))
                maxnorm = max(maxnorm, float(np.linalg.norm(T[:3, :3] @ b["normal"]-a["normal"])))
                for key in ("uv", "uv2", "uv3"):
                    maxuv = max(maxuv, float(np.max(np.abs(np.array(a[key])-b[key]))))
            assert maxpos < .0002, (name, mesh["name"], maxpos)
            assert maxnorm < .001, (name, mesh["name"], maxnorm)
            assert maxuv < 1e-6, (name, mesh["name"], maxuv)
            report[mesh["name"]] = dict(position_error_blender=maxpos, normal_error=maxnorm, uv_error=maxuv,
                                        vertices=len(mesh["vertices"]))
        assert not old_meshes
        geo = parse(path.with_suffix(".geo"))
        lookup = {m["name"]: m for m in new["meshes"]}
        for row in geo.find("m_Meshes"):
            mesh_name = txt(row, "m_Name")
            assert int(row.findtext("m_nBoundBoneCount")) == len(lookup[mesh_name]["boneBindings"]), (
                mesh_name, "GEO/FGX bone-binding count mismatch")
        results[name] = report
    (out/"native-geometry-check.json").write_text(json.dumps(results, indent=2))
    print("NATIVE_GEOMETRY_PASS", json.dumps(results))


def preserve_native(out):
    """Preserve the installed triangulation/vertex ordering while rebasing native attributes."""
    N = np.linalg.inv(np.array(json.loads((out/"transform.json").read_text())["local_to_district"]))
    converter = ROOT/"project/tools/cn6libs/CN6ToFGX.exe"
    report = {}
    for name in STATIC:
        path = out/"staged/Geometries"/(name+".cn6")
        text = path.read_text()
        header = text[:text.index("meshes:")]
        skeleton = {m.group(2):int(m.group(1)) for m in re.finditer(r'^(\d+) "([^"]+)"', header, re.M)}
        raw = json.loads((out/"native-before"/(name+".json")).read_text())
        geo = parse(out/"before/Geometries"/(name+".geo"))
        materials = {txt(m, "m_Name"):[txt(g, "m_Name") for g in m.findall("m_Groups/Element")]
                     for m in geo.findall("m_Meshes/Element")}
        rows = [header.rstrip(), f"meshes:{len(raw['meshes'])}"]
        for mesh in raw["meshes"]:
            rows.extend([f'mesh:"{mesh["name"]}"', "materials",
                         *[f'"{m}"' for m in materials[mesh["name"]]], "vertices"])
            for v in mesh["vertices"]:
                floats = list((N @ [*v["position"], 1])[:3])
                for key in ("normal", "tangent", "binormal"):
                    floats.extend(N[:3, :3] @ v[key])
                for key in ("uv", "uv2", "uv3"):
                    floats.extend(v[key])
                # CivNexus includes even zero-weight indices in its mesh binding list.
                active = [skeleton[mesh["boneBindings"][i]]
                          for i, w in zip(v["boneIndices"], v["boneWeights"]) if w]
                assert active, (mesh["name"], "vertex has no positive bone weight")
                indices = [skeleton[mesh["boneBindings"][i]] if w else active[0]
                           for i, w in zip(v["boneIndices"], v["boneWeights"])]
                rows.append(" ".join([*[f"{v:.9f}" for v in floats],
                                      *map(str, indices), *map(str, v["boneWeights"])]))
            rows.append("triangles")
            rows.extend(" ".join(map(str, tri)) for tri in mesh["triangles"])
        rows.append("end")
        path.write_text("\n".join(rows)+"\n")
        result = subprocess.run([str(converter), str(path), str(path.with_suffix(".fgx")), "2"],
                                cwd=converter.parent, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout+result.stderr)
        shutil.copy2(out/"before/Geometries"/(name+".geo"), path.with_suffix(".geo"))
        report[name] = dict(source="installed FGX baseline", retained="vertex ordering, triangulation, UVs, bone bindings",
                            transform="district_to_local")
    (out/"preserved-native-export.json").write_text(json.dumps(report, indent=2))
    print("PRESERVED_NATIVE_EXPORTED")


def stage_delivery(out):
    native = out/"delivery"
    checks = json.loads((native/"native-check.json").read_text())
    assert checks["combined_donkey"] and abs(checks["master_clip"]["duration"]-68) < .001
    assert max(checks["master_vertex_errors"].values()) < .2
    assert checks["donkey_error_at_previous_scale"] < .4
    for suffix, folder, extension in (("_Model.fgx", "Geometries", ".fgx"),
                                     ("_Model.geo", "Geometries", ".geo"),
                                     (".fgx", "Animations", ".fgx"),
                                     (".anm", "Animations", ".anm")):
        source = native/("CSC_TEST_TAILORS_Delivery_Master"+suffix)
        target = out/"staged"/folder/(DELIVERY_NATIVE+extension)
        target.parent.mkdir(parents=True, exist_ok=True)
        if extension == ".fgx":
            shutil.copy2(source, target)
        else:
            root = parse(source)
            root.find("m_Name").set("text", DELIVERY_NATIVE)
            for node in root.findall("m_DataFiles/Element/m_RelativePath"):
                node.set("text", DELIVERY_NATIVE+".fgx")
            save(root, target)
    print("DELIVERY_STAGED", DELIVERY_NATIVE)


def prepare_review(out):
    for label in ("before", "staged"):
        overlay = out/label
        resolver = Resolver(MOD, DEFAULT_SDK)
        for path in overlay.rglob("*"):
            if path.suffix.lower() in (".ast", ".geo", ".fgx", ".xlp"):
                resolver.index[path.name.casefold()] = {path}
        assembly = Assembly(resolver)
        root = assembly.asset(overlay/"Assets/CSC_BAKERS_Classical_Base_03.ast")
        run = out/"review"/label
        run.mkdir(parents=True, exist_ok=True)
        prepare_geometry(assembly, out/"cache", run)
        job = dict(root=root, assets=assembly.assets, geometries=assembly.geometries,
                   materials=assembly.materials, warnings=assembly.warnings, output=str(run))
        (run/"job.json").write_text(json.dumps(job, indent=2))
        print("REVIEW_PREPARED", label, len(assembly.assets), "assets")


def install(out):
    """Publish the checked trial with baseline guards and recoverable backups."""
    assert (out/"native-geometry-check.json").exists()
    assert (out/"assembly-check.json").exists()
    assert (out/"delivery-source-check.json").exists()
    stage = out/"staged"
    payload = [p for p in stage.rglob("*") if p.suffix in (".ast", ".geo", ".fgx", ".anm")]
    sources = Path(r"C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L")
    source_pairs = [(p, sources/("Delivery" if "Delivery" in p.stem else "")/p.name)
                    for p in (out/"sources").glob("*.blend")]
    for p in payload:
        target, old = MOD/p.relative_to(stage), out/"before"/p.relative_to(stage)
        if target.exists():
            assert target.read_bytes() == p.read_bytes() or (old.exists() and target.read_bytes() == old.read_bytes()), f"Changed since snapshot: {target}"
    for source, target in source_pairs:
        assert target.read_bytes() in (source.read_bytes(), (out/"before-sources"/source.name).read_bytes()), f"Source changed: {target}"
    backup = out/("install-backup-"+time.strftime("%Y%m%d-%H%M%S"))
    backup.mkdir()
    changed = []

    def publish(path, data):
        if path.exists():
            relative = path.relative_to(ROOT) if path.is_relative_to(ROOT) else Path("external")/path.name
            saved = backup/relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, saved)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        changed.append(str(path))

    for p in payload:
        publish(MOD/p.relative_to(stage), p.read_bytes())
    for source, target in source_pairs:
        publish(target, source.read_bytes())
    xlp = MOD/"XLPs/CSC_Tilebases.xlp"
    raw = xlp.read_bytes()
    if DELIVERY.encode() not in raw:
        entry = (f'\t\t<Element>\r\n\t\t\t<m_EntryID text="{DELIVERY}" />\r\n'
                 f'\t\t\t<m_ObjectName text="{DELIVERY}" />\r\n\t\t</Element>\r\n').encode()
        assert raw.count(b"</m_Entries>") == 1
        publish(xlp, re.sub(rb"(?m)^[ \t]*</m_Entries>", entry+b"\t</m_Entries>", raw))
    project = MOD/"Civ Supply Chains.civ6proj"
    raw = project.read_bytes()
    additions = []
    for p in payload:
        if (out/"before"/p.relative_to(stage)).exists():
            continue
        rel = str(p.relative_to(stage)).replace("/", "\\")
        if f'Include="{rel}"'.encode() not in raw:
            additions.append(f'    <Content Include="{rel}">\r\n      <SubType>Content</SubType>\r\n    </Content>\r\n')
    if additions:
        marker = b"  <Import Project="
        assert raw.count(marker) == 1
        publish(project, raw.replace(marker, ("  <ItemGroup>\r\n"+"".join(additions)+"  </ItemGroup>\r\n").encode()+marker))
    # Register descriptor dependencies for externally authored assets in AE's browser.
    cache_path = Path(os.environ["APPDATA"])/"AssetCloud/mod-Civ Supply Chains-asset-deps.json"
    cache_raw = cache_path.read_bytes()
    cache = json.loads(cache_raw.decode("utf-8-sig"))
    index = {(Path(e["Filename"]).suffix.lower(), Path(e["Filename"]).stem.casefold()):
             e["Filename"].replace("\\", "/") for e in cache["Files"]}
    for p in MOD.rglob("*"):
        if p.is_file():
            index[(p.suffix.lower(), p.stem.casefold())] = p.relative_to(ROOT).as_posix()
    records = {e["Filename"].replace("\\", "/"):e for e in cache["Files"]}
    dependencies = {}
    for p in payload:
        if p.suffix not in (".ast", ".geo", ".anm"):
            continue
        target = MOD/p.relative_to(stage)
        key = target.relative_to(ROOT).as_posix()
        root = parse(target)
        refs = {str(Path(key).parent/e.get("text")).replace("\\", "/")
                for e in root.findall(".//m_DataFiles/Element/m_RelativePath")}
        for tag, ext in (("m_GeoName", ".geo"), ("m_AnimationName", ".anm"),
                         ("m_EntryName", ".ast"), ("m_dsgName", ".dsg")):
            for e in root.findall(".//"+tag):
                name = e.get("text")
                if name:
                    refs.add(index[(ext, name.replace("\\", "/").split("/")[-1].casefold())])
        for e in root.findall(".//Element"):
            name, kind = e.find("m_ObjectName"), e.find("m_eObjectType")
            if name is not None and kind is not None and name.get("text"):
                ext = {"MATERIAL":".mtl", "TEXTURE":".tex", "GEOMETRY":".geo"}.get(kind.text)
                if ext:
                    refs.add(index[(ext, name.get("text").replace("\\", "/").split("/")[-1].casefold())])
        record = dict(Filename=key, Timestamp=int(target.stat().st_mtime*10000000)+116444736000000000,
                      Status=0, Type=2, EntityType={".ast":0, ".geo":2, ".anm":4}[p.suffix],
                      EntityClass=txt(root, "m_ClassName"), Filesize=target.stat().st_size,
                      Tags=[e.get("text") for e in root.findall("m_Tags/Element")], Stats={})
        if key in records:
            records[key].update(record)
        else:
            cache["Files"].append(record)
        dependencies[key] = sorted(refs)
        cache["Dependencies"][key] = sorted(refs)
    cache["Timestamp"] = int(time.time()*10000000)+116444736000000000
    assert cache_path.read_bytes() == cache_raw, "AssetCloud changed during installation"
    publish(cache_path, json.dumps(cache, separators=(",", ":")).encode())
    for p in payload:
        assert (MOD/p.relative_to(stage)).read_bytes() == p.read_bytes()
    E.parse(project)
    E.parse(xlp)
    (out/"install-report.json").write_text(json.dumps(dict(files=changed, backup=str(backup),
        dependencies=dependencies, installed=True, game_verified=False), indent=2))
    print("INSTALLED", len(changed), "files;", "backup:", backup)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("snapshot", "assembly", "native-check", "stage-delivery", "preserve-native", "prepare-review", "install"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    {"snapshot":snapshot, "assembly":assembly, "native-check":native_check,
     "stage-delivery":stage_delivery, "preserve-native":preserve_native,
     "prepare-review":prepare_review, "install":install}[args.phase](args.output)


if __name__ == "__main__":
    main()
