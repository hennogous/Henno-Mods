"""Recenter the saved eleven-piece wall assembly and compensate both Cafe parents."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

import numpy as np
from storage_family_pivot import asset, canonical
from storage_pivot_trial import (
    MOD, POINTS, MODELS, parse, txt, save, point_matrix, parameter,
    helper, Resolver, Assembly, DEFAULT_SDK, prepare_geometry,
)

WALL = "CSC_ALL_Stage_4_Wall"
CAFES = ("CSC_BAKERS_Cafe", "CSC_BAKERS_Cafe_2")
NAMES = (WALL, *CAFES)


def shift(point, delta):
    # Translation only: retain the exact authored rotation, scale and settings.
    for axis, offset in zip("xyz", delta):
        e = point.find("m_position/"+axis)
        e.text = f"{float(e.text) + offset / 10:.9f}"


def without_positions(root, names):
    root = copy.deepcopy(root)
    for p in root.find(POINTS):
        if txt(p, "m_Name") in names:
            for e in p.find("m_position"):
                e.text = "POSITION"
    return canonical(root)


def stage(out):
    assert not (out/"migration.json").exists(), "Use a fresh snapshot; never rebase twice."
    before = {}
    for name in NAMES:
        src = MOD/f"Assets/{name}.ast"
        dst = out/f"before/Assets/{name}.ast"
        dst.parent.mkdir(parents=True, exist_ok=True)
        assert not dst.exists()
        shutil.copy2(src, dst)
        before[name] = parse(src)
    wall = copy.deepcopy(before[WALL])
    points = wall.find(POINTS)
    assert len(points) == 11
    consumers = []
    for p in (MOD/"Assets").glob("*.ast"):
        root = parse(p)
        consumers.extend(p.stem for q in root.findall(POINTS+"/Element") if asset(q) == WALL)
    assert sorted(consumers) == sorted(CAFES), consumers
    # Exact native vertices provide a stable XY bounding-box center at ground Z=0.
    exe, _ = helper(out/"cache")
    raw_models = {}
    for p in points:
        name = asset(p)
        assert name in ("CSC_ALL_Garden_Wall_Curve", "CSC_ALL_Garden_Wall_Curve_2")
        if name not in raw_models:
            child = parse(MOD/f"Assets/{name}.ast")
            models = list(child.find(MODELS))
            assert len(models) == 1
            geo = txt(models[0], "m_GeoName")
            dst = out/(geo+".json")
            subprocess.run([str(exe), str(exe.parent), str(MOD/f"Geometries/{geo}.fgx"), str(dst)],
                           cwd=exe.parent, check=True, capture_output=True)
            raw_models[name] = json.loads(dst.read_text())
    vertices = []
    for p in points:
        matrix = point_matrix(p)
        for mesh in raw_models[asset(p)]["meshes"]:
            vertices.extend((matrix @ [*v["position"], 1])[:3] for v in mesh["vertices"])
    vertices = np.array(vertices)
    lower, upper = vertices.min(axis=0), vertices.max(axis=0)
    center = (lower+upper)/2
    center[2] = 0
    assert np.linalg.norm(center[:2]) > 10
    for p in points:
        shift(p, -center)
    names = [txt(p, "m_Name") for p in points]
    assert without_positions(wall, names) == without_positions(before[WALL], names)
    save(wall, out/f"staged/Assets/{WALL}.ast")
    checks = {}
    for name in CAFES:
        root = copy.deepcopy(before[name])
        targets = [p for p in root.find(POINTS) if asset(p) == WALL]
        assert len(targets) == 1
        p = targets[0]
        assert txt(parameter(p, "TerrainFollowMode"), "m_Value") == "Pivot Height"
        parent_before = point_matrix(p)
        # A rotated/scaled parent needs the center vector in its own transformed frame.
        shift(p, parent_before[:3, :3] @ center)
        errors = []
        for old, new in zip(before[WALL].find(POINTS), points):
            errors.append(float(np.max(np.abs(
                parent_before @ point_matrix(old) - point_matrix(p) @ point_matrix(new)))))
        assert max(errors) < 1e-7, (name, errors)
        assert without_positions(root, [txt(p, "m_Name")]) == without_positions(before[name], [txt(p, "m_Name")])
        checks[name] = dict(max_matrix_error=max(errors), parent_position_ae=[
            float(p.findtext("m_position/"+a)) for a in "xyz"])
        save(root, out/f"staged/Assets/{name}.ast")
    # Independent saved-AST reconstruction includes the fitted courtyard decal.
    resolver = Resolver(MOD, DEFAULT_SDK)
    geometry_cache = {}
    for label in ("before", "staged"):
        for name in NAMES:
            resolver.index[(name+".ast").casefold()] = {out/f"{label}/Assets/{name}.ast"}
        assembly = Assembly(resolver)
        assembly.is_decal = lambda ident, near: False
        root = assembly.asset(out/f"{label}/Assets/{CAFES[0]}.ast")
        run = out/"review"/label
        run.mkdir(parents=True, exist_ok=True)
        prepare_geometry(assembly, out/"cache", run)
        job = dict(root=root, assets=assembly.assets, geometries=assembly.geometries,
                   materials=assembly.materials, warnings=assembly.warnings, output=str(run))
        (run/"job.json").write_text(json.dumps(job, indent=2))
        geometry_cache.update({g["source"]: hashlib.sha256(Path(g["source"]).read_bytes()).hexdigest()
                               for g in assembly.geometries.values()})
    report = dict(center_blender=center.tolist(), center_ae=(center/10).tolist(),
                  old_native_bounds=[lower.tolist(), upper.tolist()], checks=checks,
                  geometry_hashes=geometry_cache, only_attachment_positions_changed=True)
    (out/"migration.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report["checks"], indent=2), "CENTER_AE", (center/10).tolist())


def install(out):
    report = json.loads((out/"migration.json").read_text())
    assert (out/"review/staged/top.png").is_file()
    for path, digest in report["geometry_hashes"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest, path
    for name in NAMES:
        assert (MOD/f"Assets/{name}.ast").read_bytes() == (out/f"before/Assets/{name}.ast").read_bytes(), name
    cache_path = Path(os.environ["APPDATA"])/"AssetCloud/mod-Civ Supply Chains-asset-deps.json"
    cache_raw = cache_path.read_bytes()
    cache = json.loads(cache_raw.decode("utf-8-sig"))
    records = {e["Filename"].replace("\\", "/"): e for e in cache["Files"]}
    now = int(time.time()*10000000)+116444736000000000
    for name in NAMES:
        record = records["Civ Supply Chains/Assets/"+name+".ast"]
        record.update(Timestamp=now, Filesize=(out/f"staged/Assets/{name}.ast").stat().st_size)
    cache["Timestamp"] = now
    (out/"AssetCloud-before.json").write_bytes(cache_raw)
    assert cache_path.read_bytes() == cache_raw
    for name in NAMES:
        shutil.copy2(out/f"staged/Assets/{name}.ast", MOD/f"Assets/{name}.ast")
    cache_path.write_text(json.dumps(cache, separators=(",", ":")), encoding="utf-8")
    print("INSTALLED: eleven wall offsets and two compensated parent offsets; geometry unchanged")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("stage", "install"))
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    {"stage": stage, "install": install}[args.phase](args.output)
