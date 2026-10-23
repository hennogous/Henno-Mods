"""Prepare fixed flour geometry from saved Water Mill placements and native meshes."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np
from storage_family_pivot import asset, canonical
from storage_pivot_trial import MOD, ROOT, POINTS, MODELS, parse, txt, save, point_matrix, helper
from storage_pivot_trial import Resolver, Assembly, DEFAULT_SDK, prepare_geometry

MILL = "CSC_BAKERS_Water_Mill"
VARIANTS = (MILL, MILL+"_2")
FLOUR = ("CSC_BAKERS_Flour_Closed", "CSC_BAKERS_Flour_Open")
SOURCE = Path(r"C:\Users\Shadow\Desktop\Working Files\3D Art\Level 1\Bakers")/(MILL+".blend")


def plan(out):
    assert not (out/"plan.json").exists()
    roots = {}
    for name in (*VARIANTS, *FLOUR):
        p = MOD/f"Assets/{name}.ast"
        dst = out/"before"/p.relative_to(MOD)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
        roots[name] = parse(p)
    for name in (MILL, *FLOUR):
        for ext in (".fgx", ".geo"):
            p = MOD/f"Geometries/{name}{ext}"
            dst = out/"before"/p.relative_to(MOD)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dst)
    (out/"before-sources").mkdir(exist_ok=True)
    shutil.copy2(SOURCE, out/"before-sources"/SOURCE.name)
    before_geo = parse(MOD/f"Geometries/{MILL}.geo")
    native = json.loads((out/(MILL+".json")).read_text())
    matrices = {}
    points = {}
    for name in VARIANTS:
        points[name] = [p for p in roots[name].find(POINTS) if asset(p) in FLOUR]
        matrices[name] = [point_matrix(p) for p in points[name]]
    assert [len(points[n]) for n in VARIANTS] == [13, 16]
    slots = []
    used = set()
    for i, p in enumerate(points[MILL]):
        matches = [j for j, q in enumerate(points[MILL+"_2"])
                   if j not in used and asset(q) == asset(p)
                   and np.max(np.abs(matrices[MILL][i]-matrices[MILL+"_2"][j])) < 1e-8]
        assert matches
        j = matches[0]
        used.add(j)
        slots.append(dict(name=f"CSC_Fixed_Mill_Flour_{i+1:02}", source=asset(p),
                          matrix=matrices[MILL][i].tolist(),
                          points={MILL:txt(p, "m_Name"), MILL+"_2":txt(points[MILL+"_2"][j], "m_Name")}))
    kept = []
    for j, p in enumerate(points[MILL+"_2"]):
        if j in used:
            continue
        if matrices[MILL+"_2"][j][0, 3] < -90:
            kept.append(txt(p, "m_Name"))
        else:
            slots.append(dict(name="CSC_Fixed_Mill_Flour_Variant_2", source=asset(p),
                              matrix=matrices[MILL+"_2"][j].tolist(),
                              points={MILL+"_2":txt(p, "m_Name")}))
    assert len(slots) == 14 and len(kept) == 2
    meshes = copy.deepcopy(native["meshes"])
    groups = {txt(m, "m_Name"): [txt(g, "m_Name") for g in m.find("m_Groups")]
              for m in before_geo.find("m_Meshes")}
    geo = copy.deepcopy(before_geo)
    for slot in slots:
        raw = json.loads((out/(slot["source"]+".json")).read_text())
        assert len(raw["meshes"]) == 1
        mesh = copy.deepcopy(raw["meshes"][0])
        mesh["name"] = slot["name"]
        matrix = np.array(slot["matrix"])
        normal = np.linalg.inv(matrix[:3, :3]).T
        assert abs(np.linalg.det(matrix[:3, :3])-1) < 1e-6
        for v in mesh["vertices"]:
            v["position"] = (matrix @ [*v["position"], 1])[:3].tolist()
            for key in ("normal", "tangent", "binormal"):
                v[key] = (normal @ v[key]).tolist()
        mesh["boneBindings"] = ["Bone"]
        for v in mesh["vertices"]:
            v["boneIndices"] = [0]*8
            v["boneWeights"] = [255]+[0]*7
        meshes.append(mesh)
        descriptor = parse(MOD/f"Geometries/{slot['source']}.geo")
        mesh_geo = copy.deepcopy(descriptor.find("m_Meshes")[0])
        mesh_geo.find("m_Name").set("text", slot["name"])
        geo.find("m_Meshes").append(mesh_geo)
        slot["groups"] = groups[slot["name"]] = [txt(g, "m_Name") for g in mesh_geo.find("m_Groups")]
    for name in VARIANTS:
        root = roots[name]
        main = next(m for m in root.find(MODELS) if txt(m, "m_GeoName") == MILL)
        states = main.find("m_GroupStates")
        original_meshes = {m["name"] for m in native["meshes"]}
        stale = [s for s in states if txt(s, "m_MeshName") not in original_meshes]
        assert len(stale) == 50
        for s in stale:
            states.remove(s)
        remove = set()
        for slot in slots:
            prop = roots[slot["source"]]
            for s in prop.find(MODELS)[0].find("m_GroupStates"):
                row = copy.deepcopy(s)
                row.find("m_MeshName").set("text", slot["name"])
                if name not in slot["points"]:
                    for v in row.findall("m_Values/m_Values/Element"):
                        if txt(v, "m_ParamName") == "Visible":
                            v.find("m_bValue").text = "false"
                states.append(row)
            if name in slot["points"]:
                remove.add(slot["points"][name])
        for p in list(root.find(POINTS)):
            if txt(p, "m_Name") in remove:
                root.find(POINTS).remove(p)
        assert len(remove) == (13 if name == MILL else 14)
        original = parse(out/f"before/Assets/{name}.ast")
        assert [canonical(p) for p in root.find(POINTS)] == [
            canonical(p) for p in original.find(POINTS) if txt(p, "m_Name") not in remove]
        assert [canonical(s) for s in states if txt(s, "m_MeshName") in original_meshes] == [
            canonical(s) for s in original.find(MODELS)[0].find("m_GroupStates")
            if txt(s, "m_MeshName") in original_meshes]
        save(root, out/f"staged/Assets/{name}.ast")
    save(geo, out/f"staged/Geometries/{MILL}.geo")
    merged = dict(models=native["models"], meshes=meshes)
    (out/"merged-native.json").write_text(json.dumps(merged))
    result = dict(slots=slots, groups=groups, kept_cart_flour=kept, source=str(SOURCE),
                  source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
                  original_meshes=[m["name"] for m in native["meshes"]],
                  vertices=sum(len(m["vertices"]) for m in meshes),
                  triangles=sum(len(m["triangles"]) for m in meshes))
    (out/"plan.json").write_text(json.dumps(result, indent=2))
    assembly = Assembly(Resolver(MOD, DEFAULT_SDK))
    material_keys = {}
    for row in roots[MILL].find(MODELS)[0].find("m_GroupStates"):
        if txt(row, "m_StateName") != "Worked":
            continue
        group = txt(row, "m_GroupName")
        material = next(txt(e, "m_ObjectName") for e in row.findall("m_Values/m_Values/Element")
                        if txt(e, "m_ParamName") == "Material")
        if group not in material_keys:
            material_keys[group] = assembly.material(material, {}, MOD/f"Assets/{MILL}.ast", True)
    (out/"materials.json").write_text(json.dumps(dict(materials=assembly.materials, keys=material_keys)))
    print("PLANNED", len(slots), "fixed flour meshes;", result["vertices"], "native vertices;", kept, "remain with cart")


def convert(out):
    raw = json.loads((out/"merged-native.json").read_text())
    plan = json.loads((out/"plan.json").read_text())
    template = (out/"source-header.cn6").read_text()
    header = template[:template.index("meshes:")]
    import re
    skeleton = {m.group(2):int(m.group(1)) for m in re.finditer(r'^(\d+) "([^"]+)"', header, re.M)}
    rows = [header.rstrip(), f"meshes:{len(raw['meshes'])}"]
    for mesh in raw["meshes"]:
        rows.extend([f'mesh:"{mesh["name"]}"', "materials",
                     *[f'"{g}"' for g in plan["groups"][mesh["name"]]], "vertices"])
        for v in mesh["vertices"]:
            floats = [x for key in ("position","normal","tangent","binormal","uv","uv2","uv3") for x in v[key]]
            # CivNexus builds mesh bindings from every index, including zero-weight
            # slots. Keep inactive slots on a real influence instead of model root.
            active = [skeleton[mesh["boneBindings"][i]]
                      for i, w in zip(v["boneIndices"], v["boneWeights"]) if w]
            assert active, (mesh["name"], "vertex has no positive bone weight")
            indices = [skeleton[mesh["boneBindings"][i]] if w else active[0]
                       for i, w in zip(v["boneIndices"], v["boneWeights"])]
            rows.append(" ".join([*[f"{x:.9f}" for x in floats], *map(str,indices), *map(str,v["boneWeights"])]))
        rows.append("triangles")
        rows.extend(" ".join(map(str, tri)) for tri in mesh["triangles"])
    rows.append("end")
    path=out/f"staged/Geometries/{MILL}.cn6"
    path.write_text("\n".join(rows)+"\n")
    converter=ROOT/"project/tools/cn6libs/CN6ToFGX.exe"
    result=subprocess.run([str(converter),str(path),str(path.with_suffix(".fgx")),"2"],
                          cwd=converter.parent,capture_output=True,text=True)
    (out/"conversion.log").write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    exe,_=helper(out/"cache")
    subprocess.run([str(exe),str(exe.parent),str(path.with_suffix(".fgx")),str(out/"converted.json")],
                   cwd=exe.parent,check=True,capture_output=True)
    new=json.loads((out/"converted.json").read_text())
    checks={}
    lookup={m["name"]:m for m in new["meshes"]}
    for m in raw["meshes"]:
        b=lookup[m["name"]]
        assert m["boneBindings"] == b["boneBindings"], (
            m["name"], "native bone bindings changed", m["boneBindings"], b["boneBindings"])
        assert m["triangles"]==b["triangles"]
        assert len(m["vertices"])==len(b["vertices"])
        errors={k:max(float(np.max(np.abs(np.array(v[k])-w[k]))) for v,w in zip(m["vertices"],b["vertices"]))
                for k in ("position","normal","tangent","binormal","uv","uv2","uv3")}
        assert max(errors.values())<.0001,(m["name"],errors)
        checks[m["name"]]=errors
    assert len(lookup)==len(raw["meshes"])
    geo = parse(path.with_suffix(".geo"))
    for row in geo.find("m_Meshes"):
        name = txt(row, "m_Name")
        assert int(row.findtext("m_nBoundBoneCount")) == len(lookup[name]["boneBindings"]), (
            name, "GEO/FGX bone-binding count mismatch")
    (out/"native-validation.json").write_text(json.dumps(checks,indent=2))
    print("NATIVE_PASS",len(checks),"meshes; position/normal/tangent/UV parity and exact triangles")


def review(out):
    plan = json.loads((out/"plan.json").read_text())
    resolver = Resolver(MOD, DEFAULT_SDK)
    for name in VARIANTS:
        root = parse(out/f"before/Assets/{name}.ast")
        rows = root.find(MODELS)[0].find("m_GroupStates")
        for row in list(rows):
            if txt(row,"m_MeshName") not in plan["original_meshes"]:
                rows.remove(row)
        save(root,out/f"review-inputs/before/Assets/{name}.ast")
    def overlay(folder):
        for p in folder.rglob("*"):
            if p.suffix in (".ast",".geo",".fgx"):
                resolver.index[p.name.casefold()]={p}
    checks = []
    for state in ("Worked","Unworked","Pillaged","Construction","Unbuilt"):
        overlay(out/"staged")
        assembly = Assembly(resolver,state)
        for name in VARIANTS:
            key = assembly.asset(out/f"staged/Assets/{name}.ast")
            model = next(m for m in assembly.assets[key]["models"] if m["id"]==MILL)
            fixed = [g for g in model["groups"] if g["mesh"].startswith("CSC_Fixed_")]
            expected = []
            for slot in plan["slots"]:
                prop = parse(out/f"before/Assets/{slot['source']}.ast")
                rows = prop.find(MODELS)[0].find("m_GroupStates")
                visible = any(txt(r,"m_StateName")==state and any(
                    txt(v,"m_ParamName")=="Visible" and v.findtext("m_bValue")=="true"
                    for v in r.findall("m_Values/m_Values/Element")) for r in rows)
                if name in slot["points"] and visible:
                    expected.append(slot["name"])
            assert sorted(g["mesh"] for g in fixed)==sorted(expected),(name,state)
            assert all(assembly.materials[g["material"]]["id"]=="CSC_ALL_Props_01" for g in fixed)
            checks.append(dict(asset=name,state=state,fixed_flour_visible=len(fixed),
                materials={g["mesh"]:assembly.materials[g["material"]]["id"] for g in model["groups"]}))
        print("STATE_PASS",state,flush=True)
    for label in ("before","staged"):
        overlay(out/"before/Geometries")
        overlay(out/"review-inputs/before")
        if label=="staged":
            overlay(out/"staged")
        assembly = Assembly(resolver)
        assembly.is_decal = lambda ident,near:False
        path = out/(f"review-inputs/before/Assets/{MILL}_2.ast" if label=="before" else f"staged/Assets/{MILL}_2.ast")
        key = assembly.asset(path)
        run = out/"review"/label
        run.mkdir(parents=True,exist_ok=True)
        prepare_geometry(assembly,out/"cache",run)
        (run/"job.json").write_text(json.dumps(dict(root=key,assets=assembly.assets,
            geometries=assembly.geometries,materials=assembly.materials,warnings=assembly.warnings,
            output=str(run)),indent=2))
        print("REVIEW_PREPARED",label,flush=True)
    (out/"state-validation.json").write_text(json.dumps(checks,indent=2))


def install(out):
    plan = json.loads((out/"plan.json").read_text())
    assert json.loads((out/"source-validation.json").read_text())["error_count"] == 0
    assert len(json.loads((out/"native-validation.json").read_text())) == 17
    assert len(json.loads((out/"source-geometry-validation.json").read_text())) == 17
    assert len(json.loads((out/"state-validation.json").read_text())) == 10
    assert (out/"review/staged/storage.png").is_file()
    payload = [out/f"staged/Assets/{n}.ast" for n in VARIANTS]
    payload += [out/f"staged/Geometries/{MILL}{e}" for e in (".geo",".fgx")]
    for p in payload:
        rel = p.relative_to(out/"staged")
        assert (MOD/rel).read_bytes() == (out/"before"/rel).read_bytes(), rel
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == plan["source_hash"]
    cache_path = Path(os.environ["APPDATA"])/"AssetCloud/mod-Civ Supply Chains-asset-deps.json"
    cache_raw = cache_path.read_bytes()
    cache = json.loads(cache_raw.decode("utf-8-sig"))
    index = {(Path(e["Filename"]).suffix.lower(),Path(e["Filename"]).stem.casefold()):
             e["Filename"].replace("\\","/") for e in cache["Files"]}
    for folder in ("Assets","Geometries","Materials","Textures","Animations"):
        for p in (MOD/folder).glob("*"):
            if p.is_file():
                index[(p.suffix.lower(),p.stem.casefold())]=p.relative_to(ROOT).as_posix()
    records={e["Filename"].replace("\\","/"):e for e in cache["Files"]}
    dependencies={}
    now=int(time.time()*10000000)+116444736000000000
    for p in payload:
        if p.suffix==".fgx":
            continue
        r=parse(p)
        key="Civ Supply Chains/"+p.relative_to(out/"staged").as_posix()
        refs={str(Path(key).parent/e.get("text")).replace("\\","/")
              for e in r.findall(".//m_DataFiles/Element/m_RelativePath")}
        for tag,ext in (("m_GeoName",".geo"),("m_AnimationName",".anm"),
                        ("m_EntryName",".ast"),("m_dsgName",".dsg")):
            for e in r.findall(".//"+tag):
                if e.get("text"):
                    refs.add(index[(ext,e.get("text").replace("\\","/").split("/")[-1].casefold())])
        for e in r.findall(".//Element"):
            obj,kind=e.find("m_ObjectName"),e.find("m_eObjectType")
            if obj is not None and kind is not None and obj.get("text"):
                ext={"MATERIAL":".mtl","TEXTURE":".tex","GEOMETRY":".geo"}.get(kind.text)
                if ext:
                    refs.add(index[(ext,obj.get("text").replace("\\","/").split("/")[-1].casefold())])
        records[key].update(Timestamp=now,Filesize=p.stat().st_size)
        cache["Dependencies"][key]=dependencies[key]=sorted(refs)
    cache["Timestamp"]=now
    source_pairs=[(out/"sources"/SOURCE.name,SOURCE)]
    source_pairs += [(p,SOURCE.parent/"textures"/p.name) for p in (out/"sources/textures").glob("*.png")]
    backup=out/("install-backup-"+time.strftime("%H%M%S"))
    def publish(path,data):
        if path.exists():
            rel=path.relative_to(ROOT) if path.is_relative_to(ROOT) else (
                Path("source")/path.relative_to(SOURCE.parent) if path.is_relative_to(SOURCE.parent)
                else Path("AssetCloud")/path.name)
            saved=backup/rel
            saved.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(path,saved)
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(data)
    assert cache_path.read_bytes()==cache_raw
    for p in payload:
        publish(MOD/p.relative_to(out/"staged"),p.read_bytes())
    for src,dst in source_pairs:
        publish(dst,src.read_bytes())
    publish(cache_path,json.dumps(cache,separators=(",",":")).encode())
    (out/"install-report.json").write_text(json.dumps(dict(backup=str(backup),
        runtime=[p.relative_to(out/"staged").as_posix() for p in payload],
        source=str(SOURCE),dependencies=dependencies),indent=2))
    print("INSTALLED: shared mill geometry, both ASTs, editable master and portable textures")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("phase",choices=("plan","convert","review","install"))
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    {"plan":plan,"convert":convert,"review":review,"install":install}[args.phase](args.output)
